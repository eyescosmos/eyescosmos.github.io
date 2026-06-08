#!/usr/bin/env python3
"""Fix era page cards to match archive.html styles and idx numbers."""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def extract_first_div(html: str, start_pattern: str) -> str | None:
    """Extract a balanced div starting at the first match of start_pattern."""
    m = re.search(start_pattern, html)
    if not m:
        return None
    start = m.start()
    depth = 0
    i = start
    while i < len(html):
        if html[i:i+4] == '<div':
            depth += 1
            i += 4
        elif html[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                return html[start:i + 6]
            i += 6
        else:
            i += 1
    return None


def extract_articles(html: str) -> list[str]:
    """Extract all <article>...</article> blocks from HTML."""
    articles = []
    search_from = 0
    while True:
        m = re.search(r'<article[^>]*>', html[search_from:])
        if not m:
            break
        start = search_from + m.start()
        depth = 0
        i = start
        while i < len(html):
            if html[i:i+8] == '<article':
                depth += 1
                i += 8
            elif html[i:i+10] == '</article>':
                depth -= 1
                if depth == 0:
                    articles.append(html[start:i + 10])
                    search_from = i + 10
                    break
                i += 10
            else:
                i += 1
        else:
            break
    return articles


def build_archive_lookup(arch_html: str) -> tuple[dict[str, dict], dict[str, dict]]:
    """Build: (ja_name → {idx, pc_top_html}, en_name_lower → {idx, pc_top_html})."""
    ja_lookup: dict[str, dict] = {}
    en_lookup: dict[str, dict] = {}

    for article in extract_articles(arch_html):
        name_m = re.search(r'class="pc-body__name">(.*?)</h3>', article)
        en_m = re.search(r'class="pc-body__name-en">([^<]+)<', article)
        idx_m = re.search(r'class="idx">(\d+)<', article)
        if not (name_m and idx_m):
            continue
        pc_top = extract_first_div(article, r'<div class="pc-top[^>]*>')
        if not pc_top:
            continue

        entry = {'idx': idx_m.group(1), 'pc_top': pc_top}
        name_ja = name_m.group(1)
        ja_lookup[name_ja] = entry
        if en_m:
            en_lookup[en_m.group(1).lower()] = entry

    return ja_lookup, en_lookup


def build_card_data_lookup(card_data: dict) -> tuple[dict[str, dict], dict[str, dict]]:
    """Build: (ja_name → entry, en_name_lower → entry) from card-data.json."""
    ja_lookup: dict[str, dict] = {}
    en_lookup: dict[str, dict] = {}
    for p in card_data.get('photographers', []):
        name_ja = p.get('nameJa', '')
        name_en = p.get('nameEn', '')
        if name_ja:
            ja_lookup[name_ja] = p
        if name_en:
            en_lookup[name_en.lower()] = p
    return ja_lookup, en_lookup


def get_country_from_card(card_html: str) -> str:
    """Extract the country/label from the second span in pc-top__meta."""
    m = re.search(r'class="idx">\d+</span><span>([^<]*)</span>', card_html)
    return m.group(1) if m else 'PHOTOGRAPHER'


def swap_meta_country(pc_top_html: str, new_country: str) -> str:
    """Replace the second span (originally 'PHOTOGRAPHER') with country code."""
    return re.sub(
        r'(<span class="idx">\d+</span>)<span>[^<]*</span>',
        lambda _m: _m.group(1) + f'<span>{new_country}</span>',
        pc_top_html,
        count=1,
    )


def _build_art_html(style: str, art_text: str, p: dict) -> str:
    """Build pc-top__art inner HTML based on style."""
    if style == 'pc-top--kanji':
        return f'<div style="font-size:118px;">{art_text}</div>'
    if style == 'pc-top--kanji-foreign':
        parts = art_text.split() if ' ' in art_text else [art_text, '']
        char, gloss = parts[0], parts[1] if len(parts) > 1 else ''
        if gloss:
            return f'<span class="kf-char">{char}</span><span class="kf-gloss">{gloss}</span>'
        return f'<span class="kf-char">{char}</span>'
    if style == 'pc-top--initials':
        if len(art_text) >= 2:
            return f'{art_text[0]}<span class="accent">{art_text[1]}</span>'
        return art_text
    if style == 'pc-top--slash':
        name_en = p.get('nameEn', '')
        parts = name_en.split() if name_en else art_text.split()
        if len(parts) >= 2:
            fn = parts[0].upper()
            ln = parts[-1].upper()
            return f'<span class="fn">{fn}</span><span class="ln">{ln}</span>'
        return f'<span class="ln">{art_text}</span>'
    if style == 'pc-top--year':
        meta = p.get('metaJa', '')
        ym = re.search(r'(\d{4})[\s–\-·]+(\d{4})', meta)
        if ym:
            return (f'<span class="yr-birth">{ym.group(1)}</span>'
                    f'<span class="yr-dash">—</span>'
                    f'<span class="yr-death">{ym.group(2)}</span>')
        return art_text
    if style == 'pc-top--stacked':
        return f'<span>{art_text}</span>'
    if style == 'pc-top--cite':
        parts = art_text.split()
        if len(parts) >= 2:
            return f'<span class="cty">{parts[0]}</span><span class="cyr">{parts[1]}</span>'
        return art_text
    if style == 'pc-top--country':
        nat = p.get('nationality', '')
        return nat[:3] if nat else art_text
    # pc-top--serif, --title, --grid, --number, --fragment, --outline, --rotate, --twosize
    return art_text


def construct_pc_top_from_card_data(p: dict, country: str, hint: str) -> str:
    """Construct a pc-top div from card-data.json entry."""
    idx = str(p.get('idx', '?'))
    style = p.get('style', 'pc-top--kanji')
    art_text = p.get('artText', '')
    hint_text = p.get('hintText', hint)
    art_html = _build_art_html(style, art_text, p)
    return (
        f'<div class="pc-top {style}">'
        f'<div class="pc-top__meta"><span class="idx">{idx}</span><span>{country}</span></div>'
        f'<div class="pc-top__art">{art_html}</div>'
        f'<div class="pc-top__hint">{hint_text}</div>'
        f'</div>'
    )


def fix_card(
    card_html: str,
    arch_ja: dict, arch_en: dict,
    cd_ja: dict, cd_en: dict,
) -> tuple[str, bool]:
    """Fix the pc-top of one card. Returns (updated_html, changed)."""
    name_m = re.search(r'class="pc-body__name">(.*?)</h3>', card_html)
    if not name_m:
        return card_html, False
    name_ja = name_m.group(1)
    en_m = re.search(r'class="pc-body__name-en">([^<]+)<', card_html)
    name_en = en_m.group(1).lower() if en_m else ''

    country = get_country_from_card(card_html)
    hint_m = re.search(r'class="pc-top__hint">([^<]*)<', card_html)
    existing_hint = hint_m.group(1) if hint_m else ''

    new_pc_top: str | None = None

    # Priority: archive by ja name → archive by en name → card-data by ja → card-data by en
    if name_ja in arch_ja:
        new_pc_top = swap_meta_country(arch_ja[name_ja]['pc_top'], country)
    elif name_en and name_en in arch_en:
        new_pc_top = swap_meta_country(arch_en[name_en]['pc_top'], country)
    elif name_ja in cd_ja:
        new_pc_top = construct_pc_top_from_card_data(cd_ja[name_ja], country, existing_hint)
    elif name_en and name_en in cd_en:
        new_pc_top = construct_pc_top_from_card_data(cd_en[name_en], country, existing_hint)
    else:
        return card_html, False

    # Replace the old pc-top with new
    old_pc_top = extract_first_div(card_html, r'<div class="pc-top[^>]*>')
    if not old_pc_top:
        return card_html, False
    updated = card_html.replace(old_pc_top, new_pc_top, 1)
    return updated, updated != card_html


def fix_page(
    html: str,
    arch_ja: dict, arch_en: dict,
    cd_ja: dict, cd_en: dict,
) -> tuple[str, int]:
    """Fix all cards in a page. Returns (updated_html, num_changed)."""
    articles = extract_articles(html)
    changes = 0
    result = html
    for article in articles:
        updated, changed = fix_card(article, arch_ja, arch_en, cd_ja, cd_en)
        if changed:
            result = result.replace(article, updated, 1)
            changes += 1
    return result, changes


def has_sequential_numbering(html: str) -> bool:
    """Return True if this page's first pc-card idx is '01' or '1'."""
    idxs = re.findall(r'class="idx">(\d+)<', html)
    return bool(idxs) and idxs[0] in ('01', '1')


def main() -> None:
    arch_html = (REPO / 'archive.html').read_text(encoding='utf-8')
    card_data = json.loads((REPO / 'card-data.json').read_text(encoding='utf-8'))

    arch_ja, arch_en = build_archive_lookup(arch_html)
    cd_ja, cd_en = build_card_data_lookup(card_data)

    print(f"Archive lookup: {len(arch_ja)} (ja) + {len(arch_en)} (en) photographers")
    print(f"Card-data lookup: {len(cd_ja)} (ja) + {len(cd_en)} (en) photographers")

    # Fix era pages (all of them — most use sequential numbering)
    era_dir = REPO / 'eras'
    print("\nEra pages:")
    for html_path in sorted(era_dir.glob('*.html')):
        html = html_path.read_text(encoding='utf-8')
        updated, count = fix_page(html, arch_ja, arch_en, cd_ja, cd_en)
        if count:
            html_path.write_text(updated, encoding='utf-8')
            print(f"  Updated {html_path.name}: {count} cards fixed")
        else:
            print(f"  Skipped {html_path.name}: no changes needed")

    # Fix movement pages that still use sequential local numbering
    mvt_dir = REPO / 'movements'
    print("\nMovement pages:")
    for html_path in sorted(mvt_dir.glob('*.html')):
        html = html_path.read_text(encoding='utf-8')
        if not has_sequential_numbering(html):
            continue
        updated, count = fix_page(html, arch_ja, arch_en, cd_ja, cd_en)
        if count:
            html_path.write_text(updated, encoding='utf-8')
            print(f"  Updated {html_path.name}: {count} cards fixed")
        else:
            print(f"  Skipped {html_path.name}: no changes needed")


if __name__ == '__main__':
    main()
