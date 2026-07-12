from collections.abc import Mapping
from dataclasses import replace

from app.common.ids import generate_prefixed_id
from app.core.constants import JournalReferencePrefix
from app.domain.ledger.enums import LedgerAccountType, PostingType
from app.domain.ledger.exceptions import JournalAlreadyPostedError, JournalImbalanceError
from app.domain.ledger.models import JournalEntry, LedgerAccount

# Account types whose normal balance is a DEBIT (i.e. debits increase, credits decrease).
_DEBIT_NORMAL = {LedgerAccountType.ASSET, LedgerAccountType.EXPENSE}


class LedgerService:
    def post(
        self,
        journal: JournalEntry,
        accounts: Mapping[str, LedgerAccount],
    ) -> JournalEntry:
        """Apply a journal entry to the provided ledger accounts.

        Expects a mapping of ``ledger_account_id → LedgerAccount``.

        Applies standard double-entry normal-balance rules:

        - ASSET / EXPENSE  → Debit increases, Credit decreases.
        - LIABILITY / EQUITY / REVENUE → Credit increases, Debit decreases.

        Returns:
            A new, frozen, posted ``JournalEntry`` (the original is never mutated).

        Raises:
            JournalAlreadyPostedError: If the journal has already been posted.
            JournalImbalanceError: If debits ≠ credits.
            ValueError: If a posting references an account not in ``accounts``.
        """
        if journal.posted:
            raise JournalAlreadyPostedError()

        if not journal.is_balanced:
            raise JournalImbalanceError()

        for posting in journal.postings:
            account = accounts.get(posting.ledger_account_id)
            if not account:
                raise ValueError(
                    f"Account '{posting.ledger_account_id}' not provided for posting."
                )

            debit_normal = account.account_type in _DEBIT_NORMAL

            if posting.side is PostingType.DEBIT:
                # Debit: increases debit-normal accounts, decreases credit-normal accounts.
                if debit_normal:
                    account.balance += posting.amount
                else:
                    account.balance -= posting.amount
            else:
                # Credit: increases credit-normal accounts, decreases debit-normal accounts.
                if debit_normal:
                    account.balance -= posting.amount
                else:
                    account.balance += posting.amount

        return replace(journal, posted=True)

    def reverse(
        self,
        original_journal: JournalEntry,
        reference_prefix: str = JournalReferencePrefix.REVERSAL,
    ) -> JournalEntry:
        """Create a reversal journal for an existing posted journal entry.

        Does not mutate or delete the original journal, preserving immutable
        accounting history. The reversal journal is returned *unposted* — call
        ``post()`` to apply it.

        Args:
            original_journal: The posted journal to reverse.
            reference_prefix: Prefix used to build the reversal reference.
                Defaults to ``JournalReferencePrefix.REVERSAL`` (``"REV"``).

        Raises:
            ValueError: If ``original_journal`` has not been posted yet.
        """
        if not original_journal.posted:
            raise ValueError("Cannot reverse an unposted journal.")

        new_postings = [
            replace(
                p,
                id=generate_prefixed_id("pst"),
                side=PostingType.CREDIT if p.side is PostingType.DEBIT else PostingType.DEBIT,
            )
            for p in original_journal.postings
        ]

        return JournalEntry(
            id=generate_prefixed_id("jrn"),
            reference=f"{reference_prefix}-{original_journal.reference}",
            description=f"Reversal of {original_journal.id}",
            postings=new_postings,
            posted=False,
        )
