from __future__ import annotations

# Supported currency codes
SUPPORTED_CURRENCIES: set[str] = {"USD", "EUR", "GBP", "INR", "CAD", "JPY"}

# Mapping of currency code to its minor-unit scale (decimal places)
CURRENCY_SCALES: dict[str, int] = {
    "USD": 2,
    "EUR": 2,
    "GBP": 2,
    "INR": 2,
    "CAD": 2,
    "JPY": 0,
}
