---
id: M11B
phase: m1
status: review
owner: codex
depends_on: [M11]
files:
  - tasks/index.yaml
  - tasks/M11b-real-data-baseline.md
  - scripts/build_real_map.py
  - scripts/verify_real_map.py
  - scripts/screenshot_real_map.py
  - scripts/normalize_ome_sources.py
  - templates/real-map.html
  - Makefile
  - README.md
  - OPEN-ISSUES.md
  - DECISIONS.md
  - data/catalog.yaml
  - data/reports/source-audit-summary.md
  - prototype/real-map.html
  - data/normalized/ome/real_map.json
  - docs/assets/proximity-role-real-map.png
acceptance:
  - 正規化済みの青梅市データから実データHTMLを再生成できる
  - 生成物が「施設位置のみ」であり、徒歩時間・到達圏を主張しない
  - 境界、診療所・病院、介護サービス事業所の件数と出典が検証できる
  - 外部API・CDNなしで生成HTMLを開ける
  - オンライン時は表示専用の背景地図、失敗時は実座標グリッドへフォールバックする
  - 同じ入力から決定論的に同じ生成物を得られる
  - 1366×768のスクリーンショットを保存できる
human_gate: false
---

## Work log

- agent: codex
- started_at: 2026-08-23
- completed_at: 2026-08-23
- changed: 青梅市の正規化済み施設・境界データからprototype/real-map.htmlを再生成するビルダー、実座標グリッド・北矢印・2km縮尺・OpenStreetMap表示専用背景とオフラインフォールバック、標準ライブラリ検証器、データ品質表示（境界外座標の監査対象化）、安全なテキスト表示、スクリーンショット経路を追加
- verified: make doctor、make demo、make verify-demo、make real-map、python3 -m py_compile、ブラウザ実操作（レイヤー切替・施設詳細・コンソールエラーなし）、1366×768スクリーンショット
- evidence: docs/assets/proximity-role-real-map.png、data/normalized/ome/real_map.json、prototype/real-map.html
- remaining: 道路ネットワーク、標高DEM、人口・世帯との結合、徒歩到達圏計算は本タスクの対象外。M12/M13の人間承認・データ監査後に着手する。
