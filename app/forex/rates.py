from __future__ import annotations

from decimal import Decimal

from app.common.settings import SUPPORTED_CURRENCIES

# Global dictionary of exchange rates: (from_currency, to_currency) -> rate (Decimal)
EXCHANGE_RATES: dict[tuple[str, str], Decimal] = {}


def add_exchange_rate(
    from_currency: str,
    to_currency: str,
    rate: Decimal | str | float | int,
) -> None:
    """Register/add an exchange rate to the global configuration.

    The rate should convert major-to-major units (e.g. 1 USD = 1.35 CAD).
    """
    from_code = from_currency.upper()
    to_code = to_currency.upper()

    if from_code not in SUPPORTED_CURRENCIES:
        raise ValueError(f"Unsupported source currency: {from_code}")
    if to_code not in SUPPORTED_CURRENCIES:
        raise ValueError(f"Unsupported target currency: {to_code}")

    dec_rate = Decimal(str(rate))
    if dec_rate <= 0:
        raise ValueError("Exchange rate must be positive.")

    EXCHANGE_RATES[(from_code, to_code)] = dec_rate


def get_exchange_rate(from_currency: str, to_currency: str) -> Decimal:
    """Retrieve the exchange rate between two currencies.

    If a direct rate is not registered, fallback to the mathematical inverse of the rate.
    Returns Decimal('1.0') if both currencies are identical.
    """
    from_code = from_currency.upper()
    to_code = to_currency.upper()

    if from_code == to_code:
        return Decimal("1.0")

    # 1. Direct rate
    if (from_code, to_code) in EXCHANGE_RATES:
        return EXCHANGE_RATES[(from_code, to_code)]

    # 2. Inverse rate
    if (to_code, from_code) in EXCHANGE_RATES:
        return Decimal("1.0") / EXCHANGE_RATES[(to_code, from_code)]

    raise ValueError(
        f"No exchange rate configured for {from_code} -> {to_code}"
    )
