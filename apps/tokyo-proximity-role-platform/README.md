# 東京10分生活圏・地域役割プラットフォーム

単身・高齢世帯が生活に必要な近隣機能（食・服薬・一次医療・福祉・交通）へ実効徒歩5/10/15分で届くかを可視化し、
不足地域の改善案（小規模生活拠点／Human Bridge／短距離モビリティ）を比較する「地図系統」と、
その不足を人が担える作業へ分解し既存の就労・福祉・地域参加制度へつなぐ「地域役割系統」を、
2系統に分けて段階実装するプロダクトです。

- 正本（要求・設計）: [`SPEC.md`](./SPEC.md)
- 正本（実装順序）: [`IMPLEMENTATION.md`](./IMPLEMENTATION.md)
- 正本（エージェント運用規約）: [`AGENTS.md`](./AGENTS.md)
- 決定記録（ADR）: [`DECISIONS.md`](./DECISIONS.md)
- 未決事項: [`OPEN-ISSUES.md`](./OPEN-ISSUES.md)
- 設計パッケージ原本: [`docs/design/20260823-tokyo-proximity-role-platform/`](../../docs/design/20260823-tokyo-proximity-role-platform/)

既存の `apps/tokyo-aging-stress-test/` とは別プロダクトです。データ・主張は混在させません。

## 現在のフェーズ

**D0完了 / M1準備中**。`make demo` で合成データのオフライン単一HTMLデモを再現できます。
青梅市については、`make real-map` で実座標の行政区域・施設点・座標グリッドを生成できます。
オンライン時はOpenStreetMapの表示専用背景を重ね、オフライン時はグリッドへ戻ります。徒歩時間・道路到達圏・人口按分は未実装です。
実在データ側にも政策判断用ではない旨を表示しています。

## クイックスタート

```bash
make doctor        # 実行環境の確認
make demo          # data/demo/*.json と prototype/index.html を生成
make serve-demo     # http://localhost:8000 でデモを開く（任意）
make verify-demo    # 決定論的な性質検査
make screenshot      # docs/assets/proximity-role-demo.png を生成
make real-map        # 青梅市の実データ施設位置マップを生成・検証
```

`prototype/index.html` は `python3 -m http.server` を使わずダブルクリックで直接ブラウザに開いても動作します（外部API・CDN不要、データはHTML内に埋め込み）。

## ディレクトリ

```text
tasks/       D0〜R2のタスク定義（依存順）
data/        catalog.yaml、demo/（合成データ）、raw/normalized/processed/methodology/reports（M1以降）
schemas/     JSON Schema（cell / infrastructure / scenario / role-card）
templates/   demo.html / real-map.html（ビルド前テンプレート）
scripts/     build_demo.py / build_prototype.py / verify.py / screenshot.py 等
prototype/   生成物。直接編集しない
tests/       検証スクリプト
```

## 自律実装の範囲

`AGENTS.md` §5 に従い、データの真偽・法的区分・採否・本人意思は自律確定しません。
該当する判断が必要になった場合は `OPEN-ISSUES.md` に `needs-human` として記録し、停止します。
