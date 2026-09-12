# SEO 選定ツール 設計図 — Photo Coordinates

作成 2026-09-10。ChatGPT 版「SEO Rank Watch」を、このサイトの実測結果に合わせて再設計したもの。

---

## 0. これは何か / これは何ではないか

**これは選定ツールである。** GSC と Bing Webmaster Tools の実測から、次に本文を厚くすべき
写真家を月1回名指しし、そのページがどんなクエリで検索されているかを添えて出す。

**これは編集ツールではない。** ページを一切書き換えない。title も meta も内部リンクも触らない。
出力は名簿とレポートだけ。実装は既存の写真家バッチ update 工程が行う。

この分離が設計の中心。理由は §1 と §9。

---

## 1. 前提 — 実測で確定している事実

この設計はすべて以下の実測に依存している。ここが覆れば設計も変わる。

| 事実 | 出典 | 設計への影響 |
|---|---|---|
| title / meta 改善はクリック増に寄与しない | 2026-08-14 の28日フル再検証 | メタ情報の自動改善を**やらない** |
| 効いたのは写真家ページ本文のバッチ更新のみ | 同上。yuki-tawada 0→14クリック等 | 出力を**本文更新の名簿**にする |
| Google は全セッションの 23.6% | GA4 2026-08-14 | GSC 単独を基準にせず **BWT を併用** |
| Bing 5.25 クリック/日 > Google 4.46 クリック/日 | BWT 実データ 2026-08-22 | 同上 |
| 本番ドメインは eyescosmos.com | 2026-08-27 移行完了 | github.io は使わない |
| ページ平均順位はクエリ構成変化で汚染される | 2026-08-14 | 順位単独で判定**しない** |
| EN の CTR 評価は原理的に不可 | 同上 | EN は impressions と clicks のみで見る |
| 同質素材のバッチは 9名30分、単体は 13〜22分 | 2026-07-13 実測 | 名簿は**1名ではなく10名**単位 |

JA 写真家ページは HTML 自身が正本で手編集できる。再生成は走らない。EN は正本 JSON 経由で
1コマンド。つまり**編集の手間は障害ではない**。障害は「371枚のどこから手をつけるか決められないこと」。
このツールはそこだけを引き受ける。

---

## 2. 全体像

```
  [月1回・自動]
  Google Search Console API ─┐
                             ├─→ scripts/seo_fetch.py ─→ data/seo/snapshots/*.json
  Bing Webmaster Tools API ──┘                                    │
                                                                  ↓
                                                       scripts/seo_select.py
                                                                  │
                              ┌───────────────────────────────────┤
                              ↓                                   ↓
                  data/seo/report-YYYY-MM-DD.md      data/seo/selection-log.json
                  （人が読む。名簿＋クエリ＋依頼文）      （機械可読。判定の材料）
                              │
  [手動]                      ↓
                  Daisuke がレビュー・名簿を確定
                              ↓
                  ChatGPT で10名分の素材を作成
                              ↓
                  Claude にバッチ update を依頼（既存 §14 フロー）
                              ↓
                  preflight → push → IndexNow
                              ↓
                  selection-log に actionDate を記録
                              ↓
                  28日後、次回の自動実行で判定が出る
```

---

## 3. データ取得 — `scripts/seo_fetch.py`

### 3.1 Google Search Console

- API: Search Console API v1 `searchanalytics.query`
- 認証: サービスアカウント。GSC のプロパティ設定で、サービスアカウントのメールアドレスを
  ユーザーとして追加する。OAuth より自動実行に向く。
- **新旧どちらのプロパティにも追加する。** 旧 `eyescosmos.github.io` は移行後も数字が入り続けており
  （2026-09-08 時点で表示回数146）、API から引けば CSV より細かい移行前データが取れる。
- 依存: `google-api-python-client`, `google-auth`。`.venv/` は gitignore 済み。
- 取得軸: `dimensions=["page","query"]`、`rowLimit=25000`、ページング対応
- `siteUrl`: **新旧2本を毎回取得して合算する。** 片方だけでは実態が見えない。
  - `https://eyescosmos.com/`（URL プレフィックス。§11-1 参照）
  - `https://eyescosmos.github.io/`（旧。移行後も露出が続いている）

  2026-09-11 の実測（2026-08-12〜09-08 の28日窓）:

  | プロパティ | クリック | 表示 | 平均順位 |
  |---|---|---|---|
  | eyescosmos.com | 58 | 5211 | 20.7 |
  | eyescosmos.github.io | 65 | 5182 | 12.6 |

  旧のほうがクリックが多い。合算しないと候補選定を誤る。
  合算時は URL のホスト名を剥がしてパスで突き合わせる（`/photographers/xxx.html`）。
  旧はパスが percent-encoded のことがあるので `unquote` してから突き合わせる。
- 認証確認済み 2026-09-11。サービスアカウント `seo-reader@eyescosmos-seo.iam.gserviceaccount.com`、
  両プロパティに `siteRestrictedUser` で登録済み。鍵は `~/.config/eyescosmos-seo/gsc-service-account.json`（600）。
  venv は リポジトリ直下 `.venv/`（gitignore 済）。`google-api-python-client` + `google-auth`。
- 期間: 直近28日窓。バックフィルできるのは **2026-08-26 以降のみ**。新プロパティにそれ以前のデータがない。
  2026-09-10 時点の実測: 8/26〜9/7 の13日間でクリック54回、1日あたり約4.2回。
  インデックス登録済み741ページ、未登録117ページ。
- JA と EN はページ URL のプレフィックスで分ける。`/en/` を含むものが EN。

### 3.2 Bing Webmaster Tools

- API: `https://ssl.bing.com/webmaster/api.svc/json/` の `GetQueryStats` / `GetPageStats` /
  `GetPageQueryStats`。API キーを GET パラメータで渡すだけ。認証は GSC より単純。
- **制約を明記しておく。** BWT API は GSC のような任意期間の query×page 集計を提供しない。
  取得できるのは直近の集計と、ページ単位のクエリ内訳。したがって BWT は
  **補助シグナル**として扱い、主軸は GSC に置く。Bing だけで伸びているページの検出に使う。
- 前期比較は、こちらで毎回スナップショットを取り続けることで自前に作る。

### 3.3 認証情報の置き場

リポジトリの外に置く。コミットしない。

```
~/.config/eyescosmos-seo/gsc-service-account.json
~/.config/eyescosmos-seo/bwt-api-key.txt
```

`.gitignore` に `data/seo/*.local.*` を追加して二重の保険をかける。

### 3.4 保存形式

**このリポジトリには置かない。** `eyescosmos.github.io` は GitHub Pages の公開リポジトリなので、
コミットすると検索クエリのデータがそのまま公開される（2026-09-11 に Daisuke 判断で非公開に決定）。

置き場は、すでに GA4 / GSC / BWT のエクスポート置き場として使われている以下の配下に統一する。

```
~/Desktop/claude code/photography history/seo-watch/
├── snapshots/gsc-YYYY-MM-DD.json      追記専用。既存ファイルを書き換えない
├── snapshots/bwt-YYYY-MM-DD.json      同上
├── reports/report-YYYY-MM-DD.md       人が読むレポート
└── selection-log.json                 選定と判定の履歴
```

Git 管理はしない。append-only のスナップショットに履歴管理の価値は薄く、
必要なのは公開しないことだけだったため。
**バックアップは Time Machine / iCloud 任せ。**BWT のデータは再取得できないので、
バックアップが効いていないことが分かったら非公開リポジトリへ移す。

念のため、メインリポジトリの `.gitignore` に `data/seo/` を追加して事故を防ぐ。

---

## 4. 選定ロジック — `scripts/seo_select.py`

### 4.1 集計単位

**写真家1名につき1枠**。JA と EN は別々に評価するが、名簿では統合する。素材は共通で作れるため。
写真家ページ以外は選定対象にしない。国別・年代・運動ページは参考数値としてレポート末尾に出すだけ。

### 4.2 層

| 層 | 条件 | 意味 |
|---|---|---|
| A 順位余地 | position 5〜20 かつ impressions28d ≥ 20 | 評価はされている。厚くすれば上がる |
| B 露出あり流入なし | impressions28d ≥ 30 かつ clicks28d ≤ 1 | 出ているが選ばれていない |
| C 評価開始 | impressions が前期比 +100% 以上 かつ ≥ 15 | Google が拾い始めた |
| D Bing 先行 | BWT impressions ≥ 30 かつ GSC impressions < 10 | Google 側の掘り起こし余地 |

**閾値はすべて暫定。** Phase 1 の実データを見てから較正する。導出根拠のある数字ではない。
閾値は設定ファイルに切り出して、コードを触らずに変えられるようにする。

### 4.3 除外

- 直近56日以内に本文を update 済み。効果判定の期間中のため
- position 1〜3 かつ CTR が同サイト中央値以上。十分取れている
- EN の shim ページ。`jp-` 漢字 id の対応シムは実体がない
- 前回の名簿に載って未着手のもの。二重に出さず、繰越として別枠に出す

### 4.4 出力枠

既定10名。候補が足りなければ**足りないまま出す**。無理に埋めない。0名なら判定レポートだけ出す。

---

## 5. 効果判定

`selection-log.json` の `actionDate` から28日経過したものを判定する。

- 比較: 更新前28日窓 と 更新後28日窓 の impressions / clicks / position
- 判定: `positive` / `neutral` / `negative`
- **断定しない。** 「改善が確認できる」までにとどめ、「改善した」と書かない

**判定の限界を明記しておく。** 1ページあたりのクリックは1桁のことが多く、個人単位の判定は
ノイズに埋もれる。したがって判定は次の2段で読む。

1. **バッチ単位**が主。10名合計の impressions と clicks が動いたか
2. **個人単位**は参考。0→14 のような明確な立ち上がりだけを拾う

同じ層で3バッチ連続 neutral なら、その層の選定条件そのものを疑う。

---

## 6. 出力

### 6.1 レポート `data/seo/report-YYYY-MM-DD.md`

人が読む。以下の順で書く。

1. **判定** — 28日経過したバッチの結果。バッチ合計と個別
2. **変化** — 前期から大きく動いた page × query
3. **名簿** — 今回選んだ10名。各人につき次を書く
   - slug、層、JA / EN の数値
   - 上位クエリ5件
   - 選定理由を1文
   - **そのクエリから読み取れる検索ニーズを1〜2文**
   - **ChatGPT へ渡す素材依頼文の下書き**
4. **繰越** — 前回の名簿で未着手のもの
5. **参考** — 写真家以外のページの数値

3 の検索ニーズと依頼文は機械では書けない。スクリプトはクエリと数値まで出し、
言語化はスケジュールタスクで起動した私が行う。ここが唯一の判断部分。

### 6.2 履歴 `data/seo/selection-log.json`

```json
{
  "batches": [
    {
      "batchId": "2026-10-01",
      "selectedAt": "2026-10-01",
      "actionDate": null,
      "reviewDueDate": null,
      "verdict": null,
      "members": [
        {
          "slug": "alec-soth",
          "tier": "A",
          "ja": { "position": 7.4, "impressions": 210, "clicks": 5 },
          "en": { "impressions": 34, "clicks": 0 },
          "topQueries": ["アレック・ソス 作風", "alec soth sleeping by the mississippi"],
          "needs": "作風と代表作の特徴を短時間で把握したい層",
          "status": "selected"
        }
      ]
    }
  ]
}
```

`actionDate` は update を push した日に手で入れる。ここが判定の起点になる。

---

## 7. 運用ワークフロー

| # | 誰が | 何を | 頻度 |
|---|---|---|---|
| 1 | 自動 | `seo_fetch.py` でスナップショット取得 | 月1回 |
| 2 | 自動 | `seo_select.py` で名簿と判定を生成 | 月1回 |
| 3 | 自動（Claude） | クエリから検索ニーズを言語化、素材依頼文を下書き | 月1回 |
| 4 | Daisuke | レポートを見て名簿を確定。外したい人を外す | 月1回 |
| 5 | Daisuke | ChatGPT で10名分の素材を作成 | 月1回 |
| 6 | Claude | バッチ update。既存の §14 キックオフ定型 | 月1回 |
| 7 | Claude | preflight → push → IndexNow | 同上 |
| 8 | Claude | `selection-log.json` に `actionDate` を記録 | 同上 |
| 9 | 自動 | 28日後の実行で判定が出る | 翌々月 |

4 以降は現行の運用と変わらない。増えるのは 1 から 3 と 8 だけ。

---

## 8. 自動実行

macOS のスケジュールタスクとして登録する。

- 実行日: **毎月10日 09:00 JST（`0 9 10 * *`）**（2026-09-12 変更。当初は毎月1日）
- 実行内容: `seo_fetch.py` → `seo_select.py` → レポートの言語化 → 結果を Daisuke に通知
- 制約: この Mac が起動している必要がある
- クラウド実行にはしない。リポジトリと認証情報がローカルにあるため

**10日にした理由**: update の push はバッチ作業の都合で月の中旬になる。0911バッチの
`actionDate` は 2026-09-12 で、28日窓が閉じるのは 2026-10-10。月初に置くと 10/01 の実行では
判定が出ず、11/01 まで待つことになる（push から50日）。10日に置けば「update を push した
翌月の10日に判定が出る」リズムで揃う。

薄いスキルを `.claude/skills/seo-selector/` に置き、スケジュールタスクからそれを呼ぶ。
スキルが持つのは §6.1 の 3 の言語化ルールだけ。計算はすべてスクリプト側。

### 代替案 — GitHub Actions（2026-09-10 時点では採用しない）

Mac の起動もアプリの起動も不要にしたい場合、GitHub Actions で `seo_fetch.py` と
`seo_select.py` を回し、レポートをコミットする構成に移せる。言語化だけは Claude が必要なので、
コミットされたレポートを Daisuke が任意のタイミングで読ませる形になる。

**採用しない理由**: Daisuke が日常的に Mac と Claude を開くため、取りこぼしのリスクが低い。
Bing のデータだけは遡れないので、数ヶ月アプリを開かない期間が発生したら、
このときに収集だけ Actions へ移す。

移す場合の判断材料: このリポジトリは Pages のユーザーサイトで公開されている。
認証情報を Secrets に置くか、収集用の非公開リポジトリを分けるかを先に決める必要がある。
漏洩時の影響は、GSC のサービスアカウントは読み取りのみ、BWT の API キーは URL 送信が可能。

---

## 9. ガードレール

- **ページを編集しない。** 名簿と提案のみ。これが既存ガードと衝突しないための最重要条件
- title / meta / OGP の一括改善を提案しない。効果なしと決着済み
- Google SERP を独自スクレイピングしない
- 認証情報を出力・コミットしない
- `data/seo/snapshots/` の既存ファイルを書き換えない。追記のみ
- 順位を固定順位として扱わない。GSC の average position は平均値
- 効果を予測で断定しない
- 候補がなければ少なく出す。無理に埋めない
- 新規ページの自動生成をしない。提案として記録するのみ
- JA と EN を混同しない。片方の結論を他方へ機械的に持ち込まない

---

## 10. 実装フェーズ

**進捗 2026-09-11**: Phase 0 と Phase 1 完了。`scripts/seo_fetch.py` が動作確認済みで、
スナップショット7本を取得済み（当日分1本＋バックフィル6本、2026-03-31 まで遡及）。

**★スケジュールを前倒しできる。** バックフィルで28日窓が6本そろったため、
「データがたまるまで待つ」理由が消えた。当初の 10-01 較正 / 11-01 本運用は前倒し可能。

| Phase | 内容 | 担当 | 目安 |
|---|---|---|---|
| 0 | GSC サービスアカウント作成、プロパティへ追加、BWT API キー発行 | Daisuke | 30分 |
| 1 | `seo_fetch.py`。手動実行でデータが取れることを確認。過去16ヶ月をバックフィル | Claude | 実装1回 |
| 2 | 実データを見て §4.2 の閾値を較正 | Claude + Daisuke | 較正1回 |
| 3 | `seo_select.py`、レポート生成、`selection-log.json` | Claude | 実装1回 |
| 4 | スキルとスケジュールタスクを登録 | Claude | 短時間 |
| 5 | 1バッチ実走。28日後に判定が出ることを確認 | 両方 | 1サイクル |

Phase 2 を飛ばさない。閾値を実データなしで固定すると、名簿が的外れになったときに
ツールの問題か選定条件の問題か切り分けられなくなる。

---

## 11. 着手前に決めること

1. ~~GSC プロパティの種類と URL~~ → **決定済み 2026-09-10。URL プレフィックス、`https://eyescosmos.com/`**。
   GSC の URL が `resource_id=https://eyescosmos.com/` になっていることで確認した。
   ドメインプロパティなら `sc-domain:eyescosmos.com` になる。API の `siteUrl` にはこの文字列をそのまま渡す。
   URL プレフィックスなので www 有無と http は別プロパティ扱いになるが、サイトは https 非 www 統一なので影響しない
2. **サービスアカウント方式でよいか**。自動実行には必要だが、GSC 側でユーザー追加が要る
3. **BWT API キーを発行するか**。Bing を主軸の一つにするなら必要
4. **1回の名簿人数**。既定10名
5. **除外の冷却期間**。既定56日

---

## 参照

- データ置き場: `~/Desktop/claude code/photography history/seo-watch/`（非公開・Git 管理外）
- 移行前 GSC の CSV 退避: `~/Desktop/claude code/photography history/GSC/ドメイン移行前過去分/`
  実データは 2026-03-31 以降のみ。粒度は日別合計とクエリ別合計まで。query×page×date は入っていない
- 既存のバッチ update フロー: `docs/importer-scaffold-inject-spec.md` §14
- 実測の記録先: `docs/importer-run-log.md`
- push 前チェックとガード: `docs/generators-and-guards.md`
- IndexNow 送信: `scripts/indexnow_submit.py`
