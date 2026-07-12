from collections.abc import Mapping
from dataclasses import replace

from app.common.ids import generate_prefixed_id
from app.core.constants import JournalReferencePrefix
from app.domain.ledger.enums import JournalStatus, PostingType
from app.domain.ledger.exceptions import JournalAlreadyPostedError, JournalImbalanceError
from app.domain.ledger.models import JournalEntry, LedgerAccount


class LedgerService:
    def post(
        self,
        journal: JournalEntry,
        accounts: Mapping[str, LedgerAccount],
    ) -> JournalEntry:
        """Apply a journal entry to the provided ledger accounts.

        Expects a mapping of ``ledger_account_id → LedgerAccount``.

        Uses ``LedgerAccount.apply_debit()`` / ``apply_credit()`` which
        encode standard double-entry normal-balance rules.

        Returns:
            A new, frozen ``JournalEntry`` with status ``POSTED``.

        Raises:
            JournalAlreadyPostedError: If the journal is not in DRAFT status.
            JournalImbalanceError: If debits ≠ credits.
            ValueError: If a posting references an account not in ``accounts``.
        """
        if journal.status is not JournalStatus.DRAFT:
            raise JournalAlreadyPostedError()

        if not journal.is_balanced:
            raise JournalImbalanceError()

        for posting in journal.postings:
            account = accounts.get(posting.ledger_account_id)
            if not account:
                raise ValueError(
                    f"Account '{posting.ledger_account_id}' not provided for posting."
                )

            if posting.side is PostingType.DEBIT:
                account.apply_debit(posting.amount)
            else:
                account.apply_credit(posting.amount)

        return replace(journal, status=JournalStatus.POSTED)

    def reverse(
        self,
        original_journal: JournalEntry,
        reference_prefix: str = JournalReferencePrefix.REVERSAL,
    ) -> JournalEntry:
        """Create a reversal journal for an existing posted journal entry.

        Does not mutate or delete the original journal, preserving immutable
        accounting history. The reversal journal is returned in ``DRAFT``
        status — call ``post()`` to apply it.

        Args:
            original_journal: The posted journal to reverse.
            reference_prefix: Prefix used to build the reversal reference.
                Defaults to ``JournalReferencePrefix.REVERSAL`` (``"REV"``).

        Raises:
            ValueError: If ``original_journal`` is not in ``POSTED`` status.
        """
        if original_journal.status is not JournalStatus.POSTED:
            raise ValueError("Cannot reverse a journal that is not POSTED.")

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
            status=JournalStatus.DRAFT,
        )
