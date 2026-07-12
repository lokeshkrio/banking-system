import secrets
import uuid
from uuid6 import uuid7

# common id generation strategy for fintech system
# User ID                 -> UUIDv7
# Wallet ID               -> UUIDv7
# Public Account Number   -> Mod97
# Card Number             -> Luhn
# Transaction Ref         -> Mod11
# Customer ID (CIF)       -> Mod11
# Merchant ID             -> Mod11
# KYC Application ID      -> Mod11
# Invoice Number          -> Mod11


# ----------------------------------------
# ID generator using uuid
# ----------------------------------------


def generate_prefixed_id(prefix: str) -> str:
    return f"{prefix}_{uuid7()}"


def parse_prefixed_id(full_id: str) -> tuple[str, uuid.UUID]:
    parts = full_id.split("_", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(f"Invalid prefixed ID format: {full_id}")

    prefix, uid_str = parts
    return prefix, uuid.UUID(uid_str)


def get_prefix_from_id(full_id: str) -> str:
    return full_id.split("_", 1)[0]


def validate_prefix(prefixed_id: str, expected_prefix: str) -> bool:
    """Check that an ID has the expected prefix."""
    try:
        prefix, _ = parse_prefixed_id(prefixed_id)
        return prefix == expected_prefix
    except ValueError:
        return False


# ----------------------------------------
# mod 11 functionalities
# ----------------------------------------


def mod11_compute_check_digit(
    base_str: str, weights: list[int] | None = None
) -> int | None:
    """Compute Mod11 check digit."""
    if weights is None:
        weights = [2, 3, 4, 5, 6, 7, 8, 9]
    total = sum(
        int(digit) * weights[i % len(weights)]
        for i, digit in enumerate(reversed(base_str))
    )
    rem = total % 11

    if rem == 0:
        return 0
    return None if rem == 1 else 11 - rem


def mod11_validate(number: str) -> bool:
    if len(number) < 2 or not number.isdigit():
        return False

    payload = number[:-1]
    expected = mod11_compute_check_digit(payload)

    return False if expected is None else int(number[-1]) == expected


def generate_mod11_id(prefix: str, length: int = 12) -> str:
    # length is total length including prefix
    base_len = length - len(prefix) - 1
    if base_len < 4:
        raise ValueError("Length too short for prefix + check digit")

    base = "".join(str(secrets.randbelow(10)) for _ in range(base_len))
    check = mod11_compute_check_digit(base)
    if check is None:
        return generate_mod11_id(prefix, length)  # retry if check is Nones
    return f"{prefix}{base}{check}"


# ----------------------------------------
# IBAN mod 97 functionalities
# ----------------------------------------


def _letters_to_digits(text: str) -> str:
    """
    Convert letters to IBAN numeric form:
    A=10, B=11, ..., Z=35
    """
    result = []

    for ch in text.upper():
        if ch.isdigit():
            result.append(ch)
        elif ch.isalpha():
            result.append(str(ord(ch) - ord("A") + 10))
        else:
            raise ValueError(f"Invalid character: {ch}")

    return "".join(result)


def compute_mod97_check_digits(
    country_code: str,
    bban: str,
) -> str:
    """
    Compute IBAN check digits.
    """

    country_code = country_code.upper()

    # Move country code and placeholder digits to end
    temp = bban + country_code + "00"

    numeric = _letters_to_digits(temp)

    remainder = int(numeric) % 97

    check = 98 - remainder

    return f"{check:02d}"


def generate_iban(
    country_code: str = "UX",
    bban_length: int = 16,
) -> str:
    """
    Generate an IBAN-like account number.
    """

    bban = "".join(str(secrets.randbelow(10)) for _ in range(bban_length))

    check = compute_mod97_check_digits(
        country_code,
        bban,
    )

    return f"{country_code}{check}{bban}"


def validate_iban(iban: str) -> bool:
    """
    Validate an IBAN.
    """

    iban = iban.replace(" ", "").upper()

    if len(iban) < 5:
        return False

    rearranged = iban[4:] + iban[:4]

    numeric = _letters_to_digits(rearranged)

    return int(numeric) % 97 == 1


def pretty_iban(iban: str) -> str:
    return " ".join(iban[i : i + 4] for i in range(0, len(iban), 4))


# ----------------------------------------
# Luhn mod 10 functionalities
# ----------------------------------------


def luhn_compute_check_digit(base_str: str) -> int:
    """
    Compute Luhn mod 10 check digit.
    """
    if not base_str or not base_str.isdigit():
        raise ValueError("Input must be a non-empty string of digits")

    total = 0
    for i, digit in enumerate(reversed(base_str)):
        val = int(digit)
        if i % 2 == 0:
            val *= 2
            if val > 9:
                val -= 9
        total += val

    return (10 - (total % 10)) % 10


def luhn_validate(number: str) -> bool:
    """
    Validate that a number has a valid Luhn check digit.
    """
    if len(number) < 2 or not number.isdigit():
        return False

    payload = number[:-1]
    try:
        expected = luhn_compute_check_digit(payload)
        return int(number[-1]) == expected
    except ValueError:
        return False


def generate_luhn_id(prefix: str, length: int = 16) -> str:
    """
    Generate a Luhn-compliant identifier (e.g. card number).
    """
    # length is total length including prefix
    base_len = length - len(prefix) - 1
    if base_len < 4:
        raise ValueError("Length too short for prefix + check digit")

    base = "".join(str(secrets.randbelow(10)) for _ in range(base_len))
    payload = prefix + base
    check = luhn_compute_check_digit(payload)
    return f"{payload}{check}"


def luhn_format(number: str) -> str:
    """
    Format a number with spaces every 4 digits.
    """
    return " ".join(number[i : i + 4] for i in range(0, len(number), 4))


# ----------------------------------------
# Bank Account Number Generation (Mod97/IBAN)
# ----------------------------------------


def generate_bank_account_number(bank_code: str = "UX") -> str:
    """
    Generate an 18-character IBAN-like bank account number using the Mod97 strategy:
    - 2-letter country code (default 'UX')
    - 2 check digits
    - 14-digit BBAN
    """
    if len(bank_code) != 2 or not bank_code.isalpha():
        raise ValueError("Bank/Country code must be 2 alphabetic characters")

    return generate_iban(country_code=bank_code.upper(), bban_length=14)


def validate_bank_account_number(
    account_number: str, expected_bank_code: str | None = None
) -> bool:
    """
    Validate a bank account number:
    - Must be 18 characters.
    - Uses validate_iban for Mod97 validation.
    - Optionally, checks if it starts with expected_bank_code.
    """
    if not account_number or len(account_number) != 18:
        return False

    if expected_bank_code is not None and not account_number.upper().startswith(
        expected_bank_code.upper()
    ):
        return False

    return validate_iban(account_number)


# ----------------------------------------
# Specific ID Generators & Validators (Internal UUIDv7)
# ----------------------------------------
from app.core.constants import InternalIDPrefix, ExternalReferencePrefix, JournalReferencePrefix

def generate_user_id() -> str:
    return generate_prefixed_id(InternalIDPrefix.USER)

def validate_user_id(user_id: str) -> bool:
    return validate_prefix(user_id, InternalIDPrefix.USER)

def generate_customer_id() -> str:
    return generate_prefixed_id(InternalIDPrefix.CUSTOMER)

def validate_customer_id(customer_id: str) -> bool:
    return validate_prefix(customer_id, InternalIDPrefix.CUSTOMER)

def generate_account_id() -> str:
    return generate_prefixed_id(InternalIDPrefix.ACCOUNT)

def validate_account_id(account_id: str) -> bool:
    return validate_prefix(account_id, InternalIDPrefix.ACCOUNT)

def generate_transaction_id() -> str:
    return generate_prefixed_id(InternalIDPrefix.TRANSACTION)

def validate_transaction_id(transaction_id: str) -> bool:
    return validate_prefix(transaction_id, InternalIDPrefix.TRANSACTION)

def generate_journal_id() -> str:
    return generate_prefixed_id(InternalIDPrefix.JOURNAL)

def validate_journal_id(journal_id: str) -> bool:
    return validate_prefix(journal_id, InternalIDPrefix.JOURNAL)

def generate_posting_id() -> str:
    return generate_prefixed_id(InternalIDPrefix.POSTING)

def validate_posting_id(posting_id: str) -> bool:
    return validate_prefix(posting_id, InternalIDPrefix.POSTING)

def generate_kyc_id() -> str:
    return generate_prefixed_id(InternalIDPrefix.KYC)

def validate_kyc_id(kyc_id: str) -> bool:
    return validate_prefix(kyc_id, InternalIDPrefix.KYC)

def generate_session_id() -> str:
    return generate_prefixed_id(InternalIDPrefix.SESSION)

def validate_session_id(session_id: str) -> bool:
    return validate_prefix(session_id, InternalIDPrefix.SESSION)

def generate_audit_id() -> str:
    return generate_prefixed_id(InternalIDPrefix.AUDIT)

def validate_audit_id(audit_id: str) -> bool:
    return validate_prefix(audit_id, InternalIDPrefix.AUDIT)

def generate_transfer_id() -> str:
    return generate_prefixed_id(InternalIDPrefix.TRANSFER)

def validate_transfer_id(transfer_id: str) -> bool:
    return validate_prefix(transfer_id, InternalIDPrefix.TRANSFER)

def generate_dispute_id() -> str:
    return generate_prefixed_id(InternalIDPrefix.DISPUTE)

def validate_dispute_id(dispute_id: str) -> bool:
    return validate_prefix(dispute_id, InternalIDPrefix.DISPUTE)

def generate_refund_id() -> str:
    return generate_prefixed_id(InternalIDPrefix.REFUND)

def validate_refund_id(refund_id: str) -> bool:
    return validate_prefix(refund_id, InternalIDPrefix.REFUND)

def generate_notification_id() -> str:
    return generate_prefixed_id(InternalIDPrefix.NOTIFICATION)

def validate_notification_id(notification_id: str) -> bool:
    return validate_prefix(notification_id, InternalIDPrefix.NOTIFICATION)

def generate_webhook_id() -> str:
    return generate_prefixed_id(InternalIDPrefix.WEBHOOK)

def validate_webhook_id(webhook_id: str) -> bool:
    return validate_prefix(webhook_id, InternalIDPrefix.WEBHOOK)


# ----------------------------------------
# Specific ID Generators & Validators (External Mod11)
# ----------------------------------------

def generate_customer_ref() -> str:
    return generate_mod11_id(ExternalReferencePrefix.CUSTOMER, length=12)

def validate_customer_ref(ref: str) -> bool:
    return ref.startswith(ExternalReferencePrefix.CUSTOMER) and mod11_validate(ref)

def generate_account_ref() -> str:
    return generate_mod11_id(ExternalReferencePrefix.ACCOUNT, length=12)

def validate_account_ref(ref: str) -> bool:
    return ref.startswith(ExternalReferencePrefix.ACCOUNT) and mod11_validate(ref)

def generate_transaction_ref() -> str:
    return generate_mod11_id(ExternalReferencePrefix.TRANSACTION, length=12)

def validate_transaction_ref(ref: str) -> bool:
    return ref.startswith(ExternalReferencePrefix.TRANSACTION) and mod11_validate(ref)

def generate_dispute_ref() -> str:
    return generate_mod11_id(ExternalReferencePrefix.DISPUTE, length=12)

def validate_dispute_ref(ref: str) -> bool:
    return ref.startswith(ExternalReferencePrefix.DISPUTE) and mod11_validate(ref)

def generate_refund_ref() -> str:
    return generate_mod11_id(ExternalReferencePrefix.REFUND, length=12)

def validate_refund_ref(ref: str) -> bool:
    return ref.startswith(ExternalReferencePrefix.REFUND) and mod11_validate(ref)

def generate_kyc_ref() -> str:
    return generate_mod11_id(ExternalReferencePrefix.KYC, length=12)

def validate_kyc_ref(ref: str) -> bool:
    return ref.startswith(ExternalReferencePrefix.KYC) and mod11_validate(ref)

def generate_invoice_ref() -> str:
    return generate_mod11_id(ExternalReferencePrefix.INVOICE, length=12)

def validate_invoice_ref(ref: str) -> bool:
    return ref.startswith(ExternalReferencePrefix.INVOICE) and mod11_validate(ref)

def generate_order_ref() -> str:
    return generate_mod11_id(ExternalReferencePrefix.ORDER, length=12)

def validate_order_ref(ref: str) -> bool:
    return ref.startswith(ExternalReferencePrefix.ORDER) and mod11_validate(ref)

def generate_notification_ref() -> str:
    return generate_mod11_id(ExternalReferencePrefix.NOTIFICATION, length=12)

def validate_notification_ref(ref: str) -> bool:
    return ref.startswith(ExternalReferencePrefix.NOTIFICATION) and mod11_validate(ref)


# ----------------------------------------
# Specific ID Generators & Validators (Journal References Mod11)
# ----------------------------------------

def generate_reversal_ref() -> str:
    return generate_mod11_id(JournalReferencePrefix.REVERSAL, length=12)

def validate_reversal_ref(ref: str) -> bool:
    return ref.startswith(JournalReferencePrefix.REVERSAL) and mod11_validate(ref)

def generate_adjustment_ref() -> str:
    return generate_mod11_id(JournalReferencePrefix.ADJUSTMENT, length=12)

def validate_adjustment_ref(ref: str) -> bool:
    return ref.startswith(JournalReferencePrefix.ADJUSTMENT) and mod11_validate(ref)


# ----------------------------------------
# Other Specific Generators (Luhn / Miscellaneous)
# ----------------------------------------

def generate_card_number(bin_prefix: str = "400000") -> str:
    """Generate a 16-digit Luhn-compliant card number."""
    return generate_luhn_id(prefix=bin_prefix, length=16)

def validate_card_number(card_number: str) -> bool:
    return luhn_validate(card_number)

def generate_wallet_id() -> str:
    """Generate a UUIDv7 wallet ID."""
    return generate_prefixed_id("wal")

def validate_wallet_id(wallet_id: str) -> bool:
    return validate_prefix(wallet_id, "wal")
