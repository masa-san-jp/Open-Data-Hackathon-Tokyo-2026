# 自律型AIエージェントによる行政サービスデザインと行政経営の世界的進化：実世界と仮想世界における実装と次世代ガバナンス

> 原文: [Google Docs](https://docs.google.com/document/d/1GIcd8nUS2b2oy64iz5FzW2XvWKCAoS984Jz8q9C2Mvk)

公的セクターにおけるデジタル技術の活用は、Webサイトの整備や各種手続きのオンライン化を中心とした電子政府（e-ガバメント）の段階を経て、大規模言語モデル（LLM）や自律型AIエージェントを基盤とする新たな行政経営のパラダイムへと移行しつつある。従来の生成AIが人間の入力したプロンプトに応じて単一のテキストや回答を出力する対話ツールにとどまっていたのに対し、最新の自律型AIエージェントは自らの置かれた環境を認識し、与えられた目的に向かってタスクを推論・計画し、外部データソースやシステムAPIと連携しながら独立して行動する「デジタル・チームメイト」として位置づけられている1。

この進化は、行政サービスデザインにおけるフロントエンドのインターフェース構造を本質的に変容させている。従来型の「市民が申請フォームを検索して入力するセルフサービス型」から、バックグラウンドでシステムが状況を検知して能動的に給付や手続きを行う「プッシュ型・見えない行政（Ambient Government）」への再構築が加速している2。さらに、こうしたAIエージェントの動態は、物理的な実世界の行政手続きのみならず、メタバースなどの仮想都市空間や、人間的相互作用と都市インフラを高度に結合させた「自律型都市デジタルツイン（Agentic Urban Digital Twins）」における政策シミュレーション領域にまで急速に広がっている3。本レポートは、世界各国で展開されている先進的な事例を網羅的に分析し、実世界および仮想世界におけるAIエージェントの実装実態と、それに伴う組織、ガバナンス、倫理的課題を解明するものである。

## 実世界における自律型行政エージェントの推進と行政経営の構造転換

### シンガポールにおけるGovTechのエコシステムと「デジタル・チームメイト」構想

シンガポール政府のデジタルサービス推進を担うGovTech（Government Technology Agency）は、AIエージェントを単なる問い合わせ対応のチャットボットではなく、複雑な定型業務を自動処理し、公務員が高度な戦略立案や市民支援に集中できるようにする「デジタル・チームメイト」として配置している1。GovTechのエコシステムは、相互に機能が補完された複数の専門エージェントと、それらを全政府規模で支える共通インフラストラクチャによって構成されている1。

市民や事業者とのフロントエンド対話を担う「VICA（Virtual Intelligent Chat Assistant）」は、60以上の政府機関において100以上の専門チャットボットとして導入されている1。自然言語処理と生成AI、各省庁の検証済みデータソースを組み合わせることで、単に既存のFAQを検索するだけでなく、市民が言葉にしていない後続の疑問や潜在的ニーズを予測して包括的な情報を提供する1。また、バックオフィスにおけるドキュメント解析を担当する「AISAY」は、人間の視覚・読解プロセスを模倣する知覚・自動化エージェントとして機能している1。非構造化文書から必要なデータを抽出・検証し、基幹システムへの入力データへと自動変換することで、手入力作業を徹底的に排除し手続き処理の大幅な迅速化を実現している1。

これらのエージェント群の迅速なデプロイと低コストでの運用を支えるのが、GovTechが開発した全政府共通のAI/MLOpsプラットフォーム「MAESTRO」である1。Amazon Web Services（AWS）との協働により構築されたMAESTROは、大規模言語モデルの運用コストパフォーマンスを大幅に改善し、ノーコード・ローコードのインターフェースを通じて各省庁でのAIモデル構築・監視を安全かつスケーラブルに実施することを可能にした6。たとえば、人材省（MOM）などの行政機関がMAESTROを活用して生成AI基盤のツールを短期間で試作・導入し、行政サービスの質の向上を図っている6。

市政課題への対応においては、市民がWhatsAppやTelegramなどの普及型メッセージングアプリを通じてインフラの破損や街区の清掃リクエストを行う「OneService Chatbot」が成果を上げている7。月間約30,000件にのぼる相談案件に対し、AIエージェントがテキストや画像から内容を予測・自動分類し、適切な担当省庁へ即座に自動ルーティングを行うことで、年間約2,000人時の業務削減とケース解決までに要する期間の最大2日短縮を達成した7。さらに、出産登録や育児手当の申請など15以上の機関横断的な手続きを単一のアプリで完結させる「Moments of Life」プラットフォームとの統合を進めることで、行政手続きに要する平均時間を70%削減させるなど、包括的な行政経営改革が進められている8。

GovTechはまた、AIエージェントの自律的な意思決定が引き起こし得る予期せぬリスクを制御するため、「Agentic AI向けモデルAIガバナンス・フレームワーク」を提示し、サンドボックス環境での技術的検証を強化している9。このサンドボックスでは、デジタルサービスの自動品質保証（QA）テストや自律型AIモデルの安全性試験のほか、社会福祉プログラムの受給申請において市民をナビゲートするエージェントの動作検証が行われており、過度な自律化による倫理的逸脱を防ぐ技術的・政策的ブレーキが組み込まれている1。

### エストニアにおけるBürokratt 2.0と「ゼロ・ビューロクラシー」の追求

電子国家として世界的な地位を確立してきたエストニアは、国家データ交換基盤「X-Road」とデジタルID基盤を最大限に活かし、従来の電子政府（e-Government）からAI主導型政府（AI-Government）、さらには適応的かつ能動的な意思決定能力を備えた「自律型国家（Agentic State）」への移行を強力に推進している2。その中核となるのが、情報システム庁（RIA）および経済通信省が主導する統合型AI仮想アシスタントネットワーク「Bürokratt」である2。

現在実装が進む次世代構造「Bürokratt 2.0」は、従来の「市民からの検索や申請を待つ受け身のポータルサイト」という概念を完全に覆し、リアルタイムのデータイベントをトリガーとする「イベント駆動型・プッシュ型サービスデリバリ」を実現する2。Bürokratt 2.0は個別のチャットボットではなく、X-Road上に分散された複数の専門AIエージェントが連携する統合エコシステムとして設計されている2。たとえば、海外の電子居住者（e-Resident）や国内中小企業において、事業者の年間売上高が法的な付加価値税（VAT）登録義務の閾値である40,000ユーロを超過した際、AIエージェントがリアルタイムでデータを検知する2。システムは事業者が自ら制度変更に気づくのを待つことなく、自動的にVAT登録申請書を作成・補正し、事業者の画面上に「ワンクリックで承認可能な状態」として提示する2。

この高度な自律処理の背後には、政府が市民や事業者に対して同じ情報を二度尋ねてはならないという「ワンスオンリー（Once-Only）」原則の法的徹底が存在する2。Bürokratt 2.0は省庁間のデータベースを自律的に照会・横断分析し、個々の事業者が利用可能な補助金、税制優遇、法改正に伴う遵守事項を自動で特定して能動的に通知を行う2。エストニア政府の試算によれば、このプッシュ型アプローチによって中小企業が定型的な行政手続きに費やす時間は約70%削減されると予測されている2。

このような自律型エージェントの深層化に伴い、エストニアではデータガバナンスと透明性の担保が厳格に制度化されている2。市民や電子居住者は「データトラッカー（Personal Data Usage Monitor）」を通じて、Bürokrattがいつ、どの機関の、どのような目的で自身の個人データにアクセスしたかのログを全履歴リアルタイムで確認・監査することができる2。さらに、2026年から完全適用される欧州連合（EU）の「AI法（EU AI Act）」において、公共セクターにおける一部の自動意思決定システムが「高リスク」に分類されることを受け、エストニア政府はアルゴリズムによる事前査定や通知作成はAIエージェントに委任しつつも、最終的な法的責任や権利制限を決定する「法的意志（Legal Intent）」は常に人間に留保する厳格なアーキテクチャを採用している2。

## 仮想世界とデジタルツイン領域における行政・政策シミュレーションの統合

### 仮想都市空間における行政サービスデザインとMetaverse Seoul

行政におけるAIエージェントの適用範囲は、物理空間での手続き自動化にとどまらず、メタバースに代表される仮想空間上の公共インフラ構築や市民エンゲージメント領域へと拡張されている3。その最も包括的な先行事例が、韓国のソウル特別市が展開する世界初の都市統合型メタバースプラットフォーム「Metaverse Seoul（メタバース・ソウル）」である3。

Metaverse Seoulは、経済、教育、税務、行政手続き、コミュニケーションの5つの基幹分野にわたる行政サービスを3D仮想空間上で統合している16。市民は自らのアバターを介して仮想市役所にアクセスし、アバター行政官やAIガイドと対話しながら、住民登録等本国証明書の発行、地方税のシミュレーションと納付、各種の不服申し立てや市民苦情の相談処理を完結させることができる3。また、物理的な制限を超えて市長室の仮想レプリカを訪問し、パブリックコメントの提示や自治体主催の各種コンテストへ直接参加することも可能となっている3。

仮想空間における行政展開にあたり、ソウル市は技術的利便性の向上だけでなく、倫理的ガバナンスの確立にも早くから着手してきた16。ソウルデジタル財団（SDF）と共同で制定された「メタバース倫理指針」は、「社会的公正」「尊重」「現実との接続」という3つの基本原則を定め、アバター間の不健全な接触や嫌がらせ行為に対する安全対策とデータプライバシーの保護規定を明文化している16。このような仮想領域への進出は、アラブ首長国連邦の「Sharjaverse」による仮想トランザクションセンターでの行政書類処理や、バルバドス政府による世界初の「メタバース大使館」開設を通じたデジタル領域における主権行使など、グローバルな行政デザインの標準となりつつある17。

### 自律型都市デジタルツイン（AUDiTs）とソーシャル・デジタルツイン（SDTs）

行政経営における最も革新的な技術的跳躍の一つとして挙げられるのが、従来の物理的な都市構造物を模倣するデジタルツインに、大規模言語モデルと人間行動モデルを統合した「自律型都市デジタルツイン（Agentic Urban Digital Twins: AUDiTs）」および「ソーシャル・デジタルツイン（Social Digital Twins: SDTs）」の台頭である4。従来の都市デジタルツインが主に地理空間データやIoTセンサーデータの視覚化に焦点を当てていたのに対し、AUDiTsは個別認識・行動推論機能を持つ無数の「AIエージェント市民」を仮想環境内に配置し、ミクロな人間行動が集積して生じるマクロな社会現象をシミュレーションする4。

このシステムの中核を成すのが、自然言語処理と空間認識モデルを統合した「自律型GISエンジン」および「データキュレーターエージェント」である5。データキュレーターエージェントは、オープンデータ、移動履歴、SNSの投稿データ、センサーストリームなどの異種多頭データを自律的に統合し、差分プライバシーや合成データ生成技術を用いてプライバシーを保護しながら、都市全体の高精度な合成人口（Synthetic Population）をリアルタイムで生成・更新する4。

この技術基盤の優位性は、政策担当者が複雑なコードや数式を用いることなく、自然言語による対話を通じて高度な政策「What-If（もし〜だったらどうなるか）」シミュレーションを実行できる点にある4。たとえば、スペインのラス・パルマス・デ・グラン・カナリアにおける都市モビリティ分析モデルでは、Gemini 2.5 Flash Liteを基盤とする対話型AIエージェントが政策立案者の「特定路線のバス運行頻度を15分間隔から10分間隔に変更した場合の交通渋滞および利用客の行動変化を示せ」といった自然言語の指示を即座に認識・解釈する23。対話エージェントは抽出したパラメータを構造化JSONデータへ変換して検証を行った上で、SimPy（離散イベントシミュレーション）、NetworkX、OSMnx（地理空間ネットワーク）で構成されるデジタルツインシミュレーションエンジンへ引き渡し、実行結果をリアルタイムで可視化・応答する23。

さらに、こうしたソーシャル・デジタルツインは、交通やエネルギーといったインフラ分野を超えて、高度に人間的な社会政策の不確実性を制御するツールとしても機能している4。ノルウェーのクラゲリョ（Kragerø）市で実証されている若年層の中退問題に対する政策シミュレーションや、先端AI技術（DeepSeek等）の社会実装に伴う市民の感情移入・反発動態をモデル化する研究では、LLMを組み込んだエージェント群が社会的に多様な視点や感情的変化を模倣して相互作用を行う4。これにより行政側は、現実世界で失敗した際のリスクが極めて大きい社会政策やリスクコミュニケーション戦略を、仮想空間上で事前にテストし、最適化された政策介入策をデータ駆動型でデザインすることが可能となっている4。

## 実世界および仮想世界における先進導入モデルの比較分析

以下の表は、本レポートで分析した世界の先進的なAIエージェント活用事例について、その技術基盤、具体的用途、ガバナンス構造、および行政経営上の測定インパクトを構造的に比較整理したものである。

| 対象国家／都市 | 活用プラットフォーム／主要エージェント | 技術的アーキテクチャと基盤 | 具体的行政用途・サービスデザイン | ガバナンス・倫理的運用枠組み | 測定されたインパクト・成果 |
| :-- | :-- | :-- | :-- | :-- | :-- |
| **シンガポール**〔cite: 1, 6, 7, 9〕 | VICA, AISAY, MAESTRO, OneService Chatbot | AWS基盤のMLOps（MAESTRO）、LLM、自然言語処理、文書知覚AI1 | 総合問合せ対応、非構造化申請書類の自動解析、自治体不具合報告の分類・自動ルーティング1 | Agentic AIガバナンス枠組み、サンドボックス環境での自動QAおよび安全度テスト9 | 自治体案件で年間2,000人時削減、解決期間2日短縮、クロス省庁手続き時間70%削減7 |
| **エストニア**〔cite: 2, 10, 13, 14〕 | Bürokratt 2.0 | X-Road統合型分散AIエージェント、デジタルID、Rasa + LLM2 | 売上閾値検知によるVAT自動登録、受給可能補助金の能動的提示、プッシュ型申請2 | EU AI Act（高リスク要件）準拠、データトラッカーによるアクセス可視化、最終的人間責任2 | 中小企業の行政対応時間を約70%削減、画面操作を必要としないバックグラウンド処理の推進2 |
| **ソウル特別市**（韓国）3 | Metaverse Seoul | Web 3.0 3D空間、アバターインターフェース、証明書発行・決済エンジン3 | 仮想市役所での行政相談、各種証明書発行、地方税納付シミュレーション、市民参画イベント3 | ソウル・メタバース倫理指針（社会的公正、尊重、現実との統合）の策定16 | 物理窓口を訪問できない市民へのアクセシビリティ向上、若い世代の市民エンゲージメント創出3 |
| **都市・社会デジタルツイン**（例: ラス・パルマス、ノルウェー等）4 | AUDiTs / Social Digital Twins (Social Digital Twinner) | LLM（Gemini等）＋ Agent-Based Modeling（SimPy, OSMnx）、自律型GIS5 | 自然言語によるモビリティ政策シミュレーション、中退対策などの社会政策効果測定4 | Human-AI共同学習、合成データによる差分プライバシー保護、アルゴリズム偏見検知5 | 政策決定前のシナリオテスト可視化、政策試行錯誤に伴う財政・社会的失敗リスクの回避4 |

## 行政経営と制度設計に及ぼす構造的インパクトと直面する課題

### 行政組織の再構築と市民エンゲージメントの質的進化

自律型AIエージェントの実装は、単なる業務の迅速化にとどまらず、公的セクターにおける組織構造と職員の役割定義を根本から再構築している1。定型的なデータ入力、添付書類の一次審査、案件の分類・振り分けといった従来の初動タスクをAIエージェントが受任することにより、公務員の職務価値は「データの処理者」から「AIの判断プロセスを監視・統制し、複雑な個別事案に対応する人間中心型支援の設計者」へとシフトしている1。この変化に伴い、行政経営においては公務員に対する高度なプロンプトエンジニアリング教育やAIガバナンスリテラシーの修得、さらにはAIエージェントのパフォーマンスを調整・管理するデータキュレーターとしての能力開発が急務となっている2。

また、市民と行政の関係性においても顕著な質的進化が認められる。従来型の行政サービスは、市民が必要な制度を自ら調べ、手続きを能動的に申請する関係性に依存していた。しかし、Bürokratt 2.0に代表されるプッシュ型モデルの導入により、行政は市民のライフイベントや事業展開の状況をデータで検知し、自律的にサービスを届けるパートナーへと変容している2。さらに、ソーシャル・デジタルツインの発展は、政策の立案段階において市民が仮想空間上のシミュレーションに直接参画し、政策変更が自らの生活環境に及ぼす影響を定量的に確認しながら合意形成を図るという、新たな双方向的コミュニケーション（対話的リスニング）の可能性を開いている4。

### 「行政効率化のパラドックス」とアルゴリズム的ガバナンスのリスク

一方で、AIエージェントへの依存を強める行政経営は、これまでのデジタル改革では顕在化しなかった新たな制度的リスクや歪みに直面している8。

第一の課題は、ペーパーレス化やAI自動検証の徹底が招く「行政効率化のパラドックス（Administrative Efficiency Paradox）」とデジタル排斥の問題である8。手続きがバックグラウンドで高度に自動化される反面、言語能力の十分でない移民、IT機器の操作に慣れていない高齢者、あるいは複雑な家庭環境を抱える弱者層が、テクノロジーのブラックボックス化により自身の権利や利用可能な支援制度から取り残されるリスクが存在する8。シンガポールの事例分析でも指摘されているように、デジタルリテラシーの乏しい高齢者が家族や第三者に代行を頼らざるを得ず、結果として本人の主体性やプライバシーが損なわれるケースが生じており、効率化の陰で対面による福祉的サポートの需要が現場職員に集中するという現象が発生している8。

第二の課題は、アルゴリズムによる偏見（バイアス）の再現と自動意思決定（ADM）における法的責任の曖昧化である15。AIエージェントが過去の行政データに基づいて不服審査、福祉手当の支給判定、あるいは不正受給のリスク分析を行う際、学習データ内に潜む過去の差別構造や歪みを不意に拡大・固定化させるおそれがある2。オランダで発生した児童手当を巡るアルゴリズム差別問題（Toeslagenaffaire）のように、不透明な自動判定が特定の不利益を市民に与えた場合、法的・道義的責任が開発ベンダー、アルゴリズム、政策担当者のいずれに帰属するのかという救済手続きの構築が遅れている15。そのため、エストニアやシンガポールのように、AIエージェントの判断プロセスを定期的に監査する第三者機関の設置や、アルゴリズムによる自動意思決定に対して市民が人による審理を請求できる権利（Human-in-the-Loopの法的保障）の確立が強固な前提条件となる2。

第三の課題は、省庁間データ連携に伴うデータ主権とサイバーセキュリティの脆弱性である2。AIエージェントが高度なプッシュ型サービスを提供するためには、医療、税務、雇用、住民基本台帳などの機微情報が相互に照会可能な状態になければならない2。このデータインフラに対し、外部からのサイバー攻撃や内部権限の不当行使が発生した場合、国家規模での個人情報流出や行政機能の停止を引き起こす深刻な脅威となる11。したがって、暗号化技術や分散型データ照会プロトコルの導入とともに、エージェントのデータアクセスログを市民自らが常時確認できる高い透明性設計が不可欠となっている2。

## 結論と次世代行政経営への戦略的展望

本調査における多角的な分析結果は、AIエージェントの導入が単なる「既存の業務プロセスを効率化するITツール」の枠を超え、国家および自治体のガバナンス構造そのものを再定義する不可逆な構造変革であることを明確に示している1。実世界における手続きの無人化・プッシュ型化から、仮想都市空間やデジタルツインにおける政策の事前検証に至るまで、テクノロジーは行政サービスをより予防的、パーソナライズされ、かつ機動的なものへと進化させている2。

今後の次世代行政経営を成功させるためには、第一に「見えない行政（Ambient Government）」の実現に向けたデータインフラと法制度の定着が求められる2。行政手続きのフロントエンドを意識させることなく、バックグラウンドでのデータ共有とAIエージェントの自律処理によって市民の権利や給付を保障するアーキテクチャへの統一が推奨される2。第二に、政策立案における「仮想空間シミュレーション（AUDiTs/SDTs）」の標準化である4。実社会での政策適用前に、自律型都市デジタルツイン上でAIエージェント市民による行動・感情変化を予測分析することで、失敗に伴う財政的・社会的コストを最小化する意思決定プロセスを定着させるべきである18。

最終的に、AI主導型ガバナンスの成否を決定づけるのは、技術的最適性のみならず、市民からの根深い「信頼」である1。信頼の構築には、AIエージェントの自律性に適切な倫理的ブレーキをかけるガバナンス枠組み、個人データの利用履歴に関する徹底した透明性の確保、そしてデジタル弱者を包摂する人間的な対面サポート体制の維持が不可欠である2。先進諸国の取り組みが提示する技術的イノベーションと倫理的ガバナンスの均衡（バランス）こそが、持続可能で公的に正当な次世代行政経営を確立するための唯一の道筋であると言える1。

## 引用文献

1. AI agents explained: From fundamentals to real world impact - GovTech Singapore, <https://www.tech.gov.sg/technews/ai-agents/>
2. Estonia's 'Bürokratt' 2.0: How AI Virtual Assistants are Revolutionizing e-Residency Productivity | Blog | LyncMe, <https://www.lync.me/blog/955/estonia-burokratt-ai-assistant-2026>
3. Artificial Intelligence-Enabled Metaverse for Sustainable Smart Cities: Technologies, Applications, Challenges, and Future Directions - MDPI, <https://www.mdpi.com/2079-9292/13/24/4874>
4. Towards an LLM-powered Social Digital Twinning Platform - arXiv, <https://arxiv.org/html/2505.10681v1>
5. (PDF) Towards Agentic Urban Digital Twins (AUDiTs): advancing new urban science through Human-AI co-learning agents - ResearchGate, <https://www.researchgate.net/publication/402497386_Towards_Agentic_Urban_Digital_Twins_AUDiTs_advancing_new_urban_science_through_Human-AI_co-learning_agents>
6. GovTech Case Study | Amazon Web Services, <https://aws.amazon.com/solutions/case-studies/govtech/>
7. How GovTech uses AI to enhance digital public services - GovTech Singapore, <https://www.tech.gov.sg/technews/how-govtech-uses-ai-to-enhance-digital-public-service/>
8. AI for the Next Generation of Public Services, <https://www.undp.org/sites/g/files/zskgke326/files/2025-12/ai-for-the-next-generation-of-public-services.pdf>
9. MODEL AI GOVERNANCE FRAMEWORK FOR AGENTIC AI - IMDA, <https://www.imda.gov.sg/-/media/imda/files/about/emerging-tech-and-research/artificial-intelligence/mgf-for-agentic-ai.pdf>
10. (PDF) From e-Government to AI-Government and Toward the Agentic State: A Reflexive Framework for Public Sector Transformation through the Estonian Bürokratt Case - ResearchGate, <https://www.researchgate.net/publication/399186271_From_e-Government_to_AI-Government_and_Toward_the_Agentic_State_A_Reflexive_Framework_for_Public_Sector_Transformation_through_the_Estonian_Burokratt_Case>
11. The future of public governance: Transition from e- government to a-government - DergiPark, <https://dergipark.org.tr/en/download/article-file/4995229>
12. Bürokratt: Estonia's single network of AI assistants ... - Apolitical, <https://apolitical.co/en/navigator/case-studies/burokratt-estonia-s-single-network-of-ai-assistants-replacing-dozens-of-separate-agency-chatbots>
13. AI in Estonian Public Sector (Road to Buerokratt) - BOSA, <https://bosa.belgium.be/sites/default/files/content/documents/P1_AI%20in%20Estonian%20Public%20Sector%20(Road%20to%20BYK).pdf>
14. Building a Data-Driven Government: Lessons Learned from E, <https://digitalgov.network/data-driven-government-estonia/>
15. Estonia and automated decision-making: challenges for public administration, <https://e-estonia.com/estonia-and-automated-decision-making-challenges-for-public-administration/>
16. INTERNATIONAL GENEVA IN THE METAVERSE.docx, <https://www.graduateinstitute.ch/sites/internet/files/2024-01/INTERNATIONAL%20GENEVA%20IN%20THE%20METAVERSE.docx%20-%20Margherita%20Vazzoler.pdf>
17. Governments, Users, and Virtual Worlds: Institutional Strategies in the Age of Big Data and IA, <https://docta.ucm.es/bitstreams/e675ef51-a282-4a1e-b88c-bc135bee6f83/download>
18. The metaverse: city planner's dream or urban nightmare? - Raconteur, <https://www.raconteur.net/technology/metaverse-planners-dream-urban-nightmare>
19. Ｗｅｂ３時代に向けたメタバース等の利活用に関する研究会 報告書 - 総務省, <https://www.soumu.go.jp/main_content/000892205.pdf>
20. Executive briefing on the metaverse - ITU, <https://www.itu.int/dms_pub/itu-t/opb/tut/T-TUT-METAVERSE-2023-1-PDF-E.pdf>
21. Government in the metaverse: Requirements and suitability for providing digital public services - ResearchGate, <https://www.researchgate.net/publication/379512505_Government_in_the_metaverse_Requirements_and_suitability_for_providing_digital_public_services>
22. Intelligent Digital Twin for Predicting Technology Discourse Patterns: Agent-Based Modeling of User Interactions and Sentiment Dynamics in DeepSeek Discourse Case - MDPI, <https://www.mdpi.com/2079-8954/13/6/451>
23. Generative AI-Driven Digital Twin Architecture for Urban Mobility Simulation and Decision Support - Preprints.org, <https://www.preprints.org/manuscript/202605.0772>
24. Generative AI-Driven Digital Twin Architecture for Urban Mobility Simulation and Decision Support - MDPI, <https://www.mdpi.com/2624-6511/9/7/109>
25. AI-ENABLED ORGANISATIONAL LISTENING – LEVERAGING ARTIFICIAL INTELLIGENCE FOR A MORE RELATIONAL APPROACH TO GOVERNMENT COMMUNICATION - Lee Kuan Yew School of Public Policy - NUS, <https://lkyspp.nus.edu.sg/docs/default-source/ips/ips-working-paper-no-61_ai-enabled-organisational-listening---leveraging-artificial-intelligence-for-a-more-relational-approach-to-government-communication.pdf>
