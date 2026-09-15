#!/usr/bin/env python3
"""Keep EN §REL one-line annotations in sync with the JA §REL.

Background
----------
EN photographer pages store the §REL "Related photographers / movements" links
and their optional one-line English blurbs directly in EN HTML.

The JA page is the source of the blurb: each visible §REL item is
``<li><a href=...>name</a> ― one sentence.</li>``. This tool aligns the JA
blurbs with the EN links and reports / scaffolds / writes the EN HTML, so the
EN annotations never silently drift behind the JA §REL.

Alignment
---------
Links are matched **per group, in order, among linked JA items** — NOT by global
position (a JA §REL may list unlinked items the EN directory drops, e.g.
jikei-sato lists 10 but links 3). People and movements are aligned separately.
Count mismatches per group are reported as ``REVIEW`` rather than guessed.

Modes
-----
  --audit                 (default) report every EN page whose JA §REL has a
                          blurb but the EN HTML annotation is missing it. Exit 1 if
                          any gap, for preflight wiring. ``--slug``/``--files``
                          narrow the scope (touched-only).
  --emit-worklist --slug X [--slug Y ...]
                          print JSON [{slug, en_href, name_en, desc_ja}, ...] of
                          items needing an English blurb (translation input).
  --inject-html --slug X --from FILE
                          FILE = JSON { en_href: "English HTML blurb", ... }.
                          Add those blurbs directly to slug X's EN §REL.

"""
import argparse
import json
import os
from urllib.parse import unquote, urlparse
import re
import sys

import en_content

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JA_DIR = os.path.join(ROOT, 'photographers')

DASH = re.compile(r'\s*[―—–\-]\s+')  # name ― desc  (require trailing space to avoid hyphenated names)


def _strip_tags(s):
    return re.sub(r'<[^>]+>', '', s)


def ja_rel_groups(ja_html):
    """Return {'people': [...], 'movements': [...]} of dicts
    {ja_href, name_ja, desc_ja} in document order, linked or not."""
    groups = {'people': [], 'movements': []}
    for m in re.finditer(r'<ul class="ph-rel-list([^"]*)">(.*?)</ul>', ja_html, re.S):
        key = 'movements' if 'ph-rel-movements' in m.group(1) else 'people'
        for li in re.findall(r'<li>(.*?)</li>', m.group(2), re.S):
            a = re.search(r'<a href="([^"]+)">([^<]+)</a>', li)
            txt = _strip_tags(li).strip()
            parts = DASH.split(txt, maxsplit=1)
            name = parts[0].strip()
            desc = parts[1].strip() if len(parts) > 1 else ''
            groups[key].append({
                'ja_href': a.group(1) if a else None,
                'name_ja': name,
                'desc_ja': desc,
            })
    return groups


def en_dir_groups(site_directory_html):
    """Return {'people': [(href,name,blurb),...], 'movements': [...]} in order.

    Current EN HTML ``ph-rel-list`` blocks are canonical. The legacy
    ``site-directory-group`` form remains readable for older HTML compatibility.
    """
    groups = {'people': [], 'movements': []}
    for gm in re.finditer(r'<ul class="ph-rel-list([^"]*)">(.*?)</ul>',
                          site_directory_html, re.S):
        key = 'movements' if 'ph-rel-movements' in gm.group(1) else 'people'
        for li in re.findall(r'<li>(.*?)</li>', gm.group(2), re.S):
            am = re.search(r'<a href="([^"]+)">([^<]+)</a>', li)
            if not am:
                continue
            tail = li[am.end():]
            dash = re.match(r'\s*(?:&mdash;|&#8212;|&#x2014;|[―—–-])\s*(.*)',
                            tail, re.S | re.I)
            blurb = _strip_tags(dash.group(1)).strip() if dash else ''
            groups[key].append((am.group(1), am.group(2), blurb))
    if any(groups.values()):
        return groups

    for gm in re.finditer(
            r'<div class="site-directory-group site-directory-group-contextual">(.*?)</div>\s*</div>',
            site_directory_html, re.S):
        group = gm.group(1)
        lm = re.search(r'<div class="site-directory-label">([^<]+)</div>', group)
        if not lm:
            continue
        label = lm.group(1).strip().lower()
        key = 'movements' if 'movement' in label else 'people'
        for am in re.finditer(r'<a href="([^"]+)">([^<]+)</a>', group):
            groups[key].append((am.group(1), am.group(2), ''))
    return groups


def ja_file_for(slug, en_html):
    """EN ページに対応する JA ファイル名を EN HTML 自身の hreflang="ja" から引く。

    jp-漢字 slug（例 ihei-kimura ↔ jp-木村伊兵衛.html）は slug 名が一致しないので、
    `<slug>.html` 決め打ちだと JA ページを見失う。EN 402枚すべてが hreflang="ja" を
    持つので、レジストリ（classification.json）ではなく HTML 自身を正本にする。
    """
    m = re.search(r'hreflang="ja"\s+href="([^"]+)"', en_html)
    if m:
        name = unquote(os.path.basename(urlparse(m.group(1)).path))
        if name.endswith('.html'):
            return name
    return slug + '.html'


def page_alignment(slug, en_html):
    """Yield (status, en_href, name_en, desc_ja) for one page.
    status in {'have','need','review'}."""
    ja_path = os.path.join(JA_DIR, ja_file_for(slug, en_html))
    if not os.path.exists(ja_path):
        return [('review', None, None, 'no JA page %s' % ja_path)]
    ja_html = open(ja_path, encoding='utf-8').read()
    ja = ja_rel_groups(ja_html)
    en = en_dir_groups(en_html)
    rows = []
    for key in ('people', 'movements'):
        ja_linked = [x for x in ja[key] if x['ja_href']]
        en_items = en[key]
        if len(ja_linked) != len(en_items):
            rows.append(('review', None, None,
                         '%s group: JA linked=%d EN=%d (count mismatch)'
                         % (key, len(ja_linked), len(en_items))))
            continue
        for jx, (href, name_en, blurb_en) in zip(ja_linked, en_items):
            if not jx['desc_ja']:
                continue  # JA item has no blurb -> nothing to sync
            status = 'have' if blurb_en else 'need'
            rows.append((status, href, name_en, jx['desc_ja']))
    return rows


def slugs_from_args(args, page_keys):
    real_keys = {key for key in page_keys if not en_content.is_shim(key)}
    if args.slug:
        requested = [s if s.endswith('.html') else s + '.html' for s in args.slug]
        return [s[:-5] for s in requested if s in real_keys]
    if args.files:
        out = []
        for f in args.files:
            base = os.path.basename(f)
            base = re.sub(r'\.html$', '', base)
            if base + '.html' in real_keys:
                out.append(base)
        return out
    return [k[:-5] for k in page_keys if k in real_keys]


def cmd_audit(args):
    page_keys = en_content.load_en_page_keys()
    total_need = 0
    total_review = 0
    affected = []
    for slug in slugs_from_args(args, page_keys):
        rows = page_alignment(slug, en_content.load_en_html(slug + '.html'))
        need = [r for r in rows if r[0] == 'need']
        review = [r for r in rows if r[0] == 'review']
        if need or review:
            affected.append((slug, len(need), len(review), review))
            total_need += len(need)
            total_review += len(review)
    for slug, n, rv, review in sorted(affected, key=lambda x: -x[1]):
        msg = '  %-40s need=%d' % (slug, n)
        if rv:
            msg += '  REVIEW=%d (%s)' % (rv, '; '.join(r[3] for r in review))
        print(msg)
    print('---')
    print('pages affected: %d | EN blurbs missing: %d | review items: %d'
          % (len(affected), total_need, total_review))
    return 1 if (total_need or total_review) else 0


def cmd_emit_worklist(args):
    page_keys = en_content.load_en_page_keys()
    work = []
    for slug in slugs_from_args(args, page_keys):
        en_html = en_content.load_en_html(slug + '.html')
        for status, href, name_en, desc_ja in page_alignment(slug, en_html):
            if status == 'need':
                work.append({'slug': slug, 'en_href': href,
                             'name_en': name_en, 'desc_ja': desc_ja})
    print(json.dumps(work, ensure_ascii=False, indent=2))
    return 0


EN_DIR = os.path.join(ROOT, 'en', 'photographers')


def inject_html_for_slug(slug, annotations):
    """Surgically add ' &mdash; blurb' to the §REL bare <li> links of the EN
    HTML, editing only those lines. Used for older pages where a full builder
    rebuild would drift unrelated markup (e.g. regress dual-nationality country
    chips back to Japanese). Returns (changed:int, html or None)."""
    path = os.path.join(EN_DIR, slug + '.html')
    if not os.path.exists(path):
        return (0, None)
    html = open(path, encoding='utf-8').read()
    # restrict edits to the §REL ph-rel-list <ul> blocks
    changed = [0]

    def repl_ul(m):
        block = m.group(0)

        def repl_li(lm):
            href, name = lm.group('href'), lm.group('name')
            blurb = annotations.get(href)
            if not blurb:
                return lm.group(0)
            if '&mdash;' in lm.group(0) or '—' in lm.group(0):
                return lm.group(0)  # already annotated
            changed[0] += 1
            return ('<li><a href="%s">%s</a> &mdash; %s</li>'
                    % (href, name, blurb))

        return re.sub(
            r'<li><a href="(?P<href>[^"]+)">(?P<name>[^<]+)</a></li>',
            repl_li, block)

    new_html = re.sub(r'<ul class="ph-rel-list[^"]*">.*?</ul>',
                      repl_ul, html, flags=re.S)
    if changed[0] == 0:
        return (0, None)
    return (changed[0], new_html)


def cmd_inject_html(args):
    """Inject supplied annotations into live EN HTML §REL without a rebuild."""
    if not args.from_file:
        sys.exit('--inject-html requires --from FILE')
    supplied = json.load(open(args.from_file, encoding='utf-8'))
    if not isinstance(supplied, dict) or not supplied:
        sys.exit('--from FILE must be a non-empty annotation object')
    if args.slug and len(args.slug) == 1 and all(isinstance(v, str) for v in supplied.values()):
        batch = {args.slug[0].removesuffix('.html'): supplied}
    elif all(isinstance(v, dict) for v in supplied.values()):
        batch = {slug.removesuffix('.html'): value for slug, value in supplied.items()}
    else:
        sys.exit('--from FILE must be {href: blurb} with one --slug, or {slug: {href: blurb}}')
    wanted = {slug.removesuffix('.html') for slug in (args.slug or batch)}
    total = 0
    touched = 0
    for slug, ann in batch.items():
        if slug not in wanted:
            continue
        if not ann:
            continue
        n, new_html = inject_html_for_slug(slug, ann)
        if n and new_html is not None:
            tmp = os.path.join(EN_DIR, slug + '.html.tmp')
            with open(tmp, 'w', encoding='utf-8') as fh:
                fh.write(new_html)
            os.replace(tmp, os.path.join(EN_DIR, slug + '.html'))
            total += n
            touched += 1
    print('injected %d blurb(s) into %d page(s)' % (total, touched))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--audit', action='store_true')
    ap.add_argument('--emit-worklist', action='store_true')
    ap.add_argument('--inject-html', action='store_true')
    ap.add_argument('--slug', action='append')
    ap.add_argument('--files', nargs='*')
    ap.add_argument('--from', dest='from_file')
    args = ap.parse_args()
    if args.emit_worklist:
        sys.exit(cmd_emit_worklist(args))
    if args.inject_html:
        sys.exit(cmd_inject_html(args))
    sys.exit(cmd_audit(args))


if __name__ == '__main__':
    main()
