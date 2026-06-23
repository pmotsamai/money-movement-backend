from market_data_service import MarketDataFetcher, Analytics
import pandas as pd

def test_fetch_returns_data():
    fetcher = MarketDataFetcher(["AAPL"], "2024-01-01", "2024-04-01")
    test = fetcher.fetch()
    assert test["AAPL"] is not None
    assert "Close" in test["AAPL"].columns

def test_comp_returns_adds_columns():
    test = Analytics(pd.DataFrame({"Close": [100, 101, 99, 102, 98]}))
    test.compute_returns()
    assert "Return" in test.df.columns

def test_compute_var_is_positive():
    test = Analytics(pd.DataFrame({"Close": [100, 101, 99, 102, 98]}))
    assert test.compute_var() >= 0
