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

Compiler-suite corpus (C-compiler-grade behavioral pins):

- `test_arithmetic_ops.flow`: integer arithmetic / compares
- `test_struct_ops.flow`: nested structs + field stores
- `test_array_ops.flow`: array read/write + sum
- `test_match_bool.flow`: bool match
- `test_recursion.flow`: recursion + mutual recursion
- `test_pointers.flow`: address-of + `ptr` field mutate
- `test_string_len.flow`: `strlen` extern
- `test_printf_hello.flow` + `.expected`: stdout golden

Also present:

- `test_control_flow.flow`: if/else, while, for loops
- `test_generics.flow`: monomorphization correctness (concrete stand-ins)
- `test_effects*.flow` / concurrency / async / fiber / netpoll: feature areas

Compiler unit checks live in flowc itself (its self-tests run in
`compiler/scripts/self_host_full.flow`) and in `tests/lang/`, run by
`./flow test-lang`. Tool and script behaviour is covered by `./flow test-scripts`.
