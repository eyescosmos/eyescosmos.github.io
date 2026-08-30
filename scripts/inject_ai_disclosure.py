#!/usr/bin/env python3
"""AI開示ブロックを全ページへ適用する（冪等）。

  python3 scripts/inject_ai_disclosure.py --dry-run          # 差分の下見
  python3 scripts/inject_ai_disclosure.py --only photographers/ansel-adams.html
  python3 scripts/inject_ai_disclosure.py --all              # 全対象ページへ適用

ブロックの文面・見た目は scripts/ai_disclosure.py が正本。文面を直したらこのスクリプトを
`--all` で回し直せば全ページが揃う。

対象外（意図的）:
  - リダイレクトシム（meta http-equiv=refresh のみのページ）
  - design/ 配下（iframe埋め込み用の素片）
  - cards-archive.html（カードの正データ。ページとして読まれない）
  - colophon/index.html · en/colophon/index.html（コロフォン本体。全文が載っている）
  - Search Console の所有権確認ファイル
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ai_disclosure as d

ROOT = Path(__file__).resolve().parent.parent

EXCLUDE_EXACT = {
    'cards-archive.html',       # カードの正データ。ページとして読まれない
    'colophon/index.html',      # コロフォン本体。短縮版を重ねても意味が無い
    'en/colophon/index.html',
}
EXCLUDE_PREFIX = ('design/',)
RE_SHIM = re.compile(r'http-equiv=["\']refresh["\']', re.I)


def tracked_html():
    out = subprocess.run(['git', 'ls-files', '-z', '*.html'], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    return [p for p in out.split('\0') if p]


def is_target(rel, text):
    if rel in EXCLUDE_EXACT:
        return False, 'excluded'
    if rel.startswith(EXCLUDE_PREFIX):
        return False, 'excluded'
    if re.match(r'^google[0-9a-f]+\.html$', rel):
        return False, 'excluded'
    if RE_SHIM.search(text):
        return False, 'redirect-shim'
    if '</main>' not in text and '<footer' not in text:
        return False, 'no-anchor'
    return True, ''


def lang_of(rel):
    return 'en' if rel == 'en' or rel.startswith('en/') else 'ja'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--all', action='store_true', help='全対象ページへ適用')
    ap.add_argument('--only', action='append', default=[],
                    help='このパスだけ処理（複数指定可）')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    if not args.all and not args.only:
        ap.error('--all か --only を指定してください（無指定での全書き換えは禁止）')

    files = args.only if args.only else tracked_html()
    stats = {'inserted': 0, 'updated': 0, 'unchanged': 0}
    skipped = {}
    changed = []

    for rel in files:
        p = ROOT / rel
        if not p.exists():
            print(f'MISSING  {rel}')
            continue
        before = p.read_text(encoding='utf-8')
        ok, why = is_target(rel, before)
        if not ok:
            if args.only:
                print(f'SKIP({why})  {rel}')
            skipped[why] = skipped.get(why, 0) + 1
            continue

        after, action = d.ensure(before, lang_of(rel))
        if action == 'no-anchor':
            print(f'NO-ANCHOR  {rel}')
            skipped['no-anchor'] = skipped.get('no-anchor', 0) + 1
            continue

        # 安全確認: 開示ブロック以外は1バイトも変えない
        if d.strip_block(after) != d.strip_block(before):
            print(f'ABORT  {rel}: ブロック以外に差分が出ています')
            return 1

        stats[action] += 1
        if action != 'unchanged':
            changed.append(rel)
            if not args.dry_run:
                p.write_text(after, encoding='utf-8')

    tag = '[dry-run] ' if args.dry_run else ''
    print(f'{tag}inserted={stats["inserted"]} updated={stats["updated"]} '
          f'unchanged={stats["unchanged"]}')
    if skipped:
        print('skipped: ' + ', '.join(f'{k}={v}' for k, v in sorted(skipped.items())))
    if args.dry_run and changed:
        print(f'変更対象 {len(changed)} 件（先頭5件）: ' + ', '.join(changed[:5]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
