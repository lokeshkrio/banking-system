import secrets
import uuid

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
    return f"{prefix}_{uuid.uuid4()}"


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


def mod11_compute_check_digit(base_str: str, weights: list[int] | None = None) -> int | None:
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
    if rem == 1:
        return None
    return 11 - rem


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


def validate_bank_account_number(account_number: str, expected_bank_code: str | None = None) -> bool:
    """
    Validate a bank account number:
    - Must be 18 characters.
    - Uses validate_iban for Mod97 validation.
    - Optionally, checks if it starts with expected_bank_code.
    """
    if not account_number or len(account_number) != 18:
        return False

    if expected_bank_code is not None and not account_number.upper().startswith(expected_bank_code.upper()):
        return False

    return validate_iban(account_number)
