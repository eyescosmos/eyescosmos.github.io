#!/usr/bin/env python3
"""
build_photographers_en.py
=========================
Stage 2/3 — Photographer-page Englishization.

Rebuild en/photographers/<slug>.html using the v5.1 Japanese pages
(photographers/*.html) as structural templates and injecting harvested
English content from data/photographers-en-content.json.

Idempotent overwrite generator. Python 3 stdlib only.

  python3 scripts/build_photographers_en.py --pilot
  python3 scripts/build_photographers_en.py --slug ansel-adams [--slug ...]
  python3 scripts/build_photographers_en.py --all

Never imports/runs scripts/generate_photographer_pages.py.
Never modifies photographers/ (JA pages are read-only).
Never touches en/photographers/jp-*.html or stieglitz-backup.html.
"""

import argparse
import html as htmllib
import json
import os
import re
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

# Reuse tables from the taxonomy builder (import has no side effects; main-guarded)
from build_taxonomy_en import (  # noqa: E402
    STUB_TO_SLUG,
    SLUG_TO_STUB,
    SLUG_TO_EN_NAME,
    FALLBACK_COUNTRY_EN,
)

CONTENT_JSON = os.path.join(ROOT, 'data', 'photographers-en-content.json')
CLASSIFICATION_JSON = os.path.join(ROOT, 'data', 'photographers-en-classification.json')
JA_DIR = os.path.join(ROOT, 'photographers')
EN_DIR = os.path.join(ROOT, 'en', 'photographers')

BASE = 'https://eyescosmos.github.io'

# ── JA country name → EN display name (slug comes from the JA href) ────────
COUNTRY_JA_TO_EN = {
    '日本': 'Japan',
    'アメリカ': 'United States',
    'ドイツ': 'Germany',
    'オランダ': 'Netherlands',
    'カナダ': 'Canada',
    '南アフリカ': 'South Africa',
    'ウクライナ': 'Ukraine',
    'イギリス': 'United Kingdom',
    'フランス': 'France',
    'イタリア': 'Italy',
    'スペイン': 'Spain',
    'オーストリア': 'Austria',
    'ベルギー': 'Belgium',
    'スイス': 'Switzerland',
    'スウェーデン': 'Sweden',
    'ロシア': 'Russia',
    'ハンガリー': 'Hungary',
    'ポーランド': 'Poland',
    'チェコ': 'Czech Republic',
    'ブラジル': 'Brazil',
    'メキシコ': 'Mexico',
    'オーストラリア': 'Australia',
    '中国': 'China',
    '韓国': 'South Korea',
    'インド': 'India',
}

PILOT_SLUGS = ['ansel-adams', 'moriyama', 'jp-植田正治', 'alexander-gardner', 'aglaia-konrad']

CJK_RE = re.compile(r'[぀-ヿ㐀-䶿一-鿿豈-﫿]')


# ── balanced-tag extraction helper (depth-counting, no naive regex) ───────
def extract_balanced(html, start_idx, tag):
    """Return (inner_html, end_index_after_close) for the element whose opening
    tag begins at start_idx. start_idx must point at '<tag'. Handles nesting."""
    open_re = re.compile(r'<' + tag + r'(?:\s[^>]*)?>', re.I)
    close_tag = '</' + tag + '>'
    m = open_re.match(html, start_idx)
    if not m:
        # start_idx might be at the '<' but with attributes spanning; fall back
        m = open_re.search(html, start_idx)
        if not m or m.start() != start_idx:
            raise ValueError('no opening tag at index for <%s>' % tag)
    pos = m.end()
    depth = 1
    token_re = re.compile(r'<' + tag + r'(?:\s[^>]*)?>|</' + tag + r'>', re.I)
    while depth > 0:
        t = token_re.search(html, pos)
        if not t:
            raise ValueError('unbalanced <%s>' % tag)
        if t.group(0).lower().startswith(close_tag.lower()):
            depth -= 1
            pos = t.end()
        else:
            depth += 1
            pos = t.end()
    inner = html[m.end():pos - len(close_tag)]
    return inner, pos, m.start()


def find_element(html, tag, attr_substr):
    """Find the first <tag ...attr_substr...> and return (full_outer, start, end).
    attr_substr is a literal substring expected within the opening tag."""
    open_re = re.compile(r'<' + tag + r'(?:\s[^>]*)?>', re.I)
    for m in open_re.finditer(html):
        if attr_substr in m.group(0):
            inner, end, start = extract_balanced(html, m.start(), tag)
            return html[start:end], start, end, inner
    return None


# ── small helpers ─────────────────────────────────────────────────────────
def esc(t):
    return (t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def unesc(t):
    return htmllib.unescape(t)


def attr_esc(t):
    return (t.replace('&', '&amp;').replace('"', '&quot;')
             .replace('<', '&lt;').replace('>', '&gt;'))


def cjk_ratio(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = text.strip()
    if not text:
        return 0.0
    cjk = len(CJK_RE.findall(text))
    return cjk / max(1, len(text))


def en_page_exists(slug):
    return os.path.exists(os.path.join(EN_DIR, slug + '.html'))


def en_country_exists(slug):
    return os.path.exists(os.path.join(ROOT, 'en', 'countries', slug + '.html'))


def en_movement_exists(slug):
    return os.path.exists(os.path.join(ROOT, 'en', 'movements', slug + '.html'))


def en_era_exists(era):
    return os.path.exists(os.path.join(ROOT, 'en', 'eras', era + '.html'))


def file_exists_rel(abs_path):
    return os.path.exists(abs_path)


# ── classification / slug mapping ─────────────────────────────────────────
def load_classification():
    return json.load(open(CLASSIFICATION_JSON, encoding='utf-8'))


def build_jp_slug_map(classification):
    """Return dicts:
       ja_file → en_file (for kanji-named JA files), and
       en_file → ja_file."""
    ja_to_en = {}
    en_to_ja = {}
    for en_file, info in classification.get('jp_slug_mapping', {}).items():
        ja_file = info['ja_file']
        ja_to_en[ja_file] = en_file
        en_to_ja[en_file] = ja_file
    return ja_to_en, en_to_ja


def ja_file_to_en_file(ja_file, ja_to_en):
    """photographers/<ja_file>.html → en output filename (no dir)."""
    if ja_file in ja_to_en:
        return ja_to_en[ja_file]
    return ja_file


# ── movement term translation (handles slash/dot inside name) ─────────────
def translate_movement_name(ja_name):
    ja_name = ja_name.strip()
    slug = STUB_TO_SLUG.get(ja_name)
    if slug:
        return SLUG_TO_EN_NAME.get(slug, ja_name), slug
    return ja_name, None


# ── HEAD rebuild ───────────────────────────────────────────────────────────
def build_head_meta(page, slug):
    en_url = f'{BASE}/en/photographers/{slug}.html'
    hreflang = page.get('hreflang') or {}
    ja_url = hreflang.get('ja') or f'{BASE}/photographers/{slug}.html'
    en_href = hreflang.get('en') or en_url
    xd = hreflang.get('x-default') or ja_url

    title = page.get('title') or page.get('h1', '')
    desc = page.get('meta_description') or ''
    og = page.get('og') or {}
    tw = page.get('twitter') or {}

    lines = []
    lines.append(f'<title>{esc(unesc(title))}</title>')
    if desc:
        lines.append(f'<meta name="description" content="{attr_esc(unesc(desc))}">')
    lines.append(f'<link rel="canonical" href="{en_url}">')
    lines.append('<meta name="robots" content="index, follow">')
    lines.append(f'<link rel="alternate" hreflang="ja" href="{ja_url}">')
    lines.append(f'<link rel="alternate" hreflang="en" href="{en_href}">')
    lines.append(f'<link rel="alternate" hreflang="x-default" href="{xd}">')
    # OG
    lines.append(f'<meta property="og:type" content="{attr_esc(og.get("type", "article"))}">')
    lines.append(f'<meta property="og:site_name" content="{attr_esc(og.get("site_name", "Photo Coordinates"))}">')
    lines.append(f'<meta property="og:title" content="{attr_esc(unesc(og.get("title", title)))}">')
    if og.get('description') or desc:
        lines.append(f'<meta property="og:description" content="{attr_esc(unesc(og.get("description", desc)))}">')
    lines.append(f'<meta property="og:url" content="{attr_esc(og.get("url", en_url))}">')
    lines.append(f'<meta property="og:locale" content="{attr_esc(og.get("locale", "en_US"))}">')
    if og.get('image'):
        lines.append(f'<meta property="og:image" content="{attr_esc(og["image"])}">')
        if og.get('image:width'):
            lines.append(f'<meta property="og:image:width" content="{attr_esc(og["image:width"])}">')
        if og.get('image:height'):
            lines.append(f'<meta property="og:image:height" content="{attr_esc(og["image:height"])}">')
        if og.get('image:alt'):
            lines.append(f'<meta property="og:image:alt" content="{attr_esc(og["image:alt"])}">')
    # Twitter
    lines.append(f'<meta name="twitter:card" content="{attr_esc(tw.get("card", "summary"))}">')
    lines.append(f'<meta name="twitter:title" content="{attr_esc(unesc(tw.get("title", title)))}">')
    if tw.get('description') or desc:
        lines.append(f'<meta name="twitter:description" content="{attr_esc(unesc(tw.get("description", desc)))}">')
    if tw.get('image'):
        lines.append(f'<meta name="twitter:image" content="{attr_esc(tw["image"])}">')
    # JSON-LD
    for block in (page.get('jsonld') or []):
        if isinstance(block, (dict, list)):
            txt = json.dumps(block, ensure_ascii=False, indent=2)
        else:
            txt = str(block)
        lines.append('<script type="application/ld+json">\n' + txt + '\n</script>')
    return '\n'.join(lines)


def replace_head(html, page, slug):
    """Strip the JA per-page meta tags (between viewport and the fonts link)
    and insert the EN meta block. Preserve charset/viewport/fonts/style/GA."""
    # Anchor 1: end of the viewport meta tag.
    vp = re.search(r'<meta name="viewport"[^>]*>', html)
    if not vp:
        raise ValueError('no viewport meta')
    head_open_end = vp.end()
    # Anchor 2: the fonts <link> (preconnect + stylesheet block start).
    fonts = re.search(r'<link rel="preconnect"', html)
    if not fonts or fonts.start() < head_open_end:
        raise ValueError('no fonts preconnect after viewport')
    new_block = '\n' + build_head_meta(page, slug) + '\n'
    return html[:head_open_end] + new_block + html[fonts.start():]


# ── EN readability style override (idempotent) ────────────────────────────
def insert_readability_style(html):
    marker = '.essay p,.ph-abstract p,.ph-thesis__body{text-align:left;}'
    if marker in html:
        return html
    style_close = html.find('</style>')
    if style_close == -1:
        return html
    insert = ('</style>\n<style>'
              '.essay p,.ph-abstract p,.ph-thesis__body{text-align:left;}'
              '</style>')
    return html[:style_close] + insert + html[style_close + len('</style>'):]


# ── HEADER (brand, crumbs, lang toggle, mobile search labels) ─────────────
def rebuild_header(html, page, slug, ja_file):
    # lang attr
    html = html.replace('<html lang="ja">', '<html lang="en">', 1)
    # brand link → /en/index.html
    html = html.replace('<a href="/index.html"><span class="head__brand-photo">写真</span>の座標</a>',
                        '<a href="/en/index.html"><span class="head__brand-photo">写真</span>の座標</a>')
    # crumbs
    html = rebuild_crumbs(html, page)
    # lang toggle: JP→JA page, EN active
    ja_path = '/photographers/' + urllib.parse.quote(ja_file)
    # mark with a sentinel so the link-localization pass leaves it pointing
    # at the JA page; the sentinel is stripped afterward.
    toggle = (f'<div class="head__lang">\n'
              f'      <a data-lang-toggle href="{ja_path}"><button>JP</button></a>\n'
              f'      <button class="is-active">EN</button>\n'
              f'    </div>')
    html = re.sub(r'<div class="head__lang">.*?</div>', toggle, html, count=1, flags=re.S)
    # mobile search labels
    html = html.replace('SEARCH · 写真家を探す', 'SEARCH · Find a photographer')
    html = html.replace('placeholder="写真家名・運動・キーワード"', 'placeholder="Name, movement, keyword"')
    html = html.replace('aria-label="検索"', 'aria-label="Search"')
    return html


def rebuild_crumbs(html, page):
    m = find_element(html, 'div', 'class="head__crumbs"')
    if not m:
        return html
    outer, start, end, inner = m
    # English name in uppercase
    en_name = (page.get('h1') or '').upper()
    # Extract trailing groups after the name: split on the sep spans
    # The JA crumbs look like: <em>PHOTOGRAPHERS</em><span class="sep">/</span>NAME ... · MOVEMENT ... · UPDATED ...
    # Rebuild from scratch using known parts.
    parts = ['<em>PHOTOGRAPHERS</em><span class="sep">/</span>' + esc(en_name)]
    # movement: from JA crumbs translate
    mv_match = re.findall(r'·\s*([^·<]+?)(?=\s*<span|\s*·|\s*$)', inner)
    # easier: pull movement & updated explicitly
    # Movement: any JA movement term present in STUB_TO_SLUG
    for ja_mv in sorted(STUB_TO_SLUG, key=len, reverse=True):
        if ja_mv in inner:
            en_mv, _ = translate_movement_name(ja_mv)
            parts.append(f'<span class="sep">·</span>{esc(en_mv)}')
            break
    # GROUP / CHANNEL token like GROUP F/64 (uppercase ascii) — keep if present
    up = re.search(r'·\s*([A-Z][A-Z0-9/ ]+?)\s*(?=<span class="sep">·</span>UPDATED|$)', inner)
    if up and 'UPDATED' not in up.group(1):
        token = up.group(1).strip()
        if token and not CJK_RE.search(token):
            parts.append(f'<span class="sep">·</span>{esc(token)}')
    # updated date
    upd = re.search(r'UPDATED&nbsp;<span class="updated-date">([^<]+)</span>', inner)
    if upd:
        parts.append(f'<span class="sep">·</span>UPDATED&nbsp;<span class="updated-date">{upd.group(1)}</span>')
    new_inner = '\n    ' + '\n    '.join(parts) + '\n  '
    new_outer = '<div class="head__crumbs">' + new_inner + '</div>'
    return html[:start] + new_outer + html[end:]


# ── HERO ───────────────────────────────────────────────────────────────────
def rebuild_hero(html, page):
    # eyebrow: translate trailing movement term
    eyem = find_element(html, 'div', 'class="ph-hero__eyebrow"')
    if eyem:
        outer, start, end, inner = eyem
        new_inner = inner
        for ja_mv in sorted(STUB_TO_SLUG, key=len, reverse=True):
            if ja_mv in new_inner:
                en_mv, _ = translate_movement_name(ja_mv)
                new_inner = new_inner.replace(ja_mv, en_mv)
                break
        html = html[:start] + '<div class="ph-hero__eyebrow">' + new_inner + '</div>' + html[end:]

    # h1 name = EN, capture JA name
    ja_name = None
    nm = find_element(html, 'h1', 'class="ph-hero__name"')
    if nm:
        outer, start, end, inner = nm
        ja_name = inner.strip()
        en_h1 = esc(page.get('h1', '').strip())
        html = html[:start] + f'<h1 class="ph-hero__name">{en_h1}</h1>' + html[end:]

    # ph-hero__en: replace EN text node with JA name, keep years span
    enm = find_element(html, 'div', 'class="ph-hero__en"')
    if enm and ja_name is not None:
        outer, start, end, inner = enm
        years_m = re.search(r'<span class="ph-hero__years">.*?</span>', inner, re.S)
        years = years_m.group(0) if years_m else ''
        new_inner = f'\n      {esc(ja_name)}\n      {years}\n    '
        html = html[:start] + '<div class="ph-hero__en">' + new_inner + '</div>' + html[end:]

    # meta-row: translate Country & Movement values, labels stay
    html = translate_meta_row(html, page)
    return html


def translate_meta_row(html, page):
    mr = find_element(html, 'div', 'class="ph-hero__meta-row"')
    if not mr:
        return html
    outer, start, end, inner = mr
    new_inner = translate_meta_values(inner)
    html = html[:start] + '<div class="ph-hero__meta-row">' + new_inner + '</div>' + html[end:]
    return html


def translate_meta_values(fragment):
    """Translate Country/Movement display values inside meta spans/dd cells.
    Country JA name → EN name; Movement JA term → EN term. Slugs/links handled
    by translate_internal_links later, plus en-existence link adjustments here."""
    # Country
    def repl_country(m):
        ja_country = m.group(1).strip()
        en_country = COUNTRY_JA_TO_EN.get(ja_country, ja_country)
        return m.group(0).replace('>' + ja_country + '<', '>' + en_country + '<')
    # Replace country display text where the country slug link present
    fragment = re.sub(
        r'href="(?:/|\.\./)?(?:en/)?countries/[^"]+\.html">([^<]+)</a>',
        lambda m: m.group(0).replace('>' + m.group(1) + '<', '>' + COUNTRY_JA_TO_EN.get(m.group(1).strip(), m.group(1)) + '<'),
        fragment)
    # Plain country in strong (hero meta-row Country<strong>日本</strong>)
    for ja_c, en_c in COUNTRY_JA_TO_EN.items():
        fragment = fragment.replace('<strong>' + ja_c + '</strong>', '<strong>' + en_c + '</strong>')
        fragment = fragment.replace('Country<strong>' + ja_c, 'Country<strong>' + en_c)
        # channel suffix " · JAPAN" stays as-is (already roman)
    # Movement terms — only translate visible text (between > and <), never
    # inside href slugs (link localization handles hrefs separately).
    for ja_mv in sorted(STUB_TO_SLUG, key=len, reverse=True):
        en_mv, _ = translate_movement_name(ja_mv)
        fragment = fragment.replace('>' + ja_mv + '<', '>' + en_mv + '<')
        fragment = fragment.replace('<strong>' + ja_mv + '</strong>',
                                    '<strong>' + en_mv + '</strong>')
    return fragment


# ── ABSTRACT ───────────────────────────────────────────────────────────────
def strip_lead_wrapper(lead_html):
    """Return inner of <p class="lead">…</p>."""
    m = re.search(r'<p class="lead">(.*)</p>\s*$', lead_html.strip(), re.S)
    if m:
        return m.group(1).strip()
    return lead_html.strip()


def rebuild_abstract(html, page):
    am = find_element(html, 'div', 'class="ph-abstract"')
    if not am:
        return html
    outer, start, end, inner = am
    lead = page.get('lead_html')
    if not lead:
        return html
    body = strip_lead_wrapper(lead)
    new_inner = (
        '\n        <div class="ph-abstract__label">Abstract</div>\n'
        f'        <p>{body}</p>\n      '
    )
    html = html[:start] + '<div class="ph-abstract">' + new_inner + '</div>' + html[end:]
    return html


# ── THESIS ───────────────────────────────────────────────────────────────
def rebuild_thesis(html, page):
    tm = find_element(html, 'div', 'class="ph-thesis"')
    if not tm:
        return html
    outer, start, end, inner = tm
    thesis = page.get('thesis_html')
    if not thesis:
        # remove the whole ph-thesis div (and surrounding blank line)
        before = html[:start].rstrip('\n ')
        after = html[end:]
        # drop a leading blank line in 'after'
        after = re.sub(r'^\s*\n', '\n', after)
        return before + '\n\n' + after.lstrip('\n')
    label = 'What this photographer changed'
    new_inner = (
        f'\n        <div class="ph-thesis__label">{label}</div>\n'
        f'        <p class="ph-thesis__body">{thesis}</p>\n      '
    )
    return html[:start] + '<div class="ph-thesis">' + new_inner + '</div>' + html[end:]


# ── ENTRY META ─────────────────────────────────────────────────────────────
def rebuild_entry_meta(html):
    """Translate Country/Movement/Period values + links inside ph-entry-meta."""
    em = find_element(html, 'dl', 'class="ph-entry-meta"')
    if not em:
        return html
    outer, start, end, inner = em
    new_inner = translate_meta_values(inner)
    return html[:start] + '<dl class="ph-entry-meta">' + new_inner + '</dl>' + html[end:]


# ── KEYWORDS (body + sidebar) ──────────────────────────────────────────────
def translate_keyword_movements(fragment):
    for ja_mv in sorted(STUB_TO_SLUG, key=len, reverse=True):
        if ja_mv in fragment:
            en_mv, _ = translate_movement_name(ja_mv)
            fragment = fragment.replace('>' + ja_mv + '<', '>' + en_mv + '<')
    return fragment


def rebuild_keywords(html):
    km = find_element(html, 'div', 'class="ph-keywords"')
    if km:
        outer, start, end, inner = km
        inner2 = inner.replace('<span class="ph-keywords__label">Keywords</span>',
                               '<span class="ph-keywords__label">Keywords</span>')
        inner2 = translate_keyword_movements(inner2)
        html = html[:start] + '<div class="ph-keywords">' + inner2 + '</div>' + html[end:]
    return html


# ── WORKS section ──────────────────────────────────────────────────────────
def rebuild_works(html, page):
    """Translate the WORKS section: title, note, and append harvest notable_works
    chip-links whose URL is not already present."""
    # Find the WORKS section by its § WORKS num token
    m = re.search(r'<span class="ph-section__name">作品を見る</span>', html)
    if m:
        html = html.replace('<span class="ph-section__name">作品を見る</span>',
                            '<span class="ph-section__name">View Works</span>', 1)
    note_ja = '本サイトでは作品画像を掲載していません。下記の公式アーカイブで作品をご覧ください。'
    note_en = ('This site does not display work images. '
               'Please visit the official archives below.')
    html = html.replace(note_ja, note_en)

    # Append notable works chips not already present
    nw = page.get('notable_works_html')
    if nw:
        wl = find_element(html, 'div', 'class="ph-works-links"')
        if wl:
            outer, start, end, inner = wl
            existing_urls = set(re.findall(r'href="([^"]+)"', inner))
            extra = []
            for am in re.finditer(r'<a class="chip-link"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', nw, re.S):
                url = am.group(1)
                if url not in existing_urls:
                    extra.append(am.group(0))
                    existing_urls.add(url)
            if extra:
                new_inner = inner.rstrip() + '\n            ' + '\n            '.join(extra) + '\n          '
                html = html[:start] + '<div class="ph-works-links">' + new_inner + '</div>' + html[end:]
    return html


# ── ESSAY SECTIONS + TOC ───────────────────────────────────────────────────
def build_essay_body(body_html, h3_counter):
    """Convert harvested body_html: ensure .essay wrapper, convert <h4> → <h3 id>.
    Returns (essay_html, list_of_(h3_id, h3_text))."""
    inner = body_html.strip()
    # unwrap an outer <div class="essay"> if present (we re-wrap uniformly)
    m = re.match(r'<div class="essay">(.*)</div>\s*$', inner, re.S)
    if m:
        inner = m.group(1)
    h3s = []

    def repl_h4(mm):
        text = mm.group(1)
        hid = 'h3-%02d' % h3_counter[0]
        h3_counter[0] += 1
        h3s.append((hid, text))
        return f'<h3 data-gen id="{hid}">{text}</h3>'

    inner = re.sub(r'<h4[^>]*>(.*?)</h4>', repl_h4, inner, flags=re.S)

    # Renumber any pre-existing harvest <h3> (without our data-gen marker).
    def repl_h3(mm):
        attrs = mm.group(1) or ''
        if 'data-gen' in attrs:
            return mm.group(0)  # already converted above
        text = mm.group(2)
        hid = 'h3-%02d' % h3_counter[0]
        h3_counter[0] += 1
        h3s.append((hid, text))
        return f'<h3 data-gen id="{hid}">{text}</h3>'
    inner = re.sub(r'<h3(\s[^>]*)?>(.*?)</h3>', repl_h3, inner, flags=re.S)

    # strip the temporary marker
    inner = inner.replace('<h3 data-gen id=', '<h3 id=')
    return '<div class="essay">' + inner + '</div>', h3s


def build_sections_and_toc(page):
    sections = page.get('sections') or []
    n = len(sections)
    h3_counter = [1]
    section_blocks = []
    toc_sections = []
    for i, sec in enumerate(sections, 1):
        sec_id = 'sec-%02d' % i
        title = unesc(sec.get('title', ''))
        num_label = '§ %02d / %02d' % (i, n)
        essay_html, h3s = build_essay_body(sec.get('body_html', ''), h3_counter)
        block = (
            f'      <!-- {sec_id} -->\n'
            f'      <section class="ph-section" id="{sec_id}">\n'
            f'        <div class="ph-section__head">\n'
            f'          <div class="ph-section__title">\n'
            f'            <span class="ph-section__num">{num_label}</span>\n'
            f'            <span class="ph-section__name">{esc(title)}</span>\n'
            f'          </div>\n'
            f'        </div>\n'
            f'        <div class="ph-section__body">\n'
            f'          {essay_html}\n'
            f'        </div>\n'
            f'      </section>'
        )
        section_blocks.append(block)
        toc_sections.append((sec_id, num_label_short(i), title, h3s))

    # Build TOC
    toc_items = []
    for idx, (sec_id, short_num, title, h3s) in enumerate(toc_sections):
        active = ' is-active' if idx == 0 else ''
        if h3s:
            subs = '\n'.join(
                f'                <li><a href="#{hid}">{htext}</a></li>'
                for hid, htext in h3s)
            item = (
                f'            <li class="toc-section{active}">\n'
                f'              <a href="#{sec_id}"><span class="toc-num">{short_num}</span> {esc(title)}</a>\n'
                f'              <ul class="toc-sub">\n{subs}\n              </ul>\n'
                f'            </li>')
        else:
            item = (
                f'            <li class="toc-section{active}"><a href="#{sec_id}">'
                f'<span class="toc-num">{short_num}</span> {esc(title)}</a></li>')
        toc_items.append(item)
    toc = (
        '      <details class="ph-toc">\n'
        '        <summary>Contents · Table of Contents</summary>\n'
        '        <div class="toc-body">\n'
        '          <ol class="toc-list">\n'
        + '\n'.join(toc_items) + '\n'
        '          </ol>\n'
        '        </div>\n'
        '      </details>'
    )
    return '\n\n'.join(section_blocks), toc


def num_label_short(i):
    return '§ %02d' % i


def replace_toc_and_sections(html, page):
    """Remove JA ph-toc + all id=sec-NN sections, insert EN-built ones."""
    sections_html, toc_html = build_sections_and_toc(page)

    # Remove existing ph-toc <details>
    tm = find_element(html, 'details', 'class="ph-toc"')
    if not tm:
        raise ValueError('no ph-toc found')
    t_outer, t_start, t_end, _ = tm

    # Find span of all sec-NN sections (contiguous run). Locate first & last.
    sec_starts = [mm.start() for mm in re.finditer(r'<section class="ph-section" id="sec-\d+">', html)]
    if not sec_starts:
        raise ValueError('no sec-NN sections found')
    first_sec = sec_starts[0]
    # end of last sec-NN section
    last_start = sec_starts[-1]
    _, last_end, _ = extract_balanced(html, last_start, 'section')

    # Sanity: the ph-toc precedes the first section
    if not (t_end <= first_sec):
        raise ValueError('ph-toc not before sections')

    new_segment = toc_html + '\n\n' + sections_html
    # Replace from toc start to last section end, preserving the comment lines
    # between toc and first section if any (there is a blank line / comment).
    return html[:t_start] + new_segment + html[last_end:]


# ── RELATED section ────────────────────────────────────────────────────────
def rebuild_related(html, page):
    relm = None
    m = re.search(r'<span class="ph-section__name">関連する写真家・運動</span>', html)
    sd = page.get('site_directory_html') or ''
    people = extract_directory_group(sd, 'Related people')
    movements = extract_directory_group(sd, 'Related movements')

    # locate RELATED section by its § REL token
    relnum = re.search(r'<span class="ph-section__num">§ REL</span>', html)
    if not relnum:
        return html
    # the section element containing this token
    sec_open = html.rfind('<section class="ph-section">', 0, relnum.start())
    if sec_open == -1:
        return html
    _, sec_end, _ = extract_balanced(html, sec_open, 'section')

    if not people and not movements:
        # remove the whole REL section
        return html[:sec_open].rstrip('\n ') + '\n\n' + html[sec_end:].lstrip('\n')

    body_parts = []
    if people:
        body_parts.append('          <div class="ph-rel-label">Related photographers</div>')
        body_parts.append('          <ul class="ph-rel-list">')
        for href, name in people:
            body_parts.append(f'            <li><a href="{href}">{name}</a></li>')
        body_parts.append('          </ul>')
    if movements:
        body_parts.append('          <div class="ph-rel-label">Related movements</div>')
        body_parts.append('          <ul class="ph-rel-list ph-rel-movements">')
        for href, name in movements:
            body_parts.append(f'            <li><a href="{href}">{name}</a></li>')
        body_parts.append('          </ul>')

    new_sec = (
        '      <!-- RELATED -->\n'
        '      <section class="ph-section">\n'
        '        <div class="ph-section__head">\n'
        '          <div class="ph-section__title">\n'
        '            <span class="ph-section__num">§ REL</span>\n'
        '            <span class="ph-section__name">Related photographers &amp; movements</span>\n'
        '          </div>\n'
        '        </div>\n'
        '        <div class="ph-section__body">\n'
        + '\n'.join(body_parts) + '\n'
        '        </div>\n'
        '      </section>'
    )
    return html[:sec_open] + new_sec + html[sec_end:]


def extract_directory_group(sd_html, label_prefix):
    """Return list of (href, name) for a contextual directory group."""
    # find the label then the following items div
    out = []
    for gm in re.finditer(r'<div class="site-directory-group site-directory-group-contextual">(.*?)</div>\s*</div>', sd_html, re.S):
        group = gm.group(1)
        lm = re.search(r'<div class="site-directory-label">([^<]+)</div>', group)
        if not lm:
            continue
        if not lm.group(1).strip().startswith(label_prefix):
            continue
        for am in re.finditer(r'<a href="([^"]+)">([^<]+)</a>', group):
            out.append((am.group(1), am.group(2)))
    return out


# ── FURTHER READING section ────────────────────────────────────────────────
def rebuild_further(html, page):
    refnum = re.search(r'<span class="ph-section__num">§ REF</span>', html)
    if not refnum:
        return html
    sec_open = html.rfind('<section class="ph-section">', 0, refnum.start())
    _, sec_end, _ = extract_balanced(html, sec_open, 'section')

    body_parts = []
    # Photobooks
    photobooks = parse_photobooks(page.get('photobooks_html') or '')
    if photobooks:
        body_parts.append('          <div class="ph-rel-label">Photobooks</div>')
        for pb in photobooks:
            body_parts.append(render_book(pb))
    # Databases & archives (external links)
    ext = page.get('external_links_html') or ''
    ext_links = re.findall(r'<a class="chip-link"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', ext, re.S)
    if ext_links:
        body_parts.append('          <div class="ph-rel-label">Databases &amp; archives</div>')
        body_parts.append('          <ul class="ph-further-links">')
        for href, text in ext_links:
            text = re.sub(r'\s*↗\s*$', '', text.strip())
            body_parts.append(f'            <li><a href="{href}" target="_blank" rel="noopener">{text}</a></li>')
        body_parts.append('          </ul>')
    # further_reading_html (append verbatim)
    fr = page.get('further_reading_html')
    if fr:
        body_parts.append('          ' + fr.strip())

    if not body_parts:
        return html[:sec_open].rstrip('\n ') + '\n\n' + html[sec_end:].lstrip('\n')

    new_sec = (
        '      <!-- FURTHER READING -->\n'
        '      <section class="ph-section">\n'
        '        <div class="ph-section__head">\n'
        '          <div class="ph-section__title">\n'
        '            <span class="ph-section__num">§ REF</span>\n'
        '            <span class="ph-section__name">Further reading</span>\n'
        '          </div>\n'
        '        </div>\n'
        '        <div class="ph-section__body">\n'
        + '\n'.join(body_parts) + '\n'
        '        </div>\n'
        '      </section>'
    )
    return html[:sec_open] + new_sec + html[sec_end:]


def parse_photobooks(pb_html):
    """Parse harvested book-card blocks into dicts."""
    books = []
    for cm in re.finditer(r'<div class="book-card">(.*?)(?=<div class="book-card">|</div>\s*</section>|$)', pb_html, re.S):
        block = cm.group(1)
        tm = re.search(r'<div class="book-title">(.*?)</div>', block, re.S)
        nm = re.search(r'<div class="book-note">(.*?)</div>', block, re.S)
        am = re.search(r'<a class="chip-link amazon-cta"[^>]*href="([^"]+)"', block)
        if not tm or not am:
            continue
        books.append({
            'title': tm.group(1).strip(),
            'note': (nm.group(1).strip() if nm else ''),
            'amazon': am.group(1),
        })
    return books


def render_book(pb):
    note = (f'            <p class="ph-book__note">{pb["note"]}</p>\n' if pb['note'] else '')
    return (
        '          <div class="ph-book">\n'
        f'            <div class="ph-book__title">{pb["title"]}</div>\n'
        + note +
        '            <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">\n'
        f'              <a class="ph-book-cta" href="{pb["amazon"]}" target="_blank" rel="noopener sponsored">View on Amazon ↗</a>\n'
        '              <span class="ph-aff">* Affiliate link</span>\n'
        '            </div>\n'
        '          </div>'
    )


# ── SOURCES section ────────────────────────────────────────────────────────
def rebuild_sources(html, page):
    srcnum = re.search(r'<span class="ph-section__num">§ SRC</span>', html)
    if not srcnum:
        return html
    sec_open = html.rfind('<section class="ph-section">', 0, srcnum.start())
    _, sec_end, _ = extract_balanced(html, sec_open, 'section')

    sources_html = page.get('sources_html') or ''
    cites = parse_sources(sources_html)
    cite_rows = []
    for num, anchor in cites:
        cite_rows.append(
            f'            <div class="ph-cite" id="cite-{num}"><div class="ph-cite__num">*{num}</div>'
            f'<div>{anchor}</div></div>')

    new_sec = (
        '      <!-- SOURCES -->\n'
        '      <section class="ph-section">\n'
        '        <div class="ph-section__head">\n'
        '          <div class="ph-section__title">\n'
        '            <span class="ph-section__num">§ SRC</span>\n'
        '            <span class="ph-section__name">Sources</span>\n'
        '          </div>\n'
        '        </div>\n'
        '        <div class="ph-section__body">\n'
        '          <div class="ph-sources">\n'
        + '\n'.join(cite_rows) + '\n'
        '          </div>\n'
        '        </div>\n'
        '      </section>'
    )
    return html[:sec_open] + new_sec + html[sec_end:], set(n for n, _ in cites)


def parse_sources(sources_html):
    """Parse <div class="cite-item" id="cite-N"><div class="cite-num">*N</div><a ...>..</a></div>."""
    out = []
    for cm in re.finditer(
            r'<div class="cite-item" id="cite-(\d+)"><div class="cite-num">\*\d+</div>(.*?)</div>',
            sources_html, re.S):
        num = int(cm.group(1))
        anchor = cm.group(2).strip()
        out.append((num, anchor))
    return out


# ── cite integrity: unlink sup-refs whose target cite is missing ──────────
def fix_orphan_suprefs(html, cite_set):
    def repl(m):
        n = int(m.group(1))
        if n in cite_set:
            return m.group(0)
        # plain text the anchor
        return f'<sup class="sup-ref">*{n}</sup>'
    return re.sub(r'<sup class="sup-ref"><a href="#cite-(\d+)">\*\d+</a></sup>', repl, html)


# ── SIDEBAR ────────────────────────────────────────────────────────────────
def rebuild_sidebar(html, page, slug, ja_file, prev_link):
    # search labels & aria
    html = html.replace('placeholder="写真家名・運動・キーワード"', 'placeholder="Name, movement, keyword"')
    html = html.replace('aria-label="検索"', 'aria-label="Search"')
    # block heads
    html = html.replace('<div class="ph-side-block__head">Entry · 写真家データ</div>',
                        '<div class="ph-side-block__head">Entry · Profile</div>')
    html = html.replace('<div class="ph-side-block__head">Keywords · キーワード</div>',
                        '<div class="ph-side-block__head">Keywords</div>')
    html = html.replace('<div class="ph-side-block__head">Works · 作品リンク</div>',
                        '<div class="ph-side-block__head">Works · Links</div>')
    html = html.replace('<div class="ph-side-block__head">Navigate · 移動</div>',
                        '<div class="ph-side-block__head">Navigate</div>')

    # side-meta values
    sm = find_element(html, 'div', 'class="ph-side-meta"')
    if sm:
        outer, start, end, inner = sm
        new_inner = translate_meta_values(inner)
        html = html[:start] + '<div class="ph-side-meta">' + new_inner + '</div>' + html[end:]

    # side chips movements
    scb = find_element(html, 'div', 'class="ph-side-chips"')
    if scb:
        outer, start, end, inner = scb
        new_inner = translate_keyword_movements(inner)
        html = html[:start] + '<div class="ph-side-chips">' + new_inner + '</div>' + html[end:]

    # side nav
    html = rebuild_side_nav(html, prev_link)
    # search JS not-found message
    html = html.replace('該当する写真家が見つかりません', 'No photographers found')
    return html


def rebuild_side_nav(html, prev_link):
    nm = find_element(html, 'nav', 'class="ph-side-nav"')
    if not nm:
        return html
    outer, start, end, inner = nm
    archive_href = '/en/archive.html' if file_exists_rel(os.path.join(ROOT, 'en', 'archive.html')) else '/archive.html'
    parts = []
    parts.append(f'          <a href="{archive_href}"><span>← All photographers</span><span>Archive</span></a>')
    if prev_link:
        parts.append(f'          <a href="{prev_link[0]}"><span>← {esc(prev_link[1])}</span><span>Prev</span></a>')
    parts.append('          <a href="/en/index.html"><span>Top page</span><span>Top</span></a>')
    new_inner = '\n' + '\n'.join(parts) + '\n        '
    return html[:start] + '<nav class="ph-side-nav">' + new_inner + '</nav>' + html[end:]


def compute_prev_link(html, ja_to_en):
    """From the JA side-nav middle link, produce EN equivalent (href, name)."""
    nm = find_element(html, 'nav', 'class="ph-side-nav"')
    if not nm:
        return None
    inner = nm[3]
    links = re.findall(r'<a href="([^"]+)"><span>([^<]*)</span><span>([^<]*)</span></a>', inner)
    # middle one is the prev photographer (label 前)
    for href, label, tag in links:
        if tag.strip() == '前':
            m = re.match(r'/photographers/([^"]+)\.html$', href)
            if m:
                ja_file = m.group(1) + '.html'
                en_file = ja_to_en.get(ja_file, ja_file)
                en_slug = en_file[:-5]
                if en_page_exists(en_slug):
                    return ('/en/photographers/' + en_slug + '.html', label.replace('← ', '').strip())
                else:
                    return ('/photographers/' + urllib.parse.quote(ja_file), label.replace('← ', '').strip())
    return None


# ── FOOTER ─────────────────────────────────────────────────────────────────
def rebuild_footer(html):
    html = html.replace('美術館・アーカイブ・専門資料に基づく',
                        'Based on museum, archive, and specialist sources')
    privacy = '/en/privacy-policy.html' if file_exists_rel(os.path.join(ROOT, 'en', 'privacy-policy.html')) else '/privacy-policy.html'
    html = re.sub(r'<a href="/privacy-policy\.html">プライバシーポリシー</a>',
                  f'<a href="{privacy}">Privacy</a>', html)
    html = re.sub(r'<a href="/colophon">コロフォン</a>',
                  '<a href="/colophon">Colophon</a>', html)
    return html


# ── INTERNAL LINK final pass ────────────────────────────────────────────────
def absolutize_and_localize_links(html, slug, ja_to_en):
    """Resolve ../ links to absolute, then map JA internal links to EN when an
    EN page exists. external/#/amazon untouched."""
    def repl(m):
        if m.group(1):  # data-lang-toggle sentinel → leave JA href intact
            return m.group(0)
        href = m.group(2)
        if href.startswith('#') or href.startswith('http') or 'amzn.to' in href or 'amazon.' in href:
            return m.group(0)
        # normalize ../ relative
        abs_href = href
        if abs_href.startswith('../'):
            abs_href = '/' + abs_href[3:]
        elif abs_href.startswith('./'):
            abs_href = '/photographers/' + abs_href[2:]
        if not abs_href.startswith('/'):
            return m.group(0)

        # already /en/ links → verify existence, else leave
        new = localize_path(abs_href, ja_to_en)
        return f'href="{new}"'

    html = re.sub(r'(data-lang-toggle )?href="([^"]+)"', repl, html)
    # strip sentinel
    html = html.replace('<a data-lang-toggle href=', '<a href=')
    return html


def localize_path(path, ja_to_en):
    """Map a JA absolute internal path to its EN equivalent when EN exists."""
    m = re.match(r'/photographers/([^"#?]+)\.html(.*)$', path)
    if m:
        ja_file = m.group(1) + '.html'
        tail = m.group(2)
        en_file = ja_to_en.get(ja_file, ja_file)
        en_slug = en_file[:-5]
        if en_page_exists(en_slug):
            return f'/en/photographers/{en_slug}.html{tail}'
        return path
    m = re.match(r'/movements/([^"#?]+)\.html(.*)$', path)
    if m:
        ja_mv = m.group(1)
        tail = m.group(2)
        slug = STUB_TO_SLUG.get(ja_mv, ja_mv)
        if en_movement_exists(slug):
            return f'/en/movements/{slug}.html{tail}'
        return path
    m = re.match(r'/eras/(\d+)\.html(.*)$', path)
    if m:
        era = m.group(1)
        tail = m.group(2)
        if en_era_exists(era):
            return f'/en/eras/{era}.html{tail}'
        return path
    m = re.match(r'/countries/([^"#?]+)\.html(.*)$', path)
    if m:
        cslug = m.group(1)
        tail = m.group(2)
        if en_country_exists(cslug):
            return f'/en/countries/{cslug}.html{tail}'
        return path
    # /en/ links: verify existence
    m = re.match(r'/en/photographers/([^"#?]+)\.html(.*)$', path)
    if m:
        if en_page_exists(m.group(1)):
            return path
        # EN missing → fall back to JA absolute
        ja_path = f'/photographers/{m.group(1)}.html{m.group(2)}'
        return ja_path
    return path


# ── data-nosnippet on chrome ─────────────────────────────────────────────
def add_nosnippet(html):
    for sel in ['<header class="head">', '<aside class="ph-side">', '<footer class="foot">']:
        if sel in html and 'data-nosnippet' not in sel:
            tag = sel[:-1] + ' data-nosnippet>'
            # only add if not already present right after
            html = html.replace(sel, tag, 1)
    return html


# ── KEYWORDS label translation (Keywords already English label) ────────────

# ── main per-page processing ───────────────────────────────────────────────
def process_page(ja_file, page, ja_to_en, warnings):
    ja_path = os.path.join(JA_DIR, ja_file)
    if not os.path.exists(ja_path):
        warnings.append(f'{ja_file}: JA source missing, skipped')
        return None, None
    html = open(ja_path, encoding='utf-8').read()

    en_file = ja_file_to_en_file(ja_file, ja_to_en)
    slug = en_file[:-5]

    prev_link = compute_prev_link(html, ja_to_en)

    html = replace_head(html, page, slug)
    html = insert_readability_style(html)
    html = rebuild_header(html, page, slug, ja_file)
    html = rebuild_hero(html, page)
    html = rebuild_abstract(html, page)
    html = rebuild_thesis(html, page)
    html = rebuild_entry_meta(html)
    html = rebuild_keywords(html)
    html = rebuild_works(html, page)
    html = replace_toc_and_sections(html, page)
    html = rebuild_related(html, page)
    html = rebuild_further(html, page)
    html, cite_set = rebuild_sources(html, page)
    html = fix_orphan_suprefs(html, cite_set)
    html = rebuild_sidebar(html, page, slug, ja_file, prev_link)
    html = rebuild_footer(html)
    html = absolutize_and_localize_links(html, slug, ja_to_en)
    html = add_nosnippet(html)

    return slug, html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--slug', action='append', default=[])
    ap.add_argument('--pilot', action='store_true')
    ap.add_argument('--all', action='store_true')
    args = ap.parse_args()

    content = json.load(open(CONTENT_JSON, encoding='utf-8'))
    pages = content['pages']
    classification = load_classification()
    ja_to_en, en_to_ja = build_jp_slug_map(classification)
    missing_true = set(classification.get('missing_en_true', []))

    # Determine target JA files
    if args.pilot:
        targets = []
        for s in PILOT_SLUGS:
            targets.append(s + '.html')
    elif args.slug:
        targets = []
        for s in args.slug:
            fn = s if s.endswith('.html') else s + '.html'
            targets.append(fn)
    elif args.all:
        targets = []
        for fn in sorted(os.listdir(JA_DIR)):
            if not fn.endswith('.html'):
                continue
            if fn.endswith('-backup.html'):
                continue
            targets.append(fn)
    else:
        ap.error('one of --pilot / --slug / --all required')

    warnings = []
    written = []
    for ja_file in targets:
        if ja_file in missing_true:
            warnings.append(f'{ja_file}: in missing_en_true, skipped (Stage 4)')
            continue
        # harvest is keyed by JA filename for romaji pages, but by the EN
        # output filename for kanji (jp-*) pages (the jp-*.html key, if present,
        # is an empty stub). Prefer the EN-file key when it carries content.
        en_file_key = ja_file_to_en_file(ja_file, ja_to_en)
        page = None
        if en_file_key != ja_file and pages.get(en_file_key) and pages[en_file_key].get('h1'):
            page = pages[en_file_key]
        if page is None:
            page = pages.get(ja_file)
        if page is None or not page.get('h1'):
            page = pages.get(en_file_key)
        if page is None:
            warnings.append(f'{ja_file}: no harvest content, skipped')
            continue
        # per-page sanity warnings
        if not page.get('photobooks_html'):
            warnings.append(f'{ja_file}: no photobooks_html')
        if not page.get('external_links_html'):
            warnings.append(f'{ja_file}: no external_links_html')
        if not page.get('site_directory_html'):
            warnings.append(f'{ja_file}: no site_directory_html (no RELATED)')
        if len(page.get('supref_ids', [])) and len(page.get('cite_ids', [])):
            orphan = set(page['supref_ids']) - set(page['cite_ids'])
            if orphan:
                warnings.append(f'{ja_file}: supref→missing cites {sorted(orphan)} (will be unlinked)')
        try:
            slug, out = process_page(ja_file, page, ja_to_en, warnings)
        except Exception as e:
            warnings.append(f'{ja_file}: BUILD ERROR {type(e).__name__}: {e}')
            continue
        if out is None:
            continue
        out_path = os.path.join(EN_DIR, slug + '.html')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(out)
        written.append((slug + '.html', len(out.encode('utf-8'))))

    print('Wrote %d page(s):' % len(written))
    for fn, size in written:
        print('  %-40s %8d bytes (%.1f KB)' % (fn, size, size / 1024))
    if warnings:
        print('\nWarnings (%d):' % len(warnings))
        for w in warnings:
            print('  ! ' + w)


if __name__ == '__main__':
    main()
