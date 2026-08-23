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
<title>東京の働き手は、いま入れ替わっている</title>
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
<h1>東京の働き手は、いま入れ替わっている</h1>
<div class="sub">65歳以上の昼間就業者が、どこで、どれだけ増えるか（2020→2045）</div>

<div class="lead">
  <h2>東京で働く65歳以上</h2>
  <div class="big">
    <span><b id="w2020">-</b> <span class="yr">2020年</span></span>
    <span class="arrow">→</span>
    <span><b id="w2045" style="color:var(--accent)">-</b> <span class="yr">2045年</span></span>
    <span class="yr" id="wdelta"></span>
  </div>
  <p id="lead2"></p>
</div>

<div class="hint">既定は<b>増加数の多い順</b>。列の見出しを押すと並べ替わる。
<b>「就業者に占める割合」で並べ替えると、都心と郊外が入れ替わる。</b>
都心は人数が増え、郊外は割合が高くなる。増える場所と、頼りになる場所は違う。</div>

<div class="scroll">
<table id="t">
 <thead><tr>
  <th data-k="name">自治体</th>
  <th data-k="delta">増加数 2020→2045</th>
  <th data-k="elderly_workers">65歳以上就業者 2045</th>
  <th data-k="workforce_elderly_share">就業者に占める割合</th>
  <th data-k="elderly_working_rate">高齢者の就業率</th>
  <th data-k="aging_rate">高齢化率 2045</th>
 </tr></thead>
 <tbody></tbody>
</table>
</div>

<div id="detail"><p class="none">行を押すと、2020年から2045年までの推移が出ます。</p></div>

<div class="lead" style="margin-top:24px;border-left-color:var(--mut)">
  <h2>受け皿が要る規模</h2>
  <p style="color:var(--fg)">全体の就業者は<b id="allw"></b>。その中で65歳以上だけが<b id="oldw"></b>。
  <b>減っていく労働力を、高齢者の労働が埋めている。</b>
  この人たちが働き続けられる環境（移動・暑さ・仕事の割り当て）は、いま設計されていない。</p>
</div>

<footer>
 <div>65歳以上就業者 ＝ その自治体で働く65歳以上（従業地ベース。住んでいる場所ではない）。
  高齢者の就業率 ＝ 65歳以上就業者 ÷ その自治体に住む65歳以上人口。
  <b>分子は従業地、分母は常住地なので、昼間人口の流入が大きい都心では100%を超える。</b>
  参考として支え手比率（昼間就業者 ÷ 65歳以上人口）も詳細に出している。</div>
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

const sum = (y,k) => M.reduce((a,m) => a + m.series[String(y)][k], 0);
const w20 = sum(2020,'elderly_workers'), w45 = sum(2045,'elderly_workers');
const a20 = sum(2020,'workers'), a45 = sum(2045,'workers');
const pct = (a,b) => ((b/a-1)*100).toFixed(1);
document.getElementById('w2020').textContent = (w20/10000).toFixed(0) + '万人';
document.getElementById('w2045').textContent = (w45/10000).toFixed(0) + '万人';
document.getElementById('wdelta').textContent = '（+' + pct(w20,w45) + '%）';
document.getElementById('lead2').textContent =
  '同じ期間、東京の全就業者は ' + pct(a20,a45) + '% 。全体が減る中で、'
  + '高齢者の労働だけが3割増える。2045年、東京で働く人の '
  + (w45/a45*100).toFixed(1) + '% が65歳以上になる。';
document.getElementById('allw').textContent = nf(a20) + '人 → ' + nf(a45) + '人（' + pct(a20,a45) + '%）';
document.getElementById('oldw').textContent = nf(w20) + '人 → ' + nf(w45) + '人（+' + pct(w20,w45) + '%）';

const delta = m => s45(m).elderly_workers - m.series['2020'].elderly_workers;
let sortKey = 'delta', asc = false, picked = null;
const tbody = document.querySelector('#t tbody');

function draw(){
  const rows = [...M].sort((a,b) => {
    if (sortKey === 'name') return asc ? a.name.localeCompare(b.name,'ja') : b.name.localeCompare(a.name,'ja');
    const d = sortKey === 'delta' ? delta(a) - delta(b) : s45(a)[sortKey] - s45(b)[sortKey];
    return asc ? d : -d;
  });
  tbody.innerHTML = rows.map(m => {
    const s = s45(m), d = delta(m);
    return `<tr data-n="${m.name}"${m.name===picked?' class="on"':''}>`
      + `<td>${m.name}</td><td${d>0?' class="low"':''}>${d>0?'+':''}${nf(d)}</td>`
      + `<td>${nf(s.elderly_workers)}</td>`
      + `<td>${s.workforce_elderly_share.toFixed(1)}%</td>`
      + `<td>${s.elderly_working_rate.toFixed(1)}%</td>`
      + `<td>${s.aging_rate.toFixed(1)}%</td></tr>`;
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
    + `<th>65歳以上就業者</th><th>就業者に占める割合</th><th>高齢者の就業率</th>`
    + `<th>全就業者</th><th>65歳以上人口</th><th>支え手比率</th></tr></thead><tbody>`
    + Y.map(y => { const s = m.series[String(y)];
        return `<tr><td>${y}</td><td class="low">${nf(s.elderly_workers)}</td>`
          + `<td>${s.workforce_elderly_share.toFixed(1)}%</td>`
          + `<td>${s.elderly_working_rate.toFixed(1)}%</td>`
          + `<td>${nf(s.workers)}</td><td>${nf(s.elderly)}</td>`
          + `<td>${s.support_ratio.toFixed(2)}</td></tr>`;
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
