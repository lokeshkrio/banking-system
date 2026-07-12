from dataclasses import dataclass, field

from app.common.money import Money
from app.domain.ledger.enums import JournalStatus, LedgerAccountType, PostingType
from app.domain.ledger.exceptions import CurrencyMismatchError


# Account types whose normal balance is a DEBIT (i.e. debits increase, credits decrease).
_DEBIT_NORMAL = {LedgerAccountType.ASSET, LedgerAccountType.EXPENSE}


@dataclass(slots=True)
class LedgerAccount:
    """Mutable ledger account with controlled balance access.

    Balance mutations are only permitted through :meth:`apply_debit` and
    :meth:`apply_credit`, which encode standard double-entry normal-balance rules.
    Direct assignment to ``balance`` is discouraged.
    """

    id: str
    account_id: str
    currency: str
    account_type: LedgerAccountType
    _balance: Money = field(repr=False)

    def __init__(
        self,
        id: str,
        account_id: str,
        currency: str,
        account_type: LedgerAccountType,
        balance: Money,
    ) -> None:
        self.id = id
        self.account_id = account_id
        self.currency = currency
        self.account_type = account_type
        self._balance = balance

    @property
    def balance(self) -> Money:
        return self._balance

    def apply_debit(self, amount: Money) -> None:
        """Apply a debit posting to this account.

        - ASSET / EXPENSE → balance **increases**.
        - LIABILITY / EQUITY / REVENUE → balance **decreases**.
        """
        if self.account_type in _DEBIT_NORMAL:
            self._balance = self._balance + amount
        else:
            self._balance = self._balance - amount

    def apply_credit(self, amount: Money) -> None:
        """Apply a credit posting to this account.

        - ASSET / EXPENSE → balance **decreases**.
        - LIABILITY / EQUITY / REVENUE → balance **increases**.
        """
        if self.account_type in _DEBIT_NORMAL:
            self._balance = self._balance - amount
        else:
            self._balance = self._balance + amount


@dataclass(slots=True)
class Posting:
    id: str
    ledger_account_id: str
    side: PostingType
    amount: Money


@dataclass(frozen=True, slots=True)
class JournalEntry:
    """Immutable accounting record.

    Once constructed, a JournalEntry must not be mutated.
    Use ``dataclasses.replace(journal, status=JournalStatus.POSTED)`` to produce a posted copy.
    """

    id: str
    reference: str
    description: str
    postings: list[Posting]
    status: JournalStatus = field(default=JournalStatus.DRAFT)

    @property
    def is_posted(self) -> bool:
        """Convenience check: True if this journal has been posted."""
        return self.status is JournalStatus.POSTED

    @property
    def is_balanced(self) -> bool:
        if not self.postings:
            return True

        currencies = {p.amount.currency_code for p in self.postings}
        if len(currencies) > 1:
            raise CurrencyMismatchError()

        currency = next(iter(currencies))
        debit = Money.zero(currency)
        credit = Money.zero(currency)

        for p in self.postings:
            if p.side is PostingType.DEBIT:
                debit += p.amount
            else:
                credit += p.amount

        return debit == credit
