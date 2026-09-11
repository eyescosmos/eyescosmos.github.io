#!/usr/bin/env python3
"""GSC と Bing Webmaster Tools から検索データを取得してスナップショットに保存する。

設計と運用は docs/seo-selector-spec.md を参照。要点だけ:

- **ページを一切書き換えない。** 取得と保存だけを行う。
- GSC は新旧2プロパティを毎回引く。移行後も旧 github.io 側に露出が残っており、
  片方だけではクリックの半分が見えない（2026-09-11 実測）。
- Bing は過去に遡れない。回さなかった月のデータは永久に失われる。
- 保存先はリポジトリの外。eyescosmos.github.io は公開リポジトリのため。

認証（どちらもリポジトリ外・600）:
  ~/.config/eyescosmos-seo/gsc-service-account.json
  ~/.config/eyescosmos-seo/bwt-api-key.txt

使い方:
  python3 scripts/seo_fetch.py                      直近28日窓を取得して保存
  python3 scripts/seo_fetch.py --dry-run            取得するが保存しない
  python3 scripts/seo_fetch.py --window 7           窓の長さを変える
  python3 scripts/seo_fetch.py --backfill 2026-03-31  GSC の過去分を28日刻みで遡って保存
  python3 scripts/seo_fetch.py --gsc-only           Bing を叩かない
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# --- 置き場 -------------------------------------------------------------
DATA_HOME = Path("~/Desktop/claude code/photography history/seo-watch").expanduser()
SNAP_DIR = DATA_HOME / "snapshots"

GSC_KEY = Path("~/.config/eyescosmos-seo/gsc-service-account.json").expanduser()
BWT_KEY = Path("~/.config/eyescosmos-seo/bwt-api-key.txt").expanduser()

# 新旧そろえて引く。順番は「新, 旧」で固定
PROPERTIES = ["https://eyescosmos.com/", "https://eyescosmos.github.io/"]

GSC_SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"
BWT_BASE = "https://ssl.bing.com/webmaster/api.svc/json/"

# GSC の確定データは数日遅れる。既定でこの日数だけ手前を終端にする
END_LAG_DAYS = 3


# --- 共通ヘルパ ---------------------------------------------------------
def normalize_path(url: str) -> str:
    """URL からホストを剥がし、percent-encoding を戻してパスだけにする。

    新旧プロパティを突き合わせるための鍵になる。旧側はパスが encode されて
    返ることがあるため unquote が必須。
    """
    parsed = urllib.parse.urlsplit(url)
    path = parsed.path or "/"
    return urllib.parse.unquote(path)


def bwt_date(value: str) -> str | None:
    """BWT の `/Date(1787875200000)/` 形式を YYYY-MM-DD に直す。"""
    if not isinstance(value, str) or not value.startswith("/Date("):
        return None
    try:
        ms = int(value[6:].split(")")[0].split("+")[0].split("-")[0])
    except (ValueError, IndexError):
        return None
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).date().isoformat()


# --- GSC ---------------------------------------------------------------
def gsc_service():
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        sys.exit(
            "google-api-python-client が入っていない。\n"
            "  .venv/bin/pip install google-api-python-client google-auth"
        )
    if not GSC_KEY.exists():
        sys.exit(f"GSC の鍵がない: {GSC_KEY}\n  docs/seo-selector-spec.md §11 の Phase 0-A を参照")
    creds = service_account.Credentials.from_service_account_file(str(GSC_KEY), scopes=[GSC_SCOPE])
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)


def gsc_query(svc, site: str, start: date, end: date, dimensions: list[str]) -> list[dict]:
    """1プロパティ分を全ページ取得する。rowLimit は 25000 が上限。"""
    rows, offset = [], 0
    while True:
        body = {
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "dimensions": dimensions,
            "rowLimit": 25000,
            "startRow": offset,
            "dataState": "final",
        }
        got = svc.searchanalytics().query(siteUrl=site, body=body).execute().get("rows", [])
        rows.extend(got)
        if len(got) < 25000:
            return rows
        offset += len(got)


def fetch_gsc(svc, start: date, end: date) -> dict:
    out = {"window": {"start": start.isoformat(), "end": end.isoformat()}, "properties": {}}
    for site in PROPERTIES:
        totals = gsc_query(svc, site, start, end, [])
        t = totals[0] if totals else {}
        rows = []
        for r in gsc_query(svc, site, start, end, ["page", "query"]):
            page, query = r["keys"]
            rows.append({
                "path": normalize_path(page),
                "query": query,
                "clicks": int(r.get("clicks", 0)),
                "impressions": int(r.get("impressions", 0)),
                "ctr": round(r.get("ctr", 0.0), 6),
                "position": round(r.get("position", 0.0), 2),
            })
        out["properties"][site] = {
            "totals": {
                "clicks": int(t.get("clicks", 0)),
                "impressions": int(t.get("impressions", 0)),
                "ctr": round(t.get("ctr", 0.0), 6),
                "position": round(t.get("position", 0.0), 2),
            },
            "rows": rows,
        }
        print(f"  GSC {site:<34} {len(rows):>5} 行  "
              f"クリック{out['properties'][site]['totals']['clicks']} "
              f"表示{out['properties'][site]['totals']['impressions']}")
    return out


# --- Bing ---------------------------------------------------------------
def bwt_call(key: str, method: str, **params) -> dict:
    params["apikey"] = key
    url = BWT_BASE + method + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "eyescosmos-seo/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        return {"__error__": f"HTTP {exc.code}", "body": exc.read().decode()[:300]}
    except Exception as exc:  # ネットワーク断など。取得失敗でも他を止めない
        return {"__error__": repr(exc)[:200]}


def fetch_bwt() -> dict:
    if not BWT_KEY.exists():
        print(f"  Bing: 鍵がないので飛ばす ({BWT_KEY})")
        return {"skipped": "no key"}
    key = BWT_KEY.read_text().strip()
    out = {"properties": {}}
    for site in PROPERTIES:
        prop: dict = {}
        for method, label in (
            ("GetQueryStats", "queries"),
            ("GetPageStats", "pages"),
            ("GetRankAndTrafficStats", "daily"),
        ):
            res = bwt_call(key, method, siteUrl=site)
            if "__error__" in res:
                prop[label] = {"error": res["__error__"]}
                print(f"  Bing {site:<34} {label}: {res['__error__']}")
                continue
            rows = []
            for r in res.get("d", []):
                row = {
                    "clicks": r.get("Clicks"),
                    "impressions": r.get("Impressions"),
                    "date": bwt_date(r.get("Date", "")),
                }
                if label == "queries":
                    row["query"] = r.get("Query")
                    row["position"] = r.get("AvgImpressionPosition")
                elif label == "pages":
                    # このエンドポイントは Query キーに URL を入れて返す
                    row["path"] = normalize_path(r.get("Query") or r.get("Url") or "")
                    row["position"] = r.get("AvgImpressionPosition")
                rows.append(row)
            prop[label] = rows
            print(f"  Bing {site:<34} {label}: {len(rows)} 行")
        out["properties"][site] = prop
    return out


# --- 保存 ---------------------------------------------------------------
def save(payload: dict, kind: str, stamp: str, dry_run: bool) -> Path | None:
    path = SNAP_DIR / f"{kind}-{stamp}.json"
    if dry_run:
        print(f"  [dry-run] 保存しない: {path}")
        return None
    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    if path.exists():
        # スナップショットは追記専用。同日の再実行は上書きせず連番で逃がす
        n = 2
        while (alt := SNAP_DIR / f"{kind}-{stamp}.{n}.json").exists():
            n += 1
        path = alt
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"  保存: {path}")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--window", type=int, default=28, help="窓の日数（既定28）")
    ap.add_argument("--end-lag", type=int, default=END_LAG_DAYS, help="終端を何日手前にするか（既定3）")
    ap.add_argument("--dry-run", action="store_true", help="取得するが保存しない")
    ap.add_argument("--gsc-only", action="store_true", help="Bing を叩かない")
    ap.add_argument("--bwt-only", action="store_true", help="GSC を叩かない")
    ap.add_argument("--backfill", metavar="YYYY-MM-DD",
                    help="この日付まで GSC を28日刻みで遡って保存する（Bing は遡れないので対象外）")
    args = ap.parse_args()

    end = date.today() - timedelta(days=args.end_lag)

    if args.backfill:
        try:
            floor = date.fromisoformat(args.backfill)
        except ValueError:
            sys.exit("--backfill は YYYY-MM-DD 形式で指定する")
        svc = gsc_service()
        cursor, made = end, 0
        while cursor > floor:
            start = max(cursor - timedelta(days=args.window - 1), floor)
            print(f"[backfill] {start} 〜 {cursor}")
            save(fetch_gsc(svc, start, cursor), "gsc", cursor.isoformat(), args.dry_run)
            made += 1
            cursor = start - timedelta(days=1)
        print(f"\nbackfill 完了: {made} 窓")
        return 0

    start = end - timedelta(days=args.window - 1)
    stamp = date.today().isoformat()
    print(f"期間 {start} 〜 {end}  （取得日 {stamp}）")

    if not args.bwt_only:
        payload = fetch_gsc(gsc_service(), start, end)
        payload["fetched_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
        save(payload, "gsc", stamp, args.dry_run)

    if not args.gsc_only:
        payload = fetch_bwt()
        payload["fetched_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
        payload["note"] = "Bing は任意期間を指定できない。返るのは直近の集計"
        save(payload, "bwt", stamp, args.dry_run)

    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONWARNINGS", "ignore")
    raise SystemExit(main())
