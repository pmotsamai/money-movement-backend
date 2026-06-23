from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class Account:
    def __init__(self, name: str, cash_bal: float):
        self.name = name
        self.cash_bal = cash_bal
        self.positions = {}
        self.ledger = Ledger()

    def deposit(self, amount: float) -> LedgerEntry:
        self.cash_bal += amount
        entry = self.ledger.record(LedgerEntry(EntryType.DEPOSIT, datetime.now(), amount, self.cash_bal))

        return entry

    def withdraw(self, amount: float) -> LedgerEntry:
        if amount > self.cash_bal:
            raise ValueError("Insufficient Funds")
        self.cash_bal -= amount
        entry = self.ledger.record(LedgerEntry(EntryType.WITHDRAWAL, datetime.now(), -1 * amount, self.cash_bal))

        return entry

    def buy(self, ticker: str, quantity: float, price: float) -> LedgerEntry:
        amount = quantity * price
        if amount > self.cash_bal:
            raise ValueError("Insufficient Funds")
        
        if ticker not in self.positions:
            self.positions[ticker] = Position(ticker, quantity, price, amount)

        else:
            self.positions[ticker].total_invested += amount
            self.positions[ticker].quantity += quantity
            self.positions[ticker].update_avg_cost()

        self.cash_bal -= amount
        entry = self.ledger.record(LedgerEntry(EntryType.BUY, datetime.now(), -1 * amount, self.cash_bal, ticker, quantity, price))

        return entry
    
    def sell(self, ticker: str, quantity: float, price: float) -> LedgerEntry:
        amount = quantity * price
        if ticker not in self.positions or quantity > self.positions[ticker].quantity:
            raise ValueError("Insufficient Holdings")  

        else:
            self.positions[ticker].total_invested -= amount
            self.positions[ticker].quantity -= quantity
            self.positions[ticker].update_avg_cost()

        self.cash_bal += amount
        entry = self.ledger.record(LedgerEntry(EntryType.SELL, datetime.now(), amount, self.cash_bal, ticker, quantity, price))

        if self.positions[ticker].quantity ==0:
            del self.positions[ticker]

        return entry
    
    def get_balance(self) -> float:
        return self.cash_bal
    
    def get_net_value(self, market_prices: dict) -> float:
        net_value = self.cash_bal
        for ticker in self.positions:
            net_value += self.positions[ticker].market_value(market_prices[ticker])

        return net_value


class Position:
    def __init__(self, ticker: str, quantity: float, avg_cost: float, total_invested: float):
        self.ticker = ticker
        self.quantity = quantity
        self.avg_cost = avg_cost
        self.total_invested = total_invested

    def update_avg_cost(self):
        if self.quantity == 0:
            self.avg_cost = 0
        else:
            self.avg_cost = self.total_invested / self.quantity
        

    def market_value(self, current_price: float) -> float:
        return current_price * self.quantity
    
    def unrealized_pnl(self, current_price: float) -> float:
        return self.market_value(current_price) - self.avg_cost * self.quantity
    
class EntryType(Enum):
        DEPOSIT = "deposit"
        WITHDRAWAL = "withdrawal"
        BUY = "buy"
        SELL = "sell"

@dataclass(frozen=True)
class LedgerEntry:
    entry_type: EntryType
    timestamp: datetime
    cash_delta: float
    cash_balance: float
    ticker: Optional[str] = None
    quantity: Optional[float] = None
    price: Optional[float] = None

class Ledger: #Records cash movement 
    def __init__(self):
        self.ledger = []

    def record(self, entry: LedgerEntry) -> LedgerEntry:
        self.ledger.append(entry)
        return entry

    #returns a copy so the internal Ledger cannot be modified
    def get_history(self) -> list:
        return self.ledger.copy()