"""Tests for the transfer domain: TransferService."""

from decimal import Decimal
import pytest

from app.common.enums import AccountStatus, AccountType, Currency
from app.common.money import Money
from app.core.exceptions import InsufficientFundsError, SameAccountTransferError
from app.domain.accounts import Account
from app.domain.ledger.enums import LedgerAccountType
from app.domain.ledger.models import LedgerAccount
from app.domain.ledger.services import LedgerService
from app.domain.transfer.enums import TransferStatus
from app.domain.transfer.service import TransferService
from app.forex.rates import EXCHANGE_RATES, add_exchange_rate


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def make_account(
    account_id: str = "acc_001",
    customer_id: str = "cst_001",
    currency: Currency = Currency.USD,
    status: AccountStatus = AccountStatus.ACTIVE,
) -> Account:
    return Account(
        id=account_id,
        customer_id=customer_id,
        currency=currency,
        account_type=AccountType.CHECKING,
        status=status,
        ledger_account_id=f"la_{account_id}",
    )


def make_ledger_account(
    for_account: Account,
    balance_minor: int = 0,
) -> LedgerAccount:
    return LedgerAccount(
        id=for_account.ledger_account_id,
        account_id=for_account.id,
        currency=for_account.currency,
        account_type=LedgerAccountType.ASSET,
        balance=Money(balance_minor, for_account.currency),
    )


def make_transfer_service() -> TransferService:
    return TransferService(ledger_service=LedgerService())


# ---------------------------------------------------------------------------
# TransferService.execute_p2p_transfer()
# ---------------------------------------------------------------------------


class TestTransferServiceP2P:
    def test_happy_path_balances_update_correctly(self) -> None:
        sender = make_account("acc_sender", "cst_001")
        receiver = make_account("acc_receiver", "cst_002")
        sender_la = make_ledger_account(sender, balance_minor=10_000)  # USD 100.00
        receiver_la = make_ledger_account(receiver, balance_minor=0)

        service = make_transfer_service()
        transfer = service.execute_p2p_transfer(
            source_account=sender,
            destination_account=receiver,
            source_ledger_account=sender_la,
            destination_ledger_account=receiver_la,
            amount=Money(3000, "USD"),  # USD 30.00
            reference="TXN0000001",
        )

        assert transfer.status is TransferStatus.COMPLETED
        assert transfer.journal_id is not None
        assert transfer.destination_journal_id is None
        assert transfer.source_account_id == sender.id
        assert transfer.destination_account_id == receiver.id
        assert transfer.amount == Money(3000, "USD")
        assert transfer.reference == "TXN0000001"
        # Sender debited (ASSET credit → decreases)
        assert sender_la.balance == Money(7000, "USD")
        # Receiver credited (ASSET debit → increases)
        assert receiver_la.balance == Money(3000, "USD")

    def test_same_account_raises(self) -> None:
        account = make_account("acc_same")
        ledger = make_ledger_account(account, balance_minor=5000)
        service = make_transfer_service()

        with pytest.raises(SameAccountTransferError):
            service.execute_p2p_transfer(
                source_account=account,
                destination_account=account,
                source_ledger_account=ledger,
                destination_ledger_account=ledger,
                amount=Money(100, "USD"),
                reference="TXN_SAME",
            )

    def test_insufficient_funds_raises(self) -> None:
        sender = make_account("acc_sender")
        receiver = make_account("acc_receiver")
        sender_la = make_ledger_account(sender, balance_minor=500)   # USD 5.00
        receiver_la = make_ledger_account(receiver, balance_minor=0)
        service = make_transfer_service()

        with pytest.raises(InsufficientFundsError):
            service.execute_p2p_transfer(
                source_account=sender,
                destination_account=receiver,
                source_ledger_account=sender_la,
                destination_ledger_account=receiver_la,
                amount=Money(1000, "USD"),  # USD 10.00 — more than balance
                reference="TXN_BROKE",
            )

    def test_currency_mismatch_source_raises(self) -> None:
        sender = make_account("acc_usd", currency=Currency.USD)
        receiver = make_account("acc_eur", currency=Currency.EUR)
        sender_la = make_ledger_account(sender, balance_minor=5000)
        receiver_la = make_ledger_account(receiver, balance_minor=0)
        service = make_transfer_service()

        # Missing FX position accounts should raise ValueError
        with pytest.raises(ValueError, match="FX position accounts must be provided"):
            service.execute_p2p_transfer(
                source_account=sender,
                destination_account=receiver,
                source_ledger_account=sender_la,
                destination_ledger_account=receiver_la,
                amount=Money(1000, "USD"),
                reference="TXN_FX",
            )

    def test_transfer_id_has_correct_prefix(self) -> None:
        sender = make_account("acc_sender")
        receiver = make_account("acc_receiver")
        sender_la = make_ledger_account(sender, balance_minor=5000)
        receiver_la = make_ledger_account(receiver, balance_minor=0)
        service = make_transfer_service()

        transfer = service.execute_p2p_transfer(
            source_account=sender,
            destination_account=receiver,
            source_ledger_account=sender_la,
            destination_ledger_account=receiver_la,
            amount=Money(1000, "USD"),
            reference="TXN_PREFIX",
        )

        assert transfer.id.startswith("trf_")

    def test_exact_balance_transfer_succeeds(self) -> None:
        """Edge case: transfer exactly the full balance."""
        sender = make_account("acc_sender")
        receiver = make_account("acc_receiver")
        sender_la = make_ledger_account(sender, balance_minor=1000)
        receiver_la = make_ledger_account(receiver, balance_minor=0)
        service = make_transfer_service()

        transfer = service.execute_p2p_transfer(
            source_account=sender,
            destination_account=receiver,
            source_ledger_account=sender_la,
            destination_ledger_account=receiver_la,
            amount=Money(1000, "USD"),
            reference="TXN_EXACT",
        )

        assert transfer.status is TransferStatus.COMPLETED
        assert sender_la.balance == Money(0, "USD")
        assert receiver_la.balance == Money(1000, "USD")

    def test_cross_currency_transfer_success(self) -> None:
        # Register exchange rate
        EXCHANGE_RATES.clear()
        add_exchange_rate("USD", "EUR", "0.90")

        sender = make_account("acc_usd", currency=Currency.USD)
        receiver = make_account("acc_eur", currency=Currency.EUR)

        sender_la = make_ledger_account(sender, balance_minor=10_000)  # USD 100.00
        receiver_la = make_ledger_account(receiver, balance_minor=0)

        source_fx = LedgerAccount("la_fx_usd", "acc_fx_usd", "USD", LedgerAccountType.ASSET, Money(0, "USD"))
        dest_fx = LedgerAccount("la_fx_eur", "acc_fx_eur", "EUR", LedgerAccountType.ASSET, Money(0, "EUR"))

        service = make_transfer_service()
        transfer = service.execute_p2p_transfer(
            source_account=sender,
            destination_account=receiver,
            source_ledger_account=sender_la,
            destination_ledger_account=receiver_la,
            amount=Money(5000, "USD"),  # USD 50.00
            reference="TXN_FX_GOOD",
            source_fx_ledger_account=source_fx,
            destination_fx_ledger_account=dest_fx,
        )

        assert transfer.status is TransferStatus.COMPLETED
        assert transfer.journal_id is not None
        assert transfer.destination_journal_id is not None
        assert transfer.exchange_rate == Decimal("0.90")

        # Sender debited 5000 USD (decreases ASSET) -> 10000 - 5000 = 5000
        assert sender_la.balance == Money(5000, "USD")
        # Source FX debited 5000 USD (increases ASSET) -> 0 + 5000 = 5000
        assert source_fx.balance == Money(5000, "USD")

        # Recipient credited 4500 EUR (50.00 USD * 0.90 = 45.00 EUR) -> 0 + 4500 = 4500
        assert receiver_la.balance == Money(4500, "EUR")
        # Destination FX credited 4500 EUR (decreases ASSET) -> 0 - 4500 = -4500
        assert dest_fx.balance == Money(-4500, "EUR")

    def test_cross_currency_transfer_unconfigured_rate_raises(self) -> None:
        EXCHANGE_RATES.clear()

        sender = make_account("acc_usd", currency=Currency.USD)
        receiver = make_account("acc_eur", currency=Currency.EUR)

        sender_la = make_ledger_account(sender, balance_minor=5000)
        receiver_la = make_ledger_account(receiver, balance_minor=0)

        source_fx = LedgerAccount("la_fx_usd", "acc_fx_usd", "USD", LedgerAccountType.ASSET, Money(0, "USD"))
        dest_fx = LedgerAccount("la_fx_eur", "acc_fx_eur", "EUR", LedgerAccountType.ASSET, Money(0, "EUR"))

        service = make_transfer_service()

        with pytest.raises(ValueError, match="No exchange rate configured"):
            service.execute_p2p_transfer(
                source_account=sender,
                destination_account=receiver,
                source_ledger_account=sender_la,
                destination_ledger_account=receiver_la,
                amount=Money(1000, "USD"),
                reference="TXN_FX_NORATE",
                source_fx_ledger_account=source_fx,
                destination_fx_ledger_account=dest_fx,
            )
