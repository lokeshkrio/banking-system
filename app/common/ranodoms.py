import random
import secrets
import string

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

    return "".join(random.choices(population, k=length))  # noqa: S311


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
    if encoding == "base64":
        return secrets.token_urlsafe(length * 3 // 4).rstrip("=")
    if encoding == "bytes":
        return secrets.token_bytes(length).hex()
    raise ValueError(f"Unsupported encoding: {encoding}")
