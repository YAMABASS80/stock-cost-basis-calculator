# Implementation Plan: 米国株取得費計算スクリプト

## Overview

日本の税法に基づく総平均法で米国株の取得費を計算するPythonスクリプトを実装する。Python 3.14、uvパッケージマネージャを使用。

## Tasks

- [x] 1. プロジェクト構造とデータモデルのセットアップ
  - [x] 1.1 データクラスの定義（Transaction, CostBasisResult）
    - `src/models.py` に Transaction と CostBasisResult データクラスを作成
    - Decimal型を使用して精度を確保
    - _Requirements: 1.2, 4.1_
  - [ ]* 1.2 Property 4: 円建て金額計算プロパティテスト
    - **Property 4: 円建て金額計算の正確性**
    - ランダムな unit_price, unit, exchange_rate に対して amount_jpy = unit_price × unit × exchange_rate を検証
    - **Validates: Requirements 4.1, 4.2**

- [-] 2. ユーティリティ関数の実装
  - [x] 2.1 切り上げ関数の実装
    - `src/utils.py` に ceil_yen 関数を作成
    - Decimal値を受け取り、1円未満を切り上げた整数を返す
    - _Requirements: 3.3_
  - [ ]* 2.2 Property 2: 切り上げプロパティテスト
    - **Property 2: 1円未満切り上げの正確性**
    - ランダムな正の小数に対して result >= x かつ result < x + 1 かつ整数を検証
    - **Validates: Requirements 3.3**

- [x] 3. CSV読み込みとパース機能の実装
  - [x] 3.1 CSVReader クラスの実装
    - `src/csv_reader.py` に CSVReader クラスを作成
    - ファイル存在チェック、必須フィールドチェックを含む
    - _Requirements: 1.1, 1.3, 1.4_
  - [x] 3.2 TransactionParser クラスの実装
    - `src/parser.py` に TransactionParser クラスを作成
    - 文字列データを Transaction オブジェクトに変換
    - _Requirements: 1.2, 2.1-2.5_
  - [ ]* 3.3 CSV読み込みとパースの単体テスト
    - 正常系：有効なCSVの読み込み
    - 異常系：ファイル不在、フィールド欠落、不正な値
    - _Requirements: 1.1-1.4, 2.1-2.6_

- [x] 4. 取引ソート機能の実装
  - [x] 4.1 TransactionSorter の実装
    - `src/sorter.py` に sort_transactions 関数を作成
    - 日付昇順、同日は買い→売りの順でソート
    - _Requirements: 6.1, 6.2_
  - [ ]* 4.2 Property 5: ソート順序プロパティテスト
    - **Property 5: ソート順序の保証**
    - ランダムな取引リストに対して、ソート後の順序が正しいことを検証
    - **Validates: Requirements 6.1, 6.2**

- [x] 5. Checkpoint - 基盤機能の確認
  - すべてのテストが通ることを確認
  - 質問があればユーザーに確認

- [x] 6. 取得費計算エンジンの実装
  - [x] 6.1 CostBasisCalculator クラスの実装
    - `src/calculator.py` に CostBasisCalculator クラスを作成
    - 総平均法による取得単価計算
    - 売却時の取得費計算と残株数更新
    - _Requirements: 3.1-3.5_
  - [x] 6.2 Property 1: 株数整合性プロパティテスト
    - **Property 1: 株数整合性**
    - ランダムな取引履歴に対して、保有株数 = 購入合計 - 売却合計を検証
    - **Validates: Requirements 3.5**
  - [x]* 6.3 Property 3: 取得費計算プロパティテスト
    - **Property 3: 取得費計算の整合性**
    - ランダムな売却取引に対して、取得費 = 単価 × 株数を検証
    - **Validates: Requirements 3.4**
  - [x]* 6.4 国税庁計算例による検証テスト
    - 国税庁の計算例（X1年9月売却、X2年7月売却）を再現
    - 期待値との一致を確認
    - _Requirements: 3.1-3.5_

- [x] 7. 出力機能の実装
  - [x] 7.1 OutputFormatter クラスの実装
    - `src/output.py` に OutputFormatter クラスを作成
    - CSV出力とコンソール出力の両方をサポート
    - _Requirements: 5.1-5.4_
  - [ ]* 7.2 Property 6: 出力完全性プロパティテスト
    - **Property 6: 出力完全性**
    - ランダムな CostBasisResult に対して、必須フィールドがすべて含まれることを検証
    - **Validates: Requirements 5.1, 5.2**

- [x] 8. メインスクリプトの統合
  - [x] 8.1 CLI インターフェースの実装
    - `src/main.py` にコマンドライン引数処理を実装
    - 入力ファイルパス、出力形式（csv/console）の指定
    - _Requirements: 5.3, 5.4_
  - [x] 8.2 全コンポーネントの統合
    - パイプライン処理の実装
    - エラーハンドリングの統合
    - _Requirements: 1.1-6.2_

- [ ] 9. Final Checkpoint - 全機能の確認
  - すべてのテストが通ることを確認
  - サンプルCSVでの動作確認
  - 質問があればユーザーに確認

## Notes

- タスクに `*` マークがあるものはオプション（テスト関連）
- Python 3.14、uvパッケージマネージャを使用
- プロパティテストには Hypothesis ライブラリを使用
- 各タスクは要件への参照を含む
