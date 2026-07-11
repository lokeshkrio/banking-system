from decimal import Decimal

import pytest

from app.common.money import Money
from app.forex.rates import EXCHANGE_RATES, add_exchange_rate, get_exchange_rate


def test_money_creation_and_validation() -> None:
    # Valid creation
    m = Money(1234, "USD")
    assert m.amount_minor == 1234
    assert m.currency_code == "USD"

    # Lowercase currency code normalization
    m2 = Money(9950, "inr")
    assert m2.currency_code == "INR"

    # Invalid amount type
    with pytest.raises(TypeError):
        Money(12.34, "USD")  # type: ignore

    # Invalid currency type
    with pytest.raises(TypeError):
        Money(100, 123)  # type: ignore

    # Invalid currency format
    with pytest.raises(ValueError):
        Money(100, "US")
    with pytest.raises(ValueError):
        Money(100, "US1")


def test_money_from_and_to_major() -> None:
    # Standard scale 2
    m1 = Money.from_major("12.34", "USD")
    assert m1.amount_minor == 1234
    assert m1.to_major() == Decimal("12.34")

    # JPY scale 0
    m2 = Money.from_major("1500", "JPY")
    assert m2.amount_minor == 1500
    assert m2.to_major() == Decimal("1500")

    # Bankers rounding on from_major
    m3 = Money.from_major("12.345", "USD")  # ROUND_HALF_EVEN
    assert m3.amount_minor == 1234

    m4 = Money.from_major("12.355", "USD")
    assert m4.amount_minor == 1236

    # Custom scale override
    m5 = Money.from_major("12.3456", "USD", scale=4)
    assert m5.amount_minor == 123456
    assert m5.to_major(scale=4) == Decimal("12.3456")


def test_money_arithmetic() -> None:
    m1 = Money(1000, "USD")
    m2 = Money(500, "USD")

    # Addition
    assert (m1 + m2) == Money(1500, "USD")

    # Subtraction
    assert (m1 - m2) == Money(500, "USD")

    # Negation
    assert -m1 == Money(-1000, "USD")

    # Absolute value
    assert abs(-m1) == Money(1000, "USD")

    # Multiplication
    assert m1 * 3 == Money(3000, "USD")
    assert 2 * m2 == Money(1000, "USD")

    # Invalid multiplication type
    with pytest.raises(TypeError):
        m1 * 2.5  # type: ignore

    # Currency mismatch
    m_inr = Money(1000, "INR")
    with pytest.raises(ValueError):
        m1 + m_inr


def test_money_division() -> None:
    m1 = Money(1000, "USD")

    # Division by int
    assert m1 / 3 == Money(333, "USD")  # ROUND_HALF_EVEN: 333.333 -> 333

    # Division by Decimal
    assert m1 / Decimal("2.5") == Money(400, "USD")

    # Division by another Money (same currency)
    m2 = Money(250, "USD")
    assert m1 / m2 == Decimal("4")

    # Division by zero
    with pytest.raises(ZeroDivisionError):
        m1 / 0
    with pytest.raises(ZeroDivisionError):
        m1 / Money(0, "USD")

    # Division with mismatched currency
    with pytest.raises(ValueError):
        m1 / Money(100, "INR")

    # Invalid divisor type
    with pytest.raises(TypeError):
        m1 / "two"


def test_money_comparison() -> None:
    m1 = Money(100, "USD")
    m2 = Money(200, "USD")
    m3 = Money(100, "USD")

    assert m1 < m2
    assert m1 <= m2
    assert m1 <= m3
    assert m2 > m1
    assert m2 >= m1
    assert m1 >= m3
    assert m1 == m3
    assert m1 != m2

    # Mismatched currency comparisons should raise ValueError
    m_inr = Money(100, "INR")
    with pytest.raises(ValueError):
        _ = m1 < m_inr


def test_money_predicates() -> None:
    assert Money(0, "USD").is_zero is True
    assert Money(1, "USD").is_zero is False

    assert Money(100, "USD").is_positive is True
    assert Money(0, "USD").is_positive is False
    assert Money(-100, "USD").is_positive is False

    assert Money(-100, "USD").is_negative is True
    assert Money(0, "USD").is_negative is False


def test_money_serialization_and_display() -> None:
    m = Money(1234, "USD")

    assert m.to_dict() == {"amount_minor": 1234, "currency": "USD"}
    assert str(m) == "USD 12.34"
    assert repr(m) == "Money(amount_minor=1234, currency_code='USD')"


def test_settings_exchange_rates() -> None:
    # Clear global rates for testing
    EXCHANGE_RATES.clear()

    # Register/add rate
    add_exchange_rate("USD", "EUR", "0.90")
    assert get_exchange_rate("USD", "EUR") == Decimal("0.90")

    # Inverse fallback
    assert get_exchange_rate("EUR", "USD") == Decimal("1.0") / Decimal("0.90")

    # Same currency
    assert get_exchange_rate("USD", "USD") == Decimal("1.0")

    # Unregistered rate
    with pytest.raises(ValueError):
        get_exchange_rate("USD", "INR")

    # Invalid source/target currencies
    with pytest.raises(ValueError):
        add_exchange_rate("US", "EUR", 1.0)
    with pytest.raises(ValueError):
        add_exchange_rate("USD", "EUR", -0.5)


def test_money_conversion() -> None:
    # Clear global rates for testing
    EXCHANGE_RATES.clear()

    # Scale 2 to Scale 2 conversion
    m_usd = Money(1000, "USD")  # 10.00 USD
    # Explicit rate (major-to-major)
    m_eur = m_usd.convert("EUR", rate=Decimal("0.90"))
    assert m_eur.currency_code == "EUR"
    assert m_eur.amount_minor == 900  # 9.00 EUR

    # Scale 2 to Scale 0 conversion (e.g. USD to JPY)
    # 10.00 USD * 150 = 1500 JPY
    m_jpy = m_usd.convert("JPY", rate=Decimal("150"))
    assert m_jpy.currency_code == "JPY"
    assert m_jpy.amount_minor == 1500

    # Scale 0 to Scale 2 conversion (e.g. JPY to USD)
    # 1500 JPY * 0.0067 = 10.05 USD
    m_jpy_base = Money(1500, "JPY")
    m_usd_back = m_jpy_base.convert("USD", rate=Decimal("0.0067"))
    assert m_usd_back.currency_code == "USD"
    assert m_usd_back.amount_minor == 1005  # 10.05 USD

    # Test conversion using default registry settings
    add_exchange_rate("USD", "INR", "83.50")
    m_inr = m_usd.convert("INR")
    assert m_inr.currency_code == "INR"
    assert m_inr.amount_minor == 83500  # 835.00 INR
