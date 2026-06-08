#!/usr/bin/env python3
"""
era pages の以下2点を修正:
1. 検索フィールドを Entry ブロックの直前に移動
2. カードCSS を archive (card-v4-base.css) に合わせる:
   - pc-top min-height: 200px → 220px
   - pc-top background: var(--surface-2) → #e8e4dc
   - pc-body background: var(--surface-2) → #e8e4dc
"""
import os, re

ERA_DIR = "/Users/aiharadaisuke/Desktop/claude code/broken picture/new-design/eras"

def fix_era_page(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # ─────────────────────────────────────────────
    # 1. カードCSS修正
    # ─────────────────────────────────────────────

    # pc-top min-height: 200px → 220px
    content = re.sub(
        r'(\.pc-top\s*\{[^}]*min-height:\s*)200px',
        r'\g<1>220px',
        content
    )

    # pc-top background: var(--surface-2) → #e8e4dc
    # (pc-top の background だけを対象に。.pc-body は別で処理)
    content = re.sub(
        r'(\.pc-top\s*\{[^}]*background:\s*)var\(--surface-2\)',
        r'\g<1>#e8e4dc',
        content
    )

    # pc-body background: var(--surface-2) → #e8e4dc
    content = re.sub(
        r'(\.pc-body\s*\{[^}]*background:\s*)var\(--surface-2\)',
        r'\g<1>#e8e4dc',
        content
    )

    # ─────────────────────────────────────────────
    # 2. 検索フィールドを Entry 直前に移動
    # ─────────────────────────────────────────────

    # 検索ブロック（Search · 写真家を探す）を抜き出す
    search_pattern = re.compile(
        r'(\s*<div class="ph-side-block">\s*<div class="ph-side-block__head">Search[^<]*</div>.*?</div>\s*</div>)',
        re.DOTALL
    )
    m = search_pattern.search(content)
    if m:
        search_block = m.group(1)
        # 元の位置から削除
        content_without_search = content[:m.start()] + content[m.end():]

        # Entry ブロックの直前に挿入
        entry_pattern = re.compile(
            r'(<div class="ph-side-block">\s*<div class="ph-side-block__head">Entry[^<]*</div>)'
        )
        em = entry_pattern.search(content_without_search)
        if em:
            insert_pos = em.start()
            content = (content_without_search[:insert_pos]
                      + search_block + '\n'
                      + content_without_search[insert_pos:])
        else:
            content = content_without_search  # Entry が見つからない場合はそのまま
    else:
        pass  # 検索ブロックが見つからない場合はスキップ

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# 全年代ページを処理
print('=== era pages のカードCSS・検索フィールド位置を修正 ===')
for fname in sorted(os.listdir(ERA_DIR)):
    if fname.endswith('.html'):
        fpath = os.path.join(ERA_DIR, fname)
        fix_era_page(fpath)
        print(f'  ✓ {fname}')

print('\n完了！')
