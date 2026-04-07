#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
import html
import re

REPO = Path("/Users/aiharadaisuke/Documents/New project/repo")
SITE = "https://eyescosmos.github.io"
GA_ID = "G-2VRTV8BZEJ"
ASSET_VERSION = "20260406b"
NON_PHOTOGRAPHER_IDS = {
    "anri-sala",
    "ana-torfs",
    "charles-wirgman",
    "claude-closky",
    "collectif-fact",
    "eve-sussman",
    "fabian-marti",
    "g-r-a-m",
    "gabriel-orozco",
    "multiplicity",
    "ohio",
    "the-atlas-group-walid-raad",
    "useful-photography",
    "wangechi-mutu",
}

COUNTRY_META = {
    "FR": {"ja_code": "FR", "ja_name": "フランス", "en_name": "France", "slug": "france"},
    "GB": {"ja_code": "GB", "ja_name": "イギリス", "en_name": "United Kingdom", "slug": "united-kingdom"},
    "US": {"ja_code": "US", "ja_name": "アメリカ", "en_name": "United States", "slug": "united-states"},
    "IT / GB": {"ja_code": "IT / GB", "ja_name": "イタリア / イギリス", "en_name": "Italy / United Kingdom", "slug": "italy-united-kingdom"},
    "GB / US": {"ja_code": "GB / US", "ja_name": "イギリス / アメリカ", "en_name": "United Kingdom / United States", "slug": "united-kingdom-united-states"},
    "DK / US": {"ja_code": "DK / US", "ja_name": "デンマーク / アメリカ", "en_name": "Denmark / United States", "slug": "denmark-united-states"},
    "DE": {"ja_code": "DE", "ja_name": "ドイツ", "en_name": "Germany", "slug": "germany"},
    "JP": {"ja_code": "JP", "ja_name": "日本", "en_name": "Japan", "slug": "japan"},
    "BR": {"ja_code": "BR", "ja_name": "ブラジル", "en_name": "Brazil", "slug": "brazil"},
    "CA": {"ja_code": "CA", "ja_name": "カナダ", "en_name": "Canada", "slug": "canada"},
}

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


def esc(text: str) -> str:
    return html.escape(text or "")


def movement_slug(name: str) -> str:
    import re
    return re.sub(r"[^A-Za-z\u3000-\u9fff]", "", name or "")


def photographer_path(photographer: dict, lang: str) -> str:
    return f"/{'en/' if lang == 'en' else ''}photographers/{photographer['id']}.html"


def era_path(era_id: str, lang: str) -> str:
    return f"/{'en/' if lang == 'en' else ''}eras/{era_id}.html"


def country_path(nationality: str, lang: str) -> str:
    slug = COUNTRY_META.get(nationality, {}).get("slug", "unknown")
    return f"/{'en/' if lang == 'en' else ''}countries/{slug}.html"


def movement_path(name: str, lang: str) -> str:
    return f"/{'en/' if lang == 'en' else ''}movements/{movement_slug(name)}.html"


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
    return COUNTRY_META.get(nationality, {}).get("ja_code") or nationality or "—"


def country_label(nationality: str, lang: str) -> str:
    meta = COUNTRY_META.get(nationality, {})
    return meta.get("en_name") if lang == "en" else meta.get("ja_name") or nationality


def era_short_label(era: dict, lang: str) -> str:
    period = era.get("period") or ""
    if lang == "en":
        return period.replace(" — ", "–")
    return period.replace(" — ", "–")


def sort_photographers(photographers: list[dict], lang: str) -> list[dict]:
    if lang == "en":
        return sorted(photographers, key=lambda p: (display_name(p, "en") or "").lower())
    return sorted(photographers, key=japanese_sort_key)


def group_heading(photographer: dict, lang: str) -> str:
    if lang == "en":
        name = display_name(photographer, lang).strip()
        if not name:
            return "#"
        return name[0].upper()
    return gojuon_heading_from_reading(japanese_sort_key(photographer))


def top_movements(photographers: list[dict], movements_meta: dict, lang: str, limit: int = 5) -> list[tuple[str, str]]:
    counts = Counter()
    for photographer in photographers:
        for movement in photographer.get("movements") or []:
            counts[movement] += 1
    items = []
    for movement, _count in counts.most_common(limit):
        label = movements_meta.get(movement, {}).get("en", movement) if lang == "en" else movement
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
            return f"{short} was shaped by {title}, a context in which photographic institutions and expression changed significantly. This page follows photographers from the era through {movement_text}, world events, and shifts in photographic expression."
        return f"{short} was shaped by {title}, a context in which photographic institutions and expression changed significantly. This page follows the photographers of the era through world events and shifts in photographic expression."
    if movement_text:
        return f"{short}は、{title}を背景に、写真の制度や表現が大きく動いた時代です。このページでは、{movement_text}などの表現を手がかりに、この時代の写真家と写真史の流れをたどります。"
    return f"{short}は、{title}を背景に、写真の制度や表現が大きく動いた時代です。このページでは、この時代の写真家を世界情勢や写真表現の変化とあわせてたどります。"


def english_country_phrase(country: str) -> str:
    if country in {"United States", "United Kingdom"}:
        return f"the {country}"
    return country


def country_lead_text(country: str, people: list[dict], movements_meta: dict, lang: str) -> str:
    movement_text = join_labels(movement_labels_for_text(people, movements_meta, lang, 3), lang)
    if lang == "en":
        country_text = english_country_phrase(country)
        if movement_text:
            return f"This page gathers photographers connected to {country_text} and traces how they relate to {movement_text} within the history of photography. It is a country-based entry point for following photographers, eras, and movements in Photo Coordinates."
        return f"This page gathers photographers connected to {country_text} and places them within the wider history of photography. It is a country-based entry point for following photographers, eras, and movements in Photo Coordinates."
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
            return f"{movement_label} is an important thread within the history of photography. {context} This page follows the photographers, eras, and related contexts connected to it."
        return f"{movement_label} is an important thread within the history of photography. This page follows the photographers, eras, and related contexts connected to it."
    if summary:
        summary_body = summary if summary.endswith("。") else f"{summary.rstrip('。')}。"
        return f"{movement_label}は、写真史の流れを考えるうえで重要な表現のひとつです。{summary_body}このページでは、関係する写真家や時代の流れをたどります。"
    return f"{movement_label}は、写真史の流れを考えるうえで重要な表現のひとつです。このページでは、関係する写真家や時代背景をあわせてたどります。"


def render_taxonomy_page(*, lang: str, page_kind: str, title: str, keywordline: str, canonical: str, description: str, lead: str, home_href: str, archive_href: str, back_label: str, controls_html: str, hero_groups_html: str, context_html: str, list_title: str, list_html: str) -> str:
    kind_label = "Movement" if page_kind == "movement" else ("Country" if page_kind == "country" else "Era")
    label = f"Photo Coordinates / {kind_label}"
    structured = page_structured_data(title, description, canonical, lang, title.split("｜")[0].split("|")[0].strip())
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
<meta property="og:type" content="article">
<meta property="og:site_name" content="{'Photo Coordinates' if lang == 'en' else '写真の座標'}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
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
  <div class="page-shell">
    <div class="topline">
      <div class="label-stack">
        <div class="label">{label}</div>
        <div class="keywordline">{keywordline}</div>
      </div>
      <div class="lang-toggle">
        <a href="{canonical.replace('/en/', '/') if lang == 'en' else canonical.replace(f'{SITE}', f'{SITE}/en', 1)}">{'Japanese' if lang == 'en' else 'English'}</a>
      </div>
    </div>
    <div class="hero">
      <div class="top-links">
        <a href="{home_href}">{'Back to Home' if lang == 'en' else 'トップへ戻る'}</a>
        <a href="{archive_href}">{back_label}</a>
        {controls_html}
      </div>
      <h1 class="title">{esc(title.split('｜')[0].split('|')[0].strip())}</h1>
      <p class="lead">{esc(lead)}</p>
      <div class="hero-meta">{hero_groups_html}</div>
    </div>
    <div class="section-grid">
      {context_html}
      <section class="section">
        <h2>{esc(list_title)}</h2>
        <div class="photographer-grid">{list_html}</div>
      </section>
    </div>
    <footer class="site-footer">
      <div>{esc(footer_line1)}</div>
      <div class="footer-secondary">{esc(footer_line2)}</div>
      {footer_extra}
      <div class="footer-links"><a href="{privacy_href}">{privacy_label}</a></div>
    </footer>
  </div>
</body>
</html>
"""


def render_photographer_cards(photographers: list[dict], lang: str, era_lookup: dict) -> str:
    groups = defaultdict(list)
    for photographer in photographers:
        groups[group_heading(photographer, lang)].append(photographer)
    ordered_heads = sorted(groups.keys(), key=lambda x: x)
    chunks = []
    for head in ordered_heads:
        cards = []
        for photographer in groups[head]:
            cards.append(
                f'<a class="photographer-card" href="{photographer_path(photographer, lang)}">'
                f'<div class="photographer-card-name">{esc(display_name(photographer, lang))}</div>'
                f'</a>'
            )
        chunks.append(
            f'<div class="alphabet-group"><div class="alphabet-label">{esc(head)}</div><div class="photographer-grid">{"".join(cards)}</div></div>'
        )
    return f'<div class="alphabet-groups">{"".join(chunks)}</div>'


def render_movement_cards(photographers: list[dict], movements_meta: dict, lang: str) -> str:
    cards = []
    for label, original in top_movements(photographers, movements_meta, lang, 5):
        cards.append(f'<a class="tag-card" href="{movement_path(original, lang)}">{esc(label)}</a>')
    return "".join(cards) or f'<p>{"Related movements coming soon." if lang == "en" else "関連する運動は準備中です。"}</p>'


def render_country_select(all_nationalities: list[str], current: str | None, lang: str, placeholder_label: str | None = None) -> str:
    label = "Browse countries" if lang == "en" else "国別でみる"
    options = []
    if placeholder_label:
        options.append(f'<option value="" selected>{esc(placeholder_label)}</option>')
    for nationality in all_nationalities:
        selected = ' selected' if placeholder_label is None and nationality == current else ''
        options.append(f'<option value="{country_path(nationality, lang)}"{selected}>{esc(country_label(nationality, lang))}</option>')
    return f'<span class="select-wrap"><select class="tax-select" aria-label="{label}" onchange="if(this.value) window.location.href=this.value">{ "".join(options) }</select></span>'


def render_era_select(eras: list[dict], current_id: str | None, lang: str, placeholder_label: str | None = None) -> str:
    label = "Browse eras" if lang == "en" else "年代順にみる"
    options = []
    if placeholder_label:
        options.append(f'<option value="" selected>{esc(placeholder_label)}</option>')
    for era in eras:
        selected = ' selected' if placeholder_label is None and era["id"] == current_id else ''
        options.append(f'<option value="{era_path(era["id"], lang)}"{selected}>{esc(era_short_label(era, lang))}</option>')
    return f'<span class="select-wrap"><select class="tax-select" aria-label="{label}" onchange="if(this.value) window.location.href=this.value">{ "".join(options) }</select></span>'


def render_movement_select(movements: list[str], current: str | None, movements_meta: dict, lang: str, placeholder_label: str | None = None) -> str:
    label = "Browse movements" if lang == "en" else "表現からみる"
    options = []
    if placeholder_label:
        options.append(f'<option value="" selected>{esc(placeholder_label)}</option>')
    for movement in movements:
        movement_label = movements_meta.get(movement, {}).get("en", movement) if lang == "en" else movement
        selected = ' selected' if placeholder_label is None and movement == current else ''
        options.append(f'<option value="{movement_path(movement, lang)}"{selected}>{esc(movement_label)}</option>')
    return f'<span class="select-wrap"><select class="tax-select" aria-label="{label}" onchange="if(this.value) window.location.href=this.value">{ "".join(options) }</select></span>'


def main():
    photographers = eval_js([
        "data/photographers.js",
        "data/photographers-manual-additions.js",
        "data/photographers-supplement.js",
    ], "PHOTOGRAPHERS")
    photographers = [p for p in photographers if p["id"] not in NON_PHOTOGRAPHER_IDS]
    movements_meta = eval_js(["data/movements.js"], "MOVEMENTS_META")
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
        photographers_by_country[photographer.get("nationality")].append(photographer)
        movement_values = []
        for movement in photographer.get("movements") or []:
            if movement and movement not in movement_values:
                movement_values.append(movement)
        for movement in movement_values:
            photographers_by_movement[movement].append(photographer)

    all_nationalities = sorted([n for n in photographers_by_country.keys() if n in COUNTRY_META], key=lambda n: country_label(n, "ja"))
    all_movements = sorted(
        [movement for movement, items in photographers_by_movement.items() if items],
        key=lambda movement: movements_meta.get(movement, {}).get("en", movement).lower(),
    )

    for lang in ("ja", "en"):
        # Era pages
        for era in eras:
            era_id = era["id"]
            era_title = era.get("titleEn") if lang == "en" else era.get("title")
            short = era_short_label(era, lang)
            title = f"{short} | Photographers | History of Photography | Photo Coordinates | Eyes Cosmos" if lang == "en" else f"{short}｜写真家｜写真史｜写真の座標｜Eyes Cosmos"
            keyword = f"{short} | Photographers | History of Photography | Photo Coordinates |" if lang == "en" else f"{short}｜写真家｜写真史｜<a href=\"/\">写真の座標</a>｜"
            people = sort_photographers(photographers_by_era.get(era_id, []), lang)
            canonical = f"{SITE}/{'en/' if lang == 'en' else ''}eras/{era_id}.html"
            description = (
                f"Explore photographers from {short} in Photo Coordinates, with the history of photography, related movements, and visual context."
                if lang == "en"
                else f"{short}の写真家を一覧できる写真史ページです。写真の座標で、この時代の写真家、関連運動、写真史の流れをたどれます。"
            )
            lead = era_lead_text(era, short, people, movements_meta, lang)
            context_html = (
                f'''<section class="section taxonomy-context">
        <h2>{"Context" if lang == "en" else "この時代の背景"}</h2>
        <div class="context-grid">
          <div class="context-block">
            <div class="context-label">{"World events" if lang == "en" else "世界情勢"}</div>
            <div class="context-text">{esc(short_block_text((era.get("worldEvents") or {}).get("textEn" if lang == "en" else "text") or (era.get("worldEvents") or {}).get("text") or "", lang, 260 if lang == "en" else 130))}</div>
          </div>
          <div class="context-block">
            <div class="context-label">{"Photography and the era" if lang == "en" else "写真と時代"}</div>
            <div class="context-text">{esc(short_block_text((era.get("photoContext") or {}).get("textEn" if lang == "en" else "text") or (era.get("photoContext") or {}).get("text") or "", lang, 260 if lang == "en" else 130))}</div>
          </div>
        </div>
      </section>'''
            )
            hero_groups = (
                f'<div class="meta-group"><div class="group-label">{"Basic facts" if lang == "en" else "基本情報"}</div><div class="mini-card-grid"><div class="mini-card"><span class="mini-card-label">{"Era" if lang == "en" else "年代"}</span><span class="mini-card-value">{esc(short)}</span></div><div class="mini-card"><span class="mini-card-label">{"Photographers" if lang == "en" else "写真家数"}</span><span class="mini-card-value">{len(people)}</span></div></div></div>'
                f'<div class="meta-group"><div class="group-label">{"Related movements" if lang == "en" else "関連する運動"}</div><div class="tag-grid">{render_movement_cards(people, movements_meta, lang)}</div></div>'
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
                archive_href="/en/archive.html" if lang == "en" else "/archive.html",
                back_label="Browse by Era" if lang == "en" else "年代順にみる",
                controls_html=(
                    render_era_select(eras, era_id, lang)
                    + render_country_select(all_nationalities, None, lang, "Browse countries" if lang == "en" else "国別でみる")
                    + render_movement_select(all_movements, None, movements_meta, lang, "Browse by Movement" if lang == "en" else "表現からみる")
                ),
                hero_groups_html=hero_groups,
                context_html=context_html,
                list_title="Photographers" if lang == "en" else "写真家一覧",
                list_html=render_photographer_cards(people, lang, era_lookup),
            )
            (eras_en_dir if lang == "en" else eras_dir).joinpath(f"{era_id}.html").write_text(page, encoding="utf-8")

        # Country pages
        for nationality in all_nationalities:
            label = country_label(nationality, lang)
            short = label
            title = f"{short} | Photographers | History of Photography | Photo Coordinates | Eyes Cosmos" if lang == "en" else f"{short}｜写真家｜写真史｜写真の座標｜Eyes Cosmos"
            keyword = f"{short} | Photographers | History of Photography | Photo Coordinates |" if lang == "en" else f"{short}｜写真家｜写真史｜<a href=\"/\">写真の座標</a>｜"
            people = sort_photographers(photographers_by_country.get(nationality, []), lang)
            canonical = f"{SITE}/{'en/' if lang == 'en' else ''}countries/{COUNTRY_META[nationality]['slug']}.html"
            lead = country_lead_text(short, people, movements_meta, lang)
            description = (
                f"A country guide to photographers linked to {short} on Photo Coordinates. Explore photography history, related movements, and key figures."
                if lang == "en"
                else f"{short}の写真家を一覧できる写真史ページです。写真の座標で、写真家、関連運動、時代の流れをまとめてたどれます。"
            )
            hero_groups = (
                f'<div class="meta-group"><div class="group-label">{"Basic facts" if lang == "en" else "基本情報"}</div><div class="mini-card-grid"><div class="mini-card"><span class="mini-card-label">{"Country" if lang == "en" else "国"}</span><span class="mini-card-value">{esc(short)}</span></div><div class="mini-card"><span class="mini-card-label">{"Photographers" if lang == "en" else "写真家数"}</span><span class="mini-card-value">{len(people)}</span></div></div></div>'
                f'<div class="meta-group"><div class="group-label">{"Related movements" if lang == "en" else "関連する運動"}</div><div class="tag-grid">{render_movement_cards(people, movements_meta, lang)}</div></div>'
            )
            controls_html = (
                render_country_select(all_nationalities, nationality, lang)
                + render_era_select(eras, None, lang, "Browse by Era" if lang == "en" else "年代順にみる")
                + render_movement_select(all_movements, None, movements_meta, lang, "Browse by Movement" if lang == "en" else "表現からみる")
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
                archive_href="/en/archive.html" if lang == "en" else "/archive.html",
                back_label="Browse by Era" if lang == "en" else "年代順にみる",
                controls_html=controls_html,
                hero_groups_html=hero_groups,
                context_html="",
                list_title="Photographers" if lang == "en" else "写真家一覧",
                list_html=render_photographer_cards(people, lang, era_lookup),
            )
            (countries_en_dir if lang == "en" else countries_dir).joinpath(f"{COUNTRY_META[nationality]['slug']}.html").write_text(page, encoding="utf-8")

        # Movement pages
        for movement in all_movements:
            people = sort_photographers(photographers_by_movement.get(movement, []), lang)
            movement_label = movements_meta.get(movement, {}).get("en", movement) if lang == "en" else movement
            title = f"{movement_label} | Photography Movement | History of Photography | Photo Coordinates | Eyes Cosmos" if lang == "en" else f"{movement_label}｜表現｜写真史｜写真の座標｜Eyes Cosmos"
            keyword = f"{movement_label} | Photography Movement | History of Photography | Photo Coordinates |" if lang == "en" else f"{movement_label}｜表現｜写真史｜<a href=\"/\">写真の座標</a>｜"
            canonical = f"{SITE}/{'en/' if lang == 'en' else ''}movements/{movement_slug(movement)}.html"
            description = (
                f"Explore {movement_label} on Photo Coordinates through photographers, related eras, and the wider history of photography."
                if lang == "en"
                else f"{movement_label}を写真史の中でたどるためのページです。写真の座標で、この表現に関わる写真家や時代背景、関連する運動を一覧できます。"
            )
            movement_desc = movements_meta.get(movement, {}).get("descEn" if lang == "en" else "desc") or movements_meta.get(movement, {}).get("desc") or ""
            lead = movement_lead_text(movement_label, movement_desc, lang)
            context_html = (
                f'''<section class="section taxonomy-context">
        <h2>{"Overview" if lang == "en" else "この表現について"}</h2>
        <div class="context-grid">
          <div class="context-block">
            <div class="context-label">{"Movement" if lang == "en" else "表現"}</div>
            <div class="context-text">{esc(short_block_text(movement_desc, lang, 260 if lang == "en" else 150))}</div>
          </div>
        </div>
      </section>'''
            ) if movement_desc else ""
            hero_groups = (
                f'<div class="meta-group"><div class="group-label">{"Basic facts" if lang == "en" else "基本情報"}</div><div class="mini-card-grid"><div class="mini-card"><span class="mini-card-label">{"Movement" if lang == "en" else "表現"}</span><span class="mini-card-value">{esc(movement_label)}</span></div><div class="mini-card"><span class="mini-card-label">{"Photographers" if lang == "en" else "写真家数"}</span><span class="mini-card-value">{len(people)}</span></div></div></div>'
            )
            controls_html = (
                render_era_select(eras, None, lang, "Browse by Era" if lang == "en" else "年代順にみる")
                + render_country_select(all_nationalities, None, lang, "Browse countries" if lang == "en" else "国別でみる")
                + render_movement_select(all_movements, movement, movements_meta, lang)
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
                archive_href="/en/archive.html" if lang == "en" else "/archive.html",
                back_label="Browse by Era" if lang == "en" else "年代順にみる",
                controls_html=controls_html,
                hero_groups_html=hero_groups,
                context_html=context_html,
                list_title="Photographers" if lang == "en" else "写真家一覧",
                list_html=render_photographer_cards(people, lang, era_lookup),
            )
            (movements_en_dir if lang == "en" else movements_dir).joinpath(f"{movement_slug(movement)}.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
