#!/usr/bin/env python3
"""コロフォン（制作方針）ページを生成する。

  python3 scripts/build_colophon.py

`privacy-policy.html` / `en/privacy-policy.html` の chrome（ヘッダー・ヒーロー・フッター・
検索・GA・SEOタグ一式）を型として使い、本文だけ差し替える。出力は

  colophon/index.html      → /colophon
  en/colophon/index.html   → /en/colophon

ディレクトリ + index.html にしているのは、サイト全ページのフッターが拡張子なしの
`/colophon` を指しているため。ディレクトリindexなら拡張子なしURLが確実に解決する。

本文（3行 + 制作方針の3段落）は scripts/ai_disclosure.py と同じ内容を人が読む形に
展開したもの。文面を直すときは両方そろえる。
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ai_disclosure as d

ROOT = Path(__file__).resolve().parent.parent

ROLE_LINE = (
    'margin:0;'
    "font-family:var(--font-mo,var(--font-mono,'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace));"
    'font-size:11px;line-height:2.1;letter-spacing:0.08em;color:var(--text-mute,#8a8478);'
)
ROLE_WRAP = 'margin:0 0 22px;padding:14px 0;border-top:1px solid var(--rule,#c4bcb0);border-bottom:1px solid var(--rule,#c4bcb0);'

BODY = {
    'ja': {
        'title': '写真の座標 | コロフォン（制作方針）',
        'desc': '「写真の座標」の制作方針。資料の収集と本文の執筆はAIが行い、構成と編集は管理人が行っています。'
                '事実確認の方法と、記事を読むときに注意していただきたい点をまとめています。',
        'crumbs': '<em>SITE</em><span class="sep">/</span>コロフォン <span class="sep">·</span>Colophon '
                  '<span class="sep">·</span>UPDATED&nbsp;<span class="updated-date">2026.08</span>',
        'art_label': 'DOCUMENT · コロフォン',
        'art_year': 'C<span>O</span>',
        'eyebrow': '§ — Editorial Policy — 制作方針',
        'h1': 'コロフォン',
        'period': 'Colophon',
        'lead': 'このページでは、写真の座標の記事がどのように作られているか、事実関係をどう確認しているか、'
                'そして読むときに注意していただきたい点をまとめています。',
        'meta_row': [('Updated', '2026.08'), ('Site', '写真の座標'), ('Type', 'Policy')],
        'sec_name': '制作方針',
        'paras': [
            'このサイトの記事は、美術館・アーカイブ・専門資料をもとに作っています。資料の収集はAIが行い、'
            '管理人が決めた構成にそって本文の執筆もAIが行い、編集は管理人が行っています。'
            '生没年・経歴・展覧会歴といった事実関係については、管理人がAIを用いて最終チェックを行っています。',
            '参照した資料は、各ページの §SRC に個別に記載しています。記事の内容に疑問を持たれたときは、'
            'まずそちらをご覧ください。一次資料にあたれるよう、可能な限り美術館・アーカイブの該当ページへ'
            '直接リンクしています。',
            '<strong>こうした工程を経てなお、事実に誤りが残っている可能性があります。</strong>'
            '特に年代・地名・人名の表記、作品の制作年や所蔵先は誤りの生じやすい箇所です。'
            '調査や執筆など、正確さが必要な用途で参照される場合は、必ず §SRC の一次資料でご確認ください。',
        ],
    },
    'en': {
        'title': 'Photo Coordinates | Colophon (Editorial Policy)',
        'desc': 'The editorial policy of Photo Coordinates. Source gathering and the writing of the text '
                'are done by AI; the structure and editing are handled by the site’s editor. '
                'How facts are checked, and what to keep in mind when reading.',
        'crumbs': '<em>SITE</em><span class="sep">/</span>Colophon '
                  '<span class="sep">·</span>UPDATED&nbsp;<span class="updated-date">2026.08</span>',
        'art_label': 'DOCUMENT · COLOPHON',
        'art_year': 'C<span>O</span>',
        'eyebrow': '§ — Editorial Policy',
        'h1': 'Colophon',
        'period': 'Editorial Policy',
        'lead': 'This page explains how the articles on Photo Coordinates are made, how factual details '
                'are checked, and what to keep in mind when reading them.',
        'meta_row': [('Updated', '2026.08'), ('Site', 'Photo Coordinates'), ('Type', 'Policy')],
        'sec_name': 'Editorial Policy',
        'paras': [
            'The articles on this site are built from museum, archive, and specialist sources. '
            'Source gathering is done by AI; the text is also written by AI, following a structure '
            'decided by the site’s editor, and the editing is done by the editor. Factual details such '
            'as dates of birth and death, biography, and exhibition history are given a final check by '
            'the editor using AI.',
            'The sources consulted are listed individually in the § SRC section of each page. If you '
            'have any doubt about what an article says, please look there first. Wherever possible we '
            'link directly to the relevant museum or archive page so that you can consult the primary '
            'source yourself.',
            '<strong>Even after this process, factual errors may remain.</strong> Dates, place names, '
            'the spelling of personal names, and the year or holding institution of a given work are '
            'especially prone to error. If you are referring to this site for research, writing, or any '
            'other purpose that requires accuracy, please confirm the details against the primary '
            'sources in § SRC.',
        ],
    },
}


def render_main(lang):
    b = BODY[lang]
    roles = '\n'.join(
        f'            <p style="{ROLE_LINE}">{label} — {value}</p>'
        for label, value in d._ROLES[lang])
    paras = '\n'.join(f'          <p>{p}</p>' for p in b['paras'])
    return (
        '      <section class="ph-section">\n'
        '        <div class="ph-section__head"><div class="ph-section__title">'
        '<span class="ph-section__num">§ 01</span>'
        f'<span class="ph-section__name">{b["sec_name"]}</span></div></div>\n'
        '        <div class="ph-section__body">\n'
        f'          <div style="{ROLE_WRAP}">\n{roles}\n          </div>\n'
        f'{paras}\n'
        '        </div>\n'
        '      </section>\n'
    )


def build(lang):
    src = ROOT / ('en/privacy-policy.html' if lang == 'en' else 'privacy-policy.html')
    html = d.strip_block(src.read_text(encoding='utf-8'))
    b = BODY[lang]

    ja_url = 'https://eyescosmos.com/colophon'
    en_url = 'https://eyescosmos.com/en/colophon'
    self_url = en_url if lang == 'en' else ja_url

    # ── SEO / meta ───────────────────────────────────────────────────────
    html = re.sub(r'<title>.*?</title>', f'<title>{b["title"]}</title>', html, count=1)
    for attr in ('name="description"', 'property="og:description"', 'name="twitter:description"'):
        html = re.sub(rf'<meta {re.escape(attr)} content="[^"]*">',
                      f'<meta {attr} content="{b["desc"]}">', html, count=1)
    for attr in ('property="og:title"', 'name="twitter:title"'):
        html = re.sub(rf'<meta {re.escape(attr)} content="[^"]*">',
                      f'<meta {attr} content="{b["title"]}">', html, count=1)
    html = re.sub(r'<link rel="canonical" href="[^"]*">',
                  f'<link rel="canonical" href="{self_url}">', html, count=1)
    html = re.sub(r'<link rel="alternate" hreflang="ja" href="[^"]*">',
                  f'<link rel="alternate" hreflang="ja" href="{ja_url}">', html, count=1)
    html = re.sub(r'<link rel="alternate" hreflang="en" href="[^"]*">',
                  f'<link rel="alternate" hreflang="en" href="{en_url}">', html, count=1)
    html = re.sub(r'<link rel="alternate" hreflang="x-default" href="[^"]*">',
                  f'<link rel="alternate" hreflang="x-default" href="{ja_url}">', html, count=1)
    html = re.sub(r'<meta property="og:url" content="[^"]*">',
                  f'<meta property="og:url" content="{self_url}">', html, count=1)

    html = html.replace('— Privacy Policy · v5.1 light paper', '— Colophon · v5.1 light paper')

    # ── chrome ───────────────────────────────────────────────────────────
    html = re.sub(r'(<div class="head__crumbs">\s*)(.*?)(\s*</div>)',
                  lambda m: m.group(1) + b['crumbs'] + m.group(3), html, count=1, flags=re.S)
    other = ja_url if lang == 'en' else en_url
    html = re.sub(r'href="https://eyescosmos\.com/(?:en/)?privacy-policy\.html"',
                  f'href="{other}"', html, count=1)
    # ヘッダーのブランドリンクは相対パスなので、1階層下がる分をルート絶対に直す
    html = html.replace('<a href="index.html">', '<a href="/index.html">')
    html = html.replace('<a href="../index.html">', '<a href="/en/index.html">')

    # ── hero ─────────────────────────────────────────────────────────────
    html = re.sub(r'<div class="era-hero__art-label">.*?</div>',
                  f'<div class="era-hero__art-label">{b["art_label"]}</div>', html, count=1)
    html = re.sub(r'<div class="era-hero__art-year">.*?</div>',
                  f'<div class="era-hero__art-year">{b["art_year"]}</div>', html, count=1)
    html = re.sub(r'<div class="era-hero__eyebrow">.*?</div>',
                  f'<div class="era-hero__eyebrow">{b["eyebrow"]}</div>', html, count=1)
    html = re.sub(r'<h1 class="era-hero__title">.*?</h1>',
                  f'<h1 class="era-hero__title">{b["h1"]}</h1>', html, count=1)
    html = re.sub(r'<div class="era-hero__period">.*?</div>',
                  f'<div class="era-hero__period">{b["period"]}</div>', html, count=1)
    html = re.sub(r'<p class="era-hero__lead">.*?</p>',
                  f'<p class="era-hero__lead">{b["lead"]}</p>', html, count=1, flags=re.S)
    meta_items = '\n      '.join(
        f'<span class="era-hero__meta-item">{k} <strong>{v}</strong></span>'
        for k, v in b['meta_row'])
    html = re.sub(r'(<div class="era-hero__meta-row">\s*).*?(\s*</div>)',
                  lambda m: m.group(1) + meta_items + m.group(2), html, count=1, flags=re.S)

    # ── main ─────────────────────────────────────────────────────────────
    html = re.sub(r'(<main class="era-main">\n).*?(\n    </main>)',
                  lambda m: m.group(1) + '\n' + render_main(lang) + m.group(2),
                  html, count=1, flags=re.S)

    out = ROOT / ('en/colophon/index.html' if lang == 'en' else 'colophon/index.html')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')
    return out


if __name__ == '__main__':
    for lang in ('ja', 'en'):
        p = build(lang)
        print(f'wrote {p.relative_to(ROOT)}  ({p.stat().st_size:,} bytes)')
