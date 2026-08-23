#!/usr/bin/env python3
"""M10 データレジストリ監査ツール。

東京都オープンデータカタログ（CKAN API）を機能コード×対象自治体で検索し、
`data/reports/source-audit.json` へ結果を記録する。

このスクリプトはネットワークアクセスが必要（実際のカタログを検索する）。
「検索でヒットした」ことは「利用可能」を意味しない。同じ結果が出ても、
実際にファイルを開いてスキーマ・カバー率・欠損を確認するまで
`production_ready: true` にしてはならない（AGENTS.md §5.1）。

使い方:
  python3 scripts/audit_sources.py --phase m1 --municipality 青梅市
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = APP_ROOT / "data" / "reports" / "source-audit.json"

CATALOG_API = "https://catalog.data.metro.tokyo.lg.jp/api/3/action/package_search"
USER_AGENT = "Mozilla/5.0 (compatible; tokyo-proximity-role-platform-audit/0.1)"

# SPEC.md §3.2 の近隣生活機能コードに対する検索クエリ候補。
# 「機能名の一般語」と「対象自治体名を含めた語」の両方を試す。
FUNCTION_QUERIES = {
    "food": ["食料品店", "スーパーマーケット"],
    "pharmacy": ["薬局", "薬局等台帳"],
    "clinic": ["医療機関", "診療所"],
    "welfare": ["介護サービス事業所", "福祉施設"],
    "toilet_rest": ["公衆トイレ", "公園"],
    "mobility_node": ["バス停", "GTFS", "コミュニティバス"],
    "population": ["人口統計", "町丁目 人口", "世帯数の予測"],
}


def query_catalog(query, rows=5):
    url = f"{CATALOG_API}?{urllib.parse.urlencode({'q': query, 'rows': rows})}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.load(resp)
    result = data["result"]
    return {
        "query": query,
        "count": result["count"],
        "results": [
            {
                "title": p["title"],
                "organization": (p.get("organization") or {}).get("title"),
                "license_id": p.get("license_id"),
                "metadata_modified": p.get("metadata_modified"),
                "resources": [{"format": r.get("format"), "url": r.get("url")} for r in p.get("resources", [])[:3]],
            }
            for p in result["results"]
        ],
    }


def audit(municipality):
    report = {"municipality": municipality, "functions": {}}
    for fn, queries in FUNCTION_QUERIES.items():
        fn_results = []
        for q in queries:
            full_query = f"{municipality} {q}" if municipality else q
            try:
                fn_results.append(query_catalog(full_query))
            except Exception as e:  # ネットワーク障害等。監査は継続する
                fn_results.append({"query": full_query, "error": str(e)})
        report["functions"][fn] = fn_results
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", default="m1", choices=["m1"])
    parser.add_argument("--municipality", default="", help="例: 青梅市")
    parser.add_argument("--output", default=str(REPORT_PATH))
    args = parser.parse_args()

    if not args.municipality:
        print("エラー: --municipality を指定してください（例: --municipality 青梅市）", file=sys.stderr)
        print("MVPの対象地域はエージェントが自律確定しない（Agent.md §5）。オーナーが指定した候補を渡すこと。", file=sys.stderr)
        sys.exit(2)

    report = audit(args.municipality)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out_path}")
    print("注意: 検索でヒットしたことは利用可能を意味しない。実ファイルを開いて確認するまで production_ready: false のままとする。")


if __name__ == "__main__":
    main()
