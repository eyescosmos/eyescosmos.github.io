#!/usr/bin/env python3
"""backfill_en_jsonld_graph.py — EN 写真家ページの JSON-LD を正典形へそろえる（一度きりの移行）。

## 何を直すか
`build_photographers_en._fb_jsonld()` が 2026-09-17 以前は flat な
WebPage / Person / BreadcrumbList の3本を返していたため、scaffold-inject で作った
EN ページ 125 枚が `@graph` を持たない形で固定されていた
（`check_new_photographer` の `en_graph_absent`）。renderer は同日に正典形へ直したが、
**EN ページは HTML 自身が正本なので再生成できない**（CLAUDE.md 絶対禁止3）。
そこで既存ページの JSON-LD だけを、そのページ自身の値から決定論的に組み直す。

## 正典形（既存 295 枚の実測・2026-09-17）
- 1本目 = `@graph` に WebPage + Person。`about` / `subjectOf` と `@id` で相互リンク。
- 2本目 = BreadcrumbList（position 1 はサイト名、末尾は人名で `item` を持たない）。
- `nationality` は Country オブジェクト（二重国籍は "A / B" の1文字列）。

## 値の出どころ（推測しない。取れなければそのページを skip して報告する）
| フィールド | 出どころ |
|---|---|
| URL | `<link rel="canonical">` |
| WebPage.name | `<title>` |
| description | 既存 Person の description → 無ければ `<meta name="description">` |
| Person.name | 既存 Person の name（title と同じなら採らない）→ `<h1>` |
| alternateName | JA ページ `photographers/<slug>.html` の Person.name（＝日本語名） |
| nationality | `card-data.json` の nationality コード → 国名（既存 86 枚で一致を実測） |
| birthDate / deathDate / sameAs | 既存 Person をそのまま持ち越す |

本文・見出し・出典には一切触れない。触るのは `<script type="application/ld+json">` だけ。

使い方:
    python3 scripts/backfill_en_jsonld_graph.py --check   # 対象を数えるだけ（既定）
    python3 scripts/backfill_en_jsonld_graph.py --apply
"""
from __future__ import annotations

import argparse
import glob
import html as H
import importlib.util
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://eyescosmos.com"
SITE_NAME = "Photo Coordinates"
LD_RE = re.compile(r'<script type="application/ld\+json">.*?</script>', re.S)


def _load_country_maps() -> tuple[dict, dict]:
    spec = importlib.util.spec_from_file_location(
        "bae", os.path.join(REPO, "scripts", "build_archive_en.py"))
    bae = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bae)
    code2ja: dict[str, str] = {}
    for ja, code in bae.COUNTRY_CODE.items():
        if ja != code:
            code2ja.setdefault(code, ja)
    with open(os.path.join(REPO, "data", "photographers-en-ui-terms.json"),
              encoding="utf-8") as fh:
        ui = json.load(fh)["countries"]
    return code2ja, ui


def _nationality_en(codes: str, code2ja: dict, ui: dict) -> str | None:
    out = []
    for code in [c.strip() for c in (codes or "").split("/") if c.strip()]:
        en = ui.get(code2ja.get(code, ""))
        if not en:
            return None
        out.append(en)
    return " / ".join(out) or None


def _blocks(html: str) -> list:
    out = []
    for raw in re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            out.append(json.loads(raw))
        except Exception:  # noqa: BLE001
            out.append(None)
    return out


def _ja_person_name(slug: str) -> str | None:
    p = os.path.join(REPO, "photographers", f"{slug}.html")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        html = fh.read()
    for node in _blocks(html):
        if isinstance(node, dict) and node.get("@type") == "Person":
            return node.get("name")
    return None


def build_graph(slug: str, html: str, card: dict, code2ja: dict,
                ui: dict) -> tuple[list | None, str]:
    """(json-ld ブロック2本, 理由) を返す。組めなければ (None, 理由)。"""
    m = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    if not m:
        return None, "canonical が無い"
    url = m.group(1)
    if url != f"{BASE}/en/photographers/{slug}.html":
        return None, f"canonical がページと一致しない: {url}"
    m = re.search(r"<title>(.*?)</title>", html, re.S)
    if not m:
        return None, "title が無い"
    title = H.unescape(m.group(1)).strip()
    m = re.search(r'<meta name="description" content="(.*?)">', html, re.S)
    meta_desc = H.unescape(m.group(1)).strip() if m else ""

    persons = [n for n in _blocks(html)
               if isinstance(n, dict) and n.get("@type") == "Person"]
    # name が title と同じ Person は旧 fallback の残骸なので「名前の出どころ」には採らない。
    # ただし birthDate / deathDate / sameAs はその残骸にしか入っていないページが 39 枚あるので、
    # 日付系は Person ノード全部から拾う（拾い落とすと preflight の
    # check_jsonld_person_key_regression が HARD で止める＝実際に 2026-09-17 に踏んだ）。
    real = next((p for p in persons if p.get("name") and p["name"] != title), None)
    src = real or {}
    carried: dict = {}
    for node in persons:
        for key in ("birthDate", "deathDate", "sameAs"):
            if node.get(key) and key not in carried:
                carried[key] = node[key]
    for key, val in carried.items():
        src.setdefault(key, val)

    name = src.get("name")
    if not name:
        m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
        if not m:
            return None, "Person 名も h1 も取れない"
        name = H.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
    if not name:
        return None, "Person 名が空"

    desc = src.get("description") or meta_desc
    alternate = _ja_person_name(slug) or card.get("nameJa")
    nationality = _nationality_en(card.get("nationality") or "", code2ja, ui)

    person_id = f"{url}#person"
    webpage = {"@type": "WebPage", "@id": url, "url": url, "name": title}
    if desc:
        webpage["description"] = desc
    webpage["inLanguage"] = "en"
    webpage["isPartOf"] = {"@type": "WebSite", "name": SITE_NAME,
                           "url": f"{BASE}/en/"}
    webpage["about"] = {"@id": person_id}

    person = {"@type": "Person", "@id": person_id, "name": name}
    if alternate and alternate != name:
        person["alternateName"] = alternate
    if desc:
        person["description"] = desc
    person["url"] = url
    person["jobTitle"] = "Photographer"
    for key in ("birthDate", "deathDate"):
        if src.get(key):
            person[key] = src[key]
    # （sameAs は nationality の後ろに置く＝正典 295 枚のキー順）
    if nationality:
        person["nationality"] = {"@type": "Country", "name": nationality}
    if src.get("sameAs"):
        person["sameAs"] = src["sameAs"]
    person["subjectOf"] = {"@id": url}

    return [
        {"@context": "https://schema.org", "@graph": [webpage, person]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList",
         "itemListElement": [
             {"@type": "ListItem", "position": 1, "name": SITE_NAME,
              "item": f"{BASE}/en/"},
             {"@type": "ListItem", "position": 2, "name": "Photographers",
              "item": f"{BASE}/en/archive.html"},
             {"@type": "ListItem", "position": 3, "name": name},
         ]},
    ], "ok"


def _render(blocks: list) -> str:
    return "\n".join(
        '<script type="application/ld+json">\n'
        + json.dumps(b, ensure_ascii=False, indent=2) + "\n</script>"
        for b in blocks)


def targets() -> list[str]:
    """JSON-LD を持ち、かつ @graph が無い EN 写真家ページ。
    JSON-LD を1本も持たない jp-漢字 shim は対象外（EN 実体は別 slug 側）。"""
    out = []
    for path in sorted(glob.glob(os.path.join(REPO, "en", "photographers", "*.html"))):
        if path.endswith("-backup.html"):
            continue
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        bs = _blocks(html)
        if not bs or any(isinstance(b, dict) and "@graph" in b for b in bs):
            continue
        out.append(path)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="EN 写真家ページの JSON-LD を正典形へ")
    ap.add_argument("--apply", action="store_true", help="実書き込み（無指定は検査のみ）")
    args = ap.parse_args()

    code2ja, ui = _load_country_maps()
    with open(os.path.join(REPO, "card-data.json"), encoding="utf-8") as fh:
        cards = {p["id"]: p for p in json.load(fh)["photographers"]}

    paths = targets()
    print(f"対象（JSON-LD があり @graph が無い EN ページ）: {len(paths)} 枚")
    wrote = skipped = 0
    for path in paths:
        slug = os.path.splitext(os.path.basename(path))[0]
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        blocks, why = build_graph(slug, html, cards.get(slug, {}), code2ja, ui)
        if blocks is None:
            print(f"  SKIP {slug}: {why}")
            skipped += 1
            continue
        found = list(LD_RE.finditer(html))
        head_end = html.find("</head>")
        found = [m for m in found if m.start() < head_end]
        if not found:
            print(f"  SKIP {slug}: head 内に JSON-LD が見つからない")
            skipped += 1
            continue
        new_html = html[:found[0].start()] + _render(blocks) + html[found[-1].end():]
        # 中間に挟まっていた JSON-LD 以外を巻き込んでいないか（本文は触らない契約）
        between = html[found[0].start():found[-1].end()]
        if LD_RE.sub("", between).strip():
            print(f"  SKIP {slug}: JSON-LD の間に別要素がある（手で確認すること）")
            skipped += 1
            continue
        if args.apply:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new_html)
        wrote += 1
    print(f"{'書込' if args.apply else '書込可'}: {wrote} 枚 / SKIP: {skipped} 枚")
    if not args.apply:
        print("（検査のみ。実書き込みは --apply）")
    return 1 if skipped else 0


if __name__ == "__main__":
    sys.exit(main())
