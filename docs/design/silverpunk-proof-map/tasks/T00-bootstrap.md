---
id: T00
phase: 0
status: done
owner: agent
depends_on: []
files:
  - apps/silverpunk-proof-map/README.md
  - apps/silverpunk-proof-map/AGENTS.md
  - apps/silverpunk-proof-map/data/
  - apps/silverpunk-proof-map/evidence/
  - apps/silverpunk-proof-map/prototype/
  - apps/silverpunk-proof-map/scripts/
---

# T00 アプリ骨格と実行契約

## 目的

アプリ実装が始められる空の構成と、最小限の実行コマンドを作る。既存アプリは変更しない。

## 実装すること

- `apps/silverpunk-proof-map/` を作成する
- `README.md` に起動方法、Phase 1 のデモ範囲、未実装範囲を書く
- `AGENTS.md` に、プロジェクト内でのタスク取得・検証・引き渡し規約を書く
- `data/`、`evidence/`、`prototype/`、`scripts/`、`tasks/` を作成する
- `evidence/run-log.md` を初期化する

## やらないこと

- 実データの取得
- 画面の作り込み
- 外部ライブラリや API の追加

## 受け入れ条件

- `cd apps/silverpunk-proof-map && python3 -m http.server 8000` が起動する
- README に `python3 scripts/verify.py` を含む予定コマンドと、未実装であることが明記されている
- 既存の `apps/tokyo-aging-stress-test/` に変更がない

## 完了時の引き渡し

```text
[T00 done]
変更: アプリ骨格、README、AGENTS.md、run-log
検査: http.server 起動
観測: ディレクトリ構成と起動コマンドを確認
残課題: T01 が JSON fixture を追加する
```

## 実施記録（2026-08-23）

実装: `apps/silverpunk-proof-map/`（README.md, AGENTS.md, data/, data/raw/, data/normalized/, evidence/, prototype/, scripts/, tasks/）を作成。
検査: `python3 -m http.server` の起動確認（`curl` で200応答）。
観測: 既存 `apps/tokyo-aging-stress-test/` は無変更。詳細は `apps/silverpunk-proof-map/evidence/run-log.md` の該当エントリ。
残課題: なし（T01 へ引き渡し済み）。
