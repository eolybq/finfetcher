# Welcome to FinFetcher

**FinFetcher** is a robust Python library designed for quantitative analysts and developers who need clean, market-aware historical financial data. It acts as a smart wrapper around `yfinance`, solving common issues with incomplete daily candles and timezone mismatches.

[![PyPI version](https://img.shields.io/pypi/v/finfetcher.svg)](https://pypi.org/project/finfetcher/)
[![License](https://img.shields.io/github/license/eolybq/finfetcher)](https://github.com/eolybq/finfetcher/blob/main/LICENSE)

---

## 🚀 Key Features

*   **Market-Aware Cleaning:** Automatically identifies if a market is currently open and removes the "unfinished" daily candle to prevent look-ahead bias.
*   **Timezone Intelligence:** Handles exchange-specific closing times for US Equities, European Markets, Asian Markets, and Crypto (UTC).
*   **Target Date Calculation:** Automatically computes the next valid trading day (or calendar day for 24/7 assets) for predictive modeling.
*   **Robust Error Handling:** Custom exceptions for missing tickers, empty data, or connection issues.
*   **Multi-Asset Support:** Native support for Equities, ETFs, Crypto, Forex, Futures, and Indices.

## 📦 Installation

Install via pip:

```bash
pip install finfetcher
```

## ⚡ Quick Start

```python
from finfetcher import DataFetcher

# 1. Initialize
fetcher = DataFetcher("AAPL")

# 2. Fetch clean data
df = fetcher.get_data(period="1y")

# 3. Access results
print(df.tail())
print(f"Prediction Target Date: {fetcher.target_date}")
```

## ❓ Why FinFetcher?

Standard data fetching tools often return the current day's data even if the market hasn't closed. For a model trained on "Close" prices, treating a 10:00 AM price as the final "Close" for the day introduces significant noise and bias.

**FinFetcher** checks the asset's specific exchange hours against the current server time and strictly enforces a "closed-only" policy for the current day's row.
