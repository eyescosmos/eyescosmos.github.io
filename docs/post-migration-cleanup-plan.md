# 移行後の総ざらい — 設計から始める引き継ぎ（2026-09-15 作成）

**いつ読むか:** EN写真家ページの正本HTML化（`docs/en-html-canon-migration.md`）が完了したあと、
残った宿題・残骸・**写真家ページ以外のサーフェスの正本化**をまとめて片付けるとき。

**★2026-09-15 更新：設計フェーズは終わった。§4 の4論点は決着している。**
**新規セッションは §9「設計フェーズの結論」を最初に読む。§9 は §2〜§5 に優先する。**
特に **§9.1（§2b の3主張のうち2つが実測で誤りと判明）** と
**§9.2（`data/taxonomy-en-content.json` が EN 散文の正本＝§3 の前提が誤り）** を読み飛ばさない。
実装は **§9.6 のフェーズ計画**の順に進める（順序に意味がある）。
**★フェーズ0〜6 は完了・push 済み。配管（正本の一本化・ガード）はクリーン。
フェーズ6 の実施結果は §11。**
**★残っているのは2つ：クラス2の残骸撤去（→ §12「残骸撤去の引き継ぎ」。次セッションはここだけ読めばよい）と、
フェーズ7＝クラス1の原稿バックログ（専用セッションは組まない既定方針）。**

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
| 3 | カードの `target="_blank"` | 公開EN **16 → 生成0** | JA も 27/298件だけで同一ページ内に混在。生成器の除去は、多数派どおりカードを同一タブへ統一する意図した正規化（2026-09-15 再決定） |
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
| `target="_blank"` | **カードでは除去を維持し、同一タブへ統一。** JA運動298カード中target付きは27件だけで、同一ページ内でも混在する。多数派271件と生成器コメント `open in same window` が一致するため、公開ENの16件も再生成時に0へ正規化する。JAの27件は別件バックログ |

## 9.6 ★フェーズ計画

**順序が重要。(a) 昇格を先にやると §9.4 の80件が永久に手作業になる。
「欠陥を直す → 一度だけ再生成して現状を最新化する → 凍結して昇格」の順で通す。**

| # | フェーズ | 内容 | 公開HTML |
|---|---|---|---|
| **0** | 生成器に `--dry-run` | ✅ **完了（`c127f0b6e`）**。共通ヘルパ `scripts/gen_dry_run.py` で would-create / would-change / unchanged に分類。受け入れテストは §9.3 の実測と一致（taxonomy 26 / archive 0 / JA国別 4 / EN国別 13）| **0枚** |
| **1** | 旧JSON書込経路の撤去 | ✅ **完了（`a4e23210e`）**。importer の `--merge-to-en` / `--update-en-json` / `--bundle-to-en`、`sync_en_rel_annotations` の `--apply` / `--apply-batch`、スクリプト6本を撤去（-3,290行）。**builder を subprocess で呼ぶ箇所が0件になった＝フェーズ2の前提が整った** | **0枚** |
| **2** | builder を module-only 化 | ✅ **完了（`7279c87a4`）**。`main()` / `_deep_merge_page()` / `CONTENT_JSON` / CLI専用 import / `ALLOW_EN_REBUILD`・`ALLOW_HAND_MAINTAINED_REBUILD` を撤去（1988→1796行）。**エンジン部は byte 一致で不変更**（`CLASSIFICATION_JSON`〜`process_page` 末尾 75,263 bytes）。直接実行は EXIT 2。`detect_content_loss()` は呼び出し元0になるが意図して残置 | **0枚** |
| **3** | EN正本JSONの物理移動 | ✅ **完了（`959c3130f`）**。stale な update 表示を撤去し、corpus audit / `build_en_migration_ledger.py` / `preflight.py` の読取先を `data/archive/` へ移行。rename 直後用の baseline フォールバックを凍結ガードに追加。**`photographers-en-classification.json` は不変** | **0枚** |
| **4** | タクソノミー生成器の欠陥修正 | ✅ **完了（`60aca8743`）**。運動カードのラベルを JA カードから継承（JA/EN 不一致 **22→0**）。`card-data.json` の `nameJa`/`nameEn` で人物名チップも訳す（`ルシェ→Ruscha`。同種は全35ページでこの1件のみ）。カードの `target` 除去は意図した正規化として維持。**年代は `swap_nationality` の挙動を変えない**（JA を鏡写しにすると JA 側の取りこぼし12件が EN へ逆流するため）| **0枚** |
| **5** | **入力データ／コンテンツ修正＋一度だけ再生成** | ✅ **完了（`8537af7fd`）**。JA運動5ページの sidebar に5名追加／`build_archive_en.py` の `CHANNEL_PREFIX` に「形態を比較する写真→Comparing form」追加（再生成で英語→日本語へ戻る退行を検出したため）／**mali のタグは修正しない判断に変更**（§9.7）。改善: 陳腐化 lede **67→0**・EN カード内の日本語 **13→0**・JA/EN ラベル不一致 **22→0**。消失は全項目 **0** | **51枚**（en/movements 25・en/countries 13・movements 5・countries 4・en/eras 3・en/archive 1）|
| **6** | **EN タクソノミーHTML を正本へ昇格** | ✅ **完了（`5c82451bc` 〜 §11）**。`build_taxonomy_en.py` を新規ページ専用にし、既存46枚への書込を `🛑 REFUSED`（解除は `ALLOW_TAXONOMY_REBUILD=1` のみ・`--dry-run` でも解除されない）。`taxonomy-en-content.json` を `data/archive/` へ move し `check_en_json_frozen()` の凍結対象に追加。直接編集疑い WARN を JA↔EN 節対称性チェックへ置換。**副作用として `add_photographer.py --apply-surfaces` の EN年代再生成が使えなくなり、手貼り手順へ差し替えた** | **0枚** |
| **7** | クラス1（原稿バックログ） | EN §REL 一言89件ほか §2f。**該当ページを update するとき一緒に直す既定方針のまま** | 都度 |

**各フェーズ共通の検証**（`§6 作業規律`をそのまま適用）:
公開HTMLの sha256 集合を作業前後で照合（フェーズ5のみ意図した39枚だけが変わる）／
`preflight.py` の出力差分／`check_content_loss.py`／`git status --short` と `git diff --name-only` で
対象外ファイルの巻き込みが0であること／**`git add -A <dir>` を使わない**（未追跡 spec.json が305件ある）。

## 9.7 フェーズ4で可視化したバックログ（**今回は直さない**）

| 件 | 数 | 中身 |
|---|---:|---|
| JA 年代ページに残る `PHOTOGRAPHER` | **12** | 1910: Florence Henri / Tina Modotti / Umbo ／ 1930: Alfred Eisenstaedt / Berenice Abbott / Cecil Beaton / Claude Cahun / Frederick Sommer / Gerda Taro ／ 1950: Aaron Siskind / Erwin Blumenfeld / Hiroshi Hamaya。2026-06-12 の国コード統一の取りこぼし。**EN 年代は 402件すべて国コードで完成している**ので、JA を直す話 |
| JA 運動カードの `target="_blank"` | **27 / 298** | 11ページに散在し、**同一ページ内で混在**（バウハウスは Umbo だけ新規タブ・Moholy-Nagy は同一タブ）。EN は再生成で0へ正規化されるので、JA だけが不統一として残る |
| `movements/リアリズム写真.html` のレガシーカード | **2** | `pc-card--photographer` ではなく素の `pc-card`。**運動35ページでここだけ**。ラベル修正は届いている（差分で確認済）|

### 9.7.1 ★フェーズ5で判断を変えた件 — mali のタグ

当初は `card-data.json` の `seydou-keita` に `コンセプチュアル` を足す計画だった
（公開ページにあって正本に無いため）。**母数を数えたら覆った。**

`cards-archive.html` にあって `card-data.json` に無いタグを持つカードは **50件**あり、
その大半が**旧語彙**だった:

| 旧語彙（cards-archive 側） | 新語彙（card-data 側） |
|---|---|
| `コンセプチュアル`（card-data では5件）| `コンセプチュアルアート`（**106件**）|
| `FSA`（3件）| `FSA写真`（7件）|
| `プライベート写真`（2件）| `インティメイト・ライフ`（12件）|

＝ **`cards-archive.html` が旧語彙を抱えたままで、`card-data.json` のほうが新しい。**
`seydou-keita` の `tags: []` は「この人にコンセプチュアルのタグは付けない」という
決定の結果であり、**再生成がタグを落とすのは正しい伝播**。足していたら決着済みの
整理を1ページだけ巻き戻していた。

**バックログ: `new-design/cards-archive.html` の旧語彙タグ50件**（今回は直さない）。

## 9.8 まだ決めていないこと

- ~~**フェーズ6で `taxonomy-en-content.json` の `meta`（title / OG / JSON-LD）をどう扱うか。**~~
  **決着（2026-09-15・§11.1）。散文と同じく HTML を正本にした。**
  「機械生成のほうが安全」は実測で否定された＝`meta` を持つ42件は**全件**が機械テンプレと不一致で、
  機械生成へ寄せると公開42枚の title/description/OG/JSON-LD が書き換わる。
- **JA タクソノミーHTML 側の hero 枚数（JA 8ページ・EN 5ページで実カード数と不一致）を、
  手で直すか実カード数から導出するか。** `sync_card_counts.py` の対象は archive とトップで、運動は入っていない。

---

# 10. ★フェーズ6 の引き継ぎ（新規セッション用・2026-09-15 作成）

**フェーズ0〜5 は完了・push 済み（`7c6edf54d`）。次はフェーズ6だけ。**
このセクションだけ読めば着手できる。設計の根拠は §9、実測は §9.3 / §9.4 / §9.7。

## 10.1 フェーズ6 でやること — EN タクソノミーHTML を正本へ昇格

Daisuke の決定（§9.5 の 4-2）＝ **(a) 昇格**。写真家ページと同じ移行を**運動・年代**に通す。

| # | やること |
|---|---|
| 1 | `build_taxonomy_en.py` を**新規ページ専用**にする。出力先が実在したら `🛑 REFUSED` で拒否。解除は `ALLOW_TAXONOMY_REBUILD=1` のみ（`--force` でも `--dry-run` でも解除しない＝写真家 builder と同じ契約）|
| 2 | `data/taxonomy-en-content.json`（275KB）を**読み取り専用アーカイブへ降格**。`data/archive/` へ move してよい（フェーズ3と同じ手順）|
| 3 | `preflight` に凍結ガードを追加（`check_en_json_frozen()` と同型。**origin/main に新パスが載るまでの旧パス・フォールバックも同型で必要**）|
| 4 | 正本マトリクス（`CLAUDE.md` / `AGENTS.md`）と `docs/en-html-canon-migration.md` §14 を書き換える |
| 5 | **`preflight` の「生成物を直接編集した疑い」WARN を作り直す**（下記 10.4）|

**公開HTMLは0枚**のはず。1枚でも動いたら設計を間違えている。

## 10.2 ★着手前に知っておくべき現在値（2026-09-15 実測）

**再生成ドリフトはほぼゼロになった。凍結するのに理想的な状態。**

| 生成器 | would-change |
|---|---:|
| `build_taxonomy_en.py --all` | **1**（下記の意図した手編集のみ）|
| `build_archive_en.py` | **0** |
| `generate_country_pages.py --all` | **0** |
| `generate_country_pages_en.py --all` | **0** |

唯一の残差＝`en/movements/color-photography.html` の Saul Leiter の
`inline-photographer-link`。再生成で落ちるのでフェーズ5で手で復旧した。
**フェーズ6で EN HTML が正本になれば、これは「正しい状態」になる。**

4本とも `--dry-run` を持っている（フェーズ0で追加）。**必ず dry-run で測ってから動かす。**

## 10.3 ★スコープ — 国別は昇格しない

- **昇格するのは 運動（35）と 年代（11）だけ。**
- **国別は対象外。** 正本は `data/country-pages.json` で、これは散文の置き場ではなく
  **本物のデータ正本**（国の登録・掲載写真家の解決）。二重正本の問題がここには無い。
  国別の EN/JA は生成物のままでよい。

## 10.4 ★忘れると事故る3点

1. **`preflight` の「生成物を直接編集した疑い」WARN は作り直しが要る。**
   現在の実装（`preflight.py` の `check_country_pages` / taxonomy / `check_archive_en`）は
   「HTML が変わったのに正本JSONが不変」で発火する。昇格後は **EN タクソノミーHTML の
   直接編集が正規の運用**になるので、運動・年代についてはこの WARN を**外すか、
   JA HTML との対称性チェックへ置き換える**（写真家ページで `check_en_json_frozen()` へ
   置き換えたときと同じ「ガードは外さず置き換える」原則）。
   **国別とアーカイブの WARN は残す**（そちらは生成物のままなので）。
2. **フェーズ3で入れた旧パス・フォールバックはもう使われない。**
   `preflight.check_en_json_frozen()` の `EN_JSON_ARCHIVE_LEGACY_PATHS` は、
   push で `origin/main` に `data/archive/` が載ったため dormant。**フェーズ6で撤去してよい**
   （コードにその条件をコメント済み）。
3. **`taxonomy-en-content.json` の `meta`（title / description / OG / JSON-LD）の扱いは未決。**
   散文と違い SEO メタは機械生成のほうが安全かもしれない。**§9.8 の未決事項。
   着手時に Daisuke に確認する。**

## 10.5 作業規律（フェーズ0〜5 で実際に効いたもの）

- **公開HTMLの sha256 を作業前後で全件照合する。** フェーズ5では 1,080枚中
  意図した51枚だけが変わり、追加・削除0を確認した
- **件数ではなく集合で比較する。** 監督の href 集合比較は `<span>` 内にネストした
  sidebar chip を取りこぼした（Codex が発見）
- **「退行」と書く前に母数を数える。** §9.1 と §9.7.1 で2回、母数を数えたら判断が覆った
- **非ASCIIパスは grep で取りこぼす。** `git -c core.quotepath=false` を使う。
  IndexNow も同じ罠があり、JA 運動ページは `--urls` で percent-encode して直指定する
- **Codex が「設計と食い違う」と言って止まったら、たいてい Codex が正しい。**
  フェーズ0〜5 で3回止まり、**3回とも監督のブリーフ不備だった**
- **Codex はクレジット上限で止まる前提でバッチを割る。** フェーズ4で実際に発生し、
  監督が受け入れテストを引き取った

## 10.6 フェーズ7（クラス1＝原稿バックログ）は既定方針のまま

EN §REL の一言解説89件ほか §2f / §9.7 のバックログは、
**該当ページを次に update するときに一緒に直す**。専用セッションは組まない。

---

# 11. ★フェーズ6 の実施結果（2026-09-15・Opus監督 / Codex実装）

**EN タクソノミーHTML（運動35＋年代11＝46枚）を正本へ昇格した。公開HTML 0枚。**
作業前後で公開HTML **1,080枚の sha256 が完全一致**（追加・削除0）。preflight の出力差分も0。

## 11.1 着手前の未決1件（§10.4-3）の決着 — meta は HTML 正本にした

「散文と違い SEO メタは機械生成のほうが安全かもしれない」は**実測で否定された**。

| 実測 | 値 |
|---|---:|
| `meta` を持つエントリ | 42（運動31 / 年代11）|
| そのうち builder の機械テンプレと**一致**する数 | **0** |
| `meta` を持たない運動（機械テンプレのまま公開中）| 4 |

title の書式が JSON 側は `X | Meaning in Photography History | …`（30件）、
テンプレ側は `X | Photography Movement | …` で、description も 42件全部が別文だった。
機械生成へ寄せると**公開42枚の head が書き換わる**＝「公開HTML 0枚」条件を破る。

**決定（Daisuke）**: (A) 散文と同じく HTML を正本にする ＋ 新規ページ用フォールバック title を
公開済み31件の多数派書式（`| Meaning in Photography History |`）へそろえる。

## 11.2 コミット

| # | commit | 内容 | 公開HTML |
|---|---|---|---|
| 6-1 | `5c82451bc` | 生成器を新規ページ専用に。既存46枚は `🛑 REFUSED`（exit 1）。新規用フォールバック title を多数派書式へ。旧書式のまま公開されている4枚は `LEGACY_TITLE_SLUGS` で据え置き | 0 |
| 6-2 | `22ab37d7d` | `data/taxonomy-en-content.json` → `data/archive/` へ move（git 上も pure rename・sha256 `8c284555…` 一致）。読み手2本の参照先を更新 | 0 |
| 6-3 | `1146993bf` | `check_en_json_frozen()` の凍結対象に追加（3本目）。直接編集疑い WARN を JA↔EN 節対称性チェックへ置換。photographers の旧パス・フォールバックを撤去し taxonomy 用に入れ直し | 0 |
| 6-4 | `97e7455f9` | `add_photographer.py` の EN年代再生成呼び出しを手貼り手順へ差し替え（下記 11.4）| 0 |

## 11.3 ★ブリーフ不備を Codex が止めた（4回目・§10.5 の通り）

フォールバック title を新書式へ変えると、**JSON に `meta` を持たない4運動**
（`contemporary-still-life` / `post-internet-photography` / `new-topographics` / `intimate-life`）に効き、
escape hatch（`ALLOW_TAXONOMY_REBUILD=1`）での rollback が **would-change 1 → 5** に劣化する。
＝**凍結するアーカイブが公開状態を再現できなくなる。**

JSON 側に title を書き足す案は、凍結ガードを入れるその push 自体で
`ALLOW_EN_JSON_ARCHIVE_WRITE=1` の迂回が要る（ガードは `origin/main` と比較するため）。
**迂回の要らない側＝builder に `LEGACY_TITLE_SLUGS`（旧書式のまま公開されている4枚）を置いて解決した。**
結果、rollback は would-change 1（`color-photography` の手編集のみ）に戻った。

## 11.4 ★昇格の代償 — 写真家追加フローが1手増えた（§10 が想定していなかった）

`add_photographer.py --apply-surfaces` は `build_taxonomy_en.py --era <era>` を subprocess で呼んでいた。
フェーズ6-1 以降これは必ず REFUSED（rc=1）になる。**放置すると**:
EN 年代ページに新カードが入らない → `preflight.check_taxonomy_presence()` が
**HARD FAIL で push を止める**（EN 年代は必須サーフェス・2026-09-05 決定）。

対処（6-4）: 呼び出しを外し、**カードを手で足す手順**を表示するようにした
（元カードは `en/archive.html` から流用 → グリッド閉じの直前へ挿入 → hero / sidebar の枚数を +1）。
`plan_surfaces` の「REGEN 面」からも EN タクソノミーを外し、手貼り面として表示する。

**EN 運動ページは任意サーフェス**（`feedback_movement_pages_are_a_surface_too`）なので
HARD にはならないが、載せるなら同じく手貼り。

## 11.5 検証（すべて実測）

| 項目 | 結果 |
|---|---|
| 公開HTML 1,080枚の sha256 | **完全一致**（追加・削除0）|
| `preflight.py` の出力 | 作業前と**差分0**・exit 0 |
| `check_content_loss.py` | exit 0 |
| `build_taxonomy_en.py --all --dry-run` | REFUSED 46 / 分類各0 / exit 1 |
| 単体 `--slug`（dry-run・実行とも）| REFUSED 1 / exit 1 / **ファイル未書込** |
| `ALLOW_TAXONOMY_REBUILD=1 --all --dry-run` | would-change **1**（`color-photography`）/ unchanged 45 / exit 0 |
| スコープ無指定 | exit 2（既存ガード健在）|
| 凍結ガード（JSON を1バイト改変）| **HARD FAIL・exit 1** → `git checkout` で復元し exit 0 |
| `ALLOW_EN_JSON_ARCHIVE_WRITE=1` | その HARD が出ない（解除が効く）|
| JA↔EN 節対称性 全46組 | mismatch **0**（置き換え先チェックは現状グリーン）|
| 巻き込み | 未追跡 spec.json 305件は未 stage。`.html` の差分0 |

## 11.6 フェーズ6 で残したもの

- ~~**`EN_JSON_ARCHIVE_LEGACY_PATHS` の taxonomy エントリ**~~ → **撤去済み**（`origin/main` へ push 後に実施）。
  フェーズ3・6 の rename がどちらも `origin/main` に載ったので、旧パス（`data/*.json`）への
  フォールバックは全廃した。**次にこの3本を move するときは、その push が済むまで
  同型のフォールバックを一時的に入れ直すこと**（コードにコメント済み）。
  撤去後に3本とも1バイト改変で HARD になることを実測済み。
- **`data/archive/taxonomy-en-content.json` は消さない。** `ALLOW_TAXONOMY_REBUILD=1` の
  緊急 rollback は、この JSON から meta / sections を復元する経路として残っている。
- §9.7 のバックログ（JA 年代の `PHOTOGRAPHER` 12件・JA 運動の `target="_blank"` 27件・
  `cards-archive.html` の旧語彙タグ50件）は**今回も直していない**。

---

# 12. ★残骸撤去の引き継ぎ（2026-09-15 作成・**次セッション用**）

**フェーズ6 完了後に「EN JSON 移行は全部クリーンか」を実測した結果、クラス2（残骸）が
3件残っていた。** 打ち手はそれぞれ違い、**1件は削除できない**（下の 12.3）。
Daisuke 決定（2026-09-15）＝**この3件を撤去する**。

**前提：配管そのものはクリーン。** ここから先は「消し忘れの掃除」であって、
事故を起こす経路の修理ではない。**急ぎではないが、やるなら実測を先にやり直すこと**
（下の数字は 2026-09-15 時点。撤去前に必ず測り直す）。

## 12.0 全体の受け入れ条件（3件共通）

- **公開HTML 1,080枚の sha256 を作業前後で全件照合**（対象＝tracked `*.html` から `design/` を除く）。
  **変更0枚**が条件。1枚でも動いたら設計を間違えている
- `preflight.py` の出力差分0・exit 0 ／ `check_content_loss.py` exit 0
- **`build_archive_en.py --dry-run` が would-change 0 のままであること**（12.1 の要）
- `git add -A` を使わない（未追跡 spec.json が305件ある）

---

## 12.1 `data/photographer-essay-overrides.js` — **半分だけ死蔵**（全消しは事故）

**★このファイルは死蔵ではない。消す前に必ずこの節を読む。**

実測（2026-09-15）:

| 項目 | 値 |
|---|---:|
| ファイルサイズ | 2,649,290 bytes |
| エントリ数 | 157 |
| `leadJa` / `leadEn` を持つエントリ | **各100（生きている）** |
| `textJa` / `textEn` を持つエントリ | 各76（死蔵）|
| `textJa` + `textEn` が占めるバイト数 | **約 1,234,310（47%）** |

**`leadEn` / `leadJa` の生きた読み手は2つ:**
1. `build_archive_en.py`（`:5, 274-289, 336`）— `en/archive.html` のカード lede の**最優先ソース**
   （`overrides.leadEn` → TOP12 → EN写真家ページ冒頭 → 手動辞書）
2. `relations.html` / `en/relations.html` の**2枚**が `global-search.js:17` で実行時にロードし、
   `:237-242` で `override.leadEn` / `override.leadJa` を表示に使う
   （relations 2枚は v5.1 移行の据え置き例外＝[[project_v51_migration_status]]）

**`textJa` / `textEn` が死蔵である根拠（全件 grep 済み）:**
読み手は `check_texten_completeness.py` と、実行禁止の
`generate_photographer_pages.py` / `generate_archive_pages.py` **だけ**。
`global-search.js:241-242` の `context.textEn` は `data/photographers*.js` 由来で
overrides ではない（`add_photographer.py:141` がその context を組んでいる）。

### やること
- **`textJa` / `textEn` を76エントリから削除**（−1.23MB）。`leadJa` / `leadEn` は**残す**
- `check_texten_completeness.py` を削除（textEn 専用の検査スクリプト・110行）
- `CLAUDE.md` の overrides 記述と `docs/content-preservation.md:31` の実行手順を更新

### ★検証（ここを外すと en/archive.html が壊れる）
- `python3 scripts/build_archive_en.py --dry-run` → **would-change 0**（撤去前後とも）
- `relations.html` / `en/relations.html` の sha256 不変
- 削除後に `leadEn` を持つエントリが **100件のまま**であること（件数で確認する）

### 済んでいること
`CLAUDE.md` の「**ライブページで `overrides.js` を読む枚数は 0**」は**誤りだったので訂正済み**
（2026-09-15・実測2枚）。`textEn` が死蔵という記述のほうは正しい。

---

## 12.2 `HAND_MAINTAINED_EN` — 強制点を失った5件

`check_en_entry.py:42` に `{'stieglitz.html', 'annie-leibovitz.html', 'shoji-ueda.html',
'toyoko-tokiwa.html', 'lee-miller.html'}` が残っている。

**フェーズ2で builder の再生成経路が消えたので、いまや全ENページが hand-maintained。**
現在の唯一の役目は `build_en_migration_ledger.py:324` が
`data/en-migration-ledger.json` に `hand_maintained_history` フラグを立てること（台帳内 6箇所）。
**preflight は台帳を読んでいない**（grep 済み）ので、撤去してもガードは1つも減らない。

### やること
- `check_en_entry.py:41-42` の定数とコメントを削除
- `build_en_migration_ledger.py:27` の import と `:324` のフラグ生成を削除
- 台帳を再生成するか、**歴史記録として据え置くか**を決める（据え置きなら台帳は触らない）
- `memory/feedback_lee_miller_no_blind_rebuild` と `memory/feedback_shoji_ueda_html_canonical` は
  「機械ガード化済」と書いているので、**撤去したら両方を「HTML 直接編集が正規手順」へ更新する**

---

## 12.3 実行禁止スクリプト3本 — **1本は削除できない**

| スクリプト | 行数 | 物理ガード | Python import | 判定 |
|---|---:|---|---:|---|
| `generate_photographer_pages.py` | 3,079 | `:2690` ABORT | 0 | **削除可** |
| `generate_archive_pages.py` | 362 | `:300` ABORT | 0 | **削除可** |
| `generate_taxonomy_pages.py` | 2,202 | 無し | **3** | **★削除できない** |

### ★`generate_taxonomy_pages.py` を消してはいけない理由
`link_country_keywords.py:30-32` が `COUNTRY_BASE_META`（`generate_taxonomy_pages.py:184`）を
import して使っている。**`link_country_keywords.py` は生きた横断スクリプト**で、
`CLAUDE.md:62` に実行後の確認手順が、`docs/content-preservation.md:112,122` に実装の説明がある。
残り2つの import 元（`generate_archive_pages.py:7` / `generate_photographer_pages.py:13`）は
どちらも削除対象なので、**実質の依存は `link_country_keywords.py` 1本**。

→ **消したいなら `COUNTRY_BASE_META` を独立モジュール（例 `scripts/country_meta.py`）へ
切り出して `link_country_keywords.py` の import を差し替えるのが先。**
そこまでやらないなら `generate_taxonomy_pages.py` は残す（実行禁止リストにも載っていない）。

### 削除する2本の波及（全部直す）
- `CLAUDE.md` 絶対禁止 **1・2番**／`AGENTS.md` 絶対禁止 **1・2番** — 「実行しない」から
  「**削除済み**」へ書き換える（履歴として何だったかは1行残す）
- `scripts/add_photographer.py:12`（docstring）と `:884`（実行時の注意書き）
- `scripts/photographer-page.js:2` のコメント
- `scripts/build_photographers_en.py:20` の `Never imports/runs ...` の行
- `scripts/add_taxonomy_nav_to_archive.py:22` のコメント
- `scripts/build_photographers_en.SPEC.md` ／ `docs/content-preservation.md` ／
  `docs/en-html-canon-migration.md` ／ `docs/photographer-leaf-spec.md` ／
  `docs/generators-and-guards.md`
- **`docs/importer-run-log.md` は履歴なので書き換えない**

### ★削除前のバックアップ＝**tag で取ってある**（2026-09-15・push 済み）

Daisuke は「あとで確認したくなる」と明言している（2026-09-15）。**消してよいが、
下の tag から必ず引けるようにしてある。** tag は `dad0c73cb`（削除前の最後の commit）を指す。

```bash
git show legacy-generators-2026-09-15:scripts/generate_photographer_pages.py > /tmp/old-gen.py
git show legacy-generators-2026-09-15:scripts/generate_archive_pages.py       > /tmp/old-archive.py
git show legacy-generators-2026-09-15:scripts/check_texten_completeness.py    > /tmp/old-texten.py
git show legacy-generators-2026-09-15:data/photographer-essay-overrides.js    > /tmp/old-overrides.js
```

tag 名: **`legacy-generators-2026-09-15`**（annotated・origin へ push 済み）。
12.1 の `textJa` / `textEn` 1.23MB もこの tag に入っている。
**この tag は消さない。**

---

## 12.5 ★実施結果（2026-09-15・完了）

**3件とも撤去した。**公開HTML 1,080枚の sha256 は作業前後で全件一致（変更0枚）。
コミットは打ち手ごとに分けた。

| 単位 | commit | 実施内容 |
|---|---|---|
| 12.1 | `729f281ce` | `overrides.js` の `textJa`/`textEn` 446プロパティを撤去（3,631,495 → 1,409,312 bytes・−2.22MB）。`check_texten_completeness.py` 削除 |
| 12.2 | `499512a8a` | `HAND_MAINTAINED_EN` を `check_en_entry.py` から撤去し、`build_en_migration_ledger.HAND_MAINTAINED_HISTORY` へ移設。台帳を再生成 |
| 12.3 | `d2b5246cd` | `generate_photographer_pages.py`（3,079行）と `generate_archive_pages.py`（362行）を削除。波及13ファイルを「実行しない」→「削除済み・復活させない」へ更新 |

### ★着手時に §12 の記述が誤っていた点（測り直して判明）

1. **12.1 の実測値が全部ズレていた。** 記載「157エントリ / leadJa 100 / textJa 76 /
   ファイル 2,649,290 bytes」に対し、実測は **265 slug / leadJa 265 / leadEn 265 /
   textJa 222 / textEn 224 / 3,631,495 bytes**。
   §12 が「撤去前に必ず測り直す」と書いていたのが効いた。
2. **12.1 の読み手リストが不完全だった。** §12 は `textEn` の読み手を
   `check_texten_completeness.py` と旧ジェネレータ2本「だけ」としていたが、
   **`scripts/site.js:662` が `override.textJa`/`textEn` を主ソースとして読む**
   （`:588` は lead へのフォールバック）。ただし **site.js を読み込む HTML は0枚**
   （参照は docs と `generate_taxonomy_pages.py` のみ）なので死蔵で確定し、撤去は安全だった。
   → **次に「死蔵」を判定するときは、ファイルを読む HTML の枚数まで数えること。**
3. **`textJa`/`textEn` には2つの直列化形式があった。** バッククォートの
   テンプレートリテラル形式（306）と、ダブルクォートの JSON 文字列形式（140）。
   片方だけ消すと eval 後に 69 件残る。実装役（Codex）が期待値不一致で停止して発覚した。

### 12.2 の未決論点は「移設」で決着

§12.2 は「台帳を再生成するか据え置くか」を未決にしていた。**移設**を選んだ。
完全削除だと台帳の `hand_maintained` flag が次の再生成で黙って消え、移行の履歴
（ページ別の理由5件）が再現できなくなるため。台帳の再生成差分は
`generated_at_commit` と `hand_maintained_registry` の2箇所のみで、
`hand_maintained` の5件は撤去前と同一＝再現性を維持した。

### 検証に使った実測（3件共通）

- 公開HTML 1,080枚（tracked `*.html` − `design/`）の sha256 全件照合 → **変更0枚**
- `preflight.py` の出力がベースラインと完全一致・exit 0
- `check_content_loss.py` exit 0
- `build_archive_en.py --dry-run` の出力がベースラインと完全一致（would-change 0）
- `parse_overrides_lead_en()` の leadEn マップ196件が撤去前と完全一致
- HEAD から当該プロパティのみを独立実装で除去した結果と**バイト単位一致**（12.1）
- `link_country_keywords.py` が削除後も import できる（`COUNTRY_BASE_META` 43件・12.3 の罠）
- `git add -A` は未使用。未追跡 spec.json 305件は最後まで未 stage

---

## 12.4 残骸ではないもの（消さない）

| ファイル | 役割 |
|---|---|
| `data/photographers-en-classification.json` | 新規ENページ生成の生きた入力 |
| `data/photographers-en-ui-terms.json` | 同上 |
| `data/en-migration-ledger.json` | 移行台帳＝バックログの正本（EN §REL 89件など）|
| `data/archive/*.json` 3本 | 凍結アーカイブ＝緊急 rollback の入力。`check_en_json_frozen()` が守る |


---

# 13. 保留中の検討事項（着手しない・Daisuke の指示待ち）

**2026-09-15 時点。どれも急ぎではない。新規6名バッチ（`docs/next-photographer-batch.md`）を
先に回してから、必要性を感じた時点で着手する。勝手に始めない。**

## 13.1 EN アーカイブ・国別の「手編集検知」ガード（★2026-09-16 実装済）

**問題**: §14 の表のとおり、この2面は**既存出力への上書き拒否ガードが無い**。
`CLAUDE.md` 絶対禁止4番（生成物の出力HTMLだけを直さない）を**規律だけで守っている**状態で、
機械的には止まらない。直したつもりの事実修正が次の再生成で黙って消える。

| サーフェス | 正本 | 上書き拒否ガード |
|---|---|---|
| EN アーカイブ `en/archive.html` | JA `archive.html` | **無し** |
| 国別 JA/EN `countries/` `en/countries/` | `data/country-pages.json` | **無し** |

**性質が今日（2026-09-15）入れた `check_classification_loss()` の EN 拡張とは違う**:
あちらは「**消える**」を止めるガード。こちらは「**直したつもりが戻る**」を止めるガード。
同じ処方箋ではない。

**考えられる打ち手**: 出力HTMLと「正本から再生成した結果」を突き合わせ、
差分があれば「生成物を直接編集した疑い」として WARN/HARD を出す
（`build_archive_en.py --dry-run` の would-change が既に近い形で存在する）。
**着手するなら、まず現状で would-change が何枚出るかを実測すること**。

### 実装（2026-09-16・Daisuke 指示「推奨案で」）
`scripts/preflight.py` の **`check_generated_surface_drift()`**。正本から再生成した結果と
実ファイルを突き合わせる（ヒューリスティックではない）。

- 対象3面と方法：`build_archive_en.py --dry-run` / `generate_country_pages.py --all --dry-run` /
  `generate_country_pages_en.py --all --dry-run` の **would-change / would-create** を読む。
- 判定は既存検査と同じ touched/untouched：
  **今回触った生成物がずれていれば HARD**（＝手編集の疑い・次の再生成で消える）、
  **触っていない分は WARN**（再生成忘れ・既存ドリフト。ブロックしない）。
- dry-run が失敗したときは「未検査」を WARN で出す（黙って素通りさせない）。

**導入時の実測**：
- 着手前のドリフトは **0枚**（EN アーカイブ1 + 国別JA 33 + 国別EN 62＝96面すべて一致）。
- 受け入れテスト3通り：①`countries/austria.html` と `en/archive.html` を手編集 → **HARD で EXIT 1**、
  ②`data/country-pages.json` だけ直して再生成を忘れた → **WARN（ブロックしない）**、
  ③正本を直して `--country austria` で再生成 → **EXIT 0**。
- preflight 実行時間 **34.3 秒 → 36.1 秒（+1.8 秒）**。

**残る選択肢（未実施・要判断）**：既存の `[EN country <slug>] / [EN archive] 生成物を直接編集した疑い`
WARN（`check_country_en` / `check_archive_en` のヒューリスティック）は、写真家追加のたびに
構造的な偽陽性を出す（§14 A-4）。今回の検査がより正確に同じ面を見るので**重複した WARN を落とせる**が、
`[EN archive]` には真陽性の前例（2026-08-31）があるため、外すかは別途判断。

## 13.2 ★正本をこれ以上 HTML へ寄せるのは「しない」で決着（2026-09-15）

「国別・EN アーカイブも HTML 正本にしたほうがいいか」を検討し、**しない**と決めた。

**判断の軸＝そのページに生成器が再現できない判断（散文）が入っているか。**
実測（カード・AI開示を除いた解説文の文字数・中央値）:

| サーフェス | 解説文 中央値 | 最大 |
|---|---:|---:|
| JA 写真家 | **7,161** | 17,786 |
| JA 年代 | 613 | 655 |
| EN 国別 | **60** | 95 |
| JA 国別 | **25** | 53 |

国別は解説文が実質ゼロ（設計どおり「解説なし・年代順」）で、中身は card-data の国籍から
機械的に導かれる写真家リスト。**再生成で失われる判断が存在しない**＝二重正本の問題が無い。
EN アーカイブも約400枚のカードの翻訳投影で、再生成こそが JA との整合を保っている。

**昇格の代償は実測済み**: EN 年代・運動の昇格で、写真家追加時のカードが手貼りになった（§14）。
同じことを国別でやると、写真家1人あたり最大4枚（JA/EN × 二重国籍）の手編集が発生し、
いま `--apply-surfaces` が1コマンドで済ませている部分が失われる。**得るものが無い。**

→ **今回の移行の本質は「JSON だから直す」ではなく「JSON に散文が溜まって二重正本に
なっていたから直す」だった。** この区別を次の設計判断でも使う。

## 13.2b 積みタスク：`renumber_eyebrow()` / `delink_missing()` の撤去（触るときに一緒に）

2026-09-16 の入口1本化で `process_ja()`（素材HTMLを素通しで公開する旧経路）を撤去した結果、
この2部品が **参照ゼロ** になった。**単独セッションは組まない。次に
`scripts/import_chatgpt_photographer.py` を触るとき一緒に落とす**（Daisuke 決定 2026-09-16）。

- `renumber_eyebrow()` … hero 眉の採番。scaffold 側が入れるので**もう要らない**。そのまま落としてよい。
- `delink_missing()` … JA 素材の「実在しないページへの内部リンク」を自動で外す部品。
  **落とす前に確認すること**＝現在この機能は生成時には働いておらず、
  `preflight.check_internal_dead_links()` が**事後**に受けている（触ったページは HARD）。
  **単純に現経路へ配線し直してはいけない**：EN ページ作成前は JA→EN の言語トグルも
  「存在しないページ」と判定され、旧経路では毎回トグルを復活させる手間が出ていた。

---

## 13.3 積み残しの未決（§9.8 から再掲）

- **JA/EN タクソノミーの hero 枚数**（JA 8ページ・EN 5ページで実カード数と不一致）を、
  手で直すか実カード数から導出するか。`sync_card_counts.py` の対象は archive とトップで、
  運動・年代は入っていない。
