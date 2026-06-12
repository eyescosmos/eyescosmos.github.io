#!/usr/bin/env python3
"""
check_photographers_en.py
=========================
Audit generated en/photographers/<slug>.html pages.

  python3 scripts/check_photographers_en.py [slug ...]

With no args, audits every en/photographers/*.html except jp-*.html redirect
stubs and *-backup.html. Prints PASS/FAIL per page with reasons.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN_DIR = os.path.join(ROOT, 'en', 'photographers')

CJK_RE = re.compile(r'[぀-ヿ㐀-䶿一-鿿豈-﫿]')


def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s)


def cjk_ratio(text):
    text = strip_tags(text).strip()
    if not text:
        return 0.0
    return len(CJK_RE.findall(text)) / max(1, len(text))


def file_exists(path):
    return os.path.exists(os.path.join(ROOT, path.lstrip('/')))


def audit(slug, html):
    fails = []

    # lang="en"
    if '<html lang="en">' not in html:
        fails.append('lang!=en')

    # GA
    if 'googletagmanager.com/gtag/js' not in html:
        fails.append('no GA')

    # canonical self URL
    cm = re.search(r'<link rel="canonical" href="([^"]+)">', html)
    expected = f'https://eyescosmos.github.io/en/photographers/{slug}.html'
    if not cm:
        fails.append('no canonical')
    elif cm.group(1) != expected:
        fails.append(f'canonical mismatch ({cm.group(1)})')

    # hreflang x3 + ja/en mutual consistency
    hl = dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">', html))
    for k in ('ja', 'en', 'x-default'):
        if k not in hl:
            fails.append(f'missing hreflang {k}')
    if hl.get('en') and hl['en'] != expected:
        fails.append('hreflang en != self')
    if hl.get('ja') and '/photographers/' not in hl['ja']:
        fails.append('hreflang ja malformed')

    # exactly one h1
    h1s = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.S)
    if len(h1s) != 1:
        fails.append(f'h1 count={len(h1s)}')
    elif CJK_RE.search(strip_tags(h1s[0])):
        fails.append('h1 contains CJK')

    # CJK ratio in .essay bodies
    for bm in re.finditer(r'<div class="essay"[^>]*>(.*?)</div>\s*</div>', html, re.S):
        r = cjk_ratio(bm.group(1))
        if r >= 0.05:
            fails.append(f'essay CJK ratio {r:.2f}')
            break
    # CJK ratio in the .ph-abstract prose (its <p>, which holds the translated
    # text — avoid over-capturing downstream blocks via greedy div matching)
    for am in re.finditer(r'<div class="ph-abstract"[^>]*>(.*?)</div>', html, re.S):
        pm = re.search(r'<p[^>]*>(.*?)</p>', am.group(1), re.S)
        if pm and cjk_ratio(pm.group(1)) >= 0.05:
            fails.append(f'ph-abstract CJK ratio {cjk_ratio(pm.group(1)):.2f}')
            break

    # sup-ref → cite-N exist
    cite_ids = set(re.findall(r'id="cite-(\d+)"', html))
    dup = [c for c in cite_ids if html.count(f'id="cite-{c}"') > 1]
    if dup:
        fails.append(f'duplicate cite ids {sorted(dup)}')
    sup_targets = re.findall(r'<sup class="sup-ref"><a href="#cite-(\d+)">', html)
    for t in sup_targets:
        if t not in cite_ids:
            fails.append(f'sup-ref→missing cite-{t}')
            break

    # TOC anchors exist
    toc_anchors = re.findall(r'href="#(sec-\d+|h3-\d+)"', html)
    id_set = set(re.findall(r'id="(sec-\d+|h3-\d+)"', html))
    for a in toc_anchors:
        if a not in id_set:
            fails.append(f'TOC anchor #{a} missing')
            break

    # no relative ../ internal links remain
    if re.search(r'href="\.\./', html):
        rels = re.findall(r'href="(\.\./[^"]+)"', html)
        fails.append(f'relative ../ links remain ({rels[0]})')

    # /en/... links exist on disk
    for href in re.findall(r'href="(/en/[^"#?]+\.html)', html):
        if not file_exists(href):
            fails.append(f'/en link missing: {href}')
            break
    # /... JA internal links exist on disk
    for href in re.findall(r'href="(/(?:photographers|movements|eras|countries)/[^"#?]+\.html)', html):
        # decode percent for filesystem check
        import urllib.parse
        decoded = urllib.parse.unquote(href)
        if not file_exists(decoded):
            fails.append(f'JA link missing: {href}')
            break

    # data-nosnippet on chrome
    if '<header class="head" data-nosnippet>' not in html:
        fails.append('header missing data-nosnippet')
    if '<aside class="ph-side" data-nosnippet>' not in html:
        fails.append('sidebar missing data-nosnippet')
    if '<footer class="foot" data-nosnippet>' not in html:
        fails.append('footer missing data-nosnippet')

    # section/div balance
    if html.count('<section') != html.count('</section>'):
        fails.append(f'section imbalance {html.count("<section")}/{html.count("</section>")}')
    if html.count('<div') != html.count('</div>'):
        fails.append(f'div imbalance {html.count("<div")}/{html.count("</div>")}')

    # file size
    if len(html.encode('utf-8')) <= 40 * 1024:
        fails.append('size <= 40KB')

    # ── NEW: head must be CJK-free in title / description / og:* / twitter:* ──
    head_m = re.search(r'<head\b[^>]*>(.*?)</head>', html, re.S | re.I)
    head = head_m.group(1) if head_m else ''

    tm = re.search(r'<title>(.*?)</title>', head, re.S | re.I)
    if tm and CJK_RE.search(tm.group(1)):
        fails.append('title contains CJK')

    dm = re.search(r'<meta name="description" content="([^"]*)"', head, re.I)
    if dm and CJK_RE.search(dm.group(1)):
        fails.append('meta description contains CJK')

    og_contents = re.findall(r'<meta property="og:[^"]*" content="([^"]*)"', head, re.I)
    if any(CJK_RE.search(c) for c in og_contents):
        fails.append('og:* content contains CJK')
    tw_contents = re.findall(r'<meta name="twitter:[^"]*" content="([^"]*)"', head, re.I)
    if any(CJK_RE.search(c) for c in tw_contents):
        fails.append('twitter:* content contains CJK')

    # ── NEW: exactly one og:title / og:description / twitter:title ──
    for prop, pat in (
        ('og:title', r'<meta property="og:title"'),
        ('og:description', r'<meta property="og:description"'),
        ('twitter:title', r'<meta name="twitter:title"'),
    ):
        n = len(re.findall(pat, html))
        if n != 1:
            fails.append(f'{prop} count={n}')

    # ── NEW: every JSON-LD block parses and is CJK-free in name/description ──
    # A leaked JA block carries a string-valued JA "name"/"description" (and a
    # string JA "alternateName"); those FAIL. The EN harvest's own Person object
    # legitimately lists the native-script name inside an alternateName *array*
    # alongside the romaji name — that array form is intentional and allowed.
    for jm in re.finditer(r'<script type="application/ld\+json">(.*?)</script>',
                          html, re.S | re.I):
        raw = jm.group(1).strip()
        try:
            data = json.loads(raw)
        except Exception as e:
            fails.append(f'jsonld parse error: {type(e).__name__}')
            continue
        blocks = data if isinstance(data, list) else [data]
        bad = False
        for b in blocks:
            if not isinstance(b, dict):
                continue
            for key in ('name', 'description', 'alternateName'):
                v = b.get(key)
                if isinstance(v, str) and CJK_RE.search(v):
                    bad = True
        if bad:
            fails.append('jsonld contains CJK in name/description/alternateName')
            break

    # ── NEW: no ph-section__name contains CJK ──
    for snm in re.findall(r'<span class="ph-section__name">(.*?)</span>', html, re.S):
        if CJK_RE.search(strip_tags(snm)):
            fails.append('ph-section__name contains CJK')
            break

    # ── NEW: ph-rel-list items contain no CJK run of 3+ chars ──
    for lm in re.finditer(r'<ul class="ph-rel-list[^"]*">(.*?)</ul>', html, re.S):
        text = strip_tags(lm.group(1))
        if re.search(r'[぀-ヿ㐀-䶿一-鿿豈-﫿]{3,}', text):
            fails.append('ph-rel-list item has CJK run 3+')
            break

    # ── NEW: zero visible CJK (text nodes only) outside ph-hero__en ──
    vis = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.S | re.I)
    vis = re.sub(r'<script\b[^>]*>.*?</script>', '', vis, flags=re.S | re.I)
    # drop the allowed native-script name element
    vis = re.sub(r'<div class="ph-hero__en">.*?</div>', '', vis, flags=re.S)
    # remove all tags (incl. attribute values) leaving only text nodes
    vis = re.sub(r'<[^>]+>', '', vis)
    runs = re.findall(r'[぀-ヿ㐀-䶿一-鿿豈-﫿][぀-ヿ㐀-䶿一-鿿豈-﫿\sぁ-ゟ・＝／]*', vis)
    runs = [r.strip() for r in runs if r.strip()]
    if runs:
        fails.append('visible CJK: ' + '; '.join(runs[:5]))

    return fails


def main():
    args = sys.argv[1:]
    if args:
        files = []
        for a in args:
            fn = a if a.endswith('.html') else a + '.html'
            files.append(fn)
    else:
        files = []
        for fn in sorted(os.listdir(EN_DIR)):
            if not fn.endswith('.html'):
                continue
            if fn.startswith('jp-') or fn.endswith('-backup.html'):
                continue
            files.append(fn)

    total = 0
    passed = 0
    for fn in files:
        path = os.path.join(EN_DIR, fn)
        if not os.path.exists(path):
            print(f'FAIL {fn}: file not found')
            continue
        html = open(path, encoding='utf-8').read()
        total += 1
        fails = audit(fn[:-5], html)
        if fails:
            print(f'FAIL {fn}: ' + '; '.join(fails))
        else:
            passed += 1
            print(f'PASS {fn}')
    print(f'\n{passed}/{total} passed')


if __name__ == '__main__':
    main()
