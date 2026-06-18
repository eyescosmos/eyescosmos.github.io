#!/usr/bin/env python3
"""Preflight checks — push 前に「過去の事故クラス」を機械的に検出する。

設計方針:
- HARD（exit 1 でブロック）は、現在グリーンで決定論的な不変条件のみ。
  ここが赤い＝今回の変更で壊した、と断定できるものだけを門にする。
- 既存スクリプト（check_*.py）は既知の事前ノイズを含むため WARN 表示に留める
  （ブロックしない）。

使い方:  python3 scripts/preflight.py
CLAUDE.md の「不可視の必須要素」「重複防止」を文章ルールから機械チェックへ移管する土台。
"""
from __future__ import annotations
import functools
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GA_TOKEN = "googletagmanager"

hard_failures: list[str] = []
warnings: list[str] = []          # 要確認（今回の変更に起因しうる）
known_warnings: list[str] = []    # 既知・非ブロック（環境差や既存ノイズ）

# check_en_entry の検査ロジックを再利用する
sys.path.insert(0, str(REPO / "scripts"))
try:
    import check_en_entry as cee  # noqa: E402
except Exception:  # noqa: BLE001
    cee = None

EN_CONTENT_JSON = "data/photographers-en-content.json"


def eval_photographers() -> list[dict]:
    """taxonomy/photographer ジェネレータと同じ3ファイルを eval して PHOTOGRAPHERS を得る。"""
    files = [
        "data/photographers.js",
        "data/photographers-manual-additions.js",
        "data/photographers-supplement.js",
    ]
    src = ["(function(){ var window=this;"]
    for f in files:
        src.append((REPO / f).read_text(encoding="utf-8"))
    src.append("console.log(JSON.stringify(PHOTOGRAPHERS.map(function(p){return p&&p.id;})));")
    src.append("})();")
    proc = subprocess.run(
        ["osascript", "-l", "JavaScript"],
        input="\n".join(src).encode("utf-8"),
        capture_output=True,
    )
    payload = proc.stderr.decode("utf-8") or proc.stdout.decode("utf-8")
    return json.loads(payload)


def check_dup_ids_js() -> None:
    """photographers.js / supplement.js の二重登録（過去事故）を検出。"""
    try:
        ids = [i for i in eval_photographers() if i]
    except Exception as e:  # noqa: BLE001
        known_warnings.append(
            "JS写真家の重複チェックをスキップ（既知・非ブロック: osascript(JavaScript) を"
            f"使えない環境。macOS 以外では正常に出る）: {e}"
        )
        return
    seen, dups = set(), set()
    for i in ids:
        (dups if i in seen else seen).add(i)
    if dups:
        hard_failures.append(
            f"data/photographers*.js の PHOTOGRAPHERS に重複id: {sorted(dups)} "
            f"(新規は supplement.js のみへ。photographers.js は中核48名で固定)"
        )


def check_dup_ids_carddata() -> None:
    data = json.loads((REPO / "card-data.json").read_text(encoding="utf-8"))
    ids = [p.get("id") for p in data.get("photographers", []) if p.get("id")]
    seen, dups = set(), set()
    for i in ids:
        (dups if i in seen else seen).add(i)
    if dups:
        hard_failures.append(f"card-data.json に重複id: {sorted(dups)}")


def is_redirect_stub(html: str) -> bool:
    return ("noindex" in html) and ("http-equiv" in html.lower() and "refresh" in html.lower())


def check_ga_coverage() -> None:
    """公開 .html に GA があるか。例外: リダイレクトスタブ / *-backup.html / Google確認ファイル。"""
    missing: list[str] = []
    dirs = [".", "photographers", "movements", "eras", "countries",
            "en", "en/photographers", "en/countries", "en/movements", "en/eras"]
    for d in dirs:
        p = REPO / d
        if not p.is_dir():
            continue
        for f in sorted(p.glob("*.html")):
            name = f.name
            if name.endswith("-backup.html") or name.startswith("google"):
                continue
            html = f.read_text(encoding="utf-8", errors="ignore")
            if is_redirect_stub(html):
                continue
            if GA_TOKEN not in html:
                missing.append(str(f.relative_to(REPO)))
    if missing:
        hard_failures.append(
            f"GA(googletagmanager)欠落 {len(missing)}件: " + ", ".join(missing[:12])
            + (" …" if len(missing) > 12 else "")
        )


def _baseline_ref() -> str:
    """比較基準。push 時に実効化するため「公開済み側」を優先する。
    upstream（@{u}）→ origin/main → HEAD の順で最初に解決できたものを使う。
    env PREFLIGHT_BASE で上書き可。"""
    forced = os.environ.get("PREFLIGHT_BASE")
    if forced:
        return forced
    for cand in ("@{u}", "origin/main"):
        proc = subprocess.run(["git", "rev-parse", "--verify", "--quiet", cand],
                              capture_output=True, text=True, cwd=REPO)
        if proc.returncode == 0 and proc.stdout.strip():
            return cand
    return "HEAD"


def _git_show(ref: str, rel_path: str) -> str | None:
    """ref 時点のファイル内容。存在しなければ None。"""
    proc = subprocess.run(["git", "show", f"{ref}:{rel_path}"],
                          capture_output=True, text=True, cwd=REPO)
    return proc.stdout if proc.returncode == 0 else None


def _en_entry_metrics(entry: dict) -> dict:
    """EN エントリの「減ってはいけない」量を数える。"""
    sources = entry.get("sources_html") or ""
    body = "\n".join(
        ([entry.get("thesis_html") or "", entry.get("lead_html") or ""]
         + [s.get("body_html", "") for s in (entry.get("sections") or [])])
    )
    links = {h for h in re.findall(r'href="(https?://[^"]+)"', _all_link_html(entry))}
    return {
        "cite": len(set(re.findall(r'id="cite-(\d+)"', sources))),
        "sections": len(entry.get("sections") or []),
        "links": links,
        "thesis": bool((entry.get("thesis_html") or "").strip()),
        "supref": len(re.findall(r'href="#cite-\d+"', body)),
    }


def _all_link_html(entry: dict) -> str:
    if cee is not None:
        return cee.all_link_html(entry)
    # フォールバック（cee 不在時）
    fields = ("lead_html", "thesis_html", "keywords_html", "view_works_links_html",
              "notable_works_html", "photobooks_html", "external_links_html",
              "further_reading_html", "sources_html", "site_directory_html")
    chunks = [entry.get(f) or "" for f in fields if entry.get(f) not in (None, "None")]
    chunks += [s.get("body_html", "") for s in (entry.get("sections") or [])]
    return "\n".join(chunks)


HAND_MAINTAINED_EN = getattr(cee, "HAND_MAINTAINED_EN", {"stieglitz.html", "annie-leibovitz.html"})


@functools.lru_cache(maxsize=1)
def _touched_en() -> dict:
    """baseline（origin/main 等）と作業ツリーを比較し、触れた EN slug を集める。
    JSON エントリの変化と en/photographers/*.html の変化の両方を合流させる。
    返り値 {slug: {"base", "work", "json_changed", "html_changed"}}。"""
    baseline = _baseline_ref()
    work_path = REPO / EN_CONTENT_JSON
    try:
        work_pages = json.loads(work_path.read_text(encoding="utf-8")).get("pages", {}) \
            if work_path.exists() else {}
    except Exception:  # noqa: BLE001
        work_pages = {}
    base_raw = _git_show(baseline, EN_CONTENT_JSON)
    try:
        base_pages = json.loads(base_raw).get("pages", {}) if base_raw else {}
    except Exception:  # noqa: BLE001
        base_pages = {}

    touched: dict[str, dict] = {}
    # 1) JSON エントリの変化
    for slug, we in work_pages.items():
        be = base_pages.get(slug)
        if be != we:
            touched[slug] = {"base": be, "work": we, "json_changed": True, "html_changed": False}
    # 2) en/photographers/*.html の変化
    proc = subprocess.run(["git", "diff", "--name-only", baseline, "--", "en/photographers"],
                          capture_output=True, text=True, cwd=REPO)
    for line in proc.stdout.splitlines():
        name = os.path.basename(line.strip())
        if not name.endswith(".html") or name.startswith("jp-") or name.endswith("-backup.html"):
            continue
        info = touched.get(name)
        if info:
            info["html_changed"] = True
        else:
            touched[name] = {"base": base_pages.get(name), "work": work_pages.get(name),
                             "json_changed": False, "html_changed": True}
    return touched


def check_en_content_loss() -> None:
    """JSON-vs-baseline: 触った EN エントリが本文・出典・リンクを失っていないか（HARD）。
    変更が無ければ必ずグリーンなので門にできる。"""
    for slug, info in _touched_en().items():
        if not info["json_changed"]:
            continue
        be, we = info["base"], info["work"]
        if be is None or we is None:
            continue  # 新規 slug / 削除は loss 判定対象外
        old, new = _en_entry_metrics(be), _en_entry_metrics(we)
        losses = []
        if new["cite"] < old["cite"]:
            losses.append(f"出典 {old['cite']}→{new['cite']}")
        if new["sections"] < old["sections"]:
            losses.append(f"本文セクション {old['sections']}→{new['sections']}")
        if new["supref"] < old["supref"]:
            losses.append(f"本文 sup-ref {old['supref']}→{new['supref']}")
        if old["thesis"] and not new["thesis"]:
            losses.append("thesis が空に")
        dropped = sorted(old["links"] - new["links"])
        if dropped:
            losses.append(f"リンク{len(dropped)}件消失: {dropped[:3]}")
        if losses:
            hard_failures.append(
                f"{EN_CONTENT_JSON} の {slug} が内容を失っている: " + " / ".join(losses)
            )


def check_en_changed_slug_closure() -> None:
    """触った slug の EN HTML が JSON 宣言と一致するか（HARD）。
    JSON を直して再生成し忘れた／生成物を直接編集して JSON と乖離した状態を捕捉。"""
    if cee is None:
        return
    for slug, info in _touched_en().items():
        if slug in HAND_MAINTAINED_EN or info["work"] is None:
            continue
        rep = cee.Report(slug)
        cee.check_html_vs_json(info["work"], slug, rep)
        for f in rep.fails:
            hard_failures.append(
                f"[EN closure] {f}（build_photographers_en.py --slug {slug[:-5]} を実行）")


def check_en_direct_edit() -> None:
    """生成物の EN HTML が直接編集された疑いを検知（WARN）。
    EN HTML が変わったのに対応する JSON が変わっていない＝手編集の兆候。
    手書き維持ページ（annie-leibovitz / stieglitz）は例外。"""
    for slug, info in _touched_en().items():
        if slug in HAND_MAINTAINED_EN:
            continue
        if info["html_changed"] and not info["json_changed"]:
            warnings.append(
                f"[EN {slug}] 生成物の EN HTML を直接編集した疑い。正本は {EN_CONTENT_JSON}。"
                f"JSON を直して build_photographers_en.py --slug {slug[:-5]} で再生成すること"
            )


def check_en_changed_slug_integrity() -> None:
    """触った slug の sup/cite・リンク健全性（WARN）。
    既存バグを抱えた slug を触っても push はブロックしないが気づけるようにする。"""
    if cee is None:
        return
    for slug, info in _touched_en().items():
        if info["work"] is None:
            continue
        rep = cee.Report(slug)
        cee.check_cite_supref(info["work"], rep)
        cee.check_links(info["work"], rep)
        for f in rep.fails:
            warnings.append(f"[EN {slug}] {f}")


# ── 写真家以外の EN ページ（国別 / 年代・運動 / アーカイブ）の軽量ガード ──────
# 設計（Codex 合意 2026-06-19）:
#   - 正本 JSON のエントリ内容消失 = HARD（変更が無ければ必ずグリーン＝門にできる）
#   - 生成物 EN HTML の直接編集疑い = WARN
#   - 触ったファイル / 触った正本エントリだけ検査（baseline は写真家ガードと共通）
#   - 本文が JSON 外（build_taxonomy_en.py の直書き）にもある混在構造でも、
#     「JSON が確実に内容を失った」ことだけを HARD にする。曖昧判定はしない。
#   - per-slug リーダは追加しない（写真家のみで十分という方針）。

COUNTRY_JSON = "data/country-pages.json"
TAXONOMY_JSON = "data/taxonomy-en-content.json"
CARD_DATA_JSON = "card-data.json"


def _is_filled(v) -> bool:
    """JSON 値が「中身を持つ」か（消失判定用）。str は空白除去、コンテナは長さで判定。"""
    if isinstance(v, str):
        return bool(v.strip())
    if isinstance(v, (list, dict)):
        return len(v) > 0
    return v is not None


def _load_json_ref(baseline: str, rel_path: str):
    """baseline 時点と作業ツリーの JSON を (base, work) で返す（解析失敗時 None）。"""
    def _parse(text):
        try:
            return json.loads(text) if text else None
        except Exception:  # noqa: BLE001
            return None
    base = _parse(_git_show(baseline, rel_path))
    wp = REPO / rel_path
    work = _parse(wp.read_text(encoding="utf-8")) if wp.exists() else None
    return base, work


def _changed_html_basenames(baseline: str, rel_dir: str) -> set[str]:
    """baseline と作業ツリーで差分のある rel_dir 直下の *.html ベース名。
    リダイレクトスタブ / *-backup.html は除外（直接編集の対象ではない）。"""
    proc = subprocess.run(["git", "diff", "--name-only", baseline, "--", rel_dir],
                          capture_output=True, text=True, cwd=REPO)
    out: set[str] = set()
    for line in proc.stdout.splitlines():
        name = os.path.basename(line.strip())
        if not name.endswith(".html") or name.endswith("-backup.html"):
            continue
        # rel_dir 直下のみ（en の archive.html 等。サブディレクトリは別 rel_dir で扱う）
        if os.path.dirname(line.strip()) != rel_dir:
            continue
        fp = REPO / rel_dir / name
        if fp.exists() and is_redirect_stub(fp.read_text(encoding="utf-8", errors="ignore")):
            continue
        out.add(name)
    return out


def check_country_en() -> None:
    """国別 EN（en/countries/*.html）の正本 country-pages.json の内容消失=HARD、
    生成物 HTML の直接編集疑い=WARN。"""
    baseline = _baseline_ref()
    base, work = _load_json_ref(baseline, COUNTRY_JSON)
    if not isinstance(work, list):
        return
    base_map = {r["slug"]: r for r in (base or []) if isinstance(r, dict) and r.get("slug")}
    work_map = {r["slug"]: r for r in work if isinstance(r, dict) and r.get("slug")}
    changed = {s for s, we in work_map.items() if base_map.get(s) != we}
    # 1) 正本の内容消失（HARD）— base/work 双方にあるエントリのみ
    for slug in changed:
        be, we = base_map.get(slug), work_map[slug]
        if be is None:
            continue  # 新規 slug は loss 判定対象外
        losses = [f for f in ("lead", "nameEn", "nameJa")
                  if _is_filled(be.get(f)) and not _is_filled(we.get(f))]
        if be.get("codes") and not we.get("codes"):
            losses.append("codes")
        if losses:
            hard_failures.append(
                f"{COUNTRY_JSON} の {slug} が内容を失っている: {', '.join(losses)}")
    # 2) 生成物 EN HTML の直接編集疑い（WARN）
    for name in _changed_html_basenames(baseline, "en/countries"):
        slug = name[:-5]
        if slug not in work_map:        # 複合スタブ等は正本に無い → 対象外
            continue
        if slug not in changed:
            warnings.append(
                f"[EN country {slug}] 生成物 en/countries/{name} を直接編集した疑い。"
                f"正本は {COUNTRY_JSON}。generate_country_pages_en.py で再生成すること")


def check_taxonomy_en() -> None:
    """年代・運動 EN（en/eras・en/movements）の正本 taxonomy-en-content.json の
    内容消失=HARD、生成物 HTML の直接編集疑い=WARN。本文が builder 直書きにも
    あるため、判定は「JSON が確実に失った」ものだけに限定する。"""
    baseline = _baseline_ref()
    base, work = _load_json_ref(baseline, TAXONOMY_JSON)
    if not isinstance(work, dict):
        return
    for group, rel_dir in (("movements", "en/movements"), ("eras", "en/eras")):
        base_g = (base or {}).get(group, {}) if isinstance(base, dict) else {}
        work_g = work.get(group, {})
        if not isinstance(work_g, dict):
            continue
        changed = {k for k, wv in work_g.items() if base_g.get(k) != wv}
        # 内容消失（HARD）
        for slug in changed:
            be, we = base_g.get(slug), work_g.get(slug)
            if be is None:
                continue
            losses = []
            bmeta, wmeta = be.get("meta", {}), we.get("meta", {})
            for field in ("title", "description"):
                if _is_filled(bmeta.get(field)) and not _is_filled(wmeta.get(field)):
                    losses.append(f"meta.{field}")
            bsec, wsec = be.get("sections", {}), we.get("sections", {})
            for key, bv in bsec.items():
                if _is_filled(bv) and not _is_filled(wsec.get(key)):
                    losses.append(f"section[{key}]")
            if losses:
                hard_failures.append(
                    f"{TAXONOMY_JSON} の {group}/{slug} が内容を失っている: "
                    + ", ".join(losses[:4]))
        # 直接編集（WARN）
        for name in _changed_html_basenames(baseline, rel_dir):
            slug = name[:-5]
            if slug not in work_g:       # JA 名スタブ等は正本キーに無い → 対象外
                continue
            if slug not in changed:
                warnings.append(
                    f"[EN {group}/{slug}] 生成物 {rel_dir}/{name} を直接編集した疑い。"
                    f"正本は {TAXONOMY_JSON}。build_taxonomy_en.py で再生成すること")


def check_archive_en() -> None:
    """アーカイブ EN（en/archive.html）の正本 card-data.json の内容消失=HARD、
    生成物 HTML だけが変わって card-data.json が不変なら直接編集疑い=WARN。"""
    baseline = _baseline_ref()
    base, work = _load_json_ref(baseline, CARD_DATA_JSON)
    if not isinstance(work, dict):
        return
    json_changed = base != work
    if isinstance(base, dict) and json_changed:
        for group in ("photographers", "movements"):
            base_list = base.get(group, []) or []
            work_list = work.get(group, []) or []
            base_map = {c.get("id"): c for c in base_list if isinstance(c, dict) and c.get("id")}
            work_map = {c.get("id"): c for c in work_list if isinstance(c, dict) and c.get("id")}
            if len(work_list) < len(base_list):
                hard_failures.append(
                    f"{CARD_DATA_JSON} の {group} カード数が減少: "
                    f"{len(base_list)}→{len(work_list)}")
            missing = sorted(set(base_map) - set(work_map))
            if missing:
                hard_failures.append(
                    f"{CARD_DATA_JSON} の {group} から card 消失: {missing[:5]}")
            for cid in set(base_map) & set(work_map):
                bc, wc = base_map[cid], work_map[cid]
                lost = [f for f in ("nameEn", "nameJa", "href")
                        if _is_filled(bc.get(f)) and not _is_filled(wc.get(f))]
                if lost:
                    hard_failures.append(
                        f"{CARD_DATA_JSON} の {group}/{cid} がフィールドを失っている: "
                        + ", ".join(lost))
    # 生成物 en/archive.html の直接編集疑い（WARN）
    proc = subprocess.run(["git", "diff", "--name-only", baseline, "--", "en/archive.html"],
                          capture_output=True, text=True, cwd=REPO)
    if proc.stdout.strip() and not json_changed:
        warnings.append(
            f"[EN archive] 生成物 en/archive.html を直接編集した疑い。"
            f"正本は {CARD_DATA_JSON}。build_archive_en.py で再生成すること")


def run_existing_check(script: str) -> None:
    path = REPO / "scripts" / script
    if not path.exists():
        return
    proc = subprocess.run([sys.executable, str(path)], capture_output=True, text=True, cwd=REPO)
    out = (proc.stdout + proc.stderr).strip()
    if proc.returncode != 0:
        tail = out.splitlines()[-1] if out else script
        known_warnings.append(
            f"{script} が非0終了（既知ノイズ・非ブロック: Biography 先頭文言等の既存指摘）: 末尾→ {tail}"
        )
    # 1文字リンク等の致命傷は returncode に関わらず拾い、要確認として上げる
    for token in ("museumangewandtekunst", ">S</a>"):
        if token in out:
            warnings.append(f"{script} 出力に '{token}' を検出（要確認）")


def main() -> int:
    check_dup_ids_js()
    check_dup_ids_carddata()
    check_ga_coverage()
    check_en_content_loss()
    check_en_changed_slug_closure()
    check_en_direct_edit()
    check_en_changed_slug_integrity()
    check_country_en()
    check_taxonomy_en()
    check_archive_en()
    run_existing_check("check_photographer_link_integrity.py")

    if warnings:
        print("── WARN（要確認・ブロックしない）──")
        for w in warnings:
            print("  ⚠ " + w)
    if known_warnings:
        print("── WARN（既知・非ブロック / 対応不要）──")
        for w in known_warnings:
            print("  · " + w)
    if hard_failures:
        print("\n── FAIL（push をブロック）──")
        for h in hard_failures:
            print("  ✗ " + h)
        print("\npreflight: FAILED")
        return 1
    print("preflight: OK（決定論チェック全通過）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
