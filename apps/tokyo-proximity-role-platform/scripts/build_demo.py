#!/usr/bin/env python3
"""D0合成デモデータの生成。data/demo/cells.json, infrastructure.json, roles.json を書き出す。

決定論性: 乱数・時刻・環境依存を一切使わない。同じスクリプトから常に同じ出力になる（MAP-007）。
デモ仮定の根拠は DECISIONS.md の ADR-0002〜0006 を参照。
"""
import json
import math
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent
DEMO_DIR = APP_ROOT / "data" / "demo"

COLS = 8
ROWS = 6
RESOLUTION_M = 250
REFERENCE_SPEED_M_PER_MIN = 80

REQUIRED_FUNCTIONS = ["pharmacy", "clinic", "welfare", "mobility_node"]

# 合成の施設仮想配置点（グリッド座標）。実在施設ではない。ADR-0003。
FACILITY_ANCHORS = {
    "pharmacy": [(1, 1), (6, 4)],
    "clinic": [(3, 0), (7, 2)],
    "welfare": [(6, 1)],
    "mobility_node": [(0, 3), (7, 5)],
}


def nearest_distance_m(col, row, anchors):
    return min(
        math.hypot(col - a_col, row - a_row) * RESOLUTION_M
        for a_col, a_row in anchors
    )


def households_for(col, row):
    # 決定論的な合成世帯数。実在人口統計ではない。
    return ((col * 3 + row * 5) % 11) + 1


def is_welfare_data_gap(col, row):
    # 福祉データが未評価のデモ用地帯（ADR-0002: 未評価は灰ハッチで示す）。
    return col >= 6 and row >= 4


def build_cells():
    cells = []
    for row in range(ROWS):
        for col in range(COLS):
            households = households_for(col, row)
            population = round(households * 1.8)
            slope_index = round(row / (ROWS - 1), 2) if ROWS > 1 else 0.0

            base_access_minutes = {
                fn: round(nearest_distance_m(col, row, anchors) / REFERENCE_SPEED_M_PER_MIN, 1)
                for fn, anchors in FACILITY_ANCHORS.items()
            }

            data_quality = {fn: "demo" for fn in REQUIRED_FUNCTIONS}
            data_quality["food"] = "unassessed"  # ADR-0002: 全都カバー未確認のため常に未評価
            if is_welfare_data_gap(col, row):
                data_quality["welfare"] = "unassessed"

            cells.append({
                "cell_id": f"DEMO-{row:02d}{col:02d}",
                "demo": True,
                "grid": {"col": col, "row": row},
                "analysis_resolution_m": RESOLUTION_M,
                "elderly_population": population,
                "elderly_single_households": households,
                "data_quality": data_quality,
                "base_access_minutes": base_access_minutes,
                "slope_index": slope_index,
            })
    return cells


def build_infrastructure():
    return {
        "demo": True,
        "walking_profiles": [
            {"id": "slow_senior", "label": "高齢者目安", "speed_m_per_min": 60},
            {"id": "cane_assist", "label": "杖使用等", "speed_m_per_min": 45},
            {"id": "wheelchair_user", "label": "車椅子等利用者", "speed_m_per_min": 55},
            {"id": "standard", "label": "成人目安", "speed_m_per_min": 80},
        ],
        "reference_speed_m_per_min": REFERENCE_SPEED_M_PER_MIN,
        "slope_model": {
            "id": "demo-linear-v1",
            "max_uphill_factor": 0.4,
            "note": "デモ仮定。実測標高・実測歩行データではない（DECISIONS.md ADR-0003）。",
        },
        "priority_thresholds": {
            "min_population_threshold": 3,
            "priority_households_threshold": 8,
        },
        "intervention_types": [
            {
                "type": "local_service_point",
                "label": "小規模生活拠点",
                "description": "食料・薬受取等の小規模拠点を仮置きする",
                "affected_functions": ["pharmacy", "clinic", "welfare"],
                "radius_cells": 1,
                "daily_capacity_households": None,
            },
            {
                "type": "human_bridge",
                "label": "Human Bridge（暫定人的支援）",
                "description": "配送・同行・送迎等の暫定人的支援。容量制約あり（ADR-0005）",
                "affected_functions": ["welfare"],
                "radius_cells": 2,
                "daily_capacity_households": 10,
            },
            {
                "type": "mobility_stop",
                "label": "モビリティノード",
                "description": "短距離モビリティ乗降点を仮置きする",
                "affected_functions": ["mobility_node"],
                "radius_cells": 2,
                "daily_capacity_households": None,
            },
        ],
    }


ROLE_TEMPLATES = [
    {
        "problem_type": "food_access",
        "title": "電話・端末による注文受付",
        "task_units": ["注文内容を定型画面へ入力", "受渡し時間を案内"],
        "functional_requirements": {
            "main_posture": "seated",
            "lifting_kg_max": 0,
            "standing_minutes_max": 10,
            "customer_contact": True,
        },
        "supervision": "required_initially",
        "compensation_required": True,
        "route_candidates": ["senior_employment", "disability_employment", "welfare_work"],
        "schedule": {"min_minutes": 60, "frequency": "weekly"},
    },
    {
        "problem_type": "pharmacy_access",
        "title": "薬受取・配送の受渡し窓口",
        "task_units": ["処方引換券の確認", "受渡し記録の記入", "配送業者への引継ぎ"],
        "functional_requirements": {
            "main_posture": "seated",
            "lifting_kg_max": 3,
            "standing_minutes_max": 15,
            "customer_contact": True,
        },
        "supervision": "required_initially",
        "compensation_required": True,
        "route_candidates": ["silver_human_resources", "welfare_work", "community_participation"],
        "schedule": {"min_minutes": 90, "frequency": "weekly"},
    },
    {
        "problem_type": "welfare_access",
        "title": "見守り訪問の同行支援",
        "task_units": ["訪問予定の確認", "同行", "訪問記録の共有"],
        "functional_requirements": {
            "main_posture": "mixed",
            "lifting_kg_max": 0,
            "standing_minutes_max": 30,
            "customer_contact": True,
        },
        "supervision": "required_ongoing",
        "compensation_required": True,
        "route_candidates": ["welfare_work", "disability_employment"],
        "schedule": {"min_minutes": 120, "frequency": "weekly"},
    },
    {
        "problem_type": "mobility_gap",
        "title": "乗降支援・ルート案内",
        "task_units": ["乗降時の声かけ・付き添い", "ルートの案内", "運行状況の共有"],
        "functional_requirements": {
            "main_posture": "standing",
            "lifting_kg_max": 5,
            "standing_minutes_max": 60,
            "customer_contact": True,
        },
        "supervision": "required_initially",
        "compensation_required": True,
        "route_candidates": ["senior_employment", "silver_human_resources", "community_participation"],
        "schedule": {"min_minutes": 60, "frequency": "weekly"},
    },
    {
        "problem_type": "clinic_access",
        "title": "受診予約・端末操作支援",
        "task_units": ["予約端末の操作補助", "受診票の記入補助（代理権限を要する手続きは対象外）"],
        "functional_requirements": {
            "main_posture": "seated",
            "lifting_kg_max": 0,
            "standing_minutes_max": 5,
            "customer_contact": True,
        },
        "supervision": "required_initially",
        "compensation_required": True,
        "route_candidates": ["welfare_work", "community_participation"],
        "schedule": {"min_minutes": 45, "frequency": "weekly"},
    },
]


def build_roles():
    return {
        "demo": True,
        "note": "承認済みテンプレートカタログ。AIはこの中から下書きを生成し、自由生成しない（SPEC.md §4.2）。",
        "templates": ROLE_TEMPLATES,
    }


def build_demo_readme(cells):
    unassessed_welfare = sum(1 for c in cells if c["data_quality"]["welfare"] == "unassessed")
    low_pop = sum(1 for c in cells if c["elderly_single_households"] < 3)
    lines = [
        "# data/demo/ — D0合成データの仮定一覧",
        "",
        "このディレクトリのデータはすべて合成デモデータである。実在地域名・実在人数ではない。",
        "画面（prototype/index.html）に常に `DEMO DATA / NOT FOR POLICY DECISION` を表示している。",
        "この値をREADMEの事実説明や政策判断へ転記してはならない（AGENTS.md §5.1）。",
        "",
        "## 生成方法",
        "",
        "`scripts/build_demo.py` により決定論的に生成する（乱数・時刻に依存しない）。再実行しても同じ出力になる。",
        "",
        "## 仮定一覧",
        "",
        f"- 分析単位: {RESOLUTION_M}m メッシュ、合成グリッド {COLS}列×{ROWS}行（{COLS*ROWS}セル）",
        f"- 基準歩行速度: {REFERENCE_SPEED_M_PER_MIN} m/min（ADR-0003のデモ仮定）",
        "- 各セル×機能の基準到達時間: 合成の施設仮想配置点までのユークリッド距離を基準速度で除した合成値。実道路経路ではない",
        "- 勾配モデル: `demo-linear-v1`。補正ONで最大+40%（実測標高ではない。ADR-0003）",
        "- 必須生活機能（色分類対象）: pharmacy / clinic / welfare / mobility_node の4機能のみ（ADR-0002）",
        "- `food` は全セルで常に未評価（`data_quality.food = \"unassessed\"`）。全都カバー未確認のため（SPEC.md §5.3）",
        f"- 福祉データ未評価地帯: {unassessed_welfare}セル（col>=6 and row>=4）。灰ハッチ表示の検証用（MAP-004）",
        f"- 対象人口が基準未満（薄灰表示対象、households<3）のセル: {low_pop}セル",
        "- 優先基準: `min_population_threshold=3`, `priority_households_threshold=8`（ADR-0004のデモ仮定）",
        "- 高齢単身世帯数・人口は決定論的な合成式によるものであり、実在の人口統計ではない",
        "",
        "## 未確定事項",
        "",
        "対象地域・必須機能セット・歩行速度モデル・優先基準の正式な確定は `OPEN-ISSUES.md` を参照。",
    ]
    return "\n".join(lines) + "\n"


def main():
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    cells = build_cells()
    infrastructure = build_infrastructure()
    roles = build_roles()

    (DEMO_DIR / "cells.json").write_text(
        json.dumps({"demo": True, "cells": cells}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (DEMO_DIR / "infrastructure.json").write_text(
        json.dumps(infrastructure, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (DEMO_DIR / "roles.json").write_text(
        json.dumps(roles, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (DEMO_DIR / "README.md").write_text(build_demo_readme(cells), encoding="utf-8")

    print(f"generated {len(cells)} cells -> {DEMO_DIR / 'cells.json'}")
    print(f"generated infrastructure -> {DEMO_DIR / 'infrastructure.json'}")
    print(f"generated {len(ROLE_TEMPLATES)} role templates -> {DEMO_DIR / 'roles.json'}")


if __name__ == "__main__":
    main()
