# app/infrastructure/models/account.py

from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    String,
    DateTime,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.infrastructure.database.base import Base


class AccountModel(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customers.id"),
    )

    account_number: Mapped[str] = mapped_column(
        String(64),
        unique=True,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
    )

    status: Mapped[str] = mapped_column(
        String(50),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    customer = relationship(
        "CustomerModel",
        lazy="joined",
    )
