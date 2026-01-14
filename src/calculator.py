"""取得費計算エンジン

総平均法による米国株の取得費計算を行うモジュール。
"""

from decimal import Decimal
from typing import List

from src.models import Transaction, CostBasisResult
from src.utils import ceil_yen
from src.sorter import sort_transactions


class CalculationError(Exception):
    """計算エラーを表す例外クラス"""
    pass


class CostBasisCalculator:
    """総平均法による取得費計算クラス
    
    日本の税法に基づき、米国株の売却時における取得費を
    総平均法で計算する。
    
    Attributes:
        total_cost_jpy: 保有株式の取得価額総額（円）
        total_shares: 保有株数
    """
    
    def __init__(self):
        """初期化"""
        self.total_cost_jpy: Decimal = Decimal("0")
        self.total_shares: int = 0
    
    def _process_buy(self, transaction: Transaction) -> None:
        """購入取引を処理
        
        Args:
            transaction: 購入取引
        """
        # 円建て購入金額を加算
        self.total_cost_jpy += transaction.amount_jpy
        # 株数を加算
        self.total_shares += transaction.unit
    
    def _process_sell(self, transaction: Transaction) -> CostBasisResult:
        """売却取引を処理し、取得費を計算
        
        Args:
            transaction: 売却取引
            
        Returns:
            売却時の取得費計算結果
            
        Raises:
            CalculationError: 保有株数を超える売却、または保有株数がゼロの場合
        """
        shares_to_sell = transaction.unit
        
        # 保有株数チェック
        if self.total_shares == 0:
            raise CalculationError(
                f"保有株数がゼロの状態での売却はできません: "
                f"売却日={transaction.transaction_date}"
            )
        
        if shares_to_sell > self.total_shares:
            raise CalculationError(
                f"保有株数を超える売却はできません: "
                f"保有株数={self.total_shares}, 売却株数={shares_to_sell}, "
                f"売却日={transaction.transaction_date}"
            )
        
        # 1株あたり取得単価を計算（総平均法）
        # Requirements 3.1, 3.2: 購入価額の総額を購入株数の総数で除す
        average_cost_decimal = self.total_cost_jpy / self.total_shares
        
        # Requirements 3.3: 1円未満切り上げ
        average_cost_per_share = ceil_yen(average_cost_decimal)
        
        # Requirements 3.4: 取得費 = 1株あたり取得単価 × 売却株数
        total_cost_basis = average_cost_per_share * shares_to_sell
        
        # Requirements 3.5: 残株数と取得価額総額を更新
        # 売却分の取得価額を減算（平均単価ベース）
        cost_of_sold_shares = average_cost_decimal * shares_to_sell
        self.total_cost_jpy -= cost_of_sold_shares
        self.total_shares -= shares_to_sell
        
        return CostBasisResult(
            transaction_date=transaction.transaction_date,
            shares_sold=shares_to_sell,
            average_cost_per_share=average_cost_per_share,
            total_cost_basis=total_cost_basis
        )
    
    def calculate(self, transactions: List[Transaction]) -> List[CostBasisResult]:
        """取引履歴から売却時の取得費を計算
        
        総平均法により、各売却時点での取得費を計算する。
        取引は日付順にソートされ、同日の場合は買い取引が先に処理される。
        
        Args:
            transactions: 取引履歴のリスト
            
        Returns:
            各売却取引に対する取得費計算結果のリスト
            
        Raises:
            CalculationError: 計算エラー（保有株数超過など）
        """
        # 状態をリセット
        self.total_cost_jpy = Decimal("0")
        self.total_shares = 0
        
        results: List[CostBasisResult] = []
        
        # Requirements 6.1, 6.2: 日付順にソート（同日は買い→売り）
        sorted_transactions = sort_transactions(transactions)
        
        for transaction in sorted_transactions:
            if transaction.transaction_type == "buy":
                self._process_buy(transaction)
            else:  # sell
                result = self._process_sell(transaction)
                results.append(result)
        
        return results
    
    def get_current_holdings(self) -> tuple[int, Decimal]:
        """現在の保有状況を取得
        
        Returns:
            (保有株数, 取得価額総額) のタプル
        """
        return self.total_shares, self.total_cost_jpy
