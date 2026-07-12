# Fintech Core Banking Engine

A small, high-performance, and extremely well-designed ledger engine built in Python. This project focuses on the core banking primitives: atomic double-entry accounting, immutable journals, IBAN account generation, and cross-currency forex transfers.

## Features

- **Double-Entry Ledger Engine:** Every transaction is recorded as a balanced, immutable journal entry (Debits = Credits).
- **Cross-Currency FX Transfers:** Natively handles transfers between different currencies by automatically inserting dual-journal entries against central FX clearing accounts.
- **Strict Domain Invariants:**
  - `JournalEntry` is immutable once created. State transitions use strict `JournalStatus` enums (`DRAFT` → `POSTED`).
  - `LedgerAccount` balances are strongly encapsulated; mutations only occur via strict `apply_debit()` and `apply_credit()` methods respecting normal-balance rules.
  - Hard guards prevent negative balances and operations on `FROZEN`, `CLOSED`, or `SUSPENDED` accounts.
- **IBAN Account Generation:** Includes a Mod97 check-digit engine and format generator for compliant banking account numbers.
- **Type-Safe Domain:** Heavily typed Python codebase utilizing `dataclasses`, `StrEnum`, protocols, and custom `Money` value objects (handling minor currency units accurately).

## Architecture

The system is designed around Domain-Driven Design (DDD) principles:

- **Entities & Value Objects:** `Money`, `Account`, `LedgerAccount`, `JournalEntry`, `Posting`, `Transfer`.
- **Services:**
  - `LedgerService`: The lowest-level accounting engine. Responsible for posting balanced journals and applying rules.
  - `TransactionService`: Handles single-account primitives like `Deposit` and `Withdrawal` against central funding/clearing accounts.
  - `TransferService`: Orchestrates complex multi-account transfers (P2P), including cross-currency exchange routing.
- **Ports & Adapters (Protocols):** Repositories are defined as `Protocols` (`CustomerRepository`, `AccountRepository`, etc.) keeping the core domain completely decoupled from the database layer.

## Folder Structure

```text
app/
├── api/             # (Planned) REST/GraphQL entry points
├── common/          # Shared utilities (Money, Enums, ID generation, IBAN generator)
├── core/            # System constants, exception hierarchies, app settings
├── domain/          # Core business logic (DDD)
│   ├── accounts/    # Customer account models
│   ├── customer/    # Customer models
│   ├── ledger/      # Double-entry accounting engine (Journal, Postings, Ledger)
│   ├── transaction/ # Deposits and withdrawals
│   ├── transfer/    # P2P Transfers
│   └── repository.py # Database interfaces (Protocols)
├── forex/           # Exchange rate registry
└── tests/           # Comprehensive pytest suite
```

## How Transfers Work

A transfer requires moving money from a `Source Account` to a `Destination Account`. Because this system relies on a double-entry ledger, it never simply updates a balance.

### 1. Same-Currency Transfer
If Alice (USD) sends to Bob (USD):
1. **Validation:** Checks account states (`ACTIVE`), verifies sufficient funds.
2. **Journal Creation (`DRAFT`):**
   - Debit: Alice's Ledger Account
   - Credit: Bob's Ledger Account
3. **Posting:** `LedgerService` validates the journal is balanced. Balances are updated via `apply_debit`/`apply_credit`.
4. **Completion:** The Journal is marked `POSTED` and the Transfer status is updated to `COMPLETED`.

### 2. Cross-Currency Transfer
If Alice (USD) sends to Bob (EUR):
1. **Validation:** Same as above.
2. **FX Calculation:** Fetches the current `USD -> EUR` exchange rate.
3. **Dual-Journal Creation:**
   - *Source Journal (USD):* Debits Alice's account, Credits the Bank's central `FX_USD` account.
   - *Destination Journal (EUR):* Debits the Bank's central `FX_EUR` account, Credits Bob's account.
4. **Posting:** Both journals are posted atomically. The bank holds the currency float in the central FX accounts.

## Development

The project uses `pytest` for testing. To run the full test suite:

```bash
uv run pytest tests/ -v
```

## Roadmap

- [x] Immutable Double-Entry Ledger
- [x] Mod97 IBAN Generation
- [x] Cross-Currency FX Engine
- [ ] Relational Database Persistence (SQLAlchemy/Alembic)
- [ ] API Layer (FastAPI)
- [ ] Containerization (Docker)
- [ ] Idempotency keys for transaction processing
