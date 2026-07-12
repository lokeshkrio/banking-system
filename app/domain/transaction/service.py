from app.common.ids import generate_prefixed_id
from app.common.money import Money
from app.core.constants import InternalIDPrefix
from app.core.exceptions import InsufficientFundsError
from app.domain.accounts import Account
from app.domain.ledger.enums import PostingType
from app.domain.ledger.models import JournalEntry, LedgerAccount, Posting
from app.domain.ledger.services import LedgerService
from app.domain.transaction.enums import TransactionStatus, TransactionType
from app.domain.transaction.models import Transaction


class TransactionService:
    """Service to orchestrate Deposit and Withdrawal operations using balanced ledger postings."""

    def __init__(self, ledger_service: LedgerService) -> None:
        self.ledger_service = ledger_service

    def execute_deposit(
        self,
        account: Account,
        ledger_account: LedgerAccount,
        funding_ledger_account: LedgerAccount,
        amount: Money,
        reference: str,
        description: str = "Deposit",
    ) -> Transaction:
        """Execute a deposit transaction.

        Credits the funding source account and debits the customer account.
        """
        if account.currency != amount.currency_code:
            raise ValueError(
                f"Account currency ({account.currency}) "
                f"does not match deposit amount currency ({amount.currency_code})."
            )
        if funding_ledger_account.currency != amount.currency_code:
            raise ValueError(
                f"Funding account currency ({funding_ledger_account.currency}) "
                f"does not match deposit amount currency ({amount.currency_code})."
            )

        # Debit customer account (increases asset), Credit funding account (balances journal)
        journal = JournalEntry(
            id=generate_prefixed_id(InternalIDPrefix.JOURNAL),
            reference=reference,
            description=description,
            postings=[
                Posting(
                    id=generate_prefixed_id(InternalIDPrefix.POSTING),
                    ledger_account_id=funding_ledger_account.id,
                    side=PostingType.CREDIT,
                    amount=amount,
                ),
                Posting(
                    id=generate_prefixed_id(InternalIDPrefix.POSTING),
                    ledger_account_id=ledger_account.id,
                    side=PostingType.DEBIT,
                    amount=amount,
                ),
            ],
            posted=False,
        )

        accounts = {
            ledger_account.id: ledger_account,
            funding_ledger_account.id: funding_ledger_account,
        }
        posted_journal = self.ledger_service.post(journal, accounts)

        txn_id = generate_prefixed_id(InternalIDPrefix.TRANSACTION)
        return Transaction(
            id=txn_id,
            account_id=account.id,
            amount=amount,
            type=TransactionType.DEPOSIT,
            status=TransactionStatus.COMPLETED,
            reference=reference,
            description=description,
            journal_id=posted_journal.id,
        )

    def execute_withdrawal(
        self,
        account: Account,
        ledger_account: LedgerAccount,
        clearing_ledger_account: LedgerAccount,
        amount: Money,
        reference: str,
        description: str = "Withdrawal",
    ) -> Transaction:
        """Execute a withdrawal transaction.

        Credits the customer account and debits the clearing account.
        Raises InsufficientFundsError if customer account has insufficient balance.
        """
        if account.currency != amount.currency_code:
            raise ValueError(
                f"Account currency ({account.currency}) "
                f"does not match withdrawal amount currency ({amount.currency_code})."
            )
        if clearing_ledger_account.currency != amount.currency_code:
            raise ValueError(
                f"Clearing account currency ({clearing_ledger_account.currency}) "
                f"does not match withdrawal amount currency ({amount.currency_code})."
            )

        if ledger_account.balance < amount:
            raise InsufficientFundsError()

        # Credit customer account (decreases asset), Debit clearing account (balances journal)
        journal = JournalEntry(
            id=generate_prefixed_id(InternalIDPrefix.JOURNAL),
            reference=reference,
            description=description,
            postings=[
                Posting(
                    id=generate_prefixed_id(InternalIDPrefix.POSTING),
                    ledger_account_id=ledger_account.id,
                    side=PostingType.CREDIT,
                    amount=amount,
                ),
                Posting(
                    id=generate_prefixed_id(InternalIDPrefix.POSTING),
                    ledger_account_id=clearing_ledger_account.id,
                    side=PostingType.DEBIT,
                    amount=amount,
                ),
            ],
            posted=False,
        )

        accounts = {
            ledger_account.id: ledger_account,
            clearing_ledger_account.id: clearing_ledger_account,
        }
        posted_journal = self.ledger_service.post(journal, accounts)

        txn_id = generate_prefixed_id(InternalIDPrefix.TRANSACTION)
        return Transaction(
            id=txn_id,
            account_id=account.id,
            amount=amount,
            type=TransactionType.WITHDRAWAL,
            status=TransactionStatus.COMPLETED,
            reference=reference,
            description=description,
            journal_id=posted_journal.id,
        )
