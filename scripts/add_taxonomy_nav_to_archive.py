#!/usr/bin/env python3
"""Add country + movement page links to the archive page's filter row.

The era filter row (`#era-toolbar`) already lists All + eras. This appends
"国 / Country" and "運動 / Movement" segments of links to the country and
movement hub pages, in the same pill-era design, and makes the whole row
horizontally scrollable.

Idempotent: the appended block is wrapped in <!-- taxo-nav --> sentinels so
re-running replaces it rather than duplicating. Edits archive.html (JA) and
en/archive.html (EN) directly — both are the v5.1 source-of-truth pages
(generate_archive_pages.py is the stale old-design generator and is not run).
"""
from __future__ import annotations

import glob
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Country pages: single-country registry (slug + names)
REG = json.loads((REPO / "data" / "country-pages.json").read_text(encoding="utf-8"))
COUNTRIES_JA = sorted(((r["slug"], r["nameJa"]) for r in REG), key=lambda x: x[1])
COUNTRIES_EN = sorted(((r["slug"], r["nameEn"]) for r in REG), key=lambda x: x[1])

# Movement pages
JA_MOVEMENTS = sorted(
    Path(f).stem for f in glob.glob(str(REPO / "movements" / "*.html"))
    if not f.endswith("-backup.html")
)
EN_MOVEMENTS = sorted(
    Path(f).stem for f in glob.glob(str(REPO / "en" / "movements" / "*.html"))
    if not f.endswith("-backup.html")
)

# Make the era row scroll horizontally instead of wrapping
SCROLL_FROM = (".toolbar-era{display:flex;align-items:stretch;flex-wrap:wrap;"
               "border-bottom:1px solid var(--rule-strong);margin:0 0 12px;}")
SCROLL_TO = (".toolbar-era{display:flex;align-items:stretch;flex-wrap:nowrap;"
             "overflow-x:auto;scrollbar-width:thin;"
             "border-bottom:1px solid var(--rule-strong);margin:0 0 12px;}"
             ".toolbar-era .toolbar-era__label,.toolbar-era .pill-era{flex:0 0 auto;}")


def build_block(country_pairs, country_base, country_label,
                movements, movement_base, movement_label) -> str:
    parts = ["<!-- taxo-nav -->"]
    parts.append(f'<span class="toolbar-era__label">{country_label}</span>')
    parts += [f'<a class="pill-era" href="/{country_base}/{slug}.html">{name}</a>'
              for slug, name in country_pairs]
    parts.append(f'<span class="toolbar-era__label">{movement_label}</span>')
    parts += [f'<a class="pill-era" href="/{movement_base}/{name}.html">{name}</a>'
              for name in movements]
    parts.append("<!-- /taxo-nav -->")
    return "".join(parts)


def patch(path: Path, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    if SCROLL_FROM in text:
        text = text.replace(SCROLL_FROM, SCROLL_TO)
    # insert/replace the taxo-nav block right before #era-toolbar closes
    if "<!-- taxo-nav -->" in text:
        text = re.sub(r"<!-- taxo-nav -->.*?<!-- /taxo-nav -->", block, text, flags=re.S)
    else:
        # era-toolbar div: insert block just before its closing </div>
        m = re.search(r'(<div class="toolbar-era"[^>]*>.*?)(\n?\s*</div>)', text, re.S)
        if not m:
            raise SystemExit(f"era-toolbar not found in {path}")
        text = text[:m.end(1)] + block + text[m.end(1):]
    path.write_text(text, encoding="utf-8")


def main() -> None:
    patch(REPO / "archive.html",
          build_block(COUNTRIES_JA, "countries", "国", JA_MOVEMENTS, "movements", "運動"))
    print("patched archive.html")
    # EN (en/archive.html) handled separately — en/movements has mixed JA/EN
    # filenames that need a curated English label set.


if __name__ == "__main__":
    main()
