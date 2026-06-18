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
