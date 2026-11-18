"""トランザクションパーサーモジュール

CSV行データをTransactionオブジェクトに変換する。
データ検証を含む。
"""

from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Literal, Optional

from src.models import Transaction
from src.fx_fetcher import FXFetcher, FXFetchError


class TransactionParser:
    """文字列データをTransactionオブジェクトに変換するクラス

    Args:
        fx_fetcher: 為替レート自動取得用のFXFetcher。指定された場合、
            exchange_rateが空欄の行については取引日のレートを自動取得する。
            Noneの場合、空欄はエラーとして扱う。
    """

    def __init__(self, fx_fetcher: Optional[FXFetcher] = None):
        self.fx_fetcher = fx_fetcher

    def parse(self, raw_data: List[Dict[str, str]]) -> List[Transaction]:
        """生データをTransactionオブジェクトに変換
        
        Args:
            raw_data: CSV読み込みで得られた辞書のリスト
            
        Returns:
            Transactionオブジェクトのリスト
            
        Raises:
            ValueError: データ検証エラーが発生した場合
        """
        transactions = []
        
        for i, row in enumerate(raw_data, start=1):
            try:
                transaction = self._parse_row(row, i)
                transactions.append(transaction)
            except ValueError as e:
                # 行番号を含むエラーメッセージを再送出
                raise ValueError(f"Row {i}: {str(e)}") from e
        
        return transactions
    
    def _parse_row(self, row: Dict[str, str], row_num: int) -> Transaction:
        """1行のデータをTransactionオブジェクトに変換
        
        Args:
            row: CSV行データ
            row_num: 行番号（エラーメッセージ用）
            
        Returns:
            Transactionオブジェクト
            
        Raises:
            ValueError: データ検証エラーが発生した場合
        """
        # transaction_date の検証とパース (YYYYMMDD形式)
        transaction_date = self._parse_date(row['transaction_date'])
        
        # transaction の検証
        transaction_type = self._parse_transaction_type(row['transaction'])
        
        # exchange_rate の検証（空欄の場合は自動取得を試みる）
        exchange_rate = self._resolve_exchange_rate(
            row.get('exchange_rate'),
            transaction_date
        )
        
        # unit の検証
        unit = self._parse_positive_int(row['unit'], 'unit')
        
        # unit_price の検証
        unit_price = self._parse_positive_decimal(
            row['unit_price'], 
            'unit_price'
        )
        
        return Transaction(
            transaction_date=transaction_date,
            transaction_type=transaction_type,
            exchange_rate=exchange_rate,
            unit=unit,
            unit_price=unit_price
        )
    
    def _resolve_exchange_rate(
        self, raw_value: Optional[str], transaction_date: date
    ) -> Decimal:
        """為替レートを解決する

        値が入力されていればそれを検証して返す。空欄の場合は
        FXFetcherが設定されていれば取引日のレートを自動取得する。

        Args:
            raw_value: CSVのexchange_rate列の値（空欄やNoneの場合あり）
            transaction_date: 取引日（自動取得に使用）

        Returns:
            為替レート（Decimal）

        Raises:
            ValueError: 値が不正、または空欄かつ自動取得できない場合
        """
        value_str = (raw_value or "").strip()

        # 値が入力されている場合は従来通り検証
        if value_str != "":
            return self._parse_positive_decimal(value_str, 'exchange_rate')

        # 空欄かつFXFetcher未設定の場合はエラー
        if self.fx_fetcher is None:
            raise ValueError(
                "[ERROR] ValidationError: exchange_rate is empty "
                "(為替レートの自動取得が無効です)"
            )

        # Yahoo Finance から取引日のレートを自動取得
        try:
            return self.fx_fetcher.get_rate(transaction_date)
        except FXFetchError as e:
            raise ValueError(
                f"[ERROR] FXFetchError: {e}"
            ) from e

    def _parse_date(self, date_str: str) -> date:
        """日付文字列をdateオブジェクトに変換
        
        Args:
            date_str: YYYYMMDD形式の日付文字列
            
        Returns:
            dateオブジェクト
            
        Raises:
            ValueError: 日付形式が不正な場合
        """
        try:
            return datetime.strptime(date_str, '%Y%m%d').date()
        except ValueError:
            raise ValueError(
                f"[ERROR] ValidationError: Invalid date format '{date_str}', expected YYYYMMDD"
            )
    
    def _parse_transaction_type(self, type_str: str) -> Literal["buy", "sell"]:
        """取引種別を検証
        
        Args:
            type_str: 取引種別文字列
            
        Returns:
            "buy" または "sell"
            
        Raises:
            ValueError: 取引種別が不正な場合
        """
        if type_str not in ("buy", "sell"):
            raise ValueError(
                f"[ERROR] ValidationError: Invalid transaction type '{type_str}', expected 'buy' or 'sell'"
            )
        return type_str  # type: ignore
    
    def _parse_positive_decimal(self, value_str: str, field_name: str) -> Decimal:
        """正の数値をDecimalに変換
        
        Args:
            value_str: 数値文字列
            field_name: フィールド名（エラーメッセージ用）
            
        Returns:
            Decimalオブジェクト
            
        Raises:
            ValueError: 数値形式が不正、または負の値の場合
        """
        try:
            value = Decimal(value_str)
        except (InvalidOperation, ValueError):
            raise ValueError(
                f"[ERROR] ValidationError: Invalid number format for {field_name}: '{value_str}'"
            )
        
        if value <= 0:
            raise ValueError(
                f"[ERROR] ValidationError: {field_name} must be positive, got '{value_str}'"
            )
        
        return value
    
    def _parse_positive_int(self, value_str: str, field_name: str) -> int:
        """正の整数を検証
        
        Args:
            value_str: 整数文字列
            field_name: フィールド名（エラーメッセージ用）
            
        Returns:
            整数値
            
        Raises:
            ValueError: 整数形式が不正、または負の値の場合
        """
        try:
            value = int(value_str)
        except ValueError:
            raise ValueError(
                f"[ERROR] ValidationError: Invalid integer format for {field_name}: '{value_str}'"
            )
        
        if value <= 0:
            raise ValueError(
                f"[ERROR] ValidationError: {field_name} must be positive, got '{value_str}'"
            )
        
        return value
