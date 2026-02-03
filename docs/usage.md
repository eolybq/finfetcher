# Usage Guide

## Basic Usage

The most common use case is fetching daily data for stocks or ETFs.

```python
from finfetcher import DataFetcher

# Initialize for Apple Inc.
fetcher = DataFetcher("AAPL")

try:
    # Fetch last 2 years of daily data
    data = fetcher.get_data(period="2y", interval="1d")
    
    print(data.head())
    print(f"Next trading day: {fetcher.target_date}")

except Exception as e:
    print(f"Error fetching data: {e}")
```

## Handling Cryptocurrencies

Cryptocurrency markets operate 24/7. `FinFetcher` handles this by using a UTC cutoff (23:59 UTC) to define the end of a "day".

```python
# Initialize for Bitcoin
btc_fetcher = DataFetcher("BTC-USD")

df = btc_fetcher.get_data(period="1mo")

# For crypto, target_date is typically the next calendar day
print(f"Target Date: {btc_fetcher.target_date}")
```

## Advanced: Custom Market Hours

Sometimes you may want to override the default market hours (e.g., for half-days, or specific strategy requirements) or add support for a new asset class.

You can achieve this by passing a `custom_cutoffs` dictionary to the `DataFetcher`.

### Structure

The configuration dictionary follows this hierarchy:
`Asset Type` -> `Timezones` (or `default`) -> `Hour/Minute`

### Example: Half-Day on NYSE

```python
from finfetcher import DataFetcher

# Define custom config
my_config = {
    "EQUITY": {
        "timezones": {
            # Force close at 13:00 (1:00 PM) for New York
            "America/New_York": {"hour": 13, "minute": 0}
        }
    }
}

fetcher = DataFetcher("SPY", custom_cutoffs=my_config)
data = fetcher.get_data()
```

### Example: Adding a Custom Asset Class

```python
from finfetcher import DataFetcher

# Define a new asset type with specific closing rules
my_config = {
    "MY_CUSTOM_ASSET": {
        "force_tz": "Asia/Tokyo",
        "default": {"hour": 15, "minute": 0}
    }
}

# Note: yfinance must still recognize the ticker!
fetcher = DataFetcher("7203.T", custom_cutoffs=my_config)
```
