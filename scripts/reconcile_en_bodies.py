#!/usr/bin/env python3
"""
reconcile_en_bodies.py
======================
EN 写真家ページの正本 JSON（data/photographers-en-content.json）と
生成物 EN HTML（en/photographers/<slug>.html）の essay 本文ドリフトを
一覧（--report）・同期（--apply）するツール。

使い方:
  # 全 slug の drift を一覧
  python3 scripts/reconcile_en_bodies.py --report

  # 特定 slug だけ
  python3 scripts/reconcile_en_bodies.py --report --slug bruno-serralongue

  # HEAD 版 HTML で比較
  python3 scripts/reconcile_en_bodies.py --report --slug bruno-serralongue --head

  # JSON へ同期（明示 apply のみ・全自動なし）
  python3 scripts/reconcile_en_bodies.py --slug bruno-serralongue --apply

  # HEAD 版 HTML から同期
  python3 scripts/reconcile_en_bodies.py --slug bruno-serralongue --apply --head

preflight の auto-fix にはしない（push 前の暗黙書換は事故説明困難）。
明示 apply のみ。
"""

import argparse
import json
import os
import re
import subprocess
import sys
from typing import List, Optional, Set, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_JSON = os.path.join(ROOT, "data", "photographers-en-content.json")
STAGE4_JSON = os.path.join(ROOT, "data", "photographers-en-stage4.json")
EN_DIR = os.path.join(ROOT, "en", "photographers")

# 手書き維持ページ（apply 拒否対象）
HAND_MAINTAINED_EN = {
    "stieglitz.html",
    "annie-leibovitz.html",
    "shoji-ueda.html",
    "toyoko-tokiwa.html",
    "lee-miller.html",
}

# avedon 類型: 自動生成テンプレ語
TEMPLATE_PHRASES = [
    "Main themes:",
    "Key works:",
    "Critical reception:",
    "Historical significance:",
    "Artistic approach:",
    "Major works:",
    "Influences:",
    "Background:",
    "Early career:",
    "Later career:",
]


# ── essay balanced 抽出 ─────────────────────────────────────────────────────


def _extract_essays_balanced(html: str) -> List[str]:
    """HTML から <div class="essay">…</div> を balanced 抽出して順序リストで返す。

    非貪欲な正規表現（.*?）では入れ子 div（figure/blockquote 内の <div>）で
    最初の </div> で打ち切られるバグがある。
    balanced 版では <div +1 / </div> -1 をカウントし、対応する閉じ tag まで取る。

    返す各文字列は <div class="essay">…</div> 全体（ラッパ div 込み）=
    JSON body_html と同形。
    """
    results = []
    search_from = 0
    while True:
        start = html.find('<div class="essay">', search_from)
        if start == -1:
            break
        depth = 0
        i = start
        end = -1
        while i < len(html):
            if html[i : i + 4] == "<div":
                depth += 1
                i += 4
            elif html[i : i + 6] == "</div>":
                depth -= 1
                if depth == 0:
                    end = i + 6
                    break
                i += 6
            else:
                i += 1
        if end == -1:
            # 対応する閉じ tag が見つからない（破損 HTML）
            break
        results.append(html[start:end])
        search_from = end
    return results


def _has_nested_div(essay_html: str) -> bool:
    """essay div 内にラッパ以外の <div> があるか（入れ子 div の有無）。"""
    # ラッパ開始 tag の直後から内側を取り出す
    inner_start = essay_html.index(">") + 1
    inner_end = essay_html.rfind("</div>")
    inner = essay_html[inner_start:inner_end]
    return bool(re.search(r"<div", inner))


# ── テキスト正規化（比較用） ────────────────────────────────────────────────


def _strip_tags_normalize(html: str) -> str:
    """タグ除去・空白正規化した素テキスト（比較用）。"""
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _text_similarity(a: str, b: str) -> float:
    """素テキストの単純な類似度（0.0〜1.0）。共通文字数 / max 長。"""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    longer = max(len(a), len(b))
    # 共通部分の文字数（簡易: len(LCS) の近似として min を使う）
    common = sum(c1 == c2 for c1, c2 in zip(a, b))
    return common / longer


# ── HTML ソース取得 ──────────────────────────────────────────────────────────


def _get_html(slug_html: str, use_head: bool) -> Optional[str]:
    """slug_html (例: 'bruno-serralongue.html') の EN HTML を返す。
    use_head=True なら git show HEAD:... から取得、False なら作業ツリーから読む。
    """
    en_path = os.path.join(EN_DIR, slug_html)
    if use_head:
        rel = os.path.relpath(en_path, ROOT)
        result = subprocess.run(
            ["git", "show", f"HEAD:{rel}"],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        if result.returncode != 0:
            return None
        return result.stdout
    else:
        if not os.path.exists(en_path):
            return None
        with open(en_path, "r", encoding="utf-8") as f:
            return f.read()


# ── avedon 類型検知 ──────────────────────────────────────────────────────────


def _detect_avedon_flags(essay_html: str, sources_html: str) -> dict:
    """avedon 類型フラグを返す。
    - template_phrase: 自動生成テンプレ語が残っているか
    - orphan_cites: sources に存在しない #cite-N href が本文にあるか
    - duplicate_cites: 同一 href="#cite-N" が重複しているか
    """
    # テンプレ語
    found_phrases = [p for p in TEMPLATE_PHRASES if p in essay_html]

    # cite orphan / duplicate
    defined = set(re.findall(r'id="cite-(\d+)"', sources_html))
    used_all = re.findall(r'href="#cite-(\d+)"', essay_html)
    used_set = set(used_all)
    orphans = sorted(used_set - defined) if defined else []
    duplicates = sorted(
        {c for c in used_all if used_all.count(c) > 1}
    )

    return {
        "template_phrases": found_phrases,
        "orphan_cites": orphans,
        "duplicate_cites": duplicates,
    }


# ── content.json 操作 ───────────────────────────────────────────────────────


def _load_content_json() -> Tuple[bytes, dict]:
    """(raw_bytes, parsed_dict) を返す。"""
    with open(CONTENT_JSON, "rb") as f:
        raw = f.read()
    data = json.loads(raw)
    return raw, data


def _dump_content_json(data: dict) -> bytes:
    """churn-safe dump（ensure_ascii=False, indent=2, 末尾改行なし）。"""
    return json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")


def _assert_roundtrip(raw: bytes, data: dict) -> None:
    """load→dump が元バイトと完全一致することを assert（churn ゼロ証明）。"""
    dumped = _dump_content_json(data)
    if raw != dumped:
        raise RuntimeError(
            f"Round-trip churn detected: "
            f"original={len(raw)} bytes, dumped={len(dumped)} bytes. "
            f"dump 設定が合っていないため中断します。"
        )


def _atomic_write(path: str, content: bytes) -> None:
    """原子的書き込み（.tmp → os.replace）。"""
    tmp = path + ".tmp"
    try:
        with open(tmp, "wb") as f:
            f.write(content)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def _assert_only_sections_changed(
    old_raw: bytes, new_raw: bytes, changed_slugs: Set[str]
) -> None:
    """content.json の変化が changed_slugs の sections フィールドだけに限定されることを assert。
    それ以外の slug・フィールドが 1 文字でも変われば例外を raise する。
    """
    old_data = json.loads(old_raw)
    new_data = json.loads(new_raw)

    # トップレベルキー不変
    assert set(old_data) == set(new_data), "トップレベルキーが変化した"

    # _meta 不変
    for k in old_data:
        if k == "pages":
            continue
        assert old_data[k] == new_data[k], f"トップレベル {k!r} が変化した"

    old_pages = old_data.get("pages", {})
    new_pages = new_data.get("pages", {})

    # ページ数不変
    assert set(old_pages) == set(new_pages), "pages のキーセットが変化した"

    for slug, old_p in old_pages.items():
        new_p = new_pages[slug]
        if slug in changed_slugs:
            # 対象 slug は sections のみ変化可
            for field in old_p:
                if field == "sections":
                    continue  # sections は変化してよい
                a = json.dumps(old_p[field], ensure_ascii=False, sort_keys=True)
                b = json.dumps(new_p.get(field), ensure_ascii=False, sort_keys=True)
                assert a == b, f"対象 slug {slug!r} の {field!r} が予期せず変化した"
        else:
            # 対象外 slug は全フィールド不変
            a = json.dumps(old_p, ensure_ascii=False, sort_keys=True)
            b = json.dumps(new_p, ensure_ascii=False, sort_keys=True)
            assert a == b, f"対象外 slug {slug!r} の内容が変化した"


# ── stage4 確認 ─────────────────────────────────────────────────────────────


def _stage4_has_sections(slug_html: str) -> bool:
    """stage4.json に sections を持つエントリとして存在するか確認。
    該当する場合、content.json への書込が stage4 により上書きされる可能性があるため
    apply を拒否すべき。"""
    if not os.path.exists(STAGE4_JSON):
        return False
    with open(STAGE4_JSON, "r", encoding="utf-8") as f:
        d4 = json.load(f)
    p = d4.get("pages", {}).get(slug_html)
    return p is not None and "sections" in p


# ── --report モード ──────────────────────────────────────────────────────────


def cmd_report(slugs: List[str], use_head: bool) -> None:
    """各 slug の drift を一覧（読み取り専用）。"""
    raw, data = _load_content_json()
    # round-trip 証明（常時）
    _assert_roundtrip(raw, data)

    pages = data.get("pages", {})
    if not slugs:
        # 全 slug
        slugs = [k[:-5] for k in pages.keys() if k.endswith(".html")]

    drift_count = 0
    missing_count = 0
    mismatch_count = 0
    avedon_count = 0

    for slug in slugs:
        slug_html = slug if slug.endswith(".html") else slug + ".html"
        slug_base = slug_html[:-5]

        page = pages.get(slug_html)
        if page is None:
            print(f"[SKIP]  {slug_base}: content.json にエントリなし")
            missing_count += 1
            continue

        json_sections = page.get("sections") or []
        sources_html = page.get("sources_html") or ""

        html = _get_html(slug_html, use_head)
        if html is None:
            src = "HEAD" if use_head else "worktree"
            print(f"[SKIP]  {slug_base}: EN HTML が {src} にない")
            missing_count += 1
            continue

        html_essays = _extract_essays_balanced(html)
        n_json = len(json_sections)
        n_html = len(html_essays)

        if n_json != n_html:
            print(
                f"[COUNT] {slug_base}: sections 数不一致 JSON={n_json} HTML={n_html}"
                f" — 手動扱い"
            )
            mismatch_count += 1
            continue

        # per-section 比較
        any_drift = False
        section_details = []
        all_nested = False

        for i, (sec, essay_html) in enumerate(zip(json_sections, html_essays)):
            json_text = _strip_tags_normalize(sec.get("body_html", ""))
            html_text = _strip_tags_normalize(essay_html)
            drift = json_text != html_text
            nested = _has_nested_div(essay_html)
            if nested:
                all_nested = True
            if drift:
                any_drift = True
                sim = _text_similarity(json_text, html_text)
                section_details.append(
                    f"sec{i+1}(drift sim={sim:.2f})"
                )

        # avedon 類型検知（全 sections の body_html を結合して検知）
        combined_body = " ".join(s.get("body_html", "") for s in json_sections)
        av_flags = _detect_avedon_flags(combined_body, sources_html)
        has_avedon = (
            bool(av_flags["template_phrases"])
            or bool(av_flags["orphan_cites"])
            or bool(av_flags["duplicate_cites"])
        )

        # 出力
        drift_tag = "DRIFT" if any_drift else "OK   "
        nested_tag = " nested-div" if all_nested else ""
        avedon_tag = " AVEDON" if has_avedon else ""
        hand_tag = " HAND" if slug_html in HAND_MAINTAINED_EN else ""
        stage4_tag = " STAGE4" if _stage4_has_sections(slug_html) else ""

        detail_str = ""
        if section_details:
            detail_str = " [" + ", ".join(section_details) + "]"

        print(
            f"[{drift_tag}] {slug_base}"
            f" secs={n_json}{nested_tag}{avedon_tag}{hand_tag}{stage4_tag}"
            f"{detail_str}"
        )

        if any_drift:
            drift_count += 1
            if has_avedon:
                avedon_count += 1

        if has_avedon and not any_drift:
            avedon_count += 1

    print()
    print(
        f"=== report 完了: drift={drift_count}, sections不一致={mismatch_count}, "
        f"skipped={missing_count}, avedon類型={avedon_count} ==="
    )


# ── --apply モード ───────────────────────────────────────────────────────────


def cmd_apply(slugs: List[str], use_head: bool) -> None:
    """HTML から essay を抽出して content.json の sections[i].body_html を更新。

    1. HAND_MAINTAINED_EN / stage4 sections 持ちは拒否
    2. balanced 抽出 → 件数 = sections 数 assert
    3. churn-safe 書込（atomic write）
    4. 対象外差分ゼロ assert
    5. ビルド検証（subprocess build_photographers_en.py --slug X）
    6. ビルド結果 essay 素テキスト = HEAD essay 素テキストを確認
    7. 失敗ならロールバック
    """
    if not slugs:
        print("ERROR: --apply は --slug 必須（全自動適用はしない）", file=sys.stderr)
        sys.exit(1)

    raw, data = _load_content_json()
    _assert_roundtrip(raw, data)

    pages = data.get("pages", {})
    applied = []
    skipped = []

    for slug in slugs:
        slug_html = slug if slug.endswith(".html") else slug + ".html"
        slug_base = slug_html[:-5]

        # --- guard: HAND_MAINTAINED_EN ---
        if slug_html in HAND_MAINTAINED_EN:
            print(
                f"[SKIP]  {slug_base}: HAND_MAINTAINED_EN — 手書き維持ページのため拒否"
            )
            skipped.append(slug_base)
            continue

        # --- guard: stage4 sections 持ち ---
        if _stage4_has_sections(slug_html):
            print(
                f"[SKIP]  {slug_base}: stage4.json に sections エントリあり"
                f" — content.json への書込が stage4 に上書きされる可能性。手動扱い"
            )
            skipped.append(slug_base)
            continue

        # --- content.json にエントリあるか ---
        page = pages.get(slug_html)
        if page is None:
            print(f"[SKIP]  {slug_base}: content.json にエントリなし")
            skipped.append(slug_base)
            continue

        json_sections = page.get("sections") or []
        n_json = len(json_sections)

        # --- HTML 取得 ---
        html = _get_html(slug_html, use_head)
        if html is None:
            src = "HEAD" if use_head else "worktree"
            print(f"[SKIP]  {slug_base}: EN HTML が {src} にない")
            skipped.append(slug_base)
            continue

        # --- HEAD の essay 素テキスト（ビルド後照合用に事前取得）---
        head_essays = _extract_essays_balanced(html)
        n_html = len(head_essays)

        # --- 件数 assert ---
        if n_json != n_html:
            print(
                f"[FAIL]  {slug_base}: sections 数不一致 JSON={n_json} HTML={n_html}"
                f" — apply 中断（手動扱い）"
            )
            skipped.append(slug_base)
            continue

        # --- drift あるか確認（なければスキップしてよい）---
        any_drift = False
        for sec, essay_html in zip(json_sections, head_essays):
            if _strip_tags_normalize(sec.get("body_html", "")) != _strip_tags_normalize(essay_html):
                any_drift = True
                break

        if not any_drift:
            print(f"[OK]    {slug_base}: drift なし — 同期不要")
            continue

        # --- 各 section に essay_html を適用 ---
        for i, (sec, essay_html) in enumerate(zip(json_sections, head_essays)):
            sec["body_html"] = essay_html

        print(f"[APPLY] {slug_base}: {n_json} sections を JSON に適用中...")

        # --- atomic write ---
        new_raw = _dump_content_json(data)
        old_backup = raw  # ロールバック用

        # 対象外差分ゼロ assert（write 前）
        try:
            _assert_only_sections_changed(raw, new_raw, {slug_html})
        except AssertionError as e:
            print(f"[FAIL]  {slug_base}: 対象外差分検出 — 中断: {e}", file=sys.stderr)
            skipped.append(slug_base)
            continue

        _atomic_write(CONTENT_JSON, new_raw)
        # raw を新しいもので更新（次の slug の比較基準に）
        raw = new_raw

        # --- ビルド検証 ---
        print(f"[BUILD] {slug_base}: build_photographers_en.py を実行中...")
        build_result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "build_photographers_en.py"),
             "--slug", slug_base],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        if build_result.returncode != 0:
            print(
                f"[FAIL]  {slug_base}: ビルド失敗 — content.json をロールバック",
                file=sys.stderr,
            )
            print(build_result.stderr[:500], file=sys.stderr)
            _atomic_write(CONTENT_JSON, old_backup)
            raw = old_backup
            skipped.append(slug_base)
            continue

        # --- ビルド結果の essay 素テキストを HEAD と照合 ---
        built_html = _get_html(slug_html, use_head=False)
        if built_html is None:
            print(
                f"[FAIL]  {slug_base}: ビルド後 HTML が見つからない — ロールバック",
                file=sys.stderr,
            )
            _atomic_write(CONTENT_JSON, old_backup)
            raw = old_backup
            skipped.append(slug_base)
            continue

        built_essays = _extract_essays_balanced(built_html)
        head_texts = [_strip_tags_normalize(e) for e in head_essays]
        built_texts = [_strip_tags_normalize(e) for e in built_essays]

        if len(built_texts) != len(head_texts):
            print(
                f"[FAIL]  {slug_base}: ビルド後 essay 数不一致 HEAD={len(head_texts)}"
                f" built={len(built_texts)} — ロールバック",
                file=sys.stderr,
            )
            _atomic_write(CONTENT_JSON, old_backup)
            raw = old_backup
            skipped.append(slug_base)
            continue

        regressions = []
        for i, (ht, bt) in enumerate(zip(head_texts, built_texts)):
            if ht != bt:
                regressions.append(i + 1)

        if regressions:
            print(
                f"[FAIL]  {slug_base}: ビルド後 essay 本文が HEAD と不一致"
                f" sections={regressions} — ロールバック",
                file=sys.stderr,
            )
            _atomic_write(CONTENT_JSON, old_backup)
            raw = old_backup
            skipped.append(slug_base)
            continue

        print(f"[DONE]  {slug_base}: 同期 + ビルド検証 OK（essay 本文回帰なし）")
        applied.append(slug_base)

    print()
    print(f"=== apply 完了: applied={len(applied)}, skipped={len(skipped)} ===")
    if applied:
        print("  applied:", ", ".join(applied))
    if skipped:
        print("  skipped:", ", ".join(skipped))


# ── CLI ─────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="EN 写真家ページ essay 本文のドリフトを一覧・同期するツール。"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="drift を一覧（読み取り専用。JSON も HTML も書き換えない）",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="HTML から essay を抽出して content.json の body_html を更新（--slug 必須）",
    )
    parser.add_argument(
        "--slug",
        action="append",
        dest="slugs",
        metavar="SLUG",
        help="対象 slug（複数可。--report は省略で全 slug）",
    )
    parser.add_argument(
        "--head",
        action="store_true",
        help="作業ツリーでなく git show HEAD:... から HTML を取得",
    )
    args = parser.parse_args()

    if not args.report and not args.apply:
        parser.print_help()
        sys.exit(0)

    if args.apply and not args.slugs:
        print("ERROR: --apply は --slug が必須（全自動適用はしない）", file=sys.stderr)
        sys.exit(1)

    if args.report and args.apply:
        print("ERROR: --report と --apply は同時に指定できません", file=sys.stderr)
        sys.exit(1)

    slugs = args.slugs or []

    if args.report:
        cmd_report(slugs, use_head=args.head)
    elif args.apply:
        cmd_apply(slugs, use_head=args.head)


if __name__ == "__main__":
    main()
