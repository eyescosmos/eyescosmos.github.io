#!/usr/bin/env python3
"""M4: 「器を捨てた」検証 — 構造の違う2ソースを render_ja_page に食わせ、出力 HTML が
byte 同一で、かつ常に正典の chrome/§構成/サイドバーになることを証明する。

docs/importer-scaffold-inject-spec.md §9-B / §10 Milestone 4。
合格条件B:「構造が違う2ソースを食わせ chrome/SEO/§構成/サイドバーが byte 同一・差分は
中身だけ」。固定具は細倉の元素材が持っていた汚れ（§IMAGE LINKS / Profile 型サイドバー /
content 先頭 head / 非正規の §マーカー名）。

設計上 render_ja_page は bundle の役割コンテンツ（lead/thesis/works/sections/related/
books/further/sources）と spec だけに依存し、素材の outer layout・sidebar・nav・
§マーカー名・head 属性順・title・keywords を一切読まない。本テストはそれを
ブラックボックスで確認する（hermetic＝外部コーパス非依存・リポ内 card-data と
ansel-adams scaffold のみ使用）。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from import_chatgpt_photographer import extract_bundle, render_ja_page  # noqa: E402

# ── A / B で完全一致させる役割要素（＝中身） ────────────────────────────────
HERO = (
    '<section class="ph-hero"><div class="ph-hero__info">'
    '<h1 class="ph-hero__name">試験 太郎</h1>'
    '<div class="ph-hero__en">Taro Shiken '
    '<span class="ph-hero__years">1970–</span></div>'
    '</div></section>')

CONTENT_MAIN = (
    '<div class="ph-abstract"><div class="ph-abstract__label">Abstract</div>'
    '<p>これはリードの本文。</p></div>'
    '<div class="ph-thesis"><div class="ph-thesis__label">XXX</div>'
    '<p class="ph-thesis__body">この写真家が変えたことの本文。</p></div>'
    '<div class="ph-keywords"><span class="ph-keywords__label">Keywords</span>'
    '<span class="ph-kw">語1</span><span class="ph-kw">語2</span></div>'
    '<section class="ph-section"><div class="ph-section__head">'
    '<div class="ph-section__title">'
    '<span class="ph-section__num">§ WORKS</span>'
    '<span class="ph-section__name">作品</span></div></div>'
    '<div class="ph-section__body"><div class="ph-works-links">'
    '<a class="chip-link" href="https://example.org/w" rel="noopener" '
    'target="_blank">作品アーカイブ ↗</a></div></div></section>'
    '<section class="ph-section" id="sec-01"><div class="ph-section__head">'
    '<div class="ph-section__title">'
    '<span class="ph-section__num">§ 01 / 02</span>'
    '<span class="ph-section__name">背景と時代</span></div></div>'
    '<div class="ph-section__body"><div class="essay"><p>第一節の本文'
    '<sup class="sup-ref"><a href="#cite-1">*1</a></sup>。</p></div></div></section>'
    '<section class="ph-section" id="sec-02"><div class="ph-section__head">'
    '<div class="ph-section__title">'
    '<span class="ph-section__num">§ 02 / 02</span>'
    '<span class="ph-section__name">表現の核心</span></div></div>'
    '<div class="ph-section__body"><div class="essay"><p>第二節の本文'
    '<sup class="sup-ref"><a href="#cite-2">*2</a></sup>。</p></div></div></section>')


def _rel(mark):
    return (
        '<section class="ph-section"><div class="ph-section__head">'
        '<div class="ph-section__title">'
        f'<span class="ph-section__num">{mark}</span>'
        '<span class="ph-section__name">関連</span></div></div>'
        '<div class="ph-section__body">'
        '<ul class="ph-rel-list"><li>'
        '<a href="/photographers/ansel-adams.html">アンセル・アダムス</a>'
        ' — 関連の理由。</li></ul>'
        '<ul class="ph-rel-list ph-rel-movements"><li>'
        '<a href="/movements/新即物主義.html">新即物主義</a>'
        ' — 文脈の理由。</li></ul>'
        '</div></section>')


def _ref(mark):
    return (
        '<section class="ph-section"><div class="ph-section__head">'
        '<div class="ph-section__title">'
        f'<span class="ph-section__num">{mark}</span>'
        '<span class="ph-section__name">本</span></div></div>'
        '<div class="ph-section__body">'
        '<div class="ph-book"><div class="ph-book__title">著者, <em>書名</em></div>'
        '<div class="ph-book__meta">出版, 2020</div>'
        '<div class="ph-book__note">注記。</div>'
        '<a class="ph-book-cta" href="https://example.org/b" rel="noopener" '
        'target="_blank">Publisher ↗</a></div>'
        '<ul class="ph-further-links"><li>'
        '<a href="https://example.org/f" rel="noopener" target="_blank">追加リンク</a>'
        '</li></ul></div></section>')


def _src(mark):
    return (
        '<section class="ph-section"><div class="ph-section__head">'
        '<div class="ph-section__title">'
        f'<span class="ph-section__num">{mark}</span>'
        '<span class="ph-section__name">出典</span></div></div>'
        '<div class="ph-section__body"><div class="ph-sources">'
        '<div class="ph-cite" id="cite-1"><span class="ph-cite__num">*1</span>'
        '<span><a href="https://example.org/s1" rel="noopener" '
        'target="_blank">出典1</a></span></div>'
        '<div class="ph-cite" id="cite-2"><span class="ph-cite__num">*2</span>'
        '<span><a href="https://example.org/s2" rel="noopener" '
        'target="_blank">出典2</a></span></div>'
        '</div></div></section>')


JUNK = (
    '<section class="ph-section"><div class="ph-section__head">'
    '<div class="ph-section__title">'
    '<span class="ph-section__num">§ IMAGE LINKS</span>'
    '<span class="ph-section__name">画像</span></div></div>'
    '<div class="ph-section__body"><p>無視されるべき重複works節。</p></div></section>')


def _doc(head, sidebar, *sections):
    return ('<!doctype html><html><head>' + head + '</head><body>' + HERO +
            '<main>' + ''.join(sections) + '</main><aside>' + sidebar +
            '</aside></body></html>')


# Source A: 細倉の元素材型の汚れ（content 先頭 head / Profile 型サイドバー /
# 非正規 §マーカー §RELATED・§BOOKS・§SOURCES / 重複 §IMAGE LINKS / 節順 REL→REF→JUNK→SRC）
HEAD_A = ('<meta charset="utf-8"/>'
          '<meta content="width=device-width, initial-scale=1.0" name="viewport"/>'
          '<meta content="ダーティな説明文" name="description"/>'
          '<title>ダーティ・タイトル</title>')
SIDE_A = ('<div class="ph-side-block"><div class="ph-side-block__head">Profile</div>'
          '<div>Name 試験太郎 / Born 1970 / Base 東京 / Field 写真</div></div>')
SOURCE_A = _doc(HEAD_A, SIDE_A, CONTENT_MAIN,
                _rel('§ RELATED'), _ref('§ BOOKS'), JUNK, _src('§ SOURCES'))

# Source B: 別の構造（name 先頭 head / 標準データ型サイドバー / 別の §マーカー名 /
# §IMAGE LINKS 無し / 節順 SRC→REL→REF / title・description も別物）
HEAD_B = ('<meta charset="utf-8"/>'
          '<meta name="viewport" content="width=device-width, initial-scale=1.0"/>'
          '<meta name="description" content="まったく別の説明テキスト"/>'
          '<title>クリーン・別タイトル</title>')
SIDE_B = ('<div class="ph-side-block"><div class="ph-side-block__head">写真家データ</div>'
          '<div>Country 日本 / Years 1970–</div></div>')
SOURCE_B = _doc(HEAD_B, SIDE_B, CONTENT_MAIN,
                _src('§ 出典'), _rel('§ 関連あれこれ'), _ref('§ 参考文献'))

SPEC = {
    "id": "test-taro-m4", "nameJa": "試験 太郎", "nameEn": "Taro Shiken",
    "years": "1970–", "nationality": "JP", "countryJa": "日本", "era": "1970",
    "idx": 999, "channel": "テスト · TEST", "tags": ["語1", "語2"],
    # 翻訳不能語を先頭に、翻訳可能語（STUB_TO_SLUG 在＝新即物主義）を後ろに置く。
    # Movement 表示欄は順序でなく「翻訳可能な語」を1語選ぶことを検証するため。
    "movements": ["テスト運動", "新即物主義"],
}

CONTENT_KEYS = ["lead_inner_html", "thesis_inner_html", "works", "sections",
                "related_people", "related_movements", "further_books",
                "further_links", "sources"]

# 出力に必ず在るべき正典 chrome / §構成 / サイドバー / SEO
CANONICAL_TOKENS = [
    '<span class="ph-section__num">§ WORKS</span>',
    '<span class="ph-section__num">§ 01 / 02</span>',
    '<span class="ph-section__num">§ 02 / 02</span>',
    '<span class="ph-section__num">§ REL</span>',
    '<span class="ph-section__num">§ REF</span>',
    '<span class="ph-section__num">§ SRC</span>',
    'Entry · 写真家データ', 'Navigate · 移動',
    '<meta name="description"', 'rel="canonical"', 'hreflang',
    'G-2VRTV8BZEJ', 'application/ld+json',
    'ph-cite" id="cite-1"', 'ph-cite" id="cite-2"',
    'ph-thesis__label">この写真家が変えたこと',
]

# 素材の器が出力に漏れていないこと（どちらのソース由来も）
LEAK_TOKENS = [
    '§ IMAGE LINKS', '§ SOURCES', '§ RELATED', '§ BOOKS',
    '§ 出典', '§ 関連あれこれ', '§ 参考文献',
    'ダーティ・タイトル', 'クリーン・別タイトル', 'ダーティな説明文',
    'まったく別の説明テキスト', '<meta content="width=device-width',
    'ph-side-block__head">Profile',
]


def main() -> int:
    ba, _ = extract_bundle(SOURCE_A, "ja", slug=SPEC["id"])
    bb, _ = extract_bundle(SOURCE_B, "ja", slug=SPEC["id"])

    # 1) 役割コンテンツは A/B で完全一致（器が違っても中身は同じ抽出になる）
    for k in CONTENT_KEYS:
        assert ba[k] == bb[k], f"FAIL: bundle 役割 '{k}' が A/B で不一致\nA={ba[k]!r}\nB={bb[k]!r}"

    ha = render_ja_page(ba, SPEC)
    hb = render_ja_page(bb, SPEC)

    # 2) 構造の違う2ソース → render は byte 同一（器が一切漏れていない）
    assert ha == hb, "FAIL: render(A) と render(B) が byte 不一致＝source 構造が漏れている"

    # 3) 出力は常に正典 chrome / §構成 / サイドバー / SEO
    for tok in CANONICAL_TOKENS:
        assert tok in ha, f"FAIL: 正典 chrome 欠落: {tok!r}"

    # 4) 素材の器（汚れ）が出力に一切漏れていない
    for leak in LEAK_TOKENS:
        assert leak not in ha, f"FAIL: source 構造が出力に漏れた: {leak!r}"

    # 5) Movement 表示欄は単一の翻訳可能運動（・連結 compound を作らない）。
    #    EN ビルダは単語単位でしか訳せず compound は未翻訳のまま残るため。
    #    movements=["テスト運動","新即物主義"] から順序によらず翻訳可能語を選ぶ。
    assert '<dt>Movement</dt><dd>新即物主義</dd>' in ha, \
        "FAIL: Movement 欄が単一の翻訳可能運動になっていない"
    assert '<span class="ph-side-meta-val">新即物主義</span>' in ha, \
        "FAIL: サイドバー Movement が単一の翻訳可能運動になっていない"
    assert 'テスト運動・新即物主義' not in ha and '新即物主義・テスト運動' not in ha, \
        "FAIL: Movement 欄に「・」連結 compound が残っている（EN で未翻訳になる）"

    print("M4 PASS:「器を捨てた」証明")
    print("  ・構造の違う2ソース（content先頭head / Profile型sidebar / 非正規§マーカー /")
    print("    §IMAGE LINKS / 節順違い / title・description違い）→ render 出力が byte 同一")
    print("  ・出力は常に正典 chrome（§WORKS/§NN/§REL/§REF/§SRC・標準サイドバー・")
    print("    canonical/hreflang/GA/JSON-LD）")
    print("  ・素材の器（§IMAGE LINKS / §SOURCES / Profile / ダーティtitle 等）の漏れゼロ")
    print(f"  render 出力サイズ: {len(ha.encode('utf-8'))} bytes（A==B）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
