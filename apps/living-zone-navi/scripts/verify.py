#!/usr/bin/env python3
"""design-spec §8 の固定点検査（この段階＝Phase 0で検査可能なもの）。

  python3 scripts/verify.py

落ちたら非ゼロで終わる。**固定点を、通すために書き換えない。**
落ちたら公開元の変化を調べ、OPEN-ISSUES.md に書いてから直す（AGENT.md）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
SOURCES_JSON = APP_DIR / "data" / "sources.json"
DATASET_JSON = APP_DIR / "data" / "processed" / "dataset.json"
INDEX_HTML = APP_DIR / "prototype" / "index.html"

# design-spec §4: reachは near(≤300m)/far(≤800m)/out(>800m)/unknown(欠損・位置不明)の4値。
# §8本文は「5値」と書いているが、値集合を定義している§4はこの4つのみを列挙している
# （仕様の記述ゆれ。OPEN-ISSUES.md参照）。ここでは§4の定義を正とする。
VALID_REACH = {"near", "far", "out", "unknown"}

LAT_RANGE = (35.0, 36.0)
LON_RANGE = (139.0, 140.0)


def fail(msg: str) -> None:
    print(f"✗ {msg}")


def main() -> int:
    ok = True

    if not SOURCES_JSON.exists():
        fail("data/sources.json が無い。scripts/fetch_sources.py を先に実行して")
        return 1
    sources = json.loads(SOURCES_JSON.read_text(encoding="utf-8"))["sources"]
    fetched_ok = [s for s in sources.values() if s.get("status") == "ok"]
    missing_meta = [s for s in fetched_ok if not s.get("fetched_at") or not s.get("sha256")]
    if missing_meta:
        fail(f"sources.json: 取得日またはsha256が無いものが{len(missing_meta)}件"
             f"（例: {missing_meta[0]['id']}）")
        ok = False
    else:
        print(f"✓ sources.json: 取得できた{len(fetched_ok)}件すべてに取得日・sha256あり")

    if not DATASET_JSON.exists():
        fail("data/processed/dataset.json が無い。scripts/build_dataset.py を先に実行して")
        return 1
    dataset = json.loads(DATASET_JSON.read_text(encoding="utf-8"))

    facilities = dataset["facilities"]
    if len(facilities) == 0:
        fail("facilities が0件")
        ok = False
    else:
        out_of_range = [
            f for f in facilities
            if f["lat"] is not None and f["lon"] is not None
            and not (LAT_RANGE[0] <= f["lat"] <= LAT_RANGE[1]
                      and LON_RANGE[0] <= f["lon"] <= LON_RANGE[1])
        ]
        if out_of_range:
            fail(f"facilities: 座標が北緯35-36度・東経139-140度の範囲外が{len(out_of_range)}件"
                 f"（例: {out_of_range[0]['id']}）")
            ok = False
        else:
            print(f"✓ facilities: {len(facilities)}件、座標は全て範囲内（位置不明を除く）")

    areas = dataset["areas"]
    bad_pop = [a for a in areas if a["pop_65plus"] > a["pop_total"]]
    if bad_pop:
        fail(f"areas: pop_65plus > pop_total が{len(bad_pop)}件（例: {bad_pop[0]['code']}）")
        ok = False
    bad_reach = [
        (a["code"], k, v) for a in areas for k, v in a["reach"].items() if v not in VALID_REACH
    ]
    if bad_reach:
        fail(f"areas: reach値が想定外が{len(bad_reach)}件（例: {bad_reach[0]}）")
        ok = False
    if not bad_pop and not bad_reach:
        print(f"✓ areas: {len(areas)}町丁、pop_65plus<=pop_total・reach値とも異常なし")

    gaps = dataset["gaps"]
    if not gaps:
        fail("gaps が空（この段階で欠損ゼロはあり得ない＝取り漏らしの兆候）")
        ok = False
    else:
        print(f"✓ gaps: {len(gaps)}件")

    if not INDEX_HTML.exists():
        fail("prototype/index.html が無い。scripts/build_prototype.py を先に実行して")
        ok = False
    else:
        html = INDEX_HTML.read_text(encoding="utf-8")
        missing_str = [n for n in ("直線距離", "取得日") if n not in html]
        if missing_str:
            fail(f"prototype/index.html に「{'」「'.join(missing_str)}」の文字列が無い")
            ok = False
        else:
            print("✓ prototype/index.html: 「直線距離」「取得日」を含む")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
