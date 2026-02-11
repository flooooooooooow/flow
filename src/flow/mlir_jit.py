#!/usr/bin/env python3
"""
MLIR JIT Execution Engine
Real JIT compilation and execution of MLIR code
"""

import ctypes
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
import os
import shutil


class MLIRJIT:
    def _find_mlir_opt(self) -> Optional[str]:
        override = os.environ.get("MLIR_OPT")
        if override:
            return override

        found = shutil.which("mlir-opt")
        if found:
            return found

        # Homebrew fallback (common on macOS): $(brew --prefix llvm)/bin/mlir-opt
        try:
            brew = shutil.which("brew")
            if brew:
                res = subprocess.run(
                    [brew, "--prefix", "llvm"], capture_output=True, text=True
                )
                if res.returncode == 0:
                    candidate = Path(res.stdout.strip()) / "bin" / "mlir-opt"
                    if candidate.exists():
                        return str(candidate)
        except Exception:
            pass

        return None

    def _find_mlir_translate(self) -> Optional[str]:
        override = os.environ.get("MLIR_TRANSLATE")
        if override:
            return override

        found = shutil.which("mlir-translate")
        if found:
            return found

        # Homebrew fallback
        try:
            brew = shutil.which("brew")
            if brew:
                res = subprocess.run(
                    [brew, "--prefix", "llvm"], capture_output=True, text=True
                )
                if res.returncode == 0:
                    candidate = Path(res.stdout.strip()) / "bin" / "mlir-translate"
                    if candidate.exists():
                        return str(candidate)
        except Exception:
            pass

        return None

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="flow_jit_")
        self.compiled_modules: Dict[str, Any] = {}

    def compile_mlir_to_llvm(
        self, mlir_code: str, module_name: str = "jit_module"
    ) -> str:
        """Compile MLIR to LLVM IR using mlir-opt"""
        mlir_opt = self._find_mlir_opt()
        if mlir_opt is None:
            raise RuntimeError(
                "mlir-opt not found on PATH. Install an LLVM/MLIR toolchain and ensure mlir-opt is available. "
                "On macOS (Homebrew): `brew install llvm` then add LLVM bin to PATH (see `brew info llvm`). "
                f"Current PATH: {os.environ.get('PATH', '')}"
            )

        mlir_translate = self._find_mlir_translate()
        if mlir_translate is None:
            raise RuntimeError(
                "mlir-translate not found on PATH. It is required to convert LLVM-dialect MLIR to LLVM IR. "
                "On macOS (Homebrew): `brew install llvm` then add LLVM bin to PATH (see `brew info llvm`)."
            )
        mlir_file = Path(self.temp_dir) / f"{module_name}.mlir"
        lowered_mlir_file = Path(self.temp_dir) / f"{module_name}.lowered.mlir"
        llvm_file = Path(self.temp_dir) / f"{module_name}.ll"

        # Write MLIR to file
        mlir_file.write_text(mlir_code)

        # 1) Lower MLIR to LLVM dialect MLIR
        try:
            # Keep this pipeline conservative and widely supported.
            # The goal for SIMD-first (implicit) is: emit LLVM-friendly IR,
            # then rely on LLVM/Clang -O3 -march=native to pick best vector width.
            result = subprocess.run(
                [
                    mlir_opt,
                    "--canonicalize",
                    "--cse",
                    "--convert-scf-to-cf",
                    "--convert-index-to-llvm",
                    "--convert-arith-to-llvm",
                    "--convert-cf-to-llvm",
                    "--convert-math-to-llvm",
                    "--convert-func-to-llvm",
                    "--finalize-memref-to-llvm",
                    "--convert-vector-to-llvm",
                    "--reconcile-unrealized-casts",
                    str(mlir_file),
                    "-o",
                    str(lowered_mlir_file),
                ],
                capture_output=True,
                text=True,
                env=os.environ.copy(),
            )

            if result.returncode != 0:
                print(f"MLIR lowering (mlir-opt) failed: {result.stderr}")
                return ""

        except FileNotFoundError:
            raise RuntimeError(
                "mlir-opt could not be executed. Check that it exists and is executable."
            )

        # 2) Translate LLVM dialect MLIR -> LLVM IR (.ll)
        try:
            result2 = subprocess.run(
                [
                    mlir_translate,
                    "--mlir-to-llvmir",
                    str(lowered_mlir_file),
                    "-o",
                    str(llvm_file),
                ],
                capture_output=True,
                text=True,
                env=os.environ.copy(),
            )

            if result2.returncode != 0:
                print(f"MLIR translation (mlir-translate) failed: {result2.stderr}")
                return ""

            return llvm_file.read_text()

        except FileNotFoundError:
            raise RuntimeError(
                "mlir-translate could not be executed. Check that it exists and is executable."
            )

    def compile_llvm_to_native(
        self, llvm_ir: str, module_name: str = "jit_module"
    ) -> Optional[ctypes.CDLL]:
        """Compile LLVM IR to native library and load it"""
        llvm_file = Path(self.temp_dir) / f"{module_name}.ll"
        so_file = Path(self.temp_dir) / f"{module_name}.so"

        # Write LLVM IR to file
        llvm_file.write_text(llvm_ir)

        try:
            # Compile LLVM IR to shared library
            result = subprocess.run(
                [
                    # SIMD-first defaults: let LLVM pick the best available ISA on this machine.
                    "clang",
                    "-shared",
                    "-fPIC",
                    "-O3",
                    "-march=native",
                    str(llvm_file),
                    "-o",
                    str(so_file),
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"LLVM compilation failed: {result.stderr}")
                return None

            # Load the shared library
            lib = ctypes.CDLL(str(so_file))
            self.compiled_modules[module_name] = lib
            return lib

        except FileNotFoundError:
            print("❌ clang not found. Install Clang for JIT compilation.")
            return None

    def execute_function(
        self,
        lib: ctypes.CDLL,
        func_name: str,
        args: Optional[List[Any]] = None,
        return_type: type = int,
    ) -> Any:
        """Execute a compiled function"""
        if func_name not in self.compiled_modules:
            # Try to find the function in the library
            try:
                func = getattr(lib, func_name)
            except AttributeError:
                print(f"❌ Function {func_name} not found in compiled module")
                return None
        else:
            func = getattr(lib, func_name)

        # Set argument and return types
        if args:
            func.argtypes = [ctypes.c_int] * len(args)
        func.restype = ctypes.c_int if return_type is int else ctypes.c_void_p

        # Call the function
        if args:
            return func(*args)
        else:
            return func()

    def jit_compile_and_run(
        self, mlir_code: str, func_name: str = "main", args: Optional[List[Any]] = None
    ) -> Optional[Any]:
        """Full JIT pipeline: MLIR -> LLVM -> Native -> Execute"""
        # print("🔥 JIT Compiling MLIR...")

        # Step 1: MLIR to LLVM IR
        llvm_ir = self.compile_mlir_to_llvm(mlir_code)
        if not llvm_ir:
            return None

        # print("LLVM IR generated")

        # Step 2: LLVM to native
        lib = self.compile_llvm_to_native(llvm_ir)
        if not lib:
            return None

        # print("🚀 Native code compiled")

        # Step 3: Execute
        result = self.execute_function(lib, func_name, args)
        # print("Function main executed")
        return result

    def cleanup(self):
        """Clean up temporary files"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)


class FlowJITRuntime:
    """Runtime support functions for FLOW JIT"""

    @staticmethod
    def create_runtime_lib() -> str:
        """Create a small runtime library for JIT functions"""
        runtime_c = """
#include <stdio.h>
#include <time.h>

// Runtime functions for FLOW JIT
void jit_print(const char* message) {
    printf("%s\\n", message);
}

double jit_time() {
    return (double)clock() / CLOCKS_PER_SEC;
}

int jit_reload_check() {
    return 1; // Always true for now
}
"""
        return runtime_c

    @staticmethod
    def compile_runtime() -> Optional[ctypes.CDLL]:
        """Compile the runtime library"""
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(FlowJITRuntime.create_runtime_lib())
            c_file = f.name

        so_file = c_file.replace(".c", ".so")

        try:
            result = subprocess.run(
                ["clang", "-shared", "-fPIC", c_file, "-o", so_file],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return ctypes.CDLL(so_file)
            else:
                print(f"Runtime compilation failed: {result.stderr}")
                return None

        except FileNotFoundError:
            print("❌ clang not found for runtime compilation")
            return None
        finally:
            Path(c_file).unlink(missing_ok=True)
            Path(so_file).unlink(missing_ok=True)


def demo_jit():
    """Demo the JIT system with a simple example"""
    mlir_code = """
module {
  func.func @main() -> i32 {
    %0 = arith.constant 42 : i32
    func.return %0 : i32
  }
}
"""

    jit = MLIRJIT()
    try:
        result = jit.jit_compile_and_run(mlir_code, "main")
        print(f"JIT Result: {result}")
    finally:
        jit.cleanup()


if __name__ == "__main__":
    demo_jit()
