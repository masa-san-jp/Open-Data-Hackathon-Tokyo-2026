# Claude Design 提供状況 公式ドキュメント調査レポート

調査日: 2026-11-14
情報源: Anthropic公式サポート記事・Claude Code公式ドキュメントのみ（ニュース記事・ブログは根拠に使用していない）

## 1. 結論

- **Claude Designは現在利用できる。** Free / Pro / Max / Ultra / Team / Enterprise の各プランが対象（公式サポート記事）。
- **ただし形態が変わった。** スタンドアロン版（claude.ai/design）は **2026-12-14 に終了**（以降は読み取り専用、新規プロジェクト作成不可）。現在はClaude本体の会話内・Artifacts内の機能として提供されている。
- **Claude Codeからは `/design` と `/design-sync` で使える。** `/design` はv2.1.234以降が必要で、Claude Code側の公式記載ではFreeが対象外。

## 2. プラン別の可用性（公式記載）

| 項目 | 記載内容 | 出典 |
|---|---|---|
| Claude Design全般 | Free, Pro, Max, Ultra, Team, Enterprise で利用可 | サポート記事 A, B, C |
| Teamプラン | 既定で有効 | C |
| Enterpriseプラン | 2026-10-15 から既定で有効（その日以前はオーナーが Organization settings > Artifacts で有効化） | B, C |
| `/design` スキル（Claude Code） | Pro, Max, Team, Enterprise。v2.1.234以降。research preview | D |

### 公式ドキュメント間の食い違い
- サポート記事は「Freeを含む」と記載。Claude Code側の `/design` は「Pro, Max, Team, Enterprise」でFreeを列挙していない。
- 解釈: Claude Design本体（会話内）はFree対応、`/design`（CLI）はFree非対応と読むのが整合的。ただし公式がこの区別を明言しているわけではない。
- Enterpriseの管理設定は2系統あり、片方を有効にしてももう片方は有効にならない（C）。
  - 会話・Artifactsタブ用の「Design template」
  - スタンドアロン版の「Enable for your organization」

## 3. アクセス方法（公式記載, B）

- 会話内: Claudeにデザインを依頼する、またはメッセージ欄で Output > Design を選択
- Artifactsタブ: Designテンプレートを選択
- Claude Code: `/design`（作成・編集・同期）、`/design-sync`（デザインシステムの取り込み）
- iOS/Android: 依頼・編集・閲覧が可能。共有設定の変更はWeb/デスクトップのみ

## 4. スライド作成について

- 新規のデザイン・デザインシステム・スライドデッキはClaude内で**アーティファクトとして作成される**（A）。
- 「Get started」記事は作成物の例として、デザイン、インタラクティブプロトタイプ、one-pager等を挙げており、スライドデッキは明示列挙されていない（B）。
- **エクスポート形式**: .zip, PDF, PPTX, Google Slides, スタンドアロンHTML（B）
- 連携: Canva, Adobe系, Miro, Vercel, Netlify, Wix など。Claude Codeへのハンドオフも可能（B）
- 判断: スライド作成そのものは公式に言及があるが、スライド専用機能の詳細は今回の公式記事から確認できていない。実機で試す必要がある。

## 5. 利用上限・課金（B）

- Claude Designに別枠の利用上限はなく、Claude Codeを含むClaude全体で共通の上限を消費する。
- 上限到達時は、リセットまでClaude Designは利用不可。
- 利用クレジットを有効にしていれば、上限超過後も継続できる。
- プロジェクトのアーカイブ（zip）のエクスポートは無料で、利用上限にカウントされない（A）。

## 6. スタンドアロン版終了に伴う注意点（A, C）

- 終了日: 2026-12-14。以降は読み取り専用。
- 終了までに、プロジェクトとデザインシステムをClaudeへ移行する必要がある。
  - 移行できるのはプロジェクトのオーナーのみ。
  - デザインシステムはArtifactsページの「Move team design systems」から移行する。
- 移行できないもの: チャットとコメント（スタンドアロン版にのみ残る）。
- 空のデザインシステムや、組み込みスターターテーマ由来のものは移行されない。
- 公開リンクは終了後に無効化される。
- HIPAA対応構成の組織は、現時点で移行不可。
- 保持期間の間、誰も開かなかった移行済みプロジェクトは完全削除されうる。
- 移行機能は、有料プランへ段階的に展開中。

## 7. 既知の制限（B）

- バージョン履歴がない。
- インラインコメントが表示されないことがある（コメントビューには表示される）。
- 巨大なコードベースでは遅延やブラウザ問題が起きうる（Claude Code側から連携する）。
- 同時の複数人編集は基本的な機能にとどまり、不安定な場合がある。
- 取り込み品質は元データの品質に依存する。
- 要素（テキストレイヤー、アートボード、図形、メモ）の追加にはマウスかトラックパッドが必要。

## 8. 確認できなかった点

- ユーザー本人のアカウントのプランと、現時点での表示有無（公式情報からは判定不可）。
- スライド作成専用の詳細な仕様（レイアウト数、テンプレート等）。
- `/design` がFreeで使えるかの明確な記述。
- 確認方法: claude.aiの会話で Output > Design が選べるか、またはClaude Codeで `/design` を実行して確認する。

## 9. 出典（すべて公式）

- A: [Move from standalone Claude Design to Claude](https://support.claude.com/en/articles/17440474-move-from-standalone-claude-design-to-claude)
- B: [Get started with Claude Design](https://support.claude.com/en/articles/14604416-get-started-with-claude-design)
- C: [Claude Design admin guide for Team and Enterprise plans](https://support.claude.com/en/articles/14604406-claude-design-admin-guide-for-team-and-enterprise-plans)
- D: [Claude Code Docs: Week 34 (Aug 17-21, 2026)](https://code.claude.com/docs/en/whats-new/2026-w34)
- 参考（発表）: [Introducing Claude Design by Anthropic Labs](https://www.anthropic.com/news/claude-design-anthropic-labs)（今回は本文を取得していない）
