#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlsplit, urlunsplit
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
    alternates: dict[str, str]


def html_files() -> list[Path]:
    files: list[Path] = []
    for path in sorted(REPO_ROOT.rglob("*.html")):
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel.startswith("templates/"):
            continue
        if re.fullmatch(r"google[0-9a-f]+\.html", path.name):
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        if re.search(r'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']*noindex', content, re.I):
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


def counterpart_rel(rel: str) -> tuple[str, str] | None:
    pairs = (
        ("photographers/", "en/photographers/"),
        ("eras/", "en/eras/"),
        ("countries/", "en/countries/"),
        ("movements/", "en/movements/"),
    )
    if rel == "index.html":
        return "index.html", "en/index.html"
    if rel == "en/index.html":
        return "index.html", "en/index.html"
    if rel == "archive.html":
        return "archive.html", "en/archive.html"
    if rel == "en/archive.html":
        return "archive.html", "en/archive.html"
    for ja_prefix, en_prefix in pairs:
        if rel.startswith(ja_prefix):
            return rel, en_prefix + rel[len(ja_prefix):]
        if rel.startswith(en_prefix):
            return ja_prefix + rel[len(en_prefix):], rel
    return None


def alternate_urls(rel: str, existing: set[str]) -> dict[str, str]:
    pair = counterpart_rel(rel)
    if not pair:
        return {}
    ja_rel, en_rel = pair
    if ja_rel not in existing or en_rel not in existing:
        return {}
    return {
        "ja": to_url(ja_rel),
        "en": to_url(en_rel),
        "x-default": to_url(ja_rel),
    }


def encode_url(url: str) -> str:
    parts = urlsplit(url)
    encoded_path = quote(parts.path, safe="/-_.~%")
    return urlunsplit((parts.scheme, parts.netloc, encoded_path, parts.query, parts.fragment))


def alternate_urls_from_html(path: Path) -> dict[str, str]:
    content = path.read_text(encoding="utf-8", errors="ignore")
    alternates: dict[str, str] = {}
    for hreflang, href in re.findall(
        r'<link\s+rel=["\']alternate["\']\s+hreflang=["\']([^"\']+)["\']\s+href=["\']([^"\']+)["\']',
        content,
        re.I,
    ):
        alternates[hreflang] = encode_url(href)
    return alternates


def pages() -> list[Page]:
    file_list = html_files()
    existing = {path.relative_to(REPO_ROOT).as_posix() for path in file_list}
    return [
        Page(
            rel=path.relative_to(REPO_ROOT).as_posix(),
            url=to_url(path.relative_to(REPO_ROOT).as_posix()),
            lastmod=to_lastmod(path),
            alternates=alternate_urls_from_html(path) or alternate_urls(path.relative_to(REPO_ROOT).as_posix(), existing),
        )
        for path in file_list
    ]


def render_urlset(page_list: list[Page]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<urlset xmlns="{SITEMAP_NS}"',
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ]
    for page in page_list:
        lines.append("  <url>")
        lines.append(f"    <loc>{xml_escape(page.url)}</loc>")
        lines.append(f"    <lastmod>{page.lastmod}</lastmod>")
        for hreflang, href in page.alternates.items():
            lines.append(f'    <xhtml:link rel="alternate" hreflang="{hreflang}" href="{xml_escape(href)}"/>')
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def write_sitemaps() -> None:
    page_list = pages()
    SITEMAP_ROOT_PATH.write_text(render_urlset(page_list), encoding="utf-8")


if __name__ == "__main__":
    write_sitemaps()
