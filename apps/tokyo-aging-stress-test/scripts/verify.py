#!/usr/bin/env python3
"""受け入れ検査。**エージェントはこれが通るまで「できた」と言わない。**

  python3 scripts/verify.py [--phase 1]

数を数えて落とすだけの検査にはしていない。「値が壊れていないか」を見る。
落ちたら非ゼロで終わる。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "stress_test.json"
PROTOTYPE = BASE / "prototype" / "index.html"

fails: list[str] = []


def want(condition: bool, message: str) -> None:
    if not condition:
        fails.append(message)


def check_data() -> dict | None:
    if not DATA.exists():
        fails.append("data/stress_test.json が無い。先に build_dataset.py を走らせる")
        return None
    d = json.loads(DATA.read_text(encoding="utf-8"))
    munis = d["municipalities"]

    want(len(munis) == 53, f"自治体が53件でない（{len(munis)}件）")
    want(len(d["excluded"]) == 9, f"除外が9件でない（{len(d['excluded'])}件）")
    want(d["years"][-1] == 2045, "2045年より先が入っている。外挿は禁止")

    by_name = {m["name"]: m for m in munis}
    # 実測値の固定点。公開元が更新されたらここで落ちる（黙って数字が変わらない）
    for name, year, key, expected in [
        ("千代田区", 2020, "aging_rate", 16.4),
        ("檜原村", 2020, "aging_rate", 53.1),
        ("東大和市", 2045, "support_ratio", 0.70),
        ("千代田区", 2045, "support_ratio", 58.74),
    ]:
        want(name in by_name, f"{name} が無い")
        if name in by_name:
            got = by_name[name]["series"][str(year)][key]
            want(abs(got - expected) < 0.01,
                 f"{name} {year} {key} が {expected} でない（{got}）")

    # 「支え手1.0未満」は 2020年 0件 → 2045年 12件
    for year, expected in ((2020, 0), (2045, 12)):
        n = sum(1 for m in munis if m["series"][str(year)]["support_ratio"] < 1.0)
        want(n == expected, f"{year}年の支え手1.0未満が{expected}件でない（{n}件）")

    # 企画の中心＝65歳以上の労働が増えること。全就業者は減ること
    ew20 = sum(m["series"]["2020"]["elderly_workers"] for m in munis)
    ew45 = sum(m["series"]["2045"]["elderly_workers"] for m in munis)
    aw20 = sum(m["series"]["2020"]["workers"] for m in munis)
    aw45 = sum(m["series"]["2045"]["workers"] for m in munis)
    want(abs(ew20 - 1_007_253) < 10, f"2020年の65歳以上就業者が1,007,253でない（{ew20:,}）")
    want(abs(ew45 - 1_349_833) < 10, f"2045年の65歳以上就業者が1,349,833でない（{ew45:,}）")
    want(ew45 > ew20, "65歳以上就業者が増えていない")
    want(aw45 < aw20, "全就業者が減っていない")

    for m in munis:
        for year, s in m["series"].items():
            want(0 < s["aging_rate"] < 100, f"{m['name']} {year} 高齢化率が範囲外")
            want(s["support_ratio"] > 0, f"{m['name']} {year} 支え手比率が0以下")
            want(s["elderly"] > 0, f"{m['name']} {year} 高齢者数が0以下")
    return d


def check_prototype() -> None:
    if not PROTOTYPE.exists():
        fails.append("prototype/index.html が無い（Phase 1 の成果物）")
        return
    html = PROTOTYPE.read_text(encoding="utf-8")
    want(len(html) > 2000, "prototype/index.html が小さすぎる")
    want("http://" not in html and "https://" not in html.replace("https://www.ipss", ""),
         "外部URLを読んでいる。プロトタイプは単体で開けること（出典表記のリンクは除く）")
    want("65歳以上就業者" in html, "65歳以上就業者が画面に出ていない")
    want("支え手" in html, "支え手比率が画面に出ていない")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", type=int, default=1)
    args = ap.parse_args()

    check_data()
    if args.phase >= 1:
        check_prototype()

    if fails:
        print(f"✗ {len(fails)} 件")
        for f in fails:
            print("   -", f)
        return 1
    print("✓ すべて通った")
    return 0


if __name__ == "__main__":
    sys.exit(main())
