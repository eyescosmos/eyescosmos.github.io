# EN写真家ページ 正本HTML化 — 移行計画（新規セッション用の引き継ぎ）

**いつ読むか:** `en/photographers/*.html` の正本を `data/archive/photographers-en-content.json` から
HTML自身へ移す作業を始めるとき。設計は 2026-09-12 に Opus 監督 / Codex 設計で確定。
**この文書が方針の正本。** 実装セッションはまずこれを読む。

---

## 0. なぜやるか（2026-09-12 の実測。再検証しなくてよい）

| 実測 | 値 |
|---|---|
| EN正本JSON | 12.4MB / 414エントリ / 1エントリ28フィールド |
| `build_photographers_en.py --all` で現HTMLと内容が変わるページ | **60 / 394（15%）** |
| うちキーワードchipから運動ページへのリンクが消えるページ | **28**（`link_country_keywords.py` がHTMLへ直接張ったもの。JSONに存在しない） |
| その消失を検知したガード | **0本**（`preflight` / `check_content_loss` / builder内 `detect_content_loss` すべて素通り） |
| 旧本文同期監査の drift | **1 / 414**（＝essay本文だけは同期している。ずれているのは本文の外側） |
| 6名バッチでのENコマンド内訳（計91回） | ビルダー実行27(30%) / 生成HTMLを読んで検証26(29%) / 正本を覗く20(22%) / 正本を書換7(8%) / その他11(12%)。JAは30回 |

**結論**：コストの主因は「JSONを直す→ビルダーを回す→生成物を読む」の往復で、劣化がゼロでも毎回発生する。
劣化（巻き戻し）は別問題で、こちらは**誰も検知していない**。HTML正本化はこの2つを同時に消す。

**部品は半分そろっている**：`extract_bundle(raw_html, source_lang)` は既に `"ja"` / `"en"` 両対応で、
0912のEN素材で実測確認済み。`render_ja_page` に対応する **`render_en_page` だけが無い**。
共通chromeをHTMLへ直接注入する方式は `scripts/ai_disclosure.py` + `inject_ai_disclosure.py --all` で実績あり。

---

## 1. 全体方針（確定）

- **既存414ページのHTMLは作り直さない。今あるbyte列をそのまま正本に昇格させる。**
  JSONから再描画する一括変換は上の60ページ差分を再発させるので**採用しない**。
- **`render_en_page` は新規ページ専用。既存ファイルへの上書き経路を作らない**（`--force` も設けない）。
- **ガードを先に入れてから正本を切り替える。** builder の安全網を失う前に代替を用意する。
- 既存の禁止事項（`generate_photographer_pages.py` / `generate_archive_pages.py` 実行禁止、
  分類生成器のスコープ必須、TOP12等の非対象サーフェス保護）は**移行を理由に解除しない**。
  ※ 前2本は移行完了後の 2026-09-15（§12.3）に**削除**された。禁止は「復活させない」に変わった。

---

## 2. 見積もりの根拠（2026-09-12 にコードを実測）

Codex の初回見積もりは合計5日だったが、**付け替えと抽出で済む所を新規構築として数えていた**。
実測で引き直した結果が下の2.5〜3日。

| 実測 | 値 | 意味 |
|---|---|---|
| `render_ja_page` の実装 | **52行** | 薄いオーケストレータ。scaffold を呼んで `_inject_*` / `_build_ja_*` を並べるだけ |
| `build_photographers_en.py` の `rebuild_*` 関数 | **16本** | header / crumbs / hero / abstract / thesis / entry_meta / keywords / works / related / further / sources / sidebar / side_nav / footer。**EN を描く部品はすべて既存** |
| `preflight.py` のチェック関数 | **33本**（うちEN専用が約10本） | 大半は「読み先を JSON から HTML へ向け直す」だけ |
| §3のガードのうち**本当に新規** | **3本** | §REL日英対称性 / 節数日英対称性 / keyword chipリンク保存 |
| `build_scaffold_html(spec, idx)` | 外部ファイル `SCAFFOLD_BASE` を読む作り | EN scaffold は「既存の良いENページを1枚 clean up して置く」で足りる可能性が高い |

**したがって `render_en_page` は新規開発ではなく抽出。** JSON の page dict ではなく bundle を
食わせるアダプタを噛ませれば `rebuild_*` はほぼそのまま動く。

**唯一の未知数は EN scaffold。** ここだけはコードから読めないので、実際に1枚作るまで見積もれない。
→ だから下の順序に **C-spike** を入れてある。

---

## 2a-DONE. 最小版は 2026-09-13 に完了・push 済み（`d09dbed7c`）

**§2a の4項目はすべて入っている。以降の記述は背景として読む。**

| 項目 | 実装 |
|---|---|
| 1. `check_en_direct_edit()` 削除 | 削除済み。**あわせて `check_en_changed_slug_closure()` も削除**（EN HTML に cite を直接足すと JSON と集合が食い違い HARD FAIL になり、最小版が成立しないため）。`scripts/check_en_entry.py` の `check_html_vs_json()` も既存ページでは検査しない（同じ理由。通常フローの検査が毎回 FAIL するため） |
| 2. builder が既存ページを拒否 | 当時は `🛑 REFUSED` と `ALLOW_EN_REBUILD=1` を導入。**その後、総ざらいフェーズ2で builder CLI と escape hatch を撤去済み。** 現在は module-only で、rollback は git で行う |
| 3. 新規ガード3本 | `check_en_keyword_chip_preservation()` / `check_ja_en_rel_symmetry()` / `check_ja_en_section_symmetry()` を `preflight.py` に追加 |
| 4. 文書更新 | `CLAUDE.md` / `AGENTS.md` / `docs/generators-and-guards.md` の正本マトリクスとENフローを更新 |

**ガード3本の判定方式は「回帰検知」にした（設計の変更点）。** §3 は touched-only HARD を求めているが、
実測した既存バックログが §REL人物 27ページ / §REL運動 11ページ / 節数 8ページ /
chip本文-sidebar不一致 7ページ（401ペア中）あり、現在値でHARDにすると無関係な push が止まる。
そこで **baseline（`origin/main`）にも在った非対称は WARN、今回の変更で新しく出たものだけ HARD** にした。
`check_content_loss_guard` と同じ設計で、狙っている事故（JA を直して EN を忘れる／chip のリンクが剥がれる）は
すべて「新しく出たもの」なので取りこぼさない。

**フェーズB の完了条件は実データで確認済み。** builder の出力を書き込まずに再現して
`preflight._chip_map` で比較したところ、**リンク付き chip が裸 span に退行するページを 28 件検出**した
（§0 の実測値と一致）。ansel-adams で chip 裸化 / JA §REL 1件削除 / EN 節1つ削除を実際に作って
`PREFLIGHT_BASE=HEAD python3 scripts/preflight.py` が HARD FAIL することも確認した。

**既知の副作用（未対応・フェーズE で片付ける）**：`scripts/import_chatgpt_photographer.py` の
`_verify_after_inject()` は既存ページに対し builder を回して結果を検証するので、**既存ページへの
thesis 注入フローは REFUSED で止まる**。既存ページの修正は EN HTML の直接編集に切り替える（それが最小版の狙い）。

---

## 2a. ★まず読む — 「昇格」自体はほぼタダ。3日の中身は昇格ではない

**今のHTMLを正本と宣言するだけなら、ほぼ何もしなくてよい。** EN ページは既に HTML から配信されており、
`--all` は誰も回していない。今日 JSON の編集をやめて HTML を直接触り始めても、何も壊れない。

3日の内訳は昇格ではなく、**builder が代わりにやっていた2つの仕事を作り直す費用**である。

| 3日の中身 | 何を買っているか |
|---|---|
| B（1日） | 今は無いガード |
| C-spike + C（1.5日） | **新規ENページを作る手段**（今は JSON + builder しか無い） |
| E（1日） | 17本のスクリプトの付け替え |
| **D（2時間）＝昇格そのもの** | **ほぼ費用ゼロ。実体は文書更新とコード経路の削除** |

### したがって推奨は「最小版」を先に出すこと（約1日）

**既存ページの編集だけを HTML 正本に切り替え、新規作成は当面 JSON + builder のまま残す。**

やることは4つだけ:

1. `preflight.py` の `check_en_direct_edit()` を**削除する**（14行・WARN）。
   EN HTML の直接編集が異常ではなく通常手順になる
2. `build_photographers_en.py` が**既存ページに対しては既定で実行を拒否する**ようにする
   （明示の環境変数でのみ解除）。うっかり再生成して巻き戻す経路を塞ぐ
3. §3の**新規ガード3本**を入れる（§REL日英対称性 / 節数日英対称性 / keyword chipリンク保存）
4. `CLAUDE.md` / `AGENTS.md` の正本マトリクスを更新する
   （EN写真家ページ＝**既存はHTML自身が正本 / 新規のみ JSON 経由**）

**これで何が手に入るか**：既存ENページの修正が JA と同じ「直して終わり」になる。
0912バッチで言えば、フェーズ3の既存12ページ＋監督の§REL修正4ページが、
すべて往復なしで済んでいた。**ENの手間の大半はここにある。**

**これで手に入らないもの**：新規追加はJSON+builderのままなので、バッチあたりのビルダー実行は残る。
JSONも残るが、既存ページについては誰も読まなくなるので、陳腐化しても実害が消える。

### 残り2日（C-spike / C / E / F）を追加で買う価値
新規作成もHTMLネイティブになり、JSONが完全に消える。ただし対象はバッチあたり数名の新規追加だけで、
**最小版が消す「既存ページ編集の往復」より効果は小さい。**
→ **最小版を先に出し、1バッチ回して効果を測ってから C 以降を判断する。**

---

## 2b. フェーズと順序（各フェーズに巻き戻し点がある）

### フェーズA — 移行台帳を固定する（3時間）
base + stage4 の有効entry / 現存EN実ページ / `jp-漢字` shim / `HAND_MAINTAINED_EN` /
JSON未登録HTML / JSONだけのentry を分類し、各ファイルのhashと構造指標を保存する。
- **★出力は機械可読な台帳ファイル1本にする（散文にしない）。** B・D・E がこれを読む
- **★一度きりのスナップショットにせず、再生成できるスクリプトにする。** ページは増える
- 完了条件：全対象が「実ページ / shim / 未公開データ / 例外」のどれか1つに分類され、未分類0件
- 巻き戻し：台帳コミットを取り消すだけ。公開HTMLは不可触

### フェーズB — HTML正本用ガードを先行実装する（1日）★単独で価値がある・ここで止めてよい
§3のガード一式。新規は3本、残りは既存関数の読み先変更。既存のJSONガードと**一時併走**させる。
- 完了条件：fixture上で cite / §REL / §REF / keyword chipリンク を各1件消すと必ず非0終了する。
  **28ページ相当の「リンク付きchip→裸span」を実データで検出できることを確認する**
- 巻き戻し：ガード追加コミットだけ取り消し、現行JSON運用を継続
- **★ここが自然な停止点。** 移行に進まなくても、今日見つけた消失クラスは止まる

### フェーズC-spike — EN scaffold が成立するか確かめる（半日）★未知数をここで潰す
既存の良いENページを1枚 scaffold 化し、`rebuild_*` 群でそのページを**再現できるか**だけを見る。
- 完了条件：既知のENページ1枚を scaffold + `rebuild_*` から再構成し、意味データが一致する
- **失敗したら C 以降を再設計する。** B までの成果は残るので損失は半日

### フェーズC — `render_en_page` を新設する（1日）
`extract_bundle(raw_html, "en")` + EN scaffold から**新規ページだけ**を生成する。
`build_photographers_en.py` の `rebuild_*` を抽出して再利用する（書き直さない）。
**既存ファイルへの書込みは既定で拒否。`--force` を作らない。**
- 完了条件：抽出→描画→再抽出した意味データが一致し、JA renderer と同じ必須構造検査を通る
- 巻き戻し：renderer と fixture のコミットを取り消す。builder には影響させない

### フェーズD — 既存ENを一括で正本へ昇格する（2時間）
再生成も整形もしない。台帳上の実ページを**そのbyte列のまま**正本と宣言する。
`HAND_MAINTAINED_EN` の5件も通常実ページへ統合する。実体はコード経路の削除と文書更新。
- 完了条件：**昇格コミットで `en/photographers/*.html` の内容差分が0**。全HTMLガードが通る
- 巻き戻し：コミットを取り消す。HTMLが不変なので内容復元は不要

### フェーズE — 利用経路を切り替える（1日・2段に割る）
- **E-1（先）**：読み取り専用＝`preflight.py` / `check_en_entry.py` / `check_new_photographer.py` /
  `en_entry.py` / `peek.py` / `en_content.py`
- **E-2（後）**：書き込む＝`import_chatgpt_photographer.py` / `add_photographer.py`
- 完了条件：新規fixtureを `render_en_page` で作成し、EN HTMLだけの編集で検査完了できる。
  **通常フローにJSON編集とbuilder実行が一度も現れない**
- 巻き戻し：スクリプト配線と文書のコミットを取り消す

### フェーズF — JSONを降格する（1時間）
base / stage4 / 有効合成結果 / 移行台帳を読み取り専用アーカイブへ移す。**削除はしない。**
- 完了条件：通常スクリプトから base/stage4 への読み書き参照が0

**合計2.5〜3日。** A → B →（停止判断）→ C-spike → C → D → E-1 → E-2 → F の順。

### なぜこの順序か
- **A が先**：B・D・E が台帳（shim一覧・除外一覧）を読むので依存が実在する。ただし3時間で切る
- **B が2番目**：移行に進まなくても価値が残る唯一のフェーズ。ここまでなら約1.5日で、
  今日の28ページ級の消失が二度と素通りしなくなる
- **C-spike を C の前に置く**：EN scaffold が計画中で唯一コードから読めない未知数。
  ここが崩れると C 以降の設計が変わるので、1日を投じる前に半日で潰す
- **D は C の後**：正本を切り替える前に、新規作成の手段が用意できていること
- **E は D の後、かつ2段**：17本を一度に切り替えない。読むだけのものを先に通す

---

## 3. EN に必要なガード（フェーズBの中身）

「baseline比の消失」と「現在値として必須」の二層。**touched-only を HARD、既存全体の穴は初期WARN**
（既存不具合で無関係なpushを止めないため）。

- **本文保存**：essay節数・各節見出し・lead・thesis・FIG・cite ID・§WORKS・§REL・§REF・§SRC の
  消失を個別にHARD検知。総section数だけでは代替不可
- **URL保存**：§WORKS / §REL / §REF / §SRC / 本文内の外部・内部href集合の減少を検知
- **cite整合**：EN単体のsup-ref参照先・重複・欠番・孤立cite。加えて **JAとENの `cite-N` 集合を完全一致**
- **§REL対称性**：JAの人物リンクと運動リンクを別集合で抽出し、JA hreflang / 明示slug表でEN実slugへ
  正規化してEN §RELと比較。片側欠落はHARD、説明文の有無は別WARN
  （★2026-09-12にこの欠落で1周損した。EN §RELのリンク実体は `site_directory_html` であり
  `related_annotations` は注釈辞書にすぎない、という構造が原因）
- **★JA/ENの本文節数対称性**（Codex案に監督が追加）：builder を捨てるとJAの構造変更がENへ伝播しなくなる。
  JAに節を足してENを忘れると静かに非対称になる。節数と各節の対応をHARDで見る
- **keyword chip保存**：`ph-kw` / `ph-side-chip` ごとに「正規化表示語→href」をbaseline比較。
  リンク付きchipが裸spanになる・hrefが変わる・本文とsidebarの対応が崩れる場合をHARD。
  **これが今回の28ページを捕まえる本命**
- **keyword実在性**：対応するEN movementページが存在するchipは本文・sidebarともリンク必須。
  非実在概念語は裸のまま許容
- **言語・パス**：`lang="en"` / ENトグルactive / JAトグルだけがJA写真家パスを指す。
  本文・§REL・keyword・ナビへの `/photographers/` 混入はHARD
- **SEO必須値**：GA `G-2VRTV8BZEJ` / title / meta description / canonical自URL /
  hreflang ja・en・x-default / og:image / og:url / Twitter / parse可能なJSON-LD Person の**存在**検査
  （baseline比の減少だけでは不足）
- **日英往復**：JA hreflangのEN URLとEN canonical、EN hreflangのJA URLを相互照合
- **sidebar検索**：`input.ph-side-search__input:not([id*=mobile])` が一意で `aria-controls` が実在候補欄を指す
- **DOM構造**：section/div開閉・h1が1個・TOCのsec/h3参照先・重複ID・必須class・CJK残存率
- **リンク健全性**：内部リンク実在・外部一文字アンカー・禁止出典・Amazon検索URL・tracking URL（既存継承）
- **入口整合**：card ID / JA実ページ / EN実ページ / 実slug / shim の関係が一意。
  **shimは本文・SEO検査の対象外**
- **共通chrome**：AI開示 / header / sidebar / footer / `data-nosnippet` が共通正本と一致

---

## 4. 17本のスクリプトの処遇

(a)HTMLを読むよう改修 / (b)役目終了 / (c)移行用に残す / (d)要判断

| スクリプト | 移行後 | 分類 |
|---|---|---|
| `add_photographer.py` | `render_en_page` によるEN HTML新規作成を案内・検証 | a |
| `check_en_entry.py` | 対象EN HTMLだけから全検査。JSON closureとHAND例外を削除 | a |
| `build_photographers_en.py` | 移行監査・緊急rollback比較専用に**凍結**。通常運用から外す | c |
| `check_content_loss.py` | ENもJAと同じHTML正本メッセージにし §REL / §REF 等を強化 | a |
| `check_new_photographer.py` | EN HTML実在・入口レジストリ・構造・SEOを検査 | a |
| `en_content.py` | EN HTML列挙 / slug解決 / 構造抽出helperへ置換（名称も変更） | a |
| `en_entry.py` | 対象HTMLの lead / thesis / 各節 / cite / リンク / SEO を要約表示 | a |
| `peek.py` | HTMLの意味ブロックを短く表示する機能へ差し替え | a |
| `preflight.py` | touched EN HTMLを正本としてJA相当ガードと日英対称性を検査。HTML直接編集警告とJSON closureは削除 | a |
| `sync_en_rel_annotations.py` | JA/EN HTML間のreportを主とし、適用は対象EN §RELの明示編集のみ | a |
| `import_chatgpt_photographer.py` | `extract_bundle(..., "en")` → `render_en_page` でEN HTMLを直接新規作成 | a |
| 移行時の収穫・本文同期監査スクリプト | 移行完了後のフェーズ1で撤去 | c |
| 年代別・個別の一回限り修正スクリプト4本 | 過去処理の完了後、フェーズ1で撤去 | b |

`data/photographer-essay-overrides.js` の `textEn` も棚卸し対象（EN本文の影の正本）。原則EN用途を廃止する。

---

## 5. 監督が決めた論点（Codex提示の選択肢に対する裁定）

| 論点 | 決定 |
|---|---|
| JSONの最終処遇 | **アーカイブへ降格し、削除しない**（12MBなので保持コストは無視できる。Codex案Bの「1リリース後に削除」は取らない） |
| stage4 | 有効合成結果と由来を台帳へ記録し、機構を廃止。HTMLへ再注入しない |
| `HAND_MAINTAINED_EN` | 廃止。全実ページを同じHTML正本として扱う。履歴は台帳にだけ残す |
| `jp-漢字` shim | 維持。ローマ字実ページだけを正本にし、shimは入口・redirect先・二重実ページ防止だけ検査 |
| JSON未登録HTML / JSONだけのentry | **ファイル実在を公開正本の基準**にする。JSONだけのentryはアーカイブ |
| EN内のJAパス | 言語トグル以外は全面禁止。EN版が無い関連項目は裸テキスト |
| JA/ENのcite番号 | 完全一致をHARD。例外はslug・番号・理由・期限つき宣言のみ |
| §REL対称性の範囲 | 人物・運動のslug集合を完全一致（説明文の一致までは求めない） |
| 共通chromeの同期 | 日英共通の注入器＋構造ガード。`ai_disclosure.py` の形を header / sidebar / footer へ広げる |
| `render_en_page` の上書き | **新規ファイル限定。`--force` を作らない** |
| `overrides.js` の `textEn` | EN用途を廃止。撤去までの期間だけ不一致ガードを置く |

### 未決（Daisuke判断が要る）
- **いつやるか。** 2.5〜3日。写真家バッチとは同時に進められない（フェーズC〜Eの間）
- **A+B（約1.5日）でいったん止めるか、Fまで通すか。** B は単独で価値があるので、
  A+B を先に走らせて効果を見てから C 以降を判断する、という分け方ができる

---

## 6. 実装セッションへの申し送り

- **写真家バッチと並行してよいフェーズ / いけないフェーズ**（下表）。
  止めるのは **D・E・F の約1.5日だけ**で、A・B・C の間は通常どおりバッチを回してよい

| フェーズ | バッチ可否 | 理由 |
|---|---|---|
| A 台帳 | ○（短いので避けるのが楽） | 読み取りのみ。台帳は再生成できるので、バッチが入ったら回し直す |
| B ガード | ○（避けるのが望ましい） | 現行パイプラインに触れない。ただし開発中のガードが誤ってHARDを出すと push が止まる。**そこでガードを無効化して通さないこと** |
| C-spike / C | ○ | `render_en_page` は既存ファイルへの書込みを拒否する。旧経路は無傷 |
| **D 昇格** | **×** | 完了条件が「昇格コミットで EN HTML の内容差分0」。新規ENページが混ざると原子的な切替が成立しない |
| **E 経路切替** | **×（最も危険）** | スクリプトが半分ずつ切り替わり、**正本が2系統同時に生きる**。旧importerがJSONへ書き、検査はHTMLを読む、という食い違いが起きる |
| **F 降格** | **×** | JSONを移動するので、参照が残っているツールが壊れる |

- **D・E・F は連続した1本の作業として通す。** 二重正本の窓をできるだけ短くする。
  途中で急ぎのバッチが入ったら、**並走させずにそのフェーズを完了させるか巻き戻す**（各フェーズに巻き戻し点がある理由）
- SEO選定の定期実行（毎月10日）はページを書き換えないので、どのフェーズ中でも走らせてよい
- **見積もりは実測で引き直してある（§2）。Codex初回の5日は水増し。**
- **効果の測り方**：移行後に1バッチ回し、ENに触れたコマンド数を数える。
  **baseline は 2026-09-12 の6名バッチで91回**（JAは30回）。ここが減らなければ移行は失敗
- フェーズごとに `docs/importer-run-log.md` へ実測を残す
- Codexの生設計は本文書に取り込み済み。原文は保持していない

関連：`docs/importer-scaffold-inject-spec.md`（§1の3部品アーキテクチャ・§14のバッチ定型）/
`docs/generators-and-guards.md`（機械チェックの意味）

---

# ★フェーズC 引き継ぎ（2026-09-14・新規セッションはここから読む）

> **★2026-09-15: 全フェーズ完了。この移行は終わった。**
> 結果は §8（C）/ §9（A）/ §10（D）/ §11（E-1）/ §12（E-2）/ §13（F・総括）にある。
> **§1〜§7 は着手前の計画で、§8〜§13 が上書きしている。新規セッションは §13 から読むこと。**

## 1. いまどこまで終わっているか

| フェーズ | 状態 |
|---|---|
| A 台帳 | **完了（2026-09-14）。`data/en-migration-ledger.json` + 再生成器。§9 を読む** |
| B ガード | 新規3本は稼働中（chip保存 / §REL対称 / 節ラベル対称）。既存ガードの読み先付け替えは未 |
| C-spike / C | **完了（2026-09-14）。§8 を読む** |
| D 昇格 | **完了（2026-09-14）。公開HTML 820枚の sha256 不変で証明済。§10 を読む** |
| E 経路切替 | **完了（E-1 2026-09-14 / E-2 2026-09-15）。§11・§12 を読む** |
| F JSON降格 | **完了（2026-09-15）。** JSON は読み取り専用アーカイブ。preflight が変更を HARD で止める。§13 を読む |

**実運用**：既存ENページは HTML 直接編集で完結する。2026-09-14 の5名 update で実証済み
（正本JSON編集0回・ビルダー実行0回・`git diff` で確認）。**新規作成だけが JSON + ビルダーのまま。**

## 2. なぜCをやるか — 「コマンド数」で測ると判断を誤る

2026-09-13 に監督が「Cが買えるのは新規1名あたり3コマンドだけ」と見積もったが、
**これはビルダーを1回呼ぶ手間しか数えていない誤った指標**だった（2026-09-14 に Daisuke の指摘で訂正）。
Cが実際に消すのは次の4つで、どれもコマンド数には出ない。

1. **正本が2系統のまま動いている。** 既存＝HTML / 新規＝JSON。ルールが2本同時に生きており、
   マトリクスを読む人間もエージェントも両方を覚える必要がある。
2. **JSONが増え続ける。** 写真家を1名足すたびに entry が1件増え、生成直後から誰も読まない死蔵データになる
   （2026-09-13 の `ed-ruscha` で415件目）。
3. **17本中14本がまだ JSON を読み書きする。** importer は新規作成で JSON に書く。
   つまり「JSONを触らない」は機械ではなく規律で守られており、最小版が塞いだ事故クラスが新規側に残っている。
4. **新規作成の経路が完成品を出さない。** `ed-ruscha` の EN 生成では、ビルダーが Person ではなく
   WebPage の JSON-LD にフォールバックし、og:image も無く、結局あとから HTML を手で直した。
   `render_en_page` はこれを直す作業でもある。

## 3. 今日できた前進 — C-spike の半分は実証済み

2026-09-14 の5名 update のために作った **`scripts/en_html_sync.py`** が、
「意味データを抜く → EN HTML へ決定論的に注入する → 日英を機械照合する」を実ページ5枚で通した。
**C-spike が確かめたかった「rebuild_* 相当の部品で EN ページを組み直せるか」のうち、注入側は済んでいる。**

残る未知数は**白紙から EN の骨組み（scaffold）を起こせるか**だけ。§2 の記述どおり、ここだけはコードから読めない。

## 4. Cでやること

`extract_bundle(raw_html, "en")` は既に `"ja"` / `"en"` 両対応（0912 実測）。
**`render_en_page` は新規開発ではなく抽出**：

- 参考にする既存実装
  - `scripts/import_chatgpt_photographer.py:1488` `render_ja_page`（52行の薄いオーケストレータ）
  - `scripts/build_photographers_en.py` の `rebuild_*` **14本**
    （header / crumbs / hero / abstract / thesis / entry_meta / keywords / works / related /
    further / sources / sidebar / side_nav / footer）。**EN を描く部品はすべて既存。書き直さない**
  - `scripts/add_photographer.py:476` `build_scaffold_html` と `SCAFFOLD_BASE`
    （JA は `photographers/ansel-adams.html` を固定コピー元にしている）
  - `scripts/en_html_sync.py`（今日追加。注入と照合の実装がある）
- **EN scaffold は「既存の良いENページを1枚 clean up して置く」で足りる可能性が高い。**
  候補は `en/photographers/ansel-adams.html`（JA の参照実装と対になる）。
- **既存ファイルへの書込みは既定で拒否。`--force` を作らない**（§5 の裁定）。
- 完了条件：抽出→描画→再抽出した意味データが一致し、JA renderer と同じ必須構造検査を通る。
  最低限 `en_html_sync.py verify` の10項目と `check_new_photographer.py` / `check_en_entry.py` が通ること。
- 巻き戻し：renderer と fixture のコミットを取り消す。ビルダーには影響させない。

## 5. 順序とバッチ並行可否（§6 の再掲）

C → A（3時間）→ D（2時間）→ E-1 → E-2 → F。
**C と A は写真家バッチと並行してよい。D・E・F は不可**（正本が2系統同時に生きる窓ができる）。
D・E・F は連続した1本の作業として通す。素材が来ていない時期を狙うのが安全。

## 6. 今日踏んだ罠（Cの設計に効くもの）

- **EN ページに `ph-thesis` ブロックが無い個体がある**（`robertfrank` / `annie-leibovitz`）。
  注入器は黙って飛ばす。`render_en_page` は必須ブロックの欠落を fail-loud にすること。
- **旧フォーマットの残骸**：`stieglitz` の EN には §REL を本文節として取り込んだ4節目があった。
  JA と節数が合わない個体は他にもありうる。
- **`§ NN / MM` の分母は JA から同期する。** 言語非依存なので EN 側で数え直さない。
- **翻訳などの外部プロセスは出力を途中状態で書く。** 完了判定はファイルサイズでなくプロセス終了で見る。
- **Met のような外部サイトは HTTP 429 を返す。** 作業中の自動事実確認はあてにしない
  （素材の事実は Daisuke × ChatGPT 担当）。

## 7. 最初に読むファイル

1. 本文書（§1 全体方針 / §3 ガード / §4 スクリプト処遇 / §5 裁定 / §6 申し送り）
2. `docs/importer-run-log.md` の 2026-09-13 と 2026-09-14 の節（最小版の実装と初回適用の実測）
3. `scripts/en_html_sync.py` の docstring
4. `CLAUDE.md` / `AGENTS.md` の正本マトリクス（既存＝HTML / 新規＝JSON の2行になっている）

---

## 8. フェーズC 完了記録（2026-09-14・Opus監督 / Codex実装）

### 8.1 結論：EN scaffold という未知数は存在しなかった

§2 と §4 は「EN scaffold だけはコードから読めない唯一の未知数」「既存の良いENページを
1枚 clean up して置くで足りる可能性が高い」と書いていた。**どちらも不要だった。**

`build_photographers_en.process_page(ja_file, page, ja_to_en, warnings)` は
**JA HTML を読み込んで各ブロックを EN へ組み直す**作りである。つまり

> **EN の scaffold は「同じ slug の JA ページ」。新しい scaffold ファイルは1枚も要らない。**

`add_photographer.SCAFFOLD_BASE`（JA が `photographers/ansel-adams.html` を固定コピー元に
している仕組み）に対応する EN 版は作っていない。**今後も作らない。**
副作用として、JA を先に作らないと EN を描けない＝ JA→EN の順序が構造的に強制され、
preflight の日英対称性ガードの前提とそろう。

### 8.2 実装したもの

| 追加 | 場所 |
|---|---|
| `render_en_page(bundle, slug, *, ja_file=None) -> (html, warnings)` | `scripts/import_chatgpt_photographer.py`（`bundle_to_en_entry` の直後） |
| `_en_head_complete()` — OGP/Twitter画像・決定論JSON-LDの補完 | 同上 |
| `_en_apply_works_labels()` — 作品ラベルを EN bundle 由来へ戻す後処理 | 同上 |
| `_validate_en_render()` — 生成後の必須構造検査（fail-loud 13項目） | 同上 |
| `EnScaffoldMissing` / `EnRenderIncomplete` | 同上 |
| CLI `--render-en <EN素材> --slug <slug>`（既定 stdout・`--apply` で新規書込） | 同上 |
| `scripts/test_render_en_roundtrip.py` — 抽出→描画→再抽出の厳密照合 | 新規 |

`bundle_to_en_entry` はrenderer内部のpage dict変換部品として維持した。
`build_photographers_en.py` も1行も変えていない（§4 分類c＝凍結。import して関数を使うだけ）。

### 8.3 裁定した論点2件

**(1) `view_works_links_html` が死蔵データだった（bug 1件）。**
`rebuild_works()` が読むのは `notable_works_html` だけで、しかも「既存に無いURLを追記する」用途のみ。
EN正本JSON 415 entry のうち **`view_works_links_html` を持つのは 308 件。これを読むコードは0本。**
結果、EN ページの作品ラベルは JA ページ由来のまま出て、`translate_residuals` の ui-terms 辞書に
載っている語だけが英訳されていた＝**辞書に無い作品名は日本語のまま新規ENページに出ていた**
（`nicephore-niepce` の `ル・グラの窓からの眺め / View from the Window at Le Gras` が実例）。

裁定：`rebuild_works()` は直さない（凍結ファイル・rollback比較の基準が動くため）。
ui-terms 辞書にも足さない（作品名は写真家ごとに無限に増える）。
**`render_en_page` 内の後処理に閉じて**、URL一致時にラベルだけを bundle 由来へ戻し、
未翻訳CJKが1件でも残ったら fail-loud にした。

**(2) 旧形式 §REF は extractor を広げない。**

| 実測 | 値 |
|---|---|
| EN で旧形式 `class="book"` | **2**（`stieglitz` / `hiroshi-sugimoto`）|
| EN で新形式 `class="ph-book"` | 182 |
| **JA で旧形式 `class="book"`** | **0** |
| JA で新形式 `class="ph-book"` | 189 |

`render_en_page` は JA ページを scaffold にするので、**新規ENページに旧形式が現れる経路は無い**。
`extract_bundle` は JA 経路と共用なので広げると影響範囲が `render_ja_page` 側まで伸びる。
この2枚が `EnRenderIncomplete: § REF が無い` で止まるのは**ガードが正しく働いている**状態なので、
テストの `EXPECTED_FAIL` 区画で固定した（黙って §REF を落としたら FAIL になる）。

### 8.4 検証結果

```
$ python3 scripts/test_render_en_roundtrip.py
ansel-adams / ed-ruscha / robertfrank / talbot /
annie-leibovitz / daisuke-yokota / nicephore-niepce / iwata-nakayama  → 8/8 PASS
stieglitz / hiroshi-sugimoto （旧形式§REF）                          → 2/2 as expected
SUMMARY: ROUNDTRIP 8/8 PASS; EXPECTED_FAIL 2/2 as expected
```

許可した正規化は3種だけで、それ以外の差分は1件でも FAIL する:
`N1 h3-id`（builder は h3 に id を必ず付ける）/ `N2 works-dedup`（同一URLの重複が畳まれる。
`annie-leibovitz` の MoMA リンクが実在の重複）/ `N3 dash`（ui-terms の ` - ` → ` — ` 正規化）。
**新しい差分クラスが出たら FAIL させ、人間が裁定してから許可リストに入れる。増やさない。**

そのほか監督側で実測したもの:

- **新規1名の実走**（リポジトリ外の JA scaffold で）：head fallback 0件、
  `og:image` + `image:width/height` + `twitter:image` あり、JSON-LD に Person / WebPage /
  BreadcrumbList、AI開示ブロックあり、`lang="en"`。**§2-4 に記録された `ed-ruscha` の head 欠陥は解消**
- **既存ENへの `--apply` は `🛑 REFUSED` で EXIT 1・SHA-256不変。`--force` を足しても拒否**
  （`--force` は `--render-en` に配線していない。環境変数の解除口も作っていない）
- **JAページ不在での `--render-en` は `EnScaffoldMissing` で EXIT 1**
- `preflight.py` は作業前後で**出力差分0**（新規 HARD / WARN 0件）。`check_content_loss.py` OK
- `en_html_sync.py verify` の10項目を描画結果に当てて7 slug 全通過
  （`iwata-nakayama` は verify 側が jp-漢字マッピングを持たないため対象外）

### 8.5 既知の残件（フェーズCのせいではない・スコープ外）

- **`ansel-adams` は JA h3=15 / EN h3=8** と本文の小見出し数が非対称。**現行ライブで既にそうで**、
  renderer はそれを忠実に再現しただけ。preflight の対称性ガードは回帰検知なので止まらない。
  このページを次に update するときに一緒に直す
- `render_en_page` はまだ**どこからも呼ばれていない**。importer の新規作成フローを
  JSON+builder から切り替えるのは **フェーズE-2**。C は手段を用意しただけで、経路は変えていない。
  したがって `CLAUDE.md` / `AGENTS.md` の正本マトリクス（新規＝JSON経由）は**まだ正しい**

### 8.6 次（フェーズA）への申し送り

- A は読み取りのみ・3時間。バッチと並行してよい。**台帳は散文でなく機械可読ファイル1本**、
  かつ**再生成できるスクリプト**にする（§2b）
- A が分類する対象に、C で判明した次の2つを足すこと:
  **旧形式 §REF の2枚**（`stieglitz` / `hiroshi-sugimoto`）と、
  **`view_works_links_html` を持つ308件が死蔵である**という事実（F の降格対象の内訳に効く）

---

## 9. フェーズA 完了記録（2026-09-14・Opus監督 / Codex実装）

### 9.1 成果物

| ファイル | 役割 |
|---|---|
| `data/en-migration-ledger.json`（約 617KB・418 records） | **機械可読な移行台帳。B・D・E・F はこれを読む** |
| `scripts/build_en_migration_ledger.py`（483行） | 台帳の生成器。`--apply` / `--check` / 無指定=dry-run |

**`--check` を `preflight.py` に配線していない。** 台帳は全ファイルの sha256 を持つので、
ページを1枚直すたびに落ちる。これは push ゲートではなく、
**D・E・F のセッションが「台帳が今のリポジトリと一致しているか」を確かめるための道具**。
とくに **D の完了条件「昇格コミットで `en/photographers/*.html` の内容差分が0」は、
台帳の sha256 集合で機械的に証明できる。**

### 9.2 分類（未分類0・例外0）

| class | 件数 |
|---|---|
| `real_page` | **402** |
| `shim`（meta-refresh） | **16** |
| `unpublished_data`（JSONだけでファイルが無い） | **0** |
| `exception` | **0** |
| `unclassified` | **0** |

`exception` か `unclassified` が1件でも出たらスクリプトは EXIT 2 で止まり、人間に判断を求める。

### 9.3 台帳が固定した事実

| 項目 | 値 |
|---|---|
| EN正本JSON `pages` | 415 |
| **うち shim 向け entry** | **16** → 実ページ向けは **399** |
| ファイルを持たない entry | **0** |
| stage4 entries | **1**（`ihei-kimura.html`）|
| **`stage4_only_canon`** | `ihei-kimura` — **base に entry が無く、JSON側の正本が stage4 単独** |
| `no_json_entry`（実ページだが base にも stage4 にも無い） | `sibylle-bergemann` / `toyoko-tokiwa` |
| `hand_maintained_history` | 5（annie-leibovitz / lee-miller / shoji-ueda / stieglitz / toyoko-tokiwa）|
| **`dead_view_works_links`** | **308**（§8.3 の死蔵データ。**F の降格対象の内訳はこれが主**）|
| `notable_works_html`（builder が実際に読む唯一の作品フィールド） | 89 |
| `old_ref_format` | `stieglitz` / `hiroshi-sugimoto`（§8.3 の裁定どおり対応しない）|
| `jp_shim_missing` | `ihei-kimura`（`en/photographers/jp-木村伊兵衛.html` が無い。17ペア中ここだけ）|
| `ja_missing` / `extract_failed` | **0 / 0** |

### 9.4 台帳で新しく可視化された日英非対称（**A は棚卸しのみ。直していない**）

| flag | 件数 | ページ |
|---|---|---|
| `section_count_asymmetry` | **7** | `annan` / `frederick-h-evans` / `marville` / `riis` / `tomishige-rihei` / `tomishige-tokuji` / `yokoyama-matsusaburo` |
| `cite_set_asymmetry` | **17** | `edward-s-curtis` / `erich-salomon` / `frantisek-drtikol` / `frederick-sommer` / `gerda-taro` / `hannah-hoch` / `herbert-ponting` / `j-dudley-johnston` / `james-van-der-zee` / `john-heartfield` / `josef-sudek` / `karl-blossfeldt` / `richard-polak` / `sakiko-nomura` / `tadahiko-hayashi` / `weegee` / `willy-ronis` |
| `h3_count_asymmetry` | **21** | `ansel-adams` ほか（§8.5 の既知件を含む）|

**これは既存のバックログであって、移行が作った退行ではない。**
§2a-DONE のとおり preflight の3ガードは回帰検知方式なので、これらでは push は止まらない。
**専用セッションは組まず、該当ページを次に update するときに一緒に直す。**

### 9.5 ついでに判明したこと

**`data/photographers-en-classification.json` は陳腐化している。**
`missing_en` に12件挙がっているが全件 EN ページが実在し、`jp_pages_without_en` の
`jp-木村伊兵衛.html` も `ihei-kimura.html` として実在する。
**今回の台帳がこのファイルの役割を置き換える。**
ただし `jp_slug_mapping`（17ペア）は `build_photographers_en.build_jp_slug_map()` が現役で読むので、
**このファイル自体はフェーズFまで消さない。**

### 9.6 検証

- `--apply` EXIT 0 / `--check` EXIT 0 / 2回生成で sha256 一致（決定論）
- 台帳を1バイト改変すると `--check` が EXIT 1 でドリフトを検知
- 無指定（dry-run）は書かない
- `preflight.py` は作業前後で**出力差分0**
- `git status` の差分は新規2ファイルのみ。公開HTML・EN正本JSON・既存スクリプトの変更 **0**

### 9.7 次（フェーズD）への申し送り

- **D からはバッチと並行できない**（§6）。素材が来ていない今が窓
- D の完了条件「昇格コミットで EN HTML の内容差分0」は、
  **`build_en_migration_ledger.py --check` が EXIT 0 のままであることで証明する**
- D の実作業は3つ：
  1. `HAND_MAINTAINED_EN`（5件）の仕組みを廃止し、全実ページを同じ HTML 正本として扱う
     （履歴は台帳の `hand_maintained_history` flag に移管済み＝**コードから消してよい**）
  2. `CLAUDE.md` / `AGENTS.md` の正本マトリクスから「新規のみ JSON 経由」の行を落とす
     — **ただしこれは E-2 で経路を切り替えてから。D では触らない**
  3. `stage4_only_canon` の `ihei-kimura` と `no_json_entry` の2件の扱いを決める
     （§5 の裁定＝ファイル実在を公開正本の基準にする、で既に答えは出ている）

---

## 10. フェーズD 完了記録（2026-09-14・Opus監督 / Codex実装）

### 10.1 §2b の文字どおりの実行はしていない — 監督の裁定

§2b は D の実体を「コード経路の削除と文書更新」とし、
「`HAND_MAINTAINED_EN` の5件も通常実ページへ統合する」と書いている。
**この「統合」を、凍結ファイルのガードを外すことと解釈しなかった。**

`scripts/build_photographers_en.py:1932` の `HAND_MAINTAINED_EN` ガードは、
当時 `ALLOW_EN_REBUILD=1`（移行監査・緊急rollback比較）の escape hatch 内でだけ効く最後の砦だった。
そのためフェーズDでは外さず、§4 の分類 **c（凍結）**を維持した。

> **昇格は宣言であって、ガードの取り外しではない。**
> D で削除するのは「JSON を既存ページの正本として扱うコード経路」だけで、安全網は残す。

したがって **フェーズDでは `build_photographers_en.py` を1行も変更していない。**
**その後、`docs/post-migration-cleanup-plan.md` §9.5 の4-1決定がこの裁定を上書きし、フェーズ2で CLI・ガード・escape hatch を撤去した。rollback は git で行う。**

### 10.2 実際にやったこと

| 変更 | 内容 |
|---|---|
| `scripts/check_en_entry.py` | `check_html_vs_json()` の `HAND_MAINTAINED_EN` 分岐を削除して一本化。フェーズD時点では定数を再生成ガード用に残した。**総ざらいフェーズ2以降は、台帳が読む履歴レジストリとしてのみ維持** |
| `scripts/import_chatgpt_photographer.py` | **`HAND_MAINTAINED_EN` の重複ハードコード定義を削除**し、`check_en_entry` からの import に一本化（二重定義のドリフト源を解消。挙動は同一） |
| `scripts/build_en_migration_ledger.py` / 台帳 | `_meta.canon` を追加して昇格を宣言。**`records` は1つも変えない** |
| `docs/generators-and-guards.md` | 「手書き維持ページは拒否」の2箇所に、全ENがHTML正本になったこと＋残置ガードである旨を**追記**（既存記述は消さない） |
| `CLAUDE.md` / `AGENTS.md` | **変更しない。** 「新規ENページのみ JSON + builder」は **E-2 で経路を切り替えるまで事実として正しい** |

**★履歴の移管を取りこぼしかけた点（監督が差し戻して修正）。**
`check_en_entry.py` から消したコメントには**ページ別の理由**（`shoji-ueda` の脚注番号不整合 /
`lee-miller` の手書き§REL / `stieglitz` の旧形式§REF 等）が入っていたのに、
台帳側は `hand_maintained_history` という**真偽フラグしか持っていなかった**。
§5 の「履歴は台帳にだけ残す」を満たさないので、
`_meta.canon.hand_maintained_history_notes` に5件のページ別理由を全文で移した。

### 10.3 昇格の証明（完了条件「EN HTML の内容差分0」）

| 検査 | 結果 |
|---|---|
| **公開HTML の sha256 集合**（EN 418 + JA 402 = **820枚**） | **作業前後で完全一致** |
| 台帳の `records`（418件） | **完全一致**（`_meta` の差分は `canon` 追加と `generated_at_commit` の HEAD 追従のみ） |
| `check_en_entry.py` の検査結論（20 slug・`HAND_MAINTAINED_EN` 5件を全部含む） | 終了コード・重大行集合・WARN件数が**全件一致**。変わったのは WARN の文言だけ（＝D の目的そのもの） |
| `preflight.py` | 作業前後で**出力差分0** |
| `check_content_loss.py` | OK |
| `test_render_en_roundtrip.py` | `ROUNDTRIP 8/8 PASS; EXPECTED_FAIL 2/2`（フェーズC の退行なし） |
| `build_en_migration_ledger.py --check` | EXIT 0 |
| `git diff --stat` に `build_photographers_en.py` | **0回**（凍結を維持） |

### 10.4 D で見つかった E-1 の対象（**直していない**）

**`toyoko-tokiwa` は台帳で `real_page` なのに `check_en_entry.py` が slug を解決できず EXIT 2 になる。**
原因は同スクリプトが **slug 解決を EN正本JSON 経由でやっている**こと
（`en_content.resolve_slug(args.slug, pages)`）。台帳で `no_json_entry` が立っている
`toyoko-tokiwa` / `sibylle-bergemann` の2件が引っかかる。

**これは E-1 の本体そのもの**（読み取り経路を JSON から HTML へ向け直す）。
D では直さず、該当箇所に1行コメントを置いて台帳と本記録に残した。
**台帳が作られた初日に、台帳が仕事をした最初の例。**

### 10.5 次（フェーズE-1）への申し送り

- **E-1 の対象（読み取り専用6本）**：`preflight.py` / `check_en_entry.py` /
  `check_new_photographer.py` / `en_entry.py` / `peek.py` / `en_content.py`
- **最初に直すのは `en_content.resolve_slug()`。** slug 解決を
  「EN正本JSON の pages キー」から「`en/photographers/*.html` の実在」へ移す。
  §5 の裁定「**ファイル実在を公開正本の基準にする**」の実装であり、
  §10.4 の `toyoko-tokiwa` / `sibylle-bergemann` がこれで解消する
- `check_new_photographer.check_en()` の `en_json_absent`（SOFT）も同じ理由で消える
  （JSON に無い＝異常、ではなくなった）
- **E-1 は読むだけなので公開HTMLは不可触。** D と同じく
  **820枚の sha256 集合が不変であること**を完了条件に入れる
- `preflight.py` の `check_en_content_loss` 系（`EN_CONTENT_JSON` を見る 528〜629行）は
  **JSON の内容消失ガード**。E-1 で HTML 側へ向け直すが、**JSON 側のガードを先に外さない**
  （F で JSON を降格するまで併走させる）

---

## 11. フェーズE-1 完了記録（2026-09-14・Opus監督 / Codex実装）

### 11.1 E-1 が直した本丸

**`scripts/check_en_entry.py` は D のあとも検査を EN 正本 JSON に対して行っていた**
（`run_one()` の `entry = pages[slug]`）。JSON は既存ページの正本ではなくなったのに、
**この検査は陳腐化したデータを見ていて、ライブの EN HTML を見ていなかった。**

| `check_en_entry.py --all` | before | after |
|---|---:|---:|
| 走査した slug 数 | 415（**JSON の pages キー**）| **418**（**EN HTML ファイル**）|
| WARN 総数 | 558 | **139** |
| 「既存ENはHTML正本」スキップ WARN | 415 | **0**（空関数を削除）|
| 出典系 WARN（孤立） | 75 | 73 |
| 禁止ドメイン WARN | 66 | 63 |
| cite-id 欠番 WARN | 2（JSON基準）| **3**（HTML実態）|
| FAIL slug | 1（`sakiko-nomura`）| 1（同じ）|

**増えた3 slug は台帳の `no_json_entry` / `stage4_only_canon` と完全一致**
（`ihei-kimura` / `sibylle-bergemann` / `toyoko-tokiwa`）。
消えた指摘は全件が「JSON にだけ残る古いリンク・古い cite 集合」で説明できた
（例: `sherman` / `stieglitz` の Wikipedia リンクは JSON にあって公開HTMLには無い）。
**新規に出た `ihei-kimura` の cite-8 孤立は公開HTMLの実態。**

復旧後の cite 欠番3件はすべて実在する: `emerson` cite-4 / `sakiko-nomura` cite-34 /
`stieglitz` cite-10（**`stieglitz` cite-10 は preflight の既知 intentional-replacement 宣言と一致**）。

### 11.2 変更した8ファイル

| ファイル | 内容 |
|---|---|
| `scripts/en_content.py` | `load_en_page_keys()`（418件）/ `is_shim()`（16件）/ `shim_target()` / `load_en_html()` / `extract_en_summary()` を追加。**`resolve_slug()` はシグネチャも中身も変えていない**（キーしか見ないため）。JSON helper は残すが docstring に「既存ページの検査には使わない」と明記 |
| `scripts/check_en_entry.py` | 検査対象を EN HTML の `<main>` へ。shim は「転送先の実ページが存在するか」だけ検査（§5）。空関数 `check_html_vs_json()` を削除。`check_git_scope()` の expected から EN正本JSON を除去 |
| `scripts/check_new_photographer.py` | `en_json_absent`（SOFT）を削除。slug 解決を HTML 実在へ。`en_missing` の案内を `--render-en` へ更新 |
| `scripts/en_entry.py` / `scripts/peek.py` | 表示を HTML ベースへ。JSON を読まない |
| `scripts/preflight.py` | **1行だけ**。メッセージ文字列の `正本(JA HTML / photographers-en-content.json・overrides.js)` → `正本(JA HTML / EN HTML)`。**`check_en_content_loss()` は変更していない**（§10.5 どおり F まで併走） |
| `scripts/build_en_migration_ledger.py` / 台帳 | 下記 11.4 |

### 11.3 ★監督のブリーフ不備で検査が2つ消えかけた（差し戻して復旧）

ブリーフに「cite は dangling / 孤立 の2種」と書いたが、**変更前の `check_cite_supref()` は5判定あった**。
Codex はそのとおり2つで実装し、**`cite-id が重複`（FAIL）と `cite-id に欠番`（WARN）が消えていた**。
レビューで検知して差し戻し、旧実装のメッセージ文言のまま復旧した。

| # | 判定 | 段位 | E-1 後 |
|---|---|---|---|
| 1 | `cite-id が重複` | FAIL | **復旧** |
| 2 | `本文 sup-ref *N に対応する出典 cite-id が無い` | FAIL | 維持 |
| 3 | `出典 cite-N が…参照されていない（孤立）` | WARN | 維持 |
| 4 | `cite-id に欠番` | WARN | **復旧** |
| 5 | `保存 cite_ids / supref_ids が実体と不一致` | WARN | **削除して正**（JSON の保存済み配列との比較。HTML 正本では意味を持たない） |

リンク判定5件（1〜2文字アンカーFAIL / 空・`#` href WARN / utm FAIL / Amazon検索URL FAIL /
禁止ドメインWARN）は**文言も段位も変えずに全部 HTML へ移した**。
ブリーフにあった「内部リンク実在の追加」は**取り下げた** —
`preflight.py:2112` の `check_internal_dead_links()` が既にサイト全体で HARD/WARN 二段＋
既知例外リスト付きで見ており、二重化になるため。

**教訓：既存関数を別の入力へ移すときは、先に旧実装の判定を全部列挙してからブリーフを書く。**

### 11.4 台帳生成器の設計不備を直した

`_meta.generated_at_commit` が `--check` の比較対象に入っていたため、
**コミットのたびに HEAD が動いて、どのコミット直後でも必ず EXIT 1 になる**構造だった。
`generated_at_commit` を比較から除外し、差があるときは EXIT 0 のまま stderr に NOTE を出す形にした。
**`records` / `counts` / `findings` / `canon` の差は従来どおり EXIT 1。**

### 11.5 検証

- **公開HTML 820枚（EN 418 + JA 402）の sha256 集合が作業前後で完全一致**
- `preflight.py` 作業前後で**出力差分0**、EXIT 0
- `check_content_loss.py` OK / `test_render_en_roundtrip.py` 8/8・2/2
- 台帳 `--check` EXIT 0、`records` 418件不変
- EN正本JSON 3本・`build_photographers_en.py`・`CLAUDE.md`・`AGENTS.md` は差分に**現れない**
- **D で見つかった2件が解消**：`toyoko-tokiwa` / `sibylle-bergemann` とも EXIT 0 で検査が走る
- shim は本文検査の対象外になり、転送先の実在だけを見る（16件すべて実在）
- `check_new_photographer.py` は `en_json_absent` を出さない

### 11.6 次（フェーズE-2）への申し送り

- **E-2 の対象は書き込む2本**：`import_chatgpt_photographer.py` / `add_photographer.py`
- **中身は「新規EN作成を JSON+builder から `render_en_page` へ切り替える」**。
  フェーズC で `--render-en` は既に動いていて、既存ファイルへの書込みは常に REFUSED。
  **やるのは呼び出し側の付け替えであって、renderer の新規開発ではない**
- 具体的には importer の旧EN JSONマージ経路を通常フローから外し、旧stage4注入後に
  builderを起動していた検証も現行rendererへ付け替える
- **E-2 で初めて `CLAUDE.md` / `AGENTS.md` の正本マトリクスを更新する。**
  「EN写真家ページ（新規作成のみ）＝ `data/archive/photographers-en-content.json`」の行を落とし、
  JA と同じ「HTML自身が正本」1行にまとめる。**E-2 より前に書き換えないこと**
- 完了条件は §2b のとおり「**通常フローに JSON 編集と builder 実行が一度も現れない**」。
  D・E-1 と同じく **820枚の sha256 不変**も入れる

---

## 12. フェーズE-2 完了記録（2026-09-15・Opus監督 / Codex実装）

### 12.1 これで「新規作成もHTML正本」になった

**旧：** importer は EN 素材から**断片 JSON を `outputs/import-preview/` に吐くだけ**で、
人間がそれを現在の `data/archive/photographers-en-content.json` へ手で移植し、
`build_photographers_en.py --slug` を回して初めて EN ページが出来ていた。

**新：** 通常モード1本で JA→EN の順に HTML を直接生成する。

```bash
python3 scripts/import_chatgpt_photographer.py --slug <slug> --ja JA.html --en EN.html --apply
```

§2b の完了条件「**通常フローに JSON 編集と builder 実行が一度も現れない**」を、
通常モードの全出力に次の文字列が**各0回**であることで確認した:
`photographers-en-content.json` / `build_photographers_en.py` / `outputs/import-preview`。

### 12.2 着手前に列挙した旧経路9箇所と、その処遇

E-1 までブリーフ側の不備が3回続いたので、**先に `grep` で旧経路を全部洗い出してから**ブリーフを書いた。

| # | 場所 | 処遇 |
|---|---|---|
| 1 | 通常モードの `if args.en:` ブロック | **`render_en_page` で EN HTML を直接生成**（本丸） |
| 2-3 | `print_runbook()` の EN 分岐と末尾の注意書き | JSON 移植・builder の案内を削除 |
| 4 | 旧EN JSON field-merge CLI | コードは非推奨として残置。後続フェーズ1で撤去 |
| 5 | 旧stage4 thesis注入CLIとbuilder起動検証 | 同上 |
| 6 | `add_photographer.py` のチェックリスト3行 | `--render-en` の案内へ |
| 7-8 | `CLAUDE.md` / `AGENTS.md` | **EN写真家の2行を1行に統合**（下記 12.3） |
| 9 | `docs/generators-and-guards.md` の EN フロー節 | 新経路を正として更新 |

### 12.3 正本マトリクスの統合

```
変更前:
| EN写真家 …（**既存**）      | HTML自身 | なし（手編集・永続） |
| EN写真家 …（**新規作成のみ**）| data/archive/photographers-en-content.json | build_photographers_en.py --slug |

変更後（1行）:
| EN写真家 `en/photographers/*.html` | **HTML自身** | 新規のみ importer 通常モード | 既存への上書きは常に拒否 |
```

「絶対禁止」3番の「新規ENページの作成だけ 当面 JSON + builder のまま」も削除した。
**これで JA と EN の正本ルールが同じ1行になった＝§2-1 の「正本が2系統のまま動いている」が解消。**

### 12.4 実装で効いた2つの注意点

- **dry-run の落とし穴**：EN scaffold は JA ページなので、新規 slug の dry-run では
  JA がまだ書かれておらず `EnScaffoldMissing` で落ちる。
  → dry-run で JA 未作成のときは EN 描画を試みず
  `(dry-run) EN は JA ページ作成後に生成される（--apply で JA→EN の順に書く）` と表示して EXIT 0
- **`--force` を EN 側に波及させない**：`--force` は JA ページ用。EN の既存ページ拒否は
  `--force` を付けても効いたまま。**しかも拒否は書き込み前の事前チェック**で、
  JA も含めて1バイトも書かれずに EXIT 1 する（実測で確認）

### 12.5 検証

| 検査 | 結果 |
|---|---|
| 公開HTML 820枚の sha256 | **完全一致**（新規ファイルも作っていない。EN 418 / JA 402 のまま）|
| `preflight.py` | 作業前後で**出力差分0**、EXIT 0 |
| `check_content_loss.py` | OK |
| `test_render_en_roundtrip.py` | 8/8 PASS・EXPECTED_FAIL 2/2 |
| 台帳 `--check` | EXIT 0 |
| `check_en_entry.py --all` | **E-1 の結果とバイト単位で完全一致**（418 slug / WARN 139 / FAIL 1）|
| EN正本JSON 3本・凍結 builder・`preflight.py` | 差分に**現れない** |

**新規1名の実走（リポジトリ外の fixture）**：JA→EN が1コマンドで両方出来ることを確認。
生成EN は `lang="en"` / `og:image` / JSON-LD Person / AI開示ブロックあり、
`sec=4 / cite=56 / dangling=0 / works-cjk=0 / ga=2`、head fallback 0件。

**既存ページへの `--apply --force`**：`🛑 REFUSED` で EXIT 1、EN・JA とも SHA-256 不変。

### 12.6 次（フェーズF・最後）への申し送り

§2b・§5 の裁定どおり **JSON は削除せず読み取り専用アーカイブへ移す**。1時間の想定。

- **移す対象**：`data/archive/photographers-en-content.json`（415 entries・12.4MB）/
  `data/archive/photographers-en-stage4.json`（1 entry）/ `data/photographers-en-classification.json`
- **ただし `-classification.json` は `jp_slug_mapping`（17ペア）を
  `build_photographers_en.build_jp_slug_map()` が現役で読む**（§9.5）。
  凍結 builder は触らない方針なので、**このファイルだけは動かさないか、
  builder が読める場所に残すかを先に決めること**
- 完了条件は §2b の「**通常スクリプトから base/stage4 への読み書き参照が0**」
- **撤去できるもの**（E-2 で非推奨バナーを付けた分）：
  importer の旧EN JSON field-merge・stage4注入・builder起動検証と、
  `check_en_entry.HAND_MAINTAINED_EN`（§10.2 の残置ガード）。
  この申し送りでは builder の `HAND_MAINTAINED_EN` 参照を保全したが、
  **総ざらい§9.5の4-1決定によりフェーズ2で CLI とともに撤去済み**
- **F でも公開HTML 820枚の sha256 不変を完了条件に入れる**

---

## 13. フェーズF 完了記録 ＋ 移行の総括（2026-09-15・Opus監督 / Codex実装）

### 13.1 ★この移行は完了した。新規セッションはここだけ読めばよい

| 知りたいこと | 答え |
|---|---|
| EN写真家ページの正本は？ | **`en/photographers/*.html` そのもの。** 既存修正も新規作成も同じ |
| 既存ページを直すには？ | **EN HTML を直接編集して終わり。** JA と同じ |
| 新規ページを作るには？ | `python3 scripts/import_chatgpt_photographer.py --slug <slug> --ja JA.html --en EN.html --apply`（JA→EN の順に両方できる） |
| `data/archive/photographers-en-content.json` は？ | **読み取り専用アーカイブ。編集すると preflight が HARD で止める** |
| `build_photographers_en.py` は？ | **EN描画エンジンの module-only ファイル。** importer が関数を利用する。直接実行は非0終了し、JSON再生成経路はない。rollback は git |

### 13.2 ★フェーズ3で JSON アーカイブを物理移動した

フェーズF当時は残存読者があったため物理移動を見送ったが、総ざらいフェーズ2で
builder の CLI 読み込みを撤去し、フェーズ3で残る正当な読者を更新して次の2本を移動した。

- `data/archive/photographers-en-content.json`
- `data/archive/photographers-en-stage4.json`

`data/photographers-en-classification.json` はエンジン部の `jp_slug_mapping`（17ペア）が現役で読むため動かしていない。
凍結ガードは rename 直後の `origin/main` に新パスが無い間だけ旧パスの baseline へフォールバックし、
フェーズ3が main に載れば新パスを直接比較する。

**降格と凍結は次の3点で維持している。**

1. **公開HTMLの通常生成・更新経路からの読み書き参照を0にした**
2. **`preflight.check_en_json_frozen()` を新設** —
   base / stage4 が baseline から**1バイトでも変化したら HARD**。
   解除は `ALLOW_EN_JSON_ARCHIVE_WRITE=1` のみ。実データで発火と解除を確認済み
3. 文書・台帳で「読み取り専用アーカイブ」と宣言

**`check_en_content_loss()`（JSON の内容"消失"だけを見ていた）はこれに置き換えた。
カバレッジは縮小ではなく拡大**（消失だけでなく、あらゆる変更を止める）。

### 13.3 残存読者の全件（§2b の完了条件）

新パスを読む経路は次の3分類だけで、通常の公開HTML生成経路に読者は無い。

| 分類 | スクリプト |
|---|---|
| (a) コーパス監査（正当な読者） | `import_chatgpt_photographer.py --audit-corpus` |
| (b) 台帳生成器（正当な読者） | `build_en_migration_ledger.py` |
| (c) 凍結ガード | `preflight.py` |

`en_content.py` の `load_data()` / `load_pages()` / `JSON_PATH` は**呼び出し元0を実測してから削除**した。

### 13.4 ★F の本丸で見つかった構造的な検査漏れ

`sync_en_rel_annotations.py` が**最後に残った通常スクリプトの JSON 読者**だった。
これを EN HTML ベースへ付け替えたところ、**旧 JSON 監査が丸ごと見落としていたページ群が出た。**

| audit | pages | missing(need) | review |
|---|---:|---:|---:|
| 旧（JSONベース・現行コード実測） | 81 | 10 | 96 |
| 新（HTMLベース・最終） | **61** | **89** | 46 |

消えた22件の内訳:
- **16件が `jp-漢字` shim**。旧監査は§RELを持たない shim を検査して
  無意味な `EN=0 (count mismatch)` を出していた（§5 どおり shim は対象外にした）
- **6件が実ページ**（`sherman` / `stieglitz` / `kelli-connell` / `natalie-czech` /
  `shannon-ebner` / `kajima-seibei`）。**JSON の `site_directory_html` が古くリンク数が少なかった**だけで、
  EN HTML は JA と一致していた（実測: sherman JA=5 / JSON=4 / **HTML=5** 等）

**★missing が 10 → 89 に増えた理由（これが発見）:**
旧監査は **`jp-漢字`ペアのローマ字実ページ15枚**（`iwata-nakayama` / `ihei-kimura` 等）を
**一度も検査していなかった**。JA ファイル名が `jp-中山岩太.html` で slug と一致しないため、
`<slug>.html` 決め打ちの解決が失敗していたのが原因。
実測すると `iwata-nakayama` の EN §REL は**一言解説が1つも付いていない**のに JA には全部ある。

> **監督が `page_alignment()` に `ja_file_for()` を追加して修正した。**
> レジストリ（`classification.json`）ではなく **EN HTML 自身の `hreflang="ja"` から JA 実体を引く**
> （EN 402枚すべてが持っている）。HTML 正本の方針とも一致する。

**memory の `project_en_rel_annotations_backfill` にある「need=0」は誤りだったことになる。**
構造的に見えていなかっただけで、実際には 89件が欠けていた。

**この89件は直していない。** F は配管のフェーズで、公開HTMLは1バイトも変えない。
台帳の `_meta.findings.en_rel_blurb_missing`（count 89 / 22ページ）に経緯ごと記録した。
**該当ページを次に update するとき一緒に直す。**

### 13.5 検証

| 検査 | 結果 |
|---|---|
| 公開HTML 820枚の sha256 | **完全一致**（枚数も 418 / 402）|
| **EN正本JSON 3本の sha256** | **完全一致**（移動も内容変更もしていない）|
| `preflight.py` | 作業前後で**出力差分0**、EXIT 0 |
| 凍結ガード | JSON を1バイト変えると **HARD FAIL**、`ALLOW_EN_JSON_ARCHIVE_WRITE=1` で解除、`git checkout` で sha256 完全復元 |
| `check_content_loss.py` / `test_render_en_roundtrip.py` | OK / 8:8・2:2 |
| `check_en_entry.py --all` | **E-2 とバイト単位で完全一致** |
| 台帳 `--check` / `records` | EXIT 0 / 418件完全一致 |
| 非推奨バナー6本 | 全6本で1回ずつ出力を確認 |

### 13.6 移行の総括 — §2-1 の4項目はどうなったか

§2 は「C が実際に消すのは次の4つ」と書いていた。全部消えた。

| # | 着手前の状態 | いま |
|---|---|---|
| 1 | **正本が2系統**（既存＝HTML / 新規＝JSON）で動いている | **1系統。** マトリクスは1行（E-2） |
| 2 | 写真家を1名足すたび JSON entry が増え、死蔵データになる | **増えない。** 新規も HTML を直接作る（C・E-2） |
| 3 | 17本中14本がまだ JSON を読み書きし、規律で守られている | **機械で守られている。** 通常経路の参照0＋凍結ガード（E-1・E-2・F） |
| 4 | 新規作成の経路が完成品を出さない（`ed-ruscha` の head 欠陥） | **出す。** og:image・JSON-LD Person・AI開示つき、head fallback 0件（C） |

### 13.7 移行が副産物として可視化した既存バックログ（**どれも移行が作った退行ではない**）

**専用セッションは組まない。該当ページを次に update するときに一緒に直す。**

| 件 | 数 | 出どころ |
|---|---:|---|
| EN §REL の一言解説が無いリンク | **89**（22ページ）| §13.4。うち大半が jp-漢字ローマ字実ページ15枚 |
| JA/EN の cite 集合非対称 | 17ページ | §9.4 |
| JA/EN の h3 数非対称 | 21ページ | §9.4（`ansel-adams` 含む）|
| JA/EN の節数非対称 | 7ページ | §9.4 |
| cite-id の欠番 | 3 | §11.3（emerson / sakiko-nomura / stieglitz）|
| 旧形式 §REF | 2 | §8.3（stieglitz / hiroshi-sugimoto。**対応しない裁定**）|
| `jp-漢字` shim の欠落 | 1 | §9.3（`ihei-kimura`。JA hreflang は正しいので実害なし）|

### 13.8 escape hatch の現状（総ざらいフェーズ2更新）

| 仕組み | 解除キー | 理由 |
|---|---|---|
| 既存EN再生成の拒否 | `ALLOW_EN_REBUILD=1` | **フェーズ2で CLI とともに撤去済み。** rollback は git |
| 手書き維持5件の再生成拒否 | `ALLOW_HAND_MAINTAINED_REBUILD=1` | **フェーズ2で撤去済み。** `check_en_entry.HAND_MAINTAINED_EN` も 2026-09-15 の §12.2 で撤去し、`build_en_migration_ledger.HAND_MAINTAINED_HISTORY` へ履歴記録として移設 |
| EN正本JSON の凍結 | `ALLOW_EN_JSON_ARCHIVE_WRITE=1` | 読み取り専用アーカイブの変更を preflight が HARD で防ぐ |

### 13.9 この移行で効いた作業規律（次の engine 作業へ）

- **既存関数を別の入力へ移すときは、先に旧実装の判定を全部列挙してからブリーフを書く。**
  E-1 でこれを怠り、`cite-id が重複`（FAIL）と `cite-id に欠番`（WARN）を消しかけた（§11.3）
- **旧経路の呼び出し箇所を着手前に grep で全部出す。** E-2 でそうしたら設計不備が0件になった（§12.2）
- **件数ではなく集合で比較する。** 「WARN が減った」は改善にも退行にも見える。
  消えた項目を全件分類して初めて判断できる（§11.1・§13.4）
- **ガードは外さず置き換える。** `check_en_content_loss` → `check_en_json_frozen` はカバレッジ拡大（§13.2）
- **凍結ファイルは触らない。** そのために JSON を動かさない判断をした（§13.2）

---

## 13.10 ★次に写真家を update / 追加するときの検証（**初回は必ずこれを回す**）

移行後の経路は **fixture でしか通していない**（`ed-ruscha` をコピーして slug 置換したもの）。
**実素材での初回だけ**、下の項目を実測して `docs/importer-run-log.md` に残す。
2回目以降は通常どおりでよい。

### 共通（着手前・1回）

```bash
find en/photographers -name '*.html' | sort | xargs shasum -a 256 > /tmp/en-before.sha256
find photographers   -name '*.html' | sort | xargs shasum -a 256 > /tmp/ja-before.sha256
python3 scripts/preflight.py > /tmp/preflight-before.txt 2>&1
```

### A. 既存ページを update する場合

| # | 見るもの | 期待 |
|---|---|---|
| 1 | `en_html_sync.py verify <slug>` | **10項目すべて OK** |
| 2 | JSON を1度も開いていないこと | `git diff --name-only` に `data/photographers-en-*.json` が出ない |
| 3 | JA §REF と EN §REF の href 集合 | 一致（`-backup.html` と差分を取る。既知の落とし穴） |
| 4 | §REL の EN 一言 | 台帳 `en_rel_blurb_missing` に該当 slug があれば**ついでに埋める** |
| 5 | `check_en_entry.py <slug>` / `check_new_photographer.py --slug <slug>` | EXIT 0 |
| 6 | `preflight.py` | 新しい HARD / WARN が増えていない |

### B. 新規1名を追加する場合（**未検証の経路。ここが本番初回**）

| # | 見るもの | 期待 |
|---|---|---|
| 1 | **素材に `§ 01` マーカーがあるか**（着手前 grep） | 無いと本文が65〜81%落ちる（既知の罠）|
| 2 | まず `--apply` **なし**で実行 | EXIT 0。JA 未作成なら `(dry-run) EN は JA ページ作成後に生成される` が出る |
| 3 | `--apply` 実行後の `[render-en]` 行 | `dangling=0` / `works-cjk=0` / `ga=2` / `sec` が素材の節数と一致 |
| 4 | warnings に `head fallback fired` | **0件**（出たら head が不完全） |
| 5 | 生成EN の head | `og:image` / `og:image:width` / `twitter:image` / JSON-LD に `Person` / `<!-- AI-DISCLOSURE -->` が各1 |
| 6 | 作品ラベル | 日本語が残っていないこと（残れば fail-loud で止まるはず） |
| 7 | `en_html_sync.py verify <slug>` | 10項目すべて OK |
| 8 | `check_new_photographer.py --slug <slug>` | `en_missing` が出ない |
| 9 | JA/EN の節数・cite集合 | 一致（preflight の日英対称性ガードが見るが、目視でも確認） |

**入口の選び方**（間違えると JA を書き直す）:
- JA も EN もこれから → `--slug X --ja JA.html --en EN.html --apply`
- JA は既にある → `--slug X --render-en EN.html --apply`

### 終わったら

```bash
find en/photographers -name '*.html' | sort | xargs shasum -a 256 | diff /tmp/en-before.sha256 -
python3 scripts/preflight.py | diff /tmp/preflight-before.txt -
```
**意図した slug 以外の差分が出たら止めて調べる。**

### 実測を残す先
`docs/importer-run-log.md` に「**移行後の実素材 初回**」と明記して1節。
**ここで問題が出なければ、この §13.10 の初回扱いは終了**として次回から通常運用にしてよい。

---

## 14. この移行の対象外だったサーフェス（2026-09-15 時点の正本）

**この移行（写真家ページ）の対象外だったサーフェスは4つあった。
そのうち EN 年代・運動は、続く総ざらい フェーズ6 で同じ昇格を通した（2026-09-15）。**

| サーフェス | 枚数 | 正本 | 生成コマンド | 既存ENへの上書き拒否ガード |
|---|---:|---|---|---|
| EN アーカイブ `en/archive.html` | 1 | **JA `archive.html`** | `build_archive_en.py` | **無し** |
| EN 年代 `en/eras/*.html` | 11 | **HTML 自身**（フェーズ6で昇格） | 新規のみ `build_taxonomy_en.py --era <YYYY>` | **有り**（`🛑 REFUSED`・解除は `ALLOW_TAXONOMY_REBUILD=1`）|
| EN 運動 `en/movements/*.html` | 35 | **HTML 自身**（フェーズ6で昇格） | 新規のみ `build_taxonomy_en.py --slug <movement>` | **有り**（同上）|
| 国別 JA/EN `countries/` `en/countries/` | 62 / 62 | **`data/country-pages.json`** | `generate_country_pages*.py` | **無し** |

**`CLAUDE.md` 絶対禁止4番が今も有効なのは、上の表で「無し」の2つ**（EN アーカイブ・国別）：
事実修正を EN 出力HTMLだけに入れてはいけない（再生成で消える）。
**EN 年代・運動はこの項の対象外になった**＝EN HTML を直接編集するのが正規手順。

**国別を昇格しなかった理由**：正本 `data/country-pages.json` は散文の置き場ではなく
**本物のデータ正本**（国の登録・掲載写真家の解決）で、二重正本の問題がそもそも無い。

**EN 年代・運動を昇格した理由**：`data/taxonomy-en-content.json` が 35運動＋11年代の
EN 本文・thesis・overview・SEO メタを全部持っており、**写真家ページと同じ「二重正本」構造が
ここにあった**。昇格でこの JSON は読み取り専用アーカイブ（`data/archive/`）へ降格した。

**昇格の代償（覚えておく）**：写真家を追加しても `build_taxonomy_en.py` が
EN 年代・運動ページへカードを足さなくなった。**EN 年代ページは必須サーフェス**で、
`preflight.check_taxonomy_presence()` が HARD で止めるので、カードは手で足す
（`add_photographer.py` がその手順を表示する）。

> **★続きの計画は `docs/post-migration-cleanup-plan.md` にある**（2026-09-15 作成）。
> 再生成ドリフトの実測（**運動は 24/35 で退行を含む**）と、未決の論点4つを置いてある。
