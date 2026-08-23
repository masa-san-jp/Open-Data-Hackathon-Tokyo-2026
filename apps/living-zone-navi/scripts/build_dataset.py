#!/usr/bin/env python3
"""raw CSVを施設・人口データに正規化し、data/processed/dataset.json を作る。

  python3 scripts/build_dataset.py

前提: scripts/fetch_sources.py が先に実行済みで、data/raw/ と data/sources.json が揃っていること。

D5の町丁人口にD6の町丁代表点を結合し、施設種別ごとの最短直線距離と
reach（near/far/out/unknown）を決定論的に計算する。経路距離は扱わない。
"""
from __future__ import annotations

import csv
import io
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
RAW = APP_DIR / "data" / "raw"
PROCESSED = APP_DIR / "data" / "processed"
SOURCES_JSON = APP_DIR / "data" / "sources.json"
CONFIG_JSON = APP_DIR / "config.json"

TEXT_ENCODINGS = ("utf-8-sig", "cp932", "utf-8")
KINDS = ("shelter", "cool", "medical", "care")
EARTH_RADIUS_M = 6_371_000.0

# D5は算用数字（例: 清澄１丁目）、D6は漢数字（例: 清澄一丁目）を
# 使うため、丁目の直前だけを数値化する。地名中の「一」「十」などを
# 無差別に置換すると固有名を壊すので、置換範囲を丁目番号に限定する。
KANJI_DIGITS = {
    "〇": 0, "零": 0, "一": 1, "二": 2, "三": 3, "四": 4,
    "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
}
KANJI_UNITS = {"十": 10, "百": 100, "千": 1000}


def kanji_number_to_int(token: str) -> int:
    """一〜千程度の日本語数詞を整数にする（町丁目番号用）。"""
    total = 0
    current = 0
    for char in token:
        if char in KANJI_DIGITS:
            current = KANJI_DIGITS[char]
        elif char in KANJI_UNITS:
            unit = KANJI_UNITS[char]
            total += (current or 1) * unit
            current = 0
    return total + current


def normalize_area_name(name: str) -> str:
    """D5/D6の町丁名を結合用に正規化する。"""
    normalized = unicodedata.normalize("NFKC", name)
    normalized = "".join(normalized.split())
    normalized = normalized.replace("ヶ", "ケ")

    def replace_chome(match: re.Match[str]) -> str:
        return f"{kanji_number_to_int(match.group(1))}丁目"

    return re.sub(r"([〇零一二三四五六七八九十百千]+)丁目", replace_chome, normalized)


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in TEXT_ENCODINGS:
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"{path}: utf-8-sig/cp932/utf-8のいずれでも読めない")


def read_rows(path: Path) -> list[list[str]]:
    return list(csv.reader(io.StringIO(read_text(path))))


def to_float(s: str) -> float | None:
    s = s.strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def build_centroids(path: Path, ward: str) -> tuple[dict[str, dict], int]:
    """D6の都全域CSVから対象区の町丁代表点を読む。"""
    rows = read_rows(path)
    if not rows:
        return {}, 0
    header, body = rows[0], rows[1:]
    idx = {name: i for i, name in enumerate(header)}
    required = ("市区町村名", "大字町丁目名", "緯度", "経度")
    missing = [name for name in required if name not in idx]
    if missing:
        raise ValueError(f"{path}: D6の必須列が無い: {'、'.join(missing)}")

    points: dict[str, dict] = {}
    duplicate_count = 0
    max_idx = max(idx.values())
    for row_index, row in enumerate(body):
        if len(row) <= max_idx or row[idx["市区町村名"]] != ward:
            continue
        name = row[idx["大字町丁目名"]].strip()
        key = normalize_area_name(name)
        lat = to_float(row[idx["緯度"]])
        lon = to_float(row[idx["経度"]])
        if not key or lat is None or lon is None:
            continue
        if key in points:
            duplicate_count += 1
            continue
        points[key] = {"lat": lat, "lon": lon, "source_row": row_index}

    if duplicate_count:
        print(f"⚠ D6: 正規化後に重複する町丁代表点を{duplicate_count}件除外", file=sys.stderr)
    return points, duplicate_count


def attach_centroids(areas: list[dict], points: dict[str, dict]) -> dict[str, int | float | list[str]]:
    """D5の町丁人口にD6の代表点を名前で結合し、結合率を返す。"""
    matched = 0
    unmatched: list[str] = []
    for area in areas:
        point = points.get(normalize_area_name(area["name"]))
        if point is None:
            area["lat"] = None
            area["lon"] = None
            unmatched.append(area["name"])
            continue
        area["lat"] = point["lat"]
        area["lon"] = point["lon"]
        matched += 1
    total = len(areas)
    rate = matched / total if total else 1.0
    return {"matched": matched, "total": total, "rate": rate, "unmatched": unmatched}


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """2点間の直線距離（メートル）。"""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (math.sin(d_phi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2)
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(min(1.0, a)))


def classify_reach(distance_m: float | None, near_m: float, far_m: float) -> str:
    if distance_m is None:
        return "unknown"
    if distance_m <= near_m:
        return "near"
    if distance_m <= far_m:
        return "far"
    return "out"


def add_nearest_and_reach(areas: list[dict], facilities: list[dict],
                          near_m: float, far_m: float) -> None:
    """町丁代表点から種別ごとの最近施設とreachを計算する。"""
    located_by_kind: dict[str, list[tuple[float, float]]] = {kind: [] for kind in KINDS}
    for facility in facilities:
        lat, lon = facility["lat"], facility["lon"]
        if lat is None or lon is None:
            continue
        located_by_kind.setdefault(facility["kind"], []).append((lat, lon))

    for area in areas:
        lat, lon = area.get("lat"), area.get("lon")
        area["nearest_m"] = {}
        area["reach"] = {}
        for kind in KINDS:
            if lat is None or lon is None or not located_by_kind[kind]:
                nearest = None
            else:
                nearest = min(
                    haversine_m(lat, lon, facility_lat, facility_lon)
                    for facility_lat, facility_lon in located_by_kind[kind]
                )
            area["nearest_m"][kind] = round(nearest, 1) if nearest is not None else None
            area["reach"][kind] = classify_reach(nearest, near_m, far_m)


def load_sources(ward: str) -> dict:
    if not SOURCES_JSON.exists():
        print("✗ data/sources.json が無い。先に scripts/fetch_sources.py を実行して", file=sys.stderr)
        sys.exit(1)
    data = json.loads(SOURCES_JSON.read_text(encoding="utf-8"))
    if data.get("ward") != ward:
        print(f"✗ sources.json の ward（{data.get('ward')}）と config.json の ward（{ward}）"
              "が食い違う。fetch_sources.py を再実行して", file=sys.stderr)
        sys.exit(1)
    return data["sources"]


def make_facility(dataset_id: str, seq: int, kind: str, name: str,
                   lat: float | None, lon: float | None, row_index: int) -> dict:
    return {
        "id": f"{dataset_id}-{seq:04d}",
        "kind": kind,
        "name": name,
        "lat": lat,
        "lon": lon,
        "source": {"file": dataset_id, "row": row_index},
    }


def build_shelters(path: Path, ward: str) -> list[dict]:
    """D1 避難所・避難場所（都全域データを ward で絞り込む）。"""
    rows = read_rows(path)
    header, body = rows[1], rows[2:]  # 1行目は空白セル、2行目が実ヘッダ
    idx = {name: i for i, name in enumerate(header)}
    out = []
    for i, row in enumerate(body):
        if len(row) <= idx["指定市区町村名"] or row[idx["指定市区町村名"]] != ward:
            continue
        out.append(make_facility(
            "D1", len(out) + 1, "shelter",
            row[idx["避難所_施設名称"]],
            to_float(row[idx["緯度"]]), to_float(row[idx["経度"]]),
            i,
        ))
    return out


def build_cooling(path: Path) -> list[dict]:
    """D2 クーリングシェルター（区が直接公開・既に ward スコープ）。"""
    rows = read_rows(path)
    header, body = rows[0], rows[1:]
    idx = {name: i for i, name in enumerate(header)}
    out = []
    for i, row in enumerate(body):
        if not row or not row[idx["施設名称"]].strip():
            continue
        out.append(make_facility(
            "D2", len(out) + 1, "cool",
            row[idx["施設名称"]],
            to_float(row[idx["緯度"]]), to_float(row[idx["経度"]]),
            i,
        ))
    return out


def build_medical(path: Path, ward: str) -> list[dict]:
    """D3 医療機関（都全域『災害拠点病院等』に狭めて取得。座標列なし＝住所のみ）。"""
    rows = read_rows(path)
    header, body = rows[2], rows[3:]  # 1-2行目はタイトルと基準日
    idx = {name: i for i, name in enumerate(header)}
    out = []
    for i, row in enumerate(body):
        if len(row) <= idx["施設名"] or not row[idx["施設名"]].strip():
            continue
        if ward not in row[idx["所在地"]]:
            continue
        out.append(make_facility(
            "D3", len(out) + 1, "medical",
            row[idx["施設名"]],
            None, None,  # 座標が無い＝位置不明として計上（design-spec §3）
            i,
        ))
    return out


def build_care(path: Path, ward: str) -> list[dict]:
    """D4 介護サービス事業所（区が直接公開・既に ward スコープ）。"""
    rows = read_rows(path)
    header, body = rows[0], rows[1:]
    idx = {name: i for i, name in enumerate(header)}
    out = []
    for i, row in enumerate(body):
        if len(row) <= idx["所在地_市区町村"] or row[idx["所在地_市区町村"]] != ward:
            continue
        out.append(make_facility(
            "D4", len(out) + 1, "care",
            row[idx["介護サービス事業所名称"]],
            to_float(row[idx["緯度"]]), to_float(row[idx["経度"]]),
            i,
        ))
    return out


def build_population(path: Path) -> list[dict]:
    """D5 町丁別・年齢別・男女別人口 → 町丁ごとの総人口/65+/75+。

    「本番」は町丁内の街区（番地）レベルの内訳であり、町丁そのものではない
    （実測: 大字コードは町丁と1対1、本番は同一町丁内で1〜数十に分かれる）。
    町丁として集計するため大字コードで合算する。
    「総人口」行のみ合算する（「外国人人口」は総人口の内数として別掲されており、
    足すと二重計上になる）。
    """
    rows = read_rows(path)
    header, body = rows[0], rows[1:]
    idx = {name: i for i, name in enumerate(header)}
    age_cols = [(i, int(h[:-1])) for i, h in enumerate(header) if h.endswith("歳")]

    areas: dict[str, dict] = {}
    for row in body:
        if row[idx["人口"]] != "総人口":
            continue
        code = row[idx["大字コード"]]
        area = areas.setdefault(code, {
            "code": code, "name": row[idx["大字名称"]],
            "pop_total": 0, "pop_65plus": 0, "pop_75plus": 0,
        })
        for i, age in age_cols:
            v = int(row[i] or 0)
            area["pop_total"] += v
            if age >= 65:
                area["pop_65plus"] += v
            if age >= 75:
                area["pop_75plus"] += v
    return sorted(areas.values(), key=lambda a: a["code"])


def make_gaps(sources: dict, centroid_join: dict[str, int | float | list[str]]) -> list[dict]:
    # バリアフリー線データ（段差・屋根・ベンチ間隔）は都ODに存在しない恒常的な欠損。
    # これは本作品の不具合ではなく公開データの現状そのもの（design-spec §3, §5）。
    gaps = [
        {"kind": "barrier_free", "reason": "not_collected",
         "note": "段差・屋根・ベンチ間隔などの歩行環境データは都オープンデータに存在しない"},
    ]
    d2 = sources.get("D2", {})
    if d2.get("status") == "not_published":
        gaps.append({"kind": "cool", "reason": "not_published",
                     "note": "クーリングシェルターの区別オープンデータが未公開"})
    d3 = sources.get("D3", {})
    if d3.get("note"):
        gaps.append({"kind": "medical", "reason": "source_missing", "note": d3["note"]})
    unmatched = centroid_join.get("unmatched", [])
    if unmatched:
        gaps.append({
            "kind": "area_centroid", "reason": "source_missing",
            "note": "D5に存在する町丁の代表点がD6に無い: " + "、".join(unmatched),
        })
    return gaps


def count_by_kind(facilities: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for f in facilities:
        counts[f["kind"]] = counts.get(f["kind"], 0) + 1
    return counts


BUILDERS = {
    "D1": lambda path, ward: build_shelters(path, ward),
    "D2": lambda path, ward: build_cooling(path),
    "D3": lambda path, ward: build_medical(path, ward),
    "D4": lambda path, ward: build_care(path, ward),
}


def main() -> int:
    config = json.loads(CONFIG_JSON.read_text(encoding="utf-8"))
    ward = config["ward"]
    sources = load_sources(ward)

    facilities: list[dict] = []
    for dataset_id, builder in BUILDERS.items():
        src = sources.get(dataset_id, {})
        if src.get("status") != "ok":
            continue
        facilities += builder(APP_DIR / src["file"], ward)

    d5 = sources.get("D5", {})
    if d5.get("status") != "ok":
        print("✗ D5（人口）が取得できていない。scripts/fetch_sources.py を先に実行して",
              file=sys.stderr)
        return 1
    areas = build_population(APP_DIR / d5["file"])

    d6 = sources.get("D6", {})
    if d6.get("status") == "ok":
        centroid_path = APP_DIR / d6["file"]
        points, _duplicate_count = build_centroids(centroid_path, ward)
    else:
        print("⚠ D6（町丁代表点）が取得できていない。areasの座標と距離はunknownになる",
              file=sys.stderr)
        points = {}
    centroid_join = attach_centroids(areas, points)
    if centroid_join["rate"] < 0.7:
        print(f"⚠ D6の町丁結合率が70%未満（{centroid_join['matched']}/"
              f"{centroid_join['total']} = {centroid_join['rate']:.1%}）",
              file=sys.stderr)

    gaps = make_gaps(sources, centroid_join)
    missing_by_kind: dict[str, int] = {}
    for f in facilities:
        if f["lat"] is None or f["lon"] is None:
            missing_by_kind[f["kind"]] = missing_by_kind.get(f["kind"], 0) + 1

    add_nearest_and_reach(
        areas, facilities,
        float(config["walk_near_m"]), float(config["walk_far_m"]),
    )

    dataset = {
        "meta": {
            "ward": ward,
            "walk_near_m": config["walk_near_m"],
            "walk_far_m": config["walk_far_m"],
            "note": "直線距離であり経路距離ではない。施設座標は出典CSVのまま（ジオコーディング補完なし）。",
            "sources": [
                {"id": s["id"], "url": s.get("url"), "fetched_at": s.get("fetched_at"),
                 "sha256": s.get("sha256"), "status": s["status"]}
                for s in sources.values()
            ],
            "facility_counts": count_by_kind(facilities),
            "missing_location_counts": missing_by_kind,
            "centroid_join": centroid_join,
        },
        "facilities": facilities,
        "areas": areas,
        "gaps": gaps,
    }

    PROCESSED.mkdir(parents=True, exist_ok=True)
    (PROCESSED / "dataset.json").write_text(
        json.dumps(dataset, ensure_ascii=False, indent=1), encoding="utf-8")

    pop_65 = sum(a["pop_65plus"] for a in areas)
    pop_75 = sum(a["pop_75plus"] for a in areas)
    print(f"✓ facilities: {len(facilities)}件 {count_by_kind(facilities)} "
          f"位置不明: {missing_by_kind}")
    print(f"✓ areas: {len(areas)}町丁 / 65歳以上 {pop_65:,}人 / 75歳以上 {pop_75:,}人")
    print(f"✓ D6 centroid join: {centroid_join['matched']}/{centroid_join['total']} "
          f"({centroid_join['rate']:.1%})")
    print(f"✓ gaps: {len(gaps)}件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
