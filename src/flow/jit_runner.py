#!/usr/bin/env python3
"""
FLOW JIT Runner
Hot reload and JIT execution using MLIR's JIT execution engine
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    _HAS_WATCHDOG = True
except Exception:
    Observer = None
    FileSystemEventHandler = object
    _HAS_WATCHDOG = False

class FlowJITRunner:
    def __init__(self, flow_file: str, watch_dir: Optional[str] = None, *, hot_mode: bool = False):
        self.flow_file = Path(flow_file)
        self.watch_dir = Path(watch_dir) if watch_dir else self.flow_file.parent
        self.hot_mode = hot_mode
        # Repo root is two levels above this file: src/flow/jit_runner.py -> repo/
        self.repo_root = Path(__file__).resolve().parents[2]
        self.src_root = self.repo_root / 'src'
        self.process: Optional[subprocess.Popen] = None
        self.last_compile_time = 0
        self.debounce_seconds = 0.5  # Debounce file changes
        self.running = True
        
        # JIT compilation cache
        self.compilation_cache: Dict[str, Any] = {}
        
    def compile_and_run(self):
        """Compile FLOW to MLIR and execute via JIT"""
        try:
            env = os.environ.copy()
            existing_pp = env.get('PYTHONPATH', '')
            src_path = str(self.src_root)
            env['PYTHONPATH'] = src_path if not existing_pp else f"{src_path}:{existing_pp}"

            # Compile to MLIR
            mode = "hot" if self.hot_mode else "jit"
            result = subprocess.run([
                sys.executable, '-m', 'flow.transpiler',
                str(self.flow_file), '--mlir', '--mode', mode
            ], capture_output=True, text=True, cwd=str(self.repo_root), env=env)
            
            if result.returncode != 0:
                print(f"❌ Compilation failed: {result.stderr}")
                return False
            
            
            # For now, just print the MLIR (real JIT would use MLIR ExecutionEngine)
            # print(f"🔥 JIT Compiled {self.flow_file.name}")
            # print("=" * 50)
            # print(mlir_code)
            # print("=" * 50)
            
            # TODO: Real MLIR JIT execution
            # This would use MLIR's ExecutionEngine to compile and run
            # mlir_context = mlir.create_context()
            # mlir_module = mlir.parse(mlir_code, mlir_context)
            # execution_engine = mlir.ExecutionEngine(mlir_module)
            # result = execution_engine.invoke("main")
            
            return True
            
        except Exception as e:
            print(f"❌ JIT error: {e}")
            return False
    
    def start_hot_reload(self):
        """Start file watcher for hot reload"""
        if _HAS_WATCHDOG:
            class FlowFileHandler(FileSystemEventHandler):
                def __init__(self, runner):
                    self.runner = runner
                    self.last_modified = {}
                    
                def on_modified(self, event):
                    if event.is_directory:
                        return
                        
                    file_path = Path(event.src_path)
                    if file_path.suffix == '.flow' or file_path.name == 'flow':
                        current_time = time.time()
                        last_time = self.last_modified.get(str(file_path), 0)
                        
                        # Debounce rapid file changes
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
                
                # Initial compilation
                self.compile_and_run()
                
                while self.running:
                    time.sleep(0.1)
                    
            except KeyboardInterrupt:
                print("\nStopping hot reload...")
                self.running = False
            finally:
                observer.stop()
                observer.join()
        else:
            # Fallback: polling-based watcher (no external deps)
            print("FLOW JIT Hot Reload started (polling mode)")
            print(f"Watching: {self.watch_dir}")
            print(f"Target: {self.flow_file}")
            print("Tip: install 'watchdog' for faster hot reload.")
            print("Press Ctrl+C to stop")

            def collect_mtimes() -> Dict[str, float]:
                mtimes: Dict[str, float] = {}
                for p in self.watch_dir.rglob('*.flow'):
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
                        # Debounce
                        time.sleep(self.debounce_seconds)
                        print(f"Detected changes ({len(changed)} file(s))")
                        self.compile_and_run()
                        last = collect_mtimes()
            except KeyboardInterrupt:
                print("\nStopping hot reload...")
                self.running = False
    
    def run_once(self):
        """Run compilation once without hot reload"""
        return self.compile_and_run()

def create_jit_template(flow_file: str) -> str:
    """Create a JIT-ready FLOW template with hot reload hooks"""
    template = f"""
# JIT Hot Reload Example
# Auto-generated for {flow_file}

# Import JIT runtime functions (would be built-in)
extern "jit" {{
    function jit_print(message: string) -> void
    function jit_time() -> f64
    function jit_reload_check() -> bool
}}

# Main function with JIT hooks
function main() -> i32 {{
    jit_print("🔥 FLOW JIT Running...")
    
    let start_time: f64 = jit_time()
    
    # Your code here
    let result: i32 = 42
    
    let end_time: f64 = jit_time()
    jit_print("⚡ Execution time: " + (end_time - start_time) + "s")
    
    return result
}}
"""
    return template

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="FLOW JIT Runner with Hot Reload")
    parser.add_argument("input", help="FLOW file to JIT compile")
    parser.add_argument("--watch", help="Directory to watch for changes (default: file directory)")
    parser.add_argument("--once", action="store_true", help="Run once without hot reload")
    parser.add_argument("--template", action="store_true", help="Generate JIT template")
    
    args = parser.parse_args()
    
    if args.template:
        template = create_jit_template(args.input)
        print(template)
        return
    
    runner = FlowJITRunner(args.input, args.watch, hot_mode=not args.once)
    
    if args.once:
        success = runner.run_once()
        sys.exit(0 if success else 1)
    else:
        runner.start_hot_reload()

if __name__ == "__main__":
    main()
