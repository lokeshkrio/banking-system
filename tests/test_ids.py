import pytest

from app.common.ids import (
    generate_luhn_id,
    generate_mod11_id,
    luhn_compute_check_digit,
    luhn_validate,
    mod11_compute_check_digit,
    mod11_validate,
)
from app.common.randoms import (
    generate_alphanumeric,
    generate_letters,
    generate_numeric,
    generate_password,
    generate_token,
)


def test_mod11_compute_check_digit_basic():
    # Test case where sum % 11 is neither 0 nor 1 (rem = 5)
    # "123" -> reversed: 3, 2, 1
    # total = 3*2 + 2*3 + 1*4 = 16
    # rem = 16 % 11 = 5
    # expected = 11 - 5 = 6
    assert mod11_compute_check_digit("123") == 6

def test_mod11_compute_check_digit_rem_zero():
    # Test case where sum % 11 == 0
    # "14" -> reversed: 4, 1
    # total = 4*2 + 1*3 = 11
    # rem = 11 % 11 = 0
    # expected = 0
    assert mod11_compute_check_digit("14") == 0

def test_mod11_compute_check_digit_rem_one():
    # Test case where sum % 11 == 1
    # "23" -> reversed: 3, 2
    # total = 3*2 + 2*3 = 12
    # rem = 12 % 11 = 1
    # expected = None
    assert mod11_compute_check_digit("23") is None

def test_mod11_compute_check_digit_empty():
    # Empty string should result in sum of 0, rem 0, check digit 0
    assert mod11_compute_check_digit("") == 0

def test_mod11_compute_check_digit_non_digit():
    # Non-digit character should raise ValueError
    with pytest.raises(ValueError):
        mod11_compute_check_digit("12a")

def test_mod11_compute_check_digit_custom_weights():
    # Custom weights test
    # "12" -> reversed: 2, 1. weights: [5, 7]
    # total = 2*5 + 1*7 = 17
    # rem = 17 % 11 = 6
    # expected = 11 - 6 = 5
    assert mod11_compute_check_digit("12", weights=[5, 7]) == 5

def test_mod11_validate_valid():
    assert mod11_validate("1236") is True
    assert mod11_validate("140") is True

def test_mod11_validate_invalid():
    # Incorrect check digit
    assert mod11_validate("1235") is False
    assert mod11_validate("141") is False

def test_mod11_validate_rem_one():
    # For payload "23", check digit is None, validation must return False for any digit
    for i in range(10):
        assert mod11_validate(f"23{i}") is False

def test_mod11_validate_invalid_inputs():
    # Short length
    assert mod11_validate("") is False
    assert mod11_validate("1") is False
    # Non-digits
    assert mod11_validate("12a") is False
    assert mod11_validate("abc") is False

def test_generate_mod11_id_success():
    prefix = "TXN"
    # Generate multiple times to ensure we hit case with retry (where check is None)
    for _ in range(50):
        id_str = generate_mod11_id(prefix, length=12)
        assert id_str.startswith(prefix)
        assert len(id_str) == 12

        # The numeric part should validate
        numeric_part = id_str[len(prefix):]
        assert numeric_part.isdigit()
        assert mod11_validate(numeric_part) is True

def test_generate_mod11_id_invalid_length():
    with pytest.raises(ValueError):
        # Prefix "TXN" (len 3), length 4 -> base_len = 4 - 3 - 1 = 0 (less than 4)
        generate_mod11_id("TXN", length=4)


# ----------------------------------------
# Luhn mod 10 tests
# ----------------------------------------

def test_luhn_compute_check_digit_basic():
    # Test with payload "7992739871" -> expected check digit 3
    assert luhn_compute_check_digit("7992739871") == 3

def test_luhn_compute_check_digit_invalid():
    # Empty string
    with pytest.raises(ValueError):
        luhn_compute_check_digit("")
    # Non-digit
    with pytest.raises(ValueError):
        luhn_compute_check_digit("12a")

def test_luhn_validate_valid():
    assert luhn_validate("79927398713") is True
    assert luhn_validate("49927398716") is True

def test_luhn_validate_invalid():
    assert luhn_validate("79927398714") is False
    assert luhn_validate("") is False
    assert luhn_validate("1") is False
    assert luhn_validate("12a") is False

def test_generate_luhn_id_success():
    prefix = "4"
    for _ in range(50):
        id_str = generate_luhn_id(prefix, length=16)
        assert id_str.startswith(prefix)
        assert len(id_str) == 16
        assert id_str.isdigit()
        assert luhn_validate(id_str) is True

def test_generate_luhn_id_invalid_length():
    with pytest.raises(ValueError):
        generate_luhn_id("4", length=5)


# ----------------------------------------
# Alphanumeric / Password / Token tests
# ----------------------------------------

def test_generate_alphanumeric():
    res = generate_alphanumeric(10, include_digits=True, include_letters=True)
    assert len(res) == 10
    assert res.isalnum()

    res_digits = generate_alphanumeric(10, include_digits=True, include_letters=False)
    assert len(res_digits) == 10
    assert res_digits.isdigit()

    res_letters = generate_alphanumeric(10, include_digits=False, include_letters=True)
    assert len(res_letters) == 10
    assert res_letters.isalpha()

    with pytest.raises(ValueError):
        generate_alphanumeric(10, include_digits=False, include_letters=False)

def test_generate_numeric():
    res = generate_numeric(8)
    assert len(res) == 8
    assert res.isdigit()

def test_generate_letters():
    res = generate_letters(8)
    assert len(res) == 8
    assert res.isalpha()

def test_generate_password():
    res = generate_password(length=12, include_digits=True, include_special=True)
    assert len(res) == 12
    # Ensure there is at least one digit
    assert any(c.isdigit() for c in res)
    # Ensure there is at least one special char
    special_chars = r"!@#$%^&*()-_=+[]{}|;:',.<>/?~`"
    assert any(c in special_chars for c in res)
    # Ensure there is at least one letter
    assert any(c.isalpha() for c in res)

    # Test error cases
    with pytest.raises(ValueError):
        generate_password(length=3)

def test_generate_token():
    res_hex = generate_token(16, encoding="hex")
    assert len(res_hex) == 16
    # Hex string matches regex [0-9a-fA-F]*
    assert all(c in "0123456789abcdefABCDEF" for c in res_hex)

    res_b64 = generate_token(24, encoding="base64")
    # Base64 url safe can be shorter due to stripping padding, but it should be close to 24 chars
    assert len(res_b64) > 15

    res_bytes = generate_token(16, encoding="bytes")
    assert len(res_bytes) == 32  # 16 bytes serialized to hex is 32 chars


