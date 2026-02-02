# FinFetcher

[![PyPI version](https://img.shields.io/pypi/v/finfetcher.svg)](https://pypi.org/project/finfetcher/)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](#)
[![License](https://img.shields.io/github/license/eolybq/finfetcher)](https://github.com/eolybq/finfetcher/blob/main/LICENSE)
[![Tests](https://github.com/eolybq/finfetcher/actions/workflows/python-package.yml/badge.svg)](https://github.com/eolybq/finfetcher/actions)

> **Quick Summary:** A robust Python library for fetching clean, market-aware historical financial data. It acts as a smart wrapper around `yfinance`, automatically handling asset-specific market hours and timezones to ensure data integrity for quantitative modeling and backtesting.

---

## 📊 The Problem it Solves

When fetching daily data during active market hours, standard tools often return an "unfinished" candle for the current day. Using this incomplete data point can introduce significant look-ahead bias or noise in statistical models.

**FinFetcher** solves this by:
1.  **Identifying the asset's exchange timezone** (e.g., NYSE vs. Tokyo SE vs. Crypto).
2.  **Checking the exact market status** relative to the server time.
3.  **Automatically filtering out** the current day's row if the market hasn't closed yet.
4.  **Calculating the valid `target_date`** (next trading day) for forecasting targets.

---

## 🏆 Key Capabilities

| Component | Feature | Details |
| :--- | :--- | :--- |
| **Smart Ingestion** | Market-aware cleaning. | Removes incomplete daily candles based on precise closing times (e.g., 16:20 ET for US Equities to account for delay). |
| **Multi-Asset** | Native handling for various types. | `EQUITY` (Stocks/ETFs), `CRYPTOCURRENCY` (24/7), `FUTURES`, `FOREX`, `INDEX`. |
| **Forecasting Prep** | Target Date Calculation. | Automatically computes the next valid business day (or calendar day for Crypto) for predictive labeling. |
| **Resiliency** | Robust Error Handling. | Wraps `yfinance` with retry logic and custom exceptions for better pipeline stability. |

---

## 📦 Installation

```bash
pip install finfetcher
```

---

## 🚀 Usage

### Basic Example

```python
from finfetcher import DataFetcher

# Initialize for an asset (Equity)
fetcher = DataFetcher("AAPL")

# Fetch data (default: period="4y", interval="1d")
# This returns a pandas DataFrame with Date index
df = fetcher.get_data(period="1mo")

print(f"Data shape: {df.shape}")
print(f"Last available close: {df.index[-1]}")

# Access the calculated target date (next trading day)
print(f"Prediction Target Date: {fetcher.target_date}")
```

### Handling Cryptocurrencies
Crypto markets never close, so the logic adjusts to use a 23:59 UTC cutoff.

```python
crypto_fetcher = DataFetcher("BTC-USD")
df = crypto_fetcher.get_data(period="5d")

# Target date will be tomorrow (calendar day), not business day
print(f"Next Target: {crypto_fetcher.target_date}")
```

### Custom Market Configuration
You can override default market hours or add new asset types by passing a `custom_cutoffs` dictionary.

```python
from finfetcher import DataFetcher

# Example: Change US Equity close to 13:00 (e.g. half-day)
custom_config = {
    "EQUITY": {
        "timezones": {
            "America/New_York": {"hour": 13, "minute": 0}
        }
    }
}

fetcher = DataFetcher("AAPL", custom_cutoffs=custom_config)
df = fetcher.get_data()
```

---

## 🛠️ Logic Details

The library contains a set of configuration of market closing times (`src/finfetcher/config.py`) to handle timezone conversions accurately.

*   **US Equities:** Closes at 16:00 ET (buffered to 16:20 to handle API delays).
*   **European Markets:** Handled via specific timezones (London, Paris, Frankfurt, etc.).
*   **Asian Markets:** Tokyo, Hong Kong, Singapore, etc.
*   **Crypto:** UTC based cutoff.

## 💻 Tech Stack
*   **Python 3.10+**
*   **Pandas & NumPy**
*   **yfinance**
*   **pytz**
