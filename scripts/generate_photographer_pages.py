#!/usr/bin/env python3
from __future__ import annotations

import html
import argparse
import json
import re
import subprocess
import csv
from pathlib import Path
from urllib.parse import urlparse

import generate_taxonomy_pages as taxonomy_meta


REPO = Path(__file__).resolve().parent.parent
SITE = "https://eyescosmos.github.io"
GA_ID = "G-2VRTV8BZEJ"
ASSET_VERSION = "20260517d"
GLOBAL_SEARCH_VERSION = "20260508a"
OGP_IMAGE_URL = f"{SITE}/assets/ogp-default.png"
ALNUM_BOUNDARY_RE = re.compile(r"[A-Za-z0-9]")
NON_PHOTOGRAPHER_IDS = {
    "charles-wirgman",
    "fabian-marti",
    "gabriel-orozco",
}
COUNTRY_META = {
    "FR": {"slug": "france", "ja": "フランス", "en": "France"},
    "GB": {"slug": "united-kingdom", "ja": "イギリス", "en": "United Kingdom"},
    "US": {"slug": "united-states", "ja": "アメリカ", "en": "United States"},
    "IT / GB": {"slug": "italy-united-kingdom", "ja": "イタリア / イギリス", "en": "Italy / United Kingdom"},
    "GB / US": {"slug": "united-kingdom-united-states", "ja": "イギリス / アメリカ", "en": "United Kingdom / United States"},
    "DK / US": {"slug": "denmark-united-states", "ja": "デンマーク / アメリカ", "en": "Denmark / United States"},
    "DE": {"slug": "germany", "ja": "ドイツ", "en": "Germany"},
    "JP": {"slug": "japan", "ja": "日本", "en": "Japan"},
    "BR": {"slug": "brazil", "ja": "ブラジル", "en": "Brazil"},
    "CA": {"slug": "canada", "ja": "カナダ", "en": "Canada"},
}
COUNTRY_ADJECTIVES_EN = {
    "France": "French",
    "United Kingdom": "British",
    "United States": "American",
    "Italy": "Italian",
    "Germany": "German",
    "Japan": "Japanese",
    "Brazil": "Brazilian",
    "Canada": "Canadian",
}
FEATURED_PHOTOGRAPHER_IDS = [
    "daguerre",
    "fenton",
    "beato",
    "nadar",
    "stieglitz",
    "strand",
    "cartierbresson",
    "hiroshi-sugimoto",
]
MOVEMENT_NAME_OVERRIDES_EN = {
    "カロタイプ": "Calotype",
    "肖像写真": "Portrait Photography",
    "ヘリオグラフィー": "Heliography",
    "建築写真": "Architectural Photography",
    "写真石版": "Photolithography",
    "明治ドキュメンタリー": "Meiji Documentary",
}
MOVEMENT_SEARCH_TERMS_EN = {
    "写真分離派": ["photo-secession", "photo secession"],
    "ストレート写真": ["straight photography"],
    "モダニズム": ["modernism", "modernist photography"],
    "新即物主義": ["neue sachlichkeit", "new objectivity"],
    "新しいヴィジョン": ["new vision"],
    "バウハウス": ["bauhaus"],
    "シュルレアリスム": ["surrealism", "surrealist photography"],
    "レイオグラフ": ["rayograph", "rayographs"],
    "自然主義写真": ["naturalistic photography", "naturalism"],
    "リアリズム写真": ["realist photography", "realism photography"],
    "ドキュメンタリー": ["documentary", "documentary photography"],
    "社会ドキュメンタリー": ["social documentary", "social documentary photography"],
    "フォトジャーナリズム": ["photojournalism", "photo journalism"],
    "FSA写真": ["fsa", "fsa photography", "farm security administration"],
    "決定的瞬間": ["decisive moment"],
    "ストリート写真": ["street photography"],
    "プロヴォーク": ["provoke"],
    "私写真": ["i-photography", "shi-shashin", "private photography"],
    "ニューカラー": ["new color"],
    "カラー写真": ["color photography", "colour photography"],
    "大判カラー写真": ["large-format color", "large format color"],
    "デュッセルドルフ派": ["dusseldorf school", "düsseldorf school"],
    "タイポロジー写真": ["typological photography", "typology photography"],
    "コンセプチュアルアート": ["conceptual art"],
    "ピクチャーズ世代": ["pictures generation"],
    "ステージド写真": ["staged photography"],
    "フェミニズム写真": ["feminist photography"],
    "シネマトグラフィック写真": ["cinematographic photography", "cinematic photography"],
}
MOVEMENT_TEXT_SKIP_KEYS = {
    "url",
    "href",
    "id",
    "num",
    "name",
    "label",
    "title",
    "citations",
    "links",
    "sources",
}
JA_MOVEMENT_PREV_BLOCK_RE = re.compile(r"[ァ-ン一-龯A-Za-z0-9]")
JA_MOVEMENT_NEXT_BLOCK_RE = re.compile(r"[ァ-ン一-龯A-Za-z0-9]")
YEAR_OVERRIDES = {
    # These entries correct legacy activity-period values in the source data.
    # They are limited to dates already present in local research notes or static copy.
    "ansel-adams": "1902-1984",
    "arthur-rothstein": "1915-1985",
    "ben-shahn": "1898-1969",
    "bill-brandt": "1904-1983",
    "brassai": "1899-1984",
    "david-seymour": "1911-1956",
    "francois-kollar": "1904-1979",
    "helen-levitt": "1913-2009",
    "jack-delano": "1914-1997",
    "john-vachon": "1914-1975",
    "jp-影山光洋": "1907-1981",
    "jp-植田正治": "1913-2000",
    "jp-金丸重嶺": "1900-1977",
    "jp-鈴木八郎": "1900-1985",
    "jp-長谷川伝次郎": "1894-1976",
    "manuel-alvarez-bravo": "1902-2002",
    "marcel-bovis": "1904-1997",
    "margaret-bourke-white": "1904-1971",
    "minor-white": "1908-1976",
    "robert-doisneau": "1912-1994",
    "russell-lee": "1903-1986",
}
STRUCTURED_DATA_ALTERNATE_NAME_OVERRIDES = {
    "eugenesmith": {
        "ja": [
            "W. Eugene Smith",
            "ユージン・スミス",
            "ユージンスミス",
        ],
        "en": [
            "Eugene Smith",
            "William Eugene Smith",
        ],
    },
    "hiroshi-sugimoto": {
        "en": [
            "Sugimoto Hiroshi",
            "杉本博司",
        ],
    },
    "edward-weston": {
        "en": [
            "Edward Henry Weston",
        ],
    },
    "renger": {
        "en": [
            "Albert Renger Patzsch",
            "Renger-Patzsch",
        ],
    },
    "moriyama": {
        "en": [
            "Moriyama Daido",
            "森山大道",
        ],
    },
    "sherman": {
        "en": [
            "Cynthia Morris Sherman",
        ],
    },
}
SEO_TEXT_OVERRIDES = {
    "annie-leibovitz": {
        "ja": {
            "title": "アニー・リーボヴィッツ｜雑誌ページと公共的イメージの肖像写真｜写真の座標",
            "description": "アニー・リーボヴィッツを、Rolling Stone、Vanity Fair、Vogue、ジョン・レノン、デミ・ムーア、Women、Wonderlandから読み解く写真史解説。",
            "lead": "アニー・リーボヴィッツは、Rolling Stone、Vanity Fair、Vogueを横断し、音楽、映画、ファッション、政治、私的記憶を公共的な肖像イメージへ変換してきたアメリカの写真家。",
        },
        "en": {
            "title": "Annie Leibovitz | Magazine Pages and Public Portraiture | Photo Coordinates",
            "description": "A photo-history essay on Annie Leibovitz through Rolling Stone, Vanity Fair, Vogue, John Lennon, Demi Moore, Women, Wonderland, and the making of public images.",
            "lead": "Annie Leibovitz is an American photographer who moved through Rolling Stone, Vanity Fair, and Vogue, turning music, film, fashion, politics, and private memory into public portrait images.",
        },
    },
    "stieglitz": {
        "ja": {
            "title": "アルフレッド・スティーグリッツ | 291ギャラリーとエクイヴァレンツ | 写真の座標",
            "description": "291ギャラリーと写真誌『カメラ・ワーク』を主宰し、写真を絵画と並ぶ芸術として美術館に送り込んだアメリカ近代写真の中核。「エクイヴァレンツ」では被写体ではなく形式そのものが内面を語ると主張し、抽象写真の理論的基盤を築いた。",
            "lead": "291ギャラリーと写真誌『カメラ・ワーク』を主宰し、写真を絵画と並ぶ芸術として美術館に送り込んだアメリカ近代写真の中核。「エクイヴァレンツ」では被写体ではなく形式そのものが内面を語ると主張し、抽象写真の理論的基盤を築いた。",
        },
        "en": {
            "title": "Alfred Stieglitz | Gallery 291 and Equivalents | Photo Coordinates",
            "description": "As the force behind Gallery 291 and Camera Work, Alfred Stieglitz helped move photography into the museum as an art beside painting. With Equivalents, he argued that visual form itself could carry inner feeling and helped establish a basis for photographic abstraction.",
            "lead": "As the force behind Gallery 291 and Camera Work, Alfred Stieglitz helped move photography into the museum as an art beside painting. With Equivalents, he argued that visual form itself could carry inner feeling and helped establish a basis for photographic abstraction.",
        },
    },
    "renger": {
        "ja": {
            "title": "アルベルト・レンガー＝パッチュ | 新即物主義と物の写真 | 写真の座標",
            "description": "レンガー＝パッチュは、ピクトリアリズムの美化ともバウハウス的な視覚実験とも異なる立場から、事物そのものの構造的な美しさを精密に示した新即物主義写真の中心人物である。",
            "lead": "レンガー＝パッチュは、ピクトリアリズムの美化ともバウハウス的な視覚実験とも異なる立場から、事物そのものの構造的な美しさを精密に示した新即物主義写真の中心人物である。",
        },
        "en": {
            "title": "Albert Renger-Patzsch | New Objectivity, Neues Sehen, and Things | Photo Coordinates",
            "description": "Albert Renger-Patzsch is explained through New Objectivity, Neues Sehen, Die Welt ist schön, industrial forms, plants, objects, and precise photographic description.",
            "lead": "Renger-Patzsch made the photographed object itself central, rejecting both pictorialist beautification and Bauhaus-style visual experiment in favor of precise structural description.",
        },
    },
    "hiroshi-sugimoto": {
        "en": {
            "title": "Hiroshi Sugimoto | Seascapes, Theaters, Dioramas, and Time | Photo Coordinates",
            "description": "Hiroshi Sugimoto is explained through Seascapes, Theaters, Dioramas, long exposure, time, memory, museums, and conceptual photography.",
        },
    },
    "edward-weston": {
        "en": {
            "title": "Edward Weston | Group f/64, Straight Photography, and Modern Form | Photo Coordinates",
            "description": "Edward Weston is explained through Group f/64, straight photography, Mexico, Pepper No. 30, nudes, shells, Point Lobos, and modern photographic form.",
        },
    },
    "evans": {
        "ja": {
            "title": "ウォーカー・エヴァンス | FSAとアメリカ・ドキュメンタリー | 写真の座標",
            "description": "ウォーカー・エヴァンスはFSAで農村の貧困を記録しながら、政策宣伝から距離を取り、アメリカの表面を冷静に読むドキュメンタリー写真を確立した。『Let Us Now Praise Famous Men』や地下鉄肖像で、写真を社会記録と批評的観察の両方へ押し広げた。",
        },
        "en": {
            "title": "Walker Evans | FSA, American Photographs, and Documentary Style | Photo Coordinates",
            "description": "Walker Evans is explained through FSA photography, American Photographs, Let Us Now Praise Famous Men, subway portraits, vernacular signs, storefronts, and documentary style.",
        },
    },
    "cartierbresson": {
        "ja": {
            "title": "アンリ・カルティエ＝ブレッソン | 決定的瞬間と写真の構成 | 写真の座標",
            "description": "アンリ・カルティエ＝ブレッソンはシュルレアリスムの感覚とライカによる即応性を結びつけ、現実の一瞬に形態、身振り、意味が重なる「決定的瞬間」を写真の方法として確立した。マグナム創設にも関わり、20世紀フォトジャーナリズムの基準を作った。",
        },
        "en": {
            "title": "Henri Cartier-Bresson | Decisive Moment | Photo Coordinates",
            "description": "Henri Cartier-Bresson joined Surrealist alertness to the mobility of the Leica, defining the decisive moment as a meeting of form, gesture, and meaning in modern photography.",
        },
    },
    "eugenesmith": {
        "ja": {
            "title": "W・ユージン・スミス｜水俣・フォトエッセイ・写真史｜写真の座標",
            "description": "W・ユージン・スミスの写真を、水俣、LIFE誌のフォト・エッセイ、ピッツバーグ、ニューヨーク・ロフト期から写真史的に解説します。",
        },
        "en": {
            "title": "W. Eugene Smith | Minamata Project and the Photo Essay | Photo Coordinates",
            "description": "W. Eugene Smith's photography is explained through the Minamata Project, LIFE photo essays, Pittsburgh, darkroom printing, and the ethics of documentary representation.",
        },
    },
    "ansel-adams": {
        "ja": {
            "title": "アンセル・アダムス | ゾーン・システムとアメリカ西部 | 写真の座標",
            "description": "アンセル・アダムスはヨセミテを中心とするアメリカ西部の風景を、大判カメラとゾーン・システムによる精密なトーン制御で表現した。Group f/64、写真教育、環境保全運動を通じて、風景写真をファインアートと環境意識の領域へ押し上げた。",
        },
        "en": {
            "title": "Ansel Adams | Zone System, Group f/64, and Print as Performance",
            "description": "How Ansel Adams connected Group f/64’s straight photography with the Zone System’s control of exposure, development, and print. A source-based essay on Yosemite, print performance, conservation, and Manzanar.",
        },
    },
    "robertfrank": {
        "ja": {
            "title": "ロバート・フランク | 『The Americans』と戦後アメリカ | 写真の座標",
            "description": "ロバート・フランクは移民の視点から戦後アメリカを横断し、『The Americans』で国旗、車、食堂、人種差別、孤独を粗い粒子と傾いた構図で写した。明朗な報道写真に対抗し、主観的で不穏なアメリカ写真の基準を作った。",
        },
        "en": {
            "title": "Robert Frank | The Americans and Postwar Photography | Photo Coordinates",
            "description": "Robert Frank crossed the United States as an outsider and made The Americans, a dark, grainy, off-kilter portrait of flags, cars, diners, race, solitude, and postwar unease.",
        },
    },
    "moriyama": {
        "ja": {
            "title": "森山大道｜プロヴォークとアレ・ブレ・ボケ｜写真の座標",
            "description": "美術館・アーカイブ資料を手がかりに、森山大道のプロヴォーク、アレ・ブレ・ボケ、写真集、都市写真、戦後日本写真を読み解く写真史解説。",
        },
        "en": {
            "title": "Daido Moriyama | Provoke, Are-Bure-Boke, and Japanese Street Photography | Photo Coordinates",
            "description": "Daido Moriyama is explained through Provoke, are-bure-boke, photobooks, Tokyo street photography, rephotography, and postwar Japanese image culture.",
        },
    },
    "wolfgang-tillmans": {
        "ja": {
            "title": "ヴォルフガング・ティルマンス | 日常・抽象・インスタレーション | 写真の座標",
            "description": "ヴォルフガング・ティルマンスは、日常、クィアな社会性、クラブ文化、抽象、政治的イメージを横断し、写真を単一の額装作品ではなく壁面、出版、インスタレーションに広がる実践として再定義した現代写真の重要作家である。",
        },
        "en": {
            "title": "Wolfgang Tillmans | Everyday Life, Abstraction, and Installation | Photo Coordinates",
            "description": "Wolfgang Tillmans redefined contemporary photography across everyday life, queer sociality, club culture, abstraction, politics, publishing, and installation, making display itself part of photographic meaning.",
        },
    },
    "cameron": {
        "ja": {
            "title": "ジュリア・マーガレット・キャメロン | ヴィクトリア朝の肖像写真家 | 写真の座標",
            "description": "湿板写真の揺らぎとソフトフォーカスを用い、家族や使用人を聖母・文学の人物として撮影。後のピクトリアリズムに先立ち、肖像写真を外見の記録から感情と想像力の像へ転じた写真家。",
            "lead": "ヴィクトリア朝イギリスで、肖像写真を単なる外見の記録から、感情、信仰、文学的想像力を帯びた像へ押し広げた写真家。ソフトフォーカス、近接、大判ネガ、湿板写真の揺らぎを用い、家族、使用人、文学者、科学者を、聖母、預言者、詩の登場人物のように撮影した。技術的な鮮明さをめぐる当時の規範に対し、写真が内面や演出を扱えることを早い時期に示した。",
        },
        "en": {
            "title": "Julia Margaret Cameron | Victorian Portrait Photographer | Photo Coordinates",
            "description": "Cameron used soft focus and wet-plate instability to photograph family and servants as Madonnas and literary figures, anticipating Pictorialism by a generation.",
            "lead": "In Victorian Britain, Julia Margaret Cameron pushed portrait photography beyond the recording of outward likeness, turning it into an image charged with feeling, faith, and literary imagination. Through soft focus, close framing, large negatives, and the instabilities of the wet-collodion process, she photographed family members, servants, writers, and scientists as if they were Madonnas, prophets, or figures from poetry. At a time when photographic value was often tied to technical sharpness, her work showed early on that the medium could also carry inwardness, staging, and mythic suggestion.",
        },
    },
    "sherman": {
        "ja": {
            "title": "シンディ・シャーマン | 演出写真・ピクチャーズ世代 | 写真の座標",
            "description": "自らを映画・広告・美術史の人物像に変え、写真がいかに女性像を演出するかを問い続けた作家。『Untitled Film Stills』を軸に、ピクチャーズ世代・フェミニズム写真・演出写真との関わりを解説する。",
            "lead": "シンディ・シャーマンは、自分自身を映画、広告、雑誌、美術史の見覚えある人物像へ変えることで、写真を「現実の証拠」や「作者の内面」を示す媒体から、イメージが人物をどう演出し、見る側にどんな欲望や物語を引き出すかを問う媒体へ押し広げた作家。1970年代後半のニューヨークで、消費社会の既成イメージを扱ったピクチャーズ世代と並走し、『Untitled Film Stills』からフェミニズム写真、演出写真、ポストモダン写真へ大きな論点を開いた。",
        },
        "en": {
            "title": "Cindy Sherman | Staged Photography and the Pictures Generation | Photo Coordinates",
            "description": "Cindy Sherman is explained through Untitled Film Stills, staged photography, the Pictures Generation, feminism, identity, media images, and the performance of female roles.",
            "lead": "Cindy Sherman transformed photography from a medium associated with evidence, likeness, and authorial self-expression into a way of testing how cinema, advertising, magazines, and art history produce recognizable roles. Working alongside the Pictures Generation in late-1970s New York, she used her own body, costume, makeup, setting, and camera position to unsettle the idea that a single image can reveal a stable person.",
        },
    },
    "irving-penn": {
        "en": {
            "title": "Irving Penn | Vogue, Studio Portraits, Still Life, and the Print | Photo Coordinates",
            "description": "Irving Penn is explained through Vogue, studio portraits, fashion photography, Small Trades, still life, platinum-palladium printing, and the boundary between magazine and fine-art photography.",
        },
    },
    "lee-miller": {
        "ja": {
            "title": "リー・ミラー | 写真史 | 写真の座標",
            "description": "暗室実験からVogueの戦時写真、第二次大戦の前線報道まで横断したアメリカの写真家。ソラリゼーション技法、戦時下の女性の表現、ダッハウ解放後の記録、マン・レイとの関係の再評価をたどる。",
        },
        "en": {
            "title": "Lee Miller | Photo History | Photo Coordinates",
            "description": "Lee Miller crossed Surrealist darkroom work, Vogue wartime photography, and Second World War frontline reporting. Solarization, women's imagery, and her reassessment beyond Man Ray are traced here.",
        },
    },
    "nicephore-niepce": {
        "ja": {
            "title": "ニセフォール・ニエプス｜世界最古の写真とヘリオグラフィー｜写真の座標",
            "description": "ニセフォール・ニエプスを、世界最古の写真《ル・グラの窓からの眺め》、ヘリオグラフィー、写真の発明史から解説。",
            "lead": "世界最古の写真《ル・グラの窓からの眺め》とヘリオグラフィーによって、写真の発明史に決定的な位置を占めた人物。",
        },
        "en": {
            "title": "Nicéphore Niépce | The First Photograph and Heliography | Photo Coordinates",
            "description": "Explore Nicéphore Niépce through heliography, View from the Window at Le Gras, and the invention of photography.",
            "lead": "A pioneer of heliography whose View from the Window at Le Gras is central to the history of the first surviving photograph.",
        },
    },
    "daguerre": {
        "ja": {
            "title": "ルイ・ダゲール｜ダゲレオタイプと写真術の公開｜写真の座標",
            "description": "ルイ・ダゲールを、ダゲレオタイプ、銀板写真、1839年の写真術公開、《タンプル大通り》から解説。",
            "lead": "ダゲレオタイプを通じて写真術を社会に広めた人物。銀板写真、都市の視覚、1839年の公開制度から写真の出発点を考える。",
        },
        "en": {
            "title": "Louis Daguerre | Daguerreotype and Early Photography | Photo Coordinates",
            "description": "Explore Louis Daguerre through the daguerreotype, Boulevard du Temple, and the public announcement of photography in 1839.",
            "lead": "The inventor associated with the daguerreotype, whose process helped bring photography into public use in 1839.",
        },
    },
    "talbot": {
        "ja": {
            "title": "フォックス・タルボット｜カロタイプと『自然の鉛筆』｜写真の座標",
            "description": "フォックス・タルボットを、カロタイプ、ネガ・ポジ法、写真集『自然の鉛筆』から解説。",
            "lead": "カロタイプとネガ・ポジ法によって、写真を複製可能なメディアへ導いた人物。『自然の鉛筆』から写真集の始まりもたどる。",
        },
        "en": {
            "title": "William Henry Fox Talbot | Calotype and The Pencil of Nature | Photo Coordinates",
            "description": "Explore Fox Talbot through the calotype, the negative-positive process, and The Pencil of Nature, one of the first photographic books.",
            "lead": "A key figure in the calotype and negative-positive process, connecting early photography to reproducibility and the photographic book.",
        },
    },
    "david-octavius-hill": {
        "ja": {
            "title": "デイヴィッド・オクタヴィアス・ヒル｜ヒル＆アダムソンとカロタイプ｜写真の座標",
            "description": "デイヴィッド・オクタヴィアス・ヒルを、ロバート・アダムソンとの協働、カロタイプ、ニューヘブン連作から解説。",
            "lead": "ロバート・アダムソンとの協働により、カロタイプを肖像と社会記録へ展開した人物。ニューヘブンの漁師たちの連作も重要。",
        },
        "en": {
            "title": "David Octavius Hill | Hill & Adamson and the Calotype | Photo Coordinates",
            "description": "Explore David Octavius Hill through his collaboration with Robert Adamson, calotype portraiture, and the Newhaven fisherfolk photographs.",
            "lead": "Known for his collaboration with Robert Adamson, Hill helped turn calotype portraiture toward social presence and early documentary form.",
        },
    },
    "robert-adamson": {
        "ja": {
            "title": "ロバート・アダムソン｜ヒル＆アダムソンのカロタイプ写真｜写真の座標",
            "description": "ロバート・アダムソンを、ヒルとの協働、カロタイプ技術、ニューヘブンの漁師たち、初期社会記録写真から解説。",
            "lead": "ヒルとの協働で、カロタイプを肖像・労働・地域社会の記録へ広げた写真家。初期写真の表現力を大きく押し広げた。",
        },
        "en": {
            "title": "Robert Adamson | Hill & Adamson and Early Calotype Photography | Photo Coordinates",
            "description": "Explore Robert Adamson through his collaboration with David Octavius Hill, calotype technique, and early social portraiture in Scotland.",
            "lead": "A photographer whose collaboration with Hill gave calotype photography unusual depth in portraiture, labor, and social record.",
        },
    },
    "fenton": {
        "ja": {
            "title": "ロジャー・フェントン｜クリミア戦争と初期戦争写真｜写真の座標",
            "description": "ロジャー・フェントンを、クリミア戦争、《死の影の谷》、戦争写真が見せたもの／隠したものから解説。",
            "lead": "クリミア戦争を撮影した初期戦争写真の代表的存在。戦場を記録する写真が、報道・国家・世論とどう結びついたかを示す。",
        },
        "en": {
            "title": "Roger Fenton | Crimean War Photography | Photo Coordinates",
            "description": "Explore Roger Fenton through Crimean War photography, Valley of the Shadow of Death, and the early limits of war reportage.",
            "lead": "One of the central figures in early war photography, known for his Crimean War images and Valley of the Shadow of Death.",
        },
    },
    "legray": {
        "ja": {
            "title": "ギュスターヴ・ル・グレー｜海景写真とコンビネーション・プリント｜写真の座標",
            "description": "ギュスターヴ・ル・グレーを、《大波》、海景写真、空と海を合成するコンビネーション・プリントから解説。",
            "lead": "海景写真とコンビネーション・プリントによって、初期写真に技術的精度と絵画的構成をもたらした写真家。",
        },
        "en": {
            "title": "Gustave Le Gray | Seascapes and Combination Printing | Photo Coordinates",
            "description": "Explore Gustave Le Gray through seascapes, The Great Wave, Sète, and combination printing in early photographic art.",
            "lead": "A leading figure in early photographic art, known for seascapes and combination printing that joined technical control with visual drama.",
        },
    },
    "nadar": {
        "ja": {
            "title": "ナダール｜肖像写真・気球・航空写真｜写真の座標",
            "description": "ナダールを、肖像写真、ボードレールやユゴーのポートレート、気球による航空写真、地下撮影から解説。",
            "lead": "肖像写真、気球による航空写真、地下撮影を横断した写真家。十九世紀パリの文化人と都市空間を写真に結びつけた。",
        },
        "en": {
            "title": "Nadar | Portrait Photography, Balloons and Aerial Views | Photo Coordinates",
            "description": "Explore Nadar through portrait photography, aerial views from balloons, underground photography, and portraits of nineteenth-century artists.",
            "lead": "A photographer of portraits, balloons, aerial views, and underground spaces, linking nineteenth-century celebrity culture with experimental photography.",
        },
    },
    "alexander-gardner": {
        "ja": {
            "title": "アレクサンダー・ガードナー｜南北戦争写真と記録の倫理｜写真の座標",
            "description": "アレクサンダー・ガードナーを、南北戦争写真、『戦争写真スケッチブック』、アンティータム、リンカーン暗殺後の記録から解説。",
            "lead": "南北戦争写真を通じて、戦場の死、記録の編集、写真の証拠性を問い直した写真家。アンティータムの記録でも知られる。",
        },
        "en": {
            "title": "Alexander Gardner | Civil War Photography and Documentary Evidence | Photo Coordinates",
            "description": "Explore Alexander Gardner through Civil War photography, Antietam, Gardner's Photographic Sketch Book, and the ethics of photographic evidence.",
            "lead": "A Civil War photographer whose images of Antietam and photographic publications raised questions about evidence, staging, and historical memory.",
        },
    },
    "brady": {
        "ja": {
            "title": "マシュー・ブレイディ｜南北戦争写真と肖像スタジオ｜写真の座標",
            "description": "マシュー・ブレイディを、南北戦争写真、アンティータムの死者、大統領肖像、写真スタジオの記録体制から解説。",
            "lead": "肖像スタジオと撮影チームを通じて、南北戦争の視覚記録を組織した写真家。戦争写真とメディア体制の接点を示す。",
        },
        "en": {
            "title": "Mathew Brady | Civil War Photography and the Portrait Studio | Photo Coordinates",
            "description": "Explore Mathew Brady through Civil War photography, presidential portraits, Antietam, and the studio network behind wartime images.",
            "lead": "A portrait studio figure who organized one of the major photographic records of the American Civil War.",
        },
    },
    "beato": {
        "ja": {
            "title": "フェリーチェ・ベアト｜幕末日本・横浜写真・手彩色写真｜写真の座標",
            "description": "フェリーチェ・ベアトを、幕末日本、横浜写真、手彩色写真、クリミア戦争から東アジアへの記録写真で解説。",
            "lead": "幕末日本、横浜写真、手彩色写真を通じて、十九世紀の東アジア像を形成した写真家。戦争写真から観光的イメージまでを横断する。",
        },
        "en": {
            "title": "Felice Beato | Japan, Yokohama Photography and Hand-Colored Prints | Photo Coordinates",
            "description": "Explore Felice Beato through photographs of Japan, Yokohama photography, hand-colored prints, and nineteenth-century visual records of Asia.",
            "lead": "A photographer associated with Bakumatsu Japan, Yokohama photography, hand-colored prints, and nineteenth-century images of Asia.",
        },
    },
    "timothy-osullivan": {
        "ja": {
            "title": "ティモシー・オサリヴァン｜南北戦争写真と西部測量写真｜写真の座標",
            "description": "ティモシー・オサリヴァンを、南北戦争写真、ゲティスバーグ、西部測量写真、ニュー・トポグラフィクスへの接続から解説。",
            "lead": "南北戦争とアメリカ西部測量を撮影した写真家。地形、戦場、国家的調査が写真の視線をどう変えたかを示す。",
        },
        "en": {
            "title": "Timothy O'Sullivan | Civil War and American West Survey Photography | Photo Coordinates",
            "description": "Explore Timothy O'Sullivan through Civil War photography, American West survey images, Gettysburg, and later links to topographic photography.",
            "lead": "A photographer of the Civil War and American West surveys whose images later became important to discussions of topographic landscape photography.",
        },
    },
    "muybridge": {
        "ja": {
            "title": "エドワード・マイブリッジ | 連続写真と映像前史 | 写真の座標",
            "description": "馬の連続写真から投影装置まで、マイブリッジの実践を科学・大学制度・映像前史の交差点として写真史的に解説。運動の分解と再生が写真と映画の境界を揺らした意味を読み解く。",
        },
        "en": {
            "title": "Eadweard Muybridge | Motion Studies and Proto-Cinema | Photo Coordinates",
            "description": "From sequential motion photography to the Zoopraxiscope, Muybridge's practice is traced through science, university research, and proto-cinema history using museum and archive sources.",
        },
    },
    "marey": {
        "ja": {
            "title": "エティエンヌ＝ジュール・マレー | クロノフォトグラフィーと身体科学 | 写真の座標",
            "description": "クロノフォトグラフィーで運動を一枚の画像に凝縮したマレーを、生理学・身体科学・映像前史の文脈から解説。マイブリッジとの方法論的対照と、近代的身体計測との関係を論じる。",
        },
        "en": {
            "title": "Étienne-Jules Marey | Chronophotography and Body Science | Photo Coordinates",
            "description": "Marey's chronophotography — multiple exposures on one plate — is examined through physiology, labor science, and proto-cinema, with comparison to Muybridge's sequential approach.",
        },
    },
    "marville": {
        "ja": {
            "title": "シャルル・マルヴィル | パリ都市変容の写真記録 | 写真の座標",
            "description": "ハウスマン改造前後のパリを市の委嘱で記録したマルヴィルの実践を、行政的近代化・都市史・写真アーカイブの観点から解説。旧市街の消滅と新都の出現という二重記録を論じる。",
        },
        "en": {
            "title": "Charles Marville | Paris Urban Photography | Photo Coordinates",
            "description": "Marville's photographs of Paris before and after Haussmann's rebuilding, analyzed as both municipal record and visual archive of modern urban transformation.",
        },
    },
    "frederick-h-evans": {
        "ja": {
            "title": "フレデリック・H・エヴァンズ | 大聖堂写真と写真芸術運動 | 写真の座標",
            "description": "ゴシック大聖堂をプラチナ印画の階調で写真化したエヴァンズを、Linked Ringと写真芸術運動・精神性・建築空間の光の組織化から解説。写真が記録から芸術的経験へ移行する過程を論じる。",
        },
        "en": {
            "title": "Frederick H. Evans | Cathedral Photography and Art Photography | Photo Coordinates",
            "description": "Evans's platinum print cathedral photographs examined through Linked Ring, the Arts and Crafts milieu, and the argument for photography as fine art.",
        },
    },
    "annan": {
        "ja": {
            "title": "トーマス・アナン | グラスゴー旧市街とドキュメンタリー前史 | 写真の座標",
            "description": "グラスゴー旧市街を改善委嘱で記録したアナンを、都市史・出版写真・ドキュメンタリー前史の文脈で解説。改善記録として撮られた写真が都市貧困の証言として再評価される逆説を論じる。",
        },
        "en": {
            "title": "Thomas Annan | Glasgow Documentary Photography | Photo Coordinates",
            "description": "Thomas Annan's Glasgow photographs examined as early documentary records, with analysis of how improvement commission images became testimony to urban poverty.",
        },
    },
    "riis": {
        "ja": {
            "title": "ジェイコブ・リース | スラムの可視化と社会改革写真 | 写真の座標",
            "description": "ニューヨークのスラムをフラッシュ写真・書籍・講演で可視化したリースを、社会改革・メディア史・ドキュメンタリー前史から解説。改革の道具としての写真が孕む表象の問題も論じる。",
        },
        "en": {
            "title": "Jacob Riis | Social Reform Photography | Photo Coordinates",
            "description": "Riis's combination of flash photography, books, and lectures as tools for social reform, traced through media history and early documentary photography.",
        },
    },
    "jp-tomishige-rihei": {
        "ja": {
            "title": "冨重利平 | 熊本・明治写真館の制度化 | 写真の座標",
            "description": "熊本で冨重写真所を創業した冨重利平を、地方写真制度の形成・明治肖像文化・写真館の継承という観点から解説。九州の明治写真史における位置づけを出典に基づき論じる。",
        },
        "en": {
            "title": "Tomishige Rihei | Meiji Portrait Photography in Kumamoto | Photo Coordinates",
            "description": "Tomishige Rihei examined through Meiji portrait culture, regional modernization, and the institutional history of photography in Kyushu.",
        },
    },
    "jp-yokoyama-matsusaburo": {
        "ja": {
            "title": "横山松三郎 | 明治視覚制度と複合メディア実践 | 写真の座標",
            "description": "写真・油絵・石版を横断し江戸城撮影・壬申検査・博覧会記録に関わった横山松三郎を、明治視覚制度の形成という文脈から解説。関係資料は重要文化財に指定されている。",
        },
        "en": {
            "title": "Yokoyama Matsusaburo | Meiji Photography and Visual Documentation | Photo Coordinates",
            "description": "Yokoyama Matsusaburo's cross-media practice examined through Meiji visual documentation systems, Edo Castle photography, and cultural heritage surveys.",
        },
    },
    "jp-tomishige-tokuji": {
        "ja": {
            "title": "冨重徳次 | 写真館の継承と地域近代 | 写真の座標",
            "description": "冨重利平の後継として冨重写真所を引き継いだ徳次を、地方近代における写真館の継承と制度持続という観点から解説。熊本の肖像文化と地域記録の長期的維持を論じる。",
        },
        "en": {
            "title": "Tomishige Tokuji | Photography Studio Succession in Kumamoto | Photo Coordinates",
            "description": "Tomishige Tokuji and the institutional continuity of the Kumamoto photography studio examined through regional Meiji and Taisho photography history.",
        },
    },
}
SAME_AS_OVERRIDES = {
    "stieglitz": [
        "https://en.wikipedia.org/wiki/Alfred_Stieglitz",
        "https://ja.wikipedia.org/wiki/%E3%82%A2%E3%83%AB%E3%83%95%E3%83%AC%E3%83%83%E3%83%89%E3%83%BB%E3%82%B9%E3%83%86%E3%82%A3%E3%83%BC%E3%82%B0%E3%83%AA%E3%83%83%E3%83%84",
        "https://www.wikidata.org/wiki/Q313055",
        "https://viaf.org/viaf/49231990",
        "https://www.getty.edu/art/collection/person/103KH0",
    ],
    "cameron": [
        "https://en.wikipedia.org/wiki/Julia_Margaret_Cameron",
        "https://ja.wikipedia.org/wiki/%E3%82%B8%E3%83%A5%E3%83%AA%E3%82%A2%E3%83%BB%E3%83%9E%E3%83%BC%E3%82%AC%E3%83%AC%E3%83%83%E3%83%88%E3%83%BB%E3%82%AD%E3%83%A3%E3%83%A1%E3%83%AD%E3%83%B3",
        "https://www.wikidata.org/wiki/Q230120",
        "https://viaf.org/viaf/61616074",
    ],
    "nicephore-niepce": [
        "https://en.wikipedia.org/wiki/Nic%C3%A9phore_Ni%C3%A9pce",
        "https://www.wikidata.org/wiki/Q52384",
        "https://viaf.org/viaf/12482609",
    ],
    "daguerre": [
        "https://en.wikipedia.org/wiki/Louis_Daguerre",
        "https://www.wikidata.org/wiki/Q183364",
        "https://viaf.org/viaf/59128560",
    ],
    "talbot": [
        "https://en.wikipedia.org/wiki/Henry_Fox_Talbot",
        "https://www.wikidata.org/wiki/Q107316",
        "https://viaf.org/viaf/56603025",
    ],
    "david-octavius-hill": [
        "https://en.wikipedia.org/wiki/David_Octavius_Hill",
        "https://www.wikidata.org/wiki/Q348282",
    ],
    "robert-adamson": [
        "https://en.wikipedia.org/wiki/Robert_Adamson_(photographer)",
        "https://www.wikidata.org/wiki/Q392453",
    ],
    "fenton": [
        "https://en.wikipedia.org/wiki/Roger_Fenton",
        "https://www.wikidata.org/wiki/Q349687",
    ],
    "legray": [
        "https://en.wikipedia.org/wiki/Gustave_Le_Gray",
        "https://www.wikidata.org/wiki/Q613302",
    ],
    "nadar": [
        "https://en.wikipedia.org/wiki/Nadar_(photographer)",
        "https://www.wikidata.org/wiki/Q292552",
        "https://viaf.org/viaf/32794097",
    ],
    "alexander-gardner": [
        "https://en.wikipedia.org/wiki/Alexander_Gardner_(photographer)",
        "https://www.wikidata.org/wiki/Q390803",
    ],
    "brady": [
        "https://en.wikipedia.org/wiki/Mathew_Brady",
        "https://www.wikidata.org/wiki/Q355819",
    ],
    "beato": [
        "https://en.wikipedia.org/wiki/Felice_Beato",
        "https://www.wikidata.org/wiki/Q23824",
    ],
    "timothy-osullivan": [
        "https://en.wikipedia.org/wiki/Timothy_H._O%27Sullivan",
        "https://www.wikidata.org/wiki/Q389282",
    ],
}
JP_TEXT_RE = re.compile(r"[ぁ-んァ-ン一-龯]")
EN_REFERENCE_REPLACEMENTS = {
    "公式アーカイブ": "official archive",
    "プレスリリース": "press release",
    "写真の小さな歴史": "A Little History of Photography",
    "マン・レイとのエピソードを含む": "including the Man Ray episode",
    "ベレニス・アボットによるアーカイブ保存": "archive preserved by Berenice Abbott",
    "ジョン・シャーコウスキーの評価": "John Szarkowski on Atget",
    "写真美術館": "Photography Museum",
    "美術館": "Museum",
    "記念館": "Memorial Museum",
    "文化庁": "Agency for Cultural Affairs",
}


def eval_js(files: list[str], expression: str):
    source = ["(function(){"]
    for rel in files:
        source.append((REPO / rel).read_text(encoding="utf-8"))
    source.append(f"console.log(JSON.stringify({expression}));")
    source.append("})();")
    proc = subprocess.run(
        ["osascript", "-l", "JavaScript"],
        input="\n".join(source).encode("utf-8"),
        capture_output=True,
        check=True,
    )
    payload = proc.stderr.decode("utf-8") or proc.stdout.decode("utf-8")
    return json.loads(payload)


def load_affiliate_books() -> dict:
    source = ["(function(){", "var window = {};"]
    source.append((REPO / "data/affiliate-books.js").read_text(encoding="utf-8"))
    source.append("console.log(JSON.stringify(window.PHOTOGRAPHER_AFFILIATE_BOOKS || {}));")
    source.append("})();")
    proc = subprocess.run(
        ["osascript", "-l", "JavaScript"],
        input="\n".join(source).encode("utf-8"),
        capture_output=True,
        check=True,
    )
    payload = proc.stderr.decode("utf-8") or proc.stdout.decode("utf-8")
    return json.loads(payload)


def load_essay_overrides() -> dict:
    source = ["(function(){", "var window = {};"]
    source.append((REPO / "data/photographer-essay-overrides.js").read_text(encoding="utf-8"))
    source.append("console.log(JSON.stringify(window.PHOTOGRAPHER_ESSAY_OVERRIDES || {}));")
    source.append("})();")
    proc = subprocess.run(
        ["osascript", "-l", "JavaScript"],
        input="\n".join(source).encode("utf-8"),
        capture_output=True,
        check=True,
    )
    payload = proc.stderr.decode("utf-8") or proc.stdout.decode("utf-8")
    return json.loads(payload)


def escape_html(text: str) -> str:
    return html.escape(text or "")


def strip_cite_markers(text: str) -> str:
    return re.sub(r"\*\d+", "", text or "").strip()


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "")


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def truncate_text(text: str, length: int) -> str:
    value = normalize_space(text)
    if len(value) <= length:
        return value
    cutoff = value.rfind(" ", 0, length)
    if cutoff < max(20, length // 2):
        cutoff = length
    return value[:cutoff].rstrip("、。,. ") + "…"


def clip_at_word(text: str, length: int) -> str:
    value = normalize_space(text)
    if len(value) <= length:
        return value
    cutoff = value.rfind(" ", 0, length)
    if cutoff < max(20, length // 2):
        cutoff = length
    return value[:cutoff].rstrip("、。,. ")


def english_movement_name(movement: str, movements_meta: dict) -> str:
    meta = movements_meta.get(movement, {})
    return meta.get("en") or MOVEMENT_NAME_OVERRIDES_EN.get(movement) or movement


def collect_text_fragments(value, bucket: list[str]) -> None:
    if isinstance(value, str):
        normalized = normalize_space(strip_cite_markers(html.unescape(value)))
        if normalized:
            bucket.append(normalized)
        return
    if isinstance(value, list):
        for item in value:
            collect_text_fragments(item, bucket)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if key in MOVEMENT_TEXT_SKIP_KEYS:
                continue
            collect_text_fragments(item, bucket)


def contains_japanese_movement_term(text: str, term: str) -> bool:
    if not text or not term:
        return False
    start = 0
    while True:
        index = text.find(term, start)
        if index < 0:
            return False
        prev_char = text[index - 1] if index > 0 else ""
        next_index = index + len(term)
        next_char = text[next_index] if next_index < len(text) else ""
        if not JA_MOVEMENT_PREV_BLOCK_RE.search(prev_char) and not JA_MOVEMENT_NEXT_BLOCK_RE.search(next_char):
            return True
        start = index + len(term)


def inferred_movement_names(
    photographer: dict,
    movements_meta: dict,
    enrichments: dict,
    override_entry: dict | None = None,
) -> list[str]:
    texts: list[str] = []
    collect_text_fragments(photographer.get("context") or {}, texts)
    collect_text_fragments(override_entry or {}, texts)
    collect_text_fragments(get_enrichment(enrichments, photographer), texts)
    if not texts:
        return []

    haystack_ja = "\n".join(texts)
    haystack_en = "\n".join(texts).lower()
    inferred: list[str] = []
    seen = set()

    for movement in taxonomy_meta.MOVEMENT_TAXONOMY.get("featured") or []:
        canonical = taxonomy_meta.canonical_movement_name(movement)
        if not canonical or canonical in seen:
            continue

        matched = contains_japanese_movement_term(haystack_ja, canonical)
        if not matched:
            for alias, alias_target in (taxonomy_meta.MOVEMENT_ALIAS_MAP or {}).items():
                if alias_target == canonical and contains_japanese_movement_term(haystack_ja, alias):
                    matched = True
                    break
        if not matched:
            english_terms = [english_movement_name(canonical, movements_meta)] + MOVEMENT_SEARCH_TERMS_EN.get(canonical, [])
            for term in english_terms:
                if term and term.lower() in haystack_en:
                    matched = True
                    break
        if matched:
            inferred.append(canonical)
            seen.add(canonical)

    return inferred


def related_movement_names(
    photographer: dict,
    movements_meta: dict,
    enrichments: dict,
    override_entry: dict | None = None,
    limit: int = 5,
) -> list[str]:
    names: list[str] = []
    seen = set()

    for movement in taxonomy_meta.visible_movement_values(photographer, enrichments):
        if movement in seen:
            continue
        names.append(movement)
        seen.add(movement)

    for movement in inferred_movement_names(photographer, movements_meta, enrichments, override_entry):
        if movement in seen:
            continue
        names.append(movement)
        seen.add(movement)
        if len(names) >= limit:
            break

    return names[:limit]


def fallback_english_reference_label(url: str) -> str:
    host = ""
    try:
        host = urlparse(url).hostname or ""
    except Exception:
        host = ""
    host = re.sub(r"^www\.", "", host)
    return f"Japanese source — {host}" if host else "Japanese source"


def english_reference_label(label: str, url: str) -> str:
    value = normalize_space(label)
    if value in {"Wikipedia (JA)", "Wikipedia JA"}:
        return "Japanese Wikipedia"
    if value in {"Wikipedia (EN)", "Wikipedia EN"}:
        return "Wikipedia"
    if "Wikipedia (JA)" in value:
        value = value.replace("Wikipedia (JA)", "Japanese Wikipedia")
    if "Wikipedia (EN)" in value:
        value = value.replace("Wikipedia (EN)", "Wikipedia")
    if not value or not JP_TEXT_RE.search(value):
        return value
    for source, target in EN_REFERENCE_REPLACEMENTS.items():
        value = value.replace(source, target)
    if not JP_TEXT_RE.search(value):
        return value
    if " — " in value:
        left, right = value.split(" — ", 1)
        if not JP_TEXT_RE.search(left):
            translated_right = right
            for source, target in EN_REFERENCE_REPLACEMENTS.items():
                translated_right = translated_right.replace(source, target)
            translated_right = re.sub(r"（[^）]*）", "", translated_right).strip()
            if not JP_TEXT_RE.search(translated_right) and translated_right:
                return f"{left} — {translated_right}"
    return fallback_english_reference_label(url)


def localize_affiliate_value(record: dict, lang: str, ja_key: str, en_key: str, fallback_key: str = "") -> str:
    if not isinstance(record, dict):
        return ""
    value = (record.get(en_key) or record.get(ja_key) or record.get(fallback_key or "") or "") if lang == "en" else (record.get(ja_key) or record.get(en_key) or record.get(fallback_key or "") or "")
    return html.unescape(str(value or "")).strip()


def build_affiliate_books_html(photographer: dict, lang: str, affiliate_books: dict, copy: dict) -> str:
    entry = affiliate_books.get(photographer.get("id")) or {}
    books = []
    for book in entry.get("books") or []:
        languages = book.get("languages")
        if isinstance(languages, list) and lang not in languages:
            continue
        title = localize_affiliate_value(book, lang, "titleJa", "titleEn", "title")
        note = localize_affiliate_value(book, lang, "noteJa", "noteEn", "note")
        url = localize_affiliate_value(book, lang, "urlJa", "urlEn", "url")
        image_url = localize_affiliate_value(book, lang, "imageUrlJa", "imageUrlEn", "imageUrl")
        image_alt = localize_affiliate_value(book, lang, "imageAltJa", "imageAltEn", "imageAlt") or title
        if title and url:
            books.append({
                "title": title,
                "note": note,
                "url": url,
                "imageUrl": image_url,
                "imageAlt": image_alt,
            })
    books = books[:5]

    if not books:
        return f"""<section class="section" data-affiliate-section data-nosnippet>
        <h2>{escape_html(books_heading(photographer, lang))}</h2>
        <div class="book-grid">
          <div class="note">{copy['booksPlaceholder']}</div>
        </div>
      </section>"""

    cards = []
    for book in books:
        image_html = ""
        if book["imageUrl"]:
            image_html = f'<img class="book-thumb" src="{escape_html(book["imageUrl"])}" alt="{escape_html(book["imageAlt"])}" loading="lazy">'
        cards.append(f"""<div class="book-card">
          <div class="book-media">
            {image_html}
            <div class="book-copy">
              <div class="book-title">{escape_html(book['title'])}</div>
              {f'<div class="book-note">{escape_html(book["note"])}</div>' if book['note'] else ''}
            </div>
          </div>
          <div class="book-actions">
            <a class="chip-link amazon-cta" href="{escape_html(book['url'])}" target="_blank" rel="noopener sponsored">{copy['amazonCta']}</a>
            <span class="affiliate-disclosure">{escape_html(copy['affiliateDisclosure'])}</span>
          </div>
        </div>""")

    return f"""<section class="section" data-affiliate-section data-nosnippet>
        <h2>{escape_html(books_heading(photographer, lang))}</h2>
        <div class="book-grid">
          {''.join(cards)}
        </div>
      </section>"""


def first_sentences(text: str, lang: str, limit: int = 2) -> list[str]:
    plain = normalize_space(strip_tags(strip_cite_markers(text or "")))
    if not plain:
        return []
    if lang == "en":
        parts = re.split(r"(?<=[.!?])\s+", plain)
    else:
        parts = re.split(r"(?<=[。！？])\s*", plain)
    return [part.strip() for part in parts if part.strip()][:limit]


def parse_years(years_text: str) -> tuple[str, str]:
    clean = normalize_space(years_text)
    if not clean:
        return "", ""
    full_match = re.fullmatch(r"(\d{4})\s*[-–—]\s*(\d{4})", clean)
    if full_match:
        return full_match.group(1), full_match.group(2)
    open_match = re.fullmatch(r"(\d{4})\s*[-–—]\s*", clean)
    if open_match:
        return open_match.group(1), ""
    return "", ""


def country_entry(nationality: str) -> dict:
    meta = taxonomy_meta.ensure_country_meta(nationality) if nationality else None
    if meta:
        return {
            "slug": meta.get("slug", ""),
            "ja": meta.get("ja_name", nationality),
            "en": meta.get("en_name", nationality),
        }
    return COUNTRY_META.get(nationality or "", {})


def raw_years_is_activity_period(years_text: str) -> bool:
    value = normalize_space(years_text)
    return bool(
        re.fullmatch(
            r"\d{3,4}s(?:–|-)?(?:\s*/\s*\d{3,4}年代)?",
            value or "",
        )
    )


def infer_years_from_text(text: str) -> str:
    value = normalize_space(strip_cite_markers(text or ""))
    if not value:
        return ""
    birth_patterns = [
        r"\bborn\b(?:[^0-9]{0,80})\b(1[789]\d{2}|20\d{2})\b",
        r"\b(1[789]\d{2}|20\d{2})\s*年生まれ",
    ]
    death_patterns = [
        r"\bdied\b(?:[^0-9]{0,80})\b(1[789]\d{2}|20\d{2})\b",
        r"\b(1[789]\d{2}|20\d{2})\s*年没",
    ]
    birth = ""
    death = ""
    for pattern in birth_patterns:
        match = re.search(pattern, value, re.I)
        if match:
            birth = match.group(1)
            break
    for pattern in death_patterns:
        match = re.search(pattern, value, re.I)
        if match:
            death = match.group(1)
            break
    if not birth:
        return ""
    return f"{birth}-{death}" if death else f"{birth}-"


def description_years(photographer: dict, lang: str) -> str:
    birth, death = parse_years(photographer.get("years") or "")
    if not birth:
        return ""
    dash = "–"
    if death:
        return f"{birth}{dash}{death}"
    return f"{birth}{dash}"


def strip_leading_identity(sentence: str, photographer: dict, lang: str) -> str:
    value = normalize_space(sentence)
    names = [
        display_name(photographer, lang),
        display_alt_name(photographer, lang),
        display_name(photographer, "ja"),
        display_name(photographer, "en"),
        display_alt_name(photographer, "ja"),
        display_alt_name(photographer, "en"),
    ]
    expanded_names = []
    for name in names:
        if not name:
            continue
        expanded_names.append(name)
        expanded_names.extend(part for part in re.split(r"[・＝= ]+", name) if part)
    names = expanded_names
    names = [name for name in names if name]
    alt = display_alt_name(photographer, lang)
    for name in names:
        combo_variants = [
            f"{name}（{alt}）" if alt else "",
            f"{name} ({alt})" if alt else "",
            name,
        ]
        for variant in combo_variants:
            if variant and value.startswith(variant):
                value = value[len(variant):].lstrip(" 　,，、。")
    if lang == "en":
        value = re.sub(r"^(?:is|was)\s+", "", value, count=1)
    else:
        value = re.sub(r"^(?:は|が|を|の)[、，]?", "", value, count=1)
    return value.strip()


def descriptor_title_phrase(descriptor: str, lang: str) -> str:
    desc = normalize_space(descriptor)
    if not desc:
        return "Photographer" if lang == "en" else "写真家"
    if lang == "en":
        lower = desc.lower()
        if lower.endswith("photography"):
            return f"Pioneer of {desc}"
        if lower.endswith("culture"):
            return f"photographer of {desc}"
        if lower.endswith("documentary"):
            return f"{desc} photographer"
        return f"{desc} photographer"
    if desc.endswith("写真"):
        return f"{desc}の重要作家"
    if desc.endswith("文化"):
        return f"{desc}を記録した写真家"
    if desc.endswith("派"):
        return f"{desc}の中心作家"
    if desc.endswith("主義"):
        return f"{desc}の重要作家"
    return f"{desc}の写真家"


def extract_title_role(photographer: dict, lang: str, era_lookup: dict, movements_meta: dict, enrichments: dict) -> str:
    essay_text, _ = collect_text_and_citations(photographer, lang)
    sentences = first_sentences(essay_text, lang, limit=2)

    if lang == "en":
        for sentence in sentences:
            match = re.search(r"\b(?:is|was)\s+(an?\s+.+?photographer(?:\s+and\s+.+?)?)\b", sentence, re.I)
            if match:
                phrase = match.group(1)
                phrase = re.split(r"\s+who\s+|\s+whose\s+|\s*,\s*", phrase, 1)[0]
                return normalize_space(phrase)
        descriptor = descriptor_for(photographer, lang, era_lookup, movements_meta, enrichments)
        return descriptor_title_phrase(descriptor, lang)

    for sentence in sentences:
        stripped = strip_leading_identity(sentence, photographer, lang).rstrip("。")
        for pattern in (
            r"(.+?を記録した写真家)",
            r"(.+?を撮り続けた写真家)",
            r"(.+?を追った写真家)",
            r"(.+?を築いた写真家)",
            r"(.+?を代表する写真家)",
            r"(.+?の写真家)",
        ):
            match = re.search(pattern, stripped)
            if match:
                phrase = normalize_space(match.group(1))
                if len(phrase) <= 32:
                    return phrase
        if "写真家" in stripped and len(stripped) <= 36:
            return normalize_space(stripped.replace("である", "").replace("です", ""))

    descriptor = descriptor_for(photographer, lang, era_lookup, movements_meta, enrichments)
    return descriptor_title_phrase(descriptor, lang)


def build_meta_summary(photographer: dict, lang: str, era_lookup: dict, movements_meta: dict, enrichments: dict) -> str:
    essay_text, _ = collect_text_and_citations(photographer, lang)
    placeholder = is_placeholder_text(essay_text, lang)
    sentences = first_sentences(essay_text, lang, limit=2)
    years = description_years(photographer, lang)
    name = display_name(photographer, lang)
    country_en = country_entry(photographer.get("nationality") or "").get("en") or (photographer.get("nationality") or "")
    descriptor = descriptor_for(photographer, lang, era_lookup, movements_meta, enrichments)
    movement_names = expanded_movement_names(photographer, lang, movements_meta, enrichments, limit=2)
    movement_phrase = join_list(movement_names, lang)

    if lang == "en":
        if not placeholder and sentences:
            summary = " ".join(sentences)
            if len(summary) <= 155 and years and name not in summary:
                stripped = strip_leading_identity(summary, photographer, lang)
                summary = f"{name} ({years}): {stripped}"
            if len(summary) <= 155:
                return summary
        parts = []
        if years:
            parts.append(f"{name} ({years})")
        else:
            parts.append(name)
        if country_en:
            country_word = COUNTRY_ADJECTIVES_EN.get(country_en, country_en)
            article = "an" if country_word[:1].lower() in {"a", "e", "i", "o", "u"} else "a"
            parts.append(f"is {article} {country_word} photographer")
        else:
            parts.append("is a photographer")
        if descriptor:
            parts.append(f"associated with {clip_at_word(descriptor.lower(), 52)}")
        elif movement_phrase:
            parts.append(f"associated with {clip_at_word(movement_phrase, 52)}")
        period = era_period(photographer, era_lookup)
        opening = " ".join(parts).rstrip(".") + "."
        if period and period != "—":
            closing = "Trace related eras, movements, figures, and sources."
        else:
            closing = "Trace related eras, movements, figures, and sources."
        summary = f"{opening} {closing}"
        clipped = clip_at_word(summary, 155).rstrip(".")
        return f"{clipped}."

    if not placeholder and sentences:
        summary = "".join(sentences)
        if years and name not in summary:
            stripped = strip_leading_identity(summary, photographer, lang)
            stripped = re.sub(r"^(?:は|が|を|の)[、，]?", "", stripped)
            summary = f"{name}（{years}）は、{stripped}"
        return truncate_text(summary, 145)

    if years:
        opening = f"{name}（{years}）"
    else:
        opening = name
    period = era_period(photographer, era_lookup)
    if descriptor:
        if period and period != "—":
            base = f"{opening}は{descriptor}を手がかりに読み解かれる写真家。{period}の時代背景や関連する作家、出典をこのページで順次たどる。"
        else:
            base = f"{opening}は{descriptor}を手がかりに読み解かれる写真家。関連する時代背景や作家、出典をこのページで順次たどる。"
    elif movement_phrase:
        if period and period != "—":
            base = f"{opening}は{movement_phrase}の文脈から読み解かれる写真家。{period}の時代背景や関連する作家、出典をこのページで順次たどる。"
        else:
            base = f"{opening}は{movement_phrase}の文脈から読み解かれる写真家。関連する時代背景や作家、出典をこのページで順次たどる。"
    else:
        if period and period != "—":
            base = f"{opening}は写真史の流れの中で位置づけをたどる写真家。{period}の時代背景や関連する作家、出典をこのページで順次整理する。"
        else:
            base = f"{opening}は写真史の流れの中で位置づけをたどる写真家。このページでは関連する時代背景や作家、出典を順次整理する。"
    return truncate_text(base, 145)


def movement_slug(name: str) -> str:
    return taxonomy_meta.movement_slug(name)


def photographer_page_path(photographer: dict, lang: str = "ja") -> str:
    base = "en/photographers" if lang == "en" else "photographers"
    return f"/{base}/{photographer['id']}.html"


def era_page_path(photographer: dict, lang: str = "ja") -> str:
    era_id = photographer.get("era") or ""
    base = "en/eras" if lang == "en" else "eras"
    return f"/{base}/{era_id}.html" if era_id else ""


def country_page_path(photographer: dict, lang: str = "ja") -> str:
    nationality = photographer.get("nationality") or ""
    slug = country_entry(nationality).get("slug")
    if not slug:
        return ""
    base = "en/countries" if lang == "en" else "countries"
    return f"/{base}/{slug}.html"


def movement_page_path(movement: str, lang: str = "ja", movements_meta: dict | None = None) -> str:
    canonical = taxonomy_meta.canonical_movement_name(movement)
    if not canonical:
        return ""
    base = "en/movements" if lang == "en" else "movements"
    return f"/{base}/{taxonomy_meta.movement_slug(canonical, lang, movements_meta or {})}.html"


def render_site_directory_nav(
    photographers: list[dict],
    eras: list[dict],
    all_nationalities: list[str],
    lang: str,
    related_movements: list[tuple[str, str]] | None = None,
    related_people: list[tuple[str, str]] | None = None,
) -> str:
    labels = {
        "ja": {
            "nav": "サイト内リンク",
            "relatedPeople": "関連する人物・写真家",
            "relatedMovements": "関連する運動",
            "eras": "年代一覧",
            "countries": "国一覧",
            "photographers": "代表写真家一覧",
        },
        "en": {
            "nav": "Site links",
            "relatedPeople": "Related people & photographers",
            "relatedMovements": "Related movements",
            "eras": "Era index",
            "countries": "Country index",
            "photographers": "Featured photographers",
        },
    }[lang]
    def render_directory_link(url: str, label: str) -> str:
        extra_attrs = ' target="_blank" rel="noopener"' if url.startswith("http") else ""
        return f'<a href="{escape_html(url)}"{extra_attrs}>{escape_html(label)}</a>'

    def render_unique_links(items: list[tuple[str, str]] | None) -> str:
        rendered = []
        seen = set()
        for url, label in items or []:
            if not url or not label:
                continue
            key = (url, label)
            if key in seen:
                continue
            seen.add(key)
            rendered.append(render_directory_link(url, label))
        return "".join(rendered)

    def render_group(label: str, links: str, contextual: bool = False) -> str:
        context_class = " site-directory-group-contextual" if contextual else ""
        return f"""        <div class="site-directory-group{context_class}">
          <div class="site-directory-label">{escape_html(label)}</div>
          <div class="site-directory-items">{links}</div>
        </div>"""

    groups = []
    related_people_links = render_unique_links(related_people)
    related_movement_links = render_unique_links(related_movements)
    if related_people_links:
        groups.append(render_group(labels["relatedPeople"], related_people_links, contextual=True))
    if related_movement_links:
        groups.append(render_group(labels["relatedMovements"], related_movement_links, contextual=True))
    if not groups:
        return ""
    directory_groups = "\n".join(groups)
    return f"""
      <nav class="site-directory-links" aria-label="{escape_html(labels['nav'])}" data-nosnippet>
{directory_groups}
      </nav>"""


def render_tax_select(
    options: list[tuple[str, str, bool]],
    label: str,
    placeholder: str | None = None,
) -> str:
    rendered = []
    if placeholder:
        rendered.append(f'<option value="" selected>{escape_html(placeholder)}</option>')
    for value, text, selected in options:
        is_selected = selected and not placeholder
        rendered.append(f'<option value="{escape_html(value)}"{ " selected" if is_selected else "" }>{escape_html(text)}</option>')
    return f'<span class="select-wrap"><select class="tax-select filter-select nav-select" aria-label="{escape_html(label)}" onchange="if(this.value) window.location.href=this.value">{"".join(rendered)}</select></span>'


def render_optional_tax_select(options: list[tuple[str, str]], label: str, placeholder: str) -> str:
    if not options:
        return ""
    rendered = [f'<option value="" selected>{escape_html(placeholder)}</option>']
    for value, text in options:
        rendered.append(f'<option value="{escape_html(value)}">{escape_html(text)}</option>')
    return f'<span class="select-wrap"><select class="tax-select filter-select nav-select" aria-label="{escape_html(label)}" onchange="if(this.value) window.location.href=this.value">{"".join(rendered)}</select></span>'


def localize_value(record: dict, ja_key: str, en_key: str) -> str:
    return record.get(ja_key) or record.get(en_key) or ""


def enrichment_value(enrichment: dict, lang: str, base_key: str) -> str:
    if not enrichment:
      return ""
    suffix = "En" if lang == "en" else "Ja"
    fallback_suffix = "Ja" if lang == "en" else "En"
    return enrichment.get(f"{base_key}{suffix}") or enrichment.get(f"{base_key}{fallback_suffix}") or ""


def get_enrichment(enrichments: dict, photographer: dict) -> dict:
    return enrichments.get(photographer.get("id"), {}) if enrichments else {}


def build_alias_targets(photographers: list[dict], alias_map: dict[str, str]):
    photographer_lookup = {p["id"]: p for p in photographers}
    aliases: dict[str, dict] = {}

    def remember(alias: str, photographer: dict | None):
        if not alias or not photographer:
            return
        aliases.setdefault(alias, photographer)

    for photographer in photographers:
        remember(photographer.get("nameJa"), photographer)
        remember(photographer.get("name"), photographer)

    for alias, photographer_id in alias_map.items():
        remember(alias, photographer_lookup.get(photographer_id))

    targets = sorted(aliases.items(), key=lambda item: len(item[0]), reverse=True)
    regex = re.compile("|".join(re.escape(alias) for alias, _ in targets)) if targets else None
    return {alias: photographer for alias, photographer in targets}, regex


def build_works_targets(essay_overrides: dict) -> tuple[dict[str, str], "re.Pattern | None"]:
    works_lookup: dict[str, str] = {}
    for entry in essay_overrides.values():
        if not isinstance(entry, dict):
            continue
        for work in entry.get("works") or []:
            url = work.get("url", "")
            if not url:
                continue
            for key in ("titleJa", "titleEn"):
                title = work.get(key, "")
                if title:
                    works_lookup[title] = url
    if not works_lookup:
        return {}, None
    pattern = "|".join(re.escape(t) for t in sorted(works_lookup, key=len, reverse=True))
    return works_lookup, re.compile(pattern)


def should_skip_alias_boundary(source: str, start: int, end: int, alias: str) -> bool:
    if not ALNUM_BOUNDARY_RE.search(alias or ""):
        return False
    prev_char = source[start - 1] if start > 0 else ""
    next_char = source[end] if end < len(source) else ""
    return bool(ALNUM_BOUNDARY_RE.search(prev_char) or ALNUM_BOUNDARY_RE.search(next_char))


def render_linked_text(
    text: str,
    lang: str,
    alias_lookup: dict[str, dict],
    regex: re.Pattern | None,
    exclude_id: str | None = None,
    linked_ids: set[str] | None = None,
    works_lookup: dict[str, str] | None = None,
    works_regex: "re.Pattern | None" = None,
) -> str:
    if not text:
        return ""
    if regex is None and works_regex is None:
        return escape_html(text).replace("\n", "<br>")

    linked_ids = linked_ids or set()

    all_matches: list[tuple[str, re.Match]] = []
    if regex:
        for m in regex.finditer(text):
            all_matches.append(("photographer", m))
    if works_regex and works_lookup:
        for m in works_regex.finditer(text):
            all_matches.append(("work", m))
    all_matches.sort(key=lambda x: (x[1].start(), -len(x[1].group(0))))

    parts: list[str] = []
    cursor = 0
    for match_type, match in all_matches:
        start, end = match.span()
        if start < cursor:
            continue
        token = match.group(0)
        if match_type == "photographer":
            photographer = alias_lookup.get(token)
            photographer_id = photographer["id"] if photographer else None
            if (
                not photographer
                or photographer_id == exclude_id
                or photographer_id in linked_ids
                or should_skip_alias_boundary(text, start, end, token)
            ):
                continue
            parts.append(escape_html(text[cursor:start]))
            parts.append(
                f'<a class="inline-photographer-link" href="{photographer_page_path(photographer, lang)}">{escape_html(token)}</a>'
            )
            cursor = end
            linked_ids.add(photographer_id)
        else:
            url = works_lookup.get(token, "")
            if not url:
                continue
            parts.append(escape_html(text[cursor:start]))
            parts.append(
                f'<a class="inline-work-link" href="{escape_html(url)}" target="_blank" rel="noopener">{escape_html(token)}</a>'
            )
            cursor = end
    parts.append(escape_html(text[cursor:]))
    return "".join(parts).replace("\n", "<br>")


def _render_cited_segment(text: str, lang: str, alias_lookup: dict[str, dict], regex: re.Pattern | None, exclude_id: str, linked_ids: set[str], works_lookup: dict[str, str] | None = None, works_regex: "re.Pattern | None" = None) -> str:
    chunks: list[str] = []
    for part in re.split(r"(\*\d+)", text or ""):
        cite = re.fullmatch(r"\*(\d+)", part or "")
        if cite:
            num = cite.group(1)
            chunks.append(f'<sup class="sup-ref"><a href="#cite-{num}">*{num}</a></sup>')
        else:
            chunks.append(render_linked_text(part, lang, alias_lookup, regex, exclude_id=exclude_id, linked_ids=linked_ids, works_lookup=works_lookup, works_regex=works_regex))
    return "".join(chunks)


def render_cited_text(text: str, lang: str, alias_lookup: dict[str, dict], regex: re.Pattern | None, exclude_id: str, works_lookup: dict[str, str] | None = None, works_regex: "re.Pattern | None" = None) -> str:
    return _render_cited_segment(text, lang, alias_lookup, regex, exclude_id, set(), works_lookup=works_lookup, works_regex=works_regex)


ESSAY_HEADING_SET = {
    '経歴',
    '表現解説',
    '批評と受容',
    'Biography',
    'How the Zone System relates to Group f/64',
    'Expression / method',
    'Seascapes, Theaters, Dioramas, and the Photograph as Time',
    'Group f/64, Straight Photography, and the Matter of Form',
    'New Objectivity and Neues Sehen: The Photography of Things',
    'FSA, American Photographs, and Documentary Style',
    'Untitled Film Stills, Staged Photography, and the Pictures Generation',
    'Vogue, Studio Portraits, Still Life, and the Print',
    'Criticism and reception',
}


def render_override_essay_html(text: str, lang: str, alias_lookup: dict[str, dict], regex: re.Pattern | None, exclude_id: str, works_lookup: dict[str, str] | None = None, works_regex: "re.Pattern | None" = None) -> str:
    if not text:
        return ""
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    linked_ids: set[str] = set()
    parts: list[str] = []
    for block in blocks:
        if block in ESSAY_HEADING_SET:
            parts.append(f"<h3>{escape_html(block)}</h3>")
        elif len(block) <= 80 and not re.search(r"\*\d+", block) and not re.search(r"[。！？.!?]$", block):
            parts.append(f"<h4>{escape_html(block)}</h4>")
        else:
            parts.append(f"<p>{_render_cited_segment(block, lang, alias_lookup, regex, exclude_id, linked_ids, works_lookup=works_lookup, works_regex=works_regex)}</p>")
    return "".join(parts)


def render_override_sections_html(sections, lang: str, alias_lookup: dict[str, dict], regex: re.Pattern | None, exclude_id: str, works_lookup: dict[str, str] | None = None, works_regex: "re.Pattern | None" = None) -> str:
    if not isinstance(sections, list):
        return ""
    heading_key = "headingEn" if lang == "en" else "headingJa"
    heading_fallback_key = "headingJa" if lang == "en" else "headingEn"
    paragraphs_key = "paragraphsEn" if lang == "en" else "paragraphsJa"
    paragraphs_fallback_key = "paragraphsJa" if lang == "en" else "paragraphsEn"
    linked_ids: set[str] = set()
    parts: list[str] = []
    for section in sections:
        if not isinstance(section, dict):
            continue
        heading = section.get(heading_key) or section.get(heading_fallback_key) or ""
        paragraphs = section.get(paragraphs_key) or section.get(paragraphs_fallback_key) or []
        if heading:
            parts.append(f"<h3>{escape_html(heading)}</h3>")
        for paragraph in paragraphs:
            if not paragraph:
                continue
            parts.append(f"<p>{_render_cited_segment(paragraph, lang, alias_lookup, regex, exclude_id, linked_ids, works_lookup=works_lookup, works_regex=works_regex)}</p>")
    return "".join(parts)


def render_manual_sectioned_essay_html(
    photographer_id: str,
    text: str,
    lang: str,
    alias_lookup: dict[str, dict],
    regex: re.Pattern | None,
    works_lookup: dict[str, str] | None = None,
    works_regex: "re.Pattern | None" = None,
) -> str:
    """Preserve curated h2-level structure for legacy one-block essays."""
    rules = {
        ("stieglitz", "ja"): [
            ("表現解説", None, "写真が純粋に抽象的"),
            ("批評と受容", "写真が純粋に抽象的", None),
        ],
        ("stieglitz", "en"): [
            ("Expression / method", None, "These pictures were among"),
            ("Criticism and reception", "These pictures were among", None),
        ],
        ("cameron", "ja"): [
            ("経歴", None, "湿板コロジオン法は"),
            ("表現解説", "湿板コロジオン法は", None),
        ],
        ("cameron", "en"): [
            ("Biography", None, "The wet-collodion process"),
            ("Analysis of Expression", "The wet-collodion process", None),
        ],
    }
    section_rules = rules.get((photographer_id, lang))
    if not section_rules or not text:
        return ""

    linked_ids: set[str] = set()
    parts: list[str] = []
    for heading, start_marker, end_marker in section_rules:
        start = text.find(start_marker) if start_marker else 0
        if start < 0:
            return ""
        end = text.find(end_marker, start) if end_marker else len(text)
        if end < 0:
            return ""
        segment = text[start:end].strip()
        if not segment:
            continue
        paragraphs = [block.strip() for block in re.split(r"\n\s*\n", segment) if block.strip()]
        parts.append(f"<h3>{escape_html(heading)}</h3>")
        for paragraph in paragraphs:
            parts.append(f"<p>{_render_cited_segment(paragraph, lang, alias_lookup, regex, photographer_id, linked_ids, works_lookup=works_lookup, works_regex=works_regex)}</p>")
    return "".join(parts)


def split_essay_into_sections(rendered_body: str, default_heading: str) -> str:
    if not rendered_body:
        return f"""      <section class="section">
        <h2>{escape_html(default_heading)}</h2>
        <div class="essay"></div>
      </section>"""

    tokens = re.split(r"(<h3>.*?</h3>)", rendered_body)
    sections: list[tuple[str, list[str]]] = []
    current_heading = default_heading
    current_parts: list[str] = []
    saw_heading = False

    for token in tokens:
        if not token:
            continue
        heading_match = re.fullmatch(r"<h3>(.*?)</h3>", token)
        if heading_match:
            if current_parts or not saw_heading:
                if current_parts:
                    sections.append((current_heading, current_parts))
            current_heading = strip_tags(heading_match.group(1))
            current_parts = []
            saw_heading = True
            continue
        current_parts.append(token)

    if current_parts:
        sections.append((current_heading, current_parts))

    if not saw_heading:
        sections = [(default_heading, [rendered_body])]

    rendered_sections = []
    for heading, parts in sections:
        body = "".join(parts)
        rendered_sections.append(f"""      <section class="section">
        <h2>{escape_html(heading)}</h2>
        <div class="essay">{body}</div>
      </section>""")
    return "\n".join(rendered_sections)


def collect_text_and_citations(photographer: dict, lang: str):
    context = photographer.get("context") or {}
    expression = photographer.get("expression") or {}
    text = context.get("textEn" if lang == "en" else "text") or context.get("text" if lang == "en" else "textEn") or ""
    citations = context.get("citations") if isinstance(context.get("citations"), list) else None
    if citations is not None:
        return text, citations

    exp_text = expression.get("textEn" if lang == "en" else "text") or expression.get("text" if lang == "en" else "textEn") or ""
    combined = exp_text + ("\n\n" if exp_text and text else "") + text
    sources = []
    seen = set()
    for src in (expression.get("sources") or []) + (context.get("sources") or []):
        url = src.get("url")
        label = src.get("text") or src.get("name") or url or ""
        if url and url not in seen:
            seen.add(url)
            sources.append({"num": len(sources) + 1, "name": label, "url": url})
    return combined, sources


def override_text_and_citations(override, lang: str):
    if not isinstance(override, dict):
        return "", None
    text_key = "textEn" if lang == "en" else "textJa"
    fallback_key = "textJa" if lang == "en" else "textEn"
    text = override.get(text_key) or override.get(fallback_key) or ""
    if not text and isinstance(override.get("sections"), list):
        parts = []
        heading_key = "headingEn" if lang == "en" else "headingJa"
        heading_fallback_key = "headingJa" if lang == "en" else "headingEn"
        paragraphs_key = "paragraphsEn" if lang == "en" else "paragraphsJa"
        paragraphs_fallback_key = "paragraphsJa" if lang == "en" else "paragraphsEn"
        for section in override.get("sections") or []:
            if not isinstance(section, dict):
                continue
            heading = section.get(heading_key) or section.get(heading_fallback_key)
            paragraphs = section.get(paragraphs_key) or section.get(paragraphs_fallback_key) or []
            if heading:
                parts.append(heading)
            parts.extend(paragraph for paragraph in paragraphs if paragraph)
        text = "\n\n".join(parts)
    citations = override.get("citations") if isinstance(override.get("citations"), list) else None
    return text, citations


def override_lead(override, lang: str) -> str:
    if not isinstance(override, dict):
        return ""
    lead_key = "leadEn" if lang == "en" else "leadJa"
    fallback_key = "leadJa" if lang == "en" else "leadEn"
    lead = override.get(lead_key) or override.get(fallback_key) or ""
    return normalize_space(re.sub(r"\*\d+", "", lead))


def override_lead_raw(override, lang: str) -> str:
    if not isinstance(override, dict):
        return ""
    lead_key = "leadEn" if lang == "en" else "leadJa"
    fallback_key = "leadJa" if lang == "en" else "leadEn"
    lead = override.get(lead_key) or override.get(fallback_key) or ""
    return normalize_space(lead)


def override_rendered_sections_html(override, lang: str) -> str:
    if not isinstance(override, dict):
        return ""
    html_key = "renderedSectionsHtmlEn" if lang == "en" else "renderedSectionsHtmlJa"
    fallback_key = "renderedSectionsHtmlJa" if lang == "en" else "renderedSectionsHtmlEn"
    return (override.get(html_key) or override.get(fallback_key) or "").strip()


def display_name(photographer: dict, lang: str) -> str:
    if lang == "en":
        return photographer.get("name") or photographer.get("nameJa") or ""
    return photographer.get("nameJa") or photographer.get("name") or ""


def display_alt_name(photographer: dict, lang: str) -> str:
    if lang == "en":
        return ""
    return photographer.get("name") or ""


def display_years(photographer: dict, lang: str) -> str:
    raw = normalize_space(photographer.get("years") or "—")
    if lang == "en":
        if " / " in raw:
            raw = raw.split(" / ", 1)[0].strip()
        raw = raw.replace("明治期", "Meiji period")
        raw = raw.replace("年代", "s")
    return raw.replace("-", "–")


def display_country(photographer: dict, lang: str) -> str:
    nationality = photographer.get("nationality") or ""
    return country_entry(nationality).get(lang) or nationality or "—"


def localized_movement_names(photographer: dict, lang: str, movements_meta: dict) -> list[str]:
    names = []
    for movement in photographer.get("movements") or []:
        meta = movements_meta.get(movement, {})
        names.append(meta.get("en", movement) if lang == "en" else movement)
    return names


def expanded_movement_names(photographer: dict, lang: str, movements_meta: dict, enrichments: dict, limit: int = 5) -> list[str]:
    enrichment = get_enrichment(enrichments, photographer)
    items = list(photographer.get("movements") or [])
    for movement in enrichment.get("extraMovements") or []:
        if movement and movement not in items:
            items.append(movement)
    localized = []
    for movement in items:
        localized.append(english_movement_name(movement, movements_meta) if lang == "en" else movement)
    return localized[:limit]


def join_list(items: list[str], lang: str) -> str:
    values = [item for item in items if item]
    if not values:
        return ""
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return f"{values[0]} and {values[1]}" if lang == "en" else f"{values[0]}と{values[1]}"
    if lang == "en":
        return ", ".join(values[:-1]) + f", and {values[-1]}"
    return "、".join(values[:-1]) + f"、{values[-1]}"


def era_period(photographer: dict, era_lookup: dict) -> str:
    era = era_lookup.get(photographer.get("era"), {})
    return era.get("period") or photographer.get("years") or "—"


def is_placeholder_text(text: str, lang: str) -> bool:
    value = normalize_space(strip_cite_markers(text))
    return value in {"準備中。", "Coming soon."}


def descriptor_for(photographer: dict, lang: str, era_lookup: dict, movements_meta: dict, enrichments: dict) -> str:
    enrichment = get_enrichment(enrichments, photographer)
    descriptor = enrichment_value(enrichment, lang, "descriptor")
    if descriptor:
        return descriptor
    movement_names = expanded_movement_names(photographer, lang, movements_meta, enrichments, limit=1)
    if movement_names:
        return movement_names[0]
    era = era_lookup.get(photographer.get("era"), {})
    return (era.get("titleEn") if lang == "en" else era.get("title")) or era.get("period") or ""


def build_keyword_line(photographer: dict, lang: str, era_lookup: dict, movements_meta: dict, enrichments: dict) -> str:
    if photographer.get("id") == "ansel-adams" and lang == "en":
        return "Ansel Adams | Zone System, Group f/64, and Print as Performance | Photo Coordinates |"
    name = display_name(photographer, lang)
    descriptor = descriptor_for(photographer, lang, era_lookup, movements_meta, enrichments)
    history_label = "History of Photography" if lang == "en" else "写真史"
    site_label = "Photo Coordinates" if lang == "en" else "写真の座標"
    parts = [name, history_label]
    if descriptor:
        parts.append(descriptor)
    parts.append(site_label)
    return "｜".join(parts) + "｜" if lang == "ja" else " | ".join(parts) + " |"


def build_keyword_line_html(photographer: dict, lang: str, era_lookup: dict, movements_meta: dict, enrichments: dict) -> str:
    if photographer.get("id") == "ansel-adams" and lang == "en":
        return 'Ansel Adams | Zone System, Group f/64, and Print as Performance | <a href="/en/">Photo Coordinates</a> |'
    name = display_name(photographer, lang)
    descriptor = descriptor_for(photographer, lang, era_lookup, movements_meta, enrichments)
    history_label = "History of Photography" if lang == "en" else "写真史"
    site_label = "Photo Coordinates" if lang == "en" else "写真の座標"
    site_href = "/en/" if lang == "en" else "/"
    parts = [escape_html(name), escape_html(history_label)]
    if descriptor:
        parts.append(escape_html(descriptor))
    parts.append(f'<a href="{site_href}">{escape_html(site_label)}</a>')
    separator = " | " if lang == "en" else "｜"
    return separator.join(parts) + separator


def books_heading(photographer: dict, lang: str) -> str:
    name = display_name(photographer, lang)
    if lang == "en":
        return f"{name} Photobooks"
    return f"{name} 写真集"


def extra_intro_phrase(photographer: dict, lang: str, movements_meta: dict, enrichments: dict) -> str:
    enrichment = get_enrichment(enrichments, photographer)
    keywords = enrichment_value(enrichment, lang, "keywords")
    representative_work = enrichment_value(enrichment, lang, "representativeWork")
    movement_names = expanded_movement_names(photographer, lang, movements_meta, enrichments, limit=3)
    movement_phrase = join_list(movement_names[:2], lang)

    if lang == "en":
        parts = []
        if keywords:
            parts.append(f"It is often discussed through {keywords}.")
        elif movement_phrase:
            parts.append(f"It is frequently read through {movement_phrase}.")
        if representative_work:
            parts.append(f"A representative work is {representative_work}.")
        return " ".join(parts)

    parts = []
    if keywords:
        parts.append(f"{keywords}といった語でもよく検索される。")
    elif movement_phrase:
        parts.append(f"{movement_phrase}の文脈からもたどりやすい。")
    if representative_work:
        parts.append(f"代表作には{representative_work}がある。")
    return "".join(parts)


def build_focus_phrase(photographer: dict, lang: str, movements_meta: dict, enrichments: dict) -> str:
    enrichment = get_enrichment(enrichments, photographer)
    keywords = enrichment_value(enrichment, lang, "keywords")
    representative_work = enrichment_value(enrichment, lang, "representativeWork")
    movement_names = expanded_movement_names(photographer, lang, movements_meta, enrichments, limit=3)
    movement_phrase = join_list(movement_names[:2], lang)

    if lang == "en":
        if keywords and representative_work:
            return f"{keywords}, and the representative work {representative_work}"
        if keywords:
            return keywords
        if representative_work:
            return f"the representative work {representative_work}"
        if movement_phrase:
            return movement_phrase
        return "key works and related movements"

    if keywords and representative_work:
        return f"{keywords}、代表作の{representative_work}"
    if keywords:
        return keywords
    if representative_work:
        return f"代表作の{representative_work}"
    if movement_phrase:
        return movement_phrase
    return "関連作家や主要な作品"


def essay_mentions_name(text: str, names: list[str]) -> bool:
    plain = normalize_space(strip_tags(strip_cite_markers(text or "")))
    return any(name and name in plain for name in names)


def build_intro(photographer: dict, lang: str, era_lookup: dict, movements_meta: dict, enrichments: dict) -> str:
    name_primary = display_name(photographer, lang)
    name_secondary = display_alt_name(photographer, lang)
    period = era_period(photographer, era_lookup)
    movement_names = expanded_movement_names(photographer, lang, movements_meta, enrichments, limit=5)
    movement_phrase = join_list(movement_names[:2], lang)
    country = display_country(photographer, lang)
    essay_text, _ = collect_text_and_citations(photographer, lang)
    placeholder = is_placeholder_text(essay_text, lang)
    focus_phrase = build_focus_phrase(photographer, lang, movements_meta, enrichments)

    if photographer.get("id") == "stieglitz":
        if lang == "en":
            return "A central figure in the shift from Pictorialism to modern photography, traced through 291, Photo-Secession, and Equivalents."
        return "291と写真分離派、《エクイヴァレンツ》を手がかりに、ピクトリアリズムから近代写真への転換をたどる重要作家。"

    if lang == "en":
        identity = name_primary if not name_secondary else f"{name_primary} ({name_secondary})"
        if placeholder:
            if movement_phrase:
                base = f"{identity} is part of Photo Coordinates, a history of photography site. This page will be expanded around {movement_phrase} and the wider photographic context of {period}."
            else:
                base = f"{identity} is part of Photo Coordinates, a history of photography site. This page will be expanded with historical context, related photographers, and sources."
            return normalize_space(base)
        if movement_phrase:
            base = f"{identity} is a key figure for understanding the history of photography around {movement_phrase}. This page follows the photographer's place in photography history through {focus_phrase}, related photographers, movements, and sources."
        else:
            base = f"{identity} appears here as part of Photo Coordinates, a site about the history of photography. This page follows the photographer through {focus_phrase}, related figures, and key sources."
        return normalize_space(base)

    identity = name_primary if not name_secondary else f"{name_primary}（{name_secondary}）"
    if placeholder:
        if movement_phrase:
            base = f"{identity}を写真史の流れの中で読むための準備ページです。{movement_phrase}や{period}の文脈とあわせて、関連作家・出典を順次追加していきます。"
        else:
            base = f"{identity}を写真史の中で位置づけるための準備ページです。写真の座標では、関連作家・時代背景・出典を今後順次整えていきます。"
        return normalize_space(base)
    if movement_phrase:
        base = f"{identity}は、{movement_phrase}を考えるうえで欠かせない写真家です。このページでは、{focus_phrase}を手がかりに、写真史の流れの中での位置づけを、関連作家・運動・出典とあわせてたどります。"
        return normalize_space(base)
    if country != "—":
        base = f"{identity}は、{country}の写真史を考えるうえで重要な写真家です。このページでは、{focus_phrase}を手がかりに、写真の座標の中での位置づけを、関連作家・出典とともに読み解きます。"
        return normalize_space(base)
    base = f"{identity}を写真史の流れの中で読み解くためのページです。このページでは、{focus_phrase}を手がかりに、関連作家や出典とともにその位置づけをたどります。"
    return normalize_space(base)


def build_description(photographer: dict, lang: str, era_lookup: dict, movements_meta: dict, enrichments: dict) -> str:
    name = display_name(photographer, lang)
    themes = photographer_meta_themes(photographer, lang, era_lookup, movements_meta, enrichments, limit=4)
    if lang == "en":
        theme_text = join_list(themes, lang) if themes else "photographic method, historical context, and critical reception"
        return normalize_space(
            f"Using museum, archive, and specialist sources, this page examines {name} through {theme_text}."
        )
    theme_text = "、".join(themes) if themes else "写真表現、時代背景、写真史上の位置づけ"
    return normalize_space(
        f"美術館・アーカイブ資料を手がかりに、{name}の{theme_text}を読み解く写真史解説。"
    )


def build_title(photographer: dict, lang: str, era_lookup: dict, movements_meta: dict, enrichments: dict) -> str:
    name_primary = display_name(photographer, lang)
    site = "Photo Coordinates" if lang == "en" else "写真の座標"
    themes = photographer_meta_themes(photographer, lang, era_lookup, movements_meta, enrichments, limit=2)
    if themes:
        theme_text = join_list(themes, lang)
        separator = " | " if lang == "en" else "｜"
        return f"{name_primary}{separator}{theme_text}{separator}{site}"
    if lang == "en":
        movement_names = expanded_movement_names(photographer, lang, movements_meta, enrichments, limit=1)
        movement = movement_names[0] if movement_names else ""
        country = country_entry(photographer.get("nationality") or "").get("en") or ""
        country_adj = COUNTRY_ADJECTIVES_EN.get(country, country)
        candidates = []
        if movement:
            candidates.append(f"{name_primary}: {movement} | {site}")
            candidates.append(f"{name_primary}: {movement} Photographer | {site}")
        if movement and country_adj:
            candidates.append(f"{name_primary}: {movement}, {country_adj} Photography | {site}")
        if country_adj:
            candidates.append(f"{name_primary} and {country_adj} Photography | {site}")
        role = extract_title_role(photographer, lang, era_lookup, movements_meta, enrichments)
        candidates.append(f"{name_primary}: {role} | {site}")
        for candidate in candidates:
            if len(candidate) <= 65:
                return candidate
        return f"{name_primary} | {site}"

    role = extract_title_role(photographer, lang, era_lookup, movements_meta, enrichments)
    base = f"{name_primary} | {role} | {site}"
    max_length = 60
    if len(base) <= max_length:
        return base
    available = max(8, max_length - len(name_primary) - len(site) - 6)
    role = truncate_text(role, available).rstrip("。")
    return f"{name_primary} | {role} | {site}"


def photographer_meta_themes(photographer: dict, lang: str, era_lookup: dict, movements_meta: dict, enrichments: dict, limit: int = 4) -> list[str]:
    values: list[str] = []
    override = SEO_TEXT_OVERRIDES.get(photographer.get("id"), {}).get(lang, {})
    override_title = override.get("title") or ""
    if override_title:
        pieces = [normalize_space(piece) for piece in re.split(r"\s*[|｜]\s*", override_title) if normalize_space(piece)]
        site = "Photo Coordinates" if lang == "en" else "写真の座標"
        name = display_name(photographer, lang)
        for piece in pieces:
            if piece in {site, name}:
                continue
            if lang == "en":
                split_pieces = re.split(r"\s+and\s+|,\s*", piece)
            else:
                split_pieces = re.split(r"と|、", piece)
            for value in split_pieces:
                value = normalize_space(value)
                if value and value not in values:
                    values.append(value)

    for movement in expanded_movement_names(photographer, lang, movements_meta, enrichments, limit=3):
        if movement and movement not in values:
            values.append(movement)

    descriptor = descriptor_for(photographer, lang, era_lookup, movements_meta, enrichments)
    descriptor = normalize_space(descriptor)
    if descriptor and not meta_theme_is_role_label(descriptor, lang) and descriptor not in values:
        values.append(descriptor)

    role = extract_title_role(photographer, lang, era_lookup, movements_meta, enrichments)
    role = normalize_space(role)
    if role and not meta_theme_is_role_label(role, lang) and role not in values:
        values.append(role)

    period = era_period(photographer, era_lookup)
    if period and period != "—" and period not in values and len(values) < 2:
        values.append(period)

    cleaned = []
    for value in values:
        value = clean_meta_theme(value, lang)
        if value and value not in cleaned:
            cleaned.append(value)
    return cleaned[:limit]


def meta_theme_is_role_label(value: str, lang: str) -> bool:
    text = normalize_space(value)
    if not text:
        return True
    if lang == "en":
        lower = text.lower()
        return lower in {"photographer", "an important photographer"} or lower.endswith(" photographer") or lower.startswith("an ") and " photographer" in lower
    return (
        "写真家" in text
        or "重要作家" in text
        or text.startswith("（")
        or text.startswith("(")
        or text in {"写真史", "Photo History"}
    )


def clean_meta_theme(value: str, lang: str) -> str:
    text = normalize_space(value)
    if lang == "en":
        text = re.sub(r"^(?:a|an)\\s+", "", text, flags=re.I)
        text = re.sub(r"\\s+[Pp]hotographer$", "", text)
        text = re.sub(r"^Pioneer of\\s+", "", text)
        return text.strip(" ,.")
    text = re.sub(r"の(?:重要作家|中心作家|写真家)$", "", text)
    text = re.sub(r"を記録した写真家$", "", text)
    text = re.sub(r"を撮り続けた写真家$", "", text)
    text = re.sub(r"を追った写真家$", "", text)
    text = re.sub(r"を築いた写真家$", "", text)
    text = re.sub(r"を代表する写真家$", "", text)
    return text.strip(" 、。")


def build_page_structured_data(photographer: dict, lang: str, title: str, description: str, canonical: str) -> str:
    birth_year, death_year = parse_years(photographer.get("years") or "")
    person_id = f"{canonical}#person"
    person = {
        "@type": "Person",
        "@id": person_id,
        "name": display_name(photographer, lang),
        "description": description,
        "url": canonical,
        "jobTitle": "Photographer" if lang == "en" else "写真家",
    }
    alternate_name = STRUCTURED_DATA_ALTERNATE_NAME_OVERRIDES.get(photographer.get("id"), {}).get(lang)
    if not alternate_name:
        alternate_name = display_alt_name(photographer, lang)
    if alternate_name:
        person["alternateName"] = alternate_name
    if birth_year:
        person["birthDate"] = birth_year
    if death_year:
        person["deathDate"] = death_year
    country_name = country_entry(photographer.get("nationality") or "").get("en")
    if country_name:
        person["nationality"] = {
            "@type": "Country",
            "name": country_name,
        }
    same_as = SAME_AS_OVERRIDES.get(photographer.get("id"))
    if same_as:
        person["sameAs"] = same_as
    person["subjectOf"] = {"@id": canonical}
    payload = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": canonical,
                "url": canonical,
                "name": title,
                "description": description,
                "inLanguage": lang,
                "isPartOf": {
                    "@type": "WebSite",
                    "name": "Photo Coordinates" if lang == "en" else "写真の座標",
                    "url": f"{SITE}/en/" if lang == "en" else f"{SITE}/",
                },
                "about": {"@id": person_id},
            },
            person,
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_breadcrumb_structured_data(photographer: dict, lang: str) -> str:
    if lang == "en":
        home_name = "Photo Coordinates"
        archive_name = "Photographers"
        home_url = f"{SITE}/en/"
        archive_url = f"{SITE}/en/archive.html"
    else:
        home_name = "写真の座標"
        archive_name = "写真家一覧"
        home_url = f"{SITE}/"
        archive_url = f"{SITE}/archive.html"
    payload = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": home_name,
                "item": home_url,
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": archive_name,
                "item": archive_url,
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": display_name(photographer, lang),
            },
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def related_photographers_for(target: dict, all_photographers: list[dict], era_index: dict, photographer_index: dict, limit: int = 5):
    candidates = []
    target_era_index = era_index.get(target.get("era"), 999)
    target_order_index = photographer_index.get(target.get("id"), 9999)
    target_movements = set(target.get("movements") or [])
    for candidate in all_photographers:
        if candidate["id"] == target["id"]:
            continue
        candidate_movements = set(candidate.get("movements") or [])
        shared = target_movements.intersection(candidate_movements)
        same_era = candidate.get("era") == target.get("era")
        same_country = bool(target.get("nationality")) and target.get("nationality") == candidate.get("nationality")
        if not shared and not same_era and not same_country:
            continue
        era_gap = abs(era_index.get(candidate.get("era"), 999) - target_era_index)
        order_gap = abs(photographer_index.get(candidate.get("id"), 9999) - target_order_index)
        score = len(shared) * 100
        score += 18 if same_era else max(0, 10 - era_gap * 3)
        score += 6 if same_country else 0
        score -= min(order_gap, 36)
        candidates.append((score, era_gap, order_gap, candidate))
    candidates.sort(key=lambda item: (-item[0], item[1], item[2], display_name(item[3], "ja")))
    return [item[3] for item in candidates[:limit]]


def person_link_url(person: dict, lang: str) -> str:
    if person.get("photographerId"):
        return photographer_page_path({"id": person["photographerId"]}, lang)
    return person.get("urlEn") if lang == "en" else (person.get("urlJa") or person.get("urlEn") or "")


def person_display_name(person: dict, lang: str) -> str:
    return (person.get("nameEn") if lang == "en" else person.get("nameJa")) or person.get("nameEn") or person.get("nameJa") or ""


def person_role(person: dict, lang: str) -> str:
    return (person.get("roleEn") if lang == "en" else person.get("roleJa")) or person.get("roleEn") or person.get("roleJa") or ("Photographer" if lang == "en" else "写真家")


def build_related_people_items(photographer: dict, lang: str, enrichments: dict, all_photographers: list[dict], era_index: dict, photographer_index: dict, essay_text: str) -> list[dict]:
    enrichment = get_enrichment(enrichments, photographer)
    items: list[dict] = []
    used = {photographer.get("id")}

    for person in (enrichment.get("relatedPeople") or [])[:2]:
        display = person_display_name(person, lang)
        alt_display = person_display_name(person, "ja" if lang == "en" else "en")
        items.append({
            "label": display,
            "url": person_link_url(person, lang),
            "role": person_role(person, lang),
            "show_role": not essay_mentions_name(essay_text, [display, alt_display]),
        })
        if person.get("photographerId"):
            used.add(person["photographerId"])

    for candidate in related_photographers_for(photographer, all_photographers, era_index, photographer_index, limit=8):
        if candidate["id"] in used:
            continue
        label = display_name(candidate, lang)
        alt_label = display_alt_name(candidate, lang)
        items.append({
            "label": label,
            "url": photographer_page_path(candidate, lang),
            "role": "Photographer" if lang == "en" else "写真家",
            "show_role": not essay_mentions_name(essay_text, [label, alt_label]),
        })
        used.add(candidate["id"])
        if len(items) >= 5:
            break

    return items[:5]


def normalized_photographer(
    photographer: dict,
    *,
    enrichments: dict,
    country_overrides: dict,
    essay_overrides: dict,
) -> dict:
    item = dict(photographer)
    enrichment = get_enrichment(enrichments, photographer)
    country_override = country_overrides.get(photographer.get("id"), {}) if country_overrides else {}
    country_code = (
        enrichment.get("countryCode")
        or enrichment.get("nationality")
        or country_override.get("countryCode")
        or country_override.get("nationality")
        or item.get("nationality")
        or ""
    )
    if country_code:
        item["nationality"] = country_code
    item_id = item.get("id") or ""
    has_activity_years = raw_years_is_activity_period(item.get("years") or "")
    if item_id in YEAR_OVERRIDES:
        item["years"] = YEAR_OVERRIDES[item_id]
    elif has_activity_years or not parse_years(item.get("years") or "")[0]:
        override = essay_overrides.get(item.get("id"), {}) if essay_overrides else {}
        candidate_text = "\n".join(
            str(value or "")
            for value in (
                override.get("leadJa"),
                override.get("leadEn"),
                override.get("textJa"),
                override.get("textEn"),
            )
            if value
        )
        inferred = infer_years_from_text(candidate_text)
        if inferred:
            item["years"] = inferred
        elif has_activity_years:
            item["years"] = ""
    return item


def render_related_people_html(items: list[dict], placeholder: str) -> str:
    if not items:
        return f'<div class="note">{placeholder}</div>'
    rendered = []
    for item in items:
        role_html = f'<div class="related-person-role">{escape_html(item["role"])}</div>' if item.get("show_role") else ""
        label_html = escape_html(item["label"])
        if item.get("url"):
            extra_attrs = ' target="_blank" rel="noopener"' if item["url"].startswith("http") else ""
            label_html = f'<a class="related-person-link" href="{escape_html(item["url"])}"{extra_attrs}>{label_html}</a>'
        else:
            label_html = f'<span class="related-person-label">{label_html}</span>'
        rendered.append(f'<div class="related-person-card">{role_html}{label_html}</div>')
    return "".join(rendered)


COPY = {
    "ja": {
        "site": "写真の座標",
        "label": "Photo Coordinates / Photographer",
        "archive": "年代順で見る",
        "coordinates": "座標で見る",
        "home": "トップへ戻る",
        "menu": "メニュー",
        "essay": "解説",
        "movements": "関連する運動",
        "relatedPeople": "関連する写真家・人物",
        "relatedPeoplePlaceholder": "関連する写真家・人物は準備中です。",
        "links": "外部リンク",
        "works": "関連作品",
        "worksPlaceholder": "",
        "books": "写真集",
        "amazonCta": "写真集を Amazon で見る ↗",
        "affiliateDisclosure": "※アフィリエイトリンクを含みます",
        "sources": "出典",
        "placeholder": "解説準備中。",
        "movementPlaceholder": "関連運動は準備中です。",
        "linksPlaceholder": "外部リンクは準備中です。",
        "booksPlaceholder": "写真集は準備中です。",
        "sourcesPlaceholder": "出典は準備中です。",
        "country": "国",
        "era": "年代",
        "langJa": "Japanese",
        "langEn": "English",
        "footerLine1": "本サイトは公開資料をもとに、写真家・運動・時代背景の関係を編集・整理する写真史プロジェクトです。",
        "footerLine2": "資料収集と整理にはAIも補助的に用い、出典を確認しながら更新しています。",
        "privacy": "プライバシーポリシー",
    },
    "en": {
        "site": "Photo Coordinates",
        "label": "Photo Coordinates / Photographer",
        "archive": "Browse by Era",
        "coordinates": "View in Coordinates",
        "home": "Back to Home",
        "menu": "Menu",
        "essay": "Essay",
        "movements": "Related movements",
        "relatedPeople": "Related photographers & figures",
        "relatedPeoplePlaceholder": "Related photographers and figures coming soon.",
        "links": "External links",
        "works": "Notable works",
        "worksPlaceholder": "",
        "books": "Photobooks",
        "amazonCta": "View on Amazon ↗",
        "affiliateDisclosure": "Includes affiliate links",
        "sources": "Sources",
        "placeholder": "Coming soon.",
        "movementPlaceholder": "Related movements coming soon.",
        "linksPlaceholder": "External links coming soon.",
        "booksPlaceholder": "Photobooks coming soon.",
        "sourcesPlaceholder": "Sources coming soon.",
        "country": "Country",
        "era": "Era",
        "langJa": "Japanese",
        "langEn": "English",
        "footerLine1": "This site is an editorial photography-history project that organizes photographers, movements, and historical context from public sources.",
        "footerLine2": "AI is used as an assistance tool for collecting and arranging sources, while citations are checked and updated over time.",
        "privacy": "Privacy Policy",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate photographer detail pages.")
    parser.add_argument(
        "--only",
        nargs="+",
        default=[],
        metavar="PHOTOGRAPHER_ID",
        help="Generate only the listed photographer IDs without rewriting every detail page.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    only_ids = set(args.only)
    all_photographers = eval_js(
        [
            "data/photographers.js",
            "data/photographers-manual-additions.js",
            "data/photographers-supplement.js",
        ],
        "PHOTOGRAPHERS",
    )
    photographers = [p for p in all_photographers if p["id"] not in NON_PHOTOGRAPHER_IDS]
    if only_ids:
        available_ids = {p["id"] for p in photographers}
        missing_ids = sorted(only_ids - available_ids)
        if missing_ids:
            raise SystemExit(f"Unknown or excluded photographer ID(s): {', '.join(missing_ids)}")
        target_photographers = [p for p in photographers if p["id"] in only_ids]
    else:
        target_photographers = photographers
    alias_map = eval_js(
        [
            "data/photographers.js",
            "data/photographers-manual-additions.js",
            "data/photographers-supplement.js",
        ],
        'typeof PHOTOGRAPHER_LINK_ALIASES !== "undefined" ? PHOTOGRAPHER_LINK_ALIASES : {}',
    )
    movements_meta = eval_js(["data/movements.js"], "MOVEMENTS_META")
    movement_taxonomy = eval_js(["data/movements.js"], "MOVEMENT_TAXONOMY")
    taxonomy_meta.configure_movement_taxonomy(movement_taxonomy)
    enrichments = eval_js(["data/photographer-enrichments.js"], 'typeof PHOTOGRAPHER_ENRICHMENTS !== "undefined" ? PHOTOGRAPHER_ENRICHMENTS : {}')
    affiliate_books = load_affiliate_books()
    essay_overrides = load_essay_overrides()
    country_overrides = taxonomy_meta.eval_site_js_object("PHOTOGRAPHER_COUNTRY_OVERRIDES")
    photographers = [
        normalized_photographer(
            photographer,
            enrichments=enrichments,
            country_overrides=country_overrides,
            essay_overrides=essay_overrides,
        )
        for photographer in photographers
    ]
    if only_ids:
        target_photographers = [p for p in photographers if p["id"] in only_ids]
    else:
        target_photographers = photographers
    eras = eval_js(
        [
            "data/eras.js",
            "data/content-helpers.js",
            "data/future/era-1990s.js",
            "data/future/era-2000s.js",
            "data/future/era-2010s.js",
        ],
        "ERAS",
    )
    era_lookup = {era["id"]: era for era in eras}
    era_index = {era["id"]: idx for idx, era in enumerate(eras)}
    photographer_index = {p["id"]: idx for idx, p in enumerate(photographers)}
    alias_lookup, alias_regex = build_alias_targets(photographers, alias_map)
    works_lookup, works_regex = build_works_targets(essay_overrides)
    all_nationalities = sorted(
        [nationality for nationality in {p.get("nationality") for p in photographers if p.get("nationality")} if country_entry(nationality).get("slug")],
        key=lambda nationality: country_entry(nationality).get("ja", nationality),
    )
    all_movements = sorted(
        {movement for photographer in photographers for movement in (photographer.get("movements") or []) if movement},
        key=lambda movement: english_movement_name(movement, movements_meta).lower(),
    )

    report_rows = []

    for lang in ("ja", "en"):
        out_dir = REPO / ("en/photographers" if lang == "en" else "photographers")
        out_dir.mkdir(parents=True, exist_ok=True)
        if not only_ids:
            for excluded_id in NON_PHOTOGRAPHER_IDS:
                excluded_file = out_dir / f"{excluded_id}.html"
                if excluded_file.exists():
                    excluded_file.unlink()
        copy = COPY[lang]

        for photographer in target_photographers:
            override_entry = essay_overrides.get(photographer["id"])
            override_body_text, override_citations = override_text_and_citations(override_entry, lang)
            body_text, citations = collect_text_and_citations(photographer, lang)
            override_sections = override_entry.get("sections") if isinstance(override_entry, dict) else None
            override_sections_html = override_rendered_sections_html(override_entry, lang)
            if override_body_text:
                body_text = override_body_text
                citations = override_citations or citations
            elif override_sections_html and override_citations:
                citations = override_citations or citations
            if isinstance(override_sections, list) and override_sections:
                rendered_body = render_override_sections_html(override_sections, lang, alias_lookup, alias_regex, photographer["id"], works_lookup=works_lookup, works_regex=works_regex)
            elif override_body_text:
                rendered_body = render_override_essay_html(override_body_text, lang, alias_lookup, alias_regex, photographer["id"], works_lookup=works_lookup, works_regex=works_regex)
            elif body_text and photographer["id"] in {"stieglitz", "cameron"}:
                rendered_body = render_manual_sectioned_essay_html(photographer["id"], body_text, lang, alias_lookup, alias_regex, works_lookup=works_lookup, works_regex=works_regex) or render_override_essay_html(body_text, lang, alias_lookup, alias_regex, photographer["id"], works_lookup=works_lookup, works_regex=works_regex)
            elif body_text:
                rendered_body = render_override_essay_html(body_text, lang, alias_lookup, alias_regex, photographer["id"], works_lookup=works_lookup, works_regex=works_regex)
            else:
                rendered_body = f"<p>{escape_html(copy['placeholder'])}</p>"
            is_placeholder_page = is_placeholder_text(body_text, lang)
            description = build_description(photographer, lang, era_lookup, movements_meta, enrichments)
            title = build_title(photographer, lang, era_lookup, movements_meta, enrichments)
            intro = build_intro(photographer, lang, era_lookup, movements_meta, enrichments)
            seo_override = SEO_TEXT_OVERRIDES.get(photographer["id"], {}).get(lang, {})
            if seo_override:
                intro = seo_override.get("lead") or intro
                description = seo_override.get("description") or description
                title = seo_override.get("title") or title
            intro = override_lead(override_entry, lang) or intro
            lead_raw = override_lead_raw(override_entry, lang)
            if lead_raw:
                lead_html = _render_cited_segment(lead_raw, lang, alias_lookup, alias_regex, photographer["id"], set(), works_lookup=works_lookup, works_regex=works_regex)
            else:
                lead_html = escape_html(intro)
            keyword_line = build_keyword_line(photographer, lang, era_lookup, movements_meta, enrichments)
            keyword_line_html = build_keyword_line_html(photographer, lang, era_lookup, movements_meta, enrichments)
            affiliate_section_html = build_affiliate_books_html(photographer, lang, affiliate_books, copy)

            movement_links = []
            movement_select_options = []
            movement_names = related_movement_names(
                photographer,
                movements_meta,
                enrichments,
                override_entry=override_entry if isinstance(override_entry, dict) else None,
            )
            for canonical_movement in movement_names:
                movement_label = english_movement_name(canonical_movement, movements_meta) if lang == "en" else canonical_movement
                movement_target = movement_page_path(canonical_movement, lang, movements_meta)
                tag = f'<a class="tag" href="{movement_target}">{escape_html(movement_label)}</a>'
                if tag not in movement_links:
                    movement_links.append(tag)
                option_tuple = (movement_target, movement_label)
                if movement_target and option_tuple not in movement_select_options:
                    movement_select_options.append(option_tuple)
                if len(movement_links) >= 5:
                    break
            movement_html = "".join(movement_links) or f'<div class="note">{copy["movementPlaceholder"]}</div>'
            if not movement_select_options:
                for canonical_movement in taxonomy_meta.MOVEMENT_TAXONOMY.get("featured") or []:
                    movement_label = english_movement_name(canonical_movement, movements_meta) if lang == "en" else canonical_movement
                    movement_target = movement_page_path(canonical_movement, lang, movements_meta)
                    option_tuple = (movement_target, movement_label)
                    if movement_target and option_tuple not in movement_select_options:
                        movement_select_options.append(option_tuple)

            related_people = build_related_people_items(photographer, lang, enrichments, photographers, era_index, photographer_index, body_text)
            related_people_html = render_related_people_html(related_people, copy["relatedPeoplePlaceholder"])
            related_people_select_options = []
            for person in related_people:
                if person.get("url") and person.get("label"):
                    option_tuple = (person["url"], person["label"])
                    if option_tuple not in related_people_select_options:
                        related_people_select_options.append(option_tuple)

            links = (override_entry.get("links") if isinstance(override_entry, dict) and override_entry.get("links") else None) or photographer.get("links") or []
            def localized_link_label(link: dict) -> str:
                if lang == "en" and link.get("labelEn"):
                    return link["labelEn"]
                label = link.get("label", "")
                return english_reference_label(label, link.get("url", "")) if lang == "en" else label

            links_html = "".join(
                f'<a class="chip-link" href="{escape_html(link["url"])}" target="_blank" rel="noopener">{escape_html(localized_link_label(link))} ↗</a>'
                for link in links
            ) or f'<div class="note">{copy["linksPlaceholder"]}</div>'
            works_for_page = (override_entry.get("works") or []) if isinstance(override_entry, dict) else []
            works_title_key = "titleEn" if lang == "en" else "titleJa"
            works_html = "".join(
                f'<a class="chip-link" href="{escape_html(w["url"])}" target="_blank" rel="noopener">{escape_html(w.get(works_title_key) or w.get("titleJa") or w.get("titleEn", ""))} ↗</a>'
                for w in works_for_page
                if w.get("url") and (w.get("titleJa") or w.get("titleEn"))
            )

            if citations:
                citations_html = "".join(
                    f'<div class="cite-item" id="cite-{cite.get("num", index + 1)}"><div class="cite-num">*{cite.get("num", index + 1)}</div><a href="{escape_html(cite.get("url", "#"))}" target="_blank" rel="noopener">{escape_html(english_reference_label(cite.get("name", cite.get("text", cite.get("url", ""))), cite.get("url", "")) if lang == "en" else cite.get("name", cite.get("text", cite.get("url", ""))))}</a></div>'
                    for index, cite in enumerate(citations)
                )
            else:
                citations_html = f'<div class="note">{copy["sourcesPlaceholder"]}</div>'

            coordinates_href = ("/en/index.html" if lang == "en" else "/index.html") + f'?focus=photographer:{photographer["id"]}'
            era_href = era_page_path(photographer, lang)
            country_href = country_page_path(photographer, lang)
            era_select_options = [
                ((("/en" if lang == "en" else "") + "/archive.html#tab-era"), copy["archive"], False)
            ] + [
                (era_page_path({"era": era["id"]}, lang), (era.get("period") or "").replace(" — ", "–"), era["id"] == photographer.get("era"))
                for era in eras
            ]
            era_select = render_tax_select(
                era_select_options,
                "Browse eras" if lang == "en" else "年代別で見る",
                "Browse eras" if lang == "en" else "年代別で見る",
            ) if photographer.get("era") else ""
            country_select = render_tax_select(
                [
                    (f"/{'en/' if lang == 'en' else ''}countries/{country_entry(nationality)['slug']}.html", country_entry(nationality)["en" if lang == "en" else "ja"], nationality == photographer.get("nationality"))
                    for nationality in all_nationalities
                ],
                "Browse countries" if lang == "en" else "国別でみる",
                "Browse countries" if lang == "en" else "国別で見る",
            ) if photographer.get("nationality") else ""
            canonical = SITE + photographer_page_path(photographer, lang)
            x_default = SITE + photographer_page_path(photographer, "ja")
            stylesheet_href = ("../../styles/photographer-page.css" if lang == "en" else "../styles/photographer-page.css") + f"?v={ASSET_VERSION}"
            search_href = ("../../scripts/global-search.js" if lang == "en" else "../scripts/global-search.js") + f"?v={GLOBAL_SEARCH_VERSION}"
            home_href = "/en/" if lang == "en" else "/"
            privacy_href = "/en/privacy-policy.html" if lang == "en" else "/privacy-policy.html"
            alt_name = display_alt_name(photographer, lang)
            page_path = photographer_page_path(photographer, lang)
            structured_data = build_page_structured_data(photographer, lang, title, description, canonical)
            breadcrumb_structured_data = build_breadcrumb_structured_data(photographer, lang)
            essay_sections_html = override_sections_html or split_essay_into_sections(rendered_body, copy["essay"])
            movement_select = render_optional_tax_select(
                movement_select_options,
                copy["movements"],
                copy["movements"],
            )
            related_people_select = render_optional_tax_select(
                related_people_select_options,
                copy["relatedPeople"],
                copy["relatedPeople"],
            )
            extra_selects = f"{country_select}{era_select}{movement_select}{related_people_select}"
            language_toggle = f"""
      <div class="lang-toggle tab-lang-toggle" aria-label="Language switch">
        <a class="lang-btn{' active' if lang == 'ja' else ''}" href="{photographer_page_path(photographer, 'ja')}">{copy['langJa']}</a>
        <a class="lang-btn{' active' if lang == 'en' else ''}" href="{photographer_page_path(photographer, 'en')}">{copy['langEn']}</a>
      </div>"""
            directory_nav = render_site_directory_nav(
                photographers,
                eras,
                all_nationalities,
                lang,
                related_movements=movement_select_options,
                related_people=related_people_select_options,
            )
            page_top_links = f"""
      <div class="page-top-links top-links">
        <div class="tab-nav-mobile-grid">
          <div class="tab-nav-selects">
            {extra_selects}
          </div>
          {language_toggle}
        </div>
      </div>"""
            page = f"""<!DOCTYPE html>
<html lang="{ 'en' if lang == 'en' else 'ja' }">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape_html(title)}</title>
<meta name="description" content="{escape_html(description)}">
{('<meta name="robots" content="noindex, follow">' if is_placeholder_page else '')}
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="ja" href="{SITE + photographer_page_path(photographer, 'ja')}">
<link rel="alternate" hreflang="en" href="{SITE + photographer_page_path(photographer, 'en')}">
<link rel="alternate" hreflang="x-default" href="{x_default}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="{escape_html(copy['site'])}">
<meta property="og:title" content="{escape_html(title)}">
<meta property="og:description" content="{escape_html(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="{ 'en_US' if lang == 'en' else 'ja_JP' }">
<meta property="og:image" content="{OGP_IMAGE_URL}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{escape_html(copy['site'])}">
<meta name="twitter:image" content="{OGP_IMAGE_URL}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape_html(title)}">
<meta name="twitter:description" content="{escape_html(description)}">
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', '{GA_ID}');
</script>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=DM+Mono:wght@300;400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{stylesheet_href}">
</head>
<body data-photographer-id="{escape_html(photographer['id'])}" data-page-lang="{lang}">
  <header class="page-header" data-nosnippet>
    <div class="container">
      <div class="header-top">
        <div class="header-label">{copy['label']}</div>
      </div>
      <div class="site-brand-title"><a class="site-brand-title-link" href="{home_href}"><em>{copy['site']}</em></a></div>
      <p class="header-keywordline">{keyword_line_html}</p>
    </div>
  </header>
  <div class="page-shell">
    <div class="hero">
      <h1 class="title">{escape_html(display_name(photographer, lang))}{f'<span class="alt">{escape_html(alt_name)}</span>' if alt_name else ''}</h1>
      <p class="lead">{lead_html}</p>
      <div class="hero-info-groups">
        <div class="info-group">
          <div class="group-label">{'Basic facts' if lang == 'en' else '基本情報'}</div>
          <div class="facts-grid">
            <div class="fact-item">
              <span class="fact-label">{copy['country']}</span>
              {f'<a class="fact-value" href="{country_href}">{escape_html(display_country(photographer, lang))}</a>' if country_href else f'<span class="fact-value">{escape_html(display_country(photographer, lang))}</span>'}
            </div>
            <div class="fact-item">
              <span class="fact-label">{copy['era']}</span>
              {f'<a class="fact-value" href="{era_href}">{escape_html(era_period(photographer, era_lookup))}</a>' if era_href else f'<span class="fact-value">{escape_html(era_period(photographer, era_lookup))}</span>'}
            </div>
            <div class="fact-item">
              <span class="fact-label">{'Years' if lang == 'en' else '生没年'}</span>
              <span class="fact-value">{escape_html(display_years(photographer, lang))}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <nav class="tab-nav" data-nosnippet>
      <div class="tab-nav-inner">
{page_top_links}
      </div>
    </nav>
    <div class="section-grid">
{essay_sections_html}
      {affiliate_section_html}
      <section class="section">
        <h2>{copy['links']}</h2>
        <div class="links">{links_html}</div>
      </section>
      {f'<section class="section"><h2>{copy["works"]}</h2><div class="links">{works_html}</div></section>' if works_html else ''}
      <section class="section">
        <h2>{copy['sources']}</h2>
        <div class="sources">{citations_html}</div>
      </section>
    </div>
    {directory_nav}
    <footer class="site-footer" data-nosnippet>
      <div>{copy['footerLine1']}</div>
      <div class="footer-secondary">{copy['footerLine2']}</div>
      <div class="footer-links"><a href="{privacy_href}">{copy['privacy']}</a></div>
    </footer>
  </div>
  <script src="{search_href}"></script>
  <script type="application/ld+json">
{structured_data}
  </script>
  <script type="application/ld+json">
{breadcrumb_structured_data}
  </script>
</body>
</html>
"""
            (out_dir / f"{photographer['id']}.html").write_text(page, encoding="utf-8")
            report_rows.append({
                "lang": lang,
                "path": page_path,
                "title": title,
                "description": description,
            })

    if not only_ids:
        report_dir = REPO / "reports"
        report_dir.mkdir(exist_ok=True)
        report_path = report_dir / "photographer-seo-report.csv"
        with report_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=["lang", "path", "title", "description"], lineterminator="\n")
            writer.writeheader()
            writer.writerows(report_rows)


if __name__ == "__main__":
    main()
