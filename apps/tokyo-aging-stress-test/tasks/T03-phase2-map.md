---
id: T03
phase: 2
status: blocked
owner:
depends_on: [T01]
files: prototype/index.html or apps/
---

# T03 地図に載せる（Phase 2）

**Phase 1 の比較でこの案が選ばれるまで着手しない**（オーナー判断 2026-08-23）。

要るもの: 区市町村ポリゴン（国土数値情報 行政区域データ か 東京都OD）。
`stress_test.json` の `name` と突き合わせる。名前で結合しているので表記ゆれの確認が要る
（`OPEN-ISSUES.md` A4）。将来は全国地方公共団体コードで結合するのが正しい。

塗り分けは **支え手比率**。高齢化率で塗ったものと並べて、
別の場所が濃くなるのを見せられると強い。

## 作業ログ（done にするとき追記）
