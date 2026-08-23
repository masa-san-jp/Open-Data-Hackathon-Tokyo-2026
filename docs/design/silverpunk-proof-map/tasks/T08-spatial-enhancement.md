---
id: T08
phase: 4
status: done
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

## 実施記録（2026-08-23）

実装: `data/normalized/spatial-demo.json` に例示4地区のローカルSVG模式図レイヤー（地区境界4件、4カテゴリの施設マーカー16件）を追加。`prototype/index.html` にレスポンシブSVG、地区・施設のクリック／Enter／Space選択、凡例、位置状態・出典・記録日・限界、実データ選択時の位置レイヤー未取得フォールバックを追加。全位置は `illustrative` / `not_verified` で、外部タイル・API・経路は使用しない。
検査: `python3 scripts/verify.py`、`python3 scripts/verify.py --phase 1`、標準ライブラリによる外部JSON・HTML埋め込みJSONの一致およびdemo fixtureとの地区／施設ID突合、Node `vm.Script` 構文検査、`git diff --check`、`python3 -m http.server 8765` + `curl` を実行し、すべて通過。
観測: 空間レイヤーは4/4地区ID・16/16施設IDが有効で、休憩・給水／休憩・医療／介護・避難の4カテゴリを含む。ブラウザは Chrome拡張接続とタブ列挙まで成功したが、localhost と `file://` のページ遷移が管理URLポリシーの検証不能で拒否され、実表示の目視確認は未達としてrun logに記録した。
残課題: 実在自治体の境界・施設位置は未取得。ブラウザのlocalhost許可後に、例示地図と実データ空状態、地区カード連動、390px幅、キーボード操作、コンソールエラーを目視確認する。
