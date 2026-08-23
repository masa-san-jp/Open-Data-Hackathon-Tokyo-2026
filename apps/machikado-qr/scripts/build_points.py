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

import csv
import io
import json
import math
import re
import sys
from pathlib import Path

import openpyxl

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "data" / "raw_stations.xlsx"
WATER = BASE / "data" / "raw_water.csv"          # 東京都水道局 Tokyowater Drinking Station 一覧
TRANSPORT = BASE / "data" / "raw_transport.csv"  # 東京都デジタルサービス局 だれでも東京（交通）
OUT = BASE / "data" / "points.json"

MUNI = re.compile(r"^(.+?[区市町村])")
# 東京都本土のおおよその範囲。ここを外れた座標は使わない。
# 2026-08-23 実測: 元ファイルは 1,243 行目以降の座標が壊れており（島根や中国の座標、
# 住所の番地も 2-25-131 のような生成値）、11,003 行のうち実データは 1,242 行だけだった。
# 件数だけ数えて中身を見ないと、9,759 件の偽の点を配ることになる。
TOKYO_BOX = (35.4, 35.95, 138.9, 139.95)


def in_tokyo(lat, lon) -> bool:
    la0, la1, lo0, lo1 = TOKYO_BOX
    return la0 <= lat <= la1 and lo0 <= lon <= lo1
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
    points, skipped, out_of_box = [], 0, 0
    for r in rows[2:]:
        if not r or not r[1] or not r[2] or not r[3] or not r[4]:
            skipped += 1
            continue
        try:
            lat_v, lon_v = float(r[3]), float(r[4])
        except (TypeError, ValueError):
            skipped += 1
            continue
        if not in_tokyo(lat_v, lon_v):
            out_of_box += 1
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
            "lat": round(lat_v, 6),
            "lon": round(lon_v, 6),
        })
    # 行き先の候補。ここは地図アプリに渡すためのもので、貼付候補地とは役割が違う。
    # オープンデータが「どこへ行けるか」を出し、案内は地図アプリに任せる。
    def coord(value: str):
        """緯度経度として読めなければ None。だれでも東京には '35.666379,139' のように
        列がずれた行が混じる（2026-08-23 実測）。直さず落として件数を報告する。"""
        try:
            f = float(str(value).strip())
        except (TypeError, ValueError):
            return None
        return f

    dest, dest_dropped = [], 0
    if WATER.exists():
        for r in csv.DictReader(io.StringIO(WATER.read_bytes().decode("cp932"))):
            if (r.get("稼働停止") or "").strip():
                continue
            lat, lon = coord(r.get("緯度")), coord(r.get("経度"))
            if lat is None or lon is None or not in_tokyo(lat, lon):
                dest_dropped += 1
                continue
            dest.append({"k": "water", "n": (r.get("施設名") or "").strip(),
                         "a": (r.get("所在地") or "").strip(), "lat": lat, "lon": lon})
    if TRANSPORT.exists():
        for r in csv.DictReader(io.StringIO(TRANSPORT.read_bytes().decode("cp932"))):
            lat, lon = coord(r.get("緯度")), coord(r.get("経度"))
            if lat is None or lon is None or not in_tokyo(lat, lon):
                dest_dropped += 1
                continue
            dest.append({"k": "station", "n": (r.get("施設名") or "").strip(),
                         "a": f"{r.get('市区町村名','')}{r.get('町丁目名','')}".strip(),
                         # エレベーターの有無は「だれでも東京」が持つ実測値。無い値は入れない
                         "ev": (r.get("エレベーターの有無") or "").strip(),
                         "lat": lat, "lon": lon})

    # 行き先の座標が住所と食い違っていないかを見る。
    # 2026-08-23 実測: 「大江戸線 本郷三丁目」は住所が文京区なのに座標が葛飾区亀有だった。
    # 迷った人に反対方向を示すのは危険なので、疑わしいものは候補から外し、件数を出す。
    def meters(a, b, c, d):
        R, r = 6371000, math.pi / 180
        x, y = (c - a) * r, (d - b) * r * math.cos((a + c) / 2 * r)
        return math.sqrt(x * x + y * y) * R

    by_muni: dict[str, list] = {}
    for pt in points:
        by_muni.setdefault(pt["m"], []).append(pt)

    kept, suspect, unjudged = [], 0, 0
    for x in dest:
        m = MUNI.search(x["a"] or "")
        peers = by_muni.get(m.group(1)) if m else None
        if not peers:
            unjudged += 1
            kept.append(x)          # 照合相手が無い。消す根拠が無いので残す
            continue
        # 住所が名乗る自治体の貼付候補のうち、いちばん近いものまでの距離で見る。
        # 重心と半径では区の形に引きずられるが、これなら形に依存しない。
        near = min(meters(x["lat"], x["lon"], q["lat"], q["lon"]) for q in peers)
        if near > 3000:
            suspect += 1            # 名乗る自治体から3km以上離れている＝座標が誤り
            continue
        kept.append(x)
    dest = kept

    OUT.write_text(json.dumps({
        "source": "東京都総務局 都内災害時帰宅支援ステーション協力店舗一覧（令和7年3月31日）",
        "note": "貼付候補地。実際に貼られた点ではない。",
        "points": points,
        "dest": dest,
        "dest_source": "東京都水道局 Tokyowater Drinking Station 一覧 ／ "
                       "東京都デジタルサービス局 だれでも東京（交通）",
    }, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    kinds = {}
    for d in dest:
        kinds[d["k"]] = kinds.get(d["k"], 0) + 1
    print(f"✓ 貼付候補 {len(points):,} 点 / {len(seq)} 自治体")
    print(f"   空行などで除外 {skipped} 件 ／ 座標が東京都の範囲外で除外 {out_of_box} 件")
    print(f"✓ 行き先候補 {len(dest):,} 点 {kinds}")
    print(f"   座標が読めず落とした {dest_dropped} 件 ／ "
          f"住所と座標が食い違い落とした {suspect} 件 ／ 判定できず残した {unjudged} 件")
    print(f"   → {OUT.relative_to(BASE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
