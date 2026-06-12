# build_photographers_en.py 仕様（Stage 2/3 — 写真家ページ英語化）

目的: JA v5.1 ページ（`photographers/*.html`、293件、構造は全ページ均一）をテンプレートに、
収穫済み英文（`data/photographers-en-content.json` の `pages`、281件に本文あり）を流し込み、
`en/photographers/<slug>.html` を上書き生成する冪等スクリプト。

## 入出力・対象
- 入力: JA ページ、`data/photographers-en-content.json`、`data/photographers-en-classification.json`
- 出力ファイル名: JA と同名。ただし `jp-漢字.html` は classification の `jp_slug_mapping` を逆引きしてローマ字名で出力（例 `jp-植田正治.html` → `shoji-ueda.html`）
- スキップ: classification `missing_en_true` の12件（英文なし、Stage 4）。`en/photographers/jp-*.html` のリダイレクトスタブと `stieglitz-backup.html` には触れない
- CLI: `--slug X`（複数可）/ `--pilot`（ansel-adams, moriyama, jp-植田正治→shoji-ueda, alexander-gardner, aglaia-konrad）/ `--all`
- `scripts/generate_photographer_pages.py` は実行・import しない。JA ページは一切変更しない

## 再利用
- `scripts/build_taxonomy_en.py` を import し `STUB_TO_SLUG`（運動 JAファイル名→ENスラッグ）、
  `SLUG_TO_EN_NAME`、`FALLBACK_COUNTRY_EN` 等のテーブルを再利用（importは副作用なし、main guard 済み）

## 変換手順（1ページ）
1. `lang="ja"` → `lang="en"`
2. **head**: title / meta description / canonical / hreflang×3 / og:* / twitter:* を harvest 値で置換
   （JA側に同名タグがあれば値置換、なければ挿入）。charset・viewport・フォント・インラインstyle・GA は温存。
   JSON-LD は harvest の `jsonld` で JA の JSON-LD を置換（JA側に無い2ページは missing 対象なので考慮不要）
3. **EN可読性style**: メイン `</style>` 直後に
   `<style>.essay p,.ph-abstract p,.ph-thesis__body{text-align:left;}</style>` 系の上書きを挿入
   （JAが justify の場合のみ意味を持つが、無条件挿入で冪等に）
4. **header**: brand リンク → `/en/index.html`。crumbs の写真家名は英名大文字、運動語は運動テーブルで英名化。
   lang切替: JP→`<a href="/photographers/<ja-file>">JP</a>`（kanjiファイル名はURLエンコード）、EN側に `is-active`
5. **hero**: `h1.ph-hero__name` → 英名（harvest h1）。`ph-hero__en` → JA名（JA h1から取得）+ 既存 years span 温存。
   eyebrow 末尾の運動語を英名化
6. **meta値の英語化**（hero meta-row / ph-entry-meta / ph-side-meta 共通）:
   - Country: JA国名→EN国名（テーブル）。リンクは `en/countries/<x>.html` が実在すれば `/en/countries/...`、なければ JA のまま
   - Movement: 運動テーブルで英名化、`/en/movements/<slug>.html` 実在チェック
   - Period: リンク `/en/eras/<n>.html` 実在チェック。値はそのまま
   - Entry / Category / Years / Updated はそのまま
7. **Abstract**: `ph-abstract` の `<p>` 内容を harvest `lead_html` の内側（`<p class="lead">` を剥がす）で置換
8. **Thesis**: harvest `thesis_html` があればラベル→ `What this photographer changed`、本文置換。
   なければ `ph-thesis` div を丸ごと削除（281中278は無し）
9. **Keywords**（本文 ph-keywords とサイド ph-side-chips）: チップは温存。運動名チップは英名化＋ENリンク。
   keywords/* リンクは JA のまま（ENキーワードページは存在しない）
10. **§ WORKS**: JA のchip-link温存、セクション名→ `View Works`、note→
    `This site does not display work images. Please visit the official archives below.`
    harvest `notable_works_html` に JAに無いURLがあれば chip-link を追記
11. **TOC＋本文**: JA の `ph-toc` と `id="sec-NN"` セクション群を削除し、harvest `sections` から再構築。
    `§ 0i / 0N`、タイトルは harvest の `title`（HTMLアンエスケープ）。body は `body_html` を使用し
    `<h4>` → `<h3 id="h3-NN">`（通し番号）。`div.essay` ラッパが無ければ付与。
    TOC は sections と h3 から JA と同じ markup（details/summary/toc-list/toc-sub、先頭 is-active）で生成。
    summary → `Contents · Table of Contents`
12. **§ REL**: harvest `site_directory_html` の contextual グループ
    （Related people & photographers / Related movements）からリンクを抽出し、
    ph-rel-list（名前リンクのみ、説明文なし）で再構築。セクション名 `Related photographers & movements`、
    ラベル `Related photographers` / `Related movements`。グループが無ければセクション削除
13. **§ REF**: セクション名 `Further reading`。
    - `photobooks_html` の book-card → ph-book 形式（title / note / `View on Amazon ↗` / `* Affiliate link`）。
      `rel="noopener sponsored"` 維持。ラベル `Photobooks`
    - `external_links_html` → ラベル `Databases & archives` の ph-further-links リスト
    - `further_reading_html` があれば末尾に付加
14. **§ SRC**: セクション名 `Sources`。harvest `sources_html` の `cite-item`→`ph-cite`、`cite-num`→`ph-cite__num`、
    リンク部を `<div>` で包む（JA v5.1 と同形式）。id=cite-N 維持
15. **cite整合**: supref が指す cite-N が無い場合（4ページ既知）、その sup-ref のアンカーをプレーンテキスト化
16. **sidebar**: ラベル英語化（SEARCH · Find a photographer / placeholder `Name, movement, keyword` /
    Entry · Profile / Keywords / Works · Links / Navigate）。side-nav:
    `← 写真家一覧`→`← All photographers`（`/en/archive.html` 実在すればEN、なければJA）、
    前リンク→EN相当ページ＋英名＋`Prev`、`トップページへ`→`Top page`（`/en/index.html`）。
    検索JSの `該当する写真家が見つかりません` → `No photographers found`
17. **footer**: 中央文言→ `Based on museum, archive, and specialist sources`、
    privacy → `/en/privacy-policy.html`（実在チェック）、コロフォン→ `Colophon`
18. **内部リンク総ざらい（最終パス）**: 文書全体の `href` について、相対 `../` を絶対化した上で
    `/photographers/X.html` → EN版が（今回生成分含め）実在すれば `/en/photographers/X'.html`
    （X' は jp-slug マッピング考慮）、`/movements|/eras|/countries` も同様。EN が無ければ JA 絶対パスのまま。
    外部URL・`#`アンカー・amazonは触らない
19. **data-nosnippet**: `header.head`・`aside.ph-side`・`footer.foot`・site-directory（あれば）に付与
20. 実装は Python3 stdlib のみ。ネスト div の抽出は深さカウントのバランス抽出ヘルパで行う（非貪欲regex禁止）

## 監査スクリプト scripts/check_photographers_en.py
生成ページ全数に対し検査し、ページ単位で PASS/FAIL と理由を出力:
- lang="en" / GA(gtag) あり / canonical が自URL / hreflang×3 あり・ja↔en相互整合
- h1 が1つで英名
- `.essay` と `.ph-abstract` 内の CJK 文字比率 < 5%（日本語本文の混入検知）
- sup-ref の参照先 cite-N が実在 / cite-N の重複なし / TOC アンカー（sec-NN, h3-NN）が実在
- 相対 `../` 内部リンクが残っていない / `/en/...` リンクはファイル実在 / `/...` JAリンクもファイル実在
- data-nosnippet が header/sidebar/footer にある
- `<section` と `</section>` の数が一致、`<div` と `</div>` の数が一致
- ファイルサイズ > 40KB
