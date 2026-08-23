# SILVERPUNK PROOF MAP

高齢者・要配慮者が、猛暑や災害時でも、医療・介護・避難・休憩の拠点へ到達できる生活圏を東京都オープンデータで可視化し、最初に実証する地区と次の30日間の行動を決めるためのプロジェクト設計。

## このディレクトリの位置づけ

このディレクトリは、実装者がそのままコードを書き始められるように、画面、データ、処理、工程、エージェント運用を一つの実装契約にまとめる場所である。実装コードは将来 `apps/silverpunk-proof-map/` に置く。

## 読む順番

1. [`AGENT.md`](./AGENT.md) — 自律実装エージェントの作業規約
2. [`20260823-silverpunk-proof-map-design-spec.md`](./20260823-silverpunk-proof-map-design-spec.md) — 何を作るか、データ契約、画面、完了条件
3. [`20260823-silverpunk-proof-map-implementation-plan.md`](./20260823-silverpunk-proof-map-implementation-plan.md) — フェーズ、タスク、時間配分、フォールバック
4. [`tasks/`](./tasks/) — 1タスク＝1成果物の実装指示

## 最初に成立させるデモ

実装後の Phase 1 デモは、`prototype/index.html` をブラウザで開くだけで動く。外部 CDN、API キー、ログイン、バックエンドを要求しない。

1. 「猛暑ストレス」シナリオを選ぶ
2. 高齢者・要配慮者にとって支援が届きにくい地区候補を比較する
3. 1地区を選び、使ったデータ、計算できない項目、次の30日間の実証アクションを見る

地図が未実装でも、ランキング、根拠、欠損、アクションカードが画面に出れば Phase 1 は成立とする。地図は Phase 4 の段階的拡張であり、最初のデモをブロックしない。

## 関連資料

- [都民ニーズに近づけるハッカソンテーマの推奨案](../../planning/20260823-tokyo-resident-needs-aligned-hackathon-theme.md)
- [公式「都民の声」テーマとの照合](../../planning/20260823-official-citizen-issues-alignment.md)
- [ハッカソンで取り組む具体的課題の絞り込み](../../proposal/20260822-hackathon-tasks-selection.md)
- [拾っておくデータ一覧](../../research/data/20260823-datasets-to-pick-up.md)

## 状態

| 項目 | 状態 |
| :-- | :-- |
| 設計仕様書 | 作成済み |
| 実装計画 | 作成済み |
| 自律実装用 `AGENT.md` | 作成済み |
| アプリ実装（Phase 1 最短経路 T00→T01→T02→T03→T06） | 完了。`apps/silverpunk-proof-map/` で `python3 scripts/verify.py` と `prototype/index.html` のデモが動く |
| T04（出典・主張台帳）/ T05（データ再生成）/ T07（比較・優先度レイヤー拡張）/ T08（地図） | 未着手 |
