# OPEN-ISSUES — 未決事項

`SPEC.md` §9「未確定事項」と、D0実装中に生じた未決事項をここに記録する。
推測で埋めてはならない。該当したら `needs-human` として実装を止める。

---

## SPEC.md §9 由来（実装前に確定または明示する）

1. **MVPの対象地域** — **確定（2026-08-23、オーナー承認）: 青梅市**（ADR-0007）。
   `clinic`（医療機関138件）・`welfare`（介護サービス事業所161件）・人口統計（地区別）はライセンス明確・
   ジオコーディング済みのデータを確認できた。`pharmacy`・`mobility_node`（バス停）はデータ未発見のため、
   M1初期は未評価扱いとする（ADR-0008）。別出典が見つかり次第、対象機能を拡張する。
2. **近隣生活機能の必須集合** — D0ではADR-0002によりデモ仮定として `pharmacy/clinic/welfare/mobility_node` の4つに限定。`food` は常に未評価、`toilet_rest`/`activity` はD0未実装。青梅市の実データ監査の結果、M1初期は`clinic`/`welfare`の2機能のみが評価可能で、`pharmacy`/`mobility_node`も未評価扱いとする（ADR-0008）。別出典が見つかれば拡張する。
3. **食料品店データの取得元** — needs-human。`SPEC.md` §5.3「東京都全域を覆うODは未確認」のまま。
4. **道路ネットワークの取得元とライセンス** — needs-human。M12で確定する。
5. **標高データの範囲・解像度** — needs-human。M12で確定する。DEM取得・ライセンス・処理検証が未完了。
6. **高齢者向け勾配補正モデル** — needs-human。D0はADR-0003の合成係数（線形0.4倍、デモ仮定と明示）を使用。実測モデルではない。
7. **優先対象世帯数の基準** — needs-human。D0はADR-0004の合成閾値（`min_population_threshold=3`, `priority_households_threshold=8`）を使用。実際の優先順位判定には使えない。
8. **Human Bridgeの定義と容量モデル** — needs-human。D0はADR-0005の簡略デモモデルを使用。M3で正式モデルに置換する。
9. **制度ルーティングの監修者** — needs-human。R1着手前に確定する。D0・R0では制度ルーティングを実装しない（役割カードの `route_candidates` は例示コードのみで、確定的な自動ルーティングロジックは持たない）。
10. **R2で保持してよい候補者項目** — needs-human。R2着手前にプライバシー影響評価が必要（`IMPLEMENTATION.md` Phase R2 前提）。D0・R0では個人情報を一切扱わない。

---

## D0実装で新たに生じた未決事項

### D0未実装の近隣生活機能

- `toilet_rest`（排泄・休息）、`activity`（活動・地域接点）はD0のデータモデル・UI・色分類から除外した（ADR-0002）。M1着手前にデータ選定・監査状況を確認し、対象に含めるか判断する。

### M11B 青梅市施設座標の境界外レコード（ADR-0009）

- `data/raw/ome/` の診療所・介護サービス事業所299件を青梅市行政区域ポリゴンへ照合したところ、11件が境界外座標だった。
  rawデータを推測で修正・削除せず、`data/normalized/ome/real_map.json` に `within_boundary: false` として残し、位置マップでは
  「地図上は非表示・要監査」と表示している。出典元による住所・座標確認が必要。

### スクリーンショット自動化のOS依存

- `scripts/screenshot.py` はmacOSローカルの Google Chrome バイナリ（`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`）をheadlessモードで呼び出す実装とした。CI環境や他OSでは動作しない可能性がある。Playwright等クロスプラットフォームなツールの導入は、依存追加の可否をオーナー判断が必要なため保留し、`needs-human` として記録する。

### JSON Schemaバリデーションライブラリ未導入

- 実行環境に `jsonschema`（Python）が未インストールだったため、`scripts/verify.py` はPython標準ライブラリのみで手書きの構造検証を行っている。将来的に `jsonschema` を導入する場合は依存追加の可否をオーナー判断とする。

### `candidate-profile.schema.json` は未作成

- `IMPLEMENTATION.md` §1のディレクトリ推奨には含まれるが、R2（本人プロフィール）着手前は用途がないため、D0/R0では作成を見送った。R2着手時に作成する。

### `make verify` はD0時点で `verify-demo` のみを実行する

- `IMPLEMENTATION.md` §6 の `verify` ターゲット定義は `verify-demo` + `verify-m1` + `test-role` を含むが、`scripts/audit_sources.py` 等M1以降のスクリプトと `tests/test_accessibility.py` 等はD0時点で未作成のため、そのまま実行すると失敗する。D0期間中は `Makefile` の `verify` を `verify-demo` のみに限定した。M10以降のスクリプト・テストを作成し次第、元の定義へ戻す。

### `data/catalog.yaml` のproduction_ready未確定

- M10で青梅市のclinic・welfare等の監査済み候補を登録済みだが、対象地域が青梅市に確定した後も、全都カバー・道路経路・標高・人口按分まで確認できていないため `production_ready: false` を維持する。D0の合成データは `data/demo/` に隔離し、実データレジストリと混在させない。

---

## D0完了ゲート判定（2026-08-23）

`docs/design/20260823-tokyo-proximity-role-platform/Agent.md` §7 のチェックリスト。

- [x] 新規アプリの骨格がある
- [x] アプリ側SPEC/IMPLEMENTATION/AGENTSがある
- [x] D0タスクが依存順に定義されている（tasks/index.yaml）
- [x] prototype/index.htmlが生成される（make demo）
- [x] 5/10/15分、速度、勾配で表示が変わる（verify.py MAP-001/002/003通過、ブラウザ実操作確認）
- [x] セルの不足理由が表示される（セル詳細パネル：機能別実効時間・閾値外タグ・データ品質）
- [x] 3介入のBefore/Afterが表示される（小規模生活拠点で実操作確認。Human Bridge/モビリティノードも同一エンジンで実装済みだが個別のブラウザ実操作は小規模生活拠点のみ実施）
- [x] 地域役割カードがdraftで生成される（ROLE-0001をブラウザで生成し確認。status="draft"はコード上固定でapproved代入経路なし）
- [x] make verify-demoが成功する
- [x] ブラウザ確認済み（claude-in-chrome経由でprototype/index.htmlを開き、閾値・セル選択・介入仮置き/除去・役割カード生成を実操作。コンソールエラーなし）
- [x] スクリーンショットが保存される（docs/assets/proximity-role-demo.png）
- [x] OPEN-ISSUES.mdに未決事項が残されている（本ファイル）

**D0はすべての完了ゲートを満たした。**

未実施・持ち越し事項:

- Human Bridge・モビリティノードのブラウザ実操作は目視確認していない（小規模生活拠点のみ実操作確認）。実装は共通の介入エンジンを通っており verify.py の intervention-revert チェックは全介入タイプに影響しないケースのみ（mobility_stopを使用）。次セッションでの操作確認を推奨
- スクリーンショットはビューポート範囲（1366×768）のみで、役割カードパネルなどページ下部は写っていない。フルページ画像が必要な場合は別途取得する
- M1の対象地域は青梅市に確定済みだが、道路ネットワーク・標高DEM・人口按分・徒歩到達圏の正式採用は未完了。M12/M13でデータ出典とモデルの人間確認が必要。
