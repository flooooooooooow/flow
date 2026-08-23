"""Correctness guards for the legacy Python dynamics DSL expander.

Keep these fixes isolated while the Python expander is being retired in favour
of the self-hosted compiler.  Importing this module does not install anything;
call :func:`install` from the package initialiser.
"""

from __future__ import annotations

import re

from . import dynamics_dsl as _dsl

_INSTALLED = False
_ORIGINAL_PARSE_DYNAMICS_DSL = _dsl.parse_dynamics_dsl


def _validate_raw_dsys(program: _dsl.DynamicsProgram) -> None:
    """Reject malformed raw ``dsys`` declarations before code generation."""
    synthesized = {f"{rep.flow_name}_lin" for rep in program.represents}

    for name, decl in program.systems.items():
        if name in synthesized:
            continue

        for dim_name, value in (("n", decl.n), ("m", decl.m), ("p", decl.p)):
            if value <= 0:
                raise SyntaxError(
                    f"dsys '{name}': {dim_name} must be positive, got {value}"
                )

        expected = (
            ("A", decl.n * decl.n, len(decl.A), f"n = {decl.n}"),
            ("B", decl.n * decl.m, len(decl.B), f"n = {decl.n}, m = {decl.m}"),
            ("C", decl.p * decl.n, len(decl.C), f"p = {decl.p}, n = {decl.n}"),
        )
        for matrix, want, got, dimensions in expected:
            if got != want:
                raise SyntaxError(
                    f"dsys '{name}': {matrix} needs {want} entries for "
                    f"{dimensions}, got {got}"
                )


def _parse_dynamics_dsl(source: str):
    program, stripped = _ORIGINAL_PARSE_DYNAMICS_DSL(source)
    _validate_raw_dsys(program)
    return program, stripped


def _inject_dynamics_setup(flow_source: str, setup: str) -> str:
    """Insert generated setup without gluing it to a one-line ``main`` body."""
    if not setup.strip():
        return flow_source

    marker = re.search(
        r"function\s+main\s*\([^)]*\)\s*->\s*\w+\s*\{", flow_source
    )
    if not marker:
        return (
            flow_source
            + "\n\nfunction main() -> i32 {\n"
            + setup
            + "\n    return 0\n}\n"
        )

    insert_at = marker.end()
    return flow_source[:insert_at] + "\n" + setup + "\n" + flow_source[insert_at:]


def install() -> None:
    global _INSTALLED
    if _INSTALLED:
        return

    _dsl.parse_dynamics_dsl = _parse_dynamics_dsl
    _dsl.inject_dynamics_setup = _inject_dynamics_setup
    _INSTALLED = True
