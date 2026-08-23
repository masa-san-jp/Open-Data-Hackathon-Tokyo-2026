# DECISIONS — ADR記録

`SPEC.md` / `IMPLEMENTATION.md` に対する実装判断のうち、`AGENTS.md` §10 で ADR 対象と定めた項目、
および D0 実装のために必要だった仮定をここに記録する。

---

## ADR-0001: D0はSVGグリッドを採用する

- status: accepted
- context: `IMPLEMENTATION.md` §9 のフォールバック方針により、地図ライブラリ導入で時間を消費せず4時間以内にD0を出す必要がある。外部API・CDNなしでオフライン単一HTMLとして開ける必要がある（`SPEC.md` §6.1）。
- decision: `prototype/index.html` の地図表現は、実座標のWebメルカトル地図ではなく、抽象化した8列×6行の合成SVYグリッド（`analysis_resolution_m: 250` を1マスとする）を用いる。実在の地理座標・地名は使用しない。
- alternatives: MapLibre GL JS + 簡略GeoJSON（CDN依存とバンドルサイズでD0の「外部API・CDN不要」条件に反するため不採用）。Leaflet + タイル（同上）。
- consequences: M1でMapLibre GL JS + 実座標GeoJSONへ置き換える際、`cell_id` とメッシュ座標の対応付けを作り直す必要がある。D0の見た目は簡略だが、条件切替・色判定・介入比較・役割カード生成というロジック面の受入条件はSVGグリッドでも全て検証できる。
- rollback: 必要であれば同一の `data/demo/cells.json` を用いてWebメルカトル版へ差し替え可能（データモデルはgeometryをSVG用grid座標かGeoJSON polygonかで抽象化している）。

---

## ADR-0002: D0の必須生活機能セットと未評価機能の扱い

- status: accepted
- context: `SPEC.md` §3.2 は7機能を候補としつつ「データ監査で『利用可能』と判定されたものだけを有効化する」と定める。D0時点ではM1データ監査（M10/M11）が未着手であり、`SPEC.md` §5.3 は食料品店データを「東京都全域を覆うODは未確認」、`toilet_rest`／`activity` も網羅性・選定が未完了と記す。
- decision: D0の色分類（青/黄/橙/赤）に使う**必須機能セット**を `pharmacy`（服薬）、`clinic`（一次医療）、`welfare`（福祉）、`mobility_node`（圏外接続）の4つに限定する。`food`（食料取得）はセルごとに常に `data_quality: "unassessed"` として保持し、色分類には含めず、セル詳細パネルに「食料: データ未確認（未評価）」として明示する。`toilet_rest` と `activity` はD0のデータモデル・UIから除外し、`OPEN-ISSUES.md` に「D0未実装」として記録する。
- alternatives: 7機能すべてを対象に含める（M1データ監査前のためデータ品質を偽ることになり、`AGENTS.md` §5.1「存在確認と利用可能性を分ける」に反するため不採用）。
- consequences: D0の「未評価セルが赤ではなく灰ハッチになる」受入条件（`SPEC.md` §8）は、`food` の未評価表示に加えて、必須4機能のうち少なくとも1つが `unassessed` となるよう合成した一部セル（デモ内で意図的に配置）でも検証する。M11で対象地域を決定した際、`food` の扱いは `IMPLEMENTATION.md` §3「食料データが未確定なら、M1は薬局・診療所・福祉・交通だけで実施」の方針に従う。
- rollback: M1データ監査で `food` が利用可能と判定されたら、必須機能セットへ追加し本ADRを更新する。

---

## ADR-0003: D0の歩行速度・勾配モデルはデモ仮定として明示する

- status: accepted
- context: `SPEC.md` §3.3 は D0 で `crossing_delay=0`、`stairs_penalty=0` を許容し、勾配係数は「デモ仮定」として画面明示する（実測値と表示しない）よう定める。
- decision:
  - 基準歩行速度（`base_walking_speed`）はデモ既定値 `80 m/min`（成人標準・目安）とし、UIから4プロファイル（表示順: 高齢者目安 60 / 杖使用等 45 / 車椅子等利用者 55 / 成人目安 80 m/min）または任意の数値（20〜100 m/min）を選択できる。プロファイルの並び順は、主な利用対象（高齢者・杖使用者・車椅子等利用者）を先に、基準値である成人目安を最後に表示する（オーナー指示、2026-08-23）。車椅子等利用者の `55 m/min` は根拠のあるデータではなく、他3プロファイルとの相対関係のみを示すデモ仮定である。
  - 勾配補正はUI既定値を **ON** とする（オーナー指示、2026-08-23）。高齢者・杖・車椅子等利用者を主対象とするプロダクトの性質上、勾配の影響を初期表示から示すことを優先した。OFFへの切替は引き続き可能。
  - 各セル×機能の基準到達時間 `base_access_minutes` は、合成グリッド上の施設仮想配置点までのユークリッド距離（250m/マス換算）を基準速度 80 m/min で除して算出する合成値であり、実測の道路経路ではない。
  - 勾配補正は各セルに合成の `slope_index`（0.0〜1.0、行番号に基づく合成の「上り」強度）を持たせ、補正ON時は `effective_minutes = base_minutes × (80 / selected_speed) × (1 + 0.4 × slope_index)`、補正OFF時は `slope_factor = 1.0` とする。`0.4` は経路が最も急な場合に所要時間を最大40%押し上げるデモ仮定の係数であり、実測値ではない。
  - `crossing_delay = 0`、`stairs_penalty = 0` をD0で採用する。
- alternatives: 実際の道路網・DEMを用いた計算（M12/M13の範囲であり、D0の4時間枠では未確定。`SPEC.md` §9 の未確定事項6「高齢者向け勾配補正モデル」に該当するため、D0では確定させず明示仮定に留める）。
- consequences: `slope_factor >= 1.0` を保証する実装とすることで、「上り補正を有効化して所要時間が短くならない」（`SPEC.md` §3.3必須性質）を構造的に満たす。同様に `effective_minutes` は速度に反比例するため「速度を下げても到達セルが増えない」を構造的に満たす。画面とエクスポートに `walking_speed_m_per_min`、`slope_model: "demo-linear-v1"`、係数 `0.4` を常時表示する。
- rollback: M12/M13で実道路網・DEMベースのモデルに置き換え、`data/methodology/walking-model.yaml` に採用モデルと根拠を記録する。

---

## ADR-0004: D0の優先地域判定基準（世帯数閾値）

- status: accepted
- context: `SPEC.md` §3.5 は「赤は『不便』のみで決めず、未充足数 × 高齢単身世帯等の需要量で決める」「優先基準は設定ファイル化し、UIに値を表示する」と定める。`SPEC.md` §9 未確定事項7「優先対象世帯数の基準」は未確定のまま。
- decision: D0では2つの合成世帯数閾値を設定値として `data/demo/cells.json` のメタデータおよびUI凡例に表示する。
  - `min_population_threshold = 3`（高齢単身世帯数がこれ未満のセルは「対象人口が基準未満」として薄灰表示。評価値自体は保持しセル詳細で確認できる）
  - `priority_households_threshold = 8`（不足機能が2つ以上、かつ高齢単身世帯数がこの値以上のセルを赤、それ未満は橙とする）
  この2値はD0のデモ仮定であり、実際の優先順位判定に使う数値ではない。
- alternatives: 固定の「不足機能数のみ」で色を決める（需要量を無視するため `SPEC.md` の定義に反する。不採用）。
- consequences: M1以降、東京都・区市町村の合意する実際の優先基準に置き換える。置き換え時は本ADRを更新し、`data/methodology/` に根拠を記録する。
- rollback: 閾値を設定ファイル化しているため、値の変更のみで対応可能。

---

## ADR-0005: D0のHuman Bridge容量モデルは簡略デモ版を用いる

- status: accepted
- context: `IMPLEMENTATION.md` Phase M3 で定義される容量モデル（`service_radius_m: 1200`、`daily_capacity: 16` 等）はM3向けであり、D0では容量・費用の最適化を行わない（`SPEC.md` §3.7）。ただし D0 でも Human Bridge 介入の Before/After 世帯数変化を実演する必要がある（`IMPLEMENTATION.md` §2.1 画面機能6/7）。
- decision: D0の `human_bridge` 介入は、M3の値をデモ用に縮小した固定パラメータ（`service_radius_cells: 2`＝合成グリッドで半径2マス、`daily_capacity_households: 10`）を用いる。半径内セルを高齢単身世帯数の多い順に並べ、容量に達するまで `welfare` の効果的到達時間を「介入後は閾値内」とみなす簡略計算とし、地理的にカバーできる世帯数と容量上カバーできる世帯数を別々に表示する。
- alternatives: 容量制約なしで半径内すべてを改善扱いにする（`IMPLEMENTATION.md` M3の容量概念をD0で完全に無視することになり、「容量上カバーできる最大件数」という出力要件（`SPEC.md` §3.7）を示せないため不採用）。
- consequences: M3で正式な容量モデルへ置き換える際、本ADRのパラメータ名 (`service_radius_cells`, `daily_capacity_households`) を `service_radius_m`, `daily_capacity` に対応付けて移行する。
- rollback: パラメータ変更のみで対応可能。

---

## ADR-0006: D0の分析メッシュ解像度と合成グリッド規模

- status: accepted
- context: `SPEC.md` §3.1 は初期値250mメッシュ、画面に実際の分析単位を常時表示することを定める。
- decision: D0では `analysis_resolution_m: 250` を採用し、8列×6行＝48セルの合成グリッドをデモ対象とする。セルIDは実在メッシュコードと誤認されないよう `DEMO-<row><col>` 形式（例: `DEMO-0203`）とする。
- alternatives: 実際の東京都のメッシュコード形式（例: `53394612-001`）を模した合成IDにする（実在データと誤認されるリスクがあるため不採用。`SPEC.md` §1.4「東京都全域を最初から完全網羅したと主張すること」を対象外とする方針にも反する）。
- consequences: M1で実座標・実メッシュコードに置き換える。
- rollback: なし（初期値のまま）。

---

## ADR-0007: M1対象地域を青梅市に確定する

- status: **accepted**（オーナー承認: 2026-08-23。`Agent.md` §5「実データ対象地域の最終選定」）
- context: M1着手には対象地域が必要（`IMPLEMENTATION.md` M11）。オーナーからは「候補を一緒に検討する」との
  指示を受けた。`docs/research/data/20260823-datasets-to-pick-up.md`（別プロジェクト向けの実測調査だが
  公開データの実測値として本プロジェクトでも参照可能）で、西多摩5市町村（青梅市・あきる野市・羽村市・
  瑞穂町・日の出町）が2050年時点で高齢化率44.5%・隣接クラスタと推計されている。
- decision（提案）: このうち人口・施設密度が最大で自治体オープンデータポータルが整備されている**青梅市**を、
  M1の「1地域」候補として監査した。監査結果は `data/reports/source-audit-summary.md` を参照。
  `clinic`・`welfare`・人口統計（地区別）は実在・ライセンス明確（CC-BY-4.0）・ジオコーディング済みで確認できた。
  一方、`pharmacy`・`mobility_node`・高齢単身世帯数の直接データ・道路網・標高DEMは未解決。
- alternatives: あきる野市・羽村市・瑞穂町・日の出町（西多摩の他4候補、未監査）。23区内の候補（人口密度は
  高いが「高齢化が最も進む地域」という企画意図とは合致しにくい）。
- consequences: 青梅市で確定する場合、`pharmacy`・`mobility_node`のデータギャップをどう扱うか
  （別出典を探す／該当機能を未評価のままM1を先行する）の判断が必要。他候補（あきる野市等）を選ぶ場合は
  同様の監査をやり直す。
- rollback: 対象地域を変更する場合、本ADRをsupersededとし、新地域で監査をやり直す。

---

## ADR-0008: M1初期は青梅市の pharmacy・mobility_node を「未評価」として扱う

- status: accepted
- context: ADR-0007で青梅市を対象地域として確定したが、`data/reports/source-audit-summary.md`の監査で
  `pharmacy`（薬局）・`mobility_node`（バス停等）のダウンロード可能なデータが見つからなかった。
  `IMPLEMENTATION.md` §9のフォールバック方針「食料データが見つからない → 食料を未評価にし、
  薬局・診療所・福祉・交通でM1」と同じ考え方を、今回はpharmacy・mobility_node自体に適用する。
- decision: M1の初期実装では、必須機能セットを一時的に `clinic`・`welfare` の2機能に限定し、
  `pharmacy`・`mobility_node`は`food`と同様に「データ未確認」として全セルで灰ハッチ表示する。
  別出典（東京都保健医療局への確認、西東京バス、OpenStreetMap等）が見つかり次第、
  本ADRを更新して機能セットを拡張する。
- alternatives: pharmacy・mobility_nodeのデータ探索が終わるまでM1全体を保留する（M1着手自体が
  遅延するため不採用。データ欠損を隠さず明示すれば、2機能でも「実データに基づく実効徒歩圏の可視化」
  というM1のゲート条件（`SPEC.md`§8）は満たせると判断）。
- consequences: D0で実装した4必須機能（pharmacy/clinic/welfare/mobility_node）の判定ロジックのうち、
  M1では2機能のみが「評価可能」となり、残り2機能は常に未評価セル扱いになる。M1の「1地域の実データMVP」
  ゲートとしては成立するが、ハッカソンデモとしての説得力はD0（4機能）より下がる可能性がある。
  道路網・標高DEMの正式採用は本ADRの範囲外（`Agent.md`§5により別途人間承認が必要）。M12着手前に
  別途確認する。
- rollback: pharmacy・mobility_nodeのデータが見つかり次第、本ADRを更新し4機能へ復帰させる。

---

## 未ADR化の検討事項

以下は `AGENTS.md` §10 のADR対象リストのうち、D0の範囲では実質的な判断が発生しなかった、またはM1以降に持ち越した項目。`OPEN-ISSUES.md` にも重複記録する。

- 道路データ・標高データの正式採用: D0では使用しない（ADR-0003参照）。M1で `OPEN-ISSUES.md` の指示に従い決定する。
- 制度ルーティングルール: D0のスコープ外（R1）。
- 個人情報項目: D0・R0では個人情報を一切扱わない（`SPEC.md` §4.6 R0段階の定義通り）。

---

## ADR-0009: M1施設座標の行政区域外レコードを監査対象として残す

- status: accepted
- context: 青梅市の医療機関138件と介護サービス事業所161件を行政区域ポリゴンへ照合したところ、11件が境界外座標だった。rawデータを出典確認なしに修正・削除してはならず、全件を同じ地図範囲へ含めると境界と施設分布が読めなくなる。
- decision: 正規化データへ `within_boundary` と `coordinate_status` を付与する。境界外レコードは `data/normalized/ome/real_map.json` に保持し、位置マップでは件数を「地図上は非表示・要監査」と明示して表示対象から除外する。地図表示件数と原データ件数を分けて表示する。
- alternatives: 境界外レコードを黙って削除する（出典追跡不能になるため不採用）、全レコードを地図範囲に含める（行政区域が極端に縮小表示されるため不採用）。
- consequences: 出典元による住所・座標確認が完了するまで、境界外11件を徒歩圏・施設密度の分析へ利用しない。確認後は座標更新または対象地域の再監査を行う。
- rollback: 出典元確認で正しい座標が得られたレコードを再正規化し、境界内表示へ戻す。誤りが確定した場合はrawデータを変更せず、監査結果を別レポートへ記録する。

---

## ADR-0010: 背景地図はOpenStreetMapの表示専用タイルと座標フォールバックを使う

- status: accepted
- context: 実座標の行政区域と施設点だけでは地図としての位置関係を読み取りにくい。一方、道路ネットワークの取得元・ライセンス・徒歩計算モデルはM12/M13で人間確認が必要であり、今回の表示改善で分析入力へ流用してはならない。
- decision: オンライン時の現在表示範囲に限り `https://tile.openstreetmap.org/{z}/{x}/{y}.png` を背景表示する。地図上にOpenStreetMapの帰属表示とODbLを明示し、道路・地形は施設到達時間や政策判定の入力に使わない。タイル取得失敗時は外部依存なしの実座標グリッド、行政区域、施設点へフォールバックする。
- alternatives: 現在の境界ポリゴンだけを表示する（位置文脈が不足するため不採用）、道路データを取得して分析に使う（M12/M13の承認前であり不採用）、タイルを事前ダウンロードして同梱する（OpenStreetMap標準タイルのオフライン利用・一括取得条件に反するため不採用）。
- consequences: 地図表示はオンライン時に道路等の文脈を持つが、タイルの可用性は保証されない。分析用道路網の採用判断は未解決のまま残る。
- rollback: 背景タイルをOFFにし、座標グリッドのみを既定表示に戻す。分析データやrawデータへの影響はない。
