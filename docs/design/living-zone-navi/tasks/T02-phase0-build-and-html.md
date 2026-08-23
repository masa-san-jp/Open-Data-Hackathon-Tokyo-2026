status: todo
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
