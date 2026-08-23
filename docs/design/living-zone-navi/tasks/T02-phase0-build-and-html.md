status: done
phase: 0

# T02 Phase 0 ビルドと数字が出るHTML

## ゴール
地図なしで、ヘッダ数字と施設件数表・欠損パネルが出る `prototype/index.html`。**ここでデモ可能になる。**

## やること
1. `scripts/build_dataset.py`: raw→facilities正規化（kind付与・座標有無判定・cp932フォールバック）、D5から区の65+/75+人口集計、gaps生成（D2欠損＋barrier_free恒常欠損）→ `data/processed/dataset.json`（design-spec §4。areasは町丁人口のみ・nearest/reachは全部 unknown でよい）
2. `scripts/build_prototype.py`: dataset.json を埋め込んだ index.html 生成（design-spec §5 の 1・4・5 のみ）
3. `scripts/verify.py`: design-spec §8 の固定点（この段階で検査可能なもの）

## 完了条件
fetch→build→verify 3本非ゼロなし。ブラウザで実装計画 §3 Phase 0 の項目が見える。

## 作業ログ
- `build_dataset.py`: facilities 360件（shelter193/cool84/medical4/care79、位置不明はmedical4件）、
  areas 159町丁（65+ 112,734人／75+ 62,399人）、gaps 2件（barrier_free・medical）を出力。
  D5の人口集計は「本番」が町丁内の街区レベル内訳（大字コードが町丁と1対1）と判明したため
  大字コード単位で合算するよう修正
- `build_prototype.py` / `verify.py` を実装。fetch→build→build_prototype→verify が非ゼロ終了なしで通過
- ローカルHTTPサーバー越しにブラウザで実際に開いて目視確認（ヘッダ4数字・施設件数表・欠損パネル・
  出典一覧を確認。file://は成果物としては引き続き対応、確認用に一時サーバーを使っただけ）
- 実装計画の「Phase0完了=cool・barrier_freeの2ギャップ」と実データの食い違い、design-spec §8の
  reach「5値」と§4定義（4値）の食い違いをOPEN-ISSUES.mdに追記
