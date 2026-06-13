#!/usr/bin/env python3
"""Add country + movement filters to the archive page's filter row.

The era row already filters the cards in place (data-era). This adds "国 /
運動" chips that ALSO filter the cards in place (not navigate): clicking a
country or movement chip shows only the matching cards, exactly like
clicking an era. Era / country / movement are mutually exclusive (one
active classification), combined with the independent type filter + search.

Matching:
  - country: each photographer card gets a data-country attribute (ISO
    codes from card-data.json); the chip carries the code → exact code match
    (so dual-nationality photographers appear under both countries).
  - movement: whole-token match against the card's data-search (movement
    tags are reliably present there).

Also: makes the row horizontally scrollable, colours the segment labels
(Era / 国 / 運動) red, and mirrors the chips into the mobile filter strip.

Idempotent: blocks are sentinel-wrapped and JS/attribute edits are guarded.
Edits archive.html only (the v5.1 source-of-truth page;
generate_archive_pages.py is the stale old-design generator, not run).
EN (en/archive.html) handled separately.
"""
from __future__ import annotations

import glob
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

REG = json.loads((REPO / "data" / "country-pages.json").read_text(encoding="utf-8"))
# (iso code, Japanese name) ordered by name
COUNTRIES = sorted(((r["codes"][0], r["nameJa"]) for r in REG), key=lambda x: x[1])
MOVEMENTS = sorted(
    Path(f).stem for f in glob.glob(str(REPO / "movements" / "*.html"))
    if not f.endswith("-backup.html")
)
NAT = {p["id"]: (p.get("nationality") or "")
       for p in json.loads((REPO / "card-data.json").read_text(encoding="utf-8"))["photographers"]}


def ea(s: str) -> str:
    return s.replace('"', "&quot;")


# ── chip blocks ─────────────────────────────────────────────────────────────

def desktop_block() -> str:
    p = ["<!-- taxo-nav -->", '<span class="toolbar-era__label">国</span>']
    p += [f'<button class="pill-era" data-taxo="{code}" data-taxokind="c">{name}</button>'
          for code, name in COUNTRIES]
    p.append('<span class="toolbar-era__label">運動</span>')
    p += [f'<button class="pill-era" data-taxo="{ea(name)}" data-taxokind="m">{name}</button>'
          for name in MOVEMENTS]
    p.append("<!-- /taxo-nav -->")
    return "".join(p)


def mobile_block() -> str:
    p = ["<!-- taxo-nav-m -->"]
    p += [f'<button class="mobile-filter-chip" data-mobile-taxo="{code}" data-mobile-taxokind="c">{name}</button>'
          for code, name in COUNTRIES]
    p += [f'<button class="mobile-filter-chip" data-mobile-taxo="{ea(name)}" data-mobile-taxokind="m">{name}</button>'
          for name in MOVEMENTS]
    p.append("<!-- /taxo-nav-m -->")
    return "".join(p)


# ── CSS ──────────────────────────────────────────────────────────────────────

SCROLL_FROM = (".toolbar-era{display:flex;align-items:stretch;flex-wrap:wrap;"
               "border-bottom:1px solid var(--rule-strong);margin:0 0 12px;}")
SCROLL_TO = (".toolbar-era{display:flex;align-items:stretch;flex-wrap:nowrap;"
             "overflow-x:auto;scrollbar-width:thin;"
             "border-bottom:1px solid var(--rule-strong);margin:0 0 12px;}"
             ".toolbar-era .toolbar-era__label,.toolbar-era .pill-era{flex:0 0 auto;}")
RED_LABEL = "/* taxo-red-label */.toolbar-era__label{color:#d6402e;}"


# ── JS (guarded string edits) ────────────────────────────────────────────────

JS_EDITS = [
    ("let currentType='all',currentEra='',currentSearch='';",
     "let currentType='all',currentEra='',currentSearch='',currentTaxo='',currentTaxoKind='';"
     "function taxoMatch(s,t){return (' '+(s||'').toLowerCase()+' ').indexOf(' '+t.toLowerCase()+' ')!==-1;}"
     "function countryMatch(card,code){return (card.dataset.country||'').split('/').some(function(x){return x.trim()===code;});}"),
    ("&&(!currentSearch||(card.dataset.search||'').toLowerCase().includes(currentSearch.toLowerCase()));",
     "&&(!currentTaxo||(currentTaxoKind==='c'?countryMatch(card,currentTaxo):taxoMatch(card.dataset.search,currentTaxo)))"
     "&&(!currentSearch||(card.dataset.search||'').toLowerCase().includes(currentSearch.toLowerCase()));"),
    ("btn.classList.add('is-active');currentEra=btn.dataset.era||'';applyFilters();",
     "btn.classList.add('is-active');if(btn.hasAttribute('data-taxo'))"
     "{currentTaxo=btn.getAttribute('data-taxo');currentTaxoKind=btn.getAttribute('data-taxokind')||'m';currentEra='';}"
     "else{currentEra=btn.dataset.era||'';currentTaxo='';}applyFilters();"),
    ("mobileStrip.querySelectorAll('[data-mobile-era]').forEach(b=>b.classList.remove('is-active'));",
     "mobileStrip.querySelectorAll('[data-mobile-era],[data-mobile-taxo]').forEach(b=>b.classList.remove('is-active'));"),
    ("currentEra=eraBtn.dataset.mobileEra||'';\n    document.querySelectorAll('#era-toolbar .pill-era').forEach(b=>b.classList.toggle('is-active',(b.dataset.era||'')===currentEra));",
     "currentEra=eraBtn.dataset.mobileEra||'';currentTaxo='';\n    document.querySelectorAll('#era-toolbar .pill-era[data-era]').forEach(b=>b.classList.toggle('is-active',(b.dataset.era||'')===currentEra));\n    document.querySelectorAll('#era-toolbar .pill-era[data-taxo]').forEach(b=>b.classList.remove('is-active'));"),
    ("    const eraBtn=e.target.closest('[data-mobile-era]');",
     "    const taxoBtn=e.target.closest('[data-mobile-taxo]');\n"
     "    if(taxoBtn){\n"
     "      mobileStrip.querySelectorAll('[data-mobile-era],[data-mobile-taxo]').forEach(b=>b.classList.remove('is-active'));\n"
     "      taxoBtn.classList.add('is-active');currentTaxo=taxoBtn.getAttribute('data-mobile-taxo');currentTaxoKind=taxoBtn.getAttribute('data-mobile-taxokind')||'m';currentEra='';\n"
     "      document.querySelectorAll('#era-toolbar .pill-era[data-era]').forEach(b=>b.classList.remove('is-active'));\n"
     "      document.querySelectorAll('#era-toolbar .pill-era[data-taxo]').forEach(b=>b.classList.toggle('is-active',b.getAttribute('data-taxo')===currentTaxo));\n"
     "      applyFilters();return;\n"
     "    }\n"
     "    const eraBtn=e.target.closest('[data-mobile-era]');"),
]


def add_data_country(text: str) -> str:
    """Add data-country (ISO codes) to each photographer card. Idempotent."""
    def repl(m):
        attrs, gap, pid = m.group(1), m.group(2), m.group(3)
        if "data-country=" in attrs:
            return m.group(0)
        nat = NAT.get(pid, "")
        if not nat:
            return m.group(0)
        return f'{attrs} data-country="{nat}"{gap}'
    return re.sub(
        r'(<article class="pc-card pc-card--photographer"[^>]*?)(>\s*<a href="photographers/([^"]+)\.html")',
        repl, text)


def patch(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    if SCROLL_FROM in text:
        text = text.replace(SCROLL_FROM, SCROLL_TO)
    if "/* taxo-red-label */" not in text:
        text = text.replace("</style>", RED_LABEL + "</style>", 1)

    text = add_data_country(text)

    desk, mob = desktop_block(), mobile_block()
    if "<!-- taxo-nav -->" in text:
        text = re.sub(r"<!-- taxo-nav -->.*?<!-- /taxo-nav -->", desk, text, flags=re.S)
    else:
        m = re.search(r'(<div class="toolbar-era"[^>]*>.*?)(\n?\s*</div>)', text, re.S)
        if not m:
            raise SystemExit("era-toolbar not found")
        text = text[:m.end(1)] + desk + text[m.end(1):]
    if "<!-- taxo-nav-m -->" in text:
        text = re.sub(r"<!-- taxo-nav-m -->.*?<!-- /taxo-nav-m -->", mob, text, flags=re.S)
    else:
        m = re.search(r'(<div class="mobile-filter-strip"[^>]*>.*?)(\n?\s*</div>)', text, re.S)
        if not m:
            raise SystemExit("mobile-filter-strip not found")
        text = text[:m.end(1)] + mob + text[m.end(1):]

    for before, after in JS_EDITS:
        if after in text:
            continue
        if before not in text:
            raise SystemExit(f"JS anchor not found: {before[:60]!r}")
        text = text.replace(before, after, 1)

    path.write_text(text, encoding="utf-8")


def main() -> None:
    patch(REPO / "archive.html")
    print("patched archive.html")


if __name__ == "__main__":
    main()
