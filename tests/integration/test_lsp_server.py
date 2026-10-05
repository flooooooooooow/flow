"""Pytest wrapper around the scripted LSP JSON-RPC harness.

Keeps the editor-less LSP suite in the same discovery path as other
integration tests (`./flow test-python` / CI pytest).
"""

import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "test_lsp_server.py"


def test_lsp_scripted_harness_passes():
    assert SCRIPT.is_file(), f"missing {SCRIPT}"
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.fail(
            "LSP harness failed\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
