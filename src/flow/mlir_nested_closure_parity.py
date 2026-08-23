"""Recursive first-class-function captures for MLIR closures.

A closure environment may itself contain Flow function values.  Those fields
must use the canonical fat-closure ABI, not an incidental storage type carried
by the symbol entry.  Keep this normalization adjacent to the closure parity
layer so nested composition has exactly the same representation at every
level.
"""

from __future__ import annotations

from typing import Any, Dict, List

from . import mlir_closure_parity as _closure


_INSTALLED = False
_ORIGINAL_ALLOCATE_CAPTURE_ENV = None


def _capture_debug(
    capture_names: List[str], capture_infos: List[Dict[str, Any]]
) -> str:
    parts = []
    for name, info in zip(capture_names, capture_infos):
        flow_type = info.get("flow_type")
        parts.append(
            f"{name}:flow={getattr(flow_type, 'name', flow_type)!r},"
            f"mlir={info.get('mlir_type')!r}"
        )
    return "; ".join(parts)


def _allocate_capture_env_recursive(
    self, capture_names: List[str], capture_infos: List[Dict[str, Any]]
):
    # Function values are recursively representable: an environment field is
    # another {code_ptr, env_ptr} value.  Normalize both the per-lambda capture
    # metadata and the live symbol entry so generate_variable loads/stores the
    # same aggregate type that the environment declares.
    for name, info in zip(capture_names, capture_infos):
        flow_type = info.get("flow_type")
        if not _closure._is_flow_fn_type(flow_type):
            continue

        info["mlir_type"] = _closure.CLOSURE_MLIR_TYPE
        symbol = self.symbol_table.get(name)
        if isinstance(symbol, dict) and _closure._is_flow_fn_type(
            symbol.get("flow_type")
        ):
            symbol["mlir_type"] = _closure.CLOSURE_MLIR_TYPE

    try:
        return _ORIGINAL_ALLOCATE_CAPTURE_ENV(self, capture_names, capture_infos)
    except NotImplementedError as exc:
        raise NotImplementedError(
            f"{exc}; captures: {_capture_debug(capture_names, capture_infos)}"
        ) from exc


def install() -> None:
    """Install recursive closure-environment normalization once."""
    global _INSTALLED
    global _ORIGINAL_ALLOCATE_CAPTURE_ENV

    if _INSTALLED:
        return

    _ORIGINAL_ALLOCATE_CAPTURE_ENV = _closure._allocate_capture_env
    _closure._allocate_capture_env = _allocate_capture_env_recursive
    _INSTALLED = True
