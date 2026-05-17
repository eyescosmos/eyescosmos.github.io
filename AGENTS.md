# Codex Project Rules

このリポジトリは写真史サイト「写真の座標 / Photo Coordinates」です。

## Critical Content Storage Rule

- 写真家の本文・解説を変更する場合は、必ず `data/photographer-essay-overrides.js` に書く。
- `photographers/*.html` と `en/photographers/*.html` は直接編集しない。
- `photographers/*.html` と `en/photographers/*.html` は `scripts/generate_photographer_pages.py` が毎回全上書き生成するファイル。
- HTMLへ直接書いた本文は、次回のジェネレータ実行で失われる。
- 過去にHTMLへ直接書かれた本文がジェネレータ再実行で上書きされ、14人分の解説が消失した。
- 写真家本文・解説の唯一の永続的な編集先は `data/photographer-essay-overrides.js`。
- ジェネレータを実行したあとは、変更された `photographers/*.html` と `en/photographers/*.html` もコミットに含める。生成結果がリポジトリ上の実体である。

## Workflow

- 本文・解説変更: `data/photographer-essay-overrides.js` を編集する。
- 生成: `scripts/generate_photographer_pages.py` を実行する。
- 確認: 対象の日本語・英語HTMLが期待通り生成されたか確認する。
- コミット: overrides JS と生成されたHTMLを一緒にコミットする。

## General Style

- 既存の構造、CSS、コンポーネントをできるだけ再利用する。
- 大きなリファクタは依頼された場合のみ行う。
- 変更は最小差分にする。
- 写真的・批評的な意味を重視し、出典・引用は明記する。
