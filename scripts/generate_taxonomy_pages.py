#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
import unicodedata
import html
import re
from urllib.parse import quote

REPO = Path(__file__).resolve().parent.parent
SITE = "https://eyescosmos.github.io"
GA_ID = "G-2VRTV8BZEJ"
ASSET_VERSION = "20260419c"
GLOBAL_SEARCH_VERSION = "20260421b"
OGP_IMAGE_URL = f"{SITE}/assets/ogp-default.png"
NON_PHOTOGRAPHER_IDS = {
    "charles-wirgman",
    "fabian-marti",
    "gabriel-orozco",
}

COUNTRY_META = {
    "FR": {"ja_code": "FR", "ja_name": "フランス", "en_name": "France", "slug": "france", "flag": "🇫🇷"},
    "GB": {"ja_code": "GB", "ja_name": "イギリス", "en_name": "United Kingdom", "slug": "united-kingdom", "flag": "🇬🇧"},
    "US": {"ja_code": "US", "ja_name": "アメリカ", "en_name": "United States", "slug": "united-states", "flag": "🇺🇸"},
    "IT / GB": {"ja_code": "IT / GB", "ja_name": "イタリア / イギリス", "en_name": "Italy / United Kingdom", "slug": "italy-united-kingdom", "flag": "🇮🇹 🇬🇧"},
    "GB / US": {"ja_code": "GB / US", "ja_name": "イギリス / アメリカ", "en_name": "United Kingdom / United States", "slug": "united-kingdom-united-states", "flag": "🇬🇧 🇺🇸"},
    "DK / US": {"ja_code": "DK / US", "ja_name": "デンマーク / アメリカ", "en_name": "Denmark / United States", "slug": "denmark-united-states", "flag": "🇩🇰 🇺🇸"},
    "DE": {"ja_code": "DE", "ja_name": "ドイツ", "en_name": "Germany", "slug": "germany", "flag": "🇩🇪"},
    "JP": {"ja_code": "JP", "ja_name": "日本", "en_name": "Japan", "slug": "japan", "flag": "🇯🇵"},
    "BR": {"ja_code": "BR", "ja_name": "ブラジル", "en_name": "Brazil", "slug": "brazil", "flag": "🇧🇷"},
    "CA": {"ja_code": "CA", "ja_name": "カナダ", "en_name": "Canada", "slug": "canada", "flag": "🇨🇦"},
    "CH": {"ja_code": "CH", "ja_name": "スイス", "en_name": "Switzerland", "slug": "switzerland", "flag": "🇨🇭"},
    "HU": {"ja_code": "HU", "ja_name": "ハンガリー", "en_name": "Hungary", "slug": "hungary", "flag": "🇭🇺"},
    "RU": {"ja_code": "RU", "ja_name": "ロシア", "en_name": "Russia", "slug": "russia", "flag": "🇷🇺"},
    "LU / US": {"ja_code": "LU / US", "ja_name": "ルクセンブルク / アメリカ", "en_name": "Luxembourg / United States", "slug": "luxembourg-united-states", "flag": "🇱🇺 🇺🇸"},
    "US / GB": {"ja_code": "US / GB", "ja_name": "アメリカ / イギリス", "en_name": "United States / United Kingdom", "slug": "united-states-united-kingdom", "flag": "🇺🇸 🇬🇧"},
    "US / FR": {"ja_code": "US / FR", "ja_name": "アメリカ / フランス", "en_name": "United States / France", "slug": "united-states-france", "flag": "🇺🇸 🇫🇷"},
    "HU / DE": {"ja_code": "HU / DE", "ja_name": "ハンガリー / ドイツ", "en_name": "Hungary / Germany", "slug": "hungary-germany", "flag": "🇭🇺 🇩🇪"},
}

MOVEMENT_NAME_OVERRIDES_EN = {
    "カロタイプ": "Calotype",
    "ヘリオグラフィー": "Heliography",
    "写真石版": "Photolithography",
    "建築写真": "Architectural Photography",
    "明治ドキュメンタリー": "Meiji Documentary",
    "肖像写真": "Portrait Photography",
}
YEAR_OVERRIDES = {
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
ACTIVITY_YEAR_RE = re.compile(r"\d{3,4}s(?:–|-)?(?:\s*/\s*\d{3,4}年代)?")

COUNTRY_BASE_META = {
    "AL": {"ja_name": "アルバニア", "en_name": "Albania", "slug": "albania", "flag": "🇦🇱"},
    "AR": {"ja_name": "アルゼンチン", "en_name": "Argentina", "slug": "argentina", "flag": "🇦🇷"},
    "AT": {"ja_name": "オーストリア", "en_name": "Austria", "slug": "austria", "flag": "🇦🇹"},
    "AU": {"ja_name": "オーストラリア", "en_name": "Australia", "slug": "australia", "flag": "🇦🇺"},
    "BE": {"ja_name": "ベルギー", "en_name": "Belgium", "slug": "belgium", "flag": "🇧🇪"},
    "BR": {"ja_name": "ブラジル", "en_name": "Brazil", "slug": "brazil", "flag": "🇧🇷"},
    "CA": {"ja_name": "カナダ", "en_name": "Canada", "slug": "canada", "flag": "🇨🇦"},
    "CH": {"ja_name": "スイス", "en_name": "Switzerland", "slug": "switzerland", "flag": "🇨🇭"},
    "CN": {"ja_name": "中国", "en_name": "China", "slug": "china", "flag": "🇨🇳"},
    "CZ": {"ja_name": "チェコ", "en_name": "Czech Republic", "slug": "czech-republic", "flag": "🇨🇿"},
    "DE": {"ja_name": "ドイツ", "en_name": "Germany", "slug": "germany", "flag": "🇩🇪"},
    "DK": {"ja_name": "デンマーク", "en_name": "Denmark", "slug": "denmark", "flag": "🇩🇰"},
    "ES": {"ja_name": "スペイン", "en_name": "Spain", "slug": "spain", "flag": "🇪🇸"},
    "FI": {"ja_name": "フィンランド", "en_name": "Finland", "slug": "finland", "flag": "🇫🇮"},
    "FR": {"ja_name": "フランス", "en_name": "France", "slug": "france", "flag": "🇫🇷"},
    "GB": {"ja_name": "イギリス", "en_name": "United Kingdom", "slug": "united-kingdom", "flag": "🇬🇧"},
    "HU": {"ja_name": "ハンガリー", "en_name": "Hungary", "slug": "hungary", "flag": "🇭🇺"},
    "IE": {"ja_name": "アイルランド", "en_name": "Ireland", "slug": "ireland", "flag": "🇮🇪"},
    "IR": {"ja_name": "イラン", "en_name": "Iran", "slug": "iran", "flag": "🇮🇷"},
    "IT": {"ja_name": "イタリア", "en_name": "Italy", "slug": "italy", "flag": "🇮🇹"},
    "JP": {"ja_name": "日本", "en_name": "Japan", "slug": "japan", "flag": "🇯🇵"},
    "KE": {"ja_name": "ケニア", "en_name": "Kenya", "slug": "kenya", "flag": "🇰🇪"},
    "KR": {"ja_name": "韓国", "en_name": "South Korea", "slug": "south-korea", "flag": "🇰🇷"},
    "LB": {"ja_name": "レバノン", "en_name": "Lebanon", "slug": "lebanon", "flag": "🇱🇧"},
    "LT": {"ja_name": "リトアニア", "en_name": "Lithuania", "slug": "lithuania", "flag": "🇱🇹"},
    "LU": {"ja_name": "ルクセンブルク", "en_name": "Luxembourg", "slug": "luxembourg", "flag": "🇱🇺"},
    "MA": {"ja_name": "モロッコ", "en_name": "Morocco", "slug": "morocco", "flag": "🇲🇦"},
    "MK": {"ja_name": "北マケドニア", "en_name": "North Macedonia", "slug": "north-macedonia", "flag": "🇲🇰"},
    "ML": {"ja_name": "マリ", "en_name": "Mali", "slug": "mali", "flag": "🇲🇱"},
    "MX": {"ja_name": "メキシコ", "en_name": "Mexico", "slug": "mexico", "flag": "🇲🇽"},
    "NG": {"ja_name": "ナイジェリア", "en_name": "Nigeria", "slug": "nigeria", "flag": "🇳🇬"},
    "NL": {"ja_name": "オランダ", "en_name": "Netherlands", "slug": "netherlands", "flag": "🇳🇱"},
    "NO": {"ja_name": "ノルウェー", "en_name": "Norway", "slug": "norway", "flag": "🇳🇴"},
    "PL": {"ja_name": "ポーランド", "en_name": "Poland", "slug": "poland", "flag": "🇵🇱"},
    "RO": {"ja_name": "ルーマニア", "en_name": "Romania", "slug": "romania", "flag": "🇷🇴"},
    "RU": {"ja_name": "ロシア", "en_name": "Russia", "slug": "russia", "flag": "🇷🇺"},
    "SE": {"ja_name": "スウェーデン", "en_name": "Sweden", "slug": "sweden", "flag": "🇸🇪"},
    "SK": {"ja_name": "スロバキア", "en_name": "Slovakia", "slug": "slovakia", "flag": "🇸🇰"},
    "UA": {"ja_name": "ウクライナ", "en_name": "Ukraine", "slug": "ukraine", "flag": "🇺🇦"},
    "US": {"ja_name": "アメリカ", "en_name": "United States", "slug": "united-states", "flag": "🇺🇸"},
    "VE": {"ja_name": "ベネズエラ", "en_name": "Venezuela", "slug": "venezuela", "flag": "🇻🇪"},
    "VN": {"ja_name": "ベトナム", "en_name": "Vietnam", "slug": "vietnam", "flag": "🇻🇳"},
    "ZA": {"ja_name": "南アフリカ", "en_name": "South Africa", "slug": "south-africa", "flag": "🇿🇦"},
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

JAPANESE_READING_OVERRIDES = {
    "domon": "どもんけん",
    "araki": "あらきのぶよし",
    "tomatsu": "とまつしょうめい",
    "moriyama": "もりやまだいどう",
    "takeji-iwamiya": "いわみやたけじ",
    "kikuji-kawada": "かわだきくじ",
    "masahisa-fukase": "ふかせまさひさ",
    "jp-横山松三郎": "よこやままつさぶろう",
    "jp-冨重利平": "とみしげりへい",
    "jp-冨重徳次": "とみしげとくじ",
    "jp-鹿島清兵衛": "かしませいべえ",
    "jp-亀井茲明": "かめいこれあき",
    "jp-屋須弘平": "やすこうへい",
    "jp-鳥居龍蔵": "とりいりゅうぞう",
    "jp-福原信三": "ふくはらしんぞう",
    "jp-野島康三": "のじまやすぞう",
    "jp-中山岩太": "なかやまいわた",
    "jp-安井仲治": "やすいなかじ",
    "jp-植田正治": "うえだしょうじ",
    "jp-金丸重嶺": "かなまるしげね",
    "jp-鈴木八郎": "すずきはちろう",
    "jp-長谷川伝次郎": "はせがわでんじろう",
    "jp-影山光洋": "かげやまこうよう",
    "takeyoshi-tanuma": "たぬまたけよし",
    "hideo-haga": "はがひでお",
    "eikoh-hosoe": "ほそええいこう",
    "kishin-shinoyama": "しのやまきしん",
    "takuma-nakahira": "なかひらたくま",
    "hiroshi-sugimoto": "すぎもとひろし",
    "issei-suda": "すだいっせい",
    "kazuyoshi-nomachi": "のまちかずよし",
    "mitsuaki-iwago": "いわごうみつあき",
    "miyako-ishiuchi": "いしうちみやこ",
    "yoshino-oishi": "おおいしよしの",
    "keizo-kitajima": "きたじまけいぞう",
    "hiromi-tsuchida": "つちだひろみ",
    "yasumasa-morimura": "もりむらやすまさ",
    "rinko-kawauchi": "かわうちりんこ",
    "takashi-yasumura": "やすむらたかし",
    "naoya-hatakeyama": "はたけやまなおや",
    "wang-qingsong": "おうけいしょう",
    "yang-fudong": "ようふくとう",
    "jikei-sato": "さとうじけい",
    "norihiko-matsumoto": "まつもとのりひこ",
    "yurie-nagashima": "ながしまゆりえ",
    "mika-ninagawa": "にながわみか",
    "taiji-matsue": "まつえたいじ",
    "lieko-shiga": "しがりえこ",
    "noriko-hayashi": "はやしのりこ",
    "daisuke-yokota": "よこただいすけ",
}

GOJUON_ROWS = {
    "ア": set("あいうえおぁぃぅぇぉゔ"),
    "カ": set("かきくけこがぎぐげご"),
    "サ": set("さしすせそざじずぜぞ"),
    "タ": set("たちつてとだぢづでど"),
    "ナ": set("なにぬねの"),
    "ハ": set("はひふへほばびぶべぼぱぴぷぺぽ"),
    "マ": set("まみむめも"),
    "ヤ": set("やゆよゃゅょ"),
    "ラ": set("らりるれろ"),
    "ワ": set("わをんゎ"),
}


def eval_js(files: list[str], expression: str):
    source = ["(function(){", "var window = this;"]
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


def eval_site_js_object(object_name: str):
    source = (REPO / "scripts/site.js").read_text(encoding="utf-8")
    match = re.search(rf"const {re.escape(object_name)} = (\{{.*?\n\}});", source, re.S)
    if not match:
        return {}
    proc = subprocess.run(
        ["osascript", "-l", "JavaScript"],
        input=f"const {object_name} = {match.group(1)};\nconsole.log(JSON.stringify({object_name}));".encode("utf-8"),
        capture_output=True,
        check=True,
    )
    payload = proc.stderr.decode("utf-8") or proc.stdout.decode("utf-8")
    return json.loads(payload)


def ensure_country_meta(nationality: str) -> dict | None:
    code = (nationality or "").strip()
    if not code:
        return None
    if code in COUNTRY_META:
        return COUNTRY_META[code]
    parts = [part.strip() for part in code.split("/") if part.strip()]
    if not parts:
        return None
    part_meta = [COUNTRY_BASE_META.get(part) for part in parts]
    if any(meta is None for meta in part_meta):
        return None
    meta = {
        "ja_code": code,
        "ja_name": " / ".join(meta["ja_name"] for meta in part_meta if meta),
        "en_name": " / ".join(meta["en_name"] for meta in part_meta if meta),
        "slug": "-".join(meta["slug"] for meta in part_meta if meta),
        "flag": " ".join(meta["flag"] for meta in part_meta if meta),
    }
    COUNTRY_META[code] = meta
    return meta


def photographer_country_code(photographer: dict, enrichments: dict, country_overrides: dict) -> str:
    enrichment = enrichments.get(photographer.get("id"), {})
    country_override = country_overrides.get(photographer.get("id"), {})
    return (
        enrichment.get("countryCode")
        or enrichment.get("nationality")
        or country_override.get("countryCode")
        or country_override.get("nationality")
        or photographer.get("nationality")
        or ""
    )


def esc(text: str) -> str:
    return html.escape(text or "")


def ascii_slug(text: str) -> str:
    value = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii")
    value = value.lower().replace("&", " and ").replace("+", " plus ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "movement"


def movement_slug(name: str, lang: str = "ja", movements_meta: dict | None = None) -> str:
    if lang == "en":
        label = localized_movement_name(name, movements_meta or {}, "en")
        return ascii_slug(label)
    return re.sub(r"[^A-Za-z\u3000-\u9fff]", "", name or "")


def photographer_path(photographer: dict, lang: str) -> str:
    return f"/{'en/' if lang == 'en' else ''}photographers/{photographer['id']}.html"


def era_path(era_id: str, lang: str) -> str:
    return f"/{'en/' if lang == 'en' else ''}eras/{era_id}.html"


def country_path(nationality: str, lang: str) -> str:
    meta = ensure_country_meta(nationality) or {}
    slug = meta.get("slug", "unknown")
    return f"/{'en/' if lang == 'en' else ''}countries/{slug}.html"


def movement_path(name: str, lang: str, movements_meta: dict | None = None) -> str:
    return f"/{'en/' if lang == 'en' else ''}movements/{movement_slug(name, lang, movements_meta)}.html"


def display_name(photographer: dict, lang: str) -> str:
    return photographer.get("name") if lang == "en" else (photographer.get("nameJa") or photographer.get("name") or "")


def display_alt_name(photographer: dict, lang: str) -> str:
    return photographer.get("nameJa") if lang == "en" else (photographer.get("name") or "")


def katakana_to_hiragana(text: str) -> str:
    chars = []
    for char in text:
        code = ord(char)
        if 0x30A1 <= code <= 0x30F6:
            chars.append(chr(code - 0x60))
        else:
            chars.append(char)
    return "".join(chars)


def normalized_japanese_reading(photographer: dict) -> str:
    override = JAPANESE_READING_OVERRIDES.get(photographer.get("id"))
    if override:
        return override

    name = (photographer.get("nameJa") or photographer.get("name") or "").strip()
    if not name:
        return ""

    paren_match = re.search(r"[（(]([ァ-ヶーぁ-ん]+(?:[・･][ァ-ヶーぁ-ん]+)*)[）)]", name)
    if paren_match:
        return katakana_to_hiragana(paren_match.group(1)).replace("・", "").replace("･", "")

    name = re.sub(r"^[A-Za-zＡ-Ｚａ-ｚ0-9０-９\.\-・･\s]+", "", name)
    name = katakana_to_hiragana(name)
    return name


def gojuon_heading_from_reading(reading: str) -> str:
    text = (reading or "").strip()
    if not text:
        return "#"
    for char in text:
        if char in "ー・･ ":
            continue
        for heading, chars in GOJUON_ROWS.items():
            if char in chars:
                return heading
        if re.match(r"[a-z]", char):
            return char.upper()
        if re.match(r"[A-Z]", char):
            return char
    return "#"


def japanese_sort_key(photographer: dict) -> str:
    reading = normalized_japanese_reading(photographer)
    if reading:
        return reading
    return katakana_to_hiragana((display_name(photographer, "ja") or "").lower())


def display_country_code(photographer: dict) -> str:
    nationality = photographer.get("nationality") or ""
    meta = ensure_country_meta(nationality) or {}
    return meta.get("ja_code") or nationality or "—"


def country_label(nationality: str, lang: str) -> str:
    meta = ensure_country_meta(nationality) or {}
    return meta.get("en_name") if lang == "en" else meta.get("ja_name") or nationality


def country_flag(nationality: str) -> str:
    return (ensure_country_meta(nationality) or {}).get("flag", "")


def era_short_label(era: dict, lang: str) -> str:
    period = era.get("period") or ""
    if lang == "en":
        return period.replace(" — ", "–")
    return period.replace(" — ", "–")


def parse_birth_year(photographer: dict) -> int:
    years = photographer.get("years") or ""
    match = re.search(r"(\d{4})", years)
    if match:
        return int(match.group(1))
    return 9999


def sort_photographers(photographers: list[dict], lang: str) -> list[dict]:
    return sorted(
        photographers,
        key=lambda p: (
            parse_birth_year(p),
            (display_name(p, "en") or "").lower(),
            (display_name(p, "ja") or "").lower(),
            p.get("id") or "",
        ),
    )


def top_movements(photographers: list[dict], movements_meta: dict, lang: str, limit: int = 5) -> list[tuple[str, str]]:
    counts = Counter()
    for photographer in photographers:
        for movement in photographer.get("movements") or []:
            counts[movement] += 1
    items = []
    for movement, _count in counts.most_common(limit):
        label = localized_movement_name(movement, movements_meta, lang)
        items.append((label, movement))
    return items


def page_structured_data(title: str, description: str, canonical: str, lang: str, crumb_label: str) -> str:
    payload = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": canonical,
                "url": canonical,
                "name": title,
                "description": description,
                "inLanguage": "en" if lang == "en" else "ja",
                "isPartOf": {
                    "@type": "WebSite",
                    "name": "Photo Coordinates" if lang == "en" else "写真の座標",
                    "url": f"{SITE}/en/" if lang == "en" else f"{SITE}/",
                },
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Photo Coordinates" if lang == "en" else "写真の座標", "item": f"{SITE}/en/" if lang == "en" else f"{SITE}/"},
                    {"@type": "ListItem", "position": 2, "name": crumb_label, "item": canonical},
                ],
            },
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def alternate_links_html(canonical: str, lang: str, ja_href: str | None = None, en_href: str | None = None) -> str:
    ja_href = ja_href or (canonical.replace("/en/", "/") if lang == "en" else canonical)
    en_href = en_href or (canonical if lang == "en" else canonical.replace(f"{SITE}/", f"{SITE}/en/", 1))
    return "\n".join(
        [
            f'<link rel="alternate" hreflang="ja" href="{ja_href}">',
            f'<link rel="alternate" hreflang="en" href="{en_href}">',
            f'<link rel="alternate" hreflang="x-default" href="{ja_href}">',
        ]
    )


def render_redirect_page(*, from_url: str, to_url: str, label: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, follow">
<meta http-equiv="refresh" content="0; url={esc(to_url)}">
<link rel="canonical" href="{esc(to_url)}">
<title>{esc(label)} | Photo Coordinates</title>
</head>
<body>
<p><a href="{esc(to_url)}">Continue to {esc(label)}</a></p>
<script>window.location.replace({json.dumps(to_url)});</script>
</body>
</html>
"""


def clean_inline_text(text: str) -> str:
    value = re.sub(r"\s+", " ", (text or "").strip())
    return value


def sentence_summary(text: str, lang: str, limit: int = 160, max_sentences: int = 2) -> str:
    value = clean_inline_text(text)
    if not value:
        return ""
    if len(value) <= limit:
        return value

    if lang == "en":
        parts = re.findall(r"[^.!?]+[.!?]", value)
        if not parts:
            parts = [value]
        result = ""
        for part in parts[:max_sentences]:
            candidate = (result + " " + part.strip()).strip()
            if len(candidate) > limit and result:
                break
            result = candidate
        if result:
            return result
        cutoff = value.rfind(" ", 0, limit)
        return value[: cutoff if cutoff > 30 else limit].rstrip(" ,.;:") + "."

    parts = [part for part in re.split(r"(?<=。)", value) if part.strip()]
    result = ""
    for part in parts[:max_sentences]:
        candidate = result + part.strip()
        if len(candidate) > limit and result:
            break
        result = candidate
    if result:
        return result
    return value[:limit].rstrip("、。") + "。"


def short_block_text(text: str, lang: str, limit: int = 120) -> str:
    return sentence_summary(text, lang, limit=limit, max_sentences=2)


def strip_citation_markers(text: str) -> str:
    return re.sub(r"\*\d+", "", clean_inline_text(text or "")).strip()


def photographer_country_meta(photographer: dict, enrichments: dict, country_overrides: dict, lang: str) -> dict:
    enrichment = enrichments.get(photographer.get("id"), {})
    nationality = photographer_country_code(photographer, enrichments, country_overrides)
    meta = ensure_country_meta(nationality) or {}
    return {
        "nationality": nationality,
        "flag": enrichment.get("flag") or meta.get("flag") or country_flag(nationality),
        "label": country_label(nationality, lang) if nationality else ("Unknown" if lang == "en" else "不明"),
        "code": meta.get("ja_code") or nationality or ("—" if lang == "ja" else "—"),
    }


def localized_enrichment_value(photographer: dict, enrichments: dict, base_key: str, lang: str) -> str:
    enrichment = enrichments.get(photographer.get("id"), {})
    primary_key = f"{base_key}{'En' if lang == 'en' else 'Ja'}"
    fallback_key = f"{base_key}{'Ja' if lang == 'en' else 'En'}"
    return enrichment.get(primary_key) or enrichment.get(fallback_key) or ""


def localized_movement_name(movement: str, movements_meta: dict, lang: str) -> str:
    if lang == "en":
        return movements_meta.get(movement, {}).get("en") or MOVEMENT_NAME_OVERRIDES_EN.get(movement) or movement
    return movement


def photographer_tag_labels(photographer: dict, movements_meta: dict, enrichments: dict, lang: str, limit: int = 2) -> tuple[list[str], int]:
    enrichment = enrichments.get(photographer.get("id"), {})
    values = []
    seen = set()
    for movement in (photographer.get("movements") or []) + (enrichment.get("extraMovements") or []):
        if not movement or movement in seen:
            continue
        seen.add(movement)
        values.append(localized_movement_name(movement, movements_meta, lang))
    return values[:limit], max(0, len(values) - limit)


def photographer_short_descriptor(photographer: dict, movements_meta: dict, enrichments: dict, era_lookup: dict, lang: str) -> str:
    descriptor = localized_enrichment_value(photographer, enrichments, "descriptor", lang)
    if descriptor:
        return descriptor
    movements, _more = photographer_tag_labels(photographer, movements_meta, enrichments, lang, 1)
    if movements:
        return movements[0]
    era = era_lookup.get(photographer.get("era")) or {}
    return era.get("titleEn") if lang == "en" else era.get("title") or ""


def first_essay_paragraph(text: str) -> str:
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text or "") if block.strip()]
    heading_set = {
        "経歴",
        "表現解説",
        "批評と受容",
        "Biography",
        "Expression / method",
        "Criticism and reception",
    }
    for block in blocks:
        if block in heading_set:
            continue
        return block
    return ""


def photographer_short_lead(
    photographer: dict,
    essay_overrides: dict,
    movements_meta: dict,
    enrichments: dict,
    era_lookup: dict,
    lang: str,
    limit: int = 115,
) -> str:
    override = essay_overrides.get(photographer.get("id"), {})
    if lang == "en":
        base = strip_citation_markers(override.get("leadEn") or first_essay_paragraph(override.get("textEn") or override.get("textJa") or ""))
    else:
        base = strip_citation_markers(override.get("leadJa") or first_essay_paragraph(override.get("textJa") or override.get("textEn") or ""))
    if base:
        return short_block_text(base, lang, limit)

    essay_fallback = first_essay_paragraph(
        (photographer.get("expression") or {}).get("textEn" if lang == "en" else "text")
        or (photographer.get("expression") or {}).get("text")
        or ""
    )
    if not essay_fallback:
        essay_fallback = first_essay_paragraph(
            (photographer.get("context") or {}).get("textEn" if lang == "en" else "text")
            or (photographer.get("context") or {}).get("text")
            or ""
        )
    essay_fallback = strip_citation_markers(essay_fallback)
    if essay_fallback:
        return short_block_text(essay_fallback, lang, limit)

    descriptor = photographer_short_descriptor(photographer, movements_meta, enrichments, era_lookup, lang)
    years = display_years(photographer, lang)
    if lang == "en":
        fallback = f"{display_name(photographer, lang)} can be followed here through {descriptor or 'the history of photography'}, related movements, and historical context."
    else:
        fallback = f"{display_name(photographer, lang)}を、{descriptor or '写真史'}の文脈からたどるための短い解説です。"
    if years and lang == "ja":
        fallback = f"{display_name(photographer, lang)}（{years}）を、{descriptor or '写真史'}の文脈からたどるための短い解説です。"
    return short_block_text(fallback, lang, limit)


def display_years(photographer: dict, lang: str) -> str:
    raw = YEAR_OVERRIDES.get(photographer.get("id") or "", photographer.get("years") or "").strip()
    if not raw:
        return ""
    if ACTIVITY_YEAR_RE.fullmatch(raw):
        return ""
    if lang == "en":
        value = raw.split(" / ", 1)[0].strip()
        value = value.replace("明治期", "Meiji period")
        value = value.replace("年代", "s")
        return value.replace("-", "–")
    return raw


def archive_list_overline_html(country_meta: dict, years: str) -> str:
    flag = country_meta.get("flag", "")
    code = country_meta.get("code", "")
    country_parts = []
    if flag:
        country_parts.append(f'<span class="archive-list-flag">{esc(flag)}</span>')
    if code:
        country_parts.append(f'<span class="archive-list-country-code">{esc(code)}</span>')
    country_html = (
        f'<span class="archive-list-country">{"".join(country_parts)}</span>'
        if country_parts else ""
    )
    years_html = f'<span class="archive-list-years">{esc(years)}</span>' if years else ""
    return f'<div class="archive-list-overline">{country_html}{years_html}</div>'


def movement_labels_for_text(photographers: list[dict], movements_meta: dict, lang: str, limit: int = 3) -> list[str]:
    return [label for label, _movement in top_movements(photographers, movements_meta, lang, limit)]


def join_labels(labels: list[str], lang: str) -> str:
    labels = [label for label in labels if label]
    if not labels:
        return ""
    if lang == "en":
        if len(labels) == 1:
            return labels[0]
        return ", ".join(labels[:-1]) + f", and {labels[-1]}"
    return "、".join(labels)


def era_lead_text(era: dict, short: str, people: list[dict], movements_meta: dict, lang: str) -> str:
    title = (era.get("titleEn") if lang == "en" else era.get("title")) or short
    movement_text = join_labels(movement_labels_for_text(people, movements_meta, lang, 3), lang)
    if lang == "en":
        if movement_text:
            return f"{short} was shaped by {title}, a context in which photographic institutions and expression changed significantly. This era page organizes photographers, movements, and historical background so readers can trace how {movement_text} emerged within a wider history of photography. Use it as a chronological entry point from individual photographers to related countries, visual languages, and source-backed historical context."
        return f"{short} was shaped by {title}, a context in which photographic institutions and expression changed significantly. This era page organizes photographers and historical background so readers can trace how photographic practices changed over time. Use it as a chronological entry point from individual photographers to related countries, movements, and source-backed historical context."
    if movement_text:
        return f"{short}は、{title}を背景に、写真の制度や表現が大きく動いた時代です。このページでは、{movement_text}などの表現を手がかりに、この時代の写真家と写真史の流れをたどります。"
    return f"{short}は、{title}を背景に、写真の制度や表現が大きく動いた時代です。このページでは、この時代の写真家を時代背景や写真表現の変化とあわせてたどります。"


def english_country_phrase(country: str) -> str:
    if country in {"United States", "United Kingdom"}:
        return f"the {country}"
    return country


def country_lead_text(country: str, people: list[dict], movements_meta: dict, lang: str) -> str:
    movement_text = join_labels(movement_labels_for_text(people, movements_meta, lang, 3), lang)
    if lang == "en":
        country_text = english_country_phrase(country)
        if movement_text:
            return f"This country page gathers photographers connected to {country_text} and traces how their work relates to {movement_text} within the history of photography. It is designed as a country-based entry point, linking individual photographers to eras, movements, and nearby figures rather than treating national photography as a closed category."
        return f"This country page gathers photographers connected to {country_text} and places them within the wider history of photography. It is designed as a country-based entry point, linking individual photographers to eras, movements, and nearby figures rather than treating national photography as a closed category."
    if movement_text:
        return f"{country}に関わる写真家を、{movement_text}などの表現とともにたどるページです。写真史の流れの中で、各作家がどの時代や運動と結びつくのかを見渡せます。"
    return f"{country}に関わる写真家を、写真史の流れの中でたどるページです。各作家がどの時代や運動と結びつくのかを見渡せます。"


def lower_initial(text: str) -> str:
    if not text:
        return text
    return text[0].lower() + text[1:]


def movement_lead_text(movement_label: str, movement_desc: str, lang: str) -> str:
    summary = sentence_summary(movement_desc, lang, limit=160 if lang == "en" else 90, max_sentences=1)
    if lang == "en":
        if summary:
            summary_body = lower_initial(summary.rstrip(".!?"))
            if summary_body.startswith(("a ", "an ", "the ")):
                context = f"It can be understood as {summary_body}."
            else:
                context = summary.rstrip(".!?") + "."
            return f"{movement_label} is an important thread within the history of photography. {context} This movement page brings together photographers, eras, and related contexts so readers can see how the approach developed, where it circulated, and which artists help define its historical position."
        return f"{movement_label} is an important thread within the history of photography. This movement page brings together photographers, eras, and related contexts so readers can see how the approach developed, where it circulated, and which artists help define its historical position."
    if summary:
        summary_body = summary if summary.endswith("。") else f"{summary.rstrip('。')}。"
        return f"{movement_label}は、写真史の流れを考えるうえで重要な表現のひとつです。{summary_body}このページでは、関係する写真家や時代の流れをたどります。"
    return f"{movement_label}は、写真史の流れを考えるうえで重要な表現のひとつです。このページでは、関係する写真家や時代背景をあわせてたどります。"


def clean_context_intro(text: str, lang: str) -> str:
    value = (text or "").strip()
    if lang == "en":
        value = re.sub(r"^(Movement|Expression)\s*[:：\-]\s*", "", value, flags=re.IGNORECASE)
        value = re.sub(r"^(Movement|Expression)\s+", "", value, flags=re.IGNORECASE)
    else:
        value = re.sub(r"^表現\s*[:：\-]\s*", "", value)
        value = re.sub(r"^表現\s+", "", value)
    return value.strip()


def taxonomy_page_title(page_kind: str, label: str, lang: str, era_title: str = "") -> str:
    if lang != "en":
        if page_kind == "movement":
            return f"{label}｜表現｜写真史｜写真の座標｜Eyes Cosmos"
        return f"{label}｜写真家｜写真史｜写真の座標｜Eyes Cosmos"
    if page_kind == "era":
        title = f"{label}: {era_title or 'Photography History'} | Photo Coordinates"
        if len(title) <= 65:
            return title
        short_era = re.split(r"[:;,]", era_title or "")[0].strip()
        title = f"{label}: {short_era or 'Photo History'} | Photo Coordinates"
        return title if len(title) <= 65 else f"{label} Photography History | Photo Coordinates"
    if page_kind == "country":
        return f"{label} Photographers | Photo Coordinates"
    if label.lower().endswith("photography"):
        return f"{label} | Photo Coordinates"
    return f"{label} Photography | Photo Coordinates"


def taxonomy_meta_description(page_kind: str, label: str, lang: str, era_title: str = "") -> str:
    if lang != "en":
        if page_kind == "movement":
            return f"{label}を写真史の中でたどるためのページです。写真の座標で、この表現に関わる写真家や時代背景、関連する運動を一覧できます。"
        return f"{label}の写真家を一覧できる写真史ページです。写真の座標で、写真家、関連運動、時代の流れをまとめてたどれます。"
    if page_kind == "era":
        return f"Explore {label} in photography history through photographers, movements, world events, and visual context on Photo Coordinates."
    if page_kind == "country":
        return f"Browse photographers connected to {label}, with related eras, movements, and historical context in the history of photography."
    return f"Explore {label} through photographers, related eras, and historical context in the history of photography."


def era_context_html(era: dict, lang: str) -> str:
    world_text = short_block_text(
        (era.get("worldEvents") or {}).get("textEn" if lang == "en" else "text") or (era.get("worldEvents") or {}).get("text") or "",
        lang,
        260 if lang == "en" else 130,
    )
    photo_text = short_block_text(
        (era.get("photoContext") or {}).get("textEn" if lang == "en" else "text") or (era.get("photoContext") or {}).get("text") or "",
        lang,
        260 if lang == "en" else 130,
    )
    blocks = [
        f'''          <div class="context-block">
            <div class="context-text">{esc(text)}</div>
          </div>'''
        for text in (world_text, photo_text)
        if text
    ]
    if not blocks:
        return ""
    return f'''<section class="section taxonomy-context">
        <h2>{"Context" if lang == "en" else "この時代の背景"}</h2>
        <div class="context-grid">
{chr(10).join(blocks)}
        </div>
      </section>'''


def render_taxonomy_page(*, lang: str, page_kind: str, title: str, keywordline: str, canonical: str, description: str, lead: str, home_href: str, controls_html: str, hero_groups_html: str, context_html: str, list_title: str, list_html: str, directory_nav_html: str, ja_href: str | None = None, en_href: str | None = None) -> str:
    kind_label = "Movement" if page_kind == "movement" else ("Country" if page_kind == "country" else "Era")
    label = f"Photo Coordinates / {kind_label}"
    structured = page_structured_data(title, description, canonical, lang, title.split("｜")[0].split("|")[0].strip())
    ja_href = ja_href or (canonical.replace("/en/", "/") if lang == "en" else canonical)
    en_href = en_href or (canonical if lang == "en" else canonical.replace(f"{SITE}/", f"{SITE}/en/", 1))
    footer_line1 = "This site gathers and organizes information from publicly available web sources with AI assistance." if lang == "en" else "本サイトの情報はAIによってウェブ上の資料から収集・整理されたものです。"
    footer_line2 = "Sources are listed where possible, but errors or outdated details may remain." if lang == "en" else "各記述には出典を明記していますが、誤りが含まれる可能性があります。"
    footer_line3 = "Please feel free to get in touch if you notice corrections or additions." if lang == "en" else "情報の訂正・追加はお気軽にお知らせください。"
    privacy_label = "Privacy Policy" if lang == "en" else "プライバシーポリシー"
    privacy_href = "/en/privacy-policy.html" if lang == "en" else "/privacy-policy.html"
    footer_extra = f'<div class="footer-secondary">{esc(footer_line3)}</div>' if page_kind == "era" else ""
    return f"""<!DOCTYPE html>
<html lang="{'en' if lang == 'en' else 'ja'}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
{alternate_links_html(canonical, lang, ja_href, en_href)}
<meta property="og:type" content="article">
<meta property="og:site_name" content="{'Photo Coordinates' if lang == 'en' else '写真の座標'}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{OGP_IMAGE_URL}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{'Photo Coordinates' if lang == 'en' else '写真の座標'}">
<meta name="twitter:image" content="{OGP_IMAGE_URL}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<script type="application/ld+json">
{structured}
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', '{GA_ID}');
</script>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=DM+Mono:wght@300;400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{'../../styles/taxonomy-page.css' if lang == 'en' else '../styles/taxonomy-page.css'}?v={ASSET_VERSION}">
</head>
<body>
  <header class="page-header" data-nosnippet>
    <div class="container">
      <div class="header-top">
        <div class="header-label">{label}</div>
      </div>
      <div class="site-brand-title"><a class="site-brand-title-link" href="{home_href}"><em>{'Photo Coordinates' if lang == 'en' else '写真の座標'}</em></a></div>
      <p class="header-keywordline">{keywordline}</p>
    </div>
  </header>
  <nav class="tab-nav" data-nosnippet>
    <div class="tab-nav-inner">
      <div class="page-top-links top-links">
        <div class="tab-nav-selects">
          {controls_html}
        </div>
      </div>
      <div class="lang-toggle tab-lang-toggle" aria-label="Language switch">
        <a class="lang-btn{' active' if lang == 'ja' else ''}" href="{ja_href}">Japanese</a>
        <a class="lang-btn{' active' if lang == 'en' else ''}" href="{en_href}">English</a>
      </div>
    </div>
  </nav>
  <div class="page-shell">
    <div class="hero">
      <h1 class="title">{esc(title.split('｜')[0].split('|')[0].strip())}</h1>
      <p class="lead">{esc(lead)}</p>
      <div class="hero-meta">{hero_groups_html}</div>
    </div>
    <div class="section-grid">
      {context_html}
      <section class="section">
        <h2>{esc(list_title)}</h2>
        <div class="archive-list-shell">{list_html}</div>
      </section>
    </div>
    {directory_nav_html}
    <footer class="site-footer" data-nosnippet>
      <div>{esc(footer_line1)}</div>
      <div class="footer-secondary">{esc(footer_line2)}</div>
      {footer_extra}
      <div class="footer-links"><a href="{privacy_href}">{privacy_label}</a></div>
    </footer>
  </div>
  <script src="{'../../scripts/global-search.js' if lang == 'en' else '../scripts/global-search.js'}?v={GLOBAL_SEARCH_VERSION}"></script>
</body>
</html>
"""
def render_archive_like_list(
    photographers: list[dict],
    lang: str,
    era_lookup: dict,
    movements_meta: dict,
    enrichments: dict,
    country_overrides: dict,
    essay_overrides: dict,
) -> str:
    if not photographers:
        return f'<div class="taxonomy-empty">{"Photographers will be added soon." if lang == "en" else "写真家は順次追加します。"}</div>'

    items = []
    for photographer in photographers:
        country_meta = photographer_country_meta(photographer, enrichments, country_overrides, lang)
        tags, more_count = photographer_tag_labels(photographer, movements_meta, enrichments, lang, 2)
        lead = photographer_short_lead(photographer, essay_overrides, movements_meta, enrichments, era_lookup, lang, 115)
        descriptor = photographer_short_descriptor(photographer, movements_meta, enrichments, era_lookup, lang)
        years = display_years(photographer, lang)
        overline_html = archive_list_overline_html(country_meta, years)
        tags_html = "".join(f'<span class="archive-list-tag">{esc(tag)}</span>' for tag in tags)
        if more_count:
            tags_html += f'<span class="archive-list-tag archive-list-tag-more">+{more_count}</span>'
        detail_label = "Read details" if lang == "en" else "詳細を読む"
        coordinate_label = "View in Coordinates" if lang == "en" else "座標で見る"
        coordinate_href = f"/{'en/' if lang == 'en' else ''}?focus=photographer%3A{quote(str(photographer.get('id') or ''))}&photographer={quote(str(photographer.get('id') or ''))}"
        descriptor_html = f'<div class="archive-list-descriptor">{esc(descriptor)}</div>' if descriptor else ""
        sub_name = display_alt_name(photographer, lang) if lang == "ja" else ""
        alt_html = f'<div class="archive-list-alt">{esc(sub_name)}</div>' if sub_name else ""
        items.append(
            f'''<details class="archive-list-card">
  <summary class="archive-list-summary">
    {overline_html}
    <div class="archive-list-heading">
      <div class="archive-list-name-wrap">
        <div class="archive-list-name">{esc(display_name(photographer, lang))}</div>
        {alt_html}
      </div>
      <div class="archive-list-chevron" aria-hidden="true">+</div>
    </div>
    {descriptor_html}
    <div class="archive-list-tags">{tags_html}</div>
  </summary>
  <div class="archive-list-body">
    <p class="archive-list-lead">{esc(lead)}</p>
    <a class="archive-list-link" href="{photographer_path(photographer, lang)}">{detail_label}</a>
    <a class="archive-list-link" href="{coordinate_href}">{coordinate_label}</a>
  </div>
</details>'''
        )
    return f'<div class="archive-list">{"".join(items)}</div>'


def render_movement_cards(photographers: list[dict], movements_meta: dict, lang: str) -> str:
    cards = []
    for label, original in top_movements(photographers, movements_meta, lang, 5):
        cards.append(f'<a class="tag-card" href="{movement_path(original, lang, movements_meta)}">{esc(label)}</a>')
    return "".join(cards) or f'<p>{"Related movements coming soon." if lang == "en" else "関連する運動は準備中です。"}</p>'


def render_related_movement_dropdown(photographers: list[dict], movements_meta: dict, lang: str) -> str:
    label = "Related movements" if lang == "en" else "関連する運動"
    options = [f'<option value="" selected>{esc(label)}</option>']
    for movement_label, original in top_movements(photographers, movements_meta, lang, 8):
        options.append(f'<option value="{movement_path(original, lang, movements_meta)}">{esc(movement_label)}</option>')
    return (
        f'<span class="select-wrap taxonomy-inline-select">'
        f'<select class="tax-select" aria-label="{label}" onchange="if(this.value) window.location.href=this.value">{"".join(options)}</select>'
        f'</span>'
    )


def render_country_select(all_nationalities: list[str], current: str | None, lang: str, placeholder_label: str | None = None) -> str:
    label = "Browse countries" if lang == "en" else "国別でみる"
    options = []
    if placeholder_label:
        options.append(f'<option value="" selected>{esc(placeholder_label)}</option>')
    for nationality in all_nationalities:
        selected = ' selected' if placeholder_label is None and nationality == current else ''
        options.append(f'<option value="{country_path(nationality, lang)}"{selected}>{esc(country_label(nationality, lang))}</option>')
    return f'<span class="select-wrap"><select class="tax-select filter-select nav-select" aria-label="{label}" onchange="if(this.value) window.location.href=this.value">{ "".join(options) }</select></span>'


def render_era_select(eras: list[dict], current_id: str | None, lang: str, placeholder_label: str | None = None) -> str:
    label = "Browse eras" if lang == "en" else "年代別で見る"
    options = []
    if placeholder_label:
        options.append(f'<option value="" selected>{esc(placeholder_label)}</option>')
    archive_href = "/en/archive.html#tab-era" if lang == "en" else "/archive.html#tab-era"
    archive_label = "Browse by Era" if lang == "en" else "年代順で見る"
    options.append(f'<option value="{archive_href}">{esc(archive_label)}</option>')
    for era in eras:
        selected = ' selected' if placeholder_label is None and era["id"] == current_id else ''
        options.append(f'<option value="{era_path(era["id"], lang)}"{selected}>{esc(era_short_label(era, lang))}</option>')
    return f'<span class="select-wrap"><select class="tax-select filter-select nav-select" aria-label="{label}" onchange="if(this.value) window.location.href=this.value">{ "".join(options) }</select></span>'


def render_movement_select(movements: list[str], current: str | None, movements_meta: dict, lang: str, placeholder_label: str | None = None) -> str:
    label = "Browse movements" if lang == "en" else "表現からみる"
    options = []
    if placeholder_label:
        options.append(f'<option value="" selected>{esc(placeholder_label)}</option>')
    for movement in movements:
        movement_label = localized_movement_name(movement, movements_meta, lang)
        selected = ' selected' if placeholder_label is None and movement == current else ''
        options.append(f'<option value="{movement_path(movement, lang, movements_meta)}"{selected}>{esc(movement_label)}</option>')
    return f'<span class="select-wrap"><select class="tax-select filter-select nav-select" aria-label="{label}" onchange="if(this.value) window.location.href=this.value">{ "".join(options) }</select></span>'


def render_site_directory_nav(
    photographers: list[dict],
    eras: list[dict],
    all_nationalities: list[str],
    lang: str,
) -> str:
    labels = {
        "ja": {
            "nav": "サイト内リンク",
            "eras": "年代一覧",
            "countries": "国一覧",
            "photographers": "代表写真家一覧",
        },
        "en": {
            "nav": "Site links",
            "eras": "Era index",
            "countries": "Country index",
            "photographers": "Featured photographers",
        },
    }[lang]
    photographer_lookup = {photographer["id"]: photographer for photographer in photographers}
    featured_links = []
    for photographer_id in FEATURED_PHOTOGRAPHER_IDS:
        photographer = photographer_lookup.get(photographer_id)
        if photographer:
            featured_links.append(
                f'<a href="{photographer_path(photographer, lang)}">{esc(display_name(photographer, lang))}</a>'
            )
    era_links = [
        f'<a href="{era_path(era["id"], lang)}">{esc(era_short_label(era, lang))}</a>'
        for era in eras
    ]
    country_links = [
        f'<a href="{country_path(nationality, lang)}">{esc(country_label(nationality, lang))}</a>'
        for nationality in all_nationalities
    ]
    return f"""
      <nav class="site-directory-links" aria-label="{esc(labels['nav'])}" data-nosnippet>
        <div class="site-directory-group">
          <div class="site-directory-label">{esc(labels['eras'])}</div>
          <div class="site-directory-items">{''.join(era_links)}</div>
        </div>
        <div class="site-directory-group">
          <div class="site-directory-label">{esc(labels['countries'])}</div>
          <div class="site-directory-items">{''.join(country_links)}</div>
        </div>
        <div class="site-directory-group">
          <div class="site-directory-label">{esc(labels['photographers'])}</div>
          <div class="site-directory-items">{''.join(featured_links)}</div>
        </div>
      </nav>"""


def main():
    photographers = eval_js([
        "data/photographers.js",
        "data/photographers-manual-additions.js",
        "data/photographers-supplement.js",
    ], "PHOTOGRAPHERS")
    photographers = [p for p in photographers if p["id"] not in NON_PHOTOGRAPHER_IDS]
    movements_meta = eval_js(["data/movements.js"], "MOVEMENTS_META")
    enrichments = eval_js(["data/photographer-enrichments.js"], "window.PHOTOGRAPHER_ENRICHMENTS || PHOTOGRAPHER_ENRICHMENTS || {}")
    country_overrides = eval_site_js_object("PHOTOGRAPHER_COUNTRY_OVERRIDES")
    essay_overrides = eval_js(["data/photographer-essay-overrides.js"], "window.PHOTOGRAPHER_ESSAY_OVERRIDES || {}")
    eras = eval_js([
        "data/eras.js",
        "data/content-helpers.js",
        "data/future/era-1990s.js",
        "data/future/era-2000s.js",
        "data/future/era-2010s.js",
    ], "ERAS")
    era_lookup = {era["id"]: era for era in eras}

    eras_dir = REPO / "eras"
    eras_en_dir = REPO / "en/eras"
    countries_dir = REPO / "countries"
    countries_en_dir = REPO / "en/countries"
    movements_dir = REPO / "movements"
    movements_en_dir = REPO / "en/movements"
    for d in (eras_dir, eras_en_dir, countries_dir, countries_en_dir, movements_dir, movements_en_dir):
        d.mkdir(parents=True, exist_ok=True)

    photographers_by_era = defaultdict(list)
    photographers_by_country = defaultdict(list)
    photographers_by_movement = defaultdict(list)
    for photographer in photographers:
        photographers_by_era[photographer.get("era")].append(photographer)
        country_code = photographer_country_code(photographer, enrichments, country_overrides)
        if country_code:
            ensure_country_meta(country_code)
            photographers_by_country[country_code].append(photographer)
        movement_values = []
        for movement in photographer.get("movements") or []:
            if movement and movement not in movement_values:
                movement_values.append(movement)
        for movement in movement_values:
            photographers_by_movement[movement].append(photographer)

    all_nationalities = sorted([n for n in photographers_by_country.keys() if ensure_country_meta(n)], key=lambda n: country_label(n, "ja"))
    all_movements = sorted(
        [movement for movement, items in photographers_by_movement.items() if items],
        key=lambda movement: localized_movement_name(movement, movements_meta, "en").lower(),
    )

    for lang in ("ja", "en"):
        # Era pages
        for era in eras:
            era_id = era["id"]
            era_title = era.get("titleEn") if lang == "en" else era.get("title")
            short = era_short_label(era, lang)
            title = taxonomy_page_title("era", short, lang, era_title or "")
            keyword = f"{short} | Photographers | History of Photography | Photo Coordinates |" if lang == "en" else f"{short}｜写真家｜写真史｜<a href=\"/\">写真の座標</a>｜"
            people = sort_photographers(photographers_by_era.get(era_id, []), lang)
            canonical = f"{SITE}/{'en/' if lang == 'en' else ''}eras/{era_id}.html"
            description = taxonomy_meta_description("era", short, lang, era_title or "")
            lead = era_lead_text(era, short, people, movements_meta, lang)
            context_html = era_context_html(era, lang)
            hero_groups = (
                f'<div class="meta-group"><div class="group-label">{"Basic facts" if lang == "en" else "基本情報"}</div><div class="mini-card-grid"><div class="mini-card"><span class="mini-card-label">{"Era" if lang == "en" else "年代"}</span><span class="mini-card-value">{esc(short)}</span></div><div class="mini-card"><span class="mini-card-label">{"Photographers" if lang == "en" else "写真家数"}</span><span class="mini-card-value">{len(people)}</span></div></div></div>'
            )
            page = render_taxonomy_page(
                lang=lang,
                page_kind="era",
                title=title,
                keywordline=keyword,
                canonical=canonical,
                description=description,
                lead=lead,
                home_href="/en/" if lang == "en" else "/",
                controls_html=(
                    render_era_select(eras, era_id, lang, "Browse eras" if lang == "en" else "年代別で見る")
                    + render_country_select(all_nationalities, None, lang, "Browse countries" if lang == "en" else "国別で見る")
                    + render_movement_select(all_movements, None, movements_meta, lang, "Browse by Movement" if lang == "en" else "表現から見る")
                    + render_related_movement_dropdown(people, movements_meta, lang).replace('class="tax-select"', 'class="tax-select filter-select nav-select"').replace('taxonomy-inline-select', '')
                ),
                hero_groups_html=hero_groups,
                context_html=context_html,
                list_title="Photographers" if lang == "en" else "写真家一覧",
                list_html=render_archive_like_list(people, lang, era_lookup, movements_meta, enrichments, country_overrides, essay_overrides),
                directory_nav_html=render_site_directory_nav(photographers, eras, all_nationalities, lang),
            )
            (eras_en_dir if lang == "en" else eras_dir).joinpath(f"{era_id}.html").write_text(page, encoding="utf-8")

        # Country pages
        for nationality in all_nationalities:
            country_meta = ensure_country_meta(nationality) or {}
            label = country_label(nationality, lang)
            short = label
            title = taxonomy_page_title("country", short, lang)
            keyword = f"{short} | Photographers | History of Photography | Photo Coordinates |" if lang == "en" else f"{short}｜写真家｜写真史｜<a href=\"/\">写真の座標</a>｜"
            people = sort_photographers(photographers_by_country.get(nationality, []), lang)
            canonical = f"{SITE}/{'en/' if lang == 'en' else ''}countries/{country_meta['slug']}.html"
            lead = country_lead_text(short, people, movements_meta, lang)
            description = taxonomy_meta_description("country", short, lang)
            hero_groups = (
                f'<div class="meta-group"><div class="group-label">{"Basic facts" if lang == "en" else "基本情報"}</div><div class="mini-card-grid"><div class="mini-card"><span class="mini-card-label">{"Country" if lang == "en" else "国"}</span><span class="mini-card-value">{esc(short)}</span></div><div class="mini-card"><span class="mini-card-label">{"Photographers" if lang == "en" else "写真家数"}</span><span class="mini-card-value">{len(people)}</span></div></div></div>'
            )
            controls_html = (
                render_country_select(all_nationalities, None, lang, "Browse countries" if lang == "en" else "国別で見る")
                + render_era_select(eras, None, lang, "Browse eras" if lang == "en" else "年代別で見る")
                + render_related_movement_dropdown(people, movements_meta, lang).replace('class="tax-select"', 'class="tax-select filter-select nav-select"').replace('taxonomy-inline-select', '')
            )
            page = render_taxonomy_page(
                lang=lang,
                page_kind="country",
                title=title,
                keywordline=keyword,
                canonical=canonical,
                description=description,
                lead=lead,
                home_href="/en/" if lang == "en" else "/",
                controls_html=controls_html,
                hero_groups_html=hero_groups,
                context_html="",
                list_title="Photographers" if lang == "en" else "写真家一覧",
                list_html=render_archive_like_list(people, lang, era_lookup, movements_meta, enrichments, country_overrides, essay_overrides),
                directory_nav_html=render_site_directory_nav(photographers, eras, all_nationalities, lang),
            )
            (countries_en_dir if lang == "en" else countries_dir).joinpath(f"{country_meta['slug']}.html").write_text(page, encoding="utf-8")

        # Movement pages
        for movement in all_movements:
            people = sort_photographers(photographers_by_movement.get(movement, []), lang)
            movement_label = localized_movement_name(movement, movements_meta, lang)
            title = taxonomy_page_title("movement", movement_label, lang)
            keyword = f"{movement_label} | Photography Movement | History of Photography | Photo Coordinates |" if lang == "en" else f"{movement_label}｜表現｜写真史｜<a href=\"/\">写真の座標</a>｜"
            ja_href = f"{SITE}/movements/{movement_slug(movement, 'ja', movements_meta)}.html"
            en_href = f"{SITE}/en/movements/{movement_slug(movement, 'en', movements_meta)}.html"
            canonical = en_href if lang == "en" else ja_href
            description = taxonomy_meta_description("movement", movement_label, lang)
            movement_desc = movements_meta.get(movement, {}).get("descEn" if lang == "en" else "desc") or movements_meta.get(movement, {}).get("desc") or ""
            movement_desc = clean_context_intro(movement_desc, lang)
            lead = movement_lead_text(movement_label, movement_desc, lang)
            context_html = (
                f'''<section class="section taxonomy-context">
        <h2>{"Overview" if lang == "en" else "この表現について"}</h2>
        <div class="context-grid">
          <div class="context-block">
            <div class="context-text">{esc(short_block_text(movement_desc, lang, 260 if lang == "en" else 150))}</div>
          </div>
        </div>
      </section>'''
            ) if movement_desc else ""
            hero_groups = (
                f'<div class="meta-group"><div class="group-label">{"Basic facts" if lang == "en" else "基本情報"}</div><div class="mini-card-grid"><div class="mini-card"><span class="mini-card-label">{"Movement" if lang == "en" else "表現"}</span><span class="mini-card-value">{esc(movement_label)}</span></div><div class="mini-card"><span class="mini-card-label">{"Photographers" if lang == "en" else "写真家数"}</span><span class="mini-card-value">{len(people)}</span></div></div></div>'
            )
            controls_html = (
                render_era_select(eras, None, lang, "Browse eras" if lang == "en" else "年代別で見る")
                + render_country_select(all_nationalities, None, lang, "Browse countries" if lang == "en" else "国別で見る")
                + render_movement_select(all_movements, None, movements_meta, lang, "Browse by Movement" if lang == "en" else "表現から見る")
            )
            page = render_taxonomy_page(
                lang=lang,
                page_kind="movement",
                title=title,
                keywordline=keyword,
                canonical=canonical,
                description=description,
                lead=lead,
                home_href="/en/" if lang == "en" else "/",
                controls_html=controls_html,
                hero_groups_html=hero_groups,
                context_html=context_html,
                list_title="Photographers" if lang == "en" else "写真家一覧",
                list_html=render_archive_like_list(people, lang, era_lookup, movements_meta, enrichments, country_overrides, essay_overrides),
                directory_nav_html=render_site_directory_nav(photographers, eras, all_nationalities, lang),
                ja_href=ja_href,
                en_href=en_href,
            )
            output_slug = movement_slug(movement, lang, movements_meta)
            (movements_en_dir if lang == "en" else movements_dir).joinpath(f"{output_slug}.html").write_text(page, encoding="utf-8")
            if lang == "en":
                legacy_slug = movement_slug(movement, "ja", movements_meta)
                if legacy_slug != output_slug:
                    redirect = render_redirect_page(
                        from_url=f"{SITE}/en/movements/{legacy_slug}.html",
                        to_url=en_href,
                        label=movement_label,
                    )
                    movements_en_dir.joinpath(f"{legacy_slug}.html").write_text(redirect, encoding="utf-8")


if __name__ == "__main__":
    main()
