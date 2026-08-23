---
id: T05
phase: 2
status: done
owner: agent
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

## 実施記録（2026-08-23）

変更: `scripts/fetch_sources.py`, `scripts/normalize_data.py`, `scripts/build_dataset.py`、`data/raw/ipss_tokyo_population.xlsx`（取得物）、`data/normalized/population.json`（生成物）、`data/proof_map.json`（生成物）。`scripts/verify.py` に `enforce_demo_coverage` オプションを追加（demo-fixture専用の網羅性検査を実データには適用しないよう修正）。
検査: 取得→正規化→生成の3コマンドがすべて終了コード0。`verify.py --fixture data/proof_map.json` 終了コード0。demo-fixture側の回帰と異常系検査も維持（終了コード0/1で正しい）。
観測: 実在62自治体（東京都全区市町村）を対象に population/aged_share を verified で生成。千代田区16.4%・檜原村53.1%が独立した既存アプリの固定点と一致（クロス検証）。hazard_exposure・support_points・supporter_ratio・拠点件数は全件 missing（未取得のため、demo priority は全62自治体で not_computable ＝ 正しい状態）。
残課題: `prototype/index.html` への接続はT07。暑熱曝露・生活支援拠点・支え手比率の実データ取得は未着手。
