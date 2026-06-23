import yfinance as yf
import logging
import os
import numpy as np
import pandas as pd
import time
from datetime import datetime

MAX_ATTEMPTS = 3
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('fetch_log')

class MarketDataFetcher:

    def __init__(self, tickers: list, start: datetime, end: datetime):
        self.tickers = tickers
        self.start = start or  datetime.today()
        self.end = end or datetime.today()
        self.data = {}

    def fetch(self) -> dict:
        df = None
        for ticker in self.tickers:
            for attempt in range(MAX_ATTEMPTS):
                try:
                    stock = yf.Ticker(ticker)
                    df = stock.history(start = self.start, end = self.end)
                    break
                except Exception as e:
                    LOGGER.warning(f"{ticker} attempt {attempt} failed: {e}")
                    if attempt < MAX_ATTEMPTS - 1:
                        time.sleep(2 ** attempt)
                    else:
                        LOGGER.warning(f"All attempts for {ticker} failed")
                        break

            if df is None or df.empty:
                LOGGER.warning(f"Invalid or empty data for ticker {ticker}")
                continue

            self.data[ticker] = df
            LOGGER.info(f"fetched data for {ticker}")
    
        return self.data
    
    def get_current_price(self, ticker: str) -> float:
        if ticker not in self.data:
            raise ValueError(f"No data for {ticker} — call fetch() first")
        
        latest_date = self.data[ticker].index[-1].date()
        if latest_date < datetime.today().date():
            raise ValueError(f"Data for {ticker} is stale — latest date is {latest_date}")
        
        return self.data[ticker]["Close"].iloc[-1]
        
    def save_to_csv(self, output_dir: str) -> None:
        if self.data:
            os.makedirs(output_dir, exist_ok=True)
            for ticker in self.data:
                self.data[ticker].to_csv(f"{output_dir}/{ticker}.csv", index=False)
                LOGGER.info(f"Saved {ticker} to {output_dir}")

        else:
            LOGGER.warning("No data available, call fetch() first")

class Analytics:

    def __init__(self, df: pd.DataFrame, window: int = 30, confidence: float = 0.95):
        self.df = df.copy()
        self.window = window
        self.confidence = confidence

    def compute_returns(self) -> pd.Series:
        if "Close" not in self.df.columns:
            LOGGER.warning("DataFrame missing 'Close' Column")
            raise ValueError("DataFrame missing 'Close' Column")
        self.df["Return"] = np.log(self.df["Close"] / self.df["Close"].shift(1))

        return self.df["Return"]
    
    def _ensure_returns(self) -> None:
            if "Return" not in self.df.columns:
                LOGGER.info("DataFrame missing 'Return' column-- adding now")
                self.compute_returns()         

    def compute_sharpe(self) -> pd.Series:
        self._ensure_returns()

        avg = self.df["Return"].rolling(self.window).mean()
        std = self.df["Return"].rolling(self.window).std()
        self.df["Sharpe"] = (avg/std) * np.sqrt(252)

        return self.df["Sharpe"]


    def compute_var(self) -> float:
        self._ensure_returns()  

        return -1 * np.nanpercentile(self.df["Return"], (1 - self.confidence) * 100) #nanpercential skips NaN in first row (no prior close)

    def _compute_window_var(self, w: pd.Series) -> float:
        return -1 * np.nanpercentile(w, (1 - self.confidence) * 100)                   

    def compute_rolling_var(self) -> pd.Series:
        self._ensure_returns()
        r_vars = self.df["Return"].rolling(self.window).apply(self._compute_window_var)

        return r_vars





if __name__ == "__main__":
    fetcher = MarketDataFetcher(["AAPL"], datetime.today(), datetime.today())
    fetcher.fetch()
    print(fetcher.get_current_price("AAPL"))
    # analytics = Analytics(fetcher.data["AAPL"])
    # analytics.compute_sharpe()
    # analytics.compute_rolling_var()