#!/usr/bin/env python3
"""4つの公式ソースを取得し、形が想定どおりかを検査して data/raw/ に置く。

  python3 scripts/fetch_sources.py            # 取得＋検査
  python3 scripts/fetch_sources.py --check    # 既存ファイルの検査のみ

検査に落ちたら非ゼロで終わる。**中身を見ずに次へ進ませないためのゲート**。
公開元が更新して形が変わったら、ここで止まる。
"""
from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
# 既定の User-Agent を弾く配信元があるため、ブラウザ相当を名乗る（認証ではない）
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

# (保存名, URL, 文字コード or None=バイナリ, 最低行数, ヘッダに必ず含まれる語)
SOURCES = [
    ("ipss_tokyo_13.xlsx",
     "https://www.ipss.go.jp/pp-shicyoson/j/shicyoson23/3kekka/Municipalities/13.xlsx",
     None, 0, ""),
    ("employment_by_age.csv",
     "https://www.toukei.metro.tokyo.lg.jp/gyosoku/gy25rv0500.csv",
     "utf-8-sig", 2000, "年齢階級区分"),
    ("households_general.csv",
     "https://www.toukei.metro.tokyo.lg.jp/syosoku/sy24rv0100.csv",
     "utf-8-sig", 60, "地域名"),
    ("households_single.csv",
     "https://www.toukei.metro.tokyo.lg.jp/syosoku/sy24rv0200.csv",
     "utf-8-sig", 170, "世帯主の性別区分"),
]


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def check(path: Path, encoding: str | None, min_lines: int, header_word: str) -> str | None:
    """問題があれば理由の文字列、無ければ None。"""
    if not path.exists():
        return "ファイルが無い"
    raw = path.read_bytes()
    if len(raw) < 1000:
        return f"小さすぎる（{len(raw)} バイト）。LFS ポインタや CAPTCHA ページの可能性"
    if encoding is None:
        return None if raw[:2] == b"PK" else "xlsx ではない（PK で始まらない）"
    try:
        text = raw.decode(encoding)
    except UnicodeDecodeError:
        return f"{encoding} で読めない"
    lines = text.splitlines()
    if len(lines) < min_lines:
        return f"行数が足りない（{len(lines)} < {min_lines}）"
    if header_word and header_word not in lines[0]:
        return f"ヘッダに「{header_word}」が無い: {lines[0][:80]}"
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="取得せず検査のみ")
    args = ap.parse_args()

    RAW.mkdir(parents=True, exist_ok=True)
    failed = 0
    for name, url, encoding, min_lines, header_word in SOURCES:
        path = RAW / name
        if not args.check:
            try:
                path.write_bytes(fetch(url))
            except Exception as exc:
                print(f"✗ {name}: 取得できない: {exc}")
                failed += 1
                continue
        reason = check(path, encoding, min_lines, header_word)
        if reason:
            print(f"✗ {name}: {reason}")
            failed += 1
        else:
            print(f"✓ {name} ({path.stat().st_size:,} バイト)")
    if failed:
        print(f"\n{failed} 件が検査に落ちた。data/raw/ を直すまで先へ進まない。")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
