#!/usr/bin/env python3
"""東京都オープンデータ全カタログCSVをタイトル検索し、D1〜D5のリソースURLを解決する。

URLをここに書き写して固定しない。呼ぶたびにカタログCSVを検索し直す
（カタログが更新されればURL・更新日も追随する）。

  from catalog import resolve_all
  resolved = resolve_all("江東区")   # {"D1": {...} | None, ...}

各値は None（未解決）か、以下のキーを持つ辞書:
  scope        "ward"（区が直接公開）| "prefecture_wide"（都全域データで代替）
  title / org / format / updated_at / dataset_url / resource_url
"""
from __future__ import annotations

import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
APP_DIR = HERE.parent
REPO_ROOT = APP_DIR.parent.parent
CATALOG_PATH = (
    REPO_ROOT / "docs" / "research" / "data"
    / "東京都オープンデータ全カタログ_9678件_20260704.csv"
)

# 検索語・除外語は design-spec §3 の「探し方」に対応する。
# fallback_contains は、都全域フォールバックが複数ヒットしたときに
# 「これが一覧そのものである」と絞り込むための語（2026-08-23 実測で確認済み）。
DATASETS = {
    "D1": {
        "label": "避難所・避難場所",
        "terms": ("避難所", "避難場所"),
        "exclude": (),
        "fallback_contains": "一覧データ",
    },
    "D2": {
        "label": "クーリングシェルター/涼み処",
        "terms": ("クーリングシェルター", "暑さ", "涼み"),
        "exclude": (),
        "fallback_contains": None,
    },
    "D3": {
        "label": "医療機関",
        # 「XX実施医療機関一覧」は手続き特化の予防接種・検査台帳であり、
        # 一般的な医療機関一覧ではないため除外する（OPEN-ISSUES.md 参照）。
        "terms": ("医療機関", "病院"),
        "exclude": ("実施医療機関",),
        "fallback_contains": "災害拠点病院",
    },
    "D4": {
        "label": "介護・福祉施設",
        "terms": ("介護", "福祉施設"),
        "exclude": (),
        "fallback_contains": None,
    },
    "D5": {
        "label": "町丁別・年齢別人口",
        "terms": ("住民基本台帳", "町丁"),
        "exclude": (),
        "fallback_contains": None,
    },
}

PREFECTURE_ORG_PREFIX = "東京都"


def load_catalog(path: Path = CATALOG_PATH) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _matches(row: dict, terms: tuple[str, ...]) -> bool:
    return any(t in row["タイトル"] for t in terms)


def _row_info(row: dict, scope: str) -> dict:
    return {
        "scope": scope,
        "title": row["タイトル"],
        "org": row["所管"],
        "format": row["形式"],
        "updated_at": row["更新日"],
        "dataset_url": row["データセットURL"],
        "resource_url": row["リソースURL(先頭)"],
    }


def _safe_int(s: str) -> int:
    try:
        return int(s)
    except ValueError:
        return 0


def resolve_one(rows: list[dict], spec: dict, ward: str) -> dict | None:
    candidates = [
        r for r in rows
        if _matches(r, spec["terms"]) and not _matches(r, spec["exclude"])
    ]

    ward_rows = [r for r in candidates if ward in r["所管"] or ward in r["タイトル"]]
    ward_csv_rows = [r for r in ward_rows if "CSV" in r["形式"]]
    pick_from = ward_csv_rows or ward_rows
    if pick_from:
        best = max(pick_from, key=lambda r: _safe_int(r["リソース数"]))
        return _row_info(best, "ward")

    wide_rows = [
        r for r in candidates
        if r["所管"].startswith(PREFECTURE_ORG_PREFIX) and "CSV" in r["形式"]
    ]
    if spec["fallback_contains"]:
        narrowed = [r for r in wide_rows if spec["fallback_contains"] in r["タイトル"]]
        if narrowed:
            wide_rows = narrowed
    if wide_rows:
        # 一覧そのものは名前が短く素直な傾向がある（統計報告書等は長くなりがち）
        best = min(wide_rows, key=lambda r: len(r["タイトル"]))
        return _row_info(best, "prefecture_wide")

    return None


def resolve_all(ward: str, path: Path = CATALOG_PATH) -> dict[str, dict | None]:
    rows = load_catalog(path)
    return {id_: resolve_one(rows, spec, ward) for id_, spec in DATASETS.items()}


if __name__ == "__main__":
    import json
    import sys

    ward = sys.argv[1] if len(sys.argv) > 1 else "江東区"
    print(json.dumps(resolve_all(ward), ensure_ascii=False, indent=1))
