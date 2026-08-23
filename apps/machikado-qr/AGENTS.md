# まちかどQR 自律実装ハーネス

このファイルは `apps/machikado-qr/` 配下を変更する実装エージェント向けの強制手順である。人命・個人情報・誤誘導に関わるため、「動く」だけでは完了としない。

## 1. 最初に読む順序

1. `README.md` — 起動方法と現状
2. `../../docs/design/machikado-qr/20260823-machikado-qr-design-spec.md` — 要件の正本
3. `../../docs/design/machikado-qr/20260823-machikado-qr-implementation-plan.md` — フェーズとゲート
4. `TASKS.md` — 実行可能タスクと依存関係
5. `data/sources.json` と `data/build-report.json` — データの利用可否

矛盾時の優先順位は、設計仕様書の安全要件、`config.json`、実装計画、`TASKS.md`、README、コードコメントの順。矛盾を黙って解釈せず、`TASKS.md` の判断待ちに記録する。

## 2. 変更禁止の不変条件

次は、人間の明示承認と根拠資料なしに変更してはならない。

- 110・119は端末の `tel:` へ直接つなぎ、中継、LLM、受付APIを挟まない
- 緊急番号は押下直後に発信せず、住所を示す確認画面を1枚挟む
- デモモードから電話を発信しない
- 連絡先、帰る場所、閲覧位置を外部へ送信又はサーバー保存しない
- 不明な住所・座標・営業時間・設備情報を推定で補わない
- `candidate` を `installed` として表示又はQR発行しない
- `waypoint_guidance_public=false` の間、通常モードで点間歩行を指示しない
- 品質ゲートで隔離されたデータをUIに戻さない
- 場所コードの重複を許さない
- 生成物を直接編集しない

## 3. 自律実装ループ

1. `TASKS.md` で依存タスクがすべて `DONE` の最上位 `READY` を1件選ぶ
2. 対象を `IN_PROGRESS` にし、成果物、変更範囲、受け入れ条件を再確認する
3. 一つの縦切り変更として実装する。無関係なリファクタリングを混ぜない
4. `make verify` を実行する
5. 変更した要件ID、テスト結果、残存リスクを `TASKS.md` に反映する
6. 受け入れ条件を満たした場合だけ `DONE` にする。満たさなければ `BLOCKED` と理由を残す
7. PR本文に「変更」「検証」「安全・プライバシー」「未解決」を記載する

作業開始時と終了時に `git status --short` を確認し、他者の変更を上書きしない。

## 4. 許可されたコマンド

```bash
cd apps/machikado-qr
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
make verify
make demo
```

個別確認:

```bash
python3 scripts/build_points.py
python3 scripts/build_prototype.py
python3 scripts/verify.py
```

## 5. 編集箇所

| 目的 | 編集する正本 | 生成物 |
|---|---|---|
| UI・操作 | `src/index.template.html`, `src/styles.css`, `src/app.js` | `prototype/index.html` |
| データ変換 | `scripts/build_points.py`, `config.json`, `data/sources.json` | `data/points.json`, `data/build-report.json` |
| ビルド | `scripts/build_prototype.py` | `prototype/index.html`, `prototype/demo.html` |
| 要件 | 設計仕様書 | README、TASKS、コード |
| 計画・状態 | 実装計画、`TASKS.md` | なし |

`prototype/index.html`、`prototype/demo.html`、`data/points.json`、`data/build-report.json` は生成物。手編集は禁止。

## 6. 必須検証

すべてのPRで `make verify` を成功させる。変更種別に応じて追加する。

| 変更 | 追加検証 |
|---|---|
| UI文言・導線 | 375×667、390×844、拡大200%で主要操作が欠けないこと |
| 音声 | iOS SafariとAndroid Chromeで自動試行と手動ボタンの双方を確認 |
| 電話 | デモで不発信、通常モードで確認後だけ `tel:` が開くこと。110・119の実発信試験は禁止 |
| データ | 入力ハッシュ、除外件数、重複、隔離件数をレビューし、差分理由を記録 |
| 経路 | 実地検証記録がない限り公開フラグを有効化しない |
| 保存 | DevToolsのNetworkで送信ゼロ、保存キーが `machikadoQr:` 名前空間内であること |

端末実機を使えない場合はタスクを `DONE` にせず、`BLOCKED` 又は `HUMAN_REVIEW` とする。

## 7. 人間へ停止・確認する条件

次に該当したら自律判断で進めない。

- 110・119、警察、消防、医療機関との運用又は表現を変える
- 実在店舗を設置済みとして公開する
- 個人情報をサーバー、分析基盤、ログ、LLMへ送る
- 外部API、Cookie、広告、アクセス解析を追加する
- データの利用条件又は帰属表示が確認できない
- 距離閾値、安全メッセージ、対象者を根拠なしに変更する
- 位置コードを既設ステッカーとの互換性確認なしに変更する
- 公開URLへのデプロイ、独自ドメイン、費用発生、外部アカウント作成が必要になる
- 現地検証を完了扱いにする

## 8. 完了定義

タスクは次をすべて満たした場合だけ完了。

- 要件IDと変更ファイルが追跡可能
- 受け入れ条件を自動テスト又は実機記録で証明
- `make verify` 成功
- データ件数の差分を説明
- 安全・プライバシー不変条件を維持
- ドキュメント、生成物、テストが同一コミットにある
- 未検証事項を成功扱いにしていない

## 9. PR本文テンプレート

```markdown
## 変更
- 対応タスク: MQR-xxx
- 対応要件: FR-xx / NFR-xx

## 検証
- `make verify`: PASS / FAIL
- 実機: 端末・ブラウザ・結果、又は未実施理由
- データ差分: 候補地点 / 表示地点 / 隔離件数

## 安全・プライバシー
- 電話経路:
- 外部送信:
- 候補地と設置済みの分離:

## 未解決
- なし、又は追跡タスクID
```
