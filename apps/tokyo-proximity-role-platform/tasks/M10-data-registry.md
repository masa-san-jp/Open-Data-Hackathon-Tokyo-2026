---
id: M10
phase: m1
status: review
owner: bootstrap-agent
depends_on: [D06]
files:
  - schemas/source.schema.json
  - scripts/audit_sources.py
  - data/catalog.yaml
  - data/reports/source-audit.json
  - data/reports/source-audit-summary.md
acceptance:
  - schemas/source.schema.json がデータレジストリの必須項目を定義している
  - scripts/audit_sources.py が東京都オープンデータカタログAPIを機能コード×自治体で検索できる
  - data/catalog.yaml に検証済みソースが登録されている（production_readyは未確定のままfalse）
  - 「存在確認済み」と「利用可能」を区別した記録になっている
human_gate: false
---

## Work log

- agent: bootstrap-agent (Claude Code)
- started_at: 2026-08-23
- completed_at: 2026-08-23
- changed: schemas/source.schema.json、scripts/audit_sources.py を作成。青梅市を対象にカタログAPI検索を実行し
  data/reports/source-audit.json（機械的な検索結果）を生成。実ファイル（xlsx）を開いて手動検証した結果を
  data/reports/source-audit-summary.md にまとめ、data/catalog.yaml へ3件の検証済みソース＋2件のギャップを登録
- verified: python3 scripts/audit_sources.py --phase m1 --municipality 青梅市（実行成功、レポート生成確認）
- evidence: data/reports/source-audit.json、data/reports/source-audit-summary.md
- remaining: M11（対象地域の正式決定）はオーナー承認待ち。pharmacy/mobility_node/高齢単身世帯/道路/標高の
  ギャップはOPEN-ISSUES.mdに転記済み
