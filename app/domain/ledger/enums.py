from enum import StrEnum


class PostingType(StrEnum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class LedgerAccountType(StrEnum):
    """Standard double-entry account types.

    Normal balance (the side that increases the account):

    | Type      | Normal balance | Debit effect | Credit effect |
    |-----------|---------------|--------------|---------------|
    | ASSET     | Debit         | Increase     | Decrease      |
    | EXPENSE   | Debit         | Increase     | Decrease      |
    | LIABILITY | Credit        | Decrease     | Increase      |
    | EQUITY    | Credit        | Decrease     | Increase      |
    | REVENUE   | Credit        | Decrease     | Increase      |
    """

    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"


class JournalStatus(StrEnum):
    """Lifecycle status of a journal entry.

    State transitions:
        DRAFT → POSTED → REVERSED
    """

    DRAFT = "DRAFT"
    POSTED = "POSTED"
    REVERSED = "REVERSED"
