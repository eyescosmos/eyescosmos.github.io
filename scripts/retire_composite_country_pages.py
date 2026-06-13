#!/usr/bin/env python3
"""Retire dual-nationality (composite) country pages.

Dual-nationality photographers already appear on BOTH single-country pages,
so composite pages carry no unique content. Rather than hard-delete (404 on
already-live URLs) we convert each composite page to a redirect stub
(noindex + meta-refresh + canonical) pointing at the single-country page of
its first code that has one, and drop composites from data/country-pages.json
so the generator no longer emits them.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

STUB = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex,follow">
<title>{name_ja}｜写真の座標</title>
<link rel="canonical" href="https://eyescosmos.github.io/countries/{target}.html">
<meta http-equiv="refresh" content="0; url=/countries/{target}.html">
</head>
<body>
<p>このページは <a href="/countries/{target}.html">{target_ja}の写真家一覧</a> に統合されました。自動的に移動します。</p>
</body>
</html>
"""


def main() -> None:
    reg = json.loads((REPO / "data" / "country-pages.json").read_text(encoding="utf-8"))
    singles = {r["codes"][0]: r for r in reg if len(r["codes"]) == 1}
    composites = [r for r in reg if len(r["codes"]) > 1]

    written = []
    for r in composites:
        target = next((singles[c] for c in r["codes"] if c in singles), None)
        if target is None:
            raise SystemExit(f"No single-page redirect target for {r['slug']}")
        stub = STUB.format(name_ja=r["nameJa"], target=target["slug"],
                           target_ja=target["nameJa"])
        (REPO / "countries" / f"{r['slug']}.html").write_text(stub, encoding="utf-8")
        written.append((r["slug"], target["slug"]))

    # Trim registry to single-country pages only
    singles_only = [r for r in reg if len(r["codes"]) == 1]
    (REPO / "data" / "country-pages.json").write_text(
        json.dumps(singles_only, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {len(written)} redirect stubs; registry trimmed to {len(singles_only)} single pages")
    for s, t in written:
        print(f"  {s} -> {t}")


if __name__ == "__main__":
    main()
