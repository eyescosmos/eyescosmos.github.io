#!/usr/bin/env python3
"""Per-slug integrity checks for one EN photographer HTML page.

対象 slug の EN HTML だけを検査する読み取り専用ツール。HTML は書き換えない。
EN 写真家本文を直す前後に、対象ページだけを安全に点検するために使う。

検査項目:
  1. <main> 内の sup-ref ↔ cite-id の対応
  2. <main> 内の Amazon 検索結果 URL / utm_source の混入
  3. <main> 内の作品・外部リンクの誤 URL（1文字アンカー・既知の誤ドメイン・空 href）
  4. <main> 内の Wikipedia / ブログ等の禁止出典の混入
  5. shim の転送先 EN 実ページの存在
  6. （任意）対象外ファイル混入の補助チェック（--git-scope）

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
EN_DIR = os.path.join(ROOT, 'en', 'photographers')

# 禁止出典ドメイン（CLAUDE.md: Wikipedia 回避・信頼ソース優先）
PROHIBITED_SOURCE_DOMAINS = (
    'wikipedia.org', 'wikimedia.org', 'blogspot.', 'wordpress.com',
    'ameblo.jp', 'note.com', 'fc2.com', 'hatenablog', 'medium.com',
    'pinterest.', 'tumblr.com',
)
# Amazon 検索結果・トラッキングの兆候
AMAZON_SEARCH_SIGNS = ('/s?', '/s/ref', '?k=', '&k=', 'field-keywords', '/gp/search')

SUPREF_RE = re.compile(r'href="#cite-(\d+)"')
CITE_ID_RE = re.compile(r'id="cite-(\d+)"')
ANCHOR_RE = re.compile(r'<a\b([^>]*)>(.*?)</a>', re.S)
HREF_RE = re.compile(r'href="([^"]*)"')
MAIN_RE = re.compile(r'<main\b[^>]*>(.*?)</main>', re.S | re.I)
SECTION_RE = re.compile(r'<section\b[^>]*>.*?</section>', re.S | re.I)
SRC_LABEL_RE = re.compile(
    r'<span\b[^>]*class="[^"]*\bph-section__num\b[^"]*"[^>]*>\s*§\s*SRC\s*</span>',
    re.S | re.I)


class Report:
    def __init__(self, slug):
        self.slug = slug
        self.fails = []
        self.warns = []
        self.ok_detail = ''

    def fail(self, msg):
        self.fails.append(msg)

    def warn(self, msg):
        self.warns.append(msg)

    def ok(self):
        return not self.fails

    def emit(self):
        head = '■ %s' % self.slug
        if not self.fails and not self.warns:
            detail = ('  %s' % self.ok_detail) if self.ok_detail else ''
            print('%s  \033[32mOK\033[0m%s' % (head, detail))
            return
        print(head)
        for m in self.fails:
            print('  \033[31mFAIL\033[0m %s' % m)
        for m in self.warns:
            print('  \033[33mWARN\033[0m %s' % m)


def main_html(html):
    """サイト共通 chrome を除いた <main> の内側を返す。"""
    match = MAIN_RE.search(html)
    return match.group(1) if match else ''


def check_cite_supref(html, rep):
    sources = next((section for section in SECTION_RE.findall(html)
                    if SRC_LABEL_RE.search(section)), '')
    body = html.replace(sources, '', 1) if sources else html
    sup_actual = [int(x) for x in SUPREF_RE.findall(body)]
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


def iter_anchors(html):
    for m in ANCHOR_RE.finditer(html):
        attrs, text = m.group(1), m.group(2)
        href_m = HREF_RE.search(attrs)
        href = href_m.group(1) if href_m else ''
        plain = re.sub(r'<[^>]+>', '', text).strip()
        yield href, plain


def check_links(html, rep):
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
        'en/photographers/%s' % slug,
        'photographers/%s' % slug,
        'scripts/en_entry.py', 'scripts/check_en_entry.py',
    )
    extra = [f for f in changed if f not in expected and base not in f]
    if extra:
        rep.warn('対象 slug と無関係に見える変更ファイル（混入確認）:\n    '
                 + '\n    '.join(extra))


def run_one(slug, git_scope=False):
    rep = Report(slug)
    path = os.path.join(EN_DIR, slug)
    if en_content.is_shim(slug):
        target = en_content.shim_target(slug)
        target_path = os.path.join(EN_DIR, target) if target else ''
        if not target:
            rep.fail('shim の転送先 EN ファイル名を取得できない')
        elif not os.path.isfile(target_path):
            rep.fail('shim の転送先 EN 実ページが存在しない: %s' % target)
        elif en_content.is_shim(target):
            rep.fail('shim の転送先が EN 実ページではない: %s' % target)
        else:
            rep.ok_detail = 'shim 転送先 EN 実ページが存在: %s' % target
    else:
        with open(path, encoding='utf-8', errors='replace') as fh:
            html = fh.read()
        body = main_html(html)
        check_cite_supref(body, rep)
        check_links(body, rep)
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

    page_keys = en_content.load_en_page_keys()

    if args.all:
        n_fail = 0
        for slug in page_keys:
            rep = run_one(slug, git_scope=False)
            if not rep.ok() or rep.warns:
                rep.emit()
            if not rep.ok():
                n_fail += 1
        print('\n%d/%d slug に FAIL' % (n_fail, len(page_keys)))
        return 1 if n_fail else 0

    if not args.slug:
        ap.error('slug を指定するか --all を使ってください')
    slug, cands = en_content.resolve_slug(args.slug, page_keys)
    if slug is None:
        if cands:
            print('slug が一意に決まりません: %s' % args.slug, file=sys.stderr)
            print('候補:', ', '.join(c[:-5] for c in cands[:15]), file=sys.stderr)
        else:
            print('slug が見つかりません: %s' % args.slug, file=sys.stderr)
        return 2
    rep = run_one(slug, git_scope=args.git_scope)
    rep.emit()
    return 0 if rep.ok() else 1


if __name__ == '__main__':
    sys.exit(main())
