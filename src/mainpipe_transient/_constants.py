"""Physical constants of the calculation (U-40, plan 01 §1.2; SCHEMA_VERSION 2.0).

Since the 2.0 contract the water density and the gravity are not inputs: every result uses
these values. Private: not exported from the package.
"""

from __future__ import annotations

__all__ = ["DENSITY_KGM3", "GRAVITY_MS2"]

DENSITY_KGM3 = 1000.0  # water density rho (kg/m3)
GRAVITY_MS2 = 9.81  # gravity g (m/s2)
