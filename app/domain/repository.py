from typing import Protocol

from app.domain.accounts import Account
from app.domain.customer.models import Customer
from app.domain.ledger.models import JournalEntry


class CustomerRepository(Protocol):
    """Protocol defining persistence operations for Customer records."""

    def get_by_id(self, customer_id: str) -> Customer | None:
        """Retrieve a customer by their unique identifier."""
        ...

    def save(self, customer: Customer) -> None:
        """Persist or update a customer record."""
        ...


class AccountRepository(Protocol):
    """Protocol defining persistence operations for Account records."""

    def get_by_id(self, account_id: str) -> Account | None:
        """Retrieve an account by its unique identifier."""
        ...

    def get_by_ledger_id(self, ledger_account_id: str) -> Account | None:
        """Retrieve an account linked to a specific ledger account ID."""
        ...

    def save(self, account: Account) -> None:
        """Persist or update an account record."""
        ...


class JournalRepository(Protocol):
    """Protocol defining persistence operations for Journal entries."""

    def get_by_id(self, journal_id: str) -> JournalEntry | None:
        """Retrieve a journal entry by its unique identifier."""
        ...

    def save(self, journal: JournalEntry) -> None:
        """Persist a journal entry."""
        ...
