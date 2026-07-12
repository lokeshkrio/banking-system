from app.core.exceptions import ConflictError, DomainValidationError


class CurrencyMismatchError(DomainValidationError):
    error_code = "CURRENCY_MISMATCH"
    detail = "Journal postings contain multiple currencies."


class JournalImbalanceError(DomainValidationError):
    error_code = "JOURNAL_IMBALANCE"
    detail = "Journal debits and credits do not balance."


class JournalAlreadyPostedError(ConflictError):
    error_code = "JOURNAL_ALREADY_POSTED"
    detail = "This journal has already been posted."
