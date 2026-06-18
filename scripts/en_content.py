#!/usr/bin/env python3
"""EN 写真家コンテンツ系ツールの共通ヘルパー。

en_entry.py / check_en_entry.py / preflight.py から共有して使う。
JSON も HTML も書き換えない（読み取り専用）。

主な提供物:
    load_pages()            -> data/photographers-en-content.json の pages dict
    resolve_slug(arg, pages) -> (slug | None, candidates)
        短い通称（atget→eugene-atget）や .html 有無を吸収して slug を解決する。
        厳密に1つへ決まるときだけ slug を返し、複数候補なら None と候補一覧を返す。
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(ROOT, 'data', 'photographers-en-content.json')


def load_data():
    with open(JSON_PATH, encoding='utf-8') as fh:
        return json.load(fh)


def load_pages():
    return load_data()['pages']


def _stem(slug):
    return slug[:-5] if slug.endswith('.html') else slug


def resolve_slug(arg, pages):
    """ユーザ入力 arg を実 slug（'eugene-atget.html'）へ解決する。

    返り値 (slug, candidates):
      - 一意に決まれば (slug, [slug])
      - 決まらなければ (None, sorted(candidates))  ※候補ゼロのときは (None, [])

    解決の優先順位:
      0. '<arg>.html' がそのまま存在（.html 有無は吸収）
      1. 語境界一致: stem が arg と完全一致 / '-arg' で終わる / 'arg-' で始まる
         （atget→eugene-atget, cameron→julia-margaret-cameron 等）
      2. 部分一致: stem に arg を含む（robertfrank で 'frank' を拾う等）
    各段で候補が1つなら解決、複数なら候補一覧を返して終了。
    """
    arg = (arg or '').strip()
    base = _stem(arg).lower()
    if not base:
        return None, []

    # 0. 直接一致（.html 有無を吸収）
    direct = base + '.html'
    if direct in pages:
        return direct, [direct]
    # 念のため大小無視の直接一致
    for k in pages:
        if k.lower() == direct:
            return k, [k]

    stems = {k: _stem(k).lower() for k in pages}

    # 1. 語境界一致
    tier1 = sorted(k for k, st in stems.items()
                   if st == base or st.endswith('-' + base) or st.startswith(base + '-'))
    if len(tier1) == 1:
        return tier1[0], tier1
    if len(tier1) > 1:
        return None, tier1

    # 2. 部分一致
    tier2 = sorted(k for k, st in stems.items() if base in st)
    if len(tier2) == 1:
        return tier2[0], tier2
    return None, tier2
