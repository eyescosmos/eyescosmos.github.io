# importer 実走ログ（写真家追加・刷新の計測）

importer 新エンジン（scaffold-inject）を実案件に通すたび1行＋詳細を記録する。目的は
**「測ってから作る」**＝carry-forward apply / EN 全フィールドマージ / M6 v3（サーフェス
自動書込）への投資要否を、勘ではなく横断比較できる実数で判断するため。

記録の分担：
- **Claude が埋める（客観）**：type・bug・手作業点（数と内容）・サーフェス変更数・
  フィデリティ差分（更新時 `--update-existing --dry-run` の出力）・発火した engine 改良。
- **Daisuke が埋める（体感）**：wall-time（所要分）。Claude は壁時計を正確に測れないため。

判断の閾値（合意）：
- carry-forward `--apply` 解禁 ← update 案件で dry-run の「保持/追加/要確認」分類が **1〜2件**信頼できると確認。
- M6 v3 解禁 ← new 案件で**サーフェス手貼りが数件まわして繰り返しボトルネック**だと測れる（詳細は importer-scaffold-inject-spec.md §… / memory）。

## サマリ（at-a-glance）

| 日付 | slug | 種別 | wall-time | bug | 手作業点 | サーフェス | 本文字数 | unique出典 |
|---|---|---|---|---|---|---|---|---|
| 2026-06-22 | jikei-sato | update | ~20分※ | 1（ネストspan節名） | 5→改良後2 | 0（既存） | 972→10233 | 3→25 |

※初回値。一度きりのバグ修正＋厚めの検証込みで、定常値ではない。

## 詳細

### 2026-06-22 — jikei-sato（update / 既存刷新）
- **wall-time**：約20分（Daisuke 自己申告）。内訳の体感＝バグ調査+修正と過剰検証が大半。
- **bug**：`_extract_sections` の節名抽出が `<span class="ph-section__name"><span>名前</span></span>`
  のネスト span で空を返す。修正済（`(.*?)</span>`+タグ除去）。一度きり・今後再発しない。
- **手作業点（実測5点）**：①description空白化 ②Period退行(1980年代←1980–1990s) ③§REF消失
  ④works固有名 ui-terms ⑤spec作成。→ **engine 改良で ①②を自動化**（残3）。さらに
  `--update-existing` で⑤(spec)自動導出・③(§REF)を計画提示 → **残る手作業は ③確定貼り・④の2点**。
- **サーフェス変更数**：0（既存写真家＝card/年代/運動は既存・不触）。
- **フィデリティ差分**：本文 972→10233字、unique出典 3→25、sup-ref 43、dangling 0、JA==EN 一致。
  EN ビルド WARN ゼロ。preflight の sup-ref 44→43 FAIL は意図的全文差替の正常フラグ。
- **発火した engine 改良**：description 自動充填・Period spec 化（このセッションで実装・push）。
- **commit**：ee292ca25(本文+バグfix) / c3fb09989(改良) / 2a06590ea(--update-existing+docs)。

---
（次の実案件からはこのテンプレで追記。空欄は「測れた範囲だけ」でよい。）
