#!/usr/bin/env python3
"""
FLOW JIT Runner
Hot reload and JIT execution via MLIRJIT (MLIR → LLVM → native shared lib).
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    _HAS_WATCHDOG = True
except Exception:
    Observer = None
    FileSystemEventHandler = object
    _HAS_WATCHDOG = False

from .module_resolver import resolve_modules
from .mlir_generator import flow_to_mlir
from .monomorphize import monomorphize
from .mlir_jit import MLIRJIT
from .transpiler import _filter_declarations


def compile_flow_to_mlir(flow_file: str, *, hot_mode: bool = False) -> str:
    """Compile a .flow file to MLIR for JIT execution."""
    path = Path(flow_file)
    if hot_mode:
        active_modes = {"hot", "jit", "mlir", "compile"}
    else:
        active_modes = {"jit", "mlir", "compile"}

    declarations = resolve_modules(str(path))
    declarations = _filter_declarations(declarations, active_modes)
    declarations = monomorphize(declarations)
    declarations = _filter_declarations(declarations, active_modes)
    return flow_to_mlir(declarations, source_file=path.name)


class FlowJITRunner:
    def __init__(self, flow_file: str, watch_dir: Optional[str] = None, *, hot_mode: bool = False):
        self.flow_file = Path(flow_file)
        self.watch_dir = Path(watch_dir) if watch_dir else self.flow_file.parent
        self.hot_mode = hot_mode
        self.debounce_seconds = 0.5
        self.running = True
        self._jit: Optional[MLIRJIT] = None
        self.compilation_cache: Dict[str, Any] = {}

    def _reset_jit(self) -> MLIRJIT:
        if self._jit is not None:
            self._jit.cleanup()
        self._jit = MLIRJIT()
        return self._jit

    def compile_and_run(self) -> bool:
        """Compile FLOW → MLIR → native via MLIRJIT and execute main()."""
        try:
            print(f"🔥 JIT compiling {self.flow_file.name}...")
            mlir_code = compile_flow_to_mlir(str(self.flow_file), hot_mode=self.hot_mode)
            jit = self._reset_jit()
            result = jit.jit_compile_and_run(mlir_code, "main")
            if result is None:
                print("❌ JIT execution failed (see errors above)")
                print("   Requires: mlir-opt, mlir-translate, clang on PATH")
                print("   macOS: brew install llvm && export PATH=\"$(brew --prefix llvm)/bin:$PATH\"")
                return False
            print(f"✅ JIT finished with exit code: {result}")
            return True
        except Exception as e:
            print(f"❌ JIT error: {e}")
            return False

    def cleanup(self) -> None:
        if self._jit is not None:
            self._jit.cleanup()
            self._jit = None

    def start_hot_reload(self):
        """Start file watcher for hot reload."""
        if _HAS_WATCHDOG:
            class FlowFileHandler(FileSystemEventHandler):
                def __init__(self, runner: "FlowJITRunner"):
                    self.runner = runner
                    self.last_modified: Dict[str, float] = {}

                def on_modified(self, event):
                    if event.is_directory:
                        return
                    file_path = Path(event.src_path)
                    if file_path.suffix == ".flow" or file_path.name == "flow":
                        current_time = time.time()
                        last_time = self.last_modified.get(str(file_path), 0)
                        if current_time - last_time > self.runner.debounce_seconds:
                            self.last_modified[str(file_path)] = current_time
                            print(f"🔄 Detected change in {file_path.name}")
                            self.runner.compile_and_run()

            observer = Observer()
            observer.schedule(FlowFileHandler(self), str(self.watch_dir), recursive=True)
            observer.start()

            try:
                print("FLOW JIT Hot Reload started")
                print(f"Watching: {self.watch_dir}")
                print(f"Target: {self.flow_file}")
                print("Press Ctrl+C to stop")

                self.compile_and_run()

                while self.running:
                    time.sleep(0.1)

            except KeyboardInterrupt:
                print("\nStopping hot reload...")
                self.running = False
            finally:
                observer.stop()
                observer.join()
                self.cleanup()
        else:
            print("FLOW JIT Hot Reload started (polling mode)")
            print(f"Watching: {self.watch_dir}")
            print(f"Target: {self.flow_file}")
            print("Tip: install 'watchdog' for faster hot reload.")
            print("Press Ctrl+C to stop")

            def collect_mtimes() -> Dict[str, float]:
                mtimes: Dict[str, float] = {}
                for p in self.watch_dir.rglob("*.flow"):
                    try:
                        mtimes[str(p)] = p.stat().st_mtime
                    except FileNotFoundError:
                        continue
                return mtimes

            last = collect_mtimes()
            self.compile_and_run()

            try:
                while self.running:
                    time.sleep(0.25)
                    now = collect_mtimes()
                    changed = [k for k, v in now.items() if last.get(k) != v]
                    if changed:
                        time.sleep(self.debounce_seconds)
                        print(f"Detected changes ({len(changed)} file(s))")
                        self.compile_and_run()
                        last = collect_mtimes()
            except KeyboardInterrupt:
                print("\nStopping hot reload...")
                self.running = False
            finally:
                self.cleanup()

    def run_once(self) -> bool:
        """Run compilation once without hot reload."""
        return self.compile_and_run()


def create_jit_template(flow_file: str) -> str:
    """Create a JIT-ready FLOW template with hot reload hooks."""
    return f"""
# JIT Hot Reload Example
# Auto-generated for {flow_file}

@only(hot, jit)
function main() -> i32 {{
    printf("🔥 FLOW JIT Running...\\n")
    return 42
}}
"""


def main():
    import argparse

    parser = argparse.ArgumentParser(description="FLOW JIT Runner with Hot Reload")
    parser.add_argument("input", help="FLOW file to JIT compile")
    parser.add_argument("--watch", help="Directory to watch for changes (default: file directory)")
    parser.add_argument("--once", action="store_true", help="Run once without hot reload")
    parser.add_argument("--template", action="store_true", help="Generate JIT template")

    args = parser.parse_args()

    if args.template:
        print(create_jit_template(args.input))
        return

    runner = FlowJITRunner(args.input, args.watch, hot_mode=not args.once)

    if args.once:
        success = runner.run_once()
        sys.exit(0 if success else 1)
    else:
        runner.start_hot_reload()


if __name__ == "__main__":
    main()