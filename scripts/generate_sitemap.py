#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re
import xml.etree.ElementTree as ET


BASE_URL = "https://eyescosmos.github.io"
REPO_ROOT = Path(__file__).resolve().parents[1]
SITEMAP_PATH = REPO_ROOT / "sitemap.xml"

SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
XHTML_NS = "http://www.w3.org/1999/xhtml"

ET.register_namespace("", SITEMAP_NS)
ET.register_namespace("xhtml", XHTML_NS)


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
    return f"{BASE_URL}/{rel}"


def to_lastmod(path: Path) -> str:
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return mtime.date().isoformat()


def paired_rel(rel: str) -> str | None:
    if rel == "index.html":
        return "en/index.html"
    if rel == "en/index.html":
        return "index.html"
    if rel.startswith("en/"):
        partner = rel[3:]
    else:
        partner = f"en/{rel}"
    partner_path = REPO_ROOT / partner
    return partner if partner_path.exists() else None


def language_for_rel(rel: str) -> str:
    return "en" if rel.startswith("en/") else "ja"


def pages() -> list[Page]:
    return [
        Page(
            rel=path.relative_to(REPO_ROOT).as_posix(),
            url=to_url(path.relative_to(REPO_ROOT).as_posix()),
            lastmod=to_lastmod(path),
        )
        for path in html_files()
    ]


def build_sitemap() -> ET.ElementTree:
    page_list = pages()
    page_map = {page.rel: page for page in page_list}
    root = ET.Element(ET.QName(SITEMAP_NS, "urlset"))

    for page in page_list:
        url_el = ET.SubElement(root, ET.QName(SITEMAP_NS, "url"))
        ET.SubElement(url_el, ET.QName(SITEMAP_NS, "loc")).text = page.url
        ET.SubElement(url_el, ET.QName(SITEMAP_NS, "lastmod")).text = page.lastmod

        partner_rel = paired_rel(page.rel)
        if partner_rel and partner_rel in page_map:
            partner = page_map[partner_rel]
            current_lang = language_for_rel(page.rel)
            partner_lang = language_for_rel(partner.rel)
            ET.SubElement(
                url_el,
                ET.QName(XHTML_NS, "link"),
                rel="alternate",
                hreflang=current_lang,
                href=page.url,
            )
            ET.SubElement(
                url_el,
                ET.QName(XHTML_NS, "link"),
                rel="alternate",
                hreflang=partner_lang,
                href=partner.url,
            )
            default_url = page.url if current_lang == "ja" else partner.url
            ET.SubElement(
                url_el,
                ET.QName(XHTML_NS, "link"),
                rel="alternate",
                hreflang="x-default",
                href=default_url,
            )

    return ET.ElementTree(root)


if __name__ == "__main__":
    tree = build_sitemap()
    tree.write(SITEMAP_PATH, encoding="UTF-8", xml_declaration=True)
