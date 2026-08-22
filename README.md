<!--
  提出フォーム項目とREADMEの対応メモ（公開情報のみ記載する方針）
  - 記載する : 1-1 チーム名 / 1-8 メンバー構成と役割 / 1-9 運用体制（任意） /
               2-1 課題の種類 / 2-2 作品名 / 2-3 サービスの詳細 / 2-4 着目した課題・背景 /
               2-5 解決方法 / 3-1 技術選定の理由 / 3-2 生成AI等の活用 / 3-7 ハードウェア有無 /
               4-1 利用データ一覧 / 5-2 画面キャプチャ
  - 条件付き : 3-3 デモURL（3-6が「はい」のときのみ）/ 3-8 デモ操作動画URL / 5-1 プレゼン資料（公開可なら）
  - 記載しない: 1-2〜1-7（個人情報・応募区分）/ 3-5 その他のURL（非公開指定）/ 6 収録日予約 / 7 同意事項
  - フォームは各310文字制限。READMEを原本として書き、フォームにはその要約を転記する。
-->

# 作品名（未定）

> 都知事杯オープンデータ・ハッカソン2026 応募作品 ｜ 課題の種類: 自由課題 / テーマあり（いずれかを残す）

<!-- TODO: サービスを1〜2文で。フォーム 2-3 の要約としてそのまま使える長さにする -->
（キャッチコピー・一行説明をここに）

## 目次

- [サービス概要](#サービス概要)
- [着目した課題・背景](#着目した課題背景)
- [解決アプローチ](#解決アプローチ)
- [デモ](#デモ)
- [スクリーンショット](#スクリーンショット)
- [利用オープンデータ](#利用オープンデータ)
- [技術構成と選定理由](#技術構成と選定理由)
- [生成AIの活用](#生成aiの活用)
- [セットアップ・実行方法](#セットアップ実行方法)
- [ディレクトリ構成](#ディレクトリ構成)
- [今後の展望・運用体制](#今後の展望運用体制)
- [チーム](#チーム)
- [ライセンス](#ライセンス)
- [調査資料](#調査資料-docsresearch)

## サービス概要

<!-- フォーム 2-3「サービスの詳細」の詳述版。誰が・何に困っているときに・何をすると・どうなるか -->
（TODO）

**主な機能**

- （TODO）
- （TODO）
- （TODO）

## 着目した課題・背景

<!-- フォーム 2-4。可能な限り一次データ・出典付きで。docs/research の調査レポートを引用できる -->
（TODO）

## 解決アプローチ

<!-- フォーム 2-5。課題のどこに効くのか、なぜその方法なのかを説明 -->
（TODO）

```mermaid
%% TODO: サービスの流れ／データフローを図示（不要なら削除）
flowchart LR
    A[オープンデータ] --> B[前処理・統合]
    B --> C[アプリケーション]
    C --> D[利用者]
```

## デモ

| 項目 | URL |
| :-- | :-- |
| デモサイト | （TODO / 一般公開が「いいえ」の場合はこの行を削除） |
| デモ操作動画（60秒以内） | （TODO / 未公開なら削除） |

> 審査用の非公開URLは README に記載せず、提出フォームの「その他のURL」欄にのみ入力する。

## スクリーンショット

提出フォーム 5-2 と同じ画像を `docs/assets/` に置き、下のコメントを外して使う（推奨 1600×900px, 最大3枚）。

<!--
| | |
| :--: | :--: |
| ![画面1](docs/assets/screenshot-01.png) | ![画面2](docs/assets/screenshot-02.png) |
| 画面1の説明 | 画面2の説明 |
-->

## 利用オープンデータ

<!-- フォーム 4-1。出典表示義務があるデータは必ずここに明記する -->

| # | データ名 | 提供元 | URL | 取得日 | ライセンス |
| :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | （TODO） | 東京都 | （TODO） | 2026-08-　 | CC BY 4.0 |
| 2 | （TODO） | （TODO） | （TODO） | 2026-08-　 | （TODO） |

- 東京都オープンデータカタログの全件一覧（9,678件・2026-07-04取得）は [`docs/research/data/`](docs/research/data) を参照。

## 技術構成と選定理由

<!-- フォーム 3-1。「何を使ったか」だけでなく「なぜそれを選んだか」を課題と結び付けて書く -->

| レイヤー | 採用技術 | 選定理由 |
| :-- | :-- | :-- |
| フロントエンド | （TODO） | （TODO） |
| バックエンド | （TODO） | （TODO） |
| データ処理 | （TODO） | （TODO） |
| インフラ・ホスティング | （TODO） | （TODO） |

**ハードウェアを含むか**: いいえ（含む場合はこの節に部品表と組立手順を追加）

## 生成AIの活用

<!-- フォーム 3-2（任意）。プロダクト内での利用と、開発プロセスでの利用を分けて書く -->

- **プロダクト内での利用**: （TODO）
- **開発プロセスでの利用**: （TODO）

## セットアップ・実行方法

```bash
git clone https://github.com/masa-san-jp/open-data-hackathon-tokyo-2026.git
cd open-data-hackathon-tokyo-2026
# TODO: 依存インストール・起動コマンド
```

**必要な環境変数**（`.env.example` をコピーして設定。秘密情報はリポジトリにコミットしない）

| 変数名 | 用途 |
| :-- | :-- |
| （TODO） | （TODO） |

## ディレクトリ構成

```text
.
├── docs/
│   ├── assets/     # スクリーンショット・図版
│   └── research/   # 事前調査レポート（下記）
└── ...             # TODO: アプリケーションのディレクトリ
```

## 今後の展望・運用体制

<!-- フォーム 1-9（任意）。誰が・どう継続運用するのか、実装しきれなかった構想を含めて -->
（TODO）

## チーム

**チーム名**: （TODO）

| 氏名 | 役割 |
| :-- | :-- |
| （TODO） | （TODO） |
| （TODO） | （TODO） |

> 連絡先は提出フォームでのみ提出し、README には記載しない。

## ライセンス

- ソースコード: （TODO: MIT など）
- ドキュメント・調査レポート: （TODO）
- 利用オープンデータ: 各データの提供元ライセンスに従う（[利用オープンデータ](#利用オープンデータ)を参照）

---

## 調査資料 (docs/research)

ハッカソンに向けた事前調査の置き場。

| ディレクトリ | 内容 |
| :-- | :-- |
| [`open-data-cases/`](docs/research/open-data-cases) | 世界のオープンデータ活用先駆事例（3本） |
| [`ai-agent-government/`](docs/research/ai-agent-government) | AIエージェントの行政活用・行政経営（3本） |
| [`reasoning-modes/`](docs/research/reasoning-modes) | アブダクション/演繹/帰納/生成AI推論の比較（3本） |
| [`quasi-public/`](docs/research/quasi-public) | 「準公共」概念の理論・制度・オープン性（3本） |
| [`population/`](docs/research/population) | 人口動態予測・人口移動・単身/未婚率、2100年の東京の一次情報整理（7本） |
| [`urban-planning/`](docs/research/urban-planning) | 都市計画の歴史と未来、15分都市（2本） |
| [`data/`](docs/research/data) | 東京都オープンデータ全カタログ 9,678件（CSV, 2026-07-04取得） |

### open-data-cases

- [世界のオープンデータ活用 先駆事例調査 ― 東京都の「好循環エコシステム」設計への示唆](docs/research/open-data-cases/20260806-global-open-data-pioneer-cases-tokyo-ecosystem.md)
- [オープンデータがつくる都市と社会の好循環：リアル・バーチャル・社会彫刻を横断するグローバル先進生態系の解析](docs/research/open-data-cases/20260806-open-data-virtuous-cycle-real-virtual-social-sculpture.md)
- [世界のオープンデータ活用先駆事例と仮想世界・社会実験・社会彫刻・アートの横断分析](docs/research/open-data-cases/20260806-global-open-data-pioneers-virtual-worlds-civic-art-tokyo-strategy.md)

### ai-agent-government

- [AIエージェントによる行政サービスデザイン・行政経営の世界事例調査](docs/research/ai-agent-government/20260806-ai-agent-government-service-design-global-cases-briefing.md)
- [AIエージェントを用いた行政サービスデザインと行政経営の世界事例調査](docs/research/ai-agent-government/20260806-global-ai-agents-public-service-design-administration-report.md)
- [自律型AIエージェントによる行政サービスデザインと行政経営の世界的進化](docs/research/ai-agent-government/20260806-autonomous-ai-agents-public-service-design-and-management.md)

### reasoning-modes

- [4つの推論様式の比較検証とデータ活用ソリューション開発への応用](docs/research/reasoning-modes/20260806-four-reasoning-modes-comparison-data-solution-development.md)
- [三項推論と生成AIにおける知的メカニズムの比較解明](docs/research/reasoning-modes/20260806-triadic-reasoning-and-generative-ai-comparison.md)
- [比較検証：アブダクション推論、演繹法、帰納法、生成AIの推論](docs/research/reasoning-modes/20260806-systematic-comparison-abduction-deduction-induction-generative-ai-reasoning.md)

### quasi-public

- [「準公共」の比較分析レポート — 経済学の準公共財、デジタル庁の準公共分野、オープンデータ／オープンソースとの比較](docs/research/quasi-public/20260806-quasi-public-comparative-analysis-economics-digital-agency-open-data-oss.md)
- [準公共領域における制度設計論：公共・市場の比較構造とオープンデータ・オープンソースとの機能的相関分析](docs/research/quasi-public/20260806-semi-public-institutional-design-open-data-oss-correlation.md)
- [準公共概念の理論・制度・オープン性に関する比較研究](docs/research/quasi-public/20260806-quasi-public-concept-market-open-data-open-source-analysis.md)

### population

- [2100年の東京：一次情報中心の調査整理（環境・人口・都市機能・経済・住環境）](docs/research/population/20260822-tokyo-2100-primary-source-research.md)
- [2100年における地球・日本・東京の人口動態予測とその構造的影響](docs/research/population/20260813-global-japan-tokyo-population-2100-structural-impacts.md)
- [2100年の地球・日本・東京：人口動態予測](docs/research/population/20260813-global-japan-tokyo-population-projections-2100.md)
- [世界・日本・東京の人口動態予測（一次情報・影響因子・予測手法のディープリサーチ）](docs/research/population/20260813-global-japan-tokyo-demographic-projections-deep-research.md)
- [グローバル・日本・東京都における人口動態予測の包括的解析](docs/research/population/20260813-population-projection.md)
- [東京圏・地方間における人口移動の構造的変態と地域・年齢階層別動向](docs/research/population/20260813-tokyo-regional-population-migration-trends.md)
- [日本および東京都における単身構造・未婚率・無子率の動態分析と将来推計](docs/research/population/20260813-japan-tokyo-single-unmarried-rates.md)

### urban-planning

- [東京における都市計画の歴史的展開、現代的再編、ならびに2040–2050年代に向けた構造予測](docs/research/urban-planning/20260813-tokyo-urban-planning-history-and-future.md)
- [都市計画の変遷と「人中心」の未来：歴史的パラダイムシフトと日本版15分都市の構築](docs/research/urban-planning/20260813-urban-planning-human-centered-future-japan-15-minute-city.md)

---

各レポート冒頭の `> 原文: [Google Docs](...)` は変換元ドキュメントへのリンク。
