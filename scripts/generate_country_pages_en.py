#!/usr/bin/env python3
"""Generate the English v5.1 country hub pages (en/countries/*.html).

Mirrors scripts/generate_country_pages.py (the JA reference) but:
  - EN chrome (header/hero/footer/search) lifted from en/eras/1839.html
  - EN cards sourced from en/archive.html (href /en/photographers/…),
    ledes kept as-is (the whole EN site shows truncated card ledes)
  - EN nav built from the (single-only) registry + card-data nameEn
  - composite pages retired to EN redirect stubs (→ /en/countries/<target>)

data/country-pages.json (single pages only) is the source of truth.
"""
from __future__ import annotations

import glob
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from generate_country_pages import (  # noqa: E402  reuse proven helpers
    extract_articles,
    extract_era_style_block,
    extract_archive_card_css,
    _toks,
    get_members,
    assert_members,
)

EN_ARCHIVE_HREF_RE = re.compile(r'href="/en/photographers/([^"]+)\.html"')

ERA_LABELS = [
    ("1839", "1839–1860s"), ("1870", "1870–1890s"), ("1890", "1890–1910s"),
    ("1910", "1910–1920s"), ("1930", "1930–1940s"), ("1950", "1950–1960s"),
    ("1970", "1970–1980s"), ("1980", "1980–1990s"), ("1990", "1990–2000s"),
    ("2000", "2000–2010s"), ("2010", "2010–2020s"),
]

# Valid EN movement slugs/labels (from the existing EN taxonomy pages)
EN_MOVEMENTS = [
    ("conceptual-art", "Conceptual Art"),
    ("documentary", "Documentary"),
    ("pictorialism", "Pictorialism"),
    ("social-documentary", "Social Documentary"),
    ("i-photography-shi-shashin", "I-Photography (Shi-shashin)"),
    ("decisive-moment", "Decisive Moment"),
    ("photojournalism", "Photojournalism"),
    ("street-photography", "Street Photography"),
]

FEATURED_IDS = ["daguerre", "fenton", "beato", "nadar",
                "stieglitz", "strand", "cartierbresson", "hiroshi-sugimoto"]

CARD_FILTER_JS = """\
<script>
(function(){
  var input=document.getElementById('country-filter');
  if(!input)return;
  var grid=document.getElementById('cards-grid');
  var none=document.getElementById('er-no-result');
  var cards=grid?[].slice.call(grid.querySelectorAll('.pc-card')):[];
  function norm(s){return (s||'').toLowerCase();}
  input.addEventListener('input',function(){
    var q=norm(this.value.trim());var shown=0;
    cards.forEach(function(c){
      var hit=!q||norm(c.textContent).indexOf(q)!==-1;
      c.style.display=hit?'':'none';
      if(hit)shown++;
    });
    if(none)none.style.display=(q&&shown===0)?'block':'none';
  });
})();
</script>"""


# ── card source ────────────────────────────────────────────────────────────

def build_en_archive_lookup(arch_html: str) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for article in extract_articles(arch_html):
        m = EN_ARCHIVE_HREF_RE.search(article)
        if m:
            lookup[m.group(1)] = article
    return lookup


def transform_card_en(article: str, pid: str, code_str: str) -> str:
    r = re.sub(r'<article[^>]*>',
               '<article class="pc-card pc-card--photographer">', article, count=1)
    r = r.replace(f'href="/en/photographers/{pid}.html"',
                  f'href="../photographers/{pid}.html"', 1)
    r = r.replace(' target="_blank"', '', 1)
    r = re.sub(r'(<span class="idx">\d+</span>)<span>PHOTOGRAPHER</span>',
               lambda m: m.group(1) + f'<span>{code_str}</span>', r, count=1)
    return r


# ── EN chrome fragments lifted from en/eras/1839.html ──────────────────────

def extract_mobile_search(era_html: str) -> str:
    m = re.search(r'(<div class="head__mobile-search">.*?</ul>\s*</div>)', era_html, re.S)
    if not m:
        raise RuntimeError("mobile search block not found in EN era page")
    return m.group(1)


def extract_bottom_scripts(era_html: str) -> str:
    m = re.search(r'</div><!-- /\.page -->(.*?)</body>', era_html, re.S)
    if not m:
        raise RuntimeError("bottom scripts not found in EN era page")
    return m.group(1).strip()


# ── nav builders (single pages only) ───────────────────────────────────────

def build_countries_select(singles: list[dict]) -> str:
    opts = ['<option value="" selected>Browse countries</option>']
    for r in sorted(singles, key=lambda r: r["nameEn"]):
        opts.append(f'<option value="/en/countries/{r["slug"]}.html">{r["nameEn"]}</option>')
    return ('<select class="tax-select filter-select nav-select" aria-label="Browse countries" '
            'onchange="if(this.value) window.location.href=this.value">' + "".join(opts) + "</select>")


def build_eras_select() -> str:
    opts = ['<option value="" selected>Browse eras</option>',
            '<option value="/en/archive.html">Browse by Era</option>']
    for y, lbl in ERA_LABELS:
        opts.append(f'<option value="/en/eras/{y}.html">{lbl}</option>')
    return ('<select class="tax-select filter-select nav-select" aria-label="Browse eras" '
            'onchange="if(this.value) window.location.href=this.value">' + "".join(opts) + "</select>")


def build_movements_select() -> str:
    opts = ['<option value="" selected>Related movements</option>']
    for slug, lbl in EN_MOVEMENTS:
        opts.append(f'<option value="/en/movements/{slug}.html">{lbl}</option>')
    return ('<select class="tax-select filter-select nav-select" aria-label="Related movements" '
            'onchange="if(this.value) window.location.href=this.value">' + "".join(opts) + "</select>")


def build_dir_eras() -> str:
    return "".join(f'<a href="/en/eras/{y}.html">{lbl}</a>' for y, lbl in ERA_LABELS)


def build_dir_countries(singles: list[dict]) -> str:
    return "".join(f'<a href="/en/countries/{r["slug"]}.html">{r["nameEn"]}</a>'
                   for r in sorted(singles, key=lambda r: r["nameEn"]))


def build_dir_photographers(card_map: dict[str, dict]) -> str:
    out = []
    for pid in FEATURED_IDS:
        name = card_map.get(pid, {}).get("nameEn", pid)
        out.append(f'<a href="/en/photographers/{pid}.html">{name}</a>')
    return "".join(out)


# ── country overrides CSS (same as JA, EN-labelled comment) ────────────────

COUNTRY_CSS_OVERRIDES = """\
<style>
.country-sticky{position:sticky;top:0;z-index:90;background:var(--bg);}
.country-toolbar{border-bottom:1.5px solid var(--rule-strong);background:var(--surface);}
.country-toolbar .toolbar__search{border-right:0;flex:1;width:100%;}
.country-strip .era-nav__label{white-space:nowrap;}
.er-no-result{display:none;padding:48px 8px;font-family:var(--font-mo);font-size:11px;letter-spacing:0.16em;text-transform:uppercase;color:var(--text-mute);}
@media(max-width:760px){.head{position:static;}}
.head__lang a{padding:4px 10px;color:var(--text-sub);font-family:var(--font-mo);font-size:10px;letter-spacing:0.20em;display:inline-block;}
.head__lang a.is-active{background:var(--text-main);color:var(--rev-text);}
.era-layout--solo{grid-template-columns:1fr;}
.country-hero .era-hero__art-year{font-size:clamp(80px,9vw,128px);letter-spacing:-0.04em;}
.site-directory-links{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:28px;padding:40px 32px;border-top:1.5px solid var(--rule-strong);background:var(--surface-2);}
.site-directory-label{font-family:var(--font-mo);font-size:9px;letter-spacing:0.24em;text-transform:uppercase;color:var(--accent-s);font-weight:500;margin-bottom:12px;}
.site-directory-items{display:flex;flex-wrap:wrap;gap:6px 12px;}
.site-directory-items a{font-family:var(--font-jp);font-size:12px;color:var(--text-sub);transition:color 120ms;}
.site-directory-items a:hover{color:var(--accent-a);}
@media(max-width:768px){.era-layout--solo{max-width:none;}}
@media(max-width:760px){.site-directory-links{padding:28px 16px;grid-template-columns:1fr;}}
</style>"""

GA_BLOCK = ('<script async src="https://www.googletagmanager.com/gtag/js?id=G-2VRTV8BZEJ"></script>\n'
            '<script>window.dataLayer = window.dataLayer || [];function gtag(){dataLayer.push(arguments);}'
            "gtag('js', new Date());gtag('config', 'G-2VRTV8BZEJ');</script>")

GOOGLE_FONTS = (
    '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:'
    'wght@400;500;700;900&family=Noto+Serif+JP:wght@400;500;700&family=Inter:'
    'wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&family='
    'Cormorant+Garamond:ital,wght@1,500;1,600&display=swap" rel="stylesheet">'
)


def render_page(cfg: dict, *, era_style, archive_card_css, mobile_search,
                bottom_scripts, strip_pairs,
                dir_eras, dir_countries, dir_photographers, cards_html,
                member_count) -> str:
    slug = cfg["slug"]
    country_strip = "\n".join(
        f'    <a class="era-nav__item{" is-active" if s == slug else ""}" '
        f'href="/en/countries/{s}.html">{label}</a>'
        for s, label in strip_pairs)
    name_en = cfg["nameEn"]
    name_ja = cfg["nameJa"]
    code = cfg["codes"][0]
    code_str = " / ".join(cfg["codes"])
    art = code[0] + (f'<span>{code[1:]}</span>' if len(code) > 1 else '')
    lead = (f"This page gathers photographers connected to {name_en} and traces how each "
            f"links to a period and movement in the history of photography.")
    title = f"{name_en} Photo History | Photographers and Visual Culture | Photo Coordinates"
    desc = (f"An overview of photographers connected to {name_en}, tracing how they relate "
            f"to movements, eras, and the wider history of photography.")
    canon = f"https://eyescosmos.github.io/en/countries/{slug}.html"
    ja_url = f"https://eyescosmos.github.io/countries/{slug}.html"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="ja" href="{ja_url}">
<link rel="alternate" hreflang="en" href="{canon}">
<link rel="alternate" hreflang="x-default" href="{ja_url}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canon}">
<meta property="og:site_name" content="Photo Coordinates">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://eyescosmos.github.io/assets/ogp-default.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="https://eyescosmos.github.io/assets/ogp-default.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{GOOGLE_FONTS}
<link rel="stylesheet" href="../../styles/card-v4-base.css"><link rel="stylesheet" href="../../styles/card-v5-overrides.css">
{era_style}
{COUNTRY_CSS_OVERRIDES}
{archive_card_css}
{GA_BLOCK}
</head>
<body class="lang-en v51">
<div class="page">

<header class="head" data-nosnippet>
  <div class="head__brand">
    <span class="head__brand-ja"><a href="../index.html"><span class="head__brand-photo">写真</span>の座標</a></span>
    <span class="head__brand-en">Photo Coordinates</span>
  </div>
  <div class="head__crumbs">
    <em>COUNTRIES</em><span class="sep">/</span>{name_en} <span class="sep">·</span>{name_ja} <span class="sep">·</span>UPDATED&nbsp;<span class="updated-date">2026.06</span>
  </div>
  <div class="head__meta">
    <div class="head__lang"><a href="{ja_url}">JP</a><a class="is-active">EN</a></div>
  </div>
{mobile_search}</header>

<section class="era-hero country-hero">
  <div class="era-hero__art">
    <div class="era-hero__art-label">COUNTRY · {name_en}</div>
    <div class="era-hero__art-year">{art}</div>
  </div>
  <div class="era-hero__info">
    <div class="era-hero__eyebrow">§ — Country Index</div>
    <h1 class="era-hero__title">{name_en}</h1>
    <div class="era-hero__period">{name_ja}</div>
    <p class="era-hero__lead">{lead}</p>
    <div class="era-hero__meta-row">
      <span class="era-hero__meta-item">Photographers <strong>{member_count}</strong></span>
      <span class="era-hero__meta-item">Country <strong>{name_en}</strong></span>
      <span class="era-hero__meta-item">Code <strong>{code_str}</strong></span>
      <span class="era-hero__meta-item">Vol <strong>COUNTRY · {code}</strong></span>
    </div>
  </div>
</section>

<!-- ── STICKY: search + browse by country ──────────────────── -->
<div class="country-sticky">
  <div class="country-toolbar" data-nosnippet>
    <label class="toolbar__search">
      <input type="search" id="country-filter" placeholder="Search by name, movement, country, or tag…" autocomplete="off" aria-label="Search photographers in this country">
    </label>
  </div>
  <nav class="era-nav country-strip" data-nosnippet aria-label="Country navigation">
    <div class="era-nav__label">§ — Browse by country</div>
    <div class="era-nav__strip">
{country_strip}
    </div>
  </nav>
</div>

<div class="era-outer">
  <div class="era-layout era-layout--solo">
    <main class="era-main">
      <section class="ph-section">
        <div class="ph-section__head">
          <div class="ph-section__title">
            <span class="ph-section__num">§ PH</span>
            <span class="ph-section__name">Photographers · {name_en}</span>
          </div>
        </div>
        <div class="ph-section__body">
          <div class="cards" id="cards-grid">

{cards_html}

          </div>
          <div class="er-no-result" id="er-no-result">No photographers match your search</div>
        </div>
      </section>
    </main>
  </div><!-- /.era-layout -->
</div><!-- /.era-outer -->

<nav class="site-directory-links" aria-label="Site links" data-nosnippet>
  <div class="site-directory-group">
    <div class="site-directory-label">Era index</div>
    <div class="site-directory-items">{dir_eras}</div>
  </div>
  <div class="site-directory-group">
    <div class="site-directory-label">Country index</div>
    <div class="site-directory-items">{dir_countries}</div>
  </div>
  <div class="site-directory-group">
    <div class="site-directory-label">Featured photographers</div>
    <div class="site-directory-items">{dir_photographers}</div>
  </div>
</nav>

<footer class="foot" data-nosnippet>
  <div>© Photo Coordinates · 写真の座標</div>
  <div class="foot__center">Based on museum, archive, and specialist sources</div>
  <div class="foot__right"><a href="/en/privacy-policy.html">Privacy</a></div>
</footer>

</div><!-- /.page -->
{bottom_scripts}
{CARD_FILTER_JS}
</body>
</html>
"""


STUB = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex,follow">
<title>{target_en} | Photo Coordinates</title>
<link rel="canonical" href="https://eyescosmos.github.io/en/countries/{target}.html">
<meta http-equiv="refresh" content="0; url=/en/countries/{target}.html">
</head>
<body>
<p>This page has been merged into <a href="/en/countries/{target}.html">{target_en} — Photographers</a>. Redirecting…</p>
</body>
</html>
"""


def main() -> None:
    registry = json.loads((REPO / "data" / "country-pages.json").read_text(encoding="utf-8"))
    singles = {r["slug"]: r for r in registry}
    card_data = json.loads((REPO / "card-data.json").read_text(encoding="utf-8"))["photographers"]
    card_map = {p["id"]: p for p in card_data}

    era_html = (REPO / "en" / "eras" / "1839.html").read_text(encoding="utf-8")
    era_style = extract_era_style_block(era_html)
    mobile_search = extract_mobile_search(era_html)
    bottom_scripts = extract_bottom_scripts(era_html)

    arch_html = (REPO / "en" / "archive.html").read_text(encoding="utf-8")
    archive_lookup = build_en_archive_lookup(arch_html)
    archive_card_css = extract_archive_card_css(arch_html)

    # Ordered (slug, nameEn) pairs for the horizontal "Browse by country" strip
    strip_pairs = sorted(((r["slug"], r["nameEn"]) for r in registry), key=lambda x: x[1])
    dir_eras = build_dir_eras()
    dir_countries = build_dir_countries(list(registry))
    dir_photographers = build_dir_photographers(card_map)

    # ── retire composite EN pages (mirror JA stub targets) ──
    en_files = {Path(f).stem for f in glob.glob(str(REPO / "en" / "countries" / "*.html"))
                if not f.endswith("-backup.html")}
    composites = sorted(en_files - set(singles))
    stub_n = 0
    for cslug in composites:
        ja_stub = (REPO / "countries" / f"{cslug}.html").read_text(encoding="utf-8")
        m = re.search(r"url=/countries/([^\"']+)\.html", ja_stub)
        if not m:
            raise SystemExit(f"Cannot resolve JA redirect target for {cslug}")
        target = m.group(1)
        target_en = singles[target]["nameEn"]
        (REPO / "en" / "countries" / f"{cslug}.html").write_text(
            STUB.format(target=target, target_en=target_en), encoding="utf-8")
        stub_n += 1

    # ── generate single EN pages ──
    page_n = 0
    for cfg in registry:
        members = get_members(cfg, card_data)
        assert_members(cfg, members)
        cards = []
        for p in members:
            art = archive_lookup.get(p["id"])
            if not art:
                print(f"WARN: {p['id']} missing in en/archive.html", file=sys.stderr)
                continue
            nat = p.get("nationality") or cfg["codes"][0]
            cards.append(transform_card_en(art, p["id"], nat))
        html = render_page(cfg, era_style=era_style, archive_card_css=archive_card_css,
                           mobile_search=mobile_search, bottom_scripts=bottom_scripts,
                           strip_pairs=strip_pairs, dir_eras=dir_eras,
                           dir_countries=dir_countries, dir_photographers=dir_photographers,
                           cards_html="\n".join(cards), member_count=len(members))
        (REPO / "en" / "countries" / f"{cfg['slug']}.html").write_text(html, encoding="utf-8")
        page_n += 1

    print(f"EN: {stub_n} composite stubs, {page_n} single pages generated")


if __name__ == "__main__":
    main()
