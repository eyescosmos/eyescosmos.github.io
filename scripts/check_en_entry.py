#!/usr/bin/env python3
"""Per-slug integrity checks for one EN photographer entry.

対象 slug だけを検査する読み取り専用ツール。JSON も HTML も書き換えない。
EN 写真家本文を直す前後に、対象ページだけを安全に点検するために使う。

検査項目:
  1. sup-ref ↔ cite-id の対応（本文の *N と出典 cite-N、保存済み配列との整合）
  2. cite-id の重複
  3. Amazon 検索結果 URL / utm_source の混入
  4. 作品・外部リンクの誤 URL（1文字アンカー・既知の誤ドメイン・空 href）
  5. Wikipedia / ブログ等の禁止出典の混入
  6. EN HTML 再生成後に JSON 宣言と一致しているか（HTML-vs-JSON closure）
  7. （任意）対象外ファイル混入の補助チェック（--git-scope）

使い方:
    python3 scripts/check_en_entry.py atget
    python3 scripts/check_en_entry.py atget --git-scope   # git 差分の混入も点検
    python3 scripts/check_en_entry.py --all               # 全 slug を検査

終了コード: FAIL があれば 1、なければ 0（WARN のみなら 0）。
"""
import argparse
import os
import re
import subprocess
import sys

import en_content

ROOT = en_content.ROOT
JSON_PATH = en_content.JSON_PATH
EN_DIR = os.path.join(ROOT, 'en', 'photographers')

# 本文系（sup-ref が出てよい場所）
BODY_FIELDS = ('lead_html', 'thesis_html')
# リンク全般を走査する場所
LINK_FIELDS = ('lead_html', 'thesis_html', 'keywords_html', 'view_works_links_html',
               'notable_works_html', 'photobooks_html', 'external_links_html',
               'further_reading_html', 'sources_html', 'site_directory_html')
# 禁止出典ドメイン（CLAUDE.md: Wikipedia 回避・信頼ソース優先）
PROHIBITED_SOURCE_DOMAINS = (
    'wikipedia.org', 'wikimedia.org', 'blogspot.', 'wordpress.com',
    'ameblo.jp', 'note.com', 'fc2.com', 'hatenablog', 'medium.com',
    'pinterest.', 'tumblr.com',
)
# EN HTML を手書きで維持している例外ページ（JSON は正本ではないので closure 検査をしない）
# - shoji-ueda: 現 EN HTML が JA ページに対応した正（本文の脚注 *1..*17 と出典が整合）。
#   JSON 側の sources_html / リンクは別系統の誤りで、本文と番号が対応しない。
#   よって JSON からの再生成は禁止（正しい HTML を壊す）。HTML を手編集で維持する。
HAND_MAINTAINED_EN = {'stieglitz.html', 'annie-leibovitz.html', 'shoji-ueda.html'}
# Amazon 検索結果・トラッキングの兆候
AMAZON_SEARCH_SIGNS = ('/s?', '/s/ref', '?k=', '&k=', 'field-keywords', '/gp/search')

SUPREF_RE = re.compile(r'href="#cite-(\d+)"')
CITE_ID_RE = re.compile(r'id="cite-(\d+)"')
ANCHOR_RE = re.compile(r'<a\b([^>]*)>(.*?)</a>', re.S)
HREF_RE = re.compile(r'href="([^"]*)"')


class Report:
    def __init__(self, slug):
        self.slug = slug
        self.fails = []
        self.warns = []

    def fail(self, msg):
        self.fails.append(msg)

    def warn(self, msg):
        self.warns.append(msg)

    def ok(self):
        return not self.fails

    def emit(self):
        head = '■ %s' % self.slug
        if not self.fails and not self.warns:
            print('%s  \033[32mOK\033[0m' % head)
            return
        print(head)
        for m in self.fails:
            print('  \033[31mFAIL\033[0m %s' % m)
        for m in self.warns:
            print('  \033[33mWARN\033[0m %s' % m)


def section_bodies(entry):
    out = []
    for f in BODY_FIELDS:
        v = entry.get(f)
        if v and v != 'None':
            out.append(v)
    for s in entry.get('sections') or []:
        b = s.get('body_html')
        if b:
            out.append(b)
    return out


def all_link_html(entry):
    chunks = list(section_bodies(entry))
    for f in LINK_FIELDS:
        v = entry.get(f)
        if v and v != 'None':
            chunks.append(v)
    return '\n'.join(chunks)


def check_cite_supref(entry, rep):
    body = '\n'.join(section_bodies(entry))
    sup_actual = [int(x) for x in SUPREF_RE.findall(body)]
    sources = entry.get('sources_html') or ''
    cite_actual = [int(x) for x in CITE_ID_RE.findall(sources)]

    # 重複 cite-id
    seen = {}
    for c in cite_actual:
        seen[c] = seen.get(c, 0) + 1
    dups = sorted(c for c, n in seen.items() if n > 1)
    if dups:
        rep.fail('cite-id が重複: %s' % dups)

    sup_set, cite_set = set(sup_actual), set(cite_actual)
    miss = sorted(sup_set - cite_set)
    if miss:
        rep.fail('本文 sup-ref *%s に対応する出典 cite-id が無い' % miss)
    orphan = sorted(cite_set - sup_set)
    if orphan:
        rep.warn('出典 cite-%s が本文 sup-ref から参照されていない（孤立）' % orphan)

    # 欠番
    if cite_set:
        gaps = sorted(set(range(1, max(cite_set) + 1)) - cite_set)
        if gaps:
            rep.warn('cite-id に欠番: %s' % gaps)

    # 保存済み配列とのズレ（生成時のスナップショットが古い兆候）
    stored_cite = set(entry.get('cite_ids') or [])
    stored_sup = set(entry.get('supref_ids') or [])
    if stored_cite and stored_cite != cite_set:
        rep.warn('保存 cite_ids %s が sources_html 実体 %s と不一致'
                 % (sorted(stored_cite), sorted(cite_set)))
    if stored_sup and stored_sup != sup_set:
        rep.warn('保存 supref_ids %s が本文実体 %s と不一致'
                 % (sorted(stored_sup), sorted(sup_set)))


def iter_anchors(html):
    for m in ANCHOR_RE.finditer(html):
        attrs, text = m.group(1), m.group(2)
        href_m = HREF_RE.search(attrs)
        href = href_m.group(1) if href_m else ''
        plain = re.sub(r'<[^>]+>', '', text).strip()
        yield href, plain


def check_links(entry, rep):
    html = all_link_html(entry)
    for href, text in iter_anchors(html):
        low = href.lower()
        # 1文字アンカー（>S</a> 事故。過去の museumangewandtekunst.de 誤リンクもこれで捕捉）
        if href.startswith('http') and len(text) <= 2 and re.fullmatch(r'[A-Za-z0-9]*', text or ''):
            rep.fail('1〜2文字アンカーの外部リンク: text=%r href=%s' % (text, href))
        # 空 href / アンカーのみ
        if href in ('', '#'):
            rep.warn('空または # の href（text=%r）' % text)
        # utm_source / トラッキング
        if 'utm_source=' in low or 'utm_medium=' in low:
            rep.fail('utm トラッキング付き URL: %s' % href)
        # Amazon 検索結果 URL（アフィリは /dp/ か /gp/product/ のはず）
        if 'amazon.' in low:
            if any(sig in low for sig in AMAZON_SEARCH_SIGNS):
                rep.fail('Amazon 検索結果 URL（/dp/ か /gp/product/ にすべき）: %s' % href)
        # 禁止出典ドメイン
        for dom in PROHIBITED_SOURCE_DOMAINS:
            if dom in low:
                rep.warn('禁止/非推奨ドメインへのリンク: %s（text=%r）' % (href, text))


def check_html_vs_json(entry, slug, rep):
    """再生成済み EN HTML が JSON 宣言と一致するか（HTML-vs-JSON closure）。"""
    if slug in HAND_MAINTAINED_EN:
        rep.warn('EN 手書き維持ページ（%s）: JSON は正本でないため closure 検査スキップ' % slug)
        return
    path = os.path.join(EN_DIR, slug)
    if not os.path.exists(path):
        rep.warn('EN HTML 未生成: en/photographers/%s（closure 検査スキップ）' % slug)
        return
    with open(path, encoding='utf-8') as fh:
        html = fh.read()

    html_cite = set(int(x) for x in CITE_ID_RE.findall(html))
    json_cite = set(int(x) for x in CITE_ID_RE.findall(entry.get('sources_html') or ''))
    if html_cite != json_cite:
        only_html = sorted(html_cite - json_cite)
        only_json = sorted(json_cite - html_cite)
        rep.fail('HTML と JSON の cite-id 集合が不一致'
                 + (' HTMLのみ:%s' % only_html if only_html else '')
                 + (' JSONのみ:%s' % only_json if only_json else ''))

    # 作品/外部リンクと Amazon リンクの集合が HTML から欠落していないか。
    # ただし禁止ドメイン（Wikipedia 等）はビルダーが意図的に落とすので closure 対象外
    # （混入自体は別途 prohibited-domain WARN で検出する）。
    def keep(h):
        low = h.lower()
        return h.startswith('http') and not any(d in low for d in PROHIBITED_SOURCE_DOMAINS)
    json_links = {h for h, _ in iter_anchors(all_link_html(entry)) if keep(h)}
    html_links = {h for h, _ in iter_anchors(html) if h.startswith('http')}
    missing = sorted(l for l in json_links if l not in html_links)
    if missing:
        rep.fail('JSON にあるが再生成 HTML に無いリンク（%d件・要EN再生成）: %s'
                 % (len(missing), missing[:5] + (['…'] if len(missing) > 5 else [])))


def check_git_scope(slug, rep):
    """対象外ファイルが git 差分に混ざっていないかの補助チェック。"""
    try:
        out = subprocess.check_output(
            ['git', 'diff', '--name-only', 'HEAD'], cwd=ROOT, text=True)
    except Exception as e:
        rep.warn('git 差分を取得できず scope チェック省略: %s' % e)
        return
    changed = [f for f in out.splitlines() if f.strip()]
    base = slug[:-5] if slug.endswith('.html') else slug
    expected = (
        'data/photographers-en-content.json',
        'en/photographers/%s' % slug,
        'photographers/%s' % slug,
        'scripts/en_entry.py', 'scripts/check_en_entry.py',
    )
    extra = [f for f in changed if f not in expected and base not in f]
    if extra:
        rep.warn('対象 slug と無関係に見える変更ファイル（混入確認）:\n    '
                 + '\n    '.join(extra))


def run_one(pages, slug, git_scope=False):
    rep = Report(slug)
    entry = pages[slug]
    check_cite_supref(entry, rep)
    check_links(entry, rep)
    check_html_vs_json(entry, slug, rep)
    if git_scope:
        check_git_scope(slug, rep)
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('slug', nargs='?', help='対象 slug（通称・.html 省略可）')
    ap.add_argument('--all', action='store_true', help='全 slug を検査')
    ap.add_argument('--git-scope', action='store_true',
                    help='git 差分に対象外ファイルが混ざっていないか補助チェック')
    args = ap.parse_args(argv)

    pages = en_content.load_pages()

    if args.all:
        n_fail = 0
        for slug in sorted(pages):
            rep = run_one(pages, slug, git_scope=False)
            if not rep.ok() or rep.warns:
                rep.emit()
            if not rep.ok():
                n_fail += 1
        print('\n%d/%d slug に FAIL' % (n_fail, len(pages)))
        return 1 if n_fail else 0

    if not args.slug:
        ap.error('slug を指定するか --all を使ってください')
    slug, cands = en_content.resolve_slug(args.slug, pages)
    if slug is None:
        if cands:
            print('slug が一意に決まりません: %s' % args.slug, file=sys.stderr)
            print('候補:', ', '.join(c[:-5] for c in cands[:15]), file=sys.stderr)
        else:
            print('slug が見つかりません: %s' % args.slug, file=sys.stderr)
        return 2
    rep = run_one(pages, slug, git_scope=args.git_scope)
    rep.emit()
    return 0 if rep.ok() else 1


if __name__ == '__main__':
    sys.exit(main())
