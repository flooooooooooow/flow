#!/usr/bin/env python3
"""Emit the denotational MLIR for the `flow` blocks in a Flow source file.

Standalone entry point for the denotational MLIR lane (see
docs/design/denotational-mlir.md). It reads a `.flow` file, finds every `flow`
evolution block, and prints its `flow.system` dialect. With `--ensemble N` it
prints the fused, vectorized `flow.ensemble` step for N instances instead.

This does not touch the compile pipeline (`src/flow/mlir_generator.py`), so it
works today while that file is under active edit. Wiring the emitter into the
pipeline is the remaining slice.

Usage:
    python scripts/emit_denotational_mlir.py FILE.flow
    python scripts/emit_denotational_mlir.py FILE.flow --ensemble 1000
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from flow.denotational_mlir import (  # noqa: E402
    raw_flow_decls,
    emit_denotational_mlir,
    emit_ensemble_step,
)


def render(source: str, ensemble: int | None) -> str:
    """Return the denotational MLIR for every flow block in `source`."""
    blocks = raw_flow_decls(source)
    if not blocks:
        return "// no flow blocks found"
    out = []
    for flow in blocks:
        if ensemble is not None:
            out.append(emit_ensemble_step(flow, ensemble))
        else:
            out.append(emit_denotational_mlir(flow))
    return "\n\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file", help="Flow source file")
    parser.add_argument(
        "--ensemble",
        type=int,
        metavar="N",
        help="Emit the fused vectorized step for N instances instead",
    )
    args = parser.parse_args(argv)

    if args.ensemble is not None and args.ensemble < 1:
        parser.error("--ensemble N requires N >= 1")

    source = Path(args.file).read_text()
    print(render(source, args.ensemble))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
