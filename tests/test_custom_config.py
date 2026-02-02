import unittest
from datetime import date, datetime
from unittest.mock import patch

import pandas as pd
import pytz

from finfetcher.core import DataFetcher
from finfetcher.services.fetch_data import get_complete_close


class TestCustomConfig(unittest.TestCase):
    def test_data_fetcher_init_merges_config(self):
        """Test that DataFetcher correctly merges user config with defaults."""
        custom = {
            "EQUITY": {"default": {"hour": 10, "minute": 0}},
            "NEW_ASSET": {"force_tz": "UTC", "default": {"hour": 12, "minute": 0}},
        }
        fetcher = DataFetcher("AAPL", custom_cutoffs=custom)

        # Check merge of existing key
        # Default EQUITY has 'timezones', verify it's still there
        self.assertIn("timezones", fetcher.config["EQUITY"])
        # Verify override
        self.assertEqual(fetcher.config["EQUITY"]["default"], {"hour": 10, "minute": 0})

        # Check new key
        self.assertIn("NEW_ASSET", fetcher.config)
        self.assertEqual(fetcher.config["NEW_ASSET"]["force_tz"], "UTC")

    @patch("finfetcher.services.fetch_data.datetime")
    def test_get_complete_close_uses_custom_config(self, mock_datetime):
        """Test that get_complete_close respects custom cutoff times."""
        # Setup: Current time is 12:00 NY
        tz = pytz.timezone("America/New_York")
        # create a datetime that is timezone aware
        mock_now = datetime(2023, 10, 10, 12, 0, 0).replace(tzinfo=tz)
        mock_datetime.now.return_value = mock_now

        # Dataframe has a row for today (2023-10-10)
        df = pd.DataFrame(
            {"Close": [100, 101]}, index=[date(2023, 10, 9), date(2023, 10, 10)]
        )

        # Scenario 1: Default config (cutoff ~16:20 for Equity).
        # 12:00 < 16:20 is True. Should remove today.
        res_default = get_complete_close(
            df.copy(),
            "EQUITY",
            date(2023, 10, 10),
            "America/New_York",
            market_config=None,
        )
        self.assertEqual(len(res_default), 1)
        self.assertEqual(res_default.index[-1], date(2023, 10, 9))

        # Scenario 2: Custom config (cutoff 11:00).
        # 12:00 < 11:00 is FALSE. Should KEEP today.
        custom_config = {
            "EQUITY": {
                "timezones": {"America/New_York": {"hour": 11, "minute": 0}},
                "default": {"hour": 18, "minute": 0},
            }
        }
        res_custom = get_complete_close(
            df.copy(),
            "EQUITY",
            date(2023, 10, 10),
            "America/New_York",
            market_config=custom_config,
        )
        self.assertEqual(len(res_custom), 2)
        self.assertEqual(res_custom.index[-1], date(2023, 10, 10))

    @patch("finfetcher.core.fetch_data")
    def test_data_fetcher_passes_config(self, mock_fetch_data):
        """Test that DataFetcher.get_data passes the config to fetch_data."""
        # Setup mock return
        mock_fetch_data.return_value = (pd.DataFrame(), None)

        # Must be valid structure now
        custom = {"TEST_ASSET": {"default": {"hour": 10, "minute": 0}}}
        fetcher = DataFetcher("AAPL", custom_cutoffs=custom)
        fetcher.get_data()

        # Verify call args
        args, kwargs = mock_fetch_data.call_args
        self.assertIn("market_config", kwargs)
        self.assertIn("TEST_ASSET", kwargs["market_config"])
