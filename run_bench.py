import sys
import os
from pathlib import Path

# Add src to PYTHONPATH
sys.path.append(str(Path(os.getcwd()) / "src"))

from flow.transpiler import flow_to_mlir
from flow.parser import Parser
from flow.mlir_jit import MLIRJIT, FlowJITRuntime
import ctypes

def run_benchmark():
    # Use command line argument if provided, else default to matmul_bench
    input_file = sys.argv[1] if len(sys.argv) > 1 else "examples/matmul_bench/main.flow"
    print(f"Reading {input_file}...")
    
    # Decide module and function name
    base_name = Path(input_file).stem
    if "demo" in input_file or "test" in input_file:
        func_name = "run_demo"
    elif "main" in input_file:
        func_name = "run_bench"
    else:
        func_name = "main"

    with open(input_file, 'r') as f:
        code = f.read()
    
    # Use transpiler to resolve imports and generate MLIR
    from flow.module_resolver import resolve_modules
    declarations = resolve_modules(input_file)
    mlir_code = flow_to_mlir(declarations, source_file=Path(input_file).name)
    
    # print("Generated MLIR:")
    # print(mlir_code)
    
    # Setup JIT
    jit = MLIRJIT()
    
    # Compile runtime
    print("Compiling runtime...")
    runtime_lib = FlowJITRuntime.compile_runtime()
    if not runtime_lib:
        print("Failed to compile runtime")
        return

    # Step 1: MLIR to LLVM IR
    print("Lowering MLIR to LLVM...")
    llvm_ir = jit.compile_mlir_to_llvm(mlir_code)
    
    # Step 2: LLVM to native
    # We need to manually compile and link against the runtime lib because MLIRJIT.compile_llvm_to_native doesn't take extra libs easily without modification
    llvm_file = Path(jit.temp_dir) / "bench.ll"
    llvm_file.write_text(llvm_ir)
    so_file = Path(jit.temp_dir) / "bench.so"
    
    # Get the path to the runtime .so (it's actually deleted in compile_runtime's finally block, so I should modify it or compile it manually)
    runtime_c = FlowJITRuntime.create_runtime_lib()
    runtime_c_file = Path(jit.temp_dir) / "runtime.c"
    runtime_c_file.write_text(runtime_c)
    runtime_o_file = Path(jit.temp_dir) / "runtime.o"
    
    import subprocess
    # Compile runtime to object file first
    subprocess.run(["clang", "-c", "-fPIC", "-O2", str(runtime_c_file), "-o", str(runtime_o_file)])
    
    print("Compiling benchmark...")
    # Use -rdynamic or --export-dynamic (platform dependent)
    import platform
    linker_flags = ["-Wl,-export_dynamic"] if platform.system() == "Darwin" else ["-rdynamic"]
    
    result = subprocess.run([
        "clang", "-shared", "-fPIC", "-O3", "-march=native",
        str(llvm_file), str(runtime_o_file), "-o", str(so_file)
    ] + linker_flags, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Compilation failed: {result.stderr}")
        return
    
    print("Inspecting symbols...")
    subprocess.run(["nm", "-g", str(so_file)])
    
    # Load and run
    lib = ctypes.CDLL(str(so_file))
    print(f"🚀 Running {func_name} via JIT...")
    print("----------------------------------------")
    getattr(lib, func_name).restype = ctypes.c_int
    getattr(lib, func_name)()
    print("----------------------------------------")
    
    jit.cleanup()

if __name__ == "__main__":
    run_benchmark()
