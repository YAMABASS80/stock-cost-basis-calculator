"""ユーティリティ関数

取得費計算に使用する補助関数を定義する。
"""

from decimal import Decimal, ROUND_CEILING


def ceil_yen(value: Decimal) -> int:
    """Decimal値を1円未満切り上げして整数に変換
    
    日本の税法に基づき、1円未満の端数を切り上げる。
    
    Args:
        value: 切り上げ対象のDecimal値
        
    Returns:
        1円未満を切り上げた整数値
        
    Examples:
        >>> ceil_yen(Decimal("100.1"))
        101
        >>> ceil_yen(Decimal("100.0"))
        100
        >>> ceil_yen(Decimal("99.999"))
        100
    """
    # Decimalを1の位で切り上げ
    rounded = value.quantize(Decimal("1"), rounding=ROUND_CEILING)
    return int(rounded)
