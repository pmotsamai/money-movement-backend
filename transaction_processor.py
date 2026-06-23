from market_data_service import MarketDataFetcher
from account_service import *
from dataclasses import dataclass

class TransactionStatus(Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CLEARED = "cleared"
    SETTLED = "settled"
    FAILED = "failed"


@dataclass
class Transaction:
    key: str
    type: EntryType
    status: TransactionStatus
    amount: float
    ticker: str = None
    quantity: int = None
    entry: Optional[LedgerEntry] = None



class TransactionProcessor:

    def __init__(self, account: Account, market_data_fetcher: MarketDataFetcher):
        self.account = account
        self.market_data_fetcher = market_data_fetcher
        self._processed_keys = {}


    def access_price(self, ticker: str) -> float:
        price = self.market_data_fetcher.get_current_price(ticker)
        return price
        
    def execute_deposit(self, amount: float) -> LedgerEntry:
        entry = self.account.deposit(amount)
        return entry
    
    def execute_withdraw(self, amount: float) -> LedgerEntry:
        entry = self.account.withdraw(amount)
        return entry


    def execute_buy(self, ticker: str, quantity: int) -> LedgerEntry:
        price = self.access_price(ticker)
        entry = self.account.buy(ticker, quantity, price)

        return entry
    
    def execute_sell(self, ticker: str, quantity: int) -> LedgerEntry:
        price = self.access_price(ticker)
        entry = self.account.sell(ticker, quantity, price)
        return entry
        

    def process_transaction(self, key: str, type: EntryType, ticker: str, quantity: int, amount: float) -> LedgerEntry:
        transaction = Transaction(key, type, TransactionStatus.PENDING, amount, ticker, quantity)

        if key in self._processed_keys:
            return self._processed_keys[key]
        
        transaction.status = TransactionStatus.AUTHORIZED

        try:
            match type:
                case EntryType.BUY:
                    entry = self.execute_buy(ticker, quantity)
                case EntryType.SELL:
                    entry = self.execute_sell(ticker, quantity)
                case EntryType.DEPOSIT:
                    entry = self.execute_deposit(amount)
                case EntryType.WITHDRAWAL:
                    entry = self.execute_withdraw(amount)
                case _:
                    raise ValueError(f"Unknown transaction type: {type}")
        except ValueError:
            transaction.status = TransactionStatus.FAILED
            self._processed_keys[key] = transaction  
            raise  
        
        transaction.entry = entry
        transaction.status = TransactionStatus.SETTLED
        self._processed_keys[key] = transaction

        return transaction
    


