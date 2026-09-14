# 移行後の総ざらい — 設計から始める引き継ぎ（2026-09-15 作成）

**いつ読むか:** EN写真家ページの正本HTML化（`docs/en-html-canon-migration.md`）が完了したあと、
残った宿題・残骸・**写真家ページ以外のサーフェスの正本化**をまとめて片付けるとき。

**このセッションでやること＝まず設計。** 実装はそのあと。
下の §4「未決の論点」を決めるところから始める。**§2 の実測は再検証しなくてよい。**

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

- **非推奨バナー付きで生きている旧経路**：`import_chatgpt_photographer.py` の
  `--merge-to-en` / `--update-en-json`、`reconcile_en_bodies.py`、`harvest_photographers_en.py`、
  `fix_1839_*` / `fix_1870_*` / `fix_1890_*` / `fix_eugenesmith_en.py`
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
- 手順は `sync_en_rel_annotations.py` の `emit-worklist → 翻訳 → inject-html`
  （`--apply` / `--apply-batch` は JSON 経由なので**使わない**。凍結ガードが止める）

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
