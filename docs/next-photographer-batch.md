# 次の写真家バッチ — 新規6名（移行後の初回検証を兼ねる）

**作成 2026-09-15。着手セッションはこのファイルを最初に読む。**
Daisuke 決定＝**次の写真家作業は新規6名**。移行（EN正本HTML化・総ざらい・残骸撤去）は
完了・push 済みなので、**残っているのは実素材での初回検証だけ**。それをこのバッチで兼ねる。

## 0. このバッチの位置づけ — ★新規追加は本番未検証

移行後の importer 経路は **fixture（`ed-ruscha` をコピーして slug 置換したもの）でしか
通していない**。update の経路は移行中に何度も通っているが、**新規追加は一度も実素材で
通っていない**。今回は6名とも新規なので、**全員が未検証の経路**に乗る。

→ **`docs/en-html-canon-migration.md` §13.10 の B（新規1名を追加する場合・9項目）を
パイロット1名で必ず回す。** 通れば §13.10 の初回扱いは終了し、以降は通常運用でよい。

## 1. 型 — パイロット1名 → 監査 → 残り5名一括

崩さない。過去のバッチで、パイロット段階で写真集19冊脱落・og:image 脱落を
全員波及前に捕捉した実績がある（[[feedback_batch_photographer_updates]]）。

**★時間とクレジットの見積もりは保守的に。** これまでのバッチ実測（9名30分・11名50分・
14名48分）は**ほぼ全部 update**。新規追加は全サーフェス投入があるぶん1名あたりが上がり、
update6＋新規1の7名バッチで 5.6分/名 だった。**6名全部が新規のバッチは前例が無い。**
0909・0910 と2回連続で ChatGPT のクレジット上限に当たっているので、
**途中成果が常に検証済みで残る形**で進める（パイロット→監査→残り、で区切る）。

## 2. 着手前の検分（素材を受け取ったらすぐ・ページを触る前）

| # | 見るもの | 落ちると何が起きるか |
|---|---|---|
| 1 | 素材12本（JA6＋EN6）が**同じ生成元・同じ形式**か | 混ざるとバッチの利点が消える |
| 2 | 各素材に **`§ 01` マーカー**があるか（grep） | 無いと本文が **65〜81% 落ちる**。ガード検知なし |
| 3 | **生没年**が入っているか | 空欄・年代文字列のまま通さない。**無ければ自分で調べて入れる** |
| 4 | デュオ写真家が居るか | **名前の並びと生年の対応**を1件裏取りする（既存慣習＝名前順＝生年順） |
| 5 | **フランス国籍**が居るか | `FRANCE_EXPECTED_IDS` ガードで必ず止まる。迂回せず**定数に1件追加**が正規手順 |

表記揺れは**素材側で担保**する方針（Daisuke 決定 2026-09-11）。importer は直さない。
受け取り時に grep して、崩れていれば**差し戻す**。

## 3. 入口 — 新規は JA も EN もこれから

```bash
python3 scripts/import_chatgpt_photographer.py --slug <slug> --ja JA.html --en EN.html --apply
```

JA→EN の順に両方できる。**EN 出力先が既に存在すれば `--force` でも拒否される。**
（`--render-en` は「JA は既にある・EN だけ足す」ときの入口。今回は使わない）

## 4. パイロットで回す検証（§13.10 B・9項目）

着手前に1回:
```bash
find en/photographers -name '*.html' | sort | xargs shasum -a 256 > /tmp/en-before.sha256
find photographers    -name '*.html' | sort | xargs shasum -a 256 > /tmp/ja-before.sha256
python3 scripts/preflight.py > /tmp/preflight-before.txt 2>&1
```

項目は `docs/en-html-canon-migration.md` §13.10 の B 表を見る（9項目・ここでは再掲しない。
再掲すると両方がドリフトする）。要点だけ:
- `--apply` **なし**で先に実行して EXIT 0 を確認
- `[render-en]` 行が `dangling=0` / `works-cjk=0` / `ga=2`、`sec` が素材の節数と一致
- warnings の `head fallback fired` が **0件**
- `en_html_sync.py verify <slug>` が **10項目すべて OK**
- `check_new_photographer.py --slug <slug>` に `en_missing` が出ない

## 5. 全サーフェス投入（新規はここが本体）

経路マップは [[playbook_add_photographer_everywhere]]。**年代・国は必須**で
`check_taxonomy_presence()` が HARD で止める。**運動は載せるか毎回判断**。

- `--apply-surfaces` が件数表示を持つ従属面を自動再生成する（JAカード4面の手貼りは不要）
- **★EN 年代ページへのカード手貼りは手作業**。`build_taxonomy_en.py` は既存ページを
  `🛑 REFUSED` で拒否するので再生成できない。忘れると `check_taxonomy_presence()` が HARD
- **カードのリード文は新規追加時だけ短縮版を作る**（既存233件のズレは直さない）
- **スターマップは `data/*.js` を読まない**。星を足すなら bin 3本の `PHOTOGRAPHERS` 配列
- **二重登録しない**（`photographers.js` と `supplement.js` の両方に入れない）

## 6. ついでに片付けるもの（フェーズ7バックログ）

専用セッションは組まない方針なので、**該当ページを触るついでに直す**。

- 6名の EN §REL に一言解説を入れる（台帳 `data/en-migration-ledger.json` の
  `_meta.findings.en_rel_blurb_missing` が正本。現在 **89件 / 22ページ**）

## 7. 測る（Required）

`docs/importer-run-log.md` に記録する。客観項目は作業側、wall-time は Daisuke。

**★このバッチはトークン測定も兼ねる。** Codex 出力量規律の効果測定はベースラインが
**0909 の6名セッション＝46,462 トークン/名**。今回も6名なので**同条件で比較できる**
（0910 は5名 40,752 で名数が違い、比較が濁っていた）。正本は
`docs/importer-scaffold-inject-spec.md` §14 A-1b。

## 8. push 前

`CLAUDE.md`「push 前チェック」のとおり。新規追加は公開HTMLが**増える**ので、
残骸撤去のときのような「sha256 全件一致」は条件にならない。**増えた分が意図どおりか**を見る。
push 後は IndexNow を1本（[[playbook_indexnow_submit]]）。

## 9. このバッチが終わってから考えること（先にやらない）

`docs/post-migration-cleanup-plan.md` **§13** に保留2件を置いてある。

- **EN アーカイブ・国別の「手編集検知」ガード**（未着手・Daisuke の指示待ち）。
  この2面は上書き拒否ガードが無く、絶対禁止4番を規律だけで守っている。
  **今日入れた消失検知とは別問題**（あちらは「消える」、こちらは「直したつもりが戻る」）
- **国別・EN アーカイブを HTML 正本へ昇格するかは「しない」で決着済み**（再提案しない）

---

**関連**: `docs/importer-scaffold-inject-spec.md` §14（キックオフ定型・最初のプロンプトに入れる）／
`docs/en-html-canon-migration.md` §13.10（初回検証の本体）／
`docs/photographer-leaf-spec.md`（本文構造）／`.claude/skills/write-photographer-section`
