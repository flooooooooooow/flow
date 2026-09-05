#!/usr/bin/env python3
"""Emit WebGPU WGSL from Flow ``shader fill`` source."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from flow.shader_codegen_wgsl import compile_shader_file_wgsl


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="Flow file containing one or more shader fill blocks")
    parser.add_argument("--out", default="build/wgsl", help="output directory")
    parser.add_argument("--name", help="emit only one named fill shader")
    args = parser.parse_args()

    output = compile_shader_file_wgsl(args.source, args.out, shader_name=args.name)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
