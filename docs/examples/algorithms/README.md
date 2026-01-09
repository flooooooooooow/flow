# Algorithm Examples

This directory contains common algorithms implemented in FLOW, demonstrating various algorithmic techniques and patterns.

## Files

- **bubble_sort.flow** - Bubble sort implementation for arrays
- **gcd.flow** - Greatest Common Divisor (Euclidean algorithm)
- **power.flow** - Power calculation (fast exponentiation)

## Running Examples

```bash
# Sort an array
flow run bubble_sort.flow

# Calculate GCD
flow run gcd.flow

# Calculate power
flow run power.flow
```

## What You'll Learn

1. **Sorting Algorithms**: How to implement sorting in FLOW
2. **Mathematical Algorithms**: Common mathematical computations
3. **Recursive Patterns**: When and how to use recursion
4. **Loop Patterns**: Iterative algorithm implementations
5. **Performance Considerations**: Basic algorithm analysis

## Algorithm Categories

### Sorting
- **Bubble Sort**: Simple comparison-based sorting
- Time complexity: O(n²)
- Space complexity: O(1)

### Mathematical
- **GCD**: Euclidean algorithm for greatest common divisor
- **Power**: Fast exponentiation for efficient power calculation
- Both demonstrate recursive and iterative approaches

## Key Patterns

### Iterative Pattern
```flow
function iterative_gcd(a: i32, b: i32) -> i32 {
    while b != 0 {
        let temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}
```

### Recursive Pattern
```flow
function recursive_gcd(a: i32, b: i32) -> i32 {
    if b == 0 {
        return a;
    }
    return recursive_gcd(b, a % b);
}
```

## Performance Tips

1. **Prefer Iteration**: For simple loops, iteration is often faster
2. **Tail Recursion**: When using recursion, prefer tail-recursive functions
3. **Avoid Repeated Work**: Cache results when possible
4. **Choose Right Algorithm**: Match algorithm to problem size

## Prerequisites

- Strong understanding of FLOW basics
- Familiarity with arrays and loops
- [Basic Examples](../basic/) completed

## Related Topics

- [Data Structures](../data-structures/) - Data structures used by algorithms
- [Performance Examples](../performance/) - Performance optimization
- [Standard Library - Math](../../library/stdlib-reference.md) - Built-in mathematical functions
