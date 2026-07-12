"""Transfer service — orchestrates the full transfer flow.

Flow:
    Account (source + destination)
        ↓  validate currencies, status, balance
    JournalEntry  (balanced Postings)
        ↓  LedgerService.post()
    LedgerAccount balances updated
        ↓
    Transfer (COMPLETED, journal_id linked)
"""

from app.common.enums import AccountStatus
from app.common.ids import generate_prefixed_id
from app.common.money import Money
from app.core.constants import InternalIDPrefix
from app.core.exceptions import (
    AccountNotActiveError,
    InsufficientFundsError,
    SameAccountTransferError,
)
from app.domain.accounts import Account
from app.domain.ledger.enums import PostingType
from app.domain.ledger.models import JournalEntry, LedgerAccount, Posting
from app.domain.ledger.services import LedgerService
from app.domain.transfer.enums import TransferStatus
from app.domain.transfer.models import Transfer
from app.forex.rates import get_exchange_rate


class TransferService:
    def __init__(self, ledger_service: LedgerService) -> None:
        self.ledger_service = ledger_service

    def execute_p2p_transfer(
        self,
        source_account: Account,
        destination_account: Account,
        source_ledger_account: LedgerAccount,
        destination_ledger_account: LedgerAccount,
        amount: Money,
        reference: str,
        description: str = "P2P Transfer",
        source_fx_ledger_account: LedgerAccount | None = None,
        destination_fx_ledger_account: LedgerAccount | None = None,
    ) -> Transfer:
        """Execute a peer-to-peer transfer between two accounts.

        Supports both same-currency and cross-currency transfers.
        For cross-currency transfers, posts two separate balanced journals using the provided
        FX position accounts.

        Args:
            source_account:                 The customer account debiting funds.
            destination_account:            The customer account receiving funds.
            source_ledger_account:          Backing ``LedgerAccount`` for the source.
            destination_ledger_account:     Backing ``LedgerAccount`` for the destination.
            amount:                         Amount to transfer (must match source account currency).
            reference:                      External-facing reference string.
            description:                    Human-readable transfer description.
            source_fx_ledger_account:       Backing ``LedgerAccount`` representing the FX clearing/position
                                            account in the source currency (required for cross-currency).
            destination_fx_ledger_account:  Backing ``LedgerAccount`` representing the FX clearing/position
                                            account in the destination currency (required for cross-currency).

        Returns:
            A ``Transfer`` in ``COMPLETED`` status with ``journal_id`` set.

        Raises:
            SameAccountTransferError:   If source and destination are the same account.
            ValueError:                 If amount currency doesn't match source account currency,
                                        or if FX position accounts are missing for cross-currency transfers.
            InsufficientFundsError:     If source ledger account has insufficient balance.
        """
        # --- Guards ---
        if source_account.id == destination_account.id:
            raise SameAccountTransferError()

        if source_account.status != AccountStatus.ACTIVE:
            raise AccountNotActiveError(
                f"Source account '{source_account.id}' is {source_account.status}."
            )

        if destination_account.status != AccountStatus.ACTIVE:
            raise AccountNotActiveError(
                f"Destination account '{destination_account.id}' is {destination_account.status}."
            )

        if source_account.currency != amount.currency_code:
            raise ValueError(
                f"Source account currency ({source_account.currency}) "
                f"does not match transfer amount currency ({amount.currency_code})."
            )

        if source_ledger_account.balance < amount:
            raise InsufficientFundsError()

        transfer_id = generate_prefixed_id(InternalIDPrefix.TRANSFER)

        # --- Same-Currency Transfer ---
        if source_account.currency == destination_account.currency:
            if destination_account.currency != amount.currency_code:
                raise ValueError(
                    f"Destination account currency ({destination_account.currency}) "
                    f"does not match transfer amount currency ({amount.currency_code})."
                )

            # Build the double-entry journal
            journal = JournalEntry(
                id=generate_prefixed_id(InternalIDPrefix.JOURNAL),
                reference=reference,
                description=description,
                postings=[
                    Posting(
                        id=generate_prefixed_id(InternalIDPrefix.POSTING),
                        ledger_account_id=source_ledger_account.id,
                        side=PostingType.CREDIT,  # Credit decreases sender's ASSET account
                        amount=amount,
                    ),
                    Posting(
                        id=generate_prefixed_id(InternalIDPrefix.POSTING),
                        ledger_account_id=destination_ledger_account.id,
                        side=PostingType.DEBIT,  # Debit increases receiver's ASSET account
                        amount=amount,
                    ),
                ],
            )

            # Post the journal
            accounts = {
                source_ledger_account.id: source_ledger_account,
                destination_ledger_account.id: destination_ledger_account,
            }
            posted_journal = self.ledger_service.post(journal, accounts)

            return Transfer(
                id=transfer_id,
                source_account_id=source_account.id,
                destination_account_id=destination_account.id,
                amount=amount,
                status=TransferStatus.COMPLETED,
                reference=reference,
                description=description,
                journal_id=posted_journal.id,
            )

        # --- Cross-Currency Transfer ---
        else:
            if source_fx_ledger_account is None or destination_fx_ledger_account is None:
                raise ValueError("FX position accounts must be provided for cross-currency transfers.")

            if source_fx_ledger_account.currency != source_account.currency:
                raise ValueError(
                    f"Source FX ledger account currency ({source_fx_ledger_account.currency}) "
                    f"must match source account currency ({source_account.currency})."
                )

            if destination_fx_ledger_account.currency != destination_account.currency:
                raise ValueError(
                    f"Destination FX ledger account currency ({destination_fx_ledger_account.currency}) "
                    f"must match destination account currency ({destination_account.currency})."
                )

            # Get exchange rate & convert amount
            rate = get_exchange_rate(source_account.currency, destination_account.currency)
            converted_amount = amount.convert(destination_account.currency, rate=rate)

            # 1. Source Journal (in source currency)
            source_journal = JournalEntry(
                id=generate_prefixed_id(InternalIDPrefix.JOURNAL),
                reference=f"{reference}-SRC",
                description=f"{description} (FX Source: {source_account.currency} -> {destination_account.currency})",
                postings=[
                    Posting(
                        id=generate_prefixed_id(InternalIDPrefix.POSTING),
                        ledger_account_id=source_ledger_account.id,
                        side=PostingType.CREDIT,  # Credit decreases sender's account
                        amount=amount,
                    ),
                    Posting(
                        id=generate_prefixed_id(InternalIDPrefix.POSTING),
                        ledger_account_id=source_fx_ledger_account.id,
                        side=PostingType.DEBIT,   # Debit increases source FX clearing account
                        amount=amount,
                    ),
                ],
            )

            # 2. Destination Journal (in destination currency)
            dest_journal = JournalEntry(
                id=generate_prefixed_id(InternalIDPrefix.JOURNAL),
                reference=f"{reference}-DST",
                description=f"{description} (FX Dest: {source_account.currency} -> {destination_account.currency})",
                postings=[
                    Posting(
                        id=generate_prefixed_id(InternalIDPrefix.POSTING),
                        ledger_account_id=destination_fx_ledger_account.id,
                        side=PostingType.CREDIT,  # Credit decreases destination FX clearing account
                        amount=converted_amount,
                    ),
                    Posting(
                        id=generate_prefixed_id(InternalIDPrefix.POSTING),
                        ledger_account_id=destination_ledger_account.id,
                        side=PostingType.DEBIT,   # Debit increases receiver's account
                        amount=converted_amount,
                    ),
                ],
            )

            # Post Source Journal
            source_accounts = {
                source_ledger_account.id: source_ledger_account,
                source_fx_ledger_account.id: source_fx_ledger_account,
            }
            posted_source_journal = self.ledger_service.post(source_journal, source_accounts)

            # Post Destination Journal
            dest_accounts = {
                destination_ledger_account.id: destination_ledger_account,
                destination_fx_ledger_account.id: destination_fx_ledger_account,
            }
            posted_dest_journal = self.ledger_service.post(dest_journal, dest_accounts)

            return Transfer(
                id=transfer_id,
                source_account_id=source_account.id,
                destination_account_id=destination_account.id,
                amount=amount,
                status=TransferStatus.COMPLETED,
                reference=reference,
                description=description,
                journal_id=posted_source_journal.id,
                destination_journal_id=posted_dest_journal.id,
                exchange_rate=rate,
            )
