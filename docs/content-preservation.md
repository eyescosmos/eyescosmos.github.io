# コンテンツ消失防止・誤リンク防止（Codex並行作業／横断スクリプト）

**いつ読むか:** Codex と並行作業するとき、横断スクリプト（`link_country_keywords.py` 等）や
EN ビルダーを走らせるとき、`photographer-essay-overrides.js` を編集するとき、
本文自動リンク・エイリアス周りを触るとき。

---

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
