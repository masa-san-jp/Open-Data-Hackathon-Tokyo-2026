# AGENT.md — エージェント向け 作業規約（living-zone-navi）

**着手する前にこの1枚を読む。** 次に `20260823-design-spec.md`、それから `tasks/` の担当分。
姉妹アプリ `apps/tokyo-aging-stress-test/AGENTS.md` と同じ規約体系。差分だけ覚えればよい。

## 0. ミッション（1文）

東京都オープンデータだけを使い、1つの区を対象に「高齢者が徒歩でシェルター・医療・福祉に届くか／届かないか／**データが無くて分からないか**」を、ブラウザで開くだけのHTMLとして可視化する。

## 1. 進め方（タスクプロトコル）

1. `docs/design/living-zone-navi/tasks/` から **status: todo の最小番号**を取る
2. そのファイル先頭を `status: doing` に書き換えて**先にコミット**（衝突防止）
3. `apps/living-zone-navi/` に実装する（無ければ T01 が骨組みを作る）
4. `python3 apps/living-zone-navi/scripts/verify.py` が通るまで終わらない
5. `status: done` にして、何をしたかを1〜3行タスク末尾に追記してコミット

複数のエージェントと人が同時に触る前提：

- 触るのは自分のタスクが名指ししたファイルだけ
- `git pull --rebase` してから push
- コミットは小さく。**main は常にデモ可能**（`prototype/index.html` が開ける状態）を壊さない

## 2. 守ること（このプロジェクト固有）

- **数字を作らない。** 座標が無い施設をジオコーディングで補わない。「位置不明 n件」として画面に出す
- **欠けを消さない。** クーリングシェルターODが無い区は「未公開」、バリアフリー線データは「未整備・確認が必要」と表示する。これは欠陥ではなく**本作品の主張**（欠損マップ）
- **直線距離は近接の代理指標。** 画面に「直線距離であり経路距離ではない」と必ず明記。経路計算はスコープ外
- **LLMにデータを直接加工させない。** 変換はすべて決定論的コード。LLMが使えるのは仕様・コードの生成まで
- **外部CDN・外部APIを画面から呼ばない。** `prototype/index.html` は file:// で開けること。地図はSVG自前描画（design-spec §5）
- **データURLはカタログから解決する。** URLを想像で書かない。`docs/research/data/東京都オープンデータ全カタログ_9678件_20260704.csv`（列: タイトル/概要/カテゴリ/所管/形式/データセットURL/リソースURL(先頭)/リソース数/更新日）をタイトル検索して取得先を決め、`data/sources.json` に URL・取得日・ハッシュを記録する
- **verify.py の固定点を、通すために書き換えない。** 落ちたら公開元の変化を調べ、`OPEN-ISSUES.md` に書いてから直す
- **個人名・個人情報を入れない。** 公開リポジトリである

## 3. 「できた」と言ってよい条件

```
python3 apps/living-zone-navi/scripts/fetch_sources.py && \
python3 apps/living-zone-navi/scripts/build_dataset.py && \
python3 apps/living-zone-navi/scripts/verify.py
```

3本とも非ゼロ終了なし。加えて **`prototype/index.html` を実際にブラウザで開き、そのフェーズの完了条件（実装計画 §3 の表）が目で見えること**。「実装した」は完了ではない。**開いて見えた**が完了。

## 4. 詰まったとき

- 取得403: ①カタログのAPI・機械向けの口を探す ②User-Agent をブラウザ相当に ③それでも駄目なら手動DLして `data/raw/` に置き `sources.json` に手動と記録
- HTTP 200 でも中身がHTMLエラーページのことがある。**サイズと先頭行を必ず検査**
- 対象区（既定: 江東区）のデータが欠けるときは実装計画 §4 のフォールバック表に従う。**判断に迷ったら想像で埋めず `OPEN-ISSUES.md` に1行足して、現時点で出せる形を出す**
- 仕様の矛盾を見つけたら、design-spec を直すのではなく `OPEN-ISSUES.md` に書く（仕様変更はオーナー判断）

## 5. 環境

- Python 3 標準ライブラリのみ（`urllib.request` / `csv` / `json` / `math` / `hashlib`）。pip install しない
- 出力は `data/processed/*.json` と `prototype/index.html`（`build_prototype.py` が生成）
- 文字コード: 入力は Shift_JIS/CP932 の CSV があり得る。`encoding='cp932'` フォールバックを必ず入れる
