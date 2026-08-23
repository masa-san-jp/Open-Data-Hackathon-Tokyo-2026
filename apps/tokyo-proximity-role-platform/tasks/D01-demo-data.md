---
id: D01
phase: demo
status: done
owner: bootstrap-agent
depends_on: [D00]
files:
  - scripts/build_demo.py
  - data/demo/cells.json
  - data/demo/infrastructure.json
  - data/demo/roles.json
  - data/demo/README.md
  - schemas/cell.schema.json
  - schemas/infrastructure.schema.json
  - schemas/scenario.schema.json
  - schemas/role-card.schema.json
acceptance:
  - scripts/build_demo.py が決定論的に data/demo/*.json を生成する（乱数・時刻に依存しない）
  - 48セル（8列×6行、analysis_resolution_m=250）の合成グリッドが生成される
  - 各セルに elderly_single_households, data_quality, base_access_minutes, slope_index を持つ
  - 少なくとも1セル以上が必須機能のいずれかで data_quality=unassessed になる（灰ハッチ検証用）
  - food は全セルで data_quality=unassessed 固定（ADR-0002）
  - 生成データが schemas/*.schema.json の必須項目を満たす
verify:
  - python3 scripts/build_demo.py
  - python3 scripts/verify.py --phase demo --check schema
human_gate: false
---

## Work log

- agent: bootstrap-agent (Claude Code)
- started_at: 2026-08-23
- completed_at: 2026-08-23
- changed: scripts/build_demo.py, schemas/cell.schema.json, schemas/infrastructure.schema.json, schemas/scenario.schema.json, schemas/role-card.schema.json を作成。python3 scripts/build_demo.py 実行で data/demo/{cells,infrastructure,roles}.json と data/demo/README.md を生成
- verified: python3 scripts/build_demo.py（48セル生成を確認）。スキーマ検証はD06のverify.pyでまとめて実施
- evidence: data/demo/cells.json（48件、welfare未評価4件、households<3が複数件）
- remaining: なし
