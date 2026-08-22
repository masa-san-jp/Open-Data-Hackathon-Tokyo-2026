# -*- coding: utf-8 -*-
"""東京都の人口を対象とした簡易コーホート要因法モデル。

目的
----
「東京都の人口増加は、地方からの国内転入と海外からの流入にどの程度依存して
いるのか」という仮説を、年齢構造を明示的に扱うモデルで定量化する。

構造
----
5歳階級（0-4歳 … 95-99歳, 100歳以上 の21階級）のコーホート要因法。
1ステップ = 5年。各ステップで次を行う。

    1. 各階級の人口 × 生残率 → 1つ上の階級へ送る
    2. 出産可能年齢（15-49歳）の女性人口 × 年齢別出生パターン × TFR → 出生数
    3. 出生数 × 乳幼児生残率 → 新しい 0-4歳階級
    4. 年齢別純移動数を加算（移動ゼロシナリオではこれを 0 にする）

データの出所
------------
[実データ] docs/research/population/ 配下の調査レポートに記載された公的統計。
  - 2020年 東京都 年齢3区分人口 157万 / 928万 / 319万
    出典: 東京都「東京の将来人口」(2050東京戦略 附属資料)
  - 2025年中の東京都人口変動の内訳（自然増減 ▲54,153人、日本人国内純移動
    +63,245人、外国人住民純増 +62,478人）
    出典: 東京都「令和7年中の人口の動き」
  - 東京都公式推計の将来値（2030年1,426万人 … 2065年1,231万人）
    出典: 同「東京の将来人口」

[独自仮定] 5歳階級別の詳細データが上記レポート群に無いため、本モデルが
置いた近似値。公的統計ではない。
  - 3区分内を5歳階級に割り振る重み（W_*）
  - 5年生残率（SURVIVAL）
  - 年齢別出生パターンの形（FERT_SHAPE）
  - 年齢別純移動の配分（MIG_SHAPE）
  - TFR水準（シナリオとして複数設定）
  - 女性割合 48.7%（全年齢一定と仮定）

検証
----
`calibration` シナリオは、2025年実績の純移動（年間約12.6万人）を投入した
場合にモデルが東京都公式推計を再現できるかを確認するためのもの。これが
大きく外れる場合、移動ゼロシナリオの結果も同じ方向に偏っている。

実行
----
    python3 tokyo_cohort_model.py            # 表を標準出力
    python3 tokyo_cohort_model.py --csv OUT  # 全系列を CSV 出力

依存ライブラリなし（Python 3 標準ライブラリのみ）。
"""

from __future__ import annotations

import argparse
import csv
import sys

# ---------------------------------------------------------------- 年齢階級定義

AGE_LABELS = [f"{5 * i}-{5 * i + 4}" for i in range(20)] + ["100+"]
N_AGE = len(AGE_LABELS)

IDX_0_14 = slice(0, 3)     # 0-4, 5-9, 10-14
IDX_15_64 = slice(3, 13)   # 15-19 … 60-64
IDX_65_UP = slice(13, N_AGE)

REPRO_START, REPRO_END = 3, 9  # 15-19 … 45-49（7階級）

# ------------------------------------------------- [実データ] 2020年 年齢3区分

POP_0_14_2020 = 1_570_000
POP_15_64_2020 = 9_280_000
POP_65_UP_2020 = 3_190_000
TOTAL_2020 = POP_0_14_2020 + POP_15_64_2020 + POP_65_UP_2020  # 14,040,000

# ------------------------------------------------ [独自仮定] 階級内の構成比

# 0-14歳：近年の出生減により若い階級ほど少ない
W_0_14 = [0.310, 0.335, 0.355]

# 15-64歳：20代前半に転入超過による山、45-49歳に団塊ジュニア世代の山
W_15_64 = [0.078, 0.118, 0.108, 0.096, 0.090,
           0.096, 0.112, 0.102, 0.098, 0.102]

# 65歳以上：高齢になるほど逓減
W_65_UP = [0.290, 0.250, 0.190, 0.130, 0.080, 0.038, 0.018, 0.004]

# ------------------------------------------------ [独自仮定] 5年生残率

SURVIVAL = [
    0.9990, 0.9993, 0.9990, 0.9985, 0.9978,   # 0-4 … 20-24
    0.9970, 0.9963, 0.9953, 0.9935, 0.9905,   # 25-29 … 45-49
    0.9855, 0.9770, 0.9630, 0.9400,           # 50-54 … 65-69
    0.9050, 0.8500, 0.7600, 0.6300,           # 70-74 … 85-89
    0.4700, 0.2900, 0.1300,                   # 90-94, 95-99, 100+
]

CHILD_SURVIVAL = 0.999
FEMALE_SHARE = 0.487

# ------------------------------------------------ [独自仮定] 出生・移動パターン

# 30-34歳をピークとする一般的な年齢別出生パターンの形
FERT_SHAPE_RAW = [0.015, 0.130, 0.310, 0.300, 0.180, 0.055, 0.010]

# 年齢別純移動の配分。東京都の転入超過は20-24歳・25-29歳に極端に集中する
# （2025年の東京都の20-24歳転入超過は都全体の転入超過の大部分を占める）。
# 30代以降は子育て世代の転出により小さく、40代以降はマイナス。
MIG_SHAPE_RAW = [
    0.010, 0.010, 0.015, 0.150, 0.420,   # 0-4 … 20-24
    0.260, 0.090, 0.030, 0.005, -0.010,  # 25-29 … 45-49
    -0.010, -0.010, -0.010, -0.010,      # 50-54 … 65-69
    -0.005, -0.005, 0.000, 0.000,        # 70-74 … 85-89
    0.000, 0.000, 0.000,                 # 90-94 … 100+
]

# ------------------------------------------- [実データ] 2025年 東京都の人口動態

NATURAL_CHANGE_2025 = -54_153        # 日本人の自然増減
NET_DOMESTIC_MIGRATION_2025 = 63_245  # 日本人の国内純移動
NET_FOREIGN_INCREASE_2025 = 62_478    # 外国人住民の純増
NET_MIGRATION_2025 = NET_DOMESTIC_MIGRATION_2025 + NET_FOREIGN_INCREASE_2025

# ------------------------------------------- [実データ] 東京都公式推計（移動あり）

OFFICIAL_PROJECTION = {
    2020: 14_050_000,
    2025: 14_210_000,
    2030: 14_260_000,   # 公式推計上のピーク
    2040: 14_030_000,
    2050: 13_570_000,
    2060: 12_780_000,
    2065: 12_310_000,   # 公式推計の終端。これより先の公式値は存在しない
}

# 2026年7月1日の実績人口（東京都「東京都の人口（推計）」）
ACTUAL_2026 = 14_301_986


def _normalize(weights: list[float]) -> list[float]:
    total = sum(weights)
    return [w / total for w in weights]


def build_base_population() -> list[float]:
    """2020年の年齢3区分人口を5歳階級へ展開する。"""
    w_young = _normalize(W_0_14)
    w_work = _normalize(W_15_64)
    w_old = _normalize(W_65_UP)
    pop = (
        [POP_0_14_2020 * w for w in w_young]
        + [POP_15_64_2020 * w for w in w_work]
        + [POP_65_UP_2020 * w for w in w_old]
    )
    assert len(pop) == N_AGE
    assert abs(sum(pop) - TOTAL_2020) < 1.0
    return pop


def project(
    base: list[float],
    tfr: float,
    steps: int,
    annual_net_migration: float = 0.0,
    migration_decay: float = 1.0,
) -> list[list[float]]:
    """5年刻みで人口を投影する。

    annual_net_migration
        年あたりの純移動数。0 を渡すと移動ゼロシナリオ。
    migration_decay
        1ステップ（5年）ごとに純移動へ掛ける減衰係数。1.0 なら永久に一定。
        東京都公式推計は「地方の若年人口枯渇により転入超過は逓減する」と
        いう減衰シナリオを組み込んでいるため、公式値の再現にはこれが要る。
    """
    fert_shape = _normalize(FERT_SHAPE_RAW)
    # 移動は正負が混在するため合計で正規化し、総和が純移動数に一致させる
    mig_total = sum(MIG_SHAPE_RAW)
    mig_shape = [m / mig_total for m in MIG_SHAPE_RAW]

    pop = list(base)
    history = [list(pop)]
    migration = annual_net_migration

    for _ in range(steps):
        women = [pop[i] * FEMALE_SHARE for i in range(REPRO_START, REPRO_END + 1)]
        births = tfr * sum(f * w for f, w in zip(fert_shape, women))

        nxt = [0.0] * N_AGE
        for i in range(N_AGE - 2):
            nxt[i + 1] = pop[i] * SURVIVAL[i]
        # 最終階級は流入と残存の合計
        nxt[-1] = pop[-2] * SURVIVAL[-2] + pop[-1] * SURVIVAL[-1]
        nxt[0] = births * CHILD_SURVIVAL

        if migration:
            migration_5yr = migration * 5
            for i in range(N_AGE):
                nxt[i] += migration_5yr * mig_shape[i]
                if nxt[i] < 0:
                    nxt[i] = 0.0

        pop = nxt
        migration *= migration_decay
        history.append(list(pop))

    return history


def summarize(history: list[list[float]], base_year: int = 2020, step: int = 5):
    """各ステップの年・総人口・年齢3区分・高齢化率を返す。"""
    rows = []
    for i, pop in enumerate(history):
        total = sum(pop)
        young = sum(pop[IDX_0_14])
        work = sum(pop[IDX_15_64])
        old = sum(pop[IDX_65_UP])
        rows.append({
            "year": base_year + i * step,
            "total": total,
            "age_0_14": young,
            "age_15_64": work,
            "age_65_up": old,
            "aging_rate": old / total * 100 if total else 0.0,
        })
    return rows


def interpolate(rows: list[dict], year: int) -> dict:
    """推計年次の間の年について線形補間する。"""
    years = [r["year"] for r in rows]
    if year in years:
        return rows[years.index(year)]
    for i in range(len(years) - 1):
        if years[i] <= year <= years[i + 1]:
            lo, hi = rows[i], rows[i + 1]
            f = (year - years[i]) / (years[i + 1] - years[i])
            out = {"year": year}
            for k in ("total", "age_0_14", "age_15_64", "age_65_up"):
                out[k] = lo[k] + f * (hi[k] - lo[k])
            out["aging_rate"] = out["age_65_up"] / out["total"] * 100
            return out
    raise ValueError(f"{year} は推計範囲外")


# キャリブレーションで決定したパラメータ。
# 2020-2065年の東京都公式推計7時点に対して RMSE を最小化する
# (migration_decay, TFR) をグリッドサーチした結果。最大乖離 +3.8%。
CALIBRATED_DECAY = 0.76   # 5年ごとに純移動が 0.76 倍へ逓減
CALIBRATED_TFR = 0.90

SCENARIOS = {
    "calibrated": {
        "label": "検証用：移動あり（公式推計の再現）TFR 0.90・移動減衰 0.76",
        "tfr": CALIBRATED_TFR,
        "migration": float(NET_MIGRATION_2025),
        "decay": CALIBRATED_DECAY,
    },
    "migration_constant": {
        "label": "参考：移動が減衰せず現水準で継続 TFR 0.90",
        "tfr": CALIBRATED_TFR,
        "migration": float(NET_MIGRATION_2025),
        "decay": 1.0,
    },
    "zero_tfr090": {
        "label": "移動ゼロ・TFR 0.90（キャリブレーション整合の主シナリオ）",
        "tfr": CALIBRATED_TFR,
        "migration": 0.0,
        "decay": 1.0,
    },
    "zero_tfr100": {
        "label": "移動ゼロ・TFR 1.00",
        "tfr": 1.00,
        "migration": 0.0,
        "decay": 1.0,
    },
    "zero_tfr136": {
        "label": "移動ゼロ・TFR 1.36（全国中位水準まで回復した場合）",
        "tfr": 1.36,
        "migration": 0.0,
        "decay": 1.0,
    },
}

REPORT_YEARS = [2026, 2030, 2050, 2075, 2100]
STEPS = 16  # 2020 → 2100

BASELINE_KEY = "calibrated"
MAIN_ZERO_KEY = "zero_tfr090"


def run_all() -> dict[str, list[dict]]:
    base = build_base_population()
    results = {}
    for key, cfg in SCENARIOS.items():
        history = project(
            base,
            tfr=cfg["tfr"],
            steps=STEPS,
            annual_net_migration=cfg["migration"],
            migration_decay=cfg.get("decay", 1.0),
        )
        results[key] = summarize(history)
    return results


def print_tables(results: dict[str, list[dict]]) -> None:
    print("=" * 82)
    print("東京都 簡易コーホート要因法モデル（5歳階級・5年ステップ）")
    print("=" * 82)

    for key, cfg in SCENARIOS.items():
        rows = results[key]
        print(f"\n■ {cfg['label']}")
        print(f"{'年':>6} | {'総人口':>10} | {'0-14歳':>9} | {'15-64歳':>9} | "
              f"{'65歳以上':>9} | {'高齢化率':>7}")
        print("-" * 70)
        for year in REPORT_YEARS:
            r = interpolate(rows, year)
            print(f"{year:>6} | {r['total'] / 10000:>8.1f}万 | "
                  f"{r['age_0_14'] / 10000:>7.1f}万 | {r['age_15_64'] / 10000:>7.1f}万 | "
                  f"{r['age_65_up'] / 10000:>7.1f}万 | {r['aging_rate']:>6.1f}%")

    print("\n" + "=" * 82)
    print("検証：キャリブレーション済モデル と 東京都公式推計 の対比")
    print("=" * 82)
    calib = results[BASELINE_KEY]
    print(f"{'年':>6} | {'モデル':>10} | {'公式推計':>10} | {'乖離':>10} | {'乖離率':>7}")
    print("-" * 60)
    worst = 0.0
    for year, official in OFFICIAL_PROJECTION.items():
        r = interpolate(calib, year)
        diff = r["total"] - official
        worst = max(worst, abs(diff / official * 100))
        print(f"{year:>6} | {r['total'] / 10000:>8.1f}万 | {official / 10000:>8.1f}万 | "
              f"{diff / 10000:>+8.1f}万 | {diff / official * 100:>+6.1f}%")
    print(f"\n最大乖離率: {worst:.1f}%")

    print(f"\n参考：2026年7月1日 実績 {ACTUAL_2026 / 10000:.1f}万人")
    r2026 = interpolate(calib, 2026)
    print(f"      同年 キャリブレーション済モデル {r2026['total'] / 10000:.1f}万人 "
          f"（乖離 {(r2026['total'] - ACTUAL_2026) / 10000:+.1f}万人）")

    print("\n" + "=" * 82)
    print("移動への依存度：キャリブレーション済（移動あり） と 移動ゼロ の差")
    print("=" * 82)
    zero = results[MAIN_ZERO_KEY]
    print(f"{'年':>6} | {'移動あり':>10} | {'移動ゼロ':>10} | {'差':>10} | {'依存率':>7}")
    print("-" * 60)
    for year in REPORT_YEARS:
        a = interpolate(calib, year)["total"]
        b = interpolate(zero, year)["total"]
        print(f"{year:>6} | {a / 10000:>8.1f}万 | {b / 10000:>8.1f}万 | "
              f"{(a - b) / 10000:>+8.1f}万 | {(a - b) / a * 100:>6.1f}%")


def write_csv(results: dict[str, list[dict]], path: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "scenario", "scenario_label", "year", "total",
            "age_0_14", "age_15_64", "age_65_up", "aging_rate_pct",
        ])
        for key, cfg in SCENARIOS.items():
            for r in results[key]:
                writer.writerow([
                    key, cfg["label"], r["year"],
                    round(r["total"]), round(r["age_0_14"]),
                    round(r["age_15_64"]), round(r["age_65_up"]),
                    round(r["aging_rate"], 2),
                ])
    print(f"\nCSV を書き出しました: {path}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", metavar="PATH", help="全系列を CSV に書き出す")
    args = parser.parse_args()

    results = run_all()
    print_tables(results)
    if args.csv:
        write_csv(results, args.csv)


if __name__ == "__main__":
    main()
