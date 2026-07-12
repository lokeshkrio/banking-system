from enum import StrEnum


class TransactionType(StrEnum):
    """Types of transaction operations."""

    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"


class TransactionStatus(StrEnum):
    """Lifecycle states of a transaction."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"
