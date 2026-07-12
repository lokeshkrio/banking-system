from app.common.ids import generate_prefixed_id
from app.common.money import Money
from app.domain.ledger.enums import PostingType
from app.domain.ledger.models import JournalEntry, LedgerAccount, Posting
from app.domain.ledger.services import LedgerService


class TransferService:
    def __init__(self, ledger_service: LedgerService):
        self.ledger_service = ledger_service

    def execute_p2p_transfer(
        self,
        sender_account: LedgerAccount,
        receiver_account: LedgerAccount,
        amount: Money,
        reference: str,
        description: str = "P2P Transfer",
    ) -> JournalEntry:
        """
        Executes a peer-to-peer transfer by generating a balanced journal and posting it.
        """
        if sender_account.currency != amount.currency_code:
            raise ValueError("Sender account currency must match transfer amount currency")

        if receiver_account.currency != amount.currency_code:
            raise ValueError("Receiver account currency must match transfer amount currency")

        journal = JournalEntry(
            id=generate_prefixed_id("jrn"),
            reference=reference,
            description=description,
            postings=[
                Posting(
                    id=generate_prefixed_id("pst"),
                    ledger_account_id=sender_account.id,
                    side=PostingType.CREDIT,  # Credit decreases sender's asset account
                    amount=amount,
                ),
                Posting(
                    id=generate_prefixed_id("pst"),
                    ledger_account_id=receiver_account.id,
                    side=PostingType.DEBIT,  # Debit increases receiver's asset account
                    amount=amount,
                ),
            ],
            posted=False,
        )

        accounts = {
            sender_account.id: sender_account,
            receiver_account.id: receiver_account,
        }

        self.ledger_service.post(journal, accounts)
        return journal
