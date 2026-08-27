#!/usr/bin/env python3
"""IndexNow へ更新URLを通知する（Bing / Yandex / Seznam / Naver 向け。Google は非対応）。

所有証明は「ルート直下の <key>.txt」方式。キーはこのスクリプトが自動発見するので、
どこにも二重に書かない（正本はルートの .txt ファイル自身）。

スコープフラグ必須（無指定は拒否）:
  --since <ref>   ref..HEAD で変更された HTML を対象にする（通常はこれ。既定 ref は origin/main）
  --paths ...     リポジトリ相対パスを直接指定
  --urls ...      URL を直接指定
  --all           sitemap.xml の全URL（初回一括のみ。日常運用では使わない）

例:
  python3 scripts/indexnow_submit.py --since origin/main --dry-run
  python3 scripts/indexnow_submit.py --since origin/main
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HOST = "eyescosmos.com"
ORIGIN = f"https://{HOST}"
ENDPOINT = "https://api.indexnow.org/IndexNow"
SITEMAP = ROOT / "sitemap.xml"
KEY_RE = re.compile(r"^[0-9a-fA-F]{8,128}\.txt$")
BATCH_MAX = 10000
TIMEOUT = 30

# IndexNow の応答コード（公式仕様）
STATUS_MEANING = {
    200: "OK（受理）",
    202: "受理。ただしキー検証は保留中（<key>.txt が未公開だとここで止まる）",
    400: "Bad request（リクエスト形式が不正）",
    403: "Forbidden（キーが無効。<key>.txt の中身と key が不一致）",
    422: "Unprocessable（URL が host に属していない／key が一致しない）",
    429: "Too Many Requests（送りすぎ。しばらく空ける）",
}


def die(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def find_key() -> str:
    """ルート直下の <16進>.txt を探し、中身をキーとして返す。"""
    candidates = []
    for p in ROOT.iterdir():
        if not p.is_file() or not KEY_RE.match(p.name):
            continue
        body = p.read_text(encoding="utf-8").strip()
        if body == p.stem:
            candidates.append(body)
        else:
            print(f"WARN: {p.name} の中身がファイル名と不一致のため無視しました", file=sys.stderr)
    if not candidates:
        die("IndexNow キーファイルが見つかりません。ルート直下に <16進32文字>.txt を作り、"
            "中身に同じ文字列だけを書いてください")
    if len(candidates) > 1:
        die(f"キーファイルが複数あります: {candidates}。1つに絞ってください")
    return candidates[0]


def sitemap_urls() -> set[str]:
    if not SITEMAP.exists():
        die("sitemap.xml がありません")
    text = SITEMAP.read_text(encoding="utf-8")
    return set(re.findall(r"<loc>\s*(.*?)\s*</loc>", text))


def changed_paths(ref: str) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMR", f"{ref}..HEAD"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout
    except subprocess.CalledProcessError as e:
        die(f"git diff に失敗しました（ref={ref}）: {e.stderr.strip()}")
    return [line for line in out.splitlines() if line.strip()]


def path_to_url(rel: str) -> str:
    return f"{ORIGIN}/{rel.lstrip('/')}"


def resolve_urls(args) -> list[str]:
    known = sitemap_urls()

    if args.all:
        return sorted(known)

    if args.urls:
        raw = list(args.urls)
    else:
        rels = list(args.paths) if args.paths else changed_paths(args.since)
        raw = [path_to_url(r) for r in rels if r.endswith(".html")]

    urls, skipped = [], []
    for u in raw:
        if urlparse(u).netloc != HOST:
            skipped.append((u, "別ホスト"))
        elif u not in known:
            # sitemap 非掲載＝ backup / new-design / 非公開ページ。送っても無意味なので落とす
            skipped.append((u, "sitemap.xml に無い"))
        else:
            urls.append(u)

    for u, why in skipped:
        print(f"skip ({why}): {u}")
    # 重複除去して順序を安定させる
    return sorted(set(urls))


def submit(key: str, urls: list[str], dry_run: bool) -> int:
    payload = {
        "host": HOST,
        "key": key,
        "keyLocation": f"{ORIGIN}/{key}.txt",
        "urlList": urls,
    }
    if dry_run:
        print("--- dry-run: 送信せずに payload を表示します ---")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
            code = res.status
    except urllib.error.HTTPError as e:
        code = e.code
    except urllib.error.URLError as e:
        die(f"通信に失敗しました: {e.reason}")

    print(f"HTTP {code}: {STATUS_MEANING.get(code, '未知の応答')}")
    return 0 if code in (200, 202) else 1


def check_key_published(key: str) -> bool:
    url = f"{ORIGIN}/{key}.txt"
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as res:
            body = res.read().decode("utf-8").strip()
    except Exception as e:  # noqa: BLE001 — 未公開・404 も含めて同じ扱い
        print(f"WARN: キーファイルを取得できません（{url}）: {e}")
        return False
    if body != key:
        print(f"WARN: 公開されているキーの中身が一致しません（{url}）")
        return False
    print(f"OK: キーファイル公開済み {url}")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    scope = ap.add_mutually_exclusive_group()
    scope.add_argument("--since", metavar="REF", nargs="?", const="origin/main",
                       help="REF..HEAD の変更HTMLを対象（既定 origin/main）")
    scope.add_argument("--paths", nargs="+", metavar="PATH", help="リポジトリ相対パスを直接指定")
    scope.add_argument("--urls", nargs="+", metavar="URL", help="URL を直接指定")
    scope.add_argument("--all", action="store_true", help="sitemap.xml の全URL（初回一括のみ）")
    ap.add_argument("--dry-run", action="store_true", help="送信せず対象と payload を表示")
    ap.add_argument("--skip-key-check", action="store_true", help="キーファイルの公開確認を省略")
    args = ap.parse_args()

    if not (args.since or args.paths or args.urls or args.all):
        die("スコープフラグが必要です（--since / --paths / --urls / --all のいずれか）")

    key = find_key()
    urls = resolve_urls(args)

    if not urls:
        print("対象URLが0件でした。何も送信しません。")
        return 0

    print(f"\n対象 {len(urls)} URL:")
    for u in urls[:20]:
        print(f"  {u}")
    if len(urls) > 20:
        print(f"  … 他 {len(urls) - 20} 件")
    print()

    if not args.dry_run and not args.skip_key_check and not check_key_published(key):
        die("キーファイルが本番で見えていません。<key>.txt を push してデプロイされてから再実行してください "
            "（確認を飛ばすなら --skip-key-check）")

    rc = 0
    for i in range(0, len(urls), BATCH_MAX):
        rc |= submit(key, urls[i:i + BATCH_MAX], args.dry_run)
    return rc


if __name__ == "__main__":
    sys.exit(main())
