#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

PHOTOGRAPHER_PAGE_GLOBS = (
    "photographers/*.html",
    "en/photographers/*.html",
)


def strip_tags(source: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", source)).strip()


def biography_text(source: str, heading: str) -> str:
    match = re.search(
        rf'<span class="ph-section__name">{re.escape(heading)}</span>.*?'
        rf'<div class="ph-section__body">\s*<div class="essay">(.*?)</div>',
        source,
        re.S,
    )
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
        if "Richard Avedon was born" in bio:
            failures.append("en/photographers/irving-penn.html: Richard Avedon biography text is mixed into Penn page")


def main() -> int:
    failures: list[str] = []

    for glob in PHOTOGRAPHER_PAGE_GLOBS:
        for path in sorted(REPO.glob(glob)):
            html = path.read_text(encoding="utf-8")
            check_one_character_external_links(path, html, failures)
            check_known_biography_starts(path, html, failures)

    if failures:
        print("Photographer link integrity check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Photographer link integrity check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
