"""
All domain enums used across the platform. These map directly to
PostgreSQL CHECK constraints on the corresponding columns.
"""

from enum import StrEnum

# ----------------------------------------
# User related enums
# ----------------------------------------


class UserStatus(StrEnum):
    """User account lifecycle states.

    | Status    | Description                                             |
    |-----------|---------------------------------------------------------|
    | active    | User is fully verified and active on the platform       |
    | inactive  | User has deactivated their account or is unregistered    |
    | suspended | User account is suspended due to violations or risk      |
    | pending   | User registration is incomplete or awaiting validation  |
    """

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING = "PENDING"


class UserRole(StrEnum):
    """User roles defining platform access privileges.

    | Role     | Description                                           |
    |----------|-------------------------------------------------------|
    | customer | Standard end-user with access to consumer wallets     |
    | admin    | Platform administrator with full access and control  |
    | support  | Customer support agent with limited read/write access |
    """

    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"
    SUPPORT = "SUPPORT"


# ----------------------------------------
# Identity & Verification enums
# ----------------------------------------


class IdentityProvider(StrEnum):
    """Authentication and identity providers.

    | Provider | Description                                     |
    |----------|-------------------------------------------------|
    | email    | Standard email and password authentication     |
    | phone    | Mobile phone OTP-based authentication           |
    | google   | Google OAuth2 federated authentication          |
    | apple    | Apple Identity/OAuth federated authentication  |
    """

    EMAIL = "EMAIL"
    PHONE = "PHONE"
    GOOGLE = "GOOGLE"
    APPLE = "APPLE"


class DocumentType(StrEnum):
    """Supported identity document types for verification.

    | Type            | Description                               |
    |-----------------|-------------------------------------------|
    | passport        | Government-issued international passport  |
    | national_id     | Government-issued national identity card  |
    | driving_license | Government-issued driver's license        |
    """

    PASSPORT = "PASSPORT"
    NATIONAL_ID = "NATIONAL_ID"
    DRIVING_LICENSE = "DRIVING_LICENSE"


class VerificationStatus(StrEnum):
    """Identity verification/KYC status states.

    | Status   | Description                                           |
    |----------|-------------------------------------------------------|
    | pending  | Verification is in progress or awaiting document review|
    | verified | Identity has been successfully verified                |
    | rejected | Verification failed due to invalid/incorrect document |
    """

    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class OtpChannel(StrEnum):
    """Channels used for delivering one-time passwords (OTPs).

    | Channel | Description                              |
    |---------|------------------------------------------|
    | email   | OTP is delivered via email notification  |
    | sms     | OTP is delivered via SMS text message    |
    """

    EMAIL = "EMAIL"
    SMS = "SMS"


# ----------------------------------------
# Account related enums
# ----------------------------------------


class AccountStatus(StrEnum):
    """Account lifecycle states.

    State machine:
        [*] → pending → active → frozen/suspended → closed → [*]

    | Status    | Can receive? | Can send? |
    |-----------|-------------|-----------|
    | pending   | No          | No        |
    | active    | Yes         | Yes       |
    | frozen    | Yes (held)  | No        |
    | suspended | No          | No        |
    | closed    | No          | No        |
    """

    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"


class Currency(StrEnum):
    """Supported currencies on the platform.

    | Currency | Description                  |
    |----------|------------------------------|
    | usd      | United States Dollar         |
    | eur      | Euro                         |
    | gbp      | British Pound Sterling       |
    | inr      | Indian Rupee                 |
    | cad      | Canadian Dollar              |
    """

    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    INR = "INR"
    CAD = "CAD"


class AccountType(StrEnum):
    """Types of accounts.

    | Type      | Description                 |
    |-----------|-----------------------------|
    | saving    | Liquid savings              |
    | checking  | Everyday spending account   |
    | credit    | Credit/loan facility        |
    """

    SAVING = "SAVING"
    CHECKING = "CHECKING"
    CREDIT = "CREDIT"


# Valid wallet status transitions
ACCOUNT_TRANSITIONS: dict[AccountStatus, set[AccountStatus]] = {
    AccountStatus.PENDING: {AccountStatus.ACTIVE, AccountStatus.CLOSED},
    AccountStatus.ACTIVE: {
        AccountStatus.FROZEN,
        AccountStatus.SUSPENDED,
        AccountStatus.CLOSED,
    },
    AccountStatus.FROZEN: {AccountStatus.ACTIVE, AccountStatus.SUSPENDED},
    AccountStatus.SUSPENDED: {AccountStatus.ACTIVE, AccountStatus.CLOSED},
    AccountStatus.CLOSED: set(),  # Terminal state
}

# ----------------------------------------
# Transaction related enums
# ----------------------------------------


class TransactionStatus(StrEnum):
    """Transaction states.

    State machine:
        [*] → initiated → processing → completed/failed/reversed → [*]

    | Status       | Meaning                             |
    |--------------|-------------------------------------|
    | initiated    | Payment started, not yet processed  |
    | processing   | Payment being processed             |
    | completed    | Payment successful                  |
    | failed       | Payment failed                      |
    | reversed     | Payment reversed (refunded)         |
    """

    INITIATED = "INITIATED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"


# Valid transaction status transitions
TRANSACTION_TRANSITIONS: dict[TransactionStatus, set[TransactionStatus]] = {
    TransactionStatus.INITIATED: {
        TransactionStatus.PROCESSING,
        TransactionStatus.FAILED,
        TransactionStatus.COMPLETED,
    },
    TransactionStatus.PROCESSING: {
        TransactionStatus.COMPLETED,
        TransactionStatus.FAILED,
        TransactionStatus.REVERSED,
    },
    TransactionStatus.COMPLETED: {TransactionStatus.REVERSED},
    TransactionStatus.FAILED: {TransactionStatus.INITIATED, TransactionStatus.REVERSED},
    TransactionStatus.REVERSED: set(),  # Terminal state
}


class TransactionCategory(StrEnum):
    """Categories of transactions.

    | Category   | Description                                |
    |------------|--------------------------------------------|
    | to_bank    | Transfer from wallet to bank account       |
    | from_bank  | Transfer from bank account to wallet       |
    | p2p        | Transfer between two wallets               |
    """

    TO_BANK = "TO_BANK"
    FROM_BANK = "FROM_BANK"
    P2P = "P2P"


class TransactionType(StrEnum):
    """Specific transaction types within categories.

    | Type       | Description                                                 |
    |------------|-------------------------------------------------------------|
    | debit      | General debit transaction (deducting funds)                 |
    | credit     | General credit transaction (adding funds)                    |
    | transfer   | Peer-to-peer or wallet-to-wallet transfer                   |
    | payment    | Purchase or service payment transaction                     |
    | withdrawal | Cash withdrawal or outward bank transfer                    |
    | deposit    | Cash deposit or inward bank transfer                        |
    | reward     | Promotional cashback or referral reward credit              |
    | fee        | Service charge or system fee transaction                    |
    | refund     | Reversed transaction returning funds to original account     |
    """

    DEBIT = "DEBIT"
    CREDIT = "CREDIT"
    TRANSFER = "TRANSFER"
    PAYMENT = "PAYMENT"
    WITHDRAWAL = "WITHDRAWAL"
    DEPOSIT = "DEPOSIT"
    REWARD = "REWARD"
    FEE = "FEE"
    REFUND = "REFUND"


# ----------------------------------------
# Dispute and Refund related enums
# ----------------------------------------


class DisputeReason(StrEnum):
    """Reasons cited for filing a transaction dispute.

    | Reason               | Description                                              |
    |----------------------|----------------------------------------------------------|
    | fraud                | Unauthorized or fraudulent transaction                   |
    | wrong_amount         | Charged amount differs from the agreed-upon amount       |
    | not_received         | Purchased goods or services were not received            |
    | not_as_described     | Goods/services received were not as described/damaged    |
    | service_not_rendered | Expected service was not provided                       |
    | other                | Any other miscellaneous or specified reason              |
    """

    FRAUD = "FRAUD"
    WRONG_AMOUNT = "WRONG_AMOUNT"
    NOT_RECEIVED = "NOT_RECEIVED"
    NOT_AS_DESCRIBED = "NOT_AS_DESCRIBED"
    SERVICE_NOT_RENDERED = "SERVICE_NOT_RENDERED"
    OTHER = "OTHER"


class DisputeStatus(StrEnum):
    """Current state of a customer transaction dispute.

    | Status             | Description                                                 |
    |--------------------|-------------------------------------------------------------|
    | open               | Dispute initiated and registered by customer                |
    | in_review          | Case is being analyzed by platform support/compliance       |
    | evidence_submitted | Evidence has been submitted to the payment network/merchant |
    | resolved           | Dispute resolution has been decided and applied             |
    | closed             | Dispute is finalized and no further action will be taken    |
    """

    OPEN = "OPEN"
    IN_REVIEW = "IN_REVIEW"
    EVIDENCE_SUBMITTED = "EVIDENCE_SUBMITTED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class DisputeResolution(StrEnum):
    """Outcome/resolution of a finalized dispute.

    | Resolution                 | Description                                                 |
    |----------------------------|-------------------------------------------------------------|
    | money_returned_to_charger   | Funds returned/retained by the merchant/charger             |
    | money_returned_to_disputer  | Funds returned to the customer filing the dispute           |
    | fee_waived                 | Any associated dispute fees have been waived                |
    | partially_refunded         | Partial refund has been agreed and issued to the disputer   |
    """

    MONEY_RETURNED_TO_CHARGER = "MONEY_RETURNED_TO_CHARGER"
    MONEY_RETURNED_TO_DISPUTER = "MONEY_RETURNED_TO_DISPUTER"
    FEE_WAIVED = "FEE_WAIVED"
    PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED"
    NO_REFUND = "NO_REFUND"


class RefundStatus(StrEnum):
    """Refund/chargeback states."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


REFUND_TRANSITIONS: dict[RefundStatus, set[RefundStatus]] = {
    RefundStatus.PENDING: {
        RefundStatus.PROCESSING,
        RefundStatus.FAILED,
        RefundStatus.COMPLETED,
        RefundStatus.PARTIAL,
    },
    RefundStatus.PROCESSING: {
        RefundStatus.COMPLETED,
        RefundStatus.FAILED,
        RefundStatus.PARTIAL,
    },
    RefundStatus.COMPLETED: {RefundStatus.PARTIAL},
    RefundStatus.FAILED: {RefundStatus.PENDING, RefundStatus.PARTIAL},
    RefundStatus.PARTIAL: set(),
}

# ----------------------------------------
# Loyalty & Reward enums
# ----------------------------------------


class RewardStatus(StrEnum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REDEEMED = "REDEEMED"
    PENDING = "PENDING"


class RewardType(StrEnum):
    CASHBACK = "CASHBACK"
    POINTS = "POINTS"
    DISCOUNT = "DISCOUNT"
    GIFT_CARD = "GIFT_CARD"


class TierStatus(StrEnum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"


# ----------------------------------------
# Notification enums
# ----------------------------------------


class NotificationStatus(StrEnum):
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    READ = "READ"
    FAILED = "FAILED"
    PENDING = "PENDING"


class NotificationType(StrEnum):
    TRANSACTION = "TRANSACTION"
    VERIFICATION = "VERIFICATION"
    MARKETING = "MARKETING"
    SYSTEM = "SYSTEM"
    PROMOTIONAL = "PROMOTIONAL"
    SECURITY = "SECURITY"
    STATEMENT = "STATEMENT"


# ----------------------------------------
# System & Admin enums
# ----------------------------------------
class AdminAction(StrEnum):
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    CREATE_USER = "CREATE_USER"
    UPDATE_USER = "UPDATE_USER"
    SUSPEND_USER = "SUSPEND_USER"
    DELETE_USER = "DELETE_USER"
    CREATE_MERCHANT = "CREATE_MERCHANT"
    APPROVE_MERCHANT = "APPROVE_MERCHANT"
    REJECT_MERCHANT = "REJECT_MERCHANT"
    UPDATE_TRANSACTION = "UPDATE_TRANSACTION"
    REFUND_TRANSACTION = "REFUND_TRANSACTION"
    CREATE_DISPUTE = "CREATE_DISPUTE"
    CLOSE_DISPUTE = "CLOSE_DISPUTE"
    ISSUE_REWARD = "ISSUE_REWARD"
    REDEEM_REWARD = "REDEEM_REWARD"
    CREATE_PAYOUT = "CREATE_PAYOUT"
    APPROVE_PAYOUT = "APPROVE_PAYOUT"
    REJECT_PAYOUT = "REJECT_PAYOUT"
    UPDATE_SYSTEM_SETTING = "UPDATE_SYSTEM_SETTING"
    MANUAL_ADJUSTMENT = "MANUAL_ADJUSTMENT"
    CREATE_DOCUMENT = "CREATE_DOCUMENT"
    APPROVE_DOCUMENT = "APPROVE_DOCUMENT"
    REJECT_DOCUMENT = "REJECT_DOCUMENT"
