# app/infrastructure/models/customer.py

from datetime import datetime

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from sqlalchemy import String, DateTime

from app.infrastructure.database.base import Base


class CustomerModel(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
    )

    status: Mapped[str] = mapped_column(
        String(50),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )