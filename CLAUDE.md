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
1. `'ペン': 'irving-penn'` をエイリアスマップから削除（`アーヴィング・ペン` 等の長いエイリアスが残存）
2. `scripts/generate_photographer_pages.py` の `should_skip_alias_boundary()` に `KATAKANA_RE` 境界チェックを追加。カタカナエイリアスが隣接カタカナに接していればリンクをスキップする。

**エイリアス登録ルール（今後）：**
- カタカナ2〜3文字のみの短いエイリアス（例: `ペン`、`マン`）は登録しない。文中の別語への誤マッチが起きる。
- `アーヴィング・ペン` のような姓名フルカタカナ形、または漢字氏名形を使う。
- 新しくエイリアスを追加した場合は、追加後にジェネレータを実行し `python3 scripts/check_photographer_link_integrity.py` で誤リンクがないか確認する。

### 手書きHTMLページ（ジェネレータ非対象）の扱い
- 以下のページは直接HTMLを編集しており、ジェネレータで上書きされない：
  - `photographers/annie-leibovitz.html` / `en/photographers/annie-leibovitz.html`
  - `photographers/stieglitz.html` / `en/photographers/stieglitz.html`
- これらのページに本文を直接書くことは許可されるが、push 後に Codex が上書きする可能性がある
- 重要な本文は `data/photographer-essay-overrides.js` への移行を検討する
