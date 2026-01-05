#!/usr/bin/env python3
"""
FLOW Language Transpiler
Main entry point for transpiling FLOW to MLIR/LLVMIR
"""

import sys
import argparse
from pathlib import Path
from .parser import parse_flow_code, FunctionDecl, EffectDecl, CapabilityDecl, StructDecl
from .mlir_generator import flow_to_mlir
from .c_generator import flow_to_c

def main():
    parser = argparse.ArgumentParser(description="FLOW Language Transpiler")
    parser.add_argument("input", help="Input FLOW file")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument("--mlir", action="store_true", help="Output MLIR (default)")
    parser.add_argument("--c", action="store_true", help="Output C code")
    parser.add_argument("--llvm", action="store_true", help="Output LLVM IR (requires mlir-opt)")
    parser.add_argument("--optimize", action="store_true", help="Run MLIR optimizations")
    parser.add_argument("--verify", action="store_true", help="Verify generated MLIR")
    parser.add_argument("--jit", action="store_true", help="JIT compile and execute")
    parser.add_argument("--hot-reload", action="store_true", help="Enable hot reload with JIT")
    parser.add_argument("--watch", help="Directory to watch for hot reload (default: file directory)")
    parser.add_argument("--debug-info", action="store_true", help="Emit DWARF debug info in MLIR")
    parser.add_argument("--opt-level", choices=["O0", "O1", "O2", "O3"], default="O2", help="Optimization level (default: O2)")
    parser.add_argument("--no-vectorization", action="store_true", help="Disable loop vectorization")
    parser.add_argument("--no-loop-fusion", action="store_true", help="Disable loop fusion")
    parser.add_argument("--opt-report", action="store_true", help="Generate optimization report")
    
    args = parser.parse_args()
    
    # Read input file
    try:
        with open(args.input, 'r') as f:
            flow_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Parse FLOW code
    try:
        declarations = parse_flow_code(flow_code)
        functions = [d for d in declarations if isinstance(d, FunctionDecl)]
        print(f"Parsed {len(functions)} functions", file=sys.stderr)
    except Exception as e:
        print(f"Parse error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Decide backend
    backend = "mlir"
    if args.c:
        backend = "c"

    if backend == "c":
        try:
            out_code = flow_to_c(functions)
        except Exception as e:
            print(f"C generation error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Generate MLIR
        try:
            source_file = Path(args.input).name
            out_code = flow_to_mlir(declarations, source_file=source_file, emit_debug_info=args.debug_info)
            
            # Apply optimizations if requested
            if args.optimize:
                from .mlir_optimizer import MLIROptimizer
                import tempfile
                
                # Write generated MLIR to temp file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.mlir', delete=False) as tmp:
                    tmp.write(out_code)
                    tmp_path = tmp.name
                
                # Optimize
                optimizer = MLIROptimizer()
                opt_result = optimizer.optimize(
                    tmp_path,
                    tmp_path,
                    enable_vectorization=not args.no_vectorization,
                    enable_loop_fusion=not args.no_loop_fusion,
                    optimization_level=args.opt_level
                )
                
                if opt_result != 0:
                    print("MLIR optimization failed", file=sys.stderr)
                    sys.exit(1)
                
                # Read optimized MLIR
                with open(tmp_path, 'r') as f:
                    out_code = f.read()
                
                # Generate optimization report if requested
                if args.opt_report:
                    report = optimizer.get_optimization_report(tmp_path)
                    print(report, file=sys.stderr)
                
                # Clean up
                Path(tmp_path).unlink()
                
        except Exception as e:
            print(f"MLIR generation error: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Handle JIT execution
    if args.jit or args.hot_reload:
        # Import JIT modules lazily so optional deps (e.g. watchdog/mlir toolchain) don't break normal usage.
        from .jit_runner import FlowJITRunner
        from .mlir_jit import MLIRJIT
        if args.hot_reload:
            # Start hot reload mode
            runner = FlowJITRunner(args.input, args.watch)
            runner.start_hot_reload()
            return
        else:
            # One-time JIT execution
            jit = MLIRJIT()
            try:
                result = jit.jit_compile_and_run(out_code, "main")
                if result is not None:
                    # print(f"JIT Result: {result}")
                    pass
                else:
                    print("JIT execution failed", file=sys.stderr)
                    sys.exit(1)
            finally:
                jit.cleanup()
            return
    
    # Output handling
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(out_code)
            if backend == "c":
                print(f"Generated C written to {args.output}", file=sys.stderr)
            else:
                print(f"Generated MLIR written to {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(out_code)

if __name__ == "__main__":
    main()
