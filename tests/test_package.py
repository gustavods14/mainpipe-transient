"""Phase 0: package shape, public API, exceptions and import purity (kit 01 §2-3, kit 02 §1)."""

from __future__ import annotations

import importlib.metadata
import importlib.resources
import re
import subprocess
import sys
from pathlib import Path

import pytest

import mainpipe_transient as mpt
from mainpipe_transient import (
    MainpipeTransientComputationError,
    MainpipeTransientError,
    MainpipeTransientValidationError,
)

REPO = Path(__file__).resolve().parents[1]


def test_public_api():
    assert set(mpt.__all__) == {
        "solve",
        "SolveRequest",
        "SolveResponse",
        "Check",
        "MainpipeTransientError",
        "MainpipeTransientValidationError",
        "MainpipeTransientComputationError",
        "__version__",
        "SCHEMA_VERSION",
    }
    for name in mpt.__all__:
        assert hasattr(mpt, name), name


def test_schema_version_is_frozen_contract():
    assert mpt.SCHEMA_VERSION == "1.0"
    assert isinstance(mpt.SCHEMA_VERSION, str)


def test_version_comes_from_distribution_metadata():
    assert mpt.__version__ == importlib.metadata.version("mainpipe-transient")


def test_py_typed_is_shipped():
    assert importlib.resources.files("mainpipe_transient").joinpath("py.typed").is_file()


def test_exception_hierarchy_and_http_status():
    assert issubclass(MainpipeTransientValidationError, MainpipeTransientError)
    assert issubclass(MainpipeTransientValidationError, ValueError)
    assert issubclass(MainpipeTransientComputationError, MainpipeTransientError)
    assert MainpipeTransientError.http_status == 500
    assert MainpipeTransientValidationError.http_status == 422
    assert MainpipeTransientComputationError.http_status == 500
    # No external service (plan 01 §1.6).
    assert not hasattr(mpt, "MainpipeTransientServiceError")


def test_solve_rejects_empty_input_with_package_error():
    with pytest.raises(MainpipeTransientError) as info:
        mpt.solve({})
    assert info.value.http_status == 422
    assert isinstance(info.value, MainpipeTransientValidationError)


def test_import_has_no_side_effects(tmp_path):
    """Importing prints nothing, writes nothing and pulls no dev-only module."""
    code = (
        "import sys, mainpipe_transient\n"
        "bad = [m for m in ('win32com', 'pywintypes', 'openpyxl') if m in sys.modules]\n"
        "assert not bad, bad\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=tmp_path, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert result.stderr == ""
    assert list(tmp_path.iterdir()) == []


def test_dev_only_tools_are_not_imported_by_src_or_tests():
    """U-27: openpyxl and pywin32 never imported from src/ or tests/."""
    pattern = re.compile(r"^\s*(import|from)\s+(win32\w*|pywintypes|pythoncom|openpyxl)\b", re.M)
    offenders = [
        p.relative_to(REPO).as_posix()
        for folder in ("src", "tests")
        for p in (REPO / folder).rglob("*.py")
        if pattern.search(p.read_text(encoding="utf-8"))
    ]
    assert offenders == []


def test_no_print_in_package():
    """kit 01 §6: no print in the package."""
    pattern = re.compile(r"\bprint\s*\(")
    offenders = [
        p.relative_to(REPO).as_posix()
        for p in (REPO / "src").rglob("*.py")
        if pattern.search(p.read_text(encoding="utf-8"))
    ]
    assert offenders == []
