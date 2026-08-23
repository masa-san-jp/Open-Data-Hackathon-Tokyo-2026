# 暑さと災害に強い生活圏ナビ（living-zone-navi）

高齢者・要配慮者が、猛暑や災害時でも、医療・介護・避難・休憩の拠点へ安全に到達できる生活圏を、
東京都オープンデータで可視化する。

出典企画: [都民ニーズに近づけるハッカソンテーマの推奨案](../../planning/20260823-tokyo-resident-needs-aligned-hackathon-theme.md)

## このディレクトリの読み順

| 順 | ファイル | 内容 |
| :-- | :-- | :-- |
| 1 | [`AGENT.md`](AGENT.md) | **エージェントは必ずここから**。作業規約・完了条件・禁止事項 |
| 2 | [`20260823-design-spec.md`](20260823-design-spec.md) | 設計仕様書（画面・データ・処理・スコープ外） |
| 3 | [`20260823-implementation-plan.md`](20260823-implementation-plan.md) | 実装計画（フェーズ・時間配分・フォールバック） |
| 4 | [`tasks/`](tasks/) | 実装タスク（T01〜T06、status 付き） |

## 実装先

コードは **`apps/living-zone-navi/`** に置く（このディレクトリには置かない）。
姉妹アプリ `apps/tokyo-aging-stress-test/` と同じ構成（`scripts/` `data/` `prototype/`）に従う。

## いま何ができるか

- Phase 0 完了時点で `prototype/index.html` をブラウザで開けばデモできる（**常にデモ可能な main を維持する**）
- フェーズの進捗は各タスクファイルの `status:` 行が正
