from enum import StrEnum


class TransferStatus(StrEnum):
    """Lifecycle states of a Transfer.

    State machine:
        [*] → PENDING → PROCESSING → COMPLETED/FAILED → REVERSED → [*]

    | Status     | Meaning                                      |
    |------------|----------------------------------------------|
    | PENDING    | Transfer created, not yet submitted          |
    | PROCESSING | Journal created and being applied            |
    | COMPLETED  | Journal posted, balances updated             |
    | FAILED     | Transfer could not be completed              |
    | REVERSED   | A reversal journal has been posted           |
    """

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"


# Valid Transfer status transitions
TRANSFER_TRANSITIONS: dict[TransferStatus, set[TransferStatus]] = {
    TransferStatus.PENDING: {TransferStatus.PROCESSING, TransferStatus.FAILED},
    TransferStatus.PROCESSING: {TransferStatus.COMPLETED, TransferStatus.FAILED},
    TransferStatus.COMPLETED: {TransferStatus.REVERSED},
    TransferStatus.FAILED: set(),   # Terminal
    TransferStatus.REVERSED: set(), # Terminal
}
