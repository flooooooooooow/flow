#!/usr/bin/env python3
"""
MLIR JIT Execution Engine
Real JIT compilation and execution of MLIR code
"""

import ctypes
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
import os
import shutil

class MLIRJIT:
    def _find_mlir_opt(self) -> Optional[str]:
        override = os.environ.get("MLIR_OPT")
        if override:
            return override

        llvm_bin = os.environ.get("LLVM_PATH")
        if llvm_bin:
            candidate = Path(llvm_bin) / "mlir-opt"
            if candidate.exists():
                return str(candidate)

        found = shutil.which("mlir-opt")
        if found:
            return found

        # Homebrew fallback (common on macOS): $(brew --prefix llvm)/bin/mlir-opt
        try:
            brew = shutil.which("brew")
            if brew:
                res = subprocess.run([brew, "--prefix", "llvm"], capture_output=True, text=True)
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

        llvm_bin = os.environ.get("LLVM_PATH")
        if llvm_bin:
            candidate = Path(llvm_bin) / "mlir-translate"
            if candidate.exists():
                return str(candidate)

        found = shutil.which("mlir-translate")
        if found:
            return found

        # Homebrew fallback
        try:
            brew = shutil.which("brew")
            if brew:
                res = subprocess.run([brew, "--prefix", "llvm"], capture_output=True, text=True)
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
        self._loaded_libs: List[ctypes.CDLL] = []
        self._module_seq = 0
        
    def compile_mlir_to_llvm(self, mlir_code: str, module_name: str = "jit_module") -> str:
        """Compile MLIR to LLVM IR using mlir-opt"""
        mlir_opt = self._find_mlir_opt()
        if mlir_opt is None:
            raise RuntimeError(
                "mlir-opt not found on PATH. Install an LLVM/MLIR toolchain and ensure mlir-opt is available. "
                "On macOS (Homebrew): `brew install llvm` then add LLVM bin to PATH (see `brew info llvm`). "
                f"Current PATH: {os.environ.get('PATH','')}"
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
            # then rely on LLVM/Clang -O2 for stable codegen (-O3 miscompiles some tensor loops).
            result = subprocess.run(
                [
                    mlir_opt,
                    # vector.transfer_* -> scf/vector.load-store must run before
                    # scf-to-cf, and convert-vector-to-llvm before func-to-llvm.
                    "--convert-vector-to-scf",
                    "--convert-scf-to-cf",
                    # complex.mul and friends become real arithmetic first; whatever
                    # the standard expansion leaves goes straight to llvm.
                    "--convert-complex-to-standard",
                    "--convert-complex-to-llvm",
                    "--convert-math-to-llvm",
                    "--memref-expand",
                    "--convert-vector-to-llvm",
                    "--convert-arith-to-llvm",
                    "--convert-index-to-llvm",
                    "--convert-cf-to-llvm",
                    "--convert-func-to-llvm",
                    "--finalize-memref-to-llvm",
                    "--reconcile-unrealized-casts",
                    str(mlir_file),
                    "-o",
                    str(lowered_mlir_file),
                ],
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
                env=os.environ.copy(),
            )
            
            if result.returncode != 0:
                print(f"MLIR lowering (mlir-opt) failed: {result.stderr}")
                return ""

        except FileNotFoundError:
            raise RuntimeError("mlir-opt could not be executed. Check that it exists and is executable.")

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
                stdin=subprocess.DEVNULL,
                env=os.environ.copy(),
            )

            if result2.returncode != 0:
                print(f"MLIR translation (mlir-translate) failed: {result2.stderr}")
                return ""

            return llvm_file.read_text()
            
        except FileNotFoundError:
            raise RuntimeError("mlir-translate could not be executed. Check that it exists and is executable.")
    
    @staticmethod
    def _asan_preferred() -> bool:
        """Prefer ASAN executable JIT on macOS arm64 (stable aggregate-return codegen)."""
        env = os.environ.get("FLOW_JIT_ASAN")
        if env is not None:
            return env.lower() not in ("0", "false", "no", "off")
        return sys.platform == "darwin"

    @staticmethod
    def _force_fast_jit() -> bool:
        """FLOW_JIT_ASAN=0: try fast -O2 executable before ASAN fallback."""
        env = os.environ.get("FLOW_JIT_ASAN")
        return env is not None and env.lower() in ("0", "false", "no", "off")

    @staticmethod
    def normalize_exit_code(code: Optional[int]) -> int:
        if code is None:
            return -1
        return code

    @classmethod
    def is_crash_exit(cls, code: Optional[int]) -> bool:
        """True when native code died from a signal (segfault, bus error, etc.)."""
        if code is None:
            return True
        if code < 0:
            return True
        return code in (134, 138, 139)

    @staticmethod
    def _clang_jit_flags(*, shared: bool, asan: bool) -> List[str]:
        flags = ["-O2"]
        if asan:
            flags = ["-fsanitize=address", "-g", "-O2", "-fno-omit-frame-pointer"]
        if shared:
            flags = ["-shared", "-fPIC", *flags]
        return flags

    @staticmethod
    def _repo_root() -> Path:
        # src/flow/mlir_jit.py → repo root
        return Path(__file__).resolve().parents[2]

    @classmethod
    def flow_runtime_link_args(cls) -> tuple:
        """Return (sources, ldflags) for core Flow runtime (JIT / optional links)."""
        import platform

        root = cls._repo_root()
        runtime = root / "runtime"
        sources: List[str] = [
            str(runtime / "flow_rt_support.c"),
            str(runtime / "flow_rt_sysinfo.c"),
            str(runtime / "flow_concurrency.c"),
            str(runtime / "flow_fiber.c"),
            str(runtime / "flow_fctx_init.c"),
            str(runtime / "flow_cont.c"),
            str(runtime / "flow_tls.c"),
            str(runtime / "flow_rt_task_store.c"),
            str(runtime / "flow_rt_fiber_async.c"),
            str(runtime / "flow_rt_parallel.c"),
            str(runtime / "flow_rt_cchan.c"),
        ]
        machine = platform.machine().lower()
        if machine in ("arm64", "aarch64"):
            sources.append(str(runtime / "flow_fctx_arm64.S"))
        elif machine in ("x86_64", "amd64"):
            sources.append(str(runtime / "flow_fctx_x86_64.S"))

        ldflags: List[str] = ["-pthread", f"-I{runtime}"]
        if sys.platform == "darwin":
            metal = runtime / "gpu_metal.m"
            if metal.exists():
                sources.append(str(metal))
                ldflags.extend(["-framework", "Metal", "-framework", "Foundation"])
        sources = [s for s in sources if Path(s).exists()]
        return sources, ldflags

    @staticmethod
    def _should_link_runtime(explicit: Optional[bool]) -> bool:
        if explicit is not None:
            return explicit
        env = os.environ.get("FLOW_JIT_LINK_RUNTIME", "0")
        return env.lower() not in ("0", "false", "no", "off", "")

    def compile_llvm_to_executable(
        self,
        llvm_ir: str,
        module_name: str = "jit_module",
        *,
        asan: bool = False,
        extra_sources: Optional[List[str]] = None,
        extra_ldflags: Optional[List[str]] = None,
        link_runtime: Optional[bool] = None,
    ) -> Optional[Path]:
        """Compile LLVM IR to a standalone executable.

        When link_runtime is True (or FLOW_JIT_LINK_RUNTIME=1), also link the
        core Flow C runtime so extern symbols resolve like ./flow mlir-run.
        """
        module_name = self._unique_module_name(module_name)
        llvm_file = Path(self.temp_dir) / f"{module_name}.ll"
        exe_file = Path(self.temp_dir) / module_name
        llvm_file.write_text(llvm_ir)

        sources: List[str] = list(extra_sources or [])
        ldflags: List[str] = list(extra_ldflags or [])
        if self._should_link_runtime(link_runtime):
            rt_sources, rt_ldflags = self.flow_runtime_link_args()
            sources.extend(rt_sources)
            ldflags.extend(rt_ldflags)

        try:
            result = subprocess.run(
                [
                    "clang",
                    *self._clang_jit_flags(shared=False, asan=asan),
                    str(llvm_file),
                    *sources,
                    "-o",
                    str(exe_file),
                    *ldflags,
                    "-lm",
                ],
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
            )
            if result.returncode != 0:
                print(f"LLVM executable build failed: {result.stderr}")
                return None
            return exe_file
        except FileNotFoundError:
            print("❌ clang not found. Install Clang for JIT compilation.")
            return None

    def _run_native_executable(self, exe: Path) -> int:
        """Run JIT code in an isolated subprocess so crashes cannot kill Python."""
        timeout_s = int(os.environ.get("FLOW_JIT_TIMEOUT", "300"))
        try:
            result = subprocess.run(
                [str(exe)],
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
                timeout=timeout_s,
            )
            if result.stdout:
                sys.stdout.write(result.stdout)
            if result.stderr:
                sys.stderr.write(result.stderr)
            return self.normalize_exit_code(result.returncode)
        except subprocess.TimeoutExpired:
            print(f"❌ JIT execution timed out after {timeout_s}s")
            return -1
        except OSError as e:
            print(f"❌ JIT subprocess failed to start: {e}")
            return -1
        except Exception as e:
            print(f"❌ JIT subprocess error: {e}")
            return -1

    def _unique_module_name(self, module_name: str = "jit_module") -> str:
        self._module_seq += 1
        token = uuid.uuid4().hex[:8]
        return f"{module_name}_{self._module_seq}_{token}"

    def compile_llvm_to_native(self, llvm_ir: str, module_name: str = "jit_module") -> Optional[ctypes.CDLL]:
        """Compile LLVM IR to native library and load it"""
        module_name = self._unique_module_name(module_name)
        llvm_file = Path(self.temp_dir) / f"{module_name}.ll"
        so_file = Path(self.temp_dir) / f"{module_name}.so"
        
        # Write LLVM IR to file
        llvm_file.write_text(llvm_ir)
        
        try:
            # Compile LLVM IR to shared library
            result = subprocess.run([
                "clang",
                *self._clang_jit_flags(shared=True, asan=False),
                str(llvm_file),
                "-o",
                str(so_file),
                "-lm",
            ], capture_output=True, text=True, stdin=subprocess.DEVNULL)
            
            if result.returncode != 0:
                print(f"LLVM compilation failed: {result.stderr}")
                return None
                
            # Load the shared library with local symbol scope to avoid cross-module clashes.
            lib = ctypes.CDLL(str(so_file), mode=ctypes.RTLD_LOCAL)
            self.compiled_modules[module_name] = lib
            self._loaded_libs.append(lib)
            return lib
            
        except FileNotFoundError:
            print("❌ clang not found. Install Clang for JIT compilation.")
            return None
    
    def execute_function(self, lib: ctypes.CDLL, func_name: str,
                         args: List[Any] = None, return_type: type = int) -> Any:
        """Execute a compiled function in-process (testing only — crashes are not catchable)."""
        try:
            func = getattr(lib, func_name)
        except AttributeError:
            print(f"❌ Function {func_name} not found in compiled module")
            return None

        if args:
            func.argtypes = [ctypes.c_int] * len(args)
        func.restype = ctypes.c_int if return_type is int else ctypes.c_void_p

        try:
            if args:
                return func(*args)
            return func()
        except Exception as e:
            print(f"❌ In-process JIT call failed: {e}")
            return None

    def jit_compile_and_run(self, mlir_code: str, func_name: str = "main",
                           args: List[Any] = None,
                           *,
                           link_runtime: Optional[bool] = None) -> Optional[Any]:
        """Full JIT pipeline: MLIR -> LLVM -> native executable -> subprocess execute.

        Native code never runs in the Python process (segfaults cannot be caught
        via try/except). On crash, automatically retries with an ASAN executable.
        """
        del func_name, args  # entry point is always main() in the JIT executable
        try:
            llvm_ir = self.compile_mlir_to_llvm(mlir_code)
            if not llvm_ir:
                return None

            attempts: List[tuple[str, bool]] = []
            if self._force_fast_jit():
                attempts.append(("fast", False))
                attempts.append(("asan-fallback", True))
            elif self._asan_preferred():
                attempts.append(("asan", True))
            else:
                attempts.append(("fast", False))
                attempts.append(("asan-fallback", True))

            last_code: Optional[int] = None
            for idx, (label, asan) in enumerate(attempts):
                exe = self.compile_llvm_to_executable(
                    llvm_ir, asan=asan, link_runtime=link_runtime
                )
                if exe is None:
                    continue
                code = self._run_native_executable(exe)
                last_code = code
                if not self.is_crash_exit(code):
                    return code
                if idx + 1 < len(attempts):
                    print(
                        "⚠️  JIT native crash (exit "
                        f"{code}); retrying with ASAN executable..."
                    )
                    continue
                print(f"❌ JIT native crash (exit {code}) after all attempts")
                return code

            return last_code
        except Exception as e:
            print(f"❌ JIT pipeline error: {e}")
            return None
    
    def cleanup(self):
        """Release JIT handles. Temp dylibs are left for the OS to reclaim at exit."""
        self.compiled_modules.clear()
        self._loaded_libs.clear()

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
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(FlowJITRuntime.create_runtime_lib())
            c_file = f.name
        
        so_file = c_file.replace('.c', '.so')
        
        try:
            result = subprocess.run([
                "clang", "-shared", "-fPIC", c_file, "-o", so_file
            ], capture_output=True, text=True)
            
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
