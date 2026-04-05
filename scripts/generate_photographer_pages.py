#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import subprocess
import csv
from pathlib import Path


REPO = Path("/Users/aiharadaisuke/Documents/New project/repo")
SITE = "https://eyescosmos.github.io"
GA_ID = "G-2VRTV8BZEJ"
ASSET_VERSION = "20260405c"
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


def movement_slug(name: str) -> str:
    return re.sub(r"[^A-Za-z\u3000-\u9fff]", "", name or "")


def photographer_page_path(photographer: dict, lang: str = "ja") -> str:
    base = "en/photographers" if lang == "en" else "photographers"
    return f"/{base}/{photographer['id']}.html"


def localize_value(record: dict, ja_key: str, en_key: str) -> str:
    return record.get(ja_key) or record.get(en_key) or ""


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
        return photographer.get("nameJa") or ""
    return photographer.get("name") or ""


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


def build_intro(photographer: dict, lang: str, era_lookup: dict, movements_meta: dict) -> str:
    name_primary = display_name(photographer, lang)
    name_secondary = display_alt_name(photographer, lang)
    period = era_period(photographer, era_lookup)
    movement_names = localized_movement_names(photographer, lang, movements_meta)[:3]
    movement_phrase = join_list(movement_names[:2], lang)
    country = display_country(photographer, lang)
    essay_text, _ = collect_text_and_citations(photographer, lang)
    placeholder = is_placeholder_text(essay_text, lang)

    if lang == "en":
        identity = name_primary if not name_secondary else f"{name_primary} ({name_secondary})"
        if placeholder:
            if movement_phrase:
                return f"{identity} is part of Photo Coordinates, a history of photography site. This page will be expanded around {movement_phrase} and the wider photographic context of {period}."
            return f"{identity} is part of Photo Coordinates, a history of photography site. This page will be expanded with historical context, related photographers, and sources."
        if movement_phrase:
            return f"{identity} is a key figure for reading the history of photography around {movement_phrase}. This page traces how the photographer fits into the broader history of photography through related photographers, movements, and sources."
        return f"{identity} is presented here as part of Photo Coordinates, a site about the history of photography. This page follows the photographer through historical context, related photographers, and key sources."

    identity = name_primary if not name_secondary else f"{name_primary}（{name_secondary}）"
    if placeholder:
        if movement_phrase:
            return f"{identity}を写真史の流れの中で読むための準備ページです。{movement_phrase}や{period}の文脈とあわせて、関連作家・出典を順次追加していきます。"
        return f"{identity}を写真史の中で位置づけるための準備ページです。写真の座標では、関連作家・時代背景・出典を今後順次整えていきます。"
    if movement_phrase:
        return f"{identity}は、{movement_phrase}を考えるうえで重要な写真家です。このページでは、写真史の流れの中での位置づけを、関連作家・運動・出典とあわせてたどります。"
    if country != "—":
        return f"{identity}は、{country}の写真史を考えるうえで重要な写真家です。このページでは、写真の座標の中での位置づけを、関連作家・出典とともに読み解きます。"
    return f"{identity}を写真史の流れの中で読み解くためのページです。関連作家や出典を手がかりに、この写真家の位置づけをたどります。"


def build_description(photographer: dict, lang: str, era_lookup: dict, movements_meta: dict) -> str:
    name_primary = display_name(photographer, lang)
    period = era_period(photographer, era_lookup)
    movement_names = localized_movement_names(photographer, lang, movements_meta)[:3]
    movement_phrase = join_list(movement_names[:2], lang)
    essay_text, _ = collect_text_and_citations(photographer, lang)
    placeholder = is_placeholder_text(essay_text, lang)

    if lang == "en":
        if placeholder:
            base = f"{name_primary} on Photo Coordinates, a history of photography site covering photographers, movements, and historical context."
        elif movement_phrase:
            base = f"{name_primary} in Photo Coordinates. Explore this photographer through {movement_phrase}, photography history, related artists, and sources."
        else:
            base = f"{name_primary} in Photo Coordinates. Explore this photographer through the history of photography, related artists, and sources."
        return truncate_text(base, 155)

    if placeholder:
        base = f"{name_primary}の写真史ページ。写真の座標で、{period}の時代背景や関連作家、出典とともに順次解説を追加します。"
    elif movement_phrase:
        base = f"{name_primary}の写真史ページ。{movement_phrase}と{period}を手がかりに、写真の座標で位置づけ・関連作家・出典をたどれます。"
    else:
        base = f"{name_primary}の写真史ページ。{period}の流れの中で、写真の座標から関連作家・時代背景・出典をたどれます。"
    return truncate_text(base, 110)


def build_title(photographer: dict, lang: str) -> str:
    name_primary = display_name(photographer, lang)
    if lang == "en":
        return f"{name_primary} | History of Photography | Photo Coordinates | Eyes Cosmos"
    return f"{name_primary}｜写真史｜写真の座標｜Eyes Cosmos"


def related_photographers_for(target: dict, all_photographers: list[dict], era_index: dict, photographer_index: dict, limit: int = 3):
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


COPY = {
    "ja": {
        "site": "写真の座標",
        "label": "Photo Coordinates / Photographer",
        "archive": "年代から見る",
        "coordinates": "座標で見る",
        "home": "トップへ戻る",
        "essay": "解説",
        "movements": "関連する運動",
        "relatedPhotographers": "関連する写真家",
        "relatedPhotographersPlaceholder": "関連する写真家は準備中です。",
        "links": "外部リンク",
        "books": "写真集",
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
    },
    "en": {
        "site": "Photo Coordinates",
        "label": "Photo Coordinates / Photographer",
        "archive": "Browse by Era",
        "coordinates": "View in Coordinates",
        "home": "Back to Home",
        "essay": "Essay",
        "movements": "Related movements",
        "relatedPhotographers": "Related photographers",
        "relatedPhotographersPlaceholder": "Related photographers coming soon.",
        "links": "External links",
        "books": "Photobooks",
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
            description = build_description(photographer, lang, era_lookup, movements_meta)
            title = build_title(photographer, lang)
            intro = build_intro(photographer, lang, era_lookup, movements_meta)

            movement_links = []
            for movement in photographer.get("movements") or []:
                meta = movements_meta.get(movement, {})
                movement_label = meta.get("en", movement) if lang == "en" else movement
                archive_path = "/en/archive.html" if lang == "en" else "/archive.html"
                movement_links.append(
                    f'<a class="tag" href="{archive_path}#movement-{movement_slug(movement)}">{escape_html(movement_label)}</a>'
                )
            movement_html = "".join(movement_links) or f'<div class="note">{copy["movementPlaceholder"]}</div>'

            related_people = related_photographers_for(photographer, photographers, era_index, photographer_index)
            related_people_html = "".join(
                f'<a class="tag" href="{photographer_page_path(candidate, lang)}">{escape_html(display_name(candidate, lang))}</a>'
                for candidate in related_people
            ) or f'<div class="note">{copy["relatedPhotographersPlaceholder"]}</div>'

            links = photographer.get("links") or []
            links_html = "".join(
                f'<a class="chip-link" href="{escape_html(link["url"])}" target="_blank" rel="noopener">{escape_html(link["label"])} ↗</a>'
                for link in links
            ) or f'<div class="note">{copy["linksPlaceholder"]}</div>'

            if citations:
                citations_html = "".join(
                    f'<div class="cite-item" id="cite-{cite.get("num", index + 1)}"><div class="cite-num">*{cite.get("num", index + 1)}</div><a href="{escape_html(cite.get("url", "#"))}" target="_blank" rel="noopener">{escape_html(cite.get("name", cite.get("text", cite.get("url", ""))))}</a></div>'
                    for index, cite in enumerate(citations)
                )
            else:
                citations_html = f'<div class="note">{copy["sourcesPlaceholder"]}</div>'

            archive_href = ("/en/archive.html" if lang == "en" else "/archive.html") + f'#photographer-{photographer["id"]}'
            coordinates_href = ("/en/index.html" if lang == "en" else "/index.html") + f'?focus=photographer:{photographer["id"]}'
            canonical = SITE + photographer_page_path(photographer, lang)
            x_default = SITE + photographer_page_path(photographer, "ja")
            stylesheet_href = ("../../styles/photographer-page.css" if lang == "en" else "../styles/photographer-page.css") + f"?v={ASSET_VERSION}"
            affiliate_href = ("../../data/affiliate-books.js" if lang == "en" else "../data/affiliate-books.js") + f"?v={ASSET_VERSION}"
            script_href = ("../../scripts/photographer-page.js" if lang == "en" else "../scripts/photographer-page.js") + f"?v={ASSET_VERSION}"
            home_href = "/en/" if lang == "en" else "/"
            alt_name = display_alt_name(photographer, lang)
            page_path = photographer_page_path(photographer, lang)
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
<meta property="og:locale:alternate" content="{ 'ja_JP' if lang == 'en' else 'en_US' }">
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
  <div class="page-shell">
    <div class="topline">
      <div class="label">{copy['label']}</div>
      <div class="lang-toggle" aria-label="Language switch">
        <a href="{photographer_page_path(photographer, 'ja')}">{copy['langJa']}</a>
        <a href="{photographer_page_path(photographer, 'en')}">{copy['langEn']}</a>
      </div>
    </div>
    <div class="hero">
      <div class="top-links">
        <a href="{home_href}">{copy['home']}</a>
        <a href="{archive_href}">{copy['archive']}</a>
        <a href="{coordinates_href}">{copy['coordinates']}</a>
      </div>
      <h1 class="title">{escape_html(display_name(photographer, lang))}{f'<span class="alt">{escape_html(alt_name)}</span>' if alt_name else ''}</h1>
      <div class="meta">
        <div class="meta-chip">{copy['country']}: {escape_html(display_country(photographer, lang))}</div>
        <div class="meta-chip">{copy['era']}: {escape_html(era_period(photographer, era_lookup))}</div>
        <div class="meta-chip">{escape_html(photographer.get('years') or '—')}</div>
      </div>
      <p class="lead">{escape_html(intro)}</p>
    </div>
    <div class="section-grid">
      <section class="section">
        <h2>{copy['essay']}</h2>
        <div class="essay">{rendered_body}</div>
      </section>
      <section class="section">
        <h2>{copy['movements']}</h2>
        <div class="tags">{movement_html}</div>
      </section>
      <section class="section">
        <h2>{copy['relatedPhotographers']}</h2>
        <div class="related-grid">{related_people_html}</div>
      </section>
      <section class="section" data-affiliate-section hidden>
        <h2>{copy['books']}</h2>
        <div class="book-grid" data-affiliate-list>
          <div class="note">{copy['booksPlaceholder']}</div>
        </div>
      </section>
      <section class="section">
        <h2>{copy['links']}</h2>
        <div class="links">{links_html}</div>
      </section>
      <section class="section">
        <h2>{copy['sources']}</h2>
        <div class="sources">{citations_html}</div>
      </section>
    </div>
  </div>
  <script src="{affiliate_href}"></script>
  <script src="{script_href}"></script>
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
