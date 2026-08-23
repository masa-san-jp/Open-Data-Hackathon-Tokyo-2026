---
id: T01
phase: 0
status: ready
owner: unassigned
depends_on: [T00]
files:
  - apps/silverpunk-proof-map/data/demo-fixture.json
  - apps/silverpunk-proof-map/data/README.md
---

# T01 JSON 契約とデモ fixture

## 目的

画面が実データ取得を待たずに動く、再現可能な最小入力を作る。fixture は実在値を装ったダミーにしない。

## 実装すること

- 設計仕様書 §6.2 の `schema_version`、`sources`、`scenarios`、`districts` を満たす JSON を作る
- 3地区以上の `illustrative` レコードを用意する
- `heat_disaster` シナリオを必ず含める
- `missing`、`not_verified`、`not_computable` を少なくとも1件ずつ含める
- 指標には単位、対象年、状態を持たせる
- `data/README.md` に fixture が例示であり、公式実測値ではないことを書く

## やらないこと

- 推測値を `verified` として登録する
- 欠損をゼロ、平均、補間値で埋める
- 2100年の値を公式予測として登録する

## 受け入れ条件

- JSON が標準ライブラリで読み込める
- 地区 ID が重複しない
- 3地区以上がある
- 画面に表示しても例示 fixture であることが判別できる状態値がある

## 完了時の引き渡し

変更ファイル、JSON の読み込みコマンド、地区数、意図的に含めた欠損状態をタスク末尾に追記する。
