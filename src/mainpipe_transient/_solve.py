"""Orchestration of :func:`solve` (plan 01 §1.1).

Phase 0 only fixes the public signature. Validation, the MOC engine and the error
wrapper arrive in phases 1 and 2.
"""

from __future__ import annotations

import logging
from typing import Any

from .exceptions import MainpipeTransientComputationError

logger = logging.getLogger("mainpipe_transient")

__all__ = ["solve"]


def solve(data: dict[str, Any]) -> dict[str, Any]:
    """Compute the water-hammer transient for one reservoir-pipe-valve case.

    Placeholder (phase 0): always raises :class:`MainpipeTransientComputationError`.
    """
    logger.debug("solve called before the engine is implemented")
    raise MainpipeTransientComputationError(
        "El motor de cálculo aún no está disponible en esta versión del paquete."
    )
