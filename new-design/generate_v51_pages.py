#!/usr/bin/env python3
"""
v5.1 photographer page generator
Reads card-data.json + photographers/*.html → outputs new-design/xxx.html
"""

import html as html_lib
import json, os, re, sys
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString, Tag

SITE_ROOT = 'https://eyescosmos.github.io'
DEFAULT_DESC = '「写真の座標」は美術館・アーカイブ・専門資料をもとに、写真家と写真史を読むサイトです。'
RUN_DATE = datetime.now().strftime('%Y.%m.%d')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARD_DATA     = os.path.join(BASE, 'new-design', 'card-data.json')
OVERRIDES_JS  = os.path.join(BASE, 'data', 'photographer-essay-overrides.js')
SRC_DIR       = os.path.join(BASE, 'photographers')
OUT_DIR       = os.path.join(BASE, 'new-design')

SKIP_IDS = {'stieglitz', 'ansel-adams'}  # already hand-crafted

ERA_LABELS = {
    '1839': '1839–1860s', '1870': '1870–1890s', '1890': '1890–1910s',
    '1910': '1910–1920s', '1930': '1930–1940s', '1950': '1950–1960s',
    '1970': '1970–1980s', '1980': '1980–1990s', '1990': '1990–2000s',
    '2000': '2000–2010s', '2010': '2010–2020s',
}

SECTION_MAP = {
    '経歴':     '背景と時代',
    '表現解説': '表現の核心',
    '批評と受容': '批評と写真史上の位置',
}

SKIP_H2_KEYWORDS = ['写真集', '外部リンク', '関連作品', '出典', 'さらに読む', 'Sources']

CSS = r"""
/* ============================================================
   写真の座標 v5.1 — 写真家ページ (generated)
   ============================================================ */
:root{
  --bg:#fafaf5;--surface:#ffffff;--surface-2:#f0ede5;
  --text-main:#0e0c0a;--text-sub:#5a554d;--text-mute:#8a8478;--text-deep:#b8b0a4;
  --border:#0e0c0a;--border-soft:#c4bcb0;
  --rule:var(--border-soft);--rule-strong:var(--border);
  --accent-s:#0a2540;--accent-a:#a83a2a;--accent-d:#d6402e;--accent-h:#ccff00;
  --rev-bg:#0e0c0a;--rev-text:#f2efe8;
  --font-jp:'Noto Sans JP','Hiragino Kaku Gothic ProN',system-ui,sans-serif;
  --font-en:'Inter','Helvetica Neue',Helvetica,Arial,sans-serif;
  --font-mo:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;
  --font-se:'Cormorant Garamond','Times New Roman',serif;
  --font-se-jp:'Noto Serif JP','Hiragino Mincho ProN','Yu Mincho','YuMincho',serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html{scroll-behavior:smooth;}
body{background:var(--bg);color:var(--text-main);font-family:var(--font-jp);font-feature-settings:"palt" 1;font-size:17px;line-height:1.85;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;}
a{color:inherit;text-decoration:none;}
img{display:block;max-width:100%;}
button{font-family:inherit;cursor:pointer;background:transparent;border:0;color:inherit;}
::selection{background:var(--rev-bg);color:var(--rev-text);}
.page{max-width:1440px;margin:0 auto;background:var(--bg);}
/* HEADER */
.head{display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:24px;padding:16px 32px;border-bottom:1.5px solid var(--rule-strong);background:var(--bg);}
.head__brand{display:inline-flex;align-items:baseline;gap:12px;}
.head__brand-ja{font-family:var(--font-jp);font-weight:700;font-size:18px;letter-spacing:0.10em;}
.head__brand-ja a{color:var(--text-main);}
.head__brand-photo{background:var(--accent-d);color:#fff;padding:0 0.05em;border-radius:2px;display:inline-block;line-height:0.96;}
.head__brand-en{font-family:var(--font-en);font-weight:500;font-size:12px;letter-spacing:0.02em;color:var(--text-sub);}
.head__crumbs{font-family:var(--font-mo);font-size:10px;letter-spacing:0.24em;text-transform:uppercase;color:var(--text-mute);text-align:center;}
.head__crumbs em{font-style:normal;color:var(--accent-s);font-weight:500;}
.head__crumbs .sep{color:var(--text-deep);margin:0 10px;}
.updated-date{background:var(--accent-h);color:var(--text-main);padding:1px 6px;border-radius:2px;letter-spacing:0.16em;font-weight:500;}
.head__meta{display:flex;align-items:center;gap:16px;}
.head__lang{display:inline-flex;border:1px solid var(--border);border-radius:2px;overflow:hidden;}
.head__lang button{padding:4px 10px;color:var(--text-sub);font-family:var(--font-mo);font-size:10px;letter-spacing:0.20em;}
.head__lang button.is-active{background:var(--text-main);color:var(--rev-text);}
/* HERO */
.ph-hero{display:grid;grid-template-columns:360px 1fr;border-bottom:1.5px solid var(--rule-strong);min-height:300px;}
.ph-hero__art{background:var(--rev-bg);display:flex;align-items:center;justify-content:center;font-family:var(--font-en);font-weight:800;font-size:clamp(130px,15vw,210px);line-height:0.82;letter-spacing:-0.065em;color:var(--rev-text);border-right:1.5px solid var(--rule-strong);user-select:none;flex-shrink:0;}
.ph-hero__art span{color:var(--accent-d);}
.ph-hero__info{padding:36px 48px;display:flex;flex-direction:column;justify-content:center;gap:16px;background:var(--surface);}
.ph-hero__eyebrow{display:flex;align-items:center;gap:14px;font-family:var(--font-mo);font-size:10px;letter-spacing:0.26em;text-transform:uppercase;color:var(--accent-s);font-weight:500;}
.ph-hero__eyebrow::before{content:'';width:40px;height:1.5px;background:var(--accent-s);flex-shrink:0;}
.ph-hero__name{font-family:var(--font-jp);font-weight:700;font-size:clamp(28px,3.2vw,50px);letter-spacing:0.04em;line-height:1.1;}
.ph-hero__en{font-family:var(--font-se);font-style:italic;font-weight:500;font-size:22px;color:var(--accent-a);display:flex;align-items:baseline;gap:16px;}
.ph-hero__years{font-family:var(--font-mo);font-style:normal;font-size:13px;letter-spacing:0.14em;color:var(--text-mute);}
.ph-hero__meta-row{display:flex;flex-wrap:wrap;gap:0;font-family:var(--font-mo);font-size:10px;letter-spacing:0.20em;text-transform:uppercase;color:var(--text-mute);padding-top:14px;border-top:1px solid var(--rule);}
.ph-hero__meta-item{padding-right:20px;margin-right:20px;border-right:1px solid var(--border-soft);line-height:1.6;}
.ph-hero__meta-item:last-child{border-right:0;padding-right:0;margin-right:0;}
.ph-hero__meta-item strong{color:var(--text-main);font-weight:500;margin-left:4px;}
/* LAYOUT */
.ph-outer{background:var(--surface);border-bottom:1.5px solid var(--rule-strong);}
.ph-layout{max-width:1200px;margin:0 auto;padding:52px 32px 96px;display:grid;grid-template-columns:1fr 284px;gap:52px;align-items:start;}
.ph-main{display:grid;gap:18px;min-width:0;}
/* ABSTRACT */
.ph-abstract{border-left:4px solid var(--accent-h);padding:16px 22px;background:var(--surface-2);}
.ph-abstract__label{font-family:var(--font-mo);font-size:9px;letter-spacing:0.28em;text-transform:uppercase;color:var(--accent-s);font-weight:500;margin-bottom:10px;}
.ph-abstract p{font-size:17px;line-height:1.95;max-width:42em;text-align:justify;text-wrap:pretty;font-family:var(--font-se-jp);}
.ph-abstract a{color:var(--accent-a);border-bottom:1px solid rgba(168,58,42,0.4);}
.ph-abstract a:hover{border-bottom-color:var(--accent-a);}
/* THESIS */
.ph-thesis{border:1.5px solid var(--border);padding:0;background:var(--bg);}
.ph-thesis__label{font-family:var(--font-mo);font-size:9px;letter-spacing:0.26em;text-transform:uppercase;color:var(--accent-s);font-weight:500;padding:12px 24px;border-bottom:1.5px solid var(--border);background:var(--surface-2);display:flex;align-items:center;gap:12px;}
.ph-thesis__label::before{content:'';width:28px;height:1.5px;background:var(--accent-s);}
.ph-thesis__body{padding:22px 24px 24px;font-size:17px;line-height:1.95;max-width:42em;text-align:justify;text-wrap:pretty;font-family:var(--font-se-jp);}
.ph-thesis__body em{font-style:normal;font-weight:700;color:var(--accent-a);}
.ph-thesis__body.is-prep{color:var(--text-mute);font-style:italic;}
/* ENTRY META */
.ph-entry-meta{display:grid;grid-template-columns:auto 1fr auto 1fr;gap:4px 16px;padding:11px 16px;border:1px solid var(--border-soft);background:var(--surface-2);font-family:var(--font-mo);font-size:11px;}
.ph-entry-meta dt{color:var(--text-mute);text-transform:uppercase;letter-spacing:0.10em;font-size:9px;padding-top:3px;white-space:nowrap;}
.ph-entry-meta dd{margin:0;color:var(--text-sub);}
.ph-entry-meta dd a{color:var(--accent-a);}
@media(max-width:680px){.ph-entry-meta{grid-template-columns:auto 1fr;}}
/* KEYWORDS */
.ph-keywords{display:flex;flex-wrap:wrap;align-items:center;gap:6px;}
.ph-keywords__label{font-family:var(--font-mo);font-size:9px;letter-spacing:0.22em;text-transform:uppercase;color:var(--accent-s);font-weight:500;white-space:nowrap;margin-right:6px;}
.ph-kw{display:inline-flex;align-items:center;padding:5px 11px;border:1px solid var(--border);background:var(--surface-2);font-family:var(--font-mo);font-size:10px;letter-spacing:0.10em;color:var(--text-sub);transition:border-color 120ms,color 120ms;}
.ph-kw a{color:inherit;}
.ph-kw:hover{border-color:var(--accent-a);color:var(--accent-a);}
/* SECTION PANELS */
.ph-section{border:1.5px solid var(--border);background:var(--surface);overflow:hidden;}
.ph-section__head{padding:14px 24px;border-bottom:1.5px solid var(--border);background:var(--surface-2);scroll-margin-top:20px;}
.ph-section__title{display:flex;align-items:baseline;gap:16px;}
.ph-section__num{font-family:var(--font-mo);font-size:10px;letter-spacing:0.22em;text-transform:uppercase;color:var(--accent-s);font-weight:500;flex-shrink:0;}
.ph-section__name{font-family:var(--font-jp);font-weight:900;font-size:23px;letter-spacing:0.03em;}
.ph-section__body{padding:26px 28px 30px;}
/* WORKS */
.ph-works-note{font-size:14px;color:var(--text-sub);margin-bottom:14px;line-height:1.75;max-width:42em;}
.ph-works-links{display:flex;flex-wrap:wrap;gap:8px;}
.chip-link{display:inline-flex;align-items:center;padding:7px 13px;border:1px solid var(--border);background:var(--surface-2);font-family:var(--font-mo);font-size:11px;letter-spacing:0.08em;color:var(--text-main);transition:border-color 120ms,color 120ms;}
.chip-link:hover{border-color:var(--accent-a);color:var(--accent-a);}
/* TOC */
.ph-toc{border:1px solid var(--border-soft);background:var(--surface-2);}
.ph-toc summary{display:flex;align-items:center;gap:10px;padding:13px 18px;cursor:pointer;list-style:none;font-family:var(--font-mo);font-size:10px;letter-spacing:0.22em;text-transform:uppercase;color:var(--text-mute);user-select:none;}
.ph-toc summary::-webkit-details-marker{display:none;}
.ph-toc summary::before{content:'▸';font-size:9px;color:var(--accent-s);transition:transform 0.15s;flex-shrink:0;}
.ph-toc[open] summary::before{transform:rotate(90deg);}
.ph-toc summary:hover{color:var(--accent-s);}
.toc-body{padding:4px 18px 14px;border-top:1px solid var(--rule);}
.toc-list{list-style:none;margin:10px 0 0;display:grid;gap:8px;}
.toc-section>a{display:inline-flex;align-items:baseline;gap:10px;color:var(--text-sub);font-size:14px;font-weight:500;}
.toc-section>a:hover{color:var(--accent-a);}
.toc-num{font-family:var(--font-mo);font-size:10px;color:var(--accent-s);letter-spacing:0.10em;flex-shrink:0;}
.toc-sub{list-style:none;margin:4px 0 0;padding-left:22px;display:grid;gap:2px;}
.toc-sub a{color:var(--text-mute);font-size:12px;line-height:1.5;}
.toc-sub a:hover{color:var(--accent-a);}
/* ESSAY */
.essay{font-size:17px;line-height:1.95;color:var(--text-main);max-width:42em;}
.essay p{margin-bottom:1.6em;text-align:justify;text-wrap:pretty;font-family:var(--font-se-jp);line-height:1.95;color:#1a1a1a;font-weight:500;font-size:16.5px;}
.essay p:last-child{margin-bottom:0;}
.essay h3{font-family:var(--font-jp);font-weight:700;font-size:18.5px;letter-spacing:0.02em;color:var(--text-main);margin:2.4em 0 0.65em;padding-left:14px;border-left:3px solid var(--accent-a);scroll-margin-top:20px;}
.essay h3:first-child{margin-top:0;}
.essay h3+p{margin-top:0;}
.essay a{color:var(--accent-a);border-bottom:1px solid rgba(168,58,42,0.38);}
.essay a:hover{border-bottom-color:var(--accent-a);}
sup{line-height:0;}
.sup-ref a{color:var(--accent-a);font-size:0.72em;font-family:var(--font-mo);border-bottom:0!important;}
/* RELATED */
.ph-rel-label{font-family:var(--font-mo);font-size:9px;letter-spacing:0.22em;text-transform:uppercase;color:var(--text-mute);margin:22px 0 8px;}
.ph-rel-label:first-child{margin-top:0;}
.ph-rel-list{list-style:none;display:grid;gap:6px;}
.ph-rel-list li{padding:10px 16px;background:var(--surface-2);border-left:3px solid var(--border-soft);font-size:14px;line-height:1.78;max-width:46em;}
.ph-rel-list li a{color:var(--accent-a);font-weight:600;}
.ph-rel-list li a:hover{background:var(--accent-h);color:var(--text-main);border-bottom:0;padding:1px 3px;margin:-1px -3px;}
.ph-rel-movements li a{color:var(--accent-s);}
.ph-rel-movements li a:hover{background:var(--accent-h);color:var(--text-main);}
/* FURTHER */
.ph-book{padding:16px 18px;border:1px solid var(--border-soft);background:var(--surface-2);max-width:46em;margin-bottom:12px;}
.ph-book__title{font-weight:700;font-size:15px;margin-bottom:4px;}
.ph-book__meta{font-family:var(--font-mo);font-size:11px;color:var(--text-mute);margin-bottom:8px;letter-spacing:0.03em;}
.ph-book__note{font-size:14px;line-height:1.78;color:var(--text-sub);margin-bottom:12px;}
.ph-book-cta{display:inline-flex;align-items:center;padding:7px 13px;border:1px solid var(--border);background:transparent;font-family:var(--font-mo);font-size:10px;letter-spacing:0.14em;text-transform:uppercase;color:var(--text-main);transition:background 120ms,color 120ms,border-color 120ms;}
.ph-book-cta:hover{background:var(--accent-a);color:var(--rev-text);border-color:var(--accent-a);}
.ph-aff{font-size:11px;color:var(--text-mute);margin-left:8px;}
.ph-further-links{font-size:14px;line-height:1.9;padding-left:18px;max-width:46em;margin:0;color:var(--text-sub);}
.ph-further-links li{margin-bottom:4px;}
.ph-further-links a{color:var(--accent-a);}
.ph-further-links a:hover{border-bottom:1px solid var(--accent-a);}
/* SOURCES */
.ph-sources{display:grid;grid-template-columns:1fr 1fr;gap:4px 24px;}
.ph-cite{display:grid;grid-template-columns:28px 1fr;gap:8px;align-items:start;font-size:12px;line-height:1.55;}
.ph-cite__num{font-family:var(--font-mo);font-size:10px;color:var(--accent-s);padding-top:2px;}
.ph-cite a{color:var(--accent-a);}
@media(max-width:640px){.ph-sources{grid-template-columns:1fr;}}
/* PREP BLOCK */
.prep-block{padding:14px 18px;background:var(--surface-2);border:1px dashed var(--border-soft);color:var(--text-mute);font-family:var(--font-mo);font-size:11px;letter-spacing:0.08em;}
/* SIDEBAR SEARCH */
.ph-side-search{border:1px solid var(--border-soft);background:var(--surface-2);}
.ph-side-search__label{display:block;font-family:var(--font-mo);font-size:9px;letter-spacing:0.24em;text-transform:uppercase;color:var(--accent-s);font-weight:500;padding:10px 14px 6px;background:var(--surface);border-bottom:1px solid var(--border-soft);}
.ph-side-search__field{display:flex;align-items:center;gap:0;transition:background 120ms;}
.ph-side-search__field:focus-within{background:var(--accent-h);}
.ph-side-search__field:focus-within .ph-side-search__input{color:var(--text-main);}
.ph-side-search__field:focus-within .ph-side-search__btn{color:var(--text-main);}
.ph-side-search__input{flex:1;font-family:var(--font-mo);font-size:11px;letter-spacing:0.08em;color:var(--text-sub);background:transparent;border:none;outline:none;padding:10px 8px 10px 14px;width:100%;min-width:0;}
.ph-side-search__input::placeholder{color:var(--text-mute);font-size:10px;}
.ph-side-search__btn{display:flex;align-items:center;justify-content:center;padding:0 12px;height:100%;color:var(--text-mute);background:transparent;border:none;cursor:pointer;transition:color 120ms;}
.ph-side-search__btn:hover{color:var(--text-main);}
/* AUTOCOMPLETE SUGGESTIONS */
.ph-search-suggestions{list-style:none;border-top:1px solid var(--border-soft);background:var(--surface);max-height:280px;overflow-y:auto;}
.ph-search-suggestions[hidden]{display:none;}
.ph-search-suggestion{display:block;border-bottom:1px solid var(--border-soft);}
.ph-search-suggestion:last-child{border-bottom:none;}
.ph-search-suggestion a{display:flex;flex-direction:column;gap:2px;padding:10px 14px;transition:background 80ms;text-decoration:none;}
.ph-search-suggestion a:hover,.ph-search-suggestion a:focus{background:var(--accent-h);outline:none;}
.ph-search-suggestion__name{font-family:var(--font-jp);font-weight:700;font-size:13px;color:var(--text-main);}
.ph-search-suggestion__name mark{background:var(--accent-h);color:var(--text-main);font-weight:700;}
.ph-search-suggestion__meta{font-family:var(--font-mo);font-size:10px;letter-spacing:0.12em;color:var(--text-mute);text-transform:uppercase;}
.ph-search-suggestion__en{font-family:var(--font-se);font-style:italic;font-size:11px;color:var(--text-sub);}
.ph-search-no-result{padding:12px 14px;font-family:var(--font-mo);font-size:10px;letter-spacing:0.14em;color:var(--text-mute);text-transform:uppercase;}
/* SIDEBAR */
.ph-side{position:sticky;top:24px;display:grid;gap:14px;align-content:start;}
.ph-side-block{border:1px solid var(--border-soft);background:var(--surface-2);overflow:hidden;}
.ph-side-block__head{padding:9px 14px;border-bottom:1px solid var(--border-soft);background:var(--surface);font-family:var(--font-mo);font-size:9px;letter-spacing:0.26em;text-transform:uppercase;color:var(--accent-s);font-weight:500;}
.ph-side-block__body{padding:14px;}
.ph-side-meta{display:grid;gap:0;}
.ph-side-meta-row{display:grid;grid-template-columns:68px 1fr;gap:8px;font-size:12px;align-items:start;padding:8px 0;border-bottom:1px solid var(--rule);}
.ph-side-meta-row:first-child{padding-top:0;}
.ph-side-meta-row:last-child{border-bottom:0;padding-bottom:0;}
.ph-side-meta-key{font-family:var(--font-mo);font-size:9px;letter-spacing:0.14em;text-transform:uppercase;color:var(--text-mute);padding-top:2px;}
.ph-side-meta-val{color:var(--text-main);line-height:1.5;}
.ph-side-meta-val a{color:var(--accent-a);}
.ph-side-chips{display:flex;flex-wrap:wrap;gap:6px;}
.ph-side-chip{display:inline-flex;padding:4px 8px;border:1px solid var(--border-soft);font-family:var(--font-mo);font-size:9px;letter-spacing:0.10em;color:var(--text-sub);cursor:default;}
.ph-side-chip a{color:inherit;}
.ph-side-chip:hover{border-color:var(--accent-a);color:var(--accent-a);}
.ph-side-chip.is-primary{background:var(--accent-h);border-color:var(--accent-h);color:var(--text-main);}
.ph-side-chip.is-primary a{color:var(--text-main);}
.ph-side-works{display:grid;gap:6px;}
.ph-side-works .chip-link{font-size:10px;padding:6px 10px;}
.ph-side-nav{display:grid;gap:0;}
.ph-side-nav a{display:flex;justify-content:space-between;align-items:center;padding:9px 14px;border-bottom:1px solid var(--rule);font-family:var(--font-mo);font-size:10px;letter-spacing:0.14em;text-transform:uppercase;color:var(--text-sub);transition:color 120ms,background 120ms;}
.ph-side-nav a:last-child{border-bottom:0;}
.ph-side-nav a:hover{color:var(--accent-a);background:var(--surface);}
.ph-side-nav a span:last-child{color:var(--text-deep);}
/* FOOTER */
.foot{padding:32px;display:grid;grid-template-columns:1fr auto 1fr;align-items:center;border-top:1.5px solid var(--rule-strong);font-family:var(--font-mo);font-size:10px;letter-spacing:0.22em;text-transform:uppercase;color:var(--text-mute);}
.foot__center{text-align:center;}
.foot__right{text-align:right;}
.foot a{color:var(--accent-a);}
/* RESPONSIVE */
@media(max-width:1100px){
  .ph-hero{grid-template-columns:280px 1fr;}
  .ph-layout{grid-template-columns:1fr;gap:28px;}
  .ph-side{position:static;grid-template-columns:1fr 1fr;gap:14px;}
}
@media(max-width:720px){
  .head{grid-template-columns:auto 1fr;gap:12px;padding:12px 16px;}
  .head__crumbs{display:none;}
  .ph-hero{grid-template-columns:1fr;min-height:auto;}
  .ph-hero__art{min-height:180px;font-size:140px;border-right:0;border-bottom:1.5px solid var(--rule-strong);}
  .ph-hero__info{padding:24px 20px;}
  .ph-layout{padding:28px 16px 64px;}
  .ph-side{grid-template-columns:1fr;}
  .foot{grid-template-columns:1fr;gap:4px;}
  .foot__center,.foot__right{text-align:left;}
}
/* TEAL TOC active */
.toc-section.is-active>a{color:var(--text-main);font-weight:600;}
.toc-section.is-active .toc-num::before{content:'';display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--accent-h);margin-right:4px;vertical-align:1px;}
"""

FONTS_URL = "https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=Noto+Serif+JP:wght@400;500;700&family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&family=Cormorant+Garamond:ital,wght@1,500;1,600&display=swap"


def get_initials(name_en):
    words = [w for w in name_en.split() if w]
    if len(words) >= 2:
        return words[0][0].upper(), words[-1][0].upper()
    elif words:
        return words[0][0].upper(), words[0][-1].upper()
    return 'X', 'X'


def parse_country_years(meta_ja):
    parts = meta_ja.split('·')
    country = parts[0].strip() if parts else ''
    years = parts[1].strip() if len(parts) > 1 else ''
    return country, years


def strip_html_tags(text):
    """Remove all HTML tags and return plain text."""
    return re.sub(r'<[^>]+>', '', text).strip()


def parse_birth_death(years_str):
    """'1902–1984' → ('1902','1984')   '1938–' → ('1938',None)"""
    m = re.match(r'(\d{4})(?:[–\-](\d{4}))?', years_str)
    if not m:
        return None, None
    return m.group(1), m.group(2)  # death is None if open-ended


def load_overrides_links():
    """overrides.js から links: 配列を持つエントリを抽出して返す。
    Returns: dict { ph_id: [{'url':..., 'label':...}, ...] }
    """
    links_map = {}
    if not os.path.exists(OVERRIDES_JS):
        return links_map
    with open(OVERRIDES_JS, encoding='utf-8') as f:
        js = f.read()
    # 各エントリブロックを取り出す (greedy で全体を走査)
    entry_pat = re.compile(
        r"['\"]([a-z0-9\-]+)['\"]\s*:\s*\{(.*?)\n\s*\}(?=\s*[,}])",
        re.DOTALL
    )
    link_pat = re.compile(
        r"\{\s*url\s*:\s*['\"]([^'\"]+)['\"]\s*,\s*label\s*:\s*['\"]([^'\"]+)['\"]\s*\}",
        re.DOTALL
    )
    for m in entry_pat.finditer(js):
        pid   = m.group(1)
        block = m.group(2)
        if 'links:' not in block:
            continue
        links_section = re.search(r'links\s*:\s*\[(.*?)\]', block, re.DOTALL)
        if not links_section:
            continue
        items = []
        for lm in link_pat.finditer(links_section.group(1)):
            items.append({'url': lm.group(1), 'label': lm.group(2)})
        if items:
            links_map[pid] = items
    return links_map


def inner_html(el):
    return el.decode_contents() if el else ''


def convert_sources(soup):
    """Convert old .cite-item format → ph-cite format"""
    cite_items = soup.select('.sources .cite-item')
    if not cite_items:
        cite_items = soup.select('.cite-item')
    result = []
    seen_ids = set()
    for item in cite_items:
        item_id = item.get('id', '')
        if item_id in seen_ids:
            continue
        seen_ids.add(item_id)
        num_el = item.select_one('.cite-num')
        num = num_el.get_text(strip=True) if num_el else ''
        if num_el:
            num_el.decompose()
        content = item.decode_contents().strip()
        result.append(
            f'<div class="ph-cite" id="{item_id}">'
            f'<div class="ph-cite__num">{num}</div>'
            f'<div>{content}</div></div>'
        )
    return '\n'.join(result)


def convert_books_section(section_el):
    """Convert .book-card / .book elements → ph-book HTML"""
    books = section_el.select('.book-card, .book')
    parts = []
    for book in books:
        title_el  = book.select_one('.book-title')
        meta_el   = book.select_one('.book-meta')
        note_el   = book.select_one('.book-note')
        amazon_el = book.select_one('a[href*="amzn"], a.amazon-cta')

        title = title_el.get_text(strip=True) if title_el else '(タイトル不明)'
        meta  = meta_el.get_text(strip=True) if meta_el else ''
        note  = note_el.get_text(strip=True) if note_el else ''

        h = ['<div class="ph-book">']
        h.append(f'  <div class="ph-book__title">{title}</div>')
        if meta:
            h.append(f'  <div class="ph-book__meta">{meta}</div>')
        if note:
            h.append(f'  <p class="ph-book__note">{note}</p>')
        if amazon_el:
            href = amazon_el.get('href', '#')
            h.append('  <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">')
            h.append(f'    <a class="ph-book-cta" href="{href}" target="_blank" rel="noopener sponsored">Amazon で見る ↗</a>')
            h.append('    <span class="ph-aff">※アフィリエイトリンクを含みます</span>')
            h.append('  </div>')
        else:
            h.append('  <div class="prep-block" data-nosnippet>Amazon リンク 準備中</div>')
        h.append('</div>')
        parts.append('\n'.join(h))
    return '\n'.join(parts)


def extract_essay_sections(soup):
    """Extract essay sections from old-format HTML.
    Returns list of dicts: {title, inner_html, h3s}
    """
    sections = []
    for s in soup.select('.section-grid .section'):
        h2 = s.select_one('h2')
        if not h2:
            continue
        # Get title
        sec_title_el = h2.select_one('.sec-title')
        title = sec_title_el.get_text(strip=True) if sec_title_el else h2.get_text(strip=True)
        # Skip non-essay sections
        if any(kw in title for kw in SKIP_H2_KEYWORDS):
            continue
        # Map title
        title = SECTION_MAP.get(title, title)

        # Get essay div inner HTML (remove the h2)
        essay_div = s.select_one('.essay, .essay.works')
        if essay_div:
            body_html = essay_div.decode_contents()
        else:
            parts = []
            for child in s.children:
                if isinstance(child, NavigableString):
                    continue
                if child.name == 'h2':
                    continue
                parts.append(str(child))
            body_html = ''.join(parts)

        # Collect h3s for TOC
        h3s = []
        target = essay_div if essay_div else s
        for h3 in target.select('h3'):
            h3_id = h3.get('id', '')
            h3_text = h3.get_text(strip=True)
            h3s.append((h3_id, h3_text))

        sections.append({'title': title, 'body': body_html, 'h3s': h3s})
    return sections


def build_toc(sections):
    items = []
    for i, sec in enumerate(sections):
        active = ' is-active' if i == 0 else ''
        sec_id = f'sec-{i+1:02d}'
        item = f'<li class="toc-section{active}"><a href="#{sec_id}"><span class="toc-num">§ {i+1:02d}</span> {sec["title"]}</a>'
        if sec['h3s']:
            item += '\n              <ul class="toc-sub">'
            for h3_id, h3_text in sec['h3s']:
                item += f'\n                <li><a href="#{h3_id}">{h3_text}</a></li>'
            item += '\n              </ul>'
        item += '\n            </li>'
        items.append(item)
    return '\n            '.join(items)


def generate_page(ph_id, card, sorted_ids, card_map, overrides_links=None, ph_index_json='[]'):
    name_ja  = card['nameJa']
    name_en  = card['nameEn']
    meta_ja  = card.get('metaJa', '')
    era      = card.get('era', '')
    channel  = card.get('channel', '—')
    idx      = card.get('idx', 0)
    tags     = card.get('tags', [])

    country, years = parse_country_years(meta_ja)
    period_label   = ERA_LABELS.get(era, era)
    init1, init2   = get_initials(name_en)

    # Load existing HTML
    html_path = os.path.join(SRC_DIR, f'{ph_id}.html')
    soup = None
    if os.path.exists(html_path):
        with open(html_path, encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

    # ── ABSTRACT ──────────────────────────────────────────
    lead_el = soup.select_one('.lead') if soup else None
    abstract_html = lead_el.decode_contents() if lead_el else card.get('ledeJa', '準備中')

    # ── THESIS ────────────────────────────────────────────
    thesis_el   = soup.select_one('.thesis-body') if soup else None
    is_prep_thesis = thesis_el is None
    thesis_html = thesis_el.decode_contents() if thesis_el else \
        '現在このセクションは編集中です。近日公開予定。'

    # ── ENTRY META ────────────────────────────────────────
    em_el = soup.select_one('.entry-meta') if soup else None
    if em_el:
        dts = em_el.select('dt')
        dds = em_el.select('dd')
        em_data = {dt.get_text(strip=True): dd for dt, dd in zip(dts, dds)}
        def em(key, default='—'):
            dd = em_data.get(key)
            return dd.decode_contents() if dd else default
        entry_no   = em('Entry', f'No. {idx:03d}')
        country_h  = em('Country', country)
        years_h    = em('Years', years)
        period_h   = em('Period', f'<a href="/eras/{era}.html">{period_label}</a>')
        movement_h = em('Movement', '—')
        updated_h  = em('Updated', '—')
    else:
        # Build from card-data
        entry_no   = f'No. {idx:03d}'
        country_h  = country
        years_h    = years
        period_h   = f'<a href="/eras/{era}.html">{period_label}</a>'
        movement_h = '—'
        updated_h  = RUN_DATE

    # ── KEYWORDS ──────────────────────────────────────────
    kw_el = soup.select_one('.page-keywords') if soup else None
    kw_chips_main = ''
    kw_chips_side = ''
    if kw_el:
        links = kw_el.select('a')
        for i, a in enumerate(links):
            href = a.get('href', '#')
            text = a.get_text(strip=True)
            kw_chips_main += f'<span class="ph-kw"><a href="{href}">{text}</a></span>\n        '
            primary = ' is-primary' if i == 0 else ''
            kw_chips_side += f'<span class="ph-side-chip{primary}"><a href="{href}">{text}</a></span>\n            '
    else:
        for i, tag in enumerate(tags[:6]):
            kw_chips_main += f'<span class="ph-kw">{tag}</span>\n        '
            primary = ' is-primary' if i == 0 else ''
            kw_chips_side += f'<span class="ph-side-chip{primary}">{tag}</span>\n            '

    # ── WORKS ─────────────────────────────────────────────
    # Priority: 1) .view-works-section  2) .関連作品 section  3) overrides.js links:
    works_links = []  # list of (href, label)

    if soup:
        works_el = soup.select_one('.view-works-section')
        if works_el:
            for a in works_el.select('.links a, a.chip-link'):
                works_links.append((a.get('href', '#'), a.get_text(strip=True)))
        if not works_links:
            # Fall back to 関連作品 section
            for s in soup.select('.section-grid .section'):
                h2 = s.select_one('h2')
                if h2 and '関連作品' in h2.get_text():
                    for a in s.select('a.chip-link, .links a'):
                        href = a.get('href', '#')
                        text = a.get_text(strip=True)
                        if href and href != '#':
                            works_links.append((href, text))
                    break

    # Fall back to overrides.js links:
    if not works_links and overrides_links and ph_id in overrides_links:
        for item in overrides_links[ph_id]:
            works_links.append((item['url'], item['label'] + ' ↗'))

    if works_links:
        note = '本サイトでは作品画像を掲載していません。下記の公式アーカイブで作品をご覧ください。'
        chips = ''
        for href, text in works_links:
            chips += f'<a class="chip-link" href="{href}" target="_blank" rel="noopener">{text}</a>\n            '
        side_works = ''
        for href, text in works_links[:4]:
            side_works += f'<a class="chip-link" href="{href}" target="_blank" rel="noopener">{text}</a>\n          '
        works_body = f'<p class="ph-works-note">{note}</p>\n          <div class="ph-works-links">\n            {chips}\n          </div>'
    else:
        side_works = ''
        works_body = '<div class="prep-block" data-nosnippet>本サイトでは作品画像を掲載していません。公式アーカイブへのリンクは準備中です。</div>'

    # ── ESSAY SECTIONS ────────────────────────────────────
    essay_sections = extract_essay_sections(soup) if soup else []
    total = max(len(essay_sections), 1)

    toc_html = build_toc(essay_sections)

    essay_parts = []
    for i, sec in enumerate(essay_sections):
        sec_id = f'sec-{i+1:02d}'
        essay_parts.append(f'''      <section class="ph-section" id="{sec_id}">
        <div class="ph-section__head">
          <div class="ph-section__title">
            <span class="ph-section__num">§ {i+1:02d} / {total:02d}</span>
            <span class="ph-section__name">{sec["title"]}</span>
          </div>
        </div>
        <div class="ph-section__body">
          <div class="essay">
            {sec["body"]}
          </div>
        </div>
      </section>''')

    essay_all = '\n\n'.join(essay_parts) if essay_parts else \
        '<section class="ph-section"><div class="ph-section__body"><div class="prep-block" data-nosnippet>本文準備中</div></div></section>'

    # CSS ivory + lime dots selectors
    ivory_ids = ', '.join(f'#sec-{i+1:02d}' for i in range(total))
    lime_sels = ',\n'.join(f'#{sec_id} .ph-section__num::before' for sec_id in [f'sec-{i+1:02d}' for i in range(total)])

    # ── RELATED ───────────────────────────────────────────
    related_el = soup.select_one('.related-section') if soup else None
    if related_el:
        labels = related_el.select('.related-label')
        lists  = related_el.select('.related-list')
        rel_blocks = []
        for label, lst in zip(labels, lists):
            ltext = label.get_text(strip=True)
            is_mv = '運動' in ltext
            cls   = 'ph-rel-list ph-rel-movements' if is_mv else 'ph-rel-list'
            items = ''
            for li in lst.select('li'):
                items += f'          <li>{li.decode_contents()}</li>\n'
            rel_blocks.append(
                f'          <div class="ph-rel-label">{ltext}</div>\n'
                f'          <ul class="{cls}">\n{items}          </ul>'
            )
        related_body = '\n'.join(rel_blocks)
    else:
        related_body = '<div class="prep-block" data-nosnippet>準備中</div>'

    # ── FURTHER READING ───────────────────────────────────
    further_el = soup.select_one('.further-section') if soup else None
    if further_el:
        books_html = convert_books_section(further_el)
        further_labels = further_el.select('.further-label')
        further_lists  = further_el.select('.further-links')
        ext_html = ''
        for lbl, lst in zip(further_labels, further_lists):
            ltext = lbl.get_text(strip=True)
            if 'データベース' in ltext or 'アーカイブ' in ltext or '外部' in ltext:
                items = ''
                for li in lst.select('li'):
                    items += f'            {str(li)}\n'
                ext_html = f'          <div class="ph-rel-label">{ltext}</div>\n          <ul class="ph-further-links">\n{items}          </ul>'
        further_body = ''
        if books_html:
            further_body += '<div class="ph-rel-label">写真集</div>\n          ' + books_html
        if ext_html:
            further_body += '\n          ' + ext_html
        if not further_body:
            further_body = '<div class="prep-block" data-nosnippet>準備中</div>'
    else:
        # Try old 写真集 section
        books_html = ''
        ext_html   = ''
        if soup:
            for s in soup.select('.section-grid .section'):
                h2 = s.select_one('h2')
                if not h2:
                    continue
                title = h2.get_text(strip=True)
                if '写真集' in title:
                    books_html = convert_books_section(s)
                if '外部リンク' in title:
                    links_html = ''
                    for a in s.select('a[href]'):
                        href = a.get('href', '')
                        text = a.get_text(strip=True)
                        if text and href:
                            links_html += f'            <li><a href="{href}" target="_blank" rel="noopener">{text}</a></li>\n'
                    if links_html:
                        ext_html = f'          <div class="ph-rel-label">関連データベース・アーカイブ</div>\n          <ul class="ph-further-links">\n{links_html}          </ul>'
        further_body = ''
        if books_html:
            further_body += '<div class="ph-rel-label">写真集</div>\n          ' + books_html
        if ext_html:
            further_body += '\n          ' + ext_html
        if not further_body:
            further_body = '<div class="prep-block" data-nosnippet>準備中</div>'

    # ── SOURCES ───────────────────────────────────────────
    sources_html = convert_sources(soup) if soup else ''
    if not sources_html:
        sources_html = '<div class="prep-block" data-nosnippet>出典準備中</div>'

    # ── NAVIGATION ────────────────────────────────────────
    try:
        pos = sorted_ids.index(ph_id)
    except ValueError:
        pos = -1
    prev_id   = sorted_ids[pos-1] if pos > 0 else None
    next_id   = sorted_ids[pos+1] if 0 <= pos < len(sorted_ids)-1 else None
    prev_card = card_map.get(prev_id) if prev_id else None
    next_card = card_map.get(next_id) if next_id else None

    prev_nav = (f'<a href="/new-design/{prev_id}.html"><span>← {prev_card["nameJa"]}</span><span>前</span></a>'
                if prev_card else '')
    next_nav = (f'<a href="/new-design/{next_id}.html"><span>{next_card["nameJa"]} →</span><span>次</span></a>'
                if next_card else '')

    # ── PAGE TITLE ────────────────────────────────────────
    title_el = soup.select_one('title') if soup else None
    page_title = title_el.get_text(strip=True) if title_el else f'{name_ja} | {name_en} | 写真の座標'

    # ── HEADER CRUMBS movement label ─────────────────────
    article_no_el = soup.select_one('.article-no') if soup else None
    crumb_movement = ''
    if article_no_el:
        txt = article_no_el.get_text(strip=True)
        parts = txt.split('—')
        if len(parts) >= 3:
            crumb_movement = parts[-1].strip()
    if not crumb_movement and tags:
        crumb_movement = tags[0]

    crumb_right = f'· {crumb_movement.upper()}' if crumb_movement else ''

    # ── SEO VARIABLES ─────────────────────────────────────
    canonical_url = f'{SITE_ROOT}/photographers/{ph_id}.html'
    abstract_plain = strip_html_tags(abstract_html)
    desc_text = abstract_plain[:150] if abstract_plain else DEFAULT_DESC
    desc_escaped = html_lib.escape(desc_text)
    title_escaped = html_lib.escape(page_title)

    birth_year, death_year = parse_birth_death(years)
    # Build Person JSON-LD
    person_ld = {
        '@context': 'https://schema.org',
        '@type': 'Person',
        'name': name_ja,
        'alternateName': name_en,
        'nationality': country,
        'description': abstract_plain[:200],
        'url': canonical_url,
    }
    if birth_year:
        person_ld['birthDate'] = birth_year
    if death_year:
        person_ld['deathDate'] = death_year
    if works_links:
        person_ld['sameAs'] = [href for href, _ in works_links]
    person_ld_str = json.dumps(person_ld, ensure_ascii=False, indent=2)

    # noindex: only if page has no essay sections at all
    is_placeholder_page = len(essay_sections) == 0
    robots_content = 'noindex, follow' if is_placeholder_page else 'index, follow'

    seo_head = f'''<meta name="description" content="{desc_escaped}">
<link rel="canonical" href="{canonical_url}">
<meta name="robots" content="{robots_content}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="写真の座標">
<meta property="og:title" content="{title_escaped}">
<meta property="og:description" content="{desc_escaped}">
<meta property="og:url" content="{canonical_url}">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{title_escaped}">
<meta name="twitter:description" content="{desc_escaped}">
<script type="application/ld+json">
{person_ld_str}
</script>'''

    # ── PRE-BUILD OPTIONAL SECTIONS ──────────────────────

    # thesis: 内容がある場合のみ出力
    if not is_prep_thesis:
        thesis_section = (
            '      <div class="ph-thesis">\n'
            '        <div class="ph-thesis__label">この写真家が変えたこと</div>\n'
            '        <p class="ph-thesis__body">' + thesis_html + '</p>\n'
            '      </div>'
        )
    else:
        thesis_section = ''

    related_section = (
        '      <section class="ph-section">\n'
        '        <div class="ph-section__head">\n'
        '          <div class="ph-section__title">\n'
        '            <span class="ph-section__num">§ REL</span>\n'
        '            <span class="ph-section__name">関連する写真家・運動</span>\n'
        '          </div>\n'
        '        </div>\n'
        '        <div class="ph-section__body">\n'
        + related_body + '\n'
        '        </div>\n'
        '      </section>'
    ) if related_body else ''

    further_section = (
        '      <section class="ph-section">\n'
        '        <div class="ph-section__head">\n'
        '          <div class="ph-section__title">\n'
        '            <span class="ph-section__num">§ REF</span>\n'
        '            <span class="ph-section__name">さらに読む</span>\n'
        '          </div>\n'
        '        </div>\n'
        '        <div class="ph-section__body">\n'
        '          ' + further_body + '\n'
        '        </div>\n'
        '      </section>'
    ) if further_body else ''

    side_works_block = (
        '      <div class="ph-side-block">\n'
        '        <div class="ph-side-block__head">Works · 作品リンク</div>\n'
        '        <div class="ph-side-block__body ph-side-works">\n'
        '          ' + side_works + '\n'
        '        </div>\n'
        '      </div>'
    ) if side_works else ''

    # ── ASSEMBLE HTML ─────────────────────────────────────

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{page_title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{seo_head}
<link href="{FONTS_URL}" rel="stylesheet">
<style>
{CSS}
/* ESSAY SECTIONS — ivory reading bg */
{ivory_ids} {{ background: #fffff8; }}
/* LIME DOTS */
{lime_sels} {{
  content: '';
  display: inline-block;
  width: 11px; height: 11px;
  border-radius: 50%;
  background: var(--accent-h);
  margin-right: 8px;
  vertical-align: 1px;
}}
</style>
</head>
<body>
<div class="page">

<header class="head">
  <div class="head__brand">
    <span class="head__brand-ja"><a href="/index-v51.html"><span class="head__brand-photo">写真</span>の座標</a></span>
    <span class="head__brand-en">Photo Coordinates</span>
  </div>
  <div class="head__crumbs">
    <em>PHOTOGRAPHERS</em><span class="sep">/</span>{name_en.upper()}
    {crumb_right}
  </div>
  <div class="head__meta">
    <div class="head__lang">
      <button class="is-active">JP</button>
      <button>EN</button>
    </div>
  </div>
</header>

<section class="ph-hero">
  <div class="ph-hero__art">{init1}<span>{init2}</span></div>
  <div class="ph-hero__info">
    <div class="ph-hero__eyebrow">§ {idx:03d} — Photographer Index — {crumb_movement}</div>
    <h1 class="ph-hero__name">{name_ja}</h1>
    <div class="ph-hero__en">
      {name_en}
      <span class="ph-hero__years">{years}</span>
    </div>
    <div class="ph-hero__meta-row">
      <span class="ph-hero__meta-item">Country<strong>{country}</strong></span>
      <span class="ph-hero__meta-item">Period<strong>{period_label}</strong></span>
      <span class="ph-hero__meta-item">Channel<strong>{channel}</strong></span>
    </div>
  </div>
</section>

<div class="ph-outer">
  <div class="ph-layout">

    <main class="ph-main">

      <div class="ph-abstract">
        <div class="ph-abstract__label">Abstract</div>
        <p>{abstract_html}</p>
      </div>

{thesis_section}

      <dl class="ph-entry-meta">
        <dt>Entry</dt><dd>{entry_no}</dd>
        <dt>Category</dt><dd>Photographer</dd>
        <dt>Country</dt><dd>{country_h}</dd>
        <dt>Years</dt><dd>{years_h}</dd>
        <dt>Period</dt><dd>{period_h}</dd>
        <dt>Movement</dt><dd>{movement_h}</dd>
        <dt>Updated</dt><dd>{updated_h}</dd>
        <dt></dt><dd></dd>
      </dl>

      <div class="ph-keywords">
        <span class="ph-keywords__label">Keywords</span>
        {kw_chips_main}
      </div>

      <section class="ph-section">
        <div class="ph-section__head">
          <div class="ph-section__title">
            <span class="ph-section__num">§ WORKS</span>
            <span class="ph-section__name">作品を見る</span>
          </div>
        </div>
        <div class="ph-section__body">
          {works_body}
        </div>
      </section>

      <details class="ph-toc">
        <summary>目次 · Table of Contents</summary>
        <div class="toc-body">
          <ol class="toc-list">
            {toc_html}
          </ol>
        </div>
      </details>

{essay_all}

{related_section}

{further_section}

      <section class="ph-section">
        <div class="ph-section__head">
          <div class="ph-section__title">
            <span class="ph-section__num">§ SRC</span>
            <span class="ph-section__name">出典</span>
          </div>
        </div>
        <div class="ph-section__body">
          <div class="ph-sources">
            {sources_html}
          </div>
        </div>
      </section>

    </main>

    <aside class="ph-side">

      <div class="ph-side-search">
        <form class="ph-side-search__form" onsubmit="return false;">
          <label class="ph-side-search__label" for="ph-search-input-{ph_id}">SEARCH · 写真家を探す</label>
          <div class="ph-side-search__field">
            <input class="ph-side-search__input" id="ph-search-input-{ph_id}" type="search" placeholder="写真家名・運動・キーワード" autocomplete="off" aria-autocomplete="list" aria-controls="ph-search-suggestions-{ph_id}" aria-expanded="false">
            <button class="ph-side-search__btn" type="button" aria-label="検索">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><circle cx="5.5" cy="5.5" r="4.5" stroke="currentColor" stroke-width="1.5"/><line x1="9" y1="9" x2="13" y2="13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
            </button>
          </div>
        </form>
        <ul class="ph-search-suggestions" id="ph-search-suggestions-{ph_id}" role="listbox" hidden></ul>
      </div>

      <div class="ph-side-block">
        <div class="ph-side-block__head">Entry · 写真家データ</div>
        <div class="ph-side-block__body">
          <div class="ph-side-meta">
            <div class="ph-side-meta-row"><span class="ph-side-meta-key">Country</span><span class="ph-side-meta-val">{country_h}</span></div>
            <div class="ph-side-meta-row"><span class="ph-side-meta-key">Years</span><span class="ph-side-meta-val">{years_h}</span></div>
            <div class="ph-side-meta-row"><span class="ph-side-meta-key">Period</span><span class="ph-side-meta-val">{period_h}</span></div>
            <div class="ph-side-meta-row"><span class="ph-side-meta-key">Movement</span><span class="ph-side-meta-val">{movement_h}</span></div>
            <div class="ph-side-meta-row"><span class="ph-side-meta-key">Updated</span><span class="ph-side-meta-val">{updated_h}</span></div>
          </div>
        </div>
      </div>

      <div class="ph-side-block">
        <div class="ph-side-block__head">Keywords · キーワード</div>
        <div class="ph-side-block__body">
          <div class="ph-side-chips">
            {kw_chips_side}
          </div>
        </div>
      </div>
{side_works_block}

      <div class="ph-side-block">
        <div class="ph-side-block__head">Navigate · 移動</div>
        <nav class="ph-side-nav">
          <a href="/new-design/cards-archive.html"><span>← 写真家一覧</span><span>Archive</span></a>
          {prev_nav}
          {next_nav}
          <a href="/index-v51.html"><span>トップページへ</span><span>Top</span></a>
        </nav>
      </div>

    </aside>

  </div>
</div>

<footer class="foot">
  <div>© Photo Coordinates · VOL. 01</div>
  <div class="foot__center">美術館・アーカイブ・専門資料に基づく</div>
  <div class="foot__right"><a href="/privacy-policy.html">プライバシーポリシー</a></div>
</footer>

</div>

<script id="photographer-index" type="application/json">
{ph_index_json}
</script>
<script>
(function(){{
  var inputId  = 'ph-search-input-{ph_id}';
  var listId   = 'ph-search-suggestions-{ph_id}';
  var input    = document.getElementById(inputId);
  var list     = document.getElementById(listId);
  if(!input||!list) return;
  var indexEl  = document.getElementById('photographer-index');
  if(!indexEl) return;
  var photographers = JSON.parse(indexEl.textContent);

  function matches(ph,q){{
    var ql = q.toLowerCase();
    return ph.name_ja.includes(q)||
           ph.name_en.toLowerCase().includes(ql)||
           ph.slug.toLowerCase().includes(ql)||
           (ph.movement&&ph.movement.toLowerCase().includes(ql))||
           (ph.country&&ph.country.includes(q));
  }}
  function highlight(text,q){{
    if(!q) return text;
    var idx=text.toLowerCase().indexOf(q.toLowerCase());
    if(idx===-1) return text;
    return text.slice(0,idx)+'<mark>'+text.slice(idx,idx+q.length)+'</mark>'+text.slice(idx+q.length);
  }}
  function render(results,q){{
    list.innerHTML='';
    if(results.length===0){{
      list.innerHTML='<li class="ph-search-no-result">該当する写真家が見つかりません</li>';
      list.hidden=false; input.setAttribute('aria-expanded','true'); return;
    }}
    results.slice(0,5).forEach(function(ph){{
      var li=document.createElement('li');
      li.className='ph-search-suggestion'; li.setAttribute('role','option');
      li.innerHTML='<a href="'+ph.url+'">'+
        '<span class="ph-search-suggestion__name">'+highlight(ph.name_ja,q)+'</span>'+
        '<span class="ph-search-suggestion__en">'+ph.name_en+'</span>'+
        '<span class="ph-search-suggestion__meta">'+(ph.country||'')+
          (ph.movement?' · '+ph.movement:'')+'</span></a>';
      list.appendChild(li);
    }});
    list.hidden=false; input.setAttribute('aria-expanded','true');
  }}
  function hide(){{ list.hidden=true; list.innerHTML=''; input.setAttribute('aria-expanded','false'); }}

  input.addEventListener('input',function(){{
    var q=this.value.trim();
    if(!q){{ hide(); return; }}
    render(photographers.filter(function(ph){{ return matches(ph,q); }}),q);
  }});
  input.addEventListener('blur',function(){{ setTimeout(hide,150); }});
  input.addEventListener('keydown',function(e){{ if(e.key==='Escape'){{ hide(); input.blur(); }} }});
}})();
</script>
</body>
</html>"""

    return html


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    with open(CARD_DATA, encoding='utf-8') as f:
        data = json.load(f)

    photographers = data['photographers']
    sorted_ph = sorted(photographers, key=lambda x: x.get('idx', 9999))
    sorted_ids = [p['id'] for p in sorted_ph]
    card_map   = {p['id']: p for p in sorted_ph}

    overrides_links = load_overrides_links()
    print(f'overrides.js links: {len(overrides_links)}件')

    # Build photographer index JSON for autocomplete (embedded in every page)
    ph_index = []
    for p in sorted_ph:
        country_str, _ = parse_country_years(p.get('metaJa', ''))
        # movement: try tags for movement-like keyword
        movement_str = ''
        for tag in p.get('tags', []):
            if any(x in tag for x in ['写真', 'ism', 'ize', '派', '主義', 'Magnum', 'Aperture', 'FSA', 'Provoke']):
                movement_str = tag
                break
        ph_index.append({
            'name_ja':  p['nameJa'],
            'name_en':  p['nameEn'],
            'slug':     p['id'],
            'url':      f'/new-design/{p["id"]}.html',
            'country':  country_str,
            'movement': movement_str,
        })
    ph_index_json = json.dumps(ph_index, ensure_ascii=False, indent=2)

    os.makedirs(OUT_DIR, exist_ok=True)

    ok = 0
    skipped = 0
    errors = []

    for card in sorted_ph:
        ph_id = card['id']
        out_path = os.path.join(OUT_DIR, f'{ph_id}.html')

        if ph_id in SKIP_IDS:
            skipped += 1
            continue

        try:
            html = generate_page(ph_id, card, sorted_ids, card_map, overrides_links, ph_index_json)
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(html)
            ok += 1
            if ok % 50 == 0:
                print(f'  {ok} pages generated...')
        except Exception as e:
            errors.append((ph_id, str(e)))
            print(f'  ERROR {ph_id}: {e}')

    print(f'\n完了: {ok}ページ生成, {skipped}スキップ, {len(errors)}エラー')
    if errors:
        print('エラー一覧:')
        for pid, err in errors:
            print(f'  {pid}: {err}')


if __name__ == '__main__':
    main()
