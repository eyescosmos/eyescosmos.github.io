# 国別ページ（ハブ型）構造基準（v5.1）

**いつ読むか:** `countries/*.html` / `en/countries/*.html` を修正・生成するとき。
**適用範囲：国別ページのみ。** リーフ型（写真家個別）基準とは別物。
2026-06-13 に**全 62 ページ（単国＋複合）を v5.1 へ移行済み**。参照実装は `countries/france.html`。

---

**生成パイプライン（再生成で再現）:**
- メタデータの正本は `data/country-pages.json`（slug / codes / nameJa / nameEn /
  lead / updated）。`scripts/build_country_registry.py` が旧ページ＋card-data から
  一度だけブートストラップ済み。**移行後は旧 h1 markup が無いので再ブート不可**。
  以後は JSON を直接編集する。
- ページ生成は `scripts/generate_country_pages.py`。`data/country-pages.json` と
  `card-data.json`・`archive.html`・`eras/1839.html`（CSS）を読む。
  **スコープフラグ必須（無指定はガードで拒否＝1ファイルも書かない）。**
  通常は対象 slug だけ再生成し、全再生成は明示時のみ：
  - `python3 scripts/generate_country_pages.py --country japan`（複数可・主表記）
  - `--all` で registry 全ページ（旧無指定と byte 一致）。`--only` は `--country` の旧別名（残置）。
  - typo の slug は照合で拒否され、全生成へ化けない。
- カード変換ロジック（href 相対化・target 除去・国コード置換・ledeJa 全文）は
  年代ページの `add_missing_era_cards.py` と共有。カードCSSは `archive.html` の
  バリアント定義を流用（`.cards` masonry ＋ `body.v51` ＋ 全 `pc-top--*`）。
- 運動ドロップダウンは `movements/*.html` 全件を列挙（全ページ共通）。
- **国別ページは単国（33ページ）のみ。二重国籍（複合）ページは廃止済み。**
  二重国籍写真家は関係する各単国ページに掲載される（例: マン・レイ→アメリカ＋フランス）。
  旧複合ページ（hungary-france.html 等 29枚）は `scripts/retire_composite_country_pages.py`
  により **redirect スタブ化**（noindex + meta-refresh + canonical → 第1コードの単国ページ）。
  ナビ・サイト内リンクからは除外済み（`generate_country_pages.py` が registry に無い
  slug を除去）。複合ページを新規に作らないこと。
  ※他セクション（en/・一部 photographer ページ）から複合ページへの旧リンクは
  スタブ経由で転送される。各ジェネレータ再実行時に単国ページへ張り替えること。

## 位置づけ
- 国別ページは**写真家一覧が主役のシンプルなハブ**。解説・thesis・abstract・
  context grid は**作らない**（リーフ型や年代ページと異なる）。
- デザインは v5.1（`styles/card-v4-base.css` + `styles/card-v5-overrides.css` +
  年代ページの `<style>` ブロックをそのまま流用）。新規 CSS は国別固有の
  最小オーバーライドのみ（`.country-nav` / `.era-layout--solo` /
  `.country-hero` / `.site-directory-links`）。

## セクション順序
1. `<head>`（title / description / canonical / hreflang ja・en・x-default /
   og / twitter。**JSON-LD は付けない**。フォント・カード CSS・年代ページ
   `<style>`・GA）
2. `header.head`（ブランド・パンくず `COUNTRIES / 国名`・言語トグル JP/EN・
   モバイル検索）— `data-nosnippet`
3. `section.era-hero.country-hero`（アート面に国コード大文字＋ラベル、
   info に国名 h1・英語名・リード文・メタ行 Photographers/Country/Code/Vol）
4. `div.country-sticky`（**position:sticky; top:0** でスクロール追従）内に：
   - `div.country-toolbar > label.toolbar__search`：アーカイブと同形の検索欄
     （`#country-filter`）。このページのカードをテキストで実時間フィルタ
     （`CARD_FILTER_SCRIPT`、ヒット0件で `#er-no-result` 表示）
   - `nav.era-nav.country-strip`：年代ページと同形の**横スクロール strip**で
     全単国を列挙（現在の国は `is-active`）。ラベル「§ — 国から読む」
     （EN は「§ — Browse by country」）
   - モバイルでは header の sticky を解除（`@media(max-width:760px){.head{position:static}}`）
     して二重 sticky の重なりを防ぐ。旧 `<select>` 3種・候補ドロップダウン検索は廃止
   — `data-nosnippet`
5. `div.era-outer > div.era-layout.era-layout--solo > main.era-main`（**サイド
   バーなし single-column**）内に `section.ph-section` 1 個。`§ PH / 国名の
   写真家` の見出し＋`div.er-cards`（カードグリッド）
6. `nav.site-directory-links`（年代一覧・国一覧・代表写真家一覧。旧ページから
   移植）— `data-nosnippet`
7. `footer.foot`（v5.1 3 カラム）— `data-nosnippet`
8. 末尾に年代ページと同じ検索 `<script>` 2 本（要素欠如をガード済みで安全）

## 掲載メンバーと並び順
- メンバーは **`card-data.json` を正**とし、`nationality` に国コードが
  **部分一致**する写真家全員（純 `FR` と二重国籍 `US / FR` 等の両方）。
- **二重国籍の写真家は関係する両方の単国ページに掲載**する（複合ページ
  `hungary-france.html` 等のフランス側メンバーも `france.html` に含める）。
  複合ページ自体の削除・リダイレクト化は後日。
- 並び順は **`era` 昇順 → 同値は `idx` 昇順**（`idx` は追加順であり厳密な
  生年順ではない点に注意）。
- 生成時、`card-data` から算出したメンバー集合をハードコードの期待リストと
  突合し、`photographers/{id}.html` の実在も assert する（欠落で fail）。

## カード仕様
- カードは年代ページと同一の `pc-card` 構造。**`archive.html` を正データ**とし、
  `scripts/add_missing_era_cards.py` の `transform_card` と同一変換を適用：
  `<article>` クラス整理 / `href` を `../photographers/` へ相対化 /
  `target="_blank"` 除去 / `<span>PHOTOGRAPHER</span>` を `card-data` の
  `nationality`（国コード）へ置換 / 切り詰め lede を `ledeJa` 全文へ差し替え。

## 不可視の必須要素
- **Google Analytics**（gtag `G-2VRTV8BZEJ`）
- **`data-nosnippet`**：header・country-nav・site-directory-links・footer の
  UI クローム、および各カードの `.pc-top` と `.pc-body__cta`
- title / description / canonical / hreflang は必須

## リンク規則
- **`/keywords/` へのリンクは一切張らない**（keywords ページは未実装）。
- リンク先は実在ページのみ（写真家・運動・年代・アーカイブ・他の国）。
- カード href は `../photographers/`（相対）、ナビ・フッターは `/…`（絶対）。

## EN 版
- 英語版（`en/countries/*.html`）も同一仕様で移行済み（単国33＋複合29スタブ）。
  生成は `scripts/generate_country_pages_en.py`：`data/country-pages.json`（共通の正本）
  ＋ EN カードは `en/archive.html`（href `/en/photographers/`、lede は EN サイト共通で
  切り詰め表示のまま）＋ EN クローム（header/hero/footer/検索）は `en/eras/1839.html`
  から抽出。h1=英名・period=和名、運動ドロップダウンは有効な EN movement 8件、
  era 系リンクは `/en/eras/`・`/en/archive.html`（旧EN国別は誤って `/eras/` を指していた）。
  複合は EN redirect スタブ（→ `/en/countries/<target>`、JA スタブの転送先を踏襲）。
  EN もスコープフラグ必須：`python3 scripts/generate_country_pages_en.py --country japan`
  （対象1ページのみ・複合スタブは触らない）／`--all`（全ページ＋スタブ再生成・旧無指定と byte 一致）。
  無指定はガードで拒否。
