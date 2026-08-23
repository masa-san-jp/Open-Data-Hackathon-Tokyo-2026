---
id: D06
phase: demo
status: review
owner: bootstrap-agent
depends_on: [D04, D05]
files:
  - scripts/verify.py
  - scripts/screenshot.py
  - docs/assets/proximity-role-demo.png
acceptance:
  - make verify-demo が全チェックを通過する
  - ブラウザで実際に prototype/index.html を開いて確認する
  - スクリーンショットが docs/assets/proximity-role-demo.png に保存される
  - OPEN-ISSUES.md にD0完了ゲートのチェック結果が転記されている
human_gate: true
---

## Work log

- agent: bootstrap-agent (Claude Code)
- started_at: 2026-08-23
- completed_at: 2026-08-23
- changed: scripts/verify.py（schema/monotonicity/intervention-revert/reproducibility/role-card/static の6チェック）、scripts/screenshot.py を作成
- verified: make doctor / make demo / make verify-demo が全て成功。python3 scripts/screenshot.py で docs/assets/proximity-role-demo.png を生成。claude-in-chrome経由でprototype/index.htmlを実際に開き、閾値切替・セル選択・介入仮置き/除去・役割カード生成を操作確認。コンソールエラーなし
- evidence: docs/assets/proximity-role-demo.png、verify.py全通過ログ
- remaining: D0完了ゲート判定はOPEN-ISSUES.mdへ転記。human_gate=trueのため、本タスクのdone確定とM1着手可否はオーナー判断を待つ
