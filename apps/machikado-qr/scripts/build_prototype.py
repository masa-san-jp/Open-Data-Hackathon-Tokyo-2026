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
 :root{--bg:#fff;--fg:#111;--mut:#5a5a5a;--line:#d4d0c8;--red:#b3261e;--blue:#0e4f7a;
  --card:#f7f6f4;--warn:#fff8e1}
 *{box-sizing:border-box}
 body{margin:0;background:var(--bg);color:var(--fg);
  font-family:"Hiragino Sans","Noto Sans JP",system-ui,sans-serif;font-size:19px;line-height:1.55}
 .wrap{max-width:520px;margin:0 auto;padding:14px 16px 48px}
 select{font-size:15px;padding:7px 10px;border:1px solid var(--line);border-radius:8px;
  background:#fff;color:var(--fg);width:100%;margin-bottom:14px}
 .here{background:var(--card);border:2px solid var(--fg);border-radius:12px;padding:16px 18px}
 .here .lb{font-size:15px;color:var(--mut)}
 .here .addr{font-size:29px;font-weight:800;line-height:1.32;margin:4px 0 8px}
 .here .meta{font-size:14px;color:var(--mut)}
 .here .meta b{font-size:18px;color:var(--fg);letter-spacing:.05em}
 h2{font-size:16px;color:var(--mut);font-weight:600;margin:24px 0 8px}
 .btns{display:grid;gap:9px}
 .btn{display:block;width:100%;text-align:left;text-decoration:none;color:var(--fg);
  background:#fff;border:2px solid var(--fg);border-radius:12px;padding:15px 17px;
  font-size:20px;font-weight:700;cursor:pointer;font-family:inherit}
 .btn .sub{display:block;font-size:14px;font-weight:400;color:var(--mut);margin-top:3px}
 .btn.ghost{border-color:var(--line);font-size:16px;font-weight:600;padding:12px 16px}
 /* 緊急は誤って押さないよう、他と離し、押しても即発信しない */
 .sos{margin-top:30px;border-top:1px solid var(--line);padding-top:16px}
 .sosrow{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px}
 .sosbtn{border:2px solid var(--line);border-radius:12px;padding:13px 8px;background:#fff;
  text-align:center;cursor:pointer;font-family:inherit;color:var(--fg)}
 .sosbtn .num{display:block;font-size:27px;font-weight:800;line-height:1.15}
 .sosbtn .cap{display:block;font-size:13px;color:var(--mut)}
 .sosbtn.p .num{color:var(--blue)} .sosbtn.f .num{color:var(--red)}
 dialog{border:3px solid var(--fg);border-radius:14px;padding:22px;max-width:420px;width:92%}
 dialog::backdrop{background:rgba(0,0,0,.5)}
 .dtitle{font-size:23px;font-weight:800;line-height:1.4}
 .dsub{font-size:15px;color:var(--mut);margin-top:8px}
 .drow{display:grid;gap:10px;margin-top:18px}
 .dgo{background:var(--red);color:#fff;border:none;border-radius:12px;padding:17px;
  font-size:22px;font-weight:800;font-family:inherit}
 .dgo.p{background:var(--blue)}
 .dno{background:#fff;border:2px solid var(--fg);border-radius:12px;padding:14px;
  font-size:18px;font-weight:700;font-family:inherit;color:var(--fg)}
 input,.sel{width:100%;font-size:19px;padding:12px;border:1px solid var(--line);
  border-radius:9px;margin-top:8px;font-family:inherit}
 #panel{margin-top:12px;background:var(--card);border-radius:12px;padding:15px 17px;display:none}
 #panel .big{font-size:21px;font-weight:700}
 #panel ul{list-style:none;margin:10px 0 0;padding:0}
 #panel li{border-top:1px solid var(--line);padding:11px 0}
 #panel li a{color:var(--fg);font-weight:700;text-decoration:none}
 #panel li .d{font-size:14px;color:var(--mut)}
 .warn{background:#fdecea;border:1px solid #dda29b;border-radius:10px;padding:15px;font-size:18px}
 footer{margin-top:30px;font-size:13px;color:var(--mut)}
 footer summary{cursor:pointer}
</style>
</head>
<body>
<div class="wrap">
 <select id="lang" aria-label="language"></select>
 <div id="app"></div>
 <footer><details><summary id="srcsum"></summary><div id="src"></div></details></footer>
</div>

<dialog id="confirm">
 <div class="dtitle" id="ctitle"></div>
 <div class="dsub" id="csub"></div>
 <div class="drow">
   <button class="dgo" id="cgo"></button>
   <button class="dno" id="cno"></button>
 </div>
</dialog>

<dialog id="reg">
 <div class="dtitle" id="rtitle"></div>
 <div class="dsub" id="rsub"></div>
 <select class="sel" id="rkind"></select>
 <input id="rname" type="text">
 <input id="rtel" type="tel" inputmode="tel" placeholder="090-0000-0000">
 <input id="rhome" type="text">
 <div class="drow">
   <button class="dgo p" id="rsave"></button>
   <button class="dno" id="rno"></button>
 </div>
</dialog>

<script>
const DATA = __DATA__;
const BY = {}; DATA.points.forEach(p => BY[p.c] = p);

const T = {
 ja:{name:"日本語",here:"現在地",mark:"目印",code:"場所番号",
  helpq:"こまったとき",call:"に電話",callsub:"登録した番号にかけます",
  reg:"連絡先を登録",regsub:"この端末の中だけに保存します",
  map:"地図を開く",mapsub:"地図アプリで現在地を開きます",
  guide:"帰り道",guidesub:"登録した住所の方向を出します",
  water:"水を飲めるところ",station:"駅",
  sos:"緊急のとき",police:"警察",fire:"救急・火事",
  cpol:"警察（110）に電話しますか",cfire:"救急・火事（119）に電話しますか",
  csub:"つながったら、この住所をそのまま読んでください。",
  go:"電話する",no:"やめる",
  rtitle:"連絡先の登録",rsub:"この端末の中だけに保存します。送りません。",
  kinds:["家族","支援の方","ホテル","職場"],
  nameph:"呼び名（例：むすめ）",homeph:"帰る場所の住所",
  save:"保存",nohome:"帰る場所が登録されていません。",
  dir:"帰る場所は",m:"メートル",km:"キロメートル",
  near:"次はここまで歩いてください",nearsub:"着いたら同じステッカーを読んでください",
  far:"遠いので歩いて帰らないでください。登録した連絡先に電話してください。",
  none:"近くに見つかりませんでした。",
  unknown:"場所がわかりません",unknownsub:"ステッカーのQRコードをもう一度読んでください。",
  src:"データの出どころ"},
 hira:{name:"にほんご（ひらがな）",here:"いま いる ところ",mark:"めじるし",code:"ばしょの ばんごう",
  helpq:"こまった とき",call:"に でんわ",callsub:"とうろく した ばんごうに かけます",
  reg:"れんらくさきを とうろく",regsub:"この でんわの なかにだけ ほぞん します",
  map:"ちずを ひらく",mapsub:"ちずアプリで いまの ばしょを ひらきます",
  guide:"かえりみち",guidesub:"とうろく した ばしょの ほうこうを だします",
  water:"みずが のめる ところ",station:"えき",
  sos:"きゅうな とき",police:"けいさつ",fire:"きゅうきゅう・かじ",
  cpol:"けいさつ（１１０）に でんわ しますか",cfire:"きゅうきゅう・かじ（１１９）に でんわ しますか",
  csub:"つながったら、この じゅうしょを そのまま よんで ください。",
  go:"でんわ する",no:"やめる",
  rtitle:"れんらくさきの とうろく",rsub:"この でんわの なかにだけ ほぞん します。おくりません。",
  kinds:["かぞく","しえんの かた","ホテル","しごとば"],
  nameph:"よびかた（れい：むすめ）",homeph:"かえる ばしょの じゅうしょ",
  save:"ほぞん",nohome:"かえる ばしょが とうろく されて いません。",
  dir:"かえる ばしょは",m:"メートル",km:"キロメートル",
  near:"つぎは ここまで あるいて ください",nearsub:"ついたら おなじ ステッカーを よんで ください",
  far:"とおいので あるいて かえらないで ください。とうろく した れんらくさきに でんわ して ください。",
  none:"ちかくに ありませんでした。",
  unknown:"ばしょが わかりません",unknownsub:"ステッカーの QRコードを もういちど よんで ください。",
  src:"データの でどころ"},
 en:{name:"English",here:"You are here",mark:"Landmark",code:"Place code",
  helpq:"If you need help",call:"",callsub:"Calls the number you saved",
  reg:"Save a contact",regsub:"Stored only on this phone",
  map:"Open the map",mapsub:"Opens this spot in your map app",
  guide:"Getting back",guidesub:"Shows the direction of the address you saved",
  water:"Drinking water",station:"Station",
  sos:"Emergency",police:"Police",fire:"Ambulance / Fire",
  cpol:"Call the police (110)?",cfire:"Call an ambulance or fire service (119)?",
  csub:"When it connects, read this address exactly as written.",
  go:"Call",no:"Cancel",
  rtitle:"Save a contact",rsub:"Stored only on this phone. Nothing is sent.",
  kinds:["Family","Support worker","Hotel","Workplace"],
  nameph:"What to call them (e.g. Anna)",homeph:"Address to return to",
  save:"Save",nohome:"No return address saved.",
  dir:"It is",m:"m",km:"km",
  near:"Walk to this place next",nearsub:"When you arrive, scan the same sticker there",
  far:"That is too far to walk. Please call the contact you saved.",
  none:"Nothing found nearby.",
  unknown:"Location unknown",unknownsub:"Please scan the QR code on the sticker again.",
  src:"Data sources"},
 zh:{name:"中文",here:"您的位置",mark:"标志物",code:"地点编号",
  helpq:"需要帮助时",call:"",callsub:"拨打已保存的号码",
  reg:"保存联系人",regsub:"仅保存在本机",
  map:"打开地图",mapsub:"在地图应用中打开此位置",
  guide:"回去的路",guidesub:"显示已保存地址的方向",
  water:"可饮用水",station:"车站",
  sos:"紧急情况",police:"警察",fire:"救护车・火警",
  cpol:"要拨打警察（110）吗？",cfire:"要拨打救护车・火警（119）吗？",
  csub:"接通后，请照原样念出此地址。",
  go:"拨打",no:"取消",
  rtitle:"保存联系人",rsub:"仅保存在本机，不会发送。",
  kinds:["家人","支援人员","酒店","单位"],
  nameph:"称呼（例：女儿）",homeph:"要返回的地址",
  save:"保存",nohome:"尚未保存返回地址。",
  dir:"方向为",m:"米",km:"公里",
  near:"请走到下一个地点",nearsub:"到达后请扫描那里相同的贴纸",
  far:"距离太远，请勿步行返回。请拨打已保存的联系人。",
  none:"附近没有找到。",
  unknown:"无法确定位置",unknownsub:"请再次扫描贴纸上的二维码。",
  src:"数据来源"},
 ko:{name:"한국어",here:"현재 위치",mark:"표지물",code:"장소 번호",
  helpq:"도움이 필요할 때",call:"",callsub:"저장한 번호로 겁니다",
  reg:"연락처 저장",regsub:"이 휴대폰에만 저장됩니다",
  map:"지도 열기",mapsub:"지도 앱에서 현재 위치를 엽니다",
  guide:"돌아가는 길",guidesub:"저장한 주소의 방향을 보여줍니다",
  water:"마실 물",station:"역",
  sos:"긴급할 때",police:"경찰",fire:"구급・화재",
  cpol:"경찰(110)에 전화할까요?",cfire:"구급・화재(119)에 전화할까요?",
  csub:"연결되면 이 주소를 그대로 읽어 주세요.",
  go:"전화",no:"취소",
  rtitle:"연락처 저장",rsub:"이 휴대폰에만 저장되며 전송하지 않습니다.",
  kinds:["가족","지원인","호텔","직장"],
  nameph:"부르는 이름 (예: 딸)",homeph:"돌아갈 주소",
  save:"저장",nohome:"돌아갈 주소가 저장되어 있지 않습니다.",
  dir:"방향은",m:"m",km:"km",
  near:"다음은 여기까지 걸어가세요",nearsub:"도착하면 그곳의 같은 스티커를 읽어 주세요",
  far:"너무 멉니다. 걸어가지 마시고 저장한 연락처로 전화해 주세요.",
  none:"근처에 없습니다.",
  unknown:"위치를 알 수 없습니다",unknownsub:"스티커의 QR 코드를 다시 읽어 주세요.",
  src:"데이터 출처"}
};
const VOICE = {ja:"ja-JP",hira:"ja-JP",en:"en-US",zh:"zh-CN",ko:"ko-KR"};
let lang = (navigator.language||"ja").slice(0,2);
if (!T[lang]) lang = "ja";

const store = {
  get(k){ try { return localStorage.getItem(k)||""; } catch(e){ return ""; } },
  set(k,v){ try { localStorage.setItem(k,v); } catch(e){} }
};

const code = new URLSearchParams(location.search).get("p");
const P = code ? BY[code] : null;

function speak(text){
  try {
    if (!window.speechSynthesis) return;
    const u = new SpeechSynthesisUtterance(text);
    u.lang = VOICE[lang]; u.rate = 0.88;
    speechSynthesis.cancel(); speechSynthesis.speak(u);
  } catch(e){}
}
function dist(a,b,c,d){
  const R=6371000, r=Math.PI/180;
  const x=(c-a)*r, y=(d-b)*r*Math.cos((a+c)/2*r);
  return Math.round(Math.sqrt(x*x+y*y)*R);
}
function bearing(a,b,c,d){
  const dy=c-a, dx=(d-b)*Math.cos(a*Math.PI/180);
  const deg=(Math.atan2(dx,dy)*180/Math.PI+360)%360;
  const w={ja:["北","北東","東","南東","南","南西","西","北西"],
           hira:["きた","きたひがし","ひがし","みなみひがし","みなみ","みなみにし","にし","きたにし"],
           en:["north","northeast","east","southeast","south","southwest","west","northwest"],
           zh:["北","东北","东","东南","南","西南","西","西北"],
           ko:["북","북동","동","남동","남","남서","서","북서"]};
  return (w[lang]||w.ja)[Math.round(deg/45)%8];
}
// 地図アプリへ「目的地」として渡す。案内は地図アプリの仕事、行き先はオープンデータの仕事
function mapUrl(lat,lon,label){
  return `geo:${lat},${lon}?q=${lat},${lon}(${encodeURIComponent(label||"")})`;
}

function render(){
  const t = T[lang];
  const sel = document.getElementById("lang");
  sel.innerHTML = Object.keys(T).map(k =>
    `<option value="${k}"${k===lang?" selected":""}>${T[k].name}</option>`).join("");
  sel.onchange = () => { lang = sel.value; render(); };

  const app = document.getElementById("app");
  document.getElementById("srcsum").textContent = t.src;
  document.getElementById("src").innerHTML =
    `${DATA.source}<br>${DATA.dest_source}<br>${DATA.note}`;

  if (!P){
    app.innerHTML = `<div class="warn"><b style="font-size:22px">${t.unknown}</b>
      <div style="margin-top:8px">${t.unknownsub}</div></div>`;
    return;
  }

  const cname = store.get("cname"), ctel = store.get("ctel");
  const callLabel = ctel
    ? (lang==="en"||lang==="zh"||lang==="ko" ? `${t.rtitle.replace(/.*/,"")}${cname}` : `${cname}${t.call}`)
    : t.reg;

  app.innerHTML = `
   <div class="here">
     <div class="lb">${t.here}</div>
     <div class="addr">${P.a}</div>
     <div class="meta">${t.mark}：${P.n}　／　${t.code} <b>${P.c}</b></div>
   </div>

   <h2>${t.helpq}</h2>
   <div class="btns">
     <button class="btn" id="bcall">${ctel ? (cname||"") + (t.call||"") : t.reg}
       <span class="sub">${ctel ? t.callsub : t.regsub}</span></button>
     <button class="btn" id="bguide">${t.guide}<span class="sub">${t.guidesub}</span></button>
     <a class="btn" href="${mapUrl(P.lat,P.lon,P.n)}">${t.map}<span class="sub">${t.mapsub}</span></a>
     ${ctel ? `<button class="btn ghost" id="breg">${t.reg}</button>` : ""}
   </div>
   <div id="panel"></div>

   <div class="sos">
     <h2 style="margin:0">${t.sos}</h2>
     <div class="sosrow">
       <button class="sosbtn p" id="b110"><span class="num">110</span><span class="cap">${t.police}</span></button>
       <button class="sosbtn f" id="b119"><span class="num">119</span><span class="cap">${t.fire}</span></button>
     </div>
   </div>`;

  document.getElementById("bcall").onclick = () => {
    const tel = store.get("ctel");
    if (!tel) return openReg();
    location.href = "tel:" + tel.replace(/[^0-9+]/g,"");
  };
  document.getElementById("bguide").onclick = showGuide;
  const br = document.getElementById("breg"); if (br) br.onclick = openReg;
  document.getElementById("b110").onclick = () => confirmCall("110", t.cpol, "p");
  document.getElementById("b119").onclick = () => confirmCall("119", t.cfire, "");

  speak(t.here + "。" + P.a);
}

// 緊急は2段階。押しただけでは発信しない
function confirmCall(num, title, cls){
  const t = T[lang], d = document.getElementById("confirm");
  document.getElementById("ctitle").textContent = title;
  document.getElementById("csub").textContent = t.csub + "　" + P.a;
  const go = document.getElementById("cgo");
  go.textContent = t.go; go.className = "dgo " + cls;
  go.onclick = () => { d.close(); location.href = "tel:" + num; };
  document.getElementById("cno").textContent = t.no;
  document.getElementById("cno").onclick = () => d.close();
  d.showModal();
}

function nearest(kind, n){
  return DATA.dest.filter(x => x.k === kind)
    .map(x => ({x, d: dist(P.lat,P.lon,x.lat,x.lon)}))
    .filter(o => o.d <= 1500).sort((a,b) => a.d - b.d).slice(0, n);
}

function showGuide(){
  const t = T[lang], g = document.getElementById("panel");
  g.style.display = "block";
  let html = "";
  const home = store.get("chome");
  if (!home){ html = `<div class="big">${t.nohome}</div>`; }
  else { html = `<div class="big">${home}</div>
     <div style="margin-top:6px;font-size:15px;color:var(--mut)">${t.nearsub}</div>`; }

  // オープンデータから行き先を出し、選ぶと地図アプリへ渡す
  for (const [kind,label] of [["water",t.water],["station",t.station]]){
    const list = nearest(kind, 2);
    if (!list.length) continue;
    html += `<ul><li style="border:0;padding-bottom:2px"><b>${label}</b></li>`
      + list.map(o => `<li><a href="${mapUrl(o.x.lat,o.x.lon,o.x.n)}">${o.x.n}</a>
          <div class="d">${o.d}${t.m}${o.x.ev==="有"?"　/ EV":""}</div></li>`).join("")
      + `</ul>`;
  }
  g.innerHTML = html;
  speak(home ? home : t.nohome);
}

function openReg(){
  const t = T[lang], d = document.getElementById("reg");
  document.getElementById("rtitle").textContent = t.rtitle;
  document.getElementById("rsub").textContent = t.rsub;
  const k = document.getElementById("rkind");
  k.innerHTML = t.kinds.map((s,i) => `<option value="${i}">${s}</option>`).join("");
  k.value = store.get("ckind") || "0";
  const nm = document.getElementById("rname");
  nm.placeholder = t.nameph; nm.value = store.get("cname");
  document.getElementById("rtel").value = store.get("ctel");
  const hm = document.getElementById("rhome");
  hm.placeholder = t.homeph; hm.value = store.get("chome");
  document.getElementById("rsave").textContent = t.save;
  document.getElementById("rno").textContent = t.no;
  d.showModal();
}
document.getElementById("rno").onclick = () => document.getElementById("reg").close();
document.getElementById("rsave").onclick = () => {
  const k = document.getElementById("rkind");
  store.set("ckind", k.value);
  store.set("cname", document.getElementById("rname").value.trim()
    || k.options[k.selectedIndex].text);
  store.set("ctel", document.getElementById("rtel").value.trim());
  store.set("chome", document.getElementById("rhome").value.trim());
  document.getElementById("reg").close();
  render();
};

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
    print(f"✓ {OUT.relative_to(BASE)} ({len(html):,} バイト / "
          f"貼付候補 {len(payload['points']):,} 点・行き先 {len(payload['dest']):,} 点)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
