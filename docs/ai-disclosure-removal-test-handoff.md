# 引き継ぎ — AI開示ブロックを全ページから外す試験（試験A）

作成 2026-10-29。**新規セッションはこれを最初に読む。** 背景は `docs/seo-index-drop-handoff.md`
（特に「★★2026-10-29 大きな訂正」「10/29 再測定」「クロールの統計情報」の節）。

---

## 1行で

**各ページ末尾の AI開示ブロックを全ページから外し、Google の表示が戻るかを2〜3か月見る。
コロフォン（`/colophon` · `/en/colophon`）の記載は残す。外すのも戻すのも正本1か所のスイッチで一括。**

Daisuke 承認済み（2026-10-29「Aをやっとこうか一旦」→ 新規セッションで実施の指示）。

---

## なぜやるのか（要点だけ）

- 本当に下がったのは**表示**（移転前 約200/日 → 現在 約54/日）。登録数（665→479）とクロール量の低下は
  移転直後の一時的な盛り上がりの終わりで、問題ではない（旧ドメインは最大で登録約130枚・クロール約10回/日だった）
- 旧ドメイン時代から実績のあったページの順位が **9/15 の Google 変動**で下がった
- 9/15 より前のサイト側の変更は **移転（8/27）と AI 開示（8/30）の2つだけ**。一括修正・新規追加はすべて 9/14 以降
- Google はコロフォンをほぼ見ていない（JA コロフォンは検出-未登録＝一度もクロールされていない、EN コロフォンはクロール済み-未登録）
  → 各ページのブロックを外せば、Google から見える「本文執筆 — AI」の記載はほぼ消える。読者向けの開示はコロフォンとフッターリンクで保たれる
- **半分だけ外す分割試験は不採用**：Google はページを読み直さずに外している（10/29 時点で新たに外れた89枚中60枚は最終クロール≤8/29）＝サイト単位の評価なので、ページ単位の比較では差が出ない

---

## 実装方針（推奨。新セッションでコードを読んで確定させる）

### 1. 正本 `scripts/ai_disclosure.py` にスイッチを1つ足す

- 例：`ENABLED = False`（コメントで「2026-10-29 試験A。戻すときは True にして inject --all」）
- `ensure(html, lang, indent)` を、`ENABLED` が False のときは **`strip_block(html)` を返す**ようにする
  （action は `'removed'` / `'unchanged'`。`'no-anchor'` は出さない）
- **理由**：`ensure()` は importer（`import_chatgpt_photographer.py:1494`）・`build_archive_en.py:544`・
  `build_taxonomy_en.py:1747/1908`・`generate_country_pages.py:915`・`generate_country_pages_en.py:509` から呼ばれている。
  ここを切り替えれば、**今後の新規追加や再生成でもブロックが勝手に戻らない**。呼び出し側は触らない
- `block()` / `_ROLES` / `_NOTE_TEXT` は残す。**`build_colophon.py` が `d._ROLES` と `d.strip_block` を使っている**（103行・120行）＝コロフォンの文面はそのまま

### 2. `scripts/inject_ai_disclosure.py`

- `ensure()` が `'removed'` を返すケースを集計に足す（`stats` のキー）
- 安全確認（`strip_block(after) != strip_block(before)` なら ABORT）はそのまま有効＝ブロック以外は1バイトも変えない
- 対象外リスト（cards-archive・colophon・design/・シム）は変えない

### 3. preflight `check_ai_disclosure()`（`scripts/preflight.py:2238`〜）

- `ENABLED` が False のときは**逆向きに検査**：ブロックが**残っている**ページを HARD（消し忘れ・再生成での復活を止める）
- コロフォンの実在・フッターのコロフォンリンク（no_link / wrong_colophon）の検査は**ENABLED に関係なく維持**（読者向け開示の導線なので）
- **安全装置の変更なので、push 前に diff を Daisuke に見せる**（feedback: ガード変更は事前報告）

### 4. 文書

- `CLAUDE.md` 禁止7と正本マトリクスの AI開示行に「2026-10-29〜 試験Aで各ページ非表示（`ENABLED=False`）。戻すときは True＋inject --all」を1行追記
- `docs/seo-index-drop-handoff.md` に開始日・コミットを記録
- `docs/importer-run-log.md` に軽量行（wall-time は Daisuke 記入）
- メモリ `project_ai_disclosure_block.md` と `project_gsc_index_drop_2026_09.md` に状態を追記

---

## 実行手順

```bash
git pull origin main
python3 scripts/inject_ai_disclosure.py --all --dry-run    # removed=約1,000 になることを確認
python3 scripts/inject_ai_disclosure.py --all
git diff --stat | tail -3                                  # 変更はブロック行の削除だけのはず
python3 scripts/generate_sitemap.py                        # lastmod を新しくして再クロールを促す
grep -c '<loc>' sitemap.xml                                # URL数が変わらないこと（いま 1,041 前後）
python3 scripts/check_content_loss.py
python3 scripts/preflight.py
```

- **sitemap の罠**：`.claude/worktrees/` の複製で URL が膨張しないか必ず数える（`reference_sitemap_generator_pitfalls`）
- 差分の確認：削除行が全部 `AI-DISCLOSURE` ブロック内か、`git diff | grep '^-' | grep -v 'ai-disclosure\|AI-DISCLOSURE\|font-size:10.5px\|font-size:11.5px\|</div>'` 等で抜き取り確認
- **IndexNow は送らない**（Bing は無傷で伸びている。約1,000URLの一斉通知で Bing 側を揺らさない。Bing は自然に再クロールする）
- **GSC の登録リクエストは送らない**（数枚だけ送っても意味が無く、比較を歪める）
- コミット例：`experiment(seo): AI開示ブロックを各ページから外す（試験A・コロフォンは維持）`

---

## 試験中のルール

- **写真家ページの一括修正をしない**（出典番号・表記統一・JSON-LD の類）。他の変化と混ざって判定できなくなる
- 新規追加は少しずつならよい（ブロックは自動で付かない）
- 書き直し試験（strand・cameron・jp-鳥居龍蔵・beato）と同時期になる＝あちらの判定は読みにくくなる前提で進める
- 積みタスク（運動ページ `/privacy`・`post-internet-photography` の JSON-LD・`cards-archive.html`）は小さいので並行してよい

---

## 判定

| 時期 | 見るもの |
|---|---|
| 12月初旬・1月初旬・2月初旬（月1回） | GSC 新旧合算の**表示/日（週平均）**とクリック、新ドメインの割合、Bing の週合計（参考） |
| **2月ごろ** | 判断。クロールは約17回/日（HTML で1日十数ページ）＝全ページ一巡に約3か月 |

- 取得：`.venv/bin/python3 scripts/seo_fetch.py --gsc-only --dry-run --window 7`、または `docs/seo-index-drop-handoff.md` の集計と同じ週次集計
- **基準（開始前）**：10/19週 表示 54/日・クリック 1.0/日・新ドメイン割合 7%。Bing 10/19週 49クリック・1,945表示
- **基準データ**：`photography history/GSC/1029/`（クロール済み-未登録 293枚・検出-未登録 243枚・新旧のクロール統計）
- **判定の目安**：表示が移転前の約200/日に向けて戻り始めれば「開示が効いていた可能性が高い」。変化が無ければ開示は主因ではない
  （比較対象が無いので Google の変動と完全には区別できない。12月前後のコアアップデートの有無を必ず確認して添える）
- 判定軸は**登録数ではなく表示とクリック**

---

## 戻し方

`scripts/ai_disclosure.py` の `ENABLED = True` → `python3 scripts/inject_ai_disclosure.py --all` → sitemap → preflight → push。
開示の最終的な扱い（戻すか、文面を変えるか）は試験の結果を見て Daisuke が決める。**Claude からは決めない。**
