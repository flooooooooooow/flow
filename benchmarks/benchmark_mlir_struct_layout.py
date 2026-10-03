#!/usr/bin/env python3
"""
Benchmark for MLIRGenerator struct layout total size calculations.
"""

import time
from flow.mlir_generator import MLIRGenerator
from flow.parser import StructDecl, Parameter, Type, StructLiteral


def run_benchmark():
    decls = []
    # Create 500 struct declarations, each with 20 fields
    fields = [Parameter(f"field_{i}", Type("i32")) for i in range(20)]
    for s in range(500):
        decls.append(StructDecl(f"Struct_{s}", fields))

    generator = MLIRGenerator()
    generator._calculate_struct_layouts(decls)

    # Prepare a workload of 100,000 struct expression type lookups
    exprs = [StructLiteral(f"Struct_{s % 500}", []) for s in range(100000)]

    t0 = time.perf_counter()
    for expr in exprs:
        generator.get_expression_type(expr)
    t1 = time.perf_counter()

    elapsed_ms = (t1 - t0) * 1000.0
    print(f"Struct layout total size calculation time: {elapsed_ms:.2f} ms")
    return elapsed_ms


if __name__ == "__main__":
    run_benchmark()
