# 移行後の総ざらい — 設計から始める引き継ぎ（2026-09-15 作成）

**いつ読むか:** EN写真家ページの正本HTML化（`docs/en-html-canon-migration.md`）が完了したあと、
残った宿題・残骸・**写真家ページ以外のサーフェスの正本化**をまとめて片付けるとき。

**★2026-09-15 更新：設計フェーズは終わった。§4 の4論点は決着している。**
**新規セッションは §9「設計フェーズの結論」を最初に読む。§9 は §2〜§5 に優先する。**
特に **§9.1（§2b の3主張のうち2つが実測で誤りと判明）** と
**§9.2（`data/taxonomy-en-content.json` が EN 散文の正本＝§3 の前提が誤り）** を読み飛ばさない。
実装は **§9.6 のフェーズ計画**の順に進める（順序に意味がある）。

---

## 0. 前提 — EN写真家ページの移行は完了している

2026-09-15 に C→A→D→E-1→E-2→F の全フェーズ完了・push 済み。
**総括は `docs/en-html-canon-migration.md` §13。先にそれを読む。**
全期間を通して公開HTML 820枚（EN 418 / JA 402）の sha256 は1バイトも変わっていない。

- EN写真家ページの正本＝`en/photographers/*.html` そのもの（既存修正も新規作成も）
- EN正本JSON＝読み取り専用アーカイブ。`preflight.check_en_json_frozen()` が変更を HARD で止める
- 新規作成＝`import_chatgpt_photographer.py`（`--ja --en` / JA既存なら `--render-en`）

---

## 1. ★このセッションの対象は3クラス。**打ち手が違うので混ぜない**

| クラス | 中身 | 性質 |
|---|---|---|
| **1. コンテンツのバックログ** | 移行が可視化した原稿の穴 | 技術負債ではない。**原稿作業** |
| **2. 移行の残骸** | 非推奨スクリプト8本 / `HAND_MAINTAINED_EN` / `overrides.js` / 動かせなかったJSON | **削除と位置づけ直し**。判断1つで大半がほどける |
| **3. 写真家以外の正本化** | EN アーカイブ / 年代 / 運動 / 国別 | **写真家と問題の質が違う。同じ処方箋を当てない** |

---

## 2. 実測済みの事実（2026-09-15・**再検証不要**）

測り方：リポジトリ外（`/tmp`）に `git worktree` を作って再生成し、diff を取った。
**公開物には一切触れていない。** 同じことをやるなら同じ方法で（`.claude/worktrees/` 配下に作らない。
sitemap が膨張する既知の罠がある）。

### 2a. いま再生成すると何ページ変わるか

| サーフェス | 変化 | 中身 |
|---|---:|---|
| EN アーカイブ `en/archive.html` | **0 / 1** | きれい |
| EN 年代 `en/eras/*` | **2 / 11** | カードのリード文だけ（1980 / 2000）|
| **EN 運動 `en/movements/*`** | **24 / 35（69%）** | **退行を含む。下記 2b** |
| EN 国別 `en/countries/*` | **13 / 62** | CSS セレクタ + リード文 |
| JA 国別 `countries/*` | **4 / 62** | CSS セレクタ + **タグ消失** |

参考：写真家移行の動機になった数字は **60 / 394（15%）**。**運動の 69% はそれより濃い。**

### 2b. 運動の再生成で実際に起きる退行（**これが本命**）

- `<span>DE</span>` → `<span>PHOTOGRAPHER</span>`
  ＝ **2026-06-12 に全廃したはずの表示が復活する**（memory `reference_era_card_tags_are_not_card_data` 周辺の経緯）
- hero の `2 PHOTOGRAPHERS` → `1 PHOTOGRAPHERS`
  （同じページ内の `mvt-hero__meta-item` は 2 のまま＝**ページ内で不整合になる**）
- memory に既知記録：「EN再生成は運動固有 lede を汎用 lede で潰す（ガード検知なし）」

### 2c. 国別は2つの生成器が互いに矛盾している

- `generate_country_pages.py`（JA）は `.head__lang a` セレクタを**削る**
- `generate_country_pages_en.py`（EN）は同じセレクタを**足す**
- JA 再生成は `<span class="pc-body__tag">コンセプチュアル</span>` を**落とす**

### 2d. 4本の生成器には `--dry-run` が無い

`build_taxonomy_en.py` / `build_archive_en.py` /
`generate_country_pages.py` / `generate_country_pages_en.py` のどれにも無い。
**だから今回 worktree を作らないと測れなかった。**

### 2e. ★`build_photographers_en.py` は捨てられない（**前提を間違えやすい所**）

「凍結して残してある古いもの」ではなく、**新経路が動く土台**。実測：

```
render_en_page が呼ぶもの:
  _en_builder.process_page      ← EN描画エンジン本体（rebuild_* 14本）
  _en_builder._fb_jsonld / DEFAULT_OG_IMAGE
  _en_builder.build_jp_slug_map / load_classification
  from build_photographers_en import CJK_RE
```

**ただしファイルは2つにきれいに割れる:**

| 部分 | 行数 | 中身 |
|---|---:|---|
| **エンジン部** | **1,821行** | `process_page` + `rebuild_*` 14本。**JSONを読まない。触らない** |
| **CLI部 `main()`** | **167行** | **ここだけ**が EN正本JSON を読み、**ここだけ**が公開ENを上書きできる |

`process_page()` は page dict を**引数で受け取る**ので JSON に依存しない。
`CONTENT_JSON` を実際に読むのは `main()` の中の1箇所だけ。

**`classification.json` はエンジン部（`load_classification()`）が使うので、CLI を外しても動かせない。**
フェーズFで「動かさない」と決めたのは正しかった。

### 2f. コンテンツのバックログ（数の正本は `data/en-migration-ledger.json`）

| 件 | 数 | 備考 |
|---|---:|---|
| EN §REL の一言解説が無いリンク | **89件 / 22ページ** | **うち15ページが jp-漢字ペアのローマ字実ページ**＝原因が1つ |
| JA/EN の cite集合非対称 | 17ページ | |
| JA/EN の h3数非対称 | 21ページ | `ansel-adams` 含む |
| JA/EN の節数非対称 | 7ページ | |
| cite-id の欠番 | 3 | emerson / sakiko-nomura / stieglitz |
| 旧形式 §REF | 2 | stieglitz / hiroshi-sugimoto。**対応しない裁定済** |

### 2g. 残骸の在庫

- **旧EN JSON書込経路はフェーズ1で撤去済み**：importerの旧マージ・stage4注入・bundle出力CLI、
  §REL同期ツールのJSON適用2モード、移行監査2本、一回限り修正4本
- `HAND_MAINTAINED_EN`（5件）— 強制点は `build_photographers_en.py` の `main()` の中だけ
- `data/photographer-essay-overrides.js`（3.6MB）— `textEn` 224件は**死蔵**
  （読むのは実行禁止の旧ジェネレータ2本と `textEn` 自身の検査だけ）。
  **ただし `leadEn` は `build_archive_en.py` が現役で読むのでファイルは消せない**
- `data/photographers-en-classification.json` — 陳腐化（`missing_en` 12件は全件EN実在）。
  **ただし `jp_slug_mapping` はエンジン部が現役で読む**

---

## 3. クラスごとの打ち手（**たたき台。設計セッションで確定させる**）

### クラス1 — コンテンツのバックログ

- **89件のうち15ページ（jp-漢字ペア）は原因が1つ**なので、同質素材として**1バッチ**で処理できる
- 残りは既定方針どおり「該当ページを update するとき一緒に直す」
- 手順は `sync_en_rel_annotations.py` の `emit-worklist → 翻訳 → inject-html`。
  JSON経由の適用モードはフェーズ1で撤去済み。

### クラス2 — 残骸

**`build_photographers_en.py` の `main()`（167行）だけを撤去する**と、次が連鎖して片付く:

1. EN正本JSON を読む最後のコードが消える → **JSON の物理移動が可能になる**（フェーズFで断念した分）
2. `HAND_MAINTAINED_EN` の唯一の強制点が消える → 撤去できる
3. 公開ENを上書きできる経路が消える → `ALLOW_EN_REBUILD` という抜け道自体が不要になる
4. **エンジン部は無傷**なので `render_en_page` はそのまま動く

**「緊急rollback用に残す」という名目は弱い**（§4-1 で判断する）:
監査は台帳の sha256 のほうが正確。rollback は git がやる。
**JSON から作り直すのは rollback ではなく退行**（実測：`--all` で 60/394 が変わり 28枚で chip リンクが消える）。

### クラス3 — 写真家以外の正本化

**写真家と同じ処方箋を当ててはいけない。** 年代・運動・アーカイブの正本は **JA HTML** であって
JSON ではないので、移行の動機だった「正本が2系統」「死蔵JSONが増える」は**ここには無い**。

実際の問題は「**横断スクリプトが EN 出力を直接直していて、生成器がそれを知らない**」。
設計は2つありえて、**どちらが正しいかは §4-2 の spike で決まる**:

- **(a) EN タクソノミーHTMLを正本に昇格**（写真家と同じ。`🛑 REFUSED` ガードを足し、生成器は新規専用）
- **(b) 生成器を直して再生成を冪等にする**（JA 正本のまま。**正本が1つのままなので本来はこちらが上**）

---

## 4. ★未決の論点（**このセッションが決めるもの**）

### 4-1. `build_photographers_en.py` の `main()`（167行）を撤去してよいか

撤去すると失うのは「JSON から EN ページを一括再構築する能力」だけ。
**§3 クラス2 の1〜4がまとめてほどける。**
Daisuke に確認済みの論点で、**エンジン部1,821行には触らない**前提なら risk は限定的。

### 4-2. クラス3は (a) 昇格 か (b) 冪等化 か — **半日の spike で決める**

**運動24枚がなぜズレたかを分類する**のが spike の中身:
- **横断修正が EN にだけ入った**のが原因 → **(a)**
- **生成器が機能的に遅れている**だけ → **(b)**（正本が1つのまま済むので望ましい）

写真家移行の C-spike と同じ位置づけ。**ここで設計が変わるので本体の前に必ず置く。**

### 4-3. 国別の2生成器の矛盾（§2c）はどちらを正とするか

`.head__lang a` セレクタは JA が削り EN が足す。**どちらかが古い。** 決めないと片方が必ず退行する。

### 4-4. スコープをどこで切るか

「全部綺麗に」だが、**クラス1（原稿）とクラス2・3（配管）は同時に進めないほうがよい**
（写真家移行で D・E・F をバッチと並行不可にしたのと同じ理由）。

---

## 5. 推奨する順番（**見積もりは spike 後に引き直す**）

| # | やること | 目安 | 備考 |
|---|---|---|---|
| **0** | **4本の生成器に `--dry-run` を足す** | 1〜2h | **これが無いと以降を安全に測れない**（§2d）|
| 1 | §4-1 を判断（作業0） | — | Yes ならクラス2が1日で終わる |
| 2 | **§4-2 の spike** | 半日 | ここで設計が変わる |
| 3 | クラス1の jp-漢字15ページ | 1バッチ | 原因が1つなので同質素材扱い |
| 4 | クラス2の掃除 | 1日 | §4-1 が Yes の場合 |
| 5 | クラス3の本体 | spike後に確定 | |

**合計2〜3日と見ているが、これは spike 前の見立て。確定させない。**
この移行では見積もりを3回外している（Codex初回5日→実測2.5〜3日→最小版1日）。
**コードを測る前に工数を言わない。**

---

## 6. 作業規律（**前回の移行で高くついた教訓。必ず守る**）

- **既存関数を別の入力へ移すときは、先に旧実装の判定を全部列挙してからブリーフを書く**
  （E-1 でこれを怠り `cite-id が重複`(FAIL) と `cite-id に欠番`(WARN) を消しかけた）
- **旧経路の呼び出し箇所を着手前に grep で全部出す**（E-2 でそうしたら設計不備が0件になった）
- **件数ではなく集合で比較する。**「WARN が減った」は改善にも退行にも見える。
  消えた項目を全件分類して初めて判断できる
- **ガードは外さず置き換える**（`check_en_content_loss` → `check_en_json_frozen` はカバレッジ拡大）
- **フェーズごとに公開HTMLの sha256 集合を取り、作業後に照合する**（820枚。これが最後の砦）
- **`git add -A <dir>` を使わない**（未追跡 spec.json 305件を巻き込んだ実例あり）
- **Codex はクレジット上限で途中停止する前提でバッチを割る**。停止したら監督が引き取る
- **Codex が「設計と食い違う」と言って止まったら、たいてい Codex が正しい**
  （前回7回の停止のうち、監督のブリーフ不備が5回）

---

## 7. 絶対にやらないこと

- `scripts/generate_photographer_pages.py` / `generate_archive_pages.py` を実行しない
- **`build_photographers_en.py` のエンジン部（`main()` より前の1,821行）を触らない**
- `data/photographers-en-classification.json` を動かさない（エンジン部が `jp_slug_mapping` を読む）
- `data/photographer-essay-overrides.js` を削除しない（`build_archive_en.py` が `leadEn` を読む）
- 生成器をスコープフラグ無指定で実行しない（`--all` はガードが拒否する設計）
- `.claude/worktrees/` 配下に worktree を作らない（sitemap が 766→3097 に膨張した実例あり）
- 公開HTMLを、意図した対象以外で1バイトも変えない

---

## 8. 最初に読むファイル

1. **`docs/en-html-canon-migration.md` §13（総括）と §14（今回の対象外サーフェスの正本）**
2. 本文書 §2（実測）と §4（未決の論点）
3. `data/en-migration-ledger.json` の `_meta`（分類・findings・canon）
4. `CLAUDE.md` の「絶対禁止」と正本マトリクス
5. `docs/generators-and-guards.md`（機械チェックの意味）

---

# 9. ★設計フェーズの結論（2026-09-15・Opus監督 / Codex調査）

**§4 の未決4論点は決着した。以降はこの §9 が §2〜§5 に優先する。**
実測は `/tmp` の worktree で再生成 → diff。作業前後で公開HTML 1,069枚の sha256 は HEAD と完全一致（tracked 差分0）。

## 9.1 ★§2b は3つの主張のうち2つが誤りだった（**先にこれを読む**）

| §2b の主張 | 実測 |
|---|---|
| `<span>DE</span>`→`PHOTOGRAPHER` は 2026-06-12 に全廃した表示の復活 | **全廃されていない。** `archive.html` / `en/archive.html` は 402件とも `PHOTOGRAPHER`、JA運動ページも 246/298 が `PHOTOGRAPHER`。全廃したのは**年代ページだけ**（JA 12/402・EN 0/402）。ただし**退行であることは正しい**：JA/EN の一致が 274→246、不一致が 22→50 に悪化する |
| hero の枚数は EN 公開側が正しく JA が古い | **両方とも古い。** hero とカード実数の不一致は **JA 8ページ / EN 5ページ**。`pictorialism` は EN も「23」でカードは25。誰も保守していない数字 |
| 運動固有 lede を汎用 lede で潰す | **運動ページの散文（`mvt-hero__lead` / `ph-abstract` / `ph-thesis__body`）は再生成で1文字も変わらない**（実測0件）。潰れるのは**カードの lede**。しかも方向が逆で、**公開EN が古く、再生成が新しい内容を取り込む** |

**教訓：`memory/reference_site_wide_norms_not_bugs`（バグに見えるサイト全体の標準）をもう一度踏んだ。
「退行」と書く前に母数を数える。**

## 9.2 ★設計を変えた発見 — `data/taxonomy-en-content.json` は EN 散文の正本

§3 の「年代・運動・アーカイブの正本は JA HTML であって JSON ではないので、
移行の動機だった『正本が2系統』はここには無い」は**誤り**。

`data/taxonomy-en-content.json`（275KB）が **35運動＋11年代の EN 本文・thesis・overview・
title / OG / JSON-LD を全部持っており、EN タクソノミーHTML はその純粋なレンダリング結果**。
読者は `build_taxonomy_en.py`（`:1809-1831` で読み、`:1461-1469` `:1508-1516` `:1542-1572` で注入）と `preflight.py`。

**＝写真家ページと同じ構造がここにある。** 現時点で JSON と公開HTMLは一致しており
（散文の再生成差分は実測0件）、ドリフトはまだ起きていない——誰も EN タクソノミー散文を手で直していないから。

依存の実体は **`EN写真家HTML → en/archive.html → EN taxonomy / EN country`**。
`en/archive.html` のカード lede は JA archive の訳ではなく、
`overrides.leadEn` → TOP12 → **EN写真家ページ冒頭** → 手動辞書 の優先順位で決まる（`build_archive_en.py:4-8, 271-343`）。
**正本マトリクスの「ENアーカイブ ← archive.html（JA正本）」という1行はこの実態を写していない。**

## 9.3 再生成で実際に失われるもの（**全件・集合で比較した結果**）

| # | 失われるもの | 数 | 原因 |
|---|---|---:|---|
| 1 | sidebar の写真家チップ | **5** | bauhaus=Umbo / modernism=Modotti / new-vision=Henri / straight-photography=Abbott / surrealism=Cahun。**EN にだけあり JA に無い**。`build_taxonomy_en.py:998-1015` は sidebar の運動名しか訳さない |
| 2 | カードの `pc-top__meta` ラベル | **38** | 生成器が JA 運動ページのカードではなく `en/archive.html` から取る |
| 3 | `target="_blank"` | **16** | `build_taxonomy_en.py:605-607` が明示的に除去 |
| 4 | 本文内リンク | **1** | `en/movements/color-photography.html` の Saul Leiter（カード lede 内の `inline-photographer-link`。lede 差し替えで巻き添え） |
| 5 | 人物名の英訳 | **1** | conceptual-art の `Ruscha` が `ルシェ` に戻る |
| 6 | カードのタグ | **1** | mali / Seydou Keïta の `コンセプチュアル`。`card-data.json` は `"tags": []` |

**構造の消失は0**（`ph-section` 名・`cite-*`・`sup-ref` は全面で増減なし）。

## 9.4 再生成で改善されるもの（**(a) を選ぶと手作業になる分**）

| 改善 | 数 |
|---|---:|
| `en/archive.html` と食い違う陳腐化した lede | **67件 / 30ページ / 52名** |
| EN ページに残った**日本語のまま**の lede・タグ・channel | **13件 / 6ページ**（dada 3・pictorialism 4・straight-photography 3・photojournalism 1・eras/1910 1・countries/germany 1）|

## 9.5 決定（Daisuke・2026-09-15）

| 論点 | 決定 |
|---|---|
| **4-1** `build_photographers_en.py` の `main()` 撤去 | **Yes。Codex 案の3コミット構成**（§9.6）|
| **4-2** クラス3の設計 | **(a) EN タクソノミーHTML を正本へ昇格。** 写真家と同じ移行を運動・年代にも通す |
| **4-3** 国別2生成器の「矛盾」 | **矛盾ではない。** `.head__lang a` は冗長な重複規則で、全ページに独立した `.head__lang a{…}` が別に存在し**見た目は同一**。実質の論点は mali のタグ1件のみ |
| **4-4** スコープ | クラス1（原稿）とクラス2・3（配管）は同一フェーズに混ぜない。**ただし「カードのリード文233件のズレ」は既決の"直さない"案件**（`memory/feedback_card_lede_policy`）なので 4-2 の lede 差分と混同しない |
| `target="_blank"` | **JA の実態に合わせる＝維持。** 実測 JA運動 372件 / EN運動 361件（再生成すると345）。**除去コード `build_taxonomy_en.py:605-607` を外す** |

## 9.6 ★フェーズ計画

**順序が重要。(a) 昇格を先にやると §9.4 の80件が永久に手作業になる。
「欠陥を直す → 一度だけ再生成して現状を最新化する → 凍結して昇格」の順で通す。**

| # | フェーズ | 内容 | 公開HTML |
|---|---|---|---|
| **0** | 生成器に `--dry-run` | ✅ **完了（`c127f0b6e`）**。共通ヘルパ `scripts/gen_dry_run.py` で would-create / would-change / unchanged に分類。受け入れテストは §9.3 の実測と一致（taxonomy 26 / archive 0 / JA国別 4 / EN国別 13）| **0枚** |
| **1** | 旧JSON書込経路の撤去 | ✅ **完了（`a4e23210e`）**。importer の `--merge-to-en` / `--update-en-json` / `--bundle-to-en`、`sync_en_rel_annotations` の `--apply` / `--apply-batch`、スクリプト6本を撤去（-3,290行）。**builder を subprocess で呼ぶ箇所が0件になった＝フェーズ2の前提が整った** | **0枚** |
| **2** | builder を module-only 化 | ✅ **完了（`7279c87a4`）**。`main()` / `_deep_merge_page()` / `CONTENT_JSON` / CLI専用 import / `ALLOW_EN_REBUILD`・`ALLOW_HAND_MAINTAINED_REBUILD` を撤去（1988→1796行）。**エンジン部は byte 一致で不変更**（`CLASSIFICATION_JSON`〜`process_page` 末尾 75,263 bytes）。直接実行は EXIT 2。`detect_content_loss()` は呼び出し元0になるが意図して残置 | **0枚** |
| **3** | EN正本JSONの物理移動 | ✅ **完了（`959c3130f`）**。stale な update 表示を撤去し、corpus audit / `build_en_migration_ledger.py` / `preflight.py` の読取先を `data/archive/` へ移行。rename 直後用の baseline フォールバックを凍結ガードに追加。**`photographers-en-classification.json` は不変** | **0枚** |
| **4** | タクソノミー生成器の欠陥修正 | §9.3 の6件。sidebar 5名は**JA へ昇格**（EN にだけある＝JA が欠けている）、カードラベルは JA カードから取る、`target` 除去をやめる、Ruscha の人物名訳、lede 差し替え後にインラインリンクを再適用、mali タグは `card-data.json` へ | **0枚** |
| **5** | **一度だけ再生成して最新化** | §9.4 の 67+13 件が解消し、§9.3 の6件が保全されることを**集合で確認**してから採用。差分は「意図した改善のみ」であること | **約39枚**（運動24・年代2・国13）|
| **6** | **EN タクソノミーHTML を正本へ昇格** | `build_taxonomy_en.py` を新規ページ専用にし、既存出力への書込を `🛑 REFUSED` で拒否（解除は `ALLOW_TAXONOMY_REBUILD=1` のみ）。`taxonomy-en-content.json` を読み取り専用アーカイブへ降格し、`preflight` に凍結ガードを追加（`check_en_json_frozen()` と同型）。正本マトリクスと §14 を書き換え | **0枚** |
| **7** | クラス1（原稿バックログ） | EN §REL 一言89件ほか §2f。**該当ページを update するとき一緒に直す既定方針のまま** | 都度 |

**各フェーズ共通の検証**（`§6 作業規律`をそのまま適用）:
公開HTMLの sha256 集合を作業前後で照合（フェーズ5のみ意図した39枚だけが変わる）／
`preflight.py` の出力差分／`check_content_loss.py`／`git status --short` と `git diff --name-only` で
対象外ファイルの巻き込みが0であること／**`git add -A <dir>` を使わない**（未追跡 spec.json が305件ある）。

## 9.7 まだ決めていないこと

- **フェーズ6で `taxonomy-en-content.json` の `meta`（title / OG / JSON-LD）をどう扱うか。**
  散文と違い SEO メタは機械生成のほうが安全な可能性がある。フェーズ5の実測後に決める。
- **JA タクソノミーHTML 側の hero 枚数（JA 8ページ・EN 5ページで実カード数と不一致）を、
  手で直すか実カード数から導出するか。** `sync_card_counts.py` の対象は archive とトップで、運動は入っていない。
