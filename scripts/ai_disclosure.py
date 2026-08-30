#!/usr/bin/env python3
"""AI開示ブロック — 全ページ共通の正本。

このモジュールが開示ブロックの唯一の正本。ブロックを直すときは必ずここを直し、
`python3 scripts/inject_ai_disclosure.py` で全ページへ再適用する。個別HTMLを直接
書き換えると、次回の再適用で戻る。

- マーカー `<!-- AI-DISCLOSURE -->` … `<!-- /AI-DISCLOSURE -->` で括る（冪等）
- 挿入位置: 最後の `</main>` の直前。`</main>` が無いページは `<footer` の直前
  （写真家ページでは §SRC セクションの直後、その他では最終セクションの直後にあたる）
- ページ側の共通CSSに依存しないよう、スタイルはインラインで完結させる
  （写真家ページはCSSがHTML内に埋め込まれており、共通stylesheetが無いページもあるため）
"""

MARKER_OPEN = '<!-- AI-DISCLOSURE -->'
MARKER_CLOSE = '<!-- /AI-DISCLOSURE -->'

_WRAP = (
    'margin:32px 0 0;padding:16px 0 0;'
    'border-top:1px solid var(--rule,#c4bcb0);'
    'color:var(--text-mute,#8a8478);'
)
_LINE = (
    'margin:0;'
    "font-family:var(--font-mo,var(--font-mono,'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace));"
    'font-size:10.5px;line-height:2;letter-spacing:0.08em;'
)
_NOTE = 'margin:12px 0 0;font-size:11.5px;line-height:1.95;max-width:52em;'

_ROLES = {
    'ja': [
        ('出典', '美術館・アーカイブ・専門資料（このページの §SRC に個別記載）'),
        ('本文執筆', 'AI'),
        ('構成・編集', '写真の座標 管理人'),
    ],
    'en': [
        ('Sources', 'museums, archives, and specialist literature '
                    '(listed individually in § SRC on this page)'),
        ('Text written by', 'AI'),
        ('Structure &amp; editing', 'the editor of Photo Coordinates'),
    ],
}

_NOTE_TEXT = {
    'ja': (
        '資料の収集と本文の執筆はAIが行い、構成と編集は管理人が行っています。'
        '事実関係は管理人がAIを用いて最終チェックしていますが、誤りが残っている可能性があります。'
        '正確さが必要な場合は、各ページ §SRC の一次資料をご確認ください。'
    ),
    'en': (
        'Source gathering and the writing of the text are done by AI; the structure and '
        'editing are handled by the site’s editor. Factual details are given a final '
        'check by the editor using AI, but errors may remain. If you need accuracy, please '
        'consult the primary sources listed in § SRC on each page.'
    ),
}


def block(lang='ja', indent='      '):
    """開示ブロックのHTMLを返す。lang は 'ja' / 'en'。"""
    lang = 'en' if lang == 'en' else 'ja'
    i = indent
    out = [f'{i}{MARKER_OPEN}',
           f'{i}<div class="ai-disclosure" data-nosnippet style="{_WRAP}">']
    for label, value in _ROLES[lang]:
        out.append(f'{i}  <p style="{_LINE}">{label} — {value}</p>')
    out.append(f'{i}  <p style="{_NOTE}">{_NOTE_TEXT[lang]}</p>')
    out.append(f'{i}</div>')
    out.append(f'{i}{MARKER_CLOSE}')
    return '\n'.join(out)


def has_block(html):
    return MARKER_OPEN in html


def strip_block(html):
    """既存ブロックを取り除く。_insert の厳密な逆操作（無ければそのまま返す）。"""
    while MARKER_OPEN in html:
        s = html.index(MARKER_OPEN)
        while s > 0 and html[s - 1] in ' \t':
            s -= 1
        e = html.index(MARKER_CLOSE, s) + len(MARKER_CLOSE)
        if e < len(html) and html[e] == '\n':
            e += 1
        html = html[:s] + html[e:]
    return html


def ensure(html, lang='ja', indent='      '):
    """ブロックを1つだけ持つHTMLを返す。(html, action) を返す。

    action は 'inserted' / 'updated' / 'unchanged' / 'no-anchor'。
    """
    blk = block(lang, indent)
    if MARKER_OPEN in html:
        current = html[html.index(MARKER_OPEN):html.index(MARKER_CLOSE) + len(MARKER_CLOSE)]
        stripped = strip_block(html)
        new = _insert(stripped, blk)
        if new is None:
            return html, 'no-anchor'
        if current.strip() == blk.strip() and new == html:
            return html, 'unchanged'
        return new, 'updated'
    new = _insert(html, blk)
    if new is None:
        return html, 'no-anchor'
    return new, 'inserted'


def _insert(html, blk):
    """最後の </main> の直前、無ければ <footer の直前に挿入する。

    アンカー行の行頭インデントまで戻ってから差し込むので、strip_block で
    1バイト残さず元へ戻せる（注入スクリプトの安全確認がこれに依存している）。
    """
    idx = html.rfind('</main>')
    if idx == -1:
        idx = html.find('<footer')
    if idx == -1:
        return None
    j = idx
    while j > 0 and html[j - 1] in ' \t':
        j -= 1
    return html[:j] + blk + '\n' + html[j:]
