status: done
phase: 0

# T01 骨組みと取得

## ゴール
`apps/living-zone-navi/` を作り、D1〜D5 のCSVが `data/raw/` に検査付きで落ちる。

## やること
1. ディレクトリ作成: `scripts/ data/raw/ data/processed/ prototype/` ＋ `config.json`（`{"ward":"江東区","walk_near_m":300,"walk_far_m":800}`）＋ `OPEN-ISSUES.md`（空でよい）
2. `scripts/catalog.py`: カタログCSV（`docs/research/data/東京都オープンデータ全カタログ_9678件_20260704.csv`）をタイトル検索し、design-spec §3 の検索語で D1〜D5 のリソースURLを解決する関数
3. `scripts/fetch_sources.py`: 解決したURLをDL→サイズ>1KB・先頭行がHTMLでないことを検査→`data/raw/` 保存→`data/sources.json` に url/fetched_at/sha256 を記録。403時はUA偽装を1段挟む
4. D2（クーリングシェルター）が解決できない場合は**エラーにせず** sources.json に `{"id":"D2","status":"not_published"}` と記録

## 完了条件
`python3 scripts/fetch_sources.py` が非ゼロ終了なし。sources.json に D1〜D5 の記録（not_published含む）が揃う。

## 作業ログ
- `apps/living-zone-navi/`（scripts/ data/raw/ data/processed/ prototype/ + config.json + OPEN-ISSUES.md + .gitignore）を作成
- `catalog.py` はカタログCSVをタイトル検索して都度URLを解決（ward優先→都全域フォールバック）。D3は区単位の一般医療機関一覧が無く「実施医療機関」系（予防接種・検査台帳）しか無かったため、都全域の「東京都の災害拠点病院等」に狭めて解決（OPEN-ISSUES.md参照）
- `fetch_sources.py` 実行: D1〜D5すべて `status: ok` で取得成功（非ゼロ終了なし）。D2は実際には解決できたが、未解決時に `not_published` を返す分岐も実装済み
