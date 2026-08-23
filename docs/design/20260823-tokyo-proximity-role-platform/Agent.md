# Agent Bootstrap — 東京10分生活圏・地域役割プラットフォーム

このディレクトリは、`apps/tokyo-proximity-role-platform/` を新規構築するための**実装開始パッケージ**である。
ここにある文書は議論メモではない。実装エージェントは、この文書群を読み、D0デモから順に自律実装する。

## 1. 文書の位置付け

| 文書 | 位置付け | 何を決めるか |
|---|---|---|
| [`20260823-tokyo-proximity-role-platform-design-spec.md`](./20260823-tokyo-proximity-role-platform-design-spec.md) | **要求・設計の正本** | プロダクト目的、地図系統と地域役割系統の責務、データモデル、UI、対象外、受入条件 |
| [`20260823-tokyo-proximity-role-platform-implementation-plan.md`](./20260823-tokyo-proximity-role-platform-implementation-plan.md) | **実装順序の正本** | D0→M1→M2→M3→R0→R1→R2の順序、タスクDAG、コマンド、テスト、フォールバック |
| [`20260823-tokyo-proximity-role-platform-agent-harness.md`](./20260823-tokyo-proximity-role-platform-agent-harness.md) | **エージェント運用規約の正本** | タスク取得、claim、変更範囲、検証、レビュー、停止条件、事実性・安全性のルール |
| `Agent.md` | **ブートストラップと読み順** | 最初のエージェントが何から着手し、どこで停止するか |

優先順位は次のとおり。

```text
設計仕様書
  > 実装計画
  > エージェントハーネス
  > 個別タスク
  > コードコメント
```

矛盾を発見した場合、下位文書やコードで独自解釈せず、`OPEN-ISSUES.md` に記録する。

## 2. 実装先

新規に次を作る。

```text
apps/tokyo-proximity-role-platform/
```

既存の次のアプリは変更しない。

```text
apps/tokyo-aging-stress-test/
```

既存アプリから再利用してよいのは、次の**運用パターン**だけである。

- `SPEC.md` / `AGENTS.md` / `tasks/` をコードの隣に置く
- 1タスク1責務で管理する
- 取得・構築・検証をスクリプト化する
- 数字を作らない
- 欠損を隠さない
- 生成物を直接編集しない
- 実際に画面を開くまで完了としない

既存アプリのデータ、指標、画面を新規アプリの事実として流用してはならない。

## 3. 最初のエージェントが行うこと

### Step 1: アプリ骨格を作る

以下を作成する。

```text
apps/tokyo-proximity-role-platform/
├── README.md
├── SPEC.md
├── IMPLEMENTATION.md
├── AGENTS.md
├── DECISIONS.md
├── OPEN-ISSUES.md
├── Makefile
├── tasks/
├── data/
├── schemas/
├── scripts/
├── templates/
├── prototype/
└── tests/
```

文書の移植方法:

- 設計仕様書を `SPEC.md` の初版とする
- 実装計画を `IMPLEMENTATION.md` の初版とする
- エージェントハーネスを `AGENTS.md` の初版とする
- このディレクトリの原文への相対リンクを各文書冒頭に残す

アプリ側の文書が作られた後は、**実行時の正本は `apps/tokyo-proximity-role-platform/` 側**とする。設計変更はアプリ側でADRを作成し、必要に応じてこの設計パッケージへ反映する。

### Step 2: D0タスクを作る

最低限、次のタスクを作成する。

```text
D00-scaffold
D01-demo-data
D02-demo-map-shell
D03-demo-controls
D04-demo-intervention
D05-demo-role-card
D06-demo-verify
```

各タスクには次を必須とする。

- `id`
- `phase`
- `status`
- `owner`
- `depends_on`
- `files`
- `acceptance`
- `verify`
- `human_gate`
- 作業ログ欄

### Step 3: D0デモを完成させる

最初の成果物は、次である。

```text
apps/tokyo-proximity-role-platform/prototype/index.html
```

必須機能:

1. 徒歩5分・10分・15分の切替
2. 歩行速度の切替
3. 勾配補正ON/OFF
4. 条件変更に応じたメッシュ色の変化
5. セル選択による不足機能・対象世帯・前提の表示
6. 小規模生活拠点、Human Bridge、モビリティの介入比較
7. 地域課題から地域役割カード下書きを1件生成
8. `DEMO DATA / NOT FOR POLICY DECISION` の常時表示

D0では合成データを使う。実在地域名・実在人数として表示しない。

### Step 4: 決定論的に検証する

最低限、次のコマンドを作る。

```bash
make doctor
make demo
make verify-demo
make screenshot
```

必須検査:

- 5分圏 ⊆ 10分圏 ⊆ 15分圏
- 歩行速度低下で到達範囲が増えない
- 勾配補正ONで上り所要時間が短くならない
- データ欠損を「未充足」に変換しない
- AI生成役割カードの状態は必ず `draft`
- AIは `approved` を作れない
- ブラウザで実際に画面が開く

### Step 5: 実データ監査へ進む

D0完了後、M1用データ監査を開始する。

データセットは、次を確認するまで本番利用不可とする。

1. 実ファイルを取得できる
2. スキーマを確認できる
3. 位置情報または再現可能な位置付与方法がある
4. 対象地域・カバー率が明確
5. 更新時点が明確
6. ライセンスが明確
7. 出典とチェックサムを保存できる

「東京都オープンデータカタログに存在する」だけでは利用可能と判定しない。

## 4. 自律実装してよい範囲

エージェントは確認なしに次を進めてよい。

- D0骨格の作成
- 合成データによるデモ
- JSON Schema、テスト、検証スクリプト
- オフライン地図UI
- 条件切替
- 介入比較のデモモデル
- 地域役割カードのテンプレートと下書きUI
- データレジストリと監査スクリプト
- 未決事項の記録

## 5. 人間承認が必要な事項

次は自律決定しない。

- 実データ対象地域の最終選定
- 道路・標高・民間POIデータの正式採用
- 歩行速度・勾配係数を政策判断に使うこと
- 東京都全域をカバーしたという表記
- 個人情報、GPS、健康情報の取得
- 契約形態、労働者性、最低賃金、請負・派遣の判断
- 障害福祉サービスとしての適合判断
- 求職者の採否
- 地域役割カードの最終承認
- 公開デプロイ

該当したら `needs-human` として停止する。

## 6. 禁止事項

- データを作る、補間して実測値と表示する
- 未評価セルを赤く塗る
- 直線距離を道路徒歩時間と表示する
- 合成データを実データと混在させる
- 求人サイトから先に作る
- AIに個人の適性・採否・制度区分を確定させる
- 診断名・生バイタルを役割提供者へ渡す設計にする
- 既存アプリを無断で変更する
- 検証を通すためにテスト条件を弱める

## 7. 最初の完了ゲート

次を全て満たしたらD0完了とする。

```text
[ ] 新規アプリの骨格がある
[ ] アプリ側SPEC/IMPLEMENTATION/AGENTSがある
[ ] D0タスクが依存順に定義されている
[ ] prototype/index.htmlが生成される
[ ] 5/10/15分、速度、勾配で表示が変わる
[ ] セルの不足理由が表示される
[ ] 3介入のBefore/Afterが表示される
[ ] 地域役割カードがdraftで生成される
[ ] make verify-demoが成功する
[ ] ブラウザ確認済み
[ ] スクリーンショットが保存される
[ ] OPEN-ISSUES.mdに未決事項が残されている
```

完了後、エージェントはD0を勝手に実データデモと呼ばず、M1データ監査の開始可否をオーナー判断へ上げる。

## 8. 最初の実行指示

```text
このディレクトリの4文書を読み、
apps/tokyo-proximity-role-platform/ を新規作成してください。
既存の apps/tokyo-aging-stress-test/ は変更しないでください。

最初はD0のオフラインデモだけを実装します。
合成データで、徒歩5/10/15分、歩行速度、勾配、セル詳細、
小規模生活拠点・Human Bridge・モビリティ介入、
地域役割カード下書きを動かしてください。

タスクを依存順にclaimし、各タスクの検証を通し、
prototype/index.htmlをブラウザで開き、スクリーンショットを保存してください。
不明点は推測せずOPEN-ISSUES.mdへ記録してください。
D0完了後は停止し、M1データ監査へ進む判断を求めてください。
```
