"""Number formatting for user-facing messages (plan 01 U-26).

Always a decimal point, ASCII minus sign. Heads and pressure heads with one fixed
decimal; x up to 1 decimal and t up to 3 decimals without trailing zeros; PN up to
1 decimal. Echoed input values use up to 10 significant digits.
"""

from __future__ import annotations

import math

__all__ = [
    "fmt_fixed",
    "fmt_trim",
    "fmt_head",
    "fmt_x",
    "fmt_time",
    "fmt_pn",
    "fmt_value",
    "floor_decimals",
    "ceil_decimals",
]

_TIME_DECIMALS = 3


def _clean_zero(text: str) -> str:
    return "0" if text in ("-0", "-0.0") else text


def fmt_fixed(value: float, decimals: int) -> str:
    """Fixed number of decimals (``-0.0`` printed as ``0.0``)."""
    text = f"{value:.{decimals}f}"
    if float(text) == 0.0:
        text = f"{0.0:.{decimals}f}"
    return text


def fmt_trim(value: float, max_decimals: int) -> str:
    """Up to ``max_decimals`` decimals, trailing zeros and dot removed."""
    text = f"{value:.{max_decimals}f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return _clean_zero(text)


def fmt_head(value: float) -> str:
    return fmt_fixed(value, 1)


def fmt_x(value: float) -> str:
    return fmt_trim(value, 1)


def fmt_time(value: float) -> str:
    return fmt_trim(value, _TIME_DECIMALS)


def fmt_pn(value: float) -> str:
    return fmt_trim(value, 1)


def fmt_value(value: float) -> str:
    """Echo of an input value: up to 10 significant digits, no exponent for usual magnitudes."""
    text = f"{value:.10g}"
    if "e" in text:
        return text
    return _clean_zero(text)


def floor_decimals(value: float, decimals: int = _TIME_DECIMALS) -> float:
    """Truncate toward -inf to ``decimals`` decimals, tolerant to binary noise just below."""
    scale = 10**decimals
    return math.floor(value * scale + 1e-6) / scale


def ceil_decimals(value: float, decimals: int = _TIME_DECIMALS) -> float:
    """Round up to ``decimals`` decimals, tolerant to binary noise just above."""
    scale = 10**decimals
    return math.ceil(value * scale - 1e-6) / scale
