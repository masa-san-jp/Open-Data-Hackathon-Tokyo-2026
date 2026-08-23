# SILVERPUNK PROOF MAP（実装）

高齢者・要配慮者が、猛暑や災害時でも医療・介護・避難・休憩の拠点へ到達できる生活圏を、
東京都オープンデータで比較し、最初の30日間で確かめる行動まで出す実装。

設計の原本はここではなく `docs/design/silverpunk-proof-map/` にある。差分が出たらこのディレクトリを正とする（`SPEC.md` は未作成。当面は設計ドキュメントを参照）。

- [設計仕様書](../../docs/design/silverpunk-proof-map/20260823-silverpunk-proof-map-design-spec.md)
- [実装計画](../../docs/design/silverpunk-proof-map/20260823-silverpunk-proof-map-implementation-plan.md)
- [エージェント規約（設計側）](../../docs/design/silverpunk-proof-map/AGENT.md)
- [`AGENTS.md`](./AGENTS.md) — このアプリ内でのタスク運用規約

## 起動方法

```bash
cd apps/silverpunk-proof-map
python3 -m http.server 8000
# ブラウザで http://localhost:8000/prototype/index.html を開く
```

`prototype/index.html` は `file://` で直接開いても動く（外部 CDN・API を呼ばない単体ファイル）。

## 検査コマンド

```bash
python3 scripts/verify.py
python3 scripts/verify.py --fixture data/proof_map.json --phase 0   # 実データ側の検査
```

`data/demo-fixture.json` の構造（必須フィールド、地区ID重複、`verified` の出典有無、`not_computable` の誤用）を検査する。
`--fixture` で別のJSONを指定すると、Phase 1 デモ専用の網羅性検査（`missing`/`not_verified`を必ず含む等）は外れ、
構造検査だけが動く。

## データ再生成（Phase 2、部分実装）

```bash
python3 scripts/fetch_sources.py     # IPSS「日本の地域別将来推計人口」東京都xlsxを data/raw/ に取得
python3 scripts/normalize_data.py    # 2020年実績値（総数・65歳以上人口・高齢化率）を自治体コード単位で正規化
python3 scripts/build_dataset.py     # data/proof_map.json を生成（実在62自治体、population/aged_shareがverified）
```

`scripts/normalize_data.py` は `openpyxl` に依存する（xlsxを読むため）。`pip install openpyxl` が必要。

`data/proof_map.json` は実データだが、`hazard_exposure`（暑熱・災害曝露）、`support_points`（生活支援拠点数）、
`supporter_ratio`（支え手比率）、拠点カテゴリ別件数はまだ取得しておらず、全62自治体で `missing`。
そのため `heat_disaster` シナリオの demo priority は全自治体で `not_computable`（意図した誠実な状態）。

`prototype/index.html` は画面上部の「データソース」で「例示データ（デモ）」と「実データ（Phase 2, 東京都62自治体）」を
切り替えられる（T07）。実データを選ぶと、population/aged_shareが確認済みの62自治体と、次に取得すべきデータの
集計（`data/gaps.json`）が表示される。

## Phase 1 のデモ範囲

- `heat_disaster`（猛暑・災害）シナリオ1本
- モデル地区4件の比較・並べ替え・詳細・30日パイロットカード
- すべて `data/demo-fixture.json` の例示（`illustrative`）データ。実測値ではない
- 地図は未実装（Phase 4）。ランキングとカードだけで成立させる

## 60秒デモ手順

1. `python3 -m http.server 8000` を起動し `prototype/index.html` を開く（または `file://` で直接開く）
2. 「シナリオ」欄で猛暑・災害シナリオと注意書きを見せる
3. 「地区候補」で4地区を比較し、優先度・高齢化率・支援拠点数・未確認欠損数のボタンを押して並べ替えを見せる（`算出不可` の地区が順位末尾に来ることも見せる）
4. 優先度が高いモデル地区（例: モデル地区D）のカードを押し、詳細パネルを開く
5. 「根拠を見る」タブで指標・拠点・計算式・比較対象・未確認/欠損/対象外の項目・出典を見せる
6. 「30日カード」タブで仮説・30日アクション・測定指標・中止条件・次の判断を見せる
7. 画面下部の免責文言（経路の安全を保証しない・公式情報を確認）を指し示して締める

## 未実装範囲

- 暑熱・災害曝露、生活支援拠点、支え手比率の実データ取得（Phase 2 継続）
- 地図・空間表示（T08、Phase 4）

## ディレクトリ

```text
apps/silverpunk-proof-map/
├── README.md
├── AGENTS.md
├── data/
│   ├── demo-fixture.json    # Phase 1 の再現可能な最小 fixture（例示データ）
│   ├── proof_map.json       # Phase 2 の生成物（実在62自治体、population/aged_shareがverified）
│   ├── gaps.json            # 欠損の集計（次に取得すべきデータの優先度リスト）
│   ├── README.md
│   ├── raw/                 # 取得原本（ipss_tokyo_population.xlsx）
│   └── normalized/          # 正規化済み中間データ（population.json, heat_disaster.json）
├── evidence/
│   ├── sources.json         # 候補・検証済みソースの台帳
│   ├── claims.json          # UIの主張と根拠の対応
│   └── run-log.md           # 実行証跡
├── prototype/
│   └── index.html           # 配布物。単体で開ける。デモ/実データをヘッダーで切替可能
├── scripts/
│   ├── fetch_sources.py     # IPSS人口推計xlsxの取得
│   ├── normalize_data.py    # 自治体コード単位への正規化
│   ├── build_dataset.py     # data/proof_map.json の生成
│   └── verify.py            # 受け入れ検査
└── tasks/                   # 実装タスク（設計側 tasks/ の写しではなく進捗記録）
```

既存の `apps/tokyo-aging-stress-test/` は変更していない。
