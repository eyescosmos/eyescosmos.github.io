# Codex Project Rules

このリポジトリは写真史サイト「写真の座標 / Photo Coordinates」です。最重要事項は、JA と EN で正本(source of truth)が違うことです。ここを間違えると、再生成で本文・thesis・関連欄・出典が静かに消えます。

## Source of Truth — Critical

### 写真家ページ

- JA 写真家ページ `photographers/*.html`
  - HTML 自身が正本。本文・thesis・関連欄・出典・Amazon欄を手編集してよい。
  - `scripts/generate_photographer_pages.py` は実行禁止。旧デザインを生成し、JAページ全体を巻き戻す。物理ガードがあっても解除しない。

- EN 写真家ページ `en/photographers/*.html`
  - 出力物。直接手編集しても `scripts/build_photographers_en.py` の再生成で消える。
  - EN本文の正本は `data/photographers-en-content.json`。
  - `body_html` = 本文、`thesis_html` = thesis、`site_directory_html` = Related people / Related movements。
  - 作業前に `python3 scripts/en_entry.py <slug>` で対象slugだけを確認する。巨大JSON全体を読む必要はない。
  - EN本文の事実を直すときは、必要に応じて `data/photographer-essay-overrides.js` の `textEn` も同じ内容にそろえる。片方だけ直すと旧経路との不整合が残る。
  - EN本文・thesis・§REL を直すときは EN HTML ではなく正本データを直し、`python3 scripts/build_photographers_en.py --slug <slug>` で再生成する。
  - ENページを修正・追加・新規作成したら、作業終了前に必ず `python3 scripts/check_en_entry.py <slug>` と `python3 scripts/preflight.py` を実行する。EN HTMLだけの差分で終えない。

### その他の生成構造

- アーカイブ: `archive.html` が JA 正本。`en/archive.html` は `scripts/build_archive_en.py` で生成。`scripts/generate_archive_pages.py` は実行禁止。
- 国別ページ: `data/country-pages.json` が正本。`scripts/generate_country_pages.py` / `scripts/generate_country_pages_en.py` で生成。
- 年代・運動ページ: JA HTML が正本。EN は `scripts/build_taxonomy_en.py` で生成。

## Required Workflow

- 事実修正(生没年・地名・書名・出版社・年・ISBN・URLなど)は、必ず正本に入れる。
  - JA 写真家ページなら `photographers/*.html`。
  - EN 写真家ページなら `data/photographers-en-content.json` の該当 `body_html` / `thesis_html` / `site_directory_html` と、必要なら `data/photographer-essay-overrides.js` の `textEn`。
- 出力HTMLだけの事実修正は禁止。再生成で誤情報が復活する。
- 捏造禁止。出典にない評価・書誌・URL・Amazonリンクを推測で作らない。
- EN生成は JA を読むだけで、JA を書き換えない。逆に EN HTML の手書き修正は、正本データに入っていない限り消える。

## Forbidden / High-Risk Commands

- 実行禁止:
  - `python3 scripts/generate_photographer_pages.py`
  - `python3 scripts/generate_archive_pages.py`
- 横断後処理 `scripts/link_country_keywords.py` は全ページを直接編集する。実行したら必ず `git status` / `git diff` で対象外ページの混入を確認し、巻き込みは revert する。二重国籍の国名が畳まれていないかも確認する。
- TOP12 ハードコードカード(`pc-top` / `idx` / `pc-top--XXX`)、フィルター/ソートUI、カードJSは依頼がない限り触らない。カードの正は `cards-archive.html` / `card-data.json`。

## Content Preservation Guards

- `scripts/build_photographers_en.py` の content-loss guard は、再生成で thesis / §RELリンク / cite-N / FIG / lead が消えるページを検知し、そのページだけ上書きせず `🛑 SKIPPED` を出す。
  - 意図的に消す場合のみ `--force`。
  - 監査だけなら `--dry-run`。
- `scripts/check_content_loss.py` は読み取り専用の横断チェック。JA/EN両方で HEAD 比の出典・セクション・FIG・thesis・lead の減少を報告する。
  - `--strict` は消失時のみ非0終了。
  - 文面だけの変化は「事実すり替えの疑い」として警告される場合がある。警告は目視確認する。
- `scripts/en_entry.py <slug>` / `scripts/check_en_entry.py <slug>` は EN 写真家ページの対象slugだけを読む・検査するためのツール。通称slugも可（例: `atget` -> `eugene-atget`）。
- `scripts/preflight.py` と `.githooks/pre-push` は id重複、card-data重複、GA欠落、触ったEN slugの内容消失、EN HTMLとJSONの乖離、EN HTML直接編集疑いなどを検査する。FAILなら push しない。緊急回避は `git push --no-verify`。
  - EN写真家: `data/photographers-en-content.json` と `en/photographers/*.html` の差分から対象slugを推定し、内容消失・再生成漏れ・直接編集疑いを検知する。
  - EN国別: `data/country-pages.json` の主要情報消失をHARD、`en/countries/*.html` だけの変更を直接編集疑いWARNにする。
  - EN年代/運動: `data/taxonomy-en-content.json` のメタ・セクション消失をHARD、`en/eras/*.html` / `en/movements/*.html` だけの変更を直接編集疑いWARNにする。
  - ENアーカイブ: `card-data.json` のカード数・id・`nameEn` / `nameJa` / `href` 消失をHARD、`en/archive.html` だけの変更を直接編集疑いWARNにする。
  - 本文消失: `scripts/check_content_loss.py` を同じbaseline・`--strict`で実行して取り込む。写真家リーフ（JA + EN）の明確な本文消失（出典cite / 本文セクション / FIG / thesis / lead の減少）をHARD、構造不変のまま文面だけ変化した「書き換えの疑い」をWARNにする。JA写真家HTML（正本）の本文消失もpush前に自動ブロックされる。
  - SEO/不可視要素: 触った公開HTML（GAと同じ範囲）を baseline 比較し、baselineにあった canonical / JSON-LD / title / meta description / data-nosnippet の消失、または hreflang の減少をHARD。OGP/Twitter減・data-nosnippet部分減・新規ページのコア欠落をWARN。元から無いページ・新規ページはブロックしない（段階導入）。
  - JA写真家ページのSEO穴検知: `check_ja_seo_holes()` は、触った `photographers/*.html` だけを対象に、canonical / OGP / data-nosnippet / hreflang / meta description / JSON-LD が「元から無い・新規ページで付け忘れた」場合に WARN を出す。上のSEO消失ガードは「baselineにあった要素が消えた事故」をHARDで止めるものだが、`check_ja_seo_holes()` は穴検知専用で、pushをブロックしない。本文修正だけでSEO要素を消していない場合は鳴らないのが正常。
  - 新規JA写真家ページの最善手: 完成済みページ（例 `photographers/winogrand.html`）を丸ごとコピーして、名前・本文・出典・作品リンクだけ差し替える。これで GA / canonical / hreflang / OGP / Twitter / meta description / JSON-LD / data-nosnippet が最初から入る。ゼロから組むとGA欠落はHARDブロック、残りのSEO穴はWARNになりやすい。
  - `scripts/fill_seo_tags.py` は、既存JA写真家ページのSEO穴を本文・出典に触らず補う冪等フィクサー。`python3 scripts/fill_seo_tags.py` はdry-run、`--apply` で書き込み。補えるのは canonical / hreflang / data-nosnippet / OGP / Twitter。meta description本文とJSON-LDは捏造回避のため生成しないので、完成済みページからの移植または手作業で別途入れる。
  - JA分類ページ本文消失: 触った `archive.html` / `eras/*` / `movements/*`（HTML正本）を baseline 比較し、`<main>`領域消失・`<h1>`消失・`pc-card`数の減少をHARD、section/リンク/data-nosnippet の減少をWARN。国別はJSON正本のため対象外。
- 新規clone / Codex環境では、最初に `bash scripts/setup_hooks.sh` を一度実行して `.githooks/pre-push` を有効化する。`core.hooksPath` はローカル設定なので、実行するまでpush前チェックは自動では走らない。
- 上記SEOガードは「baselineにあった要素が消える事故」を止めるもので、元から欠けている既存穴（例: JA hreflang）の検出・修正はしない。テンプレ差し替え時は別途確認する。

## EN 写真家ページ編集フロー — Required

```bash
python3 scripts/en_entry.py <slug>
# data/photographers-en-content.json を修正（EN HTMLは直接編集しない）
python3 scripts/build_photographers_en.py --slug <slug>
python3 scripts/check_en_entry.py <slug>
python3 scripts/preflight.py
```

- `--force` は消失ガードを外すため常用しない。誤検知や意図的な削除時だけ使う。
- `preflight.py` は baseline（通常 `origin/main`）と比較し、触ったEN slugだけを検査する。既存不具合は無関係なpushをブロックしない。

## Push前チェック — Required

push 前に必ず次を実行・確認する。

```bash
git pull origin main
python3 scripts/check_content_loss.py
python3 scripts/preflight.py
git diff origin/main
```

- `git diff origin/main` では、本文・thesis・関連欄・出典・作品画像・外部リンク・Amazonリンク・SEOタグが意図せず消えていないか目視する。
- push 前に必ず `git status --short` と `git diff --name-only` / `git diff --stat` を見て、依頼対象外ファイルの巻き込み、生成前状態への巻き戻り、本文・構造・リンク・出典の消失、意図しない差分がないことを確認する。未追跡ファイルは依頼対象でない限り stage しない。
- 警告が出た場合は、意図した変更か、正本(JA HTML / `data/photographers-en-content.json` / `data/photographer-essay-overrides.js`)と一致しているか確認してから push する。

## General Style

- 既存の構造、CSS、コンポーネントをできるだけ再利用する。
- 大きなリファクタは依頼された場合のみ行う。
- 変更は最小差分にする。
- 写真的・批評的な意味を重視し、出典・引用は明記する。
- 渡されたHTML素材は、明示指示がない限り構造を流用しない。本文・見出し・出典・作品リンク・書誌・メタなど中身だけを既存テンプレへ流し込む。
