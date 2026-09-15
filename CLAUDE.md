# Project rules

このリポジトリは写真史を扱うWebサイト。世界・日本・各国の写真家、運動、思想、時代背景、
関連性を整理し、写真史をたどれるようにすることが目的。

このファイルは**常時ロードされるコア**。タスク種別ごとの詳細仕様は `docs/` に分けてあり、
**該当タスクを始める前にそのファイルを読む**（下の「詳細仕様の参照先」を参照）。

## 絶対禁止 — NEVER — 最初に読む

1. **`scripts/generate_photographer_pages.py` は削除済み**（2026-09-15・§12.3）。旧デザインを生成し JA ページを旧構造と言語トグル破損へ巻き戻す実行禁止スクリプトだった。**復活させない。** 中身を見たいときは `git show legacy-generators-2026-09-15:scripts/generate_photographer_pages.py`。
2. **`scripts/generate_archive_pages.py` も削除済み**（同上）。JA 写真家ページ・アーカイブの正本は HTML 自身なので、生成し直す経路はもう無い。
3. **既存の `en/photographers/*.html` を再生成しない**。ENページは **HTML 自身が正本**（2026-09-13〜）。`build_photographers_en.py` は **EN描画エンジンのモジュール**であり CLI ではない（直接実行は常に非0終了）。**新規作成は EN HTML を importer で直接生成する（`--render-en` 相当）。JSON から再生成する経路はなく、rollback は git で行う。** 詳細 `docs/en-html-canon-migration.md` §11。
4. **生成物が正本でないサーフェス（国別 / ENアーカイブ / コロフォン / AI開示）で、事実修正を出力HTMLだけに入れない**。必ず正本へ入れる（再生成で誤情報が復活するため）。JA写真家ページ・EN写真家ページ・**EN年代/運動ページ**は HTML 自身が正本なので、この項の対象外。
5. **捏造しない**。出典にない評価・書誌・年・URL・Amazonリンクを推測で作らない。出典準拠。
6. **国別・年代・運動の生成スクリプトをスコープフラグ無指定で実行しない**（無指定はガードが拒否）。写真家1人追加で `--all` は不要（`docs/generators-and-guards.md`「フルリビルド・ガード」）。
7. **AI開示ブロック（`<!-- AI-DISCLOSURE -->` で括られた3行＋短縮版）を個別HTMLで直さない**。正本は `scripts/ai_disclosure.py`。直しても preflight の `check_ai_disclosure()` が HARD FAIL で止める。文面変更は正本を直して `python3 scripts/inject_ai_disclosure.py --all`。
8. **TOP12 ハードコードカード（`pc-top` / `idx` / `pc-top--XXX`）、フィルター/ソートUI、カードJSは依頼がない限り触らない**。カードの正は `cards-archive.html` / `card-data.json`。
9. **凍結EN JSON 3本（`data/archive/photographers-en-content.json` / `data/archive/photographers-en-stage4.json` / `data/archive/taxonomy-en-content.json`）を編集しない**。読み取り専用アーカイブで、preflight が変更を HARD で止める（解除は `ALLOW_EN_JSON_ARCHIVE_WRITE=1`・移行監査と緊急rollbackのみ）。EN ページの正本は `en/photographers/*.html` と `en/movements/*.html` / `en/eras/*.html`。
10. **既存の `en/movements/*.html` / `en/eras/*.html` を再生成しない**（2026-09-15〜）。`build_taxonomy_en.py` は**新規ページ専用**で、出力先が実在すれば `🛑 REFUSED` で拒否する（解除は `ALLOW_TAXONOMY_REBUILD=1` のみ・`--dry-run` でも解除されない）。修正は EN HTML を直接編集する。詳細 `docs/post-migration-cleanup-plan.md` §10。

## 正本(source of truth)マトリクス — CRITICAL

JA と EN で正本が違う。古い overrides 前提の指示と衝突する場合はこの表を優先する。

| サーフェス | 正本 | 生成コマンド | 備考 |
|---|---|---|---|
| JA写真家 `photographers/*.html` | **HTML自身** | なし（手編集・永続） | 本文・thesis・§REL・出典・書籍欄を手編集してよい |
| EN写真家 `en/photographers/*.html` | **HTML自身** | 新規のみ `python3 scripts/import_chatgpt_photographer.py --slug <slug> --ja JA.html --en EN.html --apply` | JA と同じく直接編集してよい。既存ページへの上書きは常に拒否される |
| ENアーカイブ `en/archive.html` | `archive.html`（JA正本） | `python3 scripts/build_archive_en.py` | |
| 国別 JA/EN | `data/country-pages.json` | `generate_country_pages.py` / `generate_country_pages_en.py`。`--country <slug>`（通常）/ `--all`（全生成） | スコープフラグ必須 |
| EN年代・運動 `en/eras/*.html` `en/movements/*.html` | **HTML自身** | 新規のみ `python3 scripts/build_taxonomy_en.py --slug <movement>` / `--era <YYYY>` | JA・EN写真家と同じく直接編集してよい。既存ページへの上書きは常に拒否される（`ALLOW_TAXONOMY_REBUILD=1` の緊急rollback を除く） |
| AI開示ブロック（全ページ末尾） | `scripts/ai_disclosure.py` | `python3 scripts/inject_ai_disclosure.py --all`（`--only <path>` で1枚） | 個別HTMLを直接編集しない。文面はこのモジュールが正本 |
| コロフォン `/colophon` · `/en/colophon` | `scripts/build_colophon.py` | `python3 scripts/build_colophon.py` | 実体は `colophon/index.html` / `en/colophon/index.html` |
| カード枚数表示（archive hero・「表示中 N / M」・トップ/archive の meta 枚数） | `card-data.json` | `python3 scripts/sync_card_counts.py`（`--check` で検査のみ） | 手で数字を打ち直さない。`add_photographer.py --apply-surfaces` 後に自動実行。preflight `check_card_counts()` が HARD FAIL |

### EN写真家ページの編集手順

- **既存ページの修正**：`en/photographers/<slug>.html` を直接編集して終わり。JSON は直さない。
  builder も走らせない（走らせても既定で拒否される）。JA と同じ「直して終わり」。
- **新規ページの作成**：入口が2つある。**JA ページが既にあるかで選ぶ**。

  | 状況 | コマンド |
  |---|---|
  | **JA も EN もこれから**（素材2本が揃っている） | `python3 scripts/import_chatgpt_photographer.py --slug <slug> --ja JA.html --en EN.html --apply`（JA→EN の順に両方できる） |
  | **JA は既にある。EN だけ足す**（`add_photographer.py` の後段など） | `python3 scripts/import_chatgpt_photographer.py --slug <slug> --render-en EN.html --apply` |

  上を JA 既存に対して使うと `--force` が要る（＝JA を書き直してしまう）ので、
  **JA ができているなら必ず `--render-en` を使う**。
  どちらも EN 出力先が既に存在すれば常に拒否され、`--force` でも上書きしない。
  EN scaffold は同一人物の JA ページなので、**JA が無いと EN は描けない**（dry-run はその旨を表示して正常終了）。
- **`data/photographer-essay-overrides.js` の `textJa` / `textEn` は撤去済み**（2026-09-15・446プロパティ／−2.22MB）。
  読み手が実行禁止の旧ジェネレータ2本と `check_texten_completeness.py` だけの死蔵データだった。
  **そろえる必要はなく、書き戻さないこと。** `check_texten_completeness.py` も同時に削除した。
  **生きているのは `leadEn` / `leadJa`（265件）で、これは消さない**: `build_archive_en.py` が
  `en/archive.html` のカード lede の最優先ソースとして読み、`relations.html` / `en/relations.html` の2枚が
  `global-search.js` 経由で実行時に読む。
- 検査は `python3 scripts/check_en_entry.py <slug>`（JSON closure は既存ページでは実施しない）と
  `python3 scripts/preflight.py`。preflight は EN HTML を正本として次を見る:
  keyword chip のリンク保存 / JA・EN の §REL 対称性 / JA・EN の本文節の対称性。
- **JA を直したら EN も同じ構造にする**。節を足した・§REL を足したのに EN を忘れると preflight が HARD で止める。
- 移行の背景と残りフェーズは `docs/en-html-canon-migration.md`。

### 横断スクリプト後の確認
- `scripts/link_country_keywords.py` など横断スクリプトを回したら、`git status` / `git diff` で対象外ページの巻き込みを確認し、混入差分は revert する。二重国籍の国名が畳まれていないかも確認する。

### テンプレ差し替え・デザイン移行
- GA(`G-2VRTV8BZEJ`) / canonical / hreflang / OG / JSON-LD / `data-nosnippet` を必ず引き継ぐ（詳細 `docs/generators-and-guards.md`）。

## push 前チェック — Required

```bash
git pull origin main
python3 scripts/check_content_loss.py
python3 scripts/preflight.py
git diff origin/main
```

- 警告が出たら、意図した変更か、正本（JA HTML / EN HTML。写真家ページはどちらも HTML 自身）と一致しているか確認してから push する。
- 必ず `git status --short` と `git diff --name-only` / `git diff --stat` も確認し、次がないことを確かめる: 依頼対象外ファイルの巻き込み / 生成前状態への巻き戻り / 本文・構造・リンク・出典の消失 / 意図しない差分。
- 未追跡ファイルは依頼対象でない限り stage しない。
- 機械チェック（preflight / pre-push フック）が多くの事故を自動ブロックする。仕組みの詳細は `docs/generators-and-guards.md`。

## 詳細仕様の参照先 — タスク開始前に該当ファイルを読む

| 触るもの / やること | 先に読むファイル |
|---|---|
| `photographers/*.html` の新規作成・本文修正・構造修正 | `docs/photographer-leaf-spec.md`（作業手順・リーフ型構造基準・thesis 断定度基準・見出し語ルール） |
| `countries/*.html` / `en/countries/*.html` | `docs/country-page-spec.md`（ハブ型 v5.1 構造基準） |
| `new-design/index.html` / `index-v51.html` / `cards-archive.html` / `card-data.json` / カード CSS | `docs/card-design-system.md`（変更禁止項目・スタイル割り振り・CSS体系） |
| スクリプト実行・EN 写真家ページ編集・テンプレ移行・機械チェックの意味 | `docs/generators-and-guards.md` |
| Codex 並行作業・横断スクリプト・`overrides.js`・本文自動リンク/エイリアス | `docs/content-preservation.md` |
| **ChatGPT新素材で写真家をバッチ update する（Opus監督/Codex実装）** | `docs/importer-scaffold-inject-spec.md` §14「バッチ update のキックオフ定型」（既知WARN許可リスト・Related削除SKIPの常設承認条件・既存維持フィールド・**素材に生没年が無ければ調べて入れる**・**パイロット1名で回す検証項目**）。**最初のプロンプトにこれを入れないと往復が増える** |
| ★★**移行後はじめて写真家を update / 追加する**（2026-09-15 以降の初回だけ・**次の写真家作業がこれ**） | `docs/en-html-canon-migration.md` **§13.10** ＋ `docs/next-photographer-batch.md`。移行後の経路は fixture でしか通していない（**新規追加は本番未検証**）ので、**実素材の初回だけ**チェックリストを回して `docs/importer-run-log.md` に実測を残す。**次は新規6名で確定**（Daisuke 2026-09-15）＝6名とも未検証の経路に乗る。**型＝パイロット1名→監査→残り5名一括**。通れば初回扱いは終了 |
| EN の**アーカイブ / 国**ページ（写真家・年代・運動ページではない） | `docs/en-html-canon-migration.md` **§14**。**この2つは正本が生成元のまま**（アーカイブ＝JA `archive.html`、国別＝`data/country-pages.json`）。EN 出力HTMLだけ直すと再生成で消える（絶対禁止4番）。**EN年代・運動は 2026-09-15 に HTML 自身が正本へ昇格した**（`docs/post-migration-cleanup-plan.md` §10）|
| ★**移行後の総ざらい（残骸の掃除・写真家以外の正本化）を始める** | `docs/post-migration-cleanup-plan.md`（**設計から始める引き継ぎ**。再生成ドリフトの実測・3クラスの切り分け・未決の論点4つ・作業規律）。**着手前に §2 の実測と §4 の論点を読む** |

新規 JA 写真家ページの最善手＝参照実装 `photographers/ansel-adams.html` を丸ごとコピーして
名前・本文だけ全置換する（SEO 一式と本文レイアウトの正の型が最初から入る）。詳細は
`docs/generators-and-guards.md`。

## Skill priority
- スキルは `.claude/skills/` にある（`write-photographer-section`＝写真家解説の執筆 / `sync-english-page`＝JA→EN反映）。
- 既存ファイルの形式より SKILL.md の指示を優先すること。

## Working style
- 今回の作業に必要な最小限のファイルだけ読む。リポジトリ全体を最初から走査しない
- 既存の構造、CSS、コンポーネントをできるだけ再利用する
- 大きなリファクタは依頼された場合のみ行う。最小差分で修正する
- 変更後の報告は簡潔にする
- 写真家の追加・修正、およびその他のページ修正があったときは、常に実測して `docs/importer-run-log.md` に記録する（客観項目は作業側、wall-time は Daisuke 記入。写真家以外は軽量行で可）。詳細は同ファイル冒頭と `AGENTS.md`「実測ログ — Required」

## 渡された素材（HTML 含む）の扱い — CRITICAL

Daisuke から渡された素材が HTML ファイル（ChatGPT 等の生成物を含む）であっても、
新規ページ作成・本文の追加／修正のいずれでも:

- **明示の指示がない限り、その HTML の構造・デザイン・サイドバー・chrome・節構成は一切流用しない**。
- 中身の要素（本文テキスト・見出し・出典・作品リンク・書誌・メタ等）**だけ**を抽出し、編集対象の既存ページの構造／標準テンプレへ流し込む。
- 既存ページの本文を追加／修正する場合も同じ。渡された HTML の構造に合わせず、**既存ページの構造・クラス・リンク慣習に合わせて中身だけ差し込む**。
- 構造を採用するのは「この構造のまま使って」と**明示された場合のみ**。
- 目的：作業の最小化。渡された構造を後から直す手間を発生させない。
- 写真家ページ固有の詳細（捨てる要素・標準サイドバー形・本文リンク化・素材の事実検証）は `docs/photographer-leaf-spec.md`「新規ページ作成時の入力素材の扱い」。

## Design invariants
- 本文があるページの h2 / セクションタイトル: `font-size: 14px`、`color: #c8a96e`（アンバー）を維持
- 本文内の h3 / 表現解説内の小見出し: `font-size: 1.02rem`（約16.3px）、`color: #a6bfa4`（セージグリーン）を維持
- 本文内リンクは青色で統一。通常時・hover時ともアンバーや本文色へ戻さない
- これらの表示ルールを変更する場合は、個別HTMLの本文ではなく共通CSS（例: `styles/photographer-page.css`、`styles/taxonomy-page.css`）と必要な生成元を優先して調整する

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
