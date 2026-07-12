import pytest
import re

from app.core.constants import ACCOUNT_NUMBER_REGEX
from app.common.ids import generate_bank_account_number, validate_bank_account_number


def test_generate_and_validate_defaults() -> None:
    pattern = re.compile(ACCOUNT_NUMBER_REGEX)
    for _ in range(100):
        acc = generate_bank_account_number()
        assert len(acc) == 18
        assert acc.startswith("UX")
        assert pattern.match(acc) is not None
        assert validate_bank_account_number(acc) is True
        assert validate_bank_account_number(acc, expected_bank_code="UX") is True
        assert validate_bank_account_number(acc, expected_bank_code="FR") is False


def test_generate_with_custom_codes() -> None:
    acc = generate_bank_account_number(bank_code="FR")
    assert len(acc) == 18
    assert acc.startswith("FR")
    assert validate_bank_account_number(acc) is True
    assert validate_bank_account_number(acc, expected_bank_code="FR") is True


def test_generate_validation_errors() -> None:
    with pytest.raises(ValueError, match="Bank/Country code must be 2 alphabetic characters"):
        generate_bank_account_number(bank_code="U")

    with pytest.raises(ValueError, match="Bank/Country code must be 2 alphabetic characters"):
        generate_bank_account_number(bank_code="UX1")


def test_validation_failure_modes() -> None:
    # Too short / empty
    assert validate_bank_account_number("") is False
    assert validate_bank_account_number("UX881234567890123") is False  # 17 chars

    # Non-alphabetic country code / non-numeric sequence
    assert validate_bank_account_number("128812345678901234") is False
    assert validate_bank_account_number("UX881234567890123A") is False

    # Check digit tampering
    valid_acc = generate_bank_account_number()
    # Check digits are at index 2 and 3. Let's tamper with them.
    # Swap check digits to '00' or different digits to ensure it fails mod 97 check
    check_digits = valid_acc[2:4]
    tampered_check = "00" if check_digits != "00" else "99"
    invalid_acc = valid_acc[:2] + tampered_check + valid_acc[4:]
    assert validate_bank_account_number(invalid_acc) is False
