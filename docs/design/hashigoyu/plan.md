# はしごゆ 実装計画

版: 1.0 ／ 2026-08-22
前提: `spec.md` を読んでいること。仕様と矛盾する実装は差し戻す。

---

## 0. フェーズ全体

| Phase | 目的 | 完了時に何ができるか | 状態 |
| :-- | :-- | :-- | :-- |
| **P0** | デモ | 静的HTML 4枚。ブラウザで開けば3画面を見せられる | **完了** |
| **P1** | 動くプロトタイプ | ドメイン計算がテスト付きで存在し、3アプリが同一のインメモリ・ストアを共有。管理で予算を変えると番台の目標とはしごゆの提案順が変わる。**サーバ不要** | **完了** |
| **P2** | 永続化と実データ | Hono + SQLite。銭湯マスタ投入。番台の＋1が保存され、翌日も残る | 未着手 |
| **P3** | 現場接続 | ロール認証、QR／POS からの自動計上、月次の改善提案の出力 | 未着手 |
| **P4** | 運用 | バックアップ、監査ログ、複数年度の予算、休業日管理 | 未着手 |

**P1 の完了だけで、デモとして提案できる状態になる。** P2 以降は運用に必要だが提案には必須ではない。

---

## 1. Phase 0 ─ デモ（完了）

成果物: `demo/index.html` `demo/kyaku.html` `demo/bandai.html` `demo/kanri.html`

**これらは削除・改変しない。** P1 以降の実装が壊れた場合の退避先として保持する。

デモ実演の順序:

1. `index.html` で前提と構造を示す
2. `kanri.html` → 各湯 → 若葉湯を選び、更新見込額と次の更新までの年数を見せる。「積立との差」が赤字であることを確認する
3. 「次の更新まで」を `1` → `10` に変えると 1日の必要客数が下がることを見せる
4. `bandai.html` で ＋1 を押し、残りが減ることを見せる
5. `kyaku.html` で時刻と軒数を変え、ルートが変わることを見せる

---

## 2. Phase 1 ─ 動くプロトタイプ

### ゴール

- ドメイン計算が `packages/domain` に純関数として存在し、Vitest が全て緑
- 3アプリが React + Vite で動く
- 共有ストアを通じて3画面が連動する
- サーバも DB も不要。`pnpm dev` で3つのポートが立つ

### タスク

各タスクは独立してレビュー可能な単位とする。`依存` が完了するまで着手しない。

---

**`T1-01` リポジトリ初期化**

- 依存: なし
- 状態: 完了
- 作るもの: `pnpm-workspace.yaml`、ルート `package.json`、`tsconfig.base.json`（`strict: true`）、`.gitignore`
- 受け入れ条件:
  - `pnpm install` が成功する
  - `pnpm -r exec tsc --noEmit` がエラー0で終わる（対象がまだ無くても可）
- 検証: `pnpm install && pnpm -r exec tsc --noEmit`

---

**`T1-02` ドメイン型定義**

- 依存: `T1-01`
- 状態: 完了
- 作るもの: `packages/domain/src/types.ts`
- 内容: `spec.md` §3 の型をそのまま実装する。**型を追加・改名しない**
- 受け入れ条件: `tsc --noEmit` が通る。spec §3 の全 interface が export されている
- 検証: `pnpm --filter domain exec tsc --noEmit`

---

**`T1-03` 計算関数**

- 依存: `T1-02`
- 状態: 完了
- 作るもの: `packages/domain/src/calc.ts`
- 内容: spec §4-1〜4-8 の全関数。**すべて純関数。日付は引数で受け取り `new Date()` を関数内で呼ばない**
- 受け入れ条件:
  - 下記のテストが全て通る（`packages/domain/test/calc.test.ts`）
  - `unitRevenue <= 0` のとき `requiredDailyVisitors` が `1` を返す
  - `yearsToRenewal === 0` のとき `annualRenewalReserve === renewalCost`
- テスト例（必ずこの値で検証する）:

  ```
  予算A: price=550 addon=180 operatingDays=312
         fuel=5400000 labor=7200000 otherFixed=2640000
         subsidy=900000 loanRepayment=2160000
         yearsToRenewal=7 renewalCost=32000000
    unitRevenue           = 730
    annualFixed           = 15240000
    annualRenewalReserve  = 32000000/7 ≈ 4571428.571
    requiredDailyVisitors = ceil((15240000+2160000+4571428.571-900000)/312/730) = 93

  予算B: 予算Aの yearsToRenewal=1 renewalCost=26000000 price=480 addon=40
         fuel=4200000 labor=4400000 otherFixed=1900000
         subsidy=500000 loanRepayment=720000
    unitRevenue           = 520
    annualFixed           = 10500000
    annualRenewalReserve  = 26000000
    requiredDailyVisitors = ceil((10500000+720000+26000000-500000)/312/520) = 227
  ```

- 検証: `pnpm --filter domain test`

---

**`T1-04` ルート構築**

- 依存: `T1-03`
- 状態: 完了
- 作るもの: `packages/domain/src/route.ts`
- 内容: spec §4-9・§4-10。`BATHE_HOURS = 1.1`、`ALLOCATION_WEIGHT = 0.7` を定数として export
- 受け入れ条件:
  - 1軒めが必ず `travelMinutes` 最小の営業中の湯になる
  - 2軒め以降が `suggestionScore` 降順で選ばれる
  - 同じ銭湯が2回出ない
  - 候補が尽きたら `count` より短い配列を返す（例外を投げない）
  - 全銭湯が営業時間外なら空配列を返す
- 検証: `pnpm --filter domain test`

---

**`T1-05` 改善提案**

- 依存: `T1-03`
- 状態: 完了
- 作るもの: `packages/domain/src/advice.ts`、`packages/domain/src/advice.ja.ts`
- 内容: spec §4-11。**計算と日本語文言を必ず別ファイルに分ける**
- 受け入れ条件:
  - `reserveGap < 0 && yearsToRenewal <= 3` で `RENEWAL_URGENT` のみが出て `RENEWAL_SHORT` は出ない
  - 返り値が `priority` 昇順で並ぶ
  - 該当なしのとき空配列
- 検証: `pnpm --filter domain test`

---

**`T1-06` モックストア**

- 依存: `T1-02`
- 状態: 完了
- 作るもの: `packages/store/src/index.ts`
- 内容: インメモリの銭湯6軒・予算6件・30日分の `DailyCount`。`subscribe(fn)` で変更を通知する最小の pub/sub。**localStorage を使わない**
- 銭湯データ: `demo/kyaku.html` の6軒（松の湯・あけぼの湯・富士見湯・鶴亀湯・若葉湯・日の出湯）をそのまま使う。**架空である旨をコメントで明記する**
- 受け入れ条件: `store.updateBudget()` を呼ぶと `subscribe` の購読者に通知が届く
- 検証: `pnpm --filter store test`

---

**`T1-07` はしごゆ（guest アプリ）**

- 依存: `T1-04`, `T1-06`
- 状態: 完了
- 作るもの: `apps/guest/`
- 内容: spec §6-1。`demo/kyaku.html` の見た目を維持したまま React で再実装する
- 受け入れ条件:
  - 時刻を変えるとルートと一覧の営業判定が変わる
  - 軒数を 1→3 に変えるとルートが伸びる
  - 現在地ボタンが Geolocation 拒否時にエラー文言を出し、クラッシュしない
  - 地図リンクが spec §6-1 の URL 形式である
  - 料金表示が一律 `550円`
- 検証: `pnpm --filter guest build && pnpm --filter guest exec tsc --noEmit`

---

**`T1-08` 番台（counter アプリ）**

- 依存: `T1-03`, `T1-05`, `T1-06`
- 状態: 完了
- 作るもの: `apps/counter/`
- 内容: spec §6-2。`demo/bandai.html` の見た目を維持
- 受け入れ条件:
  - ＋1／−1 が動き、`0` 未満にならない
  - 予算が**読み取り専用**である（`input` 要素を置かない）
  - 確定日と確定者が表示される
  - 番台タブでページがスクロールしない
  - 管理側で予算を変更すると、リロードせずに目標人数が変わる
- 検証: `pnpm --filter counter build && pnpm --filter counter exec tsc --noEmit`

---

**`T1-09` 管理（admin アプリ）**

- 依存: `T1-03`, `T1-05`, `T1-06`
- 状態: 完了
- 作るもの: `apps/admin/`
- 内容: spec §6-3。`demo/kanri.html` の見た目を維持
- 受け入れ条件:
  - PL/BS/CF を編集すると 1日の必要客数が即座に再計算される
  - ダッシュボードの行クリックで各湯に遷移する
  - 確定ボタンで `status` が `confirmed` になり、確定日時が入る
  - 30日グラフの破線が必要客数の位置に出る
- 検証: `pnpm --filter admin build && pnpm --filter admin exec tsc --noEmit`

---

**`T1-10` 連動の E2E スモーク**

- 依存: `T1-07`, `T1-08`, `T1-09`
- 状態: 完了
- 作るもの: `e2e/link.spec.ts`（Playwright）
- 内容: 管理で若葉湯の `yearsToRenewal` を 1→10 に変更 → 番台の目標人数が減ることを確認
- 受け入れ条件: テストが緑
- 検証: `pnpm e2e`

---

**`T1-11` 免責表示**

- 依存: `T1-07`, `T1-08`, `T1-09`
- 状態: 完了
- 内容: 3アプリすべてに「銭湯名・住所・人数・金額はすべて架空のサンプルです」を表示する
- 受け入れ条件: 3アプリの初期表示に文言が存在する
- 検証: `pnpm e2e`

---

### P1 の完了判定

```
pnpm install
pnpm -r exec tsc --noEmit     # エラー0
pnpm -r test                  # 全緑
pnpm -r build                 # 成功
pnpm e2e                      # 全緑
```

上記4つがすべて通り、`T1-01`〜`T1-11` が完了していること。

---

## 3. Phase 2 ─ 永続化と実データ

### タスク

| ID | 内容 | 依存 | 受け入れ条件 |
| :-- | :-- | :-- | :-- |
| `T2-01` | SQLite スキーマ（`bathhouses` `budgets` `visits` `daily_counts` `closures`） | P1完了 | `schema.sql` を流して全テーブルが作られる |
| `T2-02` | Hono サーバの雛形とヘルスチェック | `T2-01` | `GET /health` が `200 {ok:true}` |
| `T2-03` | spec §5 の全エンドポイント | `T2-02` | 各エンドポイントの成功系・失敗系にテスト |
| `T2-04` | `owner` の `PUT /budget` を `403` で拒否 | `T2-03` | テストで確認 |
| `T2-05` | `sessionId` からの `sequence` 採番 | `T2-03` | 同一セッション同日の3件が 1,2,3 になる |
| `T2-06` | `DailyCount` の日次集計（`unknown` を含む） | `T2-05` | 番台の＋1が `unknown` に入る |
| `T2-07` | `packages/api-client` の実装と、3アプリのストア差し替え | `T2-03` | UI を変えずに動く |
| `T2-08` | 銭湯マスタのシード | `T2-01` | **`U2` の判断待ち。着手前に保留する** |
| `T2-09` | 休業日フラグと §4-7 の連続未達ロジック修正 | `T2-01` | **`U7` の判断待ち** |

---

## 4. Phase 3 ─ 現場接続

| ID | 内容 | 前提 |
| :-- | :-- | :-- |
| `T3-01` | ロール認証（`guest` / `owner` / `admin`） | **`U1` の決定が必要** |
| `T3-02` | QR／POS からの来客自動計上 | **`U4` の決定が必要** |
| `T3-03` | 月次改善提案の出力（PDF または CSV） | `T3-01` |
| `T3-04` | 訪問順リスト（連続未達・積立不足で並べた当番表） | `T3-01` |
| `T3-05` | 固定費初期値の実データ置き換え | **`U3` の決定が必要** |

`T3-01` `T3-02` `T3-05` は未決事項の解決前に着手しない。

---

## 5. Phase 4 ─ 運用

| ID | 内容 |
| :-- | :-- |
| `T4-01` | 予算の年度管理と履歴 |
| `T4-02` | 監査ログ（誰がいつ予算を確定したか） |
| `T4-03` | バックアップとリストア手順 |
| `T4-04` | 稼働監視 |

---

## 6. 見積り

エージェント実行を前提とした概算。人手のレビュー時間を含まない。

| Phase | タスク数 | 想定 |
| :-- | --: | :-- |
| P1 | 11 | 1〜2日 |
| P2 | 9 | 2〜3日（未決2件を除く） |
| P3 | 5 | 未決の解決後 |
| P4 | 4 | 運用開始後 |

---

## 7. 中止・縮小の判断

| 条件 | 対応 |
| :-- | :-- |
| P1 が2日で終わらない | `T1-07` のみ完成させ、番台と管理は `demo/` の静的HTMLで見せる |
| `U1`（運営主体）が決まらない | P2 までで止める。P3 に進まない |
| 実データが取得できない | 架空データのまま提案する。**実データと偽って表示しない** |
