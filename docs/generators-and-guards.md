# ジェネレータ・機械チェック（門番）・EN生成フロー・テンプレ移行

**いつ読むか:** スクリプト（ジェネレータ／ビルダー）を実行するとき、EN 写真家ページを
編集するとき、機械チェックの意味を知りたいとき、テンプレ差し替え・デザイン移行をするとき。

---

## `scripts/generate_photographer_pages.py` は実行禁止 — 旧デザインで現行と乖離 — CRITICAL

**絶対に `python3 scripts/generate_photographer_pages.py` を実行しないこと。**

**理由（2026-06-13 確認）:** 現行の日本語写真家ページは v5.1 新デザイン
（`<header class="head">` ＋ `head__lang` トグル ＋ `<section class="ph-hero">`）に
移行済み。一方この旧ジェネレータは**別物の旧デザイン**（`lang-toggle`/`lang-btn`・
`title-block`・`lead-abstract`・`facts` テーブル等）を生成する。つまりジェネレータの
出力は現行ページと一致しない。

**実行した場合に起きること:**
- 294枚すべての JA 写真家ページの**デザインが旧版に巻き戻る**
- 修正済みの JA→EN 言語トグル（`<a href="/en/photographers/…"><button>EN</button></a>`）が
  消え、無反応の `<button>EN</button>` に戻る
- `ph-hero` ヒーロー・現行ヘッダー・モバイル検索などの新要素が消失する

**現在の正（source of truth）:**
- 日本語写真家ページの**構造・デザイン・ヘッダー・言語トグルは `photographers/*.html` 自身**
  （JA HTML が正）。構造・本文・解説・出典・関連欄の修正は HTML を直接編集する。
- EN 写真家本文の正本は `data/photographers-en-content.json`。
  `data/photographer-essay-overrides.js` の `textEn` に同じ文が残る場合は、事実修正時に両方をそろえる。
- 英語ページは `scripts/build_photographers_en.py` が JA HTML を入力に再生成する
  （この EN ビルダーは現行デザインを生成するので実行してよい）。

**言語トグルが再び壊れていないかの確認:**
```bash
# JA 側に無反応の素の EN ボタンが無いこと（0 件であるべき）
grep -l '<button>EN</button>' photographers/*.html movements/*.html eras/*.html
# 再発時の冪等修正
python3 scripts/fix_ja_lang_toggle.py --apply   # countries は除外・EN実在を検証
```

旧ジェネレータを現行デザイン用に作り直す場合は、Daisuke の明示依頼があったときのみ着手し、
着手前に本注意書きを更新すること。

## `scripts/generate_archive_pages.py` も実行禁止 — 旧デザイン生成 — CRITICAL

`generate_archive_pages.py` は旧デザイン（`<div class="photographer-card">` ＋ `toggleDetail()`）を
出力する。現行の `archive.html` / `en/archive.html` は v5.1 の `<article class="pc-card">`
（**JA archive.html が正本・手編集**、**EN は `scripts/build_archive_en.py`** が card-data.json から
pc-card を翻訳生成）。`generate_archive_pages.py` を実行すると v5.1 アーカイブを旧デザインへ
巻き戻す。2026-06-16 に `main()` 冒頭へ物理ガードを追加済み（解除は環境変数
`ALLOW_LEGACY_ARCHIVE_GEN=1`、generate_photographer_pages.py は `ALLOW_LEGACY_PHOTOGRAPHER_GEN=1`）。

---

## フルリビルド・ガード — 無指定実行は拒否 — CRITICAL — 2026-06-21 追加

**問題（2026-06-21）:** 写真家追加作業で `build_taxonomy_en.py` を無指定（フルリビルド）
実行し、en/eras 全11・en/movements 全31・en/countries 複数を巻き込み **43ファイルを手で
revert** した。EN 分類ページは正本 JSON より HTML が本文リッチなケースがあり、フルリビルドは
手編集を JSON 由来へ巻き戻す（＝静かに劣化させる）。

**対策:** 広範囲生成スクリプト3本に**スコープフラグを必須化**した。無指定実行は
**非0終了・1ファイルも書かず・有効な実行例を表示して拒否**する。typo の era/slug/country は
既知テーブル／registry と照合して拒否し、全生成へ化けない。

| スクリプト | フルリビルド | ターゲット（通常運用） |
|---|---|---|
| `scripts/build_taxonomy_en.py` | `--all` | `--era 2010` / `--slug street-photography`（各複数可） |
| `scripts/generate_country_pages.py`（JA） | `--all` | `--country japan`（複数可。`--only` は旧別名・残置） |
| `scripts/generate_country_pages_en.py`（EN） | `--all` | `--country japan`（対象1ページのみ・複合スタブ非関与） |

- `--all` の出力は**旧（無指定）フルリビルドと同一コードパス＝byte 完全一致**（挙動は変えていない
  ＝invocation のゲートと targeting だけ追加）。**注意: これは「コミット済み HTML との diff がゼロ」を
  意味しない。** 生成器の現在の出力とコミット済み HTML は元から完全一致していない箇所が残っている
  （EN 分類ページは正本 JSON より HTML が本文リッチ等）。だから `--all` を回すと既存差分が顕在化する。
  ガードが保証するのは「`--all` がフラグ追加前と同じものを出す」ことだけ。
- targeted は**対象ページだけ再生成**（変わる**ファイル数**は `git diff --stat` で1件＝巻き込みゼロを確認できる）。
  ただし**その1ファイルの中身には差分が出る**（言語ボタン・`data-country`・lede 等、生成器出力とコミット済み
  HTML のドリフト分）。これは正常。push 前に当該ページの diff を必ず目視し、内容・出典・SEO の消失が
  無いことを確認する。
- `build_archive_en.py` は単一ファイル出力なので対象外（ガード不要）。

### 写真家1人追加時の安全な生成コマンド集

`add_photographer.py` の末尾ランブックも、この targeted 形を案内する（nationality コードから
該当単国 slug を `data/country-pages.json` で解決して印字。複合国籍は両単国ページ分を印字）。
手で打つ場合の型：

```bash
# 1) EN アーカイブ（card-data.json から・単一ファイル出力）
python3 scripts/build_archive_en.py

# 2) 国ページ（この写真家が載る単国 slug だけ。複合国籍は両方指定）
python3 scripts/generate_country_pages.py    --country <slug> [--country <slug2>]   # JA
python3 scripts/generate_country_pages_en.py --country <slug> [--country <slug2>]   # EN

# 3) 年代ページ（その写真家の era だけ）
python3 scripts/build_taxonomy_en.py --era <YYYY>

# 4) 運動ページ（関係する運動 slug だけ。複数可）
python3 scripts/build_taxonomy_en.py --slug <movement-slug>

# 5) 完成検査 → 決定論チェック
python3 scripts/check_new_photographer.py --slug <id>
python3 scripts/preflight.py
```

**原則：写真家1人の追加で `--all` は不要。** 触るのは「その写真家が載るページ」だけ。
`--all` を使うのは、テンプレ・共通CSS・builder ロジック・正本JSONを横断的に変えて
全ページを意図的に作り直すときに限る（その場合も push 前に `git diff` で巻き込みを精査）。

---

## ChatGPT 素材インポータ（JA 整形 + EN 断片抽出）— 2026-06-21 追加

`scripts/import_chatgpt_photographer.py` — ChatGPT 生成の写真家 HTML 素材を、**機械的に
確定できる整形だけ**自動化して `photographers/<slug>.html` を作る半自動ツール（v1・独立・
preflight/フック非連動）。前回（森村+小林）で push まで4時間超かかった統合作業のうち、
決定論部分を機械化するのが目的。

```bash
# dry-run（既定・何も書かない。検証結果と差分サマリ・チェックリストを表示）
python3 scripts/import_chatgpt_photographer.py --slug <slug> --ja SRC.html [--en SRCEN.html]
# 実書き込み（既存は --force 必須・自動 backup）
python3 scripts/import_chatgpt_photographer.py --slug <slug> --ja SRC.html --en SRCEN.html --apply [--force]
```

- **書き込みは `photographers/<slug>.html` のみ**。EN 素材を渡すと著者コンテンツの**プレビュー
  断片**を `outputs/import-preview/<slug>.en-content-entry.json` に出力する（**正本
  `data/photographers-en-content.json` には触れない**＝v2 で注入予定）。`outputs/` は .gitignore 済み。
- **card-data / archive / 年代 / 国 / 運動 / 星マップ / EN 正本 JSON には触れない**（既存の
  `add_photographer.py` と各ビルダーへ委譲＝blast radius を限定）。末尾に follow-up コマンドを印字。
- 決定論変換: ① `<span class="rev2〜6">` の unwrap（ネスト対応）② `edit-red` クラストークン除去
  ③ レビュー用 CSS（`.edit-red`/`.revN` ルール・`/* revision preview */`）除去 ④ hero 眉
  `§ NNN` を card-data の idx（未登録は max+1 提案）へ採番 ⑤ 内部 `.html` リンクの実ファイル
  存在チェックで **dangling を自動 de-link**（`/colophon` 等の拡張子なしルートは対象外＝残す）。
  EN は加えてリンクを `/en/` 化＋運動 slug 変換し、EN 実在しないものを de-link。
- 自己検証: span 開閉バランス・rev/edit-red/レビューCSS の残存ゼロを assert（破れば中断）。
- **自動化しない編集判断**（サイドバー標準化・§MORE→§REF 統合・実在しない人物/運動の項目削除・
  thesis 断定度・JSON-LD 等の実体置換）は**レビューチェックリストとして印字**する。
- fixture 検証は**ゼロ diff 前提ではない**: 出荷済み `yasumasa-morimura`(134)・`kenta-cobayashi`(286)
  で決定論部分の再現を確認済み（残差は上記の編集判断＋些末な記号正規化）。

---

## 機械チェック（地雷の門番）— 文章ルールより優先 — 2026-06-16 追加

CLAUDE.md の多くのルールは過去の事故の再発防止。重要なものは機械チェックへ移管済み：
- **`scripts/preflight.py`** — 決定論的な不変条件を検査（写真家id重複：
  photographers.js と supplement.js への二重登録／card-data.json 重複／GA(googletagmanager)欠落）。
  既存 `check_*.py` は WARN 表示のみ。`python3 scripts/preflight.py`。
- **`.githooks/pre-push`**（`git config core.hooksPath .githooks`）— push 前に preflight を自動実行し
  FAIL ならブロック。緊急回避は `git push --no-verify`。
  **新規クローン・別マシン（Codex 等）では、まず `bash scripts/setup_hooks.sh` を一度実行**して
  フックを有効化すること（core.hooksPath はローカル設定でリポジトリに同梱されないため、これを実行する
  までフックは無効）。これは git 側の仕組みなので、エージェントが CLAUDE.md を読むかに依存しない。
- **`scripts/en_entry.py <slug>` / `scripts/check_en_entry.py <slug>`** — EN 写真家ページの slug 単位の
  読む導線・検査導線（読み取り専用）。slug は通称可（`atget`→`eugene-atget`）。共通解決は
  `scripts/en_content.py`。`check_en_entry.py --all` で全 297 件検査（既存不具合は WARN/FAIL で可視化）。
- **preflight の EN ガード（push 時に実効）** — baseline（`origin/main` 等）と比較し、触れた EN slug
  （`data/photographers-en-content.json` の差分 ∪ `en/photographers/*.html` の差分）について：
  - **本文・出典・thesis・リンクの消失**＝HARD（push ブロック）
  - **EN HTML が JSON 宣言と乖離（再生成漏れ・生成物の直接編集）**＝HARD
  - **生成物の EN HTML を直接編集した疑い**（HTML 変更なのに JSON 不変）＝WARN
  - sup/cite・リンクの健全性＝WARN。手書き維持ページ（`annie-leibovitz` / `stieglitz`）は closure 例外。
  既存不具合 10 件は「触った時だけ」可視化され、無関係な push はブロックしない（スコープが baseline）。
- **preflight の EN ガード（写真家以外・2026-06-19 追加）** — 同じ baseline 比較で、触れた
  国別 / 年代・運動 / アーカイブ EN ページにも軽量保護をかける。**正本 JSON のエントリ内容消失＝HARD**
  （国別=`data/country-pages.json` の lead/nameEn/nameJa/codes、年代・運動=`data/taxonomy-en-content.json`
  の meta.title/description・sections、アーカイブ=`card-data.json` のカード数・id・nameEn/nameJa/href）、
  **生成物 EN HTML の直接編集疑い（HTML 変更なのに正本 JSON 不変）＝WARN**。本文が builder 直書きにも
  ある混在構造（taxonomy）は「JSON が確実に失った」ことだけを HARD にし、closure（再生成漏れ）の HARD は
  写真家のみ。per-slug リーダは追加していない。
- **本文消失ガードをブロック経路へ昇格（2026-06-19 追加）** — `scripts/check_content_loss.py` を
  preflight が共通 baseline・`--strict` で実行し取り込む。**写真家リーフ（JA + EN）の明確な本文消失
  （出典 cite / 本文セクション / FIG / thesis / lead の減少）＝HARD**、**構造不変のまま文面だけ変化した
  「書き換えの疑い」＝WARN（ブロックしない）**。これまで push 手順書の手動実行頼みだった JA 写真家 HTML
  （正本）の本文消失が、pre-push で自動ブロックされるようになった。触ったファイルだけが対象＝無関係な
  push はグリーン。`check_content_loss.py` 単体実行（任意 ref と比較）も従来どおり可能。
- **SEO / 不可視必須要素の消失ガード（2026-06-19 追加）** — `check_seo_invisible_loss()` が触った公開 HTML
  （GA と同じ範囲）を baseline 比較し、**baseline にあった canonical / JSON-LD / title / meta description /
  data-nosnippet が消失、または hreflang が減った場合＝HARD**。OGP・Twitter の減少・data-nosnippet の部分減・
  新規ページのコア要素欠落＝WARN。元から無いページ・新規ページはブロックしない（段階導入）。stub / backup /
  google確認ファイルは対象外。「既存の SEO/スニペット対策が作業で消える事故」を止めるのが目的（既存穴の全修正は別案件）。
- **JA 分類ページの本文消失ガード（2026-06-19 追加）** — `check_ja_classification_loss()` が触った
  `archive.html` / `eras/*` / `movements/*`（HTML が正本）を baseline 比較し、**`<main>` 領域消失・`<h1>` 消失・
  `pc-card` 数の減少＝HARD**、section 数・リンク数の大幅減・data-nosnippet 減＝WARN。国別は JSON 正本のため
  今回は対象外。軽量 HTML メトリクスで明確な消失だけを拾い、文言変更だけでは鳴らない。
- **JA 写真家ページの SEO 穴検知 WARN（2026-06-19 追加）** — `check_ja_seo_holes()` が触った
  `photographers/*.html` を baseline 比較し、**canonical / OGP / data-nosnippet / hreflang / meta description /
  JSON-LD が「元から無い（付け忘れ・新規ページ）」場合に WARN**。上の消失ガードは「baseline にあったものが
  消えた」検知だが、こちらは「最初から欠けている」検知で役割が違う。**WARN 専用・push は絶対にブロックしない・
  触ったページだけ対象**（無関係な push は鳴らない）。hreflang は noindex ページと EN 不在ページを除外。
  本文だけ修正する場合は、そのページに既に SEO 一式があれば鳴らない（既存 295 ページは全項目あり）。
  - **新規 JA 写真家ページを作るときの最善手：参照実装 `photographers/ansel-adams.html` を丸ごと
    コピーして名前・本文だけ差し替える**。これで canonical/hreflang/OGP/description/JSON-LD/nosnippet/GA が
    最初から入り、かつ**本文レイアウトの正の型**（ABSTRACT → thesis → § WORKS 作品を見る →
    § 背景と時代 → § 表現の核心 → § 代表作・方法・媒体 → § 批評と写真史上の位置 → § REL → § REF → § SRC）
    も最初から入る。ゼロから組むと GA 欠落＝HARD ブロック、残り6項目＝上記 WARN になる。
    （winogrand.html は本文が「解説」1節だけの薄い型なのでコピー元にしない。）
    **コピー後は本文・cite・FIG・§REL・thesis・JSON-LD の実体値（name/生没年/sameAs）を
    すべて新写真家へ全置換し、Adams 残骸が1つも残っていないことを確認する**（本文混入バグ防止）。
  - **既存 JA ページの SEO 穴の冪等フィクサー：`python3 scripts/fill_seo_tags.py --apply`**
    （無指定は dry-run）。canonical/hreflang/nosnippet/OGP/twitter を本文・出典を触らずサージカルに補う。
    **ただし meta description 本文と JSON-LD は生成しない（捏造回避）**。この2つは完成済みページからの
    コピーか手書きで入れる。実行後は `git diff` で対象外混入を確認。
- **`scripts/add_photographer.py` ＋ `scripts/photographer-spec.example.json`** — 新規写真家を
  card-data.json／supplement.js／スターマップ bin へ重複ガード付きで投入し、v5.1 カードの
  貼り付け用 HTML と実行コマンドを出力する半自動ヘルパー。**末尾に「次に手作業で埋めるもの」
  チェックリスト（ページ作成／本文・thesis・§REL・cite／EN 正本 JSON／リンク後処理）を出す**ので、
  それに従えば 1 パスで作れる。
  - **`--scaffold`（`python3 scripts/add_photographer.py <spec.json> --apply --scaffold`）**：
    参照実装 `ansel-adams.html` をコピーし、**機械的に確定できる項目だけ**（slug / canonical /
    hreflang / og:url / JSON-LD Person.url / title / h1 / hero名 / name / 生没年 / 国 / era）を置換した
    **安全な空骨格ページ**を `photographers/<id>.html` に生成する。本文・thesis・出典・cite・FIG・
    description 本文・JSON-LD description は**生成しない（捏造回避）**。Adams 由来の本文・cite・§REL・
    書誌は残らない（hero+main+aside を空骨格に作り替える）。**既存ページは上書きしない**。生成後に
    `check_new_photographer.py --slug <id>` を自動実行し、未記入箇所を WARN 表示する。手コピー時の
    slug 置換ミス・残骸消し残しを無くすのが目的。あとは要素を流し込むだけ。
- **`scripts/check_new_photographer.py --slug <slug>`** — 新規／触った写真家ページの**完成検査**
  （構造健全さ＋決定論 cite 整合＋JSON-LD 実体準拠＝JA は Person を要求＋**本文レイアウトの型**
  ＝背景と時代/表現の核心/代表作・方法・媒体/批評と写真史上の位置 に揃っているかの soft ナッジ）。
  slug は通称可。`--strict-new` で不足を一部 HARD 化、`--all` で全ページ可視化。
  `check_photographer_link_integrity.py` とは非重複（曖昧判定は持ち込まない）。preflight にも
  touched-only で軽量統合済み（明確な破損だけ HARD・完成度不足/本文型は WARN・本文型は preflight
  非表示）。**新規ページを作ったら必ずこれを通す**。
- 旧デザイン生成器2本（写真家・アーカイブ）は実行されると物理ガードで中断する（上記）。

### EN 写真家ページ編集の必須フロー — スキップ禁止
1. `python3 scripts/en_entry.py <slug>` — 対象 slug の EN 正本を確認
2. `data/photographers-en-content.json` を修正（**EN HTML を直接編集しない。生成物**）
3. `python3 scripts/build_photographers_en.py --slug <slug>` で EN HTML 再生成
   （`--force` は消失ガードを外すので常用しない。誤発火時のみ）
4. `python3 scripts/check_en_entry.py <slug>` — 対象 slug を検査
5. `python3 scripts/preflight.py` → push（pre-push でも自動実行）

---

## Content storage — CRITICAL
- JA 写真家ページ `photographers/*.html` は HTML 自身が正本。本文・解説・thesis・§REL・出典は HTML を直接編集する。
- EN 写真家ページ `en/photographers/*.html` は出力物。本文系を直接編集してはならない。正本は `data/photographers-en-content.json`。
- EN の本文は `body_html`、thesis は `thesis_html`、§REL は `site_directory_html` に入れてから `scripts/build_photographers_en.py --slug <slug>` で再生成する。
- EN の事実修正は、必要に応じて `data/photographer-essay-overrides.js` の `textEn` も同じ内容にそろえる。

## 手書き追加が再生成で消えないためのルール — CRITICAL

**どこに手書きすれば消えないか（正本の場所）:**

| ページ種別 | 正本（手書きしてよい場所） | 再生成で消えるか |
|---|---|---|
| JA 写真家ページ `photographers/*.html` | **HTML 自身**（JA ジェネレータは実行禁止＋物理ガード） | 消えない |
| EN 写真家ページ `en/photographers/*.html` | **`data/photographer-essay-overrides.js`… ではなく** EN は `data/photographers-en-content.json`（`thesis_html` / `site_directory_html` 等） | **JSON に無いものは `build_photographers_en.py` で消える** |

- **EN 写真家ページの本文系（thesis「この写真家が変えたこと」/ §REL 関連写真家・運動 など）を
  HTML に直接手書きしてはならない。** 必ず `data/photographers-en-content.json` の該当キー
  （`thesis_html` は英訳本文、`site_directory_html` は `Related people` / `Related movements` の
  contextual グループ）に入れてから `build_photographers_en.py` で再生成する。
  JA 由来の §REL とミラーさせたいときは JSON の `site_directory_html` を JA §REL から作り直す
  （実例：`scripts/fix_1839_en_thesis_related.py`）。
- **安全装置（2026-06-16 追加）:** `build_photographers_en.py` は、上書きしようとしている EN ページの
  手書き thesis / §REL リンクが新出力に再現されない（＝消える）と検知したら、**そのページだけ
  上書きせずスキップし `🛑 SKIPPED … would delete:` と表示する**。黙って消えることはない。
  - 表示が出たら：手書き内容を `photographers-en-content.json` に入れてから再実行する。
  - 意図的に消す場合のみ `--force`。
  - この門番は手書き維持ページ（`stieglitz` / `annie-leibovitz` の EN 等）が `--all` で
    巻き込まれて消えるのも自然に防ぐ。
- **JA 写真家ページは HTML 直接編集が正**。手書き thesis/関連欄はそのまま永続する
  （旧ジェネレータを `ALLOW_LEGACY_PHOTOGRAPHER_GEN=1` で無理に動かさない限り消えない）。

---

## ページ移行・テンプレート差し替え時の必須要素 — CRITICAL

**過去に発生した問題：** 2026-06-08 の v5.1 全ページ移行（コミット 8ab5c9569）で、
新テンプレートに GA タグが含まれておらず、日本語の写真家285・運動31・年代11・
トップ・アーカイブの計測が約3日間止まった（2026-06-11 のコミット 33353c879 で復旧）。

**ルール：デザイン移行・テンプレート差し替え・ページの新版置き換えを行うときは、
見た目のHTMLだけでなく、以下の「不可視の必須要素」を新ページに引き継ぐこと。**

### 引き継ぎ必須要素チェックリスト

1. **Google Analytics**（gtag、ID: `G-2VRTV8BZEJ`）— 全公開ページに必須
2. **meta description / canonical / hreflang（ja・en・x-default）/ OG / Twitter カード**
3. **`<html lang="...">`** の言語属性
4. **data-nosnippet**（UIクローム：ヘッダー・タブ・ツールバー・フィルター・件数表示・
   フッター、カードの pc-top と pc-body__cta）
5. **構造化データ（JSON-LD）** — 旧ページにあった場合
6. `google739a609ca0f00aca.html`（サイト所有権確認ファイル）は削除・変更しない

### 移行後の検証（push 前に必須）

```bash
# GAカバレッジ一覧（リダイレクトスタブとGoogle確認ファイル以外は全数一致すること）
for d in . photographers movements eras countries en en/photographers en/countries en/movements en/eras; do
  tot=$(ls $d/*.html 2>/dev/null | wc -l); has=$(grep -l googletagmanager $d/*.html 2>/dev/null | wc -l);
  echo "$d: $tot total / $has with-GA"; done

# GA欠落の自動補完（冪等。GA済み・リダイレクトスタブ・バックアップ・en/・new-design/ は自動スキップ）
python3 scripts/insert_ga_tags.py
```

- 旧ページと新ページの `<head>` を diff し、消えるメタタグを一つずつ「消してよい」と
  確認できるまで push しない
- GA が不要なのは：リダイレクトスタブ（`noindex` + `http-equiv="refresh"` を両方持つ
  転送専用ページ）、`*-backup.html`、Google 確認ファイルのみ。
  **noindex だけのフルページ（例: fabian-marti, gabriel-orozco）には GA を入れる**
  （noindex は検索除外であって計測除外ではない）
- アーカイブ英語版は `scripts/build_archive_en.py` が SEO メタの日→英変換を含むため、
  日本語 archive.html に必須要素を入れてから再生成すれば英語側にも引き継がれる
