from dataclasses import dataclass
from app.common.enums import UserStatus


@dataclass(frozen=True, slots=True)
class Customer:
    """Domain model representing a bank Customer."""

    id: str
    name: str
    status: UserStatus
