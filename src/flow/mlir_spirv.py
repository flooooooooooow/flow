#!/usr/bin/env python3
"""MLIR GPU -> SPIR-V shared GPU compilation helpers.

SPIR-V is the portable GPU artifact. Vulkan consumes it directly; Apple targets
can lower the same SPIR-V through SPIRV-Cross to Metal Shading Language (MSL),
then optionally compile MSL to a Metal library with Xcode's ``xcrun`` tools.
"""

from pathlib import Path
from typing import Optional, List
import os
import shutil
import subprocess
import tempfile


class MLIRSPIRVCompiler:
    def __init__(
        self,
        mlir_opt: Optional[str] = None,
        mlir_translate: Optional[str] = None,
        spirv_cross: Optional[str] = None,
        xcrun: Optional[str] = None,
    ):
        self.mlir_opt = mlir_opt or self._find_mlir_opt()
        self.mlir_translate = mlir_translate or self._find_mlir_translate()
        self.spirv_cross = spirv_cross or self._find_tool("spirv-cross")
        self.xcrun = xcrun or self._find_tool("xcrun")

    def _find_tool(self, name: str) -> str:
        override_env = {
            "mlir-opt": "MLIR_OPT",
            "mlir-translate": "MLIR_TRANSLATE",
            "spirv-cross": "SPIRV_CROSS",
            "xcrun": "XCRUN",
        }.get(name)
        if override_env:
            override = os.environ.get(override_env)
            if override and Path(override).exists():
                return override

        if name in ("mlir-opt", "mlir-translate"):
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
            package = "llvm" if name in ("mlir-opt", "mlir-translate") else None
            if name == "spirv-cross":
                package = "spirv-cross"
            if package:
                try:
                    res = subprocess.run(
                        [brew, "--prefix", package], capture_output=True, text=True
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

    @staticmethod
    def _require_tool(tool: str, name: str) -> None:
        if not shutil.which(tool) and not Path(tool).exists():
            raise RuntimeError(
                f"{name} not found ({tool!r}). Install it or set the matching "
                "tool override environment variable."
            )

    def compile_mlir_to_spirv(
        self,
        mlir_code: str,
        output_path: str,
        extra_opt_args: Optional[List[str]] = None,
    ) -> None:
        self._require_tool(self.mlir_opt, "mlir-opt")
        self._require_tool(self.mlir_translate, "mlir-translate")

        extra_opt_args = extra_opt_args or []

        with tempfile.TemporaryDirectory() as tmpdir:
            mlir_file = Path(tmpdir) / "input.mlir"
            spirv_mlir = Path(tmpdir) / "spirv.mlir"
            mlir_file.write_text(mlir_code)

            # Pipeline: outline kernels and lower to SPIR-V dialect.
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

            # Serialize SPIR-V binary.
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

    def compile_spirv_to_msl(
        self,
        spirv_path: str,
        output_path: str,
        extra_args: Optional[List[str]] = None,
    ) -> None:
        """Lower a SPIR-V binary to Metal Shading Language with SPIRV-Cross."""
        self._require_tool(self.spirv_cross, "spirv-cross")

        source = Path(spirv_path)
        if not source.exists() or source.stat().st_size == 0:
            raise RuntimeError(f"SPIR-V input missing or empty: {source}")

        cmd = [self.spirv_cross, str(source), "--msl", *(extra_args or [])]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(
                f"spirv-cross MSL lowering failed (exit {res.returncode}):\n"
                f"{res.stderr or res.stdout}"
            )
        if not res.stdout.strip():
            raise RuntimeError("spirv-cross produced empty MSL output")

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(res.stdout)

    def compile_mlir_to_msl(
        self,
        mlir_code: str,
        output_path: str,
        extra_opt_args: Optional[List[str]] = None,
        spirv_cross_args: Optional[List[str]] = None,
    ) -> None:
        """Compile MLIR GPU dialect through the shared SPIR-V path to MSL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            spirv_path = Path(tmpdir) / "kernel.spv"
            self.compile_mlir_to_spirv(
                mlir_code,
                str(spirv_path),
                extra_opt_args=extra_opt_args,
            )
            self.compile_spirv_to_msl(
                str(spirv_path),
                output_path,
                extra_args=spirv_cross_args,
            )

    def compile_msl_to_metallib(
        self,
        msl_path: str,
        output_path: str,
        sdk: str = "macosx",
    ) -> None:
        """Compile MSL source to a native ``.metallib`` using Xcode tools."""
        self._require_tool(self.xcrun, "xcrun")

        source = Path(msl_path)
        if not source.exists() or source.stat().st_size == 0:
            raise RuntimeError(f"MSL input missing or empty: {source}")

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            air_path = Path(tmpdir) / "kernel.air"
            metal_cmd = [
                self.xcrun,
                "-sdk",
                sdk,
                "metal",
                "-c",
                str(source),
                "-o",
                str(air_path),
            ]
            metal_res = subprocess.run(metal_cmd, capture_output=True, text=True)
            if metal_res.returncode != 0:
                raise RuntimeError(
                    f"Metal compilation failed (exit {metal_res.returncode}):\n"
                    f"{metal_res.stderr or metal_res.stdout}"
                )

            metallib_cmd = [
                self.xcrun,
                "-sdk",
                sdk,
                "metallib",
                str(air_path),
                "-o",
                str(out),
            ]
            metallib_res = subprocess.run(
                metallib_cmd, capture_output=True, text=True
            )
            if metallib_res.returncode != 0:
                raise RuntimeError(
                    f"metallib failed (exit {metallib_res.returncode}):\n"
                    f"{metallib_res.stderr or metallib_res.stdout}"
                )

            if not out.exists() or out.stat().st_size == 0:
                raise RuntimeError("metallib completed without producing output")

    def compile_mlir_to_metallib(
        self,
        mlir_code: str,
        output_path: str,
        sdk: str = "macosx",
        extra_opt_args: Optional[List[str]] = None,
        spirv_cross_args: Optional[List[str]] = None,
    ) -> None:
        """Compile MLIR GPU dialect to a native Metal library via SPIR-V."""
        with tempfile.TemporaryDirectory() as tmpdir:
            msl_path = Path(tmpdir) / "kernel.metal"
            self.compile_mlir_to_msl(
                mlir_code,
                str(msl_path),
                extra_opt_args=extra_opt_args,
                spirv_cross_args=spirv_cross_args,
            )
            self.compile_msl_to_metallib(
                str(msl_path),
                output_path,
                sdk=sdk,
            )
