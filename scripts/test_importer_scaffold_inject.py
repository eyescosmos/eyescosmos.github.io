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
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from import_chatgpt_photographer import (  # noqa: E402
    extract_bundle, render_ja_page, unwrap_rev_spans, self_check,
)

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
    # 素材の rich keyword は spec.tags（カード用2語=語1/語2）と別語にする。
    # これで ph-kw / side-chip が bundle.keywords 由来（spec.tags 由来でない）こと、
    # サイドバーが先頭4件に切られることを検証できる。
    '<div class="ph-keywords"><span class="ph-keywords__label">Keywords</span>'
    '<span class="ph-kw">KW一</span><span class="ph-kw">KW二</span>'
    '<span class="ph-kw">KW三</span><span class="ph-kw">KW四</span>'
    '<span class="ph-kw">KW五</span></div>'
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

CONTENT_KEYS = ["lead_inner_html", "thesis_inner_html", "keywords", "works",
                "sections", "related_people", "related_movements",
                "further_books", "further_links", "sources"]

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


def test_unwrap_rev_spans_multidigit() -> None:
    """rev[0-9]+ 対応: 2桁以上の rev クラス（rev19 等）もネスト込みで unwrap される。
    非 rev span とのネストは保持される（志賀理江子刷新での実害の再発防止）。"""
    src = '<span class="rev19">a<span class="rev2">b</span>c</span>'
    out = unwrap_rev_spans(src)
    assert out == "abc", f"FAIL: 多桁 rev span が unwrap されていない: {out!r}"

    # 非 rev span とのネストは維持される
    src2 = ('<span class="rev123">a<span class="keep">b</span>c</span>'
            '<span class="rev7">d</span>')
    out2 = unwrap_rev_spans(src2)
    assert out2 == 'a<span class="keep">b</span>cd', \
        f"FAIL: 非rev spanが保持されていない: {out2!r}"

    # self_check も多桁 rev 残存を検知できること（assert しない前提の残留チェック）
    dirty = '<span class="rev42">残存</span>'
    try:
        self_check(dirty, context="test")
        raise AssertionError("FAIL: self_check が多桁 rev 残存を検知できていない")
    except AssertionError as e:
        if "self_check が多桁 rev 残存を検知できていない" in str(e):
            raise
        # 期待通り AssertionError（rev スパンが残存している）が飛ぶ

    print("test_unwrap_rev_spans_multidigit PASS: 多桁 rev（rev19/rev123等）も"
          "unwrap・非revネスト保持・self_check残存検知OK")


def test_unwrap_revision_word_spans() -> None:
    """revision-<word> 語形対応: yurie-nagashima 素材の revision-fifth/third/red 等が
    数字形と同様に unwrap される（07-05 実走で85個/ファイル手除去した実害の再発防止）。"""
    src = ('<span class="revision-fifth">a<span class="revision-third">b</span>c</span>'
           '<span class="revision-red">d</span><span class="revision-new">e</span>')
    out = unwrap_rev_spans(src)
    assert out == "abcde", f"FAIL: revision-* 語形 span が unwrap されていない: {out!r}"

    # 非 rev span とのネストは維持・revision を含むだけの無関係クラスは触らない
    src2 = ('<span class="revision-sixth">a<span class="keep">b</span>c</span>'
            '<span class="ph-revisionist">d</span>')
    out2 = unwrap_rev_spans(src2)
    assert out2 == 'a<span class="keep">b</span>c<span class="ph-revisionist">d</span>', \
        f"FAIL: 非rev span が保持されていない: {out2!r}"

    # self_check が語形残存と語形CSSセレクタ残存を検知できること
    for dirty in ('<span class="revision-fourth">残存</span>',
                  '<style>.revision-red { color: red }</style>'):
        try:
            self_check(dirty, context="test")
            raise AssertionError(f"FAIL: self_check が revision-* 残存を検知できていない: {dirty!r}")
        except AssertionError as e:
            if "検知できていない" in str(e):
                raise
            # 期待通り残存 AssertionError が飛ぶ

    print("test_unwrap_revision_word_spans PASS: 語形 rev（revision-fifth等）の"
          "unwrap・非revネスト保持・self_check残存/CSS検知OK")


def test_bare_revision_and_nonspan_rev_classes() -> None:
    """裸 `revision`（接尾辞なし）と span 以外の要素の rev クラス対応
    （mika-ninagawa 素材で `<p class="revision">` 27箇所が render へ素通りした実害の
    再発防止）。誤爆ガード（review / revised / revisionist / ph-rev-* は不可触）も検証。"""
    from import_chatgpt_photographer import (
        clean_rev_markup, strip_rev_class_tokens, strip_review_css)

    # 1) 裸 revision: 純 rev span は unwrap、<p class="revision"> は要素保持で属性削除
    src = ('<span class="revision">a</span>'
           '<p class="revision">本文</p>'
           '<p class="revision revision-v4">両方rev</p>')
    out = clean_rev_markup(src)
    assert out == 'a<p>本文</p><p>両方rev</p>', \
        f"FAIL: 裸 revision の unwrap/属性削除が不正: {out!r}"

    # 2) 複合クラス（mika 実素材の形）: 要素保持・rev トークンだけ除去
    src2 = ('<div class="ph-cite revision-final" id="cite-1">c</div>'
            '<a class="chip-link revision-v3" href="https://x">L</a>'
            '<p class="ph-thesis__body revision">t</p>'
            '<div class="essay revision">e</div>'
            '<li class="revision-new">i</li>'
            '<span class="ph-section__name revision-final">n</span>')
    out2 = clean_rev_markup(src2)
    assert out2 == ('<div class="ph-cite" id="cite-1">c</div>'
                    '<a class="chip-link" href="https://x">L</a>'
                    '<p class="ph-thesis__body">t</p>'
                    '<div class="essay">e</div>'
                    '<li>i</li>'
                    '<span class="ph-section__name">n</span>'), \
        f"FAIL: 複合クラスの rev トークン除去が不正: {out2!r}"

    # 3) 誤爆ガード: rev を含むだけの正規クラス・単語はトークン fullmatch 外＝不可触
    src3 = ('<p class="review">r</p><p class="revised">s</p>'
            '<div class="ph-rev-note">n</div><span class="revisionist">z</span>'
            '<p>本文中の revision という単語や review 文字列も無事</p>')
    assert clean_rev_markup(src3) == src3, \
        "FAIL: 正規クラス（review/revised/ph-rev-*/revisionist）が誤って消された"
    assert strip_rev_class_tokens(src3) == src3

    # 4) self_check がタグ種を問わず rev トークン残存を検知する
    for dirty in ('<p class="revision">残</p>',
                  '<div class="ph-cite revision-final">残</div>',
                  '<li class="revision-new">残</li>'):
        try:
            self_check(dirty, context="test")
            raise AssertionError(f"FAIL: self_check が非span rev 残存を検知できていない: {dirty!r}")
        except AssertionError as e:
            if "検知できていない" in str(e):
                raise
    # 正規クラスでは fail しない
    self_check('<p class="review">ok</p><span class="revisionist">ok</span>',
               context="test")

    # 5) CSS 除去: 裸 .revision ルールは除去・.revisionist 等の正規ルールは保持
    css = ('<style>.revision { background: yellow } '
           '.revision-final { color: red } '
           '.revisionist { color: blue } '
           '.essay p { margin: 0 }</style><p>x</p>')
    out5 = strip_review_css(css)
    assert '.revision {' not in out5 and '.revision-final' not in out5, \
        f"FAIL: 裸 .revision / .revision-final ルールが除去されていない: {out5!r}"
    assert '.revisionist { color: blue }' in out5 and '.essay p { margin: 0 }' in out5, \
        f"FAIL: 正規 CSS ルールが誤って消された: {out5!r}"

    print("test_bare_revision_and_nonspan_rev_classes PASS: 裸revision unwrap/属性削除・"
          "非span複合クラスのトークン除去・誤爆ガード・self_check/CSS連動OK")


def test_en_merge_skip_empty_and_invariance() -> None:
    """③ EN field-merge のロジック: skip-empty（空値で既存を消さない・bundle 非生成
    フィールドを保全）と、他 slug が byte/値レベルで不変であることを検証する。"""
    from import_chatgpt_photographer import (
        _apply_merge, _merge_field_plan, _assert_only_key_changed,
        _is_empty_merge_value, _dump_content_json)

    # skip-empty: 新値が空('', None, [], {})なら既存維持。非空なら上書き。add も。
    current = {
        "h1": "Old Name", "lead_html": "<p>old lead</p>",
        "sources_html": "<div>old</div>",
        # bundle_to_en_entry が生成しないフィールド（保全されるべき）:
        "entry_meta_html": "<dl>KEEP</dl>", "photobooks_html": "<div>KEEP</div>",
        "footer_html": "<footer>KEEP</footer>",
    }
    new = {
        "h1": "New Name",            # replace
        "lead_html": "",             # skip-empty（空で消さない）
        "sources_html": None,        # skip-empty
        "keywords_html": "<div>kw</div>",  # add
        # entry_meta_html 等は new に無い → 保全
    }
    merged = _apply_merge(current, new)
    assert merged["h1"] == "New Name", "FAIL: 非空フィールドが replace されていない"
    assert merged["lead_html"] == "<p>old lead</p>", \
        "FAIL: 空文字で既存 lead が消された（skip-empty 破れ）"
    assert merged["sources_html"] == "<div>old</div>", \
        "FAIL: None で既存 sources が消された"
    assert merged["keywords_html"] == "<div>kw</div>", "FAIL: 新規 add されていない"
    for k in ("entry_meta_html", "photobooks_html", "footer_html"):
        assert merged[k] == current[k], f"FAIL: bundle 非生成フィールド {k} が保全されていない"

    assert _is_empty_merge_value("") and _is_empty_merge_value(None) \
        and _is_empty_merge_value([]) and _is_empty_merge_value({}), \
        "FAIL: 空値判定が不正"
    assert not _is_empty_merge_value("x") and not _is_empty_merge_value(["x"]), \
        "FAIL: 非空を空と誤判定"

    plan = {p["key"]: p["action"] for p in _merge_field_plan(current, new)}
    assert plan["h1"] == "replace", f"FAIL: h1 plan={plan['h1']}"
    assert plan["lead_html"] == "skip-empty", f"FAIL: lead plan={plan['lead_html']}"
    assert plan["keywords_html"] == "add", f"FAIL: keywords plan={plan['keywords_html']}"
    assert plan["entry_meta_html"] == "skip-empty", \
        f"FAIL: 非生成 entry_meta plan={plan['entry_meta_html']}"

    # 他 slug 不変 assert: 対象 slug 以外のエントリを1文字でも変えたら fail する
    content = {"_meta": {"count": 2}, "pages": {
        "target.html": dict(current), "other.html": {"h1": "Untouched"}}}
    good = {"_meta": {"count": 2}, "pages": {
        "target.html": merged, "other.html": {"h1": "Untouched"}}}
    _assert_only_key_changed(content, good, "target.html")  # 通る
    bad = {"_meta": {"count": 2}, "pages": {
        "target.html": merged, "other.html": {"h1": "Tampered"}}}
    try:
        _assert_only_key_changed(content, bad, "target.html")
        raise AssertionError("FAIL: 他 slug 改変を assert が検知できていない")
    except AssertionError as e:
        if "検知できていない" in str(e):
            raise
    # _meta 改変も検知
    bad_meta = {"_meta": {"count": 99}, "pages": good["pages"]}
    try:
        _assert_only_key_changed(content, bad_meta, "target.html")
        raise AssertionError("FAIL: _meta 改変を assert が検知できていない")
    except AssertionError as e:
        if "検知できていない" in str(e):
            raise

    # dump が round-trip byte 一致（末尾改行なし・churn なし）
    d = {"_meta": {"count": 1}, "pages": {"x.html": {"h1": "あ", "years": "1970–"}}}
    assert json.loads(_dump_content_json(d)) == d, "FAIL: dump round-trip 破れ"
    assert not _dump_content_json(d).endswith("\n"), "FAIL: dump 末尾に改行"

    print("test_en_merge_skip_empty_and_invariance PASS: skip-empty で空値既存維持・"
          "bundle非生成フィールド保全・他slug/_meta不変assert・dump churnなし")


def test_update_existing_carry_forward_helpers() -> None:
    """④ carry-forward のロジック: §REF body 抽出・backup 必須ガード・検証失敗時の
    ロールバックを、リポの実ページに触れずに検証する（JA_DIR を tmp へ差し替え）。"""
    import tempfile
    import import_chatgpt_photographer as imp
    from import_chatgpt_photographer import _extract_ref_body

    # §REF body 抽出（_set_section_body と対称・div 入れ子対応）
    page = (
        '<section class="ph-section"><div class="ph-section__head">'
        '<div class="ph-section__title">'
        '<span class="ph-section__num">§ REF</span>'
        '<span class="ph-section__name">さらに読む</span></div></div>'
        '<div class="ph-section__body">'
        '<ul class="ph-further-links"><li><a href="https://ex.org/db">DB'
        '</a></li></ul></div></section>')
    ref = _extract_ref_body(page)
    assert ref and "ph-further-links" in ref and "https://ex.org/db" in ref, \
        f"FAIL: §REF body 抽出が不正: {ref!r}"
    assert _extract_ref_body('<div>no ref</div>') is None, \
        "FAIL: §REF が無いのに None を返さない"

    # backup 必須ガード（安全契約 b）: backup が無ければ書込せず非0
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        orig_ja = imp.JA_DIR
        try:
            imp.JA_DIR = tmp
            (tmp / "someone.html").write_text("<html>current</html>", encoding="utf-8")
            # backup 無し → rc=2 で停止、ページ不変
            spec = {"id": "someone"}
            o = {"body_chars": 100, "unique_cites": 2, "suprefs": 2,
                 "ref_links": 1, "ref_is_prep": False}
            n = {"ref_is_prep": True, "ref_links": 0}
            rc = imp._apply_update_existing(
                "someone", spec, {}, "<html>old</html>",
                "<html>new</html>", o, n)
            assert rc == 2, f"FAIL: backup 無しで停止していない（rc={rc}）"
            assert (tmp / "someone.html").read_text(encoding="utf-8") == \
                "<html>current</html>", "FAIL: backup 無しなのにページが書き換わった"
        finally:
            imp.JA_DIR = orig_ja

    print("test_update_existing_carry_forward_helpers PASS: §REF抽出・backup必須ガード"
          "（無backupで無書込・非0終了）OK")


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

    # 6) Keywords は素材（bundle.keywords）由来であり spec.tags（カード用2語）由来でない。
    #    ph-kw=全件・サイドバー ph-side-chip=先頭4件（is-primary は先頭1）。
    for k in ("KW一", "KW二", "KW三", "KW四", "KW五"):
        assert f'<span class="ph-kw">{k}</span>' in ha, \
            f"FAIL: ph-kw に素材 keyword {k!r} が無い（bundle.keywords が反映されていない）"
    for t in ("語1", "語2"):
        assert f'<span class="ph-kw">{t}</span>' not in ha, \
            f"FAIL: ph-kw に spec.tags {t!r} が残っている（素材で差し替えられていない）"
    # サイドバーは先頭4件・is-primary は先頭のみ・5件目は出ない
    assert '<span class="ph-side-chip is-primary">KW一</span>' in ha, \
        "FAIL: サイドバー先頭 chip が is-primary + 素材 keyword でない"
    for k in ("KW二", "KW三", "KW四"):
        assert f'<span class="ph-side-chip">{k}</span>' in ha, \
            f"FAIL: サイドバー ph-side-chip に {k!r} が無い（先頭4件でない）"
    assert '<span class="ph-side-chip">KW五</span>' not in ha and \
        '<span class="ph-side-chip is-primary">KW五</span>' not in ha, \
        "FAIL: サイドバーが先頭4件に切られていない（5件目 KW五 が出ている）"
    for t in ("語1", "語2"):
        assert f'<span class="ph-side-chip">{t}</span>' not in ha and \
            f'<span class="ph-side-chip is-primary">{t}</span>' not in ha, \
            f"FAIL: サイドバー chip に spec.tags {t!r} が残っている"

    print("M4 PASS:「器を捨てた」証明")
    print("  ・構造の違う2ソース（content先頭head / Profile型sidebar / 非正規§マーカー /")
    print("    §IMAGE LINKS / 節順違い / title・description違い）→ render 出力が byte 同一")
    print("  ・出力は常に正典 chrome（§WORKS/§NN/§REL/§REF/§SRC・標準サイドバー・")
    print("    canonical/hreflang/GA/JSON-LD）")
    print("  ・素材の器（§IMAGE LINKS / §SOURCES / Profile / ダーティtitle 等）の漏れゼロ")
    print(f"  render 出力サイズ: {len(ha.encode('utf-8'))} bytes（A==B）")

    test_unwrap_rev_spans_multidigit()
    test_unwrap_revision_word_spans()
    test_bare_revision_and_nonspan_rev_classes()
    test_en_merge_skip_empty_and_invariance()
    test_update_existing_carry_forward_helpers()
    return 0


if __name__ == "__main__":
    sys.exit(main())
