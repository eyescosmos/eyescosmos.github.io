#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re
from urllib.parse import quote


BASE_URL = "https://eyescosmos.github.io"
REPO_ROOT = Path(__file__).resolve().parents[1]
SITEMAP_PATH = REPO_ROOT / "sitemap.xml"

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


def xml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def build_sitemap() -> str:
    page_list = pages()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', f'<urlset xmlns="{SITEMAP_NS}">']
    for page in page_list:
        lines.append("  <url>")
        lines.append(f"    <loc>{xml_escape(page.url)}</loc>")
        lines.append(f"    <lastmod>{page.lastmod}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    SITEMAP_PATH.write_text(build_sitemap(), encoding="utf-8")
