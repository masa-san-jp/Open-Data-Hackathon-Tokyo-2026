#!/usr/bin/env python3
"""貼付候補地の台帳を作る。

  python3 scripts/build_points.py

元データ: 東京都総務局「都内災害時帰宅支援ステーション協力店舗一覧（令和7年3月31日）」
https://www.opendata.metro.tokyo.lg.jp/soumu/kitaku.shien.station_r7.3.31.csv
（拡張子は .csv だが**中身は xlsx**。2026-08-23 実測。csv として開くと壊れる）

この店舗は既に「災害時に軒先を開ける」と表明している。同じ趣旨のステッカーを
貼ってもらう交渉の出発点として、実在・住所・緯度経度が揃った唯一の名簿。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import openpyxl

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "data" / "raw_stations.xlsx"
OUT = BASE / "data" / "points.json"

MUNI = re.compile(r"^(.+?[区市町村])")
# 場所コードの接頭辞。読み上げやすさを優先して自治体名の頭2文字＋連番にする
def code_for(muni: str, seq: int) -> str:
    return f"{muni[:2]}{seq:04d}"


def main() -> int:
    if not SRC.exists():
        print(f"✗ {SRC} が無い", file=sys.stderr)
        return 1
    ws = openpyxl.load_workbook(SRC, read_only=True, data_only=True)[
        openpyxl.load_workbook(SRC, read_only=True).sheetnames[0]]
    rows = [r for r in ws.iter_rows(values_only=True)]
    seq: dict[str, int] = {}
    points, skipped = [], 0
    for r in rows[2:]:
        if not r or not r[1] or not r[2] or not r[3] or not r[4]:
            skipped += 1
            continue
        address = str(r[2]).strip()
        m = MUNI.search(address)
        if not m:
            skipped += 1
            continue
        muni = m.group(1)
        seq[muni] = seq.get(muni, 0) + 1
        points.append({
            "c": code_for(muni, seq[muni]),      # 場所コード（口頭で読み上げる）
            "n": str(r[1]).strip(),              # 店舗名
            "a": address,                        # 住所（119/110で読み上げる本体）
            "m": muni,
            "lat": round(float(r[3]), 6),
            "lon": round(float(r[4]), 6),
        })
    OUT.write_text(json.dumps({
        "source": "東京都総務局 都内災害時帰宅支援ステーション協力店舗一覧（令和7年3月31日）",
        "note": "貼付候補地。実際に貼られた点ではない。",
        "points": points,
    }, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"✓ {len(points):,} 点 / {len(seq)} 自治体（除外 {skipped}）→ {OUT.relative_to(BASE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
