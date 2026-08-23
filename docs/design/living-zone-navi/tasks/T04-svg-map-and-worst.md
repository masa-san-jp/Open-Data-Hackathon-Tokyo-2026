status: done
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

## 実施記録（2026-08-23）

- `scripts/build_prototype.py` を拡張し、町丁代表点・座標付き施設を同一スケールで投影した自己完結SVGを生成。
- 町丁円は75歳以上人口に比例し、涼み処のreach（near/far/out/unknown）を色で表示。施設は種別ごとの記号で表示し、各要素に町丁名・距離・施設名の`title`を付与。
- 涼み処が800m超の町丁を75歳以上人口順にワースト10表示し、判定不能の町丁数・人口を別掲。ヘッダにもout/unknown人口を表示。
- 欠損パネル、位置不明施設数、D1〜D6のURL・取得日をHTMLへ自動埋め込み。
- 検査: `python3 -m py_compile scripts/build_prototype.py`、`python3 scripts/build_prototype.py`、`python3 scripts/verify.py`、`git diff --check`。
- ブラウザ確認: SVG 1個、町丁158点、座標付き施設356点、ワースト10行を確認。コンソールエラーなし、インラインスクリプトのみで外部fetch/CDNなし。表示崩れなし。
