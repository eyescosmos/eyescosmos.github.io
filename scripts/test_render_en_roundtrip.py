#!/usr/bin/env python3
"""Phase C: EN HTML extract → render → extract の厳密 round-trip 検証。"""
from __future__ import annotations

import copy
import html as html_lib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from import_chatgpt_photographer import (  # noqa: E402
    EnRenderIncomplete,
    extract_bundle,
    render_en_page,
)


ROUNDTRIP_SLUGS = (
    "ansel-adams",
    "ed-ruscha",
    "robertfrank",
    "talbot",
    "annie-leibovitz",
    "daisuke-yokota",
    "nicephore-niepce",
    "iwata-nakayama",
)

# JA 側に旧形式は0枚なので新規ページ経路には現れない。ここは fail-loud の
# 固定であって、旧形式への対応予定ではない。
EXPECTED_FAIL = (
    "stieglitz",
    "hiroshi-sugimoto",
)

# 設計で許可された正規化はこの3種だけ。人間の裁定なしに増やさない。
KNOWN_NORMALIZATIONS = (
    "N1 h3-id: <h3> の id 属性（値は問わない）",
    "N2 works-dedup",
    "N3 dash",
)


def _strip_h3_ids(fragment: str) -> str:
    def strip(match: re.Match) -> str:
        tag = re.sub(
            r'''\s+id\s*=\s*(["']).*?\1''', "", match.group(0), flags=re.I)
        return tag

    return re.sub(r'<h3\b[^>]*>', strip, fragment, flags=re.I)


def _normalize_n1(before: dict, after: dict) -> int:
    count = 0
    before_sections = before.get("sections") or []
    after_sections = after.get("sections") or []
    for left, right in zip(before_sections, after_sections):
        raw_left = left.get("blocks_html") or ""
        raw_right = right.get("blocks_html") or ""
        clean_left = _strip_h3_ids(raw_left)
        clean_right = _strip_h3_ids(raw_right)
        if raw_left != raw_right and clean_left == clean_right:
            left_tags = re.findall(r'<h3\b[^>]*>', raw_left, re.I)
            right_tags = re.findall(r'<h3\b[^>]*>', raw_right, re.I)
            count += sum(a != b for a, b in zip(left_tags, right_tags))
        left["blocks_html"] = clean_left
        right["blocks_html"] = clean_right
    return count


def _normalize_n2(before: dict) -> int:
    works = before.get("works") or []
    unique = []
    seen = set()
    for work in works:
        url = html_lib.unescape(work.get("url") or "")
        if url in seen:
            continue
        seen.add(url)
        unique.append(work)
    before["works"] = unique
    return len(works) - len(unique)


def _label_map(value, path=()):
    found = {}
    if isinstance(value, dict):
        for key, item in value.items():
            here = path + (key,)
            if key == "label" and isinstance(item, str):
                found[here] = item
            else:
                found.update(_label_map(item, here))
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            found.update(_label_map(item, path + (idx,)))
    return found


def _dash_canonical(value: str) -> str:
    return value.replace(" - ", " — ")


def _normalize_dash_labels(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "label" and isinstance(item, str):
                value[key] = _dash_canonical(item)
            else:
                _normalize_dash_labels(item)
    elif isinstance(value, list):
        for item in value:
            _normalize_dash_labels(item)


def _normalize_n3(before: dict, after: dict) -> int:
    left = _label_map(before)
    right = _label_map(after)
    count = sum(
        1 for path in left.keys() & right.keys()
        if left[path] != right[path]
        and _dash_canonical(left[path]) == _dash_canonical(right[path]))
    _normalize_dash_labels(before)
    _normalize_dash_labels(after)
    return count


def _diff(left, right, path="bundle") -> list[str]:
    if type(left) is not type(right):
        return [f"{path}: type {type(left).__name__} != {type(right).__name__}"]
    if isinstance(left, dict):
        out = []
        for key in sorted(left.keys() | right.keys()):
            if key not in left:
                out.append(f"{path}.{key}: output-only")
            elif key not in right:
                out.append(f"{path}.{key}: missing from output")
            else:
                out.extend(_diff(left[key], right[key], f"{path}.{key}"))
        return out
    if isinstance(left, list):
        out = []
        if len(left) != len(right):
            out.append(f"{path}: length {len(left)} != {len(right)}")
        for idx, (a, b) in enumerate(zip(left, right)):
            out.extend(_diff(a, b, f"{path}[{idx}]"))
        return out
    return [] if left == right else [f"{path}: {left!r} != {right!r}"]


def check_slug(slug: str) -> tuple[bool, dict[str, int], list[str]]:
    source = ROOT / "en" / "photographers" / f"{slug}.html"
    raw = source.read_text(encoding="utf-8")
    before, _info = extract_bundle(raw, "en", slug=slug)
    rendered, warnings = render_en_page(before, slug)
    if any("head fallback fired" in warning for warning in warnings):
        return False, {}, ["head fallback fired"]
    after, _info = extract_bundle(rendered, "en", slug=slug)

    left = copy.deepcopy(before)
    right = copy.deepcopy(after)
    notes = {
        KNOWN_NORMALIZATIONS[0]: _normalize_n1(left, right),
        KNOWN_NORMALIZATIONS[1]: _normalize_n2(left),
    }
    notes[KNOWN_NORMALIZATIONS[2]] = _normalize_n3(left, right)
    differences = _diff(left, right)
    return not differences, notes, differences


def check_expected_fail(slug: str) -> tuple[bool, str]:
    source = ROOT / "en" / "photographers" / f"{slug}.html"
    raw = source.read_text(encoding="utf-8")
    bundle, _info = extract_bundle(raw, "en", slug=slug)
    try:
        render_en_page(bundle, slug)
    except EnRenderIncomplete as exc:
        message = str(exc)
        return "§ REF" in message, message
    except Exception as exc:
        return False, f"想定外の例外 {type(exc).__name__}: {exc}"
    return False, "EnRenderIncomplete が出ず描画に成功した"


def main() -> int:
    roundtrip_passed = 0
    for slug in ROUNDTRIP_SLUGS:
        try:
            ok, notes, differences = check_slug(slug)
        except Exception as exc:
            ok, notes, differences = False, {}, [f"{type(exc).__name__}: {exc}"]
        note_text = " ".join(
            f"{name}={notes.get(name, 0)}" for name in KNOWN_NORMALIZATIONS)
        print(f"{slug}: {'PASS' if ok else 'FAIL'} NOTE {note_text}")
        if ok:
            roundtrip_passed += 1
        else:
            for difference in differences[:10]:
                print(f"  {difference}", file=sys.stderr)

    expected_passed = 0
    for slug in EXPECTED_FAIL:
        ok, detail = check_expected_fail(slug)
        print(f"{slug}: {'PASS' if ok else 'FAIL'} EXPECTED_FAIL § REF")
        if ok:
            expected_passed += 1
        else:
            print(f"  {detail}", file=sys.stderr)

    print(
        f"SUMMARY: ROUNDTRIP {roundtrip_passed}/{len(ROUNDTRIP_SLUGS)} PASS; "
        f"EXPECTED_FAIL {expected_passed}/{len(EXPECTED_FAIL)} as expected")
    return 0 if (roundtrip_passed == len(ROUNDTRIP_SLUGS)
                 and expected_passed == len(EXPECTED_FAIL)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
