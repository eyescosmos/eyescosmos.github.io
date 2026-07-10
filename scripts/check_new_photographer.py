#!/usr/bin/env python3
"""check_new_photographer.py — 新規写真家ページの「完成検査」門番。

役割（Claude×Codex 合意 2026-06-19・[[project_new_photographer_guard]]）:
- 既存ガード群は「壊した・消した」を止める。本ツールは新規ページの
  「置き忘れた／標準構造で作れていない」を **明示の slug 単位** で検査する。
- 検査は「構造の健全さ」＋「決定論的な cite 整合」に絞る。
  本文の文言評価・曖昧判定（Biography 先頭文言 等）は持ち込まない
  （check_photographer_link_integrity.py との二重実行で WARN を増殖させない）。

使い方:
    python3 scripts/check_new_photographer.py --slug <slug>          # 完成検査
    python3 scripts/check_new_photographer.py --slug <slug> --strict-new
    python3 scripts/check_new_photographer.py --all                  # 全 JA ページを一覧検査
  slug は通称可（atget→eugene-atget）。en_content.resolve_slug で吸収する。

判定レベル（preflight と check_new で写像が変わる）:
    hard … 常に HARD。決定論的で既存295ページがグリーンな破損のみ。
    gate … 完成ゲート。check_new では HARD、preflight 常時では WARN。
    warn … 不足。check_new 既定は WARN。--strict-new で HARD 昇格。
    soft … 常に WARN。正当な遅延・偽陽性がありうるもの（手貼り遅延等）。

JSON-LD は実体準拠（実測 2026-06-19・JA=Person 295/295・EN=@graph 295/295）:
    JA は Person 型の存在＋parse 可を要求。WebPage/BreadcrumbList は JA 必須にしない。
    EN は @graph 存在＋parse 可を見るが、BreadcrumbList(282/295) は HARD にしない。

実測でグリーンにならなかったため常時 HARD にしない決定:
    cite 欠番/不連続（5ページ。出典除去で番号を残す正当ケースあり）→ warn
    cite orphan（60ページ。出典のみ掲載は一般的）→ soft・preflight では出さない
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

try:
    import en_content  # noqa: E402  EN slug 解決と pages 読み込み
except Exception:  # noqa: BLE001
    en_content = None

# ── 判定レベル ────────────────────────────────────────────────
HARD, GATE, WARN, SOFT = "hard", "gate", "warn", "soft"

# preflight 常時では「他チェックが既にカバー」または「ノイズ」な code を出さない。
#   SEO 欠落系 → check_ja_seo_holes / check_ga_coverage が担当。
#   orphan cite / 空セクション / 本文リンク僅少 → 既存295で頻出＝ノイズ。
SKIP_IN_PREFLIGHT = {
    "ga_missing", "canonical_absent", "ogp_absent", "twitter_absent",
    "hreflang_absent", "nosnippet_absent", "description_absent", "jsonld_absent",
    "cite_orphan", "works_empty", "further_empty", "related_empty",
    "body_links_scarce", "en_breadcrumb_absent", "body_shape_nonstandard",
    "description_empty", "ogp_empty",
}

# 本文レイアウトの正の型（参照実装 ansel-adams.html・実測270/295が準拠）。
# essay 節は原則この並び：背景と時代 → 表現の核心 → 代表作・方法・媒体 → 批評と写真史上の位置。
# 長さは写真家ごとに増減してよいが、節名は標準ボキャブラリに揃える。
CANON_SECTION_TOKENS = ("背景と時代", "表現の核心", "代表作", "批評と写真史")
NON_ESSAY_SECTION_NAMES = {"作品を見る", "関連する写真家・運動", "さらに読む", "出典"}

LEGACY_MARKERS = (
    r'class="lang-toggle"', r'class="lang-btn"', r'class="title-block"',
    r'class="lead-abstract"', r'class="facts"', r'<table[^>]*class="facts"',
)


class Finding:
    __slots__ = ("code", "level", "msg")

    def __init__(self, code: str, level: str, msg: str):
        self.code, self.level, self.msg = code, level, msg


# ── 小道具 ────────────────────────────────────────────────────
def ja_path(slug: str) -> Path:
    return REPO / "photographers" / f"{slug}.html"


def en_path(slug: str) -> Path:
    return REPO / "en" / "photographers" / f"{slug}.html"


def _jsonld_blocks(html: str) -> list[str]:
    return re.findall(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.S | re.I)


def _walk_types(obj, out: list[str]) -> None:
    if isinstance(obj, dict):
        if "@graph" in obj:
            for g in obj["@graph"]:
                _walk_types(g, out)
        t = obj.get("@type")
        if isinstance(t, list):
            out.extend(t)
        elif t:
            out.append(t)
        for v in obj.values():
            if isinstance(v, (dict, list)):
                _walk_types(v, out)
    elif isinstance(obj, list):
        for x in obj:
            _walk_types(x, out)


def _person_urls(obj, out: list[str]) -> None:
    if isinstance(obj, dict):
        if "@graph" in obj:
            for g in obj["@graph"]:
                _person_urls(g, out)
        if obj.get("@type") == "Person" and obj.get("url"):
            out.append(obj["url"])
        for v in obj.values():
            if isinstance(v, (dict, list)):
                _person_urls(v, out)
    elif isinstance(obj, list):
        for x in obj:
            _person_urls(x, out)


def _meta_content(html: str, *, prop: str = "", name: str = "") -> str | None:
    if prop:
        m = re.search(
            rf'<meta[^>]*property=["\']{re.escape(prop)}["\'][^>]*content=["\']([^"\']*)["\']',
            html, re.I)
    else:
        m = re.search(
            rf'<meta[^>]*name=["\']{re.escape(name)}["\'][^>]*content=["\']([^"\']*)["\']',
            html, re.I)
    return m.group(1) if m else None


# ── JA 構造検査（本命）────────────────────────────────────────
def check_ja(slug: str, html: str) -> list[Finding]:
    f: list[Finding] = []
    self_tail = f"/photographers/{slug}.html"

    # 不可視必須（GA）
    if "googletagmanager" not in html:
        f.append(Finding("ga_missing", HARD, "GA(googletagmanager)欠落"))

    # コア骨格
    title = re.search(r'<title[^>]*>(.*?)</title>', html, re.S | re.I)
    if not (title and re.sub(r'<[^>]+>', '', title.group(1)).strip()):
        f.append(Finding("title_missing", HARD, "title 欠落 or 空"))
    if not re.search(r'<h1\b', html):
        f.append(Finding("h1_missing", HARD, "h1 欠落"))
    if not re.search(r'<main\b', html):
        f.append(Finding("main_missing", HARD, "main 欠落"))
    if not re.search(r'<header\b', html):
        f.append(Finding("header_missing", HARD, "header 欠落"))
    if not re.search(r'<footer\b', html):
        f.append(Finding("footer_missing", HARD, "footer 欠落"))

    # 旧デザイン生成器由来の構造マーカー
    for marker in LEGACY_MARKERS:
        if re.search(marker, html):
            f.append(Finding("legacy_marker", HARD,
                             f"旧デザイン構造マーカー混入: {marker}"))
            break

    # canonical（欠落=gate / 自slug不一致=hard）
    cm = re.search(
        r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', html, re.I)
    if not cm:
        f.append(Finding("canonical_absent", GATE, "canonical 未設定"))
    elif not cm.group(1).endswith(self_tail):
        f.append(Finding("canonical_mismatch", HARD,
                         f"canonical が自slug不一致: {cm.group(1)}"))

    # og:url（欠落=gateはOGP一括で見る / 自slug不一致=hard）
    ogurl = _meta_content(html, prop="og:url")
    if ogurl and not ogurl.endswith(self_tail):
        f.append(Finding("ogurl_mismatch", HARD, f"og:url が自slug不一致: {ogurl}"))

    # OGP（タグ欠落＝gate / 内容空＝soft 記入待ち。scaffold は空で出すため区別する）
    ogt = _meta_content(html, prop="og:title")
    ogd = _meta_content(html, prop="og:description")
    if ogt is None or ogd is None:
        f.append(Finding("ogp_absent", GATE, "OGP(title/description) 未設定"))
    elif not (ogt.strip() and ogd.strip()):
        f.append(Finding("ogp_empty", SOFT, "OGP description が空（記入する）"))
    if not (_meta_content(html, name="twitter:title") or _meta_content(html, name="twitter:card")):
        f.append(Finding("twitter_absent", WARN, "Twitter カード未設定"))
    # meta description（タグ欠落＝gate / 内容空＝soft 記入待ち）
    desc = _meta_content(html, name="description")
    if desc is None:
        f.append(Finding("description_absent", GATE, "meta description 未設定"))
    elif not desc.strip():
        f.append(Finding("description_empty", SOFT, "meta description が空（記入する）"))
    if "data-nosnippet" not in html:
        f.append(Finding("nosnippet_absent", GATE, "data-nosnippet 未設定"))
    has_en = en_path(slug).exists()
    if not re.search(r'hreflang=', html, re.I) and "noindex" not in html and has_en:
        f.append(Finding("hreflang_absent", WARN, "hreflang 未設定"))

    # 言語トグル: EN ボタンは <a href="/en/photographers/*.html"> で囲む。
    #   素材手組み時に link ラッパを付け忘れた bare <button>EN</button> を検出する
    #   （JA から EN へ切り替わらない・mayumi-hosokura で実発生）。
    #   EN slug は JA slug と異なる正当ケース（jp-* → romaji）があるためリンク先 slug は
    #   固定せず、EN ビルドは JA 確定後のため対象ファイルの実在も要求しない。
    lang_m = re.search(r'<div class="head__lang">(.*?)</div>', html, re.S)
    if lang_m and re.search(r'>\s*EN\s*<', lang_m.group(1)) and not re.search(
            r'href=["\']/en/photographers/[^"\']+\.html["\'][^>]*>\s*<button[^>]*>\s*EN\s*<',
            lang_m.group(1)):
        f.append(Finding("en_toggle_unlinked", GATE,
                         "言語トグルの EN ボタンが /en/photographers/*.html へ"
                         "リンクされていない（bare <button>EN</button>）"))

    # JSON-LD（JA=Person 存在＋parse 可）
    f += _check_jsonld_ja(html, self_tail)

    # 出典 ↔ sup-ref の決定論整合
    f += _check_cites(html)

    # 本文セクション §NN/全数 整合
    f += _check_section_numbering(html)

    # 完成度（空セクション・本文リンク僅少）
    f += _check_completeness(html)

    # 本文レイアウトの型（ansel-adams 準拠か）
    f += _check_body_shape(html)

    return f


def _section_names(html: str) -> list[str]:
    return [re.sub(r'<[^>]+>', '', m).strip()
            for m in re.findall(r'<span class="ph-section__name">(.*?)</span>', html, re.S)]


def _check_body_shape(html: str) -> list[Finding]:
    """essay 節が標準ボキャブラリ（背景と時代/表現の核心/代表作・方法・媒体/批評と写真史上の位置）
    に揃っているか。完成検査(--slug)専用の型ナッジ。長さの増減は許容し、薄い／型崩れだけ拾う。
    実測で 270/295 が準拠＝低ノイズ・preflight には入れない（SKIP_IN_PREFLIGHT）。"""
    essay = [n for n in _section_names(html) if n not in NON_ESSAY_SECTION_NAMES]
    if not essay or essay == ["解説"]:
        return [Finding("body_shape_nonstandard", SOFT,
                        "本文が単一『解説』節（薄い型）。標準は 背景と時代 / 表現の核心 / "
                        "代表作・方法・媒体 / 批評と写真史上の位置（参照: ansel-adams.html）")]
    hits = sum(any(tok in n for n in essay) for tok in CANON_SECTION_TOKENS)
    if hits < 2:
        return [Finding("body_shape_nonstandard", SOFT,
                        f"本文節名が標準ボキャブラリから外れている: {essay}。"
                        "標準は 背景と時代 / 表現の核心 / 代表作・方法・媒体 / 批評と写真史上の位置")]
    return []


def _check_jsonld_ja(html: str, self_tail: str) -> list[Finding]:
    f: list[Finding] = []
    blocks = _jsonld_blocks(html)
    if not blocks:
        f.append(Finding("jsonld_absent", GATE, "JSON-LD 未設定（JA=Person を入れる）"))
        return f
    types: list[str] = []
    urls: list[str] = []
    parse_failed = False
    for b in blocks:
        try:
            obj = json.loads(b)
        except Exception:  # noqa: BLE001
            parse_failed = True
            continue
        _walk_types(obj, types)
        _person_urls(obj, urls)
    if parse_failed:
        f.append(Finding("jsonld_parse", HARD, "JSON-LD が parse 不能"))
    if "Person" not in types and "Organization" not in types:
        f.append(Finding("jsonld_no_person", GATE,
                         "JSON-LD に Person/Organization 型が無い（JA は実体準拠）"))
    if urls and not any(u.endswith(self_tail) for u in urls):
        f.append(Finding("jsonld_url_mismatch", HARD,
                         f"JSON-LD Person.url が自slug不一致: {urls[:2]}"))
    return f


def _check_cites(html: str) -> list[Finding]:
    f: list[Finding] = []
    defined = [int(x) for x in re.findall(r'id="cite-(\d+)"', html)]
    referenced = set(int(x) for x in re.findall(r'href="#cite-(\d+)"', html))
    # dup（決定論・破損）
    seen, dups = set(), set()
    for n in defined:
        (dups if n in seen else seen).add(n)
    if dups:
        f.append(Finding("cite_dup", HARD, f"出典番号の重複: {sorted(dups)}"))
    # dangling（参照先 cite が実在しない・決定論・破損）
    dangling = sorted(referenced - set(defined))
    if dangling:
        f.append(Finding("cite_dangling", HARD,
                         f"sup-ref の参照先 cite が不在: {dangling}"))
    if defined:
        ds = sorted(set(defined))
        # 欠番/不連続（正当な出典除去がありうる→warn）
        if ds != list(range(1, len(ds) + 1)):
            f.append(Finding("cite_gap", WARN, f"出典番号が不連続: {ds}"))
        # orphan（定義のみで本文未参照・頻出→soft）
        orphan = sorted(set(defined) - referenced)
        if orphan:
            f.append(Finding("cite_orphan", SOFT, f"本文未参照の出典: {orphan}"))
    return f


def _check_section_numbering(html: str) -> list[Finding]:
    pairs = re.findall(r'§\s*(\d+)\s*/\s*(\d+)', html)
    if not pairs:
        return []
    nums = [int(a) for a, _ in pairs]
    totals = {int(b) for _, b in pairs}
    expected = len(pairs)
    problems = []
    if len(totals) != 1 or next(iter(totals)) != expected:
        problems.append(f"全数表記={sorted(totals)} だが §セクションは {expected} 個")
    if nums != list(range(1, expected + 1)):
        problems.append(f"連番が崩れている: {nums}")
    if problems:
        return [Finding("section_count_mismatch", WARN,
                        "本文セクションの §NN/全数 不整合: " + " / ".join(problems))]
    return []


def _section_body(html: str, label: str) -> str | None:
    """`§ <label>` セクションの ph-section__body 中身を返す。"""
    m = re.search(
        rf'§\s*{re.escape(label)}\b.*?<div class="ph-section__body">(.*?)</div>\s*</section>',
        html, re.S)
    return m.group(1) if m else None


def _check_completeness(html: str) -> list[Finding]:
    f: list[Finding] = []
    works = _section_body(html, "WORKS")
    if works is not None and "chip-link" not in works and "prep-block" in works:
        f.append(Finding("works_empty", SOFT, "「作品を見る」が準備中（chip-link 無し）"))
    rel = _section_body(html, "REL")
    if rel is not None and "ph-rel-list" not in rel and "prep-block" in rel:
        f.append(Finding("related_empty", SOFT, "「関連する写真家・運動」が準備中"))
    ref = _section_body(html, "REF")
    if ref is not None and "ph-book" not in ref and "ph-further-links" not in ref:
        f.append(Finding("further_empty", SOFT, "「さらに読む」が空"))
    # 本文内リンク（essay 内の内部リンク数）
    essays = re.findall(r'<div class="essay">(.*?)</div>\s*</div>\s*</section>', html, re.S)
    body = "\n".join(essays)
    internal = re.findall(r'href="(?:\.\./|/)(?:photographers|movements|en)/', body)
    if essays and not internal:
        f.append(Finding("body_links_scarce", SOFT,
                         "本文内に内部リンク（写真家/運動）が無い"))
    return f


# ── EN 軽量検査（EN closure は preflight 既存ガードに委譲・重複しない）─────
def check_en(slug: str, en_pages: dict | None) -> list[Finding]:
    f: list[Finding] = []
    p = en_path(slug)
    if not p.exists():
        f.append(Finding("en_missing", SOFT,
                         "EN ページ未生成（build_photographers_en.py --slug で生成）"))
        return f
    html = p.read_text(encoding="utf-8", errors="ignore")
    blocks = _jsonld_blocks(html)
    types: list[str] = []
    parse_failed = False
    has_graph = False
    for b in blocks:
        try:
            obj = json.loads(b)
        except Exception:  # noqa: BLE001
            parse_failed = True
            continue
        if isinstance(obj, dict) and "@graph" in obj:
            has_graph = True
        _walk_types(obj, types)
    if parse_failed:
        f.append(Finding("en_jsonld_parse", HARD, "EN JSON-LD が parse 不能"))
    elif blocks and not has_graph:
        f.append(Finding("en_graph_absent", WARN, "EN JSON-LD に @graph が無い"))
    if "BreadcrumbList" not in types and not parse_failed and blocks:
        f.append(Finding("en_breadcrumb_absent", SOFT,
                         "EN JSON-LD に BreadcrumbList が無い（任意改善）"))
    # EN 正本 JSON に slug があるか（無い＝EN closure 対象外の手作業ページの疑い）
    if en_pages is not None and f"{slug}.html" not in en_pages:
        f.append(Finding("en_json_absent", SOFT,
                         f"EN 正本 {en_content.JSON_PATH if en_content else 'photographers-en-content.json'}"
                         f" に {slug} が無い"))
    return f


# ── card-data 在席（全体・決定論）────────────────────────────
def carddata_missing_pages() -> list[str]:
    """card-data.json に id があるのに photographers/<id>.html が無いものを返す。"""
    data = json.loads((REPO / "card-data.json").read_text(encoding="utf-8"))
    missing = []
    for p in data.get("photographers", []):
        pid = p.get("id")
        if pid and not ja_path(pid).exists():
            missing.append(pid)
    return missing


def carddata_ids() -> set[str]:
    data = json.loads((REPO / "card-data.json").read_text(encoding="utf-8"))
    return {p.get("id") for p in data.get("photographers", []) if p.get("id")}


def check_slug(slug: str) -> tuple[str, list[Finding]]:
    """1 slug 分の全 Finding を集める。返り値 (実slug, findings)。"""
    findings: list[Finding] = []
    p = ja_path(slug)
    if not p.exists():
        return slug, [Finding("ja_missing", HARD,
                              f"photographers/{slug}.html が存在しない")]
    html = p.read_text(encoding="utf-8", errors="ignore")
    findings += check_ja(slug, html)
    en_pages = None
    if en_content is not None:
        try:
            en_pages = en_content.load_pages()
        except Exception:  # noqa: BLE001
            en_pages = None
    findings += check_en(slug, en_pages)
    if slug not in carddata_ids():
        findings.append(Finding("not_in_carddata", SOFT,
                                "card-data.json に未登録（アーカイブ/星座に出ない）"))
    return slug, findings


# ── CLI ───────────────────────────────────────────────────────
def _resolve(slug_arg: str) -> str | None:
    """通称を実 slug stem に解決。EN pages 経由（無ければ素通し）。"""
    if ja_path(slug_arg).exists():
        return slug_arg
    if en_content is not None:
        try:
            resolved, _cands = en_content.resolve_slug(slug_arg, en_content.load_pages())
            if resolved:
                return resolved[:-5]  # '.html' を外して JA stem へ
        except Exception:  # noqa: BLE001
            pass
    return slug_arg


def _report(slug: str, findings: list[Finding], *, strict_new: bool) -> int:
    """check_new としての写像: hard/gate=HARD、warn(strict時HARD)、soft=WARN。"""
    hard, warn = [], []
    for fd in findings:
        if fd.level == HARD or fd.level == GATE:
            hard.append(fd)
        elif fd.level == WARN:
            (hard if strict_new else warn).append(fd)
        else:  # SOFT
            warn.append(fd)
    print(f"── check_new_photographer: {slug} "
          f"{'(--strict-new)' if strict_new else ''} ──")
    if warn:
        print("  WARN（要確認）")
        for fd in warn:
            print(f"    ⚠ [{fd.code}] {fd.msg}")
    if hard:
        print("  FAIL（完成検査ブロック）")
        for fd in hard:
            print(f"    ✗ [{fd.code}] {fd.msg}")
        print(f"\n{slug}: NOT COMPLETE")
        return 1
    print(f"{slug}: OK（構造・cite 整合・JSON-LD 実体準拠 すべて通過）")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="新規写真家ページの完成検査")
    ap.add_argument("--slug", help="検査する slug（通称可）")
    ap.add_argument("--strict-new", action="store_true",
                    help="不足(WARN)の一部を HARD へ昇格して厳しく検査")
    ap.add_argument("--all", action="store_true",
                    help="全 JA 写真家ページを一覧検査（既存不具合の可視化）")
    args = ap.parse_args()

    if args.all:
        # 全体の決定論 HARD（card-data id にページが無い）
        miss = carddata_missing_pages()
        if miss:
            print(f"✗ card-data.json に id があるがページ不在: {miss}")
        bad = 0
        for p in sorted(glob.glob(str(REPO / "photographers" / "*.html"))):
            name = os.path.basename(p)
            if name.endswith("-backup.html"):
                continue
            slug = name[:-5]
            _slug, findings = check_slug(slug)
            hards = [fd for fd in findings if fd.level in (HARD, GATE)]
            if hards:
                bad += 1
                print(f"  {slug}: " + "; ".join(f"[{fd.code}]" for fd in hards))
        print(f"\n--all: {bad} ページに HARD 級の指摘（既存不具合の可視化）")
        return 0

    if not args.slug:
        ap.error("--slug または --all を指定してください")
    slug = _resolve(args.slug)
    _slug, findings = check_slug(slug)
    return _report(slug, findings, strict_new=args.strict_new)


if __name__ == "__main__":
    raise SystemExit(main())
