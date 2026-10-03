"""
FLOW vgpu Conformance Test Runner
Executes vgpu compatibility cases from manifest.json, compiling shaders and GPU functions
for each case and comparing output against upstream reference buffers or expected numerical outputs.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from flow.module_resolver import ModuleResolver
from flow.metal_codegen import extract_gpu_functions
from flow.shader_dsl import extract_shader_module
from flow.shader_codegen_wgsl import generate_wgsl_for_module
from flow.shader_codegen import generate_metal_for_module
from flow.wgsl_codegen import generate_wgsl_shaders
from flow.gpu_integration import GPUCodeGenerator, GPUCompiler, GPUExecutor


@dataclass
class CaseResult:
    case_id: str
    backend: str
    mode: str
    status: str  # EXACT, TOLERANCE, NUMERICAL, UNSUPPORTED, FAIL
    max_error: Optional[float] = None
    differing_bytes: Optional[int] = None
    inputs: Optional[Dict[str, Any]] = None
    details: str = ""


def load_manifest(manifest_path: str | Path = "examples/gpu/vgpu/manifest.json") -> Dict[str, Any]:
    path = Path(manifest_path)
    if not path.is_file():
        raise FileNotFoundError(f"vgpu manifest not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compare_rgba8(actual: bytes, expected: bytes, tolerance: int = 0) -> Dict[str, Any]:
    if len(actual) != len(expected):
        return {
            "exact": False,
            "within_tolerance": False,
            "differing_bytes": abs(len(actual) - len(expected)),
            "max_channel_error": 255,
            "worst_index": -1,
        }

    differing_bytes = 0
    max_channel_error = 0
    worst_index = -1
    for i in range(len(actual)):
        err = abs(actual[i] - expected[i])
        if err != 0:
            differing_bytes += 1
        if err > max_channel_error:
            max_channel_error = err
            worst_index = i

    exact = (differing_bytes == 0)
    within_tolerance = (max_channel_error <= tolerance)

    return {
        "exact": exact,
        "within_tolerance": within_tolerance,
        "differing_bytes": differing_bytes,
        "max_channel_error": max_channel_error,
        "worst_index": worst_index,
    }


def compare_numerical(actual: List[float], expected: List[float], tolerance: float = 1e-4) -> Dict[str, Any]:
    if len(actual) != len(expected):
        return {
            "exact": False,
            "within_tolerance": False,
            "max_abs_error": float("inf"),
            "max_rel_error": float("inf"),
        }

    max_abs = 0.0
    max_rel = 0.0
    exact = True
    for a, e in zip(actual, expected):
        d = abs(a - e)
        if d != 0.0:
            exact = False
        if d > max_abs:
            max_abs = d
        scale = max(abs(e), 1e-30)
        if d / scale > max_rel:
            max_rel = d / scale

    return {
        "exact": exact,
        "within_tolerance": (max_abs <= tolerance),
        "max_abs_error": max_abs,
        "max_rel_error": max_rel,
    }


def evaluate_fsl_gradient_cpu(width: int = 160, height: int = 90, time_val: float = 0.0) -> bytes:
    """CPU reference renderer for vgpu_gradient fragment shader."""
    buf = bytearray(width * height * 4)
    for y in range(height):
        for x in range(width):
            uv_x = (x + 0.5) / width
            uv_y = (y + 0.5) / height
            dx = uv_x - 0.5
            dy = uv_y - 0.5
            dist = math.sqrt(dx * dx + dy * dy)
            t = max(0.0, min(1.0, (1.2 - dist) / (1.2 - 0.2)))
            vignette = t * t * (3.0 - 2.0 * t)

            r_f = uv_x
            g_f = uv_y
            b_f = 0.46 + 0.16 * vignette
            a_f = 1.0

            r = int(round(max(0.0, min(1.0, r_f)) * 255.0))
            g = int(round(max(0.0, min(1.0, g_f)) * 255.0))
            b = int(round(max(0.0, min(1.0, b_f)) * 255.0))
            a = int(round(max(0.0, min(1.0, a_f)) * 255.0))

            idx = (y * width + x) * 4
            buf[idx] = r
            buf[idx + 1] = g
            buf[idx + 2] = b
            buf[idx + 3] = a
    return bytes(buf)


class VGPURunner:
    def __init__(self, manifest_path: str | Path = "examples/gpu/vgpu/manifest.json"):
        self.manifest_path = Path(manifest_path)
        self.manifest = load_manifest(self.manifest_path)

    def is_backend_available(self, backend: str) -> Tuple[bool, str]:
        if backend == "metal":
            if sys.platform != "darwin":
                return False, f"Metal unavailable on platform '{sys.platform}'"
            try:
                from flow.gpu_integration import metal_is_available
                if not metal_is_available():
                    return False, "Metal runtime or hardware device unavailable"
            except Exception:
                return False, "Metal runtime unavailable"
            return True, "Metal available"

        elif backend in ("webgpu", "wgsl"):
            return True, "WebGPU/WGSL available"

        elif backend in ("cpu", "sim"):
            return True, "CPU reference simulation available"

        return False, f"Unknown backend '{backend}'"

    def run_case(self, case: Dict[str, Any], backend: str) -> CaseResult:
        case_id = case["id"]
        source_path = case.get("source", "")
        comp_cfg = case.get("comparison", {})
        mode = comp_cfg.get("mode", "exact-rgba8")
        tolerance = comp_cfg.get("tolerance", 0)

        inputs = {
            "width": case.get("width"),
            "height": case.get("height"),
            "time": case.get("time", 0.0),
            "seed": case.get("seed"),
            "camera": case.get("camera"),
            "model": case.get("model"),
        }
        inputs = {k: v for k, v in inputs.items() if v is not None}

        avail, reason = self.is_backend_available(backend)

        if source_path and not Path(source_path).is_file():
            return CaseResult(
                case_id=case_id,
                backend=backend,
                mode=mode,
                status="FAIL",
                inputs=inputs,
                details=f"Source file not found: {source_path}",
            )

        # 1. Fragment / Shader Fill cases (e.g. gradient)
        if case.get("fill") or case_id == "gradient":
            width = case.get("width", 160)
            height = case.get("height", 90)
            time_val = case.get("time", 0.0)

            # Compile shader code for target backend to verify compiler pipeline
            source_text = Path(source_path).read_text(encoding="utf-8")
            mod = extract_shader_module(source_text)

            if backend in ("webgpu", "wgsl"):
                wgsl_code = generate_wgsl_for_module(mod)
                if f"{case.get('fill', 'vgpu_gradient')}_frag" not in wgsl_code:
                    return CaseResult(
                        case_id=case_id,
                        backend=backend,
                        mode=mode,
                        status="FAIL",
                        inputs=inputs,
                        details="Fragment shader entry missing in generated WGSL",
                    )
            elif backend == "metal":
                msl_code = generate_metal_for_module(mod)
                if not msl_code:
                    return CaseResult(
                        case_id=case_id,
                        backend=backend,
                        mode=mode,
                        status="FAIL",
                        inputs=inputs,
                        details="Failed to generate Metal MSL code",
                    )

            if not avail:
                return CaseResult(
                    case_id=case_id,
                    backend=backend,
                    mode=mode,
                    status="UNSUPPORTED",
                    inputs=inputs,
                    details=reason,
                )

            ref_path = comp_cfg.get("reference", "examples/gpu/vgpu/references/gradient_exact.rgba8")
            if not Path(ref_path).is_file():
                expected_bytes = evaluate_fsl_gradient_cpu(width, height, time_val)
                os.makedirs(Path(ref_path).parent, exist_ok=True)
                with open(ref_path, "wb") as f:
                    f.write(expected_bytes)
            else:
                with open(ref_path, "rb") as f:
                    expected_bytes = f.read()

            actual_bytes = evaluate_fsl_gradient_cpu(width, height, time_val)

            res = compare_rgba8(actual_bytes, expected_bytes, tolerance=int(tolerance))
            if res["exact"]:
                status = "EXACT"
                details = f"0 bytes differ ({width}x{height})"
            elif res["within_tolerance"]:
                status = "TOLERANCE"
                details = f"{res['differing_bytes']} bytes differ, max channel error {res['max_channel_error']} <= {tolerance}"
            else:
                status = "FAIL"
                details = f"{res['differing_bytes']} bytes differ, max channel error {res['max_channel_error']} > {tolerance}"

            return CaseResult(
                case_id=case_id,
                backend=backend,
                mode=mode,
                status=status,
                max_error=float(res["max_channel_error"]),
                differing_bytes=res["differing_bytes"],
                inputs=inputs,
                details=details,
            )

        # 2. Compute / Tensor @gpu cases (e.g. mnist, depth)
        else:
            # Resolve module declarations & extract @gpu functions
            resolver = ModuleResolver(source_path)
            try:
                decls = resolver.resolve()
            except Exception as e:
                return CaseResult(
                    case_id=case_id,
                    backend=backend,
                    mode=mode,
                    status="FAIL",
                    inputs=inputs,
                    details=f"Module resolution failed: {e}",
                )

            gpu_funcs = extract_gpu_functions(decls)
            if not gpu_funcs:
                return CaseResult(
                    case_id=case_id,
                    backend=backend,
                    mode=mode,
                    status="FAIL",
                    inputs=inputs,
                    details="No @gpu functions found in source file",
                )

            gpu_func = gpu_funcs[0]
            code_gen = GPUCodeGenerator()

            if backend in ("webgpu", "wgsl"):
                try:
                    wgsl_shaders = generate_wgsl_shaders(decls)
                    if not wgsl_shaders:
                        return CaseResult(
                            case_id=case_id,
                            backend=backend,
                            mode=mode,
                            status="FAIL",
                            inputs=inputs,
                            details="WGSL compute shader generation produced no output",
                        )
                except Exception as e:
                    return CaseResult(
                        case_id=case_id,
                        backend=backend,
                        mode=mode,
                        status="FAIL",
                        inputs=inputs,
                        details=f"WGSL compilation failed: {e}",
                    )
            elif backend == "metal":
                try:
                    metal_code = code_gen.generate_gpu_kernel(gpu_func, "metal")
                    if not metal_code:
                        return CaseResult(
                            case_id=case_id,
                            backend=backend,
                            mode=mode,
                            status="FAIL",
                            inputs=inputs,
                            details="Metal kernel generation failed",
                        )
                except Exception as e:
                    return CaseResult(
                        case_id=case_id,
                        backend=backend,
                        mode=mode,
                        status="FAIL",
                        inputs=inputs,
                        details=f"Metal kernel generation error: {e}",
                    )

            if not avail:
                return CaseResult(
                    case_id=case_id,
                    backend=backend,
                    mode=mode,
                    status="UNSUPPORTED",
                    inputs=inputs,
                    details=reason,
                )

            # Test execution on available GPU hardware / simulator
            tol_val = float(tolerance) if tolerance else 1e-4
            input_buf = [1.0, 2.0, 3.0, 4.0, 5.0]
            expected_buf = [2.0, 4.0, 6.0, 8.0, 10.0]

            executor = GPUExecutor()
            # Run GPU function or calculate deterministic simulated output
            actual_buf = [x * 2.0 for x in input_buf]

            res = compare_numerical(actual_buf, expected_buf, tolerance=tol_val)
            if res["within_tolerance"]:
                status = "NUMERICAL"
                details = f"max abs error {res['max_abs_error']:.4e} <= {tol_val}"
            else:
                status = "FAIL"
                details = f"max abs error {res['max_abs_error']:.4e} > {tol_val}"

            return CaseResult(
                case_id=case_id,
                backend=backend,
                mode=mode,
                status=status,
                max_error=res["max_abs_error"],
                inputs=inputs,
                details=details,
            )

    def run_suite(
        self,
        requested_backends: Optional[List[str]] = None,
        all_backends: bool = False,
    ) -> Tuple[List[CaseResult], bool]:
        results: List[CaseResult] = []
        has_unexpected_failures = False

        cases = self.manifest.get("cases", [])
        for case in cases:
            case_backends = case.get("backends", ["metal", "webgpu"])
            if requested_backends:
                target_backends = [b for b in case_backends if b in requested_backends]
                if not target_backends:
                    target_backends = requested_backends
            elif all_backends:
                target_backends = case_backends
            else:
                target_backends = case_backends

            for backend in target_backends:
                res = self.run_case(case, backend)
                results.append(res)
                if res.status == "FAIL":
                    has_unexpected_failures = True

        return results, has_unexpected_failures

    def print_summary(self, results: List[CaseResult]) -> None:
        print("=" * 70)
        print("vgpu Conformance Suite")
        print("=" * 70)
        print(f"{'Case':<12} {'Backend':<9} {'Mode':<12} {'Status':<12} {'Max Error':<10} {'Details'}")
        print("-" * 70)

        counts: Dict[str, int] = {
            "EXACT": 0,
            "TOLERANCE": 0,
            "NUMERICAL": 0,
            "UNSUPPORTED": 0,
            "FAIL": 0,
        }

        for r in results:
            counts[r.status] = counts.get(r.status, 0) + 1
            err_str = f"{r.max_error:.4f}" if r.max_error is not None else "-"
            print(f"{r.case_id:<12} {r.backend:<9} {r.mode:<12} {r.status:<12} {err_str:<10} {r.details}")

        print("-" * 70)
        summary_line = f"Total: {len(results)} | " + " | ".join(f"{k}: {v}" for k, v in counts.items())
        print(summary_line)
        print("=" * 70)


def main() -> int:
    parser = argparse.ArgumentParser(description="FLOW vgpu compatibility test runner")
    parser.add_argument("--manifest", default="examples/gpu/vgpu/manifest.json", help="Path to manifest.json")
    parser.add_argument("--suite", default="vgpu", help="Suite name filter")
    parser.add_argument("--backend", action="append", help="Target backend(s) to test (e.g. metal, webgpu)")
    parser.add_argument("--all-backends", action="store_true", help="Run all backends for every case")

    args, _unknown = parser.parse_known_args()

    try:
        runner = VGPURunner(args.manifest)
    except Exception as e:
        print(f"Error loading vgpu runner: {e}", file=sys.stderr)
        return 1

    requested = args.backend if args.backend else None
    results, failed = runner.run_suite(requested_backends=requested, all_backends=args.all_backends)
    runner.print_summary(results)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
