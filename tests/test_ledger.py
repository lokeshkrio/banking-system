"""Tests for the ledger domain: JournalEntry, LedgerAccount, LedgerService."""

import pytest

from app.common.money import Money
from app.domain.ledger.enums import JournalStatus, LedgerAccountType, PostingType
from app.domain.ledger.exceptions import (
    CurrencyMismatchError,
    JournalAlreadyPostedError,
    JournalImbalanceError,
)
from app.domain.ledger.models import JournalEntry, LedgerAccount, Posting
from app.domain.ledger.services import LedgerService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def make_ledger_account(
    account_id: str = "acc_001",
    currency: str = "USD",
    balance_minor: int = 0,
    account_type: LedgerAccountType = LedgerAccountType.ASSET,
) -> LedgerAccount:
    return LedgerAccount(
        id=f"la_{account_id}",
        account_id=account_id,
        currency=currency,
        account_type=account_type,
        balance=Money(balance_minor, currency),
    )


def make_posting(
    ledger_account_id: str,
    side: PostingType,
    amount_minor: int,
    currency: str = "USD",
) -> Posting:
    return Posting(
        id=f"pst_{ledger_account_id}_{side}",
        ledger_account_id=ledger_account_id,
        side=side,
        amount=Money(amount_minor, currency),
    )


def make_balanced_journal(
    debit_account_id: str,
    credit_account_id: str,
    amount_minor: int,
    currency: str = "USD",
) -> JournalEntry:
    return JournalEntry(
        id="jrn_test",
        reference="TXN001",
        description="Test journal",
        postings=[
            make_posting(debit_account_id, PostingType.DEBIT, amount_minor, currency),
            make_posting(credit_account_id, PostingType.CREDIT, amount_minor, currency),
        ],
    )


# ---------------------------------------------------------------------------
# JournalEntry.is_balanced
# ---------------------------------------------------------------------------


class TestJournalIsBalanced:
    def test_balanced_journal_returns_true(self) -> None:
        journal = make_balanced_journal("la_a", "la_b", 1000)
        assert journal.is_balanced is True

    def test_unbalanced_journal_returns_false(self) -> None:
        journal = JournalEntry(
            id="jrn_unbalanced",
            reference="REF001",
            description="Unbalanced",
            postings=[
                make_posting("la_a", PostingType.DEBIT, 1000),
                make_posting("la_b", PostingType.CREDIT, 500),  # doesn't balance
            ],
        )
        assert journal.is_balanced is False

    def test_empty_postings_returns_true(self) -> None:
        journal = JournalEntry(
            id="jrn_empty",
            reference="REF002",
            description="Empty",
            postings=[],
        )
        assert journal.is_balanced is True

    def test_multi_currency_raises_currency_mismatch(self) -> None:
        journal = JournalEntry(
            id="jrn_multi",
            reference="REF003",
            description="Multi-currency",
            postings=[
                make_posting("la_a", PostingType.DEBIT, 1000, "USD"),
                make_posting("la_b", PostingType.CREDIT, 1000, "EUR"),
            ],
        )
        with pytest.raises(CurrencyMismatchError):
            _ = journal.is_balanced

    def test_journal_entry_is_frozen(self) -> None:
        journal = make_balanced_journal("la_a", "la_b", 500)
        with pytest.raises((AttributeError, TypeError)):
            journal.status = JournalStatus.POSTED  # type: ignore[misc]

    def test_journal_defaults_to_draft(self) -> None:
        journal = make_balanced_journal("la_a", "la_b", 500)
        assert journal.status is JournalStatus.DRAFT
        assert journal.is_posted is False


# ---------------------------------------------------------------------------
# LedgerService.post()
# ---------------------------------------------------------------------------


class TestLedgerServicePost:
    def setup_method(self) -> None:
        self.service = LedgerService()

    def test_post_returns_posted_journal(self) -> None:
        sender = make_ledger_account("acc_sender", balance_minor=5000)
        receiver = make_ledger_account("acc_receiver", balance_minor=0)

        journal = make_balanced_journal(receiver.id, sender.id, 1000)
        posted = self.service.post(journal, {sender.id: sender, receiver.id: receiver})

        assert posted.status is JournalStatus.POSTED
        assert posted.is_posted is True

    def test_post_original_journal_unchanged(self) -> None:
        """post() must not mutate the original JournalEntry."""
        sender = make_ledger_account("acc_sender", balance_minor=5000)
        receiver = make_ledger_account("acc_receiver", balance_minor=0)
        journal = make_balanced_journal(receiver.id, sender.id, 1000)

        self.service.post(journal, {sender.id: sender, receiver.id: receiver})
        assert journal.status is JournalStatus.DRAFT  # original is untouched

    def test_post_raises_if_already_posted(self) -> None:
        sender = make_ledger_account("acc_sender", balance_minor=5000)
        receiver = make_ledger_account("acc_receiver", balance_minor=0)
        journal = make_balanced_journal(receiver.id, sender.id, 1000)

        posted = self.service.post(journal, {sender.id: sender, receiver.id: receiver})

        with pytest.raises(JournalAlreadyPostedError):
            self.service.post(posted, {sender.id: sender, receiver.id: receiver})

    def test_post_raises_on_imbalanced_journal(self) -> None:
        account = make_ledger_account("acc_001", balance_minor=5000)
        unbalanced = JournalEntry(
            id="jrn_unbalanced",
            reference="BAD001",
            description="Bad journal",
            postings=[
                make_posting(account.id, PostingType.DEBIT, 1000),
                make_posting(account.id, PostingType.CREDIT, 500),
            ],
        )
        with pytest.raises(JournalImbalanceError):
            self.service.post(unbalanced, {account.id: account})

    def test_post_raises_on_missing_account(self) -> None:
        journal = make_balanced_journal("la_missing_1", "la_missing_2", 500)
        with pytest.raises(ValueError, match="not provided"):
            self.service.post(journal, {})

    def test_post_asset_account_normal_balance(self) -> None:
        """ASSET: Debit increases, Credit decreases."""
        receiver = make_ledger_account("acc_recv", balance_minor=0, account_type=LedgerAccountType.ASSET)
        sender = make_ledger_account("acc_send", balance_minor=5000, account_type=LedgerAccountType.ASSET)

        journal = make_balanced_journal(receiver.id, sender.id, 1000)
        self.service.post(journal, {receiver.id: receiver, sender.id: sender})

        assert receiver.balance == Money(1000, "USD")  # Debit increased
        assert sender.balance == Money(4000, "USD")    # Credit decreased

    def test_post_liability_account_normal_balance(self) -> None:
        """LIABILITY: Credit increases, Debit decreases."""
        liability_acct = make_ledger_account(
            "acc_liability", balance_minor=2000, account_type=LedgerAccountType.LIABILITY
        )
        asset_acct = make_ledger_account(
            "acc_asset", balance_minor=5000, account_type=LedgerAccountType.ASSET
        )
        # Debit asset (increases it), Credit liability (increases it)
        journal = make_balanced_journal(asset_acct.id, liability_acct.id, 500)
        self.service.post(journal, {asset_acct.id: asset_acct, liability_acct.id: liability_acct})

        assert asset_acct.balance == Money(5500, "USD")    # ASSET debited → increases
        assert liability_acct.balance == Money(2500, "USD") # LIABILITY credited → increases

    def test_post_revenue_account_normal_balance(self) -> None:
        """REVENUE: Credit increases, Debit decreases."""
        revenue_acct = make_ledger_account(
            "acc_revenue", balance_minor=0, account_type=LedgerAccountType.REVENUE
        )
        asset_acct = make_ledger_account(
            "acc_asset", balance_minor=1000, account_type=LedgerAccountType.ASSET
        )
        # Debit asset, credit revenue → both increase
        journal = make_balanced_journal(asset_acct.id, revenue_acct.id, 300)
        self.service.post(journal, {asset_acct.id: asset_acct, revenue_acct.id: revenue_acct})

        assert asset_acct.balance == Money(1300, "USD")  # ASSET debited → increases
        assert revenue_acct.balance == Money(300, "USD") # REVENUE credited → increases


# ---------------------------------------------------------------------------
# LedgerService.reverse()
# ---------------------------------------------------------------------------


class TestLedgerServiceReverse:
    def setup_method(self) -> None:
        self.service = LedgerService()

    def test_reverse_creates_inverted_unposted_journal(self) -> None:
        sender = make_ledger_account("acc_sender", balance_minor=5000)
        receiver = make_ledger_account("acc_receiver", balance_minor=0)
        journal = make_balanced_journal(receiver.id, sender.id, 1000)
        posted = self.service.post(journal, {sender.id: sender, receiver.id: receiver})

        reversal = self.service.reverse(posted)

        assert reversal.status is JournalStatus.DRAFT
        assert reversal.is_posted is False
        assert reversal.id != posted.id
        assert "REV" in reversal.reference
        assert len(reversal.postings) == len(posted.postings)

        # Sides must be flipped
        original_sides = {p.ledger_account_id: p.side for p in posted.postings}
        for rp in reversal.postings:
            original_side = original_sides[rp.ledger_account_id]
            expected = PostingType.CREDIT if original_side is PostingType.DEBIT else PostingType.DEBIT
            assert rp.side == expected

    def test_reverse_raises_on_unposted_journal(self) -> None:
        journal = make_balanced_journal("la_a", "la_b", 500)
        with pytest.raises(ValueError, match="not POSTED"):
            self.service.reverse(journal)

    def test_reverse_with_custom_prefix(self) -> None:
        sender = make_ledger_account("acc_sender", balance_minor=5000)
        receiver = make_ledger_account("acc_receiver", balance_minor=0)
        journal = make_balanced_journal(receiver.id, sender.id, 200)
        posted = self.service.post(journal, {sender.id: sender, receiver.id: receiver})

        reversal = self.service.reverse(posted, reference_prefix="ADJ")
        assert reversal.reference.startswith("ADJ-")
