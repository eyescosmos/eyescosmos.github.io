#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
REPORT = REPO / "reports" / "seo-meta-report.csv"


def html_files() -> list[Path]:
    files: list[Path] = []
    for path in sorted(REPO.rglob("*.html")):
        rel = path.relative_to(REPO).as_posix()
        if rel.startswith("templates/"):
            continue
        if re.fullmatch(r"google[0-9a-f]+\.html", path.name):
            continue
        files.append(path)
    return files


def extract(pattern: str, text: str) -> str:
    match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    return (match.group(1).strip() if match else "")


def main() -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in html_files():
        rel = path.relative_to(REPO).as_posix()
        text = path.read_text(encoding="utf-8")
        robots = extract(r'<meta\s+name="robots"\s+content="(.*?)"', text)
        if "noindex" in robots.lower():
            continue
        title = extract(r"<title>(.*?)</title>", text)
        description = extract(r'<meta\s+name="description"\s+content="(.*?)"', text)
        lang = extract(r"<html\b[^>]*\blang=\"(.*?)\"", text) or "ja"
        canonical = extract(r'<link\s+rel="canonical"\s+href="(.*?)"', text)
        rows.append({
            "path": rel,
            "lang": lang,
            "title": title,
            "description": description,
            "canonical": canonical,
        })

    with REPORT.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["path", "lang", "title", "description", "canonical"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
