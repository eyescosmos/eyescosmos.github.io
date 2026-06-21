# importer 作り替え仕様：reshape → 役割ベース抽出 + scaffold-inject

**いつ読むか:** `scripts/import_chatgpt_photographer.py` / `scripts/build_photographers_en.py` /
`scripts/add_photographer.py` を、ChatGPT素材からの写真家ページ生成フローとして作り替えるとき。

**前提メモ:** `memory/project_first_real_importer_run_hosokura.md`（2026-06-21 川内倫子＋細倉真弓を
現行フローで通した実測。本仕様の動機と実フォーマットの一次ソース）。

---

## 0. 背景と方針
写真家追加は、ChatGPTが「サイト風の見た目のHTML」で出した素材を取り込む。**この見た目は
Daisuke が校正で読みやすいためだけのもので、サイト構造に合わせる必要はない**
（CLAUDE.md「渡されたHTMLの構造・サイドバー・節構成は流用せず中身だけ抽出」）。

現 `import_chatgpt_photographer.py` は **ChatGPTのHTMLを残したまま、その場で軽く正規化する**
（in-place reshape）。器が標準に近いと速いが、独自構造だと手直しが出る。これは方針(=器を捨てる)と
実装(=その場修正)がズレている。

**作り替えの根本:** 正典のコンテンツ抽出器が無く、JA reshape も EN組立(Step3b) も毎回抽出を
再発明していること。**役割ベース抽出器を1つ作り、JAは scaffold へ inject、ENは同じ抽出結果から
JSON生成**する。これで素材の §マーカー名・サイドバー型・head属性順は「最初から見ない」。

補強の根拠（reshape→scaffold を先にやる理由）:
- **EN builder は JA の HTML 構造に依存する**（`build_photographers_en.py` は JA を読んで英訳を差し込む）。
  JA が常に正典になれば、§マーカー不一致・サイドバー不一致由来のENバグも同時に消える
  （実例: 細倉で JA `§READ` のせいで EN「さらに読む」が日本語のまま残った）。

---

## 1. 中核アーキテクチャ：3部品 + 共有中間表現
```
素材HTML(JA) ─extract_bundle()→ ContentBundle(ja) ─render_ja_page()──→ photographers/<slug>.html
素材HTML(EN) ─extract_bundle()→ ContentBundle(en) ─bundle_to_en_entry()→ data/photographers-en-content.json
                                                                          └build_photographers_en.py→ en/...
```
- **`extract_bundle(html) -> ContentBundle`** … 役割ベース抽出器（JA/EN共用・キーストーン）
- **`render_ja_page(bundle, idx) -> str`** … scaffold + inject（JA正本HTML生成）
- **`bundle_to_en_entry(bundle) -> dict`** … en-content.json の page エントリ生成（= Step3b）

抽出器は「構造変換器」ではなく「素材から正本候補フィールドを取り出す器」。素材の outer layout /
sidebar / nav / §マーカー名 / head属性順は**読まない・信用しない**。

---

## 2. ContentBundle スキーマ（中間表現）
JA素材とEN素材は別ファイル。各抽出は単一言語。`source_lang` を持たせ、検証を言語別に分ける
（`required_fields_for("ja")` / `required_fields_for("en")`）。

```python
{
  "source_lang": "ja" | "en",
  "slug": str, "idx": int|None,
  "name_ja": str, "name_en": str,
  "years": str, "birth_year": str, "death_year": str|None,
  "country_ja": str, "country_slug": str,
  "era": str, "period_label": str,            # "2010 — 2020s"
  "movement_label": str, "movement_slugs": [str],
  "channel": str|None,
  "keywords": [str],
  "title": str, "meta_description": str,
  "lead_inner_html": str,                     # ph-abstract <p> の中身
  "thesis_inner_html": str,                   # ph-thesis__body の中身（<em>可）
  "works": [{"label": str, "url": str}],
  "sections": [{"title": str, "blocks_html": str}],   # essay中身（<h3>/<p>列・節数可変）
  "related_people":    [{"slug": str|None, "name": str, "reason": str}],
  "related_movements": [{"slug": str|None, "name": str, "reason": str}],
  "further_books": [{"title_html": str, "meta": str, "note": str,
                     "cta_label": str, "cta_url": str}],
  "further_links": [{"label": str, "url": str}],
  "sources": [{"num": int, "anchor_html": str}],      # <a ...>title</a>
  "_confidence": {field: float}, "_unresolved": [str]
}
```

### 中断ライン（一次抽出で取れなければ abort・空埋め禁止）
`name_ja` / `name_en` / `years` / `lead` / `thesis` / `sections >= 1` / `sources >= 1`。
見出し語fallbackで取れた場合も、**初期実装では自動生成せず preview に出して人間確認**。

---

## 3. 部品A：役割ベース抽出器 `extract_bundle`
### 3.1 一次シグナル = 内側クラス（§マーカー名は見ない）
| 役割 | 一次セレクタ |
|---|---|
| lead | `.ph-abstract` 内 `<p>` |
| thesis | `.ph-thesis__body`（無ければ `.ph-thesis` 内 `<p>`） |
| essay節 | `section.ph-section` で本文 `.essay` を持つもの。`.essay` 内 `<h3>`/`<p>` を blocks_html に |
| works | `.ph-works-links a.chip-link`（label, href） |
| related | `.ph-rel-list li`（`.ph-rel-movements` は movements 側）。`<a>`→slug+name、`— ` 以降→reason、リンク無し→slug=None |
| further(books) | `.ph-book`（title/meta/note/cta） |
| further(links) | `.ph-further-links li a` |
| sources | `.ph-cite`（id=cite-N、内 `<a>`） |
| keywords | `.ph-kw` テキスト |
| name/years | `.ph-hero__name` / `.ph-hero__en` / `.ph-hero__years` |
| meta系 | `.ph-entry-meta`（Country/Period/Movement のリンク・値）/ `<title>` / `meta[name=description]` |

### 3.2 二次フォールバック（confidence付き・自動採用しない）
一次が空のときのみ見出しテキストで領域推定：Sources/出典/References、Related/関連、Works/作品、
Books/Further reading/さらに読む、Lead/Summary/導入、Thesis/この写真家が変えたこと。
- 二次は原則 **review バケット行き**。低confidenceは中断 or review。**推測でsectionを作らない**。

### 3.3 インナーマークアップ寛容性（今回の実バグ対策・必須）
- `ph-cite__num` は `<div>` でも `<span>` でも可。アンカーは `<div>`/`<span>`/二重 `<span><span>`
  ネストいずれでも **最初の `<a href>...</a>` を1つ抜く**。
- de-link 済み（プレーンテキスト化）人物は related で `slug=None` として保持。
- **既知バグ監査必須**：現 `extract_en_candidate_fields()` は `ph-cite` 在りでも `sources_html=None`
  を返すケースがある（細倉EN）。原因特定して修正してから一次採用する。

### 3.4 fail-loud契約
必須（2の中断ライン）が取れなければ中断。取れなかった任意ブロックは preview/checklist に列挙。

---

## 4. 部品B：JA scaffold-inject `render_ja_page`
### 4.1 scaffold が供給する固定枠（素材から取らない）
`add_photographer.py --scaffold`（= ansel-adams コピー + 機械確定フィールド）の出力を**土台に使う**
（scaffold を再実装しない＝head/SEO/JSON-LD/data-nosnippet の取りこぼし事故回避）。固定枠：
- head：GA / canonical / hreflang / OG / twitter / JSON-LD / data-nosnippet、**属性順は標準(name/property/rel先頭)**
- chrome：ヘッダー・言語トグル・ナビ・フッター・検索スクリプト（id は `-<slug>` 接尾辞）
- サイドバー骨格：`Entry · 写真家データ` / `Keywords · キーワード` / `Works · 作品リンク` / `Navigate · 移動`
- 節骨格：`§ WORKS` / essay / `§ REL` / `§ REF` / `§ SRC`（**マーカーは常に正典**）

### 4.2 inject する可変部
- hero：name_ja / name_en / years / eyebrow `§ <idx> — Photographer Index — <movement_label>`
- entry-meta & サイドバーEntry：country(リンク) / years / period(リンク) / movement / category / updated
- **essay は固定テンプレに押し込まない。bundle.sections から §NN/NN + TOC を生成**（節数可変。
  `build_photographers_en.py` の `build_sections_and_toc` 相当を流用）
- WORKS / REL / REF / SRC：bundle から生成。works_note は**サイト定数**で固定。
- 本文内リンク：name→slug マップ（card-data の nameJa）で本文初出を実在slugでリンク化（下記E）。

### 4.3 essay生成の helper 方針
builder内 `build_sections_and_toc` を無理に import して密結合しない。**まず importer 側に最小実装**し、
**同じ出力になることをスナップショットテスト**。安定後に共通 helper へ切り出す。

---

## 5. 部品C：builder ガード（空埋め防止 = Milestone 1）
`build_photographers_en.py` の `rebuild_hero`：`en_h1 = page.get('h1','')` が空のまま hero を空にする
事故（細倉EN）を hard error 化。**スコープ必須**（下記A）。

---

## 6. 部品D：head属性順の暫定修正
scaffold-inject が即landしないなら、現 in-place importer に「head の meta/link を name/property/rel
先頭へ並べ替える」関数を入れるストップギャップ。scaffold-inject 完成後は不要（捨て石）。

---

## 7. 部品E（Step3b）：`bundle_to_en_entry`（抽出器が安定してから）
EN bundle を en-content.json の page dict に写す。**付録A の変換を内蔵**：
- sources → `cite-item` 形式（必須）／related → `site-directory-links` nav 形式
- lead → `<p class="lead">…</p>`／thesis → inner のみ（label は builder が強制）
- `h1`/`years` 必須セット／further_reading verbatim／未訳語は `photographers-en-ui-terms.json` に追記
- **完全機械生成一本化はしない**。通常ページは機械生成、HAND_MAINTAINED は手編集維持。
- 仕上げ `build_photographers_en.py --slug X --force`（関連差替で content-loss ガードが止まるため）。

---

## 8. 部品F：カード面自動化（最後・今は手貼り維持）
- v1：現状維持（貼付HTML + 挿入位置ヒント）
- v2：`--plan-surfaces`（どのファイルのどのアンカー前後に何件、を dry-run表示）
- v3：`--apply-surfaces`（対象ファイル・anchor・件数を厳密assert→1件ずつ編集、失敗時無書込、
  `git diff --name-only` が想定面だけかassert、運動ページは件数+1 + サイドバーchipも）

---

## 9. 実装に入る前に固定する5点（今回の実データ由来・踏むと痛い）
- **A. Milestone 1 のスコープ**：hard error は「sections>=1 の実コンテンツページなのに h1 空」だけ。
  **stub / missing_en_true / sections無し は対象外**。years は `--all` 回帰で既存に空欄があれば
  warning に格下げ可（h1 は必ず hard error）。既存293の `--all --dry-run` が同集合のままであること。
- **B. Milestone 4 の合格条件**：「器を捨てた」証明は**構造が違う2ソースを食わせ chrome/SEO/§構成/
  サイドバーが byte 同一・差分は中身だけ**。固定具は**細倉の元素材**（§IMAGE LINKS・Profile型サイドバー）。
  「川内が通った」だけでは証明にならない。
- **C. scaffold 再実装禁止**：`render_ja_page` は `--scaffold` 出力を土台にし、空essay置換＋
  WORKS/REL/REF/SRC inject のみ。
- **D. idx 依存の順序**：eyebrow `§ <idx>` と Entry No. に idx が要る。新規は card-data 未登録なので
  **importer に `--idx` 必須 or 先に add_photographer で採番**、を運用確定。
- **E. 本文内リンクを render に内蔵**：素材の slug違い de-link（daido-moriyama→moriyama 等）の手貼り直しを
  恒久解決。`extract_bundle` は related の slug=None だけ保持し、本文リンクは render が name→slug で解決。

---

## 10. マイルストーン（合意順・1セッション=1コミット）
```
1. build_photographers_en.py: h1/years hard error（スコープA付き）
2. extract_bundle() 実装（class-primary + heading-fallback(review) + インナー寛容）
3. render_ja_page() scaffold-inject 実装（essay可変生成・本文リンクE）
4. 実案件1件で検証（合格条件B：2つの汚いソースで chrome byte一致）
5. bundle_to_en_entry() = Step3b（HAND_MAINTAINED維持）
6. surface plan/apply 自動化（v2→v3）
```
Step3b を先にやると in-place reshape 由来の揺れを JSON注入側で吸収し始め責務が混ざる。
**JA scaffold-inject で「器を完全に無視できる」ことを先に証明する。**

---

## 11. 受け入れ基準（全体）
- ChatGPT素材の §マーカー名・サイドバー型・head属性順を変えても、生成JAページの chrome/SEO/§構成が標準で一定。
- `check_new_photographer.py --slug X` OK（cite整合・JSON-LD実体・canonical/og/description）。
- `build_photographers_en.py --slug X --dry-run` が **SKIPしない**（CLAUDE.md要件）。EN本文にサイドバーnav以外の日本語残存なし。
- `check_content_loss.py` OK、`preflight.py` OK、`git diff --name-only` が想定面のみ。
- 必須欠落時に黙って空ページを作らず中断する。

---

## 付録A：`build_photographers_en.py` が消費するキーと正フォーマット（実測）
| key | 必須 | フォーマット / 注意 |
|---|---|---|
| `h1`,`years` | ✅ | 無いと hero 写真家名が空（builder は `page.get('h1','')`） |
| `lead_html` | ✅ | `<p class="lead">…</p>`（二重 `<p>` 注意） |
| `thesis_html` | ✅ | **inner のみ**。label は builder が `What this photographer changed` を強制 |
| `sections` | ✅ | `[{title, body_html:"<div class=\"essay\">…<h3>…<p>…</div>"}]`。builderが §NN/TOC再構築（節数可変OK） |
| `sources_html` | ✅ | **`<div class="cite-item" id="cite-N"><div class="cite-num">*N</div>{anchor}</div>` のみ parse**。`ph-cite`形式だと §SRC空＋**全sup-refがプレーン化**（fix_orphan_suprefs） |
| `site_directory_html` | ✅(REL) | `<nav class="site-directory-links">` + label `Related people &amp; photographers` / `Related movements` + `<div class="site-directory-items"><a/></div>`。§RELはリンクのみ（reasonは落ちる仕様） |
| `further_reading_html` | △ | §REF本文を verbatim（`ph-book`+`ph-further-links`）。**JA側が `§ REF` マーカーでないと発火しない**。Amazon CTAでない本は `photobooks_html` でなくこちら |
| `keywords_html` | △ | `ph-keywords`/`ph-kw` passthrough |
| `title/meta_description/og/twitter/canonical/hreflang/has_ga` | △ | 既存slugは構造再利用しテキスト差替 |
| 未訳語 | — | `data/photographers-en-ui-terms.json` の `terms`/`works_labels`/`channels`/`fixed`/`countries` に追記（durable） |

## 付録B：JA正典の節マーカー
`§ WORKS` → essay `§ NN / NN` → `§ REL`(関連する写真家・運動) → `§ REF`(さらに読む) → `§ SRC`(出典)。

## 付録C：JA head の属性順
meta/link は `name` / `property` / `rel` 先頭（例 `<meta name="description" content="…">`、
`<link rel="canonical" href="…">`）。ChatGPT素材は bs4 直列化で `content` 先頭になることがあり、
builder が `name="viewport"` 等を見つけられず **EN ビルドが "no viewport meta" で失敗**、
`check_new_photographer` も canonical/og/description を absent 誤検出する。

## 付録D：既存資産
- `add_photographer.py --scaffold`：ansel-adams コピーの空骨格（`render_ja_page` の土台）
- 旧セッションの `_assemble_en_entry.py`（消去済・再現可）：付録Aの変換（ph-cite→cite-item／
  related→nav／lead・thesis包み／h1・years／further_reading）を既に実装＝`bundle_to_en_entry` の試作
- 現 `import_chatgpt_photographer.py` の `extract_en_candidate_fields()`：Family B(ph-*)抽出の現行版。
  sources取りこぼしバグ（付録3.3）の監査対象

## 付録E：Codex/Daisuke との合意済み判断
- ContentBundle は JA/EN 共通中間表現。`source_lang` + 言語別必須検証で分ける。
- `build_sections_and_toc` は密結合importせず、importer最小実装＋同出力テスト→安定後に共通化。
- 二次フォールバックは review バケット行き。初期は自動生成しない。
- Step3b は scaffold-inject 安定後。en-content.json は機械生成一本化せず HAND_MAINTAINED 併存。
- カード面自動化は最後。いきなりHTML編集せず `--plan-surfaces` から。
