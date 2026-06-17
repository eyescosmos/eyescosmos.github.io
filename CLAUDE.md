# Project rules

このリポジトリは写真史を扱うWebサイトです。
世界・日本・各国の写真家、運動、思想、時代背景、関連性を整理し、写真史をたどれるようにすることを目的とします。

## JA/EN 正本と生成ルール — 最優先 — CRITICAL

このサイトは JA と EN で正本(source of truth)が違う。古い overrides 前提の指示と衝突する場合は、このセクションを優先する。

### 写真家ページ
- JA 写真家ページ `photographers/*.html` は **HTML 自身が正本**。本文・thesis・§REL・出典・書籍欄を手編集してよく、永続する。
- `scripts/generate_photographer_pages.py` は実行禁止。旧デザインを生成し、JA ページを旧構造と言語トグル破損へ巻き戻す。物理ガードを解除しない。
- EN 写真家ページ `en/photographers/*.html` は **出力物**。直接手編集しても `scripts/build_photographers_en.py` の再生成で消える。
- EN 写真家本文の正本は `data/photographers-en-content.json`。`body_html` が本文、`thesis_html` が thesis、`site_directory_html` が Related people / Related movements。
- EN 本文の事実を直す場合は、`data/photographers-en-content.json` の該当 `body_html` と、必要なら旧経路の `data/photographer-essay-overrides.js` の `textEn` を両方そろえる。片方だけだと不整合が残る。
- EN の本文 / thesis / §REL を直すときは EN HTML を触らず、正本データを直して `python3 scripts/build_photographers_en.py --slug <slug>` で再生成する。

### その他の正本
- アーカイブ: `archive.html` が JA 正本。`en/archive.html` は `scripts/build_archive_en.py` で生成。`scripts/generate_archive_pages.py` は実行禁止。
- 国別ページ: `data/country-pages.json` が正本。`scripts/generate_country_pages.py` / `scripts/generate_country_pages_en.py` で生成。
- 年代・運動ページ: JA HTML が正本。EN は `scripts/build_taxonomy_en.py` で生成。

### 実務ルール
- 事実修正（生没年・地名・書名・出版社・年・ISBN・URLなど）は、出力HTMLだけでなく正本へ入れる。捏造禁止・出典準拠。
- `scripts/link_country_keywords.py` など横断スクリプトを回したら、`git status` / `git diff` で対象外ページの巻き込みを確認し、混入差分は revert する。二重国籍の国名が畳まれていないかも確認する。
- TOP12 ハードコードカード（`pc-top` / `idx` / `pc-top--XXX`）、フィルター/ソートUI、カードJSは依頼がない限り触らない。カードの正は `cards-archive.html` / `card-data.json`。
- テンプレ差し替え・デザイン移行時は GA(`G-2VRTV8BZEJ`) / canonical / hreflang / OG / JSON-LD / `data-nosnippet` を必ず引き継ぐ。

### push 前チェック
```bash
git pull origin main
python3 scripts/check_content_loss.py
python3 scripts/preflight.py
git diff origin/main
```
警告が出たら、意図した変更か、正本（JA HTML / `data/photographers-en-content.json` / `data/photographer-essay-overrides.js`）と一致しているか確認してから push する。

## Skill priority
- 既存ファイルの形式よりskill.mdの指示を優先すること

## Working style
- 今回の作業に必要な最小限のファイルだけ読む
- リポジトリ全体を最初から走査しない
- 既存の構造、CSS、コンポーネントをできるだけ再利用する
- 大きなリファクタは依頼された場合のみ行う
- 最小差分で修正する
- 変更後の報告は簡潔にする

## 渡された素材（HTML 含む）の扱い — 全般ルール — CRITICAL

**新規ページ作成・本文の追加／修正のいずれでも、Daisuke から渡された素材が
HTML ファイル（ChatGPT 等の生成物を含む）であっても、明示の指示がない限り、
その HTML 構造・デザイン・サイドバー・chrome・節構成は一切流用しない。
中身の要素（本文テキスト・見出し・出典・作品リンク・書誌・メタ等）だけを抽出し、
編集対象の既存ページの構造／標準テンプレへ流し込む。**

- 目的：作業を最小化する。渡された構造を後から直す手間を発生させない。
- 既存ページの本文を追加／修正する場合も、渡された HTML の構造に合わせず、
  **既存ページの構造・クラス・リンク慣習に合わせて中身だけ差し込む**。
- 構造を採用するのは「この構造のまま使って」と**明示された場合のみ**。
- 写真家ページ固有の詳細（捨てる要素・標準サイドバー形・本文リンク化・素材の
  事実検証）は「写真家個別ページの作業手順 > 新規ページ作成時の入力素材の扱い」
  を参照。

## 写真家個別ページの作業手順

### タスク受領時（必須）

- 参照実装 `photographers/ansel-adams.html` を必ず確認してから作業を始める
- `skill.md` を読み、「さらに読む」セクション仕様など最新の編集基準を把握する
- 編集対象ページの現状を把握する（本文・構造・セクション順序の確認）

### 新規ページ作成時の入力素材の扱い — CRITICAL

新規写真家ページを作るときは、**最初から標準テンプレ（参照実装 `ansel-adams.html`）の
構造・サイドバー・本文リンク慣習に合わせて1パスで作る**。後から直す作り方をしない。

**渡された素材が ChatGPT 等の生成した HTML ファイルであっても、その HTML 構造は
一切流用しない。テキスト（本文・見出し・出典・作品・書誌・メタ）だけを抽出して
標準テンプレへ流し込む。** 具体的に捨てるもの：

- ChatGPT 独自の右サイドバー（スティッキー）。例：`Basic information` /
  `Verified works` / `On this page` 等のブロック。**サイドバーは必ず標準形式に置き換える**
  （`Entry · 写真家データ` / `Keywords · キーワード` / `Works · 作品リンク` /
  `Navigate · 移動`。EN は `Entry · Profile` / `Keywords` / `Works · Links` / `Navigate`）
- 独自の節構成・独自ラベル（`Contextual links`・独自 `ARCHIVES` 節など）。
  節は基準の順序・名称に合わせる
- 独自の `<head>`・chrome・言語トグル・フッター。GA / hreflang / canonical / OG /
  JSON-LD / `data-nosnippet` は標準ページから引き継ぐ（「ページ移行・テンプレート
  差し替え時の必須要素」参照）

**本文中の写真家・運動は、ページが実在するものを最初のパスでリンク化する**
（JA は `/photographers/…`・`/movements/…` の絶対パス、EN は `/en/…`。EN の運動 slug は
実在確認。初出1回・隣接語の重複置換に注意）。実在しない名称はリンクしない。

**EN 版は原則 `build_photographers_en.py` で生成する**
EN 本文・thesis・§REL は `data/photographers-en-content.json` に入れ、`--slug <slug>` で再生成する。
classification で `missing_en_true` のページなど、EN 正本データが未整備の例外だけは手作業方針を確認してから進める。

**ChatGPT 素材の事実・書誌・URL は捏造の可能性があるため、本文採用前に検証する**
（「情報の捏造禁止とバックアップ」参照）。重要データ（生没年・書名・出版社・年・
ISBN・URL）は検証済みにしてから組み込む。

**Daisuke に渡してもらう理想フォーマット**（これがあると最速）：JA・EN を同一構成で、
①メタ（日本語名／英語名／生没年／国／era／キーワード）②本文（節見出し＋段落）
③出典リスト（`番号 = 名称 / URL`）④本文中の出典マーカー（各文末に `[3]` 等）
⑤作品リンク・写真集（書名・著者・出版社・年・ISBN・Amazon URL）。

### 既存ページ修正時の残骸点検

既存ページを構造修正する際は、以下の残骸が残っていないか確認して除去する：
- `<section>` や `<div>` の閉じタグ忘れ・余分な開始タグ
- `page-shell` 直下のテキストノードや孤立タグ
- 意図しない空セクション（中身のない `<section>` 等）
- 参照実装に存在しないセクション種別・ID

新基準で廃止されたクラス・タグ（発見したら除去する）：
- `page-facts`, `facts-grid`, `fact-item`
- `table.facts` および facts テーブル全体
- 「外部リンク」セクション（出典と重複するため）
- 「関連作品」セクション（「作品を見る」と重複するため）
- `title-block` 内の `<span class="years">`（生没年は entry-meta に集約）
- 古い 3 列構成の entry-meta（`grid-template-columns: auto 1fr auto 1fr auto 1fr` の名残）

HTML 構造破損の典型例（発見したら修正する）：
- `page-shell` や `container` 開始直後の、対応する開始タグのない `</div>` の連続
- 開始タグだけがあり閉じタグがない `<div>` や `<section>`
- ネストが崩れたタグ階層

### 情報の捏造禁止とバックアップ

- 書誌情報（書名・著者・出版社・年・ISBN）を推測または生成しない
- 出典に書いていない評価・批評を書かない
- 不明な書籍情報・URLが必要な場合は Daisuke に確認する（空欄にして確認依頼）
- Amazon URLや外部リンクを推測で生成しない（Daisuke が用意したもののみ使用）

バックアップ作成（既存ページ修正時の必須手順）：
- 既存ページを修正する場合、編集前に必ず
  `photographers/{ファイル名}-backup.html` としてバックアップを作成する。
  バックアップなしで上書きしない。
- バックアップは `cp` コマンドまたは内蔵のファイル操作で作成する。
- バックアップ作成後、編集前のファイル内容を読み込み、本文・出典・
  書籍情報・Amazon リンクなど、復元時に参照すべき情報を把握してから
  編集に入る。

### 編集後の確認項目

- セクション順序が `ansel-adams.html` の参照実装と一致しているか
- `§ NN / 全数` の全数が実際のセクション数と一致しているか
- 「さらに読む」セクションの書籍に書名・著者・出版社・年が揃っているか
- 孤立タグ・残骸の除去が完了しているか
- 変更が最小差分になっているか（不要なリファクタが混入していないか）
- thesis に禁止表現（「完成」「完成形に」「完成させた」「決定的」「唯一の」
  「集大成」「頂点」「真の○○」など、歴史を閉じる最上級・断定表現）が
  混入していないか確認する。混入していれば本文の出典から導ける表現に書き換える
  （「thesis の断定度に関する基準」セクション参照）。
- 出典 sup-ref と cite-NN の対応関係を検証する：
  - 本文中の各 `<sup class="sup-ref"><a href="#cite-N">*N</a></sup>` の
    リンク先が、出典セクションの `cite-N` に実在するか
  - 出典セクションの各 `cite-N` が、本文中で少なくとも 1 回参照されているか
    （孤立した cite がないか）
  - 番号の重複・欠番がないか
  - 本文中で `<sup class="sup-ref">` を連続させない。`*1*2*3` や
    `[*1][*2][*3]` のような連番注は禁止
  - 1文につき注番号は最大1つまで。1段落末尾に複数出典をまとめない
  - 複数出典が必要な主張は、文を分けるか最も対応する出典を1つ選ぶ

### 適用範囲

本作業手順は写真家個別ページ（`photographers/*.html`）にのみ適用する。
以下のページ群には適用しない：

- 分類ページ（国別: `countries/*.html`、運動別: `movements/*.html`、
  年代別: `eras/*.html`、キーワード別: `keywords/*.html`）
- 日本語サイトのトップページ、アーカイブページ、サイトナビゲーションページ
- 英語版ページ（`en/photographers/*.html`）— 構造は同じだが、翻訳・校正の
  別基準を伴うため、ペアで作業する場合のみ対象

参照実装は `photographers/ansel-adams.html`、直近修正済みの実例は
`photographers/hiroshi-sugimoto.html`。

分類ページのうち**国別ページ（ハブ型）の構造基準は下記「国別ページ
（ハブ型）構造基準（v5.1）ドラフト」に定義済み**（参照実装：
`countries/france.html`）。運動別・年代別・キーワード別の基準は引き続き
後日定義する予定。基準が未定義の分類ページは、構造変更を伴う修正を行わない。

## 国別ページ（ハブ型）構造基準（v5.1）ドラフト

**適用範囲：国別ページ（`countries/*.html`）のみ。** リーフ型（写真家個別）
基準とは別物。2026-06-13 に**全 62 ページ（単国＋複合）を v5.1 へ移行済み**。
参照実装は `countries/france.html`。

**生成パイプライン（再生成で再現）:**
- メタデータの正本は `data/country-pages.json`（slug / codes / nameJa / nameEn /
  lead / updated）。`scripts/build_country_registry.py` が旧ページ＋card-data から
  一度だけブートストラップ済み。**移行後は旧 h1 markup が無いので再ブート不可**。
  以後は JSON を直接編集する。
- ページ生成は `scripts/generate_country_pages.py`。`data/country-pages.json` と
  `card-data.json`・`archive.html`・`eras/1839.html`（CSS）を読み、全ページを上書き生成。
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

### 位置づけ
- 国別ページは**写真家一覧が主役のシンプルなハブ**。解説・thesis・abstract・
  context grid は**作らない**（リーフ型や年代ページと異なる）。
- デザインは v5.1（`styles/card-v4-base.css` + `styles/card-v5-overrides.css` +
  年代ページの `<style>` ブロックをそのまま流用）。新規 CSS は国別固有の
  最小オーバーライドのみ（`.country-nav` / `.era-layout--solo` /
  `.country-hero` / `.site-directory-links`）。

### セクション順序
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

### 掲載メンバーと並び順
- メンバーは **`card-data.json` を正**とし、`nationality` に国コードが
  **部分一致**する写真家全員（純 `FR` と二重国籍 `US / FR` 等の両方）。
- **二重国籍の写真家は関係する両方の単国ページに掲載**する（複合ページ
  `hungary-france.html` 等のフランス側メンバーも `france.html` に含める）。
  複合ページ自体の削除・リダイレクト化は後日。
- 並び順は **`era` 昇順 → 同値は `idx` 昇順**（`idx` は追加順であり厳密な
  生年順ではない点に注意）。
- 生成時、`card-data` から算出したメンバー集合をハードコードの期待リストと
  突合し、`photographers/{id}.html` の実在も assert する（欠落で fail）。

### カード仕様
- カードは年代ページと同一の `pc-card` 構造。**`archive.html` を正データ**とし、
  `scripts/add_missing_era_cards.py` の `transform_card` と同一変換を適用：
  `<article>` クラス整理 / `href` を `../photographers/` へ相対化 /
  `target="_blank"` 除去 / `<span>PHOTOGRAPHER</span>` を `card-data` の
  `nationality`（国コード）へ置換 / 切り詰め lede を `ledeJa` 全文へ差し替え。

### 不可視の必須要素
- **Google Analytics**（gtag `G-2VRTV8BZEJ`）
- **`data-nosnippet`**：header・country-nav・site-directory-links・footer の
  UI クローム、および各カードの `.pc-top` と `.pc-body__cta`
- title / description / canonical / hreflang は必須

### リンク規則
- **`/keywords/` へのリンクは一切張らない**（keywords ページは未実装）。
- リンク先は実在ページのみ（写真家・運動・年代・アーカイブ・他の国）。
- カード href は `../photographers/`（相対）、ナビ・フッターは `/…`（絶対）。

### EN 版
- 英語版（`en/countries/*.html`）も同一仕様で移行済み（単国33＋複合29スタブ）。
  生成は `scripts/generate_country_pages_en.py`：`data/country-pages.json`（共通の正本）
  ＋ EN カードは `en/archive.html`（href `/en/photographers/`、lede は EN サイト共通で
  切り詰め表示のまま）＋ EN クローム（header/hero/footer/検索）は `en/eras/1839.html`
  から抽出。h1=英名・period=和名、運動ドロップダウンは有効な EN movement 8件、
  era 系リンクは `/en/eras/`・`/en/archive.html`（旧EN国別は誤って `/eras/` を指していた）。
  複合は EN redirect スタブ（→ `/en/countries/<target>`、JA スタブの転送先を踏襲）。

## Design invariants
- 本文があるページの h2 / セクションタイトルは、font-size: 14px、color: #c8a96e（アンバー）を維持する
- 本文内の h3 / 表現解説内の小見出しは、font-size: 1.02rem（約16.3px）、color: #a6bfa4（セージグリーン）を維持する
- 本文内リンクは青色で統一し、通常時・hover時ともアンバーや本文色へ戻さない
- これらの表示ルールを変更する場合は、個別HTMLの本文ではなく共通CSS（例: styles/photographer-page.css、styles/taxonomy-page.css）と必要な生成元を優先して調整する

## Writing principles
- AIの主観は書かない
- 出典・引用は明記する
- 文章は簡潔で説明的にする
- 生没年や出身地だけでなく、写真的・批評的な意味を重視する
- SEOを意識しても不自然なキーワード追加はしない

## thesis（この写真家が変えたこと）の断定度に関する基準

thesis は写真家の歴史的意義を述べる中核段落だが、評価が本文の出典から
導ける範囲を超えてはならない。以下を厳守する：

1. thesis で述べる評価は、本文中で出典（信頼ソース）によって裏づけられる
   主張の範囲にとどめる。本文に根拠のない評価的断定を thesis に書かない。

2. 歴史を閉じる最上級・断定表現を避ける。
   「完成（形）」「完成させた」「決定的」「唯一の」「集大成」「頂点」
   「真の○○」など、その写真家を到達点・終着点として閉じてしまう表現は、
   明確な出典がある場合を除いて使わない。
   代わりに、実際に行われたこと（体系化、精緻化、確立、定着、展開、
   再定義、問い直し、接続など）を具体的に記述する。

3. thesis と本文（特に批評・受容・写真史上の位置のセクション）が
   矛盾しないか確認する。本文で「後世に乗り越えられた」「批判的に
   継承された」「再評価された」と書く写真家を、thesis で「完成させた」
   と閉じることは矛盾にあたる。

4. 「○○というメディアのルールを書き換えた人ではなく、…」のような
   留保構文を使う場合、その後段の主張も同様に出典準拠であること。
   前段で過大評価を否定しながら、後段で別の過大評価に置き換えない。

例（全写真家に適用される一般ルール）：
- 避ける：「ストレート写真を完成形に到達させた」（出典なき断定、
  本文の批判的継承の論点と矛盾する可能性がある）
- 望ましい：「ストレート写真の方法論を一つの体系へと精緻化した」
  （本文の三部作・ゾーンシステム・教育の記述に準拠）

## 写真家個別ページ（リーフ型）構造基準

**適用範囲：写真家個別ページのみ。分類ページ（国別・運動別・年代別などの
ハブ型ページ）には適用しない。分類ページは別基準で定義する。**
参照実装：`photographers/ansel-adams.html`

### ページ全体のセクション順序

1. ヘッダー（サイトブランド、Photo Coordinates / Photographer ラベル、
   キーワードライン）
2. ナビゲーション（国別・年代別・運動・写真家のセレクト、検索窓、
   言語切替）— スティッキー
3. タイトルブロック（記事番号、写真家名 h1、英語名 + 生没年）
4. リード（lead-abstract / ABSTRACT）— ページ全体の要約
5. thesis（この写真家が変えたこと）— 上記「断定度に関する基準」に従う
6. entry-meta（Entry / Category / Country / Years / Period / Movement /
   Updated）。Country・Period・Movement はリンク化。facts テーブル等で
   同じ情報を重複させない（entry-meta に一元化）
7. キーワード（page-keywords）
8. 作品を見る（view-works-section）— 作品アーカイブへの外部リンク。
   コンパクトに収める
9. 目次（折りたたみ式）— 下記「目次の仕様」に従う
10. 本文（section-grid）— 下記「本文の構成」に従う
11. 関連する写真家・運動（related-section）
12. さらに読む（further-section）
13. 出典（sources）
14. サイト内リンク（site-directory-links）— フッターナビ
15. フッター（site-footer）

### 本文の構成

本文は複数のセクションに分け、各見出しは「§ NN / 全数」+
セクションタイトルの形式で進行を示す（例：§ 01 / 04 背景と時代）。
標準的な構成は以下：

- **背景と時代**：写真家の生涯・時代背景・写真史的文脈
- **表現の核心**：作家の方法論・思想を、複数の h3 小見出しで主題ごとに分節
- **代表作・方法・媒体**：代表作を作品単位に整理。各作品に h3 小見出しを立て、
  作品名・制作年を含める。代表作には通し番号マーカー（FIG. 01 形式）を付ける
- **批評と写真史上の位置**：同時代の対立軸、後続世代による継承・乗り越え、
  制度的な再評価などを h3 小見出しで分節

セクション数は写真家により増減してよい（3〜5 程度）。増減に応じて
「§ NN / 全数」の全数を調整する。本文の密度・情報量・批評の質は落とさない
（既存の執筆基準：要約・平易化をしない、出典準拠など）。

### 各セクションの内容ルール

- **thesis**：上記「thesis の断定度に関する基準」に従う
- **本文**：信頼ソース優先、Wikipedia 回避、出典は本文中に sup-ref で示し
  出典セクションの番号と対応させる
- **関連する写真家・運動**：各項目に「なぜ関連するのか」を一文で解説する。
  リンク先は実在するページに限る（存在しないページにはリンクしない）
- **さらに読む**：「写真集」「方法論・技術書」「関連データベース・アーカイブ」
  の区分で整理。Amazon アフィリエイトリンクを含む場合はアフィリエイト表示を付ける
- **出典**：本文の sup-ref と一対一で対応する典拠の一覧

### 重複の排除ルール

役割が重複するセクションを作らない：
- 「外部リンク」セクションは設けない。本文の典拠は「出典」に一元化し、
  読者向けの主要リソースは「さらに読む」のデータベース欄に載せる
- 「関連作品」のような作品リンクの重複セクションは設けない。
  作品アーカイブへのリンクは「作品を見る」に一元化する

### 目次の仕様

- `<details>` / `<summary>` によるネイティブ折りたたみで実装（JS 不要）
- デフォルトは閉じた状態（`open` 属性なし）
- 配置：「作品を見る」の直後、本文（section-grid）の直前
- 本文の各セクション（§ NN）と配下の h3 小見出しを階層表示し、
  それぞれへのアンカーリンクを張る
- アンカー id 命名規則：
  - 本文セクション：`sec-01`, `sec-02`, ... の連番
  - h3 小見出し：`h3-01`, `h3-02`, ... の本文出現順の連番
- ジャンプ先がスティッキーナビに隠れないよう `scroll-margin-top` を確保する
- 控えめなトーン（本文の補助ナビとして主張しすぎない）

### SEO・メタ情報

- 構造化データ（JSON-LD：WebPage / Person / BreadcrumbList）を含める
- `canonical`、`hreflang`（ja / en / x-default）、og、twitter のメタタグを含める
- 日本語ページと英語ページ（`/en/photographers/`）を相互に hreflang で結ぶ

### デザインについて

本基準は構造・順序・意味のみを定義する。色・余白・フォントサイズ・
カラム幅などのデザインは別途 Claude Design で決定するため、本基準では固定しない。

## Content style
- 文章は簡潔で説明的にする
- デザインと文体を維持する
- SEOは意識しても、不自然なキーワード追加はしない
- 見出しは内容を正確に表す
- 出典や引用がある場合は明記する
- 外部リンクだけで終わらせず、短くても自前の要約を書く
- 写真的・批評的な意味を重視する

## Page structure
写真家解説ページでは、必要に応じて以下の構成を使う
- 概要
- 経歴
- 表現解説
- 写真史上の位置づけ
- 批評と受容
- 関連作品・写真集
- 参考文献・出典

## Section heading rules — CRITICAL

textJa・textEn のメインセクション見出しは、ジェネレータの `ESSAY_HEADING_SET` に登録された語のみを使うこと。それ以外の語はh4（小見出し）になり、「解説」（デフォルト）という不要な見出しが出現する。

### 許可される見出し語（これ以外は使わない）
- textJa：`経歴`、`表現解説`、`批評と受容`
- textEn：`Biography`、`Expression / method`、`Criticism and reception`

### NG 例（使ってはいけない言い換え）
- `経歴と背景` → `経歴` にする
- `批評と評価` → `批評と受容` にする
- `Background and formation` → `Biography` にする
- `Critical reception` → `Criticism and reception` にする（大文字・語順に注意）

新しい見出しパターンが必要な場合は、`scripts/generate_photographer_pages.py` の `ESSAY_HEADING_SET` に追加してから使う。

## Content storage — CRITICAL
- JA 写真家ページ `photographers/*.html` は HTML 自身が正本。本文・解説・thesis・§REL・出典は HTML を直接編集する。
- EN 写真家ページ `en/photographers/*.html` は出力物。本文系を直接編集してはならない。正本は `data/photographers-en-content.json`。
- EN の本文は `body_html`、thesis は `thesis_html`、§REL は `site_directory_html` に入れてから `scripts/build_photographers_en.py --slug <slug>` で再生成する。
- EN の事実修正は、必要に応じて `data/photographer-essay-overrides.js` の `textEn` も同じ内容にそろえる。

## `scripts/generate_photographer_pages.py` は実行禁止 — 旧デザインで現行と乖離 — CRITICAL

**絶対に `python3 scripts/generate_photographer_pages.py` を実行しないこと。**

**理由（2026-06-13 確認）:** 現行の日本語写真家ページは v5.1 新デザイン
（`<header class="head">` ＋ `head__lang` トグル ＋ `<section class="ph-hero">`）に
移行済み。一方この旧ジェネレータは**別物の旧デザイン**（`lang-toggle`/`lang-btn`・
`title-block`・`lead-abstract`・`facts` テーブル等）を生成する。つまりジェネレータの
出力は現行ページと一致しない。

**実行した場合に起きること:**
- 294枚すべての JA 写真家ページの**デザインが旧版に巻き戻る**
- 修正済みの JA→EN 言語トグル（`<a href="/en/photographers/…"><button>EN</button></a>`）が
  消え、無反応の `<button>EN</button>` に戻る
- `ph-hero` ヒーロー・現行ヘッダー・モバイル検索などの新要素が消失する

**現在の正（source of truth）:**
- 日本語写真家ページの**構造・デザイン・ヘッダー・言語トグルは `photographers/*.html` 自身**
  （JA HTML が正）。構造・本文・解説・出典・関連欄の修正は HTML を直接編集する。
- EN 写真家本文の正本は `data/photographers-en-content.json`。
  `data/photographer-essay-overrides.js` の `textEn` に同じ文が残る場合は、事実修正時に両方をそろえる。
- 英語ページは `scripts/build_photographers_en.py` が JA HTML を入力に再生成する
  （この EN ビルダーは現行デザインを生成するので実行してよい）。

**言語トグルが再び壊れていないかの確認:**
```bash
# JA 側に無反応の素の EN ボタンが無いこと（0 件であるべき）
grep -l '<button>EN</button>' photographers/*.html movements/*.html eras/*.html
# 再発時の冪等修正
python3 scripts/fix_ja_lang_toggle.py --apply   # countries は除外・EN実在を検証
```

旧ジェネレータを現行デザイン用に作り直す場合は、Daisuke の明示依頼があったときのみ着手し、
着手前に本注意書きを更新すること。

## `scripts/generate_archive_pages.py` も実行禁止 — 旧デザイン生成 — CRITICAL

`generate_archive_pages.py` は旧デザイン（`<div class="photographer-card">` ＋ `toggleDetail()`）を
出力する。現行の `archive.html` / `en/archive.html` は v5.1 の `<article class="pc-card">`
（**JA archive.html が正本・手編集**、**EN は `scripts/build_archive_en.py`** が card-data.json から
pc-card を翻訳生成）。`generate_archive_pages.py` を実行すると v5.1 アーカイブを旧デザインへ
巻き戻す。2026-06-16 に `main()` 冒頭へ物理ガードを追加済み（解除は環境変数
`ALLOW_LEGACY_ARCHIVE_GEN=1`、generate_photographer_pages.py は `ALLOW_LEGACY_PHOTOGRAPHER_GEN=1`）。

## 機械チェック（地雷の門番）— 文章ルールより優先 — 2026-06-16 追加

CLAUDE.md の多くのルールは過去の事故の再発防止。重要なものは機械チェックへ移管済み：
- **`scripts/preflight.py`** — 決定論的な不変条件を検査（写真家id重複：
  photographers.js と supplement.js への二重登録／card-data.json 重複／GA(googletagmanager)欠落）。
  既存 `check_*.py` は WARN 表示のみ。`python3 scripts/preflight.py`。
- **`.githooks/pre-push`**（`git config core.hooksPath .githooks`）— push 前に preflight を自動実行し
  FAIL ならブロック。緊急回避は `git push --no-verify`。
- **`scripts/add_photographer.py` ＋ `scripts/photographer-spec.example.json`** — 新規写真家を
  card-data.json／supplement.js／スターマップ bin へ重複ガード付きで投入し、v5.1 カードの
  貼り付け用 HTML と実行コマンドを出力する半自動ヘルパー。
- 旧デザイン生成器2本（写真家・アーカイブ）は実行されると物理ガードで中断する（上記）。

## Content consistency
- アーカイブページと写真家の個別ページで同じ解説を持つ場合は、内容の整合性を保つこと
- どちらか一方の解説を更新した場合は、対応するもう一方のページにも同じ変更を適用

## Research workflow
- 小規模な調査は main conversation で行う
- 調査量が大きい場合は、調査だけを skill / subagent に委譲して要点だけ返す
- サイト掲載用の最終文面は main conversation で整える

## English sync policy
- 日本語ページで内容を確定してから英語ページへ反映する
- 英語ページ反映時は、新規調査ではなく既存の日本語内容を自然な英語に整える
- 英語ページの変更は対象セクションのみに限定する

## 手書き追加が再生成で消えないためのルール — CRITICAL

**どこに手書きすれば消えないか（正本の場所）:**

| ページ種別 | 正本（手書きしてよい場所） | 再生成で消えるか |
|---|---|---|
| JA 写真家ページ `photographers/*.html` | **HTML 自身**（JA ジェネレータは実行禁止＋物理ガード） | 消えない |
| EN 写真家ページ `en/photographers/*.html` | **`data/photographer-essay-overrides.js`… ではなく** EN は `data/photographers-en-content.json`（`thesis_html` / `site_directory_html` 等） | **JSON に無いものは `build_photographers_en.py` で消える** |

- **EN 写真家ページの本文系（thesis「この写真家が変えたこと」/ §REL 関連写真家・運動 など）を
  HTML に直接手書きしてはならない。** 必ず `data/photographers-en-content.json` の該当キー
  （`thesis_html` は英訳本文、`site_directory_html` は `Related people` / `Related movements` の
  contextual グループ）に入れてから `build_photographers_en.py` で再生成する。
  JA 由来の §REL とミラーさせたいときは JSON の `site_directory_html` を JA §REL から作り直す
  （実例：`scripts/fix_1839_en_thesis_related.py`）。
- **安全装置（2026-06-16 追加）:** `build_photographers_en.py` は、上書きしようとしている EN ページの
  手書き thesis / §REL リンクが新出力に再現されない（＝消える）と検知したら、**そのページだけ
  上書きせずスキップし `🛑 SKIPPED … would delete:` と表示する**。黙って消えることはない。
  - 表示が出たら：手書き内容を `photographers-en-content.json` に入れてから再実行する。
  - 意図的に消す場合のみ `--force`。
  - この門番は手書き維持ページ（`stieglitz` / `annie-leibovitz` の EN 等）が `--all` で
    巻き込まれて消えるのも自然に防ぐ。
- **JA 写真家ページは HTML 直接編集が正**。手書き thesis/関連欄はそのまま永続する
  （旧ジェネレータを `ALLOW_LEGACY_PHOTOGRAPHER_GEN=1` で無理に動かさない限り消えない）。

## Content preservation — Codex並行作業時の消失防止

### 作業前（必須）
- 編集を始める前に必ず `git pull origin main` で最新を取得する
- pull 後、対象ファイルの主要セクション（本文・作品画像・出典など）が残っているか確認してから編集を開始する

### push 前（必須）
- 必ず以下を実行する：
  ```bash
  git pull origin main
  python3 scripts/check_content_loss.py
  python3 scripts/preflight.py
  git diff origin/main
  ```
- push 前に `git diff origin/main` を確認し、自分の変更以外でセクションが消えていないか確認する
- 特に以下のセクションが消えていたら即座に復元する：
  - 本文（経歴・表現解説・批評と受容 / Career・Expression・Criticism）
  - 作品画像 / Work images セクション
  - 出典 / Sources セクション
  - **外部リンク（chip-link ボタン）** — 後述のジェネレータ実行前チェックで防ぐ
- `photographer-essay-overrides.js` を編集した場合は、push 前に必ず以下を実行する：
  ```
  python3 scripts/check_texten_completeness.py
  ```
  - OK が出ればそのまま push する
  - WARN が出たら、該当エントリの textEn が途中で切れていないか確認し、不足セクションを補完してから push する
  - このチェックで防ぐ問題：textJa には経歴・表現解説・批評と受容があるのに textEn が途中で切れている状態（過去に発生）

### Codex の変更を pull する前（必須）
- pull する前に `git fetch origin main` してから `git diff HEAD origin/main -- data/photographer-essay-overrides.js` を確認する
- Codex のコミットで overrides.js が変更されている場合、以下のセクションが消えていないか確認する：
  - 各エントリの `textJa` / `textEn`
  - `citations` 配列
- 消失が確認できた場合は pull せず、Codex 側に連絡して修正を依頼する
- HTML ページ（`photographers/` / `en/photographers/`）についても同様に確認する：
  - `git diff HEAD origin/main -- photographers/ en/photographers/` で本文・出典・作品画像セクションが消えていないか確認する

### Codex の変更を pull したとき
- `git show <commit>` でどのセクションが変更されたかを確認する
- Codex はアフィリエイト書籍カード・SEO・デザインを担当する。本文や出典が消えていたら復元する
- Codex の変更（書籍カード等）は上書きせず、自分の変更と共存させる

### 生成・横断処理前チェック — 外部リンク消失の防止 — CRITICAL

**過去に発生した問題：** 正本データ側に外部リンク・本文・出典が無い状態で生成/横断処理を実行すると、HTML に残っていた chip-link 外部リンクや本文要素が上書きで消える。

**注意:** `python3 scripts/generate_photographer_pages.py` は実行禁止。下記は EN ビルダーや横断スクリプトを動かす前の確認。

1. EN を再生成する場合、対象ページの `data/photographers-en-content.json` に `body_html` / `thesis_html` / `site_directory_html` / `photobooks_html` / `external_links_html` が必要分入っているか確認する。
2. EN の事実本文を直した場合、必要なら `data/photographer-essay-overrides.js` の `textEn` も同じ内容にそろえる。
3. JA HTML に chip-link 外部リンクが存在する場合、EN 正本データ側にも必要なリンクが入っているか確認する。

```bash
# HTML に外部リンクがあるか確認するコマンド例
grep "chip-link" photographers/xxx.html | grep -v "amazon\|chip-link amazon"
```

この確認を怠ると、生成や横断処理で多数ページの外部リンクが一括消失する。

### 本文混入・誤リンク再発防止 — CRITICAL

**過去に発生した問題：**
- `richard-avedon` 英語ページの `textEn` に Irving Penn 本文が混入した。
- 作品リンク自動化が全作家横断の作品名辞書として効き、`S` だけが `museumangewandtekunst.de` に飛ぶ誤リンクが複数ページで発生した。
- `The Family` のような汎用的な作品名が、`The Family of Man` の一部へ誤リンクされた。

**写真家ページやジェネレータを触る場合は必ず守ること：**
- `data/photographer-essay-overrides.js` の各エントリで、対象ID、`leadJa/leadEn`、`textJa/textEn`、`citations/citationsEn/citationsJa`、`links`、`works` が同じ作家に対応しているか確認する。
- 既存エントリを丸ごと置換する場合は、本文だけでなく、出典・外部リンク・作品リンクを消していないか確認する。必要に応じて `...current` で既存値を保持する。
- 英語だけ出典を変える場合は `citationsEn` を使い、共通 `citations` を不用意に上書きしない。日本語本文の注番号を壊す可能性がある。
- Avedon/Penn、Adams/Weston、Sugimoto/Moriyama、Avedon/Leibovitz など近い作家では、比較文脈と本文混入を区別する。別作家のBiography・Expression/method・Criticism・Photobooks・Sourcesがまとまって入っていたらFAIL。
- 本文中の作品自動リンクは、そのページ自身の `works` に登録された作品だけを対象にする。別作家の `works` をグローバルに本文へ適用しない。
- `S` / `LS` など1〜2文字のASCII英数字タイトル・別名は本文自動リンク対象にしない。作品欄のchip-linkとして表示するのはよいが、本文内の単語の一部へリンクさせない。
- 汎用語の作品名（例: `The Family`）は、必要なら `autoLink: false` を付け、作品欄には残して本文自動リンクから除外する。
- 生成後は `python3 scripts/check_photographer_link_integrity.py` を実行する。
- 生成後、`photographers/` と `en/photographers/` に `museumangewandtekunst.de` への1文字リンク、`>S</a>`、単語途中リンクが残っていないか確認する。
- canonical / hreflang / alternate / JSON-LD / `data-nosnippet` は本文やリンク修正で壊さない。生成後のdiffでSEOタグや構造タグに意図しない差分がないか確認する。
- push前に `git diff` で本文・外部リンク・作品リンク・出典が消えていないか確認する。

### エイリアスマップの短すぎる日本語エイリアス — CRITICAL

**過去に発生した問題：** `data/photographers-manual-additions.js` の `PHOTOGRAPHER_LINK_ALIASES` に `'ペン': 'irving-penn'` が登録されており、「ペンシルバニア」「スペンサー」「サーペンタイン」内の「ペン」が Irving Penn へのリンクに誤変換された（4ページで確認）。

**根本原因：** `should_skip_alias_boundary()` は ASCII 英数字の境界しかチェックしておらず、日本語（カタカナ）境界を検出できなかった。

**実施済み対応：**
- `scripts/generate_photographer_pages.py` の `should_skip_alias_boundary()` に `KATAKANA_RE` 境界チェックを追加。カタカナエイリアスの前後が隣接カタカナであればリンクをスキップする。
- `'ペン': 'irving-penn'` は意図的な略称として維持し、境界チェックで誤マッチを防ぐ。

**動作確認済みの境界チェック（ペンの場合）：**
- `ペンシルバニア`、`スペンサー`、`サーペンタイン`、`コペンハーゲン`、`ハイライター・ペン・` → SKIP（前後がカタカナ）
- `ペンと`、`ペンの`、`ペンが`、`ペンは`（前後が平仮名助詞） → LINK（正当な Penn 参照）

**エイリアス登録ルール（今後）：**
- 短いカタカナエイリアス（2〜3文字）を追加する際は、前後がカタカナの語に誤マッチしないか確認する。
- 追加後は必ずジェネレータを実行し `python3 scripts/check_photographer_link_integrity.py` で誤リンクがないか確認する。

### entry-meta 国名・キーワードのリンク（後処理）— CRITICAL

写真家ページの entry-meta `<dt>Country</dt>` の国名と、キーワード
（`.ph-kw` ＋ サイドバー Keywords ブロックの `.ph-side-chip`）は、対応ページが
実在する場合のみリンク化する。実装は `scripts/link_country_keywords.py`
（HTML を直接サージカル編集。本文・出典・書籍カードは一切触らない。冪等）。

- 国名：写真家の `nationality`（card-data）の各コードを単国ページへリンク。
  単国ページが無い国（スロバキア・リトアニア等の複合専用国）は plain のまま。
  JA→`/countries/`、EN→`/en/countries/`。
- キーワード：運動ページが実在すればリンク（JA は `/movements/{語}.html`、
  EN は slug 化して `/en/movements/{slug}.html`）。実在しない語（Magnum 等）は
  plain。`/keywords/` ページは無いのでリンクしない。
- **`build_photographers_en.py` 等で EN 写真家ページを再生成したら、必ず
  `python3 scripts/link_country_keywords.py` を再実行する**（JA ページは
  source of truth なので直接編集が残るが、EN は再生成で消えるため）。
- ただし `link_country_keywords.py` は JA+EN の多数ページを直接編集する横断処理。
  実行後は必ず `git status` / `git diff` で対象外ページの混入を確認し、作業対象外の差分は
  `git checkout -- <path>` で revert する。二重国籍の国名が単国へ畳まれていないかも確認する。

### 手書きHTMLページ（ジェネレータ非対象）の扱い
- 以下のページは過去に直接HTMLを編集した経緯があり、消失ガードの対象として特に注意する：
  - `photographers/annie-leibovitz.html` / `en/photographers/annie-leibovitz.html`
  - `photographers/stieglitz.html` / `en/photographers/stieglitz.html`
- JA は HTML 自身が正本なので直接編集してよい。
- EN は原則どおり `data/photographers-en-content.json` を正本にする。EN HTML へ直接書いた重要本文は、再生成前に必ず JSON へ移す。

## ページ移行・テンプレート差し替え時の必須要素 — CRITICAL

**過去に発生した問題：** 2026-06-08 の v5.1 全ページ移行（コミット 8ab5c9569）で、
新テンプレートに GA タグが含まれておらず、日本語の写真家285・運動31・年代11・
トップ・アーカイブの計測が約3日間止まった（2026-06-11 のコミット 33353c879 で復旧）。

**ルール：デザイン移行・テンプレート差し替え・ページの新版置き換えを行うときは、
見た目のHTMLだけでなく、以下の「不可視の必須要素」を新ページに引き継ぐこと。**

### 引き継ぎ必須要素チェックリスト

1. **Google Analytics**（gtag、ID: `G-2VRTV8BZEJ`）— 全公開ページに必須
2. **meta description / canonical / hreflang（ja・en・x-default）/ OG / Twitter カード**
3. **`<html lang="...">`** の言語属性
4. **data-nosnippet**（UIクローム：ヘッダー・タブ・ツールバー・フィルター・件数表示・
   フッター、カードの pc-top と pc-body__cta）
5. **構造化データ（JSON-LD）** — 旧ページにあった場合
6. `google739a609ca0f00aca.html`（サイト所有権確認ファイル）は削除・変更しない

### 移行後の検証（push 前に必須）

```bash
# GAカバレッジ一覧（リダイレクトスタブとGoogle確認ファイル以外は全数一致すること）
for d in . photographers movements eras countries en en/photographers en/countries en/movements en/eras; do
  tot=$(ls $d/*.html 2>/dev/null | wc -l); has=$(grep -l googletagmanager $d/*.html 2>/dev/null | wc -l);
  echo "$d: $tot total / $has with-GA"; done

# GA欠落の自動補完（冪等。GA済み・リダイレクトスタブ・バックアップ・en/・new-design/ は自動スキップ）
python3 scripts/insert_ga_tags.py
```

- 旧ページと新ページの `<head>` を diff し、消えるメタタグを一つずつ「消してよい」と
  確認できるまで push しない
- GA が不要なのは：リダイレクトスタブ（`noindex` + `http-equiv="refresh"` を両方持つ
  転送専用ページ）、`*-backup.html`、Google 確認ファイルのみ。
  **noindex だけのフルページ（例: fabian-marti, gabriel-orozco）には GA を入れる**
  （noindex は検索除外であって計測除外ではない）
- アーカイブ英語版は `scripts/build_archive_en.py` が SEO メタの日→英変換を含むため、
  日本語 archive.html に必須要素を入れてから再生成すれば英語側にも引き継がれる


## 新デザインページ（new-design/）の編集ルール — CRITICAL

### 基本原則：依頼された箇所以外は変更しない

`new-design/index.html` をはじめとする新デザインページを編集する際は、
**依頼された修正のみを行い、それ以外の箇所には一切触れない。**

リンク追加を依頼された場合 → href 属性のみ変更。他は変えない。
テキスト修正を依頼された場合 → そのテキストのみ変更。他は変えない。

### 変更禁止項目（依頼があっても勝手に触らない）

以下は「古い・間違い・改善できる」と見えても変更してはならない：

1. **TOP12カードHTML** — `pc-top`・`idx`・`pc-top__art`・`pc-top--XXX`クラス
   （JavaScript がアーカイブ版で自動上書きするため、ハードコード値は問題ない）

2. **フィルター・ソートUI** — `.pill[data-filter]`・`#nd-sort-btn`・`#nd-sort-dropdown`・
   `.sort-option[data-sort]` の構造・属性・テキスト

3. **カード制御JavaScript** — `ndRender()`・`archiveCardMap`・`ND_TOP12_NAMES`・
   `ndPhData`/`ndMvData`・フィルターイベントリスナー・ソートイベントリスナー

4. **アーカイブ取得ロジック** — `fetch('cards-archive.html')`・`fetch('card-data.json')` の処理

5. **CSSクラス体系** — `sort-wrap`・`sort-dropdown`・`sort-option`・`sort-divider` の定義

### 編集前の確認

`new-design/index.html` を編集する前に、変更対象のセクションのみを読む。
ファイル全体をリファクタ・整理・改善しない。

## カードデザインシステム（v4/v5.1）

### TOP12カード ハードコードHTML — 絶対に変更禁止 — CRITICAL

`new-design/index.html` および `index-v51.html` には TOP12 写真家のカードが HTML に直接書かれている。
**これらのカード HTML（`pc-top`・`pc-top__art`・`idx` など）は、いかなる修正作業でも絶対に変更してはならない。**

理由：
- カードのスタイル（`pc-top--cite` / `pc-top--number` など）・番号・アート内容は
  `cards-archive.html` を正とし、ページロード後に JavaScript が自動で上書きする
- ハードコード部分はロード中の一時表示にすぎず、最終表示は常にアーカイブ準拠になる
- しかし別の修正作業でこの部分を触ると「ハードコード値」が変わり、
  アーカイブ取得が失敗した場合（オフライン・fetch エラー等）に誤表示が残る

作業時の禁止事項：
- `<!-- 01 Stieglitz -->` 〜 `<!-- 12 Araki -->` の各 `<article>` 内の `pc-top` div を変更しない
- `idx` の数値を変更しない
- `pc-top__art` の内容を変更しない
- `pc-top--XXX` クラスを変更しない

リンク追加など他の修正をする際も、TOP12 カードブロックには一切触れないこと。
もしカードスタイルの変更が必要な場合は `cards-archive.html` を修正する（こちらが正）。

### ファイル構成

| ファイル | 役割 |
|---|---|
| `new-design/index.html` | 新デザイントップページ（スターマップ + TOP12カード）|
| `new-design/cards-archive.html` | 新デザイン用アーカイブ（カードの正データ）|
| `cards-archive.html` | カードアーカイブページ本体（283写真家 + 31運動 = 314枚） |
| `card-data.json` | 全314枚のカードデータ（photographers / movements） |
| `styles/card-v4-base.css` | カードデザインシステム基盤CSS |
| `styles/card-v5-overrides.css` | v5追加オーバーライドCSS |
| `index-v51.html` | v5.1トップページデザイン（スターマップ + 12枚フィーチャードカード） |

### カードの種類

- **Photographer カード** — 283枚（`data-type="photographer"`）
- **Movement カード** — 31枚（`data-type="movement"`）

### スタイル割り振りの優先順位

1. **TOP12 ハードコード**
   `stieglitz`, `takuma-nakahira`, `sherman`, `evans`, `robertfrank`, `moriyama`, `becher`, `cartierbresson`, `goldin`, `arbus`, `sander`, `araki`

2. **日本人写真家（nameJaに漢字あり）**
   → `pc-top--kanji` スタイル固定（artText は主題語）

3. **外国人写真家（主要28名）**
   → `pc-top--kanji-foreign`（概念漢字 + 英語グロス）

4. **残り外国人写真家**
   → 8スタイルをローテーション（`card-data.json` の `style` フィールド参照）

5. **運動カード**
   → 8スタイルのローテーション

### card-data.json のスタイルフィールド

card-data.json の `style` フィールドが使うのは以下 8 種のみ：
- `pc-top--kanji`（130件）
- `pc-top--title`（28件）
- `pc-top--slash`（28件）
- `pc-top--year`（27件）
- `pc-top--number`（27件）
- `pc-top--grid`（26件）
- `pc-top--stacked`（25件）
- `pc-top--initials`（23件）

### カード番号（idx）

- `card-data.json` の `idx` を正とする
- TOP12 の番号は card-data.json に合わせること（スティーグリッツ=15、中平=111 など）
- 番号は追加順（時代順でない）
- 運動カードは写真家の続番

### スタークリック（index-v51.html）

- 地図上の写真家をクリックすると、対応するカードをサイドパネルに表示する
- TOP12 の写真家 → 事前生成のフルデザインカードをクローン
- それ以外 → `card-data.json` から動的生成（`buildDynamicCard()` 関数）
- どちらにも一致しない場合 → archive へのリンクを表示

### CSSクラス体系

```
.pc-card               # カード全体
  .pc-card--photographer  # 写真家カード
  .pc-card--movement      # 運動カード
.pc-top                # カード上部（アートエリア）
  .pc-top__meta        # 番号 + ラベル
  .pc-top__art         # メインのタイポグラフィ
  .pc-top__hint        # 下部のヒントテキスト
.pc-body               # カード下部（テキストエリア）
  .pc-body__kind       # 種別ラベル
  .pc-body__name       # 日本語名
  .pc-body__name-en    # 英語名
  .pc-body__meta       # 生没年・国籍
  .pc-body__lede       # 紹介文
  .pc-body__channel    # チャンネル名
  .pc-body__tags       # タグ（最大3つ）
  .pc-body__cta        # 「写真史上の位置を読む →」
```
