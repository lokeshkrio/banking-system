"""Domain model for a customer-facing bank account.

Each ``Account`` maps 1-to-1 to a ``LedgerAccount`` in the ledger subsystem.
The ``Account`` is the *business* concept (owned by a customer, has a currency,
has a lifecycle status); the ``LedgerAccount`` is the *accounting* concept
(tracks the running balance via posted journal entries).
"""

from dataclasses import dataclass

from app.common.enums import AccountStatus, AccountType, Currency


@dataclass(frozen=True, slots=True)
class Account:
    """Customer-facing account.

    Attributes:
        id:                Internal account ID (``acc_<uuid>``).
        customer_id:       Internal customer ID (``cst_<uuid>``) of the owner.
        currency:          ISO 4217 currency code of the account.
        account_type:      Product type (SAVING, CHECKING, CREDIT).
        status:            Current lifecycle state.
        ledger_account_id: ID of the corresponding ``LedgerAccount`` in the
                           ledger subsystem. Used to look up the running balance.
    """

    id: str
    customer_id: str
    currency: Currency
    account_type: AccountType
    status: AccountStatus
    ledger_account_id: str
