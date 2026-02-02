import unittest
from datetime import date
from unittest.mock import patch

import pandas as pd

from finfetcher import DataFetcher
from finfetcher.exceptions import TickerNotFoundError


class TestCoreMocked(unittest.TestCase):
    @patch("finfetcher.core.fetch_data")
    @patch("finfetcher.core.yf.Ticker")
    def test_get_data_success(self, mock_ticker_cls, mock_fetch_data):
        """Test happy path: fetch_data returns valid DF and date."""
        # Setup Mock
        mock_df = pd.DataFrame({"Close": [100]}, index=[date(2023, 1, 1)])
        mock_target = date(2023, 1, 2)
        mock_fetch_data.return_value = (mock_df, mock_target)

        # Execute
        fetcher = DataFetcher("AAPL")
        result = fetcher.get_data()

        # Verify
        pd.testing.assert_frame_equal(result, mock_df)
        self.assertEqual(fetcher.target_date, mock_target)
        mock_fetch_data.assert_called_once()

    @patch("finfetcher.core.fetch_data")
    @patch("finfetcher.core.yf.Ticker")
    def test_propagate_exceptions(self, mock_ticker_cls, mock_fetch_data):
        """Test that exceptions from fetch_data are propagated correctly."""
        mock_fetch_data.side_effect = TickerNotFoundError("Mocked not found")

        fetcher = DataFetcher("BAD_TICKER")

        with self.assertRaises(TickerNotFoundError):
            fetcher.get_data()


if __name__ == "__main__":
    unittest.main()
