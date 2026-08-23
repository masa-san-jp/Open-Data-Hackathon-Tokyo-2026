status: done
phase: 2

# T05 2100ストレステスト・トグル

## ゴール
75+人口に係数を掛けるトグル（現在/2070相当×1.5/2100相当×2.0）でヘッダとワースト表が再計算される。

## やること
1. config.json に係数と出所注記を追加（可能なら `apps/tokyo-aging-stress-test/data/processed/` の実出力から江東区係数を読んで差し替え、出所を注記に反映）
2. index.html 内のJSで再計算（埋め込みデータのみ・外部fetchなし）
3. 「これは予測ではなくストレステストである」注記をトグル横に常時表示

## 完了条件
実装計画 §3 Phase 2 の項目が目視できる。verify に係数出所の存在検査を追加。

## 作業ログ

## 実施記録（2026-08-23）

- `config.json` に現在（×1.0）／2070相当（×1.5）／2100相当（×2.0）の係数、各シナリオの出所、ストレステスト注記を追加。
- 姉妹アプリの `data/stress_test.json` は江東区の65歳以上推計が2045年までで、2070/2100の75歳以上町丁別実出力を含まないため、設計仕様の既定係数を採用した。
- `build_prototype.py` が係数設定をHTMLへ埋め込み、インラインJSで町丁ごとの75歳以上人口を丸めて再集計。トグル操作でヘッダ、ワースト表、判定不能人口が更新される。
- `verify.py` に3シナリオの係数・出所・注記の存在検査を追加。
- 検査: `python3 -m py_compile scripts/build_prototype.py scripts/verify.py`、`python3 scripts/build_prototype.py`、`python3 scripts/verify.py`、`git diff --check`。
- ブラウザ確認: 2100相当選択で75歳以上人口が62,399人→124,798人、out人口が693人→1,386人に更新。選択状態・ワースト順位・出所注記を確認。コンソールエラーなし、外部script/link/img/fetchなし。
