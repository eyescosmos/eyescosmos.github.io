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
warnings: list[str] = []


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
        warnings.append(f"JS PHOTOGRAPHERS を eval できず重複チェックをスキップ: {e}")
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


def run_existing_check(script: str) -> None:
    path = REPO / "scripts" / script
    if not path.exists():
        return
    proc = subprocess.run([sys.executable, str(path)], capture_output=True, text=True, cwd=REPO)
    out = (proc.stdout + proc.stderr).strip()
    if proc.returncode != 0:
        warnings.append(f"{script} が非0終了 (既存ノイズの可能性): 末尾→ " + out.splitlines()[-1] if out else script)
    else:
        # 1文字リンク等の致命傷だけ拾う
        for token in ("museumangewandtekunst", ">S</a>"):
            if token in out:
                warnings.append(f"{script} 出力に '{token}' を検出")


def main() -> int:
    check_dup_ids_js()
    check_dup_ids_carddata()
    check_ga_coverage()
    run_existing_check("check_photographer_link_integrity.py")

    if warnings:
        print("── WARN（ブロックしない・要確認）──")
        for w in warnings:
            print("  ⚠ " + w)
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
