# EN写真家ページ 正本HTML化 — 移行計画（新規セッション用の引き継ぎ）

**いつ読むか:** `en/photographers/*.html` の正本を `data/photographers-en-content.json` から
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
| `reconcile_en_bodies.py --report` の drift | **1 / 414**（＝essay本文だけは同期している。ずれているのは本文の外側） |
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

## 2a-DONE. 最小版は 2026-09-13 に実装済み（現況）

**§2a の4項目はすべて入っている。以降の記述は背景として読む。**

| 項目 | 実装 |
|---|---|
| 1. `check_en_direct_edit()` 削除 | 削除済み。**あわせて `check_en_changed_slug_closure()` も削除**（EN HTML に cite を直接足すと JSON と集合が食い違い HARD FAIL になり、最小版が成立しないため）。`scripts/check_en_entry.py` の `check_html_vs_json()` も既存ページでは検査しない（同じ理由。通常フローの検査が毎回 FAIL するため） |
| 2. builder が既存ページを拒否 | `build_photographers_en.py` は `out_path` が実在すると `🛑 REFUSED` でスキップ。`--force` でも `--dry-run` でも解除されない。解除は `ALLOW_EN_REBUILD=1` のみ |
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
| `harvest_photographers_en.py` | 移行時の監査スナップショット作成のみ。通常利用禁止 | c |
| `reconcile_en_bodies.py` | **★(b)ではなく(c)**（監督修正）。フェーズA/Dで本文同期を証明する唯一の計測器。移行完了後に終了 | c |
| `fix_1839_en_thesis_related.py` | 過去の一回限り処理として終了 | b |
| `fix_1870_en_thesis_related.py` | 同上 | b |
| `fix_1890_en_thesis_related.py` | 同上 | b |
| `fix_eugenesmith_en.py` | 同上 | b |

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
