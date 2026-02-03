# Configuration & Market Hours

`FinFetcher` comes with a built-in database of market closing times to ensure accurate data cleaning. This configuration is located in `src/finfetcher/config.py`.

## Default Logic

The library uses the following logic to determine if the current day's candle is complete:

1.  **Identify Asset Type:** Based on the `instrumentType` returned by Yahoo Finance (e.g., `EQUITY`, `CRYPTOCURRENCY`, `FUTURE`).
2.  **Determine Timezone:**
    *   For **Equities**, it uses the `exchangeTimezoneName` (e.g., `America/New_York`).
    *   For **Crypto**, it forces `UTC`.
    *   For **Futures/Forex**, it defaults to `America/New_York` (unless overridden).
3.  **Check Cutoff:** It compares the current time in that timezone with the defined cutoff time.

## Built-in Cutoffs

!!! note "Buffer Time"
    Note that many cutoffs include a buffer (e.g., +20 minutes) to account for data delays from the provider.

### Equities (Stock/ETF/Index)

| Region/Exchange | Timezone | Cutoff Time (Local) |
| :--- | :--- | :--- |
| **USA / Canada** | America/New_York / Toronto | 16:20 |
| **UK (London)** | Europe/London | 16:50 |
| **Central Europe** | Europe/Berlin, Paris, etc. | 17:50 |
| **Japan** | Asia/Tokyo | 15:20 |
| **Hong Kong** | Asia/Hong_Kong | 16:20 |
| **Singapore** | Asia/Singapore | 17:20 |
| **India** | Asia/Kolkata | 15:50 |
| **Australia** | Australia/Sydney | 16:20 |
| *Default (Others)* | *Various* | 18:00 |

### Derivatives

| Type | Timezone | Cutoff Time |
| :--- | :--- | :--- |
| **Futures** | America/New_York | 17:20 |
| **Currencies (Forex)** | America/New_York | 17:20 |

### Cryptocurrency

| Type | Timezone | Cutoff Time |
| :--- | :--- | :--- |
| **All Crypto** | UTC | 23:59 |
