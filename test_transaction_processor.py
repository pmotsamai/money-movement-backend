import pytest
from account_service import *
from transaction_processor import (TransactionProcessor, TransactionStatus)

# class MockMarketDataFetcher:
#     def get_current_price(self, ticker: str) -> float:
#         return 150.0

# def test_execute_buy_returns_ledger_entry():
#     acct1 = Account("Pule's money", 500.00)
#     fetcher = MockMarketDataFetcher()
#     processor = TransactionProcessor(acct1, fetcher)
#     ledger_entry = processor.execute_buy("AAPL", 2)
#     assert ledger_entry.quantity == 2

# def test_execute_buy_insufficient_funds():
#     acct2 = Account("Pule's money", 500.00)
#     fetcher = MockMarketDataFetcher()
#     processor = TransactionProcessor(acct2, fetcher)    
#     with pytest.raises(ValueError):
#         processor.execute_buy("AAPL", 20)

# def test_execute_sell_returns_ledger_entry():
#     acct3 = Account("Pule's money", 500.00)
#     fetcher = MockMarketDataFetcher()
#     processor = TransactionProcessor(acct3, fetcher)
#     processor.execute_buy("AAPL", 3)
#     ledger_entry = processor.execute_sell("AAPL", 2)
#     assert ledger_entry.entry_type == EntryType.SELL
#     assert ledger_entry.quantity == 2


# def test_execute_sell_returns_insufficient_holdings():
#     acct3 = Account("Pule's money", 500.00)
#     fetcher = MockMarketDataFetcher()
#     processor = TransactionProcessor(acct3, fetcher)
#     processor.execute_buy("AAPL", 2)
#     with pytest.raises(ValueError):
#         processor.execute_sell("AAPL", 3)




class FakeMarketDataFetcher:
    def __init__(self, price: float):
        self._price = price

    def get_current_price(self, ticker: str) -> float:
        return self._price


@pytest.fixture
def account():
    return Account("test_user", 1000.0)


@pytest.fixture
def processor(account):
    fetcher = FakeMarketDataFetcher(price=100.0)
    return TransactionProcessor(account, fetcher)


def test_buy_succeeds_and_settles(processor, account):

    txn = processor.process_transaction(
        key="k1", type=EntryType.BUY, ticker="AAPL", quantity=5, amount=0.0
    )
    assert txn.status == TransactionStatus.SETTLED
    assert txn.entry is not None                 
    assert account.cash_bal == 500.0             
    assert account.positions["AAPL"].quantity == 5


def test_deposit_succeeds_and_settles(processor, account):
    txn = processor.process_transaction(
        key="dep1", type=EntryType.DEPOSIT, ticker=None, quantity=None, amount=250.0
    )
    assert txn.status == TransactionStatus.SETTLED
    assert account.cash_bal == 1250.0


def test_same_key_does_not_execute_twice(processor, account):
    #prove the second call did NOT re-execute.

    first = processor.process_transaction(
        key="dup", type=EntryType.BUY, ticker="AAPL", quantity=5, amount=0.0
    )
    second = processor.process_transaction(
        key="dup", type=EntryType.BUY, ticker="AAPL", quantity=5, amount=0.0
    )
    assert first is second                      
    assert account.cash_bal == 500.0            
    assert account.positions["AAPL"].quantity == 5   


def test_buy_insufficient_funds_is_atomic(processor, account):
    with pytest.raises(ValueError):
        processor.process_transaction(
            key="broke", type=EntryType.BUY, ticker="AAPL", quantity=50, amount=0.0
        )
    assert account.cash_bal == 1000.0
    assert "AAPL" not in account.positions
    failed = processor._processed_keys["broke"]
    assert failed.status == TransactionStatus.FAILED
    assert failed.entry is None                  


def test_unknown_type_fails(processor, account):
    with pytest.raises(ValueError):
        processor.process_transaction(
            key="weird", type="not_a_real_type", ticker=None, quantity=None, amount=10.0
        )
    assert processor._processed_keys["weird"].status == TransactionStatus.FAILED
    assert account.cash_bal == 1000.0