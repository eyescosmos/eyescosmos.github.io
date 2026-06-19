#!/usr/bin/env python3
"""Fill narrowly-scoped SEO gaps in hand-maintained JA photographer pages.

The JA photographer HTML files are the source of truth. This script is
idempotent and surgical:
  - edits only SEO tags inside <head>
  - adds data-nosnippet only to UI chrome / search / navigation wrappers and
    card CTA chrome
  - never rewrites essay/source/book/work-link content

Dry-run by default. Pass --apply to write files.
"""
from __future__ import annotations

import argparse
import glob
import re
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SITE = "https://eyescosmos.github.io"
TARGET_GLOB = "photographers/*.html"


@dataclass
class PageResult:
    path: Path
    changed: bool = False
    changes: list[str] = field(default_factory=list)
    skipped: str | None = None


def collect_files() -> list[Path]:
    return [Path(p) for p in sorted(glob.glob(str(REPO / TARGET_GLOB)))]


def is_redirect_or_noindex(html: str) -> bool:
    return bool(
        re.search(r'http-equiv\s*=\s*["\']refresh["\']', html, flags=re.I)
        or re.search(r'<meta\b[^>]*name\s*=\s*["\']robots["\'][^>]*content\s*=\s*["\'][^"\']*noindex', html, flags=re.I)
    )


def skip_reason(path: Path, html: str) -> str | None:
    if path.name.endswith("-backup.html"):
        return "backup file"
    if path.name.startswith("google") or "google-site-verification" in html:
        return "Google site verification"
    if is_redirect_or_noindex(html):
        return "redirect stub / noindex"
    if not re.search(r"</head\s*>", html, flags=re.I):
        return "no </head> found"
    return None


def split_head(html: str) -> tuple[str, str, str] | None:
    match = re.search(r"(<head\b[^>]*>)(.*?)(</head\s*>)", html, flags=re.I | re.S)
    if not match:
        return None
    return match.group(1), match.group(2), match.group(3)


def attr_value(tag: str, name: str) -> str | None:
    match = re.search(rf'\b{name}\s*=\s*(["\'])(.*?)\1', tag, flags=re.I | re.S)
    return match.group(2) if match else None


def has_attr(tag: str, name: str) -> bool:
    return bool(re.search(rf"\s{name}(?:\s|=|/?>)", tag, flags=re.I))


def add_attr(tag: str, attr: str) -> str:
    if has_attr(tag, attr.split("=", 1)[0]):
        return tag
    if tag.endswith("/>"):
        return tag[:-2].rstrip() + f" {attr}/>"
    return tag[:-1].rstrip() + f" {attr}>"


def remove_head_tags(head: str, predicate) -> str:
    def repl(match: re.Match[str]) -> str:
        tag = match.group(0)
        return "" if predicate(tag) else tag

    return re.sub(r"<(?:link|meta)\b[^>]*>\n?", repl, head, flags=re.I)


def canonical_url(slug: str) -> str:
    return f"{SITE}/photographers/{slug}.html"


def en_url(slug: str) -> str:
    return f"{SITE}/en/photographers/{slug}.html"


def meta_content(head: str, *, name: str | None = None, prop: str | None = None) -> str | None:
    for tag in re.findall(r"<meta\b[^>]*>", head, flags=re.I):
        if name and (attr_value(tag, "name") or "").lower() != name.lower():
            continue
        if prop and (attr_value(tag, "property") or "").lower() != prop.lower():
            continue
        content = attr_value(tag, "content")
        if content:
            return content
    return None


def title_text(head: str) -> str | None:
    match = re.search(r"<title\b[^>]*>(.*?)</title\s*>", head, flags=re.I | re.S)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(1)).strip()


def insert_after_title_or_viewport(head: str, block: str) -> str:
    title = re.search(r"</title\s*>", head, flags=re.I)
    if title:
        return head[: title.end()] + "\n" + block + head[title.end():]
    viewport = re.search(r"<meta\b[^>]*name\s*=\s*['\"]viewport['\"][^>]*>\n?", head, flags=re.I)
    if viewport:
        return head[: viewport.end()] + block + "\n" + head[viewport.end():]
    return "\n" + block + head


def upsert_canonical_and_og(head: str, slug: str) -> tuple[str, bool]:
    url = canonical_url(slug)
    changed = False
    tags: list[str] = []

    if not re.search(r"<link\b[^>]*rel\s*=\s*['\"]canonical['\"][^>]*>", head, flags=re.I):
        tags.append(f'<link rel="canonical" href="{url}">')

    if not re.search(r"<meta\b[^>]*name\s*=\s*['\"]robots['\"][^>]*>", head, flags=re.I):
        tags.append('<meta name="robots" content="index, follow">')

    title = title_text(head)
    description = meta_content(head, name="description")
    og_description = meta_content(head, prop="og:description") or description
    twitter_description = meta_content(head, name="twitter:description") or description

    og_defs: list[tuple[str, str]] = [
        ("og:type", "article"),
        ("og:site_name", "写真の座標"),
        ("og:url", url),
        ("og:locale", "ja_JP"),
    ]
    if title:
        og_defs.insert(2, ("og:title", title))
    if og_description:
        og_defs.insert(3 if title else 2, ("og:description", og_description))

    for prop, content in og_defs:
        if not re.search(rf"<meta\b[^>]*property\s*=\s*['\"]{re.escape(prop)}['\"][^>]*>", head, flags=re.I):
            tags.append(f'<meta property="{prop}" content="{content}">')

    if not re.search(r"<meta\b[^>]*name\s*=\s*['\"]twitter:card['\"][^>]*>", head, flags=re.I):
        tags.append('<meta name="twitter:card" content="summary">')
    if title and not re.search(r"<meta\b[^>]*name\s*=\s*['\"]twitter:title['\"][^>]*>", head, flags=re.I):
        tags.append(f'<meta name="twitter:title" content="{title}">')
    if twitter_description and not re.search(r"<meta\b[^>]*name\s*=\s*['\"]twitter:description['\"][^>]*>", head, flags=re.I):
        tags.append(f'<meta name="twitter:description" content="{twitter_description}">')

    if tags:
        head = insert_after_title_or_viewport(head, "\n".join(tags))
        changed = True

    # Canonical / OG URL are machine-derived from slug; correct stale values.
    def replace_href(match: re.Match[str]) -> str:
        tag = match.group(0)
        new = re.sub(r'\bhref\s*=\s*(["\']).*?\1', f'href="{url}"', tag, count=1, flags=re.I | re.S)
        return new

    def replace_content(match: re.Match[str]) -> str:
        tag = match.group(0)
        new = re.sub(r'\bcontent\s*=\s*(["\']).*?\1', f'content="{url}"', tag, count=1, flags=re.I | re.S)
        return new

    new_head = re.sub(r"<link\b[^>]*rel\s*=\s*['\"]canonical['\"][^>]*>", replace_href, head, flags=re.I)
    new_head = re.sub(r"<meta\b[^>]*property\s*=\s*['\"]og:url['\"][^>]*>", replace_content, new_head, flags=re.I)
    if new_head != head:
        head = new_head
        changed = True

    return head, changed


def upsert_hreflang(head: str, slug: str) -> tuple[str, bool]:
    if not (REPO / "en" / "photographers" / f"{slug}.html").exists():
        return head, False

    block = "\n".join(
        [
            f'<link rel="alternate" hreflang="ja" href="{canonical_url(slug)}">',
            f'<link rel="alternate" hreflang="en" href="{en_url(slug)}">',
            f'<link rel="alternate" hreflang="x-default" href="{canonical_url(slug)}">',
        ]
    )

    without = remove_head_tags(
        head,
        lambda tag: tag.lower().startswith("<link")
        and (attr_value(tag, "rel") or "").lower() == "alternate"
        and attr_value(tag, "hreflang") in {"ja", "en", "x-default"},
    )
    if block in without:
        return head, False

    canonical = re.search(r"<link\b[^>]*rel\s*=\s*['\"]canonical['\"][^>]*>\n?", without, flags=re.I)
    if canonical:
        new_head = without[: canonical.end()] + block + "\n" + without[canonical.end():]
    else:
        new_head = insert_after_title_or_viewport(without, block)
    return new_head, new_head != head


def patch_head(html: str, slug: str) -> tuple[str, list[str]]:
    parts = split_head(html)
    if not parts:
        return html, []
    open_head, head, close_head = parts
    changes: list[str] = []

    head, changed = upsert_canonical_and_og(head, slug)
    if changed:
        changes.append("canonical/og")

    head, changed = upsert_hreflang(head, slug)
    if changed:
        changes.append("hreflang")

    new_html = html.replace(open_head + parts[1] + close_head, open_head + head + close_head, 1)
    return new_html, changes


NOSNIPPET_CLASSES = {
    "head__mobile-search",
    "ph-side-search",
    "ph-search-suggestions",
    "ph-toc",
    "pc-top",
    "pc-body__cta",
}

NOSNIPPET_CLASS_PATTERNS = [
    r"(?:^|\s)[\w-]*toolbar[\w-]*(?:\s|$)",
    r"(?:^|\s)[\w-]*count[\w-]*(?:\s|$)",
]


def is_nosnippet_target(tag: str) -> bool:
    name_match = re.match(r"<\s*([a-zA-Z0-9:-]+)\b", tag)
    name = name_match.group(1).lower() if name_match else ""
    cls = attr_value(tag, "class") or ""

    if name in {"header", "nav", "footer"}:
        return True
    classes = set(cls.split())
    if classes & NOSNIPPET_CLASSES:
        return True
    return any(re.search(pattern, cls) for pattern in NOSNIPPET_CLASS_PATTERNS)


def patch_nosnippet(html: str) -> tuple[str, bool]:
    parts = split_head(html)
    if not parts:
        return html, False
    head_full = "".join(parts)
    body_start = html.find(head_full) + len(head_full)
    prefix, body = html[:body_start], html[body_start:]

    def repl(match: re.Match[str]) -> str:
        tag = match.group(0)
        if has_attr(tag, "data-nosnippet") or not is_nosnippet_target(tag):
            return tag
        return add_attr(tag, "data-nosnippet")

    new_body = re.sub(r"<(?:header|nav|footer|div|span|section|aside|details|summary|ul|li|form|label|button)\b[^>]*>", repl, body, flags=re.I)
    return prefix + new_body, new_body != body


def process_file(path: Path) -> PageResult:
    result = PageResult(path=path)
    html = path.read_text(encoding="utf-8", errors="replace")
    reason = skip_reason(path, html)
    if reason:
        result.skipped = reason
        return result

    slug = path.stem
    updated, changes = patch_head(html, slug)
    updated, nosnippet_changed = patch_nosnippet(updated)
    if nosnippet_changed:
        changes.append("nosnippet")

    result.changed = updated != html
    result.changes = changes
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = parser.parse_args()

    results: list[PageResult] = []
    for path in collect_files():
        result = process_file(path)
        results.append(result)
        if args.apply and result.changed and not result.skipped:
            html = path.read_text(encoding="utf-8", errors="replace")
            updated, _ = patch_head(html, path.stem)
            updated, _ = patch_nosnippet(updated)
            path.write_text(updated, encoding="utf-8")

    changed = [r for r in results if r.changed]
    skipped = [r for r in results if r.skipped]
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"Mode: {mode}")
    print(f"Candidate files: {len(results)}")
    print(f"Would change: {len(changed)}" if not args.apply else f"Changed: {len(changed)}")

    counts: dict[str, int] = {}
    for result in changed:
        for change in result.changes:
            counts[change] = counts.get(change, 0) + 1
    print("\n=== CHANGE CATEGORIES ===")
    for key in ("hreflang", "nosnippet", "canonical/og"):
        print(f"  {key}: {counts.get(key, 0)} files")

    print("\n=== SKIPPED ===")
    skip_counts: dict[str, int] = {}
    for result in skipped:
        skip_counts[result.skipped or "unknown"] = skip_counts.get(result.skipped or "unknown", 0) + 1
    for reason, count in sorted(skip_counts.items()):
        print(f"  {reason}: {count} files")
    for result in skipped:
        print(f"    [{result.skipped}] {result.path.relative_to(REPO)}")

    print("\n=== FILES ===")
    for result in changed:
        rel = result.path.relative_to(REPO)
        print(f"  {rel}: {', '.join(result.changes)}")


if __name__ == "__main__":
    main()
