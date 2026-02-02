import copy
import logging

import pandas as pd
import yfinance as yf

from .config import MARKET_CUTOFFS
from .exceptions import DataEmptyError, FinFetcherError, TickerNotFoundError
from .services.fetch_data import fetch_data

logger = logging.getLogger(__name__)


class DataFetcher:
    """
    Main class for fetching and cleaning financial data from Yahoo Finance.

    This class handles:
    - Connecting to Yahoo Finance.
    - Fetching historical data.
    - Cleaning data based on market hours (removing incomplete candles).
    - Calculating the next valid trading date (target_date).
    """

    def __init__(self, symbol: str, custom_cutoffs: dict | None = None) -> None:
        """
        Initialize the DataFetcher with a ticker symbol.

        Args:
            symbol (str): The ticker symbol (e.g., 'AAPL', 'BTC-USD').
            custom_cutoffs (dict, optional): Dictionary to merge with/override
                default MARKET_CUTOFFS.

                Structure & Example:
                --------------------
                The dictionary must use string keys for asset types (e.g., "EQUITY")
                and dictionaries for values.
                Time settings must contain integer "hour" and "minute".

                custom_cutoffs = {
                    "EQUITY": {
                        # Option A: Override specific timezones
                        "timezones": {
                            "America/New_York": {"hour": 13, "minute": 0}  # Early close
                        },
                        # Fallback for other timezones
                        "default": {"hour": 18, "minute": 0}
                    },
                    "MY_NEW_ASSET": {
                        # Option B: Force a specific timezone (e.g., for Crypto/Futures)
                        "force_tz": "UTC",
                        "default": {"hour": 23, "minute": 59}
                    }
                }

        Raises:
            TickerNotFoundError: If the ticker initialization fails.
            TypeError: If custom_cutoffs or its internal structure has invalid types.
            ValueError: If custom_cutoffs has missing required keys or invalid values.
        """
        self.symbol = symbol.upper()
        self.target_date = None
        self.ticker = yf.Ticker(symbol)

        if custom_cutoffs:
            if not isinstance(custom_cutoffs, dict):
                raise TypeError("custom_cutoffs must be a dictionary.")

            for asset, conf in custom_cutoffs.items():
                if not isinstance(asset, str):
                    raise TypeError(f"Asset key '{asset}' must be a string.")
                if not isinstance(conf, dict):
                    raise TypeError(
                        f"Configuration for '{asset}' must be a dictionary."
                    )

                # Validate 'default' if present
                if "default" in conf:
                    d = conf["default"]
                    if (
                        not isinstance(d, dict)
                        or not isinstance(d.get("hour"), int)
                        or not isinstance(d.get("minute"), int)
                    ):
                        raise ValueError(
                            f"Invalid 'default' for '{asset}': "
                            "must be dict with int 'hour' and 'minute'."
                        )

                # Validate 'timezones' if present
                if "timezones" in conf:
                    if not isinstance(conf["timezones"], dict):
                        raise TypeError(
                            f"'timezones' for '{asset}' must be a dictionary."
                        )
                    for tz_key, tz_val in conf["timezones"].items():
                        if (
                            not isinstance(tz_val, dict)
                            or not isinstance(tz_val.get("hour"), int)
                            or not isinstance(tz_val.get("minute"), int)
                        ):
                            raise ValueError(
                                f"Invalid config for '{asset}'->'{tz_key}': "
                                "must be dict with int 'hour' and 'minute'."
                            )

        self.config = copy.deepcopy(MARKET_CUTOFFS)
        if custom_cutoffs:
            for key, value in custom_cutoffs.items():
                if (
                    key in self.config
                    and isinstance(self.config[key], dict)
                    and isinstance(value, dict)
                ):
                    self.config[key].update(value)
                else:
                    self.config[key] = value

    def get_data(self, period: str = "4y", interval: str = "1d") -> pd.DataFrame:
        """
        Fetch historical data for the initialized symbol.

        Args:
            period (str): Data period to download (default: "4y").
            interval (str): Data interval (default: "1d").

        Returns:
            pd.DataFrame: A pandas DataFrame with the cleaned historical data.
                          The DataFrame will have date index and columns like
                          Open, High, Low, Close, Volume.

        Raises:
            TickerNotFoundError: If the ticker does not exist.
            DataEmptyError: If no data is returned for the given period.
            YFinanceConnectionError: If connection to Yahoo Finance fails.
            FinFetcherError: Base exception for other library errors.
        """
        try:
            data, target_date = fetch_data(
                ticker_obj=self.ticker,
                symbol=self.symbol,
                period=period,
                interval=interval,
                market_config=self.config,
            )

            logger.info(f"Successfully fetched {len(data)} rows for {self.symbol}")
            self.target_date = target_date
            return data

        except TickerNotFoundError as e:
            logger.error(f"Ticker not found error for {self.symbol}: {e}")
            raise

        except DataEmptyError as e:
            logger.error(f"Data empty error for {self.symbol}: {e}")
            raise

        except Exception as e:
            logger.exception(f"Unexpected error while fetching data for {self.symbol}")
            raise FinFetcherError(
                f"An unexpected error occurred for {self.symbol}"
            ) from e
