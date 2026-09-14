#!/usr/bin/env python3
"""長い行を持つ正本ファイルを、文脈を汚さずに覗くための読み取り専用ヘルパー。

このリポジトリは1行が非常に長い（写真家HTML は最大8.7KB）。
`grep -n` や `sed -n` で覗くと1行ヒットしただけで数十KBが出力に入る。
本スクリプトは必ず既定300文字で切り、切った分は `…(+N chars)` と明示する。

使い方:
  python3 scripts/peek.py grep  <file> <regex> [--max 300] [--limit 20]
  python3 scripts/peek.py lines <file> <start> <end> [--max 300]
  python3 scripts/peek.py       <slug> [block ...] [--max 300]   # EN HTMLの意味ブロック
  python3 scripts/peek.py en    <slug> [block ...] [--max 300]   # 上と同じ（旧CLI互換）
  python3 scripts/peek.py keys  <slug>                            # 意味ブロックと各長さ

書き込みは一切しない。
"""
import argparse
import re
import sys
from pathlib import Path

import en_content


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
    keys = en_content.load_en_page_keys()
    key, candidates = en_content.resolve_slug(slug, keys)
    if key is None:
        if candidates:
            sys.exit(f"ERROR: {slug} は一意に決まらない: {', '.join(candidates[:15])}")
        sys.exit(f"ERROR: {slug} は EN HTML に存在しない")
    html = en_content.load_en_html(key)
    if en_content.is_shim(key):
        return key, {"shim": en_content.shim_target(key) or "(target missing)"}
    return key, en_content.extract_en_summary(html)


def _block_value(page, field):
    if field == "sections":
        return " | ".join(f"{item['num']} {item['name']}" for item in page[field]) or "(none)"
    if field == "cites":
        ids = page["cite_ids"]
        return f"{page['cite_count']} cite(s): " + (
            ", ".join(f"cite-{n}" for n in ids) if ids else "(none)")
    if field == "links":
        links = list(dict.fromkeys((item["href"], item["text"]) for item in page[field]))
        return " | ".join(f"{text or '(no text)'} -> {href or '(empty)'}"
                          for href, text in links) or "(none)"
    if field == "seo":
        seo = page[field]
        hreflang = ", ".join(f"{lang}={href}" for lang, href in seo["hreflang"])
        return (f"title={seo['title']} | description={seo['description']} | "
                f"canonical={seo['canonical']} | hreflang={hreflang or '(missing)'} | "
                f"og:image={seo['og:image']} | GA={seo['GA']}")
    value = page[field]
    return str(value)


def cmd_en(a):
    key, page = _page(a.slug)
    fields = a.fields or (["shim"] if "shim" in page else
                          ["lead", "thesis", "sections", "cites", "links", "seo"])
    print(f"# {key}")
    for f in fields:
        if f not in page:
            if f == "cites" and "cite_count" in page:
                print(f"{f}: {clip(_block_value(page, f), a.max)}")
                continue
            print(f"{f}: (キーなし)")
            continue
        print(f"{f}: {clip(_block_value(page, f), a.max)}")


def cmd_keys(a):
    key, page = _page(a.slug)
    fields = (["shim"] if "shim" in page else
              ["lead", "thesis", "sections", "cites", "links", "seo"])
    print(f"# {key}  blocks={len(fields)}")
    for field in fields:
        print(f"  {field:26s} {len(_block_value(page, field)):7d}")


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

    argv = sys.argv[1:]
    if argv and argv[0] not in {"grep", "lines", "en", "keys"}:
        argv.insert(0, "en")
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
