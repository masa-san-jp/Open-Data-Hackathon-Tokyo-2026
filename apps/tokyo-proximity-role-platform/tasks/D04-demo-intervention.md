---
id: D04
phase: demo
status: done
owner: bootstrap-agent
depends_on: [D03]
files:
  - templates/demo.html
  - data/demo/infrastructure.json
acceptance:
  - 小規模生活拠点(local_service_point)・Human Bridge・モビリティノード(mobility_stop)の3介入を仮置きできる
  - 仮置きにより影響セルの実効到達時間が再計算される
  - 改善世帯数のBefore/Afterが表示される
  - 使用した仮定（ADR-0003/0005のパラメータ）が画面に表示される
  - 介入を削除すると元の状態に戻る（MAP-006）
verify:
  - make demo
  - python3 scripts/verify.py --phase demo --check intervention-revert
human_gate: false
---

## Work log

- agent: bootstrap-agent (Claude Code)
- started_at: 2026-08-23
- completed_at: 2026-08-23
- changed: templates/demo.html に3介入（local_service_point/human_bridge/mobility_stop）の仮置き・Before/After・容量制約（Human Bridge）を実装
- verified: python3 scripts/verify.py --phase demo --check intervention-revert（MAP-006通過）。ブラウザで小規模生活拠点を仮置き→Before/After確認→除去→ベースライン復帰を実操作確認
- evidence: verify.py出力、ブラウザ操作スクリーンショット（セッションログ参照）
- remaining: なし
