---
name: sync-english-page
description: 日本語ページで確定した変更を、対応する英語ページに最小差分で反映するときに使う。EN同期・英語版反映・英訳の依頼が対象。EN写真家・EN年代・EN運動は EN HTML 自身が正本なので直接編集し、EN国別・ENアーカイブだけ正本を経由して再生成する。
disable-model-invocation: true
---

# Sync English Page

日本語ページで追加・修正した内容を、対応する英語ページへ反映する。

## Goal
新規調査ではなく、既存の日本語内容をもとに英語ページを自然な英語へ更新する。

## 反映経路 — 対象で正本が違う — CRITICAL

**EN写真家・EN年代・EN運動は EN HTML 自身が正本＝直接編集して終わり。**
再生成する経路はもう存在しない（下の表）。EN国別・ENアーカイブだけが生成物で、
**こちらは出力HTMLを直接編集してはいけない**（再生成で消える）。

| 対象 | 正本 | やること |
|---|---|---|
| EN写真家 `en/photographers/*.html` | **HTML自身** | `en/photographers/<slug>.html` を**直接編集**。新規のみ `python3 scripts/import_chatgpt_photographer.py --slug <slug> --render-en EN.html --apply` |
| EN年代・運動 `en/eras/*.html` `en/movements/*.html` | **HTML自身**（2026-09-15〜） | 該当HTMLを**直接編集**。新規のみ `python3 scripts/build_taxonomy_en.py --era <YYYY>` / `--slug <movement>` |
| EN国別 `en/countries/*` | `data/country-pages.json` | JSON を直して `python3 scripts/generate_country_pages_en.py --country <slug>` |
| ENアーカイブ `en/archive.html` | `archive.html`（JA正本） | JA を直して `python3 scripts/build_archive_en.py` |

- **EN写真家・EN年代・EN運動を再生成しようとしないこと。** `build_photographers_en.py` は
  module-only で CLI を持たず、`build_taxonomy_en.py` は出力先が実在すれば `🛑 REFUSED` で拒否する。
  rollback は git で行う。
- **凍結EN JSON 3本（`data/archive/photographers-en-content.json` / `...-stage4.json` /
  `taxonomy-en-content.json`）は編集しない。** 読み取り専用アーカイブで preflight が HARD で止める。
- **JA を直したら EN も同じ構造にする。** 節や §REL を JA にだけ足すと preflight の
  日英対称性ガードが HARD で止める。

## 英訳スタイルの正本

**EN 本文を書く前に `translation-style.md` を読む。** Daisuke が使っている2段階の英訳指示
（Step 1 翻訳 / Step 2 校正）がそのまま入っている。冒頭に「このサイトで上書きする項目」があり、
内部リンクを `/en/` に差し替える点と、出典欄の class 名が JA と違う点はそこが優先。

## Workflow
1. 対象の日本語ページと対応する英語側の正本だけ確認する
2. `translation-style.md` を読み、文体・用語・禁止事項を把握する
3. 日本語ページで追加・変更されたセクションを特定する
4. 上の表に従う。EN写真家・EN年代・EN運動は EN HTML の対応箇所だけを直接編集する。EN国別・ENアーカイブは正本を直して再生成する
5. 既存HTML構造、見出し階層、クラス名、デザインは維持する
6. EN写真家の場合は `python3 scripts/check_en_entry.py <slug>` と `python3 scripts/preflight.py` で確認する
7. 最後に変更ファイルと反映内容だけ短く報告する

## Rules
- リポジトリ全体を読まない
- 新しい調査はしない
- 日本語を機械的に直訳せず、自然な英語に整える
- 変更範囲は対象セクションのみに限定する
- 英語版でのみ必要な文法調整は行ってよい
- 既存のトーンを崩さない
