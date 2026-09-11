#!/usr/bin/env python3
"""スナップショットを集計して「次に本文を厚くすべき写真家」の名簿を出す。

設計は docs/seo-selector-spec.md。要点:

- **ページを一切書き換えない。** 名簿とレポートを書き出すだけ。
- GSC も Bing も新旧2プロパティを合算する。片方だけでは実態が見えない。
- 直近に update 済みの写真家は除外する（効果判定の期間中のため）。

使い方:
  python3 scripts/seo_select.py                名簿を表示して保存
  python3 scripts/seo_select.py --dry-run      表示のみ
  python3 scripts/seo_select.py --limit 10     名簿の人数（既定10）
  python3 scripts/seo_select.py --cooldown 56  直近何日以内の update を除外するか
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_HOME = Path("~/Desktop/claude code/photography history/seo-watch").expanduser()
SNAP_DIR = DATA_HOME / "snapshots"
REPORT_DIR = DATA_HOME / "reports"
LOG_PATH = DATA_HOME / "selection-log.json"

PAGE_RE = re.compile(r"^/(?:en/)?photographers/([^/]+)\.html$")

# 閾値。2026-09-11 の較正回で実データを見て決めた暫定値。コードを触らずここだけ変える
TIER_RULES = {
    "A": {"label": "順位に余地", "pos_min": 5.0, "pos_max": 20.0, "impr_min": 20},
    "B": {"label": "出ているが選ばれない", "impr_min": 30, "clicks_max": 1},
    "C": {"label": "評価が始まった", "impr_min": 15, "growth_min": 2.0},
    "D": {"label": "Bing が先行", "bing_impr_min": 10, "gsc_impr_max": 10},
}


# --- 読み込み -----------------------------------------------------------
def load_snapshots() -> tuple[dict, dict | None, dict | None]:
    """最新の GSC / 一つ前の GSC / 最新の BWT を返す。"""
    gsc = sorted(SNAP_DIR.glob("gsc-*.json"))
    if not gsc:
        sys.exit(f"スナップショットがない: {SNAP_DIR}\n  先に python3 scripts/seo_fetch.py を実行する")
    latest = json.loads(gsc[-1].read_text())
    # 「一つ前」は窓が重ならないものを選ぶ。同日取得の重複を避ける
    prev = None
    for path in reversed(gsc[:-1]):
        cand = json.loads(path.read_text())
        if cand["window"]["end"] < latest["window"]["start"]:
            prev = cand
            break
    bwt_files = sorted(SNAP_DIR.glob("bwt-*.json"))
    bwt = json.loads(bwt_files[-1].read_text()) if bwt_files else None
    return latest, prev, bwt


def photographer_index() -> dict[str, dict]:
    data = json.loads((ROOT / "card-data.json").read_text())
    return {p["id"]: p for p in data.get("photographers", [])}


def aggregate_gsc(snapshot: dict) -> dict[str, dict]:
    """新旧プロパティを合算し、写真家 slug ごとにまとめる。"""
    agg: dict[str, dict] = defaultdict(
        lambda: {"clicks": 0, "impressions": 0, "pos_weighted": 0.0, "queries": defaultdict(int), "en_impr": 0}
    )
    for _prop, payload in snapshot["properties"].items():
        for row in payload["rows"]:
            match = PAGE_RE.match(row["path"])
            if not match:
                continue
            entry = agg[match.group(1)]
            entry["clicks"] += row["clicks"]
            entry["impressions"] += row["impressions"]
            entry["pos_weighted"] += row["position"] * row["impressions"]
            entry["queries"][row["query"]] += row["impressions"]
            if row["path"].startswith("/en/"):
                entry["en_impr"] += row["impressions"]
    for entry in agg.values():
        entry["position"] = entry["pos_weighted"] / entry["impressions"] if entry["impressions"] else 0.0
        entry["ctr"] = entry["clicks"] / entry["impressions"] if entry["impressions"] else 0.0
    return dict(agg)


def aggregate_bwt(snapshot: dict | None) -> dict[str, dict]:
    """Bing のページ別集計を slug ごとにまとめる。両プロパティ合算。"""
    agg: dict[str, dict] = defaultdict(lambda: {"clicks": 0, "impressions": 0})
    if not snapshot:
        return {}
    for _prop, payload in snapshot.get("properties", {}).items():
        pages = payload.get("pages")
        if not isinstance(pages, list):
            continue
        for row in pages:
            match = PAGE_RE.match(row.get("path") or "")
            if not match:
                continue
            entry = agg[match.group(1)]
            entry["clicks"] += row.get("clicks") or 0
            entry["impressions"] += row.get("impressions") or 0
    return dict(agg)


# 本文を厚くした update と、横断スクリプトの機械的な差分を分ける閾値。
# AI開示ブロック追加・ドメイン一括置換・サイドバー検索修正・エンダッシュ統一は
# いずれも1コミットあたり 1〜9 行だった（2026-09-11 実測）。本文追加はこれを大きく超える。
SUBSTANTIVE_ADDED_LINES = 50


def last_enriched() -> dict[str, date]:
    """写真家ページの本文が最後に**実質的に**更新された日を git から引く。

    単なる最終コミット日では使えない。横断スクリプトが全ページを触るため、
    それを拾うと候補のほぼ全員が除外される。追加行数で実質の update だけを見る。
    """
    out = subprocess.run(
        ["git", "log", "--numstat", "--pretty=format:@%cs", "--since=8 months ago", "--", "photographers"],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout
    enriched: dict[str, date] = {}
    current: date | None = None
    for line in out.splitlines():
        if line.startswith("@"):
            try:
                current = date.fromisoformat(line[1:])
            except ValueError:
                current = None
            continue
        parts = line.split("\t")
        if len(parts) != 3 or not current or not parts[2].endswith(".html"):
            continue
        try:
            added = int(parts[0])
        except ValueError:  # バイナリ差分の "-"
            continue
        if added < SUBSTANTIVE_ADDED_LINES:
            continue
        slug = Path(parts[2]).stem
        if slug not in enriched:  # git log は新しい順
            enriched[slug] = current
    return enriched


# --- 選定 ---------------------------------------------------------------
def growth_ratio(cur: dict, prev: dict | None) -> float | None:
    """前期比。前期の母数が小さいと比が暴れるので下限を設ける。"""
    if not prev or prev.get("impressions", 0) < 3:
        return None
    return cur["impressions"] / prev["impressions"]


def assign_tier(cur: dict, bing: dict, growth: float | None) -> tuple[str, str] | None:
    """層を割り当てる。層はラベルであって優先順位ではない（並びは score が決める）。"""
    impr, clicks, pos = cur["impressions"], cur["clicks"], cur["position"]
    note = f"・前期の{growth:.1f}倍" if growth and growth >= TIER_RULES["C"]["growth_min"] else ""

    rule = TIER_RULES["A"]
    if rule["pos_min"] <= pos <= rule["pos_max"] and impr >= rule["impr_min"]:
        return "A", f"{pos:.1f}位で表示{impr}・クリック{clicks}{note}"

    rule = TIER_RULES["B"]
    if impr >= rule["impr_min"] and clicks <= rule["clicks_max"]:
        return "B", f"表示{impr}に対しクリック{clicks}・{pos:.1f}位{note}"

    rule = TIER_RULES["D"]
    if bing.get("impressions", 0) >= rule["bing_impr_min"] and impr < rule["gsc_impr_max"]:
        return "D", f"Bing表示{bing['impressions']}に対しGoogle表示{impr}"

    rule = TIER_RULES["C"]
    if growth and growth >= rule["growth_min"] and impr >= rule["impr_min"]:
        return "C", f"表示が前期の{growth:.1f}倍（{impr}）"

    return None


def score(cur: dict, growth: float | None) -> float:
    """並び順を決める点数。表示回数を、順位の近さと勢いで割り引く。

    層（A/B/C/D）は説明のラベルであって並び順ではない。層で並べると、
    表示416の写真家が表示26の写真家より下に沈む（2026-09-11 の較正で判明）。
    """
    pos = cur["position"]
    if pos <= 0:
        pos_factor = 0.2                      # 順位が取れていない
    elif pos <= 3:
        pos_factor = 0.3                      # すでに上位。伸びしろが小さい
    elif pos <= 20:
        pos_factor = 1.0                      # 厚くすれば届く距離
    elif pos <= 40:
        pos_factor = 0.5
    else:
        pos_factor = 0.2                      # 遠い
    growth_factor = 1.5 if growth and growth >= TIER_RULES["C"]["growth_min"] else 1.0
    return cur["impressions"] * pos_factor * growth_factor


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=10, help="名簿の人数（既定10）")
    ap.add_argument("--cooldown", type=int, default=56, help="直近何日以内の update を除外するか（既定56）")
    ap.add_argument("--dry-run", action="store_true", help="保存しない")
    args = ap.parse_args()

    latest, prev, bwt = load_snapshots()
    cur_agg = aggregate_gsc(latest)
    prev_agg = aggregate_gsc(prev) if prev else {}
    bwt_agg = aggregate_bwt(bwt)
    index = photographer_index()
    enriched = last_enriched()
    today = date.today()

    candidates, excluded = [], []
    for slug in set(cur_agg) | set(bwt_agg):
        cur = cur_agg.get(slug, {"clicks": 0, "impressions": 0, "position": 0.0, "ctr": 0.0,
                                 "queries": {}, "en_impr": 0})
        bing = bwt_agg.get(slug, {"clicks": 0, "impressions": 0})
        growth = growth_ratio(cur, prev_agg.get(slug))
        verdict = assign_tier(cur, bing, growth)
        if not verdict:
            continue
        tier, reason = verdict

        if slug in enriched and (today - enriched[slug]).days < args.cooldown:
            excluded.append((slug, f"{(today - enriched[slug]).days}日前に本文を更新済み"))
            continue
        if cur["position"] and cur["position"] <= 3.0 and cur["ctr"] >= 0.10:
            excluded.append((slug, f"{cur['position']:.1f}位・CTR{cur['ctr']:.0%}で十分"))
            continue

        meta = index.get(slug, {})
        top = sorted(cur["queries"].items(), key=lambda kv: -kv[1])[:5]
        candidates.append({
            "slug": slug,
            "name": meta.get("nameJa") or slug,
            "tier": tier,
            "reason": reason,
            "clicks": cur["clicks"],
            "impressions": cur["impressions"],
            "position": round(cur["position"], 1),
            "ctr": round(cur["ctr"], 4),
            "en_impressions": cur["en_impr"],
            "bing_clicks": bing["clicks"],
            "bing_impressions": bing["impressions"],
            "growth": round(growth, 2) if growth else None,
            "score": round(score(cur, growth), 1),
            "top_queries": [{"query": q, "impressions": i} for q, i in top],
            "in_site": slug in index,
        })

    candidates.sort(key=lambda c: -c["score"])
    chosen = candidates[:args.limit]

    # --- 表示 ---
    win = latest["window"]
    print(f"\n期間 {win['start']} 〜 {win['end']}（GSC 新旧合算 + Bing）")
    if prev:
        print(f"前期 {prev['window']['start']} 〜 {prev['window']['end']}")
    print(f"候補 {len(candidates)} 名 / 除外 {len(excluded)} 名 → 名簿 {len(chosen)} 名\n")
    print(f"{'#':<3}{'層':<3}{'slug':<24}{'名前':<20}{'点':>7}  理由")
    print("-" * 104)
    for i, c in enumerate(chosen, 1):
        print(f"{i:<3}{c['tier']:<3}{c['slug'][:22]:<24}{(c['name'] or '')[:18]:<20}"
              f"{c['score']:>7.0f}  {c['reason']}")
    print()
    for c in chosen:
        qs = "、".join(q["query"] for q in c["top_queries"][:4]) or "（クエリなし）"
        print(f"  {c['slug']}: {qs}")
    if excluded:
        print(f"\n除外 {len(excluded)} 名:")
        for slug, why in sorted(excluded)[:20]:
            print(f"  {slug:<28}{why}")

    if args.dry_run:
        print("\n[dry-run] 保存しない")
        return 0

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    batch = {
        "batchId": today.isoformat(),
        "selectedAt": today.isoformat(),
        "window": win,
        "prevWindow": prev["window"] if prev else None,
        "actionDate": None,
        "reviewDueDate": None,
        "verdict": None,
        "members": [dict(c, status="selected") for c in chosen],
    }
    # レポートの骨格。検索ニーズと素材依頼文は空欄で出す。
    # ここは数字から機械的に書けないので、スケジュールタスクで起動した Claude が埋める。
    lines = [
        f"# 名簿 {today.isoformat()}",
        "",
        f"- 期間: {win['start']} 〜 {win['end']}（GSC 新旧合算 + Bing）",
        f"- 前期: {prev['window']['start']} 〜 {prev['window']['end']}" if prev else "- 前期: なし",
        f"- 候補 {len(candidates)} 名 / 除外 {len(excluded)} 名 / 名簿 {len(chosen)} 名",
        "",
        "## 名簿",
        "",
        "| # | 層 | slug | 名前 | 点 | クリック | 表示 | 順位 | Bing表示 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for i, c in enumerate(chosen, 1):
        lines.append(f"| {i} | {c['tier']} | `{c['slug']}` | {c['name']} | {c['score']:.0f} | "
                     f"{c['clicks']} | {c['impressions']} | {c['position']:.1f} | {c['bing_impressions']} |")
    lines += ["", "## 各人の詳細", ""]
    for i, c in enumerate(chosen, 1):
        lines += [
            f"### {i}. {c['name']}  `{c['slug']}`",
            "",
            f"- 層 {c['tier']}: {c['reason']}",
            f"- 上位クエリ: " + "、".join(f"{q['query']}（{q['impressions']}）" for q in c["top_queries"]),
            f"- EN ページの表示: {c['en_impressions']}",
            "- **検索ニーズ**: TODO",
            "- **素材依頼文**: TODO",
            "",
        ]
    if excluded:
        lines += ["## 除外", ""] + [f"- `{slug}` — {why}" for slug, why in sorted(excluded)] + [""]
    report_path = REPORT_DIR / f"report-{today.isoformat()}.md"
    report_path.write_text("\n".join(lines))
    print(f"保存: {report_path}")

    log = json.loads(LOG_PATH.read_text()) if LOG_PATH.exists() else {"batches": []}
    log["batches"] = [b for b in log["batches"] if b["batchId"] != batch["batchId"]] + [batch]
    LOG_PATH.write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n")
    print(f"\n保存: {LOG_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
