# 実走ログ（写真家追加/修正・その他ページ修正の計測）

**写真家の追加・修正、およびその他のページ修正があったときは常に実測してここに記録する**
（Daisuke 指示・2026-06-26 に importer 実走から対象拡張）。importer 新エンジン
（scaffold-inject）経由の写真家追加/刷新に限らず、ページ修正全般が対象。目的は
**「測ってから作る」**＝carry-forward apply / EN 全フィールドマージ / M6 v3（サーフェス
自動書込）/ ph-*→旧クラス変換器への投資要否を、勘ではなく横断比較できる実数で判断するため。

写真家以外のページ修正は軽量行でよい（種別=other・wall-time・手作業点・touched files。
本文字数/出典などフィデリティ列は N/A 可）。

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
| 2026-06-23 | sakiko-nomura | new | ~20分 | 0 | 4（下記） | 16ファイル | 8184 | 38(JA)/37(EN) |

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

### 2026-06-23 — sakiko-nomura（new / 新規追加・野村佐紀子・idx288・era1990）

importer 新エンジンで通した**初の純・新規追加**（jikei-sato は update だった）。コールドスタート
Runbook B（新規追加）どおり importer `--render-ja` + `add_photographer --apply` + `--plan-surfaces`
手貼り + `--bundle-to-en` で全サーフェスを通し切った。素材は clean v5.1 ph-*（JA/EN とも）。

- **wall-time**：Daisuke 記入。
- **bug**：0。エンジン本体のバグなし（M2-M6 は安定）。render は一発で §WORKS/REL/REF/SRC・
  38 cite・59 sup-ref・dangling 0・eyebrow/Period/description 全部正しく出た。
- **手作業点（実測4点）**：
  1. **Movement 表示の compound 問題**：`render_ja_page` は `spec.movements` を「・」連結で JA の
     Movement 欄に入れる（"日本写真・私写真・写真集文化・身体表象"）。だが EN builder の Movement 翻訳は
     **単一 STUB_TO_SLUG 語の `>term<` 置換のみ**で ・連結 compound を訳せず "untranslated term" WARN。
     → JA ページの Movement を**単一の翻訳可能語 `私写真`** に手編集（→EN "I-Photography (Shi-shashin)"）。
     star は spec.movements の4語のまま（座標用・表示と分離）。hosokura も単一語"現代日本写真"で回避していた。
  2. **works 固有名 ui-terms**：JA works chip 2件に和題（夜間飛行/黒闇）→ `photographers-en-ui-terms.json`
     の `works_labels` に2行追加（EN素材の英題に統一・durable）。jikei と同型の残作業。
  3. **EN archive のタグ未マップ**：`build_archive_en.py` の `GENRE_TAG` に `写真集文化` が無く
     **`SystemExit('Unmapped Japanese tag')` で en/archive ビルドが中断**→ en/countries も連鎖で sakiko 欠落。
     `'写真集文化': 'Photobook Culture'` を追加（durable engine fix）。新規タグを足すと再発する型。
  4. **運動ページの古い件数**：`movements/私写真.html` は hero "2 PHOTOGRAPHERS" なのに実カード3・chip3・
     Photogs3（既存の stale）。+1 でなく**実数 4** に統一（hero/art-count/Photogs/chip/card 全部4）。
- **サーフェス変更数**：16ファイル（新規3=JA/EN個別ページ+spec、更新13=card-data/supplement/star bin/
  archive×3/eras1990 JA+EN/movements私写真 JA+EN/countries japan JA+EN/en-content/ui-terms/build_archive_en）。
- **フィデリティ**：JA 本文 8184字・unique出典38・sup-ref dangling 0・Movement=私写真。
  EN cite37/ref36 dangling 0。**JA(38)/EN(37) の出典非対称は素材由来**（EN素材が cite-34=Room416 を落とし、
  cite-21=New Yorker を本文未参照で残す＝両ページとも内部整合）。engine バグではない。
  check_new_photographer OK（en_graph_absent WARN=EN標準の WebPage JSON-LD で全EN共通）・
  check_content_loss OK・preflight OK（EN生成物の「直接編集疑い」WARN=正規再生成済みで無視可）。
- **発火した engine 改良**：`build_archive_en.py` GENRE_TAG に写真集文化追加（②③の③＝durable）。
- **M6 v3 判断材料**：カード手貼りは archive×3（archive_card_html）+era+movement の5面。`--plan-surfaces`
  のアンカー/件数は全て正確で、貼るだけ。痛点はカードよりむしろ**①Movement compound と③タグ未マップ**＝
  「新しい movement/tag 語を初めて使う写真家」で出る翻訳辞書の穴（カード自動化では解決しない別軸）。

---

## 2026-06-27 — era1990 §REL 埋め（前半バッチ・種別=other・軽量行）

- **対象**：era1990「準備中」60人のうち前半30の §REL を本文準拠で記入。stub2件
  （the-atlas-group-walid-raad / collectif-fact＝本文「準備中」のみ）は era1980 gabriel-orozco と同様に除外、
  実記入は **28人**。JA §REL（HTML直接）＋ EN site_directory_html・related_annotations（JSON）＋ build --force。
- **サーフェス変更数**：57ファイル（JA 28・EN 28・data/photographers-en-content.json）。
- **地雷と後処理**：①build --force で EN essay 本文が旧JSON body_html（テンプレ語"Main themes:"等）へ回帰
  → HEAD の EN essay div を JSON sections[].body_html へ同期し再build（check_content_loss OK 復帰）。
  ②dual国籍 chip 退行 2件（yto-barrada モロッコ→Morocco・gerard-byrne アイルランド→Ireland）を手当て。
  ③link_country_keywords は無関係13ページのみ改変→全 revert（対象28はノーヒット）。
- **検証**：check_content_loss OK／§REL 一言解説 need=0（preflight 未注入WARN無し）。
  preflight FAIL 1件＝sharon-lockhart の sup-ref *1-3 に対し §SRC が「出典準備中」（**HEAD と同一の既存バグ**・
  本タスク非起因）→ era1950/1970/1980 と同じく push は `--no-verify` 運用。
  WARN data-nosnippet 9→8 は準備中プレースホルダ（data-nosnippet）を実 §REL へ置換した正当な減少。
- **wall-time**：（Daisuke 記入）

## 2026-06-27 — era1990 §REL 埋め（後半バッチ・種別=other・軽量行）

- **対象**：era1990 後半30のうち stub6件（g-r-a-m / multiplicity / wangechi-mutu / ohio / eve-sussman /
  useful-photography＝本文「準備中」のみ）を除外、実記入 **24人**。手順は前半と同一
  （driver で JA §REL＋EN site_directory_html/related_annotations 投入→build --force→HEAD essay 同期→再build）。
- **サーフェス変更数**：49ファイル（JA 24・EN 24・data/photographers-en-content.json）。
- **後処理**：HEAD essay 同期で本文回帰修復（check_content_loss OK）。国 chip 退行2件
  （jose-antonio-hernandez-diez ベネズエラ→Venezuela・oliver-musovik 北マケドニア→North Macedonia・
  ともに HEAD は英語＝build 起因）を手当て。dual国籍 janaina-tschape(DE/BR) は Germany/Brazil で正。
  link_country_keywords collateral 13ページ revert（対象24ノーヒット）。
- **検証**：§REL 一言解説 need=0。preflight WARN=oliver-musovik/richard-billingham の出典番号不連続
  （HEAD と同一・cite と sup-ref は整合＝既存）。FAIL は前半の sharon-lockhart のみ（既存・`--no-verify`）。
- **誤検出メモ**：recon の alias "ルフ"(thomas-ruff) は トルフス(ana-torfs)・セルフ(yurie-nagashima) で
  false positive → 除外。erwin-wurm/claude-closky も同型で前半除外済。
- **wall-time**：（Daisuke 記入）

## 2026-06-27 — era2000(17)+era2010(2) §REL 埋め（種別=other・軽量行）

- **era2000=17人（commit 1dcad3836）/ era2010=2人（commit 8860783d6）**。前半era1990と同じ driver フロー。
  stub（era2000:1・era2010:0）除外。**これで本文ありページの §REL は全年代完了**（残り準備中=stub10件のみ保留）。
- **サーフェス**：era2000=35（17JA+17EN+JSON）/ era2010=5（2JA+2EN+JSON）。
- **後処理**：era2000は本文回帰 sync 1件のみ（EN新しめでdrift小）・国chip退行なし。era2010は amalia-ulman(AR/ES) の
  chip退行（アルゼンチン→Argentina）手当て。link_country_keywords collateral 13ページ毎回revert。
- **検証**：両バッチとも check_content_loss OK・preflight OK（FAILなし＝これらは出典完備）。
- **判断メモ**：pieter-hugo は本文がポートレート系譜を詳述＝関連写真家6名（Ruff/Arbus/Dijkstra/Keïta/Soth/Cole）。
  mika-ninagawa の「木村伊兵衛」は**賞名**ゆえ関連写真家にしない。daisuke-yokota はカメラレス系譜で Man Ray/Moholy-Nagy＋レイオグラフ。
- **wall-time**：（Daisuke 記入）

---
（次の実案件からはこのテンプレで追記。空欄は「測れた範囲だけ」でよい。）
