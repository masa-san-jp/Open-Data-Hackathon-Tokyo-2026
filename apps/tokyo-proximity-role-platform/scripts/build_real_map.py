#!/usr/bin/env python3
"""正規化済みの青梅市実データから施設位置マップを生成する。

この出力はM1の施設位置ベースラインであり、道路経路・徒歩時間・人口按分を
計算しない。正規化処理は ``normalize_ome_sources.py``、HTML生成はこのスクリプト
に分離して、rawデータを直接編集せず再生成できるようにする。
"""
import argparse
import json
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_PATH = APP_ROOT / "data" / "normalized" / "ome" / "real_map.json"
DEFAULT_TEMPLATE_PATH = APP_ROOT / "templates" / "real-map.html"
DEFAULT_OUTPUT_PATH = APP_ROOT / "prototype" / "real-map.html"
PLACEHOLDER = "__REAL_MAP_JSON__"


def load_data(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("demo") is not False:
        raise ValueError("実データマップの入力は demo=false でなければならない")
    if data.get("area") != "青梅市":
        raise ValueError("実データベースラインの対象地域は青梅市に固定する")
    if not data.get("boundary_m") or not data.get("facilities"):
        raise ValueError("境界と施設データが空のためHTMLを生成できない")
    return data


def json_for_script(data: dict) -> str:
    """JSONをscript要素へ安全に埋め込む。

    施設名や住所に ``</script>`` 相当の文字列が含まれても、script要素が
    途中で閉じないようにHTML特殊文字だけをUnicodeエスケープする。
    """
    serialized = json.dumps(data, ensure_ascii=False, indent=2)
    return (
        serialized
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )


def render(template: str, data: dict) -> str:
    if PLACEHOLDER not in template:
        raise ValueError(f"テンプレートに {PLACEHOLDER} がない")
    rendered = template.replace(PLACEHOLDER, json_for_script(data))
    if PLACEHOLDER in rendered:
        raise ValueError("実データJSONの埋め込みに失敗した")
    return rendered.rstrip() + "\n"


def build(data_path: Path, template_path: Path, output_path: Path) -> dict:
    data = load_data(data_path)
    template = template_path.read_text(encoding="utf-8")
    output = render(template, data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding="utf-8")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()

    data = build(args.data, args.template, args.output)
    counts = {}
    for facility in data["facilities"]:
        code = facility["function_code"]
        counts[code] = counts.get(code, 0) + 1
    print(f"built {args.output}")
    print(f"area: {data['area']}; boundary points: {len(data['boundary_m'])}; facilities: {counts}")


if __name__ == "__main__":
    main()
