# Money Movement Backend

A layered backend system for processing and tracking financial transactions, built in Python.

## Layers

### Layer 1 — Market Data Service
Fetches historical stock price data and computes return analytics.
- `MarketDataFetcher` — retrieves OHLCV data via yfinance; caches and saves to CSV
- `Analytics` — log returns, 30-day rolling Sharpe ratio, 95% historical VaR

### Layer 2 — Account & Ledger Service
Models accounts, positions, and a cash ledger.
- `Account` — cash balance, positions, deposit/withdraw/buy/sell with validation
- `Position` — tracks quantity, average cost, total invested, unrealized P&L
- `Ledger` — append-only cash ledger; returns immutable copies of history
- `LedgerEntry` — frozen dataclass recording each cash movement

### Layer 3 — Transaction Processor
Processes transactions with lifecycle management and idempotency guarantees.
- `TransactionProcessor` — orchestrates execution; enforces idempotency via client-generated keys; never re-executes a seen key
- `Transaction` — carries request fields, lifecycle status, and resulting ledger entry
- `TransactionStatus` — `PENDING → AUTHORIZED → SETTLED` (or `FAILED` on error)

## Design Notes
- **Cash ledger:** all ledger entries record cash movements; position state lives in `Account.positions`
- **Idempotency:** duplicate keys return the cached `Transaction` without re-executing
- **Atomicity:** account state is never mutated if validation fails; failed attempts are recorded for audit

## Requirements
```
pip install yfinance pandas numpy pytest
```

## Running Tests
```
pytest -v
```