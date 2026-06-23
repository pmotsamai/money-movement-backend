from account_service import *
from market_data_service import MarketDataFetcher
import pytest

def test_insufficent_funds():
    my_acct = Account("Pule's Investments", 200.00)
    with pytest.raises(ValueError):
        my_acct.buy("FAKESTOCK", 10, 30.561)


def test_insufficent_holdings():
    my_acct = Account("Pule's Investments", 200.00)
    my_acct.buy("FAKESTOCK", 5, 30.561)
    with pytest.raises(ValueError):
        my_acct.sell("FAKESTOCK", 10, 30.561) 

def test_bal_pos_changes():
    my_acct = Account("Pule's Investments", 200.00)
    my_acct.buy("FAKESTOCK", 5, 20.00)
    my_acct.sell("FAKESTOCK", 5, 20.00) 


    assert "FAKESTOCK" not in my_acct.positions
    assert my_acct.cash_bal == 200.00

def test_net_value():
    my_acct = Account("Pule's Investments", 200.00)
    my_acct.buy("FAKESTOCK", 5, 20.00)
    market_prices = {"FAKESTOCK": 25.00}
    
    assert my_acct.get_net_value(market_prices) == 225

def test_ledger():
    my_acct = Account("Pule's Investments", 200.00)
    my_acct.buy("FAKESTOCK", 5, 20.00)
    my_ledger = my_acct.ledger.get_history()
    assert my_ledger[0].entry_type == EntryType.BUY
    assert my_ledger[0].cash_delta == -100
    assert my_ledger[0].cash_balance == 100
    assert my_ledger[0].ticker == "FAKESTOCK"
    assert my_ledger[0].quantity == 5
    assert my_ledger[0].price == 20

def test_avg_cost():
    my_acct = Account("Pule's Investments", 200.00)
    my_acct.buy("FAKESTOCK", 5, 20.00)
    my_acct.buy("FAKESTOCK", 5, 10.00)
    
    assert my_acct.positions["FAKESTOCK"].avg_cost == 15.00

