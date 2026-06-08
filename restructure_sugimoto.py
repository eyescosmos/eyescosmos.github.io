#!/usr/bin/env python3
"""
Restructure photographers/hiroshi-sugimoto.html to Adams-compatible format.
"""

import re

HTML_PATH = "/Users/aiharadaisuke/Desktop/claude code/broken picture/photographers/hiroshi-sugimoto.html"

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. Remove <div class="hero"> block ───────────────────────────────────────
# Matches from '    <div class="hero">' through its closing '    </div>'
hero_pattern = re.compile(
    r'    <div class="hero">.*?    </div>\n',
    re.DOTALL,
)
html, hero_count = hero_pattern.subn("", html, count=1)
assert hero_count == 1, f"Expected to remove 1 hero block, removed {hero_count}"

# ── 2. Insert new elements BEFORE <nav class="tab-nav" ───────────────────────
NEW_HEADER_BLOCK = '''    <div class="title-block">
    <div class="article-no">§ 064 — Photographer Index — コンセプチュアルアート</div>
    <h1 class="title">杉本博司</h1>
    <div class="en-title">Hiroshi Sugimoto<span class="years">1948–</span></div>
  </div>
    <div class="lead-abstract">
      <p class="lead">自然史博物館のジオラマ、映画館の投影光、海の水平線、蝋人形の肖像、数理模型や光学実験を、大判カメラと長時間露光で撮影してきた作家。杉本博司は、被写体の内容だけでなく、展示・映画・肖像・科学模型・暗室技術が「本物らしく見える像」を生む過程を作品化し、写真が時間や歴史をどのように像へ変えるかを問い続けている。</p>
    </div>
    <div class="thesis">
    <div class="thesis-label">この写真家が変えたこと</div>
    <p class="thesis-body">杉本博司は写真の「記録機能」を否定した人ではなく、〈ジオラマ〉〈劇場〉〈海景〉〈人物〉という連作を通じて、展示・映画館・蝋人形・光学実験が「現実らしく見える像」を作る条件を、写真の問題として<em>系統的に可視化した</em>作家である。長時間露光と大判カメラを、時間の蓄積と現実らしさの生産を顕在化させる方法として運用することで、記録媒体としての写真が自明ではなく、つねに条件によって支えられていることを定着させた。</p>
  </div>
    <dl class="entry-meta">
    <dt>Entry</dt><dd>No. 064</dd>
    <dt>Category</dt><dd>Photographer</dd>
    <dt>Country</dt><dd><a href="/countries/japan.html">日本</a></dd>
    <dt>Years</dt><dd>1948–</dd>
    <dt>Period</dt><dd><a href="/eras/1970.html">1970 — 1980s</a></dd>
    <dt>Movement</dt><dd><a href="/movements/コンセプチュアルアート.html">コンセプチュアルアート</a></dd>
    <dt>Updated</dt><dd>2026.05.29</dd>
  </dl>
    <div class="page-keywords"><b>キーワード:</b><a href="/movements/コンセプチュアルアート.html">コンセプチュアルアート</a><span class="kw-sep">/</span>長時間露光<span class="kw-sep">/</span>時間<span class="kw-sep">/</span>記憶<span class="kw-sep">/</span>ゼラチンシルバー<span class="kw-sep">/</span>ジオラマ</div>
    <section class="section view-works-section">
        <h2>作品を見る</h2>
        <p class="view-works-note">本サイトでは作品画像を掲載していません。下記の公式アーカイブで作品をご覧ください。</p>
        <div class="links"><a class="chip-link" href="https://www.sugimotohiroshi.com/new-page-54" target="_blank" rel="noopener">Hiroshi Sugimoto — Dioramas ↗</a><a class="chip-link" href="https://www.sugimotohiroshi.com/new-page-7" target="_blank" rel="noopener">Hiroshi Sugimoto — Theaters ↗</a><a class="chip-link" href="https://www.sugimotohiroshi.com/seascapes-1" target="_blank" rel="noopener">Hiroshi Sugimoto — Seascapes ↗</a><a class="chip-link" href="https://www.moma.org/collection/works/49997" target="_blank" rel="noopener">MoMA — Polar Bear ↗</a><a class="chip-link" href="https://www.metmuseum.org/art/collection/search/267318" target="_blank" rel="noopener">The Met — Avalon Theatre, Catalina Island ↗</a><a class="chip-link" href="https://www.moma.org/collection/works/45308" target="_blank" rel="noopener">MoMA — U.A. Walker, New York ↗</a></div>
      </section>
    <nav class="tab-nav"'''

html = html.replace('    <nav class="tab-nav"', NEW_HEADER_BLOCK, 1)
assert 'title-block' in html, "title-block not inserted"

# ── 3. Insert TOC between </nav> and <div class="section-grid"> ──────────────
TOC_BLOCK = '''    </nav>
    <details class="toc">
      <summary class="toc-summary">目次</summary>
      <ol class="toc-list">
        <li class="toc-section">
          <a href="#sec-01"><span class="toc-num">§ 01</span> 経歴</a>
        </li>
        <li class="toc-section">
          <a href="#sec-02"><span class="toc-num">§ 02</span> 表現解説</a>
          <ul class="toc-sub">
            <li><a href="#h3-01">写真が本物らしさを作る場所</a></li>
            <li><a href="#h3-02">映画の時間を光として残す</a></li>
            <li><a href="#h3-03">水平線、原初の記憶、反復</a></li>
            <li><a href="#h3-04">歴史を再撮影する肖像</a></li>
            <li><a href="#h3-05">見えない形、光、電気を写真へ移す</a></li>
            <li><a href="#h3-06">なぜ写真だったのか</a></li>
          </ul>
        </li>
        <li class="toc-section">
          <a href="#sec-03"><span class="toc-num">§ 03</span> 批評と受容</a>
        </li>
      </ol>
    </details>
    <div class="section-grid">'''

html = html.replace('    </nav>\n    <div class="section-grid">', TOC_BLOCK, 1)
assert 'toc-summary' in html, "TOC not inserted"

# ── 4. Update section headings ────────────────────────────────────────────────
# 経歴 → §01
html = html.replace(
    '      <section class="section">\n        <h2>経歴</h2>',
    '      <section class="section">\n<h2 id="sec-01" class="sec-heading"><span class="sec-num">§ 01 / 03</span><span class="sec-title">経歴</span></h2>',
    1,
)
assert 'sec-01' in html, "sec-01 not inserted"

# 表現解説 → §02
html = html.replace(
    '      <section class="section">\n        <h2>表現解説</h2>',
    '      <section class="section">\n<h2 id="sec-02" class="sec-heading"><span class="sec-num">§ 02 / 03</span><span class="sec-title">表現解説</span></h2>',
    1,
)
assert 'sec-02' in html, "sec-02 not inserted"

# 批評と受容 → §03
html = html.replace(
    '      <section class="section">\n        <h2>批評と受容</h2>',
    '      <section class="section">\n<h2 id="sec-03" class="sec-heading"><span class="sec-num">§ 03 / 03</span><span class="sec-title">批評と受容</span></h2>',
    1,
)
assert 'sec-03' in html, "sec-03 not inserted"

# ── 5. Convert h4 → h3 with ids in 表現解説 ONLY ────────────────────────────
h4_replacements = [
    ('<h4>写真が本物らしさを作る場所</h4>', '<h3 id="h3-01">写真が本物らしさを作る場所</h3>'),
    ('<h4>映画の時間を光として残す</h4>',   '<h3 id="h3-02">映画の時間を光として残す</h3>'),
    ('<h4>水平線、原初の記憶、反復</h4>',   '<h3 id="h3-03">水平線、原初の記憶、反復</h3>'),
    ('<h4>歴史を再撮影する肖像</h4>',       '<h3 id="h3-04">歴史を再撮影する肖像</h3>'),
    ('<h4>見えない形、光、電気を写真へ移す</h4>', '<h3 id="h3-05">見えない形、光、電気を写真へ移す</h3>'),
    ('<h4>なぜ写真だったのか</h4>',         '<h3 id="h3-06">なぜ写真だったのか</h3>'),
]
for old, new in h4_replacements:
    assert old in html, f"h4 not found: {old}"
    html = html.replace(old, new, 1)

assert 'h3-01' in html and 'h3-06' in html, "h3 ids not inserted"

# ── 6. Replace books + 外部リンク + 関連作品 block ──────────────────────────
NEW_SECTIONS = '''      <section class="section related-section">
        <h2>関連する写真家・運動</h2>
        <div class="related-label">関連する写真家</div>
        <ul class="related-list">
          <li><a href="/photographers/yasumasa-morimura.html">森村泰昌</a> ― 写真・美術史のイメージを身体で再演し、真贋・記録・表象を問い続けた同時代の日本人作家</li>
          <li><a href="/photographers/takuma-nakahira.html">中平卓馬</a> ― 写真と言語・制度との関係を批判的に問い直した、杉本とは異なる文脈での日本のコンセプチュアル写真の展開</li>
        </ul>
        <div class="related-label">関連する運動・概念</div>
        <ul class="related-list">
          <li><a href="/movements/コンセプチュアルアート.html">コンセプチュアルアート</a> ― あらかじめ定めた概念・方法から制作を始めるという点で、杉本の各連作と共鳴する</li>
        </ul>
      </section>
      <section class="section further-section" data-affiliate-section data-nosnippet>
        <h2>さらに読む</h2>
        <div class="further-label">写真集・作品集</div>
        <div class="book">
          <div class="book-title">杉本博司 写真集</div>
          <div class="book-meta">代表的写真集・作品集</div>
          <div class="book-note">〈ジオラマ〉〈劇場〉〈海景〉などの連作を収録した主要写真集。Amazon で確認できます。</div>
          <a class="chip-link amazon-cta" href="https://amzn.to/4cGhDk0" target="_blank" rel="noopener sponsored">Amazon で見る ↗</a>
          <span class="affiliate-disclosure">※アフィリエイトリンクを含みます</span>
        </div>
        <div class="book">
          <div class="book-title">関連写真集 2</div>
          <div class="book-meta">関連写真集・作品資料</div>
          <div class="book-note">関連する作品集・展覧会カタログ。</div>
          <a class="chip-link amazon-cta" href="https://amzn.to/4tAqZUt" target="_blank" rel="noopener sponsored">Amazon で見る ↗</a>
          <span class="affiliate-disclosure">※アフィリエイトリンクを含みます</span>
        </div>
        <div class="book">
          <div class="book-title">関連写真集 3</div>
          <div class="book-meta">関連写真集・展覧会資料</div>
          <div class="book-note">杉本博司の近年の展覧会・活動に関連する資料。</div>
          <a class="chip-link amazon-cta" href="https://amzn.to/48tfWUy" target="_blank" rel="noopener sponsored">Amazon で見る ↗</a>
          <span class="affiliate-disclosure">※アフィリエイトリンクを含みます</span>
        </div>
        <div class="further-label">関連データベース・アーカイブ</div>
        <ul class="further-links">
          <li><a href="https://www.sugimotohiroshi.com/biography-1" target="_blank" rel="noopener">Hiroshi Sugimoto Official — Exhibitions</a>（作家公式サイト：展覧会一覧・各連作解説）</li>
          <li><a href="https://art21.org/watch/art-in-the-twenty-first-century/s3/hiroshi-sugimoto-in-memory-segment/" target="_blank" rel="noopener">Art21 — Hiroshi Sugimoto in "Memory"</a>（時間・化石・写真観についての作家インタビュー動画）</li>
          <li><a href="https://www.timesensitive.fm/episode/hiroshi-sugimoto-on-photography-as-a-form-of-timekeeping" target="_blank" rel="noopener">Time Sensitive — Photography as a Form of Timekeeping</a>（写真と時間をめぐる詳細インタビュー）</li>
          <li><a href="https://fraenkelgallery.com/artists/hiroshi-sugimoto" target="_blank" rel="noopener">Fraenkel Gallery — Hiroshi Sugimoto</a>（ギャラリー作家ページ：略歴と作品一覧）</li>
          <li><a href="https://ucca.org.cn/en/exhibition/hiroshi-sugimoto/" target="_blank" rel="noopener">UCCA — Hiroshi Sugimoto: Time Machine</a>（UCCAによる50年回顧展の解説）</li>
        </ul>
      </section>'''

# Build the pattern to match the old block:
# from '      <section class="section" data-affiliate-section data-nosnippet>'
# through the closing </section> of 関連作品
old_block_pattern = re.compile(
    r'      <section class="section" data-affiliate-section data-nosnippet>.*?</section>\s*'
    r'      <section class="section"><h2>関連作品</h2>.*?</section>',
    re.DOTALL,
)
html, block_count = old_block_pattern.subn(NEW_SECTIONS, html, count=1)
assert block_count == 1, f"Expected to replace 1 old block, replaced {block_count}"
assert 'further-section' in html, "further-section not inserted"
assert 'related-section' in html, "related-section not inserted"
assert '外部リンク' not in html, "外部リンク still present"
assert '関連作品' not in html, "関連作品 still present"

# ── 7. 出典 h2 stays unchanged (no action needed) ────────────────────────────

# ── Write result ─────────────────────────────────────────────────────────────
with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("Done. All transformations applied successfully.")

# ── Post-write verification ───────────────────────────────────────────────────
checks = [
    ("hero removed",           "hero" not in html and "facts-grid" not in html),
    ("toc-summary exists",     "toc-summary" in html),
    ("details.toc exists",     'class="toc"' in html),
    ("sec-heading exists",     "sec-heading" in html),
    ("sec-01 exists",          "sec-01" in html),
    ("sec-02 exists",          "sec-02" in html),
    ("sec-03 exists",          "sec-03" in html),
    ("h3-01 exists",           "h3-01" in html),
    ("h3-06 exists",           "h3-06" in html),
    ("外部リンク gone",        "外部リンク" not in html),
    ("関連作品 gone",          "関連作品" not in html),
    ("further-section exists", "further-section" in html),
    ("related-section exists", "related-section" in html),
    ("cite-31 preserved",      "cite-31" in html),
]

all_ok = True
for label, result in checks:
    status = "OK" if result else "FAIL"
    if not result:
        all_ok = False
    print(f"  [{status}] {label}")

if all_ok:
    print("\nAll checks passed.")
else:
    print("\nSome checks FAILED — review output above.")
