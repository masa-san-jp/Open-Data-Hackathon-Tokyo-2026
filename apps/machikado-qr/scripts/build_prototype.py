#!/usr/bin/env python3
"""points.json を埋め込んだ単体HTMLを prototype/index.html に出す。

  python3 scripts/build_prototype.py

?p=<場所コード> で場所が決まる。QRはこのURLを指す。
コードが無い／不明なときは、場所が分からないと画面に書く（推測で近い点を出さない）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "points.json"
OUT = BASE / "prototype" / "index.html"

TEMPLATE = r"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ここはどこ</title>
<style>
 :root{--bg:#fff;--fg:#111;--mut:#555;--line:#ccc;--red:#c0261a;--blue:#12507a;--card:#f6f5f3}
 *{box-sizing:border-box}
 body{margin:0;background:var(--bg);color:var(--fg);
  font-family:"Hiragino Sans","Noto Sans JP",system-ui,sans-serif;
  font-size:20px;line-height:1.6}
 .wrap{max-width:560px;margin:0 auto;padding:20px 16px 60px}
 .lang{display:flex;gap:6px;justify-content:flex-end;margin-bottom:10px}
 .lang button{font-size:15px;padding:6px 10px;border:1px solid var(--line);
  background:#fff;border-radius:6px}
 .lang button[aria-pressed=true]{background:var(--fg);color:#fff;border-color:var(--fg)}
 .here{background:var(--card);border:2px solid var(--fg);border-radius:10px;padding:18px}
 .here .lb{font-size:16px;color:var(--mut);margin-bottom:6px}
 .here .addr{font-size:30px;font-weight:800;line-height:1.35;letter-spacing:-.01em}
 .here .shop{font-size:17px;color:var(--mut);margin-top:8px}
 .here .code{margin-top:12px;font-size:16px}
 .here .code b{font-size:24px;letter-spacing:.06em}
 .sos{margin:18px 0;display:grid;grid-template-columns:1fr 1fr;gap:10px}
 .sos a{display:block;text-align:center;text-decoration:none;color:#fff;
  border-radius:10px;padding:16px 8px;font-weight:800}
 .sos .p{background:var(--blue)} .sos .f{background:var(--red)}
 .sos .num{font-size:34px;display:block;line-height:1.1}
 .sos .cap{font-size:15px;display:block;opacity:.95}
 .say{background:#fffbe8;border:1px solid #e6d38a;border-radius:8px;
  padding:12px 14px;font-size:17px;margin-bottom:18px}
 h2{font-size:19px;margin:26px 0 10px}
 .btns{display:grid;gap:10px}
 .btns button,.btns a{display:block;width:100%;text-align:left;text-decoration:none;
  color:var(--fg);background:#fff;border:2px solid var(--fg);border-radius:10px;
  padding:16px 18px;font-size:21px;font-weight:700;cursor:pointer}
 .btns .sub{display:block;font-size:15px;font-weight:400;color:var(--mut);margin-top:4px}
 dialog{border:2px solid var(--fg);border-radius:10px;padding:20px;max-width:420px;width:92%}
 dialog input{width:100%;font-size:20px;padding:12px;border:1px solid var(--line);
  border-radius:8px;margin:10px 0}
 dialog .row{display:flex;gap:8px;justify-content:flex-end}
 dialog button{font-size:17px;padding:10px 16px;border-radius:8px;border:1px solid var(--fg);background:#fff}
 #guide{margin-top:14px;background:var(--card);border-radius:10px;padding:16px;display:none}
 #guide .big{font-size:22px;font-weight:700}
 footer{margin-top:34px;border-top:1px solid var(--line);padding-top:14px;
  font-size:14px;color:var(--mut)}
 .warn{background:#fdecea;border:1px solid #e2a49d;border-radius:8px;padding:14px;font-size:17px}
</style>
</head>
<body>
<div class="wrap">
 <div class="lang">
  <button data-l="ja" aria-pressed="true">日本語</button>
  <button data-l="en">English</button>
  <button data-l="zh">中文</button>
  <button data-l="ko">한국어</button>
 </div>

 <div id="app"></div>

 <footer>
  <div id="foot"></div>
  <div style="margin-top:8px">貼付候補地の出典: 東京都総務局「都内災害時帰宅支援ステーション協力店舗一覧（令和7年3月31日）」。
  これは<b>貼る候補の名簿</b>であって、実際に貼られた場所ではない。</div>
 </footer>
</div>

<dialog id="reg">
 <div id="regtitle" style="font-weight:700;font-size:20px"></div>
 <div id="reghint" style="font-size:15px;color:#555;margin-top:6px"></div>
 <input id="tel" type="tel" inputmode="tel" placeholder="090-0000-0000">
 <input id="home" type="text" placeholder="東京都○○区○○1-2-3">
 <div class="row">
  <button id="regcancel"></button><button id="regsave"></button>
 </div>
</dialog>

<script>
const POINTS = __DATA__;
const BY = {}; POINTS.points.forEach(p => BY[p.c] = p);

const T = {
 ja:{here:"いまいる ところ",shop:"めじるし",code:"ばしょの ばんごう",
  say:"けいさつ や きゅうきゅうに でんわ したら、うえの じゅうしょを そのまま よんで ください。",
  police:"けいさつ",fire:"きゅうきゅう・かじ",lost:"かえりみち",
  call:"おうちの ひとに でんわ",callsub:"とうろく した ばんごうに かけます",
  map:"ちずを ひらく",mapsub:"ちずアプリで いまの ばしょを ひらきます",
  guide:"みちを おしえて",guidesub:"とうろく した いえの ほうこうを だします",
  reg:"おうちの ひとを とうろく",regsub:"この たんまつの なかにだけ ほぞんします",
  regt:"おうちの ひとの でんわと じゅうしょ",
  regh:"この たんまつの なかにだけ ほぞんします。おくりません。",
  save:"ほぞん",cancel:"やめる",
  nohome:"いえの じゅうしょが とうろく されて いません。",
  dir:"いえは ここから",m:"メートル",km:"キロメートル",
  near:"つぎは ここまで あるいて ください",nearsub:"ついたら おなじ ステッカーを よんで ください",
  far:"とおいので、あるいて かえるのは やめて ください。おうちの ひとに でんわ してください。",
  unknown:"ばしょが わかりません",
  unknownsub:"ステッカーの QRコードを もういちど よんで ください。"},
 en:{here:"You are here",shop:"Landmark",code:"Place code",
  say:"If you call the police or an ambulance, read the address above exactly as written.",
  police:"Police",fire:"Ambulance / Fire",lost:"Getting home",
  call:"Call my family",callsub:"Calls the number you saved",
  map:"Open the map",mapsub:"Opens this spot in your map app",
  guide:"Which way is home?",guidesub:"Shows the direction of your saved home",
  reg:"Save family contact",regsub:"Stored only on this phone",
  regt:"Family phone number and home address",
  regh:"Stored only on this phone. Nothing is sent.",
  save:"Save",cancel:"Cancel",
  nohome:"No home address saved.",
  dir:"Home is",m:"metres",km:"km",
  near:"Walk to this place next",nearsub:"When you arrive, scan the same sticker there",
  far:"That is too far to walk. Please call your family.",
  unknown:"Location unknown",
  unknownsub:"Please scan the QR code on the sticker again."},
 zh:{here:"您现在的位置",shop:"标志物",code:"地点编号",
  say:"拨打警察或救护车时，请照原样念出上面的地址。",
  police:"警察",fire:"救护车・火警",lost:"回家",
  call:"给家人打电话",callsub:"拨打已保存的号码",
  map:"打开地图",mapsub:"在地图应用中打开此位置",
  guide:"家在哪个方向",guidesub:"显示已保存住址的方向",
  reg:"保存家人联系方式",regsub:"仅保存在本机",
  regt:"家人电话与住址",regh:"仅保存在本机，不会发送。",
  save:"保存",cancel:"取消",nohome:"尚未保存住址。",
  dir:"家在",m:"米",km:"公里",
  near:"请走到下一个地点",nearsub:"到达后请扫描那里相同的贴纸",
  far:"距离太远，请不要步行回家。请给家人打电话。",
  unknown:"无法确定位置",unknownsub:"请再次扫描贴纸上的二维码。"},
 ko:{here:"현재 위치",shop:"표지물",code:"장소 번호",
  say:"경찰이나 구급차에 전화할 때, 위 주소를 그대로 읽어 주세요.",
  police:"경찰",fire:"구급・화재",lost:"집으로",
  call:"가족에게 전화",callsub:"저장한 번호로 겁니다",
  map:"지도 열기",mapsub:"지도 앱에서 현재 위치를 엽니다",
  guide:"집은 어느 쪽",guidesub:"저장한 집의 방향을 보여줍니다",
  reg:"가족 연락처 저장",regsub:"이 휴대폰에만 저장됩니다",
  regt:"가족 전화번호와 집 주소",regh:"이 휴대폰에만 저장되며 전송하지 않습니다.",
  save:"저장",cancel:"취소",nohome:"집 주소가 저장되어 있지 않습니다.",
  dir:"집은",m:"미터",km:"킬로미터",
  near:"다음은 여기까지 걸어가세요",nearsub:"도착하면 그곳의 같은 스티커를 읽어 주세요",
  far:"너무 멉니다. 걸어서 가지 마시고 가족에게 전화해 주세요.",
  unknown:"위치를 알 수 없습니다",unknownsub:"스티커의 QR 코드를 다시 읽어 주세요."}
};
const VOICE = {ja:"ja-JP",en:"en-US",zh:"zh-CN",ko:"ko-KR"};
let lang = (navigator.language||"ja").slice(0,2);
if (!T[lang]) lang = "ja";

const store = {
  get(k){ try { return localStorage.getItem(k) || ""; } catch(e){ return ""; } },
  set(k,v){ try { localStorage.setItem(k,v); } catch(e){} }
};

const code = new URLSearchParams(location.search).get("p");
const P = code ? BY[code] : null;

function speak(text){
  try {
    if (!window.speechSynthesis) return;
    const u = new SpeechSynthesisUtterance(text);
    u.lang = VOICE[lang]; u.rate = 0.9;
    speechSynthesis.cancel(); speechSynthesis.speak(u);
  } catch(e){}
}

// 2点間の距離(m)と方角
function distance(a,b,c,d){
  const R=6371000, r=Math.PI/180;
  const x=(c-a)*r, y=(d-b)*r*Math.cos((a+c)/2*r);
  return Math.round(Math.sqrt(x*x+y*y)*R);
}
function bearingWord(a,b,c,d){
  const dy=c-a, dx=(d-b)*Math.cos(a*Math.PI/180);
  const deg=(Math.atan2(dx,dy)*180/Math.PI+360)%360;
  const ja=["きた","きたひがし","ひがし","みなみひがし","みなみ","みなみにし","にし","きたにし"];
  const en=["north","northeast","east","southeast","south","southwest","west","northwest"];
  const i=Math.round(deg/45)%8;
  return lang==="ja"?ja[i]:en[i];
}

function render(){
  const t = T[lang];
  document.querySelectorAll(".lang button").forEach(b =>
    b.setAttribute("aria-pressed", b.dataset.l === lang));
  const app = document.getElementById("app");

  if (!P){
    app.innerHTML = `<div class="warn"><b style="font-size:22px">${t.unknown}</b>
      <div style="margin-top:8px">${t.unknownsub}</div></div>`;
    document.getElementById("foot").textContent = "";
    return;
  }

  app.innerHTML = `
   <div class="here">
     <div class="lb">${t.here}</div>
     <div class="addr">${P.a}</div>
     <div class="shop">${t.shop}：${P.n}</div>
     <div class="code">${t.code}　<b>${P.c}</b></div>
   </div>

   <div class="sos">
     <a class="p" href="tel:110"><span class="num">110</span><span class="cap">${t.police}</span></a>
     <a class="f" href="tel:119"><span class="num">119</span><span class="cap">${t.fire}</span></a>
   </div>
   <div class="say">${t.say}</div>

   <h2>${t.lost}</h2>
   <div class="btns">
     <button id="bcall">${t.call}<span class="sub">${t.callsub}</span></button>
     <a href="geo:${P.lat},${P.lon}?q=${P.lat},${P.lon}">${t.map}<span class="sub">${t.mapsub}</span></a>
     <button id="bguide">${t.guide}<span class="sub">${t.guidesub}</span></button>
     <button id="breg">${t.reg}<span class="sub">${t.regsub}</span></button>
   </div>
   <div id="guide"></div>`;

  document.getElementById("foot").textContent =
    `${P.m}／${POINTS.points.length.toLocaleString()} 点の候補地から`;

  document.getElementById("bcall").onclick = () => {
    const tel = store.get("tel");
    if (!tel) return openReg();
    location.href = "tel:" + tel.replace(/[^0-9+]/g,"");
  };
  document.getElementById("breg").onclick = openReg;
  document.getElementById("bguide").onclick = showGuide;

  speak(t.here + "。" + P.a);
}

function showGuide(){
  const t = T[lang], g = document.getElementById("guide");
  const hlat = parseFloat(store.get("hlat")), hlon = parseFloat(store.get("hlon"));
  g.style.display = "block";
  if (!store.get("home")){ g.innerHTML = `<div class="big">${t.nohome}</div>`; speak(t.nohome); return; }
  if (isNaN(hlat)){
    // 住所しか無い場合は方角を出せない。嘘を出さずにそう書く
    g.innerHTML = `<div class="big">${store.get("home")}</div>
      <div style="margin-top:8px">${t.nearsub}</div>`;
    return;
  }
  const d = distance(P.lat,P.lon,hlat,hlon);
  if (d > 2000){ g.innerHTML = `<div class="big">${t.far}</div>`; speak(t.far); return; }
  const dir = bearingWord(P.lat,P.lon,hlat,hlon);
  const dist = d >= 1000 ? (d/1000).toFixed(1)+t.km : d+t.m;
  // 自宅方向にある最寄りの候補地＝次に読むステッカー
  let best = null;
  for (const q of POINTS.points){
    if (q.c === P.c) continue;
    const dq = distance(P.lat,P.lon,q.lat,q.lon);
    if (dq < 40 || dq > 400) continue;
    if (distance(q.lat,q.lon,hlat,hlon) >= d) continue;
    if (!best || dq < best.d) best = {q, d: dq};
  }
  g.innerHTML = `<div class="big">${t.dir} ${dir}、${dist}</div>`
    + (best ? `<div style="margin-top:12px"><b>${t.near}</b><br>${best.q.n}<br>
        <span style="color:#555">${best.q.a}（${best.d}${t.m}）</span>
        <div style="margin-top:6px;font-size:15px;color:#555">${t.nearsub}</div></div>` : "");
  speak(`${t.dir} ${dir}、${dist}` + (best ? `。${t.near}。${best.q.n}` : ""));
}

function openReg(){
  const t = T[lang], d = document.getElementById("reg");
  document.getElementById("regtitle").textContent = t.regt;
  document.getElementById("reghint").textContent = t.regh;
  document.getElementById("regsave").textContent = t.save;
  document.getElementById("regcancel").textContent = t.cancel;
  document.getElementById("tel").value = store.get("tel");
  document.getElementById("home").value = store.get("home");
  d.showModal();
}
document.getElementById("regcancel").onclick = () => document.getElementById("reg").close();
document.getElementById("regsave").onclick = () => {
  store.set("tel", document.getElementById("tel").value.trim());
  const home = document.getElementById("home").value.trim();
  store.set("home", home);
  // 住所から緯度経度は引けない（そのデータを持っていない）。持っていない値は入れない
  document.getElementById("reg").close();
  render();
};
document.querySelectorAll(".lang button").forEach(b =>
  b.onclick = () => { lang = b.dataset.l; render(); });

render();
</script>
</body>
</html>
"""


def main() -> int:
    if not DATA.exists():
        print("✗ data/points.json が無い。先に build_points.py", file=sys.stderr)
        return 1
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    html = TEMPLATE.replace("__DATA__", json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"✓ {OUT.relative_to(BASE)} ({len(html):,} バイト / {len(payload['points']):,} 点)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
