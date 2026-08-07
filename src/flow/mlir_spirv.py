#!/usr/bin/env python3
"""MLIR GPU -> SPIR-V compilation helpers.

Parallel GPU target alongside Metal (macOS) and WGSL (WebGPU). Emit-only today;
Vulkan/MoltenVK dispatch is a follow-up.
"""

from pathlib import Path
from typing import Optional, List
import os
import shutil
import subprocess
import tempfile


class MLIRSPIRVCompiler:
    def __init__(self, mlir_opt: Optional[str] = None, mlir_translate: Optional[str] = None):
        self.mlir_opt = mlir_opt or self._find_mlir_opt()
        self.mlir_translate = mlir_translate or self._find_mlir_translate()

    def _find_tool(self, name: str) -> str:
        override_env = {
            "mlir-opt": "MLIR_OPT",
            "mlir-translate": "MLIR_TRANSLATE",
        }.get(name)
        if override_env:
            override = os.environ.get(override_env)
            if override and Path(override).exists():
                return override

        llvm_bin = os.environ.get("LLVM_PATH")
        if llvm_bin:
            candidate = Path(llvm_bin) / name
            if candidate.exists():
                return str(candidate)

        found = shutil.which(name)
        if found:
            return found

        brew = shutil.which("brew")
        if brew:
            try:
                res = subprocess.run(
                    [brew, "--prefix", "llvm"], capture_output=True, text=True
                )
                if res.returncode == 0:
                    candidate = Path(res.stdout.strip()) / "bin" / name
                    if candidate.exists():
                        return str(candidate)
            except Exception:
                pass
        return name

    def _find_mlir_opt(self) -> str:
        return self._find_tool("mlir-opt")

    def _find_mlir_translate(self) -> str:
        return self._find_tool("mlir-translate")

    def compile_mlir_to_spirv(
        self,
        mlir_code: str,
        output_path: str,
        extra_opt_args: Optional[List[str]] = None,
    ) -> None:
        if not self.mlir_opt or not self.mlir_translate:
            raise RuntimeError("mlir-opt or mlir-translate not found on PATH")

        if not shutil.which(self.mlir_opt) and not Path(self.mlir_opt).exists():
            raise RuntimeError(
                f"mlir-opt not found ({self.mlir_opt!r}). "
                "Install LLVM/MLIR or set MLIR_OPT / LLVM_PATH."
            )
        if not shutil.which(self.mlir_translate) and not Path(self.mlir_translate).exists():
            raise RuntimeError(
                f"mlir-translate not found ({self.mlir_translate!r}). "
                "Install LLVM/MLIR or set MLIR_TRANSLATE / LLVM_PATH."
            )

        extra_opt_args = extra_opt_args or []

        with tempfile.TemporaryDirectory() as tmpdir:
            mlir_file = Path(tmpdir) / "input.mlir"
            spirv_mlir = Path(tmpdir) / "spirv.mlir"
            mlir_file.write_text(mlir_code)

            # Pipeline: outline kernels and lower to SPIR-V dialect
            opt_cmd = [
                self.mlir_opt,
                "-gpu-kernel-outlining",
                "-convert-scf-to-spirv",
                "-convert-memref-to-spirv",
                "-convert-arith-to-spirv",
                "-convert-index-to-spirv",
                "-convert-gpu-to-spirv",
                "-reconcile-unrealized-casts",
                *extra_opt_args,
                str(mlir_file),
                "-o",
                str(spirv_mlir),
            ]
            res = subprocess.run(opt_cmd, capture_output=True, text=True)
            if res.returncode != 0:
                raise RuntimeError(
                    f"mlir-opt SPIR-V lowering failed (exit {res.returncode}):\n"
                    f"{res.stderr or res.stdout}"
                )

            # Serialize SPIR-V binary
            translate_cmd = [
                self.mlir_translate,
                "--mlir-to-spirv",
                str(spirv_mlir),
            ]
            res2 = subprocess.run(translate_cmd, capture_output=True)
            if res2.returncode != 0:
                err = res2.stderr.decode("utf-8", errors="ignore")
                raise RuntimeError(
                    f"mlir-translate --mlir-to-spirv failed (exit {res2.returncode}):\n{err}"
                )

            if not res2.stdout:
                raise RuntimeError("mlir-translate produced empty SPIR-V output")

            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(res2.stdout)
