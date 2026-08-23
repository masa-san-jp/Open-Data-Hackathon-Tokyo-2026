#!/usr/bin/env python3
"""data/stress_test.json を埋め込んだ単体HTMLを prototype/index.html に出す。

  python3 scripts/build_prototype.py

fetch() は file:// で失敗するのでデータは HTML に直接埋める。
手書きせず生成にしてあるのは、データを作り直したら画面も作り直せるようにするため。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "stress_test.json"
OUT = BASE / "prototype" / "index.html"

TEMPLATE = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>東京都 高齢化ストレステスト</title>
<style>
 :root{--bg:#fbfbfa;--fg:#1c1b19;--mut:#6b675f;--line:#e2ded6;--accent:#9a3412;--card:#fff}
 @media (prefers-color-scheme:dark){
  :root{--bg:#161513;--fg:#eceae5;--mut:#9c968a;--line:#33302b;--accent:#fb923c;--card:#1e1d1a}}
 *{box-sizing:border-box}
 body{margin:0;background:var(--bg);color:var(--fg);
  font-family:"Hiragino Sans","Noto Sans JP",system-ui,sans-serif;line-height:1.7}
 .wrap{max-width:1000px;margin:0 auto;padding:32px 20px 80px}
 h1{font-size:1.35rem;margin:0 0 4px}
 .sub{color:var(--mut);font-size:.85rem;margin-bottom:28px}
 .lead{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent);
  border-radius:6px;padding:20px 22px;margin-bottom:12px}
 .lead h2{font-size:1rem;margin:0 0 12px;font-weight:600}
 .big{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;margin:10px 0}
 .big b{font-size:2.6rem;font-weight:700;letter-spacing:-.02em}
 .big .arrow{color:var(--mut);font-size:1.4rem}
 .big .yr{color:var(--mut);font-size:.8rem}
 .lead p{margin:10px 0 0;font-size:.9rem;color:var(--mut)}
 .hint{font-size:.82rem;color:var(--mut);margin:14px 0 8px}
 .scroll{overflow-x:auto;border:1px solid var(--line);border-radius:6px;background:var(--card)}
 table{border-collapse:collapse;width:100%;font-size:.87rem;min-width:560px}
 th,td{padding:7px 12px;text-align:right;white-space:nowrap;border-bottom:1px solid var(--line)}
 th:first-child,td:first-child{text-align:left}
 thead th{position:sticky;top:0;background:var(--card);cursor:pointer;
  font-weight:600;font-size:.8rem;color:var(--mut);user-select:none}
 thead th:hover{color:var(--fg)}
 thead th[aria-sort]{color:var(--accent)}
 tbody tr{cursor:pointer}
 tbody tr:hover{background:color-mix(in srgb,var(--accent) 7%,transparent)}
 tbody tr.on{background:color-mix(in srgb,var(--accent) 13%,transparent)}
 .low{color:var(--accent);font-weight:700}
 #detail{margin-top:18px;background:var(--card);border:1px solid var(--line);
  border-radius:6px;padding:18px 20px}
 #detail h3{margin:0 0 10px;font-size:.98rem}
 #detail .none{color:var(--mut);font-size:.87rem;margin:0}
 footer{margin-top:44px;border-top:1px solid var(--line);padding-top:20px;
  font-size:.8rem;color:var(--mut)}
 footer h4{color:var(--fg);font-size:.85rem;margin:18px 0 6px}
 footer ul{margin:0;padding-left:1.2em}
 code{background:color-mix(in srgb,var(--fg) 8%,transparent);padding:1px 5px;border-radius:3px}
</style>
</head>
<body>
<div class="wrap">
<h1>東京都 高齢化ストレステスト</h1>
<div class="sub">高齢者1人を支える昼間の働き手は、2045年に何人になるか</div>

<div class="lead">
  <h2>支え手が1人を切る街の数</h2>
  <div class="big">
    <span><b id="n2020">-</b> <span class="yr">2020年</span></span>
    <span class="arrow">→</span>
    <span><b id="n2045" style="color:var(--accent)">-</b> <span class="yr">2045年</span></span>
    <span class="yr" id="denom"></span>
  </div>
  <p>いま東京のどの区市町村も、高齢者1人に対して働き手が1人以上いる。20年後、そうでない街ができる。</p>
</div>

<div class="hint">列の見出しを押すと並べ替わる。<b>高齢化率で並べ替えると、順位が入れ替わる。</b>
高齢化率は「街に高齢者が何割いるか」しか言わず、昼間そこに働き手がいるかを言わないため。</div>

<div class="scroll">
<table id="t">
 <thead><tr>
  <th data-k="name">自治体</th>
  <th data-k="aging_rate">高齢化率 2045</th>
  <th data-k="support_ratio">支え手比率 2045</th>
  <th data-k="single_household_rate">単独世帯率 2045</th>
  <th data-k="elderly">65歳以上 2045</th>
 </tr></thead>
 <tbody></tbody>
</table>
</div>

<div id="detail"><p class="none">行を押すと、2020年から2045年までの推移が出ます。</p></div>

<footer>
 <div>支え手比率 ＝ その自治体の<b>昼間就業者数</b> ÷ 65歳以上人口。
  昼間就業者はその自治体で<b>働く</b>人で、住む人ではない。</div>
 <h4>結合できなかった自治体</h4>
 <ul id="ex"></ul>
 <h4>出典</h4>
 <ul>
  <li>国立社会保障・人口問題研究所「日本の地域別将来推計人口（令和5年推計）」東京都</li>
  <li>東京都総務局「東京都就業者数の予測（令和7年）」</li>
  <li>東京都総務局「東京都世帯数の予測」</li>
 </ul>
 <div style="margin-top:10px">2020年は実績値、以降は推計。<b>2045年より先へは外挿していない</b>
  （就業者・世帯の推計が2045年で切れるため）。
  再現は <code>scripts/fetch_sources.py</code> → <code>build_dataset.py</code> →
  <code>verify.py</code>。</div>
</footer>
</div>

<script>
const DATA = __DATA__;
const M = DATA.municipalities, Y = DATA.years;
const nf = n => n.toLocaleString('ja-JP');
const s45 = m => m.series['2045'];

document.getElementById('n2020').textContent =
  M.filter(m => m.series['2020'].support_ratio < 1).length;
document.getElementById('n2045').textContent =
  M.filter(m => s45(m).support_ratio < 1).length;
document.getElementById('denom').textContent = '（' + M.length + '自治体中）';

let sortKey = 'support_ratio', asc = true, picked = null;
const tbody = document.querySelector('#t tbody');

function draw(){
  const rows = [...M].sort((a,b) => {
    if (sortKey === 'name') return asc ? a.name.localeCompare(b.name,'ja') : b.name.localeCompare(a.name,'ja');
    const d = s45(a)[sortKey] - s45(b)[sortKey];
    return asc ? d : -d;
  });
  tbody.innerHTML = rows.map(m => {
    const s = s45(m), low = s.support_ratio < 1 ? ' class="low"' : '';
    return `<tr data-n="${m.name}"${m.name===picked?' class="on"':''}>`
      + `<td>${m.name}</td><td>${s.aging_rate.toFixed(1)}%</td>`
      + `<td${low}>${s.support_ratio.toFixed(2)}</td>`
      + `<td>${s.single_household_rate.toFixed(1)}%</td><td>${nf(s.elderly)}</td></tr>`;
  }).join('');
  document.querySelectorAll('#t thead th').forEach(th => {
    if (th.dataset.k === sortKey) th.setAttribute('aria-sort', asc ? 'ascending' : 'descending');
    else th.removeAttribute('aria-sort');
  });
}

document.querySelectorAll('#t thead th').forEach(th => th.onclick = () => {
  const k = th.dataset.k;
  if (k === sortKey) asc = !asc; else { sortKey = k; asc = (k === 'support_ratio' || k === 'name'); }
  draw();
});

tbody.onclick = e => {
  const tr = e.target.closest('tr'); if (!tr) return;
  picked = tr.dataset.n;
  const m = M.find(x => x.name === picked);
  document.getElementById('detail').innerHTML =
    `<h3>${m.name}</h3><div class="scroll"><table><thead><tr><th>年</th>`
    + `<th>高齢化率</th><th>65歳以上</th><th>昼間就業者</th><th>支え手比率</th></tr></thead><tbody>`
    + Y.map(y => { const s = m.series[String(y)];
        return `<tr><td>${y}</td><td>${s.aging_rate.toFixed(1)}%</td><td>${nf(s.elderly)}</td>`
          + `<td>${nf(s.workers)}</td>`
          + `<td${s.support_ratio<1?' class="low"':''}>${s.support_ratio.toFixed(2)}</td></tr>`;
      }).join('') + '</tbody></table></div>';
  draw();
};

document.getElementById('ex').innerHTML = DATA.excluded
  .map(e => `<li>${e.name} — ${e.missing.join('・')}が都の推計に無い</li>`).join('')
  + '<li style="list-style:none;margin-top:6px">推定で埋めていない。</li>';

draw();
</script>
</body>
</html>
"""


def main() -> int:
    if not DATA.exists():
        print("✗ data/stress_test.json が無い。先に build_dataset.py", file=sys.stderr)
        return 1
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    html = TEMPLATE.replace("__DATA__", json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"✓ {OUT.relative_to(BASE)} ({len(html):,} バイト / {len(payload['municipalities'])} 自治体)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
