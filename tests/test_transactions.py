import pytest

from app.common.enums import AccountStatus, AccountType, Currency
from app.common.money import Money
from app.core.exceptions import InsufficientFundsError
from app.domain.accounts import Account
from app.domain.ledger.enums import LedgerAccountType
from app.domain.ledger.models import LedgerAccount
from app.domain.ledger.services import LedgerService
from app.domain.transaction.enums import TransactionStatus, TransactionType
from app.domain.transaction.service import TransactionService


def make_account(
    account_id: str = "acc_001",
    currency: Currency = Currency.USD,
) -> Account:
    return Account(
        id=account_id,
        customer_id="cst_001",
        currency=currency,
        account_type=AccountType.CHECKING,
        status=AccountStatus.ACTIVE,
        ledger_account_id=f"la_{account_id}",
    )


def make_ledger_account(
    for_account: Account,
    balance_minor: int = 0,
    account_type: LedgerAccountType = LedgerAccountType.ASSET,
) -> LedgerAccount:
    return LedgerAccount(
        id=for_account.ledger_account_id,
        account_id=for_account.id,
        currency=for_account.currency,
        account_type=account_type,
        balance=Money(balance_minor, for_account.currency),
    )


def test_execute_deposit_success() -> None:
    customer_account = make_account("acc_cust", Currency.USD)
    customer_ledger = make_ledger_account(customer_account, balance_minor=1000)  # $10.00
    funding_ledger = LedgerAccount(
        id="la_funding",
        account_id="acc_funding",
        currency="USD",
        account_type=LedgerAccountType.ASSET,
        balance=Money(5000, "USD"),  # $50.00
    )

    service = TransactionService(ledger_service=LedgerService())
    deposit_amount = Money(2000, "USD")  # $20.00

    txn = service.execute_deposit(
        account=customer_account,
        ledger_account=customer_ledger,
        funding_ledger_account=funding_ledger,
        amount=deposit_amount,
        reference="DEP001",
    )

    assert txn.status == TransactionStatus.COMPLETED
    assert txn.type == TransactionType.DEPOSIT
    assert txn.amount == deposit_amount
    assert txn.journal_id is not None
    assert txn.id.startswith("txn_")

    # Customer ledger account debited (ASSET debit increases balance): 1000 + 2000 = 3000
    assert customer_ledger.balance == Money(3000, "USD")
    # Funding ledger account credited (ASSET credit decreases balance): 5000 - 2000 = 3000
    assert funding_ledger.balance == Money(3000, "USD")


def test_execute_deposit_currency_mismatch() -> None:
    customer_account = make_account("acc_cust", Currency.USD)
    customer_ledger = make_ledger_account(customer_account, balance_minor=1000)
    funding_ledger = LedgerAccount(
        id="la_funding",
        account_id="acc_funding",
        currency="USD",
        account_type=LedgerAccountType.ASSET,
        balance=Money(5000, "USD"),
    )

    service = TransactionService(ledger_service=LedgerService())

    # Deposit EUR into USD account
    with pytest.raises(ValueError, match="currency"):
        service.execute_deposit(
            account=customer_account,
            ledger_account=customer_ledger,
            funding_ledger_account=funding_ledger,
            amount=Money(1000, "EUR"),
            reference="DEP_BAD",
        )


def test_execute_withdrawal_success() -> None:
    customer_account = make_account("acc_cust", Currency.USD)
    customer_ledger = make_ledger_account(customer_account, balance_minor=5000)  # $50.00
    clearing_ledger = LedgerAccount(
        id="la_clearing",
        account_id="acc_clearing",
        currency="USD",
        account_type=LedgerAccountType.ASSET,
        balance=Money(1000, "USD"),  # $10.00
    )

    service = TransactionService(ledger_service=LedgerService())
    withdrawal_amount = Money(2000, "USD")  # $20.00

    txn = service.execute_withdrawal(
        account=customer_account,
        ledger_account=customer_ledger,
        clearing_ledger_account=clearing_ledger,
        amount=withdrawal_amount,
        reference="WTH001",
    )

    assert txn.status == TransactionStatus.COMPLETED
    assert txn.type == TransactionType.WITHDRAWAL
    assert txn.amount == withdrawal_amount
    assert txn.journal_id is not None

    # Customer ledger account credited (ASSET credit decreases balance): 5000 - 2000 = 3000
    assert customer_ledger.balance == Money(3000, "USD")
    # Clearing ledger account debited (ASSET debit increases balance): 1000 + 2000 = 3000
    assert clearing_ledger.balance == Money(3000, "USD")


def test_execute_withdrawal_insufficient_funds() -> None:
    customer_account = make_account("acc_cust", Currency.USD)
    customer_ledger = make_ledger_account(customer_account, balance_minor=1000)  # $10.00
    clearing_ledger = LedgerAccount(
        id="la_clearing",
        account_id="acc_clearing",
        currency="USD",
        account_type=LedgerAccountType.ASSET,
        balance=Money(1000, "USD"),
    )

    service = TransactionService(ledger_service=LedgerService())

    # Try to withdraw $20.00 when balance is $10.00
    with pytest.raises(InsufficientFundsError):
        service.execute_withdrawal(
            account=customer_account,
            ledger_account=customer_ledger,
            clearing_ledger_account=clearing_ledger,
            amount=Money(2000, "USD"),
            reference="WTH_BROKE",
        )
