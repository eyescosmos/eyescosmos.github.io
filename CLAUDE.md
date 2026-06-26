# Project rules

このリポジトリは写真史を扱うWebサイト。世界・日本・各国の写真家、運動、思想、時代背景、
関連性を整理し、写真史をたどれるようにすることが目的。

このファイルは**常時ロードされるコア**。タスク種別ごとの詳細仕様は `docs/` に分けてあり、
**該当タスクを始める前にそのファイルを読む**（下の「詳細仕様の参照先」を参照）。

## JA/EN 正本と生成ルール — 最優先 — CRITICAL

このサイトは JA と EN で正本(source of truth)が違う。古い overrides 前提の指示と衝突する場合は、このセクションを優先する。

### 写真家ページ
- JA 写真家ページ `photographers/*.html` は **HTML 自身が正本**。本文・thesis・§REL・出典・書籍欄を手編集してよく、永続する。
- `scripts/generate_photographer_pages.py` は実行禁止。旧デザインを生成し、JA ページを旧構造と言語トグル破損へ巻き戻す。物理ガードを解除しない。
- EN 写真家ページ `en/photographers/*.html` は **出力物**。直接手編集しても `scripts/build_photographers_en.py` の再生成で消える。
- EN 写真家本文の正本は `data/photographers-en-content.json`。`body_html` が本文、`thesis_html` が thesis、`site_directory_html` が Related people / Related movements。
- EN 本文の事実を直す場合は、`data/photographers-en-content.json` の該当 `body_html` と、必要なら旧経路の `data/photographer-essay-overrides.js` の `textEn` を両方そろえる。片方だけだと不整合が残る。
- EN の本文 / thesis / §REL を直すときは EN HTML を触らず、正本データを直して `python3 scripts/build_photographers_en.py --slug <slug>` で再生成する。
- EN ページを修正・追加・新規作成したら、作業終了前に必ず `data/photographers-en-content.json`（同slugがあれば `data/photographers-en-stage4.json` も）を確認し、`python3 scripts/build_photographers_en.py --slug <slug> --dry-run` が `SKIPPED` しないことを確認する。EN HTMLだけの差分で終えない。
- 詳細な EN 編集フロー・手書き保持ルールは `docs/generators-and-guards.md`。

### その他の正本
- アーカイブ: `archive.html` が JA 正本。`en/archive.html` は `scripts/build_archive_en.py` で生成。`scripts/generate_archive_pages.py` は実行禁止。
- 国別ページ: `data/country-pages.json` が正本。`scripts/generate_country_pages.py` / `scripts/generate_country_pages_en.py` で生成。スコープフラグ必須（`--country <slug>` 通常 / `--all` 全生成）。無指定は拒否。
- 年代・運動ページ: JA HTML が正本。EN は `scripts/build_taxonomy_en.py` で生成。スコープフラグ必須（`--era <YYYY>` / `--slug <movement>` 通常 / `--all` 全生成）。無指定は拒否。写真家1人追加で `--all` は不要（`docs/generators-and-guards.md`「フルリビルド・ガード」）。

### 実務ルール
- 事実修正（生没年・地名・書名・出版社・年・ISBN・URLなど）は、出力HTMLだけでなく正本へ入れる。捏造禁止・出典準拠。
- `scripts/link_country_keywords.py` など横断スクリプトを回したら、`git status` / `git diff` で対象外ページの巻き込みを確認し、混入差分は revert する。二重国籍の国名が畳まれていないかも確認する。
- TOP12 ハードコードカード（`pc-top` / `idx` / `pc-top--XXX`）、フィルター/ソートUI、カードJSは依頼がない限り触らない。カードの正は `cards-archive.html` / `card-data.json`。
- テンプレ差し替え・デザイン移行時は GA(`G-2VRTV8BZEJ`) / canonical / hreflang / OG / JSON-LD / `data-nosnippet` を必ず引き継ぐ（詳細 `docs/generators-and-guards.md`）。

### push 前チェック
```bash
git pull origin main
python3 scripts/check_content_loss.py
python3 scripts/preflight.py
git diff origin/main
```
警告が出たら、意図した変更か、正本（JA HTML / `data/photographers-en-content.json` / `data/photographer-essay-overrides.js`）と一致しているか確認してから push する。
push 前には必ず `git status --short` と `git diff --name-only` / `git diff --stat` も確認し、依頼対象外ファイルの巻き込み、生成前状態への巻き戻り、本文・構造・リンク・出典の消失、意図しない差分がないことを確認する。未追跡ファイルは依頼対象でない限り stage しない。

機械チェック（preflight / pre-push フック）が多くの事故を自動ブロックする。仕組みの詳細は `docs/generators-and-guards.md`。

## 詳細仕様の参照先 — タスク開始前に該当ファイルを読む

| 触るもの / やること | 先に読むファイル |
|---|---|
| `photographers/*.html` の新規作成・本文修正・構造修正 | `docs/photographer-leaf-spec.md`（作業手順・リーフ型構造基準・thesis 断定度基準・見出し語ルール） |
| `countries/*.html` / `en/countries/*.html` | `docs/country-page-spec.md`（ハブ型 v5.1 構造基準） |
| `new-design/index.html` / `index-v51.html` / `cards-archive.html` / `card-data.json` / カード CSS | `docs/card-design-system.md`（変更禁止項目・スタイル割り振り・CSS体系） |
| スクリプト実行・EN 写真家ページ編集・テンプレ移行・機械チェックの意味 | `docs/generators-and-guards.md` |
| Codex 並行作業・横断スクリプト・`overrides.js`・本文自動リンク/エイリアス | `docs/content-preservation.md` |

新規 JA 写真家ページの最善手＝参照実装 `photographers/ansel-adams.html` を丸ごとコピーして
名前・本文だけ全置換する（SEO 一式と本文レイアウトの正の型が最初から入る）。詳細は
`docs/generators-and-guards.md`。

## Skill priority
- 既存ファイルの形式よりskill.mdの指示を優先すること

## Working style
- 今回の作業に必要な最小限のファイルだけ読む
- リポジトリ全体を最初から走査しない
- 既存の構造、CSS、コンポーネントをできるだけ再利用する
- 大きなリファクタは依頼された場合のみ行う
- 最小差分で修正する
- 変更後の報告は簡潔にする
- 写真家の追加・修正、およびその他のページ修正があったときは、常に実測して `docs/importer-run-log.md` に記録する（客観項目は作業側、wall-time は Daisuke 記入。写真家以外は軽量行で可）。詳細は同ファイル冒頭と `AGENTS.md`「実測ログ — Required」

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
  事実検証）は `docs/photographer-leaf-spec.md`「新規ページ作成時の入力素材の扱い」を参照。

## Design invariants
- 本文があるページの h2 / セクションタイトルは、font-size: 14px、color: #c8a96e（アンバー）を維持する
- 本文内の h3 / 表現解説内の小見出しは、font-size: 1.02rem（約16.3px）、color: #a6bfa4（セージグリーン）を維持する
- 本文内リンクは青色で統一し、通常時・hover時ともアンバーや本文色へ戻さない
- これらの表示ルールを変更する場合は、個別HTMLの本文ではなく共通CSS（例: styles/photographer-page.css、styles/taxonomy-page.css）と必要な生成元を優先して調整する

## Writing principles / Content style
- AIの主観は書かない。出典・引用は明記する
- 文章は簡潔で説明的にする。デザインと文体を維持する
- 生没年や出身地だけでなく、写真的・批評的な意味を重視する
- SEOを意識しても不自然なキーワード追加はしない
- 見出しは内容を正確に表す
- 外部リンクだけで終わらせず、短くても自前の要約を書く
- thesis の断定度・写真家ページの構成・許可見出し語は `docs/photographer-leaf-spec.md`

## Content consistency
- アーカイブページと写真家の個別ページで同じ解説を持つ場合は、内容の整合性を保つ
- どちらか一方の解説を更新した場合は、対応するもう一方のページにも同じ変更を適用

## Research workflow
- 小規模な調査は main conversation で行う
- 調査量が大きい場合は、調査だけを skill / subagent に委譲して要点だけ返す
- サイト掲載用の最終文面は main conversation で整える

## English sync policy
- 日本語ページで内容を確定してから英語ページへ反映する
- 英語ページ反映時は、新規調査ではなく既存の日本語内容を自然な英語に整える
- 英語ページの変更は対象セクションのみに限定する
