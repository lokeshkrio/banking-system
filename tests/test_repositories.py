import pytest

from app.common.enums import AccountStatus, AccountType, Currency, UserStatus
from app.domain.accounts import Account
from app.domain.customer.models import Customer
from app.domain.ledger.models import JournalEntry
from app.domain.repository import AccountRepository, CustomerRepository, JournalRepository


# ---------------------------------------------------------------------------
# In-Memory Implementation Mocks conforming to Protocols
# ---------------------------------------------------------------------------


class InMemoryCustomerRepository:
    def __init__(self) -> None:
        self._store: dict[str, Customer] = {}

    def get_by_id(self, customer_id: str) -> Customer | None:
        return self._store.get(customer_id)

    def save(self, customer: Customer) -> None:
        self._store[customer.id] = customer


class InMemoryAccountRepository:
    def __init__(self) -> None:
        self._store: dict[str, Account] = {}

    def get_by_id(self, account_id: str) -> Account | None:
        return self._store.get(account_id)

    def get_by_ledger_id(self, ledger_account_id: str) -> Account | None:
        for acc in self._store.values():
            if acc.ledger_account_id == ledger_account_id:
                return acc
        return None

    def save(self, account: Account) -> None:
        self._store[account.id] = account


class InMemoryJournalRepository:
    def __init__(self) -> None:
        self._store: dict[str, JournalEntry] = {}

    def get_by_id(self, journal_id: str) -> JournalEntry | None:
        return self._store.get(journal_id)

    def save(self, journal: JournalEntry) -> None:
        self._store[journal.id] = journal


# ---------------------------------------------------------------------------
# Protocol Verification Tests
# ---------------------------------------------------------------------------


def test_customer_repository_protocol() -> None:
    repo: CustomerRepository = InMemoryCustomerRepository()
    customer = Customer(id="cst_1", name="Alice", status=UserStatus.ACTIVE)

    repo.save(customer)
    retrieved = repo.get_by_id("cst_1")

    assert retrieved == customer
    assert repo.get_by_id("cst_nonexistent") is None


def test_account_repository_protocol() -> None:
    repo: AccountRepository = InMemoryAccountRepository()
    account = Account(
        id="acc_1",
        customer_id="cst_1",
        currency=Currency.USD,
        account_type=AccountType.CHECKING,
        status=AccountStatus.ACTIVE,
        ledger_account_id="la_acc_1",
    )

    repo.save(account)
    assert repo.get_by_id("acc_1") == account
    assert repo.get_by_ledger_id("la_acc_1") == account
    assert repo.get_by_id("acc_nonexistent") is None


def test_journal_repository_protocol() -> None:
    repo: JournalRepository = InMemoryJournalRepository()
    journal = JournalEntry(
        id="jrn_1",
        reference="REF1",
        description="Initial deposit",
        postings=[],
    )

    repo.save(journal)
    assert repo.get_by_id("jrn_1") == journal
    assert repo.get_by_id("jrn_nonexistent") is None
