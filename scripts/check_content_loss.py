#!/usr/bin/env python3
"""写真家ページの「本文がいつの間にか消える」事故を検知する横断チェック。

どのスクリプト・どの作業が原因であっても、写真家リーフページ
(photographers/*.html, en/photographers/*.html) から下記の実体が
基準(既定: HEAD)に比べて減っていたら報告する:

  - 出典アンカー id="cite-N"
  - 本文セクション <section class="ph-section">
  - 代表作マーカー FIG. NN
  - thesis ブロック (この写真家が変えたこと / What this photographer changed)
  - lead/abstract 段落

これは build_photographers_en.py の detect_content_loss と同じ堅牢シグナルを、
「生成」ではなく「コミット/作業ツリー全体」に対して後追いで当てるもの。

加えて「消失ではないが本文の事実がすり替わった」事故（例: renger の経歴が
再生成で誤事実へ巻き戻った件）も拾う。これは消失ガードの盲点だった:
  - 出典数・セクション数・FIG 数といった構造シグナルが一切変わっていないのに、
    経歴/表現/批評などの本文テキスト・lead・thesis の文面だけが変化している場合を
    「書き換えの疑い（要目視）」として情報警告する。
  - 構造が増減する通常の加筆・§REL だけの変更では鳴らない（低ノイズ設計）。

特徴（安全側に倒す）:
  - ファイルを一切書き換えない（読み取りのみ）。
  - 既定では exit 0（報告のみ・push を止めない）。
  - --strict を付けたときだけ、「消失」検知で exit 1（書き換え警告は常に exit 0）。
  - reformat に強い「明確な減少」だけを拾い、誤検知を避ける。

使い方:
  python3 scripts/check_content_loss.py              # 作業ツリー vs HEAD
  python3 scripts/check_content_loss.py --against origin/main
  python3 scripts/check_content_loss.py --strict     # 損失で非0終了
"""
import argparse
import re
import subprocess
import sys

SCOPE_DIRS = ('photographers', 'en/photographers')


def git(*args):
    return subprocess.run(['git', *args], capture_output=True, text=True)


def repo_root():
    r = git('rev-parse', '--show-toplevel')
    return r.stdout.strip()


def changed_html(ref):
    """基準 ref と現在の作業ツリーで差分のある対象 HTML パス一覧。"""
    r = git('diff', '--name-only', ref, '--', *SCOPE_DIRS)
    out = []
    for line in r.stdout.splitlines():
        line = line.strip()
        if line.endswith('.html') and not line.endswith('-backup.html'):
            out.append(line)
    return out


def old_blob(ref, path):
    """基準 ref 時点の内容（無ければ None＝新規ファイルなので損失なし）。"""
    r = git('show', f'{ref}:{path}')
    if r.returncode != 0:
        return None
    return r.stdout


def new_text(path):
    try:
        with open(path, encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None  # 削除されたファイルは別途扱う


# ── 堅牢シグナル（build_photographers_en.py と同基準）────────────────────
def cite_ids(html):
    return set(re.findall(r'id="cite-(\d+)"', html))


def section_count(html):
    return len(re.findall(r'<section class="ph-section"', html))


def fig_count(html):
    return len(set(re.findall(r'FIG\.\s*(\d+)', html)))


def has_thesis(html):
    m = re.search(r'<p class="ph-thesis__body[^"]*">(.*?)</p>', html, re.S)
    return bool(m and re.sub(r'<[^>]+>', '', m.group(1)).strip())


def has_lead(html):
    m = re.search(r'<div class="ph-abstract">.*?<p[^>]*>(.*?)</p>', html, re.S)
    return bool(m and re.sub(r'<[^>]+>', '', m.group(1)).strip())


def detect_losses(old, new):
    losses = []
    dropped = cite_ids(old) - cite_ids(new)
    if dropped:
        losses.append('出典 %d 件 [cite-%s]' % (
            len(dropped), ','.join(sorted(dropped, key=int))))
    if section_count(old) > section_count(new):
        losses.append('本文セクション %d 個' % (section_count(old) - section_count(new)))
    if fig_count(old) > fig_count(new):
        losses.append('代表作 FIG %d 個' % (fig_count(old) - fig_count(new)))
    if has_thesis(old) and not has_thesis(new):
        losses.append('thesis ブロック')
    if has_lead(old) and not has_lead(new):
        losses.append('lead/abstract 段落')
    return losses


# ── 本文の「書き換え」検知（消失ではない事実すり替え）─────────────────────
def _norm_text(fragment):
    """HTML 断片を比較用の素テキストへ正規化（タグ除去・実体参照・空白畳み）。"""
    t = re.sub(r'<[^>]+>', ' ', fragment)
    for a, b in (('&#x27;', "'"), ('&#39;', "'"), ('&quot;', '"'),
                 ('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'), ('&nbsp;', ' ')):
        t = t.replace(a, b)
    return re.sub(r'\s+', ' ', t).strip()


def essay_text(html):
    """全 .essay 本文ブロック（経歴/表現/批評など）の正規化テキストを連結。"""
    blocks = re.findall(r'<div class="essay">(.*?)</div>', html, re.S)
    return _norm_text(' '.join(blocks))


def lead_text(html):
    m = re.search(r'<div class="ph-abstract">.*?<p[^>]*>(.*?)</p>', html, re.S)
    return _norm_text(m.group(1)) if m else ''


def thesis_text(html):
    m = re.search(r'<p class="ph-thesis__body[^"]*">(.*?)</p>', html, re.S)
    return _norm_text(m.group(1)) if m else ''


def structurally_unchanged(old, new):
    """出典・セクション・FIG が一切増減していない（=加筆や再構成でない）。"""
    return (cite_ids(old) == cite_ids(new)
            and section_count(old) == section_count(new)
            and fig_count(old) == fig_count(new))


def detect_rewrites(old, new):
    """消失ではないが本文の文面だけが変化したケース（事実すり替えの疑い）。
    構造シグナルが完全に不変のときだけ拾い、通常の加筆では鳴らさない。"""
    if not structurally_unchanged(old, new):
        return []
    rewrites = []
    if essay_text(old) and essay_text(old) != essay_text(new):
        rewrites.append('経歴/表現/批評などの本文テキスト')
    if lead_text(old) and lead_text(old) != lead_text(new):
        rewrites.append('lead/abstract 段落の文面')
    if thesis_text(old) and thesis_text(old) != thesis_text(new):
        rewrites.append('thesis の文面')
    return rewrites


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--against', default='HEAD',
                    help='比較基準の git ref（既定: HEAD。例: origin/main）')
    ap.add_argument('--strict', action='store_true',
                    help='損失を検知したら exit 1（既定は報告のみ exit 0）')
    args = ap.parse_args()

    root = repo_root()
    if root:
        import os
        os.chdir(root)

    findings = []
    rewrite_findings = []
    for path in changed_html(args.against):
        old = old_blob(args.against, path)
        if old is None:
            continue  # 新規ファイル: 損失なし
        new = new_text(path)
        if new is None:
            # ファイルごと削除された
            findings.append((path, ['ページ全体が削除されている']))
            continue
        losses = detect_losses(old, new)
        if losses:
            findings.append((path, losses))
        rewrites = detect_rewrites(old, new)
        if rewrites:
            rewrite_findings.append((path, rewrites))

    if not findings and not rewrite_findings:
        print('check_content_loss: OK（%s と比べて本文の消失・書き換えなし）' % args.against)
        return 0

    if findings:
        print('🛑 本文消失の疑い（%s と比較。書き換えはしていません）:' % args.against)
        for path, losses in findings:
            print('  ✋ %s' % path)
            for l in losses:
                print('       − %s' % l)
        print('  → 意図的な削除でなければ復元してください。'
              '生成で消えた場合は正本(JA HTML / photographers-en-content.json)に戻してから再生成。')

    if rewrite_findings:
        print('⚠ 本文の書き換え（消失ではない・構造不変のまま文面が変化＝事実すり替えの疑い・要目視）:')
        for path, rewrites in rewrite_findings:
            print('  ✋ %s' % path)
            for r in rewrites:
                print('       ~ %s' % r)
        print('  → 意図した修正なら問題なし。EN は再生成で巻き戻った可能性があるので、'
              '正本(JA HTML / photographers-en-content.json・overrides.js)と一致しているか確認。')

    # 書き換え警告だけのときは push を止めない（加筆・正当な修正で日常的に出るため）。
    return 1 if (findings and args.strict) else 0


if __name__ == '__main__':
    sys.exit(main())
