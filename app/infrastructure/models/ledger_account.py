# app/infrastructure/models/ledger_account.py

from sqlalchemy import (
    ForeignKey,
    String,
    BigInteger,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.infrastructure.database.base import Base


class LedgerAccountModel(Base):
    __tablename__ = "ledger_accounts"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    account_id: Mapped[str] = mapped_column(
        ForeignKey("accounts.id"),
        unique=True,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
    )

    balance_minor: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
    )
