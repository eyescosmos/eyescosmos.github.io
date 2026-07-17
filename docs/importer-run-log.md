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
| 2026-07-01 | (運動)new-topographics | other | （Daisuke記入） | 2 | 3（下記） | 27ファイル | N/A | 4 |
| 2026-07-01 | (運動)newtopo第2弾3名 | other | （Daisuke記入） | 0 | 1（下記） | 15ファイル | N/A | N/A |
| 2026-07-02-03 | (運動)contemporary-still-life | other | （Daisuke記入） | 3 | 2（下記） | 29ファイル | N/A | 4 |
| 2026-07-04 | lieko-shiga | other | （Daisuke記入） | 0 | 0 | 2ファイル | N/A | N/A |
| 2026-07-05 | yurie-nagashima | update | ~13分 | 0 | 6 | 4ファイル | 787→9849 | 3→38 |
| 2026-07-05 | lieko-shiga(EN JSON同期) | other | （Daisuke記入） | 0 | 1 | 1ファイル | N/A | N/A |
| 2026-07-05 | (engine)時間短縮①② | engine | （Daisuke記入） | 0 | 0 | 3ファイル | N/A | N/A |
| 2026-07-05 | yurie-nagashima(写真集Amazonリンク4+3冊) | other | （Daisuke記入） | 0 | 0 | 3ファイル | N/A | N/A |
| 2026-07-07 | yuki-onodera | update | （Daisuke記入） | 0 | 1（§REL手復元） | 7ファイル | 763→9763 | 4→32 |
| 2026-07-07 | (engine)works ui-terms自動化＋intentional-replacements | engine | （Daisuke記入） | 0 | 0 | 3ファイル | N/A | N/A |
| 2026-07-08 | yuki-onodera(写真集Amazonリンク3+4冊＋§REL写真家3名) | other | （Daisuke記入） | 0 | 0 | 3ファイル | N/A | N/A |
| 2026-07-10 | (JSON-LD birthDate/deathDate復元＋preflight) | other | （Daisuke記入） | 1（v5.1移行でJSON-LD日付欠落） | 0（機械復元・機械検証） | 154ファイル | N/A | N/A |
| 2026-07-10 | (JSON-LD初期欠落11件補完＋presenceガード) | other | （Daisuke記入） | 1（JSON-LD日付キー初期欠落） | 0（機械照合・機械検証） | 11ファイル | N/A | N/A |
| 2026-07-10 | (JSON-LD hero年照合ガード) | other | （Daisuke記入） | 1（本文で取れない日付キー欠落の死角） | 0（機械照合・機械検証） | 2ファイル | N/A | N/A |
| 2026-07-11 | asako-narahashi(写真集Amazonリンク JA3冊/EN3冊) | other | 10分弱 | 0 | 0 | 3ファイル | N/A | N/A |
| 2026-07-13 | **9名バッチupdate**(steichen/lartigue/hosoe/winogrand/kawada/araki/tomatsu/klein/friedlander) | update | 30分 | 4（engine穴・下記） | 0（全機械化） | 22ファイル | 計8664→39668 | 計40→190 |
| 2026-07-14 | **6名バッチupdate**(don-mccullin/ed-van-der-elsken/seydou-keita/larry-clark/philip-jones-griffiths/kishin-shinoyama) | update | 41分 | 4（engine穴・下記） | 0（全機械化） | 16ファイル | 計5826→28006 | 計16→135 |
| 2026-07-14 | capa(本文組版の標準化・文言不変) | other | （Daisuke記入） | 0 | 0 | 3ファイル | N/A | N/A |
| 2026-07-14 | h4→h3一括変換(69ページ・266見出し・文言不変) | other | （Daisuke記入） | 0 | 0 | 69ファイル | N/A | N/A |
| 2026-07-15 | **5名バッチupdate**(joel-meyerowitz/joel-sternfeld/lewis-baltz/robert-adams/mapplethorpe) | update | 29分 | 0（engine穴なし） | 0（全機械化・§RELリンク化2名はスクラッチ機械編集） | 12ファイル | 計5287→21715 | 計17→84 |

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

## 2026-06-28 — nerhol（new / 新規追加・idx299・era2010）+ miyako-ishiuchi（update / 既存刷新）

### nerhol（新規追加）

- **wall-time**：（Daisuke 記入）
- **bug**：0。M2-M6 全安定。
- **手作業点（実測）**：
  1. **spec.json 手作成**：nameJa/nameEn/years/era/period/channel/movements/tags/starText/citations 手記入。
  2. **GENRE_TAG 未マップタグ対応**：素材タグ（写真と彫刻/積層写真/時間の断面/写真的オブジェクト/ブックアート）は全未マップ
     → spec.tags を既存マップ済み `['ポートレート', '日本写真']` に変更（eyebrow と card channel はこの2語で表示）。
     写真と彫刻は Movement フィールドに残す（STUB_TO_SLUG 未登録のため EN では untranslated WARN → ui-terms.terms に追加）。
  3. **ui-terms 追加 5件**（durable）：terms に「写真と彫刻」、works_labels に「千葉市美術館 - 水平線を捲る」「上野の森美術館 - VOCA展2020 Remove」「SFMOMA - ひろしま/hiroshima #71」「National Museum of Art - Endless Night / 1・9・4・7 / SCAR」「MIMOCA - 石内都 絹の夢」。
     ※ 後者3件は miyako の ui-terms 追加と同時作業。
  4. **EN entry 手 insert**：bundle-to-en stdout を data/photographers-en-content.json に挿入（キー = nerhol.html）。
- **サーフェス変更数**：9ファイル（新規2=JA+EN個別ページ、更新=card-data/supplement.js/star bin/en-content.json/ui-terms.json、spec.json+バックアップ3件は未追跡）。Phase 2 残=archive/cards-archive×3/eras/2010/en/eras/2010/countries/japan。
- **フィデリティ**：JA 本文 chars大（28 cite・0 dangling）。EN cite 28・supref 28 dangling 0。JA==EN 出典一致。
  check_new_photographer OK（en_graph_absent=EN全共通WARN）。check_content_loss OK。preflight OK。
- **発火した engine 改良**：なし（既存エンジン正常動作）。
- **WARN 残（非ブロック）**：EN: no photobooks_html / no external_links_html / jsonld fallback（いずれもコンテンツ有で正常）。

### miyako-ishiuchi（update / 既存刷新）

- **wall-time**：（Daisuke 記入）
- **bug**：0。
- **手作業点（実測）**：
  1. **バックアップ**：JA+EN 両ページを -backup.html にコピー（guardrail 準拠）。
  2. **--update-existing dry-run 実行**：フィデリティ差分確認（本文 1026→8855字、出典 2→31、sup-ref 6→67）。
     carry-forward 計画：§REF 既存2件（SFMOMA/Tate Modern）→ 新「準備中」に手貼り。
  3. **spec.json 手作成**：derive_spec から years/period/channel/era/idx 引き継ぎ。movements は素材から 私写真/ドキュメンタリー追加。
  4. **§REF 手貼り**：backup から SFMOMA/Tate Modern リンク2件を新 JA ページの §REF body へ差込（prep-block → actual content）。
  5. **EN entry 手 insert**：bundle-to-en stdout を data/photographers-en-content.json に挿入（既存エントリを新内容で置換）。
     further_reading_html を手動追加（SFMOMA/Tate Modern リンク英語版）。
  6. **ui-terms 追加**（miyako 固有 3件）：works_labels に「SFMOMA - ひろしま/hiroshima #71」「National Museum of Art - Endless Night / 1・9・4・7 / SCAR」「MIMOCA - 石内都 絹の夢」。
- **サーフェス変更数**：5ファイル更新（JA/EN 個別ページ・en-content.json・ui-terms.json）。card-data/supplement.js/star bin は変更なし（既存写真家＝不触）。
- **フィデリティ**：JA 31 cite・31 supref dangling 0。EN 31 cite・31 supref dangling 0。JA==EN 出典一致。
  data-nosnippet 9→8（JA）/ 8→7（EN）: 「準備中」prep-block 2件が実コンテンツへ置換された正当な減少。
  check_new_photographer OK。check_content_loss OK。preflight OK（WARN=nosnippet減少=上記理由で正常）。
- **WARN 残（非ブロック）**：EN: no photobooks_html / no external_links_html / jsonld fallback（旧エントリ由来フィールドは Phase 2 EN全フィールドマージで対応）。

### Phase 2 — nerhol サーフェス統合（miyako は既存写真家＝サーフェス作業不要）

- **キーワードチップ修正**（Phase 1 後の content-fidelity fix・両写真家）：render が `ph-kw`/`ph-side-chip` を spec.tags（2語）から
  埋めて素材の rich keyword を落としていた。素材どおりに手修正。nerhol=6語（写真と彫刻/ポートレート/積層写真/時間の断面/
  写真的オブジェクト/ブックアート、sidebar 先頭4）。miyako=9語（横須賀/私写真/暗室/表面/染織/衣服/傷跡/戦後日本/記憶、sidebar 先頭4）。
  **coordinator は miyako を「8語・私写真不在」と誤認したが、JA/EN 素材とも実際は 9語（私写真/Shishashin 含む）**＝素材忠実に 9 維持。
  EN keywords_html は既に正しく 9（変更なし）。card-data tags は不触。
- **JA カード手貼り 4面**：archive.html / cards-archive.html / new-design/cards-archive.html（前者2はトラッキング・後者は
  gitignore 済の runtime コピー＝コミット対象外）の最初の `.pc-card--movement` 直前へ archive_card_html（data-country=JP）。
  eras/2010.html のグリッド末尾へ era card。eras hero count 8→11 に是正（**旧 8 は既存の stale。実カード数は 10＋nerhol=11**）。
  写真と彫刻に運動ページなし＝運動カード挿入なし。
- **engine fix（durable）**：`build_archive_en.GENRE_TAG` に `'写真と彫刻': 'Photography and Sculpture'` 追加。
  これが無いと nerhol channel 接尾辞「写真と彫刻」で `SystemExit('Unmapped Japanese tag')`→en/archive 中断（sakiko の写真集文化と同型）。
- **EN/派生再生成（順序厳守）**：build_archive_en（320カード）→ build_taxonomy_en --era 2010 → generate_country_pages --country japan
  → generate_country_pages_en --country japan。
- **8面プレゼンス確認**：archive / cards-archive / new-design/cards-archive / eras/2010 / countries/japan / en/archive /
  en/eras/2010 / en/countries/japan すべて nerhol 掲載 ✓。
- **collateral 確認・revert なし**：
  - countries/japan・en/countries/japan の hero count 57→61 は generator がカードデータ実数（JP=61）へ是正した正当な決定論差分（既存 stale の追いつき）。
  - en/countries/japan の `.head__lang` CSS に `, .head__lang a` セレクタ追加は generator の lang-toggle fix（退行でなく改善）。lang toggle は EN active / JP→JA で正。
  - 他写真家カード・dual国籍 chip・TOP12（pc-top--XXX）・filter/sort UI・カード JS への混入差分ゼロ（確認済）。
  - link_country_keywords は実行せず（指示どおり）。
- **検証**：check_content_loss OK。preflight OK（WARN=①en/countries・en/eras「直接編集疑い」＝正規再生成済の既知偽陽性 ②miyako nosnippet 減少＝prep-block 置換の正当減少）。
- **監督後修正（Opus・同日）**：
  1. **miyako キーワード 9→8**：Daisuke 指示で `私写真`/`Shishashin` を keyword chip から除去（JA chip・JA sidebar・EN keywords_html・EN再ビルド）。
     本文 prose の shishashin 論（受容・批評）は substantive のため残置。card-data tags は不変。
  2. **国別 generator の人数表示バグを修正（durable）**：`generate_country_pages.py` / `generate_country_pages_en.py` の
     `member_count` を **`len(members)`（card-data 実数）→ 実際にレンダリングしたカード数** に変更。原因＝archive.html に未掲載の
     メンバーはカード生成ループで skip されるのに hero 人数は card-data 実数を表示し、**日本のみ 61 表示 / 58 カードの不整合**が出た
     （他国は drift なしで一致＝唯一の不整合）。Daisuke 判断「範囲を絞る」を採用し japan を **58/58 で整合**（HEAD 57/57 + nerhol）。
     他国は drift がないため数値不変（regen していないので committed も不変）。
  3. **別件として記録した既存 drift**：archive.html に card-data の 10名が未掲載（alec-soth/boris-mikhailov/edward-burtynsky/
     gregory-crewdson/masashi-asada/rineke-dijkstra/thomas-struth/zanele-muholi/arata-dodo/jp-木村伊兵衛）。本タスク範囲外。
- **wall-time**：（Daisuke 記入）

---

## 2026-06-28 — バックフィル#2: archive.html 未掲載10名（国別カウントの根） — 軽量行

- **対象**：card-data 在籍だが archive.html 未掲載の idx289–298（alec-soth/boris-mikhailov/edward-burtynsky/
  gregory-crewdson/masashi-asada/rineke-dijkstra/thomas-struth/zanele-muholi/arata-dodo/jp-木村伊兵衛）。
- **手順**：cards-archive.html の既存レンダリング済カードを雛形に、`data-nationality→data-country` と hint の
  era→years（meta から抽出）の2変換のみで archive.html へ10枚追加（nerhol 直後・movement カード群の前）。
  → 写真家カード 289→299（card-data と一致）。en/archive は build_archive_en.py で再生成（330カード／photog299）。
  → 影響7国を generate_country_pages(_en) --country で再生成し hero==cards を確認。
- **jp-木村伊兵衛（サイト唯一の意図的 JA専用＝EN無し）も Daisuke 指示で掲載**：
  build_archive_en.py に①NO_EN_PAGE 登録（en カードは JA ページへリンク）②手書きEN lede（JA本文準拠）
  ③GENRE_TAG 追加（報道写真/ライカ ＋ 新規カードの未マップ tag/channel 接尾辞: 写真集/ポストソ連/人新世/
  産業風景/演出写真/映画的写真/郊外/家族写真/移行期/身体/大判写真/美術館/Visual Activism/Queer Archive/旅写真/
  アクティヴィズム/旅）。
  generate_country_pages_en.py は EN archive lookup を JA-only href も拾うよう拡張（kimura を en/countries/japan へ
  parity 掲載・JAページリンク／再発WARN解消）。→ japan JA61/EN61 で一致。
- **国別 hero==cards 確認**：US 77/77, UA 3/3, CA 6/6, JP 61/61(EN61), NL 13/13, DE 30/30, ZA 5/5（JA/EN とも）。
- **collateral**：article 開閉330均衡・重複idxなし・10名全在。TOP12/filter/sort/カードJS 不変。link_country_keywords 未実行。
- **検証**：check_content_loss OK。preflight OK（WARN=再生成 en/countries・en/archive の「直接編集疑い」＋avedon Biography＝既知良性）。
- **対象外の並行差分**：scripts/import_chatgpt_photographer.py / test_importer_scaffold_inject.py が working tree に
  別セッションの importer 摩擦修正として未コミット在中。本タスク範囲外につき**触らず・stage しない**。
- **wall-time**：（Daisuke 記入）

---

## 2026-06-28 — importer engine 改善4点（nerhol/石内都の摩擦の源流つぶし・種別=engine・軽量行）

写真家追加ではなく engine 修正（実案件で踏んだ摩擦の恒久化）。別セッションの archive バックフィルと
同じ working tree 上で並行実施（こちらは scripts/ の importer engine、向こうは archive/countries の生成物）。

- **① JAキーワードを素材から入れる（最優先）**：`import_chatgpt_photographer.render_ja_page` が scaffold の
  `ph-kw`/`ph-side-chip` を spec.tags（カード用2語）のまま出し素材の rich keyword を落としていた恒久バグを是正。
  `_inject_ja_keywords` を追加し、scaffold 出力後に `ph-kw`=bundle.keywords 全件、サイドバー `ph-side-chip`=先頭4件
  （is-primary 先頭1）へ差し替え。空なら従来 spec.tags フォールバック維持。EN `_en_keywords_html` と対。
  検証：`--render-ja photographers/nerhol.html`（既存 nerhol を素材代用）で ph-kw=6語・side-chip 先頭4が
  committed の手修正ページと完全一致（修正前は spec.tags の2語のみ）。`test_importer_scaffold_inject` に
  「ph-kw/side-chip が bundle.keywords 由来・spec.tags 由来でない・先頭4切り」assert 追加（素材語を tags と別語に）。
- **② 素材プリチェック CLI**：`--precheck --slug X --ja A.html [--en B.html]`（read-only・書込なし）。(a)新規/既存判定
  (b)CJK比率で日英取り違え警告（nerhol が日英とも EN だった事故の予防）(c)keyword/運動/出典件数＋運動名（―区切りを
  クリーン）の STUB_TO_SLUG/GENRE_TAG 有無。tag×GENRE_TAG は spec 確定後の add_photographer 事前 lint（④）へ委譲。
- **③ ドリフト検知を preflight に追加（WARN）**：`check_archive_presence`（card-data 全 id が archive.html に在るか＝
  国別カウント崩れの根）＋ `check_country_hero_counts`（countries/*.html の hero 人数==実カード数）。現在は並行
  バックフィルで整合済のため検知0件＝将来ドリフトの番兵。
- **④ channel 接尾辞 lint**：`add_photographer._lint_unmapped_tags` を spec.tags に加え channel の `' · '` 接尾辞も
  GENRE_TAG 未登録なら着手前警告（今回 channel 接尾辞「写真と彫刻」で `SystemExit('Unmapped Japanese tag')`）。
  返り値を (語,出所) 化し `_print_tag_lint` で出所表示。spec.md §13 に1行追記。
- **触ったファイル（5）**：scripts/import_chatgpt_photographer.py・scripts/preflight.py・scripts/add_photographer.py・
  scripts/test_importer_scaffold_inject.py・docs/importer-scaffold-inject-spec.md。**並行セッションの archive/countries/
  build_archive_en/generate_country_pages_en/本ログの差分には触れていない**。
- **検証**：py_compile OK・test_importer_scaffold_inject PASS（byte同一）・check_content_loss OK・preflight OK
  （新 FAIL なし・既知良性 WARN のみ）。
- **wall-time**：（Daisuke 記入）

## 2026-06-28 — バックフィル#1: era ページ hero 人数のスタレ修正（種別=other・軽量行）

- **発見（handoff の前提とズレ）**：「eras/1970 未掲載8名」は**サイトから欠落ではなく他 era ページに単独配置**
  （anders-petersen/an-my-le→1990, barbara-probst/hellen-van-meene→2000, simone-nieweg/lidwien-van-de-ven→2010,
  miyako-ishiuchi/keizo-kitajima→1980）。card-data `era` と era ページ実配置が**14件ズレ**。サイトは単独配置
  （重複は rinko-kawauchi の 1990+2000 の1件のみ）。真の欠落（どの era ページにも不在）=jp-木村伊兵衛/gabriel-orozco/
  fabian-marti の3件。→ 配置・3欠落・rinko重複は**editorial判断**として Daisuke レビュー保留。
- **今回実施（Daisuke「実際の人数にして」）**：全 era ページの hero `Photographers <strong>N</strong>` が
  ハードコードで古い（1970=12表示/26実・1980=10/65・1990=8/66 等）→ **実際の表示カード数へ是正**。
  JA 8ページ手修正（1890→15,1910→14,1930→30,1950→25,1970→26,1980→65,1990→66,2000→23）→
  build_taxonomy_en.py --era 各個 で EN 再生成。1839/1870/2010 は既に一致。
- **検証**：全11 era で hero==cards（JA/EN とも）。card 数・配置・本文は不変（hero 数字のみ）。
  check_content_loss OK／preflight OK（WARN=avedon Biography 既知のみ）。
- **保留（要 Daisuke レビュー・URL 提示済）**：①era 配置の正本（card-data era vs ページ実配置）②3真欠落の補完要否
  ③rinko-kawauchi 重複の解消先。
- **wall-time**：（Daisuke 記入）

## 2026-06-28 — バックフィル#3: 石内都を星マップ(bin)へ追加（種別=other・軽量行）

- **確認**：石内都は個別ページ（JA/EN・本日刷新済）はあるが star bin に未登録（grep 0件）＝handoff のとおり星だけ欠落。
- **bin 構造**：`design/toptest-assets/d369d828-….bin` の `const PHOTOGRAPHERS = [...]`。本体48件はシングルクォート＋無引用符キー、
  直近追加5件（hosokura/nerhol 等）はダブルクォートJSON の混在。**直近形式（JSON）で nerhol の直後に1件追加**＝計54件。
- **データは既存ページから忠実取得（捏造なし）**：id=miyako-ishiuchi / name=Miyako Ishiuchi / nameJa=石内都 / nationality=JP /
  years=1947–（群馬県桐生市生まれ・birthDate 1947 を JA ページで確認）/ gender=女性 / era=1970 /
  **movements=[ドキュメンタリー, 日本写真]**（接続用の共有運動・bin で各53/13件使用＝星座リンク成立。**私写真は不使用**＝方針踏襲）/
  links・citations=SFMOMA artist ページ＋Getty "Postwar Shadows"（ページの出典から）/ context text・textEn はリード要約。
- **検証**：文字列考慮の括弧バランス（brace/bracket とも最終0・最小0で負化なし）、miyako entry を JSON.loads で妥当性確認、
  重複id なし、構造 `nerhol},miyako{…}];` 正。check_content_loss OK／preflight OK。bin diff +43/−6（−6 は nerhol 周辺の空行/末尾カンマ整形）。
- **注意**：bin は手編集が正本（ビルド不要・add_photographer は既存在籍で使えない）。`-backup.bin`（未追跡）は触らず。
- **wall-time**：（Daisuke 記入）

## 2026-06-28 — バックフィル#1続: era 配置の是正（17人・単独配置）+ 連鎖整合（種別=other）

- **判明**：card-data/リーフの era には誤バッチ（EntryNo110–119 CONCEPTUAL を機械的に era=1970 入力。hellen-van-meene は1972生で1970s不可等）。
  リーフ・card-data・era ページが三者食い違い＝機械決定不可。Daisuke 承認の表に従い**代表作・確立期の年代**で17人を確定。
- **era 配置（Daisuke 承認表どおり）**：1970←anders-petersen/miyako-ishiuchi｜1980←keizo-kitajima｜
  1990←simone-nieweg/naoya-hatakeyama/wolfgang-tillmans/yurie-nagashima/gabriel-orozco｜
  2000←an-my-le/barbara-probst/hellen-van-meene/lidwien-van-de-ven/rinko-kawauchi/mika-ninagawa/lieko-shiga/fabian-marti｜
  1930←jp-木村伊兵衛。**rinko の 1990+2000 重複は2000へ一本化**。orozco/marti は EXCLUDED_IDS だったが指示で追加。
- **仕組み**：era カードの idx はグローバル card-data idx・誤配置でも hint は本来 era 表示＝**カードは中身正で載るページのみ誤り**。
  → `<article>` の cut/paste 移動（balanced抽出）＋ hint を移動先 era に統一。3追加は archive カードを era 形式へ変換。
- **連鎖整合**：①card-data era 9件更新＋orozco/marti の nationality(MX/CH)・metaJa 補完（生年はサイト未記載＝捏造せず国のみ）
  ②CONCEPTUAL バッチの壊れ metaJa（"1970s/1970年代"）を era カードの正値（country・生年）で card-data/archive/cards-archive 統一
  ③archive/cards-archive の data-era 9件＋orozco/marti に data-country/data-nationality 付与
  ④全 era ページ hero＋サイドバー Photogs を実カード数へ（前回 hero のみ→今回サイドバーも）
  ⑤EN 再生成：build_archive_en＋build_taxonomy_en(9 era)＋国 JA/EN(japan/germany/netherlands/united-states＝並び替え、
  mexico/switzerland＝orozco/marti 新規メンバー)。⑥EN archive 国メタ用に build_archive_en の COUNTRY_CODE に メキシコ/ベトナム追加＋
  tr_meta に単独国名分岐（orozco "メキシコ"→MX 等）。⑦星 bin は miyako=1970(target) で既に整合・他16は bin 非在籍。
- **検証**：17人すべて単独配置（JA/EN）・era 全11で cards==hero==Photogs（JA/EN）・era 横断で重複ゼロ・国別 hero==cards・
  archive/en-archive 299・article 開閉balance全OK・追加3カード整形正常・EN国メタ VN/US・MX・CH。check_content_loss OK。
- **既知 preflight FAIL（intended・push時 `--no-verify`要 Daisuke 確認）**：eras/1980(133→129)・eras/2010(25→17) の per-page
  カード減少＝他 era への**移動**であり実消失でない（移動先在＋総数保存を検証済）。
- **未対応（要判断・別surface）**：誤バッチ写真家のリーフページ era 表記（eyebrow/Period の "1970s / 1970年代"）は
  多箇所散在で一括編集リスク高につき今回は未変更。元々事実誤りで、JA/EN リーフ生成も絡む別タスク。
- **wall-time**：（Daisuke 記入）

---

## 2026-06-30 — トップ虫眼鏡検索を全アーカイブ化（other）

- **type**：other（バグ修正・JSのみ）
- **bug**：`index.html` / `en/index.html` のヘッダ虫眼鏡検索が、検索インデックスを
  静的 `.pc-card`（DOM上の TOP12 のみ）から構築していたため、TOP12 以外＝新規追加を含む
  約287名がヒットせず「該当なし」になっていた。カードビューのツールバー検索・archive.html・
  写真家ページのサイドバー検索は `card-data.json`（全299名）を参照しており正常だった。
- **手作業点**：1（`searchIndex` 静的構築を `buildSearchIndex()` 関数化し、`cvPhData`+`cvMvData`
  〔card-data.json 由来〕優先・未取得時のみ DOM フォールバックへ。`runSearch` の参照を差し替え）。
- **サーフェス変更数**：2ファイル（index.html / en/index.html・各 +11/-2 行）。
- **検証**：ローカルサーバ＋ブラウザ実機。修正後、虫眼鏡で 石内都/Nerhol/川内倫子/フランス13件
  ヒット・nonsense は「該当なし」。EN も Ishiuchi/Nerhol/Moriyama ヒット（href は /en/ 配下の
  EN 個別ページへ解決・存在確認済）。check_content_loss / preflight 通過。
- **残（データモデル制約・今回対象外）**：card-data の国名が日本語（metaJa）のため
  EN 側で "United States" 等の英語国名検索は全検索共通で 0 件。movement 名（例「プロヴォーク」）も
  per-photographer フィールドが無く全検索共通でヒットしない（channel は英語カテゴリ名のみ）。
- **wall-time**：（Daisuke 記入）

---

## 2026-07-01 — link integrity チェックの整理＋preflight実ガード化（other）

- **type**：other（スクリプト整理・preflight配線修正のみ、ページ本文は不変更）
- **bug**：`scripts/check_photographer_link_integrity.py` が冒頭で実行禁止の
  `generate_photographer_pages` に依存し、旧構造（`<section class="section"><h2>関連作品</h2>`
  等）を基準に検査していたため、v5.1 現行構造（`ph-section` / `ph-works-links` / `ph-section__name`）
  へ移行済みの現行ページで常に誤検出していた（作品欄44件＝22名×2言語＋Biography先頭一致2件＝計46件、
  実害ゼロ）。preflight 側もこれを「既知ノイズ・非ブロック」として丸ごと無視しており、本物のリンク
  退行が起きても検知できない状態だった。
- **対応**：①旧ジェネレータ依存・overrides.js 基準の作品欄検査（WORKS_REQUIRED_IDS /
  RESTORED_EXTERNAL_LINK_IDS ループ）を除去。②h1と写真集見出しの照合（`<h2>...Photobooks</h2>`）は
  現行ページに該当構造が存在せず恒久的に不発の死んだ検査だったため除去。③1文字外部リンクテキスト検査
  はセレクタ非依存で現行ページでも有効なため維持。④Avedon⇄Penn の Biography 先頭一致・本文混入検査は
  セレクタを現行 `ph-section__name`/`essay` 構造へ更新し維持（相互混入の逆方向チェックも追加）。
  ⑤`scripts/preflight.py` の `run_existing_check()` を非ブロックの `known_warnings` 蓄積から
  `hard_failures` 蓄積（実ガード）へ変更、既存の1文字リンク用トークンスキャン workaround も
  本チェックが blocking になったため撤去。
- **手作業点**：0（ページ本文は不触。スクリプト2本のみ変更）。
- **サーフェス変更数**：2ファイル（scripts/check_photographer_link_integrity.py・scripts/preflight.py）。
- **検証**：`check_photographer_link_integrity.py` 単体 exit 0（46→0件）。`preflight.py` exit 0
  （このチェックが hard_failures 経路でグリーン通過することを確認）。`check_content_loss.py` exit 0。
- **wall-time**：（Daisuke 記入）

---

## 2026-07-01 — movements 掲載漏れ監査＋backfill（種別=other・軽量行）

- **対象**：正本（photographers.js／-supplement.js／-manual-additions.js の movements[] 統合290名）と
  movements/*.html 31枚を突き合わせ、掲載漏れ・逆ドリフトを監査。小規模backfill5ページ・計14名を追加。
  社会ドキュメンタリー（annan/domon/lange/paul-geniaux/sander/tomatsu 6名）・モダニズム
  （irving-penn/jp-中山岩太/jp-安井仲治 3名）・ピクトリアリズム（jp-安井仲治/jp-野島康三 2名）・
  私写真（araki/masahisa-fukase 2名）・リアリズム写真（domon 1名）。カード内容は card-data.json の
  nameJa/nameEn/metaJa/ledeJa/channel/tags/style/artText/hintText を転記。
- **対象外（Daisuke判断）**：コンセプチュアルアート（正本115・掲載7）とドキュメンタリー（正本37・掲載8）は
  規模が桁違いで、ページが1960-70年代の狭い歴史的運動として書かれている一方、正本タグは写真史全般へ
  広く付与されており性質が異なる。ページ性格を維持し今回は対象外。逆ドリフト14件（stieglitz/moholy/
  salgado/goldin 等、正本 movements[] に無いがページには掲載）も現状維持で確認のみ・変更なし。
  `コンセプチュアル`(37名)と`コンセプチュアルアート`(115名)が別タグとして併存している点は別途要検討。
- **副産物**：jp-木村伊兵衛はリーフページが存在し Movement=リアリズム写真 を明記しているが、3つの
  movements[] 正本ファイルのどこにもエントリが無い（build_taxonomy_en.py も同一警告＝MISSING CARDS）。
  掲載自体は正しいが正本データにこの写真家が丸ごと欠落。報告のみ・対応せず。
- **サーフェス変更数**：10ファイル（JA 5・EN 5、build_taxonomy_en.py --slug で個別再生成）。
- **検証**：各対象ページで カード数==hero==サイドバー件数を確認（13/11/10/6/2）。check_content_loss.py OK。
  preflight.py OK（EN側5件は「直接編集疑い」WARNのみ＝写真家カードがJA HTML由来でJSON側は不変という
  既知の偽陽性パターン、他era backfillと同型）。無関係ページの巻き込みなし（git diff --stat で確認）。
- **wall-time**：（Daisuke 記入）

---
## 2026-07-01 — 誤バッチ写真家9名のリーフera表記backfill（種別=other・軽量行）

- **対象**：commit 3304539c8 で card-data era を訂正した9名（an-my-le/barbara-probst/
  hellen-van-meene/lidwien-van-de-ven/simone-nieweg/gabriel-orozco/naoya-hatakeyama/
  rinko-kawauchi/keizo-kitajima）のリーフページ(photographers/*.html)側のera表記
  （title/og/twitter・hero Period・hero Years・entry-meta Period・side-meta Period）を
  新eraへ統一。rinko-kawauchiは既に正しく変更不要。本文プロース中の活動期記述（例:
  「1980年代から…」）は事実記述として据え置き、機械一括置換はせず1人ずつ判断。
- **副産物発見**：gabriel-orozcoのentry-meta（`<dl class="ph-entry-meta">`側のみ、
  サイドバー側は無事）で `dt>Country` に国名でなくera値（旧"1980s / 1980年代"）が入り
  `dt>Years` が空という既存の構造バグを発見。今回はera数値のみ新eraへ更新し、
  dt/ddの誤対応自体は範囲外として温存（要Daisuke判断）。
- **EN反映**：8名分 `build_photographers_en.py --slug <id>` で再生成（JSON側は無変更のため
  preflightは「EN直接編集疑い」WARN×8＝既知の偽陽性パターン、他era backfillと同型）。
- **サーフェス変更数**：16ファイル（JA 8・EN 8）。
- **検証**：`check_content_loss.py` OK。`preflight.py` OK（HARDなし、WARNのみ＝上記EN偽陽性＋
  an-my-le側の既存supref[29]欠損cite・今回変更とは無関係の既知データ不備）。
  `git diff --stat` で対象16ファイル以外の巻き込みなしを確認。
- **wall-time**：（Daisuke 記入）

---

### 2026-07-01 — 運動「ニュー・トポグラフィックス」新設＋4名再分類（other / コンセプチュアルアート解体1運動目）
- **内容**：新運動ページ movements/ニュー・トポグラフィックス.html 新規（コンセプチュアルアート.html雛形・
  本文は出典準拠ドラフト cite4本）。frank-van-der-salm/takashi-homma/john-riddy→ニュートポ、
  simone-nieweg→既存デュッセルドルフ派へ移動。本文・§REL不介入（機能タグのみ）。
- **サーフェス**：JS(supplement)4名・leaf機能タグ4枚・星bin(d632c32e 4名+ffc7bdc4 META)・data/movements.js・
  build_taxonomy_en.py 4辞書・taxonomy-en-content.json sections・photographers-en-content.json SEO36箇所・
  card-data.json tags4名・cards-archive/archive/eras静的カード・EN再生成一式＝計27ファイル。
- **bug/発見（2件）**：①EN運動ページはtaxonomy-en-content.json/ABSTRACTS_EN/THESES_EN未登録だとJA本文が
  fallbackで残る（検出→3系統登録で解消）②build_archive_en.py GENRE_TAG未登録だとSystemExit（1行追加）。
  ③既知メモの「card-data.jsonはmovement無関係」は誤り＝tags[]が運動名を保持しカード面の正（メモ訂正済）。
- **手作業点（3）**：①新ページ本文ドラフト（機械化対象外）②EN builder 4辞書＋JSON sections のEN文（同）
  ③era1990のsimoneカード既存ドリフト（誤カナ・旧タグ）の個別判断修正。
- **検証**：check_content_loss OK / preflight OK（WARN3=EN再生成の既知偽陽性）/ カード面・leaf機能タグ・
  星binの残存ゼロをスクリプト監査 / git diff 25M+2untracked=全て対象内。
- **分業**：fable監督・Sonnetサブエージェント（カードtags置換～EN再生成～検証、91 tool uses / 約6.7分）。
- **wall-time**：（Daisuke 記入）

### 2026-07-01 — ニュートポ第2弾: 1975年展出品者3名追加（other / Daisuke指摘起点）
- **内容**：robert-adams `[]`→ニュートポ / lewis-baltz `[]`→ニュートポ / stephen-shore `['コンセプチュアル']`→
  ニュートポ＋ニューカラー（ニューカラーページ1→2名）。becherは現状維持（Daisuke決定）。
- **起点**：Daisukeの「ニュートポにロバートアダムス入ってなくない？」→ 調査で**プール定義の穴**発見＝
  厳密一致抽出が別名`'コンセプチュアル'`単独30名と無所属`[]`27名を取りこぼし。恒久ルール化（新運動ごとに
  全体スキャン＋確認）をmemoryへ。
- **サーフェス**：JS・星bin・card-data tags・leaf機能タグ3枚（adams/baltzはtitleのera1970テーマ語置換＋
  eyebrow/breadcrumb/kw/chip補完、shoreは別名→2運動化）・静的カード3面・ニュートポページ+3カード(3→6)・
  ニューカラーページ+1カード(1→2)・EN JSON SEO 27箇所・EN再生成（archive→taxonomy→photographers順）。
- **手作業点（1）**：era1970のshoreカードledeに旧つづり「ニュー・トポグラフィクス」が既存（タグのみ正式つづりで
  統一・ledeは不変・要将来判断）。
- **検証**：残存ゼロ監査 / check_content_loss OK / preflight OK（WARN5=EN再生成の既知偽陽性）/
  星bin差分=意図7名+META1行のみをdiffで確認。
- **分業**：fable監督・Sonnet委譲（151 tool uses / 約12分）。
- **wall-time**：（Daisuke 記入）

## 2026-07-02 — lieko-shiga（update / 既存刷新・idx261・era2000）

- **wall-time**：（Daisuke 記入）
- **bug**：0（engine 正常。素材側に review-preview の rev19/20/21 span が JA/EN 計75個混入＝素材品質問題、下記手作業3）。
- **手作業点（実測）**：
  1. **バックアップ**：JA+EN 両ページを -backup.html にコピー。
  2. **spec.json 手作成**：derive_spec から years/period(`2000–2010s`)/channel/era/idx 引き継ぎ。movements は素材の
     「日本現代写真」がページ非実在のため採らず、既存の ステージド写真 のみ（movementSlugJa 同値・リンク切れ回避）。
  3. **rev-highlight 除去**：素材 JA/EN 双方に rev19/20/21 span 計75個混入。importer は未知クラスで素通り
     → JA レンダ出力・EN bundle エントリ双方からテキスト保持で除去（ネスト対応 innermost-first）。
  4. **§REF/§REL carry-forward**：新素材は §REF「準備中」・§REL なし → backup から MoMA/Getty Iris 外部リンク2件を
     §REF へ、ステージド写真 の §REL 1件を splice（EN site_directory_html は field-merge で保全）。
  5. **EN field-merge**：bundle-to-en 出力を en-content.json 既存エントリへ空値スキップで merge
     （photobooks/external_links/footer/jsonld/site_directory 等の既存値保全・diff は lieko ブロックのみ確認済）。
  6. **ui-terms 追加 1件**：works_labels「Art Platform Japan - 螺旋海岸」→ Rasen Kaigan（untranslated WARN 解消）。
- **サーフェス変更数**：4ファイル更新（JA/EN 個別ページ・en-content.json・ui-terms.json）。card-data/supplement.js/
  star bin/archive/era/国/運動は不触（既存写真家）。未追跡=backup 2件+spec 1件（stage しない）。
- **フィデリティ**：本文 773→11,169字・出典 3→33・sup-ref 5→63。JA==EN cite 33 一致・dangling 0（両言語）。
  keywords は engine 改善どおり bundle 由来 8語自動（sidebar 先頭4）。description は lead 由来自動充填。
  Period 3箇所 `2000–2010s` 保持。
- **検証**：check_new_photographer OK / check_content_loss OK / preflight **FAIL 1件**＝
  「SFMOMA リンク消失 `.../artist/lieko_shiga/`」＝実体は URL 大小文字変更のみ（新は `Lieko_Shiga`・同一ページ・
  SFMOMA リンク自体は増加）＝content-loss ガードの case-sensitive 偽陽性。push 時 Daisuke 確認の上 --no-verify 案件。
  WARN 2件＝nosnippet 9→8/8→7（prep-block→実コンテンツ置換の正当減少・miyako と同型）。
- **発火した engine 改良**：keyword bundle 由来注入・description 自動充填・Period spec 化（いずれも正常動作）。
- **分業**：fable監督・Opusサブエージェント実装（41 tool uses / 約5.7分 / subagent約122kトークン）。

---

## 2026-07-02 — importer rev多桁span対応（lieko-shiga摩擦の源流つぶし・種別=engine・軽量行）

- **起点**：lieko-shiga刷新で素材の `rev19/20/21` span 計77個（rev19×35/rev20×29/rev21×13）が
  unwrap も self_check 残存assertも**両方すり抜け**、手動除去が必要になった。
- **原因**：`import_chatgpt_photographer.py` のrev処理4正規表現が `rev[0-9]`（1桁限定）。
  2桁クラスは REV_OPEN_RE 不一致で素通り、self_check も同パターンのため検知不能＝盲点が対称。
- **対応**：4箇所（REV_OPEN_RE / REVIEW_CSS_RULE_RE / self_check残存チェック2本）を `rev[0-9]+` へ。
  `test_importer_scaffold_inject.py` に `test_unwrap_rev_spans_multidigit`（多桁＋ネストunwrap・
  非revスパン保持・self_checkの多桁残存検知）を追加。
- **検証**：M4決定論テスト＋新テスト全PASS / lieko素材の再render（scratchpad出力のみ）でrev残存0 /
  preflight OK / check_content_loss OK / 差分2ファイルのみ。
- **分業**：fable監督・Sonnet委譲（初回1箇所で停止→再指示で完遂、計12 tool uses / subagent約79k
  トークン=うち約39kは停止分の無駄。この規模の数行修正は委譲オーバーヘッドの方が高い可能性あり）。
- **wall-time**：（Daisuke 記入）

---

### 2026-07-02〜03 — 運動「スティルライフ」新設＋6名再分類（other / コンセプチュアルアート解体2運動目）
- **内容**：movements/スティルライフ.html 新規（EN=Contemporary Still Life / slug contemporary-still-life・cite4本）。
  laura-letinsky / takashi-yasumura / valerie-belin / gabriel-orozco / anuschka-blommers-niels-schumm / roe-ethridge の
  6名を単独タグ/別名タグ→スティルライフへ。tillmans/shahbazi/rdland/mouleneはレビューで据え置き。
- **プール拡張初適用**：厳密105名に加え別名30名・無所属27名を含む155名から候補化（恒久ルール初回）。
- **bug/発見（3）**：①Sonnet委譲エージェントが実作業せず幻の再委譲→2回の再指示で完走（委譲プロンプトに
  「Agent系ツール禁止」を明記すべき教訓）②ffc7bdc4星binでスティルライフ行が既存行と同一行に連結される書式欠陥
  →監査で検出し改行修正③出典URL: MoMA /artists/ はcurl/WebFetch双方403でbot遮断＝検証不能→検証可能な
  Gagosian頁へ差し替え（AIC letinsky/Thames&Hudson/MoMA orozco展caléndarは200検証済）。
- **orozco特殊形**：title運動語なし→title不触。en-content JSONにキー無し→EN WARNは既知偽陽性。entry-metaバグ温存。
- **検証**：全カード面・leaf機能タグ・星binの残存ゼロ（channel/§REL/本文の正当残存は除外判定）/
  check_content_loss OK / preflight OK（WARN3=既知偽陽性のみ）/ 対象27M+新規2のみ巻き込みゼロ。
- **分業**：fable監督・監査（出典URL自主検証・bin書式修正含む）、Sonnet実装（計3ラウンド・セッション上限で1回中断）。
- **wall-time**：（Daisuke 記入）

（次の実案件からはこのテンプレで追記。空欄は「測れた範囲だけ」でよい。）

---

### 2026-07-03 — 運動「ポストインターネット」新設＋5名再分類（other / コンセプチュアルアート解体3運動目）
- **内容**：movements/ポストインターネット.html 新規（EN=Post-Internet Photography / slug post-internet-photography・cite5本、
  Vierkant論考PDF/UCCA2014展/New Museum(Ulman)/Aperture(Photography Is Magic)/Tate(Performing for the Camera)＝全URL挿入前検証済）。
  lucas-blalock / kate-steciw / artie-vierkant / sara-vanderbeek / amalia-ulman の5名を別名タグ「コンセプチュアル」→ポストインターネットへ。
  quinlan/eaton はレビューで見送り（素材主義的抽象・光学プロセス＝ネット流通と別軸）。mcginley はインティメイト候補へ送り。
- **命名調査**：Daisuke質問「世界共通の用語か」→Olson(2006–08)/McHugh(2009)/Vierkant(2010)/UCCA(2014)/Cotton『Photography Is Magic』(2015)で
  確立済みと確認。「ポスト写真」(Mitchell/Fontcuberta系の別概念)は併記せず切り離し（Daisuke承認）。
- **プール実測**：単独97＋別名27＋無所属25＝149名（正パーサ3条件）。プール外の全サイトledeスキャン＝該当ゼロ。
- **bug/発見（2）**：①Sonnet の step⑩ 一括regexが非greedy `.*?` で無関係カード30枚超を破損→Sonnet自身が diff --stat で検出し
  checkout--で復旧・article境界分割で再実行（最終diffは対象のみ）②era2000 EN再生成が志賀理江子の旧EN lede既存ドリフトを
  巻き込み→1行手動revertでスコープ維持（**既存ドリフトとして未解消・次のera2000再生成時に再浮上する**）。
- **教訓の効果**：委譲プロンプトに「Agent系ツール禁止」明記→幻の再委譲ゼロ・1ラウンド完走（前回3ラウンド）。
- **検証**：星bin=META1行追加＋d632c32e値5箇所のみ / 全カード面・leaf機能タグ置換済（channel/§REL/本文の正当残存のみ）/
  check_content_loss OK / preflight OK（WARN2=既知偽陽性）/ 26M＋新規2のみ巻き込みゼロ。
- **分業**：fable監督・監査（命名調査・出典検証・支給文字列作成・監査）、Sonnet実装（1ラウンド完走・216k tokens・160 tool calls・約12分）。
- **wall-time**：（Daisuke 記入）

## 2026-07-03 インティメイト・ライフ新設・12名再分類＋mvt-nav相互リンク一括更新（コンセプチュアルアート解体4運動目・最終）
- **対象**：新運動「インティメイト・ライフ」(Intimate Life / intimate-life) 新設。12名再分類=larry-clark/anders-petersen/
  goldin/elina-brotherus/diana-scheunemann/richard-billingham/j-h-engstrom/wolfgang-tillmans/manfred-willmann/
  paul-albert-leitner/hellen-van-meene/ryan-mcginley。goldinのみプール外（プライベート写真alias→私写真から移設・
  私写真ページ6→5名）。tillmansは3回目審査で採用（Cotton "Intimate Life"章の代表格＝最後の受け皿）。
- **命名**：JA/EN/slugともCotton章名準拠「インティメイト・ライフ」（"Intimate Photography"はブドワール検索衝突で不採用・Daisuke確定）。
- **差分**：修正49＋新規2（movements/インティメイト・ライフ.html、en/movements/intimate-life.html）＋nav一括（JA35＋EN34）。
  出典5本=Luhring Augustine/Aperture/MoMA calendar/MACK/Thames&Hudson（全URL WebFetch検証済・MoMA /artists/不使用）。
- **mvt-nav一括**：4運動完成を受け全35運動ページのnavを35項目正準ストリップへ統一（自運動is-active・ニュートポは
  デュッセルドルフ派の前・他3つは末尾）。EN全35slug再生成。
- **監査での検出・修正3件**（fable）：①petersen title旧era テーマ語残存→adams前例に合わせJA/EN SEO置換
  ②goldin側chip/kw欄がリンクなしspan（旧プライベート写真構造の引き継ぎ）→リンク化 ③私写真.htmlのgoldin本文言及3件=
  本文不介入原則で意図的据え置き（john-riddy前例と同型）。
- **地雷実績**：(g)志賀理江子era2000 ENドリフト=今回意図的更新として取り込み（Daisuke事前承認枠）。(h)scheunemann dual国籍
  Country欄=巻き戻りなし。billingham出典番号不連続[1,3,4,5]=既存バグ（本件と無関係・未対応）。
- **検証**：星bin=META1行＋12名のみ / check_content_loss=goldin意図的WARN1のみ / preflight OK（WARN=EN再生成の既知偽陽性）。
- **分業**：fable監督・監査（相談・命名・提案マップ・出典検証・支給文字列・監査修正3件・nav一括）、Sonnet実装
  （プール抽出45k＋本体実装315k tokens・計226+10 tool calls・約20分・1ラウンド完走）。
- **wall-time**：（Daisuke 記入）

## 2026-07-03 — 既存運動へ25名再分類（コンセプチュアルアート解体・第2弾＝新運動ページ作成なし・種別=other・軽量行）
- **対象**：単独タグ/空movementsの25名を既存13運動へ再分類（新運動ページなし）。FSA写真+5 / デュッセルドルフ派+2 /
  ニューカラー+3 / ストリート写真+4 / フォトジャーナリズム+2 / ストレート写真+1（weston既掲載） / モダニズム+1 /
  ピクチャーズ世代+1 / ステージド写真+4 / シネマトグラフィック写真+1 / ドキュメンタリー+1 / カラー写真+1 / タイポロジー写真+1。
  dual6名=meyerowitz/weston/levine/demand/casebere/graham（levine/demand/casebereは第2タグにコンセプチュアルアート維持）。
- **面**：supplement.js / 星bin(d632c32e。dcf38762は写真家12エントリにmovementsありだが25名該当なし・fbdfe095はcuratedConnections手書きペアでラベル整合のため、いずれも不触=fable監査で裏取り済) / JA leaf25枚機能タグ
  （標準型10=シェリー・レヴィーン型置換・eraテーマ語型15=adams/petersen前例・機関chip型4=運動chip先頭挿入+機関chip降格） /
  13運動ページカード+chips+件数3箇所 / card-data.json / archive+cards-archive+eras6 / EN JSON SEO 24名×7フィールド
  （weston EN=手書きタイトル保持で不触） / EN再生成（archive+taxonomy13+6+photographers25）。
- **地雷実績**：(h) ben-shahn/dorothy-bohm Country「リトアニア」和訳戻り2件revert（seymour/delano発生なし）。
  (g) era EN再生成の無関係ドリフト=なし（diffはtags/data-searchのみ）。
- **検証**：check_content_loss=OK / preflight=OK（WARN=EN再生成の既知偽陽性のみ） / 13運動ページ cards=hero=Photogs=chips 全一致 /
  件数ドリフト=実カード基準で存在せず（旧hero=旧実数一致・新hero=旧+追加数どおり）。
- **wall-time**：（Daisuke 記入）
- **分業**：fable監督・監査（提案マップ25名・dual/単独の判定・recon・委譲・監査=dcf38762実態裏取り含む）、
  Sonnet実装（セッション上限で1回中断→state実測+SendMessage再開で完走・計537k tokens・114 tool calls・約21分）。
- **wall-time**：（Daisuke 記入）

## 2026-07-03 — コンセプチュアルアート正規メンバー確定＋表記正準化（解体タスク2・種別=other・軽量行）
- **対象**：(a)タグから除去3名（mapplethorpe/pieter-hugo/mayumi-hosokura・他タグ残存）＋ページからカード除去 /
  (b)無所属化3名（seydou-keita=era1950テーマ語・eileen-quinlan/jessica-eaton=era2000テーマ語） /
  (c)ステージド写真へ移送4名（kaoru-izima/michael-janiszewski/sonja-braas/jean-pierre-khazem） /
  (d)表記正準化9名（kruger/sherman=多タグ内置換・sophie-calle/erwin-wurm/shannon-ebner/nikki-s-lee/james-welling=
  単独置換＋ページ掲載・sharon-lockhart/rashid-johnson=正準化のみ）。コンセプチュアルアートページ8−3＋17＝22名
  （A組12名=JS不変・掲載のみ）・ステージド写真7→11名。
- **面**：photographers.js+manual-additions.js+supplement.js / 星bin（d369d828=4名・d632c32e=14名。dcf38762=19名該当なし・
  fbdfe095=名前リストのみで不触） / JA leaf19枚機能タグ（title×3/meta/JSON-LD/ph-abstract定型文/breadcrumb/eyebrow/
  ph-kw/side-chip。無所属型=doisneau/kollar前例の空欄形・Channel行不介入） / 両運動ページカード+hero+chips
  （22・11一致） / card-data.json（機関・国タグ保持） / archive+cards-archive+eras6面 / EN JSON SEO 17名
  （sherman/mayumi-hosokura=SEO言及なしで不変・pieter-hugo/krugerはdescription内タグ列も修正） /
  EN再生成（archive+taxonomy2+eras6+photographers18・sherman=手書き保護スキップ→EN HTML直接2行修正=lee-miller前例）。
- **地雷実績**：(h) seydou-keita EN Country「マリ」和訳戻り1件revert（他発生なし）。(g) era再生成の無関係ドリフト=なし
  （JA/EN diffともtags/data-searchのみ・19名分と一致）。
- **残存チェック**：'コンセプチュアル'単独=19名スコープでJS/card-data 0件（残5件=sugimoto/morimura/hausswolff/sassen/
  mikhailov等スコープ外・aliasマップ行は保険で維持）。「コンセプチュアルアートアート」=全域0件。
- **検証**：check_content_loss=WARN2（kruger/mapplethorpe abstract定型文=意図的変更のみ） / preflight=WARN（EN再生成の
  既知偽陽性）＋FAIL1（sharon-lockhart dangling cite=既存バグ・HEAD比較で本件差分と無関係を確認済） /
  両ページ cards=hero=Photogs=chips 全一致（22/11）。
- **メモ**：eras/1970 mapplethorpe名「マッピルソープ」誤字（既存・不触）。mayumi-hosokura EN ph-kw=keywords_htmlが正本で
  SEO headフィールド外のため据え置き（JA/EN不整合1件・要判断）。en/movements/pictures-generation.html等の他運動ページの
  kruger/shermanカード旧表記=「他の運動ページ不変」原則で据え置き。
- **fable監査追記**：①push阻害FAIL=sharon-lockhart宙吊りcite（既知バグ・今回leaf接触で発火）→本文が名指しする出典3本
  （Hammer 2009展/公式スタジオ/MCA 2001回顧展・全URL WebFetch検証済）で出典欄を修復しpreflight exit 0へ。EN側はsup-ref
  リンク自体なし=自己整合で不触。②hosokura EN側side-chip「conceptual art」1個を手維持EN前例（sherman方式）で直接除去
  （§REL解説文のConceptual Art言及は本文不介入原則で意図的据え置き）。
- **分業**：fable監督・監査（提案マップ・lockhart出典修復・hosokura EN整合・監査）、Sonnet実装（watchdog停止1回→state実測
  +SendMessage再開で完走・計333k tokens・375 tool calls・約63分）。
- **wall-time**：（Daisuke 記入）

## 2026-07-04 — lieko-shiga § REF 写真集リンク追加（種別=other・軽量行）
- **対象**：§ REF「さらに読む / Further reading」に写真集ラベル＋Amazonアフィリエイトリンク4冊を追加（JA/EN各4冊・計8リンク）。
- **面**：photographers/lieko-shiga.html（`ph-rel-label` 直前へ挿入）・en/photographers/lieko-shiga.html（同構造・EN手組みページのため直接編集）。
- **本文根拠**：4冊とも既存本文（螺旋海岸=北釜での中心的仕事、CANARY=2000年代半ばの初期代表作、Blind Date=丸亀市猪熊弦一郎現代美術館個展、Lilly=CANARYと同時期の初期作品集）に基づくnote文で新規事実の追加なし。
- **検証**：`git diff --stat` で対象2ファイルのみに差分を確認。amzn.to URL 8本を目視突合（JA4/EN4・取り違えなし）。
- **wall-time**：（Daisuke 記入）

---

## 2026-07-05 — yurie-nagashima（update / 既存刷新・idx245・era1990）

- **wall-time**：約13分（Daisuke 申告・2026-07-05）
- **bug**：0（engine 正常。素材側に revision-* span 混入＝素材品質問題、下記手作業3）。
- **手作業点（実測）**：
  1. **バックアップ**：JA+EN 両ページを -backup.html にコピー。
  2. **spec.json 手作成**：derive_spec から years/period(`1990–2000s`・素材の`1990s—2020s`は不採用)/era/idx 引き継ぎ。
     movements は既存 chip `私写真`/`フェミニズム写真` を carry-forward（JA/EN 運動ページ実在確認済）。
  3. **revision-* span 除去**：素材 JA/EN 双方に `revision-fifth/third/sixth/red/fourth/new` span 計85個/ファイル混入。
     07-02 の engine fix（rev多桁span対応）は `rev[0-9]+` 数字形のみ対応で**語形 `revision-<word>` は素通り**
     → JA レンダ出力・EN バンドル出力双方からテキスト保持・ネスト対応(innermost-first)で除去。残存0検証済。
     **2件連続発生＝importer unwrap を `revision-*` 語形へ拡張するか、素材プロンプトで rev-highlight 抜き出力を徹底する価値あり**。
  4. **carry-forward 不要**：素材が §REF(13リンク)/§REL(6件=写真家4+運動2)/出典(38) すべて充実・「準備中」マーカー0。
     keyword chip は素材 rich 版6語（engine 改善どおり bundle 由来）。
  5. **EN field-merge**：bundle 出力を en-content.json 既存エントリへ空値スキップ merge（更新15フィールド・
     保全4=photobooks 229/external_links 660/footer 468/jsonld 2056）。他 slug 差分0 assert・末尾改行なし dump。
  6. **ui-terms 追加 2件**：works_labels「TOP Museum - 展覧会作品」「TOP Museum - 黄色い野生の花」
     （untranslated WARN 2件解消・EN素材の "Exhibition Works"/"Yellow Wildflowers" 表記に統一）。
- **サーフェス変更数**：4ファイル更新（JA/EN 個別ページ・en-content.json・ui-terms.json）。card-data/supplement.js/
  star bin/archive/era/国/運動は不触（既存写真家）。未追跡=backup 2件+spec 1件（stage しない）。
- **フィデリティ**：本文 787→9,849字・出典 3→38・sup-ref 5→88・§REL 2→6・作品リンク 0→3。
  **JA==EN cite 38 / supref 88 一致・dangling 0（両言語）**。Period 3箇所 `1990–2000s` 保持・description lead 由来自動充填。
- **検証**：check_new_photographer OK / check_content_loss OK / preflight **OK・FAIL 0**。WARN 2件のみ＝
  nosnippet JA 9→8 / EN 8→7（prep-block→実コンテンツ置換の正当減少・lieko/miyako と同型）。
  GA/canonical/hreflang/OG/JSON-LD 引き継ぎ・§REL 全リンク（JA root絶対形式・EN /en/ 形式）の実在を監督側で独立再確認。
- **発火した engine 改良**：keyword bundle 由来注入・description 自動充填・Period spec 化（正常動作）。
- **分業**：fable監督・Opusサブエージェント実装（48 tool uses / 約6.4分 / subagent約68kトークン）。

---

## 2026-07-05 — importer時間短縮①②実装（yurie実測起票の源流つぶし・種別=engine・軽量行）

- **① revision-* 語形unwrap拡張**：rev処理の正規表現4箇所を共通トークン `REV_CLASS_PAT`
  （`rev[0-9]+|revision-[a-z0-9]+(?:-[a-z0-9]+)*`）へ統一し、yurie素材で85個/ファイル手除去した
  `revision-fifth` 等の語形に対応（数字形は07-02対応済）。self_check の残存検知・レビューCSS除去も
  同トークン化＝盲点の対称性を排除。`test_unwrap_revision_word_spans` 新設（語形unwrap・ネスト・
  非rev保持・self_check検知）。**yurie実素材で検証＝JA/EN各 rev span 55→0・CSSセレクタ残0・
  span開閉均衡・render指標が committed ページと一致**。spec.md §13 に「レビュー用ハイライトを
  素材に含めない」源流カット項を追記。
- **② --prepare 実装**：`--update-existing --prepare` で update案件冒頭の定型準備
  （JA/EN→-backup.htmlコピー・derive_spec→scripts/<slug>-spec.json書出）を一括化。
  **既存 backup/spec は上書きしない**（変更前状態の保全が目的のため）。period/movements の
  人間判断は書出後のspec編集に残す。yurieで両パス実機検証（既存スキップ／新規作成→git復元で原状回復）。
- **検証時ヒヤリ**：新規作成パス検証でJA/EN backupを同一scratchdirへ退避→同名衝突でJA原本消失
  →git履歴(a83f49c6e^)から完全復元・cmp一致確認済。教訓＝同名ファイルの退避はサブディレクトリを分ける。
- **サーフェス変更数**：3ファイル（import_chatgpt_photographer.py / test_importer_scaffold_inject.py /
  importer-scaffold-inject-spec.md）。ページ本文・正本は不触。
- **検証**：importer全テストPASS / check_content_loss OK / preflight OK。
- **wall-time**：（Daisuke 記入）

## 2026-07-05 — lieko-shiga EN写真集AmazonリンクのJSON同期（種別=other・軽量行）

- **対象**：264beb05a でEN HTMLへ直接追加されたAmazonリンク4冊が EN正本 `photobooks_html` 未反映＝`--force`再生成で消失する状態を解消。
- **面**：data/photographers-en-content.json のみ（1フィールド・-1/+1行）。§REFのAmazon 4冊は `rebuild_further()`→`parse_photobooks()` 経由の `photobooks_html` 由来、MoMA/Gettyは `external_links_html` 由来（不触）と特定。
- **検証**：再生成HTMLが現行と**byte一致**（cmp＋監督側の独立再ビルドでも差分0）。他slug差分0・check_content_loss OK・preflight OK。
- **分業**：fable監督・Sonnetサブエージェント実装（14 tool uses / 約2.9分 / 約46kトークン。初回spawnが誤待機停止→再指示1回）。
- **wall-time**：（Daisuke 記入）

## 2026-07-05 — mika-ninagawa 刷新（update・新素材差し替え）＋③④実装初実走＋Amazonリンク13本

- **種別**：update（既存815字→新素材6143字の全文刷新）。素材=re-photographer/mika-ninagawa.html（JA/EN・v5.1 ph-*）。
- **③④をこの案件で実装**（Daisuke指示どおり実案件検証しながら・Opusサブエージェント実装/fable監督）：
  - **③ `--merge-to-en`**＝EN field-merge のCLI化。既定dry-run（field別 add/replace/preserve/skip-empty計画表示）→`--apply`でatomic書込。skip-empty・他slug/_meta byte不変assert・違反時ロールバック・HAND_MAINTAINED_EN拒否・末尾改行なしdump（round-trip byte一致実測）。
  - **④ `--update-existing --apply`**＝carry-forward実適用の解禁実装。安全契約(a)-(f)全部=--applyなし常時dry-run／backup必須（--prepare前段）／render→description注入→§REFスプライス／適用後検証（§REF実在・フィデリティ非減少・dangling 0・check_content_loss）／失敗時自動ロールバック／書込対象1ファイル限定。
- **engineバグ発見1件（修正済）**：①のREV_CLASS_PATが**裸 `revision`（接尾辞なし）とspan以外の要素class属性**（`<p class="revision">`×27）を素通し。→PAT拡張＋`strip_rev_class_tokens()`（全要素class属性からトークン単位除去・review/revisionist等は誤爆ガード）＋self_check全要素化。テスト追加。修正後再適用でrev 0。
- **実走**：--prepare→④apply（1回目でrev残存発見→importer修正→再apply）→③apply→build --force。works固有名 ui-terms 1件追加（東京都庭園美術館 - 瞬く光の庭）。
- **結果**：本文815→6143字・出典5→30・sup-ref 5→64（JA==EN 65一致・dangling 0）・§REL 1→6件・作品リンク0→5。check_new_photographer/check_content_loss OK。
- **preflight**：FAIL 1件=EN正本の旧公式バイオURL消失（www.mikaninagawa.com/html/biography/→mikaninagawa.com/biography/への意図的置換・新URL 200確認済）＝jikei同型の正常フラグ。WARN=data-nosnippet減（scaffold正典標準数）。
- **Amazonリンク**：JA7冊（§REF内ph-book）/EN6冊（正本photobooks_html経由→再生成）。タイトル・出版社・年はAmazon実ページから取得（Sonnetサブエージェント）、一言解説は商品説明＋本文出典済み記述＋nippon.com裏取り（Pink Rose Suite=木村伊兵衛賞対象）準拠・捏造なし。
- **分業**：fable監督・監査／Opus=③④実装＋①穴修正（2走・計約70万tok）／Sonnet=Amazonタイトル・説明取得（2走・計約10万tok）。
- **wall-time**：約26分（Daisuke実測。③④実装＋①穴修正＋Amazonリンク13冊を同一案件に同梱した時間）

## 2026-07-07 — yuki-onodera 刷新（update・新素材差し替え）＋改善2件実装（works ui-terms自動化・intentional-replacements宣言）

- **種別**：update（既存763字→新素材9763字の全文刷新）。素材=re-photographer/yuki-onodera.html（JA/EN・v5.1 ph-*・clean＝revision残存0）。
- **改善2件をこの案件で実装**（Daisuke指示どおり実案件検証しながら・Opus監督/Sonnetサブエージェント実装）：
  - **① works固有名 ui-terms 自動化**：`--merge-to-en` 時にJA/EN素材のworksチップをURL突き合わせ→CJK JAラベルの英訳を `photographers-en-ui-terms.json` works_labels へ自動追記（既定dry-runで追記案表示・`--apply`で書込・既存差異値は上書きせずconflict報告）。新関数 `propose_works_ui_terms`/`works_ui_terms_plan`/`apply_works_ui_terms`＋`_extract_works_by_class`（本文＋ph-side-works両方）。既存 `_extract_works` は不改変。**Onoderaで5件自動追記→EN再生成のuntranslated works label WARN=0**（従来は毎案件必ず1回の手作業）。
  - **② intentional-replacements 宣言ファイル**：`scripts/intentional-replacements.json`（`{slug,url,reason,declared}` の使い捨てリスト）＋preflight `check_content_loss_guard` を (slug×url) 部分一致で消失HARDから除外。`_filter_loss_items_by_declarations` は純関数（unit検証）。消費宣言はINFO・不一致宣言はstale WARNで削除を促す。origin/main合流後は自然にstale化＝自動失効。目的は**--no-verify全素通しの回避**（jikei・mikaで2回発生の意図的URL置換FAILをスコープ限定でPASS）。
- **手作業1件（§REL手復元）＋guard-hole発見**：新素材に§RELセクションが無く、carry-forward render が§RELを`準備中`にして既存の「コンセプチュアルアート」運動関連を暗黙ドロップ。`_apply_update_existing`の安全チェックも`check_content_loss.py`も§REL件数を追跡せず（cite/section/FIG/thesis/leadのみ）＝無警告ですり抜ける穴。backup(457行)からverbatim復元（捏造なし・新本文のconceptual photo記述と整合）。→**§REF同様の§RELスプライス/件数ガードは未実装＝次案件の改善候補**。
- **実走**：--prepare→④--update-existing --apply --force→③--merge-to-en --apply→build_photographers_en.py --slug --force→--dry-run（SKIPPEDなし）。
- **結果**：本文763→9763字・出典4→32・sup-ref 5→59・作品リンク0→5・§REL 1（手復元）。EN merge=add4/replace9/preserve5/skip-empty10（site_directory/external_links/photobooks は空bundleのためpreserve）。en-content.jsonは yuki-onodera キーのみ変更・他slug不変。check_content_loss OK。
- **preflight**：**OK**（FAILなし＝intentional-replacements.jsonは`[]`。今回は意図的URL消失が発生せずmika型FAILなし）。WARN=data-nosnippet減（8→7/9→8・scaffold正典標準数）。importer test 5/5 PASS。
- **分業**：Opus監督・レビュー（source探索・pipeline確定・feature設計・§REL復元判定・出力全検証）／Sonnetサブエージェント実装（pipeline実走＋feature①②実装＋検証・約18万tok・113 tool uses）。
- **wall-time**：22分（Daisuke実測。内訳の主因＝Sonnet実装+検証走 約15分（うち改善2件のimporter/preflight実装+unit/rebuild検証、§REL穴の調査+手復元）／素材フォルダ探索（repo外・記載名と不一致）数分／監督のcontext構築+出力レビュー）。§REL保留・push。

## 2026-07-08 — yuki-onodera 写真集Amazonリンク（JA3冊/EN4冊）＋§REL関連写真家3名（種別=other）

- **種別**：other（既存ページへの追記のみ。本文・thesis・出典は不触）。**Codex CLI を実装役に使った初案件**。
- **面**：3ファイル（`photographers/yuki-onodera.html` +35行 / `data/photographers-en-content.json` +6-3行 /
  `en/photographers/yuki-onodera.html` +39行＝正本JSONから再生成）。EN HTML直編集なし。
- **調査（監督側・捏造防止）**：渡されたのは `amzn.to` 短縮URL 7本のみで書名不明。curl でリダイレクト解決→ASIN確定
  （JA: 4891764775 / 4473036650 / 4902080478、EN: 1590050274 / 159005086X / 4473036669 / 4902080478）。
  AmazonはWebFetch 500で読めず、書名・出版社・年は**公式 yukionodera.fr/en/publications/**（既存cite同源）と
  ISBN照合で確定。淡交社の連番2冊（…3665-0=JA版 / …3666-9=EN版）と Nazraeli 2冊（How to Make a Pearl 2002 /
  Transvest 2004）の対応もここで分離。第28回木村伊兵衛賞（カメラキメラ）は**東文研アーカイブDB**で裏取り（本文に未記載の新情報）。
- **§REL**：既存は運動1件のみ。関連写真家3名を追加＝杉本博司（装置・露光条件の主題化）/ 石内都（他者の衣服＝
  《古着のポートレート》と主題共有）/ ソフィ・カル（規則駆動の連作・パリ拠点）。EN は `related_annotations` 3件追加で
  ビルダーが §REL へ注入。ボルタンスキーは本文言及ありだがサイトに個別ページ無しのため見送り。
- **分業**：**Opus監督・監査／Codex（gpt-5.5・reasoning=high）実装**。Codex呼び出しは1回（MCP `mcp__codex__codex`、
  `sandbox=workspace-write` / `approval-policy=never`）。事実・書名・解説文は全て監督側で確定してから渡し、
  Codexには「一字一句そのまま使う・Web検索禁止・触ってよいファイル2つのみ」を明示。**Codexのバグ0・逸脱0**。
- **落とし穴（事前に潰した）**：`photographers-en-content.json` は 26,711行。素朴な `json.dump` だと全体が再整形される。
  `json.dumps(d, ensure_ascii=False, indent=2)`（**末尾改行なし**）でバイト一致することを監督側で先に実測し、Codexに強制。
  結果、JSON差分は3キー6行のみ・他297ページ byte不変を確認。
- **EN正規化の把握**：正本の `book-card` / `affiliate-disclosure` / `data-affiliate-section` はビルダーが
  `ph-book` / `ph-aff`（"* Affiliate link"）へ正規化する（長島ページと同型）。EN HTML側に book-card は現れないのが正。
- **検証**：JA3本/EN4本のリンクが**言語別に正しく分離**（相互混入0）・`rel="noopener sponsored"` 全数付与・
  check_content_loss OK・preflight OK・ビルダー再実行で冪等・SEO一式（GA/canonical/hreflang/OG/JSON-LD）維持・
  cite数/section数/further-links数 不変・依頼対象外ファイルの巻き込み0。
- **Codexのトークン使用量は取得できず**：MCP経由（`mcp__codex__codex`）の応答に usage が含まれないため。
  測るなら Bash の `codex exec --json`（`turn.completed.usage`）で回す必要がある。
- **wall-time**：（Daisuke 記入。監督側の実測は開始14:33→終了14:54＝約21分。うち大半は書名・出版社・年の裏取り調査）

## 2026-07-08 — EN §REL 誤情報除去（8ページ）＋entry-meta Country修正（2ページ）＋ENビルダー2バグ修正（種別=engine+other）

- **発端**：「JA §REL が空のページを年代ごとに埋める」タスクの残り10ページを片付ける依頼。着手前の実測で
  **10ページ全部が本文「準備中。」・出典0・thesis無しのスタブ**と判明（`§REL` が空なのは書き忘れではなくページ自体が空）。
  本文根拠ゼロで関連写真家を並べるのは捏造になるため、**§REL記入は本文執筆待ちとして中止**。実行可能な部分だけへ再スコープ。
- **やったこと**
  1. **EN の誤「Related photographers」撤去（8ページ）**：`collectif-fact / eve-sussman / g-r-a-m / multiplicity /
     ohio / the-atlas-group-walid-raad / useful-photography / wangechi-mutu`。JA が「準備中」なのに EN だけ
     `site_directory`（名簿の近傍エントリ＝相互に指し合う無関係5名）が §REL 見出し下に出ていた＝**本番に出ていた誤情報**。
     正本 `data/photographers-en-content.json` の `site_directory_html` を `""` にして `--slug` 再生成。
  2. **entry-meta Country バグ修正（2ページ）**：`gabriel-orozco`（→メキシコ）/ `fabian-marti`（→スイス）。
     `<dt>Country</dt>` の dd に era 文字列が入っていた。国は `card-data.json` の nationality（MX / CH）が根拠。
     JA を直し `rebuild_entry_meta()` の翻訳経由で EN も追従（EN HTML 直編集なし）。
- **ENビルダーのバグ2件を修正**（`scripts/build_photographers_en.py`）
  - **① 混在チップの国名が未翻訳**（memory「dual国籍chip和訳戻り」の正体）。`_translate_node()` の
    `re.fullmatch(r'<a …>(.*?)</a>')` が `.*?` で `</a> / <a>` を飲み込むため、`<a>イギリス</a> / <a>アメリカ</a>` も
    `ケニア / <a>アメリカ</a>` も丸ごと `_translate_compound` に渡り未翻訳のまま残る。アンカーごと／裸断片ごとに
    独立翻訳するよう修正。**該当9ページ**（eve-sussman, the-atlas-group, wangechi-mutu ＋ **未再生成の時限爆弾6件**：
    alexander-gardner, beato, coburn, manray, muybridge, riis）。この6件は EN が現在正しいが、次に `--slug` を
    掛けた瞬間に日本語へ退行するところだった。回帰テスト `scripts/test_build_en_chip_translation.py` 新規（4ケース）。
  - **② §REL を削除でなく prep-block に**。`rebuild_related()` は people/movements が両方空だと §REL セクションごと
    削除する仕様で、`check_content_loss.py` が「本文セクション1個消失」→ **preflight HARD FAIL**。しかもこの消失種別は
    `scripts/intentional-replacements.json` では**原理上宣言できない**（preflight.py の docstring 参照）。
    セクションを残して `<div class="prep-block" data-nosnippet>In preparation</div>` を出すよう変更。
    結果ガードはグリーンのまま、**JA（§REL＋準備中）と EN で構造が揃う**。
- **やらなかったこと（実測して「バグではない」と判明）** — 2件とも危うく2ページだけ直して不整合を作るところだった
  - `<dt>Years</dt>` の空欄：JA写真家299ページ中 **153ページが空**＝生没年サイト未記載時の標準。orozco だけ行を消すと逆に不整合。
  - `ph-hero__meta-item` / `ph-side-meta-row` / 埋め込みJSON の Country に era 文字列：**147ページが同じ形**
    （国名表示は152ページ）。era表記backfill（ec317aa3e）が entry-meta だけ直して残りを温存した既存不整合。別タスク。
- **効果**：`sync_en_rel_annotations.py --audit` の review items **70 → 54**（C分類「JA準備中×EN汎用リンク」16件が消滅）。
  なお audit の残 54 のうち **44 items は slug 偽陽性**（JA=`jp-中山岩太.html` / EN=`iwata-nakayama.html` の対応表欠落）。
- **分業**：**Opus監督・調査・設計／Sonnet実装**（サブエージェント2回）。1回目は指示の前提誤り（「サイドバーは既に正しい」）と
  `--force` 由来の退行3件を**自分で検知して停止・報告**＝正しい振る舞い。2回目でビルダー修正＋再生成。
  Opus 側は「バグに見えるものが実はサイト標準」を2回とも実測で捕まえた（Years / hero Country）。
- **検証**：`check_content_loss.py` OK（消失なし）／`preflight.py` **exit 0**（WARN 2件は orozco・fabian-marti の
  「EN HTML直接編集の疑い」＝JA正本追従の再生成に対する既知の誤検知）／時限爆弾6ページの diff 0／
  退行3ページの国名 diff 0／GA・canonical・hreflang・OG・JSON-LD 維持／`--all` 不使用・対象外ファイル巻き込み0。
- **wall-time**：（Daisuke 記入。監督側の実測は調査〜検証完了まで約35分。うち大半は「本当にバグか」の実測4回）

## 2026-07-09 — asako-narahashi（new / 新規追加・楢橋朝子・idx300・era2000）＋engine robustness 2件（Codex実装）

- **種別**：new（純・新規追加）。素材=re-photographer/asako-narahashi.html（JA/EN・v5.1・clean）。
  読み=**Asako**（依頼文の「asaka」は誤り。楢橋朝子＝Asako Narahashi）。slug=asako-narahashi。
- **分業**：**Opus監督・監査／Codex（reasoning=high・MCP mcp__codex__codex）実装**。監督側で全判断
  （spec.json 全項目・idx・era・starText・citations・movementSlugJa・両renderの read-only 事前検証・
  card 文字列と挿入アンカーの確定・ui-terms 英訳語の確定）を先に固め、Codex には決定論コマンド列と
  byte-exact な挿入スクリプトだけを渡した（Web検索禁止・触ってよいファイル明示）。
- **判断点（実測）**：
  1. **era=2000 / movementSlugJa=風景写真**：素材の side Movement は 日本写真 だが、EN 翻訳可能で
     ジャンルを正確に表す **風景写真（→Landscape Photography・STUB_TO_SLUG 在）** を Movement 欄に採用。
     eyebrow/channel は 日本写真。star 用 movements=[風景写真, 写真集文化, 日本写真]。
  2. **運動ページ面＝なし**：3運動（自主ギャラリー/写真集文化/風景写真）とも movements/*.html が未存在。
     plan_surfaces は存在フィルタで自動 skip。§REL の運動リンクは importer が自動 de-link（dangling 0）。
     新規運動ページは作らない（依頼「あれば」＝該当なし）。
  3. **§REL**：JA/EN とも関連写真家3名（森山大道/石内都/マーティン・パー＝素材の一言解説つき・実在ページ）で対称。
- **engine robustness 2件（durable・別バグ）**：`add_photographer.py` と `preflight.py` の
  `js_existing_ids`/`eval_photographers` が osascript(JavaScript) の稀な**前後警告行混入**で
  `json.loads` "Extra data" → add_photographer は**クラッシュ**、preflight は**重複チェックを黙ってスキップ**。
  両者を「先頭が `[` の行だけ拾う」ループに変更（既存の "known非ブロック" スキップも解消＝dedup が実走するように）。
- **面**：tracked 14（archive/cards-archive 各JA・card-data・countries japan JA/EN・en-content(+127)・
  ui-terms(+2key)・supplement・star bin・en/archive・eras2000 JA/EN・add_photographer・preflight）＋
  new-design/cards-archive.html（**git-ignore なので diff 非表示・disk 上は投入済**）＋新規 JA/EN 個別ページ2・spec.json。
- **手作業1件**：EN untranslated 2件を ui-terms へ。works_labels `"MOMAT - 楢橋朝子 所蔵作品" →
  "MOMAT — Works by Asako Narahashi"`（EN素材の同URL チップが正）、terms `"NU・E"→"NU・E"`（誌名・恒等）。
  → EN 再ビルドで untranslated WARN 0。
- **フィデリティ**：JA 本文 4節・31 cite・66 sup-ref・dangling 0。EN 4節・§REL 3名・dangling 0。
- **検証**：check_new_photographer OK（en_graph_absent=EN標準WARN）／check_content_loss OK／
  **preflight exit 0**（残WARN2＝en/countries/japan・en/eras/2000 の「直接編集疑い」＝scoped 再生成に対する
  既知の誤検知・07-08 と同型）。`--all` 不使用・link_country_keywords 不実行・対象外巻き込み0。
- **Codex 挙動**：逸脱0。Step1 で私の grep -c 閾値ミス（cite は1行に集約→行数=1）を正しく FAIL 検知して停止＝
  正しい振る舞い（実カウントは31で正常と監督側が確認）。Step4 の osascript バグも停止・報告。
- **backup（未追跡・GH Pages 実機確認後に削除）**：card-data-backup.json / -supplement-backup.js / star -backup.bin。
- **wall-time**：24分（Daisuke 実測）。

---

## 2026-07-10 — GSC由来 SEO メタ修正（JA・杉本博司 / archive）

- **種別**：other（メタのみ・本文ゼロ変更）／**wall-time**：__分（Daisuke 記入）
- **面（tracked 3）**：`photographers/hiroshi-sugimoto.html`・`archive.html`・`scripts/build_archive_en.py`
- **入力**：GSC 2026-06-10〜07-07 のページ/クエリCSV。JA課題は CTR ではなく順位。
- **変更**：
  - 杉本：title/og:title/twitter:title の3箇所を `日本写真とコンセプチュアル` → `海景・劇場・ジオラマから読む写真表現`。
    素クエリ「杉本博司」42位に対し「杉本博司 カメラ」9.75位＝修飾語つき複合クエリを取る判断。
    あわせて JSON-LD `birthDate` の era 混入 `1970` → `1948`（根拠＝同ページ `Years: 1948–`。外部調査不要）。
  - archive：title 3箇所 `写真家アーカイブ｜時代・国・運動から探す` → `写真家一覧｜写真史を時代・国・運動から探す`。
    description 3箇所は「写真家アーカイブ」→「写真家一覧」の1語のみ。5.94位 / CTR 0% への対処。
    H1「カードで読む写真史」・ナビUI の「アーカイブ」表記は据え置き（サイト内概念）。
- **地雷1件（事前検知・対処済）**：`build_archive_en.py:433-436` が archive.html の title/desc を**完全一致で置換**し、
  不一致で `SystemExit('Chrome string not found')` ハード停止する。JA_TITLE/JA_DESC を同一差分で同期。
  EN_TITLE/EN_DESC は不変 → `build_archive_en.py` 実行後も `en/archive.html` はバイト不変を実測確認。
- **ガードの穴（記録のみ）**：`check_content_loss.py` の `SCOPE_DIRS` は `photographers`/`en/photographers` のみ＝
  `archive.html` は本文消失ガードの対象外。今回はメタのみなので実害なし。
- **検証**：check_content_loss exit 0／preflight OK。残WARN2件（`en/photographers/eugenesmith.html`・`moriyama.html`）は
  **並行実行中の別セッション（EN作業）由来**で本作業の差分ではない。`git diff` は12挿入/12削除＝全てメタ行。
- **副産物（別タスクへ切り出し）**：
  - JSON-LD `birthDate` の era 混入が他に約17件（16件が era 年代と完全一致＋2件が `"2000s / 2000年代"` 等の不正 Date）。
    杉本以外は `Years` 欄も年代文字列で**正しい生年がページ上に無く、外部出典の裏取りが要る**ため分離。
  - `sitemap.xml` が `new-design/<slug>.html` を **325 URL** 送信。全ページ `robots: index,follow` かつ
    canonical は `photographers/` を指す＝正規化で必ず捨てられる重複。GSC 実データにも1件も出現せず。
- **Codex 挙動**：逸脱0。read-only での方針レビュー→workspace-write で実装。
  レビュー時に `twitter:title` の存在を指摘（監督側の grep 見落とし）＝有効な貢献。
  実装後に `new-design/hiroshi-sugimoto.html` の旧title残存を自主報告（canonical で正規化されるため実害なし）。
- **分業メモ**：判断（クエリ解釈・title文言・スコープ切り分け）は Opus、機械置換と検証実行は Codex。

## 2026-07-10 — GSC由来 SEO メタ修正（EN・別セッション作業／JA側で合流検証）

- **種別**：other（入口のみ・本文/出典/注番号ゼロ変更）／**wall-time**：__分（Daisuke 記入）
- **面（tracked 4）**：`data/photographers-en-content.json`（lead_html 2件）・`en/photographers/moriyama.html`・
  `en/photographers/eugenesmith.html`・`en/photographers/sibylle-bergemann.html`
- **入力**：GSC 同期間。EN は表示回数が JA を圧倒するのに CTR ほぼ0（moriyama 1172表示/1click、eugenesmith 853/1、sibylle 683/0）。
- **変更**：
  - moriyama：lead に are-bure-boke の語義と Provoke 文脈を1文追加（`are bure boke meaning authoritative source` 系クエリ群に対応）。
  - eugenesmith：lead に 1971年移住・Aileen Mioko Smith・チッソ・3か月予定が3年 を1文追加
    （`w. eugene smith minamata duration stay` / `why did w. eugene smith go to minamata` に対応）。
  - sibylle-bergemann：title系4箇所（`<title>`/`og:title`/`twitter:title`/JSON-LD `name`）を
    `East German Photography, Fashion and Das Denkmal` → `East German Photographer of Fashion, Portraits and Das Denkmal`。
- **合流時の監督側検証（JAセッション＝Opus が実施）**：
  - **捏造チェック合格**。EN lead の追加事実はいずれも JA 正本に裏付けあり。
    eugenesmith → JA本文「アイリーン・美緒子・スミスの共同作業であり、当初3か月予定だった滞在が3年に及んだ」「1971年には水俣病の現場を記録するため日本へ渡り」。
    moriyama → JA本文の MoMA 出典*4「プロヴォークのアレ、ブレ、ボケが…フォトジャーナリズムや直截的な商業写真に寄りがちだった日本の写真文化を揺さぶろうとした」＋「Provoke, 1968–1970」。
  - **巻き戻りリスク検証**：`sibylle-bergemann` は `photographers-en-content.json` の 302 ページに**存在しない**。
    `build_photographers_en.py --slug sibylle-bergemann --dry-run` → `no harvest content, skipped`（0 page）＝
    **ビルダーが上書きし得ない**ので EN HTML が正本。`--all` を回しても巻き戻らない。
  - `--slug moriyama` / `--slug eugenesmith` の dry-run は **SKIPPED せず**（CLAUDE.md 必須検査を通過）＝ JSON 正本と HTML が整合。
- **検証**：check_content_loss exit 0／preflight OK。
  残WARN2種は**いずれも想定内**: ①eugenesmith/moriyama の lead 文面変化（＝意図した加筆）
  ②sibylle の「EN HTML 直接編集疑い」（＝builder 対象外のため WARN の助言「JSONを直して再生成」は本ページには当てはまらない・既知の誤検知）。
- **分業メモ**：EN 実装は別セッション、合流時の消失/巻き込み/巻き戻り検証と push は JA セッション（Opus）。

## 2026-07-10 — sitemap.xml から new-design/ の 325 URL を除去＋生成元を修正

- **種別**：other（sitemap とその生成元のみ。HTML・本文・出典・メタはゼロ変更）／**wall-time**：__分（Daisuke 記入）
- **面（tracked 2）**：`sitemap.xml`（1300行削除・追加0）・`scripts/generate_sitemap.py`（+3行）
- **入力**：直前エントリの「副産物」として切り出した課題。
- **前提の訂正 — 重要**：直前エントリは 325 URL を「robots: index,follow ＋ canonical が `photographers/` を指す
  ＝正規化で捨てられる重複」と記録したが、**誤り**。実際は **全 325 URL が本番で 404**。
  `new-design/` は `.gitignore:12` で除外されており git 追跡ファイル 0 件＝**デプロイされていない**。
  curl で 6 カテゴリ全て 404 を実測（`<slug>` / `movements/` / `jp-` / `eras/` / `index.html` / `cards-archive.html`）。
  対して `photographers/ansel-adams.html` は 200。GSC に出現しない理由も「canonical で除外」ではなく 404 と考えるのが自然。
- **根本原因**：`generate_sitemap.py:27` の `REPO_ROOT.rglob("*.html")` が **git ではなくディスクを走査**するため、
  gitignore 済みの `new-design/` のローカル 286 ファイルを全部拾う。時系列が符合する：
  `dd8bc74cf`(2026-06-08) new-design を git から削除 → `4ea56655b`(2026-06-12) gitignore 追加 →
  `1e5d0ab7b`(2026-06-19) sitemap 再生成で **ディスクから 325 件が復活**。
- **325 件の内訳**：写真家 `<slug>.html` 265 ／ `movements/` 31 ／ `jp-<日本語名>.html` 16 ／ `eras/` 11 ／
  `index.html` 1 ／ `cards-archive.html` 1。
- **変更**：
  - `sitemap.xml`：`<loc>` に `/new-design/` を含む `<url>` ブロック 325 個を外科的に除去（325×4行＝1300行）。
    **再生成はしない**。残る 748 ブロックはバイト不変（`git show HEAD:sitemap.xml` を同条件でフィルタ→`cmp` 一致で証明）。
    loc 1073 → 748。
  - `generate_sitemap.py`：`html_files()` の `templates/` スキップの隣に `rel.startswith("new-design/")` スキップを追加。
    末尾スラッシュ必須なので `new-design-foo.html` を誤爆しない。
- **不採用の選択肢（記録）**：
  - `new-design/*.html` に `robots: noindex` → **無意味**。本番にファイルが無く Google が meta を読めない。
  - `new-design/` 自体の削除 → **反対**。`cards-archive.html` がカードの正データ（CLAUDE.md 7項）。SEO 上は既に無害。
  - sitemap 再生成 → **今回は不可**。`lastmod` が mtime 由来で **728 件 churn** し、無関係差分で diff が読めなくなる。
- **触っていないもの**：`new-design/` 配下は 1 バイトも変更なし。sitemap の `<loc>` 行を消すこととファイルを触ることは別問題。
  TOP12 カード・フィルター/ソート UI・カード JS も無変更。
- **検証**：`grep -c "<loc>" sitemap.xml` = 748 ／ `grep -c "<loc>.*new-design"` = 0 ／ XML パース OK ／
  check_content_loss exit 0 ／ preflight OK ／ `git diff --stat` = 2 files, +3 / -1300 ／ 未追跡 10 件は未 stage。
  **巻き添え除外の否定**：パッチ後の生成元を書き込みなし dry-run したところ、現行 748 URL が **1 件も落ちない**
  （`cur - new = 0`）＝正規ページを誤って除外していない。
- **副産物（別タスクへ切り出し）**：パッチ後の再生成は **実在する未掲載ページ 18 件**を新たに拾う
  （`en/photographers/asako-narahashi.html`・`en/movements/new-topographics.html` 等、200 実測済）。
  ただし同時に `lastmod` 728 件が churn するため分離。sitemap 追加は別途 Daisuke 判断。
- **Codex 挙動**：逸脱 0。診断は監督（Opus）が実施し、Codex は実装と検証のみ。
  バイト不変性を `git show HEAD:sitemap.xml` からの再構成＋`cmp` で自主的に証明＝有効な貢献。
- **分業メモ**：診断・前提の訂正・不採用判断・Daisuke への方針確認は Opus、機械的な除去と検証実行は Codex。

## 2026-07-10 — sitemap 未掲載18件を追加＋lastmod を mtime から git コミット日へ

- **種別**：other（sitemap とその生成元のみ。HTML・本文・出典・メタはゼロ変更）／**wall-time**：__分（Daisuke 記入）
- **面（tracked 2）**：`sitemap.xml`・`scripts/generate_sitemap.py`
- **入力**：直前エントリで「別タスクへ切り出し」とした積み残し。
- **課題**：sitemap が 2026-06-19 以降再生成されておらず、**本番200の実在ページ18件が未掲載**だった。
  内訳＝JA写真家5（asako-narahashi / kenta-cobayashi / mayumi-hosokura / nerhol / sakiko-nomura）＋同EN5＋
  JA運動4（インティメイト・ライフ / スティルライフ / ニュー・トポグラフィックス / ポストインターネット）＋同EN4。
- **前回見立ての訂正**：直前エントリは「再生成すると lastmod が728件 churn するので分離」と書いたが、
  **churn は案を問わず不可避**だった。現行 sitemap の lastmod は既に古く（例：`archive.html` は `2026-06-18` だが
  実際は `2026-07-10` に変更済）、2026-06-19 以降に触った約721ページで嘘になっている。
  争点は「churn するか否か」ではなく「churn 後の値が真か嘘か」だった。
- **変更**：
  - `generate_sitemap.py`：`<lastmod>` を **mtime → git コミット日**へ。`git -c core.quotepath=false log
    --format=C%as --name-only -- '*.html'` の一括1パスで `{rel: YYYY-MM-DD}` を作る（newest-first なので初出が最新）。
    mtime 経路は**未commitファイル用のフォールバックとして残す**。
    mtime は clone/checkout でリセットされ、同一内容を書き直す横断スクリプトでも進むため、公開日として嘘をつく。
  - `sitemap.xml`：再生成。loc **748 → 766**（+18）。既存721件の lastmod が**真の値へ一度だけ補正**、27件は不変、
    失われたURL **0件**。
- **地雷2件（実測で検知・対処済）**：
  - **`core.quotepath`**：無指定だと git が非ASCIIパスを `"movements/\343\202\263..."` とエスケープし、
    **52ページが無言でフォールバックに落ちる**。このリポジトリは日本語ファイル名が多く必ず踏む。`-c core.quotepath=false` で0件化。
  - **日付マーカーの誤読**：`--format=C%as` の行判定が `line.startswith("C")` だと、将来 `Contact.html` のような
    **Cで始まるパス**を日付行と誤認する。現状該当0件だが `re.fullmatch(r"C(\d{4}-\d{2}-\d{2})$")` へ厳密化。
    厳密化後も sitemap.xml はバイト不変を確認（＝挙動を変えていない）。
- **副作用の検証**：`photographers/jp-木村伊兵衛.html` が alternate 3本を新規獲得したが、これは 06-19 以降に
  JA HTML へ hreflang が入った結果を正しく拾ったもの。指す先3本とも **200 実測**。
  **既存URLが alternate を失った件数は0**（`<url>` ブロック単位で新旧を突き合わせ）。
- **検証**：loc=766 ／ new-design loc=0 ／ XMLパースOK ／ 消失URL=0 ／ git日付なし(mtimeフォールバック)=0 ／
  **冪等性**＝2回実行して `cmp` 一致 ／ check_content_loss exit 0 ／ preflight OK ／ 未追跡10件は未stage。
- **並行作業**：`photographers/*.html` の JSON-LD `birthDate` 修正が**別セッションで進行中**。
  本作業は `photographers/` を一切触らず、重なるのは本ファイルのみ。commit 直前に pull して衝突を回避した。
  なお birthDate の**正しい生年は各ページの本文と meta description に既にある**（細江1933・中平1938・畠山1958・北島1954を実測）。
  直前エントリの「正しい生年がページ上に無く外部出典の裏取りが要る」は**誤り**。外部調査は不要。
- **Codex 挙動**：逸脱0。予告した4つの数値（766 / 721 / 27 / 0）を全て的中させ、冪等性も自主検証。
  `core.quotepath` は監督側が事前に実測して指示に含めた。日付マーカー厳密化は監督側で後追い実施。
- **分業メモ**：設計判断（mtime vs git日付・churnの質の評価）と地雷の事前実測は Opus、実装と検証実行は Codex。

## 2026-07-10 — JSON-LD birthDate の era 混入を修正（22ページ）＋パーサ2件を堅牢化＋preflight ガード追加（種別=data+engine）

- **wall-time**: （Daisuke 記入）
- **対象**: `photographers/*.html` の JSON-LD `birthDate`。**JAのみ。EN は無変更**（EN は全件正しい値を保持していた）。
- **根本原因（git で特定）**: 発生源は `8ab5c9569`「v5.1 全ページ移行完了」(2026-06-08)。
  同commitが全写真家の JSON-LD を `@graph` → 単一 `Person` へ平坦化した際、`card-data.json` に
  **`years` フィールドが存在せず `era` しか無い**ため、era 文字列を `birthDate` に流し込んだ。
  **同commitはスクリプトを1本も触っていない**（＝未commitのアドホックスクリプトで実行された）。
  これが「どの生成スクリプトを読んでも `"1970"` を再現できない」理由。
  その後 `5c2cddb9a`(07-06 importer) が `add_photographer._parse_years`（ダッシュ分割のみ）で
  蜷川実花を `"2000s / 2000年代"` へ**二重に**破壊した。移行前(`5d6c07c3c`)は蜷川=1972・中平=1938/2015 と**正しかった**。
- **件数の訂正**: 依頼時の検出コマンドは `birthDate` を**ページ先頭の `eras/YYYY.html` リンク1本**としか
  突き合わせないため **5件取りこぼす**。実際の破損は **17件ではなく22件**。
  追加分＝`eikoh-hosoe`(1960→1933) / `jp-影山光洋`(1940→1907) / `keizo-kitajima`(1970→1954) /
  `kishin-shinoyama`(1960→1940) / `naoya-hatakeyama`(1980→1958)。5件とも本文・git移行前・ENの3点で一致。
- **裏取り**: 21件の生年は「本文 / 移行前git値 / ENページ」の**3独立ソース**が一致。
  本文に生年が無い2件のみ外部出典で確認 —
  蜷川実花 **1972**（東京オペラシティ アートギャラリー 公式プロフィール）、
  オノデラユキ **1962**（作家公式サイト "born in Tokyo (1962)"）。両者とも移行前git値・ENページと一致。捏造なし。
- **multiplicity.html**: イタリアの研究集団。本文に生年・結成年の記述が一切無い。
  `@type: Person` → `Organization`、`birthDate` 削除、`nationality` → `address.addressCountry: "IT"`。
  **`foundingDate` は本文に典拠が無いため追加しない**（Daisuke 判断）。
- **エンジン修正2件（再発防止の本体）**:
  - `add_photographer._parse_years`: ダッシュ分割のみ→lifespan 厳密判定。era 文字列は `("","")` を返す。
  - `build_photographers_en._parse_years`: `re.findall(r'\d{4}')` が **`"2000s / 2000年代"` → birth=2000, death=2000**
    と解釈し**存命作家を没年つきで出力する潜在バグ**だった。同じ厳密判定で `(None,None)` 化。
- **`years` の二重責務（設計上の真因）**: `years` は EN hero の表示文字列（`ph-hero__years">2000s`）と
  `birthDate` の供給元を**兼ねている**。hero の era 文字列はサイト標準（147p）なので `years` 自体は直せない。
  よってパーサ側で「lifespan 形でなければ birthDate を出さない」と**縁を切る**のが正解。
  `data/photographers-en-content.json` の `pages["mika-ninagawa.html"].years` は現在も `"2000s"` だが、
  同entryは正しい `jsonld` を持ちフォールバックが発火しないため**実害なし**。堅牢化後は仮に発火しても birthDate を出さない。
- **preflight ガード `check_jsonld_birthdate()`**（JA/EN 両方を走査）:
  1. HARD: `birthDate`/`deathDate` が `^\d{4}(-\d{2}(-\d{2})?)?$` 以外（`jp-植田正治` の `1913-03-27` は通す）
  2. HARD: JA本文から**厳密正規表現**で生年を1件だけ特定できる場合、`birthDate` と不一致なら失敗
  3. HARD: `@type` が Person でないノードに `birthDate`/`deathDate` がある
  4. WARN: `birthDate` が10の倍数 かつ 同年の `eras/YYYY.html` リンクがあり 本文で確証が取れない
- **正規表現の誤検知を実測で潰した**: 初版 `年[^。\n]{0,12}?生まれ` は
  「2000年頃の城ヶ島で偶然**生まれ**た2点」(asako-narahashi・作品)、
  「2004年に同エージェンシーから**生まれ**たOstkreuzschule」(sibylle-bergemann・学校)、
  「1858年（一部の資料では1861年）に**生まれ**た」(jp-亀井茲明・括弧内の異説) を拾い **3件の誤検知**。
  年と生まれの間を「`、`＋漢字/カタカナ地名のみ」に制限（ひらがなを挟ませない）して解消。
- **ガードの実測**: 修正後コーパス **PASS=36 / SKIP=100 / FAIL=0（誤検知0）**。
  破損していた旧値21件を replay して **21/21 を HARD FAIL で捕捉**（19件が本文照合、2件が形式）。
  4ルールとも手動で mutation テストし発火を確認（JA era回帰 / 不正形式 / 非Person / EN側形式）→ 復元後 OK。
- **検証**: `check_content_loss.py` OK ／ `preflight.py` OK ／ 変更26ファイル
  （JA html 22 ＋ `add_photographer.py` / `build_photographers_en.py` / `preflight.py` / `check_new_photographer.py`）／
  **`<dt>Years</dt>`・hero の変更行数 0** ／ EN・data 無変更 ／ 未追跡10件は未stage ／ staged 0。
- **積み残し（別タスク・Daisuke 承認済）**: 同 `8ab5c9569` は **deathDate を33ページから、birthDate を144ページから
  完全に削除**している（中平の `deathDate:2015`、篠山の `2024` 等）。今回は対象外。移行前git値の妥当性を
  1件ずつ検証する必要があるため独立PRで扱う。今回のガードで**再発は阻止済み**。
- **Codex 挙動**: 逸脱0。監督側の rule 2 正規表現が誤検知3件を出した際、**content ページを勝手に直さず停止して報告**
  （指示通り）。誤りは監督側の仕様。EN 正本 `years="2000s"` の潜在回帰は Codex は検知せず、監督側が実測で発見。
- **分業メモ**: 根本原因の git 追跡・件数の実測訂正・外部出典の裏取り・正規表現の誤検知潰しと全コーパス検証は Opus、
  22ファイルの機械置換・パーサ堅牢化・ガード実装は Codex。

### 2026-07-10 — JSON-LD birthDate/deathDate復元＋preflight（other）
- **wall-time**: （Daisuke記入）。
- **bug**: v5.1移行 `8ab5c9569` で、JA写真家ページの単一 Person JSON-LD から `birthDate` / `deathDate` が欠落。
- **手作業点**: 0。旧 `@graph` Person 値と本文/EN years照合に基づく機械復元。jp-* 5件の `deathDate` はJA本文の一意な没年から補完。
- **サーフェス変更数**: 154ファイル（JA写真家HTML 153 + `scripts/preflight.py`）。EN HTML / `<dt>Years</dt>` / hero は変更なし。
- **フィデリティ差分**: N/A。本文・出典・関連欄は変更せず、JSON-LD script内に `birthDate` 143件・`deathDate` 33件を追加。
- **発火した engine 改良**: `preflight.py` に `_JA_DEATH_RE` / `_ja_body_death_years()` を追加し、JA本文の没年が一意に取れる場合のみ `deathDate` 不一致をHARD FAIL化。
- **検証**: dry-run 176件・153ファイル PASS（JA本文+EN 137 / ENのみ 34 / JA本文のみ 5）。変更行は全てJSON-LD script内。JSON-LD load OK。`preflight.py` OK（既存WARN 3件のみ）/ `check_content_loss.py` OK。mutation testで `deathDate` / `birthDate` の本文不一致を各1件HARD FAIL確認後、復元。

### 2026-07-10 — JSON-LD初期欠落11件補完＋presenceガード（other）
- **wall-time**: （Daisuke記入）。
- **bug**: v5.1移行前から単一 Person JSON-LD に `birthDate` / `deathDate` キーが無かったページが残存。値不一致ガードだけではキー欠落を検知できなかった。
- **手作業点**: 0。対象11キーを本文正規表現 `_JA_BIRTH_RE` / `_JA_DEATH_RE` で一意照合。EN `years` がパース可能な `jp-冨重徳次` は `tomishige-tokuji.html` の `1862–1938` と一致。
- **サーフェス変更数**: 11ファイル（JA写真家HTML 10 + `scripts/preflight.py`）。`louis-vaire.html` は `birthDate` / `deathDate` の2キー補完。EN HTML / `<dt>Years</dt>` / hero は変更なし。
- **フィデリティ差分**: N/A。本文・出典・関連欄は変更せず、JSON-LD script内に `birthDate` 10件・`deathDate` 1件を追加。
- **発火した engine 改良**: `preflight.py` に presence ガードを追加。JA本文から生年/没年が一意に取れ、かつPersonノードが存在する場合、全Personノードで該当キーが無ければHARD FAIL。Personノードなしページは誤検知防止のため対象外。
- **検証**: Personなし実測は `multiplicity.html` 1件、ld+jsonなしは0件。タスクA適用後 `preflight.py` OK（誤検知0）/ `check_content_loss.py` OK。mutation testで birthDateキー削除 / deathDateキー削除 / deathDate値不一致を各1件HARD FAIL確認後、復元。

### 2026-07-10 — JSON-LD hero年照合ガード（other）
- **wall-time**: （Daisuke記入）。
- **bug**: 本文正規表現だけでは生没年を一意取得できないページがあり、JSON-LD日付キー欠落・値不一致の死角が残っていた。
- **手作業点**: 0。`ph-hero__years` を読み取り専用で厳密パースし、`YYYY–YYYY` / `YYYY–` のみ確認源に採用。`2000s–` 等のera型は対象外。
- **サーフェス変更数**: 2ファイル（`scripts/preflight.py` + `photographers/gregory-crewdson.html`）。hero表示 / `<dt>Years</dt>` / EN HTML は変更なし。
- **フィデリティ差分**: N/A。本文・出典・関連欄は変更せず、hero照合で新たに検出した `gregory-crewdson` の `birthDate: 1962` をJSON-LD script内に追加。
- **発火した engine 改良**: hero確認年を本文確認年と統合し、mismatch / presence の両方へ適用。本文年とhero年が両方あり矛盾する場合もHARD FAIL。
- **検証**: strict hero parse 116件。本文に無くheroで増える確認源は birth 92件 / death 51件。本文×hero矛盾0件、既存JSON-LD値不一致0件。`preflight.py` OK / `check_content_loss.py` OK。mutation testで hero由来birthDateキー削除 / hero由来birthDate値不一致 / era型無視 / 既存本文照合デグレなしを確認後、復元。

## 2026-07-10 — eiko-yamazawa（new / 新規追加・山沢栄子・idx301・era1930）＋importer時短2件を実装（②--apply-surfaces / ③bundle側ui-terms）

- **種別**：new（純・新規追加）。素材=re-photographer/eiko-yamazawa.html / -en.html（JA/EN・v5.1・clean・Amazonリンク入り）。slug=eiko-yamazawa。
- **分業**：**Fable監督・監査／Codex（reasoning=high・MCP）実装**。監督側で全判断（spec全項目・idx=301・era=1930・
  movementSlugJa=モダニズム・GENRE_TAG/terms追加語・de-link判断・挿入アンカー）、Codexはimporter改善2件の実装のみ
  （触ってよいファイル明示・Web検索禁止・実行はpy_compileまで）。パイプライン実行は監督側。
- **importer時短2件（積み残し2026-07-09分・今回実装＋本番テスト）**：
  - **② `add_photographer.py --apply-surfaces`**：JAカード4面（archive.html / cards-archive.html /
    new-design/cards-archive.html / eras/<era>.html）を決定論アンカーで自動挿入。backup（既存backup上書きなし）＋
    冪等skip＋書込後検証（ref存在・写真家カード+1）失敗時restore。`--apply --apply-surfaces` 併用時はデータ投入後に
    surfaces実行（監査でearly-return罠を検出→修正済）。**本番初回で4面すべてINSERT成功・手貼りゼロ**。
  - **③ `--bundle-to-en` に works ui-terms 提案を配線**：run_merge_to_en の①ブロックを `report_works_ui_terms()` へ
    抽出し両経路から呼ぶ（merge側は挙動不変のリファクタ）。新規経路で3件提案→--applyで自動書込
    （ToMuCo—Transparent Blue / Third Gallery Aya—Works and Chronology / Transparent Blue）。**手作業だったui-terms works登録が消えた**。
- **判断点（実測）**：
  1. **movementSlugJa=モダニズム**：素材heroのMovementは抽象写真だが movements/抽象写真.html 未存在＋STUB_TO_SLUG未登録。
     entry-meta/§RELが唯一リンクする既存運動＝モダニズム（modernism）を運動ページ面に採用。star用movements=[モダニズム,抽象写真,構成写真]。
  2. **GENRE_TAG追加1語**：「抽象写真」→ Abstract Photography（build_archive_en.py。未登録のままだとen/archive連鎖停止）。
     ui-terms terms にも「抽象写真」→ Abstract photography を追加（hero眉/Channel未翻訳WARN 2件解消）。
  3. **de-link 2名**：consuelo-kanaga / imogen-cunningham はページ未存在→JA本文・§RELの計4リンクを名前だけ残して除去
     （EN側はimporterが自動de-link・dangling 0実測）。
- **面（tracked 17）**：新規JA/EN個別ページ2＋archive/cards-archive JA・card-data・countries japan JA/EN・
  en-content(+94)・ui-terms(+4)・supplement・star bin・en/archive・eras1930 JA/EN・モダニズム JA/EN（件数12→13・chip追加）・
  scripts3（add_photographer / import_chatgpt / build_archive_en 1行）＋new-design/cards-archive.html（git-ignore・disk投入済）。
- **フィデリティ**：JA 3節・18 cite・50 sup-ref・dangling 0（[render-ja]自己検査）。EN merge add=20/skip-empty=2・
  他slug byte不変assert通過。EN残WARN3（no photobooks_html / no external_links_html / jsonld WebPageフォールバック）は
  asako同型の標準（amzn.to 2件はfurther_reading経由で反映済を実測）。
- **検証**：check_new_photographer OK（WARN=節名非標準〔素材準拠〕・en_graph_absent〔EN標準〕）／check_content_loss OK／
  link integrity OK／**preflight exit 0**（残WARN3＝en/countries/japan・en/eras/1930・en/movements/modernism の
  「直接編集疑い」＝scoped再生成への既知の誤検知・07-09と同型）。`--all` 不使用・link_country_keywords 不実行・対象外巻き込み0。
- **Codex 挙動**：逸脱0。②のCLIフラグ併用罠（--apply --apply-surfaces でデータ投入がearly-returnでスキップ）を監査で指摘→即修正。
- **backup（未追跡・GH Pages 実機確認後に削除）**：archive-backup.html / cards-archive-backup.html / eras/1930-backup.html /
  movements/モダニズム-backup.html / card-data-backup.json / -supplement-backup.js / star -backup.bin。
- **wall-time**：30分未満（Daisuke 概算・計測忘れ）。

## 2026-07-11 — asako-narahashi 写真集Amazonリンク（JA3冊/EN3冊・種別=other）

- **種別**：other（既存ページ§REFへの追記のみ。本文・thesis・出典は不触）。onodera 07-08 と同じプレイブックの5回目実走。
- **面**：3ファイル（`photographers/asako-narahashi.html` +29行 / `data/photographers-en-content.json` +3-1行＝photobooks_html新キー追加 / `en/photographers/asako-narahashi.html` +25行＝`--slug`再生成）。EN HTML直編集なし。
- **調査（監督側・捏造防止）**：渡されたのは amzn.to 短縮URL 6本のみ。curl でASIN解決（JA: 4938628279 / 4905254027 / 4905254086、EN: 1590052153 / 4938628279 / 4905254124）。Amazonは直接読めないため、書名・出版社・年は 蒼穹舎既刊リスト・日本の古本屋（NU・E＝蒼穹舎1997）／pg-web.net（Ever After＝オシリス2013・カラー58点・付録インタビュー）／shashasha（ギプス＝オシリス2018・1991年骨折時のモノクロ）／Antenne Books ほか（Dawn in Spring＝オシリス2022・1989年「春は曙」初書籍化）／AbeBooks・josefchladek（half awake…＝Nazraeli 2007・Parr/Nazraeli Edition of Ten 第2作・Martin Parr文）で確定。解説文はJA本文の記述（03FOTOS 17回展・骨折旅行撮影）と整合させた。
- **分業**：**Fable監督・監査／Codex（MCP・workspace-write/never）実装**。書名・年・解説文・挿入位置・JSON書き戻し方式（`json.dumps(..., ensure_ascii=False, indent=2)` 末尾改行なし）まで全て監督側で確定して一字一句指定。Codex呼び出し1回・**バグ0・逸脱0**。
- **検証**：言語別リンク完全分離（JA 3本/EN 3本・相互混入0）・`rel="noopener sponsored"` 全6本・既存 ph-further-links 4件無傷・JSON差分は該当ページのみ・check_content_loss OK・preflight OK（exit 0）・対象外巻き込み0。
- **wall-time**：10分弱（Daisuke 実測）。大半は書誌裏取り。

## 2026-07-11 — mari-katayama（new / 新規追加・片山真理・idx302・era2010）＋§REL carry-forwardガード実装

- **種別**：new（純・新規追加）。素材=re-photographer/mari-katayama.html / -en.html（JA/EN・v5.1・clean・Amazonリンク各2冊入り）。slug=mari-katayama。表記は素材どおり「片山真理」（依頼文の「真里」は誤記と判断）。
- **分業**：**Fable監督・監査／Codex（MCP・workspace-write/never）実装**。監督側で全判断（spec全項目・idx=302・era=2010・movementSlugJa=ステージド写真・§RELリンク先・件数アンカー・GENRE_TAG追加語）、Codex呼び出し2回（①JA§REL修正5編集＋EN正本JSON2キー＋運動ページJA手挿入 ②§RELガード実装）。パイプライン実行と監査は監督側。**Codexバグ0・逸脱0**。
- **判断点（実測）**：
  1. **運動面=ステージド写真**（§04が演出写真史に位置づけ・JA/ENページ既存・featured登録済・11→12名）。フェミニズム写真もfeaturedだがJA/EN不整合リスク（EN自動メンバー化）のためstar用movements=[ステージド写真,日本写真,セルフポートレート]からも除外。
  2. **GENRE_TAG追加1語**：「セルフポートレート」→ Self-Portrait（build_archive_en.py。未登録でen/archive連鎖停止＝eikoの抽象写真と同型）。ui-terms terms は既登録で追加不要。
  3. **§REL修正**：素材の morimura.html は dangling（正=yasumasa-morimura.html）。sherman/miyako-ishiuchi/yurie-nagashima をリンク化、テーマにステージド写真リンクを追加。
  4. **EN §REL抽出漏れ**：素材§RELラベル「Related Photographers and Themes / Related Themes」を importer が site_directory_html に抽出できず「In preparation」化→ 正本JSONへ site_directory_html＋related_annotations 5件を手投入して --force 再生成で解消（新規経路にも§REL落ちの穴がある実例）。
  5. **運動ページサイドバー Photogs=7 は stale**（実カード11）→ 挿入後の実数12に合わせて修正。
- **importer改善（積み残し2026-07-07分・今回実装）**：**§REL carry-forwardガード**を _apply_update_existing に追加（Codex実装/Fable監査）。新素材の§RELが「準備中」なら旧§RELを§REF同型でsplice、件数減はHARD FAIL（意図的削減は ALLOW_REL_REDUCTION=1）。書込前後の二重検証＋dry-run計画表示。合成素材（onodera §REL除去版）dry-runと関数テストで検証済。**実update案件での --apply 実走検証は次回update時**。
- **面（tracked 16）**：新規JA/EN個別ページ2＋archive/cards-archive JA・card-data・countries japan JA/EN・en-content(+119)・ui-terms(+2 works)・supplement・star bin・en/archive・eras2010 JA/EN・ステージド写真 JA/EN（11→12・chip追加・stale7→12）・scripts2（build_archive_en 1行 / import_chatgpt +49-7）＋new-design/cards-archive.html（git-ignore・投入済）。
- **フィデリティ**：JA 4節・27 cite・48 sup-ref・dangling 0（render-ja自己検査）。EN merge add=18/skip-empty=4・他slug byte不変assert通過。EN残WARN3（no photobooks_html / no external_links_html / jsonld fallback）=eiko同型の標準（amzn.to 2件はfurther_reading経由で反映済を実測）。
- **検証**：check_new_photographer OK（WARN=en_graph_absent〔EN標準〕のみ）／check_content_loss OK／link integrity OK／**preflight exit 0**（残WARN3=en/countries/japan・en/eras/2010・en/movements/staged-photography の「直接編集疑い」＝scoped再生成への既知の誤検知・07-10と同型）。--all 不使用・link_country_keywords 不実行・対象外巻き込み0。
- **backup（未追跡・GH Pages 実機確認後に削除）**：archive-backup.html / cards-archive-backup.html / eras/2010-backup.html / movements/ステージド写真-backup2.html / card-data-backup.json / -supplement-backup.js / star -backup.bin。
- **wall-time**：（Daisuke記入）

## 2026-07-12 — aya-fujioka（new / 新規追加・藤岡亜弥・idx303・era2010）＋era面アンカー恒久修正

- **種別**：new（純・新規追加）。素材=re-photographer/aya-fujioka.html / -en.html（JA/EN・v5.1・clean・書籍リンク入り＝JA Amazon3冊/EN shashasha3冊）。slug=aya-fujioka。
- **分業**：**Fable監督・監査／Codex（MCP・workspace-write/never）実装**。監督側で全判断（spec全項目・idx=303・era=2010・channel=スナップショット・運動ページ面skip判断・リンク化対象と挿入位置・GENRE_TAG/terms追加語・shashasha URL裏取り）、Codex呼び出し4回（①EN正本further_reading復元＋ui-terms3種＋GENRE_TAG ②era面アンカー修正 ③head属性順正規化＋ENトグル復元 ④本文初出リンク化JA/EN各4）。パイプライン実行と監査は監督側。**Codexバグ0・逸脱0**。
- **判断点（実測）**：
  1. **運動ページ面=skip**：hero Movement=スナップショットは movements/ページ未存在＋素材の§REL文脈（スナップショット/写真集文化/広島と戦後記憶）にリンク一切なし＝eiko型の「§RELが唯一リンクする既存運動」も不在。asako-narahashi 前例（運動ページ非掲載）に合わせた。star用movements=[スナップショット,写真集文化,日本写真]（写真集文化でnarahashiと星座接続）。
  2. **GENRE_TAG/terms追加1語**：「スナップショット」→ Snapshot Photography（build_archive_en.py と ui-terms terms の2箇所）。
  3. **hero Channel正規化**：素材の「写真集」は非標準→カードと同じ「写真史の論点 · スナップショット」へ（narahashi/katayama と同型）。
  4. **EN further_reading 抽出漏れ**：importer が ph-book の note＋第2CTA（shashasha）＋flexラッパを脱落させ簡略版のみ抽出→素材原文3ブロックを正本JSONへ復元（shashasha 3URLは実在裏取り済＝here-goes-river-1がI don't sleepなのはshashasha側の実slug）。**新規経路の既知の穴・3例目**。
  5. **本文初出リンク化 JA/EN各4**：カルティエ＝ブレッソン/土門拳/中平卓馬/『PROVOKE』（多木浩二・笹岡啓子はページ未存在で据え置き）。
- **importer恒久修正（今回実装）**：**era面挿入アンカーの空白許容化**（add_photographer.py）。前回挿入が `</article>\n</div>...` と改行を残すため二世代目の同一era実行で完全一致markerが0件→FAILする設計バグ。regex `</article>\s*</div></div></section></main>` へ変更（Codex実装/Fable監査）。eras/2010で本番実証。他に importer render-ja が素材の属性順（content先行）をそのまま出す件は今回手修正（viewport/canonical/OGP/description/hreflang）＝**未自動化の積み残し**。ENトグルはEN未存在時にimporterがde-linkするため新規は毎回復元が要る（既知）。
- **面（tracked 14＋新規2）**：新規JA/EN個別ページ2＋archive/cards-archive JA・card-data・countries japan JA/EN・en-content(+114)・ui-terms(+12行)・supplement・star bin・en/archive・eras2010 JA/EN・scripts2（add_photographer +6-5 / build_archive_en 1行）＋new-design/cards-archive.html（git-ignore・投入済）。
- **フィデリティ**：JA 4節・25 cite・54 sup-ref・dangling 0。EN merge add=20/skip-empty=2・他slug byte不変assert通過。EN残WARN3（no photobooks_html / no external_links_html / jsonld fallback）=eiko/mari同型の標準（shashasha 3件はfurther_reading経由で反映済を実測）。
- **検証**：check_new_photographer OK（WARN=en_graph_absent〔EN標準〕のみ）／check_content_loss OK／link integrity OK／**preflight exit 0**（残WARN2=en/countries/japan・en/eras/2010 の「直接編集疑い」＝scoped再生成への既知の誤検知）。--all 不使用・link_country_keywords 不実行・対象外巻き込み0・タグ開閉均衡JA/EN実測OK。
- **backup（未追跡・GH Pages 実機確認後に削除）**：mari回の既存backupを温存（上書きなしガード）＋今回新規なし（既存backupへ相乗り）。
- **wall-time**：28分（Daisuke実測）

## 2026-07-13 — 9名バッチupdate（ChatGPT新素材で本文全刷新・steichen/jacques-henri-lartigue/eikoh-hosoe/winogrand/kikuji-kawada/araki/tomatsu/williamklein/friedlander）

- **種別**：update×9（既存本文722〜1335字 → 新素材4012〜4664字の全文刷新）。素材=re-photographer/photographers_batch_20260713_final/（JA/EN・v5.1 ph-*・clean）。eugene-atget は既存本文十分のため不使用（Daisuke指示）。
- **分業**：**Fable監督・監査／Codex（MCP・workspace-write/never）実装**。パイロット（steichen）→監査→残り8名逐次。Codex呼び出し4回・Codexバグ0・逸脱0（安全契約FAILで2回正しく自主停止）。
- **監督判断（実測）**：
  1. **§REL全員「既存維持」**：既存§RELは全件サイト内リンク付き（8/5/3/4/3/4/7/3/6件）、新素材§RELは6件中1〜3件しかリンクなし（Rodin等ページ未存在の裸名あり）→素材から§REL節だけ除去したスクラッチコピーを作成し、§RELガードの「準備中→既存verbatimスプライス」経路に載せた。**§REL carry-forwardガード（07-11実装）の実update発動を9/9で確認＝検証完了**。
  2. **sup-ref減少2件は正当**：hosoe 25→13 / kawada 24→16 は旧ページが同一3出典を繰返す旧型で、unique出典は3→22 / 3→20と大幅増＝意図的全文差替。
- **engine穴4件（発見→即修正）**：
  1. **JA §REF写真集ブロック(ph-book)脱落**：carry-forwardが新素材§REFで丸ごと置換しAmazonカードを落とす（7/9名で計19冊）→ scratchpad/restore_books.py でbackupからverbatim復元（§REF内カウント検証つき）。**恒久対応=importerの「ph-book丸ごと抽出」（aya-fujioka回からの積み残し）が本修正で必要性実証**。
  2. **EN §REFリンク重複**：merge-to-enが旧external_links_htmlをpreserveしつつ新further_reading_htmlをaddし同一リンクが二重表示→ fix_en_ref_links.py で新リンクをchip-link化しexternal_links_htmlへ移設・further_reading空化（Databases & archivesラベル付き正規形）。
  3. **EN og:image/twitter:image脱落**：merge-to-enのog/twitter replaceが素材由来dict（image系キーなし）で上書き→9名全員のog:image+width/height/alt+locale・twitter:imageをorigin/main JSONから機械復元・再生成。**merge-to-enのog/twitterマージをキー単位skip-emptyにする恒久修正が次回候補**。
  4. **sup-ref減少ガードにオーバーライドなし**：ALLOW_REL_REDUCTION と非対称→ `ALLOW_SUPREF_REDUCTION=1` を実装（pre/post両検証・unique出典/本文字数ガードは維持・unit test 5/5 PASS）。
- **preflight配線1件**：check_en_content_loss（EN JSONリンク消失HARD）に intentional-replacements.json フィルタが未配線だった→ _filter_loss_items_by_declarations をURL単位で適用・消費宣言はinfo・stale判定は両ガード共有。今回の意図的リンク置換37件を宣言（push後にstale WARN→削除の合図）。
- **面（tracked 22）**：JA9＋EN9＋en-content.json（対象9キーのみ・他slug不変assert通過）＋importer＋preflight＋intentional-replacements.json。ui-terms変更なし（works対象なし）。カード・年代・国・運動・スターマップ面は不触（既存写真家のため）。
- **フィデリティ（9名計）**：本文8664→39668字・unique出典40→190・§REL全員既存件数維持・JA/EN books/amzn件数一致（19冊無傷）・dangling 0。
- **検証**：check_content_loss OK／9slug --dry-run SKIPPEDなし／**preflight OK**（残WARN=data-nosnippet 9→8・8→7×5名＝scaffold正典標準数・onodera回と同型）／対象外巻き込み0。
- **backup（未追跡・GH Pages実機確認後に削除）**：photographers/<slug>-backup.html×9・en/photographers/<slug>-backup.html×9・scripts/<slug>-spec.json×9。
- **wall-time**：30分（Daisuke実測。9名バッチとしては速い＝1名あたり約3.3分）

## 2026-07-14 — 6名バッチupdate（ChatGPT新素材で本文全刷新・don-mccullin/ed-van-der-elsken/seydou-keita/larry-clark/philip-jones-griffiths/kishin-shinoyama）

- **種別**：update×6（既存本文905〜1095字 → 新素材3627〜5742字の全文刷新）。素材=re-photographer/20260714/（JA/EN・v5.1 ph-*・clean。Amazonカードなし・ph-book書誌カード2〜3枚/名）。
- **分業**：**Fable監督・監査／Codex（MCP・workspace-write/never）実装**。パイロット（don-mccullin）→監査→残り5名逐次。Codex呼び出し8回・Codexバグ0・逸脱0（安全契約系で4回正しく自主停止）。
- **監督判断（実測）**：
  1. **§REL全員「既存維持」**：素材§RELに裸名（W・ユージン・スミス等）・seydou-keitaはリンク0 → 前回同様、素材から§REL節を除去したスクラッチコピーで既存verbatimスプライス経路に載せた。6/6維持確認。
  2. **sup-ref減少2件は正当**：philip 20→19 / kishin 22→17（旧反復出典型・unique出典2→21/3→20）→ `ALLOW_SUPREF_REDUCTION=1`。
  3. **hero Years空欄・Country年代文字列は既存維持**（サイト標準153p/147p・素材値へ「補正」しない）。
  4. **1文字アンカー de-link**：kishin本文の《家》/`Ie` 外部リンクをJA/ENともプレーン化（URLは作品チップ・§REF・出典に残存。JA=HTML直編集・EN=正本JSON経由）。
- **engine穴4件（発見→恒久修正）**：
  1. **ph-book note脱落**：`_extract_books()` が `div.ph-book__note` 限定で素材の `p.ph-book__note` を落とす → **積み残し①「ph-bookブロックinner HTML無加工保持」を実装**（JA/EN両レンダラー・note/第2CTA/flexラッパの類型ごと解消）。
  2. **merge-to-en og/twitter dict丸ごとreplace**（前回9名全員で発生した既知バグ） → **積み残し①c「キー単位skip-emptyマージ」を実装**。今回6名でog:image系消失ゼロを実地確認。
  3. **idx未導出→Entry「§ None / No. None」**：derive_spec_from_existing() がidxをspecに入れず → card-data導出＋既存Entryフォールバックを実装。
  4. **entry-meta Countryへhero用spec値流用**（ed実例: リンク付「オランダ」→「1950s / 1950年代」に化ける） → 既存<dd>のverbatim carry-forward＋書込前後検証を実装。hero Countryとentry-metaは別値になり得る仕様として分離。
  - 付随: **積み残し①d相当**（further_reading×external_linksのURL-union重複排除・ph-book CTAとの同一URL重複排除）も実装。
- **intentional-replacements**：前回9名バッチの37宣言（push済でstale化）を削除。今回の旧cite由来消失2件（don-mccullin Tate shop / ed Stedelijk）を新規宣言 → **push後にstale WARN化したら削除**。
- **ui-terms（durable）**：countries「マリ→Mali」、works_labels「ToMuCo - 《家》1975 → ToMuCo — Ie, 1975」「ToMuCo - 小林旭, 1974 → ToMuCo — Kobayashi Akira, 1974」。
- **EN Countryリンクのプレーン化は標準への収束**：donのEN backupのみ旧link_country_keywords時代のリンク持ち。前回9名の再生成ENは全員プレーン表記＝現行ビルダー標準。link_country_keywords.pyは実行せず。
- **面（tracked 16）**：JA6＋EN6＋en-content.json（対象6キーのみ・top-level/page key set不変assert通過）＋ui-terms.json＋importer＋intentional-replacements.json。カード・年代・国・運動・スターマップ面は不触（既存写真家）。
- **フィデリティ（6名計）**：本文5826→28006字・unique出典16→135・§REL全員既存verbatim維持・ph-book素材とinner HTML完全一致（note/CTA無傷）・dangling 0・Entry番号6名JA/EN一致。
- **検証**：check_content_loss OK／6slug --dry-run SKIPPEDなし・untranslated 0／**preflight FAIL 0・WARN 0**／en-content変更は対象6キーのみ／対象外巻き込み0。
- **backup（未追跡・GH Pages実機確認後に削除）**：photographers/<slug>-backup.html×6・en/photographers/<slug>-backup.html×6・scripts/<slug>-spec.json×6。
- **wall-time**：41分（Daisuke実測。engine穴4件の発見→恒久修正込み。1名あたり約6.8分）

## 2026-07-14 — capa（本文組版の標準化・種別=other・軽量行）

- **対象**：photographers/capa.html＋en/photographers/capa.html（正本JSON経由）。**文言変更ゼロ**（JA/ENとも可視テキストのcharacter-identicalを機械照合済み）。
- **内容**：①JA §02の小見出し5本が**CSS定義のない`<h4>`**（素のブラウザ表示）だった→標準の`<h3 id="h3-01..05">`へ変換（赤ボーダーの標準スタイルが適用される）。ENはビルダーがh4→h3変換済みで対応不要。②壁段落の分割: JA/EN §01を3段落・§03を2段落へ（文境界のみ・JAはHTML直編集、ENはen-content.json文字列置換→builder再生成）。
- **検証**：preflight OK／check_content_loss rc=0（構造変化WARNは目視＝再組版のみと確認済）／JSON変更はcapaキーのみ／EN --dry-run SKIPPEDなし。
- **メモ**：capaのCSSは標準と同一だった。差は本文マークアップのみ（h4問題）。同様の「h4残存」ページが他にもある可能性→必要なら `grep -l '<h4' photographers/*.html` で母数を数えてから対応。

## 2026-07-14 — h4→h3一括変換（69ページ・種別=other・軽量行）

- **対象**：capa回で発見した「CSS定義のない`<h4>`小見出し」の残り全ページ。**事前実測**＝69ページ・266見出し・全て属性なし`<h4>`・セクション本文内のみ・既存h3との混在ゼロ・`#h3-`アンカー参照ゼロ・全ページに`.essay h3`CSS定義あり・**EN側69ページはh4ゼロ（ビルダー変換済み）＝EN/JSON対応不要**。
- **内容**：`<h4>` → `<h3 id="h3-NN">`（ページ内出現順連番・文言不変）。ページごとに可視テキストcharacter-identical・変換完全性・連番一意性をassertしながら機械変換。
- **検証**：変更69ファイル全てphotographers/配下・EN/JSON差分ゼロ・h4残存ゼロ（JA/EN）・check_content_loss OK（WARNなし）・preflight OK。

## 2026-07-15 — 5名バッチupdate（ChatGPT新素材で本文全刷新・joel-meyerowitz/joel-sternfeld/lewis-baltz/robert-adams/mapplethorpe）

- **種別**：update×5（既存本文869〜1269字 → 新素材3754〜4995字の全文刷新）。素材=re-photographer/20260715/（JA/EN・clean。masahisa-fukase-final.htmlはEN素材が無く**対象外・保留**）。
- **分業**：**Fable監督・監査／Codex（MCP・workspace-write/never）実装**。パイロット（robert-adams）→監査→残り4名。Codex呼び出し6回・Codexバグ0・engine穴0（前回までの恒久修正が全部効いた）。安全ガードで3回正しく自主停止（Sternfeld/Baltz のEN Related置換ガード2回・EN JSONリンク消失HARD FAIL 1回）。
- **監督判断（実測）**：
  1. **§RELは今回「素材採用」**（前回までの「既存維持」と逆）：meyerowitz 7/7・baltz 6/6・adams 6/6 は素材リンク全実在でそのまま採用。**sternfeld は素材の裸項目5件（Eggleston/Shore/Robert Adams/New Color/New Topographics）をスクラッチコピーでリンク化**・Postdocumentary（ページ無し）は項目削除→7/7。**mapplethorpe は裸項目5件（ページ無し）を削除し既存 Staged Photography 項目を合流**→3/3。JA/EN一致。
  2. **旧EN Related 5リンクの置換ガード（sternfeld 3・baltz 2）**：§REL全面刷新に伴う意図的置換と認定し `build_photographers_en.py --force`。
  3. **旧Sources URL消失6件**（sternfeld Met 1 / baltz Getty 1 / mapplethorpe ICP・mapplethorpe.org・Smithsonian×2）：全刷新に伴う正当な置換 → intentional-replacements 6宣言追加。**push後にstale WARN化したら削除**。前回バッチのstale 2宣言（don-mccullin Tate / ed Stedelijk）は削除済。
  4. **hero Years空欄・Country年代文字列は既存維持**（サイト標準・補正しない）。precheckのCJK比率言語WARN 4件は英語出典が多い素材の誤検知と判断（advisory）。
  5. **data-nosnippet 各1減WARN**は旧prep-block（作品リンク準備中）→実コンテンツ置換によるもの。正当・許容。
- **ui-terms**：追加0（untranslated WARN 0。ポストドキュメンタリー等の未登録運動語はkeywords面に出ず発火せず）。
- **面（tracked 12）**：JA5＋EN5＋en-content.json（対象5キーのみ・assert通過）＋intentional-replacements.json。カード・年代・国・運動・スターマップ面は不触（既存写真家）。
- **フィデリティ（5名計）**：本文5287→21715字・unique cite 17→84・sup-ref 28→132・dangling 0・Entry/idx・entry-meta Country（リンク付）全員verbatim維持・EN不可視要素（GA/canonical/hreflang/OG/og:image/JSON-LD日付/data-nosnippet）全員維持。
- **検証**：check_content_loss OK／5slug --dry-run SKIPPEDなし・untranslated 0／**preflight FAIL 0**（WARNは許容済data-nosnippetのみ）／en-content変更は対象5キーのみ／対象外巻き込み0／素材原本ハッシュ不変。
- **backup（未追跡・GH Pages実機確認後に削除）**：photographers/<slug>-backup.html×5・en/photographers/<slug>-backup.html×5・scripts/<slug>-spec.json×5。
- **wall-time**：29分（Daisuke実測。engine穴0・全機械化。1名あたり約5.8分＝過去最速）

## 2026-07-15 — masahisa-fukase（ChatGPT新素材で本文全刷新）

- **種別**：update（JA本文882→7104字、unique出典3→17、sup-ref 24→38、§REL 2→7、作品リンク2→8）。
- **bug / engine改良**：なし。Related置換ガードは発火せず、EN JSONリンク消失HARDは承認済みArtforum PDF 1件だけを scoped intentional-replacement 宣言で処理。
- **手作業点**：3点。①素材§RELの裸WORKSHOP項目をJA/EN各1件削除、②external_links_html全刷新（MoMA後継URL採用・Setanta shop意図的削除）の監督承認、③works ui-terms 6件の文言監査・承認。ボトルネックは§RELの実在リンク判定と旧URL消失の意図確認。
- **面（tracked 6）**：JA/EN個別ページ2＋en-content.json（masahisa-fukase.htmlキーのみ）＋ui-terms.json（6件）＋intentional-replacements.json（1件）＋本ログ。カード・年代・国・運動・スターマップ面は不触。
- **フィデリティ**：JA適用後検証OK、ENビルド1ページ・dry-run SKIPPEDなし、§REL 7リンク全て実在、Entry/Country JA/ENともbackupからverbatim維持、GA/canonical/hreflang/og:image/JSON-LD維持。
- **検証**：check_content_loss OK／preflight FAIL 0（既存他作家のstale intentional-replacement WARN 6件のみ）／対象外巻き込み0／素材原本ハッシュ不変。
- **commit**：未コミット。
- **wall-time**：13分（Daisuke実測）。

## 2026-07-17 — yuki-tawada（new / 新規追加・多和田有希・idx304・era2000）＋importer積み残し7件を実装

- **種別**：new（純・新規追加）。素材=re-photographer/yuki-tawada(8).html / yuki-tawada-en.html（JA/EN・v5.1型・revision-latest赤字マーカー入り）。slug=yuki-tawada。
- **分業**：**Fable監督・監査／Codex（MCP・workspace-write/never）実装**。監督側で全判断（spec全項目・idx=304・era=2000・artText=治癒・GENRE_TAG/terms追加語・運動ページ面スキップ判断）とパイプライン実行。Codexはimporter機能実装のみ（触ってよいファイル明示・Web検索禁止・py_compileまで）。Codex呼び出し2回・逸脱0。
- **importer積み残し実装（memoの残り全件＋新規1件）**：
  - **②render-ja head属性順正規化**（新規経路のみ・meta=name/property/http-equiv先頭・link=rel先頭。素材のcontent-first meta 12→0を実測）。
  - **③ENトグル自動リンク**（新規renderで /en/photographers/<slug>.html を保証・既に正しければbyte不変）。
  - **④works_labelsキー正規化＋↗strip統一**（キー=実ラベルverbatim・em dash保持／`\s*↗\s*$` の単一ヘルパー `_strip_trailing_arrow` に統一）。
  - **①e §RELラベル抽出許容拡大**（"Related Photographers…"/"Related Movements…"/"Related Themes…"包含判定＋href種別優先）。
  - **⑤precheck WARN 2種**（ジャンル語GENRE_TAG/ui-terms未登録・hero眉標準形）— 本番で両方正しく発火。
  - **⑦本文初出リンク候補の印字**（precheckで印字のみ・**render_ja_pageの全自動 `_link_body_names` は撤去**＝メモの「全自動禁止→半自動」方針どおり。今回素材は候補0）。
  - **（新規）revision-latestマーカーstrip**（span unwrap・複合classからトークン除去・編集確認用CSS除去。JA/EN各15箇所→出力0・可視テキスト不変）。
- **engine穴1件（発見→即修正）**：④でui-terms新キーがem dash保持になった一方、build_photographers_en.py のworksルックアップがdash潰し正規化キーで照合→untranslated WARN 4件。**verbatim→legacy正規化キーの2段フォールバック**をCodexが実装（旧「 - 」キーの後方互換維持）。修正後WARN 0。
- **判断点（実測）**：
  1. **運動ページ面はスキップ**：hero Movement=ポスト・フォトグラフィーは movements/ページ未存在・STUB_TO_SLUG未登録・素材の§REL運動3項目（ポスト・フォトグラフィー/写真の物質性/写真療法）も全て裸テキスト＝リンクすべき既存運動ページなし。eiko回（抽象写真→モダニズム採用）と違い、entry-meta/§RELがリンクする既存運動が無いため無理な所属付けをしない。star用movementsに日本写真を入れ星座接続は確保。
  2. **GENRE_TAG/terms追加1語**：「ポスト・フォトグラフィー」→ Post-Photography（build_archive_en.py）/ Post-photography（ui-terms terms）。
  3. **works ui-terms 7件**：merge-to-en自動提案を全承認（素材EN準拠・em dash保持を確認）。
  4. **check_new_photographer残WARN 2件は許容**：body_links_scarce（precheck候補0＝素材に既存slug該当名なし）・en_graph_absent（EN標準）。
  5. **en/countries/japan.html のTomatsu lede差し替え1件**は正本card-data準拠への追い付き（stale HTML→再生成）で消失ではない。
  6. stale intentional-replacement（masahisa-fukase Artforum PDF・push済）を削除→preflight WARN解消。
- **面（tracked 16）**：新規JA/EN個別ページ2（未追跡）＋archive/cards-archive JA・card-data・countries japan JA/EN・eras2000 JA/EN・en/archive・en-content(+21 add/replace 0)・ui-terms(+8=works7+terms1)・supplement・star bin・scripts3（import_chatgpt / build_photographers_en / build_archive_en 1行）＋intentional-replacements.json（-1）＋new-design/cards-archive.html（git-ignore・投入済）。
- **フィデリティ**：JA 4節・cite 25・sup-ref 35・dangling 0・span balance OK。EN merge add=21/replace=0・他slug byte不変assert通過。ph-book「Her smoke rose up forever」JA/EN inner HTML無傷。EN不可視要素（GA/canonical/hreflang×3/JSON-LD/data-nosnippet）維持。全7面で本人参照=1・photographers.js混入0（星bin/supplement各1）。
- **検証**：check_new_photographer OK／check_content_loss OK／link integrity OK／EN --slug --dry-run SKIPPEDなし／**preflight FAIL 0**（残WARN=en/countries/japan・en/eras/2000の「直接編集疑い」＝scoped再生成への既知の誤検知）。`--all`不使用・link_country_keywords不実行・対象外巻き込み0・素材原本ハッシュ不変。
- **backup（未追跡・GH Pages実機確認後に削除）**：archive-backup.html等は前回分が既存のため据え置き＋eras/2000-backup.html・new-design/cards-archive-backup.html・card-data-backup.json・supplement/star binバックアップ（add_photographer自動）・scripts/yuki-tawada-spec.json（未追跡のまま残す）。
- **wall-time**：23分（Daisuke実測。importer積み残し7件＋engine穴1件の実装込み）

## 2026-07-18 — 3名バッチupdate（ChatGPT新素材で本文全刷新・takuma-nakahira/chris-killip/kruger）

- **種別**：update×3（既存本文1213/891/1559字 → 新素材5035/5142/5264字の全文刷新）。素材=re-photographer/0717/（killip・kruger JA/EN）＋re-photographer/直下（takuma-nakahira-final-complete.html / takuma-nakahira-en.html）。依頼文は「新規追加」だったが、**3名とも全サーフェス（個別JA/EN・card-data・archive3面・eras/1970・国・運動計3〜5面・星bin）収録済みを事前実測**→update認定・カード/年代/国/運動/星マップ面は不触（追加不要＝既に整合）。
- **分業**：**Fable監督・監査／Codex（MCP・workspace-write/never）実装**。パイロット（takuma-nakahira）→監査→残り2名。Codex呼び出し5回・Codexバグ0・逸脱0（ui-terms候補で2回・preflight HARDで1回、正しく自主停止）。engine穴0。
- **監督判断（実測）**：
  1. **§REL全員「素材採用」**：素材§RELリンク先全実在（moriyama/parr/sherman/arbus＋各運動ページ）・既存§RELリンクは全て素材に包含＝消失なし（2→7・1→7・4→7件）。ガード発火なし・--force不使用。
  2. **precheck言語WARN 2件（killip 14.38%/kruger 14.74%→en誤判定）は誤検知**：英語見出し・引用の多い素材（07-15バッチと同型のadvisory）。
  3. **works ui-terms 2件承認**（素材EN準拠）：MOMAT — Takuma Nakahira: Burn—Overflow / Smithsonian — Belief+Doubt (video)。
  4. **kruger旧Sources 3URL消失（ICP pictures-generation/Tate artist/TheArtStory）は正当置換**：3URLとも新素材JA/EN不在を実測→intentional-replacements 3宣言追加。**push後にstale WARN化したら削除**。
  5. hero Years空欄・Country値は既存維持（サイト標準・補正しない）。data-nosnippet各1減WARNは旧prep-block→実コンテンツ置換の既知正当パターン。
- **面（tracked 9）**：JA3＋EN3＋en-content.json（対象3キーのみ・他slug不変assert通過）＋ui-terms.json（+2）＋intentional-replacements.json（+3）。
- **フィデリティ（3名計）**：本文3663→15441字・unique出典12→81・§REL 7/7/7・EN photobooks_html carry-forward 3名（229/226/2030字無傷）・dangling 0・Entry/idx verbatim維持（No.111等）・JA/ENともdiv/section開閉一致・revisionマーカー残存0・EN不可視要素（GA/canonical/hreflang/og:image/JSON-LD/data-nosnippet）全員維持。
- **検証**：check_content_loss OK／link integrity OK／3slug --dry-run SKIPPEDなし・untranslated 0／**preflight FAIL 0**（WARN=data-nosnippet 6件のみ=許容済）／対象外巻き込み0（card-data/archive/eras/countries/movements/star bin差分ゼロ）／素材原本6ファイルmtime・サイズ不変。
- **backup（未追跡・GH Pages実機確認後に削除）**：photographers/<slug>-backup.html×3・en/photographers/<slug>-backup.html×3・scripts/<slug>-spec.json×3（specは未追跡のまま残す）。
- **commit**：あり（本行のコミットと同一）。
- **wall-time**：16分（Daisuke実測。1名あたり約5.3分）
