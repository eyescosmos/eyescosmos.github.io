# Codex Project Rules

このリポジトリは写真史サイト「写真の座標 / Photo Coordinates」です。最重要事項は、JA と EN で正本(source of truth)が違うことです。ここを間違えると、再生成で本文・thesis・関連欄・出典が静かに消えます。

## 絶対禁止 — NEVER — 最初に読む

1. **`python3 scripts/generate_photographer_pages.py` を実行しない**。旧デザインを生成し、JAページ全体を巻き戻す。物理ガードがあっても解除しない。
2. **`python3 scripts/generate_archive_pages.py` を実行しない**。
3. **既存の `en/photographers/*.html` を再生成しない**。既存ENページは **HTML 自身が正本**（2026-09-13〜）。`build_photographers_en.py` は既存ページへの書き込みを既定で拒否する（解除は `ALLOW_EN_REBUILD=1`・移行監査と緊急 rollback 比較のみ）。**新規ENページの作成だけ** `data/photographers-en-content.json` + builder のまま。詳細 `docs/en-html-canon-migration.md` §2a。
4. **生成物が正本でないサーフェス（国別 / 年代・運動EN / ENアーカイブ）で、事実修正を出力HTMLだけに入れない**。必ず正本へ入れる。再生成で誤情報が復活する。JA写真家ページと既存EN写真家ページは HTML 自身が正本なので対象外。
5. **捏造しない**。出典にない評価・書誌・URL・Amazonリンクを推測で作らない。
6. **国別・年代・運動の生成スクリプトをスコープフラグ無指定で実行しない**（無指定はガードで拒否）。写真家1人追加で `--all` は不要。安全な生成コマンド集は `docs/generators-and-guards.md`「フルリビルド・ガード」。
7. **TOP12 ハードコードカード（`pc-top` / `idx` / `pc-top--XXX`）、フィルター/ソートUI、カードJSは依頼がない限り触らない**。カードの正は `cards-archive.html` / `card-data.json`。

## 正本(source of truth)マトリクス — Critical

| サーフェス | 正本 | 生成コマンド | 備考 |
|---|---|---|---|
| JA写真家 `photographers/*.html` | **HTML自身** | なし（手編集・永続） | 本文・thesis・関連欄・出典・Amazon欄を手編集してよい |
| EN写真家 `en/photographers/*.html`（**既存**） | **HTML自身** | なし（手編集・永続） | JA と同じく直接編集してよい。JSON は読まれない |
| EN写真家 `en/photographers/*.html`（**新規作成のみ**） | `data/photographers-en-content.json` | `python3 scripts/build_photographers_en.py --slug <slug>` | 出力先が未作成のときだけ書ける。既存ページは builder が拒否 |
| ENアーカイブ `en/archive.html` | `archive.html`（JA正本） | `python3 scripts/build_archive_en.py` | |
| 国別 JA/EN | `data/country-pages.json` | `generate_country_pages.py` / `generate_country_pages_en.py`。`--country <slug>`（通常）/ `--all`（全生成） | スコープフラグ必須 |
| 年代・運動 EN | JA HTML | `python3 scripts/build_taxonomy_en.py`。`--era <YYYY>` / `--slug <movement>`（通常）/ `--all`（全生成） | スコープフラグ必須 |

- 既存EN写真家ページは HTML 自身が正本なので、`en/photographers/<slug>.html` を直接編集して終わり。JSON は読まれない。
- EN本文の事実を直すときは、必要に応じて `data/photographer-essay-overrides.js` の `textEn` も同じ内容にそろえる。片方だけ直すと旧経路との不整合が残る。
- JA を直したら EN も同じ構造にそろえる。節や §REL を JA にだけ足すと preflight の日英対称性ガードが HARD で止める。

## EN 写真家ページ編集フロー — Required

**既存ページの修正**（通常はこちら）:

```bash
# en/photographers/<slug>.html を直接編集する（JSON も builder も使わない）
python3 scripts/check_en_entry.py <slug>
python3 scripts/preflight.py
```

**新規ページの作成**（当面のみ JSON + builder）:

```bash
python3 scripts/en_entry.py <slug>
# data/photographers-en-content.json に entry を入れる
python3 scripts/build_photographers_en.py --slug <slug>   # 出力先が未作成のときだけ書ける
python3 scripts/check_en_entry.py <slug>
python3 scripts/preflight.py
```

- 既存ページに対して builder を回すと `🛑 REFUSED` で拒否される。これは正常。直接編集に切り替える。
  `ALLOW_EN_REBUILD=1` は移行監査・緊急 rollback 比較だけに使う。
- ENページを修正・追加・新規作成したら、作業終了前に必ず `python3 scripts/check_en_entry.py <slug>` と `python3 scripts/preflight.py` を実行する。
- `preflight.py` は baseline（通常 `origin/main`）と比較し、触ったEN slugだけを検査する。既存不具合は無関係なpushをブロックしない。
- preflight の EN 向け HTML ガード（2026-09-13 追加）:
  - keyword chip（`ph-kw` / `ph-side-chip`）のリンクが baseline 比で裸span化・href変更した場合は HARD。
  - JA と EN の §REL（人物・運動の slug 集合）の非対称は、今回入れたものが HARD、既存分は WARN。
  - JA と EN の本文節ラベル（`ph-section__num`）の非対称も同じ判定。

## Required Workflow

- 事実修正(生没年・地名・書名・出版社・年・ISBN・URLなど)は、必ず正本に入れる。
  - JA 写真家ページなら `photographers/*.html`。
  - EN 写真家ページなら `en/photographers/*.html`（既存ページは HTML 自身が正本）と、必要なら `data/photographer-essay-overrides.js` の `textEn`。新規作成中のページだけ `data/photographers-en-content.json`。
- 横断後処理 `scripts/link_country_keywords.py` は全ページを直接編集する。実行したら必ず `git status` / `git diff` で対象外ページの混入を確認し、巻き込みは revert する。二重国籍の国名が畳まれていないかも確認する。

### 実測ログ — Required

写真家の追加・修正、およびその他のページ修正があったときは、**常に実測して `docs/importer-run-log.md` に記録する**。目的は「測ってから作る」＝ツール投資（ph-*→旧クラス変換器・carry-forward apply・M6 v3 サーフェス自動書込）の要否を実数で判断するため。

- 客観項目（種別 new/update/other・bug・手作業点の数と具体内容・サーフェス変更数・フィデリティ差分・発火した engine 改良・commit）は作業した側が埋める。**wall-time（所要分）は Daisuke が記入**。
- 写真家以外のページ修正は軽量行でよい（種別=other・wall-time・手作業点・touched files。フィデリティ列 N/A 可）。
- 手作業ボトルネック（特に lead/sources/view_works の手移植、新規 movement/tag 語の翻訳辞書穴）を一言添える。

### 新規写真家追加フロー — Required

新規写真家をゼロから追加するときは、後からSEO・構造・掲載漏れを直す往復を避けるため、次の順で進める。

```bash
python3 scripts/add_photographer.py spec.json --apply --scaffold
# --scaffold で photographers/<id>.html の安全な空骨格が生成される（既存は上書きしない）
# 出力された貼り付けカードと手作業チェックリストに従う
# EN新規ページは data/photographers-en-content.json に entry を入れ、build_photographers_en.py --slug <slug> で生成（以後の修正は EN HTML を直接編集）
python3 scripts/check_new_photographer.py --slug <slug>
python3 scripts/preflight.py
```

- `scripts/add_photographer.py` は card-data / supplement.js / スターマップ投入と、archive・年代・運動カードの貼り付け用HTML、手作業チェックリストを出す作業ナビ。危険な旧生成器は呼ばない。
- `--scaffold` は `photographers/<id>.html` の**安全な空骨格**を生成する（コピー元は `ansel-adams.html` 固定）。slug / canonical / hreflang / og:url / JSON-LD `Person.url` / title / h1 / hero名 / name / 生没年 / 国 / era など**機械的に確定できる項目だけ**置換し、本文・thesis・出典・cite・FIG・description本文・JSON-LD descriptionは生成しない（捏造回避）。Adams由来の本文/cite/REL/WORKS/書誌は残らない。**既存ページは上書きしない**。生成後 `check_new_photographer.py --slug <id>` を自動実行して未記入WARNを出す。手コピー時の置換ミス・残骸消し残しを無くすのが目的。
- JAページは参照実装 `photographers/ansel-adams.html` をコピーし、名前・slug・本文・thesis・出典・作品リンクを差し替える。`photographers/winogrand.html` は本文が単一「解説」節の薄い型なのでコピー元にしない。canonical / og:url / JSON-LD `Person.url` は必ず自slugに合わせる。JA JSON-LDは現状実体に合わせて `Person` 型を必須とし、WebPage / BreadcrumbList は必須にしない。
- `scripts/check_new_photographer.py --slug <slug>` は構造・cite整合・JSON-LD実体準拠の完成検査。通称slug可。`--strict-new` は不足を一部HARD化する明示検査用。`--all` は既存不具合の可視化用で、既存全ページを一括修正する指示ではない。
- `preflight.py` には同検査の touched-only 軽量版が入っている。常時preflightは明確な破損だけHARD、完成度不足はWARN中心。完成検査の本命は必ず `check_new_photographer.py --slug <slug>` で行う。
- 既存バグ（例: `sharon-lockhart` の dangling cite）は、そのページを修正する時に直す。無関係な新規追加作業では触らない。

## Content Preservation Guards

- `scripts/build_photographers_en.py` は**既存 EN ページへの書き込みを既定で拒否**し `🛑 REFUSED` を出す（既存ページは HTML 自身が正本）。解除は `ALLOW_EN_REBUILD=1` のみ。
- 新規作成時に効く content-loss guard は、再生成で thesis / §RELリンク / cite-N / FIG / lead が消えるページを検知し、そのページだけ上書きせず `🛑 SKIPPED` を出す。
  - 意図的に消す場合のみ `--force`。
  - 監査だけなら `--dry-run`。
- `scripts/check_content_loss.py` は読み取り専用の横断チェック。JA/EN両方で HEAD 比の出典・セクション・FIG・thesis・lead の減少を報告する。
  - `--strict` は消失時のみ非0終了。
  - 文面だけの変化は「事実すり替えの疑い」として警告される場合がある。警告は目視確認する。
- `scripts/en_entry.py <slug>` / `scripts/check_en_entry.py <slug>` は EN 写真家ページの対象slugだけを読む・検査するためのツール。通称slugも可（例: `atget` -> `eugene-atget`）。
- `scripts/preflight.py` と `.githooks/pre-push` は id重複、card-data重複、GA欠落、触ったEN slugの内容消失、EN keyword chip のリンク消失、JA/EN の §REL・本文節の非対称などを検査する。FAILなら push しない。緊急回避は `git push --no-verify`。
  - EN写真家: 触った `en/photographers/*.html` を baseline と比較し、本文・出典の消失、keyword chip のリンク退行、JA ページとの §REL・本文節の非対称を検知する。EN HTML の直接編集は通常手順なので警告しない。
  - EN国別: `data/country-pages.json` の主要情報消失をHARD、`en/countries/*.html` だけの変更を直接編集疑いWARNにする。
  - EN年代/運動: `data/taxonomy-en-content.json` のメタ・セクション消失をHARD、`en/eras/*.html` / `en/movements/*.html` だけの変更を直接編集疑いWARNにする。
  - ENアーカイブ: `card-data.json` のカード数・id・`nameEn` / `nameJa` / `href` 消失をHARD、`en/archive.html` だけの変更を直接編集疑いWARNにする。
  - 本文消失: `scripts/check_content_loss.py` を同じbaseline・`--strict`で実行して取り込む。写真家リーフ（JA + EN）の明確な本文消失（出典cite / 本文セクション / FIG / thesis / lead の減少）をHARD、構造不変のまま文面だけ変化した「書き換えの疑い」をWARNにする。JA写真家HTML（正本）の本文消失もpush前に自動ブロックされる。
  - SEO/不可視要素: 触った公開HTML（GAと同じ範囲）を baseline 比較し、baselineにあった canonical / JSON-LD / title / meta description / data-nosnippet の消失、または hreflang の減少をHARD。OGP/Twitter減・data-nosnippet部分減・新規ページのコア欠落をWARN。元から無いページ・新規ページはブロックしない（段階導入）。
  - JA写真家ページのSEO穴検知: `check_ja_seo_holes()` は、触った `photographers/*.html` だけを対象に、canonical / OGP / data-nosnippet / hreflang / meta description / JSON-LD が「元から無い・新規ページで付け忘れた」場合に WARN を出す。上のSEO消失ガードは「baselineにあった要素が消えた事故」をHARDで止めるものだが、`check_ja_seo_holes()` は穴検知専用で、pushをブロックしない。本文修正だけでSEO要素を消していない場合は鳴らないのが正常。
  - JA分類ページ本文消失: 触った `archive.html` / `eras/*` / `movements/*`（HTML正本）を baseline 比較し、`<main>`領域消失・`<h1>`消失・`pc-card`数の減少をHARD、section/リンク/data-nosnippet の減少をWARN。国別はJSON正本のため対象外。
- 新規JA写真家ページの最善手: 参照実装 `photographers/ansel-adams.html` を丸ごとコピーして、名前・本文・出典・作品リンクだけ差し替える。これで GA / canonical / hreflang / OGP / Twitter / meta description / JSON-LD / data-nosnippet が最初から入る。`photographers/winogrand.html` は薄い型なのでコピー元にしない。ゼロから組むとGA欠落はHARDブロック、残りのSEO穴はWARNになりやすい。
- `scripts/fill_seo_tags.py` は、既存JA写真家ページのSEO穴を本文・出典に触らず補う冪等フィクサー。`python3 scripts/fill_seo_tags.py` はdry-run、`--apply` で書き込み。補えるのは canonical / hreflang / data-nosnippet / OGP / Twitter。meta description本文とJSON-LDは捏造回避のため生成しないので、完成済みページからの移植または手作業で別途入れる。
- 新規clone / Codex環境では、最初に `bash scripts/setup_hooks.sh` を一度実行して `.githooks/pre-push` を有効化する。`core.hooksPath` はローカル設定なので、実行するまでpush前チェックは自動では走らない。
- 上記SEOガードは「baselineにあった要素が消える事故」を止めるもので、元から欠けている既存穴（例: JA hreflang）の検出・修正はしない。テンプレ差し替え時は別途確認する。

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
- 警告が出た場合は、意図した変更か、正本(JA HTML / EN HTML。写真家ページはどちらも HTML 自身)と一致しているか確認してから push する。

## 詳細仕様の参照先 — タスク開始前に該当ファイルを読む

| 触るもの / やること | 先に読むファイル |
|---|---|
| `photographers/*.html` の新規作成・本文修正・構造修正 | `docs/photographer-leaf-spec.md` |
| `countries/*.html` / `en/countries/*.html` | `docs/country-page-spec.md` |
| `new-design/index.html` / `index-v51.html` / `cards-archive.html` / `card-data.json` / カード CSS | `docs/card-design-system.md` |
| スクリプト実行・EN 写真家ページ編集・テンプレ移行・機械チェックの意味 | `docs/generators-and-guards.md` |
| Codex 並行作業・横断スクリプト・`overrides.js`・本文自動リンク/エイリアス | `docs/content-preservation.md` |

## General Style

- 既存の構造、CSS、コンポーネントをできるだけ再利用する。
- 大きなリファクタは依頼された場合のみ行う。
- 変更は最小差分にする。
- 写真的・批評的な意味を重視し、出典・引用は明記する。AIの主観は書かない。
- 渡されたHTML素材は、明示指示がない限り構造を流用しない。本文・見出し・出典・作品リンク・書誌・メタなど中身だけを既存テンプレへ流し込む。
- 本文があるページの見出しスタイルを維持する: h2=14px `#c8a96e`（アンバー）/ 本文内h3=1.02rem `#a6bfa4`（セージグリーン）/ 本文内リンクは青。変更は個別HTMLでなく共通CSS（`styles/photographer-page.css` 等）で行う。
