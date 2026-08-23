---
id: T05
phase: 2
status: ready
owner: unassigned
depends_on: [T04, T04V]
files:
  - apps/silverpunk-proof-map/data/raw/
  - apps/silverpunk-proof-map/data/normalized/
  - apps/silverpunk-proof-map/data/proof_map.json
  - apps/silverpunk-proof-map/scripts/fetch_sources.py
  - apps/silverpunk-proof-map/scripts/normalize_data.py
  - apps/silverpunk-proof-map/scripts/build_dataset.py
---

# T05 検証済みデータの再生成

## 目的

東京都の公開データを、取得・正規化・静的 JSON 生成の順で再現可能にする。データ取得が失敗しても Phase 1 を壊さない。

## 実装すること

- 取得処理を `fetch_sources.py` に閉じ込める
- 原本を `data/raw/`、中間データを `data/normalized/` に保存する
- 自治体コードを第一キーにし、名称は表示用にする
- `build_dataset.py` で決定的に `proof_map.json` を生成する
- 取得失敗、形式変更、空ファイル、HTML ポインタを成功扱いしない
- 既存の検証済みデータを再利用する場合も元の出典を引き継ぐ

## 受け入れ条件

- 同一入力から同一の JSON を再生成できる
- 取得日時・基準日・検証状態が残る
- 失敗時に `demo-fixture.json` へ戻せる
- 取得不能な項目をゼロ、平均、手入力で補完していない

## フォールバック

403、形式変更、未検証の場合は、最後の検証済み snapshot を明示して使用する。snapshot もなければ T01 fixture を使い、未取得項目を表示する。
