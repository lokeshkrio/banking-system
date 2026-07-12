from dataclasses import dataclass, field

from app.common.money import Money
from app.domain.ledger.enums import LedgerAccountType, PostingType
from app.domain.ledger.exceptions import CurrencyMismatchError


@dataclass(slots=True)
class LedgerAccount:
    id: str
    account_id: str
    currency: str
    account_type: LedgerAccountType
    balance: Money


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
    Use ``dataclasses.replace(journal, posted=True)`` to produce a posted copy.
    """

    id: str
    reference: str
    description: str
    postings: list[Posting]
    posted: bool = field(default=False)

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
