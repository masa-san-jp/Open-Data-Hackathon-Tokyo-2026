#!/usr/bin/env python3
"""data/processed/dataset.json を埋め込んだ単体HTMLを prototype/index.html に出す。

  python3 scripts/build_prototype.py

fetch() は file:// で失敗するのでデータは HTML に直接埋め込む。
SVG地図・ワースト表を含むdesign-spec §5のPhase 1画面を作る。
データはHTMLに直接埋め込むため、file://で開いても外部fetchは発生しない。
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
DATA = APP_DIR / "data" / "processed" / "dataset.json"
CONFIG = APP_DIR / "config.json"
OUT = APP_DIR / "prototype" / "index.html"

KIND_LABELS = {
    "shelter": "避難所・避難場所",
    "cool": "クーリングシェルター（涼み処）",
    "medical": "医療機関",
    "care": "介護・福祉施設",
    "barrier_free": "バリアフリー環境（段差・屋根等）",
    "area_centroid": "町丁代表点",
}

REASON_LABELS = {
    "not_published": "未公開",
    "not_collected": "未整備・確認が必要",
    "not_applicable": "対象外",
    "unknown": "不明",
    "source_missing": "機械可読な公開データが存在しない",
    "extraction_failed": "取得・抽出に失敗",
    "under_review": "確認中",
}

MAP_WIDTH = 760
MAP_HEIGHT = 520
MAP_PADDING = 30
REACH_COLORS = {
    "near": "#18794e",
    "far": "#a66a00",
    "out": "#b42318",
    "unknown": "#77736c",
}
REACH_LABELS = {
    "near": "near（300m以内）",
    "far": "far（300〜800m）",
    "out": "out（800m超）",
    "unknown": "unknown（判定不能）",
}
FACILITY_COLORS = {
    "shelter": "#255c99",
    "cool": "#0b7285",
    "medical": "#8e3b46",
    "care": "#6b4f9b",
}
FACILITY_SYMBOLS = {
    "shelter": "■",
    "cool": "●",
    "medical": "◆",
    "care": "▲",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def number(value: int | float) -> str:
    return f"{value:,}"


def distance_label(value: object) -> str:
    if isinstance(value, (int, float)):
        return f"{value:,.1f}m"
    return "位置不明"


def make_projection(payload: dict):
    """座標の縦横比を保ったSVG投影関数を返す。"""
    coordinates = [
        (a["lat"], a["lon"])
        for a in payload["areas"]
        if a.get("lat") is not None and a.get("lon") is not None
    ]
    coordinates.extend(
        (f["lat"], f["lon"])
        for f in payload["facilities"]
        if f.get("lat") is not None and f.get("lon") is not None
    )
    if not coordinates:
        return lambda _lat, _lon: (MAP_WIDTH / 2, MAP_HEIGHT / 2)

    min_lat = min(lat for lat, _lon in coordinates)
    max_lat = max(lat for lat, _lon in coordinates)
    min_lon = min(lon for _lat, lon in coordinates)
    max_lon = max(lon for _lat, lon in coordinates)
    lat_span = max(max_lat - min_lat, 0.000001)
    lon_span = max(max_lon - min_lon, 0.000001)
    usable_width = MAP_WIDTH - 2 * MAP_PADDING
    usable_height = MAP_HEIGHT - 2 * MAP_PADDING
    scale = min(usable_width / lon_span, usable_height / lat_span)
    drawn_width = lon_span * scale
    drawn_height = lat_span * scale
    left = (MAP_WIDTH - drawn_width) / 2
    top = (MAP_HEIGHT - drawn_height) / 2

    def project(lat: float, lon: float) -> tuple[float, float]:
        x = left + (lon - min_lon) * scale
        y = top + (max_lat - lat) * scale
        return x, y

    return project


def make_area_title(area: dict) -> str:
    reach = area["reach"].get("cool", "unknown")
    return (
        f"{area['name']} / 75歳以上 {number(area['pop_75plus'])}人 / "
        f"涼み処 {distance_label(area['nearest_m'].get('cool'))} "
        f"{REACH_LABELS.get(reach, reach)} / "
        f"避難所 {distance_label(area['nearest_m'].get('shelter'))}"
    )


def build_svg(payload: dict) -> str:
    """町丁円と座標付き施設マーカーを含む自己完結SVGを作る。"""
    project = make_projection(payload)
    located_areas = [a for a in payload["areas"] if a.get("lat") is not None]
    max_pop = max((a["pop_75plus"] for a in located_areas), default=1)
    area_markup = []
    for area in payload["areas"]:
        if area.get("lat") is None or area.get("lon") is None:
            continue
        x, y = project(area["lat"], area["lon"])
        reach = area["reach"].get("cool", "unknown")
        radius = 3.5 + 14 * area["pop_75plus"] / max_pop
        color = REACH_COLORS.get(reach, REACH_COLORS["unknown"])
        area_markup.append(
            f'<circle class="area-point" cx="{x:.2f}" cy="{y:.2f}" r="{radius:.2f}" '
            f'fill="{color}" fill-opacity=".78" stroke="#fff" stroke-width="1">'
            f"<title>{esc(make_area_title(area))}</title></circle>"
        )

    facility_markup = []
    for facility in payload["facilities"]:
        if facility.get("lat") is None or facility.get("lon") is None:
            continue
        x, y = project(facility["lat"], facility["lon"])
        kind = facility["kind"]
        color = FACILITY_COLORS.get(kind, "#444")
        symbol = FACILITY_SYMBOLS.get(kind, "?")
        if kind == "shelter":
            shape = f'<rect x="{x - 3:.2f}" y="{y - 3:.2f}" width="6" height="6" />'
        elif kind == "cool":
            shape = f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.3" />'
        elif kind == "medical":
            shape = (f'<path d="M {x:.2f} {y - 4:.2f} L {x + 4:.2f} {y:.2f} '
                     f'L {x:.2f} {y + 4:.2f} L {x - 4:.2f} {y:.2f} Z" />')
        else:
            shape = (f'<path d="M {x:.2f} {y - 4:.2f} L {x + 4:.2f} {y + 3:.2f} '
                     f'L {x - 4:.2f} {y + 3:.2f} Z" />')
        facility_markup.append(
            f'<g class="facility-marker" fill="{color}" stroke="#fff" stroke-width=".8">'
            f'{shape}<title>{esc(KIND_LABELS.get(kind, kind))}: {esc(facility["name"])} '
            f'（記号 {esc(symbol)}）</title></g>'
        )

    return (
        f'<svg class="map-svg" viewBox="0 0 {MAP_WIDTH} {MAP_HEIGHT}" '
        'role="img" aria-labelledby="map-title map-desc">'
        f'<title id="map-title">{esc(payload["meta"]["ward"])}の町丁別、涼み処reachと拠点分布</title>'
        '<desc id="map-desc">円の大きさは75歳以上人口、色は涼み処への直線距離。'
        '施設記号は座標があるものだけを表示。</desc>'
        f'<rect class="map-background" x="0" y="0" width="{MAP_WIDTH}" height="{MAP_HEIGHT}" />'
        + "".join(area_markup)
        + "".join(facility_markup)
        + "</svg>"
    )


def build_worst_rows(payload: dict) -> tuple[str, int, int, int]:
    """涼み処reachがoutの町丁を75+人口順で最大10件返す。"""
    areas = payload["areas"]
    out_areas = sorted(
        (a for a in areas if a["reach"].get("cool") == "out"),
        key=lambda a: (-a["pop_75plus"], a["code"]),
    )
    unknown_areas = [a for a in areas if a["reach"].get("cool") == "unknown"]
    out_population = sum(a["pop_75plus"] for a in out_areas)
    unknown_population = sum(a["pop_75plus"] for a in unknown_areas)
    rows = []
    for rank, area in enumerate(out_areas[:10], 1):
        rows.append(
            f'<tr data-area-code="{esc(area["code"])}" tabindex="0" aria-selected="false"><td>{rank}</td><td>{esc(area["name"])}</td>'
            f'<td>{number(area["pop_75plus"])}人</td>'
            f'<td>{distance_label(area["nearest_m"].get("cool"))}</td>'
            f'<td><span class="reach out">out</span></td></tr>'
        )
    return "".join(rows), out_population, unknown_population, len(unknown_areas)

TEMPLATE = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>暑さと災害に強い生活圏ナビ</title>
<style>
 :root{--bg:#fbfbfa;--fg:#1c1b19;--mut:#6b675f;--line:#e2ded6;--accent:#9a3412;--card:#fff;--warn:#8a6d00}
 @media (prefers-color-scheme:dark){
  :root{--bg:#161513;--fg:#eceae5;--mut:#9c968a;--line:#33302b;--accent:#fb923c;--card:#1e1d1a;--warn:#e0b83d}}
 *{box-sizing:border-box}
 body{margin:0;background:var(--bg);color:var(--fg);
  font-family:"Hiragino Sans","Noto Sans JP",system-ui,sans-serif;line-height:1.7}
 .wrap{max-width:980px;margin:0 auto;padding:32px 20px 80px}
 h1{font-size:1.3rem;margin:0 0 6px}
 .claim{color:var(--mut);font-size:.92rem;margin-bottom:26px;max-width:56em}
 .stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:28px}
 .stat{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:16px 18px}
 .stat .n{font-size:1.7rem;font-weight:700;letter-spacing:-.02em}
 .stat .n.pending{font-size:1.05rem;color:var(--warn);font-weight:600}
 .stat .l{font-size:.78rem;color:var(--mut);margin-top:4px}
 section{margin-bottom:28px}
 h2{font-size:1rem;margin:0 0 10px}
 .scroll{overflow-x:auto;border:1px solid var(--line);border-radius:6px;background:var(--card)}
 table{border-collapse:collapse;width:100%;font-size:.87rem;min-width:420px}
 th,td{padding:7px 12px;text-align:right;white-space:nowrap;border-bottom:1px solid var(--line)}
 th:first-child,td:first-child{text-align:left}
 thead th{font-weight:600;font-size:.8rem;color:var(--mut)}
 .map-shell{border:1px solid var(--line);border-radius:6px;background:var(--card);padding:10px}
 .map-svg{display:block;width:100%;height:auto;min-height:280px}
 .map-background{fill:color-mix(in srgb,var(--fg) 3%,var(--card));stroke:var(--line);stroke-width:1}
 .legend{display:flex;flex-wrap:wrap;gap:8px 14px;margin-top:10px;font-size:.78rem;color:var(--mut)}
 .legend span{display:inline-flex;align-items:center;gap:5px}
 .swatch{width:11px;height:11px;border-radius:50%;display:inline-block;border:1px solid color-mix(in srgb,var(--fg) 30%,transparent)}
 .swatch.near{background:#18794e}.swatch.far{background:#a66a00}.swatch.out{background:#b42318}.swatch.unknown{background:#77736c}
 .marker-key{margin-top:5px;font-size:.76rem;color:var(--mut)}
 .marker-key b{margin-right:4px}
 .reach{display:inline-block;padding:1px 6px;border-radius:999px;font-size:.72rem;font-weight:700;line-height:1.5}
 .reach.out{color:#fff;background:#b42318}.reach.near{color:#fff;background:#18794e}
 .reach.far{color:#fff;background:#a66a00}.reach.unknown{color:#fff;background:#77736c}
 .table-note{font-size:.8rem;color:var(--mut);margin:8px 0 0}
 .stress-controls{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 14px;margin:-12px 0 28px}
 .stress-controls .label{font-size:.8rem;color:var(--mut);margin-right:8px}
 .stress-buttons{display:inline-flex;flex-wrap:wrap;gap:6px;vertical-align:middle}
 .stress-button{appearance:none;border:1px solid var(--line);border-radius:999px;background:var(--bg);color:var(--fg);cursor:pointer;font:inherit;font-size:.82rem;padding:4px 10px}
 .stress-button[aria-pressed="true"]{background:var(--fg);border-color:var(--fg);color:var(--bg);font-weight:700}
 .stress-button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
 .stress-note{font-size:.78rem;color:var(--mut);margin:8px 0 0}
 .stress-note strong{color:var(--fg)}
 #worst-body tr{cursor:pointer}
 #worst-body tr:hover,#worst-body tr:focus{background:color-mix(in srgb,var(--accent) 8%,var(--card));outline:none}
 #worst-body tr[aria-selected="true"]{box-shadow:inset 3px 0 0 var(--accent);background:color-mix(in srgb,var(--accent) 10%,var(--card))}
 .pilot-section[hidden]{display:none}
 .pilot-card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:18px}
 .pilot-card-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;border-bottom:1px solid var(--line);padding-bottom:12px}
 .pilot-kicker{color:var(--mut);font-size:.75rem;letter-spacing:.04em;margin:0}
 .pilot-card h3{font-size:1.35rem;margin:2px 0 0}
 .pilot-card h4{font-size:.85rem;margin:0 0 7px}
 .pilot-meta{color:var(--mut);font-size:.8rem;margin:4px 0 0}
 .print-button{appearance:none;border:1px solid var(--fg);border-radius:5px;background:var(--fg);color:var(--bg);cursor:pointer;font:inherit;font-size:.82rem;padding:6px 10px;white-space:nowrap}
 .print-button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
 .pilot-summary{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}
 .pilot-summary .summary-item{background:color-mix(in srgb,var(--fg) 5%,var(--card));border:1px solid var(--line);border-radius:5px;padding:7px 10px}
 .pilot-summary .summary-item b{display:block;font-size:1.05rem}
 .pilot-summary .summary-item span{color:var(--mut);font-size:.72rem}
 .pilot-card table{min-width:0}
 .pilot-card th,.pilot-card td{padding:6px 8px}
 .pilot-card th:first-child,.pilot-card td:first-child{text-align:left}
 .pilot-card .reach{white-space:nowrap}
 .pilot-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:18px;margin-top:16px}
 .pilot-subsection{min-width:0}
 .pilot-list{font-size:.78rem;margin:0;padding-left:1.15em}
 .pilot-list li{margin:3px 0}
 .pilot-list code{font-size:.72rem}
 .pilot-list a{overflow-wrap:anywhere}
 .pilot-actions{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:18px;margin-top:16px}
 .write-box{min-height:74px;border:1px solid var(--line);border-radius:4px;background:repeating-linear-gradient(to bottom,transparent 0,transparent 25px,var(--line) 26px,var(--line) 27px);padding:5px 8px}
 .write-box.short{min-height:52px}
 .pilot-footnote{color:var(--mut);font-size:.75rem;margin:14px 0 0}
 .gaps{list-style:none;margin:0;padding:0}
 .gaps li{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--warn);
  border-radius:6px;padding:12px 16px;margin-bottom:8px}
 .gaps .tag{font-size:.72rem;color:var(--warn);font-weight:700;letter-spacing:.02em}
 .gaps .note{font-size:.87rem;margin-top:4px}
 .callout{font-size:.85rem;color:var(--mut);margin-top:10px}
 footer{margin-top:36px;border-top:1px solid var(--line);padding-top:18px;
  font-size:.8rem;color:var(--mut)}
 footer h3{color:var(--fg);font-size:.88rem;margin:16px 0 6px}
 footer ul{margin:0;padding-left:1.2em}
 footer li{margin:2px 0}
 code{background:color-mix(in srgb,var(--fg) 8%,transparent);padding:1px 5px;border-radius:3px}
 @media print{
  @page{size:A4 portrait;margin:10mm}
  body{background:#fff;color:#111;font-size:9.5pt;line-height:1.4}
  body .wrap{max-width:none;padding:0}
  body .wrap> *:not(#pilot-section){display:none !important}
  #pilot-section{display:block !important;margin:0}
  .pilot-card{border:1px solid #111;border-radius:0;padding:5mm;box-shadow:none}
  .pilot-card-head{padding-bottom:3mm}
  .pilot-card h3{font-size:17pt}
  .pilot-meta,.pilot-footnote,.pilot-list{font-size:8pt}
  .print-button{display:none}
  .pilot-summary{gap:5px;margin:3mm 0}
  .pilot-summary .summary-item{padding:4px 7px}
  .pilot-summary .summary-item b{font-size:11pt}
  .pilot-grid,.pilot-actions{gap:4mm;margin-top:3mm}
  .pilot-card h4{font-size:9pt;margin-bottom:4px}
  .pilot-card th,.pilot-card td{padding:3px 5px}
  .write-box{min-height:42mm}
  .write-box.short{min-height:28mm}
  .pilot-footnote{margin-top:3mm}
 }
</style>
</head>
<body>
<div class="wrap">
<h1>暑さと災害に強い生活圏ナビ</h1>
<p class="claim">あなたの町の高齢者は、歩いて涼める場所・避難できる場所に届くか。
届かない町がどこかと、<b>そもそもデータが無くて分からない町がどこか</b>を、
東京都オープンデータだけで見せる。「全部つながった綺麗な地図」ではなく、
届く／届かない／分からない の3値を主役にする。</p>

<div class="stats" id="stats"></div>

<div class="stress-controls" aria-label="75歳以上人口のストレステスト">
 <span class="label">75歳以上人口シナリオ:</span>
 <span class="stress-buttons" id="stress-buttons"></span>
 <p class="stress-note"><strong>これは予測ではなくストレステストです。</strong> <span id="stress-note"></span></p>
 <p class="stress-note" id="stress-source"></p>
</div>

<section>
 <h2>町丁の届きやすさ（涼み処）</h2>
 <div class="map-shell">__MAP__</div>
 <div class="legend" aria-label="reachの凡例">
  <span><i class="swatch near"></i>near（300m以内）</span>
  <span><i class="swatch far"></i>far（300〜800m）</span>
  <span><i class="swatch out"></i>out（800m超）</span>
  <span><i class="swatch unknown"></i>unknown（判定不能）</span>
 </div>
 <div class="marker-key"><b>施設記号:</b> ■ 避難所　● 涼み処　◆ 医療　▲ 介護・福祉</div>
 <p class="callout">円の大きさは75歳以上人口に比例。色は涼み処への直線距離で、施設の記号は座標があるものだけを表示。</p>
</section>

<section>
 <h2>涼み処が800mを超える町丁（<span id="worst-scenario">現在</span>の75歳以上人口順）</h2>
 <div class="scroll">
 <table>
  <thead><tr><th>順位</th><th>町丁</th><th>75歳以上</th><th>最近の涼み処</th><th>判定</th></tr></thead>
  <tbody id="worst-body">__WORST_ROWS__</tbody>
 </table>
 </div>
 <p class="table-note">対象: 涼み処のreachがout（800m超）の町丁。unknownは表から除外し、下に別掲。</p>
 <p class="table-note" id="unknown-note">涼み処の判定不能: __UNKNOWN_COOL_AREAS__町丁 / __UNKNOWN_COOL_POP__人。</p>
</section>

<section class="pilot-section" id="pilot-section" hidden>
 <div class="pilot-card" id="pilot-card" aria-live="polite">
  <div class="pilot-card-head">
   <div>
    <p class="pilot-kicker">30日パイロット確認カード</p>
    <h3 id="pilot-area-name"></h3>
    <p class="pilot-meta" id="pilot-area-meta"></p>
   </div>
   <button type="button" class="print-button" id="print-card">このカードを印刷</button>
  </div>
  <div class="pilot-summary" id="pilot-summary"></div>
  <section class="pilot-subsection">
   <h4>拠点までの直線距離とreach</h4>
   <div class="scroll">
    <table>
     <thead><tr><th>種別</th><th>最近の拠点</th><th>判定</th></tr></thead>
     <tbody id="pilot-reach"></tbody>
    </table>
   </div>
   <p class="pilot-meta" id="pilot-location-note"></p>
  </section>
  <div class="pilot-grid">
   <section class="pilot-subsection">
    <h4>欠損理由コード一覧（区全体）</h4>
    <ul class="pilot-list" id="pilot-gaps"></ul>
   </section>
   <section class="pilot-subsection">
    <h4>出典</h4>
    <ul class="pilot-list" id="pilot-sources"></ul>
   </section>
  </div>
  <div class="pilot-actions">
   <section>
    <h4>次の30日で確認すること</h4>
    <div class="write-box" aria-label="次の30日で確認することの記入欄"></div>
   </section>
   <section>
    <h4>中止条件</h4>
    <div class="write-box short" aria-label="中止条件の記入欄"></div>
   </section>
  </div>
  <p class="pilot-footnote" id="pilot-footnote"></p>
 </div>
</section>

<section>
 <h2>拠点の件数（位置不明を含む）</h2>
 <div class="scroll">
 <table>
  <thead><tr><th>種別</th><th>件数</th><th>うち位置不明</th></tr></thead>
  <tbody id="facility-table"></tbody>
 </table>
 </div>
</section>

<section>
 <h2>欠損パネル</h2>
 <ul class="gaps" id="gaps"></ul>
 <p class="callout">これは本作品の不具合ではなく、公開データの現状である。</p>
</section>

<footer>
 <div><b>直線距離であり経路距離ではない。</b>徒歩の実際の道のりや段差・信号待ちは考慮していない。
 経路計算はスコープ外。</div>
 <div id="missing-note" style="margin-top:6px"></div>
 <h3>出典（URL・取得日）</h3>
 <ul id="sources"></ul>
 <div style="margin-top:10px">対象区: <b id="ward-name"></b>（<code>config.json</code> で変更可能）。
  再現は <code>scripts/fetch_sources.py</code> → <code>scripts/build_dataset.py</code> →
  <code>scripts/verify.py</code>。</div>
</footer>
</div>

<script>
const DATA = __DATA__;
const KIND_LABELS = __KIND_LABELS__;
const REASON_LABELS = __REASON_LABELS__;
const REACH_LABELS = __REACH_LABELS__;
const STRESS = __STRESS_CONFIG__;
const nf = n => n.toLocaleString('ja-JP');

const meta = DATA.meta, areas = DATA.areas, gaps = DATA.gaps;
document.getElementById('ward-name').textContent = meta.ward;

const pop65 = areas.reduce((a, x) => a + x.pop_65plus, 0);
const stressScenarios = STRESS.scenarios || [];
const stressById = Object.fromEntries(stressScenarios.map(s => [s.id, s]));
const defaultStress = stressById.current || stressScenarios[0];
const scaled75 = (area, scenario) => Math.round(area.pop_75plus * scenario.factor);
let activeStress = defaultStress;
let selectedAreaCode = null;

document.getElementById('stress-note').textContent = STRESS.note;
document.getElementById('stress-source').textContent = '係数の出所: ' + STRESS.source;
document.getElementById('stress-buttons').innerHTML = stressScenarios.map(s =>
  `<button type="button" class="stress-button" data-scenario="${s.id}" aria-pressed="false">${s.label} ×${s.factor}</button>`
).join('');

function renderStats(scenario) {
  const pop75 = areas.reduce((total, area) => total + scaled75(area, scenario), 0);
  const coolOut = areas.filter(a => a.reach.cool === 'out');
  const coolUnknown = areas.filter(a => a.reach.cool === 'unknown');
  const coolOutPop = coolOut.reduce((total, area) => total + scaled75(area, scenario), 0);
  const coolUnknownPop = coolUnknown.reduce((total, area) => total + scaled75(area, scenario), 0);
  const stats = [
    {label: '対象区', value: meta.ward, pending: false},
    {label: '65歳以上人口 / 75歳以上人口（' + scenario.label + '）', value: nf(pop65) + '人 / ' + nf(pop75) + '人', pending: false},
    {label: '800m以内に涼み処が無い75歳以上（' + scenario.label + '）', value: nf(coolOutPop) + '人', pending: false},
    {label: '涼み処のデータ欠損で判定不能な75歳以上（' + scenario.label + '）', value: nf(coolUnknownPop) + '人', pending: true},
  ];
  document.getElementById('stats').innerHTML = stats.map(s =>
    `<div class="stat"><div class="n${s.pending ? ' pending' : ''}">${s.value}</div>`
    + `<div class="l">${s.label}</div></div>`
  ).join('');
}

function renderWorst(scenario) {
  const outAreas = areas.filter(a => a.reach.cool === 'out')
    .map(area => ({area, population: scaled75(area, scenario)}))
    .sort((left, right) => right.population - left.population || left.area.code.localeCompare(right.area.code));
  document.getElementById('worst-body').innerHTML = outAreas.slice(0, 10).map((item, index) => {
    const area = item.area;
    const distance = typeof area.nearest_m.cool === 'number' ? nf(area.nearest_m.cool.toFixed(1)) + 'm' : '位置不明';
    const selected = area.code === selectedAreaCode;
    return `<tr data-area-code="${area.code}" tabindex="0" aria-selected="${selected}"><td>${index + 1}</td><td>${area.name}</td>`
      + `<td>${nf(item.population)}人</td><td>${distance}</td><td><span class="reach out">out</span></td></tr>`;
  }).join('');
  const unknownAreas = areas.filter(a => a.reach.cool === 'unknown');
  const unknownPopulation = unknownAreas.reduce((total, area) => total + scaled75(area, scenario), 0);
  document.getElementById('unknown-note').textContent =
    '涼み処の判定不能: ' + nf(unknownAreas.length) + '町丁 / ' + nf(unknownPopulation) + '人（' + scenario.label + '）。';
  document.getElementById('worst-scenario').textContent = scenario.label;
  if (selectedAreaCode) {
    const selectedArea = areas.find(area => area.code === selectedAreaCode);
    if (selectedArea) renderPilotCard(selectedArea);
  }
}

const htmlEscape = value => String(value).replace(/[&<>"']/g, character => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[character]));
const distanceText = value => typeof value === 'number'
  ? value.toLocaleString('ja-JP', {minimumFractionDigits: 1, maximumFractionDigits: 1}) + 'm'
  : '位置不明';

function renderPilotCard(area) {
  const scenario = activeStress;
  document.getElementById('pilot-area-name').textContent = area.name;
  document.getElementById('pilot-area-meta').textContent =
    'コード: ' + area.code + ' ／ 選択シナリオ: ' + scenario.label + '（×' + scenario.factor + '）';
  document.getElementById('pilot-summary').innerHTML = [
    {value: nf(scaled75(area, scenario)) + '人', label: '75歳以上人口（' + scenario.label + '）'},
    {value: nf(area.pop_65plus) + '人', label: '65歳以上人口（現況）'},
    {value: REACH_LABELS[area.reach.cool] || area.reach.cool, label: '涼み処 reach'},
  ].map(item => `<div class="summary-item"><b>${htmlEscape(item.value)}</b><span>${htmlEscape(item.label)}</span></div>`).join('');
  document.getElementById('pilot-reach').innerHTML = ['shelter', 'cool', 'medical', 'care'].map(kind => {
    const reach = area.reach[kind];
    return `<tr><th>${htmlEscape(KIND_LABELS[kind])}</th><td>${distanceText(area.nearest_m[kind])}</td>`
      + `<td><span class="reach ${htmlEscape(reach)}">${htmlEscape(REACH_LABELS[reach] || reach)}</span></td></tr>`;
  }).join('');
  document.getElementById('pilot-location-note').textContent = area.lat === null
    ? 'この町丁は代表点が未結合のため、全拠点の距離判定から除外されています。'
    : '町丁代表点: 北緯 ' + area.lat.toFixed(6) + ' ／ 東経 ' + area.lon.toFixed(6) + '（距離は直線距離）';
  const areaGap = area.lat === null
    ? `<li><code>source_missing</code> 町丁代表点: この町丁の代表点がD6にありません</li>` : '';
  document.getElementById('pilot-gaps').innerHTML = gaps.map(g =>
    `<li><code>${htmlEscape(g.reason)}</code> ${htmlEscape(KIND_LABELS[g.kind] || g.kind)}: ${htmlEscape(g.note)}</li>`
  ).join('') + areaGap;
  document.getElementById('pilot-sources').innerHTML = meta.sources.map(source => {
    const date = (source.fetched_at || '').slice(0, 10) || '不明';
    return `<li>${htmlEscape(source.id)}（${htmlEscape(date)}）<br>`
      + `<a href="${htmlEscape(source.url)}">${htmlEscape(source.url)}</a></li>`;
  }).join('');
  document.getElementById('pilot-footnote').textContent =
    'このカードは選択時点のストレステスト表示です。経路距離・段差・信号待ちは含まず、位置不明データは判定不能として扱います。';
  document.getElementById('pilot-section').hidden = false;
}

function selectArea(code) {
  const area = areas.find(candidate => candidate.code === code);
  if (!area) return;
  selectedAreaCode = area.code;
  document.querySelectorAll('#worst-body tr[data-area-code]').forEach(row => {
    row.setAttribute('aria-selected', row.dataset.areaCode === selectedAreaCode ? 'true' : 'false');
  });
  renderPilotCard(area);
  document.getElementById('pilot-section').scrollIntoView({behavior: 'smooth', block: 'start'});
}

function selectStressScenario(id) {
  const scenario = stressById[id] || defaultStress;
  activeStress = scenario;
  document.querySelectorAll('.stress-button').forEach(button => {
    button.setAttribute('aria-pressed', button.dataset.scenario === scenario.id ? 'true' : 'false');
  });
  renderStats(scenario);
  renderWorst(scenario);
}

document.querySelectorAll('.stress-button').forEach(button => {
  button.addEventListener('click', () => selectStressScenario(button.dataset.scenario));
});
selectStressScenario(defaultStress.id);

document.getElementById('worst-body').addEventListener('click', event => {
  const row = event.target.closest('tr[data-area-code]');
  if (row) selectArea(row.dataset.areaCode);
});
document.getElementById('worst-body').addEventListener('keydown', event => {
  if (event.key !== 'Enter' && event.key !== ' ') return;
  const row = event.target.closest('tr[data-area-code]');
  if (!row) return;
  event.preventDefault();
  selectArea(row.dataset.areaCode);
});
document.getElementById('print-card').addEventListener('click', () => window.print());

const kinds = ['shelter', 'cool', 'medical', 'care'];
document.getElementById('facility-table').innerHTML = kinds.map(k => {
  const count = meta.facility_counts[k] || 0;
  const missing = meta.missing_location_counts[k] || 0;
  return `<tr><td>${KIND_LABELS[k]}</td><td>${nf(count)}</td><td>${missing ? nf(missing) + '件' : '—'}</td></tr>`;
}).join('');

document.getElementById('gaps').innerHTML = gaps.map(g =>
  `<li><div class="tag">${KIND_LABELS[g.kind] || g.kind} ／ ${REASON_LABELS[g.reason] || g.reason}</div>`
  + `<div class="note">${g.note}</div></li>`
).join('');

const totalMissing = Object.values(meta.missing_location_counts).reduce((a, b) => a + b, 0);
document.getElementById('missing-note').textContent =
  '位置不明の施設: ' + nf(totalMissing) + '件（座標が無いためこの段階では地図・距離判定から除外）。';

document.getElementById('sources').innerHTML = meta.sources.map(s => {
  const date = (s.fetched_at || '').slice(0, 10);
  return `<li>${s.id}: <a href="${s.url}">${s.url}</a>（取得日 ${date || '不明'}）</li>`;
}).join('');
</script>
</body>
</html>
"""


def main() -> int:
    if not DATA.exists():
        print("✗ data/processed/dataset.json が無い。先に scripts/build_dataset.py", file=sys.stderr)
        return 1
    if not CONFIG.exists():
        print("✗ config.json が無い", file=sys.stderr)
        return 1
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    stress_config = {
        "scenarios": config.get("stress_scenarios", []),
        "source": config.get("stress_source", ""),
        "note": config.get("stress_note", ""),
    }
    worst_rows, _out_population, unknown_population, unknown_area_count = build_worst_rows(payload)
    html = (
        TEMPLATE
        .replace("__DATA__", json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
        .replace("__KIND_LABELS__", json.dumps(KIND_LABELS, ensure_ascii=False))
        .replace("__REASON_LABELS__", json.dumps(REASON_LABELS, ensure_ascii=False))
        .replace("__REACH_LABELS__", json.dumps(REACH_LABELS, ensure_ascii=False))
        .replace("__STRESS_CONFIG__", json.dumps(stress_config, ensure_ascii=False, separators=(",", ":")))
        .replace("__MAP__", build_svg(payload))
        .replace("__WORST_ROWS__", worst_rows)
        .replace("__UNKNOWN_COOL_AREAS__", number(unknown_area_count))
        .replace("__UNKNOWN_COOL_POP__", number(unknown_population))
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"✓ {OUT.relative_to(APP_DIR)} ({len(html):,} バイト / {len(payload['areas'])} 町丁 / "
          f"{len(payload['facilities'])} 施設)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
