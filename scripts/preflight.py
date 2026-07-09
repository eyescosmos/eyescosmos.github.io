#!/usr/bin/env python3
"""Preflight checks — push 前に「過去の事故クラス」を機械的に検出する。

設計方針:
- HARD（exit 1 でブロック）は、現在グリーンで決定論的な不変条件のみ。
  ここが赤い＝今回の変更で壊した、と断定できるものだけを門にする。
- 既存スクリプト（check_*.py）は既知の事前ノイズを含むため WARN 表示に留める
  （ブロックしない）。

使い方:  python3 scripts/preflight.py
CLAUDE.md の「不可視の必須要素」「重複防止」を文章ルールから機械チェックへ移管する土台。
"""
from __future__ import annotations
import functools
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GA_TOKEN = "googletagmanager"

# GA カバレッジと同じ「公開 HTML」対象範囲（ルート直下＋各分類ディレクトリ）
PUBLIC_HTML_DIRS = [".", "photographers", "movements", "eras", "countries",
                    "en", "en/photographers", "en/countries", "en/movements", "en/eras"]

hard_failures: list[str] = []
warnings: list[str] = []          # 要確認（今回の変更に起因しうる）
known_warnings: list[str] = []    # 既知・非ブロック（環境差や既存ノイズ）
infos: list[str] = []             # 消費された intentional-replacement 宣言など（ブロックしない）

INTENTIONAL_REPLACEMENTS_JSON = REPO / "scripts" / "intentional-replacements.json"

# check_en_entry の検査ロジックを再利用する
sys.path.insert(0, str(REPO / "scripts"))
try:
    import check_en_entry as cee  # noqa: E402
except Exception:  # noqa: BLE001
    cee = None

# 新規写真家ページの構造／cite 検査（touched-only の軽量網として再利用）
try:
    import check_new_photographer as cnp  # noqa: E402
except Exception:  # noqa: BLE001
    cnp = None

EN_CONTENT_JSON = "data/photographers-en-content.json"


def eval_photographers() -> list[dict]:
    """taxonomy/photographer ジェネレータと同じ3ファイルを eval して PHOTOGRAPHERS を得る。"""
    files = [
        "data/photographers.js",
        "data/photographers-manual-additions.js",
        "data/photographers-supplement.js",
    ]
    src = ["(function(){ var window=this;"]
    for f in files:
        src.append((REPO / f).read_text(encoding="utf-8"))
    src.append("console.log(JSON.stringify(PHOTOGRAPHERS.map(function(p){return p&&p.id;})));")
    src.append("})();")
    proc = subprocess.run(
        ["osascript", "-l", "JavaScript"],
        input="\n".join(src).encode("utf-8"),
        capture_output=True,
    )
    payload = proc.stderr.decode("utf-8") or proc.stdout.decode("utf-8")
    # osascript(JavaScript) は稀に JSON 行の前後へ警告行を混ぜる（"Extra data" で
    # json.loads が落ち、重複チェックが黙ってスキップされる）。先頭が '[' の行だけ拾う。
    for line in payload.splitlines():
        line = line.strip()
        if line.startswith("["):
            return json.loads(line)
    return json.loads(payload)


def check_dup_ids_js() -> None:
    """photographers.js / supplement.js の二重登録（過去事故）を検出。"""
    try:
        ids = [i for i in eval_photographers() if i]
    except Exception as e:  # noqa: BLE001
        known_warnings.append(
            "JS写真家の重複チェックをスキップ（既知・非ブロック: osascript(JavaScript) を"
            f"使えない環境。macOS 以外では正常に出る）: {e}"
        )
        return
    seen, dups = set(), set()
    for i in ids:
        (dups if i in seen else seen).add(i)
    if dups:
        hard_failures.append(
            f"data/photographers*.js の PHOTOGRAPHERS に重複id: {sorted(dups)} "
            f"(新規は supplement.js のみへ。photographers.js は中核48名で固定)"
        )


def check_dup_ids_carddata() -> None:
    data = json.loads((REPO / "card-data.json").read_text(encoding="utf-8"))
    ids = [p.get("id") for p in data.get("photographers", []) if p.get("id")]
    seen, dups = set(), set()
    for i in ids:
        (dups if i in seen else seen).add(i)
    if dups:
        hard_failures.append(f"card-data.json に重複id: {sorted(dups)}")


def is_redirect_stub(html: str) -> bool:
    return ("noindex" in html) and ("http-equiv" in html.lower() and "refresh" in html.lower())


def check_ga_coverage() -> None:
    """公開 .html に GA があるか。例外: リダイレクトスタブ / *-backup.html / Google確認ファイル。"""
    missing: list[str] = []
    for d in PUBLIC_HTML_DIRS:
        p = REPO / d
        if not p.is_dir():
            continue
        for f in sorted(p.glob("*.html")):
            name = f.name
            if name.endswith("-backup.html") or name.startswith("google"):
                continue
            html = f.read_text(encoding="utf-8", errors="ignore")
            if is_redirect_stub(html):
                continue
            if GA_TOKEN not in html:
                missing.append(str(f.relative_to(REPO)))
    if missing:
        hard_failures.append(
            f"GA(googletagmanager)欠落 {len(missing)}件: " + ", ".join(missing[:12])
            + (" …" if len(missing) > 12 else "")
        )


def _baseline_ref() -> str:
    """比較基準。push 時に実効化するため「公開済み側」を優先する。
    upstream（@{u}）→ origin/main → HEAD の順で最初に解決できたものを使う。
    env PREFLIGHT_BASE で上書き可。"""
    forced = os.environ.get("PREFLIGHT_BASE")
    if forced:
        return forced
    for cand in ("@{u}", "origin/main"):
        proc = subprocess.run(["git", "rev-parse", "--verify", "--quiet", cand],
                              capture_output=True, text=True, cwd=REPO)
        if proc.returncode == 0 and proc.stdout.strip():
            return cand
    return "HEAD"


def _git_show(ref: str, rel_path: str) -> str | None:
    """ref 時点のファイル内容。存在しなければ None。"""
    proc = subprocess.run(["git", "show", f"{ref}:{rel_path}"],
                          capture_output=True, text=True, cwd=REPO)
    return proc.stdout if proc.returncode == 0 else None


def _en_entry_metrics(entry: dict) -> dict:
    """EN エントリの「減ってはいけない」量を数える。"""
    sources = entry.get("sources_html") or ""
    body = "\n".join(
        ([entry.get("thesis_html") or "", entry.get("lead_html") or ""]
         + [s.get("body_html", "") for s in (entry.get("sections") or [])])
    )
    links = {h for h in re.findall(r'href="(https?://[^"]+)"', _all_link_html(entry))}
    cite_id_set = set(re.findall(r'id="cite-(\d+)"', sources))
    # 本文の脚注参照は「sources に実在する cite を指すものだけ」を一意に数える。
    # 旧自動版 JSON に残っていた描画されない重複／壊れアンカー（同一 cite-N の
    # 重複・sources に無い cite-N）を HEAD 本文同期で除去しても、それは実体の
    # 消失ではないので偽陽性 HARD にしない。一方、実在する被引用への参照が
    # 本当に消えた場合は集合が縮むため依然 HARD（era1980 bruno-serralongue /
    # beate-gutschow の偽陽性根治・commit 33a775400 参照）。
    reachable_suprefs = {n for n in re.findall(r'href="#cite-(\d+)"', body)
                         if n in cite_id_set}
    return {
        "cite": len(cite_id_set),
        "sections": len(entry.get("sections") or []),
        "links": links,
        "thesis": bool((entry.get("thesis_html") or "").strip()),
        "supref": len(reachable_suprefs),
    }


def _all_link_html(entry: dict) -> str:
    if cee is not None:
        return cee.all_link_html(entry)
    # フォールバック（cee 不在時）
    fields = ("lead_html", "thesis_html", "keywords_html", "view_works_links_html",
              "notable_works_html", "photobooks_html", "external_links_html",
              "further_reading_html", "sources_html", "site_directory_html")
    chunks = [entry.get(f) or "" for f in fields if entry.get(f) not in (None, "None")]
    chunks += [s.get("body_html", "") for s in (entry.get("sections") or [])]
    return "\n".join(chunks)


HAND_MAINTAINED_EN = getattr(cee, "HAND_MAINTAINED_EN", {"stieglitz.html", "annie-leibovitz.html"})


@functools.lru_cache(maxsize=1)
def _touched_en() -> dict:
    """baseline（origin/main 等）と作業ツリーを比較し、触れた EN slug を集める。
    JSON エントリの変化と en/photographers/*.html の変化の両方を合流させる。
    返り値 {slug: {"base", "work", "json_changed", "html_changed"}}。"""
    baseline = _baseline_ref()
    work_path = REPO / EN_CONTENT_JSON
    try:
        work_pages = json.loads(work_path.read_text(encoding="utf-8")).get("pages", {}) \
            if work_path.exists() else {}
    except Exception:  # noqa: BLE001
        work_pages = {}
    base_raw = _git_show(baseline, EN_CONTENT_JSON)
    try:
        base_pages = json.loads(base_raw).get("pages", {}) if base_raw else {}
    except Exception:  # noqa: BLE001
        base_pages = {}

    touched: dict[str, dict] = {}
    # 1) JSON エントリの変化
    for slug, we in work_pages.items():
        be = base_pages.get(slug)
        if be != we:
            touched[slug] = {"base": be, "work": we, "json_changed": True, "html_changed": False}
    # 2) en/photographers/*.html の変化
    proc = subprocess.run(["git", "diff", "--name-only", baseline, "--", "en/photographers"],
                          capture_output=True, text=True, cwd=REPO)
    for line in proc.stdout.splitlines():
        name = os.path.basename(line.strip())
        if not name.endswith(".html") or name.startswith("jp-") or name.endswith("-backup.html"):
            continue
        info = touched.get(name)
        if info:
            info["html_changed"] = True
        else:
            touched[name] = {"base": base_pages.get(name), "work": work_pages.get(name),
                             "json_changed": False, "html_changed": True}
    return touched


def check_en_content_loss() -> None:
    """JSON-vs-baseline: 触った EN エントリが本文・出典・リンクを失っていないか（HARD）。
    変更が無ければ必ずグリーンなので門にできる。"""
    for slug, info in _touched_en().items():
        if not info["json_changed"]:
            continue
        be, we = info["base"], info["work"]
        if be is None or we is None:
            continue  # 新規 slug / 削除は loss 判定対象外
        old, new = _en_entry_metrics(be), _en_entry_metrics(we)
        losses = []
        if new["cite"] < old["cite"]:
            losses.append(f"出典 {old['cite']}→{new['cite']}")
        if new["sections"] < old["sections"]:
            losses.append(f"本文セクション {old['sections']}→{new['sections']}")
        if new["supref"] < old["supref"]:
            losses.append(f"本文 sup-ref {old['supref']}→{new['supref']}")
        if old["thesis"] and not new["thesis"]:
            losses.append("thesis が空に")
        dropped = sorted(old["links"] - new["links"])
        if dropped:
            losses.append(f"リンク{len(dropped)}件消失: {dropped[:3]}")
        if losses:
            hard_failures.append(
                f"{EN_CONTENT_JSON} の {slug} が内容を失っている: " + " / ".join(losses)
            )


def check_en_changed_slug_closure() -> None:
    """触った slug の EN HTML が JSON 宣言と一致するか（HARD）。
    JSON を直して再生成し忘れた／生成物を直接編集して JSON と乖離した状態を捕捉。"""
    if cee is None:
        return
    for slug, info in _touched_en().items():
        if slug in HAND_MAINTAINED_EN or info["work"] is None:
            continue
        rep = cee.Report(slug)
        cee.check_html_vs_json(info["work"], slug, rep)
        for f in rep.fails:
            hard_failures.append(
                f"[EN closure] {f}（build_photographers_en.py --slug {slug[:-5]} を実行）")


def check_en_direct_edit() -> None:
    """生成物の EN HTML が直接編集された疑いを検知（WARN）。
    EN HTML が変わったのに対応する JSON が変わっていない＝手編集の兆候。
    手書き維持ページ（annie-leibovitz / stieglitz）は例外。"""
    for slug, info in _touched_en().items():
        if slug in HAND_MAINTAINED_EN:
            continue
        if info["html_changed"] and not info["json_changed"]:
            warnings.append(
                f"[EN {slug}] 生成物の EN HTML を直接編集した疑い。正本は {EN_CONTENT_JSON}。"
                f"JSON を直して build_photographers_en.py --slug {slug[:-5]} で再生成すること"
            )


def check_en_changed_slug_integrity() -> None:
    """触った slug の sup/cite・リンク健全性（WARN）。
    既存バグを抱えた slug を触っても push はブロックしないが気づけるようにする。"""
    if cee is None:
        return
    for slug, info in _touched_en().items():
        if info["work"] is None:
            continue
        rep = cee.Report(slug)
        cee.check_cite_supref(info["work"], rep)
        cee.check_links(info["work"], rep)
        for f in rep.fails:
            warnings.append(f"[EN {slug}] {f}")


def check_en_rel_annotations() -> None:
    """触った EN ページで、JA §REL に一言解説がある関連リンクなのに EN の
    related_annotations が欠けている取りこぼしを検知（WARN）。
    年代バッチの §REL 埋めで JA HTML と site_directory_html を更新したとき、
    EN の一言（related_annotations）を入れ忘れる divergence を毎回可視化する。
    backfill は scripts/sync_en_rel_annotations.py（--emit-worklist / --apply）。"""
    try:
        sys.path.insert(0, str(REPO / "scripts"))
        import sync_en_rel_annotations as sra  # noqa: PLC0415
    except Exception:  # noqa: BLE001
        return
    try:
        pages = sra.load_pages()
    except Exception:  # noqa: BLE001
        return
    for key in _touched_en():  # keys are "<slug>.html"
        slug = key[:-5] if key.endswith(".html") else key
        entry = pages.get("pages", {}).get(key)
        if not entry:
            continue
        try:
            rows = sra.page_alignment(slug, entry)
        except Exception:  # noqa: BLE001
            continue
        missing = [r for r in rows if r[0] == "need"]
        if missing:
            warnings.append(
                f"[EN {slug}] §REL 一言解説 未注入 {len(missing)}件"
                f"（JAにあり/ENに無し）: sync_en_rel_annotations.py で backfill")


# ── 写真家以外の EN ページ（国別 / 年代・運動 / アーカイブ）の軽量ガード ──────
# 設計（Codex 合意 2026-06-19）:
#   - 正本 JSON のエントリ内容消失 = HARD（変更が無ければ必ずグリーン＝門にできる）
#   - 生成物 EN HTML の直接編集疑い = WARN
#   - 触ったファイル / 触った正本エントリだけ検査（baseline は写真家ガードと共通）
#   - 本文が JSON 外（build_taxonomy_en.py の直書き）にもある混在構造でも、
#     「JSON が確実に内容を失った」ことだけを HARD にする。曖昧判定はしない。
#   - per-slug リーダは追加しない（写真家のみで十分という方針）。

COUNTRY_JSON = "data/country-pages.json"
TAXONOMY_JSON = "data/taxonomy-en-content.json"
CARD_DATA_JSON = "card-data.json"


def _is_filled(v) -> bool:
    """JSON 値が「中身を持つ」か（消失判定用）。str は空白除去、コンテナは長さで判定。"""
    if isinstance(v, str):
        return bool(v.strip())
    if isinstance(v, (list, dict)):
        return len(v) > 0
    return v is not None


def _load_json_ref(baseline: str, rel_path: str):
    """baseline 時点と作業ツリーの JSON を (base, work) で返す（解析失敗時 None）。"""
    def _parse(text):
        try:
            return json.loads(text) if text else None
        except Exception:  # noqa: BLE001
            return None
    base = _parse(_git_show(baseline, rel_path))
    wp = REPO / rel_path
    work = _parse(wp.read_text(encoding="utf-8")) if wp.exists() else None
    return base, work


def _changed_html_basenames(baseline: str, rel_dir: str) -> set[str]:
    """baseline と作業ツリーで差分のある rel_dir 直下の *.html ベース名。
    リダイレクトスタブ / *-backup.html は除外（直接編集の対象ではない）。"""
    proc = subprocess.run(["git", "diff", "--name-only", baseline, "--", rel_dir],
                          capture_output=True, text=True, cwd=REPO)
    out: set[str] = set()
    for line in proc.stdout.splitlines():
        name = os.path.basename(line.strip())
        if not name.endswith(".html") or name.endswith("-backup.html"):
            continue
        # rel_dir 直下のみ（en の archive.html 等。サブディレクトリは別 rel_dir で扱う）
        if os.path.dirname(line.strip()) != rel_dir:
            continue
        fp = REPO / rel_dir / name
        if fp.exists() and is_redirect_stub(fp.read_text(encoding="utf-8", errors="ignore")):
            continue
        out.add(name)
    return out


def check_country_en() -> None:
    """国別 EN（en/countries/*.html）の正本 country-pages.json の内容消失=HARD、
    生成物 HTML の直接編集疑い=WARN。"""
    baseline = _baseline_ref()
    base, work = _load_json_ref(baseline, COUNTRY_JSON)
    if not isinstance(work, list):
        return
    base_map = {r["slug"]: r for r in (base or []) if isinstance(r, dict) and r.get("slug")}
    work_map = {r["slug"]: r for r in work if isinstance(r, dict) and r.get("slug")}
    changed = {s for s, we in work_map.items() if base_map.get(s) != we}
    # 1) 正本の内容消失（HARD）— base/work 双方にあるエントリのみ
    for slug in changed:
        be, we = base_map.get(slug), work_map[slug]
        if be is None:
            continue  # 新規 slug は loss 判定対象外
        losses = [f for f in ("lead", "nameEn", "nameJa")
                  if _is_filled(be.get(f)) and not _is_filled(we.get(f))]
        if be.get("codes") and not we.get("codes"):
            losses.append("codes")
        if losses:
            hard_failures.append(
                f"{COUNTRY_JSON} の {slug} が内容を失っている: {', '.join(losses)}")
    # 2) 生成物 EN HTML の直接編集疑い（WARN）
    for name in _changed_html_basenames(baseline, "en/countries"):
        slug = name[:-5]
        if slug not in work_map:        # 複合スタブ等は正本に無い → 対象外
            continue
        if slug not in changed:
            warnings.append(
                f"[EN country {slug}] 生成物 en/countries/{name} を直接編集した疑い。"
                f"正本は {COUNTRY_JSON}。generate_country_pages_en.py --country {slug} で再生成すること")


def check_taxonomy_en() -> None:
    """年代・運動 EN（en/eras・en/movements）の正本 taxonomy-en-content.json の
    内容消失=HARD、生成物 HTML の直接編集疑い=WARN。本文が builder 直書きにも
    あるため、判定は「JSON が確実に失った」ものだけに限定する。"""
    baseline = _baseline_ref()
    base, work = _load_json_ref(baseline, TAXONOMY_JSON)
    if not isinstance(work, dict):
        return
    for group, rel_dir in (("movements", "en/movements"), ("eras", "en/eras")):
        base_g = (base or {}).get(group, {}) if isinstance(base, dict) else {}
        work_g = work.get(group, {})
        if not isinstance(work_g, dict):
            continue
        changed = {k for k, wv in work_g.items() if base_g.get(k) != wv}
        # 内容消失（HARD）
        for slug in changed:
            be, we = base_g.get(slug), work_g.get(slug)
            if be is None:
                continue
            losses = []
            bmeta, wmeta = be.get("meta", {}), we.get("meta", {})
            for field in ("title", "description"):
                if _is_filled(bmeta.get(field)) and not _is_filled(wmeta.get(field)):
                    losses.append(f"meta.{field}")
            bsec, wsec = be.get("sections", {}), we.get("sections", {})
            for key, bv in bsec.items():
                if _is_filled(bv) and not _is_filled(wsec.get(key)):
                    losses.append(f"section[{key}]")
            if losses:
                hard_failures.append(
                    f"{TAXONOMY_JSON} の {group}/{slug} が内容を失っている: "
                    + ", ".join(losses[:4]))
        # 直接編集（WARN）
        for name in _changed_html_basenames(baseline, rel_dir):
            slug = name[:-5]
            if slug not in work_g:       # JA 名スタブ等は正本キーに無い → 対象外
                continue
            if slug not in changed:
                regen_flag = f"--era {slug}" if group == "eras" else f"--slug {slug}"
                warnings.append(
                    f"[EN {group}/{slug}] 生成物 {rel_dir}/{name} を直接編集した疑い。"
                    f"正本は {TAXONOMY_JSON}。build_taxonomy_en.py {regen_flag} で再生成すること")


def check_archive_en() -> None:
    """アーカイブ EN（en/archive.html）の正本 card-data.json の内容消失=HARD、
    生成物 HTML だけが変わって card-data.json が不変なら直接編集疑い=WARN。"""
    baseline = _baseline_ref()
    base, work = _load_json_ref(baseline, CARD_DATA_JSON)
    if not isinstance(work, dict):
        return
    json_changed = base != work
    if isinstance(base, dict) and json_changed:
        for group in ("photographers", "movements"):
            base_list = base.get(group, []) or []
            work_list = work.get(group, []) or []
            base_map = {c.get("id"): c for c in base_list if isinstance(c, dict) and c.get("id")}
            work_map = {c.get("id"): c for c in work_list if isinstance(c, dict) and c.get("id")}
            if len(work_list) < len(base_list):
                hard_failures.append(
                    f"{CARD_DATA_JSON} の {group} カード数が減少: "
                    f"{len(base_list)}→{len(work_list)}")
            missing = sorted(set(base_map) - set(work_map))
            if missing:
                hard_failures.append(
                    f"{CARD_DATA_JSON} の {group} から card 消失: {missing[:5]}")
            for cid in set(base_map) & set(work_map):
                bc, wc = base_map[cid], work_map[cid]
                lost = [f for f in ("nameEn", "nameJa", "href")
                        if _is_filled(bc.get(f)) and not _is_filled(wc.get(f))]
                if lost:
                    hard_failures.append(
                        f"{CARD_DATA_JSON} の {group}/{cid} がフィールドを失っている: "
                        + ", ".join(lost))
    # 生成物 en/archive.html の直接編集疑い（WARN）
    proc = subprocess.run(["git", "diff", "--name-only", baseline, "--", "en/archive.html"],
                          capture_output=True, text=True, cwd=REPO)
    if proc.stdout.strip() and not json_changed:
        warnings.append(
            f"[EN archive] 生成物 en/archive.html を直接編集した疑い。"
            f"正本は {CARD_DATA_JSON}。build_archive_en.py で再生成すること")


# ── ③ ドリフト検知（WARN のみ・archive掲載漏れ＋country hero 件数ズレ）────────────

def check_archive_presence() -> None:
    """card-data.json の全 photographer id が archive.html に掲載されているか検知（WARN）。
    archive.html への未掲載 = 国別ページのカウント崩れの根になる。"""
    try:
        card_data = json.loads((REPO / "card-data.json").read_text(encoding="utf-8"))
    except Exception:
        return
    archive_path = REPO / "archive.html"
    if not archive_path.exists():
        return
    html = archive_path.read_text(encoding="utf-8", errors="ignore")
    archived_slugs = set(re.findall(r'href="photographers/([^"]+)\.html"', html))
    all_ids = [p["id"] for p in card_data.get("photographers", []) if p.get("id")]
    missing = [pid for pid in all_ids if pid not in archived_slugs]
    if missing:
        sample = missing[:15]
        warnings.append(
            f"archive.html に未掲載の photographers: {len(missing)} 件"
            f"（国別カウント崩れの根。先頭{len(sample)}件: {sample}"
            + (" …" if len(missing) > 15 else "")
            + "）"
        )


def check_country_hero_counts() -> None:
    """countries/*.html の hero 表示人数と実カード数がズレていないか検知（WARN）。
    <span class="era-hero__meta-item">Photographers <strong>N</strong></span> の N と
    pc-card--photographer の出現数を比較する。"""
    countries_dir = REPO / "countries"
    if not countries_dir.exists():
        return
    for fpath in sorted(countries_dir.glob("*.html")):
        try:
            html = fpath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        m = re.search(r'Photographers\s*<strong>(\d+)</strong>', html)
        if not m:
            continue  # hero meta が無いページは skip
        hero_n = int(m.group(1))
        card_n = html.count('pc-card--photographer')
        if hero_n != card_n:
            warnings.append(
                f"countries/{fpath.name}: hero人数 {hero_n} / 実カード {card_n}"
                f" ＝ drift か手編集の兆候"
            )


# ── SEO / 不可視必須要素 & JA 分類ページの本文消失（baseline 比較・触ったものだけ）──
# 設計（2026-06-19 追加）:
#   - 既存ページには穴がある前提で「baseline にあった要素が消えた」ときだけ HARD。
#     元から無いページ・新規ページはブロックしない（段階導入）。
#   - redirect stub / *-backup.html / google確認ファイル / 削除済みは対象外。
#   - 触った公開 HTML だけが対象＝無関係な push は必ずグリーン。

def _touched_html(baseline: str, allowed_dirs: list[str]) -> list[tuple[str, str]]:
    """baseline と作業ツリーで差分のある公開 HTML を (rel_path, work_html) で返す。
    stub / backup / google / 削除済みは除外。allowed_dirs は直下のみ（再帰しない）。"""
    allowed = set(allowed_dirs)
    proc = subprocess.run(["git", "diff", "--name-only", baseline],
                          capture_output=True, text=True, cwd=REPO)
    out: list[tuple[str, str]] = []
    for line in proc.stdout.splitlines():
        rel = line.strip()
        if not rel.endswith(".html") or rel.endswith("-backup.html"):
            continue
        d = os.path.dirname(rel) or "."
        if d not in allowed:
            continue
        if os.path.basename(rel).startswith("google"):
            continue
        fp = REPO / rel
        if not fp.exists():
            continue  # 削除はページ単位の事象として別扱い
        html = fp.read_text(encoding="utf-8", errors="ignore")
        if is_redirect_stub(html):
            continue  # スタブ化は意図的な転送なので対象外
        out.append((rel, html))
    return out


def _seo_metrics(html: str) -> dict:
    title = re.search(r'<title[^>]*>(.*?)</title>', html, re.S | re.I)
    return {
        "canonical": len(re.findall(r'rel=["\']canonical["\']', html, re.I)),
        "hreflang": len(re.findall(r'hreflang=', html, re.I)),
        "jsonld": len(re.findall(r'application/ld\+json', html, re.I)),
        "nosnippet": len(re.findall(r'data-nosnippet', html, re.I)),
        "title": 1 if (title and re.sub(r'<[^>]+>', '', title.group(1)).strip()) else 0,
        "description": len(re.findall(r'name=["\']description["\']', html, re.I)),
        "og": len(re.findall(r'og:title|og:description', html, re.I)),
        "twitter": len(re.findall(r'twitter:title|twitter:description', html, re.I)),
    }


def check_seo_invisible_loss() -> None:
    """公開 HTML の不可視必須要素（canonical / hreflang / JSON-LD / data-nosnippet /
    title / description / OGP / Twitter）が baseline 比で消えていないか。
    完全消失・hreflang 減＝HARD、OGP/Twitter 減・nosnippet 部分減・新規欠落＝WARN。"""
    baseline = _baseline_ref()
    for rel, work_html in _touched_html(baseline, PUBLIC_HTML_DIRS):
        wm = _seo_metrics(work_html)
        base_html = _git_show(baseline, rel)
        if base_html is None:
            missing = [k for k in ("canonical", "title", "description") if wm[k] == 0]
            if missing:
                warnings.append(
                    f"[SEO新規 {rel}] コア要素が未設定: {', '.join(missing)}")
            continue
        bm = _seo_metrics(base_html)
        hard = []
        for key, label in (("canonical", "canonical"), ("jsonld", "JSON-LD"),
                           ("title", "title"), ("description", "meta description"),
                           ("nosnippet", "data-nosnippet")):
            if bm[key] > 0 and wm[key] == 0:
                hard.append(f"{label} 消失")
        if bm["hreflang"] > wm["hreflang"]:
            hard.append(f"hreflang {bm['hreflang']}→{wm['hreflang']}")
        if hard:
            hard_failures.append(
                f"[SEO {rel}] baseline 比で必須要素が消失: " + " / ".join(hard))
        warn = []
        if bm["og"] > wm["og"]:
            warn.append(f"OGP {bm['og']}→{wm['og']}")
        if bm["twitter"] > wm["twitter"]:
            warn.append(f"Twitter {bm['twitter']}→{wm['twitter']}")
        if 0 < wm["nosnippet"] < bm["nosnippet"]:
            warn.append(f"data-nosnippet {bm['nosnippet']}→{wm['nosnippet']}")
        if warn:
            warnings.append(f"[SEO {rel}] 不可視要素が減少（要確認）: " + " / ".join(warn))


def check_ja_seo_holes() -> None:
    """JA 写真家ページの既存 SEO 穴を WARN で検知する。
    check_seo_invisible_loss は「baseline にあった要素の消失」検知。
    こちらは「触った JA ページに要素が元から無い / 付け忘れ」を検知する。
    WARN 専用で、push は絶対にブロックしない。"""
    baseline = _baseline_ref()
    for rel, work_html in _touched_html(baseline, ["photographers"]):
        m = _seo_metrics(work_html)
        missing = []
        if m["canonical"] == 0:
            missing.append("canonical 未設定")
        if m["og"] == 0:
            missing.append("OGP 未設定")
        if m["nosnippet"] == 0:
            missing.append("data-nosnippet 未設定")
        if m["description"] == 0:
            missing.append("meta description 未設定")
        if m["jsonld"] == 0:
            missing.append("JSON-LD 未設定")
        slug = os.path.splitext(os.path.basename(rel))[0]
        has_en = (REPO / "en" / "photographers" / f"{slug}.html").exists()
        if m["hreflang"] == 0 and "noindex" not in work_html and has_en:
            missing.append("hreflang 未設定")
        if missing:
            warnings.append(f"[SEO穴 {rel}] 未設定: {', '.join(missing)}")


def _classif_metrics(html: str) -> dict:
    return {
        "main": len(re.findall(r'<main\b', html, re.I)),
        "h1": len(re.findall(r'<h1\b', html, re.I)),
        "cards": len(re.findall(r'pc-card', html)),
        "section": len(re.findall(r'<section\b', html, re.I)),
        "anchors": len(re.findall(r'<a\s', html, re.I)),
        "nosnippet": len(re.findall(r'data-nosnippet', html)),
    }


def check_ja_classification_loss() -> None:
    """JA 分類ページ（archive.html / eras / movements）の主要コンテンツが baseline 比で
    大きく消えていないか。HTML が正本のため軽量メトリクスで明確な消失だけ拾う。
    main 領域消失・h1 消失・カード数減＝HARD、section/リンク/nosnippet 減＝WARN。
    国別は JSON 正本なので今回は対象外。"""
    baseline = _baseline_ref()
    targets = _touched_html(baseline, ["eras", "movements"])
    targets += [(rel, html) for rel, html in _touched_html(baseline, ["."])
                if os.path.basename(rel) == "archive.html"]
    for rel, work_html in targets:
        base_html = _git_show(baseline, rel)
        if base_html is None:
            continue  # 新規分類ページはブロックしない
        bm, wm = _classif_metrics(base_html), _classif_metrics(work_html)
        hard = []
        if bm["main"] > 0 and wm["main"] == 0:
            hard.append("main 領域消失")
        if bm["h1"] > 0 and wm["h1"] == 0:
            hard.append("h1 消失")
        if wm["cards"] < bm["cards"]:
            hard.append(f"カード {bm['cards']}→{wm['cards']}")
        if hard:
            hard_failures.append(
                f"[JA分類 {rel}] 主要コンテンツが消失: " + " / ".join(hard))
        warn = []
        if wm["section"] < bm["section"]:
            warn.append(f"section {bm['section']}→{wm['section']}")
        if bm["anchors"] - wm["anchors"] >= 10 and wm["anchors"] < bm["anchors"] * 0.85:
            warn.append(f"リンク {bm['anchors']}→{wm['anchors']}")
        if wm["nosnippet"] < bm["nosnippet"]:
            warn.append(f"data-nosnippet {bm['nosnippet']}→{wm['nosnippet']}")
        if warn:
            warnings.append(f"[JA分類 {rel}] 指標が減少（要確認）: " + " / ".join(warn))


def _load_intentional_replacements() -> list[dict]:
    """scripts/intentional-replacements.json を読む（無ければ空リスト・壊れていても
    フェイルオープンで空リスト＝宣言ファイルの不備で他のガードを巻き込んで壊さない）。
    各エントリ: {"slug": str, "url": str, "reason": str, "declared": "YYYY-MM-DD"}。"""
    if not INTENTIONAL_REPLACEMENTS_JSON.exists():
        return []
    try:
        data = json.loads(INTENTIONAL_REPLACEMENTS_JSON.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return data if isinstance(data, list) else []


def _filter_loss_items_by_declarations(items: list[dict], declarations: list[dict]) -> tuple[list[dict], set[int]]:
    """items（[{file, detail}]）を declarations（[{slug, url, ...}]）で絞り込む純粋関数。
    (slug, url) は「file に slug が部分一致」×「detail に url が部分一致」で判定する。
    戻り値: (remaining, consumed_indices)。remaining=宣言に一致しなかった item のみ。
    consumed_indices=実際にどれか1件以上を除外できた宣言（declarations の index 集合）。
    副作用なし（hard_failures/warnings/infos に触らない）＝ unit test しやすい形。"""
    remaining = []
    consumed: set[int] = set()
    for it in items:
        matched_idx = None
        for i, decl in enumerate(declarations):
            slug, url = decl.get("slug", ""), decl.get("url", "")
            if not slug or not url:
                continue
            if slug in it["file"] and url in it["detail"]:
                matched_idx = i
                break
        if matched_idx is not None:
            consumed.add(matched_idx)
        else:
            remaining.append(it)
    return remaining, consumed


def check_content_loss_guard() -> None:
    """写真家リーフ（JA + EN）の本文消失をブロック経路へ昇格する。
    check_content_loss.py を preflight と共通の baseline・--strict で実行し:
      - 明確な消失（出典 / 本文セクション / FIG / thesis / lead）= HARD
      - 構造不変のまま文面だけ変化した「書き換えの疑い」= WARN（ブロックしない）
    触ったファイルだけが対象なので、変更が無ければ必ずグリーン＝門にできる。
    JA 写真家 HTML（正本）の本文消失はこれまで手動チェック頼みだった穴を塞ぐ。

    scripts/intentional-replacements.json（① 意図的URL置換の宣言・使い捨て設計）:
    事実の出典/公式URLを新しい参照へ意図的に差し替えたとき、旧URLが「消失」として
    HARD FAIL するのを、宣言済み (slug, url) の項目だけスコープを絞って通す。
    (slug, url) は「file パスに slug が含まれる」×「消失 detail 文字列に url が
    部分一致する」で判定する（detail の文字列そのものに URL が出ない消失種別
    （出典件数・section数・FIG数など）は原理上マッチしない＝宣言してもすり抜けを
    防げない。URL がそのまま出る種別だけが対象）。
    自動失効は作らない：宣言を使って push しベースラインが origin/main へ進めば、
    次回 diff ではその URL はもう「消えていない」ので自然に不整合（stale）になる。
    stale 宣言は毎回 WARN で報告するので、それを見て手で削除するのがクリーンアップの
    合図（詳細は docs/generators-and-guards.md）。"""
    script = REPO / "scripts" / "check_content_loss.py"
    if not script.exists():
        return
    baseline = _baseline_ref()
    proc = subprocess.run(
        [sys.executable, str(script), "--against", baseline, "--strict"],
        capture_output=True, text=True, cwd=REPO)
    out = proc.stdout
    loss_part, _, rewrite_part = out.partition("⚠ 本文の書き換え")
    declarations = _load_intentional_replacements()
    consumed: set[int] = set()
    # 消失（HARD）— --strict は損失検知時のみ exit 1
    if proc.returncode != 0:
        items, cur = [], None
        for line in loss_part.splitlines():
            s = line.strip()
            if s.startswith("✋"):
                cur = s[1:].strip()
            elif s.startswith("−") and cur:
                items.append({"file": cur, "detail": s[1:].strip()})

        remaining, consumed = _filter_loss_items_by_declarations(items, declarations)

        if remaining:
            detail = " / ".join(f"{r['file']}（{r['detail']}）" for r in remaining[:6])
            hard_failures.append(
                "本文消失の疑い（check_content_loss・JA/EN 写真家）: " + detail
                + "。意図的でなければ正本(JA HTML / photographers-en-content.json)へ復元。"
                + "意図的な置換なら scripts/intentional-replacements.json へ宣言を追加")

    for i in consumed:
        decl = declarations[i]
        infos.append(
            f"intentional-replacement 適用: slug={decl.get('slug')} url={decl.get('url')}"
            f"（{decl.get('reason', '(理由未記入)')}・宣言日={decl.get('declared', '?')}）"
            "＝ 消失HARDから除外")
    for i, decl in enumerate(declarations):
        if i not in consumed:
            warnings.append(
                "stale intentional-replacement 宣言（今回の消失検知に一致せず・削除候補）: "
                f"slug={decl.get('slug')} url={decl.get('url')}"
                "（scripts/intentional-replacements.json）")

    # 書き換え（WARN）— 文面だけの変化。事実すり替えの疑いとして目視
    if rewrite_part.strip():
        files = [l.strip()[1:].strip() for l in rewrite_part.splitlines()
                 if l.strip().startswith("✋")]
        warnings.append(
            "本文の書き換えの疑い（構造不変のまま文面が変化・要目視）: "
            + ", ".join(files[:6])
            + "。正本(JA HTML / photographers-en-content.json・overrides.js)と一致するか確認")


def check_new_photographer_pages() -> None:
    """新規／触った JA 写真家ページの構造・cite 整合を touched-only で検査する。
    設計（[[project_new_photographer_guard]]・2026-06-19 合意）:
      - 明確な破損（決定論・既存295グリーン）だけ HARD。完成度不足は WARN。
      - SEO 欠落系・空セクション・orphan cite は既存チェック／頻出ノイズのため
        preflight では出さない（check_new_photographer.SKIP_IN_PREFLIGHT）。
      - 完成検査の本命は `check_new_photographer.py --slug <slug>`。これは網。
    """
    if cnp is None:
        return
    # 全体の決定論不変条件: card-data に id があるのにページが無い（HARD）
    try:
        miss = cnp.carddata_missing_pages()
    except Exception:  # noqa: BLE001
        miss = []
    if miss:
        hard_failures.append(
            f"card-data.json に id があるが photographers/<id>.html が不在: {miss[:8]}")
    # 触った JA 写真家ページだけ構造検査
    baseline = _baseline_ref()
    try:
        carddata = cnp.carddata_ids()
    except Exception:  # noqa: BLE001
        carddata = set()
    for rel, work_html in _touched_html(baseline, ["photographers"]):
        slug = os.path.splitext(os.path.basename(rel))[0]
        for fd in cnp.check_ja(slug, work_html):
            if fd.code in cnp.SKIP_IN_PREFLIGHT:
                continue
            if fd.level in (cnp.HARD, cnp.GATE):
                # GATE（完成ゲート）は preflight 常時では WARN に落とす
                if fd.level == cnp.HARD:
                    hard_failures.append(f"[新規写真家 {slug}] {fd.msg}")
                else:
                    warnings.append(f"[新規写真家 {slug}] {fd.msg}")
            elif fd.level == cnp.WARN:
                warnings.append(f"[新規写真家 {slug}] {fd.msg}")
        if slug not in carddata:
            warnings.append(
                f"[新規写真家 {slug}] card-data.json に未登録"
                f"（アーカイブ/星座に出ない。add_photographer.py で投入）")


def check_scaffold_inject_determinism() -> None:
    """importer scaffold-inject の決定論不変条件（M4・合格条件B）。
    構造の違う2ソースを render_ja_page に食わせ、出力が byte 同一かつ常に正典
    chrome になることを hermetic に検証する（test_importer_scaffold_inject.py）。
    決定論で現在グリーンなので HARD（素材の器が出力へ漏れたら push をブロック）。"""
    path = REPO / "scripts" / "test_importer_scaffold_inject.py"
    if not path.exists():
        return
    proc = subprocess.run([sys.executable, str(path)],
                          capture_output=True, text=True, cwd=REPO)
    if proc.returncode != 0:
        out = (proc.stdout + proc.stderr).strip()
        tail = out.splitlines()[-1] if out else "test_importer_scaffold_inject.py"
        hard_failures.append(
            "scaffold-inject の byte 一致検証が失敗（render_ja_page に素材の器が"
            f"漏れている疑い）: {tail}")


def run_existing_check(script: str) -> None:
    path = REPO / "scripts" / script
    if not path.exists():
        return
    proc = subprocess.run([sys.executable, str(path)], capture_output=True, text=True, cwd=REPO)
    out = (proc.stdout + proc.stderr).strip()
    if proc.returncode != 0:
        tail = out.splitlines()[-1] if out else script
        hard_failures.append(f"{script} が非0終了: 末尾→ {tail}\n{out}")


def check_en_lang_toggle_active() -> None:
    """EN pages must not keep the Japanese page's active JP language toggle."""
    offenders: list[str] = []
    for f in sorted((REPO / "en").rglob("*.html")):
        html = f.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r'<div class="head__lang">.*?</div>', html, flags=re.S)
        if not m:
            continue
        if re.search(r'<button[^>]*class="[^"]*\bis-active\b[^"]*"[^>]*>\s*JP\s*</button>', m.group(0)):
            offenders.append(str(f.relative_to(REPO)))
    if offenders:
        hard_failures.append(
            "ENページの言語トグルに JP active button が残存: "
            + ", ".join(offenders[:12])
            + (" …" if len(offenders) > 12 else "")
        )


def main() -> int:
    check_dup_ids_js()
    check_dup_ids_carddata()
    check_ga_coverage()
    check_en_lang_toggle_active()
    check_en_content_loss()
    check_en_changed_slug_closure()
    check_en_direct_edit()
    check_en_changed_slug_integrity()
    check_en_rel_annotations()
    check_country_en()
    check_taxonomy_en()
    check_archive_en()
    check_archive_presence()      # ③ archive 掲載漏れ（WARN）
    check_country_hero_counts()   # ③ country hero件数ズレ（WARN）
    check_content_loss_guard()
    check_seo_invisible_loss()
    check_ja_seo_holes()
    check_ja_classification_loss()
    check_new_photographer_pages()
    check_scaffold_inject_determinism()
    run_existing_check("check_photographer_link_integrity.py")

    if infos:
        print("── INFO（宣言により処理済み・ブロックしない）──")
        for i in infos:
            print("  ℹ " + i)
    if warnings:
        print("── WARN（要確認・ブロックしない）──")
        for w in warnings:
            print("  ⚠ " + w)
    if known_warnings:
        print("── WARN（既知・非ブロック / 対応不要）──")
        for w in known_warnings:
            print("  · " + w)
    if hard_failures:
        print("\n── FAIL（push をブロック）──")
        for h in hard_failures:
            print("  ✗ " + h)
        print("\npreflight: FAILED")
        return 1
    print("preflight: OK（決定論チェック全通過）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
