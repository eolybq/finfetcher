import unittest
from datetime import date

import pandas as pd

from finfetcher import DataFetcher
from finfetcher.exceptions import DataEmptyError, TickerNotFoundError


class TestFinFetcher(unittest.TestCase):
    def test_successful_fetch(self):
        """Test fetching data for a well-known ticker (AAPL)."""
        fetcher = DataFetcher("AAPL")
        data = fetcher.get_data(period="1mo")

        self.assertIsInstance(data, pd.DataFrame)
        self.assertFalse(data.empty)
        self.assertIsInstance(fetcher.target_date, date)
        print(
            f"\n[OK] Fetched {len(data)} rows for {fetcher.symbol}. "
            f"Next target date: {fetcher.target_date}"
        )

    def test_invalid_ticker(self):
        """Test that an invalid ticker raises TickerNotFoundError."""
        # yfinance often returns empty DF for non-existent tickers rather than error
        # but our fetch_data logic should catch empty DF and raise
        # DataEmptyError or TickerNotFoundError
        fetcher = DataFetcher("NONEXISTENT_TICKER_12345")
        with self.assertRaises((TickerNotFoundError, DataEmptyError)):
            fetcher.get_data(period="1mo")
        print("[OK] Invalid ticker correctly raised an error.")

    def test_crypto_fetch(self):
        """Test fetching data for a cryptocurrency (BTC-USD)."""
        fetcher = DataFetcher("BTC-USD")
        data = fetcher.get_data(period="5d")

        self.assertIsInstance(data, pd.DataFrame)
        self.assertFalse(data.empty)
        print(f"[OK] Fetched {len(data)} rows for BTC-USD.")


if __name__ == "__main__":
    unittest.main()
