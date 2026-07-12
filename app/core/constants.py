"""
System-wide constants and configurations.

Contains:
- ID prefixes
- Security parameters
- Validation settings
- HTTP headers
- Regex patterns
"""

from __future__ import annotations

from enum import StrEnum

# =============================================================================
# Internal IDs
# =============================================================================


class InternalIDPrefix(StrEnum):
    """Internal database/system identifiers."""

    USER = "usr"
    CUSTOMER = "cst"

    ACCOUNT = "acc"
    TRANSACTION = "txn"

    JOURNAL = "jrn"
    POSTING = "pst"

    KYC = "kyc"

    SESSION = "ses"
    AUDIT = "adt"

    DISPUTE = "dsp"
    REFUND = "rfd"

    NOTIFICATION = "ntf"
    WEBHOOK = "whk"


# =============================================================================
# External References
# =============================================================================


class ExternalReferencePrefix(StrEnum):
    """Customer-facing references."""

    CUSTOMER = "CST"

    ACCOUNT = "ACC"

    TRANSACTION = "TXN"
    DISPUTE = "DSP"
    REFUND = "RFD"

    KYC = "KYC"

    INVOICE = "INV"
    ORDER = "ORD"

    NOTIFICATION = "NTF"


# =============================================================================
# Security
# =============================================================================

# OWASP recommended minimums
ARGON2_TIME_COST = 3
ARGON2_MEMORY_COST = 65536  # 64 MiB
ARGON2_PARALLELISM = 4


# =============================================================================
# HTTP Headers
# =============================================================================

HEADER_AUTHORIZATION = "Authorization"

HEADER_IDEMPOTENCY_KEY = "Idempotency-Key"

HEADER_REQUEST_ID = "X-Request-ID"
HEADER_CORRELATION_ID = "X-Correlation-ID"

HEADER_RATE_LIMIT_LIMIT = "X-RateLimit-Limit"
HEADER_RATE_LIMIT_REMAINING = "X-RateLimit-Remaining"
HEADER_RATE_LIMIT_RESET = "X-RateLimit-Reset"


# =============================================================================
# Defaults
# =============================================================================

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


# =============================================================================
# Validation
# =============================================================================

MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 20

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

OTP_LENGTH = 6


# =============================================================================
# Reference Lengths
# =============================================================================

CUSTOMER_REFERENCE_LENGTH = 12
ACCOUNT_REFERENCE_LENGTH = 12

TRANSACTION_REFERENCE_LENGTH = 16

KYC_REFERENCE_LENGTH = 12

INVOICE_REFERENCE_LENGTH = 12
ORDER_REFERENCE_LENGTH = 12

DISPUTE_REFERENCE_LENGTH = 15
REFUND_REFERENCE_LENGTH = 15
NOTIFICATION_REFERENCE_LENGTH = 15


# =============================================================================
# Regex
# =============================================================================

PHONE_REGEX = r"^\+?[1-9]\d{1,14}$"

EMAIL_REGEX = (
    r"^[a-zA-Z0-9._%+-]+@"
    r"[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)

PASSWORD_REGEX = (
    r"^(?=.*[a-z])"
    r"(?=.*[A-Z])"
    r"(?=.*\d)"
    r"(?=.*[!@#$%^&*()\-_+=\[\]{}|;:',.<>/?~`]).+$"
)

USERNAME_REGEX = (
    rf"^[a-zA-Z]"
    rf"[a-zA-Z0-9_]{{"
    rf"{MIN_USERNAME_LENGTH - 1},"
    rf"{MAX_USERNAME_LENGTH - 1}"
    rf"}}$"
)


# =============================================================================
# UUID
# =============================================================================

UUID_REGEX_PATTERN = (
    r"[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{12}"
)


# =============================================================================
# Internal IDs
# =============================================================================

INTERNAL_USER_ID_REGEX = (
    rf"^{InternalIDPrefix.USER}_{UUID_REGEX_PATTERN}$"
)

INTERNAL_CUSTOMER_ID_REGEX = (
    rf"^{InternalIDPrefix.CUSTOMER}_{UUID_REGEX_PATTERN}$"
)

INTERNAL_ACCOUNT_ID_REGEX = (
    rf"^{InternalIDPrefix.ACCOUNT}_{UUID_REGEX_PATTERN}$"
)

INTERNAL_TRANSACTION_ID_REGEX = (
    rf"^{InternalIDPrefix.TRANSACTION}_{UUID_REGEX_PATTERN}$"
)

INTERNAL_JOURNAL_ID_REGEX = (
    rf"^{InternalIDPrefix.JOURNAL}_{UUID_REGEX_PATTERN}$"
)

INTERNAL_POSTING_ID_REGEX = (
    rf"^{InternalIDPrefix.POSTING}_{UUID_REGEX_PATTERN}$"
)

INTERNAL_KYC_ID_REGEX = (
    rf"^{InternalIDPrefix.KYC}_{UUID_REGEX_PATTERN}$"
)

INTERNAL_SESSION_ID_REGEX = (
    rf"^{InternalIDPrefix.SESSION}_{UUID_REGEX_PATTERN}$"
)

INTERNAL_AUDIT_ID_REGEX = (
    rf"^{InternalIDPrefix.AUDIT}_{UUID_REGEX_PATTERN}$"
)

INTERNAL_DISPUTE_ID_REGEX = (
    rf"^{InternalIDPrefix.DISPUTE}_{UUID_REGEX_PATTERN}$"
)

INTERNAL_REFUND_ID_REGEX = (
    rf"^{InternalIDPrefix.REFUND}_{UUID_REGEX_PATTERN}$"
)

INTERNAL_NOTIFICATION_ID_REGEX = (
    rf"^{InternalIDPrefix.NOTIFICATION}_{UUID_REGEX_PATTERN}$"
)

INTERNAL_WEBHOOK_ID_REGEX = (
    rf"^{InternalIDPrefix.WEBHOOK}_{UUID_REGEX_PATTERN}$"
)


# =============================================================================
# External References
# =============================================================================

CUSTOMER_REFERENCE_REGEX = (
    rf"^{ExternalReferencePrefix.CUSTOMER}"
    rf"\d{{{CUSTOMER_REFERENCE_LENGTH - 3}}}$"
)

ACCOUNT_REFERENCE_REGEX = (
    rf"^{ExternalReferencePrefix.ACCOUNT}"
    rf"\d{{{ACCOUNT_REFERENCE_LENGTH - 3}}}$"
)

TRANSACTION_REFERENCE_REGEX = (
    rf"^{ExternalReferencePrefix.TRANSACTION}"
    rf"\d{{{TRANSACTION_REFERENCE_LENGTH - 3}}}$"
)

KYC_REFERENCE_REGEX = (
    rf"^{ExternalReferencePrefix.KYC}"
    rf"\d{{{KYC_REFERENCE_LENGTH - 3}}}$"
)

DISPUTE_REFERENCE_REGEX = (
    rf"^{ExternalReferencePrefix.DISPUTE}"
    rf"\d{{{DISPUTE_REFERENCE_LENGTH - 3}}}$"
)

REFUND_REFERENCE_REGEX = (
    rf"^{ExternalReferencePrefix.REFUND}"
    rf"\d{{{REFUND_REFERENCE_LENGTH - 3}}}$"
)

INVOICE_REFERENCE_REGEX = (
    rf"^{ExternalReferencePrefix.INVOICE}"
    rf"\d{{{INVOICE_REFERENCE_LENGTH - 3}}}$"
)

ORDER_REFERENCE_REGEX = (
    rf"^{ExternalReferencePrefix.ORDER}"
    rf"\d{{{ORDER_REFERENCE_LENGTH - 3}}}$"
)

NOTIFICATION_REFERENCE_REGEX = (
    rf"^{ExternalReferencePrefix.NOTIFICATION}"
    rf"\d{{{NOTIFICATION_REFERENCE_LENGTH - 3}}}$"
)


# =============================================================================
# OTP
# =============================================================================

OTP_REGEX = rf"^\d{{{OTP_LENGTH}}}$"