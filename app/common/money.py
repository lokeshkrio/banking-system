from __future__ import annotations

from dataclasses import dataclass
from decimal import (
    ROUND_FLOOR,
    ROUND_HALF_EVEN,
    Decimal,
)
from typing import Self

from app.common.settings import CURRENCY_SCALES, SUPPORTED_CURRENCIES


@dataclass(frozen=True, slots=True)
class Money:
    """
    Immutable monetary value object.

    Amounts are stored in minor units:
        USD 12.34 -> 1234
        INR 99.50 -> 9950
        JPY 100   -> 100
    """

    amount_minor: int
    currency_code: str

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:
        if not isinstance(self.amount_minor, int):
            raise TypeError("amount_minor must be an integer.")

        if not isinstance(self.currency_code, str):
            raise TypeError("currency_code must be a string.")

        code = self.currency_code.upper()

        if code not in SUPPORTED_CURRENCIES:
            raise ValueError(
                f"Unsupported currency: {code}. Must be one of {SUPPORTED_CURRENCIES}"
            )

        object.__setattr__(self, "currency_code", code)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _assert_money(self, other: object) -> Money:
        if not isinstance(other, Money):
            raise TypeError(f"Expected Money, got {type(other).__name__}")
        return other

    def _assert_same_currency(
        self,
        other: object,
    ) -> Money:
        other = self._assert_money(other)

        if self.currency_code != other.currency_code:
            raise ValueError(
                f"Currency mismatch: "
                f"{self.currency_code} "
                f"vs "
                f"{other.currency_code}"
            )

        return other

    # ------------------------------------------------------------------
    # Arithmetic
    # ------------------------------------------------------------------

    def __add__(self, other: object) -> Money:
        other = self._assert_same_currency(other)

        return Money(
            self.amount_minor + other.amount_minor,
            self.currency_code,
        )

    def __sub__(self, other: object) -> Money:
        other = self._assert_same_currency(other)

        return Money(
            self.amount_minor - other.amount_minor,
            self.currency_code,
        )

    def __neg__(self) -> Money:
        return Money(
            -self.amount_minor,
            self.currency_code,
        )

    def __abs__(self) -> Money:
        return Money(
            abs(self.amount_minor),
            self.currency_code,
        )

    def __mul__(self, factor: int) -> Money:
        if not isinstance(factor, int):
            raise TypeError("Money can only be multiplied by integers.")

        return Money(
            self.amount_minor * factor,
            self.currency_code,
        )

    def __rmul__(self, factor: int) -> Money:
        return self * factor

    def __truediv__(self, divisor: object) -> Money | Decimal:
        if isinstance(divisor, Money):
            other = self._assert_same_currency(divisor)
            if other.amount_minor == 0:
                raise ZeroDivisionError("Division by zero.")
            return Decimal(self.amount_minor) / Decimal(other.amount_minor)

        if not isinstance(divisor, (int, Decimal)):
            raise TypeError(
                "Money can only be divided by integers, Decimals, or Money of the same currency."
            )
        if divisor == 0:
            raise ZeroDivisionError("Division by zero.")

        result = Decimal(self.amount_minor) / Decimal(divisor)
        rounded = int(result.to_integral_value(rounding=ROUND_HALF_EVEN))
        return Money(rounded, self.currency_code)

    # ------------------------------------------------------------------
    # Comparison
    # ------------------------------------------------------------------

    def __lt__(self, other: object) -> bool:
        other = self._assert_same_currency(other)
        return self.amount_minor < other.amount_minor

    def __le__(self, other: object) -> bool:
        other = self._assert_same_currency(other)
        return self.amount_minor <= other.amount_minor

    def __gt__(self, other: object) -> bool:
        other = self._assert_same_currency(other)
        return self.amount_minor > other.amount_minor

    def __ge__(self, other: object) -> bool:
        other = self._assert_same_currency(other)
        return self.amount_minor >= other.amount_minor

    # ------------------------------------------------------------------
    # Predicates
    # ------------------------------------------------------------------

    @property
    def is_zero(self) -> bool:
        return self.amount_minor == 0

    @property
    def is_positive(self) -> bool:
        return self.amount_minor > 0

    @property
    def is_negative(self) -> bool:
        return self.amount_minor < 0

    # ------------------------------------------------------------------
    # Factories
    # ------------------------------------------------------------------

    @classmethod
    def zero(
        cls,
        currency_code: str,
    ) -> Self:
        return cls(
            0,
            currency_code,
        )

    @classmethod
    def from_major(
        cls,
        amount: str | Decimal,
        currency_code: str,
        *,
        scale: int | None = None,
    ) -> Self:
        """
        Example:
            Money.from_major("12.34", "USD")
        """
        if scale is None:
            scale = CURRENCY_SCALES.get(currency_code.upper(), 2)

        d = Decimal(str(amount))

        quant = Decimal("1." + ("0" * scale)) if scale > 0 else Decimal("1")

        d = d.quantize(
            quant,
            rounding=ROUND_HALF_EVEN,
        )

        minor = int(d * (10**scale))

        return cls(
            minor,
            currency_code,
        )

    # ------------------------------------------------------------------
    # Conversion
    # ------------------------------------------------------------------

    def to_major(
        self,
        *,
        scale: int | None = None,
    ) -> Decimal:
        if scale is None:
            scale = CURRENCY_SCALES.get(self.currency_code, 2)
        return Decimal(self.amount_minor) / Decimal(10**scale)

    def convert(
        self,
        target_currency: str,
        rate: Decimal | str | float | int | None = None,
    ) -> Money:
        """Convert this Money instance to another currency using major-to-major rates.

        If rate is not provided, queries the settings configuration rates.
        The conversion automatically handles differing currency scales.
        """
        target_currency = target_currency.upper()
        if target_currency not in SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported target currency: {target_currency}")

        if rate is None:
            from app.forex.rates import get_exchange_rate

            rate = get_exchange_rate(self.currency_code, target_currency)

        dec_rate = Decimal(str(rate))
        if dec_rate <= 0:
            raise ValueError("rate must be positive.")

        source_major = self.to_major()
        target_major = source_major * dec_rate

        target_scale = CURRENCY_SCALES.get(target_currency, 2)
        quant = (
            Decimal("1." + ("0" * target_scale)) if target_scale > 0 else Decimal("1")
        )

        target_major_rounded = target_major.quantize(quant, rounding=ROUND_FLOOR)
        target_minor = int(target_major_rounded * (10**target_scale))

        return Money(target_minor, target_currency)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, int | str]:
        return {
            "amount_minor": self.amount_minor,
            "currency": self.currency_code,
        }

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        major = self.to_major()

        return f"{self.currency_code} " f"{major:,.2f}"

    def __repr__(self) -> str:
        return (
            f"Money("
            f"amount_minor={self.amount_minor}, "
            f"currency_code='{self.currency_code}'"
            f")"
        )
