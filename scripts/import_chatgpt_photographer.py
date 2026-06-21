#!/usr/bin/env python3
"""import_chatgpt_photographer.py — ChatGPT 生成の写真家 HTML 素材を、決定論的な
整形だけ自動化して photographers/<slug>.html を1パスで作る半自動インポータ（v1）。

設計方針（landmine 化を避ける / blast radius を限定する）:
  - 機械的に確定できる整形だけ自動化する：rev スパンの unwrap・edit-red クラストークン
    除去・hero 眉番号 §NNN の idx 採番・内部リンクの実ファイル存在チェックによる
    自動 de-link。判断が要る編集（サイドバー標準化・§統合・項目削除・thesis 断定度）は
    自動化せず、末尾にレビューチェックリストとして印字する。
  - 書き込みは **photographers/<slug>.html の1ファイルのみ**（--apply 時）。既存上書きは
    --force 必須＋自動バックアップ。dry-run 既定。
  - EN 素材を渡したときは、正本 JSON には一切触れず、**完成形の著者コンテンツ断片**を
    outputs/import-preview/<slug>.en-content-entry.json に出力する（v2 で正本へ注入予定）。
  - card-data / archive / 年代 / 国 / 運動 / 星マップ / EN 正本 JSON には触れない
    （既存の add_photographer.py と各ビルダーへ委譲）。
  - preflight / pre-push フックには連動しない（独立ツール）。

使い方:
  python3 scripts/import_chatgpt_photographer.py --slug yasumasa-morimura \\
      --ja path/to/morimura.html [--en path/to/morimuraEN.html] \\
      [--apply] [--force] [--idx 134]

  --apply なし = dry-run（何も書かず、検証結果・差分サマリ・チェックリストだけ表示）。
  --idx なし   = card-data.json から該当 slug の idx を引く。未登録なら max idx+1 を提案。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

# データ表のみ import（build_taxonomy_en は main ガード済みで import 副作用なし）
from build_taxonomy_en import STUB_TO_SLUG, SLUG_TO_EN_NAME  # noqa: E402

CARD_DATA = REPO / "card-data.json"
JA_DIR = REPO / "photographers"
EN_DIR = REPO / "en" / "photographers"
PREVIEW_DIR = REPO / "outputs" / "import-preview"


# ── 存在チェック（de-link 判定の正） ───────────────────────────────────────

def ja_page_exists(slug: str) -> bool:
    return (JA_DIR / f"{slug}.html").exists()


def en_page_exists(slug: str) -> bool:
    return (EN_DIR / f"{slug}.html").exists()


def en_movement_exists(slug: str) -> bool:
    return (REPO / "en" / "movements" / f"{slug}.html").exists()


def en_country_exists(slug: str) -> bool:
    return (REPO / "en" / "countries" / f"{slug}.html").exists()


def repo_file_exists(rel: str) -> bool:
    """`/foo/bar.html` や `../eras/x.html` をリポジトリルート相対で解決して存在判定。"""
    rel = rel.split("#", 1)[0].split("?", 1)[0]
    rel = rel.lstrip("/")
    while rel.startswith("../"):
        rel = rel[3:]
    return (REPO / rel).exists()


# ── 決定論変換（JA / EN 共有） ─────────────────────────────────────────────

REV_OPEN_RE = re.compile(r'<span class="rev[0-9]">')
SPAN_TAG_RE = re.compile(r'<span\b[^>]*>|</span>')


def strip_edit_red(html: str) -> str:
    """class 属性内の `edit-red` トークンだけ除去（要素自体は残す）。
    `ph-section edit-red` → `ph-section`、`edit-red foo` → `foo` など順不同で安全。"""
    def repl(m: re.Match) -> str:
        tokens = [t for t in m.group(1).split() if t != "edit-red"]
        return f'class="{" ".join(tokens)}"'
    return re.sub(r'class="([^"]*)"', repl, html)


# レビュー用 CSS（`.edit-red`/`.revN` セレクタのルール）と注釈コメント
REVIEW_CSS_RULE_RE = re.compile(r'[^{}]*\.(?:edit-red|rev[0-9])[^{}]*\{[^}]*\}')
REVIEW_COMMENT_RE = re.compile(r'/\*\s*revision preview\s*\*/')


def strip_review_css(html: str) -> str:
    """<style> ブロック内のレビュー用 CSS（.edit-red / .rev[0-9] ルール）と
    `/* revision preview */` コメントを除去。本番ページには残さない（出荷済みと一致）。"""
    def repl(m: re.Match) -> str:
        style = m.group(0)
        style = REVIEW_CSS_RULE_RE.sub("", style)
        style = REVIEW_COMMENT_RE.sub("", style)
        return style
    return re.sub(r'<style\b[^>]*>.*?</style>', repl, html, flags=re.S | re.I)


def unwrap_rev_spans(html: str) -> str:
    """<span class="rev[0-9]">…</span> をネスト対応で unwrap（中身は保持）。
    rev 以外の <span> と入れ子になっていても、対応する開閉だけを取り除く。"""
    out = []
    pos = 0
    stack = []  # 各 <span> が rev か否か（True=rev）を積む
    for m in SPAN_TAG_RE.finditer(html):
        tag = m.group(0)
        out.append(html[pos:m.start()])
        pos = m.end()
        if tag.startswith("</span"):
            is_rev = stack.pop() if stack else False
            if not is_rev:
                out.append(tag)  # 非 rev の閉じは残す
            # rev の閉じは捨てる
        else:
            is_rev = bool(REV_OPEN_RE.match(tag))
            stack.append(is_rev)
            if not is_rev:
                out.append(tag)  # 非 rev の開きは残す
            # rev の開きは捨てる
    out.append(html[pos:])
    return "".join(out)


def renumber_eyebrow(html: str, idx: int) -> tuple[str, str | None, str | None]:
    """hero 眉 `<div class="ph-hero__eyebrow">§ NNN — …` の番号を idx（3桁0埋め）へ。
    返り値: (新html, 旧番号文字列, 新番号文字列)。眉が無ければ番号は None。"""
    old_new = {}

    def repl(m: re.Match) -> str:
        old_new["old"] = m.group(2)
        new = f"{idx:03d}"
        old_new["new"] = new
        return f"{m.group(1)}{new}"

    new_html = re.sub(
        r'(<div class="ph-hero__eyebrow">§\s*)(\d+)',
        repl, html, count=1)
    return new_html, old_new.get("old"), old_new.get("new")


# 内部リンク（site のページ規約 = .html で終わる絶対/相対パス）
INTERNAL_HREF_RE = re.compile(r'href="((?:\.\.?/|/)[^"]+\.html)"')
# <a …>…</a>（属性内に > を含まない素朴な想定。site の本文リンクはこの形）
ANCHOR_RE = re.compile(r'<a\b[^>]*\bhref="([^"]+)"[^>]*>(.*?)</a>', re.S)

# script / style ブロックは de-link 対象から除外（JS 文字列の href を触らない）
SCRIPT_STYLE_RE = re.compile(r'<(script|style)\b.*?</\1>', re.S | re.I)


def _mask_scripts(html: str) -> tuple[str, list[str]]:
    saved: list[str] = []

    def stash(m: re.Match) -> str:
        saved.append(m.group(0))
        return f"\x00MASK{len(saved) - 1}\x00"

    return SCRIPT_STYLE_RE.sub(stash, html), saved


def _unmask_scripts(html: str, saved: list[str]) -> str:
    for i, blk in enumerate(saved):
        html = html.replace(f"\x00MASK{i}\x00", blk)
    return html


def delink_missing(html: str, exists_fn, *, label: str) -> tuple[str, list[str]]:
    """内部 .html リンクのうち、リンク先が存在しないものを unwrap（テキストは残す）。
    exists_fn(href)->bool。script/style 内は対象外。返り値: (新html, de-link した href 一覧)。"""
    masked, saved = _mask_scripts(html)
    delinked: list[str] = []

    def repl(m: re.Match) -> str:
        href, inner = m.group(1), m.group(2)
        # 内部 .html だけ判定。外部・#・mailto・拡張子なし(/colophon 等)は触らない
        if not INTERNAL_HREF_RE.fullmatch(f'href="{href}"'):
            return m.group(0)
        if exists_fn(href):
            return m.group(0)
        delinked.append(href)
        return inner  # アンカーを外して中身だけ残す

    masked = ANCHOR_RE.sub(repl, masked)
    return _unmask_scripts(masked, saved), delinked


# ── EN リンク localize（/en/ 化 + 運動 slug 変換、EN 実在で de-link） ───────

def localize_en_links(html: str) -> tuple[str, list[str]]:
    """EN 素材の JA 形内部リンクを EN 側へ localize。EN が存在しないものは de-link。
    返り値: (新html, de-link した元 href 一覧)。"""
    masked, saved = _mask_scripts(html)
    delinked: list[str] = []

    def repl(m: re.Match) -> str:
        href, inner = m.group(1), m.group(2)
        # 写真家
        pm = re.fullmatch(r'/photographers/([^"/]+)\.html', href)
        if pm:
            slug = pm.group(1)
            if en_page_exists(slug):
                return m.group(0).replace(f'href="{href}"', f'href="/en/photographers/{slug}.html"')
            delinked.append(href)
            return inner
        # 運動（JA ファイル名 → EN slug）
        mm = re.fullmatch(r'/movements/([^"/]+)\.html', href)
        if mm:
            ja_name = mm.group(1)
            slug = STUB_TO_SLUG.get(ja_name)
            if slug and en_movement_exists(slug):
                return m.group(0).replace(f'href="{href}"', f'href="/en/movements/{slug}.html"')
            delinked.append(href)
            return inner
        # 国
        cm = re.fullmatch(r'/countries/([^"/]+)\.html', href)
        if cm:
            slug = cm.group(1)
            if en_country_exists(slug):
                return m.group(0).replace(f'href="{href}"', f'href="/en/countries/{slug}.html"')
            delinked.append(href)
            return inner
        # 年代
        em = re.fullmatch(r'(?:\.\./)?(?:/)?eras/(\d+)\.html', href)
        if em:
            era = em.group(1)
            return m.group(0).replace(f'href="{href}"', f'href="/en/eras/{era}.html"')
        return m.group(0)

    masked = ANCHOR_RE.sub(repl, masked)
    return _unmask_scripts(masked, saved), delinked


# ── 自己検証 ───────────────────────────────────────────────────────────────

def self_check(html: str, *, context: str) -> list[str]:
    """決定論整形後の不変条件を assert（破ったら例外）。返り値は情報用の注記。"""
    notes = []
    n_open = len(re.findall(r"<span\b", html))
    n_close = len(re.findall(r"</span>", html))
    if n_open != n_close:
        raise AssertionError(f"[{context}] span 開閉数が不一致: open={n_open} close={n_close}")
    if re.search(r'<span class="rev[0-9]"', html):
        raise AssertionError(f"[{context}] rev スパンが残存している")
    if re.search(r'\.(?:edit-red|rev[0-9])\b', html):
        raise AssertionError(f"[{context}] レビュー用 CSS セレクタ（.edit-red/.revN）が残存している")
    if "edit-red" in html:
        raise AssertionError(f"[{context}] edit-red トークンが残存している")
    notes.append(f"span balance OK ({n_open}) / rev・edit-red・レビューCSS 残存ゼロ")
    return notes


# ── idx 解決 ───────────────────────────────────────────────────────────────

def resolve_idx(slug: str, override: int | None) -> tuple[int, str]:
    data = json.loads(CARD_DATA.read_text(encoding="utf-8"))["photographers"]
    if override is not None:
        return override, f"--idx 指定値 {override}"
    for p in data:
        if p.get("id") == slug:
            return p["idx"], f"card-data.json の既存 idx {p['idx']}"
    proposed = max(p.get("idx", 0) for p in data) + 1
    return proposed, f"card-data.json 未登録 → max idx+1 = {proposed} を提案（add_photographer.py で確定）"


# ── JA 整形パイプライン ────────────────────────────────────────────────────

def process_ja(html: str, idx: int) -> tuple[str, dict]:
    report: dict = {}
    n_rev = len(REV_OPEN_RE.findall(html))
    n_editred = html.count("edit-red")
    html = strip_review_css(html)
    html = strip_edit_red(html)
    html = unwrap_rev_spans(html)
    html, old_no, new_no = renumber_eyebrow(html, idx)
    html, delinked = delink_missing(html, repo_file_exists, label="JA")
    report["rev_unwrapped"] = n_rev
    report["edit_red_removed"] = n_editred
    report["eyebrow"] = (old_no, new_no)
    report["delinked"] = delinked
    report["checks"] = self_check(html, context="JA")
    return html, report


# ── EN 著者コンテンツ断片の抽出 ────────────────────────────────────────────

PH_SECTION_RE = re.compile(
    r'<section class="ph-section[^"]*"[^>]*>(.*?)</section>', re.S)
SECTION_NAME_RE = re.compile(r'<span class="ph-section__name">([^<]+)</span>')


def extract_en_fragment(en_html: str, slug: str) -> tuple[dict, dict]:
    """EN 素材から著者コンテンツの断片を抽出（正本 JSON には書かない）。
    rev/edit-red を整形し、リンクを EN へ localize したうえで section 単位に分解する。"""
    report: dict = {}
    n_rev = len(REV_OPEN_RE.findall(en_html))
    n_editred = en_html.count("edit-red")
    en_html = strip_review_css(en_html)
    en_html = strip_edit_red(en_html)
    en_html = unwrap_rev_spans(en_html)
    en_html, delinked = localize_en_links(en_html)
    report["rev_unwrapped"] = n_rev
    report["edit_red_removed"] = n_editred
    report["delinked"] = delinked
    report["checks"] = self_check(en_html, context="EN")

    sections = []
    for m in PH_SECTION_RE.finditer(en_html):
        block = m.group(1)
        nm = SECTION_NAME_RE.search(block)
        title = nm.group(1).strip() if nm else None
        sections.append({"title": title, "body_html": block.strip()})

    fragment = {
        "_note": "v1 抽出のプレビュー断片。正本 data/photographers-en-content.json には未注入。",
        "slug": slug,
        "section_count": len(sections),
        "sections": sections,
        "_review": [
            "section の粒度・タイトルが正本スキーマ（Biography/Expression 等）に対応するか確認",
            "lead / thesis / sources(cite) / site_directory を正本フィールドへ手で割り当てる",
            "localize 済みリンク・de-link 済み箇所が意図どおりか確認",
        ],
    }
    report["section_count"] = len(sections)
    report["section_titles"] = [s["title"] for s in sections]
    return fragment, report


# ── レビューチェックリスト（自動化しない編集判断） ─────────────────────────

REVIEW_CHECKLIST = [
    "サイドバーを標準形へ（Basic Info → Entry / Keywords / Works / Navigate）",
    "§MORE 等の付加セクションを §REF へ統合（参照実装 ansel-adams の節構成に合わせる）",
    "実在しない人物/運動のサイドバー項目を削除（本文リンクは de-link 済みでも項目は手動）",
    "thesis の断定度を基準内へ（docs/photographer-leaf-spec.md）",
    "JSON-LD / canonical / hreflang / OGP / description の実体値を新写真家へ全置換",
    "本文に参照実装由来の残骸（Adams 等）が無いか・cite と sup の対応を確認",
]


def print_runbook(slug: str, wrote_ja: bool, wrote_en: bool):
    print("\n" + "=" * 70)
    print("レビューチェックリスト（自動化しない編集判断・人手で確認）")
    print("=" * 70)
    for i, item in enumerate(REVIEW_CHECKLIST, 1):
        print(f"  [{i}] {item}")
    print("\n" + "=" * 70)
    print("次に実行するコマンド（importer の後段）")
    print("=" * 70)
    print(f"  python3 scripts/check_new_photographer.py --slug {slug}   # 完成検査")
    print(f"  python3 scripts/add_photographer.py <spec.json> --apply   # 全サーフェス反映")
    if wrote_en:
        print(f"  # EN: outputs/import-preview/{slug}.en-content-entry.json を正本へ手で移植後")
        print(f"  python3 scripts/build_photographers_en.py --slug {slug}")
    print(f"  python3 scripts/preflight.py                              # push 前ネット")
    print("\n注意: card-data / 年代 / 国 / 運動 / 星 / EN 正本 JSON は本ツールでは触れていない。")


# ── main ───────────────────────────────────────────────────────────────────

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="ChatGPT 写真家 HTML 素材の決定論インポータ（JA 整形 + EN 断片抽出・v1）",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug", required=True, help="出力 slug（例 yasumasa-morimura）")
    ap.add_argument("--ja", required=True, help="JA 素材 HTML のパス")
    ap.add_argument("--en", help="EN 素材 HTML のパス（省略可。あれば断片を抽出）")
    ap.add_argument("--idx", type=int, help="hero 眉採番に使う idx（省略時 card-data から解決）")
    ap.add_argument("--apply", action="store_true", help="実書き込み（無指定は dry-run）")
    ap.add_argument("--force", action="store_true", help="既存 photographers/<slug>.html を上書き（backup あり）")
    args = ap.parse_args(argv)

    ja_src = Path(args.ja)
    if not ja_src.exists():
        sys.stderr.write(f"ERROR: JA 素材が見つからない: {ja_src}\n")
        return 2

    idx, idx_note = resolve_idx(args.slug, args.idx)
    print(f"slug={args.slug} / idx={idx}（{idx_note}）")

    ja_html = ja_src.read_text(encoding="utf-8")
    out_html, ja_report = process_ja(ja_html, idx)

    print("\n── JA 決定論整形 ──")
    print(f"  rev unwrap         : {ja_report['rev_unwrapped']} 箇所")
    print(f"  edit-red 除去      : {ja_report['edit_red_removed']} 箇所")
    old_no, new_no = ja_report["eyebrow"]
    print(f"  hero 眉採番        : §{old_no} → §{new_no}" if old_no else "  hero 眉採番        : 眉が見つからない（要確認）")
    if ja_report["delinked"]:
        print(f"  自動 de-link       : {len(ja_report['delinked'])} 件 → {ja_report['delinked']}")
    else:
        print("  自動 de-link       : 0 件（dangling 内部リンクなし）")
    for n in ja_report["checks"]:
        print(f"  自己検証           : {n}")

    ja_out = JA_DIR / f"{args.slug}.html"
    wrote_ja = False
    if args.apply:
        if ja_out.exists() and not args.force:
            sys.stderr.write(
                f"ERROR: {ja_out} は既存。上書きには --force が必要（backup を取る）。\n")
            return 2
        if ja_out.exists():
            bak = ja_out.with_name(ja_out.stem + "-backup" + ja_out.suffix)
            bak.write_text(ja_out.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"  backup → {bak.relative_to(REPO)}")
        ja_out.write_text(out_html, encoding="utf-8")
        wrote_ja = True
        print(f"  ✅ 書込: {ja_out.relative_to(REPO)}")
    else:
        print(f"  (dry-run) 書込先: {ja_out.relative_to(REPO)}（--apply で書込）")

    wrote_en = False
    if args.en:
        en_src = Path(args.en)
        if not en_src.exists():
            sys.stderr.write(f"ERROR: EN 素材が見つからない: {en_src}\n")
            return 2
        fragment, en_report = extract_en_fragment(en_src.read_text(encoding="utf-8"), args.slug)
        print("\n── EN 断片抽出（正本 JSON には書かない） ──")
        print(f"  rev unwrap / edit-red 除去 : {en_report['rev_unwrapped']} / {en_report['edit_red_removed']}")
        if en_report["delinked"]:
            print(f"  EN localize de-link        : {len(en_report['delinked'])} 件 → {en_report['delinked']}")
        print(f"  抽出 section               : {en_report['section_count']} 件 {en_report['section_titles']}")
        for n in en_report["checks"]:
            print(f"  自己検証                   : {n}")
        out_json = PREVIEW_DIR / f"{args.slug}.en-content-entry.json"
        if args.apply:
            PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
            out_json.write_text(json.dumps(fragment, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            wrote_en = True
            print(f"  ✅ 書込: {out_json.relative_to(REPO)}")
        else:
            print(f"  (dry-run) 断片出力先: {out_json.relative_to(REPO)}（--apply で書込）")

    print_runbook(args.slug, wrote_ja, wrote_en)
    return 0


if __name__ == "__main__":
    sys.exit(main())
