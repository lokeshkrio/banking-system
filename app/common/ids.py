import uuid
import random
import secrets
import string


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
    return prefix, str(uid_str)


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


def mod11_compute_check_digit(base_str: str, weights: list[int] | None = None) -> int:
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
    elif rem == 1:
        return None
    else:
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
# Masking utilities
# ----------------------------------------


def mask_ssn(ssn: str) -> str:
    """Mask SSN, revealing only last 4 digits.

    Example:
        800-05-1234 → ***-**-1234
    """
    if not ssn or len(ssn) != 11:
        raise ValueError("SSN must be 11 characters (XXX-XX-XXXX)")

    groups = ssn.split("-")
    if len(groups) != 3 or len(groups[2]) != 4:
        raise ValueError("Invalid SSN format")

    return f"***-**-{groups[2]}"


def mask_card(number: str, visible: int = 4) -> str:
    """
    Mask a card number, revealing only the last `visible` digits.
    """
    if not number or not number.isdigit():
        raise ValueError("Invalid card number")

    visible = max(0, min(visible, len(number)))

    masked = "*" * (len(number) - visible)
    return f"{masked}{number[-visible:]}"


def mask_email(email: str, visible: int = 4) -> str:
    """
    Mask an email address.

    Example:
        john.doe-2026@example.com
        → j*****e-2026@****.com
    """
    if "@" not in email:
        raise ValueError("Invalid email address")

    local, domain = email.split("@", 1)

    # Visible prefix of local part
    visible_local = local[:visible]
    masked_local = visible_local + "*" * (len(local) - visible)

    # Mask domain
    masked_domain = "*" * len(domain)

    return f"{masked_local}@{masked_domain}"


# ----------------------------------------
# Random alphanumeric generators
# ----------------------------------------


def generate_alphanumeric(
    length: int,
    include_digits: bool = True,
    include_letters: bool = True,
) -> str:
    """
    Generate a random alphanumeric string.
    """
    if include_digits and include_letters:
        population = string.ascii_letters + string.digits
    elif include_digits:
        population = string.digits
    elif include_letters:
        population = string.ascii_letters
    else:
        raise ValueError("Must include at least digits or letters")

    return "".join(random.choices(population, k=length))


def generate_numeric(length: int) -> str:
    """
    Generate a random numeric string (OTP style).
    """
    return generate_alphanumeric(length, include_digits=True, include_letters=False)


def generate_letters(length: int) -> str:
    """
    Generate a random alphabetic string.
    """
    return generate_alphanumeric(length, include_digits=False, include_letters=True)


# ----------------------------------------
# Random strong password
# ----------------------------------------


def generate_password(
    length: int = 16,
    include_digits: bool = True,
    include_special: bool = True,
) -> str:
    """
    Generate a strong random password with configurable complexity.
    """
    special_chars = r"!@#$%^&*()-_=+[]{}|;:',.<>/?~`"
    parts = [string.ascii_letters]
    if include_digits:
        parts.append(string.digits)
    if include_special:
        parts.append(special_chars)

    population = "".join(parts)

    if not (population):
        raise ValueError("Cannot generate password with no character sets")
    if length < 4:
        raise ValueError("Password length should be at least 4")

    # Ensure at least one of each requested type
    # Letters are always included
    password = [secrets.choice(string.ascii_letters)]
    if include_digits:
        password.append(secrets.choice(string.digits))
    if include_special:
        password.append(secrets.choice(special_chars))

    # Fill remaining length randomly
    while len(password) < length:
        password.append(secrets.choice(population))

    random.shuffle(password)
    return "".join(password)


# ----------------------------------------
# Random secure token
# ----------------------------------------


def generate_token(
    length: int = 64,
    encoding: str = "base64",
) -> str:
    """
    Generate a cryptographically secure random token.
    """
    if encoding == "hex":
        return secrets.token_hex(length // 2)
    elif encoding == "base64":
        return secrets.token_urlsafe(length * 3 // 4).rstrip("=")
    elif encoding == "bytes":
        return secrets.token_bytes(length).hex()
    else:
        raise ValueError(f"Unsupported encoding: {encoding}")
