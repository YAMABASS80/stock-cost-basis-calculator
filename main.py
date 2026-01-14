"""米国株取得費計算スクリプト

日本の税法に基づく総平均法で米国株の取得費を計算する。
"""

import argparse
import sys
from pathlib import Path

from src.csv_reader import CSVReader
from src.parser import TransactionParser
from src.calculator import CostBasisCalculator, CalculationError
from src.output import OutputFormatter


def parse_arguments() -> argparse.Namespace:
    """コマンドライン引数をパース
    
    Returns:
        パースされた引数
    """
    parser = argparse.ArgumentParser(
        description='米国株の取得費を総平均法で計算します',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'input_file',
        type=str,
        help='入力CSVファイルのパス'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        choices=['csv', 'console'],
        default='console',
        help='出力形式 (デフォルト: console)'
    )
    
    parser.add_argument(
        '-f', '--output-file',
        type=str,
        help='CSV出力時の出力ファイルパス (出力形式がcsvの場合に必須)'
    )
    
    return parser.parse_args()


def main():
    """メイン処理"""
    # コマンドライン引数をパース
    args = parse_arguments()
    
    # 出力形式がcsvの場合、出力ファイルパスが必須
    if args.output == 'csv' and not args.output_file:
        print("[ERROR] ArgumentError: --output-file is required when output format is 'csv'", file=sys.stderr)
        sys.exit(1)
    
    try:
        # 1. CSVファイルを読み込む
        input_path = Path(args.input_file)
        reader = CSVReader()
        raw_data = reader.read(input_path)
        
        # 2. トランザクションデータをパース
        parser = TransactionParser()
        transactions = parser.parse(raw_data)
        
        # 3. 取得費を計算
        calculator = CostBasisCalculator()
        results = calculator.calculate(transactions)
        
        # 4. 結果を出力
        formatter = OutputFormatter()
        if args.output == 'csv':
            output_path = Path(args.output_file)
            formatter.to_csv(results, output_path)
            print(f"結果を {output_path} に出力しました")
        else:  # console
            formatter.to_console(results)
        
        sys.exit(0)
        
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except CalculationError as e:
        print(f"[ERROR] CalculationError: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
