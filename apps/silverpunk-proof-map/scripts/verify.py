#!/usr/bin/env python3
"""受け入れ検査。エージェントはこれが通るまで「できた」と言わない。

  python3 scripts/verify.py [--fixture path/to/file.json] [--phase 1]

数を数えて落とすだけの検査にはしていない。「値が壊れていないか」「主張が誠実か」を見る。
落ちたら非ゼロで終わる。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DEFAULT_FIXTURE = BASE / "data" / "demo-fixture.json"
PROTOTYPE = BASE / "prototype" / "index.html"

REQUIRED_TOP = ["schema_version", "sources", "scenarios", "districts"]
REQUIRED_METRIC_FIELDS = {"value", "unit", "year", "status"}
VALID_METRIC_STATUS = {
    "verified", "illustrative", "missing", "not_verified",
    "not_comparable", "not_applicable", "stale",
}
VALID_PRIORITY_STATUS = {"illustrative", "verified", "not_computable"}

fails: list[str] = []


def want(condition: bool, message: str) -> None:
    if not condition:
        fails.append(message)


def check_fixture(path: Path, enforce_demo_coverage: bool = True) -> dict | None:
    if not path.exists():
        fails.append(f"{path} が無い")
        return None
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fails.append(f"{path} が JSON として読めない: {e}")
        return None

    for key in REQUIRED_TOP:
        want(key in d, f"必須キー '{key}' が無い")
    if any(key not in d for key in REQUIRED_TOP):
        return d

    source_ids = {s.get("id") for s in d["sources"]}

    # 地区ID重複チェック
    district_ids = [dist.get("id") for dist in d["districts"]]
    want(len(district_ids) == len(set(district_ids)), "地区IDが重複している")
    want(len(d["districts"]) >= 3, f"地区が3件未満（{len(d['districts'])}件）")

    for dist in d["districts"]:
        did = dist.get("id", "?")
        metrics = dist.get("metrics", {})
        want(len(metrics) > 0, f"{did}: metrics が空")

        for mkey, m in metrics.items():
            missing_fields = REQUIRED_METRIC_FIELDS - set(m.keys())
            want(not missing_fields, f"{did}.{mkey}: 必須フィールド不足 {missing_fields}")

            status = m.get("status")
            want(status in VALID_METRIC_STATUS, f"{did}.{mkey}: 不正な status '{status}'")

            # verified を名乗るなら出典と取得日が要る（推測値の verified 混入を防ぐ）
            if status == "verified":
                want(bool(m.get("source_id")), f"{did}.{mkey}: verified なのに source_id が無い")
                want(bool(m.get("as_of") or m.get("year")),
                     f"{did}.{mkey}: verified なのに取得日/対象年が無い")
                sid = m.get("source_id")
                want(sid in source_ids, f"{did}.{mkey}: source_id '{sid}' が sources に無い")

            # missing なのに値が入っている、はデータのごまかし
            if status in ("missing", "not_applicable", "not_verified"):
                want(m.get("value") is None,
                     f"{did}.{mkey}: status が '{status}' なのに value が入っている（0/missingの混同）")

            if status == "illustrative":
                want(m.get("value") is not None,
                     f"{did}.{mkey}: illustrative なのに value が無い")

        # facilities の状態値検査（0件と未確認の混同防止）
        for f in dist.get("facilities", []):
            fstatus = f.get("status")
            want(fstatus in VALID_METRIC_STATUS,
                 f"{did}.facilities[{f.get('category')}]: 不正な status '{fstatus}'")
            if fstatus == "missing":
                want(f.get("count") is None,
                     f"{did}.facilities[{f.get('category')}]: missing なのに count が入っている")

        # priority: not_computable のスコアが順位計算に使われていないことを検査
        priority = dist.get("priority", {})
        pstatus = priority.get("status")
        want(pstatus in VALID_PRIORITY_STATUS, f"{did}.priority: 不正な status '{pstatus}'")
        if pstatus == "not_computable":
            want(priority.get("value") is None,
                 f"{did}.priority: not_computable なのに value が入っている（順位計算に使われる恐れ）")
        if pstatus in ("illustrative", "verified"):
            want(priority.get("value") is not None,
                 f"{did}.priority: {pstatus} なのに value が無い")

    if enforce_demo_coverage:
        # Phase 1 デモ fixture 専用の網羅性検査（T01 受け入れ条件）。
        # 実データ（proof_map.json 等）は「未取得は missing だけ」のような偏った構成が正しい場合が
        # あるため、既定の demo-fixture.json を検査するときだけ強制する。
        all_statuses = set()
        for dist in d["districts"]:
            for m in dist.get("metrics", {}).values():
                all_statuses.add(m.get("status"))
            for f in dist.get("facilities", []):
                all_statuses.add(f.get("status"))
            all_statuses.add(dist.get("priority", {}).get("status"))
        for required_status in ("missing", "not_verified"):
            want(required_status in all_statuses,
                 f"fixture 全体に '{required_status}' が1件も無い")
        want("not_computable" in {dist.get("priority", {}).get("status") for dist in d["districts"]},
             "fixture 全体に priority.status: not_computable が1件も無い")

        computable = [dist for dist in d["districts"] if dist["priority"]["status"] != "not_computable"]
        want(len(computable) >= 1, "priority が算出できる地区が1件も無い（並べ替えの動作確認ができない）")

    return d


def check_prototype() -> None:
    if not PROTOTYPE.exists():
        fails.append("prototype/index.html が無い（Phase 1 の成果物）")
        return
    html = PROTOTYPE.read_text(encoding="utf-8")
    want(len(html) > 2000, "prototype/index.html が小さすぎる")
    external = [
        line for line in html.splitlines()
        if ("http://" in line or "https://" in line)
        and "cdn" in line.lower()
    ]
    want(not external, f"外部CDNへの参照がある: {external}")
    want("未確認" in html, "「未確認」の表示文言が画面に無い")
    want("例示" in html, "「例示」の表示文言が画面に無い（illustrative の明示）")
    want("経路の安全" in html or "公式情報" in html, "免責・注意書きが画面に無い")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    ap.add_argument("--phase", type=int, default=1)
    args = ap.parse_args()

    check_fixture(args.fixture, enforce_demo_coverage=(args.fixture == DEFAULT_FIXTURE))
    if args.phase >= 1:
        check_prototype()

    if fails:
        print(f"✗ {len(fails)} 件")
        for f in fails:
            print("   -", f)
        return 1
    print("✓ すべて通った")
    return 0


if __name__ == "__main__":
    sys.exit(main())
