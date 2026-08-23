# 実行証跡

各エントリは `## YYYY-MM-DD HH:MM Txx` の形式で追記する。上書きしない。

## 2026-08-23 12:01 T00

- 実装: `apps/silverpunk-proof-map/` 骨格を作成（`README.md`, `AGENTS.md`, `data/`, `data/raw/`, `data/normalized/`, `evidence/`, `prototype/`, `scripts/`, `tasks/`）
- 検査: `mkdir -p` で作成、`ls -la` で構成を確認
- 観測: ディレクトリが揃った。`python3 -m http.server 8000` はまだ配布物（`prototype/index.html`）が無いため T02 完了後に確認する
- 残課題: T01 が `data/demo-fixture.json` を追加する。既存 `apps/tokyo-aging-stress-test/` は無変更

## 2026-08-23 12:10 T01

- 実装: `data/demo-fixture.json`（モデル地区4件）、`data/README.md`
- 検査: `python3 -c "json.load(...)"` で読み込み・地区ID重複なし・4地区を確認
- 観測: `illustrative`/`missing`/`not_verified`/`not_comparable`/`not_applicable`/`stale`/`not_computable` の7状態すべてを含む。実在自治体名は使わず「モデル地区A〜D」とした
- 残課題: T02 が画面に埋め込む。地図・実データ取得は未着手のまま

## 2026-08-23 12:15 T04V

- 実装: `scripts/verify.py`（構造・必須フィールド・地区ID重複・verified の出典有無・missing/0の混同・not_computable の誤用・facilities状態を検査）
- 検査: `python3 scripts/verify.py --phase 0` → 終了コード0
- 観測: `population` を意図的に `verified`（source_id なし）に壊した一時JSONで実行 → 終了コード1、2件の指摘を検出。正常系・異常系とも意図通り
- 残課題: `--phase 1` は `prototype/index.html` が無いため未実行。T02 完了後に通す

## 2026-08-23 12:40 T02

- 実装: `prototype/index.html`（単体HTML。`data/demo-fixture.json` を `<script type="application/json">` に埋め込み、外部CDN/フェッチなし）。シナリオ表示、全体像サマリー、地区候補カード一覧、4種類の並べ替えボタン（優先度/高齢化率/支援拠点数/未確認・欠損数）を実装
- 検査: `python3 scripts/verify.py --phase 1` → 終了コード0
- 観測: `python3 -m http.server 8130` を起動し、claude-in-chrome でブラウザ実機確認。初期表示でモデル地区D(0.65)→A(0.35)が優先度降順、算出不可のB/Cは末尾。コンソールエラーなし（`read_console_messages` で確認）。「高齢化率」ボタンで並べ替えが実際に切り替わることを `aria-pressed` 属性で確認（41.5%→34.2%→29.8%→未確認の順）
- 残課題: T03 で地区詳細・30日カードを追加する

## 2026-08-23 12:55 T03

- 実装: `prototype/index.html` に地区詳細パネル（指標カード、拠点一覧、優先度計算式と比較対象、未確認・欠損・対象外の一覧、関連出典）と「30日カード」タブ（仮説・30日アクション・測定指標・中止条件・次の判断）を追加。タブは「根拠を見る」「30日カード」の2つ
- 検査: `python3 scripts/verify.py --phase 1` → 終了コード0
- 観測: ブラウザでモデル地区Dのカードをクリックし詳細パネルが開くことを確認。「根拠を見る」タブで指標・拠点・計算式・欠損項目・出典テーブルを、「30日カード」タブで仮説からの5項目すべてを目視確認。免責文言（経路の安全を保証しない／公式情報を確認）が両タブ下部に表示されている
- 注意（ブラウザ自動化の制約）: `resize_window` および合成 `Tab` キーイベントがこの環境では実ページの `document.activeElement` / viewport に反映されないことを確認した（既知のツール制約。JSで `document.documentElement.style.width` を強制して390px相当のレイアウト崩れがないことは目視確認済み）。実装は全操作をネイティブ `<button>` で構成しており、実ブラウザでは標準のTab/Enter/Spaceでキーボード操作できる設計になっている
- 残課題: T06 で60秒デモ手順とQA証跡をまとめる。T04（出典・主張台帳の本格運用）とT05（データ再生成）は未着手

## 2026-08-23 13:05 T06

- 実装: `README.md` に「60秒デモ手順」（7ステップ）を追記
- 検査: `python3 scripts/verify.py --phase 1` → 終了コード0（最終再実行）
- 観測（60秒デモのリハーサル、claude-in-chrome + `python3 -m http.server 8130` で実施）:
  - 4地区（モデル地区A〜D）が一覧表示される
  - デフォルト並び順は優先度降順（D:0.65 → A:0.35 → B:算出不可 → C:算出不可）。「高齢化率」ボタンで並べ替えると D(41.5%) → A(34.2%) → B(29.8%) → C(未確認) の順に切り替わることを `aria-pressed` 属性と表示順で確認
  - モデル地区Dのカードを開き、「根拠を見る」→指標カード7件・拠点4カテゴリ・計算式と比較対象（2/4件で比較）・未確認欠損3件・出典テーブルが表示されることを確認
  - 「30日カード」タブで仮説・30日アクション3件・測定指標・中止条件2件・次の判断が表示されることを確認
  - `read_console_messages` でエラー・例外ゼロを複数回確認（初回ロード後、並べ替え後、詳細操作後）
  - 外部通信: HTML内に `cdn` を含む外部URL参照なし（`verify.py` の検査項目でも確認）。ソース欄の出典URLはリンクとして表示されるのみで、自動フェッチはしていない
  - 画面幅: 通常表示（1456×815相当、1440px相当に近い）とJSで強制した390px幅の両方で、地区カードが1〜4列に自然に折り返し、操作ボタンも折り返して隠れないことを目視確認
- 制約として記録: `mcp__claude-in-chrome__resize_window` と合成 `Tab` キー操作は、この自動化環境では実ページの `window.innerWidth` / `document.activeElement` に反映されなかった（拡張機能側の既知の制約とみられる）。そのため 390px は `document.documentElement.style.width` を強制する代替手段で、キーボード操作可能性は実装がすべてネイティブ `<button>` であることのコードレビューで確認した。実機（実際のブラウザウィンドウをリサイズ・実キーボード操作）での再確認は次のエージェントまたは人手に委ねる
- 残課題:
  - 実機ブラウザでの390px幅キーボードTab操作の目視確認（自動化ツールの制約により今回は代替確認のみ）
  - T04（出典・主張台帳の本格運用）、T05（検証済みデータの再生成）、T07（地区比較・欠損・優先度レイヤーの拡張）、T08（地図）は未着手
  - Phase 1 の最短デモ経路 `T00 → T01 → T02 → T03 → T06` はここで完了

## 2026-08-23 14:10 T04

- 実装: `evidence/sources.json`（候補ソース3件。title/url/provider/取得日/対象年/粒度/形式/verification/確認方法/使用claim を記録）、`evidence/claims.json`（主張11件。demo priorityの算出根拠、算出不可の理由、拠点・出典候補、fixtureの例示性、not_comparable/staleの宣言を登録）
- 検査: `python3 -c "json.load(...)"` で両ファイルの読み込み確認。`claims[].sources` が `sources.json` に存在するIDのみを参照していること、`status: verified` の主張が0件（=出典未確認の誠実な状態）であることをスクリプトで確認
- 検査: `python3 scripts/verify.py --phase 1` → 終了コード0
- 観測: すべてのソースが `not_verified`。`verified` を名乗る主張・ソースは1件も無い（実データ未取得のため正しい状態）
- 残課題: T05（検証済みデータの再生成）はソースが実際に検証されてから着手する。`prototype/index.html` の表示ロジックは変更していない（fixture内蔵のsourcesと内容は重複するが、claims.jsonはUI主張の原本として今後参照する）

## 2026-08-23 15:00 T05

- 実装: `scripts/fetch_sources.py`（IPSS xlsx をUser-Agent偽装ありで取得、PKマジックバイトとサイズで検査）、`scripts/normalize_data.py`（openpyxlでシートを開き、2020年実績値の総数・65歳以上人口・高齢化率を自治体コード単位に正規化。数値でないセルは`excluded`に理由付きで残す）、`scripts/build_dataset.py`（`data/proof_map.json` を決定的に生成。population/aged_shareをverified、他5指標をmissingとして明示）
- 検査:
  - `python3 scripts/fetch_sources.py` → xlsx取得成功（335,267バイト、PKマジックバイト確認）
  - `python3 scripts/normalize_data.py` → 62自治体を正規化、除外0件
  - `python3 scripts/build_dataset.py` → `data/proof_map.json` 出力（62自治体、population/aged_shareがverified、demo priority算出可能0/62件＝正しい状態）
  - `python3 scripts/verify.py --fixture data/proof_map.json --phase 0` → 終了コード0
  - `python3 scripts/verify.py --phase 1`（demo-fixture側の回帰）→ 終了コード0
  - 意図的に壊した一時JSONでの異常系 → 終了コード1（回帰なし）
- 観測: 千代田区（高齢化率16.4%）・檜原村（53.1%）が、独立した既存アプリ `apps/tokyo-aging-stress-test/scripts/verify.py` の固定点と完全一致することを確認（クロス検証）。IPSSシートの構造（総数=5行目、65歳以上=28行目、高齢化率=34行目、B列=2020年）はxlsxの実物をopenpyxlで開いて確認した
- 変更: `scripts/verify.py` に `enforce_demo_coverage` 引数を追加。T01のfixture専用網羅性検査（missing/not_verifiedを必ず含む等）を、`--fixture`でdemo-fixture.json以外を指定したときは適用しないよう修正（proof_map.jsonは「hazard_exposure等が全件missing」という偏った構成が正しい状態のため）
- 注意: `normalize_data.py` は `openpyxl` に依存する（標準ライブラリにxlsxパーサが無いため）。`data/raw/`, `data/normalized/`, `data/proof_map.json` はいずれもリポジトリにコミットされる生成物ではなく、スクリプト実行で再生成する想定
- 残課題: `prototype/index.html` はまだ `proof_map.json` を表示しない（T07で対応）。`hazard_exposure`（暑熱曝露）・`support_points`（生活支援拠点）・`supporter_ratio`（支え手比率）・拠点カテゴリ別件数の実データ取得は未着手

## 2026-08-23 16:00 T07

- 実装:
  - `scripts/build_dataset.py` に `build_scenario_inputs()`（heat_disasterの必須入力3つだけを対象年・単位を揃えて抽出）と `build_gaps()`（欠損を項目別に集計）を追加。出力を `data/normalized/heat_disaster.json` と `data/gaps.json` に追加
  - `evidence/claims.json` にスコア手法（式・重み・正規化範囲・限界）と、Phase 2実データが全62自治体でnot_computableである根拠のclaimを2件追加（計13件）
  - `prototype/index.html` に「データソース」切替（例示データ／実データ）を追加。`DEMO_FIXTURE`/`REAL_FIXTURE`/`GAPS` を埋め込み、`activeFixture()` 経由で全描画関数（一覧・詳細・根拠・出典）を両データソースに対応させた。実データ選択時は全体像に欠損サマリー（次に取得すべきデータの優先度リスト）を表示
- 検査:
  - `python3 scripts/build_dataset.py` → `heat_disaster.json`・`gaps.json` を追加出力（実装直後は9種類の欠損項目、62/62地区）
  - `python3 scripts/verify.py --phase 1` / `--fixture data/proof_map.json --phase 0` → いずれも終了コード0
  - claude-in-chromeで実ブラウザ確認: 「実データ」ボタンで62自治体（対象地区数62、高齢化率14.1%〜53.1%(verified)、千代田区16.4%等）が表示され、優先度は全件「算出不可」。デモへの切り戻しも正常。コンソールエラーなし
- 不具合と修正: 初回実装では地区詳細の「未確認・欠損・対象外の項目」が同じ項目を2回ずつ表示していた（`build_district()` の `gaps` 配列が `metrics` のmissing項目と完全重複していたため、画面側の `gapItems()` が両方から二重に拾っていた）。`gaps` を空配列にし、`build_gaps()` を metrics/facilities のmissing状態から直接集計する方式に変更して解消（9種類・558件=62×9に）。修正後、`data/proof_map.json` と `prototype/index.html` を再生成・再埋め込みし、ブラウザで重複解消を確認した
- 観測: 東京都全62自治体で `heat_disaster` の必須入力（hazard_exposure, support_points）が揃わず、demo priorityは0/62件。これは実装の誤りではなく、Phase 2でこの2指標をまだ取得していないという正直な状態
- 残課題: `heat_disaster.json`（シナリオ入力抽出）は生成しているが画面からは未参照（将来スコア計算ロジックの検証に使う想定）。暑熱曝露・生活支援拠点データの実取得はT05残課題のまま未着手

## 2026-08-23 14:51 T08

- 実装: `data/normalized/spatial-demo.json` に、例示4地区のローカルSVG模式図レイヤーを追加。地区境界4件、休憩・給水／休憩・医療／介護・避難の施設マーカー各4件（計16件）を `district_id` / 施設IDで管理し、全位置を `illustrative`・`not_verified` として出典・記録日・限界つきで記録
- 実装: `prototype/index.html` に地図セクション、レスポンシブなSVG描画、地区・施設マーカーのクリック／Enter／Space操作、凡例、位置状態・出典・注意書きを追加。例示データでは地図を表示し、実データ62自治体では位置レイヤー未取得の空状態にして一覧・詳細を維持する。外部タイル・API・経路を使用しない
- 検査: `python3 scripts/verify.py` → 終了コード0。`python3 scripts/verify.py --phase 1` → 終了コード0。標準ライブラリで外部JSONとHTML埋め込みJSONの一致、地区／施設IDの一意性・結合・4カテゴリを確認。Node `vm.Script` で実行スクリプトの構文確認 → OK。`git diff --check` → 問題なし。`python3 -m http.server 8765` と `curl` で更新HTMLに地図セクション・埋め込みレイヤーが含まれることを確認
- 追検査: HTML内のdemo fixtureと空間レイヤーを突合し、4/4地区ID・16/16施設IDが一致。実行スクリプト構文と `python3 scripts/verify.py` を最終再実行して通過
- ブラウザ確認: Chrome拡張への接続とタブ列挙は成功したが、localhost / `file://` のページ遷移は管理 URL ポリシーの検証不能（admin-enforced policy unavailable）で拒否された。ポリシー回避は行わず、地図・一覧・詳細・キーボード操作の実ブラウザ目視は未達として残す
- 残課題: 実在自治体の境界・施設位置は未取得。ブラウザのlocalhost許可後に、例示データで地図表示・地区カード連動・4カテゴリ凡例・実データの空状態・390px幅・コンソールエラーなしを目視確認する
