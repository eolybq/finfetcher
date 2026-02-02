class FinFetcherError(Exception):
    """Base exception for the FinFetcher library."""

    pass


class TickerNotFoundError(FinFetcherError):
    """Raised when the ticker symbol does not exist or cannot be found."""

    pass


class DataEmptyError(FinFetcherError):
    """
    Raised when the ticker exists, but no data was returned for the requested period.
    """

    pass


class YFinanceConnectionError(FinFetcherError):
    """Raised when there are network or API issues with yfinance."""

    pass
