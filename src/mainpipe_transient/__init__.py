"""Water hammer by valve closure in a gravity main, solved with the Method of Characteristics.

Public API (kit 01 §3, plan 01 §1.1). Everything not listed in ``__all__`` is private.
Importing the package computes nothing and touches neither disk nor network.
"""

from importlib.metadata import PackageNotFoundError, version

from ._solve import solve
from .exceptions import (
    MainpipeTransientComputationError,
    MainpipeTransientError,
    MainpipeTransientValidationError,
)
from .schemas import SCHEMA_VERSION, Check, SolveRequest, SolveResponse

try:
    __version__ = version("mainpipe-transient")
except PackageNotFoundError:  # pragma: no cover - only when run from an uninstalled tree
    __version__ = "unknown"

__all__ = [
    "solve",
    "SolveRequest",
    "SolveResponse",
    "Check",
    "MainpipeTransientError",
    "MainpipeTransientValidationError",
    "MainpipeTransientComputationError",
    "__version__",
    "SCHEMA_VERSION",
]
