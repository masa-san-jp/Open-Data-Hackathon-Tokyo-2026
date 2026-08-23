# SILVERPUNK PROOF MAP — 実装計画書

作成日: 2026-08-23  
状態: 自律実装エージェントに渡せる初版  
対象仕様: [`20260823-silverpunk-proof-map-design-spec.md`](./20260823-silverpunk-proof-map-design-spec.md)  
実装先: `apps/silverpunk-proof-map/`

## 1. 実装方針

最初に「データを全部集めてから画面を作る」進め方を取らない。15〜30分で起動する画面を先に作り、データの精度を上げても画面契約が壊れないようにする。

優先順位は次の順で固定する。

1. オフラインで開く
2. 60秒で主張が伝わる
3. 根拠・取得日・限界が見える
4. データ更新を再現できる
5. 地図・高度なスコア・外部連携を追加する

Phase 1 のデモに地図、外部 API、個人データを入れない。これらは価値を増やす可能性はあるが、最初の動作確認をブロックするためである。

## 2. リリース目標

### R0 — 15分で起動する骨格

```bash
cd apps/silverpunk-proof-map
python3 -m http.server 8000
# ブラウザで http://127.0.0.1:8000/prototype/ を開く
```

空の状態でも、タイトル、シナリオ、`未確認` の表示、出典欄、注意書きが出ること。

### R1 — Phase 1 デモ

目標時間: 2〜4時間（1エージェントの場合）  
成果物: `prototype/index.html`、`data/demo-fixture.json`、`scripts/verify.py`

- 3地区以上の比較
- シナリオ切替
- 詳細カード
- 根拠と欠損の表示
- 30日パイロットカード
- ブラウザでエラーなし
- 外部通信なし

数値が未検証なら fixture に `illustrative` または `not_verified` を付け、実測値のように表示しない。デモで見せる主張は `claims.json` に登録する。

### R2 — Phase 2 検証済みデータ

目標時間: 半日〜1日  
成果物: `raw/`、`normalized/`、`sources.json`、生成スクリプト、固定点テスト

既存の `apps/tokyo-aging-stress-test/data/stress_test.json` を再利用できる項目は、出典を引き継いで変換する。それ以外は東京都の公開元を一つずつ開いて形を確認してから使う。

### R3 — Phase 3 意思決定デモ

目標時間: 半日〜1日  
成果物: T4/T7/T8/T9 の統合画面

- 暑熱×要支援の比較入力が揃った地区だけスコアを算出
- 揃わない地区は `not_computable` とし、欠損カードへ送る
- 地区候補の上位3件を、指標と根拠つきで比較
- 1地区の現地検証アクションと中止条件を出力

## 3. フェーズ別作業

### Phase 0: Contract（30〜45分）

| 順 | 作業 | 成果物 | 完了条件 |
| :-- | :-- | :-- | :-- |
| 0-1 | アプリの空ディレクトリを作る | `apps/silverpunk-proof-map/` | 既存アプリを変更しない |
| 0-2 | 最小 JSON を作る | `data/demo-fixture.json` | schema version、sources、scenarios、districts がある |
| 0-3 | 検証コマンドを作る | `scripts/verify.py` | JSON 不備を非ゼロ終了で検知する |
| 0-4 | 単体 HTML の枠を作る | `prototype/index.html` | `file://` または HTTP で開く |
| 0-5 | 作業状態を初期化する | `evidence/run-log.md` | 実行日時と状態が残る |

**遅延時のフォールバック**: 0-2 の fixture が未確定でも、実在データを捏造せず `illustrative` レコード3件を使う。画面に「例示 fixture」と表示して R0 を完了する。

### Phase 1: Demo（2〜4時間）

| 順 | 作業 | 成果物 | 完了条件 |
| :-- | :-- | :-- | :-- |
| 1-1 | ヘッダーとシナリオ切替 | `prototype/index.html` または分離 JS | `heat_disaster` を選べる |
| 1-2 | 指標カードと地区一覧 | 同上 | 3地区以上、並べ替え可能 |
| 1-3 | 地区詳細 | 同上 | 根拠・データ状態・欠損が見える |
| 1-4 | 30日パイロットカード | 同上 | 仮説・行動・指標・中止条件がある |
| 1-5 | 出典・注意書き | 同上 | 画面下部に常時表示 |
| 1-6 | UI 検査 | `evidence/run-log.md` | 390px/1440px とキーボード操作を確認 |

**遅延時のフォールバック**:

- 地区カードが間に合わない場合は、固定3地区の一覧と1地区詳細に絞る
- スコアが決まらない場合は、順位を付けず「比較候補」と表示する
- グラフが間に合わない場合は、数値カードと表で代替する
- 地図が間に合わない場合は、地図を作らない。カードが完成していれば Phase 1 完了とする

### Phase 2: Evidence（半日〜1日）

| 順 | 作業 | 成果物 | 完了条件 |
| :-- | :-- | :-- | :-- |
| 2-1 | ソース一覧を確定 | `evidence/sources.json` | URL、タイトル、取得日、検証状態がある |
| 2-2 | 原本取得 | `data/raw/` | 取得失敗を隠さずログに残す |
| 2-3 | 正規化 | `data/normalized/` | 列名、自治体コード、型、単位が揃う |
| 2-4 | 既存データの再利用 | `build_dataset.py` | 高齢者・就業者の既存指標を再生成できる |
| 2-5 | 固定点・件数検証 | `scripts/verify.py` | 期待件数、型、除外理由、出典を検査する |
| 2-6 | HTML 生成 | `scripts/build_prototype.py` | 同じ入力から同じ画面を再生成する |

**遅延時のフォールバック**: 取得元が 403、形式変更、未検証の場合は最後の検証済み snapshot を使い、画面の基準日を明示する。取得できない値をゼロや平均値で埋めない。

### Phase 3: Decision（半日〜1日）

| 順 | 作業 | 成果物 | 完了条件 |
| :-- | :-- | :-- | :-- |
| 3-1 | T7 入力を定義 | `data/normalized/heat_disaster.json` | 暑熱、要支援、拠点の定義が別々にある |
| 3-2 | スコア版を固定 | `evidence/claims.json` | 式、重み、正規化範囲、限界が記録される |
| 3-3 | T8 欠損カード | UI と `data/gaps.json` | 「0」と「比較不能」を区別する |
| 3-4 | T4 地区比較 | UI | 上位3件を根拠つきで比較できる |
| 3-5 | T9 出力 | UI / 印刷用 CSS（任意） | 30日カードを1画面で共有できる |

### Phase 4: Spatial（任意）

地図は R3 が動いたあとだけ着手する。

- ローカル SVG または GeoJSON を第一候補にする
- 外部タイルや経路 APIを必須にしない
- 地図が壊れてもランキング・詳細・根拠カードを表示する
- ルートを描く場合は「候補経路」「現地確認が必要」と表記する

## 4. タスク依存関係

```text
T00 Bootstrap
  ├── T01 Data contract & fixture
  │     └── T02 Static prototype shell
  │           └── T03 Detail & pilot card
  ├── T04 Source manifest & verification
  │     └── T05 Reproducible dataset build
  └── T06 QA & demo evidence

T03 + T05 ──> T07 T4/T7/T8/T9 decision layer
T07 ────────> T08 optional spatial layer
```

Phase 1 の最短経路は `T00 → T01 → T02 → T03 → T06`。データ取得で止まった場合もこの経路でデモを出す。

## 5. タスクの実装契約

`tasks/` の各ファイルは、次の形式で独立して実装できるようにする。

```yaml
id: T02
phase: 1
status: ready
owner: unassigned
depends_on: [T01]
files:
  - prototype/index.html
acceptance:
  - python3 scripts/verify.py
  - ブラウザでシナリオ切替ができる
```

エージェントは、担当前に `status: doing`、完了後に `status: done` または `blocked` を書く。完了ログには「変更ファイル、実行コマンド、観測結果、残課題」を3〜8行で残す。

## 6. 並行作業の分け方

### Lane A: Data / Evidence

- T01: JSON 契約と fixture
- T04: 出典・主張台帳
- T05: 取得・正規化・検証

### Lane B: UI / Demo

- T02: 静的プロトタイプ
- T03: 詳細・30日カード
- T07: 地区比較・欠損カード

### Lane C: QA / Story

- T06: ブラウザ検査、アクセシビリティ、60秒デモ
- T08: 地図の progressive enhancement（任意）

T01 の JSON 契約ができたら Lane A と Lane B は並行できる。T07 は T03 と T05 が終わるまで開始しない。

## 7. 推奨ファイル変更順

1. `apps/silverpunk-proof-map/data/demo-fixture.json`
2. `apps/silverpunk-proof-map/scripts/verify.py`
3. `apps/silverpunk-proof-map/prototype/index.html`
4. `apps/silverpunk-proof-map/evidence/sources.json`
5. `apps/silverpunk-proof-map/evidence/claims.json`
6. `apps/silverpunk-proof-map/scripts/fetch_sources.py`
7. `apps/silverpunk-proof-map/scripts/normalize_data.py`
8. `apps/silverpunk-proof-map/scripts/build_dataset.py`
9. `apps/silverpunk-proof-map/scripts/build_prototype.py`
10. `apps/silverpunk-proof-map/evidence/run-log.md`

画面を先に直接書いてよいが、数値・URL・計算式は必ず fixture または台帳に戻す。画面 JS に主張をハードコードしない。

## 8. 実行コマンド契約

アプリ実装後は、README に次のコマンドを掲載する。

```bash
# 1. データの形を検査
python3 scripts/verify.py

# 2. 検証済み snapshot からデータを再生成（存在する場合）
python3 scripts/build_dataset.py

# 3. 単体 HTML を再生成（存在する場合）
python3 scripts/build_prototype.py

# 4. ブラウザで確認
python3 -m http.server 8000
```

Phase 1 では `build_dataset.py` と `build_prototype.py` が未実装でもよい。ただし、その場合は `verify.py` が fixture を検査し、README に「生成スクリプト未実装」と明記する。

## 9. 60秒デモ手順

1. 画面を開き、「猛暑・災害」を選ぶ（5秒）
2. 「今日の東京では、必要な場所とデータの両方が見えていない」と説明する（10秒）
3. 地区候補を、優先候補・高齢化・拠点・欠損で比較する（15秒）
4. 1地区を選び、確認済みの値と未確認の値を切り替える（15秒）
5. 30日パイロットカードで、現地確認と中止条件を示す（10秒）
6. 「作って終わりではなく、次の検証に接続する」と締める（5秒）

デモ中に数値の根拠を聞かれた場合は、地区カードの出典を開く。根拠が開けない値は、デモで主張しない。

## 10. QA チェックリスト

### データ

- [ ] `python3 scripts/verify.py` が終了コード0
- [ ] すべての `verified` 値にソースと取得日がある
- [ ] 数値の対象年・単位が表示される
- [ ] `0` と `missing` が別表示される
- [ ] 指標の分母・分子が同じ粒度である
- [ ] 地区名の表記ゆれがコードまたは対応表で処理されている
- [ ] 未検証 URL を「公式値」と表示していない

### UI

- [ ] `file://` またはローカル HTTP で開く
- [ ] 外部リクエストがない
- [ ] コンソールにエラーがない
- [ ] 390px 幅で横スクロールなしに主要操作できる
- [ ] キーボードフォーカスが見える
- [ ] 色だけに依存していない
- [ ] 緊急時は公式情報を確認する注意書きがある

### ストーリー

- [ ] 60秒で課題・比較・次の行動が伝わる
- [ ] 高齢者を一方的な支援対象として描いていない
- [ ] スコアを安全保証として表現していない
- [ ] 「データがない」を責任追及ではなく整備課題として示す

## 11. フォールバック判断表

| 障害 | その場の判断 | 出すもの |
| :-- | :-- | :-- |
| データ URL が取得できない | 取得を止め、最後の検証済み snapshot を使用 | 基準日つき静的デモ |
| CSV/XLSX の列が変わった | 正規化を止め、差分をログに残す | 旧データ＋未更新表示 |
| スコアの重みが合意できない | スコアを出さず指標一覧にする | 比較候補カード |
| 地区境界がない | 地図を延期する | 地区一覧・詳細・根拠 |
| ブラウザ自動検査が使えない | 手動チェックリストを実行する | run-log に観測結果 |
| 依存ライブラリを追加できない | Vanilla JS / SVG に戻す | 単体 HTML |
| エージェント間でファイルが衝突する | 担当外のファイルを戻さず、blocked と記録 | 手動統合待ち |

## 12. 完了判定と引き渡し

Phase 1 を「できた」と言ってよい条件は、次の全てを満たすこと。

1. `prototype/index.html` がローカルで開く
2. 3地区以上を表示し、1地区の詳細を開ける
3. 根拠・取得日・データ状態・限界をたどれる
4. 30日パイロットカードがある
5. `python3 scripts/verify.py` が通る
6. 60秒デモを実際に再生した記録がある
7. `evidence/run-log.md` に未解決事項が残っている（隠していない）

引き渡しコメントは次の形式にする。

```text
[T03 done]
変更: prototype/index.html, evidence/run-log.md
検査: python3 scripts/verify.py / ブラウザ手動確認
観測: 3地区表示、詳細開閉、未確認表示、30日カードを確認
残課題: 実データの暑熱拠点は Phase 2 で検証する
```

