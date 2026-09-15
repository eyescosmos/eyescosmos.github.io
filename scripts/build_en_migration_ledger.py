#!/usr/bin/env python3
"""Build the regenerable EN HTML-canon migration ledger.

This is a read-only inventory tool except for ``--apply``, which writes only
``data/en-migration-ledger.json``.  The ledger contains file hashes, so
``--check`` is intentionally NOT wired into ``preflight.py``: it is a session
start check for phases D/E/F, not a push gate that must be refreshed after
every photographer-page edit.

Usage:
    python3 scripts/build_en_migration_ledger.py
    python3 scripts/build_en_migration_ledger.py --apply
    python3 scripts/build_en_migration_ledger.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

from import_chatgpt_photographer import extract_bundle
from preflight import PH_KW_RE, PH_SIDE_RE, _chip_map
import sync_en_rel_annotations as sra

# 2026-09-15 §12.2 で check_en_entry.py から移設。**ガードではなく履歴記録**。
# フェーズDで EN 実ページは全件 HTML 自身が正本になり、フェーズ2で builder の再生成経路も
# 消えたので「手書き維持」に強制力は無い。台帳の hand_maintained_history flag を
# 再生成可能に保つためだけに残している。新規に足さないこと。
HAND_MAINTAINED_HISTORY = {
    'stieglitz.html', 'annie-leibovitz.html', 'shoji-ueda.html',
    'toyoko-tokiwa.html', 'lee-miller.html',
}


ROOT = Path(__file__).resolve().parent.parent
EN_DIR = ROOT / "en" / "photographers"
JA_DIR = ROOT / "photographers"
BASE_JSON = ROOT / "data" / "archive" / "photographers-en-content.json"
STAGE4_JSON = ROOT / "data" / "archive" / "photographers-en-stage4.json"
LEDGER_JSON = ROOT / "data" / "en-migration-ledger.json"

CLASSES = {"real_page", "shim", "unpublished_data", "exception"}


class PageStructureParser(HTMLParser):
    """Collect structural facts without duplicating the content extractor."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.h1 = 0
        self.h3 = 0
        self.has_ph_section = False
        self.refresh_content: str | None = None
        self.has_old_ref = False
        self.has_new_ref = False
        self.en_hreflang: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attr = {key.lower(): value for key, value in attrs}
        classes = set((attr.get("class") or "").split())

        if tag == "h1":
            self.h1 += 1
        elif tag == "h3":
            self.h3 += 1

        if "ph-section" in classes:
            self.has_ph_section = True
        if "book" in classes:
            self.has_old_ref = True
        if "ph-book" in classes or "ph-further-links" in classes:
            self.has_new_ref = True

        if tag == "meta" and (attr.get("http-equiv") or "").lower() == "refresh":
            self.refresh_content = attr.get("content")
        if tag == "link" and (attr.get("hreflang") or "").lower() == "en":
            self.en_hreflang = attr.get("href")


def parse_structure(raw: str) -> PageStructureParser:
    parser = PageStructureParser()
    parser.feed(raw)
    parser.close()
    return parser


def target_filename(href: str | None) -> str | None:
    if not href:
        return None
    path = unquote(urlparse(href.strip()).path)
    name = Path(path).name
    return name if name.endswith(".html") else None


def shim_target(refresh_content: str | None) -> str | None:
    if not refresh_content:
        return None
    _delay, separator, destination = refresh_content.partition(";")
    if not separator:
        return None
    destination = destination.strip()
    if destination.lower().startswith("url="):
        destination = destination[4:].strip().strip("'\"")
    return target_filename(destination)


def load_pages(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    pages = data.get("pages")
    if not isinstance(pages, dict):
        raise ValueError(f"{path.relative_to(ROOT)}: pages must be an object")
    return pages


def short_head() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def ja_target_map(ja_paths: list[Path]) -> dict[str, str]:
    """Map each JA leaf's hreflang EN target back to the JA filename."""
    result: dict[str, str] = {}
    for path in ja_paths:
        raw = path.read_text(encoding="utf-8")
        target = target_filename(parse_structure(raw).en_hreflang)
        if target is None:
            continue
        previous = result.get(target)
        if previous is not None and previous != path.name:
            raise ValueError(
                f"duplicate JA hreflang target {target}: {previous}, {path.name}"
            )
        result[target] = path.name
    return result


def metric_shell(path: Path, structure: PageStructureParser) -> dict:
    payload = path.read_bytes()
    raw = payload.decode("utf-8")
    kw = _chip_map(raw, PH_KW_RE)
    side = _chip_map(raw, PH_SIDE_RE)
    if structure.has_old_ref:
        ref_format = "old"
    elif structure.has_new_ref:
        ref_format = "new"
    else:
        ref_format = "none"
    return {
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "h3": structure.h3,
        "kw_chips": len(kw),
        "kw_chips_linked": sum(href is not None for href in kw.values()),
        "side_chips": len(side),
        "side_chips_linked": sum(href is not None for href in side.values()),
        "ref_format": ref_format,
    }


def extract_metrics(
    path: Path, lang: str, slug: str, structure: PageStructureParser
) -> tuple[dict, set[int], bool]:
    """Return serialized metrics, cite-id set, and extraction-failure state."""
    metrics = metric_shell(path, structure)
    raw = path.read_text(encoding="utf-8")
    try:
        bundle, _info = extract_bundle(raw, lang, slug=slug)
    except Exception as exc:  # noqa: BLE001 - ledger must preserve the exact failure
        metrics.update(
            {
                "sections": None,
                "cites": None,
                "suprefs": None,
                "works": None,
                "rel_people": None,
                "rel_movements": None,
                "ref_books": None,
                "ref_links": None,
                "has_thesis": None,
                "has_abstract": None,
                "extract_error": f"{type(exc).__name__}: {exc}",
            }
        )
        return metrics, set(), True

    cite_ids = set(bundle["cite_ids"])
    metrics.update(
        {
            "sections": len(bundle["sections"]),
            "cites": len(cite_ids),
            "suprefs": len(bundle["supref_ids"]),
            "works": len(bundle["works"]),
            "rel_people": len(bundle["related_people"]),
            "rel_movements": len(bundle["related_movements"]),
            "ref_books": len(bundle["further_books"]),
            "ref_links": len(bundle["further_links"]),
            "has_thesis": bool(bundle["thesis_inner_html"]),
            "has_abstract": bool(bundle["lead_inner_html"]),
        }
    )
    ordered = {
        key: metrics[key]
        for key in (
            "sha256",
            "bytes",
            "sections",
            "h3",
            "cites",
            "suprefs",
            "works",
            "rel_people",
            "rel_movements",
            "ref_books",
            "ref_links",
            "has_thesis",
            "has_abstract",
            "kw_chips",
            "kw_chips_linked",
            "side_chips",
            "side_chips_linked",
            "ref_format",
        )
    }
    return ordered, cite_ids, False


def json_facts(key: str, base: dict[str, dict], stage4: dict[str, dict]) -> dict:
    in_base = key in base
    in_stage4 = key in stage4
    if in_base and in_stage4:
        source = "base+stage4"
    elif in_base:
        source = "base"
    elif in_stage4:
        source = "stage4"
    else:
        source = "none"
    effective = stage4.get(key) if in_stage4 else base.get(key, {})
    return {
        "in_base": in_base,
        "in_stage4": in_stage4,
        "canon_source": source,
        "has_view_works_links_html": bool(effective.get("view_works_links_html")),
        "has_notable_works_html": bool(effective.get("notable_works_html")),
    }


def classify(en_path: Path | None, structure: PageStructureParser | None) -> tuple[str, str | None]:
    if en_path is None:
        return "unpublished_data", None
    assert structure is not None
    if structure.refresh_content is not None:
        return "shim", None
    if structure.h1 == 1 and structure.has_ph_section:
        return "real_page", None
    reasons = []
    if structure.h1 != 1:
        reasons.append(f"h1_count={structure.h1}")
    if not structure.has_ph_section:
        reasons.append("ph-section_missing")
    return "exception", "exception:" + ",".join(reasons)


def build_ledger() -> dict:
    base = load_pages(BASE_JSON)
    stage4 = load_pages(STAGE4_JSON)
    en_paths = sorted(EN_DIR.glob("*.html"), key=lambda path: path.name)
    ja_paths = sorted(JA_DIR.glob("*.html"), key=lambda path: path.name)
    en_by_name = {path.name: path for path in en_paths}
    ja_by_name = {path.name: path for path in ja_paths}
    en_to_ja = ja_target_map(ja_paths)
    keys = sorted(set(en_by_name) | set(base) | set(stage4))

    structures: dict[str, PageStructureParser] = {}
    classes: dict[str, str] = {}
    class_reasons: dict[str, str | None] = {}
    for key, path in en_by_name.items():
        structure = parse_structure(path.read_text(encoding="utf-8"))
        structures[key] = structure
        classes[key], class_reasons[key] = classify(path, structure)
    for key in keys:
        if key not in classes:
            classes[key], class_reasons[key] = classify(None, None)

    records = []
    for key in keys:
        slug = Path(key).stem
        record_class = classes[key]
        en_path = en_by_name.get(key)
        json_info = json_facts(key, base, stage4)
        flags: list[str] = []
        if class_reasons[key]:
            flags.append(class_reasons[key])

        if key in ja_by_name:
            ja_name = key
        else:
            candidate = en_to_ja.get(key)
            ja_name = candidate if candidate in ja_by_name else None
        ja_path = ja_by_name.get(ja_name) if ja_name else None

        en_metrics = None
        en_cites: set[int] = set()
        en_failed = False
        if en_path is not None and record_class != "shim":
            en_metrics, en_cites, en_failed = extract_metrics(
                en_path, "en", slug, structures[key]
            )

        ja_metrics = None
        ja_cites: set[int] = set()
        ja_failed = False
        if ja_path is not None:
            ja_structure = parse_structure(ja_path.read_text(encoding="utf-8"))
            ja_metrics, ja_cites, ja_failed = extract_metrics(
                ja_path, "ja", slug, ja_structure
            )

        if key in HAND_MAINTAINED_HISTORY:
            flags.append("hand_maintained_history")
        if json_info["in_stage4"] and not json_info["in_base"]:
            flags.append("stage4_only_canon")
        if record_class == "real_page" and json_info["canon_source"] == "none":
            flags.append("no_json_entry")
        if json_info["has_view_works_links_html"]:
            flags.append("dead_view_works_links")
        if en_metrics is not None and en_metrics["ref_format"] == "old":
            flags.append("old_ref_format")
        if ja_name is not None and ja_name.startswith("jp-"):
            flags.append("jp_kanji_pair")
            if ja_name not in en_by_name:
                flags.append("jp_shim_missing")
        if record_class == "real_page" and ja_path is None:
            flags.append("ja_missing")
        if en_metrics is not None and ja_metrics is not None and not (en_failed or ja_failed):
            if en_metrics["sections"] != ja_metrics["sections"]:
                flags.append("section_count_asymmetry")
            if en_metrics["h3"] != ja_metrics["h3"]:
                flags.append("h3_count_asymmetry")
            if en_cites != ja_cites:
                flags.append("cite_set_asymmetry")
        if en_failed or ja_failed:
            flags.append("extract_failed")

        record = {
            "key": key,
            "slug": slug,
            "class": record_class,
            "en": en_metrics,
            "ja_file": ja_name,
            "ja": ja_metrics,
            "json": json_info,
            "shim_target": (
                shim_target(structures[key].refresh_content)
                if record_class == "shim"
                else None
            ),
            "flags": sorted(set(flags)),
        }
        records.append(record)

    class_counts = {name: sum(r["class"] == name for r in records) for name in CLASSES}
    unclassified = sum(r["class"] not in CLASSES for r in records)
    real_records = [r for r in records if r["class"] == "real_page"]
    en_rel_blurb_missing_pages: list[str] = []
    en_rel_blurb_missing_count = 0
    for record in real_records:
        en_html = (EN_DIR / record["key"]).read_text(encoding="utf-8")
        missing = [
            row for row in sra.page_alignment(record["slug"], en_html)
            if row[0] == "need"
        ]
        if missing:
            en_rel_blurb_missing_pages.append(record["slug"])
            en_rel_blurb_missing_count += len(missing)
    findings = {
        "en_files": len(en_paths),
        "en_real_pages": class_counts["real_page"],
        "en_shims": class_counts["shim"],
        "ja_files": len(ja_paths),
        "ja_kanji_files": sum(path.name.startswith("jp-") for path in ja_paths),
        "base_entries": len(base),
        "base_entries_for_shims": sum(
            key in en_by_name and classes[key] == "shim" for key in base
        ),
        "base_entries_for_real_pages": sum(
            key in en_by_name and classes[key] == "real_page" for key in base
        ),
        "base_entries_without_file": sum(key not in en_by_name for key in base),
        "stage4_entries": len(stage4),
        "stage4_only_canon": sorted(key for key in stage4 if key not in base),
        "real_pages_without_json": [
            r["key"] for r in real_records if r["json"]["canon_source"] == "none"
        ],
        "hand_maintained": sorted(
            r["key"] for r in records if "hand_maintained_history" in r["flags"]
        ),
        "dead_view_works_links": sum(
            bool(entry.get("view_works_links_html")) for entry in base.values()
        ),
        "notable_works_html": sum(
            bool(entry.get("notable_works_html")) for entry in base.values()
        ),
        "old_ref_format": [
            r["key"] for r in real_records if "old_ref_format" in r["flags"]
        ],
        "jp_shim_missing": [
            r["key"] for r in real_records if "jp_shim_missing" in r["flags"]
        ],
        "asymmetry": {
            "section_count": sum(
                "section_count_asymmetry" in r["flags"] for r in real_records
            ),
            "h3_count": sum("h3_count_asymmetry" in r["flags"] for r in real_records),
            "cite_set": sum("cite_set_asymmetry" in r["flags"] for r in real_records),
        },
        "en_rel_blurb_missing": {
            "count": en_rel_blurb_missing_count,
            "pages": sorted(en_rel_blurb_missing_pages),
            "note": "EN HTML の §REL に一言解説が無いリンク。フェーズFで HTML ベース監査に切り替えて可視化した既存バックログで、移行が作った退行ではない。★内訳の大半は jp-漢字ペアのローマ字実ページ（iwata-nakayama / ihei-kimura 等 15枚）。旧 JSON 監査はこれらを一度も見ておらず、代わりに §REL を持たない jp-漢字 shim を検査して無意味な count mismatch を出していた＝構造的な検査漏れだった。該当ページを次に update するとき一緒に直す",
        },
    }
    counts = {
        "records": len(records),
        "real_page": class_counts["real_page"],
        "shim": class_counts["shim"],
        "unpublished_data": class_counts["unpublished_data"],
        "exception": class_counts["exception"],
        "unclassified": unclassified,
    }
    return {
        "_meta": {
            "schema_version": 1,
            "generated_by": "scripts/build_en_migration_ledger.py",
            "generated_at_commit": short_head(),
            "canon": {
                "policy": "html",
                "declared_at": "2026-09-14 phase D",
                "statement": "en/photographers/*.html の real_page 全件が HTML 自身の正本。再生成しない。",
                "hand_maintained_is_history": True,
                "hand_maintained_registry": "scripts/build_en_migration_ledger.py の HAND_MAINTAINED_HISTORY（2026-09-15 §12.2 で check_en_entry.py から移設。ガードではなく履歴記録。rollback は git）",
                # 撤去前に check_en_entry.py のコメントが持っていたページ別の理由。
                # §5「履歴は台帳にだけ残す」の実体。コードから消えてもここに残す。
                "hand_maintained_history_notes": {
                    "shoji-ueda.html": "現 EN HTML が JA ページに対応した正（本文の脚注 *1..*17 と出典が整合）。JSON 側の sources_html / リンクは本文と番号が対応しない別系統の誤りで、JSON からの再生成は正しい HTML を壊した。",
                    "toyoko-tokiwa.html": "EN HTML は手作りで EN 正本 JSON に未登録。ビルダーは JSON に無いため SKIP していた＝もともと再生成対象外。台帳では no_json_entry flag。",
                    "lee-miller.html": "手書き §REL 解説と3節本文が JSON に無く、再生成すると劣化した（feedback_lee_miller_no_blind_rebuild）。",
                    "stieglitz.html": "旧フォーマットの §REF（class=\"book\"）と手編集の本文を持ち、再生成で失われた。台帳では old_ref_format flag。",
                    "annie-leibovitz.html": "EN に ph-thesis ブロックが無く、手編集で維持されていた個体。",
                },
                "new_page_path": "python3 scripts/import_chatgpt_photographer.py --slug <slug> --ja JA.html --en EN.html --apply（フェーズE-2）",
                "json_status": "読み取り専用アーカイブ。総ざらいフェーズ3（2026-09-15）で data/archive/ へ物理移動済み。build_photographers_en.py は module-only 化され JSON を読まない（フェーズ2）。preflight の check_en_json_frozen() が変更を HARD で止める",
            },
            "counts": counts,
            "findings": findings,
        },
        "records": records,
    }


def render(ledger: dict) -> bytes:
    return (json.dumps(ledger, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def emit_summary(ledger: dict) -> None:
    meta = ledger["_meta"]
    print(json.dumps(meta, ensure_ascii=False, indent=2), file=sys.stderr)


def comparison_ledger(ledger: dict) -> dict:
    """Return a comparison copy without scan-time-only metadata."""
    comparable = json.loads(json.dumps(ledger, ensure_ascii=False))
    comparable.get("_meta", {}).pop("generated_at_commit", None)
    return comparable


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="write the ledger JSON")
    mode.add_argument("--check", action="store_true", help="compare the ledger with a fresh scan")
    args = parser.parse_args()

    try:
        ledger = build_ledger()
    except Exception as exc:  # noqa: BLE001 - scan failures must be fail-loud
        print(f"ERROR: ledger scan failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    payload = render(ledger)
    emit_summary(ledger)
    status = 0
    if args.apply:
        LEDGER_JSON.write_bytes(payload)
        print(f"wrote {LEDGER_JSON.relative_to(ROOT)} ({len(payload)} bytes)", file=sys.stderr)
    elif args.check:
        if not LEDGER_JSON.exists():
            print(f"OUT OF DATE: {LEDGER_JSON.relative_to(ROOT)} does not exist", file=sys.stderr)
            status = 1
        else:
            try:
                current = json.loads(LEDGER_JSON.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                print(f"OUT OF DATE: {LEDGER_JSON.relative_to(ROOT)} cannot be read: {exc}",
                      file=sys.stderr)
                status = 1
            else:
                old_commit = current.get("_meta", {}).get("generated_at_commit")
                new_commit = ledger.get("_meta", {}).get("generated_at_commit")
                if old_commit != new_commit:
                    print(
                        f"NOTE: generated_at_commit {old_commit} → {new_commit}"
                        "（スキャン時点の記録。母集団の差ではない）",
                        file=sys.stderr,
                    )
                if comparison_ledger(current) != comparison_ledger(ledger):
                    print(
                        f"OUT OF DATE: {LEDGER_JSON.relative_to(ROOT)} differs from the fresh scan",
                        file=sys.stderr,
                    )
                    status = 1
                else:
                    print(f"OK: {LEDGER_JSON.relative_to(ROOT)} matches the fresh scan",
                          file=sys.stderr)

    counts = ledger["_meta"]["counts"]
    if counts["exception"] or counts["unclassified"]:
        print(
            "ERROR: exception/unclassified records require human classification",
            file=sys.stderr,
        )
        return 2
    return status


if __name__ == "__main__":
    raise SystemExit(main())
