#!/usr/bin/env python3
"""MLIR GPU -> SPIR-V compilation helpers."""

from pathlib import Path
from typing import Optional, List
import shutil
import subprocess
import tempfile


class MLIRSPIRVCompiler:
    def __init__(
        self, mlir_opt: Optional[str] = None, mlir_translate: Optional[str] = None
    ):
        self.mlir_opt = mlir_opt or self._find_mlir_opt()
        self.mlir_translate = mlir_translate or self._find_mlir_translate()

    def _find_mlir_opt(self) -> str:
        found = shutil.which("mlir-opt")
        if found:
            return found
        # Homebrew fallback (macOS)
        brew = shutil.which("brew")
        if brew:
            try:
                res = subprocess.run(
                    [brew, "--prefix", "llvm"], capture_output=True, text=True
                )
                if res.returncode == 0:
                    candidate = Path(res.stdout.strip()) / "bin" / "mlir-opt"
                    if candidate.exists():
                        return str(candidate)
            except Exception:
                pass
        return "mlir-opt"

    def _find_mlir_translate(self) -> str:
        found = shutil.which("mlir-translate")
        if found:
            return found
        brew = shutil.which("brew")
        if brew:
            try:
                res = subprocess.run(
                    [brew, "--prefix", "llvm"], capture_output=True, text=True
                )
                if res.returncode == 0:
                    candidate = Path(res.stdout.strip()) / "bin" / "mlir-translate"
                    if candidate.exists():
                        return str(candidate)
            except Exception:
                pass
        return "mlir-translate"

    def compile_mlir_to_spirv(
        self,
        mlir_code: str,
        output_path: str,
        extra_opt_args: Optional[List[str]] = None,
    ) -> None:
        if not self.mlir_opt or not self.mlir_translate:
            raise RuntimeError("mlir-opt or mlir-translate not found on PATH")

        extra_opt_args = extra_opt_args or []

        with tempfile.TemporaryDirectory() as tmpdir:
            mlir_file = Path(tmpdir) / "input.mlir"
            spirv_mlir = Path(tmpdir) / "spirv.mlir"
            mlir_file.write_text(mlir_code)

            # Pipeline: outline kernels and lower to SPIR-V dialect
            opt_cmd = [
                self.mlir_opt,
                "-gpu-kernel-outlining",
                "-convert-gpu-to-spirv",
                *extra_opt_args,
                str(mlir_file),
                "-o",
                str(spirv_mlir),
            ]
            res = subprocess.run(opt_cmd, capture_output=True, text=True)
            if res.returncode != 0:
                raise RuntimeError(f"mlir-opt failed: {res.stderr}")

            # Serialize SPIR-V
            translate_cmd = [
                self.mlir_translate,
                "--mlir-to-spirv",
                str(spirv_mlir),
            ]
            res2 = subprocess.run(translate_cmd, capture_output=True)
            if res2.returncode != 0:
                raise RuntimeError(
                    f"mlir-translate failed: {res2.stderr.decode('utf-8', errors='ignore')}"
                )

            Path(output_path).write_bytes(res2.stdout)
