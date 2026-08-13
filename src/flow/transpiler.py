#!/usr/bin/env python3
"""
FLOW Language Transpiler
Main entry point for transpiling FLOW to MLIR/LLVMIR
With module system and GPU integration
"""

import sys
import argparse
from pathlib import Path
from .parser import (
    FunctionDecl,
    EffectDecl,
    CapabilityDecl,
    StructDecl,
)
from .mlir_generator import flow_to_mlir
from .c_generator import flow_to_c
from .module_resolver import resolve_modules, get_module_resolver
from .gpu_integration import get_gpu_integration
from .type_checker import TypeChecker
from .monomorphize import monomorphize


def _parse_decorator(attr: str) -> tuple[str, list[str]]:
    if "(" in attr and attr.endswith(")"):
        name, rest = attr.split("(", 1)
        args = [a.strip() for a in rest[:-1].split(",") if a.strip()]
        return name, args
    return attr, []


def _active_modes(args, backend: str) -> set[str]:
    if args.mode:
        base = {args.mode}
    else:
        if args.hot_reload:
            base = {"hot", "jit"}
        elif args.jit:
            base = {"jit"}
        else:
            base = {"compile"}
    base.add(backend)
    if backend == "mlir":
        base.add("compile")
    if backend == "c":
        base.add("compile")
    return base


def mlir_opt_kwargs_from_args(args) -> dict:
    """Map CLI `--no-*` / `--opt-level` flags to MLIROptimizer.optimize kwargs."""
    return {
        "enable_vectorization": not getattr(args, "no_vectorization", False),
        "enable_loop_fusion": not getattr(args, "no_loop_fusion", False),
        "enable_mem2reg": not getattr(args, "no_mem2reg", False),
        "enable_sccp": not getattr(args, "no_sccp", False),
        "enable_licm": not getattr(args, "no_licm", False),
        "enable_gvn": not getattr(args, "no_cse", False),
        "enable_dce": not getattr(args, "no_dce", False),
        "enable_inline": not getattr(args, "no_inline", False),
        "optimization_level": getattr(args, "opt_level", "O2"),
    }


def _function_allowed(fn: FunctionDecl, active_modes: set[str]) -> bool:
    attrs = getattr(fn, "attributes", []) or []
    guard_modes: list[str] = []
    has_guard = False

    for attr in attrs:
        name, args = _parse_decorator(attr)
        if name in ("only", "guard"):
            has_guard = True
            guard_modes.extend(args)
        elif name in active_modes or name in ("hot", "jit", "compile", "interp", "mlir", "c"):
            has_guard = True
            guard_modes.append(name)

    if not has_guard:
        return True
    return any(mode in active_modes for mode in guard_modes)


def _filter_declarations(declarations, active_modes: set[str]):
    filtered = []
    for decl in declarations:
        if isinstance(decl, FunctionDecl):
            if not _function_allowed(decl, active_modes):
                continue
        filtered.append(decl)
    return filtered


def main():
    parser = argparse.ArgumentParser(description="FLOW Language Transpiler")
    parser.add_argument("input", nargs="?", help="Input FLOW file")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument("--mlir", action="store_true", help="Output MLIR (default)")
    parser.add_argument("--c", action="store_true", help="Output C code")
    parser.add_argument(
        "--llvm", action="store_true", help="Output LLVM IR (requires mlir-opt)"
    )
    parser.add_argument(
        "--wasm32",
        action="store_true",
        help="ILP32/wasm32 ABI: lower libc size_t/long as i32 in MLIR (for emcc)",
    )
    parser.add_argument(
        "--optimize", action="store_true", help="Run MLIR optimizations"
    )
    parser.add_argument("--verify", action="store_true", help="Verify generated MLIR")
    parser.add_argument("--jit", action="store_true", help="JIT compile and execute")
    parser.add_argument(
        "--hot-reload", action="store_true", help="Enable hot reload with JIT"
    )
    parser.add_argument(
        "--watch", help="Directory to watch for hot reload (default: file directory)"
    )
    parser.add_argument(
        "--debug-info", action="store_true", help="Emit DWARF debug info in MLIR"
    )
    parser.add_argument(
        "--strict-effects",
        action="store_true",
        help="Abort on unhandled effect ops (also: FLOW_STRICT_EFFECTS=1 at runtime)",
    )
    parser.add_argument(
        "--opt-level",
        choices=["O0", "O1", "O2", "O3"],
        default="O2",
        help="Optimization level (default: O2)",
    )
    parser.add_argument(
        "--no-vectorization", action="store_true", help="Disable loop vectorization"
    )
    parser.add_argument(
        "--no-loop-fusion", action="store_true", help="Disable loop fusion"
    )
    parser.add_argument(
        "--no-mem2reg", action="store_true", help="Disable mem2reg (O2+)"
    )
    parser.add_argument(
        "--no-sccp", action="store_true", help="Disable SCCP (O2+)"
    )
    parser.add_argument(
        "--no-licm", action="store_true", help="Disable loop-invariant code motion (O2+)"
    )
    parser.add_argument(
        "--no-cse",
        action="store_true",
        help="Disable CSE (GVN stand-in; O1+)",
    )
    parser.add_argument(
        "--no-dce", action="store_true", help="Disable symbol-dce + canonicalize (O1+)"
    )
    parser.add_argument(
        "--no-inline", action="store_true", help="Disable module inliner (O2+)"
    )
    parser.add_argument(
        "--print-pass-pipeline",
        action="store_true",
        help="Print the mlir-opt --pass-pipeline for the selected flags and exit",
    )
    parser.add_argument(
        "--opt-report", action="store_true", help="Generate optimization report"
    )
    parser.add_argument("--gpu", action="store_true", help="Enable GPU compilation")
    parser.add_argument(
        "--gpu-backend",
        choices=["cuda", "opencl"],
        default="cuda",
        help="GPU backend (default: cuda)",
    )
    parser.add_argument(
        "--mlir-gpu",
        action="store_true",
        help="Emit MLIR GPU dialect for @gpu functions",
    )
    parser.add_argument(
        "--emit-spirv",
        action="store_true",
        help="Lower MLIR GPU module to SPIR-V (requires mlir-opt/mlir-translate)",
    )
    parser.add_argument(
        "--spirv-out",
        help="SPIR-V output path (default: build/<input>.spv)",
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help=(
            "Print the selected compilation plan for every declarative "
            "construct (sort, find): what was considered, each cost, the "
            "choice, and the constraint each rejected candidate failed"
        ),
    )
    parser.add_argument(
        "--module-info", action="store_true", help="Show module information"
    )
    parser.add_argument(
        "--validate-imports", action="store_true", help="Validate import statements"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=True,
        help="Strict type checking (default)",
    )
    parser.add_argument(
        "--lenient", action="store_true", help="Lenient type checking (warnings only)"
    )
    parser.add_argument(
        "--library",
        action="store_true",
        help="Emit a linkable runtime/library TU (static _ui_state, no name mangling)",
    )
    parser.add_argument(
        "--no-bounds-check",
        action="store_true",
        help="Disable runtime array bounds checks (for performance-critical builds)",
    )
    parser.add_argument(
        "--python", action="store_true", help="Generate Python package (wheel)"
    )
    parser.add_argument(
        "--python-name", help="Python module name (default: input filename)"
    )
    parser.add_argument(
        "--python-version", default="0.1.0", help="Python package version"
    )
    parser.add_argument(
        "--python-source-only",
        action="store_true",
        help="Generate C extension source without building wheel",
    )
    parser.add_argument(
        "--mode",
        choices=["compile", "jit", "hot", "interp", "mlir", "c"],
        help="Guard mode for @only/@guard decorators (default: inferred)",
    )
    parser.add_argument(
        "--export",
        nargs="*",
        default=[],
        help="Function names to export with stable C symbols (for WASM/FFI). "
        "Use --export foo bar to export foo() and bar() as flow_export_foo / flow_export_bar.",
    )
    parser.add_argument(
        "--module-name",
        help="Module name for WASM/Python package (default: input filename stem). "
        "Sets the Emscripten MODULARIZE name and the --export prefix.",
    )

    args = parser.parse_args()

    if getattr(args, "print_pass_pipeline", False):
        from .mlir_optimizer import MLIROptimizer

        print(MLIROptimizer.build_pass_pipeline(**mlir_opt_kwargs_from_args(args)))
        sys.exit(0)

    if not args.input:
        parser.error("the following arguments are required: input")

    if args.c and args.llvm:
        print("Error: --llvm is only valid for MLIR backend (remove --c).", file=sys.stderr)
        sys.exit(1)

    # --lenient overrides --strict
    strict_mode = args.strict
    if args.lenient:
        strict_mode = False

    # Read input file
    try:
        with open(args.input, "r") as f:
            f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Resolve modules and imports
    try:
        print("Resolving modules...", file=sys.stderr)
        declarations = resolve_modules(args.input)

        # Process @cImport directives: parse C headers and generate externs
        from .c_header_parser import resolve_c_imports
        import os as _os
        source_dir = _os.path.dirname(_os.path.abspath(args.input))
        declarations = resolve_c_imports(declarations, source_dir)

        # Decide backend early so mode filtering can use it.
        backend = "mlir"
        if args.c:
            backend = "c"

        active_modes = _active_modes(args, backend)
        declarations = _filter_declarations(declarations, active_modes)

        # Type checking phase
        type_checker = TypeChecker()
        # Wire CLI --strict/--lenient into checker policy (bool↔numeric,
        # immutable assign, non-bool if/while, unknown annotations, …).
        type_checker.strict = strict_mode
        # --strict-effects enables compile-time effect-row checking (Phase 1)
        # in addition to runtime abort on unhandled ops.
        if getattr(args, "strict_effects", False):
            type_checker.check_effect_rows = True
        type_result = type_checker.check(declarations)

        if type_result.errors:
            if strict_mode:
                print("Type errors:", file=sys.stderr)
                for error in type_result.errors[:10]:
                    print(f"  ✗ {error}", file=sys.stderr)
                if len(type_result.errors) > 10:
                    print(
                        f"  ... and {len(type_result.errors) - 10} more",
                        file=sys.stderr,
                    )
                print(
                    f"\n{len(type_result.errors)} type error(s). Use --lenient to compile anyway.",
                    file=sys.stderr,
                )
                sys.exit(1)
            else:
                print("Type warnings (lenient mode):", file=sys.stderr)
                for error in type_result.errors[:5]:
                    print(f"  ⚠ {error}", file=sys.stderr)
                if len(type_result.errors) > 5:
                    print(
                        f"  ... and {len(type_result.errors) - 5} more", file=sys.stderr
                    )

        # Monomorphization pass: expand generics to concrete types
        declarations = monomorphize(declarations)
        declarations = _filter_declarations(declarations, active_modes)

        functions = [d for d in declarations if isinstance(d, FunctionDecl)]
        structs = [d for d in declarations if isinstance(d, StructDecl)]
        effects = [d for d in declarations if isinstance(d, EffectDecl)]
        capabilities = [d for d in declarations if isinstance(d, CapabilityDecl)]

        print(
            f"Parsed {len(functions)} functions, {len(structs)} structs, {len(effects)} effects, {len(capabilities)} capabilities",
            file=sys.stderr,
        )

        # Show module information if requested
        if args.module_info:
            resolver = get_module_resolver(args.input)
            print("\nModule Information:", file=sys.stderr)
            for module_path, module_info in resolver.modules.items():
                print(f"  Module: {module_path}", file=sys.stderr)
                print(
                    f"    Dependencies: {len(module_info.dependencies)}",
                    file=sys.stderr,
                )
                print(f"    Symbols: {len(module_info.symbols)}", file=sys.stderr)
                exported_symbols = [
                    name
                    for name, symbol in module_info.symbols.items()
                    if symbol.is_exported
                ]
                print(f"    Exported: {len(exported_symbols)}", file=sys.stderr)

        # Validate imports if requested
        if args.validate_imports:
            resolver = get_module_resolver(args.input)
            errors = resolver.validate_imports()
            if errors:
                print("Import validation errors:", file=sys.stderr)
                for error in errors:
                    print(f"  - {error}", file=sys.stderr)
                if len(errors) > 0:
                    sys.exit(1)
            else:
                print("All imports validated successfully", file=sys.stderr)

    except Exception as e:
        print(f"Error resolving modules: {e}", file=sys.stderr)
        sys.exit(1)

    # GPU integration if requested
    if args.gpu:
        try:
            gpu_integration = get_gpu_integration()
            if gpu_integration.is_gpu_available():
                print(
                    f"GPU available: {gpu_integration.get_gpu_info()}", file=sys.stderr
                )

                # Compile functions for GPU
                gpu_functions = []
                for func in functions:
                    # Mark functions that should run on GPU
                    if hasattr(func, "name") and (
                        "gpu_" in func.name or "cuda_" in func.name
                    ):
                        gpu_functions.append(func)

                if gpu_functions:
                    print(
                        f"Compiling {len(gpu_functions)} functions for GPU",
                        file=sys.stderr,
                    )
                    for func in gpu_functions:
                        try:
                            result = gpu_integration.compile_and_execute(func, [])
                            print(
                                f"GPU function {func.name}: {result}", file=sys.stderr
                            )
                        except Exception as e:
                            print(
                                f"GPU compilation failed for {func.name}: {e}",
                                file=sys.stderr,
                            )
                else:
                    print("No GPU functions found", file=sys.stderr)
            else:
                print("GPU not available", file=sys.stderr)
        except Exception as e:
            print(f"GPU integration error: {e}", file=sys.stderr)

    # Handle Python target separately
    if args.python:
        try:
            from .python_generator import PythonTarget
            from pathlib import Path as PyPath

            # Determine module name
            module_name = args.python_name
            if not module_name:
                module_name = (
                    PyPath(args.input).stem.replace("-", "_").replace(".", "_")
                )

            # Create Python target
            target = PythonTarget(
                declarations,
                module_name=module_name,
                version=args.python_version,
                verbose=True,
            )

            # Print export analysis
            target.print_diagnostics()

            # Compile
            target.compile()

            # Output
            if args.output:
                output_dir = PyPath(args.output)
            else:
                output_dir = PyPath("dist")

            output_dir.mkdir(parents=True, exist_ok=True)

            if args.python_source_only:
                # Just generate C extension source
                ext_path = output_dir / f"{module_name}_ext.c"
                target.write_extension_source(ext_path)
                print(f"✅ Generated: {ext_path}")
            else:
                # Build wheel
                try:
                    wheel_path = target.build_wheel(output_dir)
                    print(f"✅ Built wheel: {wheel_path}")
                    print(f"   Install with: pip install {wheel_path}")
                except Exception as e:
                    print(f"⚠️  Wheel build failed: {e}")
                    print("   Falling back to source-only output...")
                    ext_path = output_dir / f"{module_name}_ext.c"
                    target.write_extension_source(ext_path)
                    print(f"   Generated: {ext_path}")

            sys.exit(0)

        except Exception as e:
            print(f"Python generation error: {e}", file=sys.stderr)
            import traceback

            traceback.print_exc()
            sys.exit(1)

    # Decide backend (may have been inferred earlier)
    backend = "mlir"  # Default backend
    if args.c:
        backend = "c"

    if backend == "c":
        try:
            # For the C backend, reuse --debug-info to emit coarse source mappings
            # (via C preprocessor #line directives) for LLDB/GDB.
            src_path = args.input
            if args.debug_info:
                try:
                    src_path = str(Path(args.input).resolve())
                except Exception:
                    src_path = args.input
            out_code = flow_to_c(
                declarations,
                source_file=src_path,
                debug_info=args.debug_info,
                strict_effects=args.strict_effects,
                library=args.library,
                no_bounds_check=getattr(args, "no_bounds_check", False),
                export_names=getattr(args, "export", None),
                module_name=getattr(args, "module_name", None),
            )
            if getattr(args, "explain", False):
                from .plan_selector import format_selections

                selections = getattr(flow_to_c, "last_selections", []) or []
                print(
                    format_selections(selections, source=args.input),
                    file=sys.stderr,
                )
            overload_warnings = getattr(flow_to_c, "last_warnings", None)
            if overload_warnings:
                print("Overload resolution warnings:", file=sys.stderr)
                for warning in overload_warnings[:10]:
                    print(f"  ⚠ {warning}", file=sys.stderr)
                if len(overload_warnings) > 10:
                    print(
                        f"  ... and {len(overload_warnings) - 10} more",
                        file=sys.stderr,
                    )
        except Exception as e:
            print(f"C generation error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Generate MLIR
        try:
            source_file = Path(args.input).name
            out_code = flow_to_mlir(
                declarations,
                source_file=source_file,
                emit_debug_info=args.debug_info,
                emit_gpu=args.mlir_gpu,
                size_t_bits=32 if args.wasm32 else 64,
            )

            # Apply optimizations if requested
            if args.optimize:
                from .mlir_optimizer import MLIROptimizer
                import tempfile

                # Write generated MLIR to temp file
                tmp_path = None
                try:
                    with tempfile.NamedTemporaryFile(
                        mode="w", suffix=".mlir", delete=False
                    ) as tmp:
                        tmp.write(out_code)
                        tmp_path = tmp.name

                    # Optimize
                    optimizer = MLIROptimizer()
                    opt_kwargs = mlir_opt_kwargs_from_args(args)
                    opt_result = optimizer.optimize(
                        tmp_path,
                        tmp_path,
                        **opt_kwargs,
                    )

                    if opt_result != 0:
                        print("MLIR optimization failed", file=sys.stderr)
                        sys.exit(1)

                    # Read optimized MLIR
                    with open(tmp_path, "r") as f:
                        out_code = f.read()

                    # Generate optimization report if requested
                    if args.opt_report:
                        report = optimizer.get_optimization_report(
                            tmp_path, **opt_kwargs
                        )
                        print(report, file=sys.stderr)
                finally:
                    if tmp_path and Path(tmp_path).exists():
                        Path(tmp_path).unlink()

        except Exception as e:
            print(f"MLIR generation error: {e}", file=sys.stderr)
            sys.exit(1)

        # Optional: Lower MLIR to LLVM IR
        if args.llvm:
            try:
                from .mlir_jit import MLIRJIT
                jit = MLIRJIT()
                try:
                    out_code = jit.compile_mlir_to_llvm(out_code)
                finally:
                    jit.cleanup()
            except Exception as e:
                print(f"LLVM IR generation failed: {e}", file=sys.stderr)
                sys.exit(1)

    # Optional: Lower GPU module to SPIR-V
    if backend != "c" and args.emit_spirv:
        try:
            from .mlir_spirv import MLIRSPIRVCompiler

            spirv_out = args.spirv_out
            if not spirv_out:
                out_base = Path(args.input).stem + ".spv"
                spirv_out = str(Path("build") / out_base)
            Path(spirv_out).parent.mkdir(parents=True, exist_ok=True)
            compiler = MLIRSPIRVCompiler()
            compiler.compile_mlir_to_spirv(out_code, spirv_out)
            print(f"Generated SPIR-V: {spirv_out}", file=sys.stderr)
        except Exception as e:
            print(f"SPIR-V generation failed: {e}", file=sys.stderr)
            sys.exit(1)

    # Handle JIT execution
    if args.jit or args.hot_reload:
        # Import JIT modules lazily so optional deps (e.g. watchdog/mlir toolchain) don't break normal usage.
        from .jit_runner import FlowJITRunner
        from .mlir_jit import MLIRJIT

        if args.hot_reload:
            runner = FlowJITRunner(args.input, args.watch, hot_mode=True)
            runner.start_hot_reload()
            return
        else:
            jit = MLIRJIT()
            try:
                result = jit.jit_compile_and_run(out_code, "main")
                if result is not None:
                    print(f"JIT exit code: {result}", file=sys.stderr)
                else:
                    print("JIT execution failed", file=sys.stderr)
                    print(
                        "Requires mlir-opt, mlir-translate, and clang on PATH.",
                        file=sys.stderr,
                    )
                    sys.exit(1)
            finally:
                jit.cleanup()
            return

    # Output handling
    if args.output:
        try:
            with open(args.output, "w") as f:
                f.write(out_code)
            if backend == "c":
                print(f"Generated C written to {args.output}", file=sys.stderr)
            elif args.llvm:
                print(f"Generated LLVM IR written to {args.output}", file=sys.stderr)
            else:
                print(f"Generated MLIR written to {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(out_code)


if __name__ == "__main__":
    main()
