---
id: T07
phase: 3
status: done
owner: agent
depends_on: [T03, T05]
files:
  - apps/silverpunk-proof-map/data/normalized/heat_disaster.json
  - apps/silverpunk-proof-map/data/gaps.json
  - apps/silverpunk-proof-map/evidence/claims.json
  - apps/silverpunk-proof-map/prototype/index.html
---

# T07 地区比較・欠損・優先度レイヤー

## 目的

地区を「危険度」や「安全度」で断定せず、公開データで確認できた範囲から、最初に現地検証する候補を比較する。

## 実装すること

- 暑熱、要支援、生活拠点を別入力として定義する
- 指標の対象年、粒度、単位を揃える
- 必須入力が検証済みの地区だけ比較用スコアを算出する
- 算出不能な地区は `not_computable` として欠損カードへ送る
- 欠損を「次に取得・現地確認するデータ」として表示する
- 式、重み、正規化範囲、限界を `claims.json` に残す

## 受け入れ条件

- 上位候補3件を根拠つきで比較できる、または入力不足時に順位を出さない
- `0` と `missing`、`not_comparable` が区別される
- スコアを避難可否・医療判断・個人の安全保証として表現していない

## フォールバック

重みや正規化範囲に合意できない場合はスコアを廃止し、指標一覧と欠損一覧で比較する。

## 実施記録（2026-08-23）

変更: `scripts/build_dataset.py`（シナリオ入力抽出・欠損集計を追加）、`data/normalized/heat_disaster.json`、`data/gaps.json`（新規生成物）、`evidence/claims.json`（スコア手法claim追加）、`prototype/index.html`（データソース切替UI追加、実データ62自治体を表示可能に）。
検査: `verify.py`（demo-fixture / proof_map.json 両方）終了コード0。ブラウザ実機確認で実データ62自治体・欠損サマリー・地区詳細の表示を確認。
不具合修正: 地区詳細の欠損項目が二重表示されるバグ（gaps配列とmetricsのmissing状態が重複）を発見し修正。9種類・558件（62×9）に正しく収束。
観測: 全62自治体でheat_disasterのdemo priorityはnot_computable（hazard_exposure・support_pointsが未取得のため）。これはフォールバック条件どおり「入力不足時に順位を出さない」を実データで実演した状態。
残課題: `heat_disaster.json`は生成のみで画面未参照。暑熱曝露・生活支援拠点の実データ取得は未着手（T05残課題のまま）。
