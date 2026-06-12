#!/usr/bin/env python3
"""
harvest_photographers_en.py
Extract English content from old-design EN photographer pages into JSON.
Usage: python3 scripts/harvest_photographers_en.py
Output: data/photographers-en-content.json
"""

import os
import re
import json
import glob
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
EN_DIR = os.path.join(REPO_ROOT, "en", "photographers")
OUTPUT_FILE = os.path.join(REPO_ROOT, "data", "photographers-en-content.json")

# ---------------------------------------------------------------------------
# Helpers: balanced-tag extraction
# ---------------------------------------------------------------------------

def extract_balanced(html: str, start_re: str, tag: str):
    """
    Find the first match of start_re, then collect until the matching closing
    tag (counting nested open/close of `tag`).  Returns the full element text
    including opening and closing tags, or None.
    """
    m = re.search(start_re, html, re.IGNORECASE | re.DOTALL)
    if not m:
        return None
    pos = m.start()
    open_pat = re.compile(r'<' + re.escape(tag) + r'(?:\s[^>]*)?>',
                          re.IGNORECASE)
    close_pat = re.compile(r'</' + re.escape(tag) + r'\s*>',
                           re.IGNORECASE)
    depth = 0
    i = pos
    end = len(html)
    while i < end:
        om = open_pat.match(html, i)
        cm = close_pat.match(html, i)
        if om and (not cm or om.start() <= cm.start()):
            depth += 1
            i = om.end()
        elif cm:
            depth -= 1
            i = cm.end()
            if depth == 0:
                return html[pos:i]
        else:
            i += 1
    return None  # unbalanced


def inner_html(outer: str, tag: str) -> str:
    """Return content between first open tag and last close tag of `tag`."""
    if not outer:
        return ""
    m_open = re.search(r'<' + re.escape(tag) + r'(?:\s[^>]*)?>',
                       outer, re.IGNORECASE)
    m_close_iter = list(re.finditer(r'</' + re.escape(tag) + r'\s*>',
                                    outer, re.IGNORECASE))
    if not m_open or not m_close_iter:
        return outer
    return outer[m_open.end(): m_close_iter[-1].start()]


def text_of(html: str) -> str:
    """Strip HTML tags and decode common entities."""
    t = re.sub(r'<[^>]+>', '', html)
    t = t.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>') \
         .replace('&quot;', '"').replace('&#39;', "'") \
         .replace('&#x27;', "'").replace('&nbsp;', ' ')
    t = re.sub(r'\s+', ' ', t).strip()
    return t


# ---------------------------------------------------------------------------
# Per-file parser
# ---------------------------------------------------------------------------

def parse_file(path: str) -> tuple[dict, list[str]]:
    """
    Parse one HTML file and return (data_dict, warnings_list).
    """
    warnings: list[str] = []
    fname = os.path.basename(path)

    with open(path, encoding='utf-8', errors='replace') as fh:
        html = fh.read()

    data: dict = {}

    # ---- <title> -----------------------------------------------------------
    m = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    data['title'] = text_of(m.group(1)) if m else None

    # ---- meta description --------------------------------------------------
    m = re.search(r'<meta\s[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']',
                  html, re.IGNORECASE)
    if not m:
        m = re.search(r'<meta\s[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']description["\']',
                      html, re.IGNORECASE)
    data['meta_description'] = m.group(1) if m else None

    # ---- canonical ---------------------------------------------------------
    m = re.search(r'<link\s[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']',
                  html, re.IGNORECASE)
    if not m:
        m = re.search(r'<link\s[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\']canonical["\']',
                      html, re.IGNORECASE)
    data['canonical'] = m.group(1) if m else None

    # ---- hreflang ----------------------------------------------------------
    hreflang: dict = {}
    for m in re.finditer(
            r'<link\s[^>]*rel=["\']alternate["\'][^>]*hreflang=["\']([^"\']+)["\'][^>]*href=["\']([^"\']+)["\']',
            html, re.IGNORECASE):
        hreflang[m.group(1)] = m.group(2)
    for m in re.finditer(
            r'<link\s[^>]*href=["\']([^"\']+)["\'][^>]*hreflang=["\']([^"\']+)["\'][^>]*rel=["\']alternate["\']',
            html, re.IGNORECASE):
        hreflang[m.group(2)] = m.group(1)
    data['hreflang'] = hreflang

    # ---- og / twitter metas ------------------------------------------------
    og: dict = {}
    for m in re.finditer(
            r'<meta\s[^>]*property=["\']og:([^"\']+)["\'][^>]*content=["\']([^"\']*)["\']',
            html, re.IGNORECASE):
        og[m.group(1)] = m.group(2)
    for m in re.finditer(
            r'<meta\s[^>]*content=["\']([^"\']*)["\'][^>]*property=["\']og:([^"\']+)["\']',
            html, re.IGNORECASE):
        og[m.group(2)] = m.group(1)
    data['og'] = og

    twitter: dict = {}
    for m in re.finditer(
            r'<meta\s[^>]*name=["\']twitter:([^"\']+)["\'][^>]*content=["\']([^"\']*)["\']',
            html, re.IGNORECASE):
        twitter[m.group(1)] = m.group(2)
    for m in re.finditer(
            r'<meta\s[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']twitter:([^"\']+)["\']',
            html, re.IGNORECASE):
        twitter[m.group(2)] = m.group(1)
    data['twitter'] = twitter

    # ---- GA present --------------------------------------------------------
    data['has_ga'] = 'googletagmanager' in html

    # ---- h1.title ----------------------------------------------------------
    m = re.search(r'<h1\s[^>]*class=["\'][^"\']*\btitle\b[^"\']*["\'][^>]*>(.*?)</h1>',
                  html, re.IGNORECASE | re.DOTALL)
    data['h1'] = text_of(m.group(1)) if m else None
    if not data['h1']:
        warnings.append(f"{fname}: missing h1.title")

    # ---- years -------------------------------------------------------------
    years_val = None
    # span.years near h1
    m = re.search(r'<span\s[^>]*class=["\'][^"\']*\byears\b[^"\']*["\'][^>]*>(.*?)</span>',
                  html, re.IGNORECASE | re.DOTALL)
    if m:
        years_val = text_of(m.group(1)).strip()
    # fallback: entry-meta dt=Years dd=...
    if not years_val:
        m = re.search(r'<dt>Years</dt>\s*<dd>(.*?)</dd>', html,
                      re.IGNORECASE | re.DOTALL)
        if m:
            years_val = text_of(m.group(1)).strip()
        # also try inside info-group / fact-item
        if not years_val:
            m = re.search(r'<span class=["\']fact-label["\']>Years</span>.*?<span class=["\']fact-value["\']>(.*?)</span>',
                          html, re.IGNORECASE | re.DOTALL)
            if m:
                v = text_of(m.group(1)).strip()
                if v and v != '—':
                    years_val = v
    data['years'] = years_val if years_val and years_val.strip() not in ('', '—') else None

    # ---- entry-meta --------------------------------------------------------
    entry_meta_html = extract_balanced(html, r'<dl\s[^>]*class=["\'][^"\']*entry-meta[^"\']*["\']', 'dl')
    data['entry_meta_html'] = entry_meta_html

    # ---- lead-abstract (or plain p.lead) -----------------------------------
    lead_outer = extract_balanced(html, r'<div\s[^>]*class=["\'][^"\']*lead-abstract[^"\']*["\']', 'div')
    lead_html = None
    if lead_outer:
        inner = inner_html(lead_outer, 'div')
        # Strip leading abstract-label div if present
        inner = re.sub(r'^\s*<div\s[^>]*class=["\'][^"\']*abstract-label[^"\']*["\'][^>]*>.*?</div>\s*',
                       '', inner, flags=re.IGNORECASE | re.DOTALL)
        lead_html = inner.strip()
    if not lead_html:
        # Fallback: <p class="lead"> (most older pages)
        m = re.search(r'<p\s[^>]*class=["\'][^"\']*\blead\b[^"\']*["\'][^>]*>(.*?)</p>',
                      html, re.IGNORECASE | re.DOTALL)
        if m:
            lead_html = m.group(0).strip()
    data['lead_html'] = lead_html
    if not lead_html:
        warnings.append(f"{fname}: missing lead-abstract")

    # ---- thesis ------------------------------------------------------------
    thesis_outer = extract_balanced(html, r'<div\s[^>]*class=["\'][^"\']*\bthesis\b[^"\']*["\']', 'div')
    thesis_label = None
    thesis_html = None
    if thesis_outer:
        m = re.search(r'<div\s[^>]*class=["\'][^"\']*thesis-label[^"\']*["\'][^>]*>(.*?)</div>',
                      thesis_outer, re.IGNORECASE | re.DOTALL)
        if m:
            thesis_label = text_of(m.group(1))
        m = re.search(r'<p\s[^>]*class=["\'][^"\']*thesis-body[^"\']*["\'][^>]*>(.*?)</p>',
                      thesis_outer, re.IGNORECASE | re.DOTALL)
        if m:
            thesis_html = m.group(1).strip()
    data['thesis_label'] = thesis_label
    data['thesis_html'] = thesis_html

    # ---- page-keywords -----------------------------------------------------
    kw_outer = extract_balanced(html, r'<div\s[^>]*class=["\'][^"\']*page-keywords[^"\']*["\']', 'div')
    data['keywords_html'] = kw_outer

    # ---- view-works section ------------------------------------------------
    # Normalize: section with h2 containing "view works" (case-insensitive)
    view_works_note = None
    view_works_links_html = None
    # Find the section
    vw_match = re.search(
        r'<section\s[^>]*class=["\'][^"\']*\bsection\b[^"\']*view-works-section[^"\']*["\'][^>]*>',
        html, re.IGNORECASE)
    if not vw_match:
        # Try by h2 content
        vw_match = re.search(
            r'<section\s[^>]*class=["\'][^"\']*\bsection\b[^"\']*["\'][^>]*>(?:(?!</section>).)*?<h2[^>]*>\s*[Vv]iew\s+[Ww]orks?\s*</h2>',
            html, re.IGNORECASE | re.DOTALL)
    if vw_match:
        vw_section = extract_balanced(html[vw_match.start():],
                                      r'<section', 'section')
        if vw_section:
            m = re.search(r'<p\s[^>]*class=["\'][^"\']*view-works-note[^"\']*["\'][^>]*>(.*?)</p>',
                          vw_section, re.IGNORECASE | re.DOTALL)
            if m:
                view_works_note = text_of(m.group(1))
            links_outer = extract_balanced(vw_section, r'<div\s[^>]*class=["\'][^"\']*\blinks\b[^"\']*["\']', 'div')
            view_works_links_html = links_outer
    data['view_works_note'] = view_works_note
    data['view_works_links_html'] = view_works_links_html

    # ---- Main essay sections -----------------------------------------------
    # Identify section-grid or page-shell and collect <section class="section"> children
    # Approach: iterate all <section class="section"> in html, classify by h2 text.

    SKIP_H2_PATTERNS = [
        r'^view\s+works?$',
        r'photobooks?$',
        r'^external\s+links?$',
        r'^notable\s+works?$',
        r'^sources?$',
        r'^further\s+reading$',
    ]

    sections: list[dict] = []
    photobooks_html = None
    external_links_html = None
    notable_works_html = None
    further_reading_html = None
    sources_html = None

    # Find each <section class="section"...>
    sec_iter = re.finditer(
        r'<section\s[^>]*class=["\'][^"\']*\bsection\b[^"\']*["\'][^>]*>',
        html, re.IGNORECASE)

    for sec_start_m in sec_iter:
        sec_text = extract_balanced(html[sec_start_m.start():],
                                    r'<section', 'section')
        if not sec_text:
            continue

        # Get h2 text
        h2_m = re.search(r'<h2[^>]*>(.*?)</h2>', sec_text,
                         re.IGNORECASE | re.DOTALL)
        h2_raw = h2_m.group(1) if h2_m else ''
        h2_text = text_of(h2_raw).strip()

        # Classify
        h2_lower = h2_text.lower().strip()

        if re.search(r'^view\s+works?$', h2_lower, re.IGNORECASE):
            # already handled above
            continue

        if re.search(r'photobooks?', h2_lower, re.IGNORECASE):
            photobooks_html = sec_text
            continue

        if re.search(r'^external\s+links?$', h2_lower, re.IGNORECASE):
            links_outer = extract_balanced(sec_text,
                                           r'<div\s[^>]*class=["\'][^"\']*\blinks\b[^"\']*["\']', 'div')
            external_links_html = links_outer
            continue

        if re.search(r'^notable\s+works?$', h2_lower, re.IGNORECASE):
            links_outer = extract_balanced(sec_text,
                                           r'<div\s[^>]*class=["\'][^"\']*\blinks\b[^"\']*["\']', 'div')
            notable_works_html = links_outer
            continue

        if re.search(r'^further\s+reading$', h2_lower, re.IGNORECASE):
            further_reading_html = inner_html(sec_text, 'section')
            continue

        if re.search(r'^sources?$', h2_lower, re.IGNORECASE):
            sources_outer = extract_balanced(sec_text,
                                             r'<div\s[^>]*class=["\'][^"\']*\bsources\b[^"\']*["\']', 'div')
            sources_html = sources_outer
            continue

        # Essay section: parse num / title from sec-heading or plain h2
        sec_num = None
        sec_title = None
        h2_full = h2_m.group(0) if h2_m else ''
        num_m = re.search(r'<span\s[^>]*class=["\'][^"\']*sec-num[^"\']*["\'][^>]*>(.*?)</span>',
                          h2_full, re.IGNORECASE | re.DOTALL)
        title_m = re.search(r'<span\s[^>]*class=["\'][^"\']*sec-title[^"\']*["\'][^>]*>(.*?)</span>',
                            h2_full, re.IGNORECASE | re.DOTALL)
        if num_m:
            sec_num = text_of(num_m.group(1)).strip()
        if title_m:
            sec_title = text_of(title_m.group(1)).strip()
        else:
            # plain h2
            sec_title = text_of(h2_raw).strip()

        # body_html = everything after the h2 tag within sec_text
        body_start = h2_m.end() if h2_m else 0
        body_html = sec_text[body_start:].strip()
        # Remove trailing </section>
        body_html = re.sub(r'\s*</section>\s*$', '', body_html, flags=re.IGNORECASE).strip()

        sections.append({
            'num': sec_num,
            'title': sec_title,
            'body_html': body_html,
        })

    data['sections'] = sections
    if not sections:
        warnings.append(f"{fname}: no essay sections found")

    data['photobooks_html'] = photobooks_html
    data['external_links_html'] = external_links_html
    data['notable_works_html'] = notable_works_html
    data['further_reading_html'] = further_reading_html
    data['sources_html'] = sources_html

    if not sources_html:
        warnings.append(f"{fname}: missing sources section")

    # ---- cite_ids ----------------------------------------------------------
    cite_ids = sorted(set(int(m) for m in re.findall(
        r'id=["\']cite-(\d+)["\']', html, re.IGNORECASE)))
    data['cite_ids'] = cite_ids

    # ---- supref_ids (from body sections only) ------------------------------
    body_text = ' '.join(s.get('body_html', '') for s in sections)
    supref_ids = sorted(set(int(m) for m in re.findall(
        r'href=["\']#cite-(\d+)["\']', body_text, re.IGNORECASE)))
    data['supref_ids'] = supref_ids

    # Warn if suprefs not subset of cites
    missing_cites = set(supref_ids) - set(cite_ids)
    if missing_cites:
        warnings.append(f"{fname}: supref_ids {sorted(missing_cites)} not in cite_ids")

    # ---- site-directory-links ----------------------------------------------
    site_dir = extract_balanced(html, r'<nav\s[^>]*class=["\'][^"\']*site-directory-links[^"\']*["\']', 'nav')
    data['site_directory_html'] = site_dir

    # ---- footer ------------------------------------------------------------
    footer_html = extract_balanced(html, r'<footer\s[^>]*class=["\'][^"\']*site-footer[^"\']*["\']', 'footer')
    data['footer_html'] = footer_html

    # ---- JSON-LD -----------------------------------------------------------
    jsonld_list = re.findall(
        r'<script\s[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.IGNORECASE | re.DOTALL)
    data['jsonld'] = [j.strip() for j in jsonld_list]

    return data, warnings


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    files = sorted(glob.glob(os.path.join(EN_DIR, '*.html')))
    # Exclude stieglitz-backup.html
    files = [f for f in files if os.path.basename(f) != 'stieglitz-backup.html']

    pages: dict = {}
    all_warnings: list[str] = []
    section_title_counts: dict[str, int] = {}

    for path in files:
        fname = os.path.basename(path)
        data, warnings = parse_file(path)
        pages[fname] = data
        all_warnings.extend(warnings)
        for sec in data.get('sections', []):
            t = sec.get('title') or ''
            if t:
                section_title_counts[t] = section_title_counts.get(t, 0) + 1

    total = len(pages)
    with_lead = sum(1 for p in pages.values() if p.get('lead_html'))
    with_thesis = sum(1 for p in pages.values() if p.get('thesis_html'))
    with_sections = sum(1 for p in pages.values() if p.get('sections'))
    with_sources = sum(1 for p in pages.values() if p.get('sources_html'))
    with_photobooks = sum(1 for p in pages.values() if p.get('photobooks_html'))
    with_notable_works = sum(1 for p in pages.values() if p.get('notable_works_html'))

    meta = {
        'count': total,
        'harvested_at': datetime.now(timezone.utc).isoformat(),
        'stats': {
            'with_lead': with_lead,
            'with_thesis': with_thesis,
            'with_sections_ge1': with_sections,
            'with_sources': with_sources,
            'with_photobooks': with_photobooks,
            'with_notable_works': with_notable_works,
        },
        'top_section_titles': sorted(section_title_counts.items(), key=lambda x: -x[1])[:10],
        'warning_count': len(all_warnings),
        'warnings': all_warnings,
    }

    output = {'_meta': meta, 'pages': pages}

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as fh:
        json.dump(output, fh, ensure_ascii=False, indent=2)

    size_bytes = os.path.getsize(OUTPUT_FILE)
    size_mb = size_bytes / (1024 * 1024)

    print(f"\n=== Harvest complete ===")
    print(f"Total pages harvested : {total}")
    print(f"With lead             : {with_lead}")
    print(f"With thesis           : {with_thesis}")
    print(f"With sections >= 1    : {with_sections}")
    print(f"With sources          : {with_sources}")
    print(f"With photobooks       : {with_photobooks}")
    print(f"With notable_works    : {with_notable_works}")
    print()
    print("Top 10 section titles:")
    for title, count in sorted(section_title_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {count:4d}  {title}")
    print()
    print(f"Warnings              : {len(all_warnings)}")
    print("First 20 warnings:")
    for w in all_warnings[:20]:
        print(f"  {w}")
    print()
    print(f"Output file           : {OUTPUT_FILE}")
    print(f"Output size           : {size_bytes:,} bytes ({size_mb:.2f} MB)")
    print()
    print("3 example keys:")
    example_keys = list(pages.keys())[:3]
    for k in example_keys:
        p = pages[k]
        print(f"  {k}: h1={p.get('h1')!r}, sections={len(p.get('sections', []))}, "
              f"cite_ids_count={len(p.get('cite_ids', []))}")


if __name__ == '__main__':
    main()
