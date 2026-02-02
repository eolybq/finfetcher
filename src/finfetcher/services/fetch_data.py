import logging
import time
from datetime import date, datetime, timedelta

import pandas as pd
import pytz
import yfinance as yf
from pandas.tseries.offsets import BusinessDay

from ..config import MARKET_CUTOFFS
from ..exceptions import (
    DataEmptyError,
    TickerNotFoundError,
    YFinanceConnectionError,
)

logger = logging.getLogger(__name__)


def get_complete_close(
    df: pd.DataFrame,
    asset_type: str | None,
    last_day_df: date,
    ticker_tz_name: str | None,
    market_config: dict | None = None,
) -> pd.DataFrame:
    if market_config is None:
        market_config = MARKET_CUTOFFS

    conf = market_config.get(asset_type)  # type: ignore
    if not conf:
        logger.warning(
            f"Unknown asset type '{asset_type}', falling back to EQUITY rules."
        )
        conf = market_config.get("EQUITY", MARKET_CUTOFFS["EQUITY"])

    if conf.get("force_tz"):
        # CRYPTO, FOREX, FUTURES
        ticker_tz_name = conf["force_tz"]
        close_time = conf["default"]
    else:
        # EQUITY, ETF, INDEX
        conf_timezones = conf.get("timezones", {})
        if ticker_tz_name in conf_timezones:
            close_time = conf_timezones[ticker_tz_name]
            logger.debug(
                f"EQUITY TICKER: Using override close_time for {ticker_tz_name}: "
                f"{close_time}"
            )
        else:
            close_time = conf["default"]
            logger.debug(
                f"EQUITY TICKER: Using default fallback close_time for "
                f"{ticker_tz_name}: {close_time}"
            )

    try:
        if not ticker_tz_name:
            raise ValueError("Timezone not specified")
        tz = pytz.timezone(ticker_tz_name)
    except Exception:
        logger.warning(
            f"Unknown timezone '{ticker_tz_name}', fallback to America/New_York"
        )
        tz = pytz.timezone("America/New_York")

    now_in_tz = datetime.now(tz)
    today_in_tz = now_in_tz.date()

    cutoff_time = now_in_tz.replace(
        hour=close_time["hour"], minute=close_time["minute"], second=0, microsecond=0
    )

    if (last_day_df == today_in_tz) and (now_in_tz < cutoff_time):
        df = df.iloc[:-1]
        logger.debug(
            f"Removed unfinished day {last_day_df}. "
            f"Asset: {asset_type}, TZ: {ticker_tz_name}. "
            f"Current: {now_in_tz.strftime('%H:%M')} < "
            f"Cutoff: {cutoff_time.strftime('%H:%M')}"
        )

    return df


def fetch_data(
    ticker_obj: yf.Ticker,
    symbol: str,
    period: str = "4y",
    interval: str = "1d",
    attempts=10,
    market_config: dict | None = None,
) -> tuple[pd.DataFrame, date]:
    """
    Fetches and cleans historical data for a given symbol.

    Args:
        ticker_obj: Initialized yfinance Ticker object.
        symbol: Ticker symbol string.
        period: Data period to download.
        interval: Data interval.
        attempts: Number of retry attempts.
        market_config: Optional dictionary to override market cutoffs.

    Raises:
        TickerNotFoundError: If the ticker info cannot be retrieved.
        DataEmptyError: If yfinance returns no data.
        YFinanceConnectionError: If connection fails after retries.
    """
    try:
        ticker_info = ticker_obj.fast_info
        quote_type = ticker_info.get("quoteType")
        if quote_type:
            quote_type = quote_type.upper()
        ticker_tz_name = ticker_info.get("timezone")

    except Exception as e:
        try:
            quote_type = ticker_obj.info.get("quoteType")
            ticker_tz_name = ticker_obj.info.get("timezone")
        except Exception:
            logger.error(f"Could not retrieve ticker info for {symbol}")
            raise TickerNotFoundError(
                f"Ticker '{symbol}' information not found or accessible."
            ) from e

    logger.debug(f"Detected asset type for {symbol}: {quote_type}")
    logger.debug(f"Detected timezone for {symbol}: {ticker_tz_name}")

    df = None
    last_exception = None

    for i in range(attempts):
        try:
            df = yf.download(
                symbol,
                period=period,
                interval=interval,
                auto_adjust=True,
                progress=False,
            )

            if df is not None and not df.empty:
                break

            logger.debug(
                f"Ticker {symbol} returned no data.\n"
                f"Attempt: {i + 1}/{attempts}\nRetrying..."
            )

        except Exception as e:
            last_exception = e
            logger.debug(
                f"Exception fetching {symbol}: {e}\n"
                f"Attempt: {i + 1}/{attempts}\nRetrying..."
            )

        if i < attempts - 1:
            time.sleep(2)

    if df is None or df.empty:
        if last_exception:
            raise YFinanceConnectionError(
                f"Failed to download data for {symbol} after {attempts} attempts."
            ) from last_exception
        raise DataEmptyError(
            f"No historical data found for symbol '{symbol}' (period={period})."
        )

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    df.index = pd.to_datetime(df.index).date  # type: ignore

    last_df_date = df.index[-1]

    data = get_complete_close(
        df, quote_type, last_df_date, ticker_tz_name, market_config
    )

    if data.empty:
        raise DataEmptyError(
            f"Data for {symbol} is empty after filtering unfinished days."
        )

    last_data_date = data.index[-1]

    if quote_type == "CRYPTOCURRENCY":
        target_date = last_data_date + timedelta(days=1)
    else:
        target_date = (last_data_date + BusinessDay(1)).date()

    logger.debug(f"Final data date range: {data.index.min()} -> {last_data_date}")
    logger.info(f"Fetched {symbol} data from yfinance")

    return data, target_date
