"""データモデル定義

米国株取得費計算に使用するデータクラスを定義する。
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal


@dataclass
class Transaction:
    """株式取引を表すデータクラス
    
    Attributes:
        transaction_date: 取引日
        transaction_type: 取引種別（"buy" または "sell"）
        exchange_rate: 為替レート（円/ドル）
        unit: 株数
        unit_price: 1株あたり価格（USD）
    """
    transaction_date: date
    transaction_type: Literal["buy", "sell"]
    exchange_rate: Decimal
    unit: int
    unit_price: Decimal
    
    @property
    def amount_jpy(self) -> Decimal:
        """円建て金額を計算
        
        Returns:
            円建ての取引金額（unit_price × unit × exchange_rate）
        """
        return self.unit_price * self.unit * self.exchange_rate


@dataclass
class CostBasisResult:
    """売却時の取得費計算結果を表すデータクラス
    
    Attributes:
        transaction_date: 売却日
        shares_sold: 売却株数
        average_cost_per_share: 1株あたり取得単価（円、1円未満切り上げ済み）
        total_cost_basis: 取得費合計（円）
    """
    transaction_date: date
    shares_sold: int
    average_cost_per_share: int  # 円（1円未満切り上げ済み）
    total_cost_basis: int  # 円
