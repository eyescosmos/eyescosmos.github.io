---
name: sync-english-page
description: 日本語ページで確定した変更を、対応する英語ページに最小差分で反映するときに使う。EN同期・英語版反映・英訳の依頼が対象。ページ種別ごとに正本（JSON/JA HTML）を経由して再生成する。
disable-model-invocation: true
---

# Sync English Page

日本語ページで追加・修正した内容を、対応する英語ページへ反映する。

## Goal
新規調査ではなく、既存の日本語内容をもとに英語ページを自然な英語へ更新する。

## 反映経路 — ページ種別ごとに正本を経由する（EN HTML 直接編集は禁止）

| 対象 | 編集する正本 | 再生成コマンド |
|---|---|---|
| EN写真家 `en/photographers/*.html` | `data/photographers-en-content.json`（`body_html` / `thesis_html` / `site_directory_html`） | `python3 scripts/build_photographers_en.py --slug <slug>` |
| EN年代・運動 `en/eras/*` `en/movements/*` | JA HTML が正本（EN文面は builder のデータ） | `python3 scripts/build_taxonomy_en.py --era <YYYY>` / `--slug <movement>` |
| EN国別 `en/countries/*` | `data/country-pages.json` | `python3 scripts/generate_country_pages_en.py --country <slug>` |
| ENアーカイブ `en/archive.html` | `archive.html`（JA正本） | `python3 scripts/build_archive_en.py` |

- EN HTML を直接編集しても再生成で消える。必ず正本を直して再生成する
- EN写真家の事実修正では、必要に応じて `data/photographer-essay-overrides.js` の `textEn` も同内容にそろえる
- 手書き維持ページ（例: lee-miller, shoji-ueda）はブラインド再生成禁止。迷ったら `--dry-run` で確認する

## 英訳スタイルの正本

**EN 本文を書く前に `translation-style.md` を読む。** Daisuke が使っている2段階の英訳指示
（Step 1 翻訳 / Step 2 校正）がそのまま入っている。冒頭に「このサイトで上書きする項目」があり、
内部リンクを `/en/` に差し替える点と、出典欄の class 名が JA と違う点はそこが優先。

## Workflow
1. 対象の日本語ページと対応する英語側の正本だけ確認する
2. `translation-style.md` を読み、文体・用語・禁止事項を把握する
3. 日本語ページで追加・変更されたセクションを特定する
4. 上の表に従い、英語側の正本の対応箇所にだけ反映して再生成する
5. 既存HTML構造、見出し階層、クラス名、デザインは維持する
6. EN写真家の場合は `python3 scripts/build_photographers_en.py --slug <slug> --dry-run` が `SKIPPED` しないことを確認する
7. 最後に変更ファイルと反映内容だけ短く報告する

## Rules
- リポジトリ全体を読まない
- 新しい調査はしない
- 日本語を機械的に直訳せず、自然な英語に整える
- 変更範囲は対象セクションのみに限定する
- 英語版でのみ必要な文法調整は行ってよい
- 既存のトーンを崩さない
