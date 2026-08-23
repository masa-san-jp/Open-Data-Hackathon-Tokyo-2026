#!/usr/bin/env python3
"""青梅市実データ位置マップの構造・出典・生成再現性を検証する。

徒歩時間や到達圏を推定する検査は意図的に含めない。このフェーズでは、
実在施設の位置を出典付きで表示することと、未実装範囲を隠さないことだけを検証する。
"""
import importlib.util
import json
import math
import re
import sys
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = APP_ROOT / "data" / "normalized" / "ome" / "real_map.json"
TEMPLATE_PATH = APP_ROOT / "templates" / "real-map.html"
OUTPUT_PATH = APP_ROOT / "prototype" / "real-map.html"
BUILDER_PATH = APP_ROOT / "scripts" / "build_real_map.py"

FAILURES = []


def fail(check_id: str, message: str) -> None:
    FAILURES.append(f"[{check_id}] {message}")


def ok(check_id: str, message: str) -> None:
    print(f"  OK  {check_id}: {message}")


def finite_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail("REAL-FILES", f"{path} をJSONとして読めない: {exc}")
        return None


def check_data(data) -> None:
    if not isinstance(data, dict):
        fail("REAL-SCHEMA", "real_map.json がオブジェクトではない")
        return
    if data.get("demo") is not False:
        fail("REAL-DEMO-FLAG", "実データ出力の demo は false でなければならない")
    if data.get("area") != "青梅市" or data.get("local_government_code") != "13205":
        fail("REAL-AREA", "対象地域が青梅市（地方公共団体コード13205）ではない")

    projection = data.get("projection")
    required_projection = {"method", "lon0", "lat0", "meters_per_deg_lat", "meters_per_deg_lon"}
    if not isinstance(projection, dict) or not required_projection.issubset(projection):
        fail("REAL-PROJECTION", "投影メタデータが不足している")
    else:
        for key in required_projection - {"method"}:
            if not finite_number(projection[key]):
                fail("REAL-PROJECTION", f"projection.{key} が数値ではない")

    boundary = data.get("boundary_m")
    if not isinstance(boundary, list) or len(boundary) < 3:
        fail("REAL-BOUNDARY", "境界ポリゴンが3点未満")
    else:
        for index, point in enumerate(boundary):
            if not isinstance(point, list) or len(point) != 2 or not all(finite_number(v) for v in point):
                fail("REAL-BOUNDARY", f"境界点{index}の座標が不正")

    facilities = data.get("facilities")
    if not isinstance(facilities, list) or not facilities:
        fail("REAL-FACILITIES", "施設が空")
    else:
        allowed_codes = {"clinic", "welfare"}
        required = {
            "name", "type", "address", "lat", "lon", "x_m", "y_m",
            "function_code", "within_boundary", "coordinate_status",
        }
        counts = {}
        for index, facility in enumerate(facilities):
            if not isinstance(facility, dict) or not required.issubset(facility):
                fail("REAL-FACILITIES", f"施設{index}の必須項目が不足")
                continue
            code = facility["function_code"]
            counts[code] = counts.get(code, 0) + 1
            if code not in allowed_codes:
                fail("REAL-FUNCTION", f"施設{index}の機能コードが不正: {code}")
            for key in ("lat", "lon", "x_m", "y_m"):
                if not finite_number(facility[key]):
                    fail("REAL-FACILITIES", f"施設{index}の{key}が数値ではない")
            if not (20 <= facility["lat"] <= 46 and 120 <= facility["lon"] <= 155):
                fail("REAL-FACILITIES", f"施設{index}の緯度経度が日本の範囲外")
            expected_status = "inside_boundary" if facility["within_boundary"] else "outside_boundary"
            if facility["coordinate_status"] != expected_status:
                fail("REAL-FACILITIES", f"施設{index}の座標品質ステータスが不一致")
        if counts.get("clinic", 0) == 0 or counts.get("welfare", 0) == 0:
            fail("REAL-FUNCTION", f"clinic/welfareの両方が必要: {counts}")
        else:
            ok("REAL-FACILITIES", f"施設座標と機能コードを検証: {counts}")

        quality = data.get("data_quality_summary")
        if not isinstance(quality, dict):
            fail("REAL-QUALITY", "data_quality_summary がない")
        else:
            within_count = sum(1 for facility in facilities if facility.get("within_boundary") is True)
            outside_count = sum(1 for facility in facilities if facility.get("within_boundary") is False)
            if quality.get("facility_total") != len(facilities):
                fail("REAL-QUALITY", "facility_total が施設件数と一致しない")
            if quality.get("within_boundary") != within_count or quality.get("outside_boundary") != outside_count:
                fail("REAL-QUALITY", "境界内外の集計が施設フラグと一致しない")
            else:
                ok("REAL-QUALITY", f"境界外座標を除外せず監査対象として記録: {outside_count}件")

    sources = data.get("sources")
    if not isinstance(sources, list):
        fail("REAL-SOURCES", "sources が配列ではない")
    else:
        source_ids = {source.get("id") for source in sources if isinstance(source, dict)}
        for source_id in ("ome_boundary_n03_2021", "ome_clinic_list_2025", "ome_welfare_care_service_2025"):
            if source_id not in source_ids:
                fail("REAL-SOURCES", f"出典 {source_id} がない")
        for index, source in enumerate(sources):
            for key in ("id", "title", "provider", "source_url", "license", "retrieved_at"):
                if not source.get(key):
                    fail("REAL-SOURCES", f"出典{index}の{key}が空")
        if not FAILURES:
            ok("REAL-SOURCES", "境界・施設の出典、ライセンス、取得日を検証")


def extract_embedded_data(html: str):
    start_marker = '<script id="real-map-data" type="application/json">'
    end_marker = "</script>"
    start = html.find(start_marker)
    if start < 0:
        fail("REAL-HTML-DATA", "埋め込みデータscriptがない")
        return None
    start += len(start_marker)
    end = html.find(end_marker, start)
    if end < 0:
        fail("REAL-HTML-DATA", "埋め込みデータscriptが閉じていない")
        return None
    try:
        return json.loads(html[start:end])
    except json.JSONDecodeError as exc:
        fail("REAL-HTML-DATA", f"埋め込みJSONが不正: {exc}")
        return None


def check_output(data) -> None:
    if not OUTPUT_PATH.exists():
        fail("REAL-OUTPUT", "prototype/real-map.html がない。先に make build-real-map を実行する")
        return
    html = OUTPUT_PATH.read_text(encoding="utf-8")
    if "__REAL_MAP_JSON__" in html:
        fail("REAL-OUTPUT", "生成物にJSONプレースホルダーが残っている")
    embedded = extract_embedded_data(html)
    if embedded is not None and embedded != data:
        fail("REAL-HTML-DATA", "HTMLに埋め込まれたデータがnormalizedデータと一致しない")
    required_disclosures = (
        "REAL DATA（M1途中経過）",
        "歩行時間・徒歩到達圏（アクセシビリティ計算）はまだ実装していません",
        "政策判断には使用しないでください",
        "境界外座標",
        "地図上は非表示・要監査",
    )
    missing = [text for text in required_disclosures if text not in html]
    if missing:
        fail("REAL-DISCLOSURE", f"未実装範囲の明示がない: {missing}")
    else:
        ok("REAL-DISCLOSURE", "実データ表示と未実装範囲の明示あり")
    if re.search(r"(?:src|href)\s*=\s*[\"'](?:https?:)?//", html, re.IGNORECASE):
        fail("REAL-OFFLINE", "HTMLに外部script/link依存がある")
    else:
        ok("REAL-OFFLINE", "外部API・CDN依存なし")


def check_reproducibility(data) -> None:
    spec = importlib.util.spec_from_file_location("build_real_map", BUILDER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    expected = module.render(template, data)
    actual = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
    if expected != actual:
        fail("REAL-REPRO", "現在のHTMLがビルダーの決定論的出力と一致しない")
    else:
        ok("REAL-REPRO", "同じnormalized入力から同じHTMLを再生成できる")


def main() -> None:
    data = load_json(DATA_PATH)
    if data is not None:
        check_data(data)
        check_output(data)
        check_reproducibility(data)
    if FAILURES:
        print("\n検証失敗:")
        for failure in FAILURES:
            print(f" - {failure}")
        sys.exit(1)
    print("\n実データ位置マップの全チェック通過")


if __name__ == "__main__":
    main()
