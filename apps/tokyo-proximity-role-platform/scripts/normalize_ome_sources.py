#!/usr/bin/env python3
"""青梅市の実データ（境界・医療機関・介護サービス事業所）を正規化する。

入力（data/raw/ome/、rawデータは編集しない — AGENTS.md §6）:
  - ome_boundary_n03_2021.geojson  国土数値情報（行政区域）加工版
    出典: 国土交通省 国土数値情報, via smartnews-smri/japan-topography
    retrieved_at: 2026-08-23（元データ取得: 2021-09-28、smartnews-smri記載）
  - 132055_hospital.xlsx            青梅市オープンデータ「医療機関一覧」CC-BY-4.0
  - 132055_care_service.xlsx        青梅市オープンデータ「介護サービス事業所一覧」CC-BY-4.0

出力（data/normalized/ome/）:
  - real_map.json  境界ポリゴン（等距円筒図法で投影したメートル座標）＋施設点

このスクリプトは実データのみを扱う。data/demo/ とは混在させない（AGENTS.md §5.1）。
"""
import json
import math
from pathlib import Path

import openpyxl

APP_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = APP_ROOT / "data" / "raw" / "ome"
OUT_DIR = APP_ROOT / "data" / "normalized" / "ome"

METERS_PER_DEG_LAT = 111320.0


def load_boundary():
    geo = json.loads((RAW_DIR / "ome_boundary_n03_2021.geojson").read_text(encoding="utf-8"))
    coords = geo["geometry"]["coordinates"][0]
    return [(lon, lat) for lon, lat in coords]


def load_facilities(filename, name_col, lat_col, lon_col, type_col, addr_col, function_code):
    wb = openpyxl.load_workbook(RAW_DIR / filename, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    header = rows[0]
    idx = {h: i for i, h in enumerate(header)}
    facilities = []
    for row in rows[1:]:
        lat = row[idx[lat_col]]
        lon = row[idx[lon_col]]
        if lat is None or lon is None:
            continue
        facilities.append({
            "name": row[idx[name_col]],
            "type": row[idx[type_col]],
            "address": row[idx[addr_col]],
            "lat": lat,
            "lon": lon,
            "function_code": function_code,
        })
    return facilities


def project(points_lonlat, lon0, lat0):
    meters_per_deg_lon = METERS_PER_DEG_LAT * math.cos(math.radians(lat0))
    out = []
    for lon, lat in points_lonlat:
        x_m = (lon - lon0) * meters_per_deg_lon
        y_m = (lat - lat0) * METERS_PER_DEG_LAT
        out.append((x_m, y_m))
    return out, meters_per_deg_lon


def point_in_polygon(lon, lat, polygon):
    """境界ポリゴン内かを判定する（境界外座標を黙って採用しないための監査用）。"""
    inside = False
    previous_lon, previous_lat = polygon[-1]
    for current_lon, current_lat in polygon:
        crosses = (current_lat > lat) != (previous_lat > lat)
        if crosses:
            intersection_lon = (previous_lon - current_lon) * (lat - current_lat) / (
                previous_lat - current_lat
            ) + current_lon
            if lon < intersection_lon:
                inside = not inside
        previous_lon, previous_lat = current_lon, current_lat
    return inside


def main():
    boundary_lonlat = load_boundary()
    lons = [p[0] for p in boundary_lonlat]
    lats = [p[1] for p in boundary_lonlat]
    lon0 = (min(lons) + max(lons)) / 2
    lat0 = (min(lats) + max(lats)) / 2

    boundary_m, meters_per_deg_lon = project(boundary_lonlat, lon0, lat0)

    clinics = load_facilities(
        "132055_hospital.xlsx",
        name_col="名称", lat_col="緯度", lon_col="経度",
        type_col="医療機関の種類", addr_col="所在地_連結表記", function_code="clinic",
    )
    welfare = load_facilities(
        "132055_care_service.xlsx",
        name_col="介護サービス事業所名称", lat_col="緯度", lon_col="経度",
        type_col="実施サービス", addr_col="所在地_連結表記", function_code="welfare",
    )

    all_facilities = clinics + welfare
    facility_lonlat = [(f["lon"], f["lat"]) for f in all_facilities]
    facility_m, _ = project(facility_lonlat, lon0, lat0)
    outside_by_function = {}
    for f, (x_m, y_m) in zip(all_facilities, facility_m):
        f["x_m"] = round(x_m, 1)
        f["y_m"] = round(y_m, 1)
        f["within_boundary"] = point_in_polygon(f["lon"], f["lat"], boundary_lonlat)
        f["coordinate_status"] = "inside_boundary" if f["within_boundary"] else "outside_boundary"
        if not f["within_boundary"]:
            code = f["function_code"]
            outside_by_function[code] = outside_by_function.get(code, 0) + 1

    output = {
        "demo": False,
        "area": "青梅市",
        "local_government_code": "13205",
        "projection": {
            "method": "equirectangular_local",
            "note": "青梅市中心付近の緯度でcos補正した等距円筒図法。狭域のみ有効な簡易投影。",
            "lon0": lon0,
            "lat0": lat0,
            "meters_per_deg_lat": METERS_PER_DEG_LAT,
            "meters_per_deg_lon": meters_per_deg_lon,
        },
        "boundary_lonlat": [[round(lon, 7), round(lat, 7)] for lon, lat in boundary_lonlat],
        "boundary_m": [[round(x, 1), round(y, 1)] for x, y in boundary_m],
        "facilities": all_facilities,
        "data_quality_summary": {
            "facility_total": len(all_facilities),
            "within_boundary": len(all_facilities) - sum(outside_by_function.values()),
            "outside_boundary": sum(outside_by_function.values()),
            "outside_by_function": outside_by_function,
            "coordinate_rule": "施設の緯度経度を行政区域ポリゴンへpoint-in-polygon判定。境界外は地図表示から除外し、データ監査対象として残す。",
        },
        "display_sources": [
            {
                "id": "osm_standard_tiles_display_only",
                "title": "OpenStreetMap 標準タイル（表示専用）",
                "provider": "OpenStreetMap contributors / OpenStreetMap Foundation",
                "source_url": "https://www.openstreetmap.org/copyright",
                "tile_url": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                "license": "Open Database License (ODbL)",
                "notes": "オンライン時の背景表示だけに使用。施設データ、道路経路、徒歩時間、アクセシビリティ計算の入力には使用しない。タイル取得に失敗した場合は座標グリッドへフォールバックする。",
            }
        ],
        "sources": [
            {
                "id": "ome_boundary_n03_2021",
                "title": "青梅市 行政区域境界（国土数値情報 加工版）",
                "provider": "国土交通省 国土数値情報（smartnews-smri/japan-topography 加工）",
                "source_url": "https://github.com/smartnews-smri/japan-topography",
                "license": "国土数値情報利用規約（国土交通省クレジット表示が必要）。加工版はスマートニュース社クレジット不要、商用・非商用問わず無償利用可",
                "retrieved_at": "2026-08-23",
                "notes": "元データ取得はsmartnews-smri記載で2021-09-28（令和3年1月1日時点の行政区域）。境界線は1%に簡素化済み。",
            },
            {
                "id": "ome_clinic_list_2025",
                "title": "東京都青梅市における医療機関一覧",
                "provider": "青梅市",
                "source_url": "https://www.opendata.metro.tokyo.lg.jp/ome/132055_hospital.xlsx",
                "license": "CC-BY-4.0",
                "retrieved_at": "2026-08-23",
                "notes": f"{len(clinics)}件。",
            },
            {
                "id": "ome_welfare_care_service_2025",
                "title": "東京都青梅市における介護サービス事業所一覧",
                "provider": "青梅市",
                "source_url": "https://www.opendata.metro.tokyo.lg.jp/ome/132055_care_service.xlsx",
                "license": "CC-BY-4.0",
                "retrieved_at": "2026-08-23",
                "notes": f"{len(welfare)}件。",
            },
        ],
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "real_map.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8"
    )
    print(f"boundary points: {len(boundary_m)}")
    print(f"clinics: {len(clinics)}, welfare: {len(welfare)}")
    print(f"wrote {OUT_DIR / 'real_map.json'}")


if __name__ == "__main__":
    main()
