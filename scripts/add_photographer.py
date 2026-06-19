#!/usr/bin/env python3
"""add_photographer.py — 新規写真家を全サーフェスへ反映する半自動ヘルパー。

設計方針（landmine 化を避けるため）:
- 「重複しやすい・取りこぼしやすいデータ投入」は自動化する：
  card-data.json（idx 自動採番）／data/photographers-supplement.js（星データ）／
  稼働中スターマップ design/toptest-assets/d369d828-...bin（星データ）。
  いずれも追記のみ・重複ガードあり・編集前バックアップあり・冪等。
- 「フォーマットが面倒な v5.1 カード HTML」は貼り付け用に**出力**する
  （archive / cards-archive / new-design / 年代 / 運動。JA/EN 両方）。
  多数の HTML を自動で書き換えるとアンカー誤爆で新たな事故になりうるため、あえて手貼り。
- 旧デザイン生成器（generate_photographer_pages.py / generate_archive_pages.py）は
  ガード済みで呼ばない。EN アーカイブは build_archive_en.py、国ページは
  generate_country_pages(_en).py を「実行コマンド」として案内する。
- 最後に preflight.py を実行して決定論チェック。

使い方:
  python3 scripts/add_photographer.py path/to/spec.json [--apply]
  --apply 無し = ドライラン（データ投入はせず、何をするか＋スニペットだけ表示）

spec.json 必須キー:
  id, nameJa, nameEn, years("1928–2019"), nationality("JP"), countryJa("日本"),
  era("1950"), channel, channelEn, artText, ledeShortJa, ledeShortEn,
  tags(JAリスト2-3), tagsEn(ENリスト2-3), movements(JAリスト),
  flag("🇯🇵"), gender("女性"/"男性"),
  starTextJa, starTextEn, citations([{num,name,url}]), links([{label,url}])
任意キー:
  style(default: pc-top--kanji), idx(指定しなければ自動採番),
  movementSlugJa(運動ページ JA ファイル名 例 "社会ドキュメンタリー"),
  movementSlugEn(例 "social-documentary"),
  channelEnUpper(運動/年代カードの channel 表示 例 "Topics in photo history · SOCIAL DOCUMENTARY")
"""
from __future__ import annotations
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CARD_DATA = REPO / "card-data.json"
SUPPLEMENT = REPO / "data/photographers-supplement.js"
STAR_BIN = REPO / "design/toptest-assets/d369d828-79e5-4719-ae51-89a0c1b743d0.bin"

REQUIRED = [
    "id", "nameJa", "nameEn", "years", "nationality", "countryJa", "era",
    "channel", "channelEn", "artText", "ledeShortJa", "ledeShortEn",
    "tags", "tagsEn", "movements", "flag", "gender",
    "starTextJa", "starTextEn", "citations", "links",
]


def fail(msg: str):
    print(f"[ERROR] {msg}")
    raise SystemExit(1)


def load_spec(path: str) -> dict:
    spec = json.loads(Path(path).read_text(encoding="utf-8"))
    missing = [k for k in REQUIRED if k not in spec or spec[k] in ("", None)]
    if missing:
        fail(f"spec に必須キーが不足: {missing}")
    spec.setdefault("style", "pc-top--kanji")
    spec.setdefault("movementSlugJa", "")
    spec.setdefault("movementSlugEn", "")
    spec.setdefault("channelEnUpper", spec["channelEn"])
    return spec


def js_existing_ids() -> set[str]:
    files = ["data/photographers.js", "data/photographers-manual-additions.js",
             "data/photographers-supplement.js"]
    src = ["(function(){ var window=this;"]
    for f in files:
        src.append((REPO / f).read_text(encoding="utf-8"))
    src.append("console.log(JSON.stringify(PHOTOGRAPHERS.map(function(p){return p&&p.id;})));")
    src.append("})();")
    proc = subprocess.run(["osascript", "-l", "JavaScript"],
                          input="\n".join(src).encode("utf-8"), capture_output=True)
    payload = proc.stderr.decode() or proc.stdout.decode()
    return {i for i in json.loads(payload) if i}


def backup(path: Path):
    bak = path.with_name(path.stem + "-backup" + path.suffix)
    shutil.copy2(path, bak)
    print(f"  backup → {bak.relative_to(REPO)}")


def insert_card_data(spec: dict, apply: bool):
    data = json.loads(CARD_DATA.read_text(encoding="utf-8"))
    if any(p.get("id") == spec["id"] for p in data["photographers"]):
        print("  card-data.json: 既に存在 → スキップ")
        return
    idx = spec.get("idx") or max(p.get("idx", 0) for p in data["photographers"]) + 1
    entry = {
        "type": "photographer", "id": spec["id"], "href": f"photographers/{spec['id']}.html",
        "idx": idx, "nameJa": spec["nameJa"], "nameEn": spec["nameEn"],
        "metaJa": f"{spec['countryJa']} · {spec['years']}", "era": spec["era"],
        "nationality": spec["nationality"], "ledeJa": spec["ledeShortJa"],
        "channel": spec["channel"], "tags": spec["tags"], "style": spec["style"],
        "artText": spec["artText"], "hintText": f"{spec['nameEn'].upper()} · {spec['years']}",
    }
    print(f"  card-data.json: 追加 idx={idx}")
    if apply:
        backup(CARD_DATA)
        data["photographers"].append(entry)
        CARD_DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def star_object_dict(spec: dict) -> dict:
    """JSON（=有効なJS）の写真家オブジェクト。supplement.js / bin の両方で使える。"""
    return {
        "id": spec["id"], "name": spec["nameEn"], "nameJa": spec["nameJa"],
        "nationality": spec["nationality"], "flag": spec["flag"], "years": spec["years"],
        "gender": spec["gender"], "era": spec["era"], "movements": spec["movements"],
        "thumbnail": "", "links": spec["links"], "amazon": "",
        "context": {"text": spec["starTextJa"], "textEn": spec["starTextEn"],
                    "citations": spec["citations"]},
    }


def has_id(s: str, pid: str) -> bool:
    # JS（id: 'x'）と JSON（"id": "x"）の両形式を検出
    return (f"id: '{pid}'" in s) or (f'"id": "{pid}"' in s)


def insert_star(spec: dict, path: Path, apply: bool):
    s = path.read_text(encoding="utf-8")
    if has_id(s, spec["id"]):
        print(f"  {path.relative_to(REPO)}: 既に存在 → スキップ")
        return
    obj = json.dumps(star_object_dict(spec), ensure_ascii=False, indent=2)
    if "PHOTOGRAPHERS.push(" in s:
        # supplement.js 形式：末尾に push() ブロックを追記
        new = s.rstrip() + "\n\nPHOTOGRAPHERS.push(\n" + obj + "\n);\n"
    else:
        # bin 形式：const PHOTOGRAPHERS = [ ... ]; の最終 `];` 直前に挿入
        m = re.search(r"\n\s*\]\s*;\s*$", s)
        if not m:
            fail(f"{path}: PHOTOGRAPHERS 配列の終端 '];' が見つからない")
        insert_at = s.rfind("}", 0, m.start()) + 1
        indented = "\n".join("  " + line for line in obj.splitlines())
        new = s[:insert_at] + ",\n" + indented + "\n" + s[insert_at:]
    print(f"  {path.relative_to(REPO)}: 星エントリ追加")
    if apply:
        backup(path)
        path.write_text(new, encoding="utf-8")


def card_html(spec: dict, lang: str, *, label: str, href_prefix: str) -> str:
    """v5.1 pc-card（年代/運動ページ用の最小形）。lang: 'ja'|'en'"""
    if lang == "ja":
        name, name2 = spec["nameJa"], spec["nameEn"]
        meta = f"{spec['countryJa']} · {spec['years']}"
        lede, channel = spec["ledeShortJa"], spec["channel"]
        tags = spec["tags"]; cta = "写真史上の位置を読む"
    else:
        name, name2 = spec["nameEn"], spec["nameJa"]
        meta = f"{spec['nationality']} · {spec['years']}"
        lede, channel = spec["ledeShortEn"], spec["channelEnUpper"]
        tags = spec["tagsEn"]; cta = "Read their place in photo history"
    tag_html = "".join(f'<span class="pc-body__tag">{t}</span>' for t in tags)
    return f'''<article class="pc-card pc-card--photographer"><a href="{href_prefix}photographers/{spec['id']}.html"><div data-nosnippet class="pc-top {spec['style']}">
      <div class="pc-top__meta"><span class="idx">{spec.get('idx','?')}</span><span>{label}</span></div>
      <div class="pc-top__art">{spec['artText']}</div>
      <div class="pc-top__hint">{spec['nameEn'].upper()} · {spec['years']}</div>
    </div><div class="pc-body"><span class="pc-body__kind">Photographer</span><div><h3 class="pc-body__name">{name}</h3><div class="pc-body__name-en">{name2}</div></div><div class="pc-body__meta">{meta}</div><p class="pc-body__lede">{lede}</p><div class="pc-body__channel">{channel}</div><div class="pc-body__tags">{tag_html}</div><div class="pc-body__cta" data-nosnippet><span>{cta}</span><span>→</span></div></div></a></article>'''


def print_snippets_and_runbook(spec: dict):
    cd = json.loads(CARD_DATA.read_text(encoding="utf-8"))
    idx = next((p["idx"] for p in cd["photographers"] if p["id"] == spec["id"]), spec.get("idx", "?"))
    spec["idx"] = idx
    print("\n" + "=" * 70)
    print("貼り付け用カード（手作業で挿入。アンカー誤爆を避けるため自動編集しない）")
    print("=" * 70)
    print("\n--- archive.html / cards-archive.html / new-design/cards-archive.html"
          " の該当年代カード群末尾へ（JA, label=PHOTOGRAPHER）---")
    print(card_html(spec, "ja", label="PHOTOGRAPHER", href_prefix=""))
    print("\n--- eras/{era}.html の年代グリッド末尾へ（JA, label=国コード, href_prefix='../'）---".format(era=spec["era"]))
    print(card_html(spec, "ja", label=spec["nationality"], href_prefix="../"))
    print("\n--- en/eras/{era}.html（EN, label=国コード, href_prefix='../'）---".format(era=spec["era"]))
    print(card_html(spec, "en", label=spec["nationality"], href_prefix="../"))
    if spec["movementSlugJa"]:
        print(f"\n--- movements/{spec['movementSlugJa']}.html（JA, label=国コード, href_prefix='../'）---")
        print(card_html(spec, "ja", label=spec["nationality"], href_prefix="../"))
        print(f"  ＋ サイドバー Photographers に "
              f'<span class="ph-side-chip"><a href="../photographers/{spec["id"]}.html">{spec["nameEn"].split()[-1]}</a></span> '
              f"を追加し、件数(Photogs/Photographers)を+1")
    if spec["movementSlugEn"]:
        print(f"\n--- en/movements/{spec['movementSlugEn']}.html（EN, label=国コード, href_prefix='../'）---")
        print(card_html(spec, "en", label=spec["nationality"], href_prefix="../"))
    print_manual_checklist(spec)
    print("\n" + "=" * 70)
    print("次に実行するコマンド（順に）")
    print("=" * 70)
    print("  # EN アーカイブを card-data.json から再生成")
    print("  python3 scripts/build_archive_en.py")
    print("  # 国ページ（nationality に該当する国 slug を指定）")
    print(f"  python3 scripts/generate_country_pages.py    # JA（card-data の nationality={spec['nationality']} から自動）")
    print("  python3 scripts/generate_country_pages_en.py  # EN")
    print("  # 新規ページの完成検査（構造・cite・JSON-LD 実体準拠）")
    print(f"  python3 scripts/check_new_photographer.py --slug {spec['id']}")
    print("  # 最後に決定論チェック（push 前ネット）")
    print("  python3 scripts/preflight.py")
    print("\n注意: generate_photographer_pages.py / generate_archive_pages.py は旧デザイン=実行禁止（ガード済み）。")


def print_manual_checklist(spec: dict):
    """データ投入では埋まらない「次に手作業で埋めるもの」を明示する。
    自動化されるのは card-data / 星データ / 貼り付けカードまで。本体ページと
    EN 正本・本文・出典は手作業。check_new_photographer.py が後で完成度を検査する。"""
    sid = spec["id"]
    print("\n" + "=" * 70)
    print("次に手作業で埋めるもの（データ投入では埋まらない）")
    print("=" * 70)
    print(f"□ photographers/{sid}.html を作成")
    print("    最善手＝参照実装 photographers/ansel-adams.html を丸ごとコピーして")
    print("    名前・本文・slug だけ差し替える（SEO一式＝canonical/hreflang/OGP/Twitter/")
    print("    description/JSON-LD(Person)/data-nosnippet/GA ＋ 本文レイアウトの型が最初から入る）。")
    print("    ※winogrand.html は『解説』1節だけの薄い型なのでコピー元にしない。")
    print(f"    ・canonical / og:url / JSON-LD url を /photographers/{sid}.html に統一")
    print(f"    ・JSON-LD は @type:Person、name/alternateName/birthDate/deathDate を {spec['nameJa']} 実体に")
    print("    ・meta description と JSON-LD 本文は捏造せず、検証済み情報だけ手書き")
    print("    ・コピー後は Adams の本文・cite・FIG・§REL・thesis を全置換し、残骸ゼロを確認（本文混入防止）")
    print("□ 本文を出典準拠で執筆（標準の型に揃える＝ansel-adams 準拠）")
    print("    § 背景と時代 → § 表現の核心（h3で主題分節）→ § 代表作・方法・媒体（h3＝作品/FIG）")
    print("    → § 批評と写真史上の位置（h3）。長さは増減してよいが節名はこの標準に揃える。")
    print("    ・本文中の実在写真家/運動を初出1回リンク化（JA=/photographers,/movements）")
    print("    ・sup-ref *N と 出典 cite-N を 1:1 対応（欠番・重複・dangling なし）")
    print("□ thesis（この写真家が変えたこと）— 断定度基準に従う（最上級表現を避ける）")
    print("□ § REL 関連する写真家・運動、§ REF さらに読む（写真集/DB）を記入")
    print(f"□ EN 正本 data/photographers-en-content.json に {sid}.html を追加")
    print(f"    body_html / thesis_html / site_directory_html を入れて")
    print(f"    python3 scripts/build_photographers_en.py --slug {sid} で生成")
    print("□ entry-meta 国名・キーワードのリンク後処理")
    print("    python3 scripts/link_country_keywords.py（実行後 git diff で巻き込み確認）")
    print("□ 各分類ページへカード手貼り（上の貼り付け用カード参照）＋件数 +1")


def main():
    args = sys.argv[1:]
    apply = "--apply" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        fail("spec.json のパスを指定してください（--apply で実投入）")
    spec = load_spec(paths[0])

    if spec["id"] in {p.get("id") for p in json.loads(CARD_DATA.read_text(encoding='utf-8'))["photographers"]} \
       or spec["id"] in js_existing_ids():
        print(f"[注意] id '{spec['id']}' は既にデータに存在します（冪等: 既存分はスキップ）")

    print(f"\n{'[APPLY]' if apply else '[DRY-RUN]'} 写真家データ投入: {spec['id']} ({spec['nameJa']})")
    insert_card_data(spec, apply)
    insert_star(spec, SUPPLEMENT, apply)
    insert_star(spec, STAR_BIN, apply)
    print_snippets_and_runbook(spec)
    if apply:
        print("\n── preflight ──")
        subprocess.run([sys.executable, str(REPO / "scripts/preflight.py")])
    else:
        print("\n（ドライラン。実投入するには --apply を付けて再実行）")


if __name__ == "__main__":
    main()
