# 東京10分生活圏・地域役割プラットフォーム エージェントハーネス

この文書は、新規アプリ `apps/tokyo-proximity-role-platform/AGENTS.md` として転記できる実行規約である。

## 0. 目的

複数の実装エージェントが、データや制度を推測で補わず、地図系統と地域役割系統を段階的に完成させる。

エージェントは自律的にタスクを選択・実装・検証できる。  
ただし、データの真偽、法的区分、採否、本人意思を自律的に確定してはならない。

---

## 1. 読む順番

着手前に必ず次を読む。

1. `AGENTS.md`
2. `SPEC.md`
3. `IMPLEMENTATION.md`
4. `DECISIONS.md`
5. `OPEN-ISSUES.md`
6. `tasks/index.yaml`
7. 担当タスクファイル

優先順位:

```text
SPEC.md
  > IMPLEMENTATION.md
  > DECISIONS.md
  > タスクファイル
  > コードコメント
```

矛盾した場合は上位文書に従い、下位文書を直す。  
仕様にない重要判断をコードへ埋め込まない。

---

## 2. エージェントの役割

| role | 責任 | 触ってよい範囲 |
|---|---|---|
| `orchestrator` | タスク選択、依存確認、進捗集約 | tasks、ログ。製品コードは原則編集しない |
| `data-auditor` | 出典、ライセンス、スキーマ、カバー率 | data/catalog、scripts/audit、reports |
| `geo-engineer` | 道路、標高、到達時間 | pipeline、scripts、geo tests |
| `frontend-agent` | 地図UI、条件切替、詳細パネル | prototype、web、UI tests |
| `scenario-agent` | 施設・Human Bridge・モビリティ介入 | scenario schema、engine、tests |
| `role-agent` | 役割カード、テンプレート、制度候補 | schemas、role data、api、tests |
| `qa-agent` | 受入試験、ブラウザ確認、スクリーンショット | tests、reports。仕様を勝手に緩和しない |
| `reviewer` | 差分レビュー、事実・安全性検査 | 原則レビューのみ |

1タスクに複数エージェントを置かない。  
複数タスクが同じファイルを編集する場合は並列実行しない。

---

## 3. タスク状態

```text
blocked → ready → claimed → doing → review → done
                         ↘ blocked
```

タスクファイル先頭:

```yaml
---
id: D03
phase: demo
status: ready
owner:
depends_on: [D02]
files:
  - templates/demo.html
  - scripts/build_demo.py
acceptance:
  - 5/10/15分の切替でセル色が変わる
verify:
  - make verify-demo
---
```

### 3.1 取得手順

1. `git pull --rebase`
2. `tasks/index.yaml` から `status: ready` かつ依存完了の最小IDを選ぶ
3. タスクの `owner` と `status: claimed` を更新
4. **claimだけを先にコミット**
5. ブランチ名を `agent/<task-id>-<slug>` にする
6. 実装開始

claimコミット例:

```text
chore(tasks): claim D03 demo controls
```

### 3.2 完了手順

1. タスク固有の検証
2. `make verify`
3. ブラウザ実確認
4. スクリーンショットまたはテスト証跡
5. タスク末尾へ作業ログ
6. `status: review`
7. reviewerが確認
8. `status: done`
9. `git pull --rebase`
10. push

---

## 4. 自律実行ループ

```text
OBSERVE
  リポジトリ状態、仕様、タスク、検証結果を読む
    ↓
SELECT
  依存が満たされた最小タスクを1件選ぶ
    ↓
CLAIM
  タスクを先にロックする
    ↓
PLAN
  変更ファイル、検証、停止条件を3〜7行で記録
    ↓
IMPLEMENT
  担当ファイルだけ変更
    ↓
VERIFY
  タスク検証 → 全体検証 → ブラウザ確認
    ↓
REVIEW
  事実、仕様、安全性、差分範囲を検査
    ↓
COMMIT
  ログを残して完了
```

同じ失敗を3回繰り返したら自動ループを停止し、`OPEN-ISSUES.md` に記録して `status: blocked` に戻す。

---

## 5. 事実性ルール

### 5.1 データ

- 数字を作らない
- 存在確認と利用可能性を分ける
- 全都カバー未監査なら「全都」と書かない
- 欠損を0として処理しない
- 未評価は灰ハッチ
- デモデータは `demo=true`
- 画面に `DEMO DATA` を表示
- デモ値をREADMEの事実へ転記しない

### 5.2 歩行モデル

- 直線距離を道路徒歩時間と表示しない
- 勾配係数を実測値と偽らない
- 使用モデルとパラメータを保存
- 速度低下で到達範囲が増えたらテスト失敗
- 5→10→15分で充足セルが減ったらテスト失敗

### 5.3 地域役割

- AI生成直後は必ず `draft`
- AIは契約形態、労働者性、福祉サービス適合を確定しない
- AIは採否を決めない
- 診断名や生バイタルを役割提供者へ渡さない
- 制度候補には理由と `human_review_required` を付ける

---

## 6. 変更範囲

- タスクの `files` にないファイルを変更しない
- 必要ならタスクを分割してから変更する
- 生成物を直接編集しない
- `prototype/index.html` は `scripts/build_demo.py` または `scripts/build_prototype.py` から生成する
- rawデータを編集しない
- `verify.py` の期待値を通すためだけに書き換えない
- 仕様変更は `DECISIONS.md` にADRとして記録する

---

## 7. 検証コマンド

最低限:

```bash
make doctor
make demo
make verify-demo
```

M1以降:

```bash
make fetch-m1
make build-m1
make verify-m1
```

地域役割:

```bash
make test-role
```

全体:

```bash
make verify
make screenshot
```

「実装した」は完了ではない。  
**コマンドが通り、ブラウザで開き、画面を確認した**ことを完了条件とする。

---

## 8. 受入検査チェック

### 地図

- [ ] 5/10/15分で色が変化する
- [ ] 歩行速度が反映される
- [ ] 勾配ON/OFFが反映される
- [ ] 未評価が赤にならない
- [ ] 凡例が常時見える
- [ ] セル詳細に対象世帯数、時間、不足、出典がある
- [ ] 介入を削除すると元へ戻る
- [ ] Before/Afterの前提が表示される

### 地域役割

- [ ] 地域課題に紐づく
- [ ] 作業単位へ分解されている
- [ ] 時間、身体負荷、監督、報酬要否がある
- [ ] 制度候補が複数表示可能
- [ ] 最終承認が人間
- [ ] AIがapprovedにできない
- [ ] 個人の診断名を要求しない

### デモ

- [ ] 外部APIなしで開く
- [ ] デモデータ表示がある
- [ ] 1366×768で操作できる
- [ ] 60秒の操作手順を再現できる
- [ ] スクリーンショットを生成した

---

## 9. エスカレーション

次の場合は推測せず停止する。

- データのライセンスが不明
- 全都カバーか判断できない
- 座標・住所列が解釈できない
- 法的区分により実装が変わる
- 個人情報項目を追加する必要がある
- 仕様の優先順位が競合する
- 同じ検証失敗が3回続く

記録形式:

```md
## BLOCKER-YYYYMMDD-NN

- task:
- observed:
- attempted:
- evidence:
- decision_needed:
- safe_fallback:
```

safe fallbackがあれば、未実装表示のまま他タスクを進める。

---

## 10. ADR

重要判断は `DECISIONS.md` へ追加する。

```md
## ADR-0001: D0はSVGグリッドを採用

- status: accepted
- context:
- decision:
- alternatives:
- consequences:
- rollback:
```

次は必ずADR対象:

- 分析メッシュサイズ
- 道路データ
- 標高データ
- 歩行・勾配モデル
- 必須生活機能
- 優先地域判定
- Human Bridge容量
- 制度ルーティングルール
- 個人情報項目

---

## 11. 作業ログ

各タスク末尾:

```md
## Work log

- agent:
- started_at:
- completed_at:
- changed:
- verified:
- evidence:
- remaining:
```

「remaining」がある場合、隠さず `OPEN-ISSUES.md` へ転記する。

---

## 12. オーケストレータ用プロンプト

```text
あなたは tokyo-proximity-role-platform の実装オーケストレータです。

1. AGENTS.md、SPEC.md、IMPLEMENTATION.md、DECISIONS.md、
   OPEN-ISSUES.md、tasks/index.yaml を読む。
2. 依存が完了している ready タスクの最小IDを選ぶ。
3. 他タスクと編集ファイルが競合しないことを確認する。
4. タスクをclaimedにし、claimコミットを作る。
5. 担当エージェントへ、変更可能ファイル、受入条件、検証コマンド、
   禁止事項を渡す。
6. 実装後、qa-agentとreviewerを実行する。
7. make verify とブラウザ確認が通らなければdoneにしない。
8. 不明点を推測で埋めず、BLOCKERとして停止する。
```

---

## 13. レビューア用プロンプト

```text
この変更を次の順でレビューしてください。

1. タスク外ファイルを変更していないか
2. SPECの受入条件を満たすか
3. デモデータと実データを混同していないか
4. 欠損を0または未充足として扱っていないか
5. 歩行速度・閾値・勾配の単調性テストがあるか
6. AIが法的判断・採否・approved状態を作っていないか
7. 個人の診断名・生バイタルを要求していないか
8. make verify が通るか
9. ブラウザ実確認と証跡があるか

重大度を blocker / major / minor に分けて返してください。
blockerが1件でもあればdoneを拒否してください。
```
