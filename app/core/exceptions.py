
"""
Application Exception Hierarchy.

All domain exceptions inherit from AppException which can be
serialized into RFC 7807 Problem Details responses.

Hierarchy:

AppException
├── AuthenticationError
├── AuthorizationError
├── ValidationError
├── NotFoundError
├── ConflictError
├── RiskError
└── InfrastructureError
"""


from typing import Any


class AppException(Exception):
    """Base application exception."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"
    detail: str = "An unexpected error occurred."

    def __init__(
        self,
        detail: str | None = None,
        *,
        extra: dict[str, Any] | None = None,
    ) -> None:
        self.detail = detail or self.__class__.detail
        self.extra = extra or {}

        super().__init__(self.detail)

    def to_problem_detail(
        self,
        *,
        instance: str | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "type": (
                "urn:unitybankx:error:"
                f"{self.error_code.lower().replace('_', '-')}"
            ),
            "title": self.error_code.replace("_", " ").title(),
            "status": self.status_code,
            "detail": self.detail,
        }

        if instance:
            body["instance"] = instance

        if request_id:
            body["request_id"] = request_id

        body |= self.extra

        return body


# ============================================================================
# Generic Categories
# ============================================================================


class AuthenticationError(AppException):
    status_code = 401
    error_code = "AUTHENTICATION_ERROR"
    detail = "Authentication failed."


class AuthorizationError(AppException):
    status_code = 403
    error_code = "AUTHORIZATION_ERROR"
    detail = "Permission denied."


class DomainValidationError(AppException):
    status_code = 400
    error_code = "VALIDATION_ERROR"
    detail = "Validation failed."


class NotFoundError(AppException):
    status_code = 404
    error_code = "RESOURCE_NOT_FOUND"
    detail = "Requested resource was not found."


class ConflictError(AppException):
    status_code = 409
    error_code = "RESOURCE_CONFLICT"
    detail = "Resource conflict occurred."


class RiskError(AppException):
    status_code = 403
    error_code = "RISK_BLOCKED"
    detail = "Blocked by risk policies."


class InfrastructureError(AppException):
    status_code = 503
    error_code = "SERVICE_UNAVAILABLE"
    detail = "Required infrastructure is unavailable."


# ============================================================================
# Authentication
# ============================================================================


class InvalidCredentialsError(AuthenticationError):
    error_code = "INVALID_CREDENTIALS"
    detail = "Invalid email or password."


class TokenExpiredError(AuthenticationError):
    error_code = "TOKEN_EXPIRED"
    detail = "Authentication token has expired."


class TokenInvalidError(AuthenticationError):
    error_code = "TOKEN_INVALID"
    detail = "Authentication token is invalid."


class RefreshTokenReuseError(AuthenticationError):
    error_code = "REFRESH_TOKEN_REUSE"
    detail = (
        "Refresh token reuse detected. "
        "All sessions have been revoked."
    )


class MfaInvalidCodeError(AuthenticationError):
    error_code = "MFA_INVALID_CODE"
    detail = "MFA code is invalid or expired."


# ============================================================================
# Authorization
# ============================================================================


class InsufficientPermissionsError(AuthorizationError):
    error_code = "INSUFFICIENT_PERMISSIONS"
    detail = "Insufficient permissions."


class EmailNotVerifiedError(AuthorizationError):
    error_code = "EMAIL_NOT_VERIFIED"
    detail = "Email must be verified."


class AccountSuspendedError(AuthorizationError):
    error_code = "ACCOUNT_SUSPENDED"
    detail = "Account has been suspended."


class MfaRequiredError(AuthorizationError):
    error_code = "MFA_REQUIRED"
    detail = "Multi-factor authentication required."


# ============================================================================
# Users
# ============================================================================


class UserNotFoundError(NotFoundError):
    error_code = "USER_NOT_FOUND"
    detail = "User not found."


class EmailAlreadyRegisteredError(ConflictError):
    error_code = "EMAIL_ALREADY_REGISTERED"
    detail = "Email address already registered."


# ============================================================================
# Accounts
# ============================================================================


class AccountNotFoundError(NotFoundError):
    error_code = "ACCOUNT_NOT_FOUND"
    detail = "Account not found."


class AccountFrozenError(AuthorizationError):
    error_code = "ACCOUNT_FROZEN"
    detail = "Account is frozen."


class AccountClosedError(AuthorizationError):
    error_code = "ACCOUNT_CLOSED"
    detail = "Account is closed."


class AccountNotEmptyError(ConflictError):
    error_code = "ACCOUNT_NOT_EMPTY"
    detail = "Account balance must be zero."


class InvalidAccountTransitionError(ConflictError):
    error_code = "INVALID_ACCOUNT_TRANSITION"
    detail = "Invalid account status transition."


class AccountNotActiveError(DomainValidationError):
    error_code = "ACCOUNT_NOT_ACTIVE"
    detail = "Account is not in ACTIVE status."


# ============================================================================
# Transfers
# ============================================================================


class InsufficientFundsError(ConflictError):
    error_code = "INSUFFICIENT_FUNDS"
    detail = "Insufficient funds."


class DuplicateTransferError(ConflictError):
    error_code = "DUPLICATE_TRANSFER"
    detail = "Duplicate transfer detected."


class TransferNotFoundError(NotFoundError):
    error_code = "TRANSFER_NOT_FOUND"
    detail = "Transfer not found."


class TransferLimitExceededError(ConflictError):
    error_code = "TRANSFER_LIMIT_EXCEEDED"
    detail = "Transfer limit exceeded."


class SameAccountTransferError(DomainValidationError):
    error_code = "SAME_ACCOUNT_TRANSFER"
    detail = "Source and destination accounts must differ."


# ============================================================================
# Ledger
# ============================================================================


class JournalImbalanceError(AppException):
    status_code = 500
    error_code = "JOURNAL_IMBALANCE"
    detail = (
        "Journal entry is not balanced. "
        "This indicates a critical system error."
    )


class LedgerAccountNotFoundError(NotFoundError):
    error_code = "LEDGER_ACCOUNT_NOT_FOUND"
    detail = "Ledger account not found."


class JournalAlreadyPostedError(ConflictError):
    error_code = "JOURNAL_ALREADY_POSTED"
    detail = "Journal has already been posted."


# ============================================================================
# Currency & FX
# ============================================================================


class CurrencyNotFoundError(NotFoundError):
    error_code = "CURRENCY_NOT_FOUND"
    detail = "Currency not supported."


class ExchangeRateUnavailableError(InfrastructureError):
    error_code = "EXCHANGE_RATE_UNAVAILABLE"
    detail = "Exchange rate unavailable."


class StaleExchangeRateError(ConflictError):
    error_code = "STALE_EXCHANGE_RATE"
    detail = "Exchange rate is stale."


class InvalidIBANError(DomainValidationError):
    error_code = "INVALID_IBAN"
    detail = "Invalid IBAN checksum."


# ============================================================================
# Risk
# ============================================================================


class RiskBlockedError(RiskError):
    error_code = "RISK_BLOCKED"
    detail = "Transaction blocked by risk engine."


class RiskStepUpRequiredError(RiskError):
    error_code = "RISK_STEP_UP_REQUIRED"
    detail = "Additional verification required."


# ============================================================================
# Validation
# ============================================================================


class PasswordTooWeakError(DomainValidationError):
    error_code = "PASSWORD_TOO_WEAK"
    detail = "Password does not meet requirements."


class InvalidIdempotencyKeyError(DomainValidationError):
    error_code = "INVALID_IDEMPOTENCY_KEY"
    detail = "Idempotency key is invalid."


class MissingIdempotencyKeyError(DomainValidationError):
    error_code = "MISSING_IDEMPOTENCY_KEY"
    detail = "Idempotency key is required."


# ============================================================================
# Infrastructure
# ============================================================================


class RateLimitExceededError(AppException):
    status_code = 429
    error_code = "RATE_LIMIT_EXCEEDED"
    detail = "Too many requests."
