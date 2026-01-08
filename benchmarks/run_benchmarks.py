#!/usr/bin/env python3
"""
Performance Benchmark Runner for FLOW vs C
Compares performance between FLOW and C implementations on CPU and GPU
"""

import sys
import os
import subprocess
import time
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Add src to PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent / "src"))

from flow.transpiler import flow_to_mlir
from flow.parser import Parser
from flow.mlir_jit import MLIRJIT, FlowJITRuntime
import ctypes

class BenchmarkRunner:
    """Main benchmark runner class."""
    
    def __init__(self):
        self.results = {}
        self.temp_dir = Path("/tmp/flow_benchmarks")
        self.temp_dir.mkdir(exist_ok=True)
        
    def compile_c_benchmark(self) -> Tuple[bool, str]:
        """Compile C benchmark executable."""
        print("🔨 Compiling C benchmarks...")
        
        c_file = Path(__file__).parent / "c_benchmarks.c"
        exe_file = self.temp_dir / "c_benchmarks"
        
        try:
            # Compile with optimization flags
            result = subprocess.run([
                "clang", "-O3", "-march=native", "-lm",
                str(c_file), "-o", str(exe_file)
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print(f"❌ C compilation failed: {result.stderr}")
                return False, result.stderr
            
            print("✅ C benchmarks compiled successfully")
            return True, str(exe_file)
            
        except subprocess.TimeoutExpired:
            return False, "C compilation timed out"
        except Exception as e:
            return False, f"C compilation error: {e}"
    
    def compile_flow_benchmark(self) -> Tuple[bool, str]:
        """Compile FLOW benchmark executable."""
        print("🔨 Compiling FLOW benchmarks...")
        
        flow_file = Path(__file__).parent / "main.flow"
        exe_file = self.temp_dir / "flow_benchmarks"
        
        try:
            # Use the existing transpiler pipeline
            from flow.module_resolver import resolve_modules
            declarations = resolve_modules(str(flow_file))
            mlir_code = flow_to_mlir(declarations, source_file=flow_file.name)
            
            # Setup JIT
            jit = MLIRJIT()
            
            # Compile runtime
            runtime_lib = FlowJITRuntime.compile_runtime()
            if not runtime_lib:
                return False, "Failed to compile runtime"
            
            # MLIR to LLVM IR
            llvm_ir = jit.compile_mlir_to_llvm(mlir_code)
            
            # LLVM to native
            llvm_file = Path(jit.temp_dir) / "bench.ll"
            llvm_file.write_text(llvm_ir)
            so_file = Path(jit.temp_dir) / "bench.so"
            
            # Create runtime C code
            runtime_c = FlowJITRuntime.create_runtime_lib()
            runtime_c_file = Path(jit.temp_dir) / "runtime.c"
            runtime_c_file.write_text(runtime_c)
            runtime_o_file = Path(jit.temp_dir) / "runtime.o"
            
            # Compile runtime
            subprocess.run(["clang", "-c", "-fPIC", "-O2", str(runtime_c_file), "-o", str(runtime_o_file)])
            
            # Link final executable
            import platform
            linker_flags = ["-Wl,-export_dynamic"] if platform.system() == "Darwin" else ["-rdynamic"]
            
            result = subprocess.run([
                "clang", "-shared", "-fPIC", "-O3", "-march=native",
                str(llvm_file), str(runtime_o_file), "-o", str(so_file)
            ] + linker_flags, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ FLOW compilation failed: {result.stderr}")
                return False, result.stderr
            
            print("✅ FLOW benchmarks compiled successfully")
            jit.cleanup()
            return True, str(so_file)
            
        except Exception as e:
            return False, f"FLOW compilation error: {e}"
    
    def run_c_benchmarks(self, exe_path: str) -> Dict[str, float]:
        """Run C benchmarks and collect results."""
        print("🚀 Running C benchmarks...")
        
        try:
            result = subprocess.run([exe_path], capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                print(f"❌ C benchmark execution failed: {result.stderr}")
                return {}
            
            # Parse results from output
            results = self.parse_benchmark_output(result.stdout, "C")
            print("✅ C benchmarks completed")
            return results
            
        except subprocess.TimeoutExpired:
            print("❌ C benchmarks timed out")
            return {}
        except Exception as e:
            print(f"❌ C benchmark error: {e}")
            return {}
    
    def run_flow_benchmarks(self, lib_path: str) -> Dict[str, float]:
        """Run FLOW benchmarks and collect results."""
        print("🚀 Running FLOW benchmarks...")
        
        try:
            lib = ctypes.CDLL(lib_path)
            lib.run_bench.restype = ctypes.c_int
            
            # Capture output using subprocess instead of ctypes redirect
            result = subprocess.run([
                "python3", str(Path(__file__).parent.parent / "run_bench.py"),
                str(Path(__file__).parent / "main.flow")
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                print(f"❌ FLOW benchmark execution failed: {result.stderr}")
                return {}
            
            output = result.stdout
            results = self.parse_benchmark_output(output, "FLOW")
            print("✅ FLOW benchmarks completed")
            return results
            
        except Exception as e:
            print(f"❌ FLOW benchmark error: {e}")
            return {}
    
    def parse_benchmark_output(self, output: str, language: str) -> Dict[str, float]:
        """Parse benchmark output and extract timing information."""
        results = {}
        
        for line in output.split('\n'):
            if ':' in line and ('seconds' in line or 'second' in line):
                try:
                    # Extract benchmark name and time
                    parts = line.split(':')
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        time_str = parts[1].strip()
                        
                        # Extract numeric time value
                        time_parts = time_str.split()
                        if time_parts:
                            time_val = float(time_parts[0])
                            results[f"{language}_{name}"] = time_val
                except (ValueError, IndexError):
                    continue
        
        return results
    
    def compare_results(self, c_results: Dict[str, float], flow_results: Dict[str, float]) -> None:
        """Compare and display benchmark results."""
        print("\n" + "="*80)
        print("🏁 PERFORMANCE COMPARISON RESULTS")
        print("="*80)
        
        # Find matching benchmarks
        comparisons = []
        
        for c_key, c_time in c_results.items():
            benchmark_name = c_key.replace("C_", "")
            flow_key = f"FLOW_{benchmark_name}"
            
            if flow_key in flow_results:
                flow_time = flow_results[flow_key]
                speedup = c_time / flow_time if flow_time > 0 else float('inf')
                comparisons.append((benchmark_name, c_time, flow_time, speedup))
        
        # Sort by speedup
        comparisons.sort(key=lambda x: x[3], reverse=True)
        
        # Display comparison table
        print(f"{'Benchmark':<35} {'C Time (s)':<12} {'FLOW Time (s)':<14} {'Speedup':<10}")
        print("-" * 75)
        
        total_c_time = 0
        total_flow_time = 0
        
        for name, c_time, flow_time, speedup in comparisons:
            print(f"{name:<35} {c_time:<12.6f} {flow_time:<14.6f} {speedup:<10.2f}x")
            total_c_time += c_time
            total_flow_time += flow_time
        
        print("-" * 75)
        overall_speedup = total_c_time / total_flow_time if total_flow_time > 0 else float('inf')
        print(f"{'OVERALL':<35} {total_c_time:<12.6f} {total_flow_time:<14.6f} {overall_speedup:<10.2f}x")
        
        # Save results to JSON
        results_data = {
            "timestamp": time.time(),
            "c_results": c_results,
            "flow_results": flow_results,
            "comparisons": [
                {
                    "benchmark": name,
                    "c_time": c_time,
                    "flow_time": flow_time,
                    "speedup": speedup
                }
                for name, c_time, flow_time, speedup in comparisons
            ],
            "summary": {
                "total_c_time": total_c_time,
                "total_flow_time": total_flow_time,
                "overall_speedup": overall_speedup
            }
        }
        
        results_file = Path(__file__).parent / "benchmark_results.json"
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\n📊 Results saved to: {results_file}")
        
        # Performance summary
        print("\n📈 PERFORMANCE SUMMARY:")
        if overall_speedup > 1.1:
            print(f"✅ FLOW is {overall_speedup:.2f}x faster than C overall")
        elif overall_speedup < 0.9:
            print(f"⚠️  FLOW is {1/overall_speedup:.2f}x slower than C overall")
        else:
            print("🤝 FLOW performance is comparable to C")
    
    def run_all_benchmarks(self, args) -> None:
        """Run complete benchmark suite."""
        print("🎯 Starting FLOW vs C Performance Benchmarks")
        print("=" * 50)
        
        # Compile benchmarks
        c_success, c_path = self.compile_c_benchmark()
        flow_success, flow_path = self.compile_flow_benchmark()
        
        if not c_success:
            print("❌ Failed to compile C benchmarks")
            return
        
        if not flow_success:
            print("❌ Failed to compile FLOW benchmarks")
            return
        
        # Run benchmarks
        c_results = self.run_c_benchmarks(c_path)
        flow_results = self.run_flow_benchmarks(flow_path)
        
        if not c_results:
            print("❌ No C benchmark results collected")
            return
        
        if not flow_results:
            print("❌ No FLOW benchmark results collected")
            return
        
        # Compare results
        self.compare_results(c_results, flow_results)
        
        # Cleanup
        try:
            if args.cleanup:
                import shutil
                shutil.rmtree(self.temp_dir)
                print(f"🧹 Cleaned up temporary files")
        except:
            pass

def main():
    parser = argparse.ArgumentParser(description="Run FLOW vs C performance benchmarks")
    parser.add_argument("--cleanup", action="store_true", help="Clean up temporary files after running")
    parser.add_argument("--c-only", action="store_true", help="Run only C benchmarks")
    parser.add_argument("--flow-only", action="store_true", help="Run only FLOW benchmarks")
    
    args = parser.parse_args()
    
    runner = BenchmarkRunner()
    runner.run_all_benchmarks(args)

if __name__ == "__main__":
    main()
