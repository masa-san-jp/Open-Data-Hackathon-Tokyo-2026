#!/usr/bin/env python3
"""data/processed/dataset.json を埋め込んだ単体HTMLを prototype/index.html に出す。

  python3 scripts/build_prototype.py

fetch() は file:// で失敗するのでデータは HTML に直接埋め込む。
この段階（Phase 0）で作るのは design-spec §5 の 1（ヘッダ数字）・4（欠損パネル）・
5（注記）のみ。SVG地図・ワースト表（§5-2,3）は T04、2100トグル（§5-6）は T05。
reach/nearest は T03 まで全て unknown のため、reach に依存する数字は
「算出前」と正直に出す（無い数字を作らない）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
DATA = APP_DIR / "data" / "processed" / "dataset.json"
OUT = APP_DIR / "prototype" / "index.html"

KIND_LABELS = {
    "shelter": "避難所・避難場所",
    "cool": "クーリングシェルター（涼み処）",
    "medical": "医療機関",
    "care": "介護・福祉施設",
    "barrier_free": "バリアフリー環境（段差・屋根等）",
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
const nf = n => n.toLocaleString('ja-JP');

const meta = DATA.meta, areas = DATA.areas, gaps = DATA.gaps;
document.getElementById('ward-name').textContent = meta.ward;

const pop65 = areas.reduce((a, x) => a + x.pop_65plus, 0);
const pop75 = areas.reduce((a, x) => a + x.pop_75plus, 0);
const unknownAreas = areas.filter(a => Object.values(a.reach).every(v => v === 'unknown')).length;

const stats = [
  {label: '対象区', value: meta.ward, pending: false},
  {label: '65歳以上人口 / 75歳以上人口', value: nf(pop65) + '人 / ' + nf(pop75) + '人', pending: false},
  {label: '800m以内に涼み処が無い高齢者', value: '算出前（T03の距離結合が未実施）', pending: true},
  {label: 'データ欠損で判定不能な町丁', value: nf(unknownAreas) + ' / ' + nf(areas.length) + ' 町丁（reach未算出）', pending: true},
];
document.getElementById('stats').innerHTML = stats.map(s =>
  `<div class="stat"><div class="n${s.pending ? ' pending' : ''}">${s.value}</div>`
  + `<div class="l">${s.label}</div></div>`
).join('');

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
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    html = (
        TEMPLATE
        .replace("__DATA__", json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
        .replace("__KIND_LABELS__", json.dumps(KIND_LABELS, ensure_ascii=False))
        .replace("__REASON_LABELS__", json.dumps(REASON_LABELS, ensure_ascii=False))
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"✓ {OUT.relative_to(APP_DIR)} ({len(html):,} バイト / {len(payload['areas'])} 町丁 / "
          f"{len(payload['facilities'])} 施設)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
