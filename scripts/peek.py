#!/usr/bin/env python3
"""長い行を持つ正本ファイルを、文脈を汚さずに覗くための読み取り専用ヘルパー。

このリポジトリは1行が非常に長い（EN正本JSON は最大22KB、写真家HTML は最大8.7KB）。
`grep -n` や `sed -n` で覗くと1行ヒットしただけで数十KBが出力に入る。
本スクリプトは必ず既定300文字で切り、切った分は `…(+N chars)` と明示する。

使い方:
  python3 scripts/peek.py grep  <file> <regex> [--max 300] [--limit 20]
  python3 scripts/peek.py lines <file> <start> <end> [--max 300]
  python3 scripts/peek.py en    <slug> [field ...] [--max 300]   # EN正本JSONの1ページ
  python3 scripts/peek.py keys  <slug>                            # EN正本の持つキーと各長さ

書き込みは一切しない。
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EN_JSON = ROOT / "data" / "photographers-en-content.json"


def clip(s, n):
    s = s.replace("\n", "\\n")
    return s if len(s) <= n else f"{s[:n]}…(+{len(s) - n} chars)"


def cmd_grep(a):
    rx = re.compile(a.pattern)
    hits = 0
    for i, line in enumerate(Path(a.file).read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if rx.search(line):
            hits += 1
            if hits > a.limit:
                print(f"…(打ち切り: さらにヒットあり。--limit で調整)")
                return
            print(f"{i}:{clip(line, a.max)}")
    if not hits:
        print("(ヒットなし)")


def cmd_lines(a):
    lines = Path(a.file).read_text(encoding="utf-8", errors="replace").splitlines()
    for i in range(max(a.start, 1), min(a.end, len(lines)) + 1):
        print(f"{i}:{clip(lines[i - 1], a.max)}")


def _page(slug):
    pages = json.loads(EN_JSON.read_text(encoding="utf-8"))["pages"]
    key = slug if slug.endswith(".html") else f"{slug}.html"
    if key not in pages:
        sys.exit(f"ERROR: {key} は EN正本に存在しない（キーは <slug>.html 形式）")
    return key, pages[key]


def cmd_en(a):
    key, page = _page(a.slug)
    fields = a.fields or list(page)
    print(f"# {key}")
    for f in fields:
        if f not in page:
            print(f"{f}: (キーなし)")
            continue
        v = page[f]
        print(f"{f}: {clip(v if isinstance(v, str) else json.dumps(v, ensure_ascii=False), a.max)}")


def cmd_keys(a):
    key, page = _page(a.slug)
    print(f"# {key}  keys={len(page)}")
    for f, v in page.items():
        n = len(v) if isinstance(v, str) else len(json.dumps(v, ensure_ascii=False))
        print(f"  {f:26s} {n:7d}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("grep"); g.add_argument("file"); g.add_argument("pattern")
    g.add_argument("--max", type=int, default=300); g.add_argument("--limit", type=int, default=20)
    g.set_defaults(fn=cmd_grep)

    l = sub.add_parser("lines"); l.add_argument("file"); l.add_argument("start", type=int); l.add_argument("end", type=int)
    l.add_argument("--max", type=int, default=300); l.set_defaults(fn=cmd_lines)

    e = sub.add_parser("en"); e.add_argument("slug"); e.add_argument("fields", nargs="*")
    e.add_argument("--max", type=int, default=300); e.set_defaults(fn=cmd_en)

    k = sub.add_parser("keys"); k.add_argument("slug"); k.set_defaults(fn=cmd_keys)

    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
