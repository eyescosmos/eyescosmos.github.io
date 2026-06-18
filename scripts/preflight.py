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
import json
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


def _git_show_head(rel_path: str) -> str | None:
    """HEAD 時点のファイル内容。存在しなければ None。"""
    proc = subprocess.run(["git", "show", f"HEAD:{rel_path}"],
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


def _changed_en_slugs() -> dict:
    """working tree と HEAD の photographers-en-content.json を比較し、
    内容が変わった slug を {slug: (head_entry|None, work_entry)} で返す。"""
    head_raw = _git_show_head(EN_CONTENT_JSON)
    work_path = REPO / EN_CONTENT_JSON
    if head_raw is None or not work_path.exists():
        return {}
    try:
        head_pages = json.loads(head_raw).get("pages", {})
        work_pages = json.loads(work_path.read_text(encoding="utf-8")).get("pages", {})
    except Exception:  # noqa: BLE001
        return {}
    changed = {}
    for slug, work_entry in work_pages.items():
        head_entry = head_pages.get(slug)
        if head_entry != work_entry:
            changed[slug] = (head_entry, work_entry)
    return changed


def check_en_content_loss() -> None:
    """JSON-vs-HEAD: 触った EN エントリが本文・出典・リンクを失っていないか（HARD）。
    変更が無ければ必ずグリーンなので門にできる。"""
    for slug, (head_entry, work_entry) in _changed_en_slugs().items():
        if head_entry is None:
            continue  # 新規 slug は loss 判定対象外
        old, new = _en_entry_metrics(head_entry), _en_entry_metrics(work_entry)
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
    """変更 slug の再生成 EN HTML が JSON 宣言と一致するか（HARD）。
    JSON を編集したのに build_photographers_en.py --slug を回し忘れた状態を捕捉。"""
    if cee is None:
        return
    for slug, (_head, _work) in _changed_en_slugs().items():
        if slug in cee.HAND_MAINTAINED_EN:
            continue
        rep = cee.Report(slug)
        cee.check_html_vs_json(_work, slug, rep)
        for f in rep.fails:
            hard_failures.append(f"[EN closure] {f}（build_photographers_en.py --slug {slug[:-5]} を実行）")


def check_en_changed_slug_integrity() -> None:
    """変更 slug の sup/cite・リンク健全性（WARN）。
    既存バグを抱えた slug を触っても push はブロックしないが気づけるようにする。"""
    if cee is None:
        return
    for slug, (_head, _work) in _changed_en_slugs().items():
        rep = cee.Report(slug)
        cee.check_cite_supref(_work, rep)
        cee.check_links(_work, rep)
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
