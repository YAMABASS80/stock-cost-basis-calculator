"""CostBasisCalculatorのプロパティベーステスト

Feature: stock-cost-basis-calculator
"""

from datetime import date, timedelta
from decimal import Decimal
from hypothesis import given, strategies as st, assume
from src.models import Transaction
from src.calculator import CostBasisCalculator, CalculationError


# カスタム戦略: 有効な取引を生成
@st.composite
def transaction_strategy(draw, transaction_type=None):
    """有効な取引を生成する戦略
    
    Args:
        draw: Hypothesisのdraw関数
        transaction_type: 取引種別を指定（Noneの場合はランダム）
    """
    # 基準日から前後1年の範囲で日付を生成
    base_date = date(2024, 1, 1)
    days_offset = draw(st.integers(min_value=0, max_value=730))
    transaction_date = base_date + timedelta(days=days_offset)

    # 取引種別
    if transaction_type is None:
        trans_type = draw(st.sampled_from(["buy", "sell"]))
    else:
        trans_type = transaction_type

    # 為替レート: 100〜200円/ドル
    exchange_rate = draw(st.decimals(
        min_value=100,
        max_value=200,
        places=2
    ))

    # 株数: 1〜1000株
    unit = draw(st.integers(min_value=1, max_value=1000))

    # 株価: 1〜500ドル
    unit_price = draw(st.decimals(
        min_value=1,
        max_value=500,
        places=2
    ))

    return Transaction(
        transaction_date=transaction_date,
        transaction_type=trans_type,
        exchange_rate=exchange_rate,
        unit=unit,
        unit_price=unit_price
    )


@st.composite
def valid_transaction_list_strategy(draw):
    """有効な取引リストを生成する戦略
    
    時系列順に取引を生成し、保有株数を超える売却が発生しないようにする。
    """
    # 取引数: 2〜20件
    num_transactions = draw(st.integers(min_value=2, max_value=20))

    # 基準日
    base_date = date(2024, 1, 1)

    transactions = []
    current_shares = 0
    current_day = 0

    for _ in range(num_transactions):
        # 日付を単調増加させる（同日または後日）
        days_offset = draw(st.integers(min_value=current_day, max_value=current_day + 30))
        transaction_date = base_date + timedelta(days=days_offset)
        current_day = days_offset

        # 保有株数がゼロの場合は買いのみ
        # 保有株数がある場合は買いか売りをランダムに選択
        if current_shares > 0:
            trans_type = draw(st.sampled_from(["buy", "sell"]))
        else:
            trans_type = "buy"

        # 取引を生成
        transaction = draw(transaction_strategy(transaction_type=trans_type))
        transaction = Transaction(
            transaction_date=transaction_date,
            transaction_type=trans_type,
            exchange_rate=transaction.exchange_rate,
            unit=transaction.unit,
            unit_price=transaction.unit_price
        )

        if trans_type == "buy":
            current_shares += transaction.unit
        else:
            # 売却の場合、保有株数を超えないように調整
            if transaction.unit > current_shares:
                transaction = Transaction(
                    transaction_date=transaction.transaction_date,
                    transaction_type=transaction.transaction_type,
                    exchange_rate=transaction.exchange_rate,
                    unit=draw(st.integers(min_value=1, max_value=current_shares)),
                    unit_price=transaction.unit_price
                )
            current_shares -= transaction.unit

        transactions.append(transaction)

    return transactions


@given(valid_transaction_list_strategy())
def test_property_1_share_consistency(transactions):
    """Property 1: 株数整合性
    
    Feature: stock-cost-basis-calculator, Property 1: 株数整合性
    Validates: Requirements 3.5
    
    任意の取引履歴において、任意の時点での保有株数は、
    その時点までの購入株数の合計から売却株数の合計を引いた値と等しい。
    """
    calculator = CostBasisCalculator()

    # 手動で購入・売却を追跡
    total_bought = 0
    total_sold = 0

    # 取引をソートして処理
    from src.sorter import sort_transactions
    sorted_transactions = sort_transactions(transactions)

    for transaction in sorted_transactions:
        if transaction.transaction_type == "buy":
            calculator._process_buy(transaction)
            total_bought += transaction.unit
        else:
            try:
                calculator._process_sell(transaction)
                total_sold += transaction.unit
            except CalculationError:
                # エラーが発生した場合はスキップ（戦略で防いでいるはずだが念のため）
                pass

    # 保有株数の整合性を検証
    current_shares, _ = calculator.get_current_holdings()
    expected_shares = total_bought - total_sold

    assert current_shares == expected_shares, (
        f"株数整合性エラー: 保有株数={current_shares}, "
        f"期待値={expected_shares} (購入={total_bought}, 売却={total_sold})"
    )


@given(valid_transaction_list_strategy())
def test_property_3_cost_basis_calculation_consistency(transactions):
    """Property 3: 取得費計算の整合性
    
    Feature: stock-cost-basis-calculator, Property 3: 取得費計算の整合性
    Validates: Requirements 3.4
    
    任意の売却取引において、取得費は「1株あたり取得単価（切り上げ済み） × 売却株数」
    と等しくなければならない。
    """
    calculator = CostBasisCalculator()
    results = calculator.calculate(transactions)

    # すべての売却結果について検証
    for result in results:
        # 取得費 = 1株あたり取得単価 × 売却株数
        expected_cost_basis = result.average_cost_per_share * result.shares_sold

        assert result.total_cost_basis == expected_cost_basis, (
            f"取得費計算の整合性エラー: "
            f"取得費={result.total_cost_basis}, "
            f"期待値={expected_cost_basis} "
            f"(単価={result.average_cost_per_share} × 株数={result.shares_sold})"
        )
