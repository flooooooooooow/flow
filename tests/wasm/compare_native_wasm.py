from __future__ import annotations

import ctypes
import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "tests" / "fixtures" / "wasm" / "alloc_sum.flow"


def run(command: list[str], *, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def main() -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")

    with tempfile.TemporaryDirectory(prefix="flow_wasm_parity_") as temp_dir:
        temp = Path(temp_dir)
        native_ir = temp / "alloc_sum_native.ll"
        native_lib = temp / "liballoc_sum.so"
        wasm = temp / "alloc_sum.wasm"

        run(
            [
                sys.executable,
                "-m",
                "flow.transpiler",
                str(SOURCE),
                "--llvm",
                "-o",
                str(native_ir),
            ],
            env=env,
        )
        run(
            [
                "clang",
                "-shared",
                "-fPIC",
                "-O2",
                str(native_ir),
                "-o",
                str(native_lib),
                "-lm",
            ],
            env=env,
        )

        lib = ctypes.CDLL(str(native_lib))
        native_fn = lib.alloc_sum
        native_fn.argtypes = []
        native_fn.restype = ctypes.c_float
        native_result = float(native_fn())

        run(
            [
                sys.executable,
                "-m",
                "flow.wasm_compiler",
                str(SOURCE),
                "-o",
                str(wasm),
                "--export",
                "alloc_sum",
                "-O",
                "O2",
            ],
            env=env,
        )

        node = run(
            [
                "node",
                "--input-type=module",
                "-e",
                """
import fs from 'node:fs';
import {createFlowWasmRuntime} from './runtime/wasm/flow_runtime.mjs';
const bytes = fs.readFileSync(process.argv[1]);
const module = new WebAssembly.Module(bytes);
const runtime = createFlowWasmRuntime();
const instance = await WebAssembly.instantiate(module, runtime.imports);
runtime.attach(instance);
console.log(instance.exports.alloc_sum());
""",
                str(wasm),
            ],
            env=env,
        )
        wasm_result = float(node.stdout.strip().splitlines()[-1])

        if not math.isclose(native_result, wasm_result, rel_tol=0.0, abs_tol=1e-6):
            raise AssertionError(
                f"native MLIR result {native_result} != wasm result {wasm_result}"
            )

        print(
            json.dumps(
                {
                    "source": str(SOURCE.relative_to(ROOT)),
                    "native_mlir": native_result,
                    "wasm32": wasm_result,
                    "abs_error": abs(native_result - wasm_result),
                },
                sort_keys=True,
            )
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
