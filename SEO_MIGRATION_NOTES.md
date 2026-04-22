# SEO 強化テンプレート（写真家ページ向け）

Stieglitz (JA/EN) を基準テンプレートとして、残りの写真家ページに同じ構造を順次適用する。
完了したらこのファイルは削除してよい。

## テンプレート参照
- `photographers/stieglitz.html`
- `en/photographers/stieglitz.html`

## ★2 見出し構造の統一（優先度 高／回帰修正）

現状、一部ページで本文 essay セクションから `<h2>` が剥奪され、
`<span style="color: var(--accent)">経歴</span>` のような装飾 span のみで
区切られている（SEO・アクセシビリティ両面でマイナス）。

修正方針:
- 1つの essay div を「経歴／表現解説／批評と受容」の3つの `<section class="section">` に分割
- 各セクションに `<h2>` を付与
- 各段落を `<p>...</p>` で包む（`<br><br>` 区切りは使わない）

EN の見出しは `Biography / Expression / Criticism and Reception` を基準に。

検出コマンド:
```
grep -l 'span style="color: var(--accent)">経歴' photographers/*.html
grep -l 'span style="color: var(--accent)">Biography' en/photographers/*.html
```

## ★3 Person JSON-LD に `sameAs` を追加（優先度 高）

Google Knowledge Graph にエンティティとして認識されやすくする。
各写真家ごとに次の ID を調べて sameAs 配列に入れる。

最低限入れたい項目:
- Wikipedia EN URL
- Wikipedia JA URL（該当ページがある場合のみ）
- Wikidata Q 番号（Wikipedia 記事左サイドバー「Wikidata item」）
- VIAF ID（Wikidata の "VIAF cluster ID" から）
- Getty ULAN（Getty Museum の Artists ページにあれば）

Stieglitz の記述例（`photographers/stieglitz.html` 末尾 Person JSON-LD を参照）:
```json
"sameAs": [
  "https://en.wikipedia.org/wiki/Alfred_Stieglitz",
  "https://ja.wikipedia.org/wiki/...",
  "https://www.wikidata.org/wiki/Q313055",
  "https://viaf.org/viaf/49231990",
  "https://www.getty.edu/art/collection/person/103KH0"
]
```

**重要:** ID は推測しない。必ず Wikidata で実際の ID を確認してから記述すること
（誤 ID はエンティティ同定を壊す）。

## ★4 BreadcrumbList JSON-LD を追加（優先度 中）

Person JSON-LD の直後に独立した `<script type="application/ld+json">` ブロックとして追加。
JA/EN でパスを切り替える。

JA テンプレ:
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "写真の座標", "item": "https://eyescosmos.github.io/"},
    {"@type": "ListItem", "position": 2, "name": "写真家一覧", "item": "https://eyescosmos.github.io/archive.html"},
    {"@type": "ListItem", "position": 3, "name": "<写真家名>"}
  ]
}
```

EN テンプレ:
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Photo Coordinates", "item": "https://eyescosmos.github.io/en/"},
    {"@type": "ListItem", "position": 2, "name": "Photographers", "item": "https://eyescosmos.github.io/en/archive.html"},
    {"@type": "ListItem", "position": 3, "name": "<Photographer Name>"}
  ]
}
```

## 未着手（ユーザー確認待ち）

- ★1 `og:image`: OGP 画像アセットが未整備。SNS プレビュー改善には PNG/JPG
  （1200×630推奨、SVG は Twitter 非対応）が必要。サイト共通の既定画像を1枚
  作ったうえで全ページに追加するのが最小コスト。
- ★5 hero image + alt: 各写真家にパブリックドメイン肖像画像を挿入。画像探索＋
  ライセンス確認の手間が大きいため方針決定が先。
- ★6 Article スキーマ併置、★7 リード文差別化: テンプレ適用優先。

## 全ページ展開の進め方（提案）

1. ★2 h2 復旧を最優先（現状3ページしか回帰していないが、今後同パターンで
   壊される可能性があるので検出 grep を CI か事前チェックに入れたい）。
2. ★3 ★4 は JSON-LD 追加のみなので、次のような流れで10〜20ページ単位で
   バッチ化するのが現実的:
   - Wikidata/VIAF ID を一括調査（CSV でまとめる）
   - 小さな Python/Node スクリプトで JSON-LD を差し込む
   - 差し込み後に `python3 -m json.tool` で各ブロックを検証
3. 作業は **必ずコミット単位を小さく**（写真家20人ぶんごと等）。
   競合回避のため `git pull --rebase` を毎回実行。

## 検証スニペット

全写真家ページの JSON-LD を一括検証:
```python
import re, json, glob
for path in glob.glob("photographers/*.html") + glob.glob("en/photographers/*.html"):
    html = open(path).read()
    for i, block in enumerate(re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)):
        try:
            json.loads(block.strip())
        except Exception as e:
            print(f"{path} block {i+1}: {e}")
```
