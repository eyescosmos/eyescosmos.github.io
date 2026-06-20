# カードデザインシステム（v4/v5.1）と新デザインページ編集ルール

**いつ読むか:** `new-design/index.html` / `index-v51.html` / `cards-archive.html` /
`card-data.json` / カード CSS を触るとき。

---

## 新デザインページ（new-design/）の編集ルール — CRITICAL

### 基本原則：依頼された箇所以外は変更しない

`new-design/index.html` をはじめとする新デザインページを編集する際は、
**依頼された修正のみを行い、それ以外の箇所には一切触れない。**

リンク追加を依頼された場合 → href 属性のみ変更。他は変えない。
テキスト修正を依頼された場合 → そのテキストのみ変更。他は変えない。

### 変更禁止項目（依頼があっても勝手に触らない）

以下は「古い・間違い・改善できる」と見えても変更してはならない：

1. **TOP12カードHTML** — `pc-top`・`idx`・`pc-top__art`・`pc-top--XXX`クラス
   （JavaScript がアーカイブ版で自動上書きするため、ハードコード値は問題ない）

2. **フィルター・ソートUI** — `.pill[data-filter]`・`#nd-sort-btn`・`#nd-sort-dropdown`・
   `.sort-option[data-sort]` の構造・属性・テキスト

3. **カード制御JavaScript** — `ndRender()`・`archiveCardMap`・`ND_TOP12_NAMES`・
   `ndPhData`/`ndMvData`・フィルターイベントリスナー・ソートイベントリスナー

4. **アーカイブ取得ロジック** — `fetch('cards-archive.html')`・`fetch('card-data.json')` の処理

5. **CSSクラス体系** — `sort-wrap`・`sort-dropdown`・`sort-option`・`sort-divider` の定義

### 編集前の確認

`new-design/index.html` を編集する前に、変更対象のセクションのみを読む。
ファイル全体をリファクタ・整理・改善しない。

---

## TOP12カード ハードコードHTML — 絶対に変更禁止 — CRITICAL

`new-design/index.html` および `index-v51.html` には TOP12 写真家のカードが HTML に直接書かれている。
**これらのカード HTML（`pc-top`・`pc-top__art`・`idx` など）は、いかなる修正作業でも絶対に変更してはならない。**

理由：
- カードのスタイル（`pc-top--cite` / `pc-top--number` など）・番号・アート内容は
  `cards-archive.html` を正とし、ページロード後に JavaScript が自動で上書きする
- ハードコード部分はロード中の一時表示にすぎず、最終表示は常にアーカイブ準拠になる
- しかし別の修正作業でこの部分を触ると「ハードコード値」が変わり、
  アーカイブ取得が失敗した場合（オフライン・fetch エラー等）に誤表示が残る

作業時の禁止事項：
- `<!-- 01 Stieglitz -->` 〜 `<!-- 12 Araki -->` の各 `<article>` 内の `pc-top` div を変更しない
- `idx` の数値を変更しない
- `pc-top__art` の内容を変更しない
- `pc-top--XXX` クラスを変更しない

リンク追加など他の修正をする際も、TOP12 カードブロックには一切触れないこと。
もしカードスタイルの変更が必要な場合は `cards-archive.html` を修正する（こちらが正）。

## ファイル構成

| ファイル | 役割 |
|---|---|
| `new-design/index.html` | 新デザイントップページ（スターマップ + TOP12カード）|
| `new-design/cards-archive.html` | 新デザイン用アーカイブ（カードの正データ）|
| `cards-archive.html` | カードアーカイブページ本体（283写真家 + 31運動 = 314枚） |
| `card-data.json` | 全314枚のカードデータ（photographers / movements） |
| `styles/card-v4-base.css` | カードデザインシステム基盤CSS |
| `styles/card-v5-overrides.css` | v5追加オーバーライドCSS |
| `index-v51.html` | v5.1トップページデザイン（スターマップ + 12枚フィーチャードカード） |

## カードの種類

- **Photographer カード** — 283枚（`data-type="photographer"`）
- **Movement カード** — 31枚（`data-type="movement"`）

## スタイル割り振りの優先順位

1. **TOP12 ハードコード**
   `stieglitz`, `takuma-nakahira`, `sherman`, `evans`, `robertfrank`, `moriyama`, `becher`, `cartierbresson`, `goldin`, `arbus`, `sander`, `araki`

2. **日本人写真家（nameJaに漢字あり）**
   → `pc-top--kanji` スタイル固定（artText は主題語）

3. **外国人写真家（主要28名）**
   → `pc-top--kanji-foreign`（概念漢字 + 英語グロス）

4. **残り外国人写真家**
   → 8スタイルをローテーション（`card-data.json` の `style` フィールド参照）

5. **運動カード**
   → 8スタイルのローテーション

## card-data.json のスタイルフィールド

card-data.json の `style` フィールドが使うのは以下 8 種のみ：
- `pc-top--kanji`（130件）
- `pc-top--title`（28件）
- `pc-top--slash`（28件）
- `pc-top--year`（27件）
- `pc-top--number`（27件）
- `pc-top--grid`（26件）
- `pc-top--stacked`（25件）
- `pc-top--initials`（23件）

## カード番号（idx）

- `card-data.json` の `idx` を正とする
- TOP12 の番号は card-data.json に合わせること（スティーグリッツ=15、中平=111 など）
- 番号は追加順（時代順でない）
- 運動カードは写真家の続番

## スタークリック（index-v51.html）

- 地図上の写真家をクリックすると、対応するカードをサイドパネルに表示する
- TOP12 の写真家 → 事前生成のフルデザインカードをクローン
- それ以外 → `card-data.json` から動的生成（`buildDynamicCard()` 関数）
- どちらにも一致しない場合 → archive へのリンクを表示

## CSSクラス体系

```
.pc-card               # カード全体
  .pc-card--photographer  # 写真家カード
  .pc-card--movement      # 運動カード
.pc-top                # カード上部（アートエリア）
  .pc-top__meta        # 番号 + ラベル
  .pc-top__art         # メインのタイポグラフィ
  .pc-top__hint        # 下部のヒントテキスト
.pc-body               # カード下部（テキストエリア）
  .pc-body__kind       # 種別ラベル
  .pc-body__name       # 日本語名
  .pc-body__name-en    # 英語名
  .pc-body__meta       # 生没年・国籍
  .pc-body__lede       # 紹介文
  .pc-body__channel    # チャンネル名
  .pc-body__tags       # タグ（最大3つ）
  .pc-body__cta        # 「写真史上の位置を読む →」
```
