import unittest
from datetime import date, datetime
from unittest.mock import patch

import pandas as pd
import pytz

from finfetcher.services.fetch_data import get_complete_close


class TestCleaningLogic(unittest.TestCase):
    def setUp(self):
        # Create a dummy DataFrame with a "today" row
        self.today = date(2023, 10, 27)  # A Friday
        dates = pd.to_datetime(["2023-10-25", "2023-10-26", "2023-10-27"]).date
        self.df = pd.DataFrame(
            {"Open": [100, 101, 102], "Close": [105, 106, 107]}, index=dates
        )

    @patch("finfetcher.services.fetch_data.datetime")
    def test_remove_unfinished_candle_market_open(self, mock_datetime):
        """
        Scenario: Market is EQUITY (NY), Closing is 16:20.
        Current time: 15:30 (Market Open).
        Result: Last row (today) should be REMOVED.
        """
        # Mock "now" to be 15:30 NY time on the same day as the last row
        ny_tz = pytz.timezone("America/New_York")
        mock_now = ny_tz.localize(datetime(2023, 10, 27, 15, 30))

        # Configure the mock to return our specific "now" when now(tz) is called
        mock_datetime.now.side_effect = (
            lambda tz=None: mock_now.astimezone(tz) if tz else mock_now
        )

        cleaned_df = get_complete_close(
            self.df.copy(),
            asset_type="EQUITY",
            last_day_df=self.today,
            ticker_tz_name="America/New_York",
        )

        self.assertEqual(
            len(cleaned_df), 2, "Should remove the last row as market is still open"
        )
        self.assertEqual(cleaned_df.index[-1], date(2023, 10, 26))

    @patch("finfetcher.services.fetch_data.datetime")
    def test_keep_finished_candle_market_closed(self, mock_datetime):
        """
        Scenario: Market is EQUITY (NY), Closing is 16:20.
        Current time: 17:00 (Market Closed).
        Result: Last row (today) should be KEPT.
        """
        ny_tz = pytz.timezone("America/New_York")
        mock_now = ny_tz.localize(datetime(2023, 10, 27, 17, 00))

        mock_datetime.now.side_effect = (
            lambda tz=None: mock_now.astimezone(tz) if tz else mock_now
        )

        cleaned_df = get_complete_close(
            self.df.copy(),
            asset_type="EQUITY",
            last_day_df=self.today,
            ticker_tz_name="America/New_York",
        )

        self.assertEqual(
            len(cleaned_df), 3, "Should keep the last row as market is closed"
        )
        self.assertEqual(cleaned_df.index[-1], self.today)

    @patch("finfetcher.services.fetch_data.datetime")
    def test_crypto_always_open(self, mock_datetime):
        """
        Scenario: Market is CRYPTO (24/7), Cutoff is 23:59 UTC.
        Current time: 10:00 UTC.
        Result: Should behave according to config (usually remove if strictly
        < cutoff, but crypto often implies yesterday close).
        Based on your config: CRYPTO cutoff is 23:59. If now is 10:00 and we
        have a row for today, it's unfinished.
        """
        utc_tz = pytz.timezone("UTC")
        mock_now = utc_tz.localize(datetime(2023, 10, 27, 10, 00))

        mock_datetime.now.side_effect = (
            lambda tz=None: mock_now.astimezone(tz) if tz else mock_now
        )

        cleaned_df = get_complete_close(
            self.df.copy(),
            asset_type="CRYPTOCURRENCY",
            last_day_df=self.today,
            ticker_tz_name="UTC",
        )

        self.assertEqual(
            len(cleaned_df),
            2,
            "Should remove today's row for Crypto if current time < 23:59",
        )


if __name__ == "__main__":
    unittest.main()
