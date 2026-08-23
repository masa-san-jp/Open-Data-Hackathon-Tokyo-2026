# IMPLEMENTATION — 東京10分生活圏・地域役割プラットフォーム

原本: [`docs/design/20260823-tokyo-proximity-role-platform/20260823-tokyo-proximity-role-platform-implementation-plan.md`](../../docs/design/20260823-tokyo-proximity-role-platform/20260823-tokyo-proximity-role-platform-implementation-plan.md)

実行時の正本は本ファイルとする。実装順序の変更は `DECISIONS.md` にADRを追加したうえで反映する。

---

作成日: 2026-08-23
対象設計: `SPEC.md`
新規アプリ配置案: `apps/tokyo-proximity-role-platform/`

## 0. 実装方針

- 地図と地域役割マッチングを別フェーズにする。
- 最初に**オフラインで動くデモ**を出す。
- デモデータと実データを混在させない。
- 実データ化は1地域から始め、出典・カバー率を検査してから対象を広げる。
- 地域役割系統は、求人掲載より前に「地域課題の作業分解」を実装する。
- AIは下書きと候補提示に限定する。
- 全フェーズをタスクDAGと受入試験で管理し、エージェントが自律実行できるようにする。

---

## 1. 推奨ディレクトリ

```text
apps/tokyo-proximity-role-platform/
├── README.md
├── SPEC.md
├── IMPLEMENTATION.md
├── AGENTS.md
├── DECISIONS.md
├── OPEN-ISSUES.md
├── Makefile
├── pyproject.toml
├── package.json                    # M1以降
├── tasks/
│   ├── index.yaml
│   ├── D00-scaffold.md
│   ├── D01-demo-data.md
│   ├── D02-demo-map-shell.md
│   ├── D03-demo-controls.md
│   ├── D04-demo-intervention.md
│   ├── D05-demo-role-card.md
│   ├── D06-demo-verify.md
│   ├── M10-data-registry.md
│   ├── M11-source-audit.md
│   ├── M12-road-elevation-pipeline.md
│   ├── M13-accessibility-engine.md
│   ├── M14-map-ui.md
│   ├── M20-coverage-expansion.md
│   ├── M30-scenario-engine.md
│   ├── R00-role-schema.md
│   ├── R01-role-generator.md
│   ├── R10-routing-rules.md
│   ├── R11-coordinator-workflow.md
│   └── R20-assisted-matching.md
├── data/
│   ├── catalog.yaml
│   ├── demo/
│   ├── raw/
│   ├── normalized/
│   ├── processed/
│   ├── methodology/
│   └── reports/
├── schemas/
│   ├── cell.schema.json
│   ├── infrastructure.schema.json
│   ├── scenario.schema.json
│   ├── role-card.schema.json
│   └── candidate-profile.schema.json
├── templates/
│   └── demo.html
├── prototype/
│   └── index.html
├── scripts/
│   ├── build_demo.py
│   ├── audit_sources.py
│   ├── normalize_sources.py
│   ├── build_network.py
│   ├── attach_elevation.py
│   ├── calculate_accessibility.py
│   ├── build_map_dataset.py
│   ├── build_prototype.py
│   ├── verify.py
│   └── screenshot.py
├── web/                            # M1以降
├── api/                            # R1以降
└── tests/
    ├── test_demo.py
    ├── test_accessibility.py
    ├── test_scenarios.py
    ├── test_role_cards.py
    └── test_routing.py
```

既存の `apps/tokyo-aging-stress-test/` は変更しない。

---

## 2. 即時デモ計画

### 2.1 4時間以内の成果物

成果物:

- `prototype/index.html`
- `docs/assets/proximity-role-demo.png`
- `data/demo/` の固定データ
- `scripts/build_demo.py`
- `scripts/verify.py`

画面機能:

1. 5/10/15分切替
2. 歩行速度切替
3. 勾配ON/OFF
4. メッシュ色の再判定
5. セル詳細
6. 生活拠点・Human Bridge・モビリティノードの仮置き
7. 改善世帯数のBefore/After
8. 地域役割カード1件の生成・編集プレビュー

### 2.2 時間配分

| 経過 | 作業 | 完了条件 |
|---:|---|---|
| 0:00–0:30 | D00: 構造・Makefile・AGENTS | `make doctor` が通る |
| 0:30–1:10 | D01: デモデータ | JSON Schema検証が通る |
| 1:10–2:00 | D02: 地図シェル | オフライン表示 |
| 2:00–2:40 | D03: 閾値・速度・勾配 | 色が条件連動 |
| 2:40–3:15 | D04: 介入シミュレーション | Before/Afterが変化 |
| 3:15–3:40 | D05: 地域役割カード | セル課題から下書き生成 |
| 3:40–4:00 | D06: 検証・スクリーンショット | `make verify-demo` が通る |

時間超過時は、地図の見栄えより次の順で残す。

1. 条件切替
2. 色変化
3. セル詳細
4. 介入Before/After
5. 地域役割カード
6. 装飾

### 2.3 デモデータの扱い

- 実在地点名を使わない
- 値は `data/demo/README.md` に仮定として列挙
- 画面上部に `DEMO DATA / NOT FOR POLICY DECISION`
- デモ結果をREADMEの事実説明へ転記しない
- 実データ化後も `?mode=demo` で再現できるよう残す

---

## 3. 地図フェーズ

## Phase M1: 1地域の実データMVP

### 目的

デモUIを、確認済みデータと再現可能な処理へ置換する。

### 推奨順序

#### M10 データレジストリ

成果物:

- `data/catalog.yaml`
- `schemas/source.schema.json`
- `scripts/audit_sources.py`
- `data/reports/source-audit.json`

検査:

- URL
- 取得日
- ライセンス
- ファイル形式
- 文字コード
- 座標・住所列
- 時点
- 対象地域
- 全域／部分カバー
- 重複
- 更新可能性

「存在確認済み」だけで `production_ready: true` にしない。

#### M11 対象地域決定

選定基準:

- 人口・世帯データが取得できる
- 薬局・診療所・福祉・交通の位置データが取得できる
- 道路と標高を取得できる
- 施設住所または座標をジオコーディングできる
- 取得元とライセンスが明確

食料データが未確定なら、M1は薬局・診療所・福祉・交通だけで実施し、食料を灰ハッチの未評価にする。

#### M12 道路・標高パイプライン

成果物:

- 対象地域の歩行ネットワーク
- 各リンクの距離・始終点標高・勾配
- `data/methodology/walking-model.yaml`
- 経路サンプル検証レポート

禁止:

- 直線距離を道路所要時間と表示
- DEMがない地点を標高0mとして処理
- 勾配モデルの出典・仮定を隠す

#### M13 アクセシビリティ計算

入力:

- 分析メッシュ
- 道路ネットワーク
- 歩行プロファイル
- 生活機能ポイント

出力:

- 各セル×各機能×各プロファイルの最短所要時間
- データ品質
- 未充足機能
- 5/10/15分の分類

受入試験:

- 速度低下で到達範囲が増えない
- 閾値拡大で充足セルが減らない
- 不明値が0分にならない
- 同一入力で再生成結果が一致

#### M14 地図UI

成果物:

- MapLibre版または静的GeoJSON版
- 5/10/15分
- 歩行プロファイル
- 勾配ON/OFF
- レイヤー
- セル詳細
- 出典・データ品質

Gate M1:

```bash
make fetch-m1
make build-m1
make verify-m1
make screenshot-m1
```

が通り、対象地域・対象機能・時点が画面に表示される。

---

## Phase M2: 対象拡張

目的:

- 複数区市町村または東京都全域へ拡張する。
- 全都カバーを先に宣言せず、カバー率から拡張判断する。

作業:

1. 自治体別データの共通スキーマ化
2. 施設分類の名寄せ
3. 全国地方公共団体コードによる結合
4. 重複施設処理
5. 更新時点の差の表示
6. 島しょ・山間部の別条件化
7. 処理時間・タイル化

Gate M2:

- `data/reports/coverage-report.md` がある
- 自治体・機能ごとのカバー率が分かる
- 未評価地域が灰ハッチで残る
- オーナーが対象範囲表記を承認する

---

## Phase M3: 改善シミュレーション

### 介入計算

#### local service point

- 任意地点へ機能を追加
- 影響セルの到達時間だけ再計算
- 改善世帯数を表示

#### Human Bridge

M3では単純化する。

```yaml
service_radius_m: 1200
available_hours_per_day: 8
average_minutes_per_case: 30
daily_capacity: 16
```

出力:

- 地理的にカバーできる世帯
- 容量上カバーできる最大件数
- 未充足残数

#### mobility node / route

入力:

- 停留点
- 徒歩接続時間
- 平均待ち時間
- 走行時間
- 乗降時間

```text
door_to_service =
  walk_to_stop
  + wait
  + ride
  + walk_from_stop
```

Gate M3:

- 介入パラメータを保存・再読込できる
- Before/Afterの差を世帯数で出す
- 仮定を画面とエクスポートに含める
- 最適化ではなく比較シミュレーションと表示する

---

## 4. 地域役割フェーズ

## Phase R0: 地域役割カード

目的:

地図上の課題を、人が実行可能な作業へ変換する。

実装:

1. 地域課題タイプを選択
2. 承認済み役割テンプレートを取得
3. AIまたはルールで下書きを生成
4. コーディネーターが編集
5. `draft / reviewed / approved` を管理

R0で個人候補は扱わない。

成果物:

- `schemas/role-card.schema.json`
- `data/role-templates.yaml`
- 地図セルからの役割カード生成UI
- PDF/JSON/CSVエクスポート

Gate R0:

- 1つの地域課題から複数の作業カードを生成できる
- 身体条件・時間・監督・報酬要否を編集できる
- 法的区分が `human_review_required`
- AI単独で `approved` にできない

---

## Phase R1: 制度ルーティング

目的:

役割カードを、既存の就労・福祉・地域参加支援へ送る候補を作る。

実装:

- ルーティングルールをYAML化
- 候補ルートと理由を表示
- 区市町村・支援機関の担当者が選択
- 案件状態を管理
- 当初はAPI連携せずCSV/メール用エクスポートでもよい

例:

```yaml
- id: route-silver
  when:
    duration_max_minutes: 240
    work_type: short_term
    supervision: low
  suggest:
    - silver_human_resources
  requires_human_review: true
```

Gate R1:

- 複数候補を提示
- 候補理由を表示
- 自動確定しない
- ルール変更履歴を残す
- 担当機関未登録の場合は「送信不可」とする

---

## Phase R2: 人間承認型マッチング

R2はハッカソンMVP外。

前提:

- プライバシー影響評価
- 利用規約・同意
- 支援機関との運用合意
- 候補者プロフィール項目の確定
- 誤推薦・差別・不利益取扱いへの異議申立て

候補照合:

### hard constraints

- 場所・移動可能範囲
- 時間
- 資格
- 作業姿勢
- 重量
- 監督・支援の有無
- 利用可能な制度ルート

### soft preferences

- 経験
- 対人役割の希望
- 頻度
- 興味
- 学習希望

出力は候補順位と理由のみ。
採否・契約・支援計画は既存機関が決定する。

---

## 5. エージェント実装タスクDAG

```text
D00
 ├─ D01 ─ D02 ─ D03 ─ D04 ─ D06
 │                         └─ D05 ─┘
 └─ M10 ─ M11 ─ M12 ─ M13 ─ M14 ─ M20 ─ M30
                                └─ R00 ─ R01 ─ R10 ─ R11 ─ R20
```

並列可能:

- D01とUI骨格
- M10とスキーマ設計
- M12とM14のモック実装
- R00とM30
- テストは各実装タスクと並列で下書き可能

同じファイルを触るタスクは並列化しない。

---

## 6. Makeターゲット

```makefile
doctor:
	python3 --version
	node --version || true

demo:
	python3 scripts/build_demo.py

serve-demo:
	python3 -m http.server 8000 --directory prototype

verify-demo:
	python3 scripts/verify.py --phase demo

fetch-m1:
	python3 scripts/audit_sources.py --phase m1

build-m1:
	python3 scripts/normalize_sources.py
	python3 scripts/build_network.py
	python3 scripts/attach_elevation.py
	python3 scripts/calculate_accessibility.py
	python3 scripts/build_map_dataset.py

verify-m1:
	pytest -q tests/test_accessibility.py
	python3 scripts/verify.py --phase m1

test-role:
	pytest -q tests/test_role_cards.py tests/test_routing.py

verify:
	$(MAKE) verify-demo
	$(MAKE) verify-m1
	$(MAKE) test-role

screenshot:
	python3 scripts/screenshot.py
```

Node未導入でもD0を実行できるようにする。
M1のReact化まではPythonと静的HTMLだけで成立させる。

---

## 7. テスト仕様

### 7.1 地図

| ID | テスト |
|---|---|
| MAP-001 | 5→10→15分で充足セル数が単調増加 |
| MAP-002 | 歩行速度低下で充足セル数が増えない |
| MAP-003 | 上り勾配補正ONで同一路線が短縮しない |
| MAP-004 | 未評価セルが赤にならない |
| MAP-005 | セル詳細の出典がデータレジストリと一致 |
| MAP-006 | 介入削除で元の状態へ戻る |
| MAP-007 | 同一条件で結果が再現する |

### 7.2 地域役割

| ID | テスト |
|---|---|
| ROLE-001 | 地域課題IDなしでは役割カードを作れない |
| ROLE-002 | 作業単位、時間、機能条件、監督、報酬要否が必須 |
| ROLE-003 | AI生成直後の状態は必ずdraft |
| ROLE-004 | 制度候補は複数許容 |
| ROLE-005 | AIがapprovedを設定すると拒否 |
| ROLE-006 | 診断名を提供者向けカードへ含めると警告 |
| ROLE-007 | hard constraint不一致候補を推薦しない |

### 7.3 UI

- 1366×768で主要操作が見える
- キーボード操作可能
- 凡例を常時表示
- デモデータと実データが視覚的に区別される
- スクリーンショット自動生成

---

## 8. デモ手順

### 60秒版

1. 「高齢者・徒歩10分・勾配ON」を表示
2. 5分へ変更し、赤・橙が増える
3. 15分へ変更し、青が増える
4. 赤セルを選択し、不足機能と高齢単身世帯数を表示
5. モビリティノードを仮置き
6. 改善世帯数を表示
7. 「地域役割に変換」を押し、導入までの乗降支援カードを表示

### 役割部分の説明

- この段階では求職者を自動マッチングしない
- 地域課題を作業へ分解し、既存支援制度へ送れる形にする
- 最終判断はコーディネーターと支援機関

---

## 9. フォールバック

| 問題 | フォールバック |
|---|---|
| 地図ライブラリで詰まる | SVGグリッドに切替 |
| 実道路計算が間に合わない | D0は事前計算済み時間を使用。直線距離とは表示しない |
| 標高データ取得が間に合わない | D0は仮想勾配、M1では勾配OFF。未実装と表示 |
| 食料データが見つからない | 食料を未評価にし、薬局・診療所・福祉・交通でM1 |
| 東京都全域結合ができない | 1地域の実データMVPに固定 |
| API実装が間に合わない | R0をブラウザ内JSON生成に限定 |
| マッチング設計が未確定 | 地域役割カードまでで停止 |

---

## 10. 完了定義

「コードを書いた」ではなく、次を満たしたとき完了とする。

1. 指定コマンドが成功
2. ブラウザで実画面を確認
3. スクリーンショットを保存
4. 出典・仮定・未評価が表示
5. タスクファイルに作業ログを追記
6. `DECISIONS.md` と `OPEN-ISSUES.md` を更新
7. 変更対象外ファイルを触っていない
8. 次タスクが着手可能な状態

---

## 11. 最初に作成するコミット

コミット1:

```text
chore(proximity-role): scaffold autonomous implementation harness
```

含めるファイル:

- `README.md`
- `SPEC.md`
- `IMPLEMENTATION.md`
- `AGENTS.md`
- `DECISIONS.md`
- `OPEN-ISSUES.md`
- `Makefile`
- `tasks/index.yaml`
- `tasks/D00-scaffold.md`
- `tasks/D01-demo-data.md`
- `tasks/D02-demo-map-shell.md`
- `tasks/D03-demo-controls.md`
- `tasks/D04-demo-intervention.md`
- `tasks/D05-demo-role-card.md`
- `tasks/D06-demo-verify.md`

コミット2以降は1タスク1コミットを原則とする。
