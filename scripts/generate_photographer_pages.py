#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import subprocess
import csv
from pathlib import Path
from urllib.parse import urlparse


REPO = Path("/Users/aiharadaisuke/Documents/New project/repo")
SITE = "https://eyescosmos.github.io"
GA_ID = "G-2VRTV8BZEJ"
ASSET_VERSION = "20260414d"
ALNUM_BOUNDARY_RE = re.compile(r"[A-Za-z0-9]")
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
MOVEMENT_NAME_OVERRIDES_EN = {
    "カロタイプ": "Calotype",
    "肖像写真": "Portrait Photography",
    "ヘリオグラフィー": "Heliography",
    "建築写真": "Architectural Photography",
    "写真石版": "Photolithography",
    "明治ドキュメンタリー": "Meiji Documentary",
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


def english_movement_name(movement: str, movements_meta: dict) -> str:
    meta = movements_meta.get(movement, {})
    return meta.get("en") or MOVEMENT_NAME_OVERRIDES_EN.get(movement) or movement


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
    books = books[:3]

    if not books:
        return f"""<section class="section" data-affiliate-section>
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

    return f"""<section class="section" data-affiliate-section>
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
    country_en = COUNTRY_META.get(photographer.get("nationality") or "", {}).get("en") or (photographer.get("nationality") or "")
    descriptor = descriptor_for(photographer, lang, era_lookup, movements_meta, enrichments)
    movement_names = expanded_movement_names(photographer, lang, movements_meta, enrichments, limit=2)
    movement_phrase = join_list(movement_names, lang)

    if lang == "en":
        if not placeholder and sentences:
            summary = " ".join(sentences)
            if years and name not in summary:
                stripped = strip_leading_identity(summary, photographer, lang)
                summary = f"{name} ({years}): {stripped}"
            return truncate_text(summary, 155)
        parts = []
        if years:
            parts.append(f"{name} ({years})")
        else:
            parts.append(name)
        if country_en:
            parts.append(f"is a photographer associated with {country_en}")
        else:
            parts.append("is a photographer")
        if descriptor:
            parts.append(f"whose work is often discussed through {descriptor.lower()}")
        elif movement_phrase:
            parts.append(f"whose work is often discussed through {movement_phrase}")
        period = era_period(photographer, era_lookup)
        if period and period != "—":
            parts.append(f"This page traces the photographer's place in the photographic context of {period}, together with related figures and sources.")
        else:
            parts.append("This page traces the photographer's historical context, related figures, and sources.")
        return truncate_text(" ".join(parts), 155)

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
    return re.sub(r"[^A-Za-z\u3000-\u9fff]", "", name or "")


def photographer_page_path(photographer: dict, lang: str = "ja") -> str:
    base = "en/photographers" if lang == "en" else "photographers"
    return f"/{base}/{photographer['id']}.html"


def era_page_path(photographer: dict, lang: str = "ja") -> str:
    era_id = photographer.get("era") or ""
    base = "en/eras" if lang == "en" else "eras"
    return f"/{base}/{era_id}.html" if era_id else ""


def country_page_path(photographer: dict, lang: str = "ja") -> str:
    nationality = photographer.get("nationality") or ""
    slug = COUNTRY_META.get(nationality, {}).get("slug")
    if not slug:
        return ""
    base = "en/countries" if lang == "en" else "countries"
    return f"/{base}/{slug}.html"


def movement_page_path(movement: str, lang: str = "ja") -> str:
    base = "en/movements" if lang == "en" else "movements"
    return f"/{base}/{movement_slug(movement)}.html"


def render_tax_select(options: list[tuple[str, str, bool]], label: str) -> str:
    rendered = []
    for value, text, selected in options:
        rendered.append(f'<option value="{escape_html(value)}"{ " selected" if selected else "" }>{escape_html(text)}</option>')
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


def render_cited_text(text: str, lang: str, alias_lookup: dict[str, dict], regex: re.Pattern | None, exclude_id: str) -> str:
    linked_ids: set[str] = set()
    chunks: list[str] = []
    for part in re.split(r"(\*\d+)", text or ""):
        cite = re.fullmatch(r"\*(\d+)", part or "")
        if cite:
            num = cite.group(1)
            chunks.append(f'<sup class="sup-ref"><a href="#cite-{num}">*{num}</a></sup>')
        else:
            chunks.append(render_linked_text(part, lang, alias_lookup, regex, exclude_id=exclude_id, linked_ids=linked_ids))
    return "".join(chunks)


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
    country_map = {
        "FR": {"ja": "FR", "en": "France"},
        "GB": {"ja": "GB", "en": "United Kingdom"},
        "US": {"ja": "US", "en": "United States"},
        "IT / GB": {"ja": "IT / GB", "en": "Italy / United Kingdom"},
        "GB / US": {"ja": "GB / US", "en": "United Kingdom / United States"},
        "DK / US": {"ja": "DK / US", "en": "Denmark / United States"},
        "DE": {"ja": "DE", "en": "Germany"},
        "JP": {"ja": "JP", "en": "Japan"},
        "BR": {"ja": "BR", "en": "Brazil"},
        "CA": {"ja": "CA", "en": "Canada"},
    }
    nationality = photographer.get("nationality") or ""
    return country_map.get(nationality, {}).get(lang) or nationality or "—"


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
    role = extract_title_role(photographer, lang, era_lookup, movements_meta, enrichments)
    site = "Photo Coordinates" if lang == "en" else "写真の座標"
    base = f"{name_primary} | {role} | {site}"
    max_length = 60 if lang == "ja" else 70
    if len(base) <= max_length:
        return base
    available = max(8, max_length - len(name_primary) - len(site) - 6)
    role = truncate_text(role, available).rstrip("。")
    return f"{name_primary} | {role} | {site}"


def build_page_structured_data(photographer: dict, lang: str, description: str, canonical: str) -> str:
    birth_year, death_year = parse_years(photographer.get("years") or "")
    payload = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": display_name(photographer, lang),
        "description": description,
        "url": canonical,
        "jobTitle": "Photographer" if lang == "en" else "写真家",
    }
    alternate_name = display_alt_name(photographer, lang)
    if alternate_name:
        payload["alternateName"] = alternate_name
    if birth_year:
        payload["birthDate"] = birth_year
    if death_year:
        payload["deathDate"] = death_year
    country_name = COUNTRY_META.get(photographer.get("nationality") or "", {}).get("en")
    if country_name:
        payload["nationality"] = {
            "@type": "Country",
            "name": country_name,
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
        "archive": "年代順にみる",
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
        "footerLine1": "本サイトの情報はAIによってウェブ上の資料から収集・整理されたものです。",
        "footerLine2": "各記述には出典を明記していますが、誤りが含まれる可能性があります。",
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
        "footerLine1": "This site gathers and organizes information from publicly available web sources with AI assistance.",
        "footerLine2": "Sources are listed where possible, but errors or outdated details may remain.",
        "privacy": "Privacy Policy",
    },
}


def main() -> None:
    all_photographers = eval_js(
        [
            "data/photographers.js",
            "data/photographers-manual-additions.js",
            "data/photographers-supplement.js",
        ],
        "PHOTOGRAPHERS",
    )
    photographers = [p for p in all_photographers if p["id"] not in NON_PHOTOGRAPHER_IDS]
    alias_map = eval_js(
        [
            "data/photographers.js",
            "data/photographers-manual-additions.js",
            "data/photographers-supplement.js",
        ],
        'typeof PHOTOGRAPHER_LINK_ALIASES !== "undefined" ? PHOTOGRAPHER_LINK_ALIASES : {}',
    )
    movements_meta = eval_js(["data/movements.js"], "MOVEMENTS_META")
    enrichments = eval_js(["data/photographer-enrichments.js"], 'typeof PHOTOGRAPHER_ENRICHMENTS !== "undefined" ? PHOTOGRAPHER_ENRICHMENTS : {}')
    affiliate_books = load_affiliate_books()
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
        [nationality for nationality in {p.get("nationality") for p in photographers if p.get("nationality")} if nationality in COUNTRY_META],
        key=lambda nationality: COUNTRY_META[nationality]["ja"],
    )
    all_movements = sorted(
        {movement for photographer in photographers for movement in (photographer.get("movements") or []) if movement},
        key=lambda movement: (movements_meta.get(movement, {}).get("en", movement) or movement).lower(),
    )

    report_rows = []

    for lang in ("ja", "en"):
        out_dir = REPO / ("en/photographers" if lang == "en" else "photographers")
        out_dir.mkdir(parents=True, exist_ok=True)
        for excluded_id in NON_PHOTOGRAPHER_IDS:
            excluded_file = out_dir / f"{excluded_id}.html"
            if excluded_file.exists():
                excluded_file.unlink()
        copy = COPY[lang]

        for photographer in photographers:
            body_text, citations = collect_text_and_citations(photographer, lang)
            rendered_body = render_cited_text(body_text or copy["placeholder"], lang, alias_lookup, alias_regex, photographer["id"])
            description = build_description(photographer, lang, era_lookup, movements_meta, enrichments)
            title = build_title(photographer, lang, era_lookup, movements_meta, enrichments)
            intro = build_intro(photographer, lang, era_lookup, movements_meta, enrichments)
            keyword_line = build_keyword_line(photographer, lang, era_lookup, movements_meta, enrichments)
            keyword_line_html = build_keyword_line_html(photographer, lang, era_lookup, movements_meta, enrichments)
            affiliate_section_html = build_affiliate_books_html(photographer, lang, affiliate_books, copy)

            movement_links = []
            movement_select_options = []
            for movement in (photographer.get("movements") or []) + (get_enrichment(enrichments, photographer).get("extraMovements") or []):
                movement_label = english_movement_name(movement, movements_meta) if lang == "en" else movement
                movement_target = movement_page_path(movement, lang)
                tag = f'<a class="tag" href="{movement_page_path(movement, lang)}">{escape_html(movement_label)}</a>'
                if tag not in movement_links:
                    movement_links.append(tag)
                option_tuple = (movement_target, movement_label)
                if movement_target and option_tuple not in movement_select_options:
                    movement_select_options.append(option_tuple)
                if len(movement_links) >= 5:
                    break
            movement_html = "".join(movement_links) or f'<div class="note">{copy["movementPlaceholder"]}</div>'

            related_people = build_related_people_items(photographer, lang, enrichments, photographers, era_index, photographer_index, body_text)
            related_people_html = render_related_people_html(related_people, copy["relatedPeoplePlaceholder"])
            related_people_select_options = []
            for person in related_people:
                if person.get("url") and person.get("label"):
                    option_tuple = (person["url"], person["label"])
                    if option_tuple not in related_people_select_options:
                        related_people_select_options.append(option_tuple)

            links = photographer.get("links") or []
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

            archive_href = ("/en/archive.html" if lang == "en" else "/archive.html") + f'#photographer-{photographer["id"]}'
            coordinates_href = ("/en/index.html" if lang == "en" else "/index.html") + f'?focus=photographer:{photographer["id"]}'
            era_href = era_page_path(photographer, lang)
            country_href = country_page_path(photographer, lang)
            era_select = render_tax_select(
                [
                    (era_page_path({"era": era["id"]}, lang), (era.get("period") or "").replace(" — ", "–"), era["id"] == photographer.get("era"))
                    for era in eras
                ],
                "Browse by Era" if lang == "en" else "年代順にみる",
            ) if photographer.get("era") else ""
            country_select = render_tax_select(
                [
                    (f"/{'en/' if lang == 'en' else ''}countries/{COUNTRY_META[nationality]['slug']}.html", COUNTRY_META[nationality]["en" if lang == "en" else "ja"], nationality == photographer.get("nationality"))
                    for nationality in all_nationalities
                ],
                "Browse countries" if lang == "en" else "国別でみる",
            ) if photographer.get("nationality") else ""
            canonical = SITE + photographer_page_path(photographer, lang)
            x_default = SITE + photographer_page_path(photographer, "ja")
            stylesheet_href = ("../../styles/photographer-page.css" if lang == "en" else "../styles/photographer-page.css") + f"?v={ASSET_VERSION}"
            override_href = ("../../data/photographer-essay-overrides.js" if lang == "en" else "../data/photographer-essay-overrides.js") + f"?v={ASSET_VERSION}"
            script_href = ("../../scripts/photographer-page.js" if lang == "en" else "../scripts/photographer-page.js") + f"?v={ASSET_VERSION}"
            home_href = "/en/" if lang == "en" else "/"
            privacy_href = "/en/privacy-policy.html" if lang == "en" else "/privacy-policy.html"
            alt_name = display_alt_name(photographer, lang)
            page_path = photographer_page_path(photographer, lang)
            structured_data = build_page_structured_data(photographer, lang, description, canonical)
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
            page_top_links = f"""
      <div class="page-top-links top-links">
        <a class="nav-active-link" href="{archive_href}">{copy['archive']}</a>
        <a class="nav-secondary-link" href="{coordinates_href}">{copy['coordinates']}</a>
        <div class="tab-nav-selects">
          {extra_selects}
        </div>
      </div>"""
            page = f"""<!DOCTYPE html>
<html lang="{ 'en' if lang == 'en' else 'ja' }">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape_html(title)}</title>
<meta name="description" content="{escape_html(description)}">
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
  <header class="page-header">
    <div class="container">
      <div class="header-top">
        <div class="header-label">{copy['label']}</div>
      </div>
      <p class="header-keywordline">{keyword_line_html}</p>
    </div>
  </header>
  <nav class="tab-nav">
    <div class="tab-nav-inner">
{page_top_links}
      <div class="lang-toggle tab-lang-toggle" aria-label="Language switch">
        <a class="lang-btn{' active' if lang == 'ja' else ''}" href="{photographer_page_path(photographer, 'ja')}">{copy['langJa']}</a>
        <a class="lang-btn{' active' if lang == 'en' else ''}" href="{photographer_page_path(photographer, 'en')}">{copy['langEn']}</a>
      </div>
    </div>
  </nav>
  <div class="page-shell">
    <div class="hero">
      <h1 class="title">{escape_html(display_name(photographer, lang))}{f'<span class="alt">{escape_html(alt_name)}</span>' if alt_name else ''}</h1>
      <p class="lead">{escape_html(intro)}</p>
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
    <div class="section-grid">
      <section class="section">
        <h2>{copy['essay']}</h2>
        <div class="essay">{rendered_body}</div>
      </section>
      {affiliate_section_html}
      <section class="section">
        <h2>{copy['links']}</h2>
        <div class="links">{links_html}</div>
      </section>
      <section class="section">
        <h2>{copy['sources']}</h2>
        <div class="sources">{citations_html}</div>
      </section>
    </div>
    <footer class="site-footer">
      <div>{copy['footerLine1']}</div>
      <div class="footer-secondary">{copy['footerLine2']}</div>
      <div class="footer-links"><a href="{privacy_href}">{copy['privacy']}</a></div>
    </footer>
  </div>
  <script src="{override_href}"></script>
  <script src="{script_href}"></script>
  <script type="application/ld+json">
{structured_data}
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

    report_dir = REPO / "reports"
    report_dir.mkdir(exist_ok=True)
    report_path = report_dir / "photographer-seo-report.csv"
    with report_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["lang", "path", "title", "description"])
        writer.writeheader()
        writer.writerows(report_rows)


if __name__ == "__main__":
    main()
