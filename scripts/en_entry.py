#!/usr/bin/env python3
"""Read-only viewer for a single EN photographer entry.

data/photographers-en-content.json は 297 slug を抱える巨大な単一ファイル
（約 24k 行）。EN 写真家ページの本文系を直す前に、対象 slug のフィールドだけを
安全に確認するための読み取り専用ツール。

このスクリプトは JSON も HTML も一切書き換えない。

使い方:
    python3 scripts/en_entry.py atget                 # atget.html のエントリを整形表示
    python3 scripts/en_entry.py atget --field thesis_html   # 1フィールドだけ
    python3 scripts/en_entry.py atget --raw           # 該当エントリの生 JSON
    python3 scripts/en_entry.py --list                # 全 slug を一覧
    python3 scripts/en_entry.py --list atg            # 部分一致で slug を検索
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(ROOT, 'data', 'photographers-en-content.json')

# 表示順（読みたい順に並べる）。ここに無いキーは末尾に「その他」として出す。
DISPLAY_ORDER = [
    'h1', 'years', 'title', 'meta_description',
    'thesis_label', 'thesis_html',
    'lead_html',
    'entry_meta_html', 'keywords_html',
    'view_works_note', 'view_works_links_html',
    'sections',
    'notable_works_html', 'photobooks_html',
    'external_links_html', 'further_reading_html',
    'sources_html', 'supref_ids', 'cite_ids',
    'site_directory_html',
    'canonical', 'hreflang', 'has_ga',
]
# 通常は省略する重複・定型フィールド（--all で表示）
VERBOSE_ONLY = {'og', 'twitter', 'jsonld', 'footer_html'}


def norm_slug(slug):
    slug = slug.strip()
    if not slug.endswith('.html'):
        slug += '.html'
    return slug


def is_empty(v):
    return v in (None, '', 'None')


def load():
    with open(JSON_PATH, encoding='utf-8') as fh:
        return json.load(fh)


def list_slugs(pages, needle=None):
    keys = sorted(pages)
    if needle:
        keys = [k for k in keys if needle.lower() in k.lower()]
    for k in keys:
        print(k[:-5] if k.endswith('.html') else k)
    print('\n%d slug%s' % (len(keys), '' if len(keys) == 1 else 's'))


def fmt_value(key, val):
    """1フィールドを読みやすい文字列にする。"""
    if is_empty(val):
        return '(empty)'
    if key == 'sections' and isinstance(val, list):
        out = []
        for s in val:
            num = s.get('num', '?')
            title = s.get('title', '')
            body = s.get('body_html', '') or ''
            out.append('  § %s  %s\n%s' % (num, title, _indent(body)))
        return '\n'.join(out)
    if isinstance(val, (list, dict)):
        return json.dumps(val, ensure_ascii=False, indent=2)
    return str(val)


def _indent(text, pad='    '):
    return '\n'.join(pad + line for line in text.splitlines())


def show_entry(entry, only_field=None, show_all=False):
    if only_field:
        if only_field not in entry:
            print('フィールドが存在しません: %s' % only_field, file=sys.stderr)
            print('利用可能: %s' % ', '.join(entry), file=sys.stderr)
            return 2
        print(fmt_value(only_field, entry[only_field]))
        return 0

    shown = set()
    keys = list(DISPLAY_ORDER)
    # DISPLAY_ORDER に無い未知キーを末尾へ
    keys += [k for k in entry if k not in DISPLAY_ORDER and k not in VERBOSE_ONLY]
    if show_all:
        keys += [k for k in VERBOSE_ONLY if k in entry]

    for k in keys:
        if k in shown or k not in entry:
            continue
        shown.add(k)
        print('\n\033[1m── %s ──\033[0m' % k)
        print(fmt_value(k, entry[k]))

    # cite/supref の食い違いを軽く知らせる（検査本体は check_en_entry.py）
    cite = set(entry.get('cite_ids') or [])
    sup = set(entry.get('supref_ids') or [])
    if cite or sup:
        miss_cite = sorted(sup - cite)   # 本文が参照するが出典に無い
        orphan = sorted(cite - sup)      # 出典にあるが本文が参照しない
        if miss_cite or orphan:
            print('\n\033[33m⚠ cite/supref 不一致のヒント（詳細は check_en_entry.py）\033[0m')
            if miss_cite:
                print('  本文 sup-ref があるのに出典に無い: %s' % miss_cite)
            if orphan:
                print('  出典にあるのに本文 sup-ref が無い: %s' % orphan)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('slug', nargs='?', help='対象 slug（.html は省略可）')
    ap.add_argument('--field', help='指定フィールドだけ表示')
    ap.add_argument('--raw', action='store_true', help='該当エントリの生 JSON を出力')
    ap.add_argument('--all', action='store_true', help='og/twitter/jsonld/footer も表示')
    ap.add_argument('--list', dest='do_list', action='store_true',
                    help='全 slug を一覧（slug を部分一致の絞り込みに使える）')
    args = ap.parse_args(argv)

    data = load()
    pages = data['pages']

    if args.do_list:
        list_slugs(pages, needle=args.slug)
        return 0

    if not args.slug:
        ap.error('slug を指定するか --list を使ってください')

    slug = norm_slug(args.slug)
    if slug not in pages:
        print('slug が見つかりません: %s' % slug, file=sys.stderr)
        cand = [k for k in pages if args.slug.lower() in k.lower()][:10]
        if cand:
            print('もしかして:', ', '.join(c[:-5] for c in cand), file=sys.stderr)
        return 2

    entry = pages[slug]
    if args.raw:
        print(json.dumps(entry, ensure_ascii=False, indent=2))
        return 0

    if not args.field:
        print('\033[1mEN entry: %s\033[0m' % slug)
    return show_entry(entry, only_field=args.field, show_all=args.all)


if __name__ == '__main__':
    sys.exit(main())
