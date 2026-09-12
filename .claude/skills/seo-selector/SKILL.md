---
name: seo-selector
description: 月1回のSEO選定を回す。検索データから「次に本文を厚くすべき写真家10名」を名指しし、検索ニーズと素材依頼文を言語化する。スケジュールタスクからの定期実行と、手動の「SEO選定を回して」の両方が対象。ページは書き換えない。
---

# SEO Selector

**このスキルはページを書き換えない。** 名簿とレポートを出すだけ。本文の更新は既存の
バッチ update 工程（`docs/importer-scaffold-inject-spec.md` §14）が別途行う。

設計の正本は `docs/seo-selector-spec.md`。データは**リポジトリ外**の
`~/Desktop/claude code/photography history/seo-watch/`。

## 手順

```bash
cd "/Users/aiharadaisuke/Desktop/claude code/broken picture"
PYTHONWARNINGS=ignore .venv/bin/python scripts/seo_fetch.py
PYTHONWARNINGS=ignore .venv/bin/python scripts/seo_select.py
```

1. `seo_fetch.py` でスナップショットを取る。**GSC は新旧2プロパティを毎回合算する**
   （旧 `eyescosmos.github.io` 側にもクリックが残っている。片方だけでは実態の半分）。
2. `seo_select.py` で名簿とレポートを生成する。計算はすべてスクリプト側。
3. レポートの「検索ニーズ」と「素材依頼文」だけを私が書く。**ここが唯一の判断部分。**
4. 判定が出ていれば、それを先に Daisuke へ伝える。

## 言語化のルール — レポートのこの部分だけを書く

名簿の各人について次を足す。数値とクエリはスクリプトが出しているので触らない。

- **検索ニーズを1〜2文。** クエリから読み取れることだけを書く。「作風を知りたい」ではなく
  「ライティングと構図という語が直接クエリに入っており、印象論ではなく手法の説明が求められている」
  のように、どのクエリからそう読んだのかが分かる書き方にする。
- **素材依頼文の下書き。** ChatGPT に渡して素材HTMLを作らせるための指示。厚くする観点を
  具体的に列挙する。英語クエリ主導なら「EN も同時に厚くする」と書く。
- 推測で事実を足さない。出典にない評価・年・URLを書かない。

## 判定の書き方

- `selection-log.json` の `actionDate` から28日経過したバッチだけが判定対象。
- **バッチ単位が主、個人単位は参考。** 1ページのクリックは1桁が多く、個人単位はノイズに埋もれる。
  個人で拾うのは 0→14 のような明確な立ち上がりだけ。
- **断定しない。** 「改善が確認できる」までにとどめ、「改善した」と書かない。
- 順位単独で判定しない。ページ平均順位はクエリ構成の変化で汚染される（2026-08-14 の実測）。
- 同じ層で3バッチ連続 neutral なら、その層の選定条件そのものを疑って報告する。

## やらないこと

- title / meta / OGP の一括改善を提案しない。**2026-08-14 の28日フル検証で効果なしと決着済み。**
- Google SERP を独自にスクレイピングしない。
- 認証情報を出力・コミットしない。
- `snapshots/` の既存ファイルを書き換えない。追記のみ。

## update を push した後にやること

1. `python3 scripts/indexnow_submit.py --since 'origin/main@{1}'`
   **日本語パスの URL は静かに落ちる。** パーセントエンコードした URL を `--urls` で個別送信する。
2. `selection-log.json` の `actionDate` に push した日、`reviewDueDate` にその28日後を入れる。
   ここが次回の判定の起点になる。
3. 実測を `docs/importer-run-log.md` に記録する。
