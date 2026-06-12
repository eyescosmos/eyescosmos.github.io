#!/usr/bin/env python3
"""Insert missing photographer cards into Japanese era pages.

Uses archive.html as the canonical card source.
CSV: photographer-pages-missing-from-all-era-pages.csv
"""
from __future__ import annotations

import csv
import html as html_module
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

EXCLUDED_IDS = {'fabian-marti', 'gabriel-orozco', 'charles-wirgman'}


# ---------------------------------------------------------------------------
# Balanced <article> extraction (same approach as fix_era_page_cards.py)
# ---------------------------------------------------------------------------

def extract_articles(html: str) -> list[str]:
    """Extract all <article>...</article> blocks from HTML using balanced parsing."""
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


# ---------------------------------------------------------------------------
# Build archive lookup: id -> full article block
# ---------------------------------------------------------------------------

def build_archive_id_lookup(arch_html: str) -> dict[str, str]:
    """Build map: photographer id -> full <article>...</article> from archive.html."""
    lookup: dict[str, str] = {}
    for article in extract_articles(arch_html):
        # Match href="photographers/{id}.html" inside the article
        m = re.search(r'href="photographers/([^"]+)\.html"', article)
        if m:
            pid = m.group(1)
            lookup[pid] = article
    return lookup


# ---------------------------------------------------------------------------
# Transform archive article into era-page card
# ---------------------------------------------------------------------------

def transform_card(article: str, pid: str, card_entry: dict) -> str:
    """Transform an archive article into an era-page card."""
    result = article

    # 1. Replace <article ...> opening tag with clean class (drop data-* attrs)
    result = re.sub(
        r'<article[^>]*>',
        '<article class="pc-card pc-card--photographer">',
        result,
        count=1,
    )

    # 2. Fix href: "photographers/{id}.html" -> "../photographers/{id}.html"
    result = result.replace(
        f'href="photographers/{pid}.html"',
        f'href="../photographers/{pid}.html"',
        1,
    )

    # 3. Remove target="_blank" from the anchor tag
    result = result.replace(' target="_blank"', '', 1)

    # 4. Replace PHOTOGRAPHER span in pc-top__meta with nationality from card-data
    nationality = card_entry.get('nationality', '') or 'PHOTOGRAPHER'
    if not nationality:
        nationality = 'PHOTOGRAPHER'
    result = re.sub(
        r'(<span class="idx">\d+</span>)<span>PHOTOGRAPHER</span>',
        lambda _m: _m.group(1) + f'<span>{nationality}</span>',
        result,
        count=1,
    )

    # 5. Replace truncated lede with full ledeJa from card-data
    lede_full = card_entry.get('ledeJa', '')
    if lede_full:
        escaped_lede = html_module.escape(lede_full, quote=False)
        result = re.sub(
            r'<p class="pc-body__lede">.*?</p>',
            f'<p class="pc-body__lede">{escaped_lede}</p>',
            result,
            count=1,
            flags=re.S,
        )

    return result


# ---------------------------------------------------------------------------
# Insert cards into era HTML
# ---------------------------------------------------------------------------

def insert_cards_into_era(era_html: str, new_cards: list[str]) -> str | None:
    """Append new_cards at the end of the er-cards container.

    Returns updated HTML, or None if the regex doesn't match.
    """
    pattern = re.compile(
        r'(<div class="er-cards">)(.*?)(</div>(?:<!-- [^>]* -->)?\s*</div>\s*</section>)',
        re.S,
    )
    matches = list(pattern.finditer(era_html))
    if len(matches) != 1:
        return None

    m = matches[0]
    insertion = '\n' + '\n'.join(new_cards)
    new_html = (
        era_html[:m.start()]
        + m.group(1)
        + m.group(2)
        + insertion
        + m.group(3)
        + era_html[m.end():]
    )
    return new_html


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    csv_path = Path(
        '/Users/aiharadaisuke/Documents/New project/repo/outputs/'
        'photographer-pages-missing-from-all-era-pages.csv'
    )

    arch_html = (REPO / 'archive.html').read_text(encoding='utf-8')
    card_data_raw = json.loads((REPO / 'card-data.json').read_text(encoding='utf-8'))

    # Build archive lookup by id
    archive_by_id = build_archive_id_lookup(arch_html)
    print(f"Archive lookup: {len(archive_by_id)} photographer ids")

    # Build card-data lookup by id
    card_data_by_id: dict[str, dict] = {}
    for p in card_data_raw.get('photographers', []):
        pid = p.get('id', '')
        if pid:
            card_data_by_id[pid] = p
    print(f"Card-data lookup: {len(card_data_by_id)} photographer ids")

    # Load CSV, group by era
    rows_by_era: dict[str, list[dict]] = {}
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            era = row.get('era', '').strip()
            pid = row.get('id', '').strip()
            if not era or not pid:
                continue
            rows_by_era.setdefault(era, []).append({
                'era': era,
                'id': pid,
                'nameJa': row.get('nameJa', '').strip(),
                'nameEn': row.get('nameEn', '').strip(),
            })

    era_files_in_scope = {'1890', '1910', '1930', '1950', '1970', '1980', '1990', '2000', '2010'}

    total_inserted = 0
    total_skipped_already = 0
    total_unresolved = 0
    all_unresolved: list[str] = []
    all_already_present: list[str] = []
    all_no_page: list[str] = []
    changed_files: list[str] = []

    for era in sorted(rows_by_era.keys()):
        if era not in era_files_in_scope:
            print(f"[SKIP] era {era} not in scope")
            continue

        era_file = REPO / 'eras' / f'{era}.html'
        if not era_file.exists():
            print(f"[ERROR] era file not found: {era_file}")
            continue

        era_html = era_file.read_text(encoding='utf-8')

        to_insert: list[str] = []
        skipped_already: list[str] = []
        unresolved: list[str] = []
        no_page: list[str] = []

        for row in rows_by_era[era]:
            pid = row['id']

            # Guard: skip excluded ids
            if pid in EXCLUDED_IDS:
                print(f"[EXCLUDED] {era} {pid}")
                continue

            # Check if already present
            check_href = f'href="../photographers/{pid}.html"'
            if check_href in era_html:
                skipped_already.append(pid)
                continue

            # Check archive article exists
            archive_article = archive_by_id.get(pid)
            if archive_article is None:
                msg = f"UNRESOLVED (no archive): {era} {pid}"
                unresolved.append(pid)
                all_unresolved.append(msg)
                print(f"[UNRESOLVED] {era} {pid} — not found in archive.html")
                continue

            # Check card-data entry exists
            card_entry = card_data_by_id.get(pid)
            if card_entry is None:
                msg = f"UNRESOLVED (no card-data): {era} {pid}"
                unresolved.append(pid)
                all_unresolved.append(msg)
                print(f"[UNRESOLVED] {era} {pid} — not found in card-data.json")
                continue

            # Check photographer page exists on disk
            photographer_page = REPO / 'photographers' / f'{pid}.html'
            if not photographer_page.exists():
                no_page.append(pid)
                all_no_page.append(f"NO PAGE: {era} {pid}")
                print(f"[NO PAGE] {era} {pid} — photographers/{pid}.html not found")
                continue

            # Transform and queue for insertion
            transformed = transform_card(archive_article, pid, card_entry)
            to_insert.append(transformed)

        # Insert cards into era file
        if to_insert:
            updated_html = insert_cards_into_era(era_html, to_insert)
            if updated_html is None:
                print(f"[ERROR] Regex did not match exactly once in eras/{era}.html — SKIPPING file")
                continue
            era_file.write_text(updated_html, encoding='utf-8')
            changed_files.append(f'eras/{era}.html')
            inserted_ids = [rows_by_era[era][i]['id'] for i in range(len(rows_by_era[era]))
                           if rows_by_era[era][i]['id'] not in skipped_already
                           and rows_by_era[era][i]['id'] not in unresolved
                           and rows_by_era[era][i]['id'] not in no_page
                           and rows_by_era[era][i]['id'] not in EXCLUDED_IDS]
            print(
                f"[DONE] eras/{era}.html: inserted {len(to_insert)} cards"
                + (f", skipped {len(skipped_already)} already-present" if skipped_already else "")
                + (f", {len(unresolved)} unresolved" if unresolved else "")
                + (f", {len(no_page)} no-page" if no_page else "")
            )
            total_inserted += len(to_insert)
        else:
            print(
                f"[NO CHANGE] eras/{era}.html: nothing to insert"
                + (f" ({len(skipped_already)} already-present)" if skipped_already else "")
                + (f" ({len(unresolved)} unresolved)" if unresolved else "")
            )

        total_skipped_already += len(skipped_already)
        total_unresolved += len(unresolved)
        if skipped_already:
            all_already_present.extend(f"{era} {pid}" for pid in skipped_already)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Changed files: {len(changed_files)}")
    for f in changed_files:
        print(f"  {f}")
    print(f"\nTotal inserted: {total_inserted}")
    print(f"Total already-present (skipped): {total_skipped_already}")
    print(f"Total unresolved: {total_unresolved}")
    if all_unresolved:
        print("\nUNRESOLVED:")
        for u in all_unresolved:
            print(f"  {u}")
    if all_no_page:
        print("\nNO PAGE:")
        for p in all_no_page:
            print(f"  {p}")
    if all_already_present:
        print("\nALREADY PRESENT (skipped):")
        for p in all_already_present:
            print(f"  {p}")


if __name__ == '__main__':
    main()
