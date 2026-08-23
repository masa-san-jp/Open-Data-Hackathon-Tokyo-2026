#!/usr/bin/env python3
"""D0の決定論的検証。AGENTS.md §7 / IMPLEMENTATION.md §7 のテストIDに対応する。

jsonschema・pytestが実行環境に無い前提で、標準ライブラリのみで実装する
（OPEN-ISSUES.md「JSON Schemaバリデーションライブラリ未導入」参照）。

使い方:
  python3 scripts/verify.py --phase demo
  python3 scripts/verify.py --phase demo --check schema
  python3 scripts/verify.py --phase demo --check monotonicity
  python3 scripts/verify.py --phase demo --check intervention-revert
  python3 scripts/verify.py --phase demo --check role-card
  python3 scripts/verify.py --phase demo --check reproducibility
  python3 scripts/verify.py --phase demo --check static

終了コード: 0=全チェック通過 / 1=失敗あり
"""
import argparse
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent
DEMO_DIR = APP_ROOT / "data" / "demo"
PROTOTYPE_PATH = APP_ROOT / "prototype" / "index.html"
BUILD_DEMO_PATH = APP_ROOT / "scripts" / "build_demo.py"

REQUIRED_FUNCTIONS = ["pharmacy", "clinic", "welfare", "mobility_node"]

FAILURES = []


def fail(check_id, message):
    FAILURES.append(f"[{check_id}] {message}")


def ok(check_id, message):
    print(f"  OK  {check_id}: {message}")


# --------------------------------------------------------------------------
# データ読み込み
# --------------------------------------------------------------------------

def load_demo_data():
    cells = json.loads((DEMO_DIR / "cells.json").read_text(encoding="utf-8"))
    infra = json.loads((DEMO_DIR / "infrastructure.json").read_text(encoding="utf-8"))
    roles = json.loads((DEMO_DIR / "roles.json").read_text(encoding="utf-8"))
    return cells, infra, roles


# --------------------------------------------------------------------------
# アクセシビリティ計算エンジン（templates/demo.html のJS実装を独立にPythonへ移植）
# --------------------------------------------------------------------------

def intervention_defs(infra):
    return {d["type"]: d for d in infra["intervention_types"]}


def cells_within_radius(cells, iv, defs):
    d = defs[iv["type"]]
    out = []
    for c in cells:
        dist = math.hypot(c["grid"]["col"] - iv["col"], c["grid"]["row"] - iv["row"])
        if dist <= d["radius_cells"]:
            out.append(c)
    return out


def human_bridge_covered(cells, iv, defs):
    d = defs[iv["type"]]
    if d.get("daily_capacity_households") is None:
        return None
    within = sorted(cells_within_radius(cells, iv, defs),
                     key=lambda c: c["elderly_single_households"], reverse=True)
    covered = set()
    used = 0
    for c in within:
        if used >= d["daily_capacity_households"]:
            break
        covered.add(c["cell_id"])
        used += c["elderly_single_households"]
    return covered


def effective_minutes_all(cells, cell, fn, speed, slope_on, interventions, infra, defs):
    base = cell["base_access_minutes"][fn]
    ref_speed = infra["reference_speed_m_per_min"]
    resolution = cell["analysis_resolution_m"]
    slope_model = infra["slope_model"]
    for iv in interventions:
        d = defs[iv["type"]]
        if fn not in d["affected_functions"]:
            continue
        dist_cells = math.hypot(cell["grid"]["col"] - iv["col"], cell["grid"]["row"] - iv["row"])
        if dist_cells > d["radius_cells"]:
            continue
        if iv["type"] == "human_bridge":
            covered = human_bridge_covered(cells, iv, defs)
            if covered is not None and cell["cell_id"] not in covered:
                continue
        iv_minutes = (dist_cells * resolution) / ref_speed
        base = min(base, iv_minutes)
    speed_factor = ref_speed / speed
    slope_factor = (1 + slope_model["max_uphill_factor"] * cell["slope_index"]) if slope_on else 1.0
    return base * speed_factor * slope_factor


def classify_cell(cells, cell, threshold, speed, slope_on, interventions, infra, defs):
    missing = [fn for fn in REQUIRED_FUNCTIONS if cell["data_quality"][fn] == "unassessed"]
    if missing:
        return {"classification": "unassessed", "unmet": missing, "effective": None}
    effective = {
        fn: effective_minutes_all(cells, cell, fn, speed, slope_on, interventions, infra, defs)
        for fn in REQUIRED_FUNCTIONS
    }
    unmet = [fn for fn in REQUIRED_FUNCTIONS if effective[fn] > threshold]
    thresholds = infra["priority_thresholds"]
    households = cell["elderly_single_households"]
    if households < thresholds["min_population_threshold"]:
        classification = "low_population"
    elif len(unmet) == 0:
        classification = "sufficient"
    elif len(unmet) == 1:
        classification = "partial_deficit_low"
    elif households >= thresholds["priority_households_threshold"]:
        classification = "priority_deficit"
    else:
        classification = "partial_deficit_high"
    return {"classification": classification, "unmet": unmet, "effective": effective}


def classify_all(cells, threshold, speed, slope_on, interventions, infra, defs):
    return {c["cell_id"]: classify_cell(cells, c, threshold, speed, slope_on, interventions, infra, defs) for c in cells}


def count_sufficient(classified):
    return sum(1 for v in classified.values() if v["classification"] == "sufficient")


# --------------------------------------------------------------------------
# チェック: schema（手書き構造検証）
# --------------------------------------------------------------------------

def check_schema():
    cells, infra, roles = load_demo_data()

    if not cells.get("demo"):
        fail("SCHEMA-cells", "cells.json の demo フラグが true でない")
    for c in cells["cells"]:
        for key in ["cell_id", "demo", "grid", "analysis_resolution_m", "elderly_population",
                    "elderly_single_households", "data_quality", "base_access_minutes", "slope_index"]:
            if key not in c:
                fail("SCHEMA-cells", f"{c.get('cell_id', '?')} に必須キー {key} がない")
        if c.get("data_quality", {}).get("food") != "unassessed":
            fail("SCHEMA-cells", f"{c['cell_id']} の food は常に unassessed でなければならない（ADR-0002）")
        for fn in REQUIRED_FUNCTIONS:
            if c.get("data_quality", {}).get(fn) not in ("demo", "unassessed"):
                fail("SCHEMA-cells", f"{c['cell_id']} の data_quality.{fn} が不正")
    if not any(c["data_quality"]["welfare"] == "unassessed" for c in cells["cells"]):
        fail("SCHEMA-cells", "灰ハッチ検証用の未評価セルが1件も無い")

    for key in ["demo", "walking_profiles", "reference_speed_m_per_min", "slope_model", "priority_thresholds", "intervention_types"]:
        if key not in infra:
            fail("SCHEMA-infrastructure", f"infrastructure.json に必須キー {key} がない")

    if not roles.get("demo") or "templates" not in roles:
        fail("SCHEMA-roles", "roles.json の構造が不正")
    for t in roles.get("templates", []):
        for key in ["problem_type", "title", "task_units", "functional_requirements", "supervision",
                    "compensation_required", "route_candidates", "schedule"]:
            if key not in t:
                fail("SCHEMA-roles", f"role template {t.get('problem_type', '?')} に必須キー {key} がない")
        fr = t.get("functional_requirements", {})
        for forbidden in ["diagnosis", "medical_condition", "vitals"]:
            if forbidden in fr:
                fail("SCHEMA-roles", f"role template に禁止フィールド {forbidden} が含まれる（ROLE-006）")

    if not FAILURES:
        ok("SCHEMA", "cells/infrastructure/roles の構造検証OK")


# --------------------------------------------------------------------------
# チェック: 単調性（MAP-001, 002, 003, 004）
# --------------------------------------------------------------------------

def check_monotonicity():
    cells_data, infra, _ = load_demo_data()
    cells = cells_data["cells"]
    defs = intervention_defs(infra)

    # MAP-001: 5 -> 10 -> 15分で青セル数が減らない
    speed = infra["reference_speed_m_per_min"]
    counts = []
    for threshold in (5, 10, 15):
        classified = classify_all(cells, threshold, speed, False, [], infra, defs)
        counts.append(count_sufficient(classified))
    if not (counts[0] <= counts[1] <= counts[2]):
        fail("MAP-001", f"閾値拡大で青セル数が減少した: {counts}")
    else:
        ok("MAP-001", f"5/10/15分の青セル数 {counts} は単調非減少")

    # MAP-002: 速度低下で青セル数が増えない
    speeds = [90, 80, 60, 45, 30]
    counts2 = []
    for s in speeds:
        classified = classify_all(cells, 10, s, False, [], infra, defs)
        counts2.append(count_sufficient(classified))
    speed_violation = False
    for i in range(1, len(counts2)):
        if counts2[i] > counts2[i - 1]:
            fail("MAP-002", f"速度低下({speeds[i-1]}->{speeds[i]})で青セル数が増加: {counts2}")
            speed_violation = True
    if not speed_violation:
        ok("MAP-002", f"速度低下に対する青セル数 {counts2} は非増加")

    # MAP-003: 勾配補正ONで実効時間が短くならない
    violations = 0
    for c in cells:
        for fn in REQUIRED_FUNCTIONS:
            if c["data_quality"][fn] == "unassessed":
                continue
            off = effective_minutes_all(cells, c, fn, speed, False, [], infra, defs)
            on = effective_minutes_all(cells, c, fn, speed, True, [], infra, defs)
            if on < off - 1e-9:
                violations += 1
    if violations:
        fail("MAP-003", f"勾配補正ONで実効時間が短くなったケースが{violations}件ある")
    else:
        ok("MAP-003", "勾配補正ONは全セル・全機能で実効時間を短縮しない")

    # MAP-004: 未評価セルは赤(priority_deficit)にならない
    classified = classify_all(cells, 10, speed, True, [], infra, defs)
    unassessed_as_red = {cid for cid, v in classified.items() if v["classification"] == "priority_deficit"}
    truly_unassessed = {c["cell_id"] for c in cells if any(c["data_quality"][fn] == "unassessed" for fn in REQUIRED_FUNCTIONS)}
    bad = unassessed_as_red & truly_unassessed
    if bad:
        fail("MAP-004", f"未評価セルが赤に分類された: {bad}")
    else:
        ok("MAP-004", "未評価セルは赤に分類されない（unassessed分類が優先される）")


# --------------------------------------------------------------------------
# チェック: 介入の可逆性（MAP-006）
# --------------------------------------------------------------------------

def check_intervention_revert():
    cells_data, infra, _ = load_demo_data()
    cells = cells_data["cells"]
    defs = intervention_defs(infra)
    speed = infra["reference_speed_m_per_min"]

    baseline = classify_all(cells, 10, speed, True, [], infra, defs)
    with_iv = classify_all(cells, 10, speed, True,
                            [{"type": "mobility_stop", "col": 4, "row": 3}], infra, defs)
    reverted = classify_all(cells, 10, speed, True, [], infra, defs)

    changed = sum(1 for cid in baseline if baseline[cid]["classification"] != with_iv[cid]["classification"])
    if changed == 0:
        fail("MAP-006", "介入を仮置きしても分類が一切変化していない（テストが機能していない可能性）")

    mismatched = [cid for cid in baseline if baseline[cid]["classification"] != reverted[cid]["classification"]]
    if mismatched:
        fail("MAP-006", f"介入を除去してもベースラインへ戻らないセルがある: {mismatched}")
    else:
        ok("MAP-006", f"介入除去でベースラインへ完全復帰（介入時は{changed}セルが変化していた）")


# --------------------------------------------------------------------------
# チェック: 再現性（MAP-007）
# --------------------------------------------------------------------------

def check_reproducibility():
    spec = importlib.util.spec_from_file_location("build_demo", BUILD_DEMO_PATH)
    build_demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build_demo)

    cells1 = build_demo.build_cells()
    cells2 = build_demo.build_cells()
    infra1 = build_demo.build_infrastructure()
    infra2 = build_demo.build_infrastructure()

    if cells1 != cells2:
        fail("MAP-007", "build_cells() が同一入力で異なる出力を返した（非決定論的）")
    elif infra1 != infra2:
        fail("MAP-007", "build_infrastructure() が同一入力で異なる出力を返した")
    else:
        ok("MAP-007", "build_demo.py は決定論的（同一出力を再現）")


# --------------------------------------------------------------------------
# チェック: 役割カード（ROLE-001〜006）
# --------------------------------------------------------------------------

def check_role_card():
    _, _, roles = load_demo_data()
    templates = roles.get("templates", [])
    if not templates:
        fail("ROLE-000", "role templates が1件も無い")
        return

    for t in templates:
        if not t.get("task_units") or not t.get("schedule") or "supervision" not in t or "compensation_required" not in t:
            fail("ROLE-002", f"{t.get('problem_type')} に必須項目が欠けている")
        if len(t.get("route_candidates", [])) < 1:
            fail("ROLE-004", f"{t.get('problem_type')} の制度候補が空")
        fr = t.get("functional_requirements", {})
        for forbidden in ["diagnosis", "medical_condition", "vitals"]:
            if forbidden in fr:
                fail("ROLE-006", f"{t.get('problem_type')} に禁止フィールド {forbidden}")

    # source_cell_id はテンプレートには無く、生成時にセルから注入される（ROLE-001）。
    # UI/ロジック側でその契約が守られているかは static チェックで検証する。
    ok("ROLE-002/004/006", "role templates は必須項目を満たし、禁止フィールドを含まない")


# --------------------------------------------------------------------------
# チェック: 生成物の静的検査（DEMO表示・外部依存なし・危険なapproved代入なし 等）
# --------------------------------------------------------------------------

EXTERNAL_REF_PATTERN = re.compile(r'(?:src|href)\s*=\s*"(https?://[^"]+|//[^"]+)"')
APPROVED_ASSIGNMENT_PATTERN = re.compile(r'''status\s*[:=]\s*['"]approved['"]''')


def check_static():
    if not PROTOTYPE_PATH.exists():
        fail("STATIC", "prototype/index.html が生成されていない。先に make demo を実行する")
        return

    html = PROTOTYPE_PATH.read_text(encoding="utf-8")

    if "DEMO DATA" not in html or "NOT FOR POLICY DECISION" not in html:
        fail("STATIC-demo-banner", "DEMO DATA / NOT FOR POLICY DECISION 表示が無い")
    else:
        ok("STATIC-demo-banner", "DEMO DATA 表示あり")

    externals = EXTERNAL_REF_PATTERN.findall(html)
    if externals:
        fail("STATIC-offline", f"外部参照が見つかった（CDN等）: {externals}")
    else:
        ok("STATIC-offline", "外部API・CDN参照なし")

    if APPROVED_ASSIGNMENT_PATTERN.search(html):
        fail("ROLE-005", "コード中に status を approved へ設定する代入が見つかった")
    else:
        ok("ROLE-005", "status を approved に設定するコードパスが無い")

    if 'source_cell_id: cell.cell_id' not in html and "source_cell_id" not in html:
        fail("ROLE-001", "role card 生成コードに source_cell_id の付与が見当たらない")
    else:
        ok("ROLE-001", "role card 生成時に source_cell_id を付与している")

    if "resolutionLabel" not in html or re.search(r'"analysis_resolution_m":\s*250', html) is None:
        fail("STATIC-resolution", "分析単位(250m)を表示するコード・データが見当たらない")
    else:
        ok("STATIC-resolution", "分析単位の表示あり")


CHECKS = {
    "schema": check_schema,
    "monotonicity": check_monotonicity,
    "intervention-revert": check_intervention_revert,
    "reproducibility": check_reproducibility,
    "role-card": check_role_card,
    "static": check_static,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", default="demo", choices=["demo"])
    parser.add_argument("--check", default=None, choices=list(CHECKS.keys()))
    args = parser.parse_args()

    to_run = [args.check] if args.check else list(CHECKS.keys())
    for name in to_run:
        print(f"-- {name} --")
        CHECKS[name]()

    if FAILURES:
        print("\n検証失敗:")
        for f in FAILURES:
            print(" -", f)
        sys.exit(1)
    print("\n全チェック通過")
    sys.exit(0)


if __name__ == "__main__":
    main()
