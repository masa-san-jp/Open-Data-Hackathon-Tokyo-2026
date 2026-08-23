---
id: T04V
phase: 0
status: done
owner: agent
depends_on: [T01]
files:
  - apps/silverpunk-proof-map/scripts/verify.py
  - apps/silverpunk-proof-map/evidence/run-log.md
---

# T04V データ契約の検証スクリプト

## 目的

出典・主張台帳のタスク（T04）と独立して、Phase 1 の fixture を機械的に検査できる状態を作る。T04 のソース台帳が未完了でも、デモの入力検査を止めない。

## 実装すること

- `schema_version`、`sources`、`scenarios`、`districts` の必須構造を検査する
- 地区 ID の重複、状態値の誤り、単位・対象年の欠落を検知する
- `verified` の値に出典 ID と取得日がない場合は非ゼロ終了する
- `not_computable` の値を順位計算に使っていないことを検査する
- エラーを標準エラーに読みやすく出力し、終了コード1以上にする
- 実行結果を `evidence/run-log.md` に追記できるようにする

## やらないこと

- URL を開いただけで `verified` に変更する
- 欠損値をゼロ、平均、補間値で補完する
- UI の文章を検証なしに事実として承認する

## 受け入れ条件

```bash
cd apps/silverpunk-proof-map
python3 scripts/verify.py
```

が T01 の fixture に対して終了コード0になる。不正な状態値を一時 JSON に入れた場合は終了コード1以上になる。

## 実施記録（2026-08-23）

変更: `apps/silverpunk-proof-map/scripts/verify.py`。
検査: `python3 scripts/verify.py --phase 0` 終了コード0。`population` を意図的に `verified`（source_id なし）へ壊した一時JSONで実行し終了コード1・2件の指摘を確認。
観測: 地区ID重複、必須フィールド欠落、`verified`の出典欠如、`missing`なのに値が入っている、`not_computable`のスコアが残っている、等を検査対象にした。
残課題: なし（Phase 1 検査契約として運用開始）。
