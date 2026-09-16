#!/usr/bin/env python3
"""一括再生成の差分が「意図した変更だけ」であることを機械照合する。

なぜ要るか
----------
`preflight.check_generated_surface_drift()` が見ているのは **出力HTML == 生成器(正本)**
の1方向だけで、**正本の中身が正しいか**は誰も見ていない。正本を間違えて再生成すると
出力は正本と完全に整合するので、**preflight はいつでも緑になる**（2026-09-17 に
`data/country-pages.json` のチリの lead をベネズエラ文面へ差し替えて実証済み。
`check_content_loss` も `preflight` も EXIT 0 のまま、日英で内容が食い違った）。

生成物は正本1行が最大66枚へ一括伝播するため、間違いの爆発半径が写真家ページ（1枚）と
桁違いになる。そこで「再生成で増えたのは意図した文字列だけか」を機械で確かめる。

使い方
------
    # チリ追加で 66 枚が変わったが、増えたのは chile リンクだけか
    python3 scripts/verify_bulk_regen.py --since HEAD \
        --expect '<a[^>]*countries/chile\\.html[^>]*>[^<]*</a>' \
        --paths countries en/countries

    # コミット済みの範囲を後から検算する
    python3 scripts/verify_bulk_regen.py --since 611197549^ \
        --expect '<a[^>]*countries/chile\\.html[^>]*>[^<]*</a>'

★`--expect` は**挿入された要素まるごと**を書く（ここを間違えると必ず FAIL する）
-------------------------------------------------------------------------
キーワードだけ（`--expect 'chile'`）にすると、その文字だけが剥がれて
`<a href="/countries/.html">チリ</a>` のような殻が残り、旧と一致せず FAIL する。
2026-09-17 の初回実行で実際に踏んだ。**タグの開きから閉じまでを含める。**

FAIL したときは、まず `--expect` が狭すぎないかを疑う。パターンを正した上でなお
FAIL するなら、それは本物の「意図の外側の変更」。

判定
----
各ファイルについて **旧・新の両方から `--expect` 該当箇所を落とした結果が完全一致**すれば OK。
両側から落とすのは、元からあった該当箇所を相殺するため（片側だけ剥がすと誤検知する）。
あわせて該当箇所が**減っていない**ことも見る（削除は「意図した変更」に含めない）。
一致しなければ「意図の外側の変更」なので FAIL（EXIT 1）とし、最初の数行を表示する。

`--expect` を**行全体が該当する**ケース（ナビ1行の追加など）と、**行の一部**に混ざる
ケース（ディレクトリ1行の中に挿入）の両方を1つの規則で扱う:
該当箇所を除去した結果その行が空白だけになり、かつ元は空白行でなかったなら、行ごと落とす。
"""
import argparse
import difflib
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO,
                          capture_output=True, text=True).stdout


def changed_files(ref: str, prefixes: list[str]) -> list[str]:
    out = subprocess.run(["git", "diff", "--name-only", "-z", ref],
                         cwd=REPO, capture_output=True, text=True)
    files = [f for f in out.stdout.split("\0") if f.endswith(".html")]
    if prefixes:
        files = [f for f in files if any(f.startswith(p.rstrip("/") + "/") or f == p
                                         for p in prefixes)]
    return sorted(files)


def strip_expected(new: str, pat: re.Pattern) -> str:
    """new から --expect 該当箇所を取り除く（空になった行は行ごと落とす）。"""
    kept = []
    for line in new.split("\n"):
        if not pat.search(line):
            kept.append(line)
            continue
        stripped = pat.sub("", line)
        if stripped.strip() == "" and line.strip() != "":
            continue          # その行は --expect 専用の行だった
        kept.append(stripped)
    return "\n".join(kept)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="一括再生成の差分が意図した変更だけかを照合する")
    ap.add_argument("--since", default="HEAD",
                    help="比較元の ref（既定 HEAD。コミット済みを検算するなら <sha>^）")
    ap.add_argument("--expect", required=True,
                    help="増えてよい文字列の正規表現（例 'chile'）")
    ap.add_argument("--paths", nargs="*", default=[],
                    help="対象ディレクトリを絞る（例 countries en/countries）")
    args = ap.parse_args(argv)

    try:
        pat = re.compile(args.expect)
    except re.error as e:
        print(f"ERROR: --expect が正規表現として不正: {e}", file=sys.stderr)
        return 2

    files = changed_files(args.since, args.paths)
    if not files:
        print(f"対象なし（{args.since} と比べて変更された .html が0件）")
        return 0

    ok, bad, created = [], [], []
    for f in files:
        old = git("show", f"{args.since}:{f}")
        if not old:
            created.append(f)
            continue
        new = (REPO / f).read_text(encoding="utf-8")
        # 旧・新の両方から --expect 該当箇所を落として比較する。
        # 「全部落として比較」だと、元からあった該当箇所まで新側だけ剥がれて
        # 誤検知する（2026-09-17 に privacy-policy の footer で実際に踏んだ）。
        # 両側から落とせば既存分は相殺され、増えた分だけが効く。
        if strip_expected(new, pat) != strip_expected(old, pat):
            bad.append(f)
        elif len(pat.findall(new)) < len(pat.findall(old)):
            bad.append(f)          # --expect 該当箇所が減っている＝削除は「意図」に含めない
        else:
            ok.append(f)

    print(f"照合対象 {len(files)} 枚 / ref={args.since} / expect={args.expect!r}")
    print(f"  意図どおり : {len(ok)}")
    print(f"  新規作成   : {len(created)}" + (f"  {created}" if created else ""))
    print(f"  ★意図の外 : {len(bad)}")
    for f in bad[:5]:
        old = strip_expected(git("show", f"{args.since}:{f}"), pat).split("\n")
        new = strip_expected((REPO / f).read_text(encoding="utf-8"), pat).split("\n")
        print(f"\n  --- {f} ---")
        for line in difflib.unified_diff(old, new, lineterm="", n=0):
            if line[:1] in "+-" and line[:3] not in ("+++", "---"):
                print(f"    {line[:160]}")
    if bad:
        print("\n判定: ★FAIL — 意図した変更の外側に差分がある。正本の編集内容を確認すること。")
        return 1
    print("\n判定: OK — 全ファイルが「旧 + 意図した変更」だけで説明できる。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
