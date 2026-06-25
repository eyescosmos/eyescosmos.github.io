#!/usr/bin/env python3
"""Keep EN §REL one-line annotations (related_annotations) in sync with the JA §REL.

Background
----------
EN photographer pages render the §REL "Related photographers / movements" links
from ``site_directory_html`` in ``data/photographers-en-content.json`` (bare
links, owned by the era-batch §REL workflow). The one-line English blurb on each
link comes from a separate, optional per-page field ``related_annotations``
( href -> English HTML ), consumed by ``build_photographers_en.rebuild_related``.

The JA page is the source of the blurb: each visible §REL item is
``<li><a href=...>name</a> ― one sentence.</li>``. This tool aligns the JA
blurbs with the EN links and reports / scaffolds / writes the EN field, so the
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
                          blurb but related_annotations is missing it. Exit 1 if
                          any gap, for preflight wiring. ``--slug``/``--files``
                          narrow the scope (touched-only).
  --emit-worklist --slug X [--slug Y ...]
                          print JSON [{slug, en_href, name_en, desc_ja}, ...] of
                          items needing an English blurb (translation input).
  --apply --slug X --from FILE
                          FILE = JSON { en_href: "English HTML blurb", ... }.
                          Write those into related_annotations for slug X
                          (additive; asserts no other JSON bytes change besides
                          the inserted field). Re-run build separately.
"""
import argparse
import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(ROOT, 'data', 'photographers-en-content.json')
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
    """Return {'people': [(href,name),...], 'movements': [...]} in order."""
    groups = {'people': [], 'movements': []}
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
            groups[key].append((am.group(1), am.group(2)))
    return groups


def page_alignment(slug, entry):
    """Yield (status, en_href, name_en, desc_ja) for one page.
    status in {'have','need','review'}."""
    ja_path = os.path.join(JA_DIR, slug + '.html')
    if not os.path.exists(ja_path):
        return [('review', None, None, 'no JA page %s' % ja_path)]
    ja_html = open(ja_path, encoding='utf-8').read()
    ja = ja_rel_groups(ja_html)
    en = en_dir_groups(entry.get('site_directory_html') or '')
    ann = entry.get('related_annotations') or {}
    rows = []
    for key in ('people', 'movements'):
        ja_linked = [x for x in ja[key] if x['ja_href']]
        en_items = en[key]
        if len(ja_linked) != len(en_items):
            rows.append(('review', None, None,
                         '%s group: JA linked=%d EN=%d (count mismatch)'
                         % (key, len(ja_linked), len(en_items))))
            continue
        for jx, (href, name_en) in zip(ja_linked, en_items):
            if not jx['desc_ja']:
                continue  # JA item has no blurb -> nothing to sync
            status = 'have' if href in ann else 'need'
            rows.append((status, href, name_en, jx['desc_ja']))
    return rows


def load_pages():
    return json.load(open(JSON_PATH, encoding='utf-8'))


def slugs_from_args(args, pages):
    if args.slug:
        return [s for s in args.slug]
    if args.files:
        out = []
        for f in args.files:
            base = os.path.basename(f)
            base = re.sub(r'\.html$', '', base)
            if base + '.html' in pages['pages']:
                out.append(base)
        return out
    return [k[:-5] for k in pages['pages'].keys()]  # strip .html


def cmd_audit(args):
    pages = load_pages()
    total_need = 0
    total_review = 0
    affected = []
    for slug in slugs_from_args(args, pages):
        entry = pages['pages'].get(slug + '.html')
        if not entry:
            continue
        rows = page_alignment(slug, entry)
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
    pages = load_pages()
    work = []
    for slug in slugs_from_args(args, pages):
        entry = pages['pages'].get(slug + '.html')
        if not entry:
            continue
        for status, href, name_en, desc_ja in page_alignment(slug, entry):
            if status == 'need':
                work.append({'slug': slug, 'en_href': href,
                             'name_en': name_en, 'desc_ja': desc_ja})
    print(json.dumps(work, ensure_ascii=False, indent=2))
    return 0


def _apply_to_entry(entry, translations):
    """Return a new OrderedDict entry with related_annotations merged
    (additive), placed right after site_directory_html. Validates hrefs."""
    valid = {h for grp in en_dir_groups(entry.get('site_directory_html') or '').values()
             for (h, _) in grp}
    bad = set(translations) - valid
    if bad:
        raise ValueError('hrefs not in site_directory_html: %s' % sorted(bad))
    existing = collections.OrderedDict(entry.get('related_annotations') or {})
    for h, blurb in translations.items():
        existing[h] = blurb
    new_entry = collections.OrderedDict()
    placed = False
    for k, v in entry.items():
        if k == 'related_annotations':
            continue
        new_entry[k] = v
        if k == 'site_directory_html':
            new_entry['related_annotations'] = existing
            placed = True
    if not placed:
        new_entry['related_annotations'] = existing
    return new_entry


def _write_pages(data, raw):
    out = json.dumps(data, ensure_ascii=False, indent=2)
    if raw.endswith('\n'):
        out += '\n'
    tmp = JSON_PATH + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fh:
        fh.write(out)
    os.replace(tmp, JSON_PATH)


def cmd_apply(args):
    if not args.slug or len(args.slug) != 1:
        sys.exit('--apply requires exactly one --slug')
    if not args.from_file:
        sys.exit('--apply requires --from FILE')
    slug = args.slug[0]
    translations = json.load(open(args.from_file, encoding='utf-8'))
    if not isinstance(translations, dict) or not translations:
        sys.exit('--from FILE must be a non-empty {en_href: blurb} object')

    raw = open(JSON_PATH, encoding='utf-8').read()
    data = json.loads(raw, object_pairs_hook=collections.OrderedDict)
    key = slug + '.html'
    if key not in data['pages']:
        sys.exit('unknown slug: %s' % slug)
    try:
        data['pages'][key] = _apply_to_entry(data['pages'][key], translations)
    except ValueError as e:
        sys.exit('%s: %s' % (slug, e))
    _write_pages(data, raw)
    print('applied %d blurb(s) to %s' % (len(translations), slug))
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
    """Inject related_annotations into the live EN HTML §REL <li> directly,
    without a full rebuild. --slug narrows scope; default = all pages that
    carry related_annotations."""
    pages = load_pages()['pages']
    targets = ([s + '.html' for s in args.slug] if args.slug
               else list(pages.keys()))
    total = 0
    touched = 0
    for key in targets:
        entry = pages.get(key)
        if not entry:
            continue
        ann = entry.get('related_annotations') or {}
        if not ann:
            continue
        slug = key[:-5]
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


def cmd_apply_batch(args):
    """--from FILE = { "<slug>": { "<en_href>": "blurb", ... }, ... }"""
    if not args.from_file:
        sys.exit('--apply-batch requires --from FILE')
    batch = json.load(open(args.from_file, encoding='utf-8'))
    if not isinstance(batch, dict) or not batch:
        sys.exit('--from FILE must be a non-empty {slug: {href: blurb}} object')

    raw = open(JSON_PATH, encoding='utf-8').read()
    data = json.loads(raw, object_pairs_hook=collections.OrderedDict)
    total = 0
    for slug, translations in batch.items():
        key = slug + '.html'
        if key not in data['pages']:
            sys.exit('unknown slug: %s' % slug)
        if not translations:
            continue
        try:
            data['pages'][key] = _apply_to_entry(data['pages'][key], translations)
        except ValueError as e:
            sys.exit('%s: %s' % (slug, e))
        total += len(translations)
    _write_pages(data, raw)
    print('applied %d blurb(s) across %d page(s)' % (total, len(batch)))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--audit', action='store_true')
    ap.add_argument('--emit-worklist', action='store_true')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--apply-batch', action='store_true')
    ap.add_argument('--inject-html', action='store_true')
    ap.add_argument('--slug', action='append')
    ap.add_argument('--files', nargs='*')
    ap.add_argument('--from', dest='from_file')
    args = ap.parse_args()
    if args.emit_worklist:
        sys.exit(cmd_emit_worklist(args))
    if args.apply_batch:
        sys.exit(cmd_apply_batch(args))
    if args.inject_html:
        sys.exit(cmd_inject_html(args))
    if args.apply:
        sys.exit(cmd_apply(args))
    sys.exit(cmd_audit(args))


if __name__ == '__main__':
    main()
