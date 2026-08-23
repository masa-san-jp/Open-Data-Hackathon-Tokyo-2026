# エージェント向け 作業規約（アプリ内）

**着手する前にこの1枚を読む。** 次に `docs/design/silverpunk-proof-map/AGENT.md`（設計側の詳細規約）、
それから `docs/design/silverpunk-proof-map/tasks/` の担当分。

## 1. 進め方

1. `docs/design/silverpunk-proof-map/tasks/` から依存が満たされた最小 ID の `status: ready` を1つ取る
2. タスクファイルの先頭を `status: doing` に変更する
3. 実装する（このディレクトリ配下、担当ファイルのみ）
4. `python3 scripts/verify.py` が通るまで終わらない
5. `status: done` にして、変更・検査・観測・残課題をタスクファイル末尾に追記する
6. `evidence/run-log.md` に実行コマンドと観測結果を追記する

## 2. 守ること

- **数字を作らない。** 出せない値は `null` と状態ラベル（`missing` / `not_verified` / `not_comparable` / `not_applicable` / `stale`）で表示する
- **`illustrative`（例示）と `verified`（実測）を混同しない。** `verified` を名乗るには出典 ID と取得日が要る
- **`not_computable` のスコアを順位計算に使わない**
- **2100年の値を公式予測として扱わない。** シナリオ・仮定と明記する
- **外部 CDN・外部 API を画面から呼ばない。** `prototype/index.html` は `file://` で単体で開けること
- **個人の健康・介護・位置履歴を保存・表示しない**
- **「危険」「安全」「避難できる」と断定しない。** 比較用の優先候補と現地確認の必要性を示す

## 3. 「できた」と言ってよい条件

```bash
python3 scripts/verify.py
```

が非ゼロ終了しないこと。加えて Phase 1 は `prototype/index.html` を実際にブラウザで開いて、
シナリオ切替・地区一覧・並べ替え・詳細・根拠・欠損・30日カードを目で見ること。
「実装した」は完了ではない。**開いて見えた**が完了。

## 4. 詰まったとき

- 仕様が足りないと思ったら、想像で埋めずに `evidence/run-log.md` に1行足して、現時点で出せる形を出す
- 地図・実データ取得・高度なスコアで詰まったら、カード・一覧・demo priority へ縮小して進める
- `blocked` にするのは、代替案を試しても外部状態または未決定事項のために推測なしで進められないときだけ

## 5. 現状

`docs/design/silverpunk-proof-map/tasks/README.md` の最短デモ経路 `T00 → T01 → T02 → T03 → T06` を参照。
進捗はこのファイルではなく設計側の `tasks/*.md` と `evidence/run-log.md` に記録する。
