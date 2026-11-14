"""Shared fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
REFERENCE_JSON = REPO / "tests" / "reference" / "excel_case.json"
ARCHIVED_XLSX = REPO / "doc" / "archive" / "2026-11-pre-hie" / "Transitorio_MOC_Animado.xlsx"


@pytest.fixture(scope="session")
def excel_reference() -> dict:
    """Frozen Excel reference (U-28). Tests only ever read this JSON."""
    return json.loads(REFERENCE_JSON.read_text(encoding="utf-8"))
