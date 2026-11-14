"""Exception hierarchy of ``mainpipe_transient`` (kit 02 §1, plan 01 §1.6).

Every exception the package raises derives from :class:`MainpipeTransientError` and
carries the HTTP status the portal router maps it to. Messages are user-facing and
therefore written in Spanish (kit 01 §5, kit 02 §3).

There is no ``MainpipeTransientServiceError``: the package calls no external service.
"""

from __future__ import annotations

__all__ = [
    "MainpipeTransientError",
    "MainpipeTransientValidationError",
    "MainpipeTransientComputationError",
]


class MainpipeTransientError(Exception):
    """Base class. Everything the package raises derives from it."""

    http_status: int = 500


class MainpipeTransientValidationError(MainpipeTransientError, ValueError):
    """Invalid input, or an input with no physical solution."""

    http_status = 422


class MainpipeTransientComputationError(MainpipeTransientError):
    """Internal computation failure; should not happen with valid input."""

    http_status = 500
