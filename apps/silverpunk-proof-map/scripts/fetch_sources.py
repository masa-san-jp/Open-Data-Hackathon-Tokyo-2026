#!/usr/bin/env python3
"""公開元から原本を取得し、data/raw/ に置く。取得だけを行い、画面ロジックは書かない。

  python3 scripts/fetch_sources.py            # 取得＋検査
  python3 scripts/fetch_sources.py --check    # 既存ファイルの検査のみ

検査に落ちたら非ゼロで終わる。403・空ファイル・HTMLポインタ・CAPTCHAを成功として扱わない。
"""
from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

# 既定の User-Agent を弾く配信元があるため、ブラウザ相当を名乗る（認証ではない）
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# (保存名, URL, source_id（evidence/sources.jsonと対応）)
SOURCES = [
    (
        "ipss_tokyo_population.xlsx",
        "https://www.ipss.go.jp/pp-shicyoson/j/shicyoson23/3kekka/Municipalities/13.xlsx",
        "src-ipss-population-2023",
    ),
]


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def check_xlsx(path: Path) -> str | None:
    """問題があれば理由の文字列、無ければ None。"""
    if not path.exists():
        return "ファイルが無い"
    raw = path.read_bytes()
    if len(raw) < 5000:
        return f"小さすぎる（{len(raw)} バイト）。HTMLポインタやCAPTCHAページの可能性"
    if raw[:2] != b"PK":
        return "xlsx（zip）として読めない（PK で始まらない）。中身がHTMLの可能性"
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="取得せず検査のみ")
    args = ap.parse_args()

    RAW.mkdir(parents=True, exist_ok=True)
    failed = 0
    for name, url, source_id in SOURCES:
        path = RAW / name
        if not args.check:
            try:
                path.write_bytes(fetch(url))
            except Exception as exc:
                print(f"✗ {name} ({source_id}): 取得できない: {exc}")
                failed += 1
                continue
        reason = check_xlsx(path)
        if reason:
            print(f"✗ {name} ({source_id}): {reason}")
            failed += 1
        else:
            print(f"✓ {name} ({source_id}, {path.stat().st_size:,} バイト)")
    if failed:
        print(f"\n{failed} 件が検査に落ちた。data/raw/ を直すまで先へ進まない。"
              "\n取得に失敗した場合は data/demo-fixture.json のPhase 1デモへ戻す（画面は動き続ける）。")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
