# data/

## demo-fixture.json

**Phase 1 の例示データであり、公式実測値ではない。** すべての地区は「モデル地区A〜D」という
架空の名称で、実在する東京都の区市町村ではない。実在の自治体名と未検証の数値を混ぜないための措置。

- 数値ステータスが `illustrative` の項目は、画面表示・並べ替え・優先度計算の動作を確認するための
  例示値であり、公開データから確認した実測値ではない
- `missing` / `not_verified` / `not_comparable` / `not_applicable` / `stale` を意図的に含めている。
  それぞれの意味は設計仕様書 FR-06 を参照
- `priority.status: "illustrative"` の値は "demo priority" であり、危険度・安全度の順位ではない
- `sources` はすべて `verification: "not_verified"` の候補ソースであり、Phase 2 で個別ファイルを
  開いて粒度・定義・取得日を確認するまでは実測データの根拠として使わない

`prototype/index.html` は現時点でも `demo-fixture.json` を埋め込んでおり、Phase 2 の実データには未接続（T07）。
このファイルは開発・デモ用として残る。

## proof_map.json

`scripts/build_dataset.py` の生成物。**実在する東京都62自治体**を対象にした Phase 2 の部分実装データ。

- `population`（総人口）と `aged_share`（高齢化率）は `status: "verified"`。
  出典は IPSS「日本の地域別将来推計人口（令和5年推計）」東京都、対象年は2020年（国勢調査による実績値、推計値ではない）
- `hazard_exposure`（暑熱・災害曝露）、`support_points`（生活支援拠点数）、`supporter_ratio`（支え手比率）、
  拠点カテゴリ別件数は、まだ取得元を確定できていないため全62自治体で `missing`
- 上記のとおり `heat_disaster` シナリオの必須入力が揃わないため、`priority.status` は全62自治体で
  `not_computable`。これは意図した誠実な状態であり、バグではない
- 千代田区・檜原村の高齢化率は `apps/tokyo-aging-stress-test/scripts/verify.py` の固定点（16.4%・53.1%）と一致することを確認済み

再生成: `python3 scripts/fetch_sources.py && python3 scripts/normalize_data.py && python3 scripts/build_dataset.py`

## raw/ / normalized/

`raw/ipss_tokyo_population.xlsx` — IPSS人口推計xlsxの原本（`fetch_sources.py` が取得）。
`normalized/population.json` — 自治体コードを第一キーにした2020年実績値の中間データ（`normalize_data.py` が生成）。
