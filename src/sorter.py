"""取引のソート機能を提供するモジュール"""

from typing import List
from src.models import Transaction


def sort_transactions(transactions: List[Transaction]) -> List[Transaction]:
    """
    取引を日付昇順でソートし、同日の場合は買い取引を売り取引より先に処理する
    
    Args:
        transactions: ソート対象の取引リスト
        
    Returns:
        ソート済みの取引リスト
        
    Requirements: 6.1, 6.2
    """
    # 日付昇順、同日は買い→売りの順でソート
    # transaction_typeが"buy"の場合は0、"sell"の場合は1として扱う
    return sorted(
        transactions,
        key=lambda t: (t.transaction_date, 0 if t.transaction_type == "buy" else 1)
    )
