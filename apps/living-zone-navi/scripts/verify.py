#!/usr/bin/env python3
"""design-spec §8 とT03の固定点検査。

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
CONFIG_JSON = APP_DIR / "config.json"
INDEX_HTML = APP_DIR / "prototype" / "index.html"

# design-spec §4: reachは near(≤300m)/far(≤800m)/out(>800m)/unknown(欠損・位置不明)の4値。
# §8本文は「5値」と書いているが、値集合を定義している§4はこの4つのみを列挙している
# （仕様の記述ゆれ。OPEN-ISSUES.md参照）。ここでは§4の定義を正とする。
VALID_REACH = {"near", "far", "out", "unknown"}

LAT_RANGE = (35.0, 36.0)
LON_RANGE = (139.0, 140.0)
JOIN_WARN_RATE = 0.7
KINDS = ("shelter", "cool", "medical", "care")


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

    if not CONFIG_JSON.exists():
        fail("config.json が無い（ストレス係数の出所を確認できない）")
        ok = False
    else:
        config = json.loads(CONFIG_JSON.read_text(encoding="utf-8"))
        scenarios = config.get("stress_scenarios")
        scenario_ids = {s.get("id") for s in scenarios} if isinstance(scenarios, list) else set()
        valid_scenarios = (
            isinstance(scenarios, list)
            and scenario_ids == {"current", "stress_2070", "stress_2100"}
            and all(isinstance(s.get("factor"), (int, float)) and s.get("factor") > 0
                    and s.get("source") for s in scenarios)
        )
        if not valid_scenarios or not config.get("stress_source") or not config.get("stress_note"):
            fail("config.json: ストレス係数3件または係数の出所・注記が不足")
            ok = False
        else:
            print("✓ config.json: 現在/2070/2100の係数と出所注記あり")

    facilities = dataset["facilities"]
    if len(facilities) == 0:
        fail("facilities が0件")
        ok = False
    else:
        malformed_location = [
            f for f in facilities
            if (f["lat"] is None) != (f["lon"] is None)
        ]
        if malformed_location:
            fail(f"facilities: 緯度・経度の片方だけ欠損が{len(malformed_location)}件"
                 f"（例: {malformed_location[0]['id']}）")
            ok = False
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
    meta = dataset.get("meta", {})
    centroid_join = meta.get("centroid_join")
    if not isinstance(centroid_join, dict):
        fail("meta.centroid_join が無い（D6の結合率を記録して）")
        ok = False
    else:
        matched = centroid_join.get("matched")
        total = centroid_join.get("total")
        rate = centroid_join.get("rate")
        valid_join = (
            isinstance(matched, int) and isinstance(total, int)
            and isinstance(rate, (int, float))
            and total == len(areas) and 0 <= matched <= total
            and abs(rate - (matched / total if total else 1.0)) < 1e-9
        )
        if not valid_join:
            fail("meta.centroid_join の matched/total/rate が不整合")
            ok = False
        elif rate < JOIN_WARN_RATE:
            print(f"⚠ areas: D6町丁結合率が70%未満（{matched}/{total} = {rate:.1%}）")
        else:
            print(f"✓ areas: D6町丁結合率 {matched}/{total} ({rate:.1%})")

    bad_area_location = [
        a for a in areas
        if (a.get("lat") is None) != (a.get("lon") is None)
        or (
            a.get("lat") is not None and a.get("lon") is not None
            and not (LAT_RANGE[0] <= a["lat"] <= LAT_RANGE[1]
                     and LON_RANGE[0] <= a["lon"] <= LON_RANGE[1])
        )
    ]
    if bad_area_location:
        fail(f"areas: 町丁代表点の座標が不正なものが{len(bad_area_location)}件"
             f"（例: {bad_area_location[0]['code']}）")
        ok = False
    else:
        print("✓ areas: 町丁代表点の緯度経度は範囲内（未結合を除く）")

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

    bad_nearest = []
    near_m = meta.get("walk_near_m")
    far_m = meta.get("walk_far_m")
    if not isinstance(near_m, (int, float)) or not isinstance(far_m, (int, float)):
        fail("meta.walk_near_m / walk_far_m が数値ではない")
        ok = False
    elif near_m > far_m:
        fail("meta.walk_near_m が walk_far_m より大きい")
        ok = False
    else:
        for area in areas:
            nearest = area.get("nearest_m", {})
            reach = area.get("reach", {})
            if set(nearest) != set(KINDS) or set(reach) != set(KINDS):
                bad_nearest.append((area.get("code"), "keys"))
                continue
            for kind in KINDS:
                distance = nearest[kind]
                value = reach[kind]
                if distance is None and value != "unknown":
                    bad_nearest.append((area["code"], kind, distance, value))
                elif distance is not None:
                    expected = "near" if distance <= near_m else "far" if distance <= far_m else "out"
                    if value != expected:
                        bad_nearest.append((area["code"], kind, distance, value, expected))
        if bad_nearest:
            fail(f"areas: nearest_m と reach の不整合が{len(bad_nearest)}件"
                 f"（例: {bad_nearest[0]}）")
            ok = False
        else:
            print(f"✓ areas: {len(areas)}町丁、pop_65plus<=pop_total・reach/nearestとも異常なし")

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
        missing_str = [n for n in ("直線距離", "取得日", "ストレステスト", "予測ではなく") if n not in html]
        if missing_str:
            fail(f"prototype/index.html に「{'」「'.join(missing_str)}」の文字列が無い")
            ok = False
        else:
            print("✓ prototype/index.html: 「直線距離」「取得日」を含む")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
