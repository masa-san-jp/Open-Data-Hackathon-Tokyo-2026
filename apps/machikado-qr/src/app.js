"use strict";

const DATA = window.__MACHIKADO_DATA__;
const CONFIG = window.__MACHIKADO_CONFIG__;
const BY_CODE = Object.fromEntries(DATA.points.map((point) => [point.c, point]));
const PARAMS = new URLSearchParams(window.location.search);
const IS_DEMO = PARAMS.get("demo") === "1";
const REQUESTED_CODE = PARAMS.get("p") || (IS_DEMO ? CONFIG.demo.current_place_code : "");
const CURRENT_POINT = BY_CODE[REQUESTED_CODE] || null;
const PROFILE_KEY = "machikadoQr:profile:v1";
const LANGUAGE_KEY = "machikadoQr:language:v1";

const TEXT = {
  ja: {
    name: "日本語",
    here: "現在地",
    landmark: "目印",
    code: "場所番号",
    listen: "🔊 住所を音声で聞く",
    candidateBanner: "実証デモ用の候補地データです。この場所にステッカーが設置済みであることを示しません。",
    demoBanner: "デモモードです。電話は発信されず、帰り道は実際の歩行に使えません。",
    help: "こまったとき",
    callContact: "{name}に電話",
    callSub: "登録した番号へ直接かけます",
    register: "連絡先・帰る場所を登録",
    registerSub: "この端末内だけに保存します",
    route: "帰り道を確認",
    routeSub: "登録した場所へ向かう次の地点を確認します",
    nearby: "近くの給水スポット",
    nearbySub: "検証済みデータから近い順に表示します",
    map: "現在地を地図で開く",
    mapSub: "外部の地図アプリへ現在地を渡します",
    emergency: "緊急のとき",
    police: "警察",
    fire: "救急・火事",
    confirmPolice: "警察（110）に電話しますか",
    confirmFire: "救急・火事（119）に電話しますか",
    confirmContact: "{name}に電話しますか",
    confirmCopy: "つながったら、この住所をそのまま読んでください。",
    call: "電話する",
    cancel: "やめる",
    unknown: "場所を確定できません",
    unknownSub: "ステッカーのQRコードをもう一度読み、URLの場所番号を確認してください。",
    startDemo: "サンプル地点でデモを開く",
    sources: "データの出どころと利用状態",
    statusEnabled: "表示中",
    statusDemo: "候補地としてデモ表示",
    statusQuarantined: "品質確認まで隔離",
    profileTitle: "事前登録",
    profileCopy: "こまる前に登録します。情報はこの端末のブラウザ内だけに保存し、送信しません。",
    kindLabel: "連絡先の種類",
    kinds: ["家族", "支援の方", "ホテル", "職場"],
    nameLabel: "呼び名",
    phoneLabel: "電話番号",
    homeLabel: "帰る場所の住所",
    homeCodeLabel: "帰る場所の場所番号（任意）",
    homeCodeHelp: "帰る場所の近くにある、まちかどQRの場所番号を登録します。住所だけでは方向を計算しません。",
    save: "保存",
    clear: "端末内の登録を消す",
    invalidHomeCode: "その場所番号は、このデモデータにありません。空欄にするか確認してください。",
    cleared: "端末内の登録を削除しました。",
    demoProfile: "デモ用の設定です。変更は保存されません。",
    notice: "お知らせ",
    ok: "閉じる",
    demoNoCall: "デモのため、電話は発信しません。",
    routeUnavailable: "点から点への案内は実地検証前のため、公開利用では停止しています。連絡先か地図を使ってください。",
    noHomeCode: "住所は表示できますが、場所番号がないため方向は計算しません。",
    noHome: "帰る場所が登録されていません。",
    far: "帰る場所は遠いため、歩き出さず登録した連絡先へ電話してください。",
    arrived: "帰る場所の近くです。周囲を確認し、無理に移動しないでください。",
    noWaypoint: "安全に次へ渡せる候補地点を判定できません。歩き出さず、連絡先か地図を使ってください。",
    demoWalkWarning: "実地検証前の直線距離による試算です。デモ以外の歩行には使わないでください。",
    next: "次の候補地点",
    nextSub: "着いたら、そこに設置された同じステッカーを読む想定です。",
    leg: "ここから",
    remaining: "帰る場所まで残り直線",
    openRouteMap: "地図アプリで経路を確認",
    water: "給水スポット",
    dataStale: "営業・利用状況は変わる場合があります。現地表示を確認してください。",
    nothingNearby: "1.5km以内に表示できる地点がありません。",
    meter: "m",
    demoCallTitle: "デモ動作",
    invalidPhone: "有効な電話番号が登録されていません。",
  },
  hira: {
    name: "にほんご（ひらがな）",
    here: "いま いる ところ",
    landmark: "めじるし",
    code: "ばしょの ばんごう",
    listen: "🔊 じゅうしょを きく",
    candidateBanner: "ためすための ばしょです。ここに ステッカーが はってある という いみでは ありません。",
    demoBanner: "デモです。でんわは かかりません。かえりみちは ほんとうに あるくためには つかえません。",
    help: "こまった とき",
    callContact: "{name}に でんわ",
    callSub: "とうろくした ばんごうに でんわします",
    register: "れんらくさき・かえるばしょを とうろく",
    registerSub: "この でんわの なかだけに ほぞんします",
    route: "かえりみちを たしかめる",
    routeSub: "つぎの ばしょを たしかめます",
    nearby: "ちかくの みずが のめる ところ",
    nearbySub: "ちかい じゅんに みせます",
    map: "いまの ばしょを ちずで ひらく",
    mapSub: "ちずアプリを ひらきます",
    emergency: "きゅうな とき",
    police: "けいさつ",
    fire: "きゅうきゅう・かじ",
    confirmPolice: "けいさつ（110）に でんわしますか",
    confirmFire: "きゅうきゅう・かじ（119）に でんわしますか",
    confirmContact: "{name}に でんわしますか",
    confirmCopy: "つながったら、この じゅうしょを よんでください。",
    call: "でんわする",
    cancel: "やめる",
    unknown: "ばしょが わかりません",
    unknownSub: "ステッカーの QRコードを もういちど よんでください。",
    startDemo: "ためしに ひらく",
    sources: "データの でどころ",
    statusEnabled: "つかっています",
    statusDemo: "デモだけで つかっています",
    statusQuarantined: "たしかめるまで つかいません",
    profileTitle: "まえもって とうろく",
    profileCopy: "こまる まえに とうろくします。この でんわの そとには おくりません。",
    kindLabel: "れんらくする あいて",
    kinds: ["かぞく", "しえんの かた", "ホテル", "しごとば"],
    nameLabel: "よびかた",
    phoneLabel: "でんわばんごう",
    homeLabel: "かえる ばしょの じゅうしょ",
    homeCodeLabel: "かえる ばしょの ばんごう",
    homeCodeHelp: "かえる ばしょの ちかくにある ステッカーの ばんごうです。",
    save: "ほぞん",
    clear: "とうろくを けす",
    invalidHomeCode: "その ばしょの ばんごうは ありません。",
    cleared: "とうろくを けしました。",
    demoProfile: "デモの せっていです。ほぞんしません。",
    notice: "おしらせ",
    ok: "とじる",
    demoNoCall: "デモなので でんわは かかりません。",
    routeUnavailable: "ほんとうに あるいて たしかめる までは、この あんないを つかえません。",
    noHomeCode: "じゅうしょは みせられますが、ほうこうは わかりません。",
    noHome: "かえる ばしょが とうろくされて いません。",
    far: "とおいので あるかず、とうろくした ひとに でんわしてください。",
    arrived: "かえる ばしょの ちかくです。むりに うごかないでください。",
    noWaypoint: "つぎの ばしょを あんぜんに きめられません。あるかず、でんわか ちずを つかってください。",
    demoWalkWarning: "まっすぐの きょりだけで ためした デモです。ほんとうに あるくために つかわないでください。",
    next: "つぎの ばしょ",
    nextSub: "ついたら、そこに はった おなじ ステッカーを よむ そうていです。",
    leg: "ここから",
    remaining: "かえる ばしょまで あと",
    openRouteMap: "ちずアプリで みちを たしかめる",
    water: "みずが のめる ところ",
    dataStale: "つかえる じかんは かわることが あります。げんちで たしかめてください。",
    nothingNearby: "ちかくに みせられる ばしょが ありません。",
    meter: "メートル",
    demoCallTitle: "デモ",
    invalidPhone: "でんわばんごうが とうろくされて いません。",
  },
  en: {
    name: "English",
    here: "You are here",
    landmark: "Landmark",
    code: "Place code",
    listen: "🔊 Hear this address",
    candidateBanner: "This demo uses candidate locations. It does not mean a sticker is installed here.",
    demoBanner: "Demo mode: calls are blocked and the route must not be used for real walking.",
    help: "If you need help",
    callContact: "Call {name}",
    callSub: "Calls the number saved on this device",
    register: "Save contact and return place",
    registerSub: "Stored only in this browser",
    route: "Check the way back",
    routeSub: "Checks the next known point toward your saved place",
    nearby: "Nearby drinking water",
    nearbySub: "Shows nearby points that passed the data checks",
    map: "Open this location in a map",
    mapSub: "Hands this location to an external map app",
    emergency: "Emergency",
    police: "Police",
    fire: "Ambulance / Fire",
    confirmPolice: "Call the police (110)?",
    confirmFire: "Call ambulance or fire services (119)?",
    confirmContact: "Call {name}?",
    confirmCopy: "When connected, show or read this Japanese address.",
    call: "Call",
    cancel: "Cancel",
    unknown: "Location cannot be confirmed",
    unknownSub: "Scan the sticker again and check the place code in the URL.",
    startDemo: "Open the sample demo",
    sources: "Data sources and status",
    statusEnabled: "Enabled",
    statusDemo: "Demo candidates only",
    statusQuarantined: "Quarantined pending review",
    profileTitle: "Prepare before you need help",
    profileCopy: "This information stays in this browser and is never sent.",
    kindLabel: "Contact type",
    kinds: ["Family", "Support worker", "Hotel", "Workplace"],
    nameLabel: "Name to show",
    phoneLabel: "Phone number",
    homeLabel: "Return address",
    homeCodeLabel: "Return place code (optional)",
    homeCodeHelp: "Use the code of a Machikado QR point near the return place. An address alone is not geocoded.",
    save: "Save",
    clear: "Delete saved data",
    invalidHomeCode: "That place code is not in this demo data.",
    cleared: "Saved data was deleted from this browser.",
    demoProfile: "This is a demo profile. Changes are not saved.",
    notice: "Notice",
    ok: "Close",
    demoNoCall: "Demo mode blocked the call.",
    routeUnavailable: "Point-to-point guidance is disabled for public use until field testing is complete.",
    noHomeCode: "The address can be shown, but no direction is calculated without a place code.",
    noHome: "No return place is saved.",
    far: "The return place is too far. Stay here and call your saved contact.",
    arrived: "You are near the return place. Check your surroundings and do not move if unsafe.",
    noWaypoint: "No safe next point can be determined. Stay here and use your contact or a map.",
    demoWalkWarning: "This is an untested straight-line demo. Do not use it for real walking.",
    next: "Next candidate point",
    nextSub: "The concept is to scan the same installed sticker when you arrive.",
    leg: "From here",
    remaining: "Straight-line distance remaining",
    openRouteMap: "Check the route in a map app",
    water: "Drinking water",
    dataStale: "Hours and availability may change. Check signs at the location.",
    nothingNearby: "No displayable point was found within 1.5 km.",
    meter: "m",
    demoCallTitle: "Demo action",
    invalidPhone: "No valid phone number is saved.",
  },
  zh: {
    name: "中文",
    here: "您的位置",
    landmark: "地标",
    code: "地点编号",
    listen: "🔊 收听日文地址",
    candidateBanner: "这是候选地点的演示数据，并不表示此处已安装贴纸。",
    demoBanner: "演示模式：不会拨出电话，路线不可用于实际步行。",
    help: "需要帮助时",
    callContact: "拨打{name}",
    callSub: "拨打保存在本机的号码",
    register: "保存联系人和返回地点",
    registerSub: "仅保存在本浏览器中",
    route: "查看返回方向",
    routeSub: "查看前往已保存地点的下一个候选点",
    nearby: "附近饮水点",
    nearbySub: "按距离显示通过数据检查的地点",
    map: "在地图中打开当前位置",
    mapSub: "把当前位置交给外部地图应用",
    emergency: "紧急情况",
    police: "警察",
    fire: "急救・火警",
    confirmPolice: "拨打警察（110）？",
    confirmFire: "拨打急救或火警（119）？",
    confirmContact: "拨打{name}？",
    confirmCopy: "接通后，请出示或照读这个日文地址。",
    call: "拨打",
    cancel: "取消",
    unknown: "无法确认位置",
    unknownSub: "请再次扫描贴纸，并检查网址中的地点编号。",
    startDemo: "打开示例演示",
    sources: "数据来源及状态",
    statusEnabled: "使用中",
    statusDemo: "仅用于候选地点演示",
    statusQuarantined: "确认质量前停用",
    profileTitle: "事先登记",
    profileCopy: "信息只保存在本浏览器中，不会发送。",
    kindLabel: "联系人类型",
    kinds: ["家人", "支援人员", "酒店", "单位"],
    nameLabel: "显示名称",
    phoneLabel: "电话号码",
    homeLabel: "返回地点地址",
    homeCodeLabel: "返回地点编号（可选）",
    homeCodeHelp: "登记返回地点附近的まちかどQR编号。仅有地址时不会计算方向。",
    save: "保存",
    clear: "删除本机数据",
    invalidHomeCode: "演示数据中没有这个地点编号。",
    cleared: "已删除本浏览器中的登记信息。",
    demoProfile: "这是演示设置，修改不会保存。",
    notice: "提示",
    ok: "关闭",
    demoNoCall: "演示模式不会拨出电话。",
    routeUnavailable: "点到点指引在完成实地测试前停止公开使用。",
    noHomeCode: "可以显示地址，但没有地点编号就不会计算方向。",
    noHome: "尚未保存返回地点。",
    far: "返回地点太远。请留在原地并联系已登记的人。",
    arrived: "已接近返回地点。请观察周围，不安全时不要移动。",
    noWaypoint: "无法确定安全的下一个地点。请留在原地并使用联系人或地图。",
    demoWalkWarning: "这是未经实地测试的直线距离演示，请勿用于实际步行。",
    next: "下一个候选地点",
    nextSub: "设想抵达后扫描在那里安装的同类贴纸。",
    leg: "距此处",
    remaining: "距返回地点的剩余直线距离",
    openRouteMap: "在地图应用中确认路线",
    water: "饮水点",
    dataStale: "开放时间及可用状态可能变化，请确认现场标识。",
    nothingNearby: "1.5公里内没有可显示的地点。",
    meter: "米",
    demoCallTitle: "演示操作",
    invalidPhone: "未保存有效的电话号码。",
  },
  ko: {
    name: "한국어",
    here: "현재 위치",
    landmark: "표지물",
    code: "장소 번호",
    listen: "🔊 일본어 주소 듣기",
    candidateBanner: "후보 지점의 데모 데이터이며 스티커 설치 완료를 뜻하지 않습니다.",
    demoBanner: "데모 모드입니다. 전화는 걸리지 않으며 경로는 실제 보행에 사용할 수 없습니다.",
    help: "도움이 필요할 때",
    callContact: "{name}에 전화",
    callSub: "이 기기에 저장한 번호로 전화합니다",
    register: "연락처와 돌아갈 장소 저장",
    registerSub: "이 브라우저 안에만 저장합니다",
    route: "돌아가는 방향 확인",
    routeSub: "저장한 장소 방향의 다음 후보 지점을 확인합니다",
    nearby: "가까운 식수대",
    nearbySub: "데이터 검사를 통과한 지점을 거리순으로 표시합니다",
    map: "지도에서 현재 위치 열기",
    mapSub: "외부 지도 앱으로 현재 위치를 전달합니다",
    emergency: "긴급 상황",
    police: "경찰",
    fire: "구급・화재",
    confirmPolice: "경찰(110)에 전화할까요?",
    confirmFire: "구급・화재(119)에 전화할까요?",
    confirmContact: "{name}에 전화할까요?",
    confirmCopy: "연결되면 이 일본어 주소를 보여 주거나 읽어 주세요.",
    call: "전화",
    cancel: "취소",
    unknown: "위치를 확인할 수 없습니다",
    unknownSub: "스티커를 다시 스캔하고 URL의 장소 번호를 확인해 주세요.",
    startDemo: "샘플 데모 열기",
    sources: "데이터 출처와 상태",
    statusEnabled: "사용 중",
    statusDemo: "후보 지점 데모 전용",
    statusQuarantined: "품질 확인 전 격리",
    profileTitle: "미리 등록",
    profileCopy: "정보는 이 브라우저 안에만 저장되며 전송되지 않습니다.",
    kindLabel: "연락처 종류",
    kinds: ["가족", "지원인", "호텔", "직장"],
    nameLabel: "표시할 이름",
    phoneLabel: "전화번호",
    homeLabel: "돌아갈 장소 주소",
    homeCodeLabel: "돌아갈 장소 번호(선택)",
    homeCodeHelp: "돌아갈 장소 근처의 마치카도 QR 번호를 등록합니다. 주소만으로 방향을 계산하지 않습니다.",
    save: "저장",
    clear: "저장 데이터 삭제",
    invalidHomeCode: "데모 데이터에 없는 장소 번호입니다.",
    cleared: "이 브라우저의 저장 정보를 삭제했습니다.",
    demoProfile: "데모 설정이며 변경 사항은 저장되지 않습니다.",
    notice: "안내",
    ok: "닫기",
    demoNoCall: "데모 모드에서는 전화가 걸리지 않습니다.",
    routeUnavailable: "현장 검증이 끝날 때까지 점대점 안내의 공개 사용을 중지합니다.",
    noHomeCode: "주소는 표시하지만 장소 번호가 없으면 방향을 계산하지 않습니다.",
    noHome: "돌아갈 장소가 저장되어 있지 않습니다.",
    far: "돌아갈 장소가 멉니다. 움직이지 말고 저장한 연락처에 전화하세요.",
    arrived: "돌아갈 장소 근처입니다. 주변을 확인하고 위험하면 움직이지 마세요.",
    noWaypoint: "안전한 다음 지점을 정할 수 없습니다. 움직이지 말고 연락처나 지도를 사용하세요.",
    demoWalkWarning: "현장 검증 전 직선거리 데모입니다. 실제 보행에 사용하지 마세요.",
    next: "다음 후보 지점",
    nextSub: "도착하면 설치된 같은 스티커를 다시 스캔하는 방식입니다.",
    leg: "여기서",
    remaining: "돌아갈 장소까지 남은 직선거리",
    openRouteMap: "지도 앱에서 경로 확인",
    water: "식수대",
    dataStale: "운영 시간과 이용 가능 여부는 바뀔 수 있습니다. 현장 표시를 확인하세요.",
    nothingNearby: "1.5km 안에 표시할 수 있는 지점이 없습니다.",
    meter: "m",
    demoCallTitle: "데모 동작",
    invalidPhone: "유효한 전화번호가 저장되어 있지 않습니다.",
  },
};

function safeStoredLanguage() {
  try {
    const saved = window.localStorage.getItem(LANGUAGE_KEY);
    if (saved && TEXT[saved]) return saved;
  } catch (_error) {
    // Storage can be disabled. The app still works without persistence.
  }
  const browserLanguage = (navigator.language || "ja").slice(0, 2);
  return TEXT[browserLanguage] ? browserLanguage : "ja";
}

let language = safeStoredLanguage();
let initialSpeechAttempted = false;

function text() {
  return TEXT[language] || TEXT.ja;
}

function format(template, values) {
  return Object.entries(values).reduce(
    (result, [key, value]) => result.replaceAll(`{${key}}`, String(value)),
    template,
  );
}

function element(tag, options = {}) {
  const node = document.createElement(tag);
  if (options.className) node.className = options.className;
  if (options.text !== undefined) node.textContent = options.text;
  if (options.type) node.type = options.type;
  if (options.href) node.href = options.href;
  if (options.id) node.id = options.id;
  if (options.hidden) node.hidden = true;
  if (options.onClick) node.addEventListener("click", options.onClick);
  for (const [name, value] of Object.entries(options.attributes || {})) {
    node.setAttribute(name, value);
  }
  return node;
}

function append(parent, ...children) {
  for (const child of children.flat()) {
    if (child !== null && child !== undefined) parent.append(child);
  }
  return parent;
}

function action(label, copy, onClick, secondary = false) {
  const button = element("button", {
    className: secondary ? "secondary-action" : "action",
    type: "button",
    onClick,
  });
  append(button, document.createTextNode(label));
  if (copy) append(button, element("span", { className: "action-copy", text: copy }));
  return button;
}

function actionLink(label, copy, href, secondary = false) {
  const link = element("a", {
    className: secondary ? "secondary-action" : "action",
    href,
    attributes: { rel: "external" },
  });
  append(link, document.createTextNode(label));
  if (copy) append(link, element("span", { className: "action-copy", text: copy }));
  return link;
}

function readProfile() {
  if (IS_DEMO) {
    const home = BY_CODE[CONFIG.demo.home_place_code];
    return {
      version: 1,
      kind: 0,
      name: CONFIG.demo.contact_name,
      phone: CONFIG.demo.contact_phone,
      homeAddress: home ? home.a : "",
      homeCode: CONFIG.demo.home_place_code,
    };
  }
  try {
    const parsed = JSON.parse(window.localStorage.getItem(PROFILE_KEY) || "null");
    return parsed && parsed.version === 1 ? parsed : null;
  } catch (_error) {
    return null;
  }
}

function writeProfile(profile) {
  try {
    window.localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
    return true;
  } catch (_error) {
    return false;
  }
}

function removeProfile() {
  try {
    window.localStorage.removeItem(PROFILE_KEY);
  } catch (_error) {
    // Nothing else is required. The page remains usable without persistence.
  }
}

function distanceMeters(from, to) {
  const earthRadius = 6_371_000;
  const radians = Math.PI / 180;
  const x = (to.lat - from.lat) * radians;
  const y =
    (to.lon - from.lon) *
    radians *
    Math.cos(((from.lat + to.lat) / 2) * radians);
  return Math.round(Math.sqrt(x * x + y * y) * earthRadius);
}

function mapSearchUrl(point) {
  const url = new URL("https://www.google.com/maps/search/");
  url.searchParams.set("api", "1");
  url.searchParams.set("query", `${point.lat},${point.lon}`);
  return url.toString();
}

function mapDirectionsUrl(from, to) {
  const url = new URL("https://www.google.com/maps/dir/");
  url.searchParams.set("api", "1");
  url.searchParams.set("origin", `${from.lat},${from.lon}`);
  url.searchParams.set("destination", `${to.lat},${to.lon}`);
  url.searchParams.set("travelmode", "walking");
  return url.toString();
}

function openDialog(dialog) {
  if (typeof dialog.showModal === "function") dialog.showModal();
  else dialog.setAttribute("open", "");
}

function closeDialog(dialog) {
  if (typeof dialog.close === "function") dialog.close();
  else dialog.removeAttribute("open");
}

function showNotice(copy, title = text().notice) {
  const dialog = document.getElementById("notice-dialog");
  document.getElementById("notice-title").textContent = title;
  document.getElementById("notice-copy").textContent = copy;
  document.getElementById("notice-close").textContent = text().ok;
  document.getElementById("notice-close").onclick = () => closeDialog(dialog);
  openDialog(dialog);
}

function speakLocation() {
  if (!CURRENT_POINT || !window.speechSynthesis || !window.SpeechSynthesisUtterance) return;
  window.speechSynthesis.cancel();
  const introduction = new SpeechSynthesisUtterance(text().here);
  introduction.lang = language === "hira" ? "ja-JP" : {
    ja: "ja-JP",
    en: "en-US",
    zh: "zh-CN",
    ko: "ko-KR",
  }[language];
  introduction.rate = 0.88;
  const address = new SpeechSynthesisUtterance(CURRENT_POINT.a);
  address.lang = "ja-JP";
  address.rate = 0.82;
  window.speechSynthesis.speak(introduction);
  window.speechSynthesis.speak(address);
}

function sourceStatusLabel(status) {
  return {
    enabled: text().statusEnabled,
    enabled_as_demo_candidates: text().statusDemo,
    quarantined: text().statusQuarantined,
  }[status] || status;
}

function renderSources() {
  document.getElementById("source-summary").textContent = text().sources;
  const list = document.getElementById("source-list");
  list.replaceChildren();
  for (const source of DATA.sources) {
    const item = element("div", { className: "source-item" });
    const link = element("a", {
      text: source.title,
      href: source.catalog_url,
      attributes: { rel: "external" },
    });
    append(
      item,
      link,
      element("div", {
        text: `${source.provider} / ${sourceStatusLabel(source.runtime_status)}`,
      }),
    );
    list.append(item);
  }
}

function renderUnknown(app) {
  const box = element("section", { className: "error" });
  append(
    box,
    element("div", { className: "panel-title", text: text().unknown }),
    element("p", { text: text().unknownSub }),
    actionLink(text().startDemo, "", "./demo.html", true),
  );
  app.append(box);
}

function renderLocation(app) {
  const card = element("section", { className: "location-card" });
  const metadata = element("div", { className: "location-meta" });
  append(
    metadata,
    document.createTextNode(`${text().landmark}: ${CURRENT_POINT.n} / ${text().code}: `),
    element("span", { className: "location-code", text: CURRENT_POINT.c }),
  );
  append(
    card,
    element("div", { className: "eyebrow", text: text().here }),
    element("div", { className: "address", text: CURRENT_POINT.a }),
    metadata,
    element("button", {
      className: "listen-button",
      text: text().listen,
      type: "button",
      onClick: speakLocation,
    }),
  );
  app.append(card);
}

function confirmCall(number, title, emergency = false) {
  const normalized = String(number || "").replace(/(?!^\+)[^0-9]/g, "");
  if (!IS_DEMO && !/^\+?[0-9]{3,15}$/.test(normalized)) {
    showNotice(text().invalidPhone);
    return;
  }
  const dialog = document.getElementById("confirm-dialog");
  document.getElementById("confirm-title").textContent = title;
  document.getElementById("confirm-copy").textContent =
    `${text().confirmCopy} ${CURRENT_POINT.a}`;
  const go = document.getElementById("confirm-go");
  go.textContent = IS_DEMO ? text().ok : text().call;
  go.className = emergency ? "dialog-primary emergency" : "dialog-primary";
  go.onclick = () => {
    closeDialog(dialog);
    if (IS_DEMO) showNotice(text().demoNoCall, text().demoCallTitle);
    else window.location.href = `tel:${normalized}`;
  };
  const cancel = document.getElementById("confirm-cancel");
  cancel.textContent = text().cancel;
  cancel.onclick = () => closeDialog(dialog);
  openDialog(dialog);
}

function panelBase() {
  const panel = document.getElementById("result-panel");
  panel.replaceChildren();
  panel.hidden = false;
  return panel;
}

function showGuide() {
  const panel = panelBase();
  const profile = readProfile();
  if (!profile || (!profile.homeAddress && !profile.homeCode)) {
    panel.append(element("div", { className: "panel-title", text: text().noHome }));
    return;
  }
  if (!profile.homeCode) {
    append(
      panel,
      element("h3", { className: "panel-title", text: profile.homeAddress }),
      element("p", { className: "panel-copy", text: text().noHomeCode }),
    );
    return;
  }
  const home = BY_CODE[profile.homeCode];
  if (!home) {
    panel.append(element("div", { className: "panel-title", text: text().noHomeCode }));
    return;
  }
  if (!IS_DEMO && !DATA.capabilities.waypoint_guidance_public) {
    panel.append(element("div", { className: "warning", text: text().routeUnavailable }));
    return;
  }

  const routeConfig = CONFIG.wayfinding;
  const homeDistance = distanceMeters(CURRENT_POINT, home);
  if (homeDistance > routeConfig.maximum_walk_home_m) {
    panel.append(element("div", { className: "warning", text: text().far }));
    return;
  }
  if (homeDistance <= routeConfig.minimum_leg_m) {
    panel.append(element("div", { className: "panel-title", text: text().arrived }));
    return;
  }

  const candidates = DATA.points
    .filter((point) => point.c !== CURRENT_POINT.c)
    .map((point) => ({
      point,
      leg: distanceMeters(CURRENT_POINT, point),
      remaining: distanceMeters(point, home),
    }))
    .filter(
      (candidate) =>
        candidate.leg >= routeConfig.minimum_leg_m &&
        candidate.leg <= routeConfig.maximum_leg_m &&
        homeDistance - candidate.remaining >= routeConfig.minimum_progress_m,
    )
    .sort((left, right) => left.remaining - right.remaining || left.leg - right.leg);

  if (!candidates.length) {
    panel.append(element("div", { className: "warning", text: text().noWaypoint }));
    return;
  }

  const next = candidates[0];
  append(
    panel,
    element("div", { className: "warning", text: text().demoWalkWarning }),
    element("div", { className: "eyebrow", text: text().next }),
    element("h3", { className: "panel-title", text: next.point.n }),
    element("div", { text: next.point.a }),
    element("div", { className: "location-code", text: next.point.c }),
    element("p", {
      className: "panel-copy",
      text: `${text().leg} ${next.leg}${text().meter} / ${text().remaining} ${next.remaining}${text().meter}`,
    }),
    element("p", { className: "panel-copy", text: text().nextSub }),
    actionLink(
      text().openRouteMap,
      "",
      mapDirectionsUrl(CURRENT_POINT, next.point),
      true,
    ),
  );
}

function showNearby() {
  const panel = panelBase();
  const nearest = DATA.dest
    .filter((item) => item.k === "water")
    .map((item) => ({ item, distance: distanceMeters(CURRENT_POINT, item) }))
    .filter((candidate) => candidate.distance <= 1500)
    .sort((left, right) => left.distance - right.distance)
    .slice(0, 3);
  append(
    panel,
    element("h3", { className: "panel-title", text: text().water }),
    element("p", { className: "panel-copy", text: text().dataStale }),
  );
  if (!nearest.length) {
    panel.append(element("p", { text: text().nothingNearby }));
    return;
  }
  const list = element("ul", { className: "result-list" });
  for (const result of nearest) {
    const item = element("li");
    append(
      item,
      element("a", {
        text: result.item.n,
        href: mapDirectionsUrl(CURRENT_POINT, result.item),
        attributes: { rel: "external" },
      }),
      element("div", {
        className: "result-meta",
        text: `${result.distance}${text().meter} / ${result.item.a}`,
      }),
    );
    list.append(item);
  }
  panel.append(list);
}

function openProfile() {
  const t = text();
  const profile = readProfile() || {
    version: 1,
    kind: 0,
    name: "",
    phone: "",
    homeAddress: "",
    homeCode: "",
  };
  const dialog = document.getElementById("profile-dialog");
  document.getElementById("profile-title").textContent = t.profileTitle;
  document.getElementById("profile-copy").textContent = IS_DEMO ? t.demoProfile : t.profileCopy;
  document.getElementById("kind-label").textContent = t.kindLabel;
  document.getElementById("name-label").textContent = t.nameLabel;
  document.getElementById("phone-label").textContent = t.phoneLabel;
  document.getElementById("home-label").textContent = t.homeLabel;
  document.getElementById("home-code-label").textContent = t.homeCodeLabel;
  document.getElementById("home-code-help").textContent = t.homeCodeHelp;
  const kind = document.getElementById("contact-kind");
  kind.replaceChildren(...t.kinds.map((label, index) => new Option(label, String(index))));
  kind.value = String(profile.kind || 0);
  document.getElementById("contact-name").value = profile.name || "";
  document.getElementById("contact-phone").value = profile.phone || "";
  document.getElementById("home-address").value = profile.homeAddress || "";
  document.getElementById("home-code").value = profile.homeCode || "";
  document.getElementById("profile-error").textContent = "";
  document.getElementById("profile-save").textContent = t.save;
  document.getElementById("profile-cancel").textContent = t.cancel;
  document.getElementById("profile-clear").textContent = t.clear;
  openDialog(dialog);
}

function saveProfile(event) {
  event.preventDefault();
  const homeCode = document.getElementById("home-code").value.trim();
  if (homeCode && !BY_CODE[homeCode]) {
    document.getElementById("profile-error").textContent = text().invalidHomeCode;
    return;
  }
  const profile = {
    version: 1,
    kind: Number(document.getElementById("contact-kind").value || 0),
    name: document.getElementById("contact-name").value.trim(),
    phone: document.getElementById("contact-phone").value.trim(),
    homeAddress: document.getElementById("home-address").value.trim(),
    homeCode,
  };
  closeDialog(document.getElementById("profile-dialog"));
  if (IS_DEMO) {
    showNotice(text().demoProfile);
    return;
  }
  writeProfile(profile);
  render();
}

function clearProfile() {
  closeDialog(document.getElementById("profile-dialog"));
  if (!IS_DEMO) removeProfile();
  showNotice(IS_DEMO ? text().demoProfile : text().cleared);
  if (!IS_DEMO) render();
}

function renderActions(app) {
  const t = text();
  const profile = readProfile();
  const section = element("section", { className: "section" });
  const buttons = element("div", { className: "button-list" });
  append(section, element("h2", { className: "section-title", text: t.help }), buttons);

  if (profile && profile.phone) {
    const name = profile.name || t.kinds[profile.kind || 0];
    buttons.append(
      action(
        format(t.callContact, { name }),
        t.callSub,
        () => confirmCall(profile.phone, format(t.confirmContact, { name })),
      ),
    );
  } else {
    buttons.append(action(t.register, t.registerSub, openProfile));
  }
  buttons.append(
    action(t.route, t.routeSub, showGuide),
    action(t.nearby, t.nearbySub, showNearby),
    actionLink(t.map, t.mapSub, mapSearchUrl(CURRENT_POINT)),
  );
  if (profile && profile.phone) {
    buttons.append(action(t.register, t.registerSub, openProfile, true));
  }
  section.append(element("div", { className: "panel", id: "result-panel", hidden: true }));
  app.append(section);
}

function renderEmergency(app) {
  const section = element("section", { className: "sos" });
  const grid = element("div", { className: "sos-grid" });
  const police = element("button", {
    className: "sos-button police",
    type: "button",
    onClick: () => confirmCall("110", text().confirmPolice, true),
  });
  append(
    police,
    element("span", { className: "sos-number", text: "110" }),
    element("span", { className: "sos-caption", text: text().police }),
  );
  const fire = element("button", {
    className: "sos-button fire",
    type: "button",
    onClick: () => confirmCall("119", text().confirmFire, true),
  });
  append(
    fire,
    element("span", { className: "sos-number", text: "119" }),
    element("span", { className: "sos-caption", text: text().fire }),
  );
  append(section, element("h2", { className: "section-title", text: text().emergency }), grid);
  append(grid, police, fire);
  app.append(section);
}

function render() {
  const selector = document.getElementById("lang");
  selector.replaceChildren(
    ...Object.entries(TEXT).map(([key, value]) => new Option(value.name, key)),
  );
  selector.value = language;
  selector.onchange = () => {
    language = selector.value;
    document.documentElement.lang = language === "hira" ? "ja" : language;
    try {
      window.localStorage.setItem(LANGUAGE_KEY, language);
    } catch (_error) {
      // Persistence is optional.
    }
    render();
    speakLocation();
  };
  document.documentElement.lang = language === "hira" ? "ja" : language;
  document.getElementById("demo-badge").hidden = !IS_DEMO;
  renderSources();

  const app = document.getElementById("app");
  app.replaceChildren();
  if (!CURRENT_POINT) {
    renderUnknown(app);
    return;
  }
  if (IS_DEMO) app.append(element("div", { className: "status-banner", text: text().demoBanner }));
  app.append(element("div", { className: "status-banner", text: text().candidateBanner }));
  renderLocation(app);
  renderActions(app);
  renderEmergency(app);

  if (!initialSpeechAttempted) {
    initialSpeechAttempted = true;
    window.setTimeout(speakLocation, 120);
  }
}

document.getElementById("profile-form").addEventListener("submit", saveProfile);
document.getElementById("profile-cancel").addEventListener("click", () =>
  closeDialog(document.getElementById("profile-dialog")),
);
document.getElementById("profile-clear").addEventListener("click", clearProfile);

render();
