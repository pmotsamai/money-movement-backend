# Market Data Service

Fetches historical stock price data and computes return analytics using yfinance.

## Usage
python market_data_service.py

## Classes

### MarketDataFetcher
Fetches and stores historical OHLCV data for one or more tickers.
- `fetch()` — retrieves price data from yfinance
- `save_to_csv(output_dir)` — saves each ticker to its own CSV

### Analytics
Computes return analytics for a single ticker DataFrame.
- `compute_returns()` — daily log returns
- `compute_sharpe()` — 30-day rolling annualized Sharpe ratio
- `compute_var()` — 95% historical Value at Risk
- `compute_rolling_var()` — 30-day rolling VaR

## Requirements
pip install yfinance pandas numpy