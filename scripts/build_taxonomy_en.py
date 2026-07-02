#!/usr/bin/env python3
"""
build_taxonomy_en.py
====================
Rebuild en/movements/<slug>.html (31 files) and en/eras/<id>.html (11 files)
using the v5.1 Japanese pages as templates, inserting English content.

English content priority:
  1. data/taxonomy-en-content.json  (harvested from old EN pages)
  2. build_archive_en.py MOVEMENT_LEDES table
  3. Manual English translations of Japanese source content

A scope flag is MANDATORY (running with no scope is refused) so an accidental
full rebuild can no longer clobber unrelated EN taxonomy pages:
  python3 scripts/build_taxonomy_en.py --era 2010                  # one era page
  python3 scripts/build_taxonomy_en.py --slug street-photography   # one movement
  python3 scripts/build_taxonomy_en.py --all                       # full rebuild
"""

import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Japanese movement filename ↔ English slug mapping ──────────────────────
STUB_TO_SLUG = {
    'FSA写真':           'fsa-photography',
    'カラー写真':          'color-photography',
    'コンセプチュアルアート':  'conceptual-art',
    'シネマトグラフィック写真': 'cinematographic-photography',
    'シュルレアリスム':       'surrealism',
    'ステージド写真':        'staged-photography',
    'スティルライフ':        'contemporary-still-life',
    'ストリート写真':        'street-photography',
    'ストレート写真':        'straight-photography',
    'タイポロジー写真':      'typological-photography',
    'ダダ':               'dada',
    'デュッセルドルフ派':    'dusseldorf-school',
    'ドキュメンタリー':      'documentary',
    'ニュー・トポグラフィックス': 'new-topographics',
    'ニューカラー':          'new-color',
    'バウハウス':            'bauhaus',
    'ピクチャーズ世代':      'pictures-generation',
    'ピクトリアリズム':      'pictorialism',
    'フェミニズム写真':      'feminist-photography',
    'フォトジャーナリズム':  'photojournalism',
    'プロヴォーク':          'provoke',
    'モダニズム':            'modernism',
    'リアリズム写真':        'realism-photography',
    'レイオグラフ':          'rayograph-photogram',
    'ヴォルテクシズム':      'vorticism',
    '写真分離派':            'photo-secession',
    '大判カラー写真':        'large-format-color',
    '新しいヴィジョン':      'new-vision',
    '新即物主義':            'neue-sachlichkeit',
    '決定的瞬間':            'decisive-moment',
    '社会ドキュメンタリー':  'social-documentary',
    '私写真':               'i-photography-shi-shashin',
    '自然主義写真':          'naturalistic-photography',
}
SLUG_TO_STUB = {v: k for k, v in STUB_TO_SLUG.items()}

# ── English movement names (slug → display name) ───────────────────────────
SLUG_TO_EN_NAME = {
    'fsa-photography':           'FSA Photography',
    'color-photography':         'Color Photography',
    'conceptual-art':            'Conceptual Art',
    'cinematographic-photography': 'Cinematographic Photography',
    'surrealism':                'Surrealism',
    'staged-photography':        'Staged Photography',
    'contemporary-still-life':   'Contemporary Still Life',
    'street-photography':        'Street Photography',
    'straight-photography':      'Straight Photography',
    'typological-photography':   'Typological Photography',
    'dada':                      'Dada',
    'dusseldorf-school':         'Dusseldorf School',
    'documentary':               'Documentary',
    'new-topographics':          'New Topographics',
    'new-color':                 'New Color',
    'bauhaus':                   'Bauhaus',
    'pictures-generation':       'Pictures Generation',
    'pictorialism':              'Pictorialism',
    'feminist-photography':      'Feminist Photography',
    'photojournalism':           'Photojournalism',
    'provoke':                   'Provoke',
    'modernism':                 'Modernism',
    'realism-photography':       'Realism Photography',
    'rayograph-photogram':       'Rayograph / Photogram',
    'vorticism':                 'Vorticism',
    'photo-secession':           'Photo-Secession',
    'large-format-color':        'Large-Format Color',
    'new-vision':                'New Vision',
    'neue-sachlichkeit':         'Neue Sachlichkeit',
    'decisive-moment':           'Decisive Moment',
    'social-documentary':        'Social Documentary',
    'i-photography-shi-shashin': 'I-Photography (Shi-shashin)',
    'naturalistic-photography':  'Naturalistic Photography',
}

# ── Era metadata ───────────────────────────────────────────────────────────
ERA_META = {
    '1839': {'period': '1839–1860s', 'title_en': 'Origins of Photography', 'nav_label': '1839–60s'},
    '1870': {'period': '1870–1890s', 'title_en': 'Industrialization and Reform',  'nav_label': '1870–90s'},
    '1890': {'period': '1890–1910s', 'title_en': 'Pictorialism and Modernism', 'nav_label': '1890–1910s'},
    '1910': {'period': '1910–1920s', 'title_en': 'Modernism and the Avant-Garde', 'nav_label': '1910–20s'},
    '1930': {'period': '1930–1940s', 'title_en': 'Depression, Fascism, and War', 'nav_label': '1930–40s'},
    '1950': {'period': '1950–1960s', 'title_en': 'Cold War and LIFE Magazine', 'nav_label': '1950–60s'},
    '1970': {'period': '1970–1980s', 'title_en': 'Conceptual Art and the Art Market', 'nav_label': '1970–80s'},
    '1980': {'period': '1980–1990s', 'title_en': 'Dusseldorf School and the AIDS Crisis', 'nav_label': '1980–90s'},
    '1990': {'period': '1990–2000s', 'title_en': 'Globalization and Digitalization', 'nav_label': '1990–2000s'},
    '2000': {'period': '2000–2010s', 'title_en': 'Digital Photography and the Photobook', 'nav_label': '2000–10s'},
    '2010': {'period': '2010–2020s', 'title_en': 'Smartphones, Social Media, and Reappraisal', 'nav_label': '2010–20s'},
}

ERA_ORDER = ['1839', '1870', '1890', '1910', '1930', '1950', '1970', '1980', '1990', '2000', '2010']

# ── Japanese→English section name map ─────────────────────────────────────
SECTION_NAME_MAP = {
    '表現解説':   'Expression and Methods',
    '批評と受容': 'Criticism and Reception',
    '関連する表現': 'Related Movements',
    '写真家一覧': 'Photographers',
    '出典':       'Sources',
    'この時代の背景': 'Context of This Era',
    'この時代の写真家': 'Photographers of This Era',
}

# ── UI chrome translations ─────────────────────────────────────────────────
UI_JA_TO_EN = {
    # header / crumbs
    'MOVEMENTS': 'MOVEMENTS',
    'ERAS': 'ERAS',
    'MOVEMENT · 表現': 'MOVEMENT · Expression',
    'ERA · ': 'ERA · ',
    '表現で読む': 'Browse by Movement',
    '時代で読む': 'Browse by Era',
    '§ — Movement — 表現で読む': '§ — Movement',
    '§ — Era Index — 時代で読む': '§ — Era Index',
    # ph-abstract labels
    'Overview · この表現について': 'Overview',
    'Overview · この時代について': 'Overview',
    # ph-thesis labels
    '核心命題': 'Core thesis',
    'この時代が変えたこと': 'What this era changed',
    # section heads
    'Entry · データ': 'Entry · Data',
    'Entry · 時代データ': 'Entry · Era Data',
    'Related · 関連する表現': 'Related Movements',
    'Photographers · 写真家': 'Photographers',
    'Navigate · 移動': 'Navigate',
    'Movements · 運動・ジャンル': 'Movements',
    'Keywords · キーワード': 'Keywords',
    # sidebar meta keys
    'Movement': 'Movement',
    'English': 'English Name',
    'Photogs': 'Photographers',
    'Period': 'Period',
    'Category': 'Category',
    'Updated': 'Updated',
    'Movements': 'Movements',
    'Vol': 'Volume',
    # search
    'SEARCH · 写真家を探す': 'SEARCH · Find a photographer',
    '写真家名・運動・キーワード': 'Photographer, movement, keyword',
    '検索': 'Search',
    # navigation labels in era-nav / mvt-nav
    '§ — 表現で読む': '§ — Movements',
    '§ — 時代で読む': '§ — Eras',
    # footer
    '美術館・アーカイブ・専門資料に基づく': 'Based on museum, archive, and specialist sources',
    'プライバシー': 'Privacy',
    'コロフォン': 'Colophon',
    # card CTA
    '写真史上の位置を読む': 'Read their place in photo history',
    # Photogs count
    'PHOTOGRAPHERS': 'PHOTOGRAPHERS',
    'MOVEMENT': 'MOVEMENT',
    # mvt-hero__meta-row keys
    'Category': 'Category',
    # movement nav label
    '§ — 表現で読む': '§ — Movements',
}

# ── English translations for era context block labels ─────────────────────
ERA_CONTEXT_LABELS_EN = {
    # 1839
    '政治・社会':    'Politics & Society',
    '写真と帝国主義': 'Photography and Imperialism',
    '技術の変遷':    'Technological Change',
    '表現の方向性':  'Directions of Expression',
    # 1870
    '産業化と写真':  'Industrialization and Photography',
    # 1890
    '写真と芸術':    'Photography and Art',
    '日本の写真':    'Photography in Japan',
    # 1910
    '前衛芸術と写真': 'The Avant-Garde and Photography',
    '日本のモダン写真': 'Modern Photography in Japan',
    # 1930
    'FSAとドキュメンタリー': 'FSA and Documentary',
    'LIFE誌とフォトジャーナリズム': 'LIFE Magazine and Photojournalism',
    'マグナムの創設': 'The Founding of Magnum',
    # 1950
    'LIFE誌の黄金期と終焉': 'The Golden Age and End of LIFE Magazine',
    '日本写真の国際化': 'The Internationalization of Japanese Photography',
    'マグナムの定着': 'Magnum Consolidated',
    # 1970
    '写真と美術市場': 'Photography and the Art Market',
    'ピクチャーズ世代': 'Pictures Generation',
    '日本：私写真の深化': 'Japan: The Deepening of I-Photography',
    # 1980
    'デュッセルドルフ派': 'Dusseldorf School',
    'エイズ危機と写真': 'AIDS Crisis and Photography',
    'グローバル化と報道写真': 'Globalization and Photojournalism',
    # 1990
    'デジタル化':    'Digitalization',
    '写真集ルネサンス': 'Photobook Renaissance',
    '日本の1990年代写真': 'Japanese Photography in the 1990s',
    # 2000
    'デジタル普及':  'The Spread of Digital Photography',
    '写真集の全盛':  'The Photobook at its Peak',
    '環境写真':     'Environmental Photography',
    # 2010
    'スマートフォンとSNS': 'Smartphones and Social Media',
    '写真史の再評価': 'Reappraisal of Photography History',
    '写真集市場の拡大': 'Expansion of the Photobook Market',
}

# ── English translations for era context block texts (Japanese→English) ───
# These are translations of the Japanese context block texts.
# Format: {era_id: [{label_en, text_en}, ...]}
ERA_CONTEXT_BLOCKS_EN = {
    '1839': [
        {
            'label': 'Politics & Society',
            'text': 'European empires expanded into Asia and Africa in search of resources. Qing China was defeated in the Opium Wars (1842, 1856–60). Japan opened to the West under the Convention of Kanagawa (1854). The U.S. Civil War (1861–65) and the abolition of slavery reshaped North American society.'
        },
        {
            'label': 'Photography and Imperialism',
            'text': 'Photographers travelled with colonial armies and administrators through the Middle East, Asia, and South Asia, producing images that circulated in Europe as visual knowledge of empire. Photography entered Japan after 1853 and spread quickly among local practitioners.'
        },
        {
            'label': 'Technological Change',
            'text': 'From the daguerreotype (1839) to the calotype and wet collodion process (1851), exposure times dropped from minutes to seconds. Commercial portrait studios multiplied, and photography moved from scientific curiosity to everyday social practice.'
        },
        {
            'label': 'Directions of Expression',
            'text': "From the daguerreotype's unique, unreproducible image to Talbot's negative–positive process, two diverging logics of photography were established in the 1840s. The tension between the singular object and the reproducible print runs through the entire subsequent history."
        }
    ],
    '1870': [
        {
            'label': 'Politics & Society',
            'text': 'France lost the Franco-Prussian War (1870–71) and the German Empire was founded. The Paris Commune uprising and its violent suppression became an early photographic document of civil conflict. Industrialization accelerated in Europe and North America, expanding rail networks, factory labor, and print culture.'
        },
        {
            'label': 'Industrialization and Photography',
            'text': "Maddox's dry plate (1871) transformed photography into a more portable practice because photographers no longer had to coat plates immediately before exposure. The Eastman Kodak roll-film camera (1888) brought photography to amateurs and launched a mass market."
        },
        {
            'label': 'Technological Change',
            'text': 'Halftone printing (c. 1880s) allowed photographs to be printed directly in newspapers and magazines. This shift made photographic images part of everyday news consumption, laying the structural basis for photojournalism in the next century.'
        },
        {
            'label': 'Directions of Expression',
            'text': "Pictorialism emerged in the 1880s as photographers like P. H. Emerson argued for photography's artistic status. Soft focus, handcrafted printing, and careful composition countered the idea that photography was mere mechanical recording."
        }
    ],
    '1890': [
        {
            'label': 'Politics & Society',
            'text': 'The First Sino-Japanese War (1894–95), the Spanish-American War (1898), the Boer War (1899–1902), and the Russo-Japanese War (1904–05) brought the new century in under sustained imperial conflict. Japan emerged as a modern military power; the United States projected power into the Pacific and Caribbean.'
        },
        {
            'label': 'Photography and Art',
            'text': 'Pictorialism reached its international peak as photographers used handcrafted techniques — soft-focus lenses, platinum printing, gum bichromate — to claim recognition for photography alongside painting and printmaking. Alfred Stieglitz founded the Photo-Secession in 1902 and launched Camera Work to institutionalize this argument.'
        },
        {
            'label': 'Technological Change',
            'text': 'Roll film, hand cameras, and color processes (Lumière Autochrome, 1907) expanded what photography could do. Amateur clubs proliferated. The infrastructure of reproduction — halftone printing, illustrated magazines — made photographs central to public visual culture.'
        },
        {
            'label': 'Photography in Japan',
            'text': 'Photography spread through the Meiji period alongside newspapers, illustrated journals, and military documentation. Japanese photographers established studios, covered the Sino-Japanese and Russo-Japanese wars, and began building a distinct photographic culture that would shape later movements.'
        }
    ],
    '1910': [
        {
            'label': 'Politics & Society',
            'text': 'World War I (1914–18) brought an unprecedented scale of industrialized death through machine guns, poison gas, and aerial bombardment. The Russian Revolution (1917) transformed the political map of Europe. These upheavals shook the foundations of 19th-century culture and opened space for radical experiment in the arts.'
        },
        {
            'label': 'The Avant-Garde and Photography',
            'text': "In the United States, Paul Strand decisively broke with Pictorialism in 1916–17, helping define Straight Photography. In Europe, Dada (founded Zurich 1916), the Russian avant-garde, and the Bauhaus (founded 1919) made photography central to new visual languages — photomontage, photogram, experimental composition."
        },
        {
            'label': 'Technological Change',
            'text': "The Leica 35mm camera (1925) and improvements in film sensitivity made mobility the defining condition of 20th-century photography. Small cameras meant photographers could work in low light, crowds, and fast-moving situations — changing what it meant to photograph the street."
        },
        {
            'label': 'Modern Photography in Japan',
            'text': "Japan's Taisho Democracy (1912–26) and rapid urban growth created conditions for modern photography. Influenced by European constructivism and Bauhaus ideas, Japanese photographers explored abstraction, close-ups, and experimental forms — a local version of the New Vision movement."
        }
    ],
    '1930': [
        {
            'label': 'Politics & Society',
            'text': 'The Great Depression (1929), the rise of Hitler (1933), the Spanish Civil War (1936), World War II (1939–45), and the atomic bombings of Hiroshima and Nagasaki defined the decade as a crisis of democracy and human survival.'
        },
        {
            'label': 'FSA and Documentary',
            'text': "Within Roosevelt's Farm Security Administration photography project (1935–44), Roy Stryker directed Dorothea Lange, Walker Evans, and others to systematically record rural poverty, leaving behind roughly 170,000 images."
        },
        {
            'label': 'LIFE Magazine and Photojournalism',
            'text': 'LIFE magazine (launched 1936) sold millions of copies weekly and established photography as the primary medium of news and public memory. The picture essay — multi-image narrative journalism — defined how the world understood photojournalism.'
        },
        {
            'label': 'The Founding of Magnum',
            'text': 'In 1947, Robert Capa, Henri Cartier-Bresson, George Rodger, and others founded Magnum Photos — an independent cooperative that secured photographer copyright and autonomy, reshaping the economics and ethics of photojournalism.'
        }
    ],
    '1950': [
        {
            'label': 'Politics & Society',
            'text': 'As the Cold War began, the threat of nuclear annihilation hung over global politics. The Korean War (1950–53) and the Suez Crisis (1956) showed the new shape of imperial conflict. In the United States, McCarthyism suppressed political dissent while the civil rights movement gathered force.'
        },
        {
            'label': 'The Golden Age and End of LIFE Magazine',
            'text': 'In the 1950s, LIFE magazine, with a peak circulation of 8.5 million, stood at the summit of photojournalism. By the late 1960s, television would displace it; LIFE ceased weekly publication in 1972. The era also saw Robert Frank complete The Americans (1958), a decisive turn away from the heroic photojournalistic mode.'
        },
        {
            'label': 'The Internationalization of Japanese Photography',
            'text': "Postwar Japanese photography emerged from the ruins of wartime mobilization. Ken Domon's Realism, Shoji Ueda's staged surrealism, and the provocations of the VIVO group (founded 1959) created a distinctive postwar visual culture that gained international recognition through the 1960s."
        },
        {
            'label': 'Magnum Consolidated',
            'text': 'Magnum Photos consolidated its model of independent photojournalism, shaping how conflict, poverty, and social change were represented globally. The concept of the concerned photographer — committed yet independent — became the dominant ethical framework for documentary work.'
        }
    ],
    '1970': [
        {
            'label': 'Politics & Society',
            'text': 'The Vietnam War continued until the fall of Saigon in 1975, and televised images played a major role in shifting U.S. public opinion. Second-wave feminism, civil rights movements, and anti-colonial struggles demanded new forms of representation. The oil crisis of 1973 reshaped the global economy.'
        },
        {
            'label': 'Photography and the Art Market',
            'text': "In 1970s New York, a market emerged in which photography was exhibited and sold in museums and galleries at rising prices. The Museum of Modern Art's photography department, Aperture, and dealers like Witkin Gallery made photography collectible. This shift created the conditions for the Pictures Generation."
        },
        {
            'label': 'Pictures Generation',
            'text': "The 1977 exhibition 'Pictures' in New York gathered artists who quoted ready-made images — from advertising, film, and television — to question authorship, originality, and gender representation. Cindy Sherman, Richard Prince, and Sherrie Levine became the central figures of this turn."
        },
        {
            'label': 'Japan: The Deepening of I-Photography',
            'text': "The Provoke movement (1968–70) and its aftermath intensified Japanese photography's focus on the subjective body and private life. Nobuyoshi Araki, Masahisa Fukase, and others developed an I-Photography (shi-shashin) that turned family, lovers, loss, and memory into photographic form."
        }
    ],
    '1980': [
        {
            'label': 'Politics & Society',
            'text': 'The AIDS crisis, first reported in 1981, struck queer communities and artistic circles in New York and San Francisco with devastating force. Nan Goldin, David Wojnarowicz, and others made photography a form of witness and political response. The decade also saw the rise of neoconservatism, the Falklands War, and the beginning of the end of the Cold War.'
        },
        {
            'label': 'Dusseldorf School',
            'text': 'Artists such as Andreas Gursky, Thomas Struth, and Thomas Ruff — trained under Bernd and Hilla Becher at the Düsseldorf Kunstakademie — began exhibiting large-format color prints in the early 1980s. Their analytical, deadpan approach to landscapes, architecture, and crowds reshaped photography\'s ambitions in the gallery and auction market.'
        },
        {
            'label': 'AIDS Crisis and Photography',
            'text': 'Nan Goldin\'s "The Ballad of Sexual Dependency" (begun as a slideshow in the late 1970s, published 1986) and the collaborative projects of ACT UP and Gran Fury turned photography into an instrument of political visibility and mourning.'
        },
        {
            'label': 'Globalization and Photojournalism',
            'text': 'Cable news, fax machines, and early digital image transmission accelerated the circulation of photojournalism. The collapse of picture magazines was partially offset by new commissions from NGOs, news agencies, and the emerging documentary photography market.'
        }
    ],
    '1990': [
        {
            'label': 'Politics & Society',
            'text': 'The collapse of the Soviet Union in 1991 and the end of the Cold War reorganized the global order, while the Rwandan genocide (1994) and Balkan Wars exposed the limits of humanitarian intervention. The internet began to transform how information and images circulated.'
        },
        {
            'label': 'Digitalization',
            'text': "The 1990s were a decade in which digital photography became established. The spread of Adobe Photoshop (from 1990), early digital cameras, and CD-ROM image distribution challenged the evidentiary status of photographs. Debates about image manipulation and authenticity intensified."
        },
        {
            'label': 'Photobook Renaissance',
            'text': 'The 1990s saw a significant revival of the photobook as an art form, with small publishers, artists\' books, and self-published editions gaining critical attention. Bookshops like Printed Matter in New York and dedicated photobook fairs helped build an international community of collectors and practitioners.'
        },
        {
            'label': 'Japanese Photography in the 1990s',
            'text': "Japan's economic bubble burst in 1991, and the decade of stagnation that followed produced a distinctive photographic culture of interiority, obsession, and documentary intimacy. Photographers such as Rinko Kawauchi, Hiroh Kikai, and Daido Moriyama continued to develop Japanese photography's international presence."
        }
    ],
    '2000': [
        {
            'label': 'Politics & Society',
            'text': 'The September 11, 2001 attacks and the "war on terror" dominated global politics. Digital photography and camera phones began to transform who could make images and how quickly they circulated. The Iraq War (2003) saw embedded journalism coexist with uncontrolled mobile phone documentation.'
        },
        {
            'label': 'The Spread of Digital Photography',
            'text': "Digitalization transformed photojournalism at every level. Wire services and picture agencies switched to digital transmission; darkrooms closed. At the same time, digital tools enabled new forms of manipulation and raised fresh questions about documentary truth."
        },
        {
            'label': 'The Photobook at its Peak',
            'text': 'Dedicated photobook fairs (Paris Photo Livre, 2006; New York Art Book Fair, 2005) and growing collector interest made the photobook central to photography\'s art-world economy. Publishers like Steidl, Aperture, and Twin Palms produced significant runs alongside growing numbers of self-published artists\' books.'
        },
        {
            'label': 'Environmental Photography',
            'text': "Concerns about climate change and environmental degradation shaped major photographic projects of the decade. Edward Burtynsky's industrial landscapes and Edward Weston's legacy were revisited alongside new work on resource extraction, pollution, and ecological transformation."
        }
    ],
    '2010': [
        {
            'label': 'Politics & Society',
            'text': 'During the Arab Spring of 2010–11, photographs and videos shot on smartphones circulated through social media faster than traditional news organizations could verify or distribute them. This acceleration challenged the institutional framework of photojournalism while opening new questions about documentation, witness, and platform power.'
        },
        {
            'label': 'Smartphones and Social Media',
            'text': 'Instagram launched in 2010 and, together with smartphone cameras, transformed the meaning of the snapshot. The volume of images produced daily — now in the billions — changed the relationship between photography and scarcity, between the single image and the endless stream.'
        },
        {
            'label': 'Reappraisal of Photography History',
            'text': 'Museums, publishers, and scholars significantly expanded the canon of photography history in the 2010s, recovering overlooked figures — particularly women, non-Western, and queer photographers. Large retrospectives, new monographs, and digitized archives made the diversity of photographic practice more visible.'
        },
        {
            'label': 'Expansion of the Photobook Market',
            'text': 'The photobook market continued to grow, with dedicated fairs in Paris, New York, London, and Tokyo. Self-publishing and small-edition books proliferated alongside major museum publications. The photobook increasingly served as the primary site where photographic projects were publicly presented.'
        }
    ],
}

# ── English era period descriptions (for era-hero__period) ────────────────
ERA_PERIOD_EN = {
    '1839': 'Origins — Imperialism and the Birth of Photography',
    '1870': 'Industrialization, Social Reform, and Pictorialism',
    '1890': 'Pictorialism, Photo-Secession, and Straight Photography',
    '1910': 'Modernism, World War, and the Avant-Garde',
    '1930': 'The Great Depression, Fascism, and World War II',
    '1950': 'Cold War, LIFE Magazine, and Postwar Documentary',
    '1970': 'Conceptual Art, Feminism, and the Art Market',
    '1980': 'The Dusseldorf School, AIDS Crisis, and the Pictures Generation',
    '1990': 'Globalization, the Internet, and the Photobook Renaissance',
    '2000': 'Digital Photography, 9/11, and the Photobook at its Peak',
    '2010': 'Smartphones, Social Media, and the Reappraisal of Photo History',
}

# ── English abstract texts for movements (translations of ph-abstract) ──
# Sourced from Japanese page abstracts
MOVEMENT_ABSTRACTS_EN = {
    'fsa-photography':           "A government-sponsored project that systematically documented rural poverty and migrant labor during the Great Depression, creating one of the most extensive archives of social documentary photography.",
    'color-photography':         "The history of color photography is not simply a history of color reproduction; it tracks how the meaning of photographs changed each time a new color process — autochrome, Kodachrome, digital — redrew the line between commerce and art.",
    'conceptual-art':            "From the late 1960s into the 1970s, conceptual art used photography not to make beautiful images but to carry ideas, records, and institutional critique — placing concept and procedure above material object.",
    'cinematographic-photography': "Not simply stills that look like film, cinematographic photography concerns how much a single image can carry: the before and after of a scene, the artificiality of lighting, the gaps in a story.",
    'surrealism':                "Surrealist photography showed that a medium so bound to reality could itself produce the uncanny — that an utterly ordinary photograph can look strange once its context shifts.",
    'staged-photography':        "Staged photography constructs the situation before shooting: scene, lighting, placement of figures, at times digital compositing. It uses the fact that even a staged scene carries photographic conviction.",
    'contemporary-still-life':   "Photography that takes everyday objects and overlooked things as its subject, renewing still life as a critical genre of contemporary photography — the lineage Charlotte Cotton called 'Something and Nothing.'",
    'street-photography':        "A practice that takes the anonymous crossings, gestures, signs, and relations of public space as its subject — asking where to stand within the city's rhythm, when to release the shutter, and how to maintain an ethical distance from strangers.",
    'straight-photography':      "A practice that built a language specific to the photographic medium — lens sharpness, tonal range, composition — returning the photographer's decisions to the conditions of photography itself rather than imitating painting.",
    'typological-photography':   "A method that photographs like objects under identical conditions, repeatedly, setting them side by side so that difference and structure can be read through comparison — making visible how individuality appears.",
    'dada':                      "Dada treated the photograph not as evidence of reality or a beautiful print but as material to be cut, pasted, and made to work politically. Photomontage turned mass-reproduced media images into instruments of critique.",
    'dusseldorf-school':         "Photography made in the tradition of Bernd and Hilla Becher: postwar Germany's industrial landscapes, crowds, markets, and architecture analyzed through large prints and series — rethinking photography's institutions through typology, scale, and the art market.",
    'documentary':               "A broad term for photographs that record real events and lived worlds, but one whose meaning shifts by era. What persists is the tension between photographs treated as evidence and the editing, captions, and institutions that shape them.",
    'new-topographics':          "Photography that describes the man-altered landscape in a detached, matter-of-fact gaze stripped of emotion and heroism. Its subject is not sublime nature but the ordinary, changing land of suburbs, industrial zones, and urban peripheries.",
    'new-color':                 "In 1970s America, color was raised from the gloss of advertising and tourism into a serious art-photography language for reading suburbs, roadsides, household goods, and asphalt. Around Eggleston and Shore, color carried the temperature and vulgarity of everyday life.",
    'bauhaus':                   "The Bauhaus names less a single photographic school than a history in which photography's role was reorganized where teaching, printing, advertising, architecture, and design education crossed — from Moholy-Nagy's experimental vision to Lucia Moholy's documentation.",
    'pictures-generation':       "A group of artists discussed from the 1977 exhibition 'Pictures' onward, quoting ready-made images from advertising, film, and television to critique authorship, originality, gender representation, and consumer culture.",
    'pictorialism':              "An international movement of the late 19th and early 20th centuries that sought recognition for photography as an art equal to painting — claiming that a print is not a mere copy but a work bearing its maker's judgment.",
    'feminist-photography':      "Not a label for work by women photographers but a practice that critically asks how photography has represented women's bodies, domestic labor, desire, advertising, family, and work — recasting photography as a site where the power of the gaze operates.",
    'photojournalism':           "Photography that conveys current events, but whose substance was never the single decisive image alone — it is an institution of reporting that includes magazine editing, captions, layout, distribution, copyright, and the means of getting to the story.",
    'provoke':                   "The Japanese movement that unfolded around the photography-and-theory magazine founded in 1968, which cannot be grasped through the look of are-bure-boke alone — behind it lay distrust that language could grasp reality, and the instability of urban experience in high-growth Japan.",
    'modernism':                 "A broad current of the early 20th century that sought to turn photography into a visual language fit for modern life — abstraction, steep angles, close-ups, and repetition were its surface; a rethinking of what the medium could do was its core.",
    'realism-photography':       "In postwar Japan, 'realism' was epitomized by Ken Domon's call for the 'absolutely unstaged, absolute snapshot' — an ethic of facing social reality without staging or retouching. It was never a simple doctrine of non-intervention.",
    'rayograph-photogram':       "Cameraless photographs made by placing objects directly on photographic paper and exposing them to light. In the context of Dada and Surrealism, understood as turning the contact of things and light itself into an image.",
    'vorticism':                 "A London avant-garde of the 1910s that condensed the energy of machines, cities, and speed into abstract form — significant in photo history because Alvin Langdon Coburn's Vortographs are discussed as early abstract photographs.",
    'photo-secession':           "The group Alfred Stieglitz founded in New York in 1902 as an institutional campaign to have photography accepted as art — less a shared style than a reorganization of how photographs were shown through Camera Work, gallery 291, and exhibitions.",
    'large-format-color':        "Large-format color combines the precision of the view camera with the informational density of color, pushing photography to a scale that competes with painting and cinema in the exhibition space.",
    'new-vision':                "A photographic tendency of the 1920s–30s that sought to break habitual ways of seeing — bird's-eye views, extreme close-ups, photograms, and montage were devices for seeing the world otherwise and training perception fit for modernity.",
    'neue-sachlichkeit':         "The German movement of the 1920s that placed things and people under a cool, lucid gaze — its 'objectivity' constructed through frontality, even light, repetition, serialization, and placement in print.",
    'decisive-moment':           "The ideal of seizing the instant when form, movement, and meaning condense — spread by Cartier-Bresson's 1952 book, sustained by the small camera's mobility, bodily training on the street, and publishing culture.",
    'social-documentary':        "Documentary that makes poverty, labor, housing, migration, discrimination, and disaster visible, aiming at reform and the shaping of public opinion — not recording reality neutrally but choosing which reality is brought into public view.",
    'i-photography-shi-shashin': "A Japanese photographic mode that took shape from the 1970s, taking family, lovers, rooms, the body, memory, and death as its subjects — not as private records but as works that turn the distance between seeing and living itself into form.",
    'naturalistic-photography':  "P. H. Emerson's 19th-century argument that photography should reject contrived composites and allegorical staging, photographing nature and everyday life with focus and tonality close to actual visual experience.",
}

# ── English thesis texts for movements (translations of ph-thesis__body) ──
MOVEMENT_THESES_EN = {
    'fsa-photography':           "FSA Photography's significance lies not in documentary neutrality but in <em>systematic organization</em> — the state directing photographers, with their individual sensibilities intact, to produce an archive that simultaneously served New Deal propaganda and created a lasting record of poverty as social fact.",
    'color-photography':         "Color photography's repeated arrivals — autochrome, Kodachrome, dye transfer, digital — each time <em>unsettled the border between commerce and art</em>, between the snapshot and the work, between evidence and image.",
    'conceptual-art':            "Conceptual art's contribution to photography was to establish that <em>the idea that generated an image mattered as much as — sometimes more than — the image itself</em>, permanently expanding photography's range from beautiful picture to document, instruction, and institutional critique.",
    'cinematographic-photography': "Cinematographic photography asks whether the single photographic image can be <em>dense enough to imply time — the before and after — rather than merely freezing a moment</em>: it refuses the decisive instant in favor of the incomplete story.",
    'surrealism':                "Surrealism's core discovery for photography was that <em>the medium's very indexicality — its claim to record what is real — could be turned against itself</em>, making the familiar uncanny through displacement, chance, or a simple change of context.",
    'staged-photography':        "Staged photography's claim is that <em>the constructed scene and the documentary trace can coexist in a single image</em> — that the knowledge of staging does not dissolve photographic conviction but rather holds it in productive tension.",
    'contemporary-still-life':   "What contemporary still life inverted was <em>the hierarchy of what deserves to be photographed</em> — the most modest things, leftovers and household goods, became critical subjects for reading consumption, desire, and time.",
    'street-photography':        "Street photography's core is not the fact of photographing in public space but <em>taking on the city's anonymous crossings and chance encounters as a photographic form in themselves</em> — where to stand, when to shoot, and how to be ethically present are the real questions.",
    'straight-photography':      "Straight photography's methodological claim was that <em>the sharpness of the lens, the tonal range of the print, and the photographer's eye within the conditions of the medium</em> were sufficient — and that departing from these conditions was not refinement but evasion.",
    'typological-photography':   "The force of typology is not that it eliminates individuality but that <em>repetition under identical conditions makes individuality visible by comparison</em> — the series reveals what a single image cannot.",
    'dada':                      "Dada's contribution to photography was the discovery that <em>the photograph is not a window onto reality but a piece of printed paper that can be cut, combined, and reframed</em> — transforming mass-media images into instruments of political critique.",
    'dusseldorf-school':         "The Dusseldorf School showed that <em>large-scale, analytically cool, typologically organized photography could function as both art and social analysis</em> — placing photography in museum and auction contexts while maintaining a methodological rigor inherited from Conceptual Art.",
    'documentary':               "Documentary photography's enduring tension is between <em>photographs treated as evidence of the real and the editorial choices — selection, sequencing, captioning — that constitute the documentary form</em>: the document is never neutral.",
    'new-topographics':          "What New Topographics inverted was <em>landscape photography itself — from the celebration of sublime nature to the neutral description of land altered by people</em>: not beauty or narrative but the traces of development, habitation, and industry inscribed in the land became the subject.",
    'new-color':                 "New Color's claim was that <em>the color and vulgarity of everyday American life — the suburb, the roadside, the supermarket — were not beneath art photography but its proper subject</em>, and that color was the right tool for that reading.",
    'bauhaus':                   "The Bauhaus did not produce a unified photographic style but <em>a set of conditions — experimental vision, industrial printing, cross-disciplinary education — in which photography's social and aesthetic roles were renegotiated</em> across teaching, advertising, and architecture.",
    'pictures-generation':       "The Pictures Generation showed that <em>photography's relationship to originality, authorship, and authenticity was not natural but constructed</em> — that quoting, appropriating, and re-photographing existing images could itself constitute artistic practice.",
    'pictorialism':              "Pictorialism established that <em>the photographer's choices — in printing, tonality, framing, and edition — constitute a form of authorship</em>, forcing the question of where photographic art resides and creating the institutional frameworks that straight photography would subsequently contest.",
    'feminist-photography':      "Feminist photography's intervention was to show that <em>how photography represents women — bodies, labor, desire, family — is not a natural given but a political construction</em> that can be contested, reframed, and held up for critical examination.",
    'photojournalism':           "Photojournalism's substance was never the single decisive image but <em>the institution: the magazine, the editor, the caption, the layout, the distribution network</em> — which together decided which events became visible and how they were understood.",
    'provoke':                   "Provoke's core was not are-bure-boke as a style but <em>the conviction that the instability of the image was the only honest response to a reality that language could no longer grip</em> — a photographic materialism born from the disillusionment of postwar high growth.",
    'modernism':                 "Modernist photography's claim was that <em>the medium's formal properties — angle, abstraction, the close-up — were instruments for seeing the modern world differently</em>, not just for recording it; that the camera could train a new kind of perception.",
    'realism-photography':       "Realism in postwar Japanese photography was not a transparent window onto reality but <em>an ethical commitment — to face the social world frontally, without staging or sentimental retouching</em> — that carried the weight of wartime responsibility and postwar reconstruction.",
    'rayograph-photogram':       "The photogram shows that <em>photography is not only a matter of the camera but of light and contact</em> — that the trace of an object on sensitized paper is a photograph without the mediation of lens, viewfinder, or conventional composition.",
    'vorticism':                 "Vorticism matters in photo history because Coburn's Vortographs raise the question of whether <em>the photographic image can be purely abstract</em> — breaking from depiction entirely to make a visual structure that answers to the speed and energy of modernity.",
    'photo-secession':           "The Photo-Secession's significance was institutional: <em>it reorganized how photographs were shown, collected, and valued</em> — through Camera Work, gallery 291, and targeted exhibitions — creating the framework in which photography could claim art status.",
    'large-format-color':        "Large-format color photography claims that <em>the scale, detail density, and installation of the print are inseparable from its meaning</em> — that photography at this size competes with painting and cinema in the gallery rather than illustrating a subject.",
    'new-vision':                "The New Vision's claim was that <em>the camera could not simply record habitual ways of seeing but must break them</em> — that bird's-eye views, extreme close-ups, and photograms were not formal exercises but instruments for making the modern body and city visible.",
    'neue-sachlichkeit':         "Neue Sachlichkeit's 'objectivity' was not neutral transparency but a <em>constructed visual stance — frontal, evenly lit, repetitive</em> — that refused sentimentality and expressionist distortion to produce a cool analysis of the Weimar world.",
    'decisive-moment':           "The decisive moment names not merely a coincidence of form and content but <em>a photographic method — small camera, trained body, street knowledge</em> — that required years of practice and a particular relationship between photographer and urban environment.",
    'social-documentary':        "Social documentary's claim is that <em>bringing poverty, labor, and injustice into the public visual sphere is itself a political act</em> — that choosing which reality to photograph and how to circulate it is never neutral but always a position.",
    'i-photography-shi-shashin': "I-Photography's core was not the private subject matter — family, lovers, the body — but <em>the claim that the distance between seeing and living could itself become photographic form</em>, turning subjectivity into method rather than confession.",
    'naturalistic-photography':  "Naturalistic photography's argument was that <em>photography should draw its standards from visual experience rather than from painting</em> — that focus, tonality, and subject should correspond to how we actually see, not to allegorical convention.",
}

# ── Era overview/abstract texts (English translations of ph-abstract) ──────
ERA_ABSTRACTS_EN = {
    '1839': "The two decades following 1839 established photography's technical foundations and its social uses: portraiture, landscape, colonialism, scientific documentation. The tension between the unique daguerreotype and the reproducible calotype defined two diverging logics that run through the entire subsequent history.",
    '1870': "Dry-plate technology, Kodak roll film, and halftone printing transformed photography into a mass medium between the 1870s and 1890s. Industrialization, urbanization, and print culture made photographs part of everyday life, while Pictorialism arose to claim photography's place as art.",
    '1890': "Pictorialism reached its international peak and was challenged from within: the Photo-Secession institutionalized photography as fine art while Paul Strand and Alfred Stieglitz opened the path to Straight Photography. The era also saw photography enter Japanese modern culture.",
    '1910': "World War I, the Russian Revolution, and the Bauhaus transformed visual culture. The Leica small camera made mobility the defining condition of 20th-century photography. Dada, New Vision, and Straight Photography each claimed photography could do something new.",
    '1930': "From the Great Depression to the atomic bomb, photography was mobilized by states, magazines, and agencies. FSA, LIFE, and Magnum Photos built the institutions of photojournalism. Cartier-Bresson's Decisive Moment, Capa's combat photography, and Lange's Migrant Mother shaped how photography bore historical witness.",
    '1950': "Postwar reconstruction and Cold War anxiety shaped photography's institutions. LIFE magazine reached its peak circulation and began to decline. Robert Frank's The Americans (1958) opened a new photographic vernacular. Japanese photography developed its own postwar forms and gained international recognition.",
    '1970': "Photography entered the art market and museum as never before. Conceptual art made photography a tool of ideas rather than images. The Pictures Generation questioned the meaning of originality. Feminism challenged how photography represented women. Japanese I-Photography deepened its investigation of private life.",
    '1980': "The Dusseldorf School's large-format analytical photography reshaped gallery photography. The AIDS crisis made photography an instrument of witness and political mobilization. Nan Goldin, Cindy Sherman, and Richard Prince each reconfigured photography's relationship to the body, identity, and image.",
    '1990': "Digitalization challenged photography's evidentiary status. The photobook was revived as an art form. Japanese photography continued to produce distinctive work in the aftermath of economic collapse. Photography's global canon began to be expanded and revised.",
    '2000': "Digital photography and camera phones transformed who could make images and how quickly they circulated. The photobook market grew internationally. Environmental concerns shaped major photographic projects. Photojournalism confronted the dual challenge of digitalization and platform media.",
    '2010': "Smartphones and Instagram transformed the meaning of photography as a daily practice. Photography history was significantly expanded and revised to include overlooked figures. The photobook market continued to grow. Questions of artificial intelligence and image generation began to reshape debates about photography's future.",
}

# ── Era thesis texts (English translations of ph-thesis__body) ───────────
ERA_THESES_EN = {
    '1839': "Photography's invention in 1839 did not simply add a new image-making technology — it <em>established a new relationship between vision, evidence, and the world</em>: a mechanical trace that claimed to show reality as it was, and whose relationship to truth would be contested ever after.",
    '1870': "The period between 1870 and 1900 made photography <em>socially ubiquitous</em> — through dry plates, roll film, halftone printing, and the Kodak camera — while simultaneously producing the conditions for photography's first sustained claim to artistic status.",
    '1890': "The Photo-Secession and Straight Photography together show that <em>the question of what photography is — mechanical record or artistic expression — was not settled by the medium itself but by institutional decisions about exhibition, publication, and collection</em>.",
    '1910': "The 1910s and 1920s established that <em>photography's formal possibilities — angle, abstraction, close-up, sequence — were not limitations to overcome but tools for making modernity visible</em>, transforming the medium from record to visual argument.",
    '1930': "This era confirmed that <em>photography is not only a technology of images but a technology of power</em> — capable of mobilizing public opinion, documenting social crisis, serving state propaganda, and bearing witness to historical catastrophe, sometimes within the same project.",
    '1950': "The 1950s and 1960s showed that <em>the institutions of photojournalism — the picture magazine, the agency, the cooperative — shaped how the world was seen as much as the photographers within them</em>, and that challenges to those institutions created new photographic possibilities.",
    '1970': "The entry of photography into museums, galleries, and auction houses in the 1970s was not simply a change of venue but <em>a transformation of photography's self-understanding</em> — making questions of authorship, originality, and market value unavoidable.",
    '1980': "The 1980s demonstrated that photography could function simultaneously as <em>fine art, political witness, commercial image, and instrument of identity formation</em> — a range that required both the Dusseldorf School's cool analysis and Nan Goldin's intimate urgency.",
    '1990': "Digitalization in the 1990s did not immediately destroy the photograph but <em>made its evidential status uncertain</em> — initiating a long debate about authenticity, manipulation, and the grounds on which a photograph can be trusted.",
    '2000': "The 2000s demonstrated that <em>digital photography did not merely replace film but reorganized the entire ecosystem of image-making, distribution, and consumption</em> — from wire services to mobile phones, from darkrooms to Instagram, from LIFE magazine to the photobook fair.",
    '2010': "The 2010s did not simply add new technologies to photography but <em>fundamentally questioned who counts as a photographer, what counts as a photograph, and how photographs circulate and accumulate meaning</em> — transforming the medium's social meaning more rapidly than any decade since 1839.",
}


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def unesc(t):
    return (t.replace('&amp;', '&').replace('&#x27;', "'").replace('&quot;', '"')
             .replace('&lt;', '<').replace('&gt;', '>'))


def load_en_archive_cards(swap_nationality=False):
    """Build mapping from photographer-id → card HTML from en/archive.html.

    swap_nationality: if True, replace <span>PHOTOGRAPHER</span> with the
    nationality code from card-data.json.  Pass True only for era pages;
    movement pages keep the PHOTOGRAPHER placeholder so they stay in sync
    with the Japanese movement pages.
    """
    fp = os.path.join(ROOT, 'en/archive.html')
    html = open(fp, encoding='utf-8').read()
    cards = re.findall(
        r'(<article class="pc-card pc-card--photographer"[^>]*>.*?</article>)',
        html, re.S)
    if swap_nationality:
        # Load card-data.json for nationality lookup
        card_data_fp = os.path.join(ROOT, 'card-data.json')
        with open(card_data_fp, encoding='utf-8') as _f:
            _card_data = json.load(_f)
        _nationality_map = {p['id']: p.get('nationality', '') for p in _card_data.get('photographers', [])}
    id_to_card = {}
    for card in cards:
        m = re.search(r'href="(/en/photographers/([^"]+))"', card)
        if m:
            ph_id = m.group(2).replace('.html', '')
            # Fix href for relative path from en/movements/ or en/eras/
            fixed = card.replace('href="/en/photographers/', 'href="../photographers/')
            fixed = fixed.replace('target="_blank"', '')  # open in same window
            # Replace PHOTOGRAPHER placeholder with nationality code if requested
            if swap_nationality:
                nationality = _nationality_map.get(ph_id, '')
                if nationality and '<span>PHOTOGRAPHER</span>' in fixed:
                    fixed = fixed.replace('<span>PHOTOGRAPHER</span>', f'<span>{nationality}</span>', 1)
            id_to_card[ph_id] = fixed
    return id_to_card


def get_photographers_in_movement(ja_html):
    """Extract photographer IDs from the er-cards section of a Japanese movement page"""
    m = re.search(r'<div class="er-cards">(.*?)</div>\s*</div>\s*</section>', ja_html, re.S)
    if not m:
        return []
    cards_html = m.group(1)
    hrefs = re.findall(r'href="\.\./photographers/([^"]+)\.html"', cards_html)
    return hrefs


def get_photographers_in_era(ja_html):
    """Extract photographer IDs from the er-cards section of a Japanese era page"""
    m = re.search(r'<div class="er-cards">(.*?)', ja_html, re.S)
    hrefs = re.findall(r'href="\.\./photographers/([^"]+)\.html"', ja_html)
    return hrefs


def translate_internal_links_movement(html, slug):
    """Replace ../photographers/ → ../photographers/ (same), ./JA.html → EN slug"""
    # Movement internal links: ./日本語名.html → slug.html
    def repl_movement(m):
        ja_fn = m.group(1)
        en_slug = STUB_TO_SLUG.get(ja_fn, '')
        if en_slug:
            return f'href="./{en_slug}.html"'
        return m.group(0)
    html = re.sub(r'href="\./([^"]+)\.html"', repl_movement, html)
    return html


def translate_internal_links_era(html, era_id):
    """Replace ../movements/JA.html → ../movements/slug.html, era hrefs stay same"""
    def repl_mvt(m):
        ja_fn = m.group(1)
        en_slug = STUB_TO_SLUG.get(ja_fn, '')
        if en_slug:
            return f'href="../movements/{en_slug}.html"'
        return m.group(0)
    html = re.sub(r'href="\.\./movements/([^"]+)\.html"', repl_mvt, html)
    return html


def build_ga_script():
    return '''<script async src="https://www.googletagmanager.com/gtag/js?id=G-2VRTV8BZEJ"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-2VRTV8BZEJ');
</script>'''


def build_head_meta_movement(slug, en_name, en_desc, old_meta):
    """Build the complete <head> section for a movement EN page"""
    en_url = f'https://eyescosmos.github.io/en/movements/{slug}.html'
    ja_stub = SLUG_TO_STUB.get(slug, slug)
    ja_url = f'https://eyescosmos.github.io/movements/{ja_stub}.html'

    title = old_meta.get('title') or f'{en_name} | Photography Movement | Photo Coordinates'
    desc = old_meta.get('description') or en_desc or f'This page examines {en_name} through its origins, key photographers, visual methods, and meaning in photography history.'
    og_title = old_meta.get('og_title') or title
    og_desc = old_meta.get('og_description') or desc
    tw_title = old_meta.get('twitter_title') or title
    tw_desc = old_meta.get('twitter_description') or desc

    json_ld = old_meta.get('json_ld') or f'''{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "WebPage",
      "@id": "{en_url}",
      "url": "{en_url}",
      "name": "{esc(title)}",
      "headline": "{esc(title)}",
      "description": "{esc(desc)}",
      "inLanguage": "en",
      "isPartOf": {{
        "@type": "WebSite",
        "name": "Photo Coordinates",
        "url": "https://eyescosmos.github.io/en/"
      }}
    }},
    {{
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type": "ListItem", "position": 1, "name": "Photo Coordinates", "item": "https://eyescosmos.github.io/en/"}},
        {{"@type": "ListItem", "position": 2, "name": "{esc(en_name)}", "item": "{en_url}"}}
      ]
    }}
  ]
}}'''

    return f'''<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{en_url}">
<link rel="alternate" hreflang="ja" href="{ja_url}">
<link rel="alternate" hreflang="en" href="{en_url}">
<link rel="alternate" hreflang="x-default" href="{ja_url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Photo Coordinates">
<meta property="og:title" content="{esc(og_title)}">
<meta property="og:description" content="{esc(og_desc)}">
<meta property="og:url" content="{en_url}">
<meta property="og:image" content="https://eyescosmos.github.io/assets/ogp-default.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Photo Coordinates">
<meta name="twitter:image" content="https://eyescosmos.github.io/assets/ogp-default.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(tw_title)}">
<meta name="twitter:description" content="{esc(tw_desc)}">
<script type="application/ld+json">
{json_ld}
</script>
{build_ga_script()}'''


def build_head_meta_era(era_id, old_meta):
    """Build the complete <head> section for an era EN page"""
    period = ERA_META[era_id]['period']
    title_en = ERA_META[era_id]['title_en']
    en_url = f'https://eyescosmos.github.io/en/eras/{era_id}.html'
    ja_url = f'https://eyescosmos.github.io/eras/{era_id}.html'

    title = old_meta.get('title') or f'{period} Photo History | {title_en} | Photo Coordinates'
    desc = old_meta.get('description') or f'Photography history of {period} — {title_en} — through photographers, movements, social context, and changes in visual expression.'
    og_title = old_meta.get('og_title') or title
    og_desc = old_meta.get('og_description') or desc
    tw_title = old_meta.get('twitter_title') or title
    tw_desc = old_meta.get('twitter_description') or desc

    json_ld = old_meta.get('json_ld') or f'''{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "WebPage",
      "@id": "{en_url}",
      "url": "{en_url}",
      "name": "{esc(title)}",
      "headline": "{esc(title)}",
      "description": "{esc(desc)}",
      "inLanguage": "en",
      "isPartOf": {{
        "@type": "WebSite",
        "name": "Photo Coordinates",
        "url": "https://eyescosmos.github.io/en/"
      }}
    }},
    {{
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type": "ListItem", "position": 1, "name": "Photo Coordinates", "item": "https://eyescosmos.github.io/en/"}},
        {{"@type": "ListItem", "position": 2, "name": "{esc(period)} Photo History", "item": "{en_url}"}}
      ]
    }}
  ]
}}'''

    return f'''<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{en_url}">
<link rel="alternate" hreflang="ja" href="{ja_url}">
<link rel="alternate" hreflang="en" href="{en_url}">
<link rel="alternate" hreflang="x-default" href="{ja_url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Photo Coordinates">
<meta property="og:title" content="{esc(og_title)}">
<meta property="og:description" content="{esc(og_desc)}">
<meta property="og:url" content="{en_url}">
<meta property="og:image" content="https://eyescosmos.github.io/assets/ogp-default.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Photo Coordinates">
<meta name="twitter:image" content="https://eyescosmos.github.io/assets/ogp-default.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(tw_title)}">
<meta name="twitter:description" content="{esc(tw_desc)}">
<script type="application/ld+json">
{json_ld}
</script>
{build_ga_script()}'''


def translate_html_ui(html, page_type='movement'):
    """Translate Japanese UI chrome strings to English"""
    replacements = [
        # lang attr
        ('<html lang="ja">', '<html lang="en">'),
        # header brand
        ('<span class="head__brand-photo">写真</span>の座標', '<span class="head__brand-photo">Photo</span> Coordinates'),
        # linked language toggle
        ('.head__lang button {', '.head__lang button, .head__lang a {'),
        ('.head__lang button.is-active {', '.head__lang button.is-active, .head__lang a.is-active {'),
        # crumbs based on type
        ('<em>MOVEMENTS</em>', '<em>MOVEMENTS</em>'),
        ('<em>ERAS</em>', '<em>ERAS</em>'),
        # mobile search
        ('SEARCH · 写真家を探す</label>', 'SEARCH · Find a photographer</label>'),
        ('placeholder="SEARCH · 写真家を探す"', 'placeholder="Search photographers"'),
        ('placeholder="写真家名・運動・キーワード"', 'placeholder="Photographer, movement, keyword"'),
        ('aria-label="検索"', 'aria-label="Search"'),
        # mvt-hero labels
        ('MOVEMENT · 表現', 'MOVEMENT · Expression'),
        ('§ — Movement — 表現で読む', '§ — Movement'),
        ('§ — Era Index — 時代で読む', '§ — Era Index'),
        # ph-abstract labels
        ('Overview · この表現について', 'Overview'),
        ('Overview · この時代について', 'Overview'),
        # ph-thesis labels
        ('>核心命題<', '>Core Thesis<'),
        ('>この時代が変えたこと<', '>What This Era Changed<'),
        # section names
        ('>表現解説<', '>Expression and Methods<'),
        ('>批評と受容<', '>Criticism and Reception<'),
        ('>関連する表現<', '>Related Movements<'),
        ('>写真家一覧<', '>Photographers<'),
        ('>出典<', '>Sources<'),
        ('>この時代の背景<', '>Context of This Era<'),
        ('>この時代の写真家<', '>Photographers of This Era<'),
        # era-context-grid labels (handled separately)
        # sidebar blocks
        ('>Entry · データ<', '>Entry · Data<'),
        ('>Entry · 時代データ<', '>Entry · Era Data<'),
        ('>Related · 関連する表現<', '>Related Movements<'),
        ('>Photographers · 写真家<', '>Photographers<'),
        ('>Navigate · 移動<', '>Navigate<'),
        ('>Movements · 運動・ジャンル<', '>Movements<'),
        ('>Keywords · キーワード<', '>Keywords<'),
        # sidebar meta keys
        ('<span class="ph-side-meta-key">Movement</span>', '<span class="ph-side-meta-key">Movement</span>'),
        ('<span class="ph-side-meta-key">English</span>', '<span class="ph-side-meta-key">English Name</span>'),
        ('<span class="ph-side-meta-key">Category</span>', '<span class="ph-side-meta-key">Category</span>'),
        ('<span class="ph-side-meta-key">Updated</span>', '<span class="ph-side-meta-key">Updated</span>'),
        ('<span class="ph-side-meta-key">Photogs</span>', '<span class="ph-side-meta-key">Photographers</span>'),
        ('<span class="ph-side-meta-key">Period</span>', '<span class="ph-side-meta-key">Period</span>'),
        ('<span class="ph-side-meta-key">Movements</span>', '<span class="ph-side-meta-key">Movements</span>'),
        ('<span class="ph-side-meta-key">Vol</span>', '<span class="ph-side-meta-key">Volume</span>'),
        # sidebar search label
        ('SEARCH · 写真家を探す</label>', 'SEARCH · Find a photographer</label>'),
        ('<label class="ph-side-search__label" for="ph-search-input">SEARCH · 写真家を探す</label>',
         '<label class="ph-side-search__label" for="ph-search-input">SEARCH · Find a photographer</label>'),
        # navigate sidebar
        ('>表現一覧<', '>All Movements<'),
        ('>All Movements<', '>All Movements<'),
        ('>トップへ<', '>Top<'),
        ('>トップページへ<', '>Top<'),
        ('>次の時代 →<', '>Next Era →<'),
        ('← 前の時代', '← Previous Era'),
        ('>← 年代一覧<', '>← All Eras<'),
        # navigation labels
        ('>§ — 表現で読む<', '>§ — Movements<'),
        ('>§ — 時代で読む<', '>§ — Eras<'),
        # mvt-hero eyebrow
        ('>§ — Movement — 表現で読む<', '>§ — Movement<'),
        # era-hero eyebrow
        ('>§ — Era Index — 時代で読む<', '>§ — Era Index<'),
        # card CTA
        ('>写真史上の位置を読む<', '>Read their place in photo history<'),
        # footer
        ('美術館・アーカイブ・専門資料に基づく', 'Based on museum, archive, and specialist sources'),
        ('>プライバシー<', '>Privacy<'),
        ('>コロフォン<', '>Colophon<'),
        # breadcrumbs - movement type
        ('Photo Coordinates / Movement', 'Photo Coordinates / Movement'),
        # archive link
        ('href="../archive.html"', 'href="../archive.html"'),
        # search JS no-result message
        ('該当する写真家が見つかりません', 'No photographers found'),
        # period/era "present"
        ('–現在', '–present'),
        # era category values
        ('>Era · 1839–1860s<', '>Era · 1839–1860s<'),
        ('>大恐慌<', '>1930s<'),
        # era sidebar nav labels
        ('>座標で見る<', '>View Map<'),
        # era subtitle/breadcrumb labels
        ('黎明期 · EARLY PHOTOGRAPHY', 'Early Photography · EARLY PHOTOGRAPHY'),
        # era hero art label
        ('ERA · 01 · 黎明期', 'ERA · 01 · Early Photography'),
        # sidebar chip aliases (display text != STUB_TO_SLUG key)
        ('>コンセプチュアル・アート<', '>Conceptual Art<'),
        ('>演出写真<', '>Staged Photography<'),
        ('>写真集<', '>Photobook<'),
    ]

    for ja, en in replacements:
        html = html.replace(ja, en)

    # Translate Japanese movement names in keyword chips and ph-side-chips
    for ja_name, en_slug in STUB_TO_SLUG.items():
        en_name = SLUG_TO_EN_NAME[en_slug]
        # In chip text (but not in href)
        html = re.sub(
            r'(<span class="ph-side-chip[^"]*">)' + re.escape(ja_name) + r'(</span>)',
            rf'\g<1>{en_name}\g<2>',
            html
        )
        html = re.sub(
            r'(<span class="ph-side-chip[^"]*">)' + re.escape(ja_name) + r'(</span>)',
            rf'\g<1>{en_name}\g<2>',
            html
        )

    return html


def translate_mvt_nav(html, current_slug):
    """Replace Japanese movement nav with English nav"""
    # Build English nav
    nav_items = []
    for ja_name in STUB_TO_SLUG.keys():
        en_slug = STUB_TO_SLUG[ja_name]
        en_name = SLUG_TO_EN_NAME[en_slug]
        is_active = ' is-active' if en_slug == current_slug else ''
        nav_items.append(f'<a class="mvt-nav__item{is_active}" href="./{en_slug}.html">{esc(en_name)}</a>')

    new_nav = (f'<nav class="mvt-nav"><div class="mvt-nav__label">§ — Movements</div>'
               f'<div class="mvt-nav__strip">{"".join(nav_items)}</div></nav>')

    # Replace existing mvt-nav
    html = re.sub(r'<nav class="mvt-nav">.*?</nav>', new_nav, html, flags=re.S)
    return html


def translate_era_nav(html, current_era):
    """Replace Japanese era nav with English nav"""
    nav_items = []
    for era_id in ERA_ORDER:
        label = ERA_META[era_id]['nav_label']
        is_active = ' is-active' if era_id == current_era else ''
        nav_items.append(f'<a class="era-nav__item{is_active}" href="{era_id}.html">{label}</a>')

    new_nav = (f'<nav class="era-nav" aria-label="Era navigation">'
               f'<div class="era-nav__label">§ — Eras</div>'
               f'<div class="era-nav__strip">{"".join(nav_items)}</div></nav>')

    html = re.sub(r'<nav class="era-nav"[^>]*>.*?</nav>', new_nav, html, flags=re.S)
    return html


def translate_context_blocks(html, era_id):
    """Replace Japanese era-context-block labels with English"""
    en_blocks = ERA_CONTEXT_BLOCKS_EN.get(era_id, [])
    if not en_blocks:
        return html

    # Find era-context-grid and replace all blocks
    def build_block(b):
        return (f'<div class="era-context-block">'
                f'<div class="era-context-label">{esc(b["label"])}</div>'
                f'<p class="era-context-text">{esc(b["text"])}</p>'
                f'</div>')

    new_grid = ('<div class="era-context-grid">' +
                ''.join(build_block(b) for b in en_blocks) +
                '</div>')

    html = re.sub(
        r'<div class="era-context-grid">.*?</div>\s*</div>\s*</section>',
        new_grid + '</div></section>',
        html, flags=re.S, count=1
    )
    return html


def translate_sidebar_chips_movement(html, slug):
    """Translate Japanese movement chips in sidebar to English slugs"""
    def repl_chip_link(m):
        ja_fn = m.group(1)
        en_slug = STUB_TO_SLUG.get(ja_fn, '')
        if en_slug:
            return f'href="./{en_slug}.html"'
        return m.group(0)

    # Replace movement chip links
    html = re.sub(r'href="\./([^"]+)\.html"', repl_chip_link, html)
    # Translate Japanese movement names in ph-side-chip text
    for ja_name, en_slug in STUB_TO_SLUG.items():
        en_name = SLUG_TO_EN_NAME[en_slug]
        # Replace text in chip links and non-linked chips
        html = html.replace(f'>{ja_name}<', f'>{en_name}<')

    return html


def translate_sidebar_chips_era(html, era_id):
    """Translate Japanese links in era sidebar chips"""
    # Movements links
    def repl_mvt(m):
        ja_fn = m.group(1)
        en_slug = STUB_TO_SLUG.get(ja_fn, '')
        if en_slug:
            return f'href="../movements/{en_slug}.html"'
        return m.group(0)
    html = re.sub(r'href="\.\./movements/([^"]+)\.html"', repl_mvt, html)

    # Translate Japanese movement names to English
    for ja_name, en_slug in STUB_TO_SLUG.items():
        en_name = SLUG_TO_EN_NAME[en_slug]
        html = html.replace(f'>{ja_name}<', f'>{en_name}<')

    # Additional movement name aliases (display names differ from STUB_TO_SLUG keys)
    ERA_MVT_ALIASES = {
        'コンセプチュアル・アート': 'Conceptual Art',  # chip text vs STUB key コンセプチュアルアート
        '演出写真': 'Staged Photography',               # display alias for ステージド写真
        '写真集': 'Photobook',                          # plain chip without slug link
        '黎明期': 'Early Photography',                  # era hero/sidebar label 1839
    }
    for ja_alias, en_alias in ERA_MVT_ALIASES.items():
        html = html.replace(f'>{ja_alias}<', f'>{en_alias}<')

    # Translate Japanese country/category meta in sidebar
    # Era-data sidebar: Era · 大恐慌 → Era · 1930s
    era_categories_ja = {
        '1839': 'Era · 1839–1860s',
        '1870': 'Era · 1870–1890s',
        '1890': 'Era · 1890–1910s',
        '1910': 'Era · 1910–1920s',
        '1930': 'Era · 1930–1940s',
        '1950': 'Era · 1950–1960s',
        '1970': 'Era · 1970–1980s',
        '1980': 'Era · 1980–1990s',
        '1990': 'Era · 1990–2000s',
        '2000': 'Era · 2000–2010s',
        '2010': 'Era · 2010–2020s',
    }
    # Replace "Era · 日本語" pattern
    html = re.sub(r'Era · [^\s<]+', era_categories_ja.get(era_id, f'Era · {era_id}'), html)

    # Translate keyword chips
    ERA_KEYWORD_TRANSLATIONS = {
        '乾板写真': 'Dry Plate Photography',
        'コダック': 'Kodak Camera',
        '社会改革': 'Social Reform',
        '連続写真': 'Chronophotography',
        '都市記録': 'Urban Documentation',
        'ギャラリー291': 'Gallery 291',
        'オートクローム': 'Autochrome',
        'プラチナプリント': 'Platinum Print',
        '社会改革写真': 'Reform Photography',
        'ストレート写真': 'Straight Photography',
        'レイオグラフ': 'Rayograph',
        '新しいヴィジョン': 'New Vision',
        '構成主義': 'Constructivism',
        'フォトグラム': 'Photogram',
        'LIFE誌': 'LIFE Magazine',
        'マグナム': 'Magnum Photos',
        '決定的瞬間': 'Decisive Moment',
        '戦争写真': 'War Photography',
        'ゾーンシステム': 'Zone System',
        'プロヴォーク': 'Provoke',
        'アレ・ブレ・ボケ': 'Are-Bure-Boke',
        '公民権運動': 'Civil Rights Movement',
        'ピクチャーズ世代': 'Pictures Generation',
        'カラー写真': 'Color Photography',
        'フェミニズム': 'Feminism',
        'ニュー・トポグラフィクス': 'New Topographics',
        'ラージフォーマット': 'Large Format',
        'エイズ危機': 'AIDS Crisis',
        'ベルリンの壁': 'Berlin Wall',
        'タイポロジー': 'Typology',
        '美術市場': 'Art Market',
        'デジタル化': 'Digitalization',
        '写真集ルネサンス': 'Photobook Renaissance',
        'グローバル化': 'Globalization',
        'フォトショップ': 'Photoshop',
        '身体と記憶': 'Body and Memory',
        '同時多発テロ': '9/11',
        '写真集市場': 'Photobook Market',
        'デジタル一眼': 'Digital SLR',
        '環境写真': 'Environmental Photography',
        'ロードトリップ': 'Road Trip',
        'Instagram': 'Instagram',
        'スマートフォン': 'Smartphones',
        'デコロニアル': 'Decolonial',
        '写真史再評価': 'History Reappraisal',
        '幕末・明治': 'Bakumatsu/Meiji',
        'ダゲレオタイプ': 'Daguerreotype',
        'カロタイプ': 'Calotype',
        '肖像写真': 'Portrait Photography',
        '風景写真': 'Landscape Photography',
        '記録写真': 'Documentary Photography',
        '報道写真': 'News Photography',
        '広告写真': 'Commercial Photography',
        'ファッション写真': 'Fashion Photography',
        '植民地写真': 'Colonial Photography',
        '航空写真': 'Aerial Photography',
    }
    for ja_kw, en_kw in ERA_KEYWORD_TRANSLATIONS.items():
        html = html.replace(f'>{ja_kw}<', f'>{en_kw}<')

    return html


def translate_footer(html, page_type, label=''):
    """Translate footer content"""
    if page_type == 'movement':
        html = re.sub(
            r'<footer class="foot"><div>© Photo Coordinates · Movement</div>',
            '<footer class="foot"><div>© Photo Coordinates · Movement</div>',
            html
        )
    elif page_type == 'era':
        html = re.sub(
            r'<footer class="foot"><div>[^<]*</div>',
            f'<footer class="foot"><div>© Photo Coordinates · {label}</div>',
            html
        )
    html = html.replace(
        '美術館・アーカイブ・専門資料に基づく',
        'Based on museum, archive, and specialist sources'
    )
    html = html.replace('>プライバシー<', '>Privacy<')
    html = html.replace('>コロフォン<', '>Colophon<')
    return html


# ── 個別ページ未作成の写真家カード（en/archive.html に無い）の英訳 ──────────
# リード文は日本語カードの lede の英訳。新規の評価・調査は加えない。
FALLBACK_LEDE_EN = {
    'jp-yokoyama-matsusaburo': "A pioneering photographer who helped spread photographic technology in the Bakumatsu and Meiji periods. Born on Etorofu Island, he carried Western photographic techniques across Japan.",
    'jp-tomishige-rihei': "A key figure in Meiji-era photographic history in Kyushu. Based in Kumamoto, he established modern photographic technique there and, through his students, left deep roots in regional photographic history.",
    'jp-tomishige-tokuji': "A photographer who carried on Kumamoto's photographic history as a student of Tomishige Rihei. A bearer of regional photographic culture, recorded in databases of Bakumatsu and Meiji photographers.",
    'jp-torii-ryuzo': "An anthropologist who systematically used photography in fieldwork across Hokkaido, Taiwan, Korea, and Manchuria. A key figure for thinking about the relation between photography and imperial knowledge.",
    'jp-kamei-koreaki': "A court noble and count who organized the photographic documentation of the First Sino-Japanese War. Remembered in photographic history as an institutional starting point of Japanese war and press photography.",
    'jp-fukuhara-shinzo': "Shiseido's first president, who combined corporate management with photographic art. A cultural organizer who led Japanese Pictorialism and worked to build institutions establishing photography's artistic standing.",
    'jp-yasui-nakaji': "Born in Osaka. In the transition from Pictorialism to modernism he left one of the most important trajectories in Japanese photographic history, dying young at 39.",
    'jp-ueda-shoji': "Staging family and friends on the Tottori sand dunes, he established his distinctive 'Ueda-cho' style. A pioneer of Japanese staged photography whose surreal, poetic compositions were highly regarded abroad.",
    'rineke-dijkstra': "Photographed teenagers on beaches, mothers after childbirth, and soldiers head-on in large-format color, fixing body, identity, and rites of passage in still photographs.",
    'boris-mikhailov': "Recorded the collapse of Soviet society, the homeless of Kharkiv, and the socially excluded in raw color and black and white. Case History (1997) is his major work.",
    'thomas-struth': "His Museum Photographs, large-format color images of visitors inside museums, reexamined the three-way relation among photography, painting, and the viewer. A broad practice extending to cities, nature, and family portraits.",
    'alec-soth': "Joined Magnum with Sleeping by the Mississippi (2004), a large-format color record of people, solitude, and dreams along the Mississippi River. Established the road-trip mode in photobook culture.",
    'edward-burtynsky': "Photographed manufacturing, oil, mining, and shipbreaking in aerial and large-format color, as in Manufactured Landscapes (2003), presenting the vast aesthetics and the ethics of environmental destruction at once.",
    'gregory-crewdson': "Large-format photographs staging the unease beneath everyday American suburbia with Hollywood-scale lighting, crews, and budgets. The extreme of staged photography, questioning the border between photography and cinema at its most lavish.",
    'atarashi-dodo': "A documentary photographer whose photobooks — Shanghai Style, Taigan, and White Map on the Silk Road — build travel into a form of contemporary documentary, measuring the distance between a moving body and the texture of local life. Taigan received the Kimura Ihei Photography Award.",
    'zanele-muholi': "A photographic activist who has kept questioning human-rights abuses and visibility with Faces and Phases, portraits of South Africa's LGBTQI+ communities. A self-described 'visual activist'.",
    'masashi-asada': "Won the Kimura Ihei Award for Asadake (2008), restaging family photographs through performance and costume. Also noted for volunteering to restore photo albums in areas struck by the Great East Japan Earthquake.",
    'rieko-shiga': "Moved to the Miyagi coast and produced photography, theater, and installations in collaboration with the local community. Rasen Kaigan (2013), made after the Great East Japan Earthquake, earned international recognition.",
    'alec-soth-songbook': "Continued to explore American solitude and connection in book form with Songbook (2015) and I Know How Furiously Your Heart Is Beating (2019). Also practiced photographic publishing by founding Little Brown Mushroom.",
    'japan-photography-2010s': "After the Great East Japan Earthquake, Japanese photography fundamentally re-asked what a record is. Rieko Shiga, Masashi Asada, Atarashi Dodo, and others deepened practices facing region, family, and history, with continued international recognition.",
    'jp-福原信三': "As Shiseido's first president he shaped its corporate culture while ordering the institutions of Japanese photographic art through the founding of Shashin Geijutsu-sha and the Shiseido Gallery. A photographer and cultural figure who supported modern Japanese photography from both institutions and expression.",
    'jp-木村伊兵衛': "Born in Tokyo's shitamachi. The photographer who popularized the Leica in Japan, he kept recording the people of Akita and rural villages and everyday street scenes in light, agile snapshots.",
}

# 現在の日本語ページが使うID（日本語ファイル名・改名後ID）にも同じ英訳を割り当てる
for _old, _new in [
    ('jp-yokoyama-matsusaburo', 'jp-横山松三郎'),
    ('jp-tomishige-rihei', 'jp-冨重利平'),
    ('jp-tomishige-tokuji', 'jp-冨重徳次'),
    ('jp-torii-ryuzo', 'jp-鳥居龍蔵'),
    ('jp-kamei-koreaki', 'jp-亀井茲明'),
    ('jp-fukuhara-shinzo', 'jp-福原信三'),
    ('jp-yasui-nakaji', 'jp-安井仲治'),
    ('jp-ueda-shoji', 'jp-植田正治'),
    ('atarashi-dodo', 'arata-dodo'),
    ('rieko-shiga', 'lieko-shiga'),
]:
    FALLBACK_LEDE_EN.setdefault(_new, FALLBACK_LEDE_EN[_old])

FALLBACK_TERM_EN = {
    # channel / tag terms on fallback cards
    '明治写真': 'Meiji photography', 'ドキュメンタリー': 'Documentary',
    '民族誌写真': 'Ethnographic photography', '記録写真': 'Record photography',
    'ピクトリアリズム': 'Pictorialism', '日本近代写真': 'Modern Japanese photography',
    'モダニズム': 'Modernism', '演出写真': 'Staged photography',
    'コンセプチュアル': 'Conceptual', 'タイポロジー': 'Typology',
    '社会ドキュメンタリー': 'Social documentary', 'デュッセルドルフ派': 'Düsseldorf School',
    '写真集': 'The photobook', '環境写真': 'Environmental photography',
    '私写真': 'I-photography', '地域協働': 'Community collaboration',
    '制度を作る写真': 'Building the institution',
    '幕末': 'Bakumatsu', '地方写真': 'Regional photography',
    '戦争写真': 'War photography', '組織写真': 'Institutional photography',
    '日本写真': 'Japanese photography', 'ポートレート': 'Portrait',
    'ポストソ連': 'Post-Soviet', 'ラージフォーマット': 'Large format',
    'ノワール': 'Noir', 'アジア写真': 'Asian photography',
    'クィア写真': 'Queer photography', '家族写真': 'Family photography',
    '地域写真': 'Regional photography', '震災後写真': 'Post-disaster photography',
    'リアリズム写真': 'Realism photography', '日本': 'Japan',
}

FALLBACK_COUNTRY_EN = {
    '日本': 'JP', 'オランダ': 'NL', 'ウクライナ': 'UA', 'ドイツ': 'DE',
    'アメリカ': 'US', 'カナダ': 'CA', '南アフリカ': 'ZA',
}

# 日本語ファイル名 href の付け替えは行わない（jp-福原信三 等は EN ページが実在する）
FALLBACK_ID_ALIAS = {}


def translate_ja_card_fallback(card, ph_id):
    """en/archive.html にカードが無い写真家：日本語カードをテーブル翻訳して残す。
    リンク先は日本語ページと同名の en/photographers/ パス（現状は日英とも
    個別ページ未作成。作成され次第リンクが生きる）。"""
    name_m = re.search(r'(<(?:h3|div) class="pc-body__name">)([^<]*)(</(?:h3|div)>)', card)
    nameen_m = re.search(r'(<div class="pc-body__name-en">)([^<]*)(</div>)', card)
    if name_m and nameen_m:
        ja_name, en_name = name_m.group(2), nameen_m.group(2)
        card = card.replace(name_m.group(0), name_m.group(1) + en_name + name_m.group(3))
        card = card.replace(nameen_m.group(0), nameen_m.group(1) + ja_name + nameen_m.group(3))

    def tr_terms(text):
        for ja, en in sorted(FALLBACK_TERM_EN.items(), key=lambda kv: -len(kv[0])):
            text = text.replace(ja, en)
        return text

    meta_m = re.search(r'(<div class="pc-body__meta">)([^<]*)(</div>)', card)
    if meta_m:
        meta = meta_m.group(2)
        for ja, code in FALLBACK_COUNTRY_EN.items():
            meta = meta.replace(ja + ' ·', code + ' ·')
        meta = meta.replace('明治期', 'Meiji era').replace('2010年代', '2010s')
        card = card.replace(meta_m.group(0), meta_m.group(1) + meta + meta_m.group(3))

    ch_m = re.search(r'(<div class="pc-body__channel">)([^<]*)(</div>)', card)
    if ch_m:
        card = card.replace(ch_m.group(0), ch_m.group(1) + tr_terms(ch_m.group(2)) + ch_m.group(3))

    for tag_m in re.finditer(r'<span class="pc-body__tag">([^<]*)</span>', card):
        card = card.replace(tag_m.group(0),
                            f'<span class="pc-body__tag">{tr_terms(tag_m.group(1))}</span>')

    lede_m = re.search(r'(<p class="pc-body__lede">)(.*?)(</p>)', card, re.S)
    if lede_m and ph_id in FALLBACK_LEDE_EN:
        card = card.replace(lede_m.group(0),
                            lede_m.group(1) + esc(FALLBACK_LEDE_EN[ph_id]) + lede_m.group(3))

    hint_m = re.search(r'(<div class="pc-top__hint">)([^<]*)(</div>)', card)
    if hint_m:
        hint = tr_terms(hint_m.group(2)).replace('明治期', 'MEIJI ERA')
        card = card.replace(hint_m.group(0), hint_m.group(1) + hint + hint_m.group(3))

    kind_m = re.search(r'(<span class="pc-body__kind">)([^<]*)(</span>)', card)
    if kind_m and re.search(r'[ぁ-んァ-ヶ一-龯]', kind_m.group(2)):
        card = card.replace(kind_m.group(0), kind_m.group(1) + tr_terms(kind_m.group(2)) + kind_m.group(3))
    card = card.replace('<span>写真史上の位置を読む</span>', '<span>Read their place in photo history</span>')
    card = card.replace('<span>詳細を読む</span>', '<span>Read more</span>')
    # リンク先: EN ページがあれば相対のまま、JA ページのみなら JA ページへ、
    # どちらも無ければそのまま（日本語側と同じ将来リンク）
    if not os.path.exists(os.path.join(ROOT, 'en', 'photographers', f'{ph_id}.html')) \
            and os.path.exists(os.path.join(ROOT, 'photographers', f'{ph_id}.html')):
        card = re.sub(r'href="\.\./photographers/[^"]+"',
                      f'href="/photographers/{ph_id}.html"', card)
    return card


def replace_cards_with_en(html, ph_ids, id_to_card, page_type='movement'):
    """Replace pc-card photographer articles with EN versions.
    en/archive.html に無いカードは落とさず、テーブル翻訳して残す。"""
    missing = []

    # Find the er-cards div and replace all article elements
    # Pattern handles optional HTML comment after closing </div> (e.g., <!-- /.er-cards -->)
    m = re.search(r'(<div class="er-cards">)(.*?)(</div>(?:<!-- [^>]* -->)?)\s*</div>\s*</section>', html, re.S)
    if not m:
        return html, missing

    articles = re.findall(r'<article class="pc-card.*?</article>', m.group(2), re.S)
    new_cards_html = ''
    for article in articles:
        idm = re.search(r'href="\.\./photographers/([^"]+)\.html"', article)
        ph_id = idm.group(1) if idm else ''
        alt_id = ph_id.replace('jp-', '') if ph_id.startswith('jp-') else f'jp-{ph_id}'
        if ph_id in id_to_card:
            new_cards_html += '\n' + id_to_card[ph_id]
        elif alt_id in id_to_card:
            new_cards_html += '\n' + id_to_card[alt_id]
        else:
            missing.append(ph_id)
            new_cards_html += '\n' + translate_ja_card_fallback(article, ph_id)

    new_html = (html[:m.start()] +
                m.group(1) + new_cards_html + '\n' +
                m.group(3) + '</div></section>' +
                html[m.end():])
    return new_html, missing


def translate_search_js(html):
    """Update search JS to work with English pages"""
    # The inline search JS fetches /card-data.json and builds suggestions
    # For EN pages, we need to update the suggestion URLs to point to /en/photographers/
    # The global-search.js already handles this via lang detection
    # For inline JS in movement/era pages, update the URL construction
    html = html.replace(
        "url:p.href?(p.href[0]==='/'?p.href:'/'+p.href):''",
        "url:p.href?(p.href[0]==='/'?p.href.replace('/photographers/','/en/photographers/'):'/en/'+p.href):''"
    )
    # Also replace the no-result message
    html = html.replace(
        '該当する写真家が見つかりません',
        'No photographers found'
    )
    return html


# 英語は両端揃え（justify）だと単語間が開いて読みにくいため左揃えにする。
# 日本語テンプレート由来の justify 指定を EN ページでのみ上書きする。
EN_READABILITY_STYLE = '''<style>
/* EN readability: left-align English running text (JA template justifies) */
.mvt-hero__lead, .era-hero__lead,
.ph-abstract p, .ph-thesis__body,
.ph-section__body p, .era-context-text,
.pc-body__lede {
  text-align: left;
}
</style>'''


def unlink_orphan_cite_refs(html):
    """出典セクションに対応する cite-N が無い sup-ref リンクをプレーン表示に
    落とす（マーカーは出典の痕跡として残す）。モダニズム等、日本語側で
    出典セクションが未整備のページへの対症療法。"""
    ids = set(re.findall(r'id="cite-(\d+)"', html))

    def repl(m):
        return m.group(0) if m.group(1) in ids else \
            f'<sup class="sup-ref">*{m.group(1)}</sup>'

    return re.sub(r'<sup class="sup-ref"><a href="#cite-(\d+)">\*\d+</a></sup>',
                  repl, html)


def apply_id_aliases(html):
    """EN ページ内の photographer リンクを実在チェックで補正する。
    EN ページが無く JA ページのみ存在する場合は JA ページへ向ける。"""
    for ja_id, ascii_id in FALLBACK_ID_ALIAS.items():
        html = html.replace(f'photographers/{ja_id}.html',
                            f'photographers/{ascii_id}.html')

    def repl(m):
        ph_id = m.group(1)
        if not os.path.exists(os.path.join(ROOT, 'en', 'photographers', f'{ph_id}.html')) \
                and os.path.exists(os.path.join(ROOT, 'photographers', f'{ph_id}.html')):
            return f'href="/photographers/{ph_id}.html"'
        return m.group(0)

    return re.sub(r'href="\.\./photographers/([^"]+)\.html"', repl, html)


def add_nosnippet_chrome(html):
    """UIクローム（ヘッダー・ナビ・サイドバー・フッター・カードの pc-top と
    pc-body__cta）に data-nosnippet を付与する。冪等。"""
    for tag in ('<header class="head">', '<nav class="mvt-nav">',
                '<nav class="era-nav">', '<aside class="era-side">',
                '<footer class="foot">'):
        html = html.replace(tag, tag[:-1] + ' data-nosnippet>')
    html = re.sub(r'<div class="(pc-top pc-top--[a-z-]+)">',
                  r'<div data-nosnippet class="\1">', html)
    html = html.replace('<div class="pc-body__cta">',
                        '<div class="pc-body__cta" data-nosnippet>')
    return html


def replace_head_section(html, new_head_content):
    """Replace SEO/meta inside <head>...</head> while preserving the JA
    template's asset tags (font preconnect, Google Fonts, stylesheet links,
    inline <style>, non-GA scripts). GA is supplied by new_head_content."""
    m_open = re.search(r'<head>', html)
    m_close = re.search(r'</head>', html)
    if not (m_open and m_close):
        return html
    old_head = html[m_open.end():m_close.start()]

    assets = []
    # link tags for fonts / stylesheets (preconnect, fonts css2, local css)
    for tag in re.findall(r'<link[^>]+>', old_head):
        if ('rel="preconnect"' in tag or 'stylesheet' in tag):
            assets.append(tag)
    # inline style blocks
    assets.extend(re.findall(r'<style.*?</style>', old_head, flags=re.S))
    # head scripts other than GA (e.g. JSON-LD is rebuilt, so skip it too)
    for s in re.findall(r'<script(?![^>]*application/ld\+json).*?</script>',
                        old_head, flags=re.S):
        if 'googletagmanager' in s or 'gtag(' in s:
            continue
        assets.append(s)

    # en/ 配下は1階層深いので共通CSSの相対パスを補正する
    assets = [a.replace('href="../styles/', 'href="../../styles/') for a in assets]

    return (html[:m_open.end()] + '\n' + new_head_content + '\n' +
            '\n'.join(assets) + '\n' + EN_READABILITY_STYLE + '\n' +
            html[m_close.start():])


def add_lang_toggle_href(html, slug_or_era, page_type='movement'):
    """Update the lang toggle buttons to link to correct pages"""
    if page_type == 'movement':
        ja_stub = SLUG_TO_STUB.get(slug_or_era, slug_or_era)
        ja_url = f'https://eyescosmos.github.io/movements/{ja_stub}.html'
        en_url = f'https://eyescosmos.github.io/en/movements/{slug_or_era}.html'
    else:
        ja_url = f'https://eyescosmos.github.io/eras/{slug_or_era}.html'
        en_url = f'https://eyescosmos.github.io/en/eras/{slug_or_era}.html'

    toggle = (
        f'<div class="head__lang"><a href="{ja_url}" class="lang-btn">JP</a>'
        f'<a href="{en_url}" class="lang-btn is-active">EN</a></div>'
    )
    html, count = re.subn(
        r'<div class="head__lang">.*?</div>',
        toggle,
        html,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise RuntimeError(f"head__lang not found while building EN {page_type}: {slug_or_era}")
    return html


def process_movement_page(ja_name, slug, en_data, id_to_card):
    """Generate an English movement page from the Japanese v5.1 template"""
    ja_fp = os.path.join(ROOT, f'movements/{ja_name}.html')
    en_fp = os.path.join(ROOT, f'en/movements/{slug}.html')

    if not os.path.exists(ja_fp):
        print(f"  SKIP: missing JA source {ja_fp}")
        return [], []

    html = open(ja_fp, encoding='utf-8').read()
    en_name = SLUG_TO_EN_NAME[slug]
    old_meta = en_data['movements'].get(slug, {}).get('meta', {})
    old_sections = en_data['movements'].get(slug, {}).get('sections', {})

    # 1. Get photographer IDs for card replacement
    ph_ids = get_photographers_in_movement(html)

    # 2. Replace head
    en_lead = old_sections.get('lead', '') or MOVEMENT_ABSTRACTS_EN.get(slug, '')
    html = replace_head_section(html, build_head_meta_movement(slug, en_name, en_lead, old_meta))

    # 3. Global UI chrome translation
    html = translate_html_ui(html, 'movement')

    # 4. Translate mvt-nav
    html = translate_mvt_nav(html, slug)

    # 5. Translate lang toggle
    html = add_lang_toggle_href(html, slug, 'movement')

    # 6. Translate header crumbs - movement name
    html = re.sub(
        r'(<span class="sep">/</span>)[^<]+(<span class="sep">·</span>)',
        rf'\g<1>{esc(en_name)}\g<2>',
        html, count=1
    )
    # Replace subtitle after separator
    html = re.sub(
        r'(<span class="sep">·</span>)[^<]+(<span class="sep">·</span>)',
        rf'\g<1>{esc(en_name)}\g<2>',
        html, count=1
    )

    # 7. Translate mvt-hero content
    # eyebrow already done in UI chrome
    # title: keep Japanese name in h1, add subtitle in English
    # For EN page: h1 becomes English name
    html = re.sub(
        r'<h1 class="mvt-hero__title">[^<]+</h1>',
        f'<h1 class="mvt-hero__title">{esc(en_name)}</h1>',
        html
    )
    # Subtitle: remove Japanese subtitle (it was the EN subtitle already in JA page)
    html = re.sub(
        r'<div class="mvt-hero__subtitle">[^<]+</div>',
        f'<div class="mvt-hero__subtitle">{esc(ja_name)}</div>',
        html
    )
    # Lead: replace with English lead
    en_hero_lead = old_sections.get('lead', '') or MOVEMENT_ABSTRACTS_EN.get(slug, '')
    if en_hero_lead:
        # Strip sup-refs from old EN lead
        en_hero_lead_clean = re.sub(r'\*\d+', '', en_hero_lead).strip()
        html = re.sub(
            r'<p class="mvt-hero__lead">.*?</p>',
            f'<p class="mvt-hero__lead">{esc(en_hero_lead_clean)}</p>',
            html, flags=re.S, count=1
        )
    # Translate meta-row items (Category value)
    html = re.sub(r'<strong>表現</strong>', '<strong>Expression</strong>', html)
    html = re.sub(r'<strong>現在</strong>', '<strong>present</strong>', html)
    html = re.sub(r'<strong>(\d+)s–現在</strong>', r'<strong>\g<1>s–present</strong>', html)

    # 8. Translate ph-abstract (handles both compact and multiline formats)
    abstract_en = MOVEMENT_ABSTRACTS_EN.get(slug, '')
    if abstract_en:
        html = re.sub(
            r'(<div class="ph-abstract">\s*<div class="ph-abstract__label">Overview</div>\s*<p>)(.*?)(</p>\s*</div>)',
            rf'\g<1>{esc(abstract_en)}\g<3>',
            html, flags=re.S, count=1
        )

    # 9. Translate ph-thesis
    thesis_en = MOVEMENT_THESES_EN.get(slug, '')
    if thesis_en:
        html = re.sub(
            r'(<p class="ph-thesis__body">)(.*?)(</p>)',
            rf'\g<1>{thesis_en}\g<3>',
            html, flags=re.S, count=1
        )

    # 10. Translate section body content
    # Get English section content from old EN pages
    exp_methods = old_sections.get('Expression and Methods', [])
    crit_recep = old_sections.get('Criticism and Reception', [])
    related = old_sections.get('Related Movements', [])

    # If no Expression/Criticism sections, fall back to various old section names
    if not exp_methods:
        for k in old_sections:
            if k.startswith('What Is') or k.startswith('How It'):
                exp_methods = old_sections[k]
                break
    if not crit_recep:
        # Try multiple fallback keys
        for fallback_key in ['Where It Sits in the History of Photography',
                             'Why It Mattered in the History of Photography',
                             'Key Photographers',
                             'Photographers in View']:
            fb = old_sections.get(fallback_key, [])
            if fb:
                crit_recep = fb
                break
    # If still empty, collect all remaining section content
    if not crit_recep:
        collected = []
        skip_keys = {'lead', 'context_blocks', 'Related Movements', 'Sources', 'Photographers',
                     'Expression and Methods', 'Criticism and Reception'}
        for k, v in old_sections.items():
            if k not in skip_keys and isinstance(v, list) and v:
                collected.extend(v)
        if collected:
            crit_recep = collected

    def replace_section_body(html, section_name_en, new_paras):
        """Replace ALL paragraph content in a named section body.
        段落は個別の <p> として並べ、*N 出典マーカーは JA と同じ
        sup-ref リンクに変換する。"""
        if not new_paras:
            return html
        paras = [p for p in new_paras if p and p.strip()]
        if not paras:
            return html
        paras_html = ''.join(f'<p>{esc(p)}</p>' for p in paras)
        paras_html = re.sub(
            r'\*(\d{1,2})\b',
            r'<sup class="sup-ref"><a href="#cite-\1">*\1</a></sup>',
            paras_html)
        # Pattern: match section with given name, capture body div, replace all content up to </div></section>
        pattern = (r'(<section class="ph-section">(?:(?!</section>).)*?'
                   r'<span class="ph-section__name">' + re.escape(section_name_en) + r'</span>'
                   r'(?:(?!</section>).)*?'
                   r'<div class="ph-section__body">)'
                   r'((?:(?!</section>).)*?)'
                   r'(</div></section>)')
        replacement = r'\g<1>' + paras_html.replace('\\', '\\\\') + r'\g<3>'
        return re.sub(pattern, replacement, html, flags=re.S, count=1)

    html = replace_section_body(html, 'Expression and Methods', exp_methods)
    html = replace_section_body(html, 'Criticism and Reception', crit_recep)
    html = replace_section_body(html, 'Related Movements', related)

    # 11. Replace photographer cards with EN versions
    html, missing_cards = replace_cards_with_en(html, ph_ids, id_to_card, 'movement')

    # 12. Translate internal links (movement cross-links)
    html = translate_internal_links_movement(html, slug)

    # 13. Translate sidebar chips
    html = translate_sidebar_chips_movement(html, slug)

    # 14. Translate sidebar meta values
    # Movement name value
    html = html.replace(
        f'<span class="ph-side-meta-val">{ja_name}</span>',
        f'<span class="ph-side-meta-val">{esc(en_name)}</span>'
    )
    # Category value: 表現 → Expression
    html = re.sub(r'<span class="ph-side-meta-val">表現</span>', '<span class="ph-side-meta-val">Expression</span>', html)

    # 15. Update sidebar navigate block links
    html = html.replace('href="../archive.html"', 'href="../archive.html"')
    html = html.replace('href="../index.html"', 'href="../index.html"')
    # Fix archive link to point to en/archive.html
    html = re.sub(r'href="\.\./archive\.html"', 'href="../archive.html"', html)
    html = re.sub(r'href="\.\./index\.html"', 'href="../index.html"', html)

    # 15b. サイドナビの日英ペアが翻訳で重複表記になるのを解消
    html = html.replace('<span>All Movements</span><span>All Movements</span>',
                        '<span>All Movements</span><span>Movement Index</span>')
    html = html.replace('<span>Top</span><span>Top</span>',
                        '<span>Top</span><span>Photo Coordinates</span>')

    # 16. Footer
    html = translate_footer(html, 'movement')

    # 17. Update search JS for EN photographer URLs
    html = translate_search_js(html)

    # 17b. UIクロームに data-nosnippet を付与・日本語ファイル名リンクの統一
    html = add_nosnippet_chrome(html)
    html = apply_id_aliases(html)
    html = unlink_orphan_cite_refs(html)

    # 18. Write output
    os.makedirs(os.path.dirname(en_fp), exist_ok=True)
    with open(en_fp, 'w', encoding='utf-8') as f:
        f.write(html)

    return ph_ids, missing_cards


def process_era_page(era_id, en_data, id_to_card):
    """Generate an English era page from the Japanese v5.1 template"""
    ja_fp = os.path.join(ROOT, f'eras/{era_id}.html')
    en_fp = os.path.join(ROOT, f'en/eras/{era_id}.html')

    if not os.path.exists(ja_fp):
        print(f"  SKIP: missing JA source {ja_fp}")
        return []

    html = open(ja_fp, encoding='utf-8').read()
    period = ERA_META[era_id]['period']
    old_meta = en_data['eras'].get(era_id, {}).get('meta', {})
    old_sections = en_data['eras'].get(era_id, {}).get('sections', {})

    # 1. Get photographer IDs
    ph_ids = get_photographers_in_era(html)

    # 2. Replace head
    html = replace_head_section(html, build_head_meta_era(era_id, old_meta))

    # 3. Global UI chrome translation
    html = translate_html_ui(html, 'era')

    # 4. Translate era-nav
    html = translate_era_nav(html, era_id)

    # 5. Translate lang toggle
    html = add_lang_toggle_href(html, era_id, 'era')

    # 6. Translate header crumbs
    html = re.sub(
        r'(<span class="sep">/</span>)\d+–\d+s(<span class="sep">·</span>)',
        rf'\g<1>{period}\g<2>',
        html, count=1
    )
    # Era subtitle in crumbs (Japanese era subtitle)
    # Replace Japanese subtitle after the period
    html = re.sub(
        r'(<span class="sep">·</span>)[^·<]+(<span class="sep">·</span>UPDATED)',
        rf'\g<1>{ERA_PERIOD_EN.get(era_id, period)}\g<2>',
        html, count=1
    )

    # 7. Translate era-hero content
    html = re.sub(
        r'<h1 class="era-hero__title">[^<]+</h1>',
        f'<h1 class="era-hero__title">{period}</h1>',
        html
    )
    html = re.sub(
        r'<div class="era-hero__period">[^<]+</div>',
        f'<div class="era-hero__period">{ERA_PERIOD_EN.get(era_id, period)}</div>',
        html
    )
    # Era hero lead
    en_lead = old_sections.get('lead', '')
    if en_lead:
        html = re.sub(
            r'<p class="era-hero__lead">.*?</p>',
            f'<p class="era-hero__lead">{esc(en_lead)}</p>',
            html, flags=re.S, count=1
        )

    # 8. Translate era-hero art label
    # ERA · 05 · 大恐慌 → ERA · 05 · period
    era_idx = ERA_ORDER.index(era_id) + 1
    html = re.sub(
        r'<div class="era-hero__art-label">ERA · \d+ · [^<]+</div>',
        f'<div class="era-hero__art-label">ERA · {era_idx:02d} · {ERA_META[era_id]["title_en"]}</div>',
        html
    )

    # 9. Translate ph-abstract (handles both compact and multiline formats)
    abstract_en = ERA_ABSTRACTS_EN.get(era_id, '')
    if abstract_en:
        html = re.sub(
            r'(<div class="ph-abstract">\s*<div class="ph-abstract__label">Overview</div>\s*<p>)(.*?)(</p>\s*</div>)',
            rf'\g<1>{esc(abstract_en)}\g<3>',
            html, flags=re.S, count=1
        )

    # 10. Translate ph-thesis (handles both compact and multiline formats)
    thesis_en = ERA_THESES_EN.get(era_id, '')
    if thesis_en:
        html = re.sub(
            r'(<p class="ph-thesis__body">)(.*?)(</p>)',
            rf'\g<1>{thesis_en}\g<3>',
            html, flags=re.S, count=1
        )

    # 11. Translate era-context-grid blocks
    html = translate_context_blocks(html, era_id)

    # 12. Replace photographer cards with EN versions
    html, missing_cards = replace_cards_with_en(html, ph_ids, id_to_card, 'era')

    # 13. Translate internal links
    html = translate_internal_links_era(html, era_id)

    # 14. Translate sidebar chips
    html = translate_sidebar_chips_era(html, era_id)

    # 15. Era sidebar: translate era-side nav (next/prev era)
    idx = ERA_ORDER.index(era_id)
    if idx + 1 < len(ERA_ORDER):
        next_era = ERA_ORDER[idx + 1]
        next_period = ERA_META[next_era]['period']
    else:
        next_era = None
        next_period = None

    if idx - 1 >= 0:
        prev_era = ERA_ORDER[idx - 1]
        prev_period = ERA_META[prev_era]['period']
    else:
        prev_era = None
        prev_period = None

    # Rebuild navigate block
    nav_links = []
    if next_era:
        nav_links.append(f'<a href="{next_era}.html"><span>Next Era →</span><span>{next_period}</span></a>')
    if prev_era:
        nav_links.append(f'<a href="{prev_era}.html"><span>← Previous Era</span><span>{prev_period}</span></a>')
    nav_links.append('<a href="../archive.html"><span>← All Eras</span><span>Era Index</span></a>')
    nav_links.append('<a href="../index.html"><span>Top</span><span>Photo Coordinates</span></a>')

    new_nav_block = (f'<div class="ph-side-block"><div class="ph-side-block__head">Navigate</div>'
                     f'<nav class="ph-side-nav">{"".join(nav_links)}</nav></div>')

    html = re.sub(
        r'<div class="ph-side-block"><div class="ph-side-block__head">Navigate.*?</div></div>',
        new_nav_block,
        html, flags=re.S, count=1
    )

    # 16. Footer
    html = translate_footer(html, 'era', f'VOL. {era_idx:02d}')

    # 17. Update search JS
    html = translate_search_js(html)

    # 17b. UIクロームに data-nosnippet を付与・日本語ファイル名リンクの統一
    html = add_nosnippet_chrome(html)
    html = apply_id_aliases(html)
    html = unlink_orphan_cite_refs(html)

    # 18. Write output
    os.makedirs(os.path.dirname(en_fp), exist_ok=True)
    with open(en_fp, 'w', encoding='utf-8') as f:
        f.write(html)

    return missing_cards


def build_movements(only_slugs=None):
    en_data = json.load(open(os.path.join(ROOT, 'data/taxonomy-en-content.json'), encoding='utf-8'))
    id_to_card = load_en_archive_cards()

    all_missing = []
    generated = 0

    for ja_name, slug in STUB_TO_SLUG.items():
        if only_slugs is not None and slug not in only_slugs:
            continue
        print(f"  movement: {slug}")
        ph_ids, missing = process_movement_page(ja_name, slug, en_data, id_to_card)
        if missing:
            all_missing.extend([(slug, pid) for pid in missing])
            print(f"    MISSING CARDS: {missing}")
        generated += 1

    return generated, all_missing


def build_eras(only_eras=None):
    en_data = json.load(open(os.path.join(ROOT, 'data/taxonomy-en-content.json'), encoding='utf-8'))
    id_to_card = load_en_archive_cards(swap_nationality=True)

    all_missing = []
    generated = 0

    for era_id in ERA_ORDER:
        if only_eras is not None and era_id not in only_eras:
            continue
        print(f"  era: {era_id}")
        missing = process_era_page(era_id, en_data, id_to_card)
        if missing:
            all_missing.extend([(era_id, pid) for pid in missing])
            print(f"    MISSING CARDS: {missing}")
        generated += 1

    return generated, all_missing


USAGE_EXAMPLES = """\
Scope is required (this prevents an accidental full rebuild from clobbering
unrelated EN taxonomy pages). Choose one:

  --all                       full rebuild: all 31 movements + 11 eras
  --era 2010                  rebuild only en/eras/2010.html (repeatable)
  --slug new-topographics     rebuild only that en/movements/<slug>.html (repeatable)

Examples:
  python3 scripts/build_taxonomy_en.py --era 2010
  python3 scripts/build_taxonomy_en.py --slug street-photography
  python3 scripts/build_taxonomy_en.py --all
"""


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Rebuild EN taxonomy pages (en/movements + en/eras). "
                    "A scope flag is mandatory to avoid accidental full rebuilds.",
        epilog=USAGE_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--all', action='store_true',
                        help='full rebuild: all 31 movements + 11 eras (byte-identical to legacy run)')
    parser.add_argument('--era', action='append', metavar='YYYY', default=[],
                        help='rebuild one era page by id, e.g. --era 2010 (repeatable)')
    parser.add_argument('--slug', action='append', metavar='MOVEMENT', default=[],
                        help='rebuild one movement page by EN slug, e.g. --slug new-color (repeatable)')
    args = parser.parse_args(argv)

    # ── Guard: no scope → refuse, write nothing, non-zero exit ──────────────
    if not (args.all or args.era or args.slug):
        sys.stderr.write(
            "ERROR: refusing to run without a scope flag — no files written.\n\n"
            + USAGE_EXAMPLES)
        return 2

    if args.all and (args.era or args.slug):
        sys.stderr.write("ERROR: --all cannot be combined with --era/--slug.\n")
        return 2

    # ── Validate targets against the known tables (typo must not silently
    #    fall through to a full rebuild) ──────────────────────────────────
    if not args.all:
        bad_eras = [e for e in args.era if e not in ERA_ORDER]
        if bad_eras:
            sys.stderr.write(
                f"ERROR: unknown era id(s): {', '.join(bad_eras)}\n"
                f"Valid eras: {', '.join(ERA_ORDER)}\n")
            return 2
        bad_slugs = [s for s in args.slug if s not in SLUG_TO_STUB]
        if bad_slugs:
            sys.stderr.write(
                f"ERROR: unknown movement slug(s): {', '.join(bad_slugs)}\n"
                f"Valid slugs: {', '.join(sorted(SLUG_TO_STUB))}\n")
            return 2

    only_slugs = None if args.all else (set(args.slug) if args.slug else set())
    only_eras = None if args.all else (set(args.era) if args.era else set())

    print("Building EN taxonomy pages...")
    mvt_count = mvt_missing = era_count = era_missing = None

    # In --all mode both run fully. In targeted mode only the requested kind runs.
    if args.all or only_slugs:
        print("\n[movements]")
        mvt_count, mvt_missing = build_movements(only_slugs=only_slugs)
    if args.all or only_eras:
        print("\n[eras]")
        era_count, era_missing = build_eras(only_eras=only_eras)

    print(f"\n=== Done ===")
    if mvt_count is not None:
        print(f"Movements generated: {mvt_count}")
    if era_count is not None:
        print(f"Eras generated: {era_count}")

    if mvt_missing:
        print(f"\nMissing photographer cards in movements ({len(mvt_missing)}):")
        for slug, pid in mvt_missing:
            print(f"  {slug}: {pid}")

    if era_missing:
        print(f"\nMissing photographer cards in eras ({len(era_missing)}):")
        for era_id, pid in era_missing:
            print(f"  {era_id}: {pid}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
