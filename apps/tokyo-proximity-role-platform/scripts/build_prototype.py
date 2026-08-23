#!/usr/bin/env python3
"""templates/demo.html + data/demo/*.json -> prototype/index.html

prototype/index.html は生成物であり、直接編集しない（AGENTS.md §6）。
"""
import json
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = APP_ROOT / "templates" / "demo.html"
DEMO_DIR = APP_ROOT / "data" / "demo"
OUTPUT_PATH = APP_ROOT / "prototype" / "index.html"


def load_json(name):
    return json.loads((DEMO_DIR / name).read_text(encoding="utf-8"))


def main():
    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    cells = load_json("cells.json")
    infrastructure = load_json("infrastructure.json")
    roles = load_json("roles.json")

    html = template
    html = html.replace("__CELLS_JSON__", json.dumps(cells, ensure_ascii=False))
    html = html.replace("__INFRASTRUCTURE_JSON__", json.dumps(infrastructure, ensure_ascii=False))
    html = html.replace("__ROLES_JSON__", json.dumps(roles, ensure_ascii=False))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"built {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
