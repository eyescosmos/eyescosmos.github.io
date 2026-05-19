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


def section_html(source: str, heading: str) -> str:
    match = re.search(
        rf"<section class=\"section\"><h2>{re.escape(heading)}</h2><div class=\"links\">(.*?)</div></section>",
        source,
        re.S,
    )
    return match.group(1) if match else ""


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

    if failures:
        print("Photographer link integrity check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Photographer link integrity check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
