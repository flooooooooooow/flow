# Runtime Tests

This directory contains FLOW programs that are compiled, executed, and validated
for correct behavior.

## Test Contract

Each `.flow` file must:
- Have a `main()` function that returns `i32`
- Return `0` on success (test passes)
- Return non-zero on failure (test fails)

## Optional Output Validation

If a file `foo.expected` exists alongside `foo.flow`, the test runner will
compare stdout against the expected content.

## Running Tests

```bash
# Run all runtime tests
./flow test-runtime

# Run a specific test
./flow test-runtime tests/runtime/test_arithmetic.flow
```

## Test Categories

- `test_arithmetic.flow` - Basic math operations
- `test_control_flow.flow` - if/else, while, for loops
- `test_functions.flow` - Function calls, recursion
- `test_structs.flow` - Struct creation, field access
- `test_arrays.flow` - Array indexing, bounds
- `test_generics.flow` - Monomorphization correctness
- `test_match.flow` - Pattern matching
- `test_effects.flow` - Effect handler scoping
