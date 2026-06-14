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
    Additionally handles:
    (a) alias chips (e.g. "FSA" → FSA写真, "Conceptual" → conceptual-art)
    (b) country-name chips (e.g. "アメリカ", "United States") → country pages
    (c) slash-composite chips (e.g. "デンマーク / アメリカ") → resolve per part

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

# Alias maps: chip text → movement page stem/slug.
# Applies only when the exact text appears and the target page exists.
# Strict: exact match only; do not add entries without verifying page existence.
JA_MOVEMENT_ALIASES: dict[str, str] = {
    "コンセプチュアル": "コンセプチュアルアート",
    "FSA": "FSA写真",
    "Bauhaus": "バウハウス",
    "Provoke": "プロヴォーク",
}

EN_MOVEMENT_ALIASES: dict[str, str] = {
    "Conceptual": "conceptual-art",
    "FSA": "fsa-photography",
}


def movement_href(keyword: str, lang: str) -> str | None:
    """Return href for keyword if a movement page exists (exact match only)."""
    if lang == "en":
        slug = slugify_en(keyword)
        if (REPO / "en" / "movements" / f"{slug}.html").exists():
            return f"/en/movements/{slug}.html"
        return None
    if (REPO / "movements" / f"{keyword}.html").exists():
        return f"/movements/{keyword}.html"
    return None


def alias_movement_href(keyword: str, lang: str) -> str | None:
    """Return href via alias map when keyword has a name-variant for a movement."""
    if lang == "en":
        stem = EN_MOVEMENT_ALIASES.get(keyword)
        if stem and (REPO / "en" / "movements" / f"{stem}.html").exists():
            return f"/en/movements/{stem}.html"
    else:
        stem = JA_MOVEMENT_ALIASES.get(keyword)
        if stem and (REPO / "movements" / f"{stem}.html").exists():
            return f"/movements/{stem}.html"
    return None


def country_chip_href(keyword: str, lang: str) -> str | None:
    """Return href if keyword is an exact country name with a single country page."""
    name2code = EN_NAME2CODE if lang == "en" else JA_NAME2CODE
    code = name2code.get(keyword)
    if not code:
        return None
    meta = BASE.get(code)
    if not meta:
        return None
    slug = meta["slug"]
    base = "en/countries" if lang == "en" else "countries"
    if (REPO / base / f"{slug}.html").exists():
        return f"/{base}/{slug}.html"
    return None


def chip_href(keyword: str, lang: str) -> str | None:
    """Resolve a chip keyword to an href using priority order:
    1. Movement exact match
    2. Movement alias match
    3. Country name exact match
    Returns None if no match.
    """
    return (
        movement_href(keyword, lang)
        or alias_movement_href(keyword, lang)
        or country_chip_href(keyword, lang)
    )


def resolve_chip_inner(inner: str, lang: str) -> str:
    """Resolve a chip's inner HTML (which may contain ' / ' separated parts).

    - If inner contains ' / ', split and resolve each part independently.
      Parts that resolve get wrapped in <a>; unresolved parts stay plain.
      Results are joined with ' / '.
    - If no slash, resolve as a single keyword.
    - Already-linked inner (contains '<') is returned unchanged (idempotent).
    """
    if "<" in inner:
        # Already linked (or contains HTML) — skip to preserve idempotency
        return inner

    stripped = inner.strip()
    if " / " in stripped:
        parts = stripped.split(" / ")
        out = []
        for part in parts:
            href = chip_href(part.strip(), lang)
            if href:
                out.append(f'<a href="{href}">{esc(part)}</a>')
            else:
                out.append(esc(part))
        return " / ".join(out)
    else:
        href = chip_href(stripped, lang)
        if href:
            return f'<a href="{href}">{inner}</a>'
        return inner


def link_chips(segment: str, classes: str, lang: str) -> str:
    def repl(m):
        cls, inner = m.group(1), m.group(2)
        new_inner = resolve_chip_inner(inner, lang)
        if new_inner == inner:
            return m.group(0)
        return f'<span class="{cls}">{new_inner}</span>'
    # [^<]+ guarantees we only touch plain (unlinked) chips → idempotent
    # For slash-composite chips we need to allow ' / ' inside, so we use [^<]+
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
