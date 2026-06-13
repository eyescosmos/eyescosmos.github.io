#!/usr/bin/env python3
"""Generate v5.1-redesigned country hub pages for the photography history site.

Usage:
    python3 scripts/generate_country_pages.py

Today only emits countries/france.html.
The script is parameterized by a COUNTRY config dict so it generalises
to other countries later.
"""
from __future__ import annotations

import glob
import html as html_module
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Reuse card-extraction helpers (same logic as add_missing_era_cards.py)
# ---------------------------------------------------------------------------

def extract_articles(html: str) -> list[str]:
    """Extract all <article>...</article> blocks from HTML using balanced parsing."""
    articles: list[str] = []
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


def build_archive_id_lookup(arch_html: str) -> dict[str, str]:
    """Build map: photographer id -> full <article>...</article> from archive.html."""
    lookup: dict[str, str] = {}
    for article in extract_articles(arch_html):
        m = re.search(r'href="photographers/([^"]+)\.html"', article)
        if m:
            pid = m.group(1)
            lookup[pid] = article
    return lookup


def transform_card(article: str, pid: str, card_entry: dict) -> str:
    """Transform an archive article into a country-page card."""
    result = article

    # 1. Replace <article …> opening tag with clean class (drop data-* attrs)
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
# Extract the <style>…</style> block from eras/1839.html (verbatim)
# ---------------------------------------------------------------------------

def extract_era_style_block(era_html: str) -> str:
    """Extract the first <style>…</style> block verbatim from an era page."""
    m = re.search(r'(<style>.*?</style>)', era_html, re.S)
    if not m:
        raise RuntimeError("Could not find <style> block in era page")
    return m.group(1)


def extract_archive_card_css(archive_html: str) -> str:
    """Extract archive.html's card typographic rules so country-page cards
    render exactly like the archive page (`.cards` masonry + all pc-top--*
    variants such as cite / country / serif / rotate / outline, which the
    era page <style> does not define).

    Robust to line shifts: anchored on stable selector text, not line numbers.
    """
    m = re.search(r'<style>(.*?)</style>', archive_html, re.S)
    if not m:
        raise RuntimeError("Could not find <style> block in archive.html")
    style = m.group(1)

    # Variant typography block: from `.pc-top--year` up to (not incl.) `.archive-hero`
    v = re.search(r'(\.pc-top--year \.pc-top__art\{.*?)\.archive-hero\{', style, re.S)
    if not v:
        raise RuntimeError("Could not locate archive card variant block")
    variant_css = v.group(1).strip()

    # Extra card rules that live below the page chrome
    extras = []
    for sel in (
        r'\.pc-top__art\{overflow:hidden;\}',
        r'\.pc-top__hint\{[^}]*\}',
        r'\.pc-card\.is-hidden\{display:none;\}',
    ):
        mm = re.search(sel, style)
        if mm:
            extras.append(mm.group(0))

    return "<style>\n" + variant_css + "\n" + "\n".join(extras) + "\n</style>"


# ---------------------------------------------------------------------------
# Nav dropdowns (ported verbatim from old countries/france.html)
# ---------------------------------------------------------------------------

COUNTRIES_SELECT = (
    '<select class="tax-select filter-select nav-select" aria-label="国別でみる" '
    'onchange="if(this.value) window.location.href=this.value">'
    '<option value="" selected>国別で見る</option>'
    '<option value="/countries/ireland.html">アイルランド</option>'
    '<option value="/countries/united-states.html">アメリカ</option>'
    '<option value="/countries/united-states-united-kingdom.html">アメリカ / イギリス</option>'
    '<option value="/countries/united-states-france.html">アメリカ / フランス</option>'
    '<option value="/countries/argentina-spain.html">アルゼンチン / スペイン</option>'
    '<option value="/countries/albania.html">アルバニア</option>'
    '<option value="/countries/united-kingdom.html">イギリス</option>'
    '<option value="/countries/united-kingdom-united-states.html">イギリス / アメリカ</option>'
    '<option value="/countries/italy.html">イタリア</option>'
    '<option value="/countries/italy-united-kingdom.html">イタリア / イギリス</option>'
    '<option value="/countries/iran-switzerland.html">イラン / スイス</option>'
    '<option value="/countries/ukraine.html">ウクライナ</option>'
    '<option value="/countries/ukraine-united-states.html">ウクライナ / アメリカ</option>'
    '<option value="/countries/netherlands.html">オランダ</option>'
    '<option value="/countries/australia.html">オーストラリア</option>'
    '<option value="/countries/austria.html">オーストリア</option>'
    '<option value="/countries/austria-canada.html">オーストリア / カナダ</option>'
    '<option value="/countries/canada.html">カナダ</option>'
    '<option value="/countries/canada-united-states.html">カナダ / アメリカ</option>'
    '<option value="/countries/kenya-united-states.html">ケニア / アメリカ</option>'
    '<option value="/countries/switzerland.html">スイス</option>'
    '<option value="/countries/switzerland-germany.html">スイス / ドイツ</option>'
    '<option value="/countries/sweden.html">スウェーデン</option>'
    '<option value="/countries/spain.html">スペイン</option>'
    '<option value="/countries/slovakia-france.html">スロバキア / フランス</option>'
    '<option value="/countries/czech-republic.html">チェコ</option>'
    '<option value="/countries/denmark.html">デンマーク</option>'
    '<option value="/countries/denmark-united-states.html">デンマーク / アメリカ</option>'
    '<option value="/countries/germany.html">ドイツ</option>'
    '<option value="/countries/germany-united-kingdom.html">ドイツ / イギリス</option>'
    '<option value="/countries/germany-brazil.html">ドイツ / ブラジル</option>'
    '<option value="/countries/nigeria-united-kingdom.html">ナイジェリア / イギリス</option>'
    '<option value="/countries/norway.html">ノルウェー</option>'
    '<option value="/countries/hungary.html">ハンガリー</option>'
    '<option value="/countries/hungary-germany.html">ハンガリー / ドイツ</option>'
    '<option value="/countries/hungary-france.html">ハンガリー / フランス</option>'
    '<option value="/countries/finland.html">フィンランド</option>'
    '<option value="/countries/france.html">フランス</option>'
    '<option value="/countries/brazil.html">ブラジル</option>'
    '<option value="/countries/vietnam-united-states.html">ベトナム / アメリカ</option>'
    '<option value="/countries/venezuela.html">ベネズエラ</option>'
    '<option value="/countries/belgium.html">ベルギー</option>'
    '<option value="/countries/poland.html">ポーランド</option>'
    '<option value="/countries/poland-united-states.html">ポーランド / アメリカ</option>'
    '<option value="/countries/mali.html">マリ</option>'
    '<option value="/countries/mexico.html">メキシコ</option>'
    '<option value="/countries/mexico-switzerland.html">メキシコ / スイス</option>'
    '<option value="/countries/morocco-france.html">モロッコ / フランス</option>'
    '<option value="/countries/lithuania-united-states.html">リトアニア / アメリカ</option>'
    '<option value="/countries/lithuania-united-kingdom.html">リトアニア / イギリス</option>'
    '<option value="/countries/lithuania-france.html">リトアニア / フランス</option>'
    '<option value="/countries/luxembourg-united-states.html">ルクセンブルク / アメリカ</option>'
    '<option value="/countries/romania.html">ルーマニア</option>'
    '<option value="/countries/lebanon-united-states.html">レバノン / アメリカ</option>'
    '<option value="/countries/russia.html">ロシア</option>'
    '<option value="/countries/china.html">中国</option>'
    '<option value="/countries/north-macedonia.html">北マケドニア</option>'
    '<option value="/countries/south-africa.html">南アフリカ</option>'
    '<option value="/countries/south-africa-united-kingdom.html">南アフリカ / イギリス</option>'
    '<option value="/countries/japan.html">日本</option>'
    '<option value="/countries/south-korea.html">韓国</option>'
    '<option value="/countries/south-korea-united-states.html">韓国 / アメリカ</option>'
    '</select>'
)

ERAS_SELECT = (
    '<select class="tax-select filter-select nav-select" aria-label="年代別で見る" '
    'onchange="if(this.value) window.location.href=this.value">'
    '<option value="" selected>年代別で見る</option>'
    '<option value="/archive.html">年代順で見る</option>'
    '<option value="/eras/1839.html">1839–1860s</option>'
    '<option value="/eras/1870.html">1870–1890s</option>'
    '<option value="/eras/1890.html">1890–1910s</option>'
    '<option value="/eras/1910.html">1910–1920s</option>'
    '<option value="/eras/1930.html">1930–1940s</option>'
    '<option value="/eras/1950.html">1950–1960s</option>'
    '<option value="/eras/1970.html">1970–1980s</option>'
    '<option value="/eras/1980.html">1980–1990s</option>'
    '<option value="/eras/1990.html">1990–2000s</option>'
    '<option value="/eras/2000.html">2000–2010s</option>'
    '<option value="/eras/2010.html">2010–2020s</option>'
    '</select>'
)

MOVEMENTS_SELECT = (
    '<select class="tax-select filter-select nav-select" aria-label="関連する運動" '
    'onchange="if(this.value) window.location.href=this.value">'
    '<option value="" selected>関連する運動</option>'
    '<option value="/movements/コンセプチュアルアート.html">コンセプチュアルアート</option>'
    '<option value="/movements/ドキュメンタリー.html">ドキュメンタリー</option>'
    '<option value="/movements/ピクトリアリズム.html">ピクトリアリズム</option>'
    '<option value="/movements/社会ドキュメンタリー.html">社会ドキュメンタリー</option>'
    '<option value="/movements/私写真.html">私写真</option>'
    '<option value="/movements/決定的瞬間.html">決定的瞬間</option>'
    '<option value="/movements/フォトジャーナリズム.html">フォトジャーナリズム</option>'
    '<option value="/movements/ストリート写真.html">ストリート写真</option>'
    '</select>'
)

# site-directory-links groups (ported verbatim from old countries/france.html)
SITE_DIR_ERAS = (
    '<a href="/eras/1839.html">1839–1860s</a>'
    '<a href="/eras/1870.html">1870–1890s</a>'
    '<a href="/eras/1890.html">1890–1910s</a>'
    '<a href="/eras/1910.html">1910–1920s</a>'
    '<a href="/eras/1930.html">1930–1940s</a>'
    '<a href="/eras/1950.html">1950–1960s</a>'
    '<a href="/eras/1970.html">1970–1980s</a>'
    '<a href="/eras/1980.html">1980–1990s</a>'
    '<a href="/eras/1990.html">1990–2000s</a>'
    '<a href="/eras/2000.html">2000–2010s</a>'
    '<a href="/eras/2010.html">2010–2020s</a>'
)

SITE_DIR_COUNTRIES = (
    '<a href="/countries/ireland.html">アイルランド</a>'
    '<a href="/countries/united-states.html">アメリカ</a>'
    '<a href="/countries/united-states-united-kingdom.html">アメリカ / イギリス</a>'
    '<a href="/countries/united-states-france.html">アメリカ / フランス</a>'
    '<a href="/countries/argentina-spain.html">アルゼンチン / スペイン</a>'
    '<a href="/countries/albania.html">アルバニア</a>'
    '<a href="/countries/united-kingdom.html">イギリス</a>'
    '<a href="/countries/united-kingdom-united-states.html">イギリス / アメリカ</a>'
    '<a href="/countries/italy.html">イタリア</a>'
    '<a href="/countries/italy-united-kingdom.html">イタリア / イギリス</a>'
    '<a href="/countries/iran-switzerland.html">イラン / スイス</a>'
    '<a href="/countries/ukraine.html">ウクライナ</a>'
    '<a href="/countries/ukraine-united-states.html">ウクライナ / アメリカ</a>'
    '<a href="/countries/netherlands.html">オランダ</a>'
    '<a href="/countries/australia.html">オーストラリア</a>'
    '<a href="/countries/austria.html">オーストリア</a>'
    '<a href="/countries/austria-canada.html">オーストリア / カナダ</a>'
    '<a href="/countries/canada.html">カナダ</a>'
    '<a href="/countries/canada-united-states.html">カナダ / アメリカ</a>'
    '<a href="/countries/kenya-united-states.html">ケニア / アメリカ</a>'
    '<a href="/countries/switzerland.html">スイス</a>'
    '<a href="/countries/switzerland-germany.html">スイス / ドイツ</a>'
    '<a href="/countries/sweden.html">スウェーデン</a>'
    '<a href="/countries/spain.html">スペイン</a>'
    '<a href="/countries/slovakia-france.html">スロバキア / フランス</a>'
    '<a href="/countries/czech-republic.html">チェコ</a>'
    '<a href="/countries/denmark.html">デンマーク</a>'
    '<a href="/countries/denmark-united-states.html">デンマーク / アメリカ</a>'
    '<a href="/countries/germany.html">ドイツ</a>'
    '<a href="/countries/germany-united-kingdom.html">ドイツ / イギリス</a>'
    '<a href="/countries/germany-brazil.html">ドイツ / ブラジル</a>'
    '<a href="/countries/nigeria-united-kingdom.html">ナイジェリア / イギリス</a>'
    '<a href="/countries/norway.html">ノルウェー</a>'
    '<a href="/countries/hungary.html">ハンガリー</a>'
    '<a href="/countries/hungary-germany.html">ハンガリー / ドイツ</a>'
    '<a href="/countries/hungary-france.html">ハンガリー / フランス</a>'
    '<a href="/countries/finland.html">フィンランド</a>'
    '<a href="/countries/france.html">フランス</a>'
    '<a href="/countries/brazil.html">ブラジル</a>'
    '<a href="/countries/vietnam-united-states.html">ベトナム / アメリカ</a>'
    '<a href="/countries/venezuela.html">ベネズエラ</a>'
    '<a href="/countries/belgium.html">ベルギー</a>'
    '<a href="/countries/poland.html">ポーランド</a>'
    '<a href="/countries/poland-united-states.html">ポーランド / アメリカ</a>'
    '<a href="/countries/mali.html">マリ</a>'
    '<a href="/countries/mexico.html">メキシコ</a>'
    '<a href="/countries/mexico-switzerland.html">メキシコ / スイス</a>'
    '<a href="/countries/morocco-france.html">モロッコ / フランス</a>'
    '<a href="/countries/lithuania-united-states.html">リトアニア / アメリカ</a>'
    '<a href="/countries/lithuania-united-kingdom.html">リトアニア / イギリス</a>'
    '<a href="/countries/lithuania-france.html">リトアニア / フランス</a>'
    '<a href="/countries/luxembourg-united-states.html">ルクセンブルク / アメリカ</a>'
    '<a href="/countries/romania.html">ルーマニア</a>'
    '<a href="/countries/lebanon-united-states.html">レバノン / アメリカ</a>'
    '<a href="/countries/russia.html">ロシア</a>'
    '<a href="/countries/china.html">中国</a>'
    '<a href="/countries/north-macedonia.html">北マケドニア</a>'
    '<a href="/countries/south-africa.html">南アフリカ</a>'
    '<a href="/countries/south-africa-united-kingdom.html">南アフリカ / イギリス</a>'
    '<a href="/countries/japan.html">日本</a>'
    '<a href="/countries/south-korea.html">韓国</a>'
    '<a href="/countries/south-korea-united-states.html">韓国 / アメリカ</a>'
)

SITE_DIR_PHOTOGRAPHERS = (
    '<a href="/photographers/daguerre.html">ルイ・ダゲール</a>'
    '<a href="/photographers/fenton.html">ロジャー・フェントン</a>'
    '<a href="/photographers/beato.html">フェリーチェ・ベアト</a>'
    '<a href="/photographers/nadar.html">ナダール</a>'
    '<a href="/photographers/stieglitz.html">アルフレッド・スティーグリッツ</a>'
    '<a href="/photographers/strand.html">ポール・ストランド</a>'
    '<a href="/photographers/cartierbresson.html">アンリ・カルティエ＝ブレッソン</a>'
    '<a href="/photographers/hiroshi-sugimoto.html">杉本博司</a>'
)

# Country-page additional CSS overrides (exact per spec)
COUNTRY_CSS_OVERRIDES = """\
<style>
.country-sticky{position:sticky;top:0;z-index:90;background:var(--bg);}
.country-toolbar{border-bottom:1.5px solid var(--rule-strong);background:var(--surface);}
.country-toolbar .toolbar__search{border-right:0;flex:1;width:100%;}
.country-strip .era-nav__label{white-space:nowrap;}
@media(max-width:760px){.head{position:static;}}
.er-no-result{display:none;padding:48px 8px;font-family:var(--font-mo);font-size:11px;letter-spacing:0.16em;text-transform:uppercase;color:var(--text-mute);}
.head__lang a{padding:4px 10px;color:var(--text-sub);font-family:var(--font-mo);font-size:10px;letter-spacing:0.20em;display:inline-block;}
.head__lang a.is-active{background:var(--text-main);color:var(--rev-text);}
.era-layout--solo{grid-template-columns:1fr;}
/* country h1 is Japanese — use the JP display font (era pages assume a Latin title) */
.country-hero .era-hero__title{font-family:var(--font-jp);font-weight:900;letter-spacing:0.02em;}
.country-hero .era-hero__art-year{font-size:clamp(80px,9vw,128px);letter-spacing:-0.04em;}
.country-hero--multi .era-hero__art-year{font-size:clamp(44px,5.5vw,80px);letter-spacing:0;}
.site-directory-links{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:28px;padding:40px 32px;border-top:1.5px solid var(--rule-strong);background:var(--surface-2);}
.site-directory-label{font-family:var(--font-mo);font-size:9px;letter-spacing:0.24em;text-transform:uppercase;color:var(--accent-s);font-weight:500;margin-bottom:12px;}
.site-directory-items{display:flex;flex-wrap:wrap;gap:6px 12px;}
.site-directory-items a{font-family:var(--font-jp);font-size:12px;color:var(--text-sub);transition:color 120ms;}
.site-directory-items a:hover{color:var(--accent-a);}
/* cards use archive masonry; let the solo layout breathe full-width on small screens */
@media(max-width:768px){.era-layout--solo{max-width:none;}}
@media(max-width:760px){.site-directory-links{padding:28px 16px;grid-template-columns:1fr;}}
</style>"""

# GA block (verbatim)
GA_BLOCK = """\
<script async src="https://www.googletagmanager.com/gtag/js?id=G-2VRTV8BZEJ"></script>
<script>window.dataLayer = window.dataLayer || [];function gtag(){dataLayer.push(arguments);}gtag('js', new Date());gtag('config', 'G-2VRTV8BZEJ');</script>"""

# Bottom search scripts (verbatim from eras/1839.html)
SEARCH_SCRIPT_SIDEBAR = """\
<script>
(function(){
  var input=document.getElementById('ph-search-input'),list=document.getElementById('ph-search-suggestions');
  if(!input||!list) return;
  var photographers=[];
  fetch('/card-data.json').then(function(r){return r.json();}).then(function(data){
    photographers=(data.photographers||[]).map(function(p){
      return{name_ja:p.nameJa||'',name_en:p.nameEn||'',slug:p.id||'',url:p.href?(p.href[0]==='/'?p.href:'/'+p.href):'',
             country:(p.metaJa||'').split('\xb7')[0].trim(),movement:p.channel||''};
    });
  });
  function toKatakana(s){return s.replace(/[ぁ-ゖ]/g,function(c){return String.fromCharCode(c.charCodeAt(0)+0x60);});}
  function matches(ph,q){var ql=q.toLowerCase(),qk=toKatakana(q);
    return ph.name_ja.includes(q)||ph.name_ja.includes(qk)||ph.name_en.toLowerCase().includes(ql)||
           ph.slug.toLowerCase().includes(ql)||(ph.movement&&ph.movement.toLowerCase().includes(ql))||
           (ph.country&&ph.country.includes(q));}
  function hl(t,q){if(!q)return t;var i=t.toLowerCase().indexOf(q.toLowerCase());
    if(i===-1)return t;return t.slice(0,i)+'<mark>'+t.slice(i,i+q.length)+'</mark>'+t.slice(i+q.length);}
  function render(rs,q){list.innerHTML='';
    if(!rs.length){list.innerHTML='<li class="ph-search-no-result">\\u8a72\\u5f53\\u3059\\u308b\\u5199\\u771f\\u5bb6\\u304c\\u898b\\u3064\\u304b\\u308a\\u307e\\u305b\\u3093</li>';
      list.hidden=false;input.setAttribute('aria-expanded','true');return;}
    rs.slice(0,5).forEach(function(ph){var li=document.createElement('li');
      li.className='ph-search-suggestion';li.setAttribute('role','option');
      li.innerHTML='<a href="'+ph.url+'"><span class="ph-search-suggestion__name">'+hl(ph.name_ja,q)+'</span>'+
        '<span class="ph-search-suggestion__en">'+ph.name_en+'</span>'+
        '<span class="ph-search-suggestion__meta">'+ph.country+(ph.movement?' \\xb7 '+ph.movement:'')+'</span></a>';
      list.appendChild(li);});
    list.hidden=false;input.setAttribute('aria-expanded','true');}
  function hide(){list.hidden=true;list.innerHTML='';input.setAttribute('aria-expanded','false');}
  input.addEventListener('input',function(){var q=this.value.trim();if(!q){hide();return;}
    render(photographers.filter(function(ph){return matches(ph,q);}),q);});
  input.addEventListener('blur',function(){setTimeout(hide,150);});
  input.addEventListener('keydown',function(e){if(e.key==='Escape'){hide();input.blur();}});
})();
</script>"""

CARD_FILTER_SCRIPT = """\
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

SEARCH_SCRIPT_MOBILE = """\
<script>
(function(){
  var wrap=document.querySelector('.head__mobile-search');
  if(!wrap)return;
  var input=wrap.querySelector('.ph-side-search__input'),list=wrap.querySelector('.ph-search-suggestions');
  if(!input||!list)return;
  function normalize(items){return (items||[]).map(function(p){return{name_ja:p.name_ja||p.nameJa||'',name_en:p.name_en||p.nameEn||'',slug:p.slug||p.id||'',url:p.url||(p.href?(p.href[0]==='/'?p.href:'/'+p.href):''),country:p.country||((p.metaJa||'').split('·')[0].trim()),movement:p.movement||p.channel||''};});}
  function start(photographers){
    function toKatakana(s){return s.replace(/[ぁ-ゖ]/g,function(c){return String.fromCharCode(c.charCodeAt(0)+0x60);});}
    function matches(ph,q){var ql=q.toLowerCase(),qk=toKatakana(q);return ph.name_ja.includes(q)||ph.name_ja.includes(qk)||ph.name_en.toLowerCase().includes(ql)||ph.slug.toLowerCase().includes(ql)||(ph.movement&&ph.movement.toLowerCase().includes(ql))||(ph.country&&ph.country.includes(q));}
    function hl(t,q){if(!q)return t;var i=t.toLowerCase().indexOf(q.toLowerCase());if(i===-1)return t;return t.slice(0,i)+'<mark>'+t.slice(i,i+q.length)+'</mark>'+t.slice(i+q.length);}
    function render(rs,q){list.innerHTML='';if(!rs.length){list.innerHTML='<li class="ph-search-no-result">該当する写真家が見つかりません</li>';list.hidden=false;input.setAttribute('aria-expanded','true');return;}rs.slice(0,5).forEach(function(ph){var li=document.createElement('li');li.className='ph-search-suggestion';li.setAttribute('role','option');li.innerHTML='<a href="'+ph.url+'"><span class="ph-search-suggestion__name">'+hl(ph.name_ja,q)+'</span><span class="ph-search-suggestion__en">'+ph.name_en+'</span><span class="ph-search-suggestion__meta">'+(ph.country||'')+(ph.movement?' · '+ph.movement:'')+'</span></a>';list.appendChild(li);});list.hidden=false;input.setAttribute('aria-expanded','true');}
    function hide(){list.hidden=true;list.innerHTML='';input.setAttribute('aria-expanded','false');}
    input.addEventListener('input',function(){var q=this.value.trim();if(!q){hide();return;}render(photographers.filter(function(ph){return matches(ph,q);}),q);});
    input.addEventListener('blur',function(){setTimeout(hide,150);});
    input.addEventListener('keydown',function(e){if(e.key==='Escape'){hide();input.blur();}});
  }
  var indexEl=document.getElementById('photographer-index');
  if(indexEl){try{start(normalize(JSON.parse(indexEl.textContent)));}catch(e){}return;}
  fetch('/card-data.json').then(function(r){return r.json();}).then(function(data){start(normalize(data.photographers||[]));}).catch(function(){});
})();
</script>"""


# ---------------------------------------------------------------------------
# Country configs
# ---------------------------------------------------------------------------

# Country-page registry is the SOURCE OF TRUTH (bootstrapped once by
# scripts/build_country_registry.py). Each entry: slug, codes[], nameJa,
# nameEn, lead, updated.

# Expected ordered member IDs for France (regression guard for the pilot)
FRANCE_EXPECTED_IDS = [
    "daguerre", "nadar", "legray", "nicephore-niepce",
    "marey", "marville", "demachy", "eugene-atget",
    "jacques-henri-lartigue", "paul-geniaux", "louis-vaire", "manray",
    "cartierbresson", "brassai", "robert-doisneau", "francois-kollar",
    "marcel-bovis", "izis", "jean-luc-moulene", "sophie-calle",
    "marine-hugonnier", "jean-pierre-khazem", "jean-luc-mylayne",
    "bruno-serralongue", "yto-barrada", "valerie-belin", "claude-closky",
    "luc-delahaye", "charles-freger", "philippe-terrier-hermann",
]


def _toks(v: str) -> set[str]:
    return {t.strip() for t in v.split("/") if t.strip()}


def get_members(config: dict, card_data: list[dict]) -> list[dict]:
    """Members = photographers whose nationality contains ALL the page codes
    (single page: 1 code; composite page: both codes). Sorted era↑ then idx↑."""
    codes = set(config["codes"])
    members = [p for p in card_data
               if codes <= _toks(p.get("nationality") or "")]
    members.sort(key=lambda p: (int(p["era"]), p["idx"]))
    return members


def assert_members(config: dict, members: list[dict]) -> None:
    """Validate a page's membership; France has an exact regression guard."""
    actual_ids = [m["id"] for m in members]
    if config["slug"] == "france" and actual_ids != FRANCE_EXPECTED_IDS:
        print("ASSERTION FAILED: France member list changed!", file=sys.stderr)
        print(f"Expected: {FRANCE_EXPECTED_IDS}", file=sys.stderr)
        print(f"Actual:   {actual_ids}", file=sys.stderr)
        sys.exit(1)
    if not actual_ids:
        print(f"ASSERTION FAILED: {config['slug']} has zero members", file=sys.stderr)
        sys.exit(1)
    missing = [mid for mid in actual_ids
               if not (REPO / "photographers" / f"{mid}.html").exists()]
    if missing:
        print(f"ASSERTION FAILED: {config['slug']} missing pages: {missing}", file=sys.stderr)
        sys.exit(1)


def generate_country_page(config: dict, era_style_block: str,
                           archive_card_css: str,
                           archive_lookup: dict[str, str],
                           card_data: list[dict],
                           strip_pairs: list[tuple[str, str]]) -> str:
    """Generate the full HTML for a country hub page."""
    members = get_members(config, card_data)
    assert_members(config, members)

    member_count = len(members)
    card_map = {p["id"]: p for p in card_data}

    # Build transformed cards HTML
    cards_html_parts = []
    for m in members:
        pid = m["id"]
        article = archive_lookup.get(pid)
        if not article:
            print(f"WARNING: {pid} not found in archive.html", file=sys.stderr)
            continue
        transformed = transform_card(article, pid, card_map.get(pid, {}))
        cards_html_parts.append(transformed)
    cards_html = "\n".join(cards_html_parts)

    codes = config["codes"]
    code = codes[0]
    code_str = " / ".join(codes)
    vol_code = "·".join(codes)
    slug = config["slug"]
    name_ja = config["nameJa"]
    name_en = config["nameEn"]
    lead = config["lead"]
    updated = config["updated"]
    is_multi = len(codes) > 1

    # Hero art. Single: F<span>R</span>. Composite: HU<span>/FR</span> (shrunk via modifier).
    if is_multi:
        art_text = codes[0] + "<span>/" + "/".join(codes[1:]) + "</span>"
    else:
        art_text = code[0] + (f'<span>{code[1:]}</span>' if len(code) > 1 else '')
    hero_class = "era-hero country-hero country-hero--multi" if is_multi else "era-hero country-hero"

    # Horizontal "国から読む" strip (all single country pages, current one active)
    country_strip = "\n".join(
        f'    <a class="era-nav__item{" is-active" if s == slug else ""}" '
        f'href="/countries/{s}.html">{label}</a>'
        for s, label in strip_pairs
    )

    canonical_url = f"https://eyescosmos.github.io/countries/{slug}.html"
    en_url = f"https://eyescosmos.github.io/en/countries/{slug}.html"
    og_image = "https://eyescosmos.github.io/assets/ogp-default.png"
    title = f"{name_ja}の写真史｜写真家と表現の流れ｜写真の座標"
    description = f"美術館・アーカイブ資料を手がかりに、{name_ja}の写真史を、代表的な写真家・運動・時代背景の関係から整理します。"

    google_fonts_link = (
        '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:'
        'wght@400;500;700;900&family=Noto+Serif+JP:wght@400;500;700&family=Inter:'
        'wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&family='
        'Cormorant+Garamond:ital,wght@1,500;1,600&display=swap" rel="stylesheet">'
    )

    mobile_search_block = (
        '<div class="head__mobile-search">'
        '<form class="ph-side-search__form" onsubmit="return false;">'
        '<label class="ph-side-search__label" for="ph-search-input-mobile">SEARCH · 写真家を探す</label>'
        '<div class="ph-side-search__field">'
        '<input class="ph-side-search__input" id="ph-search-input-mobile" type="search" '
        'placeholder="SEARCH · 写真家を探す" autocomplete="off" aria-autocomplete="list" '
        'aria-controls="ph-search-suggestions-mobile" aria-expanded="false">'
        '<button class="ph-side-search__btn" type="button" aria-label="検索">'
        '<svg width="14" height="14" viewBox="0 0 14 14" fill="none">'
        '<circle cx="5.5" cy="5.5" r="4.5" stroke="currentColor" stroke-width="1.5"/>'
        '<line x1="9" y1="9" x2="13" y2="13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>'
        '</svg>'
        '</button>'
        '</div>'
        '</form>'
        '<ul class="ph-search-suggestions" id="ph-search-suggestions-mobile" role="listbox" hidden></ul>'
        '</div>'
    )

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical_url}">
<link rel="alternate" hreflang="ja" href="{canonical_url}">
<link rel="alternate" hreflang="en" href="{en_url}">
<link rel="alternate" hreflang="x-default" href="{canonical_url}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical_url}">
<meta property="og:site_name" content="写真の座標">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{og_image}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{google_fonts_link}
<link rel="stylesheet" href="../styles/card-v4-base.css"><link rel="stylesheet" href="../styles/card-v5-overrides.css">
{era_style_block}
{COUNTRY_CSS_OVERRIDES}
{archive_card_css}
{GA_BLOCK}
</head>
<body class="lang-jp v51">
<div class="page">

<!-- ── HEADER ─────────────────────────────────────────────── -->
<header class="head" data-nosnippet>
  <div class="head__brand">
    <span class="head__brand-ja"><a href="../index.html"><span class="head__brand-photo">写真</span>の座標</a></span>
    <span class="head__brand-en">Photo Coordinates</span>
  </div>
  <div class="head__crumbs">
    <em>COUNTRIES</em><span class="sep">/</span>{name_ja} <span class="sep">·</span>{name_en} <span class="sep">·</span>UPDATED&nbsp;<span class="updated-date">{updated}</span>
  </div>
  <div class="head__meta">
    <div class="head__lang"><a class="is-active">JP</a><a href="{en_url}">EN</a></div>
  </div>
{mobile_search_block}</header>

<!-- ── COUNTRY HERO ───────────────────────────────────────── -->
<section class="{hero_class}">
  <div class="era-hero__art">
    <div class="era-hero__art-label">COUNTRY · {name_ja}</div>
    <div class="era-hero__art-year">{art_text}</div>
  </div>
  <div class="era-hero__info">
    <div class="era-hero__eyebrow">§ — Country Index — 国で読む</div>
    <h1 class="era-hero__title">{name_ja}</h1>
    <div class="era-hero__period">{name_en}</div>
    <p class="era-hero__lead">{lead}</p>
    <div class="era-hero__meta-row">
      <span class="era-hero__meta-item">Photographers <strong>{member_count}</strong></span>
      <span class="era-hero__meta-item">Country <strong>{name_ja}</strong></span>
      <span class="era-hero__meta-item">Code <strong>{code_str}</strong></span>
      <span class="era-hero__meta-item">Vol <strong>COUNTRY · {vol_code}</strong></span>
    </div>
  </div>
</section>

<!-- ── STICKY: 検索 ＋ 国から読む ───────────────────────────── -->
<div class="country-sticky">
  <div class="country-toolbar" data-nosnippet>
    <label class="toolbar__search">
      <input type="search" id="country-filter" placeholder="写真家名・運動・国・タグで検索…" autocomplete="off" aria-label="この国の写真家を検索">
    </label>
  </div>
  <nav class="era-nav country-strip" data-nosnippet aria-label="国ナビゲーション">
    <div class="era-nav__label">§ — 国から読む</div>
    <div class="era-nav__strip">
{country_strip}
    </div>
  </nav>
</div>

<!-- ── MAIN CONTENT ───────────────────────────────────────── -->
<div class="era-outer">
  <div class="era-layout era-layout--solo">

    <!-- MAIN COLUMN -->
    <main class="era-main">

      <!-- Photographers section -->
      <section class="ph-section">
        <div class="ph-section__head">
          <div class="ph-section__title">
            <span class="ph-section__num">§ PH</span>
            <span class="ph-section__name">{name_ja}の写真家</span>
          </div>
        </div>
        <div class="ph-section__body">
          <div class="cards" id="cards-grid">

{cards_html}

          </div>
          <div class="er-no-result" id="er-no-result">該当する写真家がいません</div>
        </div>
      </section>

    </main>

  </div><!-- /.era-layout -->
</div><!-- /.era-outer -->

<!-- ── SITE DIRECTORY LINKS ──────────────────────────────── -->
<nav class="site-directory-links" aria-label="サイト内リンク" data-nosnippet>
  <div class="site-directory-group">
    <div class="site-directory-label">年代一覧</div>
    <div class="site-directory-items">{SITE_DIR_ERAS}</div>
  </div>
  <div class="site-directory-group">
    <div class="site-directory-label">国一覧</div>
    <div class="site-directory-items">{SITE_DIR_COUNTRIES}</div>
  </div>
  <div class="site-directory-group">
    <div class="site-directory-label">代表写真家一覧</div>
    <div class="site-directory-items">{SITE_DIR_PHOTOGRAPHERS}</div>
  </div>
</nav>

<!-- ── FOOTER ──────────────────────────────────────────────── -->
<footer class="foot" data-nosnippet>
  <div>© Photo Coordinates · 写真の座標</div>
  <div class="foot__center">美術館・アーカイブ・専門資料に基づく</div>
  <div class="foot__right"><a href="/privacy-policy.html">プライバシー</a></div>
</footer>

</div><!-- /.page -->
{CARD_FILTER_SCRIPT}
{SEARCH_SCRIPT_MOBILE}
</body>
</html>
"""
    return html


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_movements_select() -> str:
    """Full movements dropdown listing every movements/*.html page."""
    names = sorted(
        Path(f).stem for f in glob.glob(str(REPO / "movements" / "*.html"))
        if not f.endswith("-backup.html")
    )
    opts = ['<option value="" selected>関連する運動</option>']
    for n in names:
        opts.append(f'<option value="/movements/{n}.html">{n}</option>')
    return ('<select class="tax-select filter-select nav-select" aria-label="関連する運動" '
            'onchange="if(this.value) window.location.href=this.value">'
            + "".join(opts) + "</select>")


def filter_country_links(fragment: str, allowed: set[str]) -> str:
    """Drop <option>/<a> entries for country slugs not in `allowed`
    (used to remove retired composite pages from nav + site directory)."""
    fragment = re.sub(
        r'<option value="/countries/([^"]+)\.html">.*?</option>',
        lambda m: m.group(0) if m.group(1) in allowed else '',
        fragment,
    )
    fragment = re.sub(
        r'<a href="/countries/([^"]+)\.html">.*?</a>',
        lambda m: m.group(0) if m.group(1) in allowed else '',
        fragment,
    )
    return fragment


def main() -> None:
    global MOVEMENTS_SELECT, COUNTRIES_SELECT, SITE_DIR_COUNTRIES

    # Load era page for style block
    era_path = REPO / "eras" / "1839.html"
    era_html = era_path.read_text(encoding="utf-8")
    era_style_block = extract_era_style_block(era_html)
    print(f"Extracted style block: {len(era_style_block)} bytes")

    # Load archive.html
    archive_path = REPO / "archive.html"
    archive_html = archive_path.read_text(encoding="utf-8")
    archive_lookup = build_archive_id_lookup(archive_html)
    print(f"Archive lookup: {len(archive_lookup)} entries")
    archive_card_css = extract_archive_card_css(archive_html)
    print(f"Archive card CSS: {len(archive_card_css)} bytes")

    # Load card-data.json
    card_data_path = REPO / "card-data.json"
    card_data = json.loads(card_data_path.read_text(encoding="utf-8"))["photographers"]
    print(f"Card data: {len(card_data)} photographers")

    # Full movements dropdown (all movement pages) — shared by every country page
    MOVEMENTS_SELECT = build_movements_select()
    print(f"Movements dropdown: {MOVEMENTS_SELECT.count('<option')} options")

    # Load the country-page registry (source of truth)
    registry = json.loads((REPO / "data" / "country-pages.json").read_text(encoding="utf-8"))
    print(f"Country registry: {len(registry)} pages")

    # Restrict country nav + site directory to pages that still exist as full
    # pages (composite pages are retired to redirect stubs).
    allowed_slugs = {r["slug"] for r in registry}
    COUNTRIES_SELECT = filter_country_links(COUNTRIES_SELECT, allowed_slugs)
    SITE_DIR_COUNTRIES = filter_country_links(SITE_DIR_COUNTRIES, allowed_slugs)
    print(f"Country nav restricted to {len(allowed_slugs)} single pages")

    # Ordered (slug, label) pairs for the horizontal "国から読む" strip
    strip_pairs = re.findall(
        r'<option value="/countries/([^"]+)\.html">([^<]+)</option>', COUNTRIES_SELECT)

    # Optional: limit to given slugs (e.g. python3 … --only france)
    only = set(sys.argv[2:]) if len(sys.argv) > 1 and sys.argv[1] == "--only" else None

    # Generate pages
    total = 0
    for config in registry:
        if only and config["slug"] not in only:
            continue
        html = generate_country_page(config, era_style_block, archive_card_css,
                                     archive_lookup, card_data, strip_pairs)
        out_path = REPO / "countries" / f"{config['slug']}.html"
        out_path.write_text(html, encoding="utf-8")
        total += 1
    print(f"\nGenerated {total} country pages.")


if __name__ == "__main__":
    main()
