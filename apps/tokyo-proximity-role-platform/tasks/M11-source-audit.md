---
id: M11
phase: m1
status: review
owner: bootstrap-agent
depends_on: [M10]
files:
  - DECISIONS.md
  - data/catalog.yaml
  - OPEN-ISSUES.md
acceptance:
  - 対象地域が人間承認により正式決定している（ADR-0007がaccepted/rejectedに更新されている）
  - pharmacy・mobility_node・高齢単身世帯データのギャップに対する方針が決まっている
  - 道路・標高データの取得元が確認されている
human_gate: true
---

## Work log

- agent: bootstrap-agent (Claude Code)
- started_at: 2026-08-23
- completed_at: 2026-08-23
- changed: ADR-0007を青梅市確定（accepted）に更新。ADR-0008でM1初期の必須機能セット（clinic/welfareの2機能、
  pharmacy/mobility_nodeは未評価）を決定。OPEN-ISSUES.mdを更新
- verified: -
- evidence: DECISIONS.md ADR-0007/ADR-0008
- remaining: 道路網・標高DEMの正式採用は`Agent.md`§5により人間承認が必要で未着手。M12着手前に別途確認する。
  pharmacy・mobility_nodeの代替出典探索も未着手
