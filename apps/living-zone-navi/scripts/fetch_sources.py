#!/usr/bin/env python3
"""カタログから解決したD1〜D5のURLを取得し、data/raw/ に検査付きで保存する。

  python3 scripts/fetch_sources.py            # 解決＋取得＋検査＋sources.json更新
  python3 scripts/fetch_sources.py --check    # 既存 data/raw/ の検査のみ（取得しない・sources.jsonも書き換えない）

検査に落ちたら非ゼロで終わる。**中身を見ずに次へ進ませないためのゲート**。
取得した内容は一時ファイルに書き、検査を通ってから data/raw/ に置き換える
（検査落ちで直前の正常ファイルを壊さないため）。

D2（クーリングシェルター）だけは、解決できなくてもエラーにせず
sources.json に {"status": "not_published"} と記録して先へ進む
（design-spec §3: 涼み処ODが未公開の区がある想定への対応）。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalog import resolve_all  # noqa: E402

APP_DIR = Path(__file__).resolve().parent.parent
RAW = APP_DIR / "data" / "raw"
SOURCES_JSON = APP_DIR / "data" / "sources.json"
CONFIG_JSON = APP_DIR / "config.json"

# 既定のUAで弾かれた場合だけブラウザ相当を名乗る（認証ではない）
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)

HTML_MARKERS = (b"<!doctype html", b"<html")
TEXT_ENCODINGS = ("utf-8-sig", "cp932", "utf-8")

# D3は区単位の一般医療機関一覧が無く、都全域の災害拠点病院リストに
# スコープを狭めて取得している（詳細は OPEN-ISSUES.md）。sources.json
# にも理由を残し、build_dataset.py 側で見落とされないようにする。
DATASET_NOTES = {
    "D3": "区単位の一般医療機関一覧が存在せず、都全域『災害拠点病院等』に"
          "スコープを狭めて取得（座標なし・住所のみ）。詳細は OPEN-ISSUES.md",
}


def fetch(url: str) -> bytes:
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return r.read()
    except (urllib.error.HTTPError, urllib.error.URLError):
        req = urllib.request.Request(url, headers={"User-Agent": BROWSER_UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read()


def check(raw: bytes) -> str | None:
    """問題があれば理由の文字列、無ければ None。"""
    if len(raw) < 1000:
        return f"小さすぎる（{len(raw)} バイト）。エラーページの可能性"
    head = raw[:2000].lower()
    if any(m in head for m in HTML_MARKERS):
        return "中身がHTMLページ（生データではない）"
    for enc in TEXT_ENCODINGS:
        try:
            raw[:4096].decode(enc)
            return None
        except UnicodeDecodeError:
            continue
    return "utf-8-sig/cp932/utf-8のいずれでも読めない（テキストCSVではない可能性）"


def slug(dataset_id: str, resource_url: str) -> str:
    name = resource_url.rsplit("/", 1)[-1]
    if "." not in name:
        name += ".csv"
    return f"{dataset_id}_{name}"


def atomic_write(path: Path, raw: bytes) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(raw)
    os.replace(tmp, path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                     help="取得せず data/raw/ の検査のみ（sources.jsonは書き換えない）")
    args = ap.parse_args()

    ward = json.loads(CONFIG_JSON.read_text(encoding="utf-8"))["ward"]
    resolved = resolve_all(ward)

    RAW.mkdir(parents=True, exist_ok=True)
    records: dict[str, dict] = {}
    failed = 0

    for dataset_id, info in resolved.items():
        if info is None:
            if dataset_id == "D2":
                print(f"○ {dataset_id}: 未公開（カタログに該当データが無い）")
                records[dataset_id] = {"id": dataset_id, "status": "not_published"}
                continue
            print(f"✗ {dataset_id}: カタログで解決できない")
            records[dataset_id] = {"id": dataset_id, "status": "unresolved"}
            failed += 1
            continue

        path = RAW / slug(dataset_id, info["resource_url"])
        note = DATASET_NOTES.get(dataset_id)

        if args.check:
            if not path.exists():
                print(f"✗ {dataset_id}: 検査対象ファイルが無い（先に取得が要る）")
                failed += 1
                continue
            reason = check(path.read_bytes())
            if reason:
                print(f"✗ {dataset_id} ({info['title']}): {reason}")
                failed += 1
                continue
            print(f"✓ {dataset_id} ({info['title']}, {info['scope']}) "
                  f"{path.stat().st_size:,} バイト [--checkのみ・sources.json未更新]")
            continue

        try:
            raw = fetch(info["resource_url"])
        except Exception as exc:
            print(f"✗ {dataset_id}: 取得できない: {exc}")
            records[dataset_id] = {"id": dataset_id, "status": "fetch_failed",
                                    "error": str(exc), **info}
            failed += 1
            continue

        reason = check(raw)
        if reason:
            print(f"✗ {dataset_id} ({info['title']}): {reason}")
            records[dataset_id] = {"id": dataset_id, "status": "check_failed",
                                    "reason": reason, **info}
            failed += 1
            continue

        atomic_write(path, raw)
        print(f"✓ {dataset_id} ({info['title']}, {info['scope']}) "
              f"{path.stat().st_size:,} バイト")
        record = {
            "id": dataset_id,
            "status": "ok",
            "scope": info["scope"],
            "title": info["title"],
            "org": info["org"],
            "dataset_url": info["dataset_url"],
            "url": info["resource_url"],
            "file": str(path.relative_to(APP_DIR)),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
        if note:
            record["note"] = note
        records[dataset_id] = record

    if not args.check:
        SOURCES_JSON.write_text(
            json.dumps({"ward": ward, "sources": records}, ensure_ascii=False, indent=1),
            encoding="utf-8",
        )

    if failed:
        print(f"\n{failed} 件が検査に落ちた。data/raw/ か catalog.py の解決条件を直すまで先へ進まない。")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
