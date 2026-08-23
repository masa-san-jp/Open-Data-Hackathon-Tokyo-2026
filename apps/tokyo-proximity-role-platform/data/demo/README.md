# data/demo/ — D0合成データの仮定一覧

このディレクトリのデータはすべて合成デモデータである。実在地域名・実在人数ではない。
画面（prototype/index.html）に常に `DEMO DATA / NOT FOR POLICY DECISION` を表示している。
この値をREADMEの事実説明や政策判断へ転記してはならない（AGENTS.md §5.1）。

## 生成方法

`scripts/build_demo.py` により決定論的に生成する（乱数・時刻に依存しない）。再実行しても同じ出力になる。

## 仮定一覧

- 分析単位: 250m メッシュ、合成グリッド 8列×6行（48セル）
- 基準歩行速度: 80 m/min（ADR-0003のデモ仮定）
- 各セル×機能の基準到達時間: 合成の施設仮想配置点までのユークリッド距離を基準速度で除した合成値。実道路経路ではない
- 勾配モデル: `demo-linear-v1`。補正ONで最大+40%（実測標高ではない。ADR-0003）
- 必須生活機能（色分類対象）: pharmacy / clinic / welfare / mobility_node の4機能のみ（ADR-0002）
- `food` は全セルで常に未評価（`data_quality.food = "unassessed"`）。全都カバー未確認のため（SPEC.md §5.3）
- 福祉データ未評価地帯: 4セル（col>=6 and row>=4）。灰ハッチ表示の検証用（MAP-004）
- 対象人口が基準未満（薄灰表示対象、households<3）のセル: 8セル
- 優先基準: `min_population_threshold=3`, `priority_households_threshold=8`（ADR-0004のデモ仮定）
- 高齢単身世帯数・人口は決定論的な合成式によるものであり、実在の人口統計ではない

## 未確定事項

対象地域・必須機能セット・歩行速度モデル・優先基準の正式な確定は `OPEN-ISSUES.md` を参照。
