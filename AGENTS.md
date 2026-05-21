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
- 例外的に復元作業などでHTML側に本文が残っている場合でも、ジェネレータを回す前に同じ本文が `data/photographer-essay-overrides.js` に入っているか必ず確認する。
- `scripts/generate_photographer_pages.py` 実行後、対象外の写真家ページで本文、外部リンク、出典が「準備中」へ戻る差分が出た場合は、その生成結果を採用しない。対象外HTMLは復元し、本文をoverridesへ移してから再生成する。
- アフィリエイト、ナビゲーション、SEOなど本文以外の小変更でも、ジェネレータ実行で本文が消えないか `git diff` で必ず確認する。
- Claude Codeなど他エージェントの更新を取り込む前に、まず `git fetch` でリモート差分を取得し、`git diff HEAD..origin/main` などで取り込み予定の変更を確認する。写真家ページや生成元で、本文・見出し・外部リンク・出典・Amazonリンクが消える、または「準備中」へ戻る差分がないことを確認してから `git pull --rebase` する。消失が疑われる場合はpullを止め、差分内容を報告する。

## Workflow

- 本文・解説変更: `data/photographer-essay-overrides.js` を編集する。
- 生成: `scripts/generate_photographer_pages.py` を実行する。
- 確認: 対象の日本語・英語HTMLが期待通り生成されたか確認する。
- コミット: overrides JS と生成されたHTMLを一緒にコミットする。

## Photographer Page Integrity Rules — CRITICAL

過去に、写真家ページで本文混入と誤リンクが発生した。再発防止のため、写真家ページやジェネレータを触る場合は必ず以下を守る。

- 本文混入の主因は `data/photographer-essay-overrides.js` のエントリ上書き・復元ミス。例: `richard-avedon` の `textEn` に Irving Penn 本文が入った。
- overrideを追加・復元するときは、対象ID、`leadJa/leadEn`、`textJa/textEn`、`citations/citationsEn/citationsJa`、`links`、`works` が同じ作家に対応しているか確認する。
- 既存エントリを丸ごと置換する場合は、`...current` で既存の本文・リンク・作品・出典を保持するか、置換する全フィールドを明示的に確認する。本文だけ直すつもりで `links` や `works` を消さない。
- 英語だけ出典を変える場合は `citationsEn` を使い、共通 `citations` を不用意に上書きしない。日本語本文の注番号を壊す可能性がある。
- Avedon/Penn、Adams/Weston、Sugimoto/Moriyama、Avedon/Leibovitz など近い作家を扱うときは、比較文脈と本文混入を区別する。別作家のBiography・Expression/method・Criticism・Photobooks・Sourcesがまとまって入っていたらFAIL。
- 生成後は少なくとも対象ページで、H1、title、lead、Biography冒頭、Photobooks見出し、Sourcesが同じ作家に対応しているか確認する。

### Auto-linking rules — CRITICAL

- 誤リンクの主因は、作品リンク自動化が全作家横断の作品名辞書として本文へ適用されていたこと、および `S` / `LS` など短すぎる作品名・別名を拾っていたこと。
- 本文中の作品自動リンクは、そのページ自身の `works` に登録された作品だけを対象にする。別作家の `works` をグローバルに本文へ適用しない。
- 1〜2文字のASCII英数字タイトル・別名（例: `S`, `LS`）は本文自動リンク対象にしない。作品欄のchip-linkとして表示するのはよいが、本文内の単語の一部へリンクさせない。
- 汎用語の作品名（例: `The Family`）は、必要なら `autoLink: false` を付け、作品欄には残して本文自動リンクから除外する。`The Family of Man` のような別語句の一部にリンクさせない。
- `scripts/generate_photographer_pages.py` の `should_skip_alias_boundary()` と `KATAKANA_RE` 境界チェックは変更しない。純カタカナの短いエイリアスが、別のカタカナ語の語中へ誤リンクされるのを防ぐために必要。
- `data/photographers-manual-additions.js` の `PHOTOGRAPHER_LINK_ALIASES` にある `'ペン': 'irving-penn'` は削除しない。AvedonページなどでPennの略称として正当に使われるため、削除ではなく境界チェックで誤マッチを防ぐ。
- 短いカタカナエイリアス（例: `ペン`）を追加・変更した場合は、`ペンシルバニア`、`スペンサー`、`コペンハーゲン`、`サーペンタイン` のような語中リンクが起きていないか確認する。平仮名助詞が続く正当な略称リンクとは区別する。
- 生成後は `scripts/check_photographer_link_integrity.py` を実行し、1文字外部リンク、Avedon/Penn Biography混入、Photobooks見出し不一致を確認する。
- 追加で、`photographers/` と `en/photographers/` に `museumangewandtekunst.de` への1文字リンク、`>S</a>`、単語途中リンクが残っていないか確認する。
- canonical / hreflang / alternate / JSON-LD / `data-nosnippet` は本文やリンク修正で壊さない。生成後のdiffでSEOタグや構造タグに意図しない差分がないか確認する。

## General Style

- 既存の構造、CSS、コンポーネントをできるだけ再利用する。
- 大きなリファクタは依頼された場合のみ行う。
- 変更は最小差分にする。
- 写真的・批評的な意味を重視し、出典・引用は明記する。
