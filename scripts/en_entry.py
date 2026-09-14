#!/usr/bin/env python3
"""Read-only summary viewer for one canonical EN photographer HTML page.

対象 EN HTML から lead / thesis / 節見出し / cite / <main> 内リンク / SEO必須値を
抽出して表示する。JSON は読まず、HTML も書き換えない。

使い方:
    python3 scripts/en_entry.py atget
    python3 scripts/en_entry.py atget --field thesis
    python3 scripts/en_entry.py atget --raw
    python3 scripts/en_entry.py --list
    python3 scripts/en_entry.py --list atg
"""
import argparse
import signal
import sys

import en_content

# `| head` 等でパイプが早期に閉じても Python の BrokenPipeError 表示を出さない
if hasattr(signal, 'SIGPIPE'):
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

DISPLAY_ORDER = ('lead', 'thesis', 'sections', 'cites', 'links', 'seo')


def list_slugs(page_keys, needle=None):
    keys = page_keys
    if needle:
        keys = [key for key in keys if needle.lower() in key.lower()]
    for key in keys:
        print(key[:-5])
    print('\n%d slug%s' % (len(keys), '' if len(keys) == 1 else 's'))


def _fmt_sections(summary):
    sections = summary['sections']
    if not sections:
        return '(none)'
    return '\n'.join('  %s  %s' % (item['num'], item['name']) for item in sections)


def _fmt_cites(summary):
    ids = summary['cite_ids']
    return '%d cite(s): %s' % (
        summary['cite_count'], ', '.join('cite-%d' % n for n in ids) if ids else '(none)')


def _fmt_links(summary):
    links = list(dict.fromkeys((item['href'], item['text']) for item in summary['links']))
    if not links:
        return '(none)'
    return '\n'.join('  - %s -> %s' % (text or '(no text)', href or '(empty)')
                     for href, text in links)


def _fmt_seo(summary):
    seo = summary['seo']
    hreflang = seo['hreflang']
    rows = [
        '  title: %s' % (seo['title'] or '(missing)'),
        '  description: %s' % (seo['description'] or '(missing)'),
        '  canonical: %s' % (seo['canonical'] or '(missing)'),
    ]
    if hreflang:
        rows.append('  hreflang:')
        rows.extend('    %s: %s' % (lang, href) for lang, href in hreflang)
    else:
        rows.append('  hreflang: (missing)')
    rows.extend([
        '  og:image: %s' % (seo['og:image'] or '(missing)'),
        '  GA: %s' % seo['GA'],
    ])
    return '\n'.join(rows)


def field_value(summary, field):
    if field == 'lead':
        return summary['lead'] or '(empty)'
    if field == 'thesis':
        return summary['thesis'] or '(empty)'
    if field == 'sections':
        return _fmt_sections(summary)
    if field == 'cites':
        return _fmt_cites(summary)
    if field == 'links':
        return _fmt_links(summary)
    if field == 'seo':
        return _fmt_seo(summary)
    raise KeyError(field)


def show_summary(summary, only_field=None):
    if only_field:
        try:
            print(field_value(summary, only_field))
        except KeyError:
            print('フィールドが存在しません: %s' % only_field, file=sys.stderr)
            print('利用可能: %s' % ', '.join(DISPLAY_ORDER), file=sys.stderr)
            return 2
        return 0

    for field in DISPLAY_ORDER:
        print('\n\033[1m── %s ──\033[0m' % field)
        print(field_value(summary, field))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('slug', nargs='?', help='対象 slug（通称・.html 省略可）')
    ap.add_argument('--field', choices=DISPLAY_ORDER, help='指定した意味ブロックだけ表示')
    ap.add_argument('--raw', action='store_true', help='該当 EN HTML をそのまま出力')
    ap.add_argument('--list', dest='do_list', action='store_true',
                    help='全 slug を一覧（slug を部分一致の絞り込みに使える）')
    args = ap.parse_args(argv)

    page_keys = en_content.load_en_page_keys()
    if args.do_list:
        list_slugs(page_keys, needle=args.slug)
        return 0
    if not args.slug:
        ap.error('slug を指定するか --list を使ってください')

    slug, candidates = en_content.resolve_slug(args.slug, page_keys)
    if slug is None:
        if candidates:
            print('slug が一意に決まりません: %s' % args.slug, file=sys.stderr)
            print('候補:', ', '.join(key[:-5] for key in candidates[:15]), file=sys.stderr)
        else:
            print('slug が見つかりません: %s' % args.slug, file=sys.stderr)
        return 2

    html = en_content.load_en_html(slug)
    if args.raw:
        print(html, end='')
        return 0
    if en_content.is_shim(slug):
        print('\033[1mEN HTML: %s\033[0m' % slug)
        print('shim -> %s' % (en_content.shim_target(slug) or '(target missing)'))
        return 0

    print('\033[1mEN HTML: %s\033[0m' % slug)
    return show_summary(en_content.extract_en_summary(html), only_field=args.field)


if __name__ == '__main__':
    sys.exit(main())
