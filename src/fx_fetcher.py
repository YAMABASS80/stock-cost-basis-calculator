"""為替レート自動取得モジュール

Yahoo Finance の chart API から USD/JPY の為替レートを取得する。
標準ライブラリのみを使用（外部依存なし）。

市場が閉まっている日（土日・祝日）の取引については、
直前の営業日の終値レートを採用する。
"""

import json
import urllib.request
import urllib.error
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict


class FXFetchError(Exception):
    """為替レート取得エラーを表す例外クラス"""
    pass


class FXFetcher:
    """Yahoo Finance から USD/JPY レートを取得するクラス

    取得したレートは日付→レートのキャッシュに保持し、
    近接した取引日の再取得を避ける。指定日が市場閉場日
    （土日・祝日）の場合は、直前の営業日のレートを採用する。

    Attributes:
        symbol: 取得対象のシンボル（デフォルト: "USDJPY=X"）
        timeout: HTTPリクエストのタイムアウト秒数
    """

    BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    DEFAULT_SYMBOL = "USDJPY=X"
    # レートの小数点以下桁数
    QUANTIZE = Decimal("0.0001")
    # 直前営業日を遡って探す最大日数
    MAX_LOOKBACK_DAYS = 14

    def __init__(self, symbol: str = DEFAULT_SYMBOL, timeout: int = 15):
        self.symbol = symbol
        self.timeout = timeout
        # 解決済みレートおよび営業日レートのキャッシュ（date → Decimal）
        self._cache: Dict[date, Decimal] = {}

    def get_rate(self, target_date: date) -> Decimal:
        """指定日の USD/JPY レートを取得

        指定日が市場閉場日（土日・祝日）の場合は、直前の営業日の
        終値レートを返す。

        Args:
            target_date: レートを取得したい取引日

        Returns:
            USD/JPY レート（小数第4位、Decimal）

        Raises:
            FXFetchError: 取得に失敗した、または該当レートが存在しない場合
        """
        # 解決済みのレートがあればそれを返す
        if target_date in self._cache:
            return self._cache[target_date]

        # 対象日を含む前後の範囲を1回のリクエストで取得する
        window = self._fetch_window(target_date)
        self._cache.update(window)

        # 対象日のレートを決定（なければ直前の営業日を遡る）
        d = target_date
        for _ in range(self.MAX_LOOKBACK_DAYS + 1):
            if d in window:
                rate = window[d]
                # 解決済みレートとして対象日にもキャッシュしておく
                self._cache[target_date] = rate
                return rate
            d = d - timedelta(days=1)

        raise FXFetchError(
            f"為替レートが取得できませんでした: {target_date.isoformat()} "
            f"(直前の営業日のレートも見つかりません)"
        )

    def _fetch_window(self, target_date: date) -> Dict[date, Decimal]:
        """対象日の前後に余裕を持たせた範囲のレートを取得する

        Args:
            target_date: 基準となる取引日

        Returns:
            日付→レートの辞書（営業日のみ）
        """
        start = target_date - timedelta(days=self.MAX_LOOKBACK_DAYS)
        end = target_date + timedelta(days=2)
        return self._fetch_range(start, end)

    def _fetch_range(self, start: date, end: date) -> Dict[date, Decimal]:
        """指定範囲のレートを Yahoo Finance から取得する

        Args:
            start: 取得開始日
            end: 取得終了日

        Returns:
            日付→レートの辞書（営業日のみ）

        Raises:
            FXFetchError: 接続・解析に失敗した場合
        """
        period1 = int(
            datetime(start.year, start.month, start.day, tzinfo=timezone.utc).timestamp()
        )
        period2 = int(
            datetime(end.year, end.month, end.day, tzinfo=timezone.utc).timestamp()
        )
        url = (
            self.BASE_URL.format(symbol=self.symbol)
            + f"?period1={period1}&period2={period2}&interval=1d"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.load(resp)
        except urllib.error.URLError as e:
            raise FXFetchError(
                f"Yahoo Finance への接続に失敗しました: {e}"
            ) from e
        except (json.JSONDecodeError, ValueError) as e:
            raise FXFetchError(
                f"Yahoo Finance のレスポンス解析に失敗しました: {e}"
            ) from e

        return self._parse_response(data)

    def _parse_response(self, data: dict) -> Dict[date, Decimal]:
        """chart API のレスポンスを日付→レートの辞書に変換する

        Args:
            data: chart API の JSON レスポンス

        Returns:
            日付→レートの辞書（終値が null の日は除外）

        Raises:
            FXFetchError: レスポンス構造が想定と異なる場合
        """
        try:
            result = data["chart"]["result"][0]
            timestamps = result["timestamp"]
            closes = result["indicators"]["quote"][0]["close"]
        except (KeyError, IndexError, TypeError) as e:
            # エラー応答などで想定構造でない場合
            api_error = None
            if isinstance(data, dict):
                chart = data.get("chart")
                if isinstance(chart, dict):
                    api_error = chart.get("error")
            raise FXFetchError(
                f"Yahoo Finance のレスポンス形式が不正です: {api_error or e}"
            ) from e

        rates: Dict[date, Decimal] = {}
        for ts, close in zip(timestamps, closes):
            if close is None:
                continue
            d = datetime.fromtimestamp(ts, tz=timezone.utc).date()
            rates[d] = Decimal(str(close)).quantize(
                self.QUANTIZE, rounding=ROUND_HALF_UP
            )
        return rates
