#!/usr/bin/env python3
"""Surgically link entry-meta country names and keyword chips on photographer
pages, without regenerating them (the JA pages are the hand-maintained
source of truth; essays / sources / book cards must be preserved).

For every photographers/*.html (JA) and en/photographers/*.html (EN):
  - entry-meta <dt>Country</dt><dd>…</dd>: link each country name to its
    single country page when that page exists (composite-only countries
    such as Slovakia/Lithuania have no single page → stay plain text).
  - keyword chips (.ph-kw and the sidebar "Keywords" block .ph-side-chip):
    link to the matching movement page when one exists; otherwise plain.

Idempotent: re-running produces no further changes.
"""
from __future__ import annotations

import glob
import html as _html
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import generate_taxonomy_pages as tax  # noqa: E402  (COUNTRY_BASE_META)

BASE = tax.COUNTRY_BASE_META
JA_NAME2CODE = {m["ja_name"]: c for c, m in BASE.items()}
EN_NAME2CODE = {m["en_name"]: c for c, m in BASE.items()}

NAT = {p["id"]: (p.get("nationality") or "")
       for p in json.loads((REPO / "card-data.json").read_text(encoding="utf-8"))["photographers"]}


def esc(s: str) -> str:
    return _html.escape(s, quote=False)


def slugify_en(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


# ── country ────────────────────────────────────────────────────────────────

def country_dd_inner(pid: str, current_inner: str, lang: str) -> str:
    base = "en/countries" if lang == "en" else "countries"
    namekey = "en_name" if lang == "en" else "ja_name"
    plain = re.sub(r"<[^>]+>", "", current_inner).strip()  # strip existing links (idempotent)

    pairs: list[tuple[dict | None, str]] = []
    nat = NAT.get(pid, "")
    if nat:
        for code in [c.strip() for c in nat.split("/") if c.strip()]:
            pairs.append((BASE.get(code), code))
    else:
        rev = EN_NAME2CODE if lang == "en" else JA_NAME2CODE
        for name in [n.strip() for n in re.split(r"\s*/\s*", plain) if n.strip()]:
            pairs.append((BASE.get(rev.get(name, "")), name))

    out = []
    for meta, fallback in pairs:
        if not meta:
            out.append(esc(fallback))
            continue
        name = meta[namekey]
        slug = meta["slug"]
        if (REPO / base / f"{slug}.html").exists():
            out.append(f'<a href="/{base}/{slug}.html">{esc(name)}</a>')
        else:
            out.append(esc(name))
    return " / ".join(out) if out else current_inner


def patch_country(html_text: str, pid: str, lang: str) -> str:
    def repl(m):
        return m.group(1) + country_dd_inner(pid, m.group(2), lang) + m.group(3)
    return re.sub(r"(<dt>Country</dt><dd>)(.*?)(</dd>)", repl, html_text, flags=re.S)


# ── keywords ─────────────────────────────────────────────────────────────--

def movement_href(keyword: str, lang: str) -> str | None:
    if lang == "en":
        slug = slugify_en(keyword)
        return f"/en/movements/{slug}.html" if (REPO / "en" / "movements" / f"{slug}.html").exists() else None
    return f"/movements/{keyword}.html" if (REPO / "movements" / f"{keyword}.html").exists() else None


def link_chips(segment: str, classes: str, lang: str) -> str:
    def repl(m):
        cls, inner = m.group(1), m.group(2)
        href = movement_href(inner.strip(), lang)
        if not href:
            return m.group(0)
        return f'<span class="{cls}"><a href="{href}">{inner}</a></span>'
    # [^<]+ guarantees we only touch plain (unlinked) chips → idempotent
    return re.sub(rf'<span class="({classes})">([^<]+)</span>', repl, segment)


SIDEBAR_KW_RE = re.compile(
    r'(<div class="ph-side-block__head">Keywords[^<]*</div>.*?</div>\s*</div>)', re.S)


def patch_keywords(html_text: str, lang: str) -> str:
    # 1) top keyword line (.ph-kw appears only here)
    html_text = link_chips(html_text, "ph-kw", lang)
    # 2) sidebar "Keywords" block chips only (scope so Movements block is untouched)
    def block_repl(m):
        return link_chips(m.group(1), r"ph-side-chip(?: is-primary)?", lang)
    return SIDEBAR_KW_RE.sub(block_repl, html_text)


def process(path: Path, lang: str) -> bool:
    pid = path.stem
    original = path.read_text(encoding="utf-8")
    updated = patch_country(original, pid, lang)
    updated = patch_keywords(updated, lang)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    total = 0
    for lang, root in (("ja", "photographers"), ("en", "en/photographers")):
        for f in sorted(glob.glob(str(REPO / root / "*.html"))):
            if f.endswith("-backup.html"):
                continue
            total += 1
            if process(Path(f), lang):
                changed += 1
    print(f"Processed {total} pages, changed {changed}")


if __name__ == "__main__":
    main()
