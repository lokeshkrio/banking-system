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
    assert acc_pattern.match("1" * ACCOUNT_NUMBER_LENGTH) is not None

    # Invalid account numbers
    assert acc_pattern.match("1" * (ACCOUNT_NUMBER_LENGTH - 1)) is None
    assert acc_pattern.match("1" * (ACCOUNT_NUMBER_LENGTH + 1)) is None
    assert acc_pattern.match("a" * ACCOUNT_NUMBER_LENGTH) is None
    assert acc_pattern.match("") is None
