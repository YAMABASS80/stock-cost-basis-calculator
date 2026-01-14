"""国税庁の計算例による検証テスト

国税庁の公式計算例を使用して、CostBasisCalculatorの正確性を検証する。
参考: https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/1466.htm

Feature: stock-cost-basis-calculator
Requirements: 3.1-3.5
"""

from datetime import date
from decimal import Decimal
import pytest
from src.models import Transaction
from src.calculator import CostBasisCalculator


def test_nta_example_case_1():
    """国税庁計算例 ケース1: X1年9月売却
    
    取引履歴:
    - X1年1月: 100株を1株100ドル、為替150円で購入 → 1,500,000円
    - X1年5月: 50株を1株120ドル、為替155円で購入 → 930,000円
    - X1年9月: 80株を売却
    
    期待される計算:
    - 合計取得価額: 2,430,000円
    - 保有株数: 150株
    - 平均単価: 2,430,000 ÷ 150 = 16,200円/株
    - 売却時取得費: 16,200円 × 80株 = 1,296,000円
    """
    transactions = [
        # X1年1月購入
        Transaction(
            transaction_date=date(2024, 1, 15),
            transaction_type='buy',
            exchange_rate=Decimal('150'),
            unit=100,
            unit_price=Decimal('100')
        ),
        # X1年5月購入
        Transaction(
            transaction_date=date(2024, 5, 20),
            transaction_type='buy',
            exchange_rate=Decimal('155'),
            unit=50,
            unit_price=Decimal('120')
        ),
        # X1年9月売却
        Transaction(
            transaction_date=date(2024, 9, 10),
            transaction_type='sell',
            exchange_rate=Decimal('160'),
            unit=80,
            unit_price=Decimal('130')
        ),
    ]
    
    calculator = CostBasisCalculator()
    results = calculator.calculate(transactions)
    
    # 結果の検証
    assert len(results) == 1, "売却は1回のみ"
    
    result = results[0]
    assert result.transaction_date == date(2024, 9, 10)
    assert result.shares_sold == 80
    assert result.average_cost_per_share == 16200, (
        f"平均単価が期待値と異なります: {result.average_cost_per_share}円 (期待値: 16200円)"
    )
    assert result.total_cost_basis == 1296000, (
        f"取得費が期待値と異なります: {result.total_cost_basis}円 (期待値: 1,296,000円)"
    )
    
    # 残株数の確認
    remaining_shares, remaining_cost = calculator.get_current_holdings()
    assert remaining_shares == 70, f"残株数が期待値と異なります: {remaining_shares}株 (期待値: 70株)"


def test_nta_example_case_2():
    """国税庁計算例 ケース2: X2年7月売却（ケース1の続き）
    
    前提（ケース1の結果）:
    - 残株数: 70株
    - 残取得価額: 1,134,000円
    
    追加取引:
    - X2年3月: 100株を1株110ドル、為替148円で購入 → 1,628,000円
    - X2年7月: 120株を売却
    
    期待される計算:
    - 合計取得価額: 1,134,000 + 1,628,000 = 2,762,000円
    - 保有株数: 70 + 100 = 170株
    - 平均単価: 2,762,000 ÷ 170 = 16,247.05... → 16,248円/株（切り上げ）
    - 売却時取得費: 16,248円 × 120株 = 1,949,760円
    """
    transactions = [
        # X1年1月購入
        Transaction(
            transaction_date=date(2024, 1, 15),
            transaction_type='buy',
            exchange_rate=Decimal('150'),
            unit=100,
            unit_price=Decimal('100')
        ),
        # X1年5月購入
        Transaction(
            transaction_date=date(2024, 5, 20),
            transaction_type='buy',
            exchange_rate=Decimal('155'),
            unit=50,
            unit_price=Decimal('120')
        ),
        # X1年9月売却
        Transaction(
            transaction_date=date(2024, 9, 10),
            transaction_type='sell',
            exchange_rate=Decimal('160'),
            unit=80,
            unit_price=Decimal('130')
        ),
        # X2年3月購入
        Transaction(
            transaction_date=date(2025, 3, 15),
            transaction_type='buy',
            exchange_rate=Decimal('148'),
            unit=100,
            unit_price=Decimal('110')
        ),
        # X2年7月売却
        Transaction(
            transaction_date=date(2025, 7, 20),
            transaction_type='sell',
            exchange_rate=Decimal('152'),
            unit=120,
            unit_price=Decimal('140')
        ),
    ]
    
    calculator = CostBasisCalculator()
    results = calculator.calculate(transactions)
    
    # 結果の検証
    assert len(results) == 2, "売却は2回"
    
    # 1回目の売却（X1年9月）
    result1 = results[0]
    assert result1.transaction_date == date(2024, 9, 10)
    assert result1.shares_sold == 80
    assert result1.average_cost_per_share == 16200
    assert result1.total_cost_basis == 1296000
    
    # 2回目の売却（X2年7月）
    result2 = results[1]
    assert result2.transaction_date == date(2025, 7, 20)
    assert result2.shares_sold == 120
    assert result2.average_cost_per_share == 16248, (
        f"平均単価が期待値と異なります: {result2.average_cost_per_share}円 (期待値: 16248円)"
    )
    assert result2.total_cost_basis == 1949760, (
        f"取得費が期待値と異なります: {result2.total_cost_basis}円 (期待値: 1,949,760円)"
    )
    
    # 残株数の確認
    remaining_shares, remaining_cost = calculator.get_current_holdings()
    assert remaining_shares == 50, f"残株数が期待値と異なります: {remaining_shares}株 (期待値: 50株)"
