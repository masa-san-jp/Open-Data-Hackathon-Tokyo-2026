status: todo
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
