# まちかどQR — ここはどこ

軒先のQRと印字住所を「位置が確定した点」として使い、迷った子ども・高齢者・外国人が、現在地を自分で説明できなくても助けを求められるようにする実証プロトタイプ。

現時点は **候補地データを使ったデモ** であり、実際にステッカーを設置したサービスではない。点から点への帰路案内も実地検証前のため、通常モードでは停止し、デモモードだけで挙動を確認できる。

## 30秒でデモを起動

追加インストールは不要。リポジトリを取得済みなら、次だけで起動できる。

```bash
cd apps/machikado-qr
python3 -m http.server 8000 --directory prototype
```

ブラウザで <http://localhost:8000/demo.html> を開く。

デモモードでは次を一巡できる。

1. 現在地の特大表示と音声読み上げ
2. 家族への発信確認（実際の電話は発信しない）
3. 帰る場所へ向かう「次の候補地点」の提示（実歩行禁止の表示あり）
4. 近隣の給水スポット表示
5. 110・119の確認画面（実際の電話は発信しない）
6. 日本語・ひらがな・英語・中国語・韓国語の切替

`make demo` でも同じサーバーを起動できる。終了は `Ctrl+C`。

## 通常モード

場所コードを指定して開く。

```text
http://localhost:8000/index.html?p=新宿0001
```

通常モードでは110・119と登録連絡先の `tel:` リンクが有効になる。実機確認時は誤発信を防ぐため、最初にデモモードを使うこと。

## ビルドと検証

生成済みHTMLはコミットしているため、デモを見るだけなら依存関係は不要。データ又は画面を変更して再生成する場合だけセットアップする。

```bash
cd apps/machikado-qr
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
make verify
```

`make verify` は次を順に行う。

- XLSX・CSVから候補地点と表示可能地点を再生成
- データ品質レポートを生成
- CSS・JavaScript・データを単体HTMLへ埋め込み
- Python / JavaScript構文検査
- 場所コード重複、データ隔離、デモ経路、外部リソース非依存などの自動テスト

正常終了の基準は `verification passed` と全テストの `OK`。

## 画面の原則

- 救助時の主操作では入力させない。入力は事前登録画面に分離する
- QRを読んだ直後に読み上げを試み、ブラウザが自動再生を止めても押せる音声ボタンを常設する
- 110・119は他の操作から離し、確認後に端末から直接発信する
- 連絡先と帰る場所は名前空間付き `localStorage` だけに保存し、外部へ送信しない
- 座標を推定補完しない。品質ゲートを通らないデータは隔離する
- 候補地・設置済み地点・廃止地点を混同しない

## データの状態

| 用途 | 出典 | 実行時の状態 | 件数 |
|---|---|---|---:|
| ステッカー設置候補 | 東京都総務局「都内災害時帰宅支援ステーション協力店舗一覧」 | 候補地としてデモのみ | 1,242 |
| 給水スポット | 東京都水道局「Tokyowater Drinking Station 一覧」 | 表示 | 827 |
| 駅 | 東京都デジタルサービス局「だれでも東京」交通 | 隔離 | 0 |

交通データは268行中110行が同一座標を共有することを検出した。現行の自治体近接判定だけでは誤案内を防げないため、別一次情報又は現地で照合するまで表示しない。詳細は [`data/build-report.json`](data/build-report.json) と [`data/sources.json`](data/sources.json)。

元の帰宅支援ステーション配布物は拡張子が `.csv` だが実体はXLSXであり、11,003行中、品質ゲートを通る候補地点は1,242行。範囲外座標9,738行、空行・不正値21行を除外する。

## 構成

```text
apps/machikado-qr/
├── AGENTS.md              # 自律実装ハーネス（正本）
├── CLAUDE.md              # Claude向け入口
├── TASKS.md               # 依存関係付き実装バックログ
├── config.json            # 品質ゲート・経路・デモ設定
├── data/
│   ├── sources.json       # 出典、利用状態、隔離理由
│   ├── build-report.json  # 入力ハッシュと品質検査結果
│   └── points.json        # 生成済みランタイムデータ
├── src/
│   ├── index.template.html
│   ├── styles.css
│   └── app.js
├── scripts/
│   ├── build_points.py
│   ├── build_prototype.py
│   └── verify.py
├── tests/test_pipeline.py
└── prototype/
    ├── demo.html           # デモ入口
    └── index.html          # 外部依存なしの生成物
```

生成物の `prototype/index.html` と `data/points.json` は直接編集しない。`src/`、`config.json`、`data/sources.json`、`scripts/`を変更して `make verify` で再生成する。

## 設計・実装管理

- [設計仕様書 v0.2](../../docs/design/20260823-machikado-qr-design-spec.md)
- [レビュー結果](../../docs/design/20260823-machikado-qr-review.md)
- [フェーズ別実装計画](../../docs/design/20260823-machikado-qr-implementation-plan.md)
- [実装タスク](TASKS.md)
- [残課題](OPEN-ISSUES.md)

## 現在の非目標

- 緊急通報の中継又は相談窓口の運営
- GPSによる継続追跡
- 自前の地図・経路探索
- 住所の自動ジオコーディング
- 未検証地点を使った実地歩行案内
- 候補店舗を「設置済み」とみなすこと

公開実証へ進む条件は、設置同意、設置済み台帳、剥離・廃止管理、経路の現地検証、アクセシビリティ試験、データ利用条件の再確認がすべて完了すること。
