---
id: T08
phase: 4
status: ready
owner: unassigned
depends_on: [T07]
files:
  - apps/silverpunk-proof-map/data/normalized/
  - apps/silverpunk-proof-map/prototype/index.html
  - apps/silverpunk-proof-map/evidence/run-log.md
---

# T08 地図の段階的追加

## 目的

完成した Phase 1〜3 のカード・根拠・欠損表示を壊さず、位置関係を地図で追えるようにする。

## 実装すること

- ローカル SVG または GeoJSON を第一候補とする
- 地区境界、避難所、休憩・給水、医療・介護拠点を表示する
- 位置情報にも出典・取得日・状態を持たせる
- 地図が読み込めなくても一覧・詳細・根拠カードを表示する
- 経路を描く場合は「候補経路」「現地確認が必要」と表示する

## やらないこと

- 外部タイル、経路 API、リアルタイム警報を必須にする
- 地図上の表示だけで安全・避難可否を断定する

## 受け入れ条件

- 地図なしでも既存の Phase 1 デモが動く
- 地図とカードの地区 ID・施設 ID が一致する
- 位置が未検証の場合は画面上で区別できる
