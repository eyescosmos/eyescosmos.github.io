#!/usr/bin/env python3
"""
insert_taxonomy_meta_ja.py
==========================
Add SEO meta (description, canonical, hreflang, OG, Twitter) to Japanese
movements/*.html (31) and eras/*.html (11) pages.

Rules:
  - Only modifies <head>. Body, design, and GA are NOT touched.
  - Idempotent: re-running does not duplicate meta tags.
  - Inserts right after the existing <title> tag.

Run: python3 scripts/insert_taxonomy_meta_ja.py
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = 'https://eyescosmos.github.io'
OGP_IMAGE = f'{BASE_URL}/assets/ogp-default.png'
SITE_NAME_JA = '写真の座標'
SITE_NAME_EN = 'Photo Coordinates'

# ── Japanese movement file ↔ English slug ──────────────────────────────────
STUB_TO_SLUG = {
    'FSA写真':           'fsa-photography',
    'カラー写真':          'color-photography',
    'コンセプチュアルアート':  'conceptual-art',
    'シネマトグラフィック写真': 'cinematographic-photography',
    'シュルレアリスム':       'surrealism',
    'ステージド写真':        'staged-photography',
    'ストリート写真':        'street-photography',
    'ストレート写真':        'straight-photography',
    'タイポロジー写真':      'typological-photography',
    'ダダ':               'dada',
    'デュッセルドルフ派':    'dusseldorf-school',
    'ドキュメンタリー':      'documentary',
    'ニューカラー':          'new-color',
    'バウハウス':            'bauhaus',
    'ピクチャーズ世代':      'pictures-generation',
    'ピクトリアリズム':      'pictorialism',
    'フェミニズム写真':      'feminist-photography',
    'フォトジャーナリズム':  'photojournalism',
    'プロヴォーク':          'provoke',
    'モダニズム':            'modernism',
    'リアリズム写真':        'realism-photography',
    'レイオグラフ':          'rayograph-photogram',
    'ヴォルテクシズム':      'vorticism',
    '写真分離派':            'photo-secession',
    '大判カラー写真':        'large-format-color',
    '新しいヴィジョン':      'new-vision',
    '新即物主義':            'neue-sachlichkeit',
    '決定的瞬間':            'decisive-moment',
    '社会ドキュメンタリー':  'social-documentary',
    '私写真':               'i-photography-shi-shashin',
    '自然主義写真':          'naturalistic-photography',
}

# Era IDs list
ERA_IDS = ['1839', '1870', '1890', '1910', '1930', '1950', '1970', '1980', '1990', '2000', '2010']


def extract_abstract(html):
    """Extract the first paragraph from ph-abstract section."""
    m = re.search(
        r'<div class="ph-abstract__label"[^>]*>.*?</div>\s*<p>(.*?)</p>',
        html, re.S
    )
    if m:
        text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        return text[:160] if len(text) > 160 else text
    return None


def extract_title(html):
    """Extract title tag content."""
    m = re.search(r'<title>(.*?)</title>', html)
    return m.group(1) if m else ''


def build_meta_block(canonical_url, ja_url, en_url, description, og_title, twitter_title):
    """Build the SEO meta block to insert after <title>."""
    lines = [
        f'<meta name="description" content="{description}">',
        f'<link rel="canonical" href="{canonical_url}">',
        f'<link rel="alternate" hreflang="ja" href="{ja_url}">',
        f'<link rel="alternate" hreflang="en" href="{en_url}">',
        f'<link rel="alternate" hreflang="x-default" href="{ja_url}">',
        f'<meta property="og:type" content="website">',
        f'<meta property="og:url" content="{canonical_url}">',
        f'<meta property="og:site_name" content="{SITE_NAME_JA}">',
        f'<meta property="og:title" content="{og_title}">',
        f'<meta property="og:description" content="{description}">',
        f'<meta property="og:image" content="{OGP_IMAGE}">',
        f'<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{twitter_title}">',
        f'<meta name="twitter:description" content="{description}">',
        f'<meta name="twitter:image" content="{OGP_IMAGE}">',
    ]
    return '\n'.join(lines)


def already_has_meta(html):
    """Return True if the page already has description/canonical/hreflang meta."""
    return (
        'meta name="description"' in html or
        'rel="canonical"' in html or
        'hreflang' in html
    )


def insert_after_title(html, meta_block):
    """Insert meta_block right after the </title> tag."""
    return html.replace('</title>', f'</title>\n{meta_block}', 1)


def process_movement(ja_name, html_path):
    """Process one Japanese movement page."""
    html = open(html_path, encoding='utf-8').read()

    if already_has_meta(html):
        print(f'  SKIP (already has meta): {os.path.basename(html_path)}')
        return

    en_slug = STUB_TO_SLUG.get(ja_name)
    if not en_slug:
        print(f'  WARN: no slug for {ja_name}')
        return

    # URLs — use un-encoded Japanese filenames (same form as EN pages' hreflang_ja)
    ja_url = f'{BASE_URL}/movements/{ja_name}.html'
    en_url = f'{BASE_URL}/en/movements/{en_slug}.html'
    canonical_url = ja_url

    # Description from abstract
    description = extract_abstract(html)
    if not description:
        # Fallback: use title minus site name
        title = extract_title(html)
        description = re.sub(r'｜写真の座標$', '', title).strip()
        if len(description) > 160:
            description = description[:157] + '...'

    # Escape quotes in content attributes
    description = description.replace('"', '&quot;')

    # OG / Twitter title from <title>
    title_text = extract_title(html)
    # Strip ｜写真の座標 if present
    og_title = re.sub(r'\s*｜\s*写真の座標$', f' | {SITE_NAME_JA}', title_text).strip()
    og_title = og_title.replace('"', '&quot;')

    meta_block = build_meta_block(canonical_url, ja_url, en_url, description, og_title, og_title)
    new_html = insert_after_title(html, meta_block)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f'  OK: {os.path.basename(html_path)}')


def process_era(era_id, html_path):
    """Process one Japanese era page."""
    html = open(html_path, encoding='utf-8').read()

    if already_has_meta(html):
        print(f'  SKIP (already has meta): {os.path.basename(html_path)}')
        return

    # URLs
    ja_url = f'{BASE_URL}/eras/{era_id}.html'
    en_url = f'{BASE_URL}/en/eras/{era_id}.html'
    canonical_url = ja_url

    # Description from abstract
    description = extract_abstract(html)
    if not description:
        title = extract_title(html)
        description = re.sub(r'｜写真の座標$', '', title).strip()
        if len(description) > 160:
            description = description[:157] + '...'

    description = description.replace('"', '&quot;')

    # OG title
    title_text = extract_title(html)
    og_title = re.sub(r'\s*｜\s*写真の座標$', f' | {SITE_NAME_JA}', title_text).strip()
    og_title = og_title.replace('"', '&quot;')

    meta_block = build_meta_block(canonical_url, ja_url, en_url, description, og_title, og_title)
    new_html = insert_after_title(html, meta_block)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f'  OK: {os.path.basename(html_path)}')


def add_nosnippet_chrome(html):
    """UIクローム（ヘッダー・ナビ・サイドバー・フッター・カードの pc-top と
    pc-body__cta）に data-nosnippet を付与する。冪等。"""
    for tag in ('<header class="head">', '<nav class="mvt-nav">',
                '<nav class="era-nav">', '<aside class="era-side">',
                '<footer class="foot">'):
        html = html.replace(tag, tag[:-1] + ' data-nosnippet>')
    html = re.sub(r'<div class="(pc-top pc-top--[a-z-]+)">',
                  r'<div data-nosnippet class="\1">', html)
    html = html.replace('<div class="pc-body__cta">',
                        '<div class="pc-body__cta" data-nosnippet>')
    return html


def apply_nosnippet(html_path):
    with open(html_path, encoding='utf-8') as f:
        html = f.read()
    new_html = add_nosnippet_chrome(html)
    if new_html != html:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(new_html)
        print(f'  NOSNIPPET: {os.path.basename(html_path)}')


def main():
    print('=== insert_taxonomy_meta_ja.py ===')

    # Process movements
    print('\n── Movements ──')
    mvt_dir = os.path.join(ROOT, 'movements')
    for ja_name, en_slug in STUB_TO_SLUG.items():
        html_path = os.path.join(mvt_dir, f'{ja_name}.html')
        if not os.path.exists(html_path):
            print(f'  MISSING: {ja_name}.html')
            continue
        process_movement(ja_name, html_path)
        apply_nosnippet(html_path)

    # Process eras
    print('\n── Eras ──')
    era_dir = os.path.join(ROOT, 'eras')
    for era_id in ERA_IDS:
        html_path = os.path.join(era_dir, f'{era_id}.html')
        if not os.path.exists(html_path):
            print(f'  MISSING: {era_id}.html')
            continue
        process_era(era_id, html_path)
        apply_nosnippet(html_path)

    print('\nDone.')


if __name__ == '__main__':
    main()
