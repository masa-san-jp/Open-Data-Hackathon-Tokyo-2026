# はしごゆ 設計仕様書

版: 1.0 ／ 2026-08-22
この文書は実装の唯一の正とする。ここに書かれていないことは実装してはならない。判断が必要な箇所は §9 未決事項に集約する。

---

## 1. 目的と範囲

### 1-1. 解く問題

銭湯は湯を客が来る前に沸かすため、**その日の費用は開店時点でほぼ確定する**。客が1人増えても費用はほとんど増えない。したがって空席のまま閉店した分はそのまま損失になる。

入浴料は物価統制令により上限が定められ、値上げで採算を取れない。需要は自家風呂の普及で構造的に減少し、25〜30年ごとに数千万円の設備更新が来る。廃業届を出すと営業許可は戻らない。

### 1-2. システムがやること

| | |
| :-- | :-- |
| 1 | 各銭湯の確定予算から**1日の必要客数**を算出する |
| 2 | 番台で来客数を計上し、必要客数との差を表示する |
| 3 | 入浴者にはしご湯ルートを提案する。2軒め以降は必要客数に届いていない湯を優先する |
| 4 | 全湯の達成状況を集計し、優先度つきの改善提案を出す |

### 1-3. やらないこと

- 決済
- 予約
- 個人アカウント（P3まで）
- 入浴料の割引（一律550円）
- 個人属性の収集

---

## 2. 利用者と権限

| ロール | 画面 | 端末 | 権限 |
| :-- | :-- | :-- | :-- |
| `guest` | はしごゆ | スマホ | 銭湯一覧の閲覧、ルート取得、来店記録の送信 |
| `owner` | 番台 | タブレット | 自店の来客数の計上、自店の予算・分析の**閲覧のみ** |
| `admin` | 管理 | PC | 全湯の閲覧、予算の編集と確定 |

**予算の編集は `admin` のみ。`owner` は変更できない。**

---

## 3. ドメインモデル

TypeScript の型定義を正とする。実装は `packages/domain/src/types.ts` に置く。

```ts
export type BathhouseId = string;      // "B001" 形式
export type ISODate = string;          // "2026-08-22"
export type ISODateTime = string;      // "2026-08-22T19:30:00+09:00"

export interface Bathhouse {
  id: BathhouseId;
  name: string;
  address: string;                     // 全文表記。地図リンクに使う
  ward: string;                        // "墨田区"
  lat: number;
  lng: number;
  hasSauna: boolean;
  openHour: number;                    // 15 = 15:00
  closeHour: number;                   // 25 = 翌1:00。24を超える値を許す
  unionMember: boolean;
  active: boolean;                     // false = 廃業済み
}

export type BudgetStatus = "draft" | "confirmed";

export interface Budget {
  bathhouseId: BathhouseId;
  fiscalYear: number;                  // 2026
  status: BudgetStatus;
  confirmedAt: ISODateTime | null;
  confirmedBy: string | null;          // "東京都浴場組合"
  operatingDays: number;               // 年間営業日数。既定 312

  // PL（すべて年額・円。price/addon のみ1人あたり）
  price: number;                       // 入浴料。統制額。既定 550
  addon: number;                       // サウナ・物販の1人あたり平均上乗せ
  annualVisitors: number;
  fuel: number;                        // 燃料・水道
  labor: number;                       // 人件費
  otherFixed: number;
  depreciation: number;
  subsidy: number;

  // BS（円）
  asset: number;                       // 建物・設備の簿価
  land: number;
  cash: number;
  debt: number;
  yearsToRenewal: number;              // 次の大規模更新までの年数
  renewalCost: number;                 // 更新見込額

  // CF（年額・円）
  loanRepayment: number;
}

export type VisitSource = "counter" | "qr" | "pos";

export interface Visit {
  id: string;
  bathhouseId: BathhouseId;
  at: ISODateTime;
  source: VisitSource;
  sessionId: string | null;            // guest の当日セッション。null = 判定不能
  sequence: number | null;             // その日そのセッションで何軒め。null = 判定不能
}

export interface DailyCount {
  bathhouseId: BathhouseId;
  date: ISODate;
  total: number;
  first: number;                       // sequence === 1
  hop: number;                         // sequence >= 2
  unknown: number;                     // sequence === null
}
```

---

## 4. 計算仕様

`packages/domain/src/calc.ts` に純関数として実装する。**副作用を持たせない。すべてユニットテストを付ける。**

### 4-1. 客単価

```ts
unitRevenue(b: Budget): number = b.price + b.addon
```

### 4-2. 年間固定費

```ts
annualFixed(b: Budget): number = b.fuel + b.labor + b.otherFixed
```

### 4-3. 更新の年間積立額

```ts
annualRenewalReserve(b: Budget): number =
  b.yearsToRenewal > 0 ? b.renewalCost / b.yearsToRenewal : b.renewalCost
```

`yearsToRenewal === 0` は「今年来る」を意味し、全額を1年で積むものとする。

### 4-4. 1日の必要客数

```ts
requiredDailyVisitors(b: Budget): number =
  Math.max(1, Math.ceil(
    (annualFixed(b) + b.loanRepayment + annualRenewalReserve(b) - b.subsidy)
    / b.operatingDays / unitRevenue(b)
  ))
```

`unitRevenue(b) <= 0` の場合は `1` を返す。

### 4-5. PL / BS / CF

```ts
annualSales(b)      = unitRevenue(b) * b.annualVisitors
operatingProfit(b)  = annualSales(b) - annualFixed(b) - b.depreciation + b.subsidy
netAssets(b)        = b.asset + b.cash - b.debt
operatingCF(b)      = operatingProfit(b) + b.depreciation
freeCash(b)         = operatingCF(b) - b.loanRepayment
reserveGap(b)       = freeCash(b) - annualRenewalReserve(b)
```

`reserveGap < 0` は「次の更新に資金が届かない」を意味する。

### 4-6. 達成率と不足率

```ts
achievementRate(today: number, required: number) = today / required
shortfallRate(today: number, required: number)   = Math.max(0, (required - today) / required)
```

### 4-7. 連続未達日数

直近日から遡り、`DailyCount.total < requiredDailyVisitors` が続いた日数。営業していない日（`total === 0` かつ休業フラグ）は連続を切らずに読み飛ばす。休業フラグは P2 で導入する。P1 では `total === 0` の日も未達として数える。

### 4-8. 移動時間

```ts
haversineKm(a, b): number                       // 標準の Haversine
walkMinutes(a, b) = Math.max(2, Math.round(haversineKm(a,b) * 13))
travelMinutes(a, b) = walkMinutes <= 18 ? walkMinutes : Math.round(walkMinutes * 0.55)
travelMode(a, b)    = walkMinutes <= 18 ? "walk" : "transit"
```

直線距離に基づく概算である。経路探索は行わない。

### 4-9. 提案スコア

```ts
const ALLOCATION_WEIGHT = 0.7;   // サーバ定数。UIから変更させない

suggestionScore(shortfall: number, minutes: number): number =
  ALLOCATION_WEIGHT * shortfall
  + (1 - ALLOCATION_WEIGHT) * (1 - Math.min(1, minutes / 35))
```

### 4-10. ルート構築

```
入力: from{lat,lng}, startHour: number, count: 1|2|3
出力: Leg[] = { bathhouse, travelMinutes, travelMode, arrivalHour }

t = startHour
current = from
visited = []
for i in 0..count-1:
    candidates = 銭湯のうち active かつ未訪問かつ
                 isOpen(y, t + travelMinutes(current,y)/60 + 0.1)
    if candidates が空: break
    pick = (i === 0)
           ? candidates を travelMinutes 昇順で並べた先頭
           : candidates を suggestionScore 降順で並べた先頭
    t += travelMinutes(current, pick) / 60
    Leg を出力（arrivalHour = t）
    t += BATHE_HOURS            // 定数 1.1（入浴+休憩）
    current = pick; visited に追加
```

**1軒めは客の近さのみで選ぶ。店側の事情を入れない。** 2軒め以降に `suggestionScore` を用いる。

```ts
isOpen(y: Bathhouse, hour: number): boolean = hour >= y.openHour && hour < y.closeHour
```

### 4-11. 改善提案

`packages/domain/src/advice.ts`。優先度 `1|2|3` を返す。条件は上から評価し、該当するものをすべて返す。

| 優先 | 条件 | 提案ID |
| :-: | :-- | :-- |
| 1 | `reserveGap < 0 && yearsToRenewal <= 3` | `RENEWAL_URGENT` |
| 1 | `reserveGap < 0` | `RENEWAL_SHORT` |
| 1 | `todayCount < required * 0.6` | `VISITORS_SHORT` |
| 2 | `addon < 100` | `ADDON_LOW` |
| 2 | `hopRate < 0.12` | `HOP_LOW` |
| 3 | `fuel / annualFixed > 0.34` | `FUEL_HIGH` |

各提案は `{ id, priority, title, reason, action }` を返す。文言は `packages/domain/src/advice.ja.ts` に分離し、計算と混ぜない。

---

## 5. API 仕様

`apps/server`。JSON。日時は ISO8601（JST）。エラーは `{ error: { code, message } }`。

| メソッド | パス | ロール | 概要 |
| :-- | :-- | :-- | :-- |
| GET | `/api/bathhouses?lat&lng&hour` | guest | 一覧。距離・営業判定つき |
| POST | `/api/route` | guest | `{lat,lng,startHour,count}` → `Leg[]` |
| POST | `/api/visits` | guest / owner | 来店記録。`{bathhouseId, source, sessionId?}` |
| GET | `/api/bathhouses/:id/today` | owner / admin | `{total, first, hop, required, achievementRate}` |
| GET | `/api/bathhouses/:id/history?days=30` | owner / admin | `DailyCount[]` |
| GET | `/api/bathhouses/:id/budget` | owner / admin | 確定予算と派生値 |
| PUT | `/api/bathhouses/:id/budget` | **admin** | 予算の更新。`status` は `draft` になる |
| POST | `/api/bathhouses/:id/budget/confirm` | **admin** | 確定。`confirmedAt` `confirmedBy` を記録 |
| GET | `/api/bathhouses/:id/advice` | owner / admin | 改善提案 |
| GET | `/api/admin/dashboard` | admin | 全湯の集計 |

`owner` が `PUT /budget` を呼んだ場合は `403 FORBIDDEN` を返す。

### セッションによるはしご判定

`sessionId` は guest 端末が当日限りで生成する UUID（日付が変わったら破棄）。同一 `sessionId` の同日 `Visit` を時刻順に並べ、`sequence` を 1 から採番する。`sessionId` が無い記録（番台の＋1）は `sequence: null` とし、`DailyCount.unknown` に計上する。

**番台画面の「1軒め／はしご」の内訳は、`unknown` を除いた既知分の比率を全体に按分して表示する。** 按分であることを画面に明示する必要はないが、API のレスポンスには `unknown` を含める。

---

## 6. 画面仕様

### 6-1. はしごゆ（guest / スマホ）

| 要素 | 仕様 |
| :-- | :-- |
| いる場所 | テキスト入力（住所）＋ 現在地ボタン。Geolocation 失敗時は入力値を保持しエラー文言を出す |
| 入る時間 | `<input type="time">`。初期値は現在時刻 |
| 軒数 | 1／2／3 |
| ルート | 各行に 連番・店名・移動手段と所要・到着時刻・営業時間・住所・地図リンク・料金 |
| 一覧 | 距離昇順。営業時間外は淡色。住所と地図リンク |
| 地図リンク | `https://www.google.com/maps/search/?api=1&query={encodeURIComponent(address)}` |

料金は一律 `550円`。**割引・バッジ・キャンペーン文言を置かない。**

### 6-2. 番台（owner / タブレット）

タブ2つ。

**番台タブ** — 目標までの残り（大）、＋1／−1、きょうの人数・目標・売上、1軒め／はしごの内訳。常時表示前提でスクロールさせない。

**経営タブ** — 今日の来客／1日の必要客数／今月累計／月末見込、直近30日の棒グラフ（破線＝必要客数）、確定予算の**読み取り専用**表示（確定日と確定者を表示）、改善提案。

### 6-3. 管理（admin / PC）

タブ2つ。

**ダッシュボード** — 参加軒数／目標到達／30日以上未達／はしご率。表は 銭湯・来客・目標・達成率・1軒め・はしご・売上・連続未達。行クリックで各湯へ。

**各湯** — 銭湯セレクタ、KPI 4つ、30日グラフ、PL/BS/CF の**編集可能**フォーム、確定ボタン、改善提案。

---

## 7. 技術構成

| | |
| :-- | :-- |
| 言語 | TypeScript（`strict: true`） |
| フロント | React 18 + Vite（マルチページ。3エントリ） |
| スタイル | 素の CSS。フレームワークを入れない |
| サーバ | Hono（Node アダプタ） |
| DB | SQLite（`better-sqlite3`）。P4 で移行検討 |
| テスト | Vitest（ドメイン）／ Playwright（E2E スモーク） |
| パッケージ管理 | pnpm workspaces |

**localStorage / sessionStorage を使用しない。** 状態はサーバまたは React state に置く。

### ディレクトリ

```
hashigoyu/
  packages/domain/          # 型・計算・提案。副作用なし
    src/types.ts
    src/calc.ts
    src/route.ts
    src/advice.ts
    src/advice.ja.ts
    test/*.test.ts
  packages/api-client/      # fetch ラッパ。型は domain を参照
  apps/server/              # Hono + SQLite
    src/index.ts
    src/routes/*.ts
    src/db/schema.sql
    src/db/seed.ts
  apps/guest/               # はしごゆ
  apps/counter/             # 番台
  apps/admin/               # 管理
  demo/                     # P0 の静的HTML（そのまま残す）
    index.html kyaku.html bandai.html kanri.html
  docs/
    spec.md plan.md AGENTS.md
```

---

## 8. 配色とタイポグラフィ

デモで確定済み。変更しない。

```css
--ai:      #12496e;   /* 湯船のタイル藍。主要面・数値 */
--ai-dark: #0b3350;
--kero:    #f5c518;   /* ケロリン桶の黄。強調・選択中 */
--shu:     #c8332c;   /* 暖簾の朱。警告・未達 */
--green:   #2f9e5e;   /* 達成 */
--tile:    #eef4f7;   /* guest / admin の背景 */
--paper:   #f7f4ec;   /* counter の背景 */
--gray:    #6d8494;
--line:    #dde5ea;
```

見出しは明朝（`"Hiragino Mincho ProN","Yu Mincho",serif`）、本文とUIはゴシック（`"Hiragino Sans","Noto Sans JP","Yu Gothic",sans-serif`）。数値は `font-variant-numeric: tabular-nums`。

---

## 9. 未決事項

**エージェントはこれらを勝手に決めてはならない。** 該当箇所に到達したらタスクを保留し、判断を求める。

| ID | 内容 | 影響 |
| :-- | :-- | :-- |
| `U1` | 管理画面の運営主体（東京都生活衛生営業指導センター／東京都浴場組合／東京都生活文化局／区） | 権限設計、データの保有者、P3の認証方式 |
| `U2` | 銭湯マスタの取得元と更新頻度 | P2 のシード、P4 の運用 |
| `U3` | 固定費の初期値レンジ。現在の値はすべて架空 | P2 で厚生労働省「生活衛生関係営業経営実態調査（公衆浴場業）」からの取得を検討 |
| `U4` | QR／POS 連携の相手先（東京型銭湯巡り、TOKYO BATHSCAPE、キャッシュレス端末ベンダ） | P3 |
| `U5` | 組合非加盟店の扱い | P2 のマスタ設計 |
| `U6` | `ALLOCATION_WEIGHT = 0.7` の妥当性 | 提案順。実データが入るまで固定 |
| `U7` | 連続未達の判定における休業日の扱い | §4-7。P2 で休業フラグを入れる |

---

## 10. データの真正性

- **架空のデータを実データとして表示してはならない。** P0・P1 のすべての画面に「銭湯名・住所・人数・金額はすべて架空のサンプルです」と明記する
- 出典が確認できない数値を画面に出さない
- §1-1 の前提として画面に出す数値は、`demo/index.html` の出典欄に記載したものに限る
