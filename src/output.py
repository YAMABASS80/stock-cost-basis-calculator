"""出力フォーマッター

売却取引の取得費計算結果をCSVまたはコンソールに出力する。
"""

from pathlib import Path
from typing import TextIO
import csv
import sys

from src.models import CostBasisResult


class OutputFormatter:
    """取得費計算結果の出力フォーマッター
    
    CSV出力とコンソール出力の両方をサポートする。
    """
    
    def to_csv(self, results: list[CostBasisResult], output_path: Path) -> None:
        """結果をCSVファイルに出力
        
        Args:
            results: 出力する取得費計算結果のリスト
            output_path: 出力先CSVファイルのパス
            
        Requirements:
            - 5.3: CSV出力が要求された場合、結果をCSVファイルに書き込む
        """
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            self._write_csv(results, f)
    
    def to_console(self, results: list[CostBasisResult]) -> None:
        """結果を標準出力に出力
        
        Args:
            results: 出力する取得費計算結果のリスト
            
        Requirements:
            - 5.4: 標準出力が要求された場合、結果をコンソールに表示する
        """
        self._write_csv(results, sys.stdout)
    
    def _write_csv(self, results: list[CostBasisResult], file: TextIO) -> None:
        """CSV形式で結果を書き込む
        
        Args:
            results: 出力する取得費計算結果のリスト
            file: 書き込み先のファイルオブジェクト
            
        Requirements:
            - 5.1: 売却取引が処理された場合、その売却の取得費を出力する
            - 5.2: 結果出力時、取引日、売却株数、1株あたり取得単価、取得費合計を含める
        """
        writer = csv.writer(file)
        
        # ヘッダー行を書き込む
        writer.writerow([
            'transaction_date',
            'shares_sold',
            'average_cost_per_share',
            'total_cost_basis'
        ])
        
        # データ行を書き込む
        for result in results:
            writer.writerow([
                result.transaction_date.strftime('%Y-%m-%d'),
                result.shares_sold,
                result.average_cost_per_share,
                result.total_cost_basis
            ])
