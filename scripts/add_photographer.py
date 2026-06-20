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
  python3 scripts/add_photographer.py path/to/spec.json [--apply] [--scaffold]
  --apply 無し = ドライラン（データ投入はせず、何をするか＋スニペットだけ表示）
  --scaffold  = 参照実装 ansel-adams.html をコピーし、機械的に確定できる項目だけ置換した
                「安全な空骨格ページ」を photographers/<id>.html に生成する。本文・thesis・
                出典・description は生成しない（捏造回避）。既存ページは上書きしない。
                --apply と併用で書き出し（--scaffold 単独はドライラン）。生成後 check_new_photographer
                を自動実行して未記入箇所を WARN 表示する。

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
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CARD_DATA = REPO / "card-data.json"
SUPPLEMENT = REPO / "data/photographers-supplement.js"
STAR_BIN = REPO / "design/toptest-assets/d369d828-79e5-4719-ae51-89a0c1b743d0.bin"
# scaffold のコピー元は参照実装で固定（winogrand は薄い型なので使わない）
SCAFFOLD_BASE = REPO / "photographers/ansel-adams.html"
SITE = "https://eyescosmos.github.io"

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


# ── 安全な空骨格 scaffold（ansel-adams をコピー → 機械確定項目だけ置換 → 本文は空）──
# 重要: 本文・批評・description本文・JSON-LD description・cite・FIG・作品解説・関連欄本文は
# 生成しない（捏造回避）。Adams 由来の本文/cite/REL/WORKS/書誌が一切残らないよう、
# hero+main+aside を丸ごと空骨格に作り替える。head と footer 以降の chrome は流用。

def _parse_years(years: str) -> tuple[str, str]:
    """'1928–2019' → ('1928','2019')。存命 '1948–' → ('1948','')。"""
    parts = re.split(r"\s*[–—\-]\s*", (years or "").strip())
    birth = parts[0].strip() if parts else ""
    death = parts[1].strip() if len(parts) > 1 and parts[1].strip() else ""
    return birth, death


def _hero_initials(name_en: str) -> str:
    words = [w for w in re.split(r"\s+", (name_en or "").strip()) if w]
    if not words:
        return "·"
    first = words[0][0].upper()
    if len(words) >= 2:
        return f"{first}<span>{words[-1][0].upper()}</span>"
    return first


def _scaffold_jsonld(spec: dict) -> str:
    """Person 型のみ（実体準拠）。description は捏造回避のため入れない。"""
    birth, death = _parse_years(spec["years"])
    obj = {
        "@context": "https://schema.org", "@type": "Person",
        "name": spec["nameJa"], "alternateName": spec["nameEn"],
        "nationality": spec["countryJa"],
        "url": f"{SITE}/photographers/{spec['id']}.html",
    }
    if birth:
        obj["birthDate"] = birth
    if death:
        obj["deathDate"] = death
    return ('<script type="application/ld+json">\n'
            + json.dumps(obj, ensure_ascii=False, indent=2) + "\n</script>")


def _patch_head_and_header(prefix: str, spec: dict) -> str:
    """head の SEO タグ・JSON-LD と header の crumbs / 言語トグルを spec に合わせる。
    prefix（hero より前）に存在する自slug参照は ansel-adams のみなので URL は一括置換できる。"""
    pid = spec["id"]
    tags = spec.get("tags") or []
    kw_phrase = "・".join(tags[:2]) if tags else spec["nameEn"]
    title = f"{spec['nameJa']}｜{kw_phrase}｜写真の座標"
    ym = date.today().strftime("%Y.%m")

    # 1) URL の自slug（canonical / hreflang ja・en・x-default / og:url / 言語トグル EN /
    #    JSON-LD url）。en 形は ja 形を内包するので 1 回の置換で両方直る。
    prefix = prefix.replace(f"photographers/{Path(SCAFFOLD_BASE).stem}.html",
                            f"photographers/{pid}.html")

    # 2) 名前を含むタグ（title / og:title / twitter:title）→ 新タイトル。
    prefix = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", prefix, flags=re.S)
    prefix = re.sub(r'(<meta property="og:title" content=")[^"]*(">)',
                    rf"\g<1>{title}\g<2>", prefix)
    prefix = re.sub(r'(<meta name="twitter:title" content=")[^"]*(">)',
                    rf"\g<1>{title}\g<2>", prefix)

    # 3) description 系は捏造回避のため空にする（タグは残す＝手で記入）。
    for pat in (r'(<meta name="description" content=")[^"]*(">)',
                r'(<meta property="og:description" content=")[^"]*(">)',
                r'(<meta name="twitter:description" content=")[^"]*(">)'):
        prefix = re.sub(pat, r"\g<1>\g<2>", prefix)

    # 4) JSON-LD を Person だけで作り直す（Adams の name/生没年/description を残さない）。
    prefix = re.sub(r'<script type="application/ld\+json">.*?</script>',
                    lambda _m: _scaffold_jsonld(spec), prefix, count=1, flags=re.S)

    # 5) header crumbs を作り替える。
    crumbs = (
        '<div class="head__crumbs">\n'
        f'    <em>PHOTOGRAPHERS</em><span class="sep">/</span>{spec["nameEn"].upper()}\n'
        + (f'    <span class="sep">·</span>{tags[0]}\n' if tags else "")
        + f'    <span class="sep">·</span>UPDATED&nbsp;<span class="updated-date">{ym}</span>\n'
        '  </div>')
    prefix = re.sub(r'<div class="head__crumbs">.*?</div>', lambda _m: crumbs,
                    prefix, count=1, flags=re.S)
    return prefix


def _scaffold_body(spec: dict, idx) -> str:
    """hero + outer(main+aside) を spec 駆動の空骨格として生成する。"""
    pid = spec["id"]
    tags = spec.get("tags") or []
    art = _hero_initials(spec["nameEn"])
    entry_no = f"{int(idx):03d}" if str(idx).isdigit() else str(idx)
    kw = tags[0] if tags else ""
    era = spec["era"]
    period = f"{era}年代"
    updated = date.today().strftime("%Y.%m.%d")

    kw_chips = "\n        ".join(f'<span class="ph-kw">{t}</span>' for t in tags) or \
        '<span class="ph-kw">—</span>'
    side_chips = "\n            ".join(
        f'<span class="ph-side-chip{" is-primary" if i == 0 else ""}">{t}</span>'
        for i, t in enumerate(tags)) or '<span class="ph-side-chip">—</span>'

    sections = ["背景と時代", "表現の核心", "代表作・方法・媒体", "批評と写真史上の位置"]
    toc = "\n            ".join(
        f'<li class="toc-section"><a href="#sec-0{i}">'
        f'<span class="toc-num">§ 0{i}</span> {name}</a></li>'
        for i, name in enumerate(sections, 1))
    essays = "\n\n".join(f'''      <section class="ph-section" id="sec-0{i}">
        <div class="ph-section__head">
          <div class="ph-section__title">
            <span class="ph-section__num">§ 0{i} / 04</span>
            <span class="ph-section__name">{name}</span>
          </div>
        </div>
        <div class="ph-section__body">
          <div class="essay">
            <p></p>
          </div>
        </div>
      </section>''' for i, name in enumerate(sections, 1))

    return f'''<section class="ph-hero">
  <div class="ph-hero__art">{art}</div>
  <div class="ph-hero__info">
    <div class="ph-hero__eyebrow">§ {entry_no} — Photographer Index — {kw}</div>
    <h1 class="ph-hero__name">{spec['nameJa']}</h1>
    <div class="ph-hero__en">
      {spec['nameEn']}
      <span class="ph-hero__years">{spec['years']}</span>
    </div>
    <div class="ph-hero__meta-row">
      <span class="ph-hero__meta-item">Country<strong>{spec['countryJa']}</strong></span>
      <span class="ph-hero__meta-item">Period<strong>{period}</strong></span>
      <span class="ph-hero__meta-item">Channel<strong>{spec['channel']}</strong></span>
    </div>
  </div>
</section>

<div class="ph-outer">
  <div class="ph-layout">

    <main class="ph-main">

      <div class="ph-abstract">
        <div class="ph-abstract__label">Abstract</div>
        <p></p>
      </div>

      <dl class="ph-entry-meta">
        <dt>Entry</dt><dd>No. {entry_no}</dd>
        <dt>Category</dt><dd>Photographer</dd>
        <dt>Country</dt><dd>{spec['countryJa']}</dd>
        <dt>Years</dt><dd>{spec['years']}</dd>
        <dt>Period</dt><dd><a href="../eras/{era}.html">{period}</a></dd>
        <dt>Movement</dt><dd>—</dd>
        <dt>Updated</dt><dd>{updated}</dd>
        <dt></dt><dd></dd>
      </dl>

      <div class="ph-keywords">
        <span class="ph-keywords__label">Keywords</span>
        {kw_chips}
      </div>

      <section class="ph-section">
        <div class="ph-section__head">
          <div class="ph-section__title">
            <span class="ph-section__num">§ WORKS</span>
            <span class="ph-section__name">作品を見る</span>
          </div>
        </div>
        <div class="ph-section__body">
          <div class="prep-block" data-nosnippet>本サイトでは作品画像を掲載していません。公式アーカイブへのリンクは準備中です。</div>
        </div>
      </section>

      <details class="ph-toc" data-nosnippet>
        <summary>目次 · Table of Contents</summary>
        <div class="toc-body">
          <ol class="toc-list">
            {toc}
          </ol>
        </div>
      </details>

{essays}

      <section class="ph-section">
        <div class="ph-section__head">
          <div class="ph-section__title">
            <span class="ph-section__num">§ REL</span>
            <span class="ph-section__name">関連する写真家・運動</span>
          </div>
        </div>
        <div class="ph-section__body">
          <div class="prep-block" data-nosnippet>準備中</div>
        </div>
      </section>

      <section class="ph-section">
        <div class="ph-section__head">
          <div class="ph-section__title">
            <span class="ph-section__num">§ REF</span>
            <span class="ph-section__name">さらに読む</span>
          </div>
        </div>
        <div class="ph-section__body">
          <div class="prep-block" data-nosnippet>準備中</div>
        </div>
      </section>

      <section class="ph-section">
        <div class="ph-section__head">
          <div class="ph-section__title">
            <span class="ph-section__num">§ SRC</span>
            <span class="ph-section__name">出典</span>
          </div>
        </div>
        <div class="ph-section__body">
          <div class="ph-sources"></div>
        </div>
      </section>

    </main>

    <aside class="ph-side">

      <div class="ph-side-search" data-nosnippet>
        <form class="ph-side-search__form" onsubmit="return false;">
          <label class="ph-side-search__label" for="ph-search-input-{pid}">SEARCH · 写真家を探す</label>
          <div class="ph-side-search__field">
            <input class="ph-side-search__input" id="ph-search-input-{pid}" type="search" placeholder="写真家名・運動・キーワード" autocomplete="off" aria-autocomplete="list" aria-controls="ph-search-suggestions-{pid}" aria-expanded="false">
            <button class="ph-side-search__btn" type="button" aria-label="検索">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><circle cx="5.5" cy="5.5" r="4.5" stroke="currentColor" stroke-width="1.5"/><line x1="9" y1="9" x2="13" y2="13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
            </button>
          </div>
        </form>
        <ul class="ph-search-suggestions" id="ph-search-suggestions-{pid}" role="listbox" hidden data-nosnippet></ul>
      </div>

      <div class="ph-side-block">
        <div class="ph-side-block__head">Entry · 写真家データ</div>
        <div class="ph-side-block__body">
          <div class="ph-side-meta">
            <div class="ph-side-meta-row"><span class="ph-side-meta-key">Country</span><span class="ph-side-meta-val">{spec['countryJa']}</span></div>
            <div class="ph-side-meta-row"><span class="ph-side-meta-key">Years</span><span class="ph-side-meta-val">{spec['years']}</span></div>
            <div class="ph-side-meta-row"><span class="ph-side-meta-key">Period</span><span class="ph-side-meta-val"><a href="../eras/{era}.html">{period}</a></span></div>
            <div class="ph-side-meta-row"><span class="ph-side-meta-key">Movement</span><span class="ph-side-meta-val">—</span></div>
            <div class="ph-side-meta-row"><span class="ph-side-meta-key">Updated</span><span class="ph-side-meta-val">{updated}</span></div>
          </div>
        </div>
      </div>

      <div class="ph-side-block">
        <div class="ph-side-block__head">Keywords · キーワード</div>
        <div class="ph-side-block__body">
          <div class="ph-side-chips">
            {side_chips}
          </div>
        </div>
      </div>

      <div class="ph-side-block">
        <div class="ph-side-block__head">Navigate · 移動</div>
        <nav class="ph-side-nav" data-nosnippet>
          <a href="/archive.html"><span>← 写真家一覧</span><span>Archive</span></a>
          <a href="/index.html"><span>トップページへ</span><span>Top</span></a>
        </nav>
      </div>

    </aside>

  </div>
</div>

'''


def build_scaffold_html(spec: dict, idx) -> str:
    base = SCAFFOLD_BASE.read_text(encoding="utf-8")
    hero_at = base.index('<section class="ph-hero">')
    footer_at = base.index('<footer class="foot"')
    prefix = _patch_head_and_header(base[:hero_at], spec)
    suffix = base[footer_at:]              # footer + page close + 検索インデックス + scripts（流用）
    return prefix + _scaffold_body(spec, idx) + suffix


def scaffold_page(spec: dict, apply: bool):
    pid = spec["id"]
    out = REPO / "photographers" / f"{pid}.html"
    print("\n" + "=" * 70)
    print("空骨格 scaffold（ansel-adams コピー → 機械確定項目だけ置換 → 本文は空）")
    print("=" * 70)
    if out.exists():
        print(f"  🛑 {out.relative_to(REPO)} は既に存在 → 上書きしない（安全スキップ）。")
        print("     既存ページを作り直す場合は手動でバックアップしてから削除すること。")
        return False
    cd = json.loads(CARD_DATA.read_text(encoding="utf-8"))
    idx = next((p["idx"] for p in cd["photographers"] if p["id"] == pid), spec.get("idx", "—"))
    html = build_scaffold_html(spec, idx)
    if not apply:
        print(f"  [DRY-RUN] {out.relative_to(REPO)} を生成予定（--apply で書き出し）。{len(html)} bytes。")
        return False
    out.write_text(html, encoding="utf-8")
    print(f"  ✅ 生成: {out.relative_to(REPO)}（{len(html)} bytes）")
    print("  ※本文・thesis・出典・description は空。要素を流し込んで完成させること。")
    return True


def resolve_country_slugs(nationality: str) -> list[str]:
    """Map a card nationality code (e.g. "JP" or "US / FR") to the single-country
    page slug(s) this photographer appears on, using data/country-pages.json as
    the source of truth. A member belongs to every single page whose codes are a
    subset of the photographer's nationality tokens (so "US / FR" → both
    united-states and france). Returns slugs in registry order."""
    reg_path = REPO / "data" / "country-pages.json"
    if not reg_path.exists():
        return []
    registry = json.loads(reg_path.read_text(encoding="utf-8"))
    tokens = {t.strip() for t in nationality.split("/") if t.strip()}
    return [r["slug"] for r in registry if set(r.get("codes", [])) <= tokens and r.get("codes")]


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
    print("  # 国ページ（この写真家が載る単国 slug だけを再生成。無指定はガードで拒否）")
    country_slugs = resolve_country_slugs(spec["nationality"])
    if country_slugs:
        flags = " ".join(f"--country {s}" for s in country_slugs)
        print(f"  python3 scripts/generate_country_pages.py {flags}     # JA")
        print(f"  python3 scripts/generate_country_pages_en.py {flags}  # EN")
    else:
        print(f"  # nationality={spec['nationality']} に対応する単国ページが registry に無い")
        print(f"  # （該当 slug を確認のうえ）python3 scripts/generate_country_pages.py --country <slug>")
        print(f"  #                         python3 scripts/generate_country_pages_en.py --country <slug>")
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
    print("    最速＝空骨格 scaffold を生成（このスクリプトに --scaffold を付ける）：")
    print(f"      python3 scripts/add_photographer.py <spec.json> --apply --scaffold")
    print("    → ansel-adams.html をコピーし、slug/URL/名前/生没年/国/era など機械確定項目だけ")
    print("      置換した空骨格を作る（SEO一式＋本文4節の型が入り、Adams 残骸ゼロ）。")
    print("    手作業でやる場合も参照実装は ansel-adams.html（winogrand は薄い型なので使わない）。")
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
    scaffold = "--scaffold" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        fail("spec.json のパスを指定してください（--apply で実投入 / --scaffold で空骨格ページ生成）")
    spec = load_spec(paths[0])

    if spec["id"] in {p.get("id") for p in json.loads(CARD_DATA.read_text(encoding='utf-8'))["photographers"]} \
       or spec["id"] in js_existing_ids():
        print(f"[注意] id '{spec['id']}' は既にデータに存在します（冪等: 既存分はスキップ）")

    print(f"\n{'[APPLY]' if apply else '[DRY-RUN]'} 写真家データ投入: {spec['id']} ({spec['nameJa']})")
    insert_card_data(spec, apply)
    insert_star(spec, SUPPLEMENT, apply)
    insert_star(spec, STAR_BIN, apply)
    scaffolded = scaffold_page(spec, apply) if scaffold else False
    print_snippets_and_runbook(spec)
    if scaffolded:
        print("\n── 生成ページの完成検査（未記入箇所が WARN で出る）──")
        subprocess.run([sys.executable, str(REPO / "scripts/check_new_photographer.py"),
                        "--slug", spec["id"]])
    if apply:
        print("\n── preflight ──")
        subprocess.run([sys.executable, str(REPO / "scripts/preflight.py")])
    else:
        suffix = "" if scaffold else "（--scaffold で空骨格ページも生成）"
        print(f"\n（ドライラン。実投入するには --apply を付けて再実行）{suffix}")


if __name__ == "__main__":
    main()
