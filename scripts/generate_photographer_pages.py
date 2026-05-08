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
ASSET_VERSION = "20260508a"
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
SEO_TEXT_OVERRIDES = {
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
            "title": "Albert Renger-Patzsch | New Objectivity and the Photography of Things | Photo Coordinates",
            "description": "Renger-Patzsch made the photographed object itself central, rejecting both pictorialist beautification and Bauhaus-style visual experiment in favor of precise structural description.",
            "lead": "Renger-Patzsch made the photographed object itself central, rejecting both pictorialist beautification and Bauhaus-style visual experiment in favor of precise structural description.",
        },
    },
    "evans": {
        "ja": {
            "title": "ウォーカー・エヴァンス | FSAとアメリカ・ドキュメンタリー | 写真の座標",
            "description": "ウォーカー・エヴァンスはFSAで農村の貧困を記録しながら、政策宣伝から距離を取り、アメリカの表面を冷静に読むドキュメンタリー写真を確立した。『Let Us Now Praise Famous Men』や地下鉄肖像で、写真を社会記録と批評的観察の両方へ押し広げた。",
        },
        "en": {
            "title": "Walker Evans | FSA and American Documentary | Photo Coordinates",
            "description": "Walker Evans used FSA work, vernacular signs, storefronts, interiors, and subway portraits to make American documentary photography cool, precise, and critical rather than propagandistic.",
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
            "title": "W・ユージン・スミス | フォト・エッセイと倫理 | 写真の座標",
            "description": "W・ユージン・スミスは『LIFE』誌でフォト・エッセイを発展させ、長期取材と緻密な編集によって報道写真を物語的で倫理的な形式へ変えた。『Country Doctor』から『水俣』まで、写真が社会的告発になりうることを示した。",
        },
        "en": {
            "title": "W. Eugene Smith | Photo Essay and Ethics | Photo Coordinates",
            "description": "W. Eugene Smith transformed magazine photojournalism through immersive photo essays, from Country Doctor to Minamata, making documentary photography narrative, partisan, and ethically charged.",
        },
    },
    "ansel-adams": {
        "ja": {
            "title": "アンセル・アダムス | ゾーン・システムとアメリカ西部 | 写真の座標",
            "description": "アンセル・アダムスはヨセミテを中心とするアメリカ西部の風景を、大判カメラとゾーン・システムによる精密なトーン制御で表現した。Group f/64、写真教育、環境保全運動を通じて、風景写真をファインアートと環境意識の領域へ押し上げた。",
        },
        "en": {
            "title": "Ansel Adams | Zone System and the American West | Photo Coordinates",
            "description": "Ansel Adams turned the American West into a field of tonal precision and ecological imagination, using the Zone System, Group f/64, teaching, and conservation work to shape modern landscape photography.",
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
            "title": "森山大道 | プロヴォークと都市のスナップショット | 写真の座標",
            "description": "森山大道は新宿をはじめとする都市の断片を、荒れ・ブレ・ボケの写真言語で撮影し、戦後日本写真の視覚を大きく変えた。『にっぽん劇場写真帖』『写真よさようなら』などを通じて、記録と欲望、複製と記憶の境界を問い続けている。",
        },
        "en": {
            "title": "Daido Moriyama | Provoke and the Urban Snapshot | Photo Coordinates",
            "description": "Daido Moriyama transformed postwar Japanese photography through rough, blurred, high-contrast urban images, turning the street into a field of memory, desire, reproduction, and visual instability.",
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
            "title": "ジュリア・マーガレット・キャメロン | ピクトリアリズムの写真家 | 写真の座標",
            "description": "48歳でカメラを持ち12年間に約900点を残したイギリスのヴィクトリア朝写真家。意図的なソフトフォーカスで被写体の内面を表出させ、写真を芸術として確立した先駆者として知られる。姪孫にヴァージニア・ウルフを持つ。",
            "lead": "48歳でカメラを持ち12年間に約900点を残したイギリスのヴィクトリア朝写真家。意図的なソフトフォーカスで被写体の内面を表出させ、写真を芸術として確立した先駆者として知られる。姪孫にヴァージニア・ウルフを持つ。",
        },
        "en": {
            "title": "Julia Margaret Cameron: Pictorialism | Photo Coordinates",
            "description": "A Victorian British photographer who picked up a camera at forty-eight and produced around 900 works over twelve years. A pioneer who used intentional soft focus to evoke the inner life of her subjects, establishing photography as a fine art. Virginia Woolf was her great-niece.",
            "lead": "A Victorian British photographer who picked up a camera at forty-eight and produced around 900 works over twelve years. A pioneer who used intentional soft focus to evoke the inner life of her subjects, establishing photography as a fine art. Virginia Woolf was her great-niece.",
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
            "description": "Cindy Sherman transformed photography from a medium of evidence and authorial expression into a way of testing how cinema, advertising, and art history produce recognizable roles. Tracing Untitled Film Stills, the Pictures Generation, and feminist photography.",
            "lead": "Cindy Sherman transformed photography from a medium associated with evidence, likeness, and authorial self-expression into a way of testing how cinema, advertising, magazines, and art history produce recognizable roles. Working alongside the Pictures Generation in late-1970s New York, she used her own body, costume, makeup, setting, and camera position to unsettle the idea that a single image can reveal a stable person.",
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
    books = books[:4]

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
) -> str:
    if not text:
        return ""
    if regex is None:
        return escape_html(text).replace("\n", "<br>")

    linked_ids = linked_ids or set()
    parts: list[str] = []
    cursor = 0
    for match in regex.finditer(text):
        alias = match.group(0)
        start, end = match.span()
        photographer = alias_lookup.get(alias)
        photographer_id = photographer["id"] if photographer else None
        if (
            not photographer
            or photographer_id == exclude_id
            or photographer_id in linked_ids
            or should_skip_alias_boundary(text, start, end, alias)
        ):
            continue
        parts.append(escape_html(text[cursor:start]))
        parts.append(
            f'<a class="inline-photographer-link" href="{photographer_page_path(photographer, lang)}">{escape_html(alias)}</a>'
        )
        cursor = end
        linked_ids.add(photographer_id)
    parts.append(escape_html(text[cursor:]))
    return "".join(parts).replace("\n", "<br>")


def _render_cited_segment(text: str, lang: str, alias_lookup: dict[str, dict], regex: re.Pattern | None, exclude_id: str, linked_ids: set[str]) -> str:
    chunks: list[str] = []
    for part in re.split(r"(\*\d+)", text or ""):
        cite = re.fullmatch(r"\*(\d+)", part or "")
        if cite:
            num = cite.group(1)
            chunks.append(f'<sup class="sup-ref"><a href="#cite-{num}">*{num}</a></sup>')
        else:
            chunks.append(render_linked_text(part, lang, alias_lookup, regex, exclude_id=exclude_id, linked_ids=linked_ids))
    return "".join(chunks)


def render_cited_text(text: str, lang: str, alias_lookup: dict[str, dict], regex: re.Pattern | None, exclude_id: str) -> str:
    return _render_cited_segment(text, lang, alias_lookup, regex, exclude_id, set())


ESSAY_HEADING_SET = {
    '経歴',
    '表現解説',
    '批評と受容',
    'Biography',
    'Expression / method',
    'Criticism and reception',
}


def render_override_essay_html(text: str, lang: str, alias_lookup: dict[str, dict], regex: re.Pattern | None, exclude_id: str) -> str:
    if not text:
        return ""
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    linked_ids: set[str] = set()
    parts: list[str] = []
    for block in blocks:
        if block in ESSAY_HEADING_SET:
            parts.append(f"<h3>{escape_html(block)}</h3>")
        else:
            parts.append(f"<p>{_render_cited_segment(block, lang, alias_lookup, regex, exclude_id, linked_ids)}</p>")
    return "".join(parts)


def render_override_sections_html(sections, lang: str, alias_lookup: dict[str, dict], regex: re.Pattern | None, exclude_id: str) -> str:
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
            parts.append(f"<p>{_render_cited_segment(paragraph, lang, alias_lookup, regex, exclude_id, linked_ids)}</p>")
    return "".join(parts)


def render_manual_sectioned_essay_html(
    photographer_id: str,
    text: str,
    lang: str,
    alias_lookup: dict[str, dict],
    regex: re.Pattern | None,
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
            ("経歴", None, "その手段として"),
            ("表現解説", "その手段として", None),
        ],
        ("cameron", "en"): [
            ("Biography", None, "Instead of sharp definition"),
            ("Expression / method", "Instead of sharp definition", None),
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
            parts.append(f"<p>{_render_cited_segment(paragraph, lang, alias_lookup, regex, photographer_id, linked_ids)}</p>")
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
    return build_meta_summary(photographer, lang, era_lookup, movements_meta, enrichments)


def build_title(photographer: dict, lang: str, era_lookup: dict, movements_meta: dict, enrichments: dict) -> str:
    name_primary = display_name(photographer, lang)
    site = "Photo Coordinates" if lang == "en" else "写真の座標"
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
                rendered_body = render_override_sections_html(override_sections, lang, alias_lookup, alias_regex, photographer["id"])
            elif override_body_text:
                rendered_body = render_override_essay_html(override_body_text, lang, alias_lookup, alias_regex, photographer["id"])
            elif body_text and photographer["id"] in {"stieglitz", "cameron"}:
                rendered_body = render_manual_sectioned_essay_html(photographer["id"], body_text, lang, alias_lookup, alias_regex) or render_override_essay_html(body_text, lang, alias_lookup, alias_regex, photographer["id"])
            elif body_text:
                rendered_body = render_override_essay_html(body_text, lang, alias_lookup, alias_regex, photographer["id"])
            else:
                rendered_body = f"<p>{escape_html(copy['placeholder'])}</p>"
            is_placeholder_page = is_placeholder_text(body_text, lang)
            description = build_description(photographer, lang, era_lookup, movements_meta, enrichments)
            title = build_title(photographer, lang, era_lookup, movements_meta, enrichments)
            intro = build_intro(photographer, lang, era_lookup, movements_meta, enrichments)
            seo_override = SEO_TEXT_OVERRIDES.get(photographer["id"], {}).get(lang, {})
            if seo_override:
                description = seo_override.get("description") or description
                title = seo_override.get("title") or title
                intro = seo_override.get("lead") or intro
            intro = override_lead(override_entry, lang) or intro
            lead_raw = override_lead_raw(override_entry, lang)
            if lead_raw:
                lead_html = _render_cited_segment(lead_raw, lang, alias_lookup, alias_regex, photographer["id"], set())
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
            links_html = "".join(
                f'<a class="chip-link" href="{escape_html(link["url"])}" target="_blank" rel="noopener">{escape_html(english_reference_label(link["label"], link["url"]) if lang == "en" else link["label"])} ↗</a>'
                for link in links
            ) or f'<div class="note">{copy["linksPlaceholder"]}</div>'

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
      <section class="section" data-nosnippet>
        <h2>{copy['links']}</h2>
        <div class="links">{links_html}</div>
      </section>
      <section class="section" data-nosnippet>
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
