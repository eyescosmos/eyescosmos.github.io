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
import copy
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


# ── EN 著者コンテンツ断片の抽出（正本候補フィールドへ拡張・v2） ─────────────
#
# Phase 1（Step2.5）: 正本 JSON には一切書かない。EN 素材から正本スキーマと同名の
# 候補フィールドを抽出してプレビュー断片に並べ、コーパス監査で既存正本と diff する。
#
# EN 素材は2系統あることが判明している（監査で実数を確認する）:
#   Family B = 新 v5.1 テンプレ（ph-abstract / ph-thesis / ph-keywords / ph-section /
#              ph-sources / ph-cite / ph-rel）。正本JSON（旧クラス体系 lead/essay/
#              page-keywords/sources/site-directory-links）とは構造が違う＝要変換。
#   Family A = 旧テンプレ（lead / essay / sources / cite-item / site-directory-links）。
#              正本JSONとクラス体系が一致＝ほぼ素通しで対応。
# どちらも「中身（テキスト）」は正本と一致しうる。監査は normalize-text 一致と
# raw-markup 一致を分けて測り、差分が毎回同じ形か（＝変換ルールへ昇格できるか）を見る。

# 正本スキーマと同名の著者コンテンツ候補フィールド（head/meta 系は対象外）
EN_CANDIDATE_FIELDS = [
    "lead_html", "thesis_label", "thesis_html", "keywords_html",
    "view_works_note", "view_works_links_html", "sections",
    "sources_html", "cite_ids", "supref_ids", "site_directory_html",
    "notable_works_html", "external_links_html",
]

SECTION_NUMBERED_RE = re.compile(r'§\s*\d+\s*/\s*\d+')  # 「§ 01 / 04」= 本文 section
CITE_ID_RE = re.compile(r'id="cite-(\d+)"')
SUPREF_RE = re.compile(r'href="#cite-(\d+)"')


def _body_of(html: str) -> str:
    """先頭の <style>…</style> を捨てて body 相当だけ返す（CSS 内のクラス名誤検知を避ける）。"""
    i = html.rfind("</style>")
    return html[i + len("</style>"):] if i >= 0 else html


def norm_text(html: str | None) -> str:
    """タグ除去＋実体・引用符正規化＋空白畳み込み。テキスト一致判定の正規形。"""
    if not html:
        return ""
    t = re.sub(r"<[^>]+>", " ", html)
    for a, b in (("&amp;", "&"), ("&nbsp;", " "), ("&lt;", "<"), ("&gt;", ">"),
                 ("&#39;", "'"), ("&quot;", '"'), ("’", "'"), ("‘", "'"),
                 ("“", '"'), ("”", '"'), ("—", "-"), ("–", "-")):
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t).strip()


def slice_by_class(html: str, tag: str, cls: str, start: int = 0):
    """`start` 以降で最初に現れる class に `cls` トークンを含む <tag> を、同名タグの
    入れ子を数えて閉じまで切り出す。返り値 (outer, inner, end) または None。"""
    open_re = re.compile(r'<%s\b[^>]*class="([^"]*)"[^>]*>' % tag, re.I)
    scan_re = re.compile(r'<%s\b|</%s>' % (tag, tag), re.I)
    for m in open_re.finditer(html, start):
        if cls not in m.group(1).split():
            continue
        depth = 0
        for t in scan_re.finditer(html, m.start()):
            if t.group(0).startswith("</"):
                depth -= 1
                if depth == 0:
                    return html[m.start():t.end()], html[m.end():t.start()], t.end()
            else:
                depth += 1
        return html[m.start():], html[m.end():], len(html)  # 閉じ欠け
    return None


def _extract_family_b(body: str, fields: dict, meta: dict) -> None:
    """新 v5.1 テンプレ（ph-*）から候補フィールドを抽出。"""
    ab = slice_by_class(body, "div", "ph-abstract")
    if ab:
        inner = re.sub(r'<div class="ph-abstract__label">.*?</div>', "",
                       ab[1], flags=re.S).strip()
        fields["lead_html"] = inner or None
    th = slice_by_class(body, "div", "ph-thesis")
    if th:
        lbl = re.search(r'ph-thesis__label">([^<]*)<', th[1])
        fields["thesis_label"] = lbl.group(1).strip() if lbl else None
        tb = slice_by_class(th[1], "p", "ph-thesis__body")
        fields["thesis_html"] = tb[1].strip() if tb else None
    kw = slice_by_class(body, "div", "ph-keywords")
    if kw:
        fields["keywords_html"] = kw[0].strip()

    sections = []
    start = 0
    while True:
        sl = slice_by_class(body, "section", "ph-section", start)
        if not sl:
            break
        outer, inner, start = sl
        num_m = re.search(r'ph-section__num">([^<]*)<', inner)
        name_m = re.search(r'ph-section__name">([^<]*)<', inner)
        num = (num_m.group(1).strip() if num_m else "")
        name = (name_m.group(1).strip() if name_m else None)
        bb = slice_by_class(inner, "div", "ph-section__body")
        binner = (bb[1] if bb else inner).strip()
        if SECTION_NUMBERED_RE.search(num):
            sections.append({"num": num, "title": name, "body_html": binner})
        elif "WORKS" in num:
            note = re.search(r'ph-works-note">(.*?)</p>', binner, re.S)
            if note:
                fields["view_works_note"] = norm_text(note.group(1))
            links = slice_by_class(binner, "div", "ph-works-links")
            if links:
                fields["view_works_links_html"] = links[0].strip()
        elif "SRC" in num:
            src = slice_by_class(binner, "div", "ph-sources")
            fields["sources_html"] = (src[0] if src else binner).strip()
        elif "REL" in num:
            fields["site_directory_html"] = binner
        else:
            # §MORE / §REF / §LINK / §READ 等の付加節（external_links / notable_works /
            # further_reading 候補）。Phase 1 では手当て対象として記録のみ。
            meta["supplementary"].append(
                {"num": num, "title": name, "chars": len(binner)})
    fields["sections"] = sections or None


def _extract_family_a(body: str, fields: dict, meta: dict) -> None:
    """旧テンプレ（lead / essay / sources / site-directory-links）からの best-effort 抽出。"""
    lead = slice_by_class(body, "p", "lead")
    if lead:
        fields["lead_html"] = lead[0].strip()
    src = slice_by_class(body, "div", "sources")
    if src:
        fields["sources_html"] = src[0].strip()
    nav = slice_by_class(body, "nav", "site-directory-links")
    if nav:
        fields["site_directory_html"] = nav[0].strip()
    essay = slice_by_class(body, "div", "essay")
    if essay:
        # 旧テンプレは本文が単一 essay（h3 小節）で番号 section に割れていない。
        fields["sections"] = [{"num": None, "title": "Essay",
                               "body_html": essay[0].strip()}]


def extract_en_candidate_fields(en_html: str, slug: str) -> tuple[dict, dict]:
    """EN 素材から正本候補フィールドを抽出（正本 JSON には書かない）。
    返り値: (fields, meta)。fields は EN_CANDIDATE_FIELDS をキーに持つ（無いものは None）。"""
    n_rev = len(REV_OPEN_RE.findall(en_html))
    n_editred = en_html.count("edit-red")
    cleaned = unwrap_rev_spans(strip_edit_red(strip_review_css(en_html)))
    cleaned, delinked = localize_en_links(cleaned)
    body = _body_of(cleaned)

    fields = {k: None for k in EN_CANDIDATE_FIELDS}
    meta = {
        "rev_unwrapped": n_rev,
        "edit_red_removed": n_editred,
        "delinked": delinked,
        "supplementary": [],
        "checks": self_check(cleaned, context="EN"),
    }
    if "ph-section__num" in body or "ph-abstract" in body:
        family = "B"
    elif re.search(r'class="[^"]*\blead\b', body) or 'class="essay"' in body:
        family = "A"
    else:
        family = "unknown"
    meta["family"] = family

    cite_ids = [int(x) for x in CITE_ID_RE.findall(body)]
    fields["cite_ids"] = cite_ids or None
    supref = sorted({int(x) for x in SUPREF_RE.findall(body)})
    fields["supref_ids"] = supref or None

    if family == "B":
        _extract_family_b(body, fields, meta)
    elif family == "A":
        _extract_family_a(body, fields, meta)
    return fields, meta


def extract_en_fragment(en_html: str, slug: str) -> tuple[dict, dict]:
    """importer の --en パス用ラッパ。候補フィールド抽出を呼び、人手移植用の
    プレビュー断片に整形する（返り値の契約は v1 と互換＋候補フィールドを同梱）。"""
    fields, meta = extract_en_candidate_fields(en_html, slug)
    sections = fields.get("sections") or []
    fragment = {
        "_note": "v2 抽出のプレビュー断片。正本 data/photographers-en-content.json には未注入。",
        "slug": slug,
        "family": meta["family"],
        "section_count": len(sections),
        "candidate_fields": fields,
        "_review": [
            "section の粒度・タイトルが正本スキーマ（Background/Core 等）に対応するか確認",
            "Family B は ph-* クラス体系。正本（旧クラス体系）へ移植時にクラス変換が要る",
            "lead / thesis / sources(cite) / site_directory を正本フィールドへ手で割り当てる",
            "localize 済みリンク・de-link 済み箇所が意図どおりか確認",
        ],
    }
    report = {
        "rev_unwrapped": meta["rev_unwrapped"],
        "edit_red_removed": meta["edit_red_removed"],
        "delinked": meta["delinked"],
        "checks": meta["checks"],
        "family": meta["family"],
        "section_count": len(sections),
        "section_titles": [s.get("title") for s in sections],
        "extracted_fields": [k for k, v in fields.items() if v],
        "supplementary": meta["supplementary"],
    }
    return fragment, report


# ── 読み取り専用コーパス監査（Phase 1・正本/HTML 不可触・書込は outputs/ のみ） ─

CONTENT_JSON = REPO / "data" / "photographers-en-content.json"
STAGE4_JSON = REPO / "data" / "photographers-en-stage4.json"

# EN 素材ファイルの判定（JA 素材を除外）。大文字 "EN" サフィックス（例 morimuraEN /
# 「… EN」）または小文字トークン "_en" / "-en"（例 michio-hoshino_en / toyoko-tokiwa-en）。
# IGNORECASE は使わない（"eugene" の "en"・"kenta" の "en" を誤検知するため）。
EN_FILE_RE = re.compile(r'EN|[_-]en')


def _load_canonical_pages() -> dict:
    """正本 EN ページ = content.json['pages'] に stage4['pages'] を後勝ち merge（builder と同順）。"""
    pages = dict(json.loads(CONTENT_JSON.read_text(encoding="utf-8"))["pages"])
    if STAGE4_JSON.exists():
        pages.update(json.loads(STAGE4_JSON.read_text(encoding="utf-8")).get("pages", {}))
    return pages


def _hero_name(en_html: str) -> str | None:
    body = _body_of(en_html)
    m = re.search(r'ph-hero__name">([^<]+)<', body) or re.search(r'<h1[^>]*>(.*?)</h1>', body, re.S)
    return norm_text(m.group(1)) if m else None


def _build_name_index(pages: dict) -> dict:
    """正本 h1 / title 先頭 → page-key。素材の hero 名で正本エントリを引くため。"""
    idx = {}
    for key, e in pages.items():
        h1 = (e.get("h1") or "").strip()
        if h1:
            idx.setdefault(norm_text(h1).lower(), key)
    return idx


def _match_canonical(en_html: str, pages: dict, name_index: dict) -> tuple[str | None, str | None]:
    """素材を正本 page-key に対応づける。返り値 (key, hero_name)。"""
    hero = _hero_name(en_html)
    if not hero:
        return None, None
    key = name_index.get(hero.lower())
    if key:
        return key, hero
    # ゆるい部分一致（hero がフルネーム、正本 h1 がその一部などの揺れ吸収）
    hl = hero.lower()
    for nm, k in name_index.items():
        if nm and (nm in hl or hl in nm):
            return k, hero
    return None, hero


def _compare_field(field: str, extracted, canonical) -> dict:
    """1 フィールドの抽出↔正本 diff。テキスト一致と raw 一致を分けて記録。"""
    ext_present = extracted not in (None, [], "")
    can_present = canonical not in (None, [], "")
    rec = {"extracted": ext_present, "canonical": can_present}
    if field in ("cite_ids", "supref_ids"):
        es, cs = set(extracted or []), set(canonical or [])
        rec.update({
            "extracted_count": len(es), "canonical_count": len(cs),
            "set_equal": es == cs,
            "only_extracted": sorted(es - cs), "only_canonical": sorted(cs - es),
        })
        return rec
    if field == "sections":
        ex, cn = extracted or [], canonical or []
        rec.update({
            "extracted_count": len(ex), "canonical_count": len(cn),
            "count_match": len(ex) == len(cn),
            "extracted_titles": [s.get("title") for s in ex],
            "canonical_titles": [s.get("title") for s in cn],
            "title_text_match": [norm_text(s.get("title")) for s in ex]
                                == [norm_text(s.get("title")) for s in cn],
        })
        if ex and cn and len(ex) == len(cn):
            rec["body_text_match"] = all(
                norm_text(a.get("body_html")) == norm_text(b.get("body_html"))
                for a, b in zip(ex, cn))
        return rec
    if ext_present and can_present:
        rec["text_match"] = norm_text(extracted) == norm_text(canonical)
        rec["markup_identical"] = str(extracted).strip() == str(canonical).strip()
    return rec


def run_audit(corpus_dir: Path) -> int:
    """素材 dir の EN 素材を一括抽出し、既存正本と read-only で diff。
    レポートを outputs/import-preview/audit-<ts>.{json,md} へ書く。正本/HTML は触らない。"""
    import datetime
    if not corpus_dir.exists():
        sys.stderr.write(f"ERROR: 監査対象 dir が見つからない: {corpus_dir}\n")
        return 2
    pages = _load_canonical_pages()
    name_index = _build_name_index(pages)
    text_fields = [f for f in EN_CANDIDATE_FIELDS
                   if f not in ("cite_ids", "supref_ids", "sections")]

    en_files = sorted(p for p in corpus_dir.glob("*.html") if EN_FILE_RE.search(p.name))
    per_file = []
    for p in en_files:
        en_html = p.read_text(encoding="utf-8", errors="replace")
        try:
            fields, meta = extract_en_candidate_fields(en_html, p.stem)
        except AssertionError as e:
            per_file.append({"file": p.name, "error": str(e)})
            continue
        key, hero = _match_canonical(en_html, pages, name_index)
        entry = {
            "file": p.name, "hero": hero, "family": meta["family"],
            "matched_key": key,
            "delinked": meta["delinked"], "supplementary": meta["supplementary"],
            "extracted": {f: (fields[f] not in (None, [], "")) for f in EN_CANDIDATE_FIELDS},
        }
        if key and pages.get(key):
            can = pages[key]
            entry["fields"] = {
                f: _compare_field(f, fields.get(f), can.get(f))
                for f in EN_CANDIDATE_FIELDS
            }
        per_file.append(entry)

    # ── 集計（family 別） ───────────────────────────────────────────────
    summary = {}
    for fam in ("A", "B", "unknown"):
        rows = [e for e in per_file if e.get("family") == fam and "fields" in e]
        if not rows:
            summary[fam] = {"matched_files": 0}
            continue
        fam_sum = {"matched_files": len(rows), "fields": {}}
        for f in EN_CANDIDATE_FIELDS:
            recs = [e["fields"][f] for e in rows]
            extracted = sum(1 for r in recs if r["extracted"])
            comparable = [r for r in recs if r["extracted"] and r["canonical"]]
            d = {"extracted": extracted, "of": len(rows),
                 "comparable": len(comparable)}
            if f in ("cite_ids", "supref_ids"):
                d["set_equal"] = sum(1 for r in comparable if r.get("set_equal"))
            elif f == "sections":
                d["count_match"] = sum(1 for r in comparable if r.get("count_match"))
                d["body_text_match"] = sum(1 for r in comparable if r.get("body_text_match"))
            else:
                d["text_match"] = sum(1 for r in comparable if r.get("text_match"))
                d["markup_identical"] = sum(1 for r in comparable if r.get("markup_identical"))
            fam_sum["fields"][f] = d
        summary[fam] = fam_sum

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    report = {
        "_note": "Phase 1 read-only audit。正本/HTML は不可触。書込は outputs/ のみ。",
        "generated_at": ts, "corpus_dir": str(corpus_dir),
        "en_files": len(en_files),
        "matched": sum(1 for e in per_file if e.get("matched_key")),
        "summary": summary, "per_file": per_file,
    }
    out_json = PREVIEW_DIR / f"audit-{ts}.json"
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out_md = PREVIEW_DIR / f"audit-{ts}.md"
    out_md.write_text(_render_audit_md(report), encoding="utf-8")

    print(f"監査: EN素材 {len(en_files)} 件 / 正本マッチ {report['matched']} 件")
    for fam in ("A", "B", "unknown"):
        s = summary[fam]
        print(f"  Family {fam}: matched={s['matched_files']}")
    print(f"  → {out_json.relative_to(REPO)}")
    print(f"  → {out_md.relative_to(REPO)}")
    return 0


def _render_audit_md(report: dict) -> str:
    L = []
    L.append(f"# EN 抽出カバレッジ監査 — {report['generated_at']}")
    L.append("")
    L.append(f"- 素材dir: `{report['corpus_dir']}`")
    L.append(f"- EN素材: {report['en_files']} 件 / 正本マッチ: {report['matched']} 件")
    L.append("- **read-only**: 正本JSON・HTMLは不可触。書込は `outputs/import-preview/` のみ。")
    L.append("")
    for fam, label in (("A", "旧テンプレ＝正本と同クラス体系"),
                       ("B", "新v5.1 ph-* テンプレ＝要クラス変換"),
                       ("unknown", "判定不能")):
        s = report["summary"].get(fam, {})
        n = s.get("matched_files", 0)
        L.append(f"## Family {fam} — {label}（マッチ {n} 件）")
        if not n:
            L.append("\n（該当なし）\n")
            continue
        L.append("")
        L.append("| field | 抽出/対象 | 比較可 | テキスト一致 | raw一致/構造 |")
        L.append("|---|---|---|---|---|")
        for f in EN_CANDIDATE_FIELDS:
            d = s["fields"][f]
            ext = f"{d['extracted']}/{d['of']}"
            comp = d["comparable"]
            if f in ("cite_ids", "supref_ids"):
                tm = f"set_equal {d.get('set_equal', 0)}/{comp}"
                rm = "—"
            elif f == "sections":
                tm = f"body {d.get('body_text_match', 0)}/{comp}"
                rm = f"count {d.get('count_match', 0)}/{comp}"
            else:
                tm = f"{d.get('text_match', 0)}/{comp}"
                rm = f"{d.get('markup_identical', 0)}/{comp}"
            L.append(f"| {f} | {ext} | {comp} | {tm} | {rm} |")
        L.append("")
    L.append("## ファイル別")
    L.append("")
    L.append("| file | family | matched key | 抽出フィールド数 | de-link | supplementary |")
    L.append("|---|---|---|---|---|---|")
    for e in report["per_file"]:
        if "error" in e:
            L.append(f"| {e['file']} | — | ERROR | {e['error'][:40]} | — | — |")
            continue
        nf = sum(1 for v in e["extracted"].values() if v)
        supp = ",".join(s["num"] for s in e.get("supplementary", [])) or "—"
        L.append(f"| {e['file']} | {e['family']} | {e.get('matched_key') or '—'} "
                 f"| {nf}/{len(EN_CANDIDATE_FIELDS)} | {len(e.get('delinked', []))} | {supp} |")
    L.append("")
    return "\n".join(L)


# ── Step3a: EN 正本 stage4 への thesis 最小注入（Claude×Codex×Daisuke 合意 2026-06-21） ──
#
# スコープ（合意済・最小）: 注入先は data/photographers-en-stage4.json のみ。注入フィールドは
# thesis_label / thesis_html だけ（sections 等は Step3b＝ph-* → 旧クラス変換器を入れてから）。
# 安全契約: `--update-en-json` 既定OFF・`--apply` 二重明示で実書込・slug 単位 replace/add・
# 対象外 JSON 差分ゼロ assert・atomic write・手書き維持ページ拒否・churn なし（dump 厳格）・
# 注入後に build → thesis 不消失 / sources・cite・supref 非減少 / dangling なし を検証。

# thesis_label はサイト全体で単一定数（content.json 全 entry で一致）。素材の表記揺れは採らない。
CANONICAL_THESIS_LABEL = "What this photographer changed"

# 手書き維持ページ（ブラインド再生成・注入禁止）。正は scripts/check_en_entry.py の
# HAND_MAINTAINED_EN。lee-miller は feedback_lee_miller_no_blind_rebuild に従い追加。
HAND_MAINTAINED_EN = {
    'stieglitz.html', 'annie-leibovitz.html', 'shoji-ueda.html',
    'toyoko-tokiwa.html', 'lee-miller.html',
}

# EN 内部リンク（生成物の規約 = /en/<種別>/<slug>.html）
EN_INTERNAL_HREF_RE = re.compile(r'/en/(photographers|movements|countries|eras)/([^"#?]+\.html)')


def _dump_stage4(data) -> str:
    """stage4.json の既存フォーマットに完全一致する dump（ensure_ascii=False, indent=2,
    末尾改行なし）。これを外すと無関係行の churn が出るため厳格に合わせる。"""
    return json.dumps(data, ensure_ascii=False, indent=2)


def _count_cite_supref(html: str) -> tuple[int, int]:
    cites = set(re.findall(r'id="cite-(\d+)"', html))
    suprefs = set(re.findall(r'href="#cite-(\d+)"', html))
    return len(cites), len(suprefs)


def _dangling_internal_en_links(html: str) -> list[str]:
    """生成物 EN HTML 内の /en/.../<slug>.html リンクのうち、実ファイルが無いものを列挙。"""
    masked, _ = _mask_scripts(html)
    bad = []
    for m in ANCHOR_RE.finditer(masked):
        href = m.group(1)
        mm = EN_INTERNAL_HREF_RE.fullmatch(href)
        if mm and not (REPO / "en" / mm.group(1) / mm.group(2)).exists():
            bad.append(href)
    return bad


def _assert_only_key_changed(old: dict, new: dict, key: str) -> None:
    """stage4 全体で『pages[key] 以外は完全に不変』を assert（対象外 JSON 差分ゼロ）。"""
    assert set(old) == set(new), "トップレベルキーが変化した"
    for tk in old:
        if tk == "pages":
            continue
        assert old[tk] == new[tk], f"トップレベル {tk} が変化した"
    op, np_ = old.get("pages", {}), new.get("pages", {})
    assert set(np_) - set(op) <= {key}, "対象以外の新規キーが増えた"
    assert set(op) - set(np_) == set(), "既存キーが消えた"
    for k in op:
        if k == key:
            continue
        a = json.dumps(op[k], ensure_ascii=False, sort_keys=True)
        b = json.dumps(np_[k], ensure_ascii=False, sort_keys=True)
        assert a == b, f"対象外キー {k} の内容が変化した"


def _print_step3a_runbook(slug: str) -> None:
    print("\n" + "=" * 70)
    print("Step3a の後段（push 前に必須・対象 slug スコープ）")
    print("=" * 70)
    print(f"  python3 scripts/build_photographers_en.py --slug {slug}   # EN 再生成（注入反映）")
    print(f"  python3 scripts/check_new_photographer.py --slug {slug}   # 完成検査")
    print( "  git diff --name-only en/photographers/                    # 対象 1 ファイルだけのはず")
    print( "  python3 scripts/preflight.py                              # push 前ネット")
    print( "\n注意: 注入は thesis_label / thesis_html のみ。sections 等は Step3b（クラス変換）で。")


def _verify_after_inject(slug: str, key: str, new_entry: dict, old_html: str) -> int:
    """注入＋ stage4 書込の後に build し、非劣化を検証。"""
    import subprocess
    print("\n── 注入後の検証（build → 非劣化チェック） ──")
    r = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "build_photographers_en.py"), "--slug", slug],
        capture_output=True, text=True)
    out = r.stdout + r.stderr
    if "SKIPPED" in out and key in out:
        sys.stderr.write("ERROR: builder が content-loss guard で SKIP（手書き内容消失の恐れ）。注入を見直す。\n")
        return 3
    if "Wrote 1 page" not in out and "Would write" not in out:
        sys.stderr.write(f"ERROR: builder が対象 1 ページを書いていない。出力:\n{out[-400:]}\n")
        return 3
    new_path = EN_DIR / f"{slug}.html"
    new_html = new_path.read_text(encoding="utf-8")

    if norm_text(new_entry["thesis_html"]) not in norm_text(new_html):
        sys.stderr.write("ERROR: 注入後 HTML に thesis 本文が見当たらない。\n")
        return 3
    oc, osup = _count_cite_supref(old_html)
    nc, nsup = _count_cite_supref(new_html)
    if nc < oc or nsup < osup:
        sys.stderr.write(f"ERROR: cite/supref が減少（cite {oc}->{nc} / supref {osup}->{nsup}）。\n")
        return 3
    dang = _dangling_internal_en_links(new_html)
    if dang:
        sys.stderr.write(f"ERROR: dangling 内部リンク発生: {dang}\n")
        return 3

    print(f"  build           : OK（対象1ページ・SKIP なし）")
    print(f"  thesis 本文存在 : OK")
    print(f"  cite / supref   : {oc}→{nc} / {osup}→{nsup}（非減少）")
    print(f"  dangling 内部   : なし")
    print(f"  対象 HTML       : {'変化なし（冪等注入＝byte不変）' if new_html == old_html else '変化あり（thesis 更新）'}")
    _print_step3a_runbook(slug)
    return 0


def inject_thesis_to_stage4(slug: str, en_path: str, apply: bool) -> int:
    """Step3a: EN 素材の thesis_label / thesis_html を stage4.json へ最小注入。"""
    key = slug + ".html"
    print(f"Step3a thesis 注入  slug={slug}  key={key}  mode={'APPLY' if apply else 'dry-run'}")

    if key in HAND_MAINTAINED_EN:
        sys.stderr.write(f"ERROR: {key} は手書き維持ページ。注入を拒否（HAND_MAINTAINED_EN）。\n")
        return 2

    en_src = Path(en_path)
    if not en_src.exists():
        sys.stderr.write(f"ERROR: EN 素材が見つからない: {en_src}\n")
        return 2
    fields, meta = extract_en_candidate_fields(en_src.read_text(encoding="utf-8"), slug)
    thesis_html = (fields.get("thesis_html") or "").strip()
    if not thesis_html:
        sys.stderr.write("ERROR: EN 素材から thesis_html を抽出できない"
                         f"（family={meta['family']}）。Family B の ph-thesis を持つ素材のみ対象。\n")
        return 2

    content = json.loads(CONTENT_JSON.read_text(encoding="utf-8"))
    stage4 = json.loads(STAGE4_JSON.read_text(encoding="utf-8"))
    s4pages = stage4.setdefault("pages", {})
    in_stage4 = key in s4pages
    base = s4pages.get(key) or content.get("pages", {}).get(key)
    if base is None or not base.get("h1"):
        sys.stderr.write("ERROR: 既存フル正本 entry が無い。Step3a は既掲載写真家の thesis 更新のみ"
                         "（新規写真家のフルページ作成は対象外）。\n")
        return 2

    old_label, old_thesis = base.get("thesis_label"), (base.get("thesis_html") or "").strip()
    new_entry = copy.deepcopy(base)
    new_entry["thesis_label"] = CANONICAL_THESIS_LABEL
    new_entry["thesis_html"] = thesis_html

    idempotent = (old_label == CANONICAL_THESIS_LABEL and old_thesis == thesis_html)
    print(f"  thesis_label : {old_label!r} → {CANONICAL_THESIS_LABEL!r}"
          f"{'（不変）' if old_label == CANONICAL_THESIS_LABEL else '（定数へ正規化）'}")
    print(f"  thesis_html  : {'不変（冪等）' if old_thesis == thesis_html else '更新'}")
    print(f"  base 由来     : {'stage4 既存 shadow' if in_stage4 else 'content.json（→ stage4 へ full shadow 作成）'}")
    if not in_stage4:
        print("  ⚠ NOTE: stage4 に full shadow を作る。以後この slug は content.json 編集が"
              " stage4 に隠れる（後勝ち）。Step3b で部分マージ化を検討。")

    new_stage4 = copy.deepcopy(stage4)
    new_stage4["pages"][key] = new_entry
    _assert_only_key_changed(stage4, new_stage4, key)  # 対象外 JSON 差分ゼロ
    new_text = _dump_stage4(new_stage4)

    if not apply:
        print("\n  (dry-run) stage4 未書込。実書込＋ビルド検証は `--apply` を付ける。")
        if idempotent:
            print("  （注: 抽出 thesis は現正本と一致＝冪等。注入してもビルド出力は byte 不変の見込み）")
        _print_step3a_runbook(slug)
        return 0

    old_html_path = EN_DIR / f"{slug}.html"
    old_html = old_html_path.read_text(encoding="utf-8") if old_html_path.exists() else ""
    tmp = STAGE4_JSON.with_name(STAGE4_JSON.name + ".tmp")
    tmp.write_text(new_text, encoding="utf-8")
    os.replace(tmp, STAGE4_JSON)  # atomic
    print(f"  ✅ stage4 atomic 書込: {STAGE4_JSON.relative_to(REPO)}")

    return _verify_after_inject(slug, key, new_entry, old_html)


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
        description="ChatGPT 写真家 HTML 素材の決定論インポータ（JA 整形 + EN 候補抽出・v2）",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug", help="出力 slug（例 yasumasa-morimura）")
    ap.add_argument("--ja", help="JA 素材 HTML のパス")
    ap.add_argument("--en", help="EN 素材 HTML のパス（省略可。あれば候補抽出）")
    ap.add_argument("--idx", type=int, help="hero 眉採番に使う idx（省略時 card-data から解決）")
    ap.add_argument("--apply", action="store_true", help="実書き込み（無指定は dry-run）")
    ap.add_argument("--force", action="store_true", help="既存 photographers/<slug>.html を上書き（backup あり）")
    ap.add_argument("--audit-corpus", metavar="DIR",
                    help="読み取り専用監査モード: DIR の EN 素材を一括抽出し既存正本と diff "
                         "（正本/HTML 不可触・書込は outputs/import-preview/ のみ）")
    ap.add_argument("--update-en-json", action="store_true",
                    help="Step3a: EN 素材の thesis を data/photographers-en-stage4.json へ最小注入"
                         "（--apply 二重明示で実書込・atomic・非劣化検証。--slug と --en 必須）")
    args = ap.parse_args(argv)

    # 監査モード（read-only）。slug/ja は不要。
    if args.audit_corpus:
        return run_audit(Path(args.audit_corpus).expanduser())

    # Step3a 注入モード。--ja は不要（EN 正本 JSON への注入のみ）。
    if args.update_en_json:
        if not args.slug or not args.en:
            ap.error("--update-en-json は --slug と --en が必須")
        return inject_thesis_to_stage4(args.slug, args.en, args.apply)

    if not args.slug or not args.ja:
        ap.error("通常モードは --slug と --ja が必須（監査は --audit-corpus）")

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
