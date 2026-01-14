"""CSV読み込みモジュール

CSVファイルを読み込み、辞書のリストとして返す。
ファイル存在チェックと必須フィールドチェックを含む。
"""

import csv
from pathlib import Path
from typing import List, Dict


class CSVReader:
    """CSVファイルを読み込むクラス"""
    
    REQUIRED_FIELDS = {
        'transaction_date',
        'transaction',
        'exchange_rate',
        'unit',
        'unit_price'
    }
    
    def read(self, file_path: Path) -> List[Dict[str, str]]:
        """CSVファイルを読み込み、辞書のリストを返す
        
        Args:
            file_path: 読み込むCSVファイルのパス
            
        Returns:
            各行を辞書として含むリスト
            
        Raises:
            FileNotFoundError: ファイルが存在しない場合
            ValueError: 必須フィールドが欠落している場合
        """
        # ファイル存在チェック
        if not file_path.exists():
            raise FileNotFoundError(f"[ERROR] FileNotFoundError: CSV file not found: {file_path}")
        
        # CSVファイルを読み込む（BOMを自動処理）
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            # ヘッダー（フィールド名）を取得
            if reader.fieldnames is None:
                raise ValueError("[ERROR] ValidationError: CSV file is empty or has no header")
            
            fieldnames = set(reader.fieldnames)
            
            # 必須フィールドチェック
            missing_fields = self.REQUIRED_FIELDS - fieldnames
            if missing_fields:
                raise ValueError(
                    f"[ERROR] ValidationError: Missing required fields: {', '.join(sorted(missing_fields))}"
                )
            
            # データを読み込む
            data = list(reader)
            
        return data
