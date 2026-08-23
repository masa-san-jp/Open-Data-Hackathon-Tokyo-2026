---
id: D05
phase: demo
status: done
owner: bootstrap-agent
depends_on: [D03]
files:
  - templates/demo.html
  - data/demo/roles.json
  - schemas/role-card.schema.json
acceptance:
  - 不足セル（黄/橙/赤）を選択し「地域役割に変換」から役割カード下書きを1件生成できる
  - 生成された役割カードは source_cell_id を持つ（ROLE-001）
  - task_units、schedule、functional_requirements、supervision、compensation_requiredが揃う（ROLE-002）
  - status は常に draft（ROLE-003）
  - route_candidates は複数提示可能（ROLE-004）
  - UI・ロジックのどこにも status を approved に設定するコードパスがない（ROLE-005）
  - カードに診断名・生バイタルの入力欄がない（ROLE-006）
verify:
  - make demo
  - python3 scripts/verify.py --phase demo --check role-card
human_gate: false
---

## Work log

- agent: bootstrap-agent (Claude Code)
- started_at: 2026-08-23
- completed_at: 2026-08-23
- changed: templates/demo.html に役割カード生成UI、data/demo/roles.json（承認済みテンプレートカタログ）、schemas/role-card.schema.json を実装
- verified: python3 scripts/verify.py --phase demo --check role-card / --check static（ROLE-001/002/004/005/006相当を通過）。ブラウザで薬局不足セルからROLE-0001を生成し編集を確認
- evidence: verify.py出力、生成されたROLE-0001（status=draft）のスクリーンショット（セッションログ参照）
- remaining: ROLE-003（AI生成直後は必ずdraft）はコード上status="draft"固定で担保。承認UIは意図的に未実装（ボタンはdisabled表示のみ）
