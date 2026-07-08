#!/usr/bin/env python3
"""build_photographers_en.py の translate_residuals（§ _translate_node）検証。

混在コンテンツ（"<a>A</a> / <a>B</a>" や "ケニア / <a>アメリカ</a>"）のチップで
国名/用語が翻訳されずに残るバグの修正を確認する。実データでの実例:
- eve-sussman.html: <a>イギリス</a> / <a>アメリカ</a>（アンカー2個）
- wangechi-mutu.html / the-atlas-group-walid-raad.html: ケニア(レバノン) / <a>アメリカ</a>
  （アンカー外テキスト + アンカー混在）

translate_residuals は ph-side-chip / ph-kw / ph-side-meta-val の中身に対して
_translate_node 相当の処理を適用する。ここでは実際の repl_kw 経路を通す最小の
HTML 断片を translate_residuals に直接渡して検証する（hermetic・外部依存なし）。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_photographers_en import translate_residuals  # noqa: E402

FAILURES = []


def check(name, html_in, must_contain, must_not_contain=()):
    warnings = []
    out = translate_residuals(html_in, {}, 'test-slug', 'test-slug.html', warnings)
    ok = True
    for s in must_contain:
        if s not in out:
            ok = False
            print(f'FAIL [{name}]: expected to find {s!r}')
            print(f'  --- output ---\n{out}')
    for s in must_not_contain:
        if s in out:
            ok = False
            print(f'FAIL [{name}]: unexpected residual {s!r}')
            print(f'  --- output ---\n{out}')
    if ok:
        print(f'PASS [{name}]')
    else:
        FAILURES.append(name)


# Case 1: two anchors, no bare text between ("<a>A</a> / <a>B</a>")
check(
    'two-anchor country chip (eve-sussman pattern)',
    '<span class="ph-side-chip"><a href="/countries/united-kingdom.html">'
    'イギリス</a> / <a href="/countries/united-states.html">アメリカ</a></span>',
    must_contain=['>United Kingdom<', '>United States<'],
    must_not_contain=['イギリス', 'アメリカ'],
)

# Case 2: bare text + anchor ("ケニア / <a>アメリカ</a>")
check(
    'bare + anchor country chip (wangechi-mutu pattern)',
    '<span class="ph-side-chip">ケニア / '
    '<a href="/countries/united-states.html">アメリカ</a></span>',
    must_contain=['Kenya / ', '>United States<'],
    must_not_contain=['ケニア', '>アメリカ<'],
)

# Case 2b: bare text + anchor, Lebanon variant (the-atlas-group-walid-raad pattern)
check(
    'bare + anchor country chip (atlas-group pattern)',
    '<span class="ph-side-chip">レバノン / '
    '<a href="/countries/united-states.html">アメリカ</a></span>',
    must_contain=['Lebanon / ', '>United States<'],
    must_not_contain=['レバノン', '>アメリカ<'],
)

# Case 3: single anchor, already-CJK movement label — no regression.
# (In the real pipeline movement labels are pre-translated by
# translate_keyword_movements before translate_residuals runs, but
# コンセプチュアルアート is not itself a country/term-dict entry, so we use a
# country name here to exercise the single-anchor branch of _translate_node
# without depending on the movement dict.)
check(
    'single anchor country chip (no regression)',
    '<span class="ph-kw"><a href="/countries/switzerland.html">'
    'スイス</a></span>',
    must_contain=['>Switzerland<'],
    must_not_contain=['スイス'],
)

if FAILURES:
    print(f'\n{len(FAILURES)} test(s) failed: {FAILURES}')
    sys.exit(1)
print('\nAll tests passed.')
