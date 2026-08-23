---
id: D03
phase: demo
status: done
owner: bootstrap-agent
depends_on: [D02]
files:
  - templates/demo.html
acceptance:
  - 5/10/15分の切替でセル色が変わる
  - 歩行速度プロファイル切替・数値入力で到達圏が変わる
  - 勾配補正ON/OFFでセルの実効時間が変わる
  - 歩行速度を下げても青セル数が増えない（MAP-002）
  - 5→10→15分で青セル数が減らない（MAP-001）
  - 勾配補正ONで実効時間が短くならない（MAP-003）
  - 未評価セルは常に灰ハッチ（MAP-004）
  - セルクリックで対象世帯数・各機能時間・不足理由・データ品質・前提が表示される
verify:
  - make demo
  - python3 scripts/verify.py --phase demo --check monotonicity
human_gate: false
---

## Work log

- agent: bootstrap-agent (Claude Code)
- started_at: 2026-08-23
- completed_at: 2026-08-23
- changed: templates/demo.html に閾値・速度・勾配コントロールと classify エンジンを実装
- verified: python3 scripts/verify.py --phase demo --check monotonicity（MAP-001/002/003/004通過）。ブラウザで5/10/15分・速度変更・セル選択を実操作確認
- evidence: verify.py出力（本タスクファイルおよびセッションログ参照）
- remaining: なし
