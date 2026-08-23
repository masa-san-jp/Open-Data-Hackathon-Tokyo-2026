---
id: D00
phase: demo
status: ready
owner: bootstrap-agent
depends_on: []
files:
  - README.md
  - SPEC.md
  - IMPLEMENTATION.md
  - AGENTS.md
  - DECISIONS.md
  - OPEN-ISSUES.md
  - Makefile
  - tasks/index.yaml
  - tasks/D00-scaffold.md
  - tasks/D01-demo-data.md
  - tasks/D02-demo-map-shell.md
  - tasks/D03-demo-controls.md
  - tasks/D04-demo-intervention.md
  - tasks/D05-demo-role-card.md
  - tasks/D06-demo-verify.md
  - data/catalog.yaml
acceptance:
  - apps/tokyo-proximity-role-platform/ の骨格ディレクトリが揃っている
  - README/SPEC/IMPLEMENTATION/AGENTS/DECISIONS/OPEN-ISSUESが存在する
  - tasks/index.yaml にD0〜D06が依存順に定義されている
  - make doctor が成功する
verify:
  - make doctor
human_gate: false
---

## Work log

- agent: bootstrap-agent (Claude Code)
- started_at: 2026-08-23
- completed_at: 2026-08-23
- changed: ディレクトリ骨格作成、README/SPEC/IMPLEMENTATION/AGENTS/DECISIONS/OPEN-ISSUES/Makefile/tasks/index.yaml/D00-D06タスクファイル/data/catalog.yaml を作成
- verified: make doctor
- evidence: 本タスクファイル
- remaining: なし
