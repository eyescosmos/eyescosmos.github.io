#!/usr/bin/env python3
"""Restructure /photographers/ansel-adams.html per spec."""

import re
import sys

FILE = "/Users/aiharadaisuke/Desktop/claude code/broken picture/photographers/ansel-adams.html"

# ── helpers ──────────────────────────────────────────────────────────────────

def ok(msg):  print(f"  [OK]  {msg}")
def fail(msg, detail=""): print(f"  [FAIL] {msg}" + (f"\n        {detail}" if detail else ""))

# ── read ──────────────────────────────────────────────────────────────────────

with open(FILE, encoding="utf-8") as f:
    content = f.read()

original = content  # keep for comparison

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — update section numbers 03 → 04
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== Step 1: Update section numbers (03 → 04) ===")

old1 = '§ 01 / 03</span><span class="sec-title">背景と時代'
new1 = '§ 01 / 04</span><span class="sec-title">背景と時代'
old2 = '§ 02 / 03</span><span class="sec-title">表現の核心'
new2 = '§ 02 / 04</span><span class="sec-title">表現の核心'

if old1 in content:
    content = content.replace(old1, new1, 1)
    ok("§ 01 / 03 → § 01 / 04")
else:
    fail("Could not find §01/03 marker")

if old2 in content:
    content = content.replace(old2, new2, 1)
    ok("§ 02 / 03 → § 02 / 04")
else:
    fail("Could not find §02/03 marker")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — replace §03/03 + books section with new §03/04, §04/04,
#           related-section, further-section
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== Step 2: Replace §03/03 + books block ===")

MARKER_START = '<section class="section">\n<h2 class="sec-heading"><span class="sec-num">§ 03 / 03</span><span class="sec-title">批評と写真史上の位置</span>'
MARKER_END   = '      <section class="section">\n        <h2>外部リンク</h2>'

NEW_CONTENT = '''<section class="section">
<h2 class="sec-heading"><span class="sec-num">§ 03 / 04</span><span class="sec-title">代表作・方法・媒体</span></h2>
<div class="essay works">
<h3>《Monolith, the Face of Half Dome》1927年</h3>
<p>《<a href="https://www.metmuseum.org/art/collection/search/262595" rel="noopener" target="_blank">Monolith, the Face of Half Dome, Yosemite National Park, California</a>》は1927年にヨセミテで撮影され、のちに複数の年代にわたるプリントが作られた。The Metは同作を1927年のネガから1974年にプリントされたゼラチン・シルバー・プリントとして収蔵記録している<sup class="sup-ref"><a href="#cite-11">*11</a></sup>。ハーフドームの岩壁は、黒く落とされた空、岩の面、前景のシルエットが緊張する垂直の構成として現れ、地形の記録ではなく光の秩序としての自然表現を示している。同一ネガから異なる時期に複数のプリントが作られた事実は、「ネガは楽譜、プリントは演奏」というアダムスの比喩——撮影後の暗室での判断を制作の中心に置く姿勢——の実践として読める。MoMAのプレスリリースも、同じネガから時期の異なるプリントが作られることを通じて、この考えを説明している<sup class="sup-ref"><a href="#cite-8">*8</a></sup>。David Sheffによるインタビューでアダムスは、フィルムの限界の中でフィルター、露出、現像、暗室作業を選び、プリントにしたい価値をあらかじめ考えると説明しており、Monolithはその「予見」という姿勢の初期例として位置づけられる<sup class="sup-ref"><a href="#cite-20">*20</a></sup>。</p>
<h3>《Moonrise, Hernandez, New Mexico》1941年</h3>
<p>《<a href="https://www.nga.gov/artworks/66680-moonrise-hernandez-new-mexico" rel="noopener" target="_blank">Moonrise, Hernandez, New Mexico</a>》は1941年、ニューメキシコのエルナンデスで偶然に出会った光景を撮影したものである。National Gallery of Artは同作を1941年撮影・1980年プリントのゼラチン・シルバー・プリントとして公開し、月、低い山並み、教会と墓地が暗い空の下に配置される視覚記述を付している<sup class="sup-ref"><a href="#cite-12">*12</a></sup>。月、雲、墓地の白い十字架、遠い山並みが偶然に一瞬だけ並んだこの画面は、プリント上では強い明暗の配置として成立している。インタビューでアダムスは、この作品の空を暗く焼き込むことで雲の存在をほとんど消し、最初に抱いた劇的な視覚化へ近づけたと説明している<sup class="sup-ref"><a href="#cite-20">*20</a></sup>。偶然の遭遇を、露出選択と暗室での焼き込みによって「予見された」構成へ変える過程が凝縮されたこの作品は、同一ネガから多くのプリントが作られ、アダムス自身の最晩年まで刷り続けられた。</p>
<h3>マンザナー日系人収容所写真 1943年</h3>
<p>1943年、アダムスは陸軍の許可を得てカリフォルニア州マンザナー日系人強制収容所を訪れ、収容された日系人の生活を写真に記録した。Library of Congressはこのシリーズのネガとプリントを並列公開し、トリミングや暗室処理の差異も確認できるようにしている<sup class="sup-ref"><a href="#cite-13">*13</a></sup>。同コレクションには肖像、日常生活、農作業、スポーツ、余暇の写真が含まれ、強制収容という制度の中に置かれた日系人の生活が記録されている。アダムスはこの仕事を1944年に『<a href="https://www.loc.gov/pictures/collection/manz/book.html" rel="noopener" target="_blank">Born Free and Equal</a>』としてU.S. Cameraから刊行し、写真と自身の文章によって収容所内の生活を公刊した<sup class="sup-ref"><a href="#cite-14">*14</a></sup>。Japanese American National Museumは、Library of Congress、Center for Creative Photography、Honolulu Academy of Arts、同館に残る50点以上のヴィンテージプリントを集めた「Ansel Adams at Manzanar」展でこの仕事を再検討した<sup class="sup-ref"><a href="#cite-15">*15</a></sup>。マンザナー写真は、国立公園の崇高な自然だけでなく、戦時下の国家制度と人間の尊厳という問題にも向けられていたアダムスの仕事の射程を示している。</p>
<h3>媒体としての大判カメラと教育</h3>
<p>アダムスの仕事は個々の作品にとどまらず、大判ビューカメラ、ゾーンシステム、暗室技術の体系的な記述として残された。Center for Creative Photographyは、アダムスのアーカイブが2,500点以上のファインプリントに加え、書簡、インタビュー、未刊原稿、機材、商業写真、展覧会資料、シエラクラブ関連資料を含むと説明しており、彼の仕事が作品だけでなく方法論と教育の集積として残されたことがわかる<sup class="sup-ref"><a href="#cite-2">*2</a></sup>。アリゾナ大学の「Performing the Print」紹介は、同一ネガから作られた複数のプリントを比較することで、トリミング、覆い焼き、焼き込み、全体のコントラストと明るさにおけるアダムスの判断が見えると述べている<sup class="sup-ref"><a href="#cite-9">*9</a></sup>。『The Camera』『The Negative』『The Print』の三部作（Little, Brown, 1980–1983年）は、ゾーンシステムと暗室作業をアダムス自身が体系化した教科書であり、「ネガは楽譜、プリントは演奏」という比喩の実践的な根拠として位置づけられる。1975年のアリゾナ大学Center for Creative Photography共同設立は、制作の蓄積を教育と研究のアーカイブとして制度化する試みだった<sup class="sup-ref"><a href="#cite-2">*2</a></sup>。</p>
</div>
</section>
<section class="section">
<h2 class="sec-heading"><span class="sec-num">§ 04 / 04</span><span class="sec-title">批評と写真史上の位置</span></h2>
<div class="essay">
<h3>同時代の対立軸 ― 純粋写真とドキュメンタリー</h3>
<p>1930年代のアメリカ写真史において、Group f/64が追求した写真のメディウム的純粋性は、ロイ・ストライカーが指揮するFSA（農業安定局）ドキュメンタリー写真の潮流と並行して展開した。ウォーカー・エヴァンスやドロシア・ラングが属したFSAは、大恐慌と農村の窮乏を社会変革の文脈で記録することを目指したのに対し、アダムスとGroup f/64は、写真のシャープネス、階調、プリントの物質性を前景化することで、ドキュメンタリーの社会的文脈とは異なる地平に写真の自律性を確立しようとした。シカゴ美術館のスティーグリッツ資料は、ストランドが媒材の限界と潜在的な性質を尊重し技巧的な操作に頼らない写真を主張した流れの中に、アダムスを含む後続のストレート写真家を位置づけている<sup class="sup-ref"><a href="#cite-21">*21</a></sup>。SFMOMAは、Group f.64の遺産を、女性写真家、人種的不正義、労働者の権利、都市文化まで含めて読み直しており、この「純粋写真」の潮流が社会的なテーマと完全に切断されていたわけではないことも示している<sup class="sup-ref"><a href="#cite-6">*6</a></sup>。マンザナー写真は、この対立軸をアダムス自身の内部で交差させた例として読むことができる。</p>
<h3>後続世代による継承と乗り越え</h3>
<p>一方で、近年の展覧会は、アダムスをただの「自然写真の巨匠」として称賛するだけではなく、そのイメージが作ったアメリカ西部像を問い直している。Portland Art Museumの「Ansel Adams in Our Time」は、アダムスの初期作品から成熟期の国立公園写真までをたどりながら、ジョナサン・カルム、ジグ・ジャクソン、ウィル・ウィルソンら同時代作家を並置し、アダムスの国立公園イメージを、土地所有、帰属、環境危機、アメリカ西部の表象をめぐる現在の問いと並べて見直す展示として構成した<sup class="sup-ref"><a href="#cite-17">*17</a></sup>。SFMOMAのGroup f.64再検討も、同運動の遺産を、ベイエリア写真史、女性写真家、人種・労働・政治的文脈、現代作家の応答の中で読み直している<sup class="sup-ref"><a href="#cite-6">*6</a></sup>。</p>
<h3>制度的な広がりと再評価</h3>
<p>アダムスの受容は、《Moonrise, Hernandez, New Mexico》やヨセミテの名作イメージによって強く形づくられてきた。MoMAの作家ページは、同館オンラインで多数の作品を公開し、彼が複数の展覧会に関わってきたことを示している<sup class="sup-ref"><a href="#cite-18">*18</a></sup>。National Gallery of Artも作家ページで96点の作品群を公開しており、彼の写真がアメリカ近代写真の主要な美術館コレクションに深く組み込まれていることがわかる<sup class="sup-ref"><a href="#cite-19">*19</a></sup>。SFMOMAの「Ansel Adams at 100」は、彼が自然保護の代弁者として愛されたことと、写真家としての美学的達成が混同されやすいことを指摘し、作家としての再評価を企図した展覧会だった<sup class="sup-ref"><a href="#cite-24">*24</a></sup>。したがって、アダムスの歴史的位置は、高精細な大判風景写真を完成させた作家というだけではない。彼は、写真を絵画から独立させるための精度、音楽的な演奏としてのプリント、自然保護の公共的イメージ、写真教育と美術館制度、戦時下の日系人収容所記録を交差させた作家である。彼の写真の本質は、自然を美しく見せることではなく、自然や人間や場所が、光、ネガ、紙、制度、鑑賞者の記憶を通って、どのような「見るべき対象」へ変わるのかを制御しようとした点にある。</p>
</div>
</section>
      <section class="section related-section">
        <h2>関連する写真家・運動</h2>
        <div class="related-label">関連する写真家</div>
        <ul class="related-list">
          <li><a href="/photographers/stieglitz.html">アルフレッド・スティーグリッツ</a> ― 1936年のAn American Place個展でアダムスを認めた、アメリカ近代写真の制度的な後ろ盾</li>
          <li><a href="/photographers/strand.html">ポール・ストランド</a> ― 1930年の出会いがアダムスをピクトリアリズムからストレート写真へ向かわせた直接の契機</li>
          <li><a href="/photographers/edward-weston.html">エドワード・ウェストン</a> ― Group f/64の共同創設者、純粋写真を西海岸で組み立てた同志</li>
          <li><a href="/photographers/lange.html">ドロシア・ラング</a> ― 同時代のFSAドキュメンタリーを代表する社会派の視点。マンザナー写真でアダムスと対比される</li>
          <li><a href="/photographers/friedlander.html">リー・フリードランダー</a> ― アダムス的な崇高な風景を都市の断片で解体した次世代</li>
        </ul>
        <div class="related-label">関連する運動</div>
        <ul class="related-list">
          <li><a href="/movements/ストレート写真.html">ストレート写真</a> ― アダムスが技術と教育を通じて完成させた潮流</li>
          <li><a href="/movements/ピクトリアリズム.html">ピクトリアリズム</a> ― アダムスが1930年に決別した、絵画的な前世代の写真</li>
          <li><a href="/movements/モダニズム.html">モダニズム</a> ― 写真の自律性を主張する近代写真の大きな枠組み</li>
        </ul>
      </section>
      <section class="section further-section" data-affiliate-section data-nosnippet>
        <h2>さらに読む</h2>
        <div class="further-label">写真集</div>
        <div class="book">
          <div class="book-title">Ansel Adams: 400 Photographs</div>
          <div class="book-meta">Andrea G. Stillman 編 / Little, Brown / 2007年</div>
          <div class="book-note">ヨセミテからマンザナーまで、アダムスの代表作を網羅する定番。ゾーンシステムとアメリカ西部の風景表現を一冊で押さえられる。</div>
          <a class="chip-link amazon-cta" href="https://amzn.to/4sZuUtE" target="_blank" rel="noopener sponsored">Amazon で見る ↗</a>
          <span class="affiliate-disclosure">※アフィリエイトリンクを含みます</span>
        </div>
        <div class="further-label">方法論・技術書</div>
        <div class="book">
          <div class="book-title">The Camera / The Negative / The Print（三部作）</div>
          <div class="book-meta">Ansel Adams / Little, Brown / 1980–1983年</div>
          <div class="book-note">ゾーンシステムと暗室作業をアダムス自身が体系化した教科書三部作。「ネガは楽譜、プリントは演奏」という比喩の実践的な根拠がここにある。</div>
          <a class="chip-link amazon-cta" href="https://amzn.to/4mpp8iA" target="_blank" rel="noopener sponsored">Amazon で見る ↗</a>
          <span class="affiliate-disclosure">※アフィリエイトリンクを含みます</span>
        </div>
        <div class="further-label">関連データベース・アーカイブ</div>
        <ul class="further-links">
          <li><a href="https://ccp.arizona.edu/artists/ansel-adams/" target="_blank" rel="noopener">Center for Creative Photography — Ansel Adams</a>（アーカイブ全体、書簡・原稿・機材を含む）</li>
          <li><a href="https://www.metmuseum.org/essays/group-f64" target="_blank" rel="noopener">The Met — Group f/64 エッセイ</a>（運動の制度的背景）</li>
          <li><a href="https://www.loc.gov/collections/ansel-adams-manzanar/about-this-collection/" target="_blank" rel="noopener">Library of Congress — マンザナー写真</a>（ネガとプリントを並列公開）</li>
          <li><a href="https://www.nps.gov/yose/learn/historyculture/ansel-adams.htm" target="_blank" rel="noopener">National Park Service — Ansel Adams</a>（環境保護・国立公園との関係）</li>
        </ul>
      </section>
'''

start_idx = content.find(MARKER_START)
if start_idx == -1:
    fail("MARKER_START not found — cannot do Step 2")
    sys.exit(1)

end_idx = content.find(MARKER_END, start_idx)
if end_idx == -1:
    fail("MARKER_END not found — cannot do Step 2")
    sys.exit(1)

content = content[:start_idx] + NEW_CONTENT + content[end_idx:]
ok("Replaced §03/03 + books block with §03/04, §04/04, related-section, further-section")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — prune 4 chip-links from 外部リンク section
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== Step 3: Prune 4 chip-links from 外部リンク ===")

# URLs to remove
REMOVE_URLS = [
    "https://www.nps.gov/yose/learn/historyculture/ansel-adams.htm",
    "https://ccp.arizona.edu/artists/ansel-adams/",
    "https://www.metmuseum.org/essays/group-f64",
    "https://www.loc.gov/collections/ansel-adams-manzanar/about-this-collection/",
]

# We need to operate only inside the 外部リンク section's <div class="links">...</div>
# Locate the 外部リンク section
ext_section_marker = '<section class="section">\n        <h2>外部リンク</h2>'
ext_start = content.find(ext_section_marker)
if ext_start == -1:
    fail("外部リンク section not found")
    sys.exit(1)

# Find the <div class="links"> opening inside that section
links_open = content.find('<div class="links">', ext_start)
links_close = content.find('</div>', links_open) + len('</div>')
links_block = content[links_open:links_close]

# Parse individual chip-link <a> tags and filter
# Pattern: <a class="chip-link" href="URL" ...>...</a>
chip_pattern = re.compile(r'<a class="chip-link"[^>]*href="([^"]+)"[^>]*>.*?</a>', re.DOTALL)

removed = []
def replace_chip(m):
    url = m.group(1)
    for rm_url in REMOVE_URLS:
        if rm_url in url:
            removed.append(url)
            return ''
    return m.group(0)

new_links_block = chip_pattern.sub(replace_chip, links_block)
content = content[:links_open] + new_links_block + content[links_close:]

for url in REMOVE_URLS:
    if any(url in r for r in removed):
        ok(f"Removed chip-link: {url}")
    else:
        fail(f"chip-link NOT found (may already be absent): {url}")

# ─────────────────────────────────────────────────────────────────────────────
# WRITE
# ─────────────────────────────────────────────────────────────────────────────
with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

# ─────────────────────────────────────────────────────────────────────────────
# VERIFICATION
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== Verification ===")

# Re-read fresh
with open(FILE, encoding="utf-8") as f:
    final = f.read()

# V1: §01/04 count == 1, §01/03 count == 0
cnt_01_04 = final.count('§ 01 / 04')
cnt_01_03 = final.count('§ 01 / 03')
if cnt_01_04 == 1 and cnt_01_03 == 0:
    ok(f"§01/04 appears {cnt_01_04} time(s), §01/03 appears {cnt_01_03} time(s)")
else:
    fail(f"§01/04={cnt_01_04}, §01/03={cnt_01_03} (expected 1, 0)")

# V2: §03/04 and §04/04 present; §03/03 absent
has_0304 = '§ 03 / 04' in final
has_0404 = '§ 04 / 04' in final
has_0303 = '§ 03 / 03' in final
if has_0304 and has_0404 and not has_0303:
    ok("§03/04 present, §04/04 present, §03/03 absent")
else:
    fail(f"§03/04={has_0304}, §04/04={has_0404}, §03/03 still present={has_0303}")

# V3: 4 removed URLs absent from 外部リンク section
# Re-locate 外部リンク section in final content
ext_start2 = final.find('<section class="section">\n        <h2>外部リンク</h2>')
ext_end2 = final.find('</section>', ext_start2) + len('</section>')
ext_section_text = final[ext_start2:ext_end2]

for url in REMOVE_URLS:
    if url not in ext_section_text:
        ok(f"Absent from 外部リンク: {url}")
    else:
        fail(f"Still present in 外部リンク: {url}")

# V4: all cite-1 through cite-26 present
missing_cites = []
for i in range(1, 27):
    cid = f'id="cite-{i}"'
    if cid not in final:
        missing_cites.append(f"cite-{i}")
if not missing_cites:
    ok("All cite-1 through cite-26 present")
else:
    fail(f"Missing cite IDs: {', '.join(missing_cites)}")

# V5: line count
line_count = final.count('\n') + 1
ok(f"Output file line count: {line_count}")

print("\nDone.")
