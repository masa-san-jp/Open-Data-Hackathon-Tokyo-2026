status: done
phase: 1

# T03 町丁位置の結合と reach 判定

## ゴール
areas の各町丁に lat/lon・nearest_m・reach が入る。

## やること
1. `fetch_sources.py` に D6（位置参照情報 大字・町丁目レベル 東京都 https://nlftp.mlit.go.jp/isj/ ）を追加。zipはstdlib `zipfile` で展開
2. `build_dataset.py`: D5の町丁名と D6 の大字町丁目名を正規化結合（NFKC・空白除去。**丁目の漢数字/算用数字ゆらぎに注意**）。結合率を meta に記録し、70%未満なら stderr に警告
3. haversine で各町丁→最寄り施設距離（kind別）→ reach 判定（near/far/out/unknown）
4. verify.py に「結合率」「reach 5値のみ」「緯度経度範囲」を追加

## 完了条件
verify 通過＋ dataset.json の areas に reach が入り、unknown の理由（D2欠損 or 位置不明）が gaps と整合。

## 作業ログ

## 実施記録（2026-08-23）

変更: `fetch_sources.py` に国土交通省D6（令和7年度ZIP）の検査・CSV展開を追加。`build_dataset.py` にNFKC＋空白除去＋丁目漢数字変換、町丁結合、haversine、種別別nearest/reachを追加。`verify.py` に結合率・町丁座標・reach/nearest整合性の検査を追加。
検査: `fetch_sources.py --check`、`build_dataset.py`、`verify.py` がすべて終了コード0。D6の結合は158/159町丁（99.4%）。未結合の潮見３丁目は欠損パネルへ記録。D1〜D4の距離判定を生成し、座標欠損のD3医療4件は全町丁unknownとして保持。
残課題: T04で生成データをSVG地図・ワースト表へ接続する。
