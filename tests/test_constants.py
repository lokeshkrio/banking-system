import re

from app.core.constants import (
    ACCOUNT_NUMBER_LENGTH,
    ACCOUNT_NUMBER_REGEX,
    MAX_USERNAME_LENGTH,
    USERNAME_REGEX,
)


def test_username_regex() -> None:
    username_pattern = re.compile(USERNAME_REGEX)

    # Valid usernames
    assert username_pattern.match("usr") is not None  # Min length
    assert username_pattern.match("a" * MAX_USERNAME_LENGTH) is not None  # Max length
    assert username_pattern.match("user123_name") is not None

    # Invalid usernames
    assert username_pattern.match("us") is None  # Too short
    assert username_pattern.match("a" * (MAX_USERNAME_LENGTH + 1)) is None  # Too long
    assert username_pattern.match("1username") is None  # Must start with letter
    assert username_pattern.match("user-name") is None  # Invalid character '-'


def test_account_number_regex() -> None:
    acc_pattern = re.compile(ACCOUNT_NUMBER_REGEX)

    # Valid account numbers
    assert acc_pattern.match("UX" + "1" * (ACCOUNT_NUMBER_LENGTH - 2)) is not None
    assert acc_pattern.match("FR" + "0" * (ACCOUNT_NUMBER_LENGTH - 2)) is not None

    # Invalid account numbers
    assert acc_pattern.match("U" + "1" * (ACCOUNT_NUMBER_LENGTH - 1)) is None  # Too short bank code
    assert acc_pattern.match("UBX" + "1" * (ACCOUNT_NUMBER_LENGTH - 3)) is None  # Too long bank code
    assert acc_pattern.match("UX" + "1" * (ACCOUNT_NUMBER_LENGTH - 3)) is None  # Total too short
    assert acc_pattern.match("UX" + "1" * (ACCOUNT_NUMBER_LENGTH - 1)) is None  # Total too long
    assert acc_pattern.match("ux" + "1" * (ACCOUNT_NUMBER_LENGTH - 2)) is None  # Lowercase bank code
    assert acc_pattern.match("UX" + "1" * (ACCOUNT_NUMBER_LENGTH - 3) + "A") is None  # Non-numeric suffix
    assert acc_pattern.match("") is None
