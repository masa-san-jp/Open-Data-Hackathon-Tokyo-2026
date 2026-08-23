---
id: M11B
phase: m1
status: claimed
owner: codex
depends_on: [M11]
files:
  - tasks/index.yaml
  - tasks/M11b-real-data-baseline.md
  - scripts/build_real_map.py
  - scripts/verify_real_map.py
  - Makefile
  - README.md
  - prototype/real-map.html
  - data/normalized/ome/real_map.json
acceptance:
  - 正規化済みの青梅市データから実データHTMLを再生成できる
  - 生成物が「施設位置のみ」であり、徒歩時間・到達圏を主張しない
  - 境界、診療所・病院、介護サービス事業所の件数と出典が検証できる
  - 外部API・CDNなしで生成HTMLを開ける
  - 同じ入力から決定論的に同じ生成物を得られる
human_gate: false
---

## Work log

- agent: codex
- started_at: 2026-08-23
- completed_at:
- changed:
- verified:
- evidence:
- remaining: 道路ネットワーク、標高DEM、人口・世帯との結合、徒歩到達圏計算は本タスクの対象外。M12/M13の人間承認・データ監査後に着手する。
