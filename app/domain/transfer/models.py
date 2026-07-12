"""Domain model for a Transfer.

A Transfer represents the *business intent* to move funds between two accounts.
Internally it maps to a double-entry ``JournalEntry`` in the ledger subsystem.

Architecture:
    Transfer
        ↓ TransferService creates
    JournalEntry  (with balanced Postings)
        ↓ LedgerService.post() applies
    LedgerAccount balances updated
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.common.money import Money
from app.domain.transfer.enums import TransferStatus


@dataclass(frozen=True, slots=True)
class Transfer:
    """Immutable record of a fund transfer between two accounts.

    Attributes:
        id:                     Internal transfer ID (``trf_<uuid>``).
        source_account_id:      Internal ID of the sending account.
        destination_account_id: Internal ID of the receiving account.
        amount:                 Amount and currency to transfer.
        status:                 Current lifecycle state.
        reference:              External-facing reference (e.g. ``TXN0000001``).
        description:            Human-readable description.
        journal_id:             ID of the posted ``JournalEntry``, set once the
                                transfer has been completed (``None`` if pending
                                or failed before journal creation).
    """

    id: str
    source_account_id: str
    destination_account_id: str
    amount: Money
    status: TransferStatus
    reference: str
    description: str
    journal_id: str | None = None
    destination_journal_id: str | None = None
    exchange_rate: Decimal | None = None
