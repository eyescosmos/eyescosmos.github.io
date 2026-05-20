#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import generate_photographer_pages as generator  # noqa: E402


WORKS_REQUIRED_IDS = {
    "ansel-adams",
    "arbus",
    "beate-gutschow",
    "cameron",
    "cartierbresson",
    "edward-weston",
    "ernest-cole",
    "eugenesmith",
    "evans",
    "hiroshi-sugimoto",
    "irving-penn",
    "lee-miller",
    "michio-hoshino",
    "moriyama",
    "parr",
    "pieter-hugo",
    "renger",
    "richard-avedon",
    "robertfrank",
    "sherman",
    "tokuko-ushioda",
    "wolfgang-tillmans",
}

RESTORED_EXTERNAL_LINK_IDS = {
    "edward-weston",
    "hiroshi-sugimoto",
    "irving-penn",
    "richard-avedon",
}

PHOTOGRAPHER_PAGE_GLOBS = (
    "photographers/*.html",
    "en/photographers/*.html",
)


def section_html(source: str, heading: str) -> str:
    match = re.search(
        rf"<section class=\"section\"><h2>{re.escape(heading)}</h2><div class=\"links\">(.*?)</div></section>",
        source,
        re.S,
    )
    return match.group(1) if match else ""


def strip_tags(source: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", source)).strip()


def biography_text(source: str, heading: str) -> str:
    match = re.search(
        rf"<section class=\"section\">\s*<h2>{re.escape(heading)}</h2>\s*<div class=\"essay\">(.*?)</div>\s*</section>",
        source,
        re.S,
    )
    return strip_tags(match.group(1)) if match else ""


def h1_text(source: str) -> str:
    match = re.search(r"<h1 class=\"title\">(.*?)</h1>", source, re.S)
    return strip_tags(match.group(1)) if match else ""


def check_one_character_external_links(path: Path, html: str, failures: list[str]) -> None:
    for match in re.finditer(r"<a\b([^>]*)>(.*?)</a>", html, re.S):
        attrs, body = match.groups()
        href_match = re.search(r'href="([^"]+)"', attrs)
        if not href_match or not href_match.group(1).startswith(("http://", "https://")):
            continue
        text = strip_tags(body).replace("↗", "").strip()
        if len(text) == 1:
            failures.append(
                f"{path.relative_to(REPO)}: one-character external link text {text!r} -> {href_match.group(1)}"
            )


def check_known_biography_starts(path: Path, html: str, failures: list[str]) -> None:
    if path.parts[-3:] == ("en", "photographers", "richard-avedon.html"):
        bio = biography_text(html, "Biography")
        if not bio.startswith("Richard Avedon"):
            failures.append("en/photographers/richard-avedon.html: Biography does not start with Richard Avedon")
        if "Irving Penn was born" in bio:
            failures.append("en/photographers/richard-avedon.html: Irving Penn biography text is mixed into Avedon page")
    if path.parts[-3:] == ("en", "photographers", "irving-penn.html"):
        bio = biography_text(html, "Biography")
        if not bio.startswith("Irving Penn"):
            failures.append("en/photographers/irving-penn.html: Biography does not start with Irving Penn")


def check_photobook_heading(path: Path, html: str, failures: list[str]) -> None:
    if path.parts[-3] == "en":
        h1 = h1_text(html)
        for heading in re.findall(r"<h2>([^<]*Photobooks)</h2>", html):
            if h1 and h1 not in strip_tags(heading):
                failures.append(f"{path.relative_to(REPO)}: photobook heading may not match H1 ({heading!r})")


def main() -> int:
    overrides = generator.load_essay_overrides()
    failures: list[str] = []

    for photographer_id in sorted(WORKS_REQUIRED_IDS):
        works = (overrides.get(photographer_id) or {}).get("works") or []
        if not works:
            failures.append(f"{photographer_id}: missing works in data/photographer-essay-overrides.js")

        for lang, rel_path, heading in (
            ("ja", f"photographers/{photographer_id}.html", "関連作品"),
            ("en", f"en/photographers/{photographer_id}.html", "Notable works"),
        ):
            path = REPO / rel_path
            if not path.exists():
                failures.append(f"{photographer_id}: missing generated {lang} page at {rel_path}")
                continue
            html = path.read_text(encoding="utf-8")
            works_html = section_html(html, heading)
            if not works_html or "chip-link" not in works_html:
                failures.append(f"{photographer_id}: missing generated {lang} works section")

    for photographer_id in sorted(RESTORED_EXTERNAL_LINK_IDS):
        links = (overrides.get(photographer_id) or {}).get("links") or []
        if not links:
            failures.append(f"{photographer_id}: restored external links missing from source data")
        for lang, rel_path, placeholder in (
            ("ja", f"photographers/{photographer_id}.html", "外部リンクは準備中です。"),
            ("en", f"en/photographers/{photographer_id}.html", "External links coming soon."),
        ):
            html = (REPO / rel_path).read_text(encoding="utf-8")
            if placeholder in html:
                failures.append(f"{photographer_id}: generated {lang} page has empty external links")

    for glob in PHOTOGRAPHER_PAGE_GLOBS:
        for path in sorted(REPO.glob(glob)):
            html = path.read_text(encoding="utf-8")
            check_one_character_external_links(path, html, failures)
            check_known_biography_starts(path, html, failures)
            check_photobook_heading(path, html, failures)

    if failures:
        print("Photographer link integrity check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Photographer link integrity check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
