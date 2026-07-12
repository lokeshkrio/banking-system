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
