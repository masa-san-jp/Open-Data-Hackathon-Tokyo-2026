---
id: T04
phase: 2
status: ready
owner: unassigned
depends_on: [T01]
files:
  - apps/silverpunk-proof-map/evidence/sources.json
  - apps/silverpunk-proof-map/evidence/claims.json
  - apps/silverpunk-proof-map/evidence/run-log.md
---

# T04 出典・主張台帳を検証する

## 目的

画面の主張を、URL を見ただけの情報と、実際に中身を開いた情報に分ける。

## やること

- 利用する公開元を `sources.json` に登録する
- URL、タイトル、提供者、取得日、対象年、粒度、形式、検証状態を記録する
- 画面で使う主張を `claims.json` に登録する
- 都民ニーズやデータ欠損に関する主張には限界・非網羅性を書く
- 未検証のソースは `not_verified` のまま残す

## 完了条件

- すべての `verified` ソースに確認方法がある
- すべての `verified` 主張からソースへたどれる
- データが存在しないことと、カタログで横並び比較できないことを区別している

