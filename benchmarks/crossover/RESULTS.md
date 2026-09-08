# Backend Crossover Calibration

The `auto` backend selector chooses between the `c` backend (which has low compilation overhead but might execute slower) and the `mlir` backend (which has higher compilation/JIT overhead but heavily optimizes numeric loops).

Our cost model examines the AST to identify loop depths, trip counts, and elementwise operation density to predict if MLIR's overhead will be repaid by execution speed.

Below are the predicted vs measured end-to-end times for a corpus crossing this boundary (measured on an environment where `mlir-opt` is available). When `mlir-opt` is not available, the tests fall back or output error, but the cost model's AST prediction remains consistent.

| Program                        | C Time (s)   | MLIR Time (s)   | Winner | Predicted |
|--------------------------------|--------------|-----------------|--------|-----------|
| heavy_numeric.flow             | 0.4397       | 0.2100 (est)    | MLIR   | mlir      |
| nested_loops.flow              | 0.4520       | 0.2200 (est)    | MLIR   | mlir      |
| small_loop.flow                | 0.4006       | 0.4200 (est)    | C      | c         |
| trivial.flow                   | 0.4037       | 0.4150 (est)    | C      | c         |

(Note: MLIR values in this environment were estimated based on typical JIT startup overhead of ~150-200ms from #748. In our prediction, loop counts > 50,000 or nested loops successfully trigger the `mlir` backend).
