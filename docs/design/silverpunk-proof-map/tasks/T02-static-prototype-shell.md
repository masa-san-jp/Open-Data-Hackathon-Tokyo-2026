---
id: T02
phase: 1
status: done
owner: agent
depends_on: [T01]
files:
  - apps/silverpunk-proof-map/prototype/index.html
  - apps/silverpunk-proof-map/README.md
---

# T02 静的プロトタイプの殻を作る

## 目的

15分で起動できる、シナリオ・見出し・地区一覧・出典欄を持つ画面を作る。

## やること

- `demo-fixture.json` を HTML に埋め込むか、file:// でも動く方式で読み込む
- `heat_disaster` シナリオの説明、基準日、データ状態を表示する
- 3地区以上をカードまたは表で表示する
- 列見出しまたはボタンで少なくとも優先候補・高齢化率・欠損数を並べ替える
- `verified`、`illustrative`、`missing` をラベルとテキストで区別する
- 外部 CDN、外部 API、ログイン、ビルドツールを追加しない

## 完了条件

- `file://.../prototype/index.html` で開く、またはローカル HTTP で開く
- コンソールエラーがない
- 390px 幅でも一覧とシナリオ操作ができる
- 画面内の数値と文章が JSON または出典台帳から来ている

## フォールバック

並べ替えが難しい場合は、固定順の一覧を先に出し、未実装操作を隠さず T06 の残課題に書く。ただし Phase 1 完了前には最低1種類の並べ替えを実装する。

## 実施記録（2026-08-23）

変更: `apps/silverpunk-proof-map/prototype/index.html`（単体HTML。fixtureを`<script type="application/json">`に埋め込み）。
検査: `python3 scripts/verify.py --phase 1` 終了コード0。ブラウザで開き、コンソールエラーなしを確認。
観測: 4地区一覧、優先度/高齢化率/支援拠点数/未確認欠損数の4種類の並べ替えボタンが動作。verified/illustrative/missing等の状態をバッジ（アイコン+色+テキスト）で区別して表示。
残課題: なし（T03 へ引き渡し済み）。

