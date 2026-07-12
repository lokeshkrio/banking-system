from dataclasses import dataclass

from app.common.money import Money
from app.domain.transaction.enums import TransactionStatus, TransactionType


@dataclass(frozen=True, slots=True)
class Transaction:
    """Immutable domain model representing a Transaction (Deposit/Withdrawal)."""

    id: str
    account_id: str
    amount: Money
    type: TransactionType
    status: TransactionStatus
    reference: str
    description: str
    journal_id: str | None = None
