from collections.abc import Mapping
from dataclasses import replace

from app.common.ids import generate_prefixed_id
from app.domain.ledger.enums import PostingType
from app.domain.ledger.exceptions import JournalAlreadyPostedError, JournalImbalanceError
from app.domain.ledger.models import JournalEntry, LedgerAccount


class LedgerService:
    def post(self, journal: JournalEntry, accounts: Mapping[str, LedgerAccount]) -> None:
        """
        Apply a journal entry to the provided ledger accounts.
        Expects a dictionary mapping ledger_account_id to LedgerAccount instances.
        Follows the Banking convention: Debit increases asset, Credit decreases asset.
        """
        if journal.posted:
            raise JournalAlreadyPostedError

        if not journal.is_balanced:
            raise JournalImbalanceError

        for posting in journal.postings:
            account = accounts.get(posting.ledger_account_id)
            if not account:
                raise ValueError(f"Account {posting.ledger_account_id} not provided for posting")

            # Option A (Banking convention)
            if posting.side is PostingType.DEBIT:
                account.balance += posting.amount
            else:
                account.balance -= posting.amount

        journal.posted = True

    def reverse(self, original_journal: JournalEntry, reference_prefix: str = "REV") -> JournalEntry:
        """
        Create a reversal journal for an existing posted journal entry.
        Does not mutate or delete the original journal, preserving immutable accounting history.
        """
        if not original_journal.posted:
            raise ValueError("Cannot reverse an unposted journal")

        new_postings = []
        for p in original_journal.postings:
            new_side = PostingType.CREDIT if p.side is PostingType.DEBIT else PostingType.DEBIT
            new_postings.append(
                replace(
                    p,
                    id=generate_prefixed_id("pst"),
                    side=new_side
                )
            )

        return JournalEntry(
            id=generate_prefixed_id("jrn"),
            reference=f"{reference_prefix}-{original_journal.reference}",
            description=f"Reversal of {original_journal.id}",
            postings=new_postings,
            posted=False,
        )
