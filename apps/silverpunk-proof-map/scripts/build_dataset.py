#!/usr/bin/env python3
"""data/normalized/ から、画面契約（設計仕様書 §6.2）に沿った静的JSONを決定的に生成する。

  python3 scripts/build_dataset.py

同じ入力からは常に同じ出力になる（generated_atのみ実行時刻）。
verified な指標は population / aged_share の2つだけ。hazard_exposure・support_points・
supporter_ratio・拠点情報は未取得のため missing とし、demo priority は算出しない
（設計仕様書 §6.3: 必須入力が揃わない場合は not_computable）。
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
NORMALIZED = BASE / "data" / "normalized" / "population.json"
SOURCES_MANIFEST = BASE / "evidence" / "sources.json"
OUT = BASE / "data" / "proof_map.json"
OUT_SCENARIO_INPUTS = BASE / "data" / "normalized" / "heat_disaster.json"
OUT_GAPS = BASE / "data" / "gaps.json"

HEAT_DISASTER_SCENARIO = {
    "id": "heat_disaster",
    "label": "猛暑・災害",
    "description": "暑熱と災害時に、高齢者・要配慮者が休憩・給水・医療介護・避難の拠点へ到達できるかを、地区単位の公開データで比較する",
    "score_version": "demo-0.1",
    "required_inputs": ["aged_share", "hazard_exposure", "support_points"],
    "caution": "経路の安全を保証しない。緊急時は自治体・気象庁等の公式情報を確認する",
}

MISSING_METRICS = {
    "daytime_workers": {"unit": "人", "label": "昼間就業者", "note": "未取得（東京都昼夜間人口関連の公開データを次に探す）"},
    "elderly_workers": {"unit": "人", "label": "65歳以上就業者", "note": "未取得"},
    "supporter_ratio": {"unit": "人/人", "label": "支え手比率", "note": "未取得（昼間就業者データが無いため算出不可）"},
    "hazard_exposure": {"unit": "指数(0-100)", "label": "暑熱・災害曝露指数", "note": "未取得（暑熱・災害曝露の指標データを次に探す）"},
    "support_points": {"unit": "件", "label": "生活支援拠点数", "note": "未取得（生活支援拠点カテゴリ別の一次情報を次に探す）"},
}

FACILITY_CATEGORIES = [
    {"category": "heat_shelter", "label": "涼しく休める場所"},
    {"category": "water_rest", "label": "給水・休憩拠点"},
    {"category": "medical_care", "label": "医療・介護の相談先"},
    {"category": "evacuation", "label": "避難所・避難場所"},
]


def build_district(m: dict, retrieved_at: str) -> dict:
    metrics = {
        "population": {
            "value": m["population_total"], "unit": "人", "year": m["year"],
            "status": "verified", "source_id": m["source_id"], "as_of": retrieved_at,
        },
        "aged_share": {
            "value": m["aged_share_pct"], "unit": "%", "year": m["year"],
            "status": "verified", "source_id": m["source_id"], "as_of": retrieved_at,
        },
    }
    for key, spec in MISSING_METRICS.items():
        metrics[key] = {
            "value": None, "unit": spec["unit"], "year": None,
            "status": "missing", "note": spec["note"],
        }

    facilities = [
        {
            "category": f["category"], "label": f["label"], "count": None, "unit": "件",
            "status": "missing", "as_of": None, "note": "未取得。Phase 2 の次段階で一次情報を探す",
        }
        for f in FACILITY_CATEGORIES
    ]

    return {
        "id": f"tokyo-{m['code']}",
        "name": m["name"],
        "level": "municipality",
        "note": "自治体コードと人口・高齢化率は verified（IPSS令和5年推計、2020年国勢調査実績値）。"
                "その他の指標は本パイプラインではまだ取得していない",
        "metrics": metrics,
        "facilities": facilities,
        # gaps は明示的に空にする。missing の指標・拠点は metrics / facilities の status から
        # 画面側（gapItems()）が自動的に拾う設計のため、ここで同じ内容を重複登録しない
        "gaps": [],
        "priority": {
            "value": None, "unit": "score(0-1)", "version": "demo-0.1",
            "status": "not_computable",
            "calculation": "heat_disaster の必須入力 hazard_exposure, support_points が missing のため算出しない",
        },
        "pilot": {
            "hypothesis": "人口・高齢化率は確認できたが、暑熱曝露・生活支援拠点データが無く、"
                           "優先度そのものを比較できない",
            "actions_30d": [
                "暑熱曝露の代替指標（緑被率・アスファルト率等）の候補データを探す",
                "生活支援拠点（医療・介護・休憩・避難）の一次情報の候補を洗い出す",
            ],
            "measurement": "測定方法を決める",
            "stop_conditions": ["候補データが1件も見つからない"],
            "next_decision": "hazard_exposure と support_points のいずれかが verified になったら priority 再計算を検討",
        },
    }


def build_scenario_inputs(districts: list[dict], scenario: dict) -> list[dict]:
    """スコア計算に使う必須入力だけを、対象年・単位を揃えて取り出す（設計仕様書 §6.3 の下ごしらえ）。

    district本体（proof_map.json）の抜粋であり、値そのものはそちらが原本。
    「このシナリオはこの3つの入力しか使わない」ことを監査しやすくするための専用ビュー。
    """
    required = scenario["required_inputs"]
    rows = []
    for d in districts:
        inputs = {key: d["metrics"][key] for key in required}
        computable = all(inputs[key]["status"] in ("verified", "illustrative") for key in required)
        rows.append({
            "district_id": d["id"],
            "name": d["name"],
            "inputs": inputs,
            "computable": computable,
        })
    return rows


def build_gaps(districts: list[dict]) -> dict:
    """「次に取得・現地確認するデータ」を優先度順に集計する。個別地区の欠損一覧ではなく全体の集計。

    district本体の gaps 配列（明示的な追加欠損）と、metrics / facilities の missing 状態の
    両方を数える。画面側の gapItems() と同じ集計対象にすることで、件数の食い違いを避ける。
    """
    counts: dict[str, dict] = {}
    total = len(districts)

    def add(item: str, status: str, note: str) -> None:
        entry = counts.setdefault(item, {"item": item, "status": status, "affected_districts": 0, "note": note})
        entry["affected_districts"] += 1

    for d in districts:
        for g in d["gaps"]:
            add(g["item"], g["status"], g["note"])
        for key, m in d["metrics"].items():
            if m["status"] in ("missing", "not_verified", "not_comparable"):
                add(MISSING_METRICS.get(key, {}).get("label", key), m["status"], m.get("note", ""))
        for f in d["facilities"]:
            if f["status"] in ("missing", "not_verified", "not_comparable"):
                add(f["label"], f["status"], f.get("note", ""))

    ranked = sorted(counts.values(), key=lambda e: e["affected_districts"], reverse=True)
    for e in ranked:
        e["share"] = round(e["affected_districts"] / total, 3) if total else None

    return {
        "schema_version": "0.1.0",
        "source": "data/proof_map.json",
        "total_districts": total,
        "note": "件数が多い項目ほど、次に取得すべきデータの優先度が高い（多くの地区の比較を止めているため）",
        "gap_summary": ranked,
    }


def main() -> int:
    if not NORMALIZED.exists():
        print(f"build_dataset: {NORMALIZED} が無い。先に normalize_data.py を実行して", file=sys.stderr)
        return 2

    normalized = json.loads(NORMALIZED.read_text(encoding="utf-8"))
    sources_manifest = json.loads(SOURCES_MANIFEST.read_text(encoding="utf-8")) if SOURCES_MANIFEST.exists() else {"sources": []}

    src = next((s for s in sources_manifest["sources"] if s["id"] == normalized["source_id"]), None)
    if src is None:
        print(f"build_dataset: source_id '{normalized['source_id']}' が evidence/sources.json に無い", file=sys.stderr)
        return 2

    # このビルドで実際に人口xlsxを開いて数値を確認した日をas_ofとする（sources.jsonの候補記録とは別に、
    # このデータセットが実際に検証された日を残す）
    retrieved_at = datetime.now(timezone.utc).date().isoformat()

    districts = [build_district(m, retrieved_at) for m in normalized["municipalities"]]

    payload = {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "as_of": retrieved_at,
        "status": "phase2-partial",
        "sources": [
            {
                "id": src["id"], "title": src["title"], "url": src["url"],
                "retrieved_at": retrieved_at, "verification": "verified",
                "note": "総数・65歳以上人口・高齢化率（2020年実績値）をopenpyxlで実際に開いて確認した。"
                        "他の指標はこのソースに含まれない",
            }
        ],
        "scenarios": [HEAT_DISASTER_SCENARIO],
        "districts": districts,
    }

    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    computable = sum(1 for d in districts if d["priority"]["status"] != "not_computable")
    print(f"✓ {len(districts)} 自治体（すべて実在の東京都区市町村）を {OUT} に出力")
    print(f"  population/aged_share: verified（{normalized['target_year']}年実績値、{src['title']}）")
    print(f"  demo priority 算出可能: {computable}/{len(districts)} 件"
          "（hazard_exposure・support_points が全自治体で未取得のため0件が正しい状態）")

    scenario_inputs = build_scenario_inputs(districts, HEAT_DISASTER_SCENARIO)
    OUT_SCENARIO_INPUTS.parent.mkdir(parents=True, exist_ok=True)
    OUT_SCENARIO_INPUTS.write_text(json.dumps({
        "schema_version": "0.1.0",
        "scenario_id": HEAT_DISASTER_SCENARIO["id"],
        "required_inputs": HEAT_DISASTER_SCENARIO["required_inputs"],
        "districts": scenario_inputs,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ シナリオ入力抽出（heat_disaster）を {OUT_SCENARIO_INPUTS} に出力")

    gaps = build_gaps(districts)
    OUT_GAPS.write_text(json.dumps(gaps, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ 欠損集計を {OUT_GAPS} に出力（{len(gaps['gap_summary'])}種類の欠損項目）")
    for g in gaps["gap_summary"]:
        print(f"   - {g['item']}: {g['affected_districts']}/{gaps['total_districts']} 地区で未取得")

    return 0


if __name__ == "__main__":
    sys.exit(main())
