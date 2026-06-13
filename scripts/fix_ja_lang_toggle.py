#!/usr/bin/env python3
"""Fix the inert EN button in the head__lang toggle on Japanese pages.

JA pages render `<button>EN</button>` with no link, so JP→EN switching is dead.
EN pages already link back to JA. We build an authoritative JA→EN filename map by
reading each EN page's own "JP" link (which points to its JA source), then wrap the
inert EN button in an anchor to that EN page.

Scope: photographers, movements, eras (JA side). Countries are EXCLUDED on purpose
(Codex is actively editing them).
"""
import glob
import os
import re
import sys
import urllib.parse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TYPES = ["photographers", "movements", "eras"]
TOGGLE_RE = re.compile(r'<div class="head__lang">.*?</div>', re.S)
ANCHOR_RE = re.compile(r'<a\b[^>]*\bhref="([^"]*)"[^>]*>(.*?)</a>', re.S)
APPLY = "--apply" in sys.argv


def ja_name_from_href(href, t):
    seg = f"/{t}/"
    if seg not in href:
        return None
    tail = href.split(seg, 1)[1]
    tail = tail.split("#")[0].split("?")[0]
    return urllib.parse.unquote(tail)


def build_map(t):
    """JA basename -> EN basename, from each EN page's JP link."""
    m = {}
    for enf in glob.glob(os.path.join(REPO, "en", t, "*.html")):
        if enf.endswith("-backup.html"):
            continue
        html = open(enf, encoding="utf-8").read()
        block = TOGGLE_RE.search(html)
        if not block:
            continue
        for href, inner in ANCHOR_RE.findall(block.group(0)):
            if "JP" in re.sub(r"<[^>]+>", "", inner):
                ja_name = ja_name_from_href(href, t)
                if ja_name:
                    m[ja_name] = os.path.basename(enf)
                break
    return m


def main():
    grand = {"fixed": 0, "no_en": 0, "no_button": 0, "already": 0}
    for t in TYPES:
        ja_to_en = build_map(t)
        fixed = no_en = no_button = already = 0
        examples = []
        for jaf in sorted(glob.glob(os.path.join(REPO, t, "*.html"))):
            base = os.path.basename(jaf)
            if base.endswith("-backup.html"):
                continue
            html = open(jaf, encoding="utf-8").read()
            if "head__lang" not in html:
                continue
            if "<button>EN</button>" not in html:
                # already linked or different markup
                if ">EN</a>" in html or "><button>EN</button></a>" in html:
                    already += 1
                else:
                    no_button += 1
                continue
            enname = ja_to_en.get(base)
            if not enname or not os.path.exists(os.path.join(REPO, "en", t, enname)):
                no_en += 1
                continue
            href = f"/en/{t}/" + urllib.parse.quote(enname)
            new = html.replace(
                "<button>EN</button>",
                f'<a href="{href}"><button>EN</button></a>',
                1,
            )
            if new.count('<a href="/en/') < 0:  # noqa (sanity placeholder)
                pass
            if APPLY:
                open(jaf, "w", encoding="utf-8").write(new)
            fixed += 1
            if len(examples) < 3:
                examples.append(f"{base} -> {href}")
        print(f"[{t}] fixed={fixed} no_en_page={no_en} already_linked={already} other_markup={no_button}")
        for ex in examples:
            print(f"    e.g. {ex}")
        grand["fixed"] += fixed
        grand["no_en"] += no_en
        grand["already"] += already
        grand["no_button"] += no_button
    mode = "APPLIED" if APPLY else "DRY-RUN (use --apply to write)"
    print(f"== {mode} == total fixed={grand['fixed']} no_en={grand['no_en']} "
          f"already={grand['already']} other={grand['no_button']}")


if __name__ == "__main__":
    main()
