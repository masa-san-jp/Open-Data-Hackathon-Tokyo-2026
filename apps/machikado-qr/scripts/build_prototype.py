#!/usr/bin/env python3
"""ソースとデータを、外部依存のない単体HTMLへまとめる。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "points.json"
CONFIG = BASE / "config.json"
TEMPLATE = BASE / "src" / "index.template.html"
STYLES = BASE / "src" / "styles.css"
APP_JS = BASE / "src" / "app.js"
OUT = BASE / "prototype" / "index.html"
DEMO = BASE / "prototype" / "demo.html"


def script_safe_json(value: object) -> str:
    """JSONをinline scriptから脱出できない形にする。"""
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def replace_once(body: str, marker: str, replacement: str) -> str:
    count = body.count(marker)
    if count != 1:
        raise ValueError(f"テンプレートマーカー {marker} が {count} 個ある（1個必要）")
    return body.replace(marker, replacement, 1)


def main() -> int:
    required = (DATA, CONFIG, TEMPLATE, STYLES, APP_JS)
    missing = [str(path.relative_to(BASE)) for path in required if not path.exists()]
    if missing:
        print(f"✗ 必要ファイルが無い: {', '.join(missing)}", file=sys.stderr)
        return 1

    payload = json.loads(DATA.read_text(encoding="utf-8"))
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    html = TEMPLATE.read_text(encoding="utf-8")
    html = replace_once(html, "__STYLES__", STYLES.read_text(encoding="utf-8").strip())
    html = replace_once(html, "__DATA__", script_safe_json(payload))
    html = replace_once(html, "__CONFIG__", script_safe_json(config))
    html = replace_once(html, "__APP_JS__", APP_JS.read_text(encoding="utf-8").strip())

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    DEMO.write_text(
        """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="0;url=./index.html?demo=1">
<title>まちかどQR デモ</title>
</head>
<body><p><a href="./index.html?demo=1">デモを開く</a></p></body>
</html>
""",
        encoding="utf-8",
    )
    print(
        f"✓ {OUT.relative_to(BASE)} ({len(html.encode('utf-8')):,} bytes / "
        f"候補地点 {len(payload['points']):,}・周辺地点 {len(payload['dest']):,})"
    )
    print(f"✓ {DEMO.relative_to(BASE)} → index.html?demo=1")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"✗ プロトタイプ生成失敗: {error}", file=sys.stderr)
        sys.exit(2)
