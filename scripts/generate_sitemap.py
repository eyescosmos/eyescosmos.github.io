#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
import re


BASE_URL = "https://eyescosmos.github.io"
REPO_ROOT = Path(__file__).resolve().parents[1]
SITEMAP_ROOT_PATH = REPO_ROOT / "sitemap.xml"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


@dataclass(frozen=True)
class Page:
    rel: str
    url: str
    lastmod: str


def html_files() -> list[Path]:
    files: list[Path] = []
    for path in sorted(REPO_ROOT.rglob("*.html")):
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel.startswith("templates/"):
            continue
        if re.fullmatch(r"google[0-9a-f]+\.html", path.name):
            continue
        files.append(path)
    return files


def xml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def to_url(rel: str) -> str:
    if rel == "index.html":
        return f"{BASE_URL}/"
    if rel == "en/index.html":
        return f"{BASE_URL}/en/"
    encoded_rel = quote(rel, safe="/-_.~")
    return f"{BASE_URL}/{encoded_rel}"


def to_lastmod(path: Path) -> str:
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return mtime.date().isoformat()


def pages() -> list[Page]:
    return [
        Page(
            rel=path.relative_to(REPO_ROOT).as_posix(),
            url=to_url(path.relative_to(REPO_ROOT).as_posix()),
            lastmod=to_lastmod(path),
        )
        for path in html_files()
    ]


def render_urlset(page_list: list[Page]) -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', f'<urlset xmlns="{SITEMAP_NS}">']
    for page in page_list:
        lines.append("  <url>")
        lines.append(f"    <loc>{xml_escape(page.url)}</loc>")
        lines.append(f"    <lastmod>{page.lastmod}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def group_pages(page_list: list[Page]) -> dict[str, list[Page]]:
    groups = {
        "sitemap-main.xml": [],
        "sitemap-photographers-ja.xml": [],
        "sitemap-photographers-en.xml": [],
    }
    for page in page_list:
        if page.rel.startswith("photographers/"):
            groups["sitemap-photographers-ja.xml"].append(page)
        elif page.rel.startswith("en/photographers/"):
            groups["sitemap-photographers-en.xml"].append(page)
        else:
            groups["sitemap-main.xml"].append(page)
    return groups


def write_sitemaps() -> None:
    page_list = pages()
    page_groups = group_pages(page_list)

    for filename, group in page_groups.items():
        path = REPO_ROOT / filename
        path.write_text(render_urlset(group), encoding="utf-8")

    SITEMAP_ROOT_PATH.write_text(render_urlset(page_list), encoding="utf-8")


if __name__ == "__main__":
    write_sitemaps()
