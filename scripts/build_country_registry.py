#!/usr/bin/env python3
"""One-time bootstrap: derive the country-page registry from the existing
(old-design) country HTML pages + card-data.json, and write it to
data/country-pages.json.

After the country pages are migrated to v5.1 this script can no longer
re-derive (the old <h1 class="title">…の写真史</h1> markup is gone), so
data/country-pages.json becomes the SOURCE OF TRUTH consumed by
scripts/generate_country_pages.py. Do not re-run this after migration.
"""
from __future__ import annotations

import glob
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def toks(v: str) -> set[str]:
    return {t.strip() for t in v.split('/') if t.strip()}


def main() -> None:
    card = json.loads((REPO / 'card-data.json').read_text(encoding='utf-8'))['photographers']
    nat_by_id = {p['id']: (p.get('nationality') or '') for p in card}

    # ── pass 1: read every old country page → nameJa + code set + old members
    pages: dict[str, dict] = {}
    for f in sorted(glob.glob(str(REPO / 'countries' / '*.html'))):
        if f.endswith('-backup.html'):
            continue
        slug = Path(f).stem
        h = Path(f).read_text(encoding='utf-8')
        m = re.search(r'<h1 class="title">(.*?)の写真史</h1>', h)
        nameja = m.group(1) if m else None
        ids = re.findall(r'class="archive-list-link" href="/photographers/([^"]+)\.html"', h)
        seen: list[str] = []
        for i in ids:
            if i not in seen:
                seen.append(i)
        ts = [toks(nat_by_id.get(i, '')) for i in seen if nat_by_id.get(i)]
        inter = set.intersection(*ts) if ts else set()
        pages[slug] = {'nameja': nameja, 'codeset': inter, 'old': seen}

    # france is already migrated → seed it explicitly (old markup gone)
    pages['france'] = {'nameja': 'フランス', 'codeset': {'FR'}, 'old': None}

    # ── single-code maps (code → slug / nameJa / nameEn)
    code_slug: dict[str, str] = {}
    code_ja: dict[str, str] = {}
    code_en: dict[str, str] = {}
    for slug, d in pages.items():
        if len(d['codeset']) == 1:
            c = next(iter(d['codeset']))
            code_slug[c] = slug
            code_ja[c] = d['nameja']
            code_en[c] = slug.replace('-', ' ').title()

    # ── derive atoms that only appear inside composite pages (one novel code each)
    for slug, d in pages.items():
        if len(d['codeset']) == 2:
            cs = d['codeset']
            known = [c for c in cs if c in code_slug]
            unknown = [c for c in cs if c not in code_slug]
            if len(known) == 1 and len(unknown) == 1:
                ks = code_slug[known[0]]
                u = unknown[0]
                if slug.startswith(ks + '-'):
                    us = slug[len(ks) + 1:]
                elif slug.endswith('-' + ks):
                    us = slug[:-(len(ks) + 1)]
                else:
                    us = slug.replace(ks, '').strip('-')
                code_slug[u] = us
                code_en[u] = us.replace('-', ' ').title()
                if d['nameja'] and ' / ' in d['nameja']:
                    parts = d['nameja'].split(' / ')
                    if known[0] in code_ja and code_ja[known[0]] in parts:
                        rest = [p for p in parts if p != code_ja[known[0]]]
                        if rest:
                            code_ja.setdefault(u, rest[0])

    def ordered_codes(slug: str, d: dict) -> list[str]:
        cs = d['codeset']
        if len(cs) == 1:
            return [next(iter(cs))]
        for i in (d['old'] or []):
            v = nat_by_id.get(i, '')
            tk = [t.strip() for t in v.split('/')]
            if set(tk) == cs:
                return tk
        return sorted(cs)

    FRANCE_LEAD = ("フランスに関わる写真家を、写真の発明から現代美術まで、"
                   "各作家がどの時代・運動と結びつくのかとともにたどるページです。")

    registry = []
    for slug, d in sorted(pages.items()):
        oc = ordered_codes(slug, d)
        name_ja = d['nameja']
        name_en = ' / '.join(code_en.get(c, '?' + c) for c in oc)
        if slug == 'france':
            lead = FRANCE_LEAD
        elif len(oc) == 1:
            lead = (f"{name_ja}に関わる写真家を、各作家がどの時代・運動と"
                    f"結びつくのかとともにたどるページです。")
        else:
            lead = (f"{name_ja}にまたがる写真家を、各作家がどの時代・運動と"
                    f"結びつくのかとともにたどるページです。")
        registry.append({
            'slug': slug,
            'codes': oc,
            'nameJa': name_ja,
            'nameEn': name_en,
            'lead': lead,
            'updated': '2026.06',
        })

    out = REPO / 'data' / 'country-pages.json'
    out.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n',
                   encoding='utf-8')
    print(f"Wrote {out} with {len(registry)} country pages")
    # sanity
    miss = [r['slug'] for r in registry if not r['nameJa'] or '?' in r['nameEn']]
    if miss:
        print("WARN: incomplete entries:", miss)


if __name__ == '__main__':
    main()
