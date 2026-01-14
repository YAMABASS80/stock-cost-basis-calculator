# Requirements Document

## Introduction

日本の税法に基づき、米国株の売却時における取得費を総平均法で計算するPythonスクリプト。同一銘柄の株式を複数回購入・売却した場合に、各売却タイミングでの取得費を正確に算出する。

## Glossary

- **取得費 (Cost_Basis)**: 売却時点での株式の取得原価。総平均法により計算される。
- **総平均法 (Average_Cost_Method)**: 購入価額の総額を購入株数の総数で除して1株あたりの取得単価を算出する方法。
- **Calculator**: 取得費を計算するシステム。
- **Transaction**: 株式の購入または売却の取引記録。
- **Exchange_Rate**: 取引時点での為替レート（円/ドル）。

## Requirements

### Requirement 1: CSVファイルの読み込み

**User Story:** 開発者として、CSV形式の取引履歴ファイルを読み込みたい。これにより取引データを処理できるようになる。

#### Acceptance Criteria

1. WHEN a valid CSV file path is provided, THE Calculator SHALL read the file and parse transaction records
2. WHEN the CSV file contains required fields (transaction_date, transaction, exchange_rate, unit, unit_price), THE Calculator SHALL extract all field values correctly
3. IF the CSV file does not exist, THEN THE Calculator SHALL return a descriptive error message
4. IF the CSV file is missing required fields, THEN THE Calculator SHALL return a validation error

### Requirement 2: 取引データの検証

**User Story:** 開発者として、取引データが正しい形式であることを検証したい。これにより不正なデータによる計算エラーを防げる。

#### Acceptance Criteria

1. WHEN transaction_date is provided, THE Calculator SHALL validate it as YYYYMMDD format
2. WHEN transaction type is provided, THE Calculator SHALL validate it as either "buy" or "sell"
3. WHEN exchange_rate is provided, THE Calculator SHALL validate it as a positive number
4. WHEN unit is provided, THE Calculator SHALL validate it as a positive integer
5. WHEN unit_price is provided, THE Calculator SHALL validate it as a positive number (USD)
6. IF any validation fails, THEN THE Calculator SHALL return a specific error message indicating the invalid field

### Requirement 3: 総平均法による取得単価の計算

**User Story:** 投資家として、売却時点での1株あたりの取得単価を総平均法で計算したい。これにより日本の税法に準拠した取得費を算出できる。

#### Acceptance Criteria

1. WHEN calculating average cost per share, THE Calculator SHALL sum all purchase amounts up to the sale date
2. WHEN calculating average cost per share, THE Calculator SHALL divide total purchase amount by total shares held
3. WHEN the result has decimal places, THE Calculator SHALL round up to the nearest yen (1円未満切り上げ)
4. WHEN a sale occurs, THE Calculator SHALL use the current average cost to calculate cost basis
5. WHEN a sale occurs, THE Calculator SHALL update remaining shares for subsequent calculations

### Requirement 4: 円建て購入金額の計算

**User Story:** 投資家として、米国株の購入金額を円建てで計算したい。これにより日本円での取得費を正確に把握できる。

#### Acceptance Criteria

1. WHEN a buy transaction is processed, THE Calculator SHALL multiply unit_price by unit by exchange_rate to get yen amount
2. WHEN calculating purchase amount, THE Calculator SHALL use the exchange rate from the transaction record

### Requirement 5: 売却時の取得費出力

**User Story:** 投資家として、各売却タイミングでの取得費を確認したい。これにより確定申告に必要な情報を得られる。

#### Acceptance Criteria

1. WHEN a sell transaction is processed, THE Calculator SHALL output the cost basis for that sale
2. WHEN outputting results, THE Calculator SHALL include transaction date, shares sold, average cost per share, and total cost basis
3. WHEN CSV output is requested, THE Calculator SHALL write results to a CSV file
4. WHEN standard output is requested, THE Calculator SHALL print results to console

### Requirement 6: 取引の時系列処理

**User Story:** 開発者として、取引を日付順に処理したい。これにより正確な取得費計算ができる。

#### Acceptance Criteria

1. WHEN processing transactions, THE Calculator SHALL sort them by transaction_date in ascending order
2. WHEN multiple transactions have the same date, THE Calculator SHALL process buy transactions before sell transactions
