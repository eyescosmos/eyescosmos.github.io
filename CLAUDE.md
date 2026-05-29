# Project rules

このリポジトリは写真史を扱うWebサイトです。
世界・日本・各国の写真家、運動、思想、時代背景、関連性を整理し、写真史をたどれるようにすることを目的とします。

## Skill priority
- 既存ファイルの形式よりskill.mdの指示を優先すること

## Working style
- 今回の作業に必要な最小限のファイルだけ読む
- リポジトリ全体を最初から走査しない
- 既存の構造、CSS、コンポーネントをできるだけ再利用する
- 大きなリファクタは依頼された場合のみ行う
- 最小差分で修正する
- 変更後の報告は簡潔にする

## 写真家個別ページの作業手順

### タスク受領時（必須）

- 参照実装 `photographers/ansel-adams.html` を必ず確認してから作業を始める
- `skill.md` を読み、「さらに読む」セクション仕様など最新の編集基準を把握する
- 編集対象ページの現状を把握する（本文・構造・セクション順序の確認）

### 既存ページ修正時の残骸点検

既存ページを構造修正する際は、以下の残骸が残っていないか確認して除去する：
- `<section>` や `<div>` の閉じタグ忘れ・余分な開始タグ
- `page-shell` 直下のテキストノードや孤立タグ
- 意図しない空セクション（中身のない `<section>` 等）
- 参照実装に存在しないセクション種別・ID

### 情報の捏造禁止

- 書誌情報（書名・著者・出版社・年・ISBN）を推測または生成しない
- 出典に書いていない評価・批評を書かない
- 不明な書籍情報・URLが必要な場合は Daisuke に確認する（空欄にして確認依頼）
- Amazon URLや外部リンクを推測で生成しない（Daisuke が用意したもののみ使用）

### 編集後の確認項目

- セクション順序が `ansel-adams.html` の参照実装と一致しているか
- `§ NN / 全数` の全数が実際のセクション数と一致しているか
- 「さらに読む」セクションの書籍に書名・著者・出版社・年が揃っているか
- 孤立タグ・残骸の除去が完了しているか
- 変更が最小差分になっているか（不要なリファクタが混入していないか）

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
- 写真家の本文・解説は必ず `data/photographer-essay-overrides.js` に書く
- `photographers/*.html` に直接書いてはならない（ジェネレータ実行で上書きされ消える）
- ジェネレータ（`scripts/generate_photographer_pages.py`）は全HTMLを毎回上書き生成する
- HTMLへの直接編集は永久に失われる。唯一の永続ストレージは overrides JS ファイル

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

## Content preservation — Codex並行作業時の消失防止

### 作業前（必須）
- 編集を始める前に必ず `git pull origin main` で最新を取得する
- pull 後、対象ファイルの主要セクション（本文・作品画像・出典など）が残っているか確認してから編集を開始する

### push 前（必須）
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

### ジェネレータ実行前チェック — 外部リンク消失の防止 — CRITICAL

**過去に発生した問題：** overrides.js の `links:` 配列が削除・未設定の状態でジェネレータを実行すると、HTML に残っていた chip-link 外部リンクが上書きで消える。

**ジェネレータ（`python3 scripts/generate_photographer_pages.py`）を実行する前に必ず確認すること：**

1. 編集対象の写真家エントリが overrides.js に `links:` 配列を持っているか確認する
2. 対応する HTML（`photographers/xxx.html`）に chip-link 外部リンクが存在する場合、その URL が overrides.js の `links:` に入っているかを照合する
3. HTML に links があるのに overrides.js に `links:` がない場合、先に overrides.js へ追記してからジェネレータを実行する

```bash
# HTML に外部リンクがあるか確認するコマンド例
grep "chip-link" photographers/xxx.html | grep -v "amazon\|chip-link amazon"
```

この確認を怠ると、ジェネレータ実行で多数ページの外部リンクが一括消失する。

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

### 手書きHTMLページ（ジェネレータ非対象）の扱い
- 以下のページは直接HTMLを編集しており、ジェネレータで上書きされない：
  - `photographers/annie-leibovitz.html` / `en/photographers/annie-leibovitz.html`
  - `photographers/stieglitz.html` / `en/photographers/stieglitz.html`
- これらのページに本文を直接書くことは許可されるが、push 後に Codex が上書きする可能性がある
- 重要な本文は `data/photographer-essay-overrides.js` への移行を検討する
