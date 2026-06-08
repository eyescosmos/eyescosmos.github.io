#!/usr/bin/env python3
"""
era_pages_v5.1 を new-design/eras/ にコピーしてリンクを修正するスクリプト
"""
import os, re, shutil

SRC = "/Users/aiharadaisuke/Desktop/claude code/photography history/202606サイト新デザイン案/年代ページ/era_pages_v5.1"
DST = "/Users/aiharadaisuke/Desktop/claude code/broken picture/new-design/eras"

# スラッグ名の修正マップ（era pageのスラッグ → new-design のファイル名）
SLUG_FIXES = {
    'ruff':           'thomas-ruff',
    'tillmans':       'wolfgang-tillmans',
    'ninagawa-mika':  'mika-ninagawa',
    'rinko-kawauchi-2': 'rinko-kawauchi',
}

# ファイル名マッピング
ERA_FILES = {
    '1839 Era Page.html': '1839.html',
    '1870 Era Page.html': '1870.html',
    '1890 Era Page.html': '1890.html',
    '1910 Era Page.html': '1910.html',
    '1930 Era Page.html': '1930.html',
    '1950 Era Page.html': '1950.html',
    '1970 Era Page.html': '1970.html',
    '1980 Era Page.html': '1980.html',
    '1990 Era Page.html': '1990.html',
    '2000 Era Page.html': '2000.html',
    '2010 Era Page.html': '2010.html',
}

os.makedirs(DST, exist_ok=True)

def fix_photographer_link(slug):
    """写真家スラッグを new-design のファイル名に変換"""
    slug = SLUG_FIXES.get(slug, slug)
    return f'../{slug}.html'

def process_era_page(src_path, dst_path):
    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1) ホームリンク (/?focus=... を含む)
    content = re.sub(r'href="\/\?[^"]*"', 'href="../index.html"', content)
    content = re.sub(r'href="\/"(?!\w)', 'href="../index.html"', content)

    # 2) 年代ナビゲーションリンク: /XXXX Era Page.html → XXXX.html
    for old_name, new_name in ERA_FILES.items():
        year = new_name.replace('.html', '')
        # パターン1: /XXXX Era Page.html (1870-2010ページの古い形式)
        content = content.replace(f'href="/{old_name}"', f'href="{year}.html"')
        # パターン2: /eras/XXXX.html (1839ページの修正済み形式)
        content = content.replace(f'href="/eras/{year}.html"', f'href="{year}.html"')

    # 3) アーカイブリンク
    content = content.replace('href="/archive.html#tab-era"', 'href="../cards-archive.html"')

    # 4) colophon / privacy (プレースホルダー)
    content = content.replace('href="/colophon"', 'href="#"')
    content = content.replace('href="/privacy"', 'href="#"')

    # 5) 写真家リンク: /photographers/SLUG.html → ../SLUG.html
    def replace_ph_link(m):
        slug = m.group(1)
        return f'href="{fix_photographer_link(slug)}"'

    content = re.sub(r'href="/photographers/([^"]+)\.html"', replace_ph_link, content)

    with open(dst_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'  ✓ {os.path.basename(src_path)} → {os.path.basename(dst_path)}')

# 処理実行
print('=== era pages を new-design/eras/ にコピー・修正 ===')
for src_name, dst_name in ERA_FILES.items():
    src_path = os.path.join(SRC, src_name)
    dst_path = os.path.join(DST, dst_name)
    if os.path.exists(src_path):
        process_era_page(src_path, dst_path)
    else:
        print(f'  ✗ NOT FOUND: {src_name}')

print('\n完了！')
