---
id: T07
phase: 3
status: ready
owner: unassigned
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
