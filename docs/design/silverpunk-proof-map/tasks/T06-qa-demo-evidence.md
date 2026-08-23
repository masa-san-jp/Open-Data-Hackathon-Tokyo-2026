---
id: T06
phase: 1
status: ready
owner: unassigned
depends_on: [T03]
files:
  - apps/silverpunk-proof-map/evidence/run-log.md
  - apps/silverpunk-proof-map/README.md
  - apps/silverpunk-proof-map/prototype/index.html
---

# T06 QA・60秒デモ・実行証跡

## 目的

「コードがある」ではなく「実際に開いてデモができる」ことを確認し、次のエージェントが再現できる証跡を残す。

## 実装・確認すること

- `python3 scripts/verify.py` を実行する
- `python3 -m http.server 8000` または `file://` で画面を開く
- 390px と1440px相当の画面幅で確認する
- シナリオ、地区選択、並べ替え、欠損表示、30日カードを確認する
- キーボード Tab 操作、フォーカス表示、コンソールエラーを確認する
- 60秒デモの手順と観測結果を `evidence/run-log.md` に追記する

## 受け入れ条件

- 3地区以上が表示される
- 地区詳細、根拠、欠損、30日アクションが実際に操作できる
- 外部通信なしで表示できる
- 残課題がある場合、run log に隠さず残る

## フォールバック

ブラウザ自動検査が利用できない場合は、手動確認の日時・URL・確認項目を記録する。地図は未実装でも Phase 1 の完了を妨げない。
