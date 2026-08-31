#!/usr/bin/env python3
"""カード枚数表示を card-data.json から同期する（正本＝card-data.json）。

背景（2026-09-01 導入）:
  archive 系ページの「285 PHOTOGRAPHERS · 31 MOVEMENTS · 316 TOTAL」「表示中 N / M」
  meta description の「316枚のカード」「写真家285人」等がすべてベタ書きで、写真家を追加する
  たびに手で打ち直されてきた結果 316 / 285 / 283 の3種類が併存していた。
  枚数表示は card-data.json から機械的に導出できるので、ここで一元化する。

正本と検算:
  - 表示に使う数 = card-data.json の photographers / movements の要素数（total = 合計）。
  - 同時に archive.html の実カード数（data-type="photographer" / "movement"）を数え、
    card-data.json と食い違ったら **何も書かずに FAIL** する。食い違いはカード同期そのものの
    破損（archive 掲載漏れ等）であり、枚数だけ書き換えると壊れた状態を隠してしまうため。

使い方:
    python3 scripts/sync_card_counts.py            # 実書き換え
    python3 scripts/sync_card_counts.py --check    # 書き換えず、ズレがあれば exit 1

置換は数字ベタ打ちの検索置換ではなく正規表現で行うので、次回以降の枚数変化にも効く。
preflight.py の check_card_counts() がこのモジュールを import して同じ規則で検査する。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CARD_DATA = REPO / "card-data.json"

# ── 置換規則 ────────────────────────────────────────────────────────────
# (相対パス, 正規表現, 置換を作る関数, 期待マッチ数)
# 期待マッチ数に満たない場合は「文言の形が変わった＝この規則が黙って効かなくなった」ので
# エラーにする（サイレント no-op を作らない）。

# archive 3面の hero サブタイトル
HERO_RE = re.compile(r"(\d+) PHOTOGRAPHERS · (\d+) MOVEMENTS · (\d+) TOTAL")

# archive.html の meta description / og:description / twitter:description（3箇所）
JA_ARCHIVE_META_RE = re.compile(
    r"写真史を(\d+)枚のカードで整理した写真家一覧。世界と日本の写真家(\d+)人と(\d+)の写真運動を"
)

# 「表示中 N / M」「Showing N / M」の結果バー。
# 旧形（分母がベタ書きの裸数字）にもマッチし、新形（分母も span）へ正規化する。
# 分母の span には result-bar__num を付けない（付けると分母までアクセント色になり見た目が変わる）。
RESULT_BAR_RE = re.compile(
    r'(<span class="result-bar__num" id="visible-count">)\d+(</span>\s*/\s*)'
    r'(?:<span[^>]*id="total-count"[^>]*>)?\d+(?:</span>)?'
)

# トップページ meta（JA / EN 各3箇所）
JA_INDEX_META_RE = re.compile(r"世界と日本の写真家(\d+)人と(\d+)の写真運動")
EN_INDEX_META_RE = re.compile(r"Explore (\d+) photographers and (\d+) photographic movements")


def _rules(ph: int, mv: int, total: int):
    """(rel, pattern, replacement, expected_count, label) のリストを返す。"""
    hero = f"{ph} PHOTOGRAPHERS · {mv} MOVEMENTS · {total} TOTAL"
    ja_archive_meta = (
        f"写真史を{total}枚のカードで整理した写真家一覧。"
        f"世界と日本の写真家{ph}人と{mv}の写真運動を"
    )
    result_bar = (
        f'<span class="result-bar__num" id="visible-count">{total}</span> / '
        f'<span id="total-count">{total}</span>'
    )
    ja_index_meta = f"世界と日本の写真家{ph}人と{mv}の写真運動"
    en_index_meta = f"Explore {ph} photographers and {mv} photographic movements"

    rules = []
    for rel in ("archive.html", "en/archive.html", "cards-archive.html"):
        rules.append((rel, HERO_RE, hero, 1, "hero サブタイトル"))
        rules.append((rel, RESULT_BAR_RE, result_bar, 1, "結果バー 表示中 N / M"))
    rules.append(("archive.html", JA_ARCHIVE_META_RE, ja_archive_meta, 3, "meta description 3種"))
    rules.append(("index.html", JA_INDEX_META_RE, ja_index_meta, 3, "meta description 3種"))
    rules.append(("en/index.html", EN_INDEX_META_RE, en_index_meta, 3, "meta description 3種"))
    return rules


# ── 計数 ────────────────────────────────────────────────────────────────

def compute_counts() -> tuple[int, int, int]:
    data = json.loads(CARD_DATA.read_text(encoding="utf-8"))
    ph = len(data.get("photographers", []))
    mv = len(data.get("movements", []))
    return ph, mv, ph + mv


def verify_card_sync() -> list[str]:
    """card-data.json と archive.html の実カード数が一致するか検算する。
    ズレていたらエラー文字列のリストを返す（＝枚数同期をしてはいけない状態）。"""
    ph, mv, _ = compute_counts()
    html = (REPO / "archive.html").read_text(encoding="utf-8")
    ph_html = len(re.findall(r'data-type="photographer"', html))
    mv_html = len(re.findall(r'data-type="movement"', html))
    errs = []
    if ph_html != ph:
        errs.append(f"photographers: card-data.json {ph} 件 / archive.html {ph_html} 枚")
    if mv_html != mv:
        errs.append(f"movements: card-data.json {mv} 件 / archive.html {mv_html} 枚")
    return errs


# ── 差分収集 / 適用 ─────────────────────────────────────────────────────

def collect(apply: bool) -> tuple[list[str], list[str], list[str]]:
    """全規則を走査する。

    returns: (drift, missing, changed)
      drift   … 表示値が正しい値とズレている箇所（--check の失敗理由）
      missing … 規則がマッチしなかった箇所（文言の形が変わった疑い）
      changed … 実際に書き換えたファイル（apply=False なら常に空）
    """
    ph, mv, total = compute_counts()
    drift: list[str] = []
    missing: list[str] = []
    changed: list[str] = []

    by_file: dict[str, str] = {}
    for rel, pattern, repl, expected, label in _rules(ph, mv, total):
        path = REPO / rel
        if not path.exists():
            continue  # new-design/ 等の未配置ファイルは対象外
        text = by_file.get(rel)
        if text is None:
            text = path.read_text(encoding="utf-8")
            by_file[rel] = text
        hits = pattern.findall(text)
        if len(hits) < expected:
            missing.append(f"{rel}: {label} の文言にマッチしない（{len(hits)}/{expected}）")
            continue
        new_text = pattern.sub(lambda m: repl, text)
        if new_text != text:
            drift.append(f"{rel}: {label}")
            by_file[rel] = new_text

    if apply:
        for rel, text in by_file.items():
            path = REPO / rel
            if text != path.read_text(encoding="utf-8"):
                path.write_text(text, encoding="utf-8")
                changed.append(rel)
    return drift, missing, changed


def main(argv: list[str]) -> int:
    check_only = "--check" in argv or "--dry-run" in argv
    ph, mv, total = compute_counts()

    errs = verify_card_sync()
    if errs:
        print("sync_card_counts: FAILED — card-data.json と archive.html のカード数が不一致")
        for e in errs:
            print("  ✗ " + e)
        print("\nカード同期そのものが壊れている（archive 掲載漏れ / 二重掲載）。")
        print("枚数表示だけ書き換えると破損を隠すので、何も書き換えずに終了する。")
        print("先に archive.html のカードを card-data.json と揃えること。")
        return 2

    print(f"card-data.json: photographers {ph} / movements {mv} / total {total}")
    drift, missing, changed = collect(apply=not check_only)

    for m in missing:
        print("  ⚠ " + m)

    if check_only:
        if drift:
            print("── 枚数表示のズレ ──")
            for d in drift:
                print("  ✗ " + d)
            print("\n修復: python3 scripts/sync_card_counts.py")
            return 1
        if missing:
            print("sync_card_counts: 文言不一致あり（上記 WARN）。枚数のズレは無し")
            return 1
        print("sync_card_counts: OK（枚数表示は card-data.json と一致）")
        return 0

    if changed:
        print("── 更新 ──")
        for rel in changed:
            print("  ✓ " + rel)
    else:
        print("変更なし（既に一致）")
    if missing:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
