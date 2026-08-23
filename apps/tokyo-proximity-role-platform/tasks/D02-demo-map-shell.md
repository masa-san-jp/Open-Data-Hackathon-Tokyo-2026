---
id: D02
phase: demo
status: done
owner: bootstrap-agent
depends_on: [D01]
files:
  - templates/demo.html
  - scripts/build_prototype.py
  - prototype/index.html
acceptance:
  - prototype/index.html がダブルクリックまたは python3 -m http.server でオフライン表示できる
  - 外部API・CDンへの参照がない
  - DEMO DATA / NOT FOR POLICY DECISION が常時表示される
  - SVGグリッドで48セルが描画され、凡例（青/黄/橙/赤/灰ハッチ/薄灰）が常時見える
  - 分析単位（250m）が画面に表示される
verify:
  - make demo
  - grep -c "DEMO DATA" prototype/index.html
human_gate: false
---

## Work log

- agent: bootstrap-agent (Claude Code)
- started_at: 2026-08-23
- completed_at: 2026-08-23
- changed: templates/demo.html（SVGグリッド・凡例・DEMO DATAバナー）、scripts/build_prototype.py を作成
- verified: make demo、grep "DEMO DATA" prototype/index.html、Chromeで実際に開いて確認（http.server経由）
- evidence: docs/assets/proximity-role-demo.png、ブラウザ操作スクリーンショット（本タスクファイルには添付せず、コミットログ・会話記録を参照）
- remaining: なし
