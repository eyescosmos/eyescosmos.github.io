# 写真家個別ページ 編集スキル

CLAUDE.md の構造基準と合わせて参照すること。
**CLAUDE.md と本ファイルが矛盾する場合は、本ファイルを優先する。**

## さらに読む（further-section）の仕様

「写真集」「方法論・技術書」「関連データベース・アーカイブ」の区分で整理する。

### 各書籍に必須の記載情報

| 項目 | 内容 |
|------|------|
| 書名 | 原題または邦題（汎用タイトル禁止）|
| 著者・編者 | 本名を正確に記載 |
| 出版社 | 正式名称 |
| 出版年 | 西暦4桁 |

### 汎用タイトル禁止

作家名＋汎用語の組み合わせによるタイトルは使わない。

- NG: 「杉本博司 写真集」「アダムスの作品集」「写真家名 Works」
- OK: 「Time Machine」「Theaters」「In Praise of Shadows」

既存の書籍情報が汎用タイトルになっている場合は、正確なタイトルに修正する。
正確なタイトルが不明な場合は Daisuke に確認する。

### 複数冊掲載が標準

- 写真集・著作は1冊のみ掲載することを避け、代表的な複数冊を掲載する
- 既存の書籍リストを修正する際に、冊数を減らさない
- 削除が必要な場合は Daisuke に確認してから行う

### Amazon リンク

- Amazon アフィリエイトリンクは Daisuke が用意した URL のみ使用する
- URL を推測・生成しない（存在しないページや誤品へのリンクになるため）
- Amazon リンクを掲載する場合は必ずアフィリエイト表示を付ける
- Amazon リンクが未提供の場合は、テキストのみで書籍情報を記載する（空のリンクは作らない）

### 書籍カードの HTML 構造（必須形式）

各書籍カードは以下の構造を厳守する：

```html
<div class="book">
  <div class="book-title">具体的な書籍タイトル</div>
  <div class="book-meta">著者・編者 / 出版社 / 出版年</div>
  <div class="book-note">書籍の内容と意義を 1〜2 文で具体的に</div>
  <a class="chip-link amazon-cta" href="https://amzn.to/XXXXX"
     target="_blank" rel="noopener sponsored">Amazon で見る ↗</a>
  <span class="affiliate-disclosure">※アフィリエイトリンクを含みます</span>
</div>
```

クラス名は固定（`book`, `book-title`, `book-meta`, `book-note`,
`chip-link amazon-cta`, `affiliate-disclosure`）。`data-affiliate-section`
属性は親 `<section>` に付与する。

複数冊掲載する場合は `<div class="book">` を必要な冊数だけ繰り返す。
各 `.book` は独立し、ラッパー要素で囲まない。

### book-note の禁止表現

以下のような中身のない記述は禁止：
- 「Amazon で確認できます」
- 「詳細は Amazon でご覧ください」
- 「代表的な写真集です」
- 「主要な作品集」
- 「○○の写真集」（書名の言い換えにすぎないもの）

book-note には必ず以下のいずれかを含める：
- 書籍の収録内容（どの連作・どの時期の作品か）
- 書籍の編集方針（誰が編集・寄稿しているか、どの展覧会と対応するか）
- なぜこの写真家を理解するうえで重要か（方法論の出発点、回顧の決定版など）

具体例（`ansel-adams.html`, `hiroshi-sugimoto.html` より）：
- 「ヨセミテからマンザナーまで、アダムスの代表作を網羅する定番。ゾーンシステムとアメリカ西部の風景表現を一冊で押さえられる。」
- 「50 年の制作を 11 シリーズで網羅した大型回顧展カタログ。〈ジオラマ〉〈海景〉〈劇場〉から〈Lightning Fields〉まで主要連作の全貌を、Geoffrey Batchen・Edmund de Waal らの執筆陣のテキストとともに収録。」

### 関連データベース・アーカイブ欄の仕様

`<ul class="further-links">` の中に `<li>` を必要な数だけ並べる。
各リンクは以下の形式：

```html
<li><a href="https://..." target="_blank" rel="noopener">サイト名 —
    ページタイトル</a>（このリンク先で得られる情報の1行解説）</li>
```

リンク先として推奨されるもの：
- 作家公式サイト
- 美術館・財団のアーカイブページ（MoMA, The Met, SFMOMA, Tate,
  Aperture, ICP, George Eastman Museum, Center for Creative Photography,
  Library of Congress, MFA Boston, Guggenheim など）
- 信頼できるインタビュー・動画（Art21, Time Sensitive, Louisiana Channel など）
- 写真家を扱うギャラリーの作家ページ（Fraenkel, Pace, Gagosian,
  David Zwirner など、第一線の現代美術ギャラリーに限る）

避けるべきリンク先：
- Wikipedia
- ブログや個人サイトの紹介記事
- リンク切れの可能性が高い旧 URL

関連データベース欄は出典セクションと役割が異なるため、内容が一部
重複してもよい（出典は本文の典拠、データベースは読者ナビゲーション）。
