"""
Shared pytest configuration for the Python tests that remain.

These tests drive ./flow, the scripts and the Flow tools as subprocesses.
None imports the compiler, which is flowc (compiler/src).
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Set


_REPO_ROOT = Path(__file__).resolve().parent.parent
_TRACKED_TEST_FILES: Optional[Set[str]] = None


def _tracked_test_files() -> Set[str]:
    global _TRACKED_TEST_FILES
    if _TRACKED_TEST_FILES is None:
        try:
            out = subprocess.check_output(
                ["git", "-C", str(_REPO_ROOT), "ls-files", "tests"],
                text=True,
            )
            _TRACKED_TEST_FILES = {
                line for line in out.splitlines() if line.endswith(".py")
            }
        except Exception:
            _TRACKED_TEST_FILES = set()
    return _TRACKED_TEST_FILES


def pytest_ignore_collect(collection_path, config):
    """Match CI: only collect git-tracked tests unless FLOW_PYTEST_ALL=1."""
    if os.environ.get("FLOW_PYTEST_ALL") == "1":
        return False
    path = Path(str(collection_path))
    if not path.is_file() or path.suffix != ".py":
        return False
    try:
        rel = path.relative_to(_REPO_ROOT).as_posix()
    except ValueError:
        return False
    if not rel.startswith("tests/"):
        return False
    return rel not in _tracked_test_files()
