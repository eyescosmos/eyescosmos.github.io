#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

import generate_taxonomy_pages as tax


REPO = Path(__file__).resolve().parent.parent
ASSET_VERSION = tax.ASSET_VERSION


def localize_block(record: dict, lang: str) -> str:
    key = "textEn" if lang == "en" else "text"
    fallback = "text" if lang == "en" else "textEn"
    return record.get(key) or record.get(fallback) or ""


def render_optional_text(text: str) -> str:
    return tax.esc(text).replace("\n", "<br>")


def render_sources(sources: list[dict] | None) -> str:
    if not sources:
        return ""
    links = []
    for source in sources:
        label = source.get("text") or source.get("name") or source.get("url") or ""
        url = source.get("url") or "#"
        if not label:
            continue
        links.append(f'<span class="context-source"><a href="{tax.esc(url)}" target="_blank" rel="noopener">{tax.esc(label)} ↗</a></span>')
    return "".join(links)


def display_block(record: dict, lang: str) -> str:
    return render_optional_text(localize_block(record or {}, lang))


def display_era_title(era: dict, lang: str) -> str:
    return era.get("titleEn") if lang == "en" else era.get("title") or ""


def compact_era_period(era: dict) -> str:
    period = era.get("period") or era.get("id") or ""
    return period.replace(" — ", "–")


def compact_era_title(era: dict, lang: str) -> str:
    title = display_era_title(era, lang)
    if not title:
        return ""
    return title[:22] + "..." if len(title) > 22 else title


def card_search_index(photographer: dict, country_meta: dict, movements_meta: dict, lang: str) -> str:
    movement_names = [tax.localized_movement_name(m, movements_meta, lang) for m in photographer.get("movements") or []]
    values = [
        tax.display_name(photographer, lang),
        tax.display_alt_name(photographer, lang),
        tax.display_name(photographer, "ja"),
        tax.display_name(photographer, "en"),
        photographer.get("years") or "",
        country_meta.get("label") or "",
        country_meta.get("code") or "",
        *(movement_names or []),
    ]
    return tax.esc(" ".join(str(value) for value in values if value))


def display_meta(country_meta: dict) -> str:
    flag = country_meta.get("flag")
    code = country_meta.get("code")
    parts = []
    if flag:
        parts.append(tax.esc(flag))
    if code:
        parts.append(tax.esc(code))
    return " / ".join(parts) if parts else "—"


def render_card(
    photographer: dict,
    *,
    lang: str,
    all_photographers: list[dict],
    era_order: dict[str, int],
    movements_meta: dict,
    enrichments: dict,
    country_overrides: dict,
    essay_overrides: dict,
    photographer_order: dict[str, int],
    era_lookup: dict,
) -> str:
    country_meta = tax.photographer_country_meta(photographer, enrichments, country_overrides, lang)
    movement_names = [tax.localized_movement_name(m, movements_meta, lang) for m in photographer.get("movements") or []]
    compact_tags = "".join(f'<span class="card-tag">{tax.esc(name)}</span>' for name in movement_names[:2])
    if len(movement_names) > 2:
        compact_tags += f'<span class="card-tag card-tag-more">+{len(movement_names) - 2}</span>'
    years = tax.display_years(photographer, lang)
    name = tax.esc(tax.display_name(photographer, lang))
    alt = tax.display_alt_name(photographer, lang)
    alt_html = f'<div class="card-name-en">{tax.esc(alt)}</div>' if lang == "ja" and alt else ""
    summary = tax.photographer_short_lead(photographer, essay_overrides, movements_meta, enrichments, era_lookup, lang, 115)
    readmore = "Read details" if lang == "en" else "詳細を読む"
    coordinate_detail = "Details" if lang == "en" else "詳細"
    coordinate_button = "View in Coordinates" if lang == "en" else "座標で見る"
    placeholder = tax.strip_citation_markers(summary) in {"準備中。", "Coming soon.", "Essay coming soon.", "解説は準備中です。"}
    coordinate_html = ""
    if not placeholder:
        pid = tax.esc(photographer["id"])
        coordinate_html = f'<button class="coordinate-link" type="button" onclick="event.stopPropagation(); openCoordinatesForPhotographer(\'{pid}\')">{coordinate_button}</button>'
    related_people_html = render_card_related_people(
        photographer,
        all_photographers,
        era_order=era_order,
        lang=lang,
        movements_meta=movements_meta,
        enrichments=enrichments,
        country_overrides=country_overrides,
        photographer_order=photographer_order,
    )
    related_movements_html = render_card_related_movements(photographer, lang=lang, movements_meta=movements_meta)
    return f"""
    <div class="photographer-card{' placeholder' if placeholder else ''}" data-pid="{tax.esc(photographer['id'])}" data-nationality="{tax.esc(country_meta.get('nationality', ''))}" data-movements="{tax.esc(','.join(photographer.get('movements') or []))}" data-search="{card_search_index(photographer, country_meta, movements_meta, lang)}" data-placeholder="{'true' if placeholder else 'false'}" role="button" tabindex="0" onclick="toggleDetail('{tax.esc(photographer['id'])}', this)">
      <div class="card-action">
        <div class="card-action-label">{coordinate_detail}</div>
        <div class="card-arrow">↗</div>
      </div>
      <div class="card-flag-nat card-flag-nat-desktop">{display_meta(country_meta)}</div>
      <div class="card-mobile-meta">
        <div class="card-flag-nat">{display_meta(country_meta)}</div>
        <div class="card-years">{tax.esc(years)}</div>
      </div>
      <div class="card-mobile-title-line">
        <div class="card-name">{name}</div>
        <div class="card-mobile-chevron" aria-hidden="true">+</div>
      </div>
      {alt_html}
      <div class="card-years card-years-desktop">{tax.esc(years)}</div>
      <div class="card-tags"></div>
      <div class="mobile-card-tags">{compact_tags}</div>
      {coordinate_html}
      <div class="mobile-card-summary">
        <p class="mobile-card-summary-text">{tax.esc(summary)}</p>
        <a class="mobile-card-readmore" href="{tax.photographer_path(photographer, lang)}" onclick="event.stopPropagation()">{readmore}</a>
      </div>
      {related_movements_html}
      {related_people_html}
    </div>"""


def render_card_related_movements(photographer: dict, *, lang: str, movements_meta: dict) -> str:
    movements = photographer.get("movements") or []
    links = []
    for movement in movements[:3]:
        label = tax.esc(tax.localized_movement_name(movement, movements_meta, lang))
        slug = tax.esc(tax.movement_slug(movement, lang, movements_meta))
        links.append(f"<a href=\"#movement-{slug}\" onclick=\"event.stopPropagation(); openRecommendedMovement(event,'{slug}')\">{label}</a>")
    if not links:
        return ""
    label = "Related movements" if lang == "en" else "関連する運動"
    return f'<div class="card-related-movements"><span>{label}</span>{"".join(links)}</div>'


def render_card_related_people(
    photographer: dict,
    all_photographers: list[dict],
    *,
    era_order: dict[str, int],
    lang: str,
    movements_meta: dict,
    enrichments: dict,
    country_overrides: dict,
    photographer_order: dict[str, int],
) -> str:
    movement_set = set(photographer.get("movements") or [])
    country = tax.photographer_country_code(photographer, enrichments, country_overrides)
    target_era_index = era_order.get(photographer.get("era") or "", 999)
    target_order_index = photographer_order.get(photographer.get("id") or "", 9999)
    candidates = []
    for candidate in all_photographers:
        if candidate.get("id") == photographer.get("id"):
            continue
        shared = movement_set.intersection(candidate.get("movements") or [])
        same_era = candidate.get("era") == photographer.get("era")
        same_country = country and country == tax.photographer_country_code(candidate, enrichments, country_overrides)
        if not shared and not same_era and not same_country:
            continue
        era_gap = abs(era_order.get(candidate.get("era") or "", 999) - target_era_index)
        order_gap = abs(photographer_order.get(candidate.get("id") or "", 9999) - target_order_index)
        score = len(shared) * 100 + (18 if same_era else max(0, 10 - era_gap * 3)) + (6 if same_country else 0) - min(order_gap, 36)
        candidates.append((score, era_gap, order_gap, candidate))
    candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
    links = []
    for _score, _era_gap, _order_gap, candidate in candidates[:4]:
        pid = tax.esc(candidate.get("id") or "")
        label = tax.esc(tax.display_name(candidate, lang))
        links.append(f"<a href=\"#photographer-{pid}\" onclick=\"event.stopPropagation(); openRecommendedPhotographer(event,'{pid}')\">{label}</a>")
    if not links:
        return ""
    label = "Related" if lang == "en" else "関連人物"
    return f'<div class="card-related-people"><span>{label}</span>{"".join(links)}</div>'


def render_era_section(
    era: dict,
    photographers: list[dict],
    *,
    all_photographers: list[dict],
    era_order: dict[str, int],
    lang: str,
    movements_meta: dict,
    enrichments: dict,
    country_overrides: dict,
    essay_overrides: dict,
    photographer_order: dict[str, int],
    era_lookup: dict,
) -> str:
    cards = "".join(
        render_card(
            photographer,
            lang=lang,
            all_photographers=all_photographers,
            era_order=era_order,
            movements_meta=movements_meta,
            enrichments=enrichments,
            country_overrides=country_overrides,
            essay_overrides=essay_overrides,
            photographer_order=photographer_order,
            era_lookup=era_lookup,
        )
        for photographer in photographers
    ) or '<div class="photographer-card placeholder"><p>Coming soon.</p></div>'
    era_id = era.get("id") or ""
    after_dash = (era.get("period") or "").split("—")[-1].strip()
    labels = {
        "ja": {"world": "世界情勢", "photo": "写真と時代", "photographers": "この時代の写真家", "aria": "この時代の背景を読む"},
        "en": {"world": "World events", "photo": "Photography and era", "photographers": "Photographers in this era", "aria": "Read this era context"},
    }[lang]
    return f"""
  <section class="era" id="era-{tax.esc(era_id)}" data-era-id="{tax.esc(era_id)}">
    <div class="era-toggle" onclick="toggleEra('{tax.esc(era_id)}')">
      <div class="era-date">{tax.esc(era_id)}<span>— {tax.esc(after_dash)}</span></div>
      <div class="era-title" style="margin:0">{tax.esc(display_era_title(era, lang))}</div>
      <div class="era-toggle-arrow">▼</div>
    </div>
    <div class="mobile-era-sticky">{tax.esc(era_id)}</div>
    <div class="era-body">
      <div class="era-body-content">
        <div class="mobile-era-inline">
          <button class="mobile-era-inline-button" type="button" onclick="toggleMobileEraContext(event,'{tax.esc(era_id)}')" aria-label="{labels['aria']}">
            <span class="mobile-era-inline-period">{tax.esc(compact_era_period(era))}</span>
            {f'<span class="mobile-era-inline-title">{tax.esc(compact_era_title(era, lang))}</span>' if compact_era_title(era, lang) else ''}
            <span class="mobile-era-info-mark" aria-hidden="true">i</span>
          </button>
        </div>
        <div class="era-info">
          <div class="context-block">
            <div class="context-label">{labels['world']}</div>
            <div class="context-text">{display_block(era.get('worldEvents') or {{}}, lang)}</div>
            {render_sources((era.get('worldEvents') or {}).get('sources'))}
          </div>
          <div class="context-block">
            <div class="context-label">{labels['photo']}</div>
            <div class="context-text">{display_block(era.get('photoContext') or {{}}, lang)}</div>
            {render_sources((era.get('photoContext') or {}).get('sources'))}
          </div>
        </div>
        <div class="photographers-label">{labels['photographers']}</div>
        <div class="photographers-grid" id="grid-{tax.esc(era_id)}">{cards}</div>
        <div id="panels-{tax.esc(era_id)}"></div>
      </div>
    </div>
  </section>"""


def replace_between(text: str, start: str, end: str, replacement: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    return pattern.sub(start + replacement + end, text)


def update_archive(path: Path, lang: str, main_html: str, directory_html: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'<main id="era-main" class="container">.*?</main>', f'<main id="era-main" class="container">{main_html}\n  </main>', text, flags=re.S)
    text = replace_between(text, '<!-- ══════════════════════════════ FOOTER ══════════════════════════════ -->', '<footer>', "\n" + directory_html + "\n")
    text = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    photographers = tax.eval_js(
        ["data/photographers.js", "data/photographers-manual-additions.js", "data/photographers-supplement.js"],
        "PHOTOGRAPHERS",
    )
    photographers = [p for p in photographers if p["id"] not in tax.NON_PHOTOGRAPHER_IDS]
    movements_meta = tax.eval_js(["data/movements.js"], "MOVEMENTS_META")
    enrichments = tax.eval_js(["data/photographer-enrichments.js"], "window.PHOTOGRAPHER_ENRICHMENTS || PHOTOGRAPHER_ENRICHMENTS || {}")
    country_overrides = tax.eval_site_js_object("PHOTOGRAPHER_COUNTRY_OVERRIDES")
    essay_overrides = tax.eval_js(["data/photographer-essay-overrides.js"], "window.PHOTOGRAPHER_ESSAY_OVERRIDES || {}")
    eras = tax.eval_js(
        ["data/eras.js", "data/content-helpers.js", "data/future/era-1990s.js", "data/future/era-2000s.js", "data/future/era-2010s.js"],
        "ERAS",
    )
    era_lookup = {era["id"]: era for era in eras}
    era_order = {era["id"]: index for index, era in enumerate(eras)}
    photographer_order = {photographer["id"]: index for index, photographer in enumerate(photographers)}
    by_era: dict[str, list[dict]] = {}
    for photographer in photographers:
        by_era.setdefault(photographer.get("era"), []).append(photographer)

    all_nationalities = sorted(
        {
            tax.photographer_country_code(photographer, enrichments, country_overrides)
            for photographer in photographers
            if tax.photographer_country_code(photographer, enrichments, country_overrides)
        },
        key=lambda code: tax.country_label(code, "ja"),
    )

    for lang, rel in (("ja", "archive.html"), ("en", "en/archive.html")):
        sections = []
        for era in eras:
            people = by_era.get(era.get("id"), [])
            sections.append(
                render_era_section(
                    era,
                    people,
                    all_photographers=photographers,
                    era_order=era_order,
                    lang=lang,
                    movements_meta=movements_meta,
                    enrichments=enrichments,
                    country_overrides=country_overrides,
                    essay_overrides=essay_overrides,
                    photographer_order=photographer_order,
                    era_lookup=era_lookup,
                )
            )
        directory_html = tax.render_site_directory_nav(photographers, eras, all_nationalities, lang)
        update_archive(REPO / rel, lang, "\n".join(sections), directory_html)


if __name__ == "__main__":
    main()
