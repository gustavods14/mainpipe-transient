"""Test oracle for the output precision of the 2.0 contract (U-39, D-63; plan 01 §1.4, §6).

Written independently of the package: the tests compare ``solve()`` against this rule, not
against the package's own helper.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np

HALF_MM = 0.0005  # m (or L/s): a rounded list against an unrounded reference (plan 01 §6)
DIFF_TOL = 0.001 + 1e-9  # m: a difference of rounded lists against a rounded list (U-42 (2))


def r3(value: float) -> float:
    """Rounding rule of U-39 (4): Python ``round(x, 3)``, without ``-0.0``."""
    return round(float(value), 3) + 0.0


def r3_list(values: Iterable[float]) -> list[float]:
    return [r3(v) for v in np.asarray(values, dtype=float).ravel()]


def is_rounded(values: Iterable[float]) -> bool:
    """Every value equals its own 3-decimal rounding and none is ``-0.0`` (V-19)."""
    flat = np.asarray(values, dtype=float).ravel().tolist()
    return all(v == r3(v) and not (v == 0.0 and np.signbit(v)) for v in flat)
