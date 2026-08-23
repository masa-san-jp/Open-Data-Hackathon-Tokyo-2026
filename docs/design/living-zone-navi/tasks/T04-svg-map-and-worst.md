status: todo
phase: 1

# T04 SVG地図・ワースト表・欠損パネル拡充

## ゴール
design-spec §5 の 2・3 が入り、Phase 1 完了条件を満たす。

## やること
1. `build_prototype.py`: 経緯度→viewBox の等座標スケーリングでSVG生成。町丁円（半径∝75+人口、色=reach 緑/黄/赤/灰）＋施設マーカー（kind別記号）。`<title>` ホバーで町丁名・距離
2. ワースト10表（pop_75plus × out で降順。unknown は除外し「判定不能 n町丁」を表の下に明記）
3. ヘッダに「800m以内に涼み処が無い75+ n人」「判定不能 n人」
4. 注記ブロック: 直線距離・位置不明件数・出典一覧（sources.json から自動生成）

## 完了条件
verify 通過＋ブラウザで実装計画 §3 Phase 1 の項目が見える。CDN・外部fetchゼロ（devtoolsのNetworkが空）。

## 作業ログ
