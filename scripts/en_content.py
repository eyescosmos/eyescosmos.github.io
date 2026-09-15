#!/usr/bin/env python3
"""EN 写真家 HTML 系ツールの共通ヘルパー。

en_entry.py / check_en_entry.py / preflight.py から共有して使う。
HTML は書き換えない（読み取り専用）。

主な提供物:
    load_en_page_keys()       -> 実在する en/photographers/*.html のファイル名
    is_shim(key)              -> meta-refresh shim なら True
    shim_target(key)          -> shim の転送先 EN ファイル名
    resolve_slug(arg, universe) -> (slug | None, candidates)
        短い通称（atget→eugene-atget）や .html 有無を吸収して slug を解決する。
        厳密に1つへ決まるときだけ slug を返し、複数候補なら None と候補一覧を返す。

既存・新規とも EN 写真家ページの正本は HTML 自身。
"""
import os
import re
from html.parser import HTMLParser
from urllib.parse import unquote, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN_DIR = os.path.join(ROOT, 'en', 'photographers')
GA_ID = 'G-2VRTV8BZEJ'


def load_en_page_keys():
    """実在する EN 写真家 HTML のファイル名を sorted list で返す。"""
    return sorted(
        name for name in os.listdir(EN_DIR)
        if name.endswith('.html') and os.path.isfile(os.path.join(EN_DIR, name))
    )


class _RefreshMetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.content = None

    def handle_starttag(self, tag, attrs):
        if self.content is not None or tag.lower() != 'meta':
            return
        values = {k.lower(): (v or '') for k, v in attrs}
        if values.get('http-equiv', '').lower() == 'refresh':
            self.content = values.get('content', '')


def _shim_refresh_content(key):
    path = os.path.join(EN_DIR, key)
    try:
        with open(path, encoding='utf-8') as fh:
            head = fh.read(4096)
    except (OSError, UnicodeError):
        return None
    parser = _RefreshMetaParser()
    parser.feed(head)
    return parser.content


def is_shim(key):
    """ファイル先頭に meta-refresh がある EN shim なら True。"""
    return _shim_refresh_content(key) is not None


def shim_target(key):
    """meta-refresh shim の転送先 EN ファイル名を返す。取得不能なら None。"""
    content = _shim_refresh_content(key)
    if content is None:
        return None
    match = re.search(r'(?:^|;)\s*url\s*=\s*["\']?([^"\';\s]+)', content, re.I)
    if not match:
        return None
    path = unquote(urlparse(match.group(1)).path)
    marker = '/en/photographers/'
    if marker not in path:
        return None
    target = path.rsplit('/', 1)[-1]
    return target if target.endswith('.html') else None


def load_en_html(key):
    """実在する EN 写真家 HTML を読む。"""
    with open(os.path.join(EN_DIR, key), encoding='utf-8', errors='replace') as fh:
        return fh.read()


def _clean_text(parts):
    return re.sub(r'\s+', ' ', ''.join(parts)).strip()


class _EnHtmlSummaryParser(HTMLParser):
    """EN HTML の意味ブロックと必須SEO値だけを抽出する。"""

    VOID_TAGS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.main_depth = None
        self.abstract_depth = None
        self.captures = []
        self.title = ''
        self.description = ''
        self.canonical = ''
        self.hreflang = []
        self.og_image = ''
        self.lead_segments = []
        self.thesis = ''
        self.section_nums = []
        self.section_names = []
        self.cite_ids = []
        self.links = []

    @staticmethod
    def _attrs(attrs):
        return {str(k).lower(): (v or '') for k, v in attrs}

    def _capture(self, kind, tag, depth, value=None):
        self.captures.append({
            'kind': kind, 'tag': tag, 'depth': depth, 'parts': [], 'value': value})

    def _process_tag(self, tag, attrs, depth):
        values = self._attrs(attrs)
        classes = set(values.get('class', '').split())

        if tag == 'meta':
            if values.get('name', '').lower() == 'description' and not self.description:
                self.description = values.get('content', '')
            if values.get('property', '').lower() == 'og:image' and not self.og_image:
                self.og_image = values.get('content', '')
        elif tag == 'link':
            rels = set(values.get('rel', '').lower().split())
            if 'canonical' in rels and not self.canonical:
                self.canonical = values.get('href', '')
            lang = values.get('hreflang', '')
            if 'alternate' in rels and lang:
                self.hreflang.append((lang, values.get('href', '')))

        cite_id = values.get('id', '')
        match = re.fullmatch(r'cite-(\d+)', cite_id)
        if match:
            self.cite_ids.append(int(match.group(1)))

        if tag == 'title':
            self._capture('title', tag, depth)
        if tag == 'main':
            self.main_depth = depth
        if 'ph-abstract' in classes:
            self.abstract_depth = depth
        if (tag == 'p' and self.abstract_depth is not None
                and depth >= self.abstract_depth):
            self._capture('lead', tag, depth)
        if 'ph-thesis__body' in classes:
            self._capture('thesis', tag, depth)
        if 'ph-section__num' in classes:
            self._capture('section_num', tag, depth)
        if 'ph-section__name' in classes:
            self._capture('section_name', tag, depth)
        if tag == 'a' and self.main_depth is not None and depth > self.main_depth:
            self._capture('link', tag, depth, values.get('href', ''))

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in self.VOID_TAGS:
            self._process_tag(tag, attrs, len(self.stack) + 1)
            return
        self.stack.append(tag)
        self._process_tag(tag, attrs, len(self.stack))

    def handle_startendtag(self, tag, attrs):
        self._process_tag(tag.lower(), attrs, len(self.stack) + 1)

    def handle_data(self, data):
        for capture in self.captures:
            capture['parts'].append(data)

    def handle_endtag(self, tag):
        tag = tag.lower()
        depth = len(self.stack)
        closes_current = bool(self.stack and tag == self.stack[-1])
        finished = [c for c in self.captures
                    if c['tag'] == tag and c['depth'] == depth]
        for capture in finished:
            value = _clean_text(capture['parts'])
            kind = capture['kind']
            if kind == 'title':
                self.title = value
            elif kind == 'lead' and value:
                self.lead_segments.append(value)
            elif kind == 'thesis':
                self.thesis = value
            elif kind == 'section_num':
                self.section_nums.append(value)
            elif kind == 'section_name':
                self.section_names.append(value)
            elif kind == 'link':
                self.links.append({'href': capture['value'], 'text': value})
            self.captures.remove(capture)

        if self.abstract_depth == depth and closes_current:
            self.abstract_depth = None
        if self.main_depth == depth and closes_current:
            self.main_depth = None
        if self.stack:
            self.stack.pop()


def extract_en_summary(html):
    """EN HTML から表示用の意味ブロックとSEO必須値を抽出する。"""
    parser = _EnHtmlSummaryParser()
    parser.feed(html)
    count = max(len(parser.section_nums), len(parser.section_names))
    sections = []
    for index in range(count):
        sections.append({
            'num': parser.section_nums[index] if index < len(parser.section_nums) else '',
            'name': parser.section_names[index] if index < len(parser.section_names) else '',
        })
    return {
        'lead': ' '.join(parser.lead_segments),
        'thesis': parser.thesis,
        'sections': sections,
        'cite_count': len(parser.cite_ids),
        'cite_ids': parser.cite_ids,
        'links': parser.links,
        'seo': {
            'title': parser.title,
            'description': parser.description,
            'canonical': parser.canonical,
            'hreflang': parser.hreflang,
            'og:image': parser.og_image,
            'GA': GA_ID if GA_ID in html else '(missing)',
        },
    }


def _stem(slug):
    return slug[:-5] if slug.endswith('.html') else slug


def resolve_slug(arg, pages):
    """ユーザ入力 arg を実 slug（'eugene-atget.html'）へ解決する。

    返り値 (slug, candidates):
      - 一意に決まれば (slug, [slug])
      - 決まらなければ (None, sorted(candidates))  ※候補ゼロのときは (None, [])

    解決の優先順位:
      0. '<arg>.html' がそのまま存在（.html 有無は吸収）
      1. 語境界一致: stem が arg と完全一致 / '-arg' で終わる / 'arg-' で始まる
         （atget→eugene-atget, cameron→julia-margaret-cameron 等）
      2. 部分一致: stem に arg を含む（robertfrank で 'frank' を拾う等）
    各段で候補が1つなら解決、複数なら候補一覧を返して終了。
    """
    arg = (arg or '').strip()
    base = _stem(arg).lower()
    if not base:
        return None, []

    # 0. 直接一致（.html 有無を吸収）
    direct = base + '.html'
    if direct in pages:
        return direct, [direct]
    # 念のため大小無視の直接一致
    for k in pages:
        if k.lower() == direct:
            return k, [k]

    stems = {k: _stem(k).lower() for k in pages}

    # 1. 語境界一致
    tier1 = sorted(k for k, st in stems.items()
                   if st == base or st.endswith('-' + base) or st.startswith(base + '-'))
    if len(tier1) == 1:
        return tier1[0], tier1
    if len(tier1) > 1:
        return None, tier1

    # 2. 部分一致
    tier2 = sorted(k for k, st in stems.items() if base in st)
    if len(tier2) == 1:
        return tier2[0], tier2
    return None, tier2
