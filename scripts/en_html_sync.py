#!/usr/bin/env python3
"""EN 写真家ページの JA→EN 同期ツール（EN HTML が正本・2026-09-13 の HTML 正本化以降）。

既存 EN ページの更新は「EN HTML を直接編集して終わり」が正規手順になった
（`docs/en-html-canon-migration.md` §2a）。本ツールは、その手順のうち機械でやるべき部分
＝ JA からの意味データ抽出・EN HTML への決定論的な注入・日英の機械照合 を担う。
**翻訳そのものはやらない。** 翻訳は別プロセス（Codex 等）に JSON を渡して行い、
その出力を本ツールが検証して注入する。この分離が肝で、生成 HTML を翻訳側に触らせない。

初出は 2026-09-14 の5名 update バッチ（niepce / talbot / stieglitz / robertfrank / leibovitz）。
5/5 が初回で全検証を通過した。実測は `docs/importer-run-log.md` の同日の節。

  python3 scripts/en_html_sync.py extract <slug> > ja_<slug>.json
      JA ページから title / description / lead / thesis / 各節 / 出典 を抜く。
      翻訳プロセスへの入力。読み取りのみ。

  python3 scripts/en_html_sync.py check-translation ja_<slug>.json en_<slug>.json
      注入前の検証。タグ列・出典番号・URL・sup-ref 集合の一致と CJK 残存を見る。
      **必ず inject の前に通す。** 非0終了なら注入しない。

  python3 scripts/en_html_sync.py inject <slug> en_<slug>.json
      EN HTML へ注入する。書き換えるのは lead / thesis / 各節の見出しと本文 /
      §SRC / title / description / OGP / Twitter だけ。
      §WORKS・§REL・§REF・chrome・SEO の他の要素には触らない。
      節番号ラベル（§ 01 / 03）は JA から同期し、JA に無い EN 節は落とす
      （旧フォーマットで §REL を本文節として取り込んだ個体の掃除）。
      本文内の内部リンクは /photographers/ → /en/photographers/ へ機械的に寄せる。

  python3 scripts/en_html_sync.py verify <slug>
      注入後の日英照合10項目。cite集合 / dangling / 未参照cite / 節ラベル対称 /
      JAパス混入 / CJK残存 / GA / h3数 / div・section開閉。

注意（2026-09-14 に実際に踏んだもの）:
  - EN ページに `ph-thesis` ブロックが無い個体がある（robertfrank / annie-leibovitz）。
    inject は黙って飛ばすので、**verify の「未参照cite」で気づく**。手で節を足す。
  - 翻訳プロセスは出力ファイルを途中状態（`{}` や `"__CITES__"`）で書く。
    **完了判定はファイルサイズでなくプロセスの終了で見る。**
"""

import json, re, sys, html as H
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

ABSTRACT = re.compile(r'(<div class="ph-abstract">\s*<div class="ph-abstract__label">[^<]*</div>\s*<p>)(.*?)(</p>)', re.S)
THESIS   = re.compile(r'(<p class="ph-thesis__body[^"]*">)(.*?)(</p>)', re.S)
SEC      = re.compile(r'<section class="ph-section" id="(sec-\d+)">(.*?)</section>', re.S)
SEC_NAME = re.compile(r'(<span class="ph-section__name">)(.*?)(</span>)', re.S)
SEC_NUM  = re.compile(r'(<span class="ph-section__num">)(.*?)(</span>)', re.S)
SEC_BODY = re.compile(r'(<div class="ph-section__body">)(.*?)(</div>\s*</section>)', re.S)
CITE     = re.compile(r'<div class="ph-cite" id="cite-(\d+)"><span class="ph-cite__num">\*\d+</span><span>(.*?)</span></div>', re.S)
TITLE    = re.compile(r'<title>(.*?)</title>', re.S)
DESC     = re.compile(r'<meta name="description" content="([^"]*)"')

def read(p): return (ROOT/p).read_text(encoding="utf-8")
def write(p, s): (ROOT/p).write_text(s, encoding="utf-8")

def ja_sections(h):
    out = []
    for sid, inner in SEC.findall(h):
        name = SEC_NAME.search(inner)
        num = SEC_NUM.search(inner)
        body = SEC_BODY.search(inner + "</section>")
        out.append({"id": sid,
                    "name": name.group(2) if name else "",
                    "num": num.group(2).strip() if num else "",
                    "body_html": body.group(2).strip() if body else ""})
    return out

def cmd_extract(slug):
    h = read(f"photographers/{slug}.html")
    a = ABSTRACT.search(h); t = THESIS.search(h)
    data = {
        "slug": slug,
        "title_ja": H.unescape(TITLE.search(h).group(1)),
        "description_ja": H.unescape(DESC.search(h).group(1)),
        "lead_html": a.group(2).strip() if a else "",
        "thesis_html": t.group(2).strip() if t else "",
        "sections": ja_sections(h),
        "cites": [{"num": int(n), "html": c.strip()} for n, c in CITE.findall(h)],
    }
    print(json.dumps(data, ensure_ascii=False, indent=1))

def relink(s):
    """本文内の内部リンクを EN へ寄せる。"""
    s = re.sub(r'href="/photographers/', 'href="/en/photographers/', s)
    s = re.sub(r'href="/movements/([^"]+)\.html"', lambda m: 'href="/en/movements/%s.html"' % MOV.get(m.group(1), m.group(1)), s)
    return s

try:
    sys.path.insert(0, str(ROOT/"scripts"))
    from build_taxonomy_en import STUB_TO_SLUG as MOV
except Exception:
    MOV = {}

def cmd_inject(slug, tpath):
    tr = json.loads(Path(tpath).read_text(encoding="utf-8"))
    p = f"en/photographers/{slug}.html"
    h = read(p)
    if tr.get("lead_html"):
        h = ABSTRACT.sub(lambda m: m.group(1) + relink(tr["lead_html"]) + m.group(3), h, count=1)
    if tr.get("thesis_html"):
        h = THESIS.sub(lambda m: m.group(1) + relink(tr["thesis_html"]) + m.group(3), h, count=1)
    by_id = {s["id"]: dict(s) for s in tr.get("sections", [])}
    # 節番号ラベル（§ 01 / 03 など）は言語非依存なので JA 正本から取る。
    for js in ja_sections(read(f"photographers/{slug}.html")):
        if js["id"] in by_id:
            by_id[js["id"]]["num"] = js.get("num", "")
    def sec_sub(m):
        sid, inner = m.group(1), m.group(2)
        s = by_id.get(sid)
        if not s:
            return m.group(0)
        if s.get("num"):
            inner = SEC_NUM.sub(lambda n: n.group(1) + s["num"] + n.group(3), inner, count=1)
        if s.get("name"):
            inner = SEC_NAME.sub(lambda n: n.group(1) + s["name"] + n.group(3), inner, count=1)
        if s.get("body_html"):
            inner = SEC_BODY.sub(lambda b: b.group(1) + "\n" + relink(s["body_html"]) + "\n        " + b.group(3).replace("</section>", ""),
                                 inner + "</section>", count=1)
            inner = inner[:-len("</section>")] if inner.endswith("</section>") else inner
        return '<section class="ph-section" id="%s">%s</section>' % (sid, inner)
    h = SEC.sub(sec_sub, h)
    # JA に無い EN 本文節は旧フォーマットの残骸（§REL を節として取り込んだ個体など）。落とす。
    if by_id:
        def drop(m):
            return "" if m.group(1) not in by_id else m.group(0)
        h = re.sub(r'\s*<section class="ph-section" id="(sec-\d+)">.*?</section>', drop, h, flags=re.S)
    if tr.get("cites"):
        want = {c["num"]: c["html"] for c in tr["cites"]}
        block = "".join('<div class="ph-cite" id="cite-%d"><span class="ph-cite__num">*%d</span><span>%s</span></div>'
                        % (n, n, want[n]) for n in sorted(want))
        h = re.sub(r'(<div class="ph-sources">)(.*?)(</div>\s*</div>\s*</section>)',
                   lambda m: m.group(1) + block + m.group(3), h, count=1, flags=re.S)
    if tr.get("title"):
        h = TITLE.sub(lambda m: "<title>%s</title>" % tr["title"], h, count=1)
        h = re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1)+H.escape(tr["title"],quote=True)+m.group(2), h, count=1)
        h = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")', lambda m: m.group(1)+H.escape(tr["title"],quote=True)+m.group(2), h, count=1)
    if tr.get("description"):
        d = H.escape(tr["description"], quote=True)
        for pat in (r'(<meta name="description" content=")[^"]*(")',
                    r'(<meta property="og:description" content=")[^"]*(")',
                    r'(<meta name="twitter:description" content=")[^"]*(")'):
            h = re.sub(pat, lambda m: m.group(1)+d+m.group(2), h, count=1)
    write(p, h)
    print("injected:", p)

def cmd_verify(slug):
    ja = read(f"photographers/{slug}.html"); en = read(f"en/photographers/{slug}.html")
    def ids(h): return {int(x) for x in re.findall(r'id="cite-(\d+)"', h)}
    def refs(h): return {int(x) for x in re.findall(r'href="#cite-(\d+)"', h)}
    def labels(h): return sorted(re.sub(r'\s+','',re.sub(r'<[^>]+>','',x)).upper() for x in re.findall(r'ph-section__num">(.*?)</span>', h, re.S))
    def cjk(h):
        body = h[h.find('§ 01'):h.find('§ REL')]
        body = re.sub(r'<[^>]+>','',body)
        n = len(re.findall(r'[぀-ヿ一-鿿]', body))
        return n
    ok = True
    def chk(name, cond, detail=""):
        nonlocal ok
        print(("  OK  " if cond else "  FAIL") + f" {name} {detail}")
        if not cond: ok = False
    chk("cite集合 JA==EN", ids(ja)==ids(en), f"JA{len(ids(ja))} EN{len(ids(en))} 差={sorted(ids(ja)^ids(en))[:5]}")
    chk("EN dangling なし", not (refs(en)-ids(en)), sorted(refs(en)-ids(en))[:5])
    chk("EN 未参照cite なし", not (ids(en)-refs(en)), sorted(ids(en)-refs(en))[:5])
    chk("節ラベル JA==EN", labels(ja)==labels(en), f"JA{labels(ja)} EN{labels(en)}")
    chk("EN本文にJAパス無し", not re.findall(r'href="/photographers/', en[en.find('§ 01'):en.find('§ SRC')]))
    chk("EN本文にCJK残存なし", cjk(en)==0, f"{cjk(en)}字")
    chk("EN GA", en.count('G-2VRTV8BZEJ')==2)
    chk("EN h3数 JA==EN", len(re.findall(r'<h3',ja))==len(re.findall(r'<h3',en)), f"JA{len(re.findall(r'<h3',ja))} EN{len(re.findall(r'<h3',en))}")
    chk("EN div開閉", en.count('<div')==en.count('</div>'), f"{en.count('<div')}/{en.count('</div>')}")
    chk("EN section開閉", en.count('<section')==en.count('</section>'))
    return 0 if ok else 1


def cmd_check_translation(ja_path, en_path):
    """翻訳 JSON が JA と構造一致しているかを注入前に検証する。"""
    ja=json.load(open(ja_path,encoding='utf-8')); en=json.load(open(en_path,encoding='utf-8'))
    fails=[]
    def chk(name,cond,detail=""):
        print(("  OK  " if cond else "  FAIL")+f" {name} {detail}")
        if not cond: fails.append(name)
    CJK=re.compile(r'[぀-ヿ一-鿿]')
    def tags(s): return re.findall(r'<[^>]+>',s)
    chk("sections数", len(ja['sections'])==len(en['sections']), f"{len(ja['sections'])}/{len(en['sections'])}")
    chk("section id順", [s['id'] for s in ja['sections']]==[s['id'] for s in en['sections']])
    chk("cites数", len(ja['cites'])==len(en['cites']), f"{len(ja['cites'])}/{len(en['cites'])}")
    chk("cite番号一致", [c['num'] for c in ja['cites']]==[c['num'] for c in en['cites']])
    ju=[re.findall(r'href="([^"]+)"',c['html']) for c in ja['cites']]
    eu=[re.findall(r'href="([^"]+)"',c['html']) for c in en['cites']]
    chk("cite URL一致", ju==eu, f"差分{sum(1 for a,b in zip(ju,eu) if a!=b)}件")
    for key in ('lead_html','thesis_html'):
        chk(f"{key} タグ列一致", tags(ja[key])==tags(en[key]), f"{len(tags(ja[key]))}/{len(tags(en[key]))}")
        chk(f"{key} CJK無し", not CJK.search(re.sub(r'<[^>]+>','',en[key])))
    for a,b in zip(ja['sections'],en['sections']):
        chk(f"{a['id']} タグ列一致", tags(a['body_html'])==tags(b['body_html']), f"{len(tags(a['body_html']))}/{len(tags(b['body_html']))}")
        chk(f"{a['id']} CJK無し", not CJK.search(re.sub(r'<[^>]+>','',b['body_html'])))
        chk(f"{a['id']} 名前CJK無し", not CJK.search(b['name']), b['name'])
    allen=" ".join([en['lead_html'],en['thesis_html']]+[s['body_html'] for s in en['sections']])
    allja=" ".join([ja['lead_html'],ja['thesis_html']]+[s['body_html'] for s in ja['sections']])
    chk("sup-ref番号集合一致", sorted(re.findall(r'href="#cite-(\d+)"',allja))==sorted(re.findall(r'href="#cite-(\d+)"',allen)))
    chk("title 有", bool(en.get('title')) and not CJK.search(en['title']), en.get('title','')[:70])
    chk("description 有", bool(en.get('description')) and not CJK.search(en['description']), str(len(en.get('description','')))+"字")
    print("RESULT:", "PASS" if not fails else f"FAIL {fails}")
    return 0 if not fails else 1

if __name__ == "__main__":
    c = sys.argv[1]
    if c == "extract": cmd_extract(sys.argv[2])
    elif c == "inject": cmd_inject(sys.argv[2], sys.argv[3])
    elif c == "verify": sys.exit(cmd_verify(sys.argv[2]))
    elif c == "check-translation": sys.exit(cmd_check_translation(sys.argv[2], sys.argv[3]))
    else:
        sys.stderr.write(__doc__ + "\n"); sys.exit(2)
