#!/usr/bin/env python3
"""archive.html（日本語・新デザイン）から archive-en.html を生成する。

英語 lede の優先順位:
  1. data/photographer-essay-overrides.js の leadEn
  2. en/index.html TOP12 ハードコードカードの英語 lede
  3. en/photographers/{id}.html の冒頭段落（定型文は除外）
  4. このスクリプト内の手動翻訳（MANUAL_LEDES / MOVEMENT_LEDES）

実行: python3 scripts/build_archive_en.py
出力: en/archive.html
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build_movement_slug_map():
    """en/movements のリダイレクトスタブ（日本語ファイル名）から 日本語名.html → 英語スラッグ.html の対応表を作る"""
    d = os.path.join(ROOT, 'en', 'movements')
    mapping = {}
    for fn in os.listdir(d):
        if not fn.endswith('.html') or fn.isascii():
            continue
        with open(os.path.join(d, fn), encoding='utf-8') as f:
            head = f.read(1000)
        m = re.search(r'url=https://eyescosmos\.github\.io/en/movements/([^"]+?\.html)', head)
        if m:
            mapping[fn] = m.group(1)
    return mapping


MOVEMENT_SLUG_MAP = build_movement_slug_map()

LEDE_MAX = 178  # 日本語版の86字トランケートに視覚的に相当する英語の長さ

# ── チャンネル接頭辞（日本語 → 英語）。接尾辞（· 以降）は既に英語なので維持 ──
CHANNEL_PREFIX = {
    '写真史の論点': 'Topics in photo history',
    '写真史の入口': 'An entry into photo history',
    '読む報道写真': 'Documentary as reading',
    '制度を作る写真': 'Building the institution',
    '写真集という方法': 'The photobook as method',
    '都市と瞬間': 'City and the moment',
    'イメージを疑う': 'Questioning the image',
    '並べて見る写真': 'Seeing in series',
    '写真運動': 'Movement',
    '東ドイツ写真': 'East German Photography',
}

# ── メタ行の国名 → コード（en/index.html の "US · 1864–1946" 形式に合わせる） ──
COUNTRY_CODE = {
    'アメリカ': 'US', 'イギリス': 'GB', 'フランス': 'FR', 'ドイツ': 'DE',
    '日本': 'JP', 'イタリア': 'IT', 'オランダ': 'NL', 'オーストリア': 'AT',
    'カナダ': 'CA', 'スイス': 'CH', 'ロシア': 'RU', 'ブラジル': 'BR',
    'ハンガリー': 'HU', 'デンマーク': 'DK', 'ルクセンブルク': 'LU',
    'レバノン': 'LB', 'ケニア': 'KE', '南アフリカ': 'ZA', 'アルバニア': 'AL',
    'メキシコ': 'MX', 'ベトナム': 'VN',
    'BE': 'BE',
}

# ── タグ（国名はチップとして読めるよう正式名称にする） ──
COUNTRY_TAG = {
    'アメリカ': 'United States', 'イギリス': 'United Kingdom', 'フランス': 'France',
    'ドイツ': 'Germany', '日本': 'Japan', 'イタリア': 'Italy', 'オランダ': 'Netherlands',
    'オーストリア': 'Austria', 'カナダ': 'Canada', 'スイス': 'Switzerland',
    'ロシア': 'Russia', 'ブラジル': 'Brazil', 'ハンガリー': 'Hungary',
    'デンマーク': 'Denmark', 'ルクセンブルク': 'Luxembourg', 'レバノン': 'Lebanon',
    'ケニア': 'Kenya', '南アフリカ': 'South Africa', 'アルバニア': 'Albania',
}

GENRE_TAG = {
    'FSA写真': 'FSA Photography',
    'アメリカ写真': 'American photography',
    'イギリス写真': 'British photography',
    'カラー写真': 'Color Photography',
    'カロタイプ': 'Calotype',
    'コンセプチュアル': 'Conceptual',
    'コンセプチュアルアート': 'Conceptual Art',
    'シネマトグラフィック写真': 'Cinematographic Photography',
    'シュルレアリスム': 'Surrealism',
    'ステージド写真': 'Staged Photography',
    'スティルライフ': 'Contemporary Still Life',
    'ポストインターネット': 'Post-Internet',
    'インティメイト・ライフ': 'Intimate Life',
    'ストリート写真': 'Street Photography',
    'ストレート写真': 'Straight Photography',
    'タイポロジー写真': 'Typological Photography',
    'ダダ': 'Dada',
    'デュッセルドルフ派': 'Dusseldorf School',
    'ドキュメンタリー': 'Documentary',
    'ニューカラー': 'New Color',
    'ニュー・トポグラフィックス': 'New Topographics',
    'バウハウス': 'Bauhaus',
    'ピクチャーズ世代': 'Pictures Generation',
    'ピクトリアリズム': 'Pictorialism',
    'フェミニズム写真': 'Feminist Photography',
    'フォトジャーナリズム': 'Photojournalism',
    'プライベート写真': 'Private Photography',
    'プロヴォーク': 'Provoke',
    'ヘリオグラフィー': 'Heliography',
    'ポートレート': 'Portrait',
    'モダニズム': 'Modernism',
    'リアリズム写真': 'Realism Photography',
    'レイオグラフ': 'Rayograph',
    'ヴォルテクシズム': 'Vorticism',
    '写真分離派': 'Photo-Secession',
    '写真石版': 'Photolithography',
    '大判カラー写真': 'Large-Format Color',
    '実験的技法': 'Experimental techniques',
    '建築写真': 'Architectural photography',
    '戦争写真': 'War photography',
    '新しいヴィジョン': 'New Vision',
    '新即物主義': 'Neue Sachlichkeit',
    '日本写真': 'Japanese Photography',
    'デジタル写真': 'Digital Photography',
    '明治ドキュメンタリー': 'Meiji documentary',
    '植民地写真': 'Colonial photography',
    '決定的瞬間': 'Decisive Moment',
    '環境写真': 'Environmental photography',
    '発明・技術': 'Invention & technology',
    '社会ドキュメンタリー': 'Social Documentary',
    '社会的写真': 'Concerned photography',
    '私写真': 'I-Photography',
    '写真集文化': 'Photobook Culture',
    '写真と彫刻': 'Photography and Sculpture',
    '報道写真': 'Press Photography',
    'ライカ': 'Leica',
    '写真集': 'Photobook',
    'ポストソ連': 'Post-Soviet',
    '人新世': 'Anthropocene',
    '産業風景': 'Industrial landscape',
    '演出写真': 'Staged Photography',
    '映画的写真': 'Cinematic Photography',
    '郊外': 'Suburbia',
    '家族写真': 'Family photography',
    '移行期': 'Transition',
    '身体': 'The Body',
    '大判写真': 'Large-format photography',
    '美術館': 'Museums',
    'ヴィジュアル・アクティヴィズム': 'Visual Activism',
    'クィア・アーカイブ': 'Queer Archive',
    '旅写真': 'Travel photography',
    'アクティヴィズム': 'Activism',
    '旅': 'Travel',
    '科学写真': 'Scientific photography',
    '肖像写真': 'Portrait photography',
    '自然主義写真': 'Naturalistic Photography',
    '都市記録': 'Urban documentation',
    '風景写真': 'Landscape photography',
    '働く女性': 'Working Women',
    '東ドイツ写真': 'East German Photography',
    'ファッション写真': 'Fashion Photography',
    'ファッション/ドキュメンタリー': 'Fashion / Documentary',
}

# overrides に leadEn がなく、TOP12・英語ページからも取れない写真家の手動翻訳
MANUAL_LEDES = {
    'emerson': "Emerson condemned studio staging as 'dishonest' and made the single negative and single exposure the condition of photographic art. His ground was Hermann von Helmholtz's physiology of vision — only the fovea sees sharply, while peripheral vision softens of itself.",
    'steichen': "Steichen's starting point in Pictorialism was the judgment that looking like painting was photography's most effective strategy for winning artistic status equal to it. Born in Luxembourg and raised in America, he drew from childhood and absorbed the tonalism of James Whistler.",
    'williamklein': "Born in New York, Klein studied painting under Fernand Léger in postwar Paris and moved among American painters such as Ellsworth Kelly. Spotted in 1954 by Vogue's art director Alexander Liberman, he returned to New York as a photographer for the magazine.",
    'tomatsu': "Shomei Tomatsu was born in Nagoya in 1930, of the generation mobilized into munitions factories during the war, and met the American occupation directly at its end. The 'love-hate' he felt toward the occupiers shaped the themes of his life's work.",
    'winogrand': "Garry Winogrand, born in the Bronx, began as a freelance magazine photographer in the 1950s and kept a 35mm Leica with him constantly, shooting fast on the street. His style has been described as dynamic compositions built on sharp diagonals, close to Abstract Expressionism.",
    'friedlander': "Lee Friedlander, born in Aberdeen, Washington, studied photography at the Art Center School in Los Angeles from 1953 and worked from New York for magazines such as Esquire and Sports Illustrated from 1956. In 1966 Nathan Lyons included him in 'Toward a Social Landscape' at George Eastman House.",
    'mapplethorpe': "Robert Mapplethorpe was born in Flushing, New York, in 1946. After studying art at Pratt Institute he began photographing with a Polaroid camera in 1970, developing his self-taught practice into studio photography.",
    'kruger': "Barbara Kruger was born in Newark, New Jersey, in 1945. After studying under Diane Arbus and Marvin Israel at Parsons, she became an art director at Condé Nast's Mademoiselle in her early twenties.",
    'eggleston': "William Eggleston was born in Memphis, Tennessee, in 1939. He began shooting 35mm color film in the 1960s, and in 1976 MoMA presented 'William Eggleston's Guide,' curated by John Szarkowski.",
    'gursky': "Born in Leipzig in 1955 to a family of photographers, Gursky studied under Otto Steinert at the Folkwang school before joining Bernd Becher's class at the Düsseldorf Academy, carrying the Bechers' typological method toward the global spaces of capitalism.",
    'salgado': "Born in Minas Gerais, Brazil, in 1944, Salgado came to photography in Africa while working as a World Bank economist, convinced that photographs could show human suffering that figures and reports could not. He turned to photography in 1973, joining Magnum by way of Gamma and Sygma.",
    'eugene-atget': "Atget took up the camera around 1897, at forty. Having given up his hopes as actor and painter, he printed 'Documents pour artistes' on his card and made his living selling reference photographs of Paris to painters and craftsmen.",
    'jacques-henri-lartigue': "Jacques Henri Lartigue began photographing in 1901, at the age of seven. With cameras given by his wealthy industrialist father, he photographed family games at the house in Boulogne, early aviation experiments, motor races, and skiing.",
    'gabriel-orozco': "A conceptual artist from Mexico, Orozco records the poetry latent in everyday things in photographs while working across sculpture, painting, and installation. Key works include La DS and Empty Shoe Box.",
    'fabian-marti': "A Swiss artist combining photography, painting, and collage, Marti works on themes of mysticism and altered states of consciousness, known for his idiosyncratic use of darkroom processes and light-sensitive materials.",
    'jp-木村伊兵衛': "Ihei Kimura connected the speed of the small camera to literary-figure portraits, the street corners of Tokyo, and everyday life in Akita, helping to shape postwar Japanese realism and the institutions of photography. Known as a master of the Leica, his influence runs through the postwar realism debate, print media, and the Ihei Kimura Photography Award that bears his name.",
}

# 運動カード31件の英語 lede（ledeJa からの翻訳）。キーは nameEn
MOVEMENT_LEDES = {
    'Pictorialism': "Pictorialism was an international movement of the late 19th and early 20th centuries that sought recognition for photography as an art equal to painting and printmaking. At its core was the claim that a print is not a mere copy but a work bearing its maker's judgment.",
    'Photo-Secession': "The Photo-Secession was the group Alfred Stieglitz founded in New York in 1902 — an institutional campaign to have photography accepted as art. What mattered was less a shared style than how Camera Work, gallery 291, exhibitions, and collecting reorganized the way photographs were shown.",
    'Straight Photography': "Straight photography distanced itself from the painterly manipulations of Pictorialism, building a language specific to the medium out of lens sharpness, tonal range, composition, and the precision of the print — returning the photographer's decisions to the conditions of the medium itself.",
    'Modernism': "Modernist photography was a broad current of the early 20th century that sought to turn photography into a visual language fit for modern life amid urbanization, industrialization, and the expansion of print culture. Abstraction, steep angles, close-ups, and repetition were its surface, not its core.",
    'Neue Sachlichkeit': "Neue Sachlichkeit, the German movement of the 1920s, avoided sentiment and expressionist exaggeration, placing things and people under a cool, lucid gaze. Its 'objectivity' was not naturally given but constructed through frontality, even light, repetition, serialization, and placement in print.",
    'New Vision': "The New Vision unfolded through the 1920s and 30s on the idea that photography could break habitual ways of seeing and train a perception fit for the modern body and city. Bird's-eye views, extreme close-ups, photograms, and montage were devices for seeing the world otherwise.",
    'Bauhaus': "The Bauhaus names less a single photographic school than a history in which photography's role was reorganized where teaching, printing, advertising, architecture, stage, and design education crossed — from Moholy-Nagy's experimental vision to Lucia Moholy's documentation and its circulation in print.",
    'Vorticism': "Vorticism was a London avant-garde of the 1910s that condensed the energy of machines, cities, and speed into abstract form. It matters in photo history because Alvin Langdon Coburn's Vortographs are discussed as early abstract photographs that broke from depicting a subject.",
    'Dada': "Dada treated the photograph not as evidence of reality or a beautiful print but as material to be cut, pasted, rearranged, and made to work politically in print. Its importance for photo history lies in photomontage turning mass-reproduced media images into a weapon of critique.",
    'Surrealism': "Surrealist photography did not merely take dream, the unconscious, chance, and desire as subjects; it showed that a medium so bound to reality could itself produce the uncanny. Its core discovery was that an utterly ordinary photograph can look strange once its context shifts.",
    'Rayograph / Photogram': "Rayograph is the name Man Ray gave his cameraless photographs, made by placing objects directly on photographic paper and exposing them to light. In the context of Dada and Surrealism it was understood as turning the contact of things and light itself into an image.",
    'Naturalistic Photography': "Naturalistic photography, advanced by P. H. Emerson in the late 19th century, rejected contrived composites and allegorical staging, photographing nature and everyday life with focus and tonality close to actual visual experience.",
    'Realism Photography': "Realism was a powerful word in postwar Japanese photography, epitomized by Ken Domon's call for the 'absolutely unstaged, absolute snapshot' — an ethic of facing social reality head-on without staging or sentimental retouching. It was never a simple doctrine of non-intervention.",
    'Documentary': "Documentary photography is a broad term for photographs that record real events and lived worlds, but its meaning has shifted from era to era. What persists is the tension between photographs treated as evidence and the editing, captions, institutions, and positions that shape them.",
    'Social Documentary': "Social documentary makes poverty, labor, housing, migration, discrimination, and disaster visible, aiming at reform and the shaping of public opinion. It does not simply record reality: which reality is brought into public view is a political choice from the start.",
    'Photojournalism': "Photojournalism conveys current events through photographs, but its substance was never the single decisive image alone. It is an institution of reporting that includes magazine and newspaper editing, captions, layout, distribution, copyright, and even the means of getting to the story.",
    'FSA Photography': "FSA photography was the U.S. government's documentation program under the New Deal, systematically photographing rural communities, migrant workers, and small towns through the Depression — at once individual works and instruments of state publicity and archiving.",
    'Decisive Moment': "The decisive moment spread with the title of Henri Cartier-Bresson's 1952 book: the ideal of seizing the instant when form, movement, and meaning condense. In practice it was a method sustained by the small camera's mobility, bodily training on the street, and publishing culture.",
    'Street Photography': "Street photography captures chance crossings, gestures, signs, traffic, and anonymous relations in public space. Shooting in the street is not enough: it asks where to stand within the city's rhythm, when to release the shutter, and how to keep an ethical distance from strangers.",
    'Provoke': "Provoke was the Japanese movement that unfolded around the photography-and-theory magazine founded in 1968, and it cannot be grasped through the look of are-bure-boke alone. Behind it lay distrust that language could grasp reality, and the instability of urban experience in high-growth Japan.",
    'I-Photography (Shi-shashin)': "I-photography (shi-shashin) took shape in Japan from the 1970s, taking family, lovers, rooms, the body, memory, and death as its subjects — not as private records but as works that turn the distance between seeing and living itself into form.",
    'New Color': "New Color, in 1970s America, raised color from the gloss of advertising and tourism into a serious language of art photography for reading suburbs, roadsides, household goods, signs, and asphalt. Around Eggleston and Shore, color carried the temperature and vulgarity of everyday life.",
    'Color Photography': "The history of color photography is not only a history of inventing ways to reproduce color. Following hand-coloring, autochromes, Kodachrome, magazine advertising, family snapshots, and museum reception, color unsettled the border between commerce and art each time it changed what photographs mean.",
    'Large-Format Color': "Large-format color combines the precision of the view camera with the informational density of color, pushing photography to a scale that competes with painting and cinema in the exhibition space. Density of detail, distance, and the bodily experience of the gallery sustain the work's meaning.",
    'Dusseldorf School': "The Düsseldorf School grew from the teaching of Bernd and Hilla Becher, showing postwar Germany's industrial landscapes, museums, crowds, markets, and architecture analytically through large prints and series — rethinking photography's institutions through typology, scale, and the art market.",
    'Typological Photography': "Typological photography photographs like objects under identical conditions, repeatedly, and sets them side by side so that difference and structure can be read through comparison. The aim is not to erase individuality — repetition makes visible how individuality appears.",
    'Conceptual Art': "In conceptual art, photography served less to make beautiful images than to carry ideas, instructions, records, and institutional critique. As concept and procedure outweighed the material object from the late 1960s into the 70s, photography became the flexible tool of execution and evidence.",
    'Pictures Generation': "The Pictures Generation is the group of artists discussed from the 1977 exhibition 'Pictures' onward, quoting ready-made images from advertising, film, magazines, and television to critique authorship, originality, gender representation, and consumer culture.",
    'Staged Photography': "Staged photography does not wait for chance reality but constructs the situation before shooting — scene, light, placement of figures, props, at times digital compositing. It turns to its advantage the fact that even a staged scene carries photographic conviction.",
    'Feminist Photography': "Feminist photography is not a label for work by women photographers but a practice that critically asks how photography has represented women's bodies, domestic labor, desire, advertising, family, and work — recasting photography as a site where the power of the gaze operates.",
    'Cinematographic Photography': "Cinematographic photography is not a name for stills that merely look like film; it is a tendency in contemporary photography concerned with how much a single image can carry — the before and after of a scene, the artificiality of lighting, the gaps in a story.",
}

# 英語個別ページが存在しない写真家（日本語ページへリンクする）
# fabian-marti / gabriel-orozco は EN ページ作成済みのため除外（2026-06-19）
NO_EN_PAGE: set[str] = {'jp-木村伊兵衛'}


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def unesc(t):
    return (t.replace('&amp;', '&').replace('&#x27;', "'").replace('&quot;', '"')
             .replace('&lt;', '<').replace('&gt;', '>'))


def truncate_lede(t, limit=LEDE_MAX):
    t = re.sub(r'\s+', ' ', t).strip()
    if len(t) <= limit:
        return t
    cut = t[:limit]
    cut = cut[:cut.rfind(' ')] if ' ' in cut else cut
    return cut.rstrip(' ,;:.') + ' …'


def parse_overrides_lead_en():
    src = open(os.path.join(ROOT, 'data/photographer-essay-overrides.js'), encoding='utf-8').read()
    starts = []
    for m in re.finditer(r"\n\s{0,4}(['\"]?)([A-Za-z0-9_\-jp一-鿿぀-ヿ]+)\1\s*:\s*\{", src):
        starts.append((m.group(2), m.start()))
    for m in re.finditer(r"overrides\[['\"]([^'\"]+)['\"]\]\s*=\s*\{", src):
        starts.append((m.group(1), m.start()))
    starts.sort(key=lambda x: x[1])
    lead = {}
    for i, (k, s) in enumerate(starts):
        e = starts[i + 1][1] if i + 1 < len(starts) else len(src)
        chunk = src[s:e]
        m = (re.search(r"leadEn:\s*`(.*?)`\s*,?\s*\n", chunk, re.S)
             or re.search(r"leadEn:\s*(['\"])(.*?)\1\s*,?\s*\n", chunk, re.S))
        if m:
            txt = m.group(1) if m.re.pattern.startswith('leadEn:\\s*`') else m.group(2)
            txt = txt.strip()
            if len(txt) > 40:
                lead[k] = txt
    return lead


def parse_top12_en():
    src = open(os.path.join(ROOT, 'en/index.html'), encoding='utf-8').read()
    out = {}
    for m in re.finditer(r'<h3 class="pc-body__name">([^<]+)</h3>.*?<p class="pc-body__lede">(.*?)</p>', src, re.S):
        name = unesc(m.group(1).strip())
        if '${' in name:
            continue
        out[name] = unesc(m.group(2).strip())
    return out


def en_page_lede(pid):
    fp = os.path.join(ROOT, f'en/photographers/{pid}.html')
    if not os.path.exists(fp):
        return None
    t = open(fp, encoding='utf-8').read()
    m = re.search(r'<h1[^>]*>', t)
    m2 = re.search(r'<p[^>]*>(.*?)</p>', t[m.end():] if m else t, re.S)
    if not m2:
        return None
    txt = re.sub(r'<[^>]+>', '', m2.group(1))
    txt = re.sub(r'\*\d+', '', txt)
    txt = unesc(re.sub(r'\s+', ' ', txt).strip())
    if 'is a key figure for understanding' in txt or txt.startswith('Continue to') or len(txt) < 60:
        return None
    return txt


def main():
    d = json.load(open(os.path.join(ROOT, 'card-data.json')))
    name_ja2en = {}
    for c in d['photographers'] + d['movements']:
        name_ja2en[c['nameJa']] = c['nameEn']
    name_en2id = {p['nameEn']: p['id'] for p in d['photographers']}

    lead_en = parse_overrides_lead_en()
    top12 = parse_top12_en()

    def photographer_lede(name_en):
        pid = name_en2id.get(name_en)
        if pid and pid in lead_en:
            return lead_en[pid]
        if name_en in top12:
            return top12[name_en]
        if pid:
            t = en_page_lede(pid)
            if t:
                return t
            if pid in MANUAL_LEDES:
                return MANUAL_LEDES[pid]
        raise SystemExit(f'No English lede for photographer: {name_en} ({pid})')

    def tr_tag(tag):
        if tag in GENRE_TAG:
            return GENRE_TAG[tag]
        if tag in COUNTRY_TAG:
            return COUNTRY_TAG[tag]
        if tag in name_ja2en:
            return name_ja2en[tag]
        # 「アメリカ / イギリス」型の複合国
        parts = [p.strip() for p in tag.split('/')]
        if len(parts) > 1 and all(p in COUNTRY_TAG for p in parts):
            return ' / '.join(COUNTRY_TAG[p] for p in parts)
        if re.search(r'[぀-ヿ一-鿿]', tag):
            raise SystemExit(f'Unmapped Japanese tag: {tag}')
        return tag

    def tr_meta(meta):
        meta = unesc(meta)
        m = re.match(r'^(\d{4}s) / \d{4}年代$', meta)
        if m:
            return m.group(1)
        m = re.match(r'^1 photographers linked$', meta)
        if m:
            return '1 photographer linked'
        m = re.match(r'^(.+?) · (.+)$', meta)
        if m and re.search(r'[぀-ヿ一-鿿]', m.group(1)):
            parts = [p.strip() for p in m.group(1).split('/')]
            codes = [COUNTRY_CODE.get(p, p) for p in parts]
            return ' / '.join(codes) + ' · ' + m.group(2)
        # bare JA country name with no years (e.g. stub entries orozco/marti)
        if meta in COUNTRY_CODE:
            return COUNTRY_CODE[meta]
        return meta

    def tr_channel(ch):
        ch = ch.strip()
        if ' · ' in ch:
            pre, suf = ch.split(' · ', 1)
            pre = CHANNEL_PREFIX.get(pre.strip(), pre.strip())
            suf = suf.strip()
            if re.search(r'[぀-ヿ一-鿿]', suf):
                # 既存の英語接尾辞（DOCUMENTARY 等）に合わせて大文字化する
                suf = tr_tag(suf).upper()
            return f'{pre} · {suf}'
        return CHANNEL_PREFIX.get(ch, ch)

    src = open(os.path.join(ROOT, 'archive.html'), encoding='utf-8').read()

    def tr_card(m):
        card = m.group(0)
        is_movement = 'pc-card--movement' in card
        nm = re.search(r'<h3 class="pc-body__name">([^<]*)</h3><div class="pc-body__name-en">([^<]*)</div>', card)
        name_ja_raw, name_en_raw = nm.group(1), nm.group(2)
        name_en = unesc(name_en_raw)

        # 名前ブロック: 英語を主、日本語を副に入れ替え
        card = card.replace(nm.group(0),
                            f'<h3 class="pc-body__name">{name_en_raw}</h3><div class="pc-body__name-en">{name_ja_raw}</div>')

        # lede
        if is_movement:
            if name_en not in MOVEMENT_LEDES:
                raise SystemExit(f'No English lede for movement: {name_en}')
            lede = MOVEMENT_LEDES[name_en]
        else:
            lede = photographer_lede(name_en)
        card = re.sub(r'(<p class="pc-body__lede">).*?(</p>)',
                      lambda mm: mm.group(1) + esc(truncate_lede(lede)) + mm.group(2),
                      card, flags=re.S)

        # meta
        card = re.sub(r'(<div class="pc-body__meta">)(.*?)(</div>)',
                      lambda mm: mm.group(1) + esc(tr_meta(re.sub(r'<[^>]+>', '', mm.group(2)))) + mm.group(3),
                      card)

        # channel
        ch_m = re.search(r'<div class="pc-body__channel">(.*?)</div>', card)
        channel_en = tr_channel(unesc(ch_m.group(1)))
        card = card.replace(ch_m.group(0), f'<div class="pc-body__channel">{esc(channel_en)}</div>')

        # tags
        tags_m = re.search(r'<div class="pc-body__tags">(.*?)</div>', card, re.S)
        tags_ja = re.findall(r'<span class="pc-body__tag">([^<]*)</span>', tags_m.group(1))
        tags_en = [tr_tag(unesc(t)) for t in tags_ja]
        tags_html = ''.join(f'<span class="pc-body__tag">{esc(t)}</span>' for t in tags_en)
        card = card.replace(tags_m.group(0), f'<div class="pc-body__tags">{tags_html}</div>')

        # CTA
        card = card.replace('<span>写真史上の位置を読む</span>', '<span>Read their place in photo history</span>')

        # data-search: 日本語名 + 英語名 + 英語チャンネル + 英語タグ
        search = ' '.join([unesc(name_ja_raw), name_en, channel_en] + tags_en)
        card = re.sub(r'data-search="[^"]*"', f'data-search="{esc(search)}"', card)

        # href
        href_m = re.search(r'<a href="([^"]+)" target', card)
        href = href_m.group(1)
        if is_movement:
            if href.startswith('/movements/'):
                fn = unesc(href[len('/movements/'):])
                new_href = '/en/movements/' + MOVEMENT_SLUG_MAP.get(fn, fn)
            else:
                new_href = href
        else:
            pid = name_en2id.get(name_en, '')
            if pid in NO_EN_PAGE:
                new_href = '/' + href.lstrip('/')
            else:
                new_href = '/en/' + href.lstrip('/')
        card = card.replace(f'<a href="{href}" target', f'<a href="{new_href}" target', 1)
        return card

    out = re.sub(r'<article class="pc-card.*?</article>', tr_card, src, flags=re.S)

    # hint / meta に残る年代表記
    out = re.sub(r'(\d{4}s) / \d{4}年代', r'\1', out)
    out = out.replace('<div class="pc-top__hint">TOMISHIGE TOKUJI · 明治期</div>',
                      '<div class="pc-top__hint">TOMISHIGE TOKUJI · MEIJI ERA</div>')
    out = out.replace('<div class="pc-body__meta">JP · 明治期</div>',
                      '<div class="pc-body__meta">JP · Meiji era</div>')

    # ── ページ chrome ──
    JA_TITLE = '写真家アーカイブ｜時代・国・運動から探す｜写真の座標'
    EN_TITLE = 'Photographer Archive | Browse by Era, Country, and Movement | Photo Coordinates'
    JA_DESC = ('写真史を316枚のカードで整理した写真家アーカイブ。世界と日本の写真家285人と31の写真運動を、'
               '時代・国・運動・タグで検索・絞り込みできる。各カードから写真史上の位置づけの解説ページへ。')
    EN_DESC = ('Browse global and Japanese photographers by era, country, movement, and visual approach. '
               'Using museum, archive, and specialist sources, Photo Coordinates organizes relationships '
               'among photographers and their place in photo history.')
    chrome = [
        ('<html lang="ja">', '<html lang="en">'),
        (f'<title>{JA_TITLE}</title>', f'<title>{EN_TITLE}</title>'),
        (f'<meta name="description" content="{JA_DESC}">', f'<meta name="description" content="{EN_DESC}">'),
        ('<link rel="canonical" href="https://eyescosmos.github.io/archive.html">',
         '<link rel="canonical" href="https://eyescosmos.github.io/en/archive.html">'),
        ('<meta property="og:site_name" content="写真の座標 Photo Coordinates">',
         '<meta property="og:site_name" content="Photo Coordinates">'),
        (f'<meta property="og:title" content="{JA_TITLE}">', f'<meta property="og:title" content="{EN_TITLE}">'),
        (f'<meta property="og:description" content="{JA_DESC}">', f'<meta property="og:description" content="{EN_DESC}">'),
        ('<meta property="og:url" content="https://eyescosmos.github.io/archive.html">',
         '<meta property="og:url" content="https://eyescosmos.github.io/en/archive.html">'),
        ('<meta property="og:locale" content="ja_JP">', '<meta property="og:locale" content="en_US">'),
        ('<meta property="og:locale:alternate" content="en_US">', '<meta property="og:locale:alternate" content="ja_JP">'),
        (f'<meta name="twitter:title" content="{JA_TITLE}">', f'<meta name="twitter:title" content="{EN_TITLE}">'),
        (f'<meta name="twitter:description" content="{JA_DESC}">', f'<meta name="twitter:description" content="{EN_DESC}">'),
        ('<link rel="stylesheet" href="styles/card-v4-base.css">', '<link rel="stylesheet" href="/styles/card-v4-base.css">'),
        ('<link rel="stylesheet" href="styles/card-v5-overrides.css">', '<link rel="stylesheet" href="/styles/card-v5-overrides.css">'),
        ('<body class="lang-jp v51">', '<body class="lang-en v51">'),
        ('<a href="index.html" class="head__brand"', '<a href="/en/" class="head__brand"'),
        ('<em>INDEX</em><span class="sep">/</span><a href="index.html">TOP</a>',
         '<em>INDEX</em><span class="sep">/</span><a href="/en/">TOP</a>'),
        ('<div class="head__lang"><button class="is-active">JP</button><button>EN</button></div>',
         '<div class="head__lang"><button onclick="location.href=\'/archive.html\'">JP</button><button class="is-active">EN</button></div>'),
        ('<h1 class="archive-hero__title"><em>カード</em>で読む<br>写真史</h1>',
         '<h1 class="archive-hero__title">Photo history<br><em>in cards</em></h1>'),
        ('placeholder="写真家名・運動・国・タグで検索…"', 'placeholder="Search by photographer, movement, country, or tag…"'),
        ('placeholder="写真家名・運動・国・タグで検索"', 'placeholder="Search by photographer, movement, country, or tag"'),
        ('<button class="pill" data-filter="photographer">写真家</button>', '<button class="pill" data-filter="photographer">Photographers</button>'),
        ('<button class="pill" data-filter="movement">運動</button>', '<button class="pill" data-filter="movement">Movements</button>'),
        ('<button class="mobile-filter-chip" data-mobile-type="photographer">写真家</button>',
         '<button class="mobile-filter-chip" data-mobile-type="photographer">Photographers</button>'),
        ('<button class="mobile-filter-chip" data-mobile-type="movement">運動</button>',
         '<button class="mobile-filter-chip" data-mobile-type="movement">Movements</button>'),
        ('表示中 <span class="result-bar__num" id="visible-count">316</span> / 316',
         'Showing <span class="result-bar__num" id="visible-count">316</span> / 316'),
        ('<div class="no-results" id="no-results" data-nosnippet>該当するカードが見つかりませんでした</div>',
         '<div class="no-results" id="no-results" data-nosnippet>No matching cards found</div>'),
        ('<div class="foot__center">美術館・アーカイブ・専門資料に基づく</div>',
         '<div class="foot__center">Based on museum, archive, and specialist sources</div>'),
        ('<div class="foot__right"><a href="privacy-policy.html">プライバシー</a> · <a href="#">コロフォン</a></div>',
         '<div class="foot__right"><a href="/en/privacy-policy.html">Privacy</a> · <a href="#">Colophon</a></div>'),
    ]
    for a, b in chrome:
        if a not in out:
            raise SystemExit(f'Chrome string not found: {a[:60]}')
        out = out.replace(a, b)

    dst = os.path.join(ROOT, 'en/archive.html')
    open(dst, 'w', encoding='utf-8').write(out)
    n = len(re.findall(r'<article class="pc-card', out))
    print(f'Wrote {dst} ({n} cards, {len(out)} bytes)')


if __name__ == '__main__':
    main()
