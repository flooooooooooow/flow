# Memory Management Library

The FLOW memory management library provides comprehensive low-level memory operations for systems programming, including allocation, manipulation, alignment, and safety functions.

## Overview

The memory module is designed for:
- **Performance-critical applications** requiring direct memory control
- **Systems programming** with manual memory management
- **Interoperability** with C libraries and hardware interfaces
- **Memory safety** with debugging and validation utilities

## Core Categories

### 1. Memory Allocation

#### Basic Allocation
```flow
import memory

# Allocate uninitialized memory
let ptr: *mut void = memory.malloc(1024)  # 1KB
if ptr != null {
    # Use memory...
    memory.free(ptr)
}

# Allocate zero-initialized memory
let zero_ptr: *mut void = memory.calloc(256, 4)  # 256 elements of 4 bytes each
```

#### Aligned Allocation
```flow
# Allocate with specific alignment (for SIMD, DMA, etc.)
let aligned_ptr: *mut void = memory.aligned_alloc(64, 1024)  # 64-byte aligned
```

#### Reallocation
```flow
# Resize existing allocation
let new_ptr: *mut void = memory.realloc(old_ptr, new_size)
if new_ptr != null {
    old_ptr = new_ptr
}
```

### 2. Memory Manipulation

#### Copy Operations
```flow
let src: [u8; 100] = [1, 2, 3, ...]
let dest: [u8; 100] = [0; 100]

# Non-overlapping copy (fastest)
memory.memcpy(&dest, &src, 100)

# Overlapping copy (safe)
memory.memmove(&dest, &src, 100)
```

#### Fill Operations
```flow
# Zero memory
memory.memzero(&buffer, buffer_size)

# Fill with specific value
memory.memset(&buffer, 0xFF, buffer_size)

# Fill with 32-bit pattern
memory.memory_fill_pattern(&buffer, 0xDEADBEEF, pattern_count)
```

#### Comparison
```flow
# Compare memory regions
if memory.memcmp(&buffer1, &buffer2, size) == 0 {
    print("Buffers are identical")
}
```

### 3. Memory Alignment

#### Type Information
```flow
# Get size and alignment of types
let int_size: usize = memory.sizeof<i32>()
let int_align: usize = memory.alignof<i32>()

# Get struct field offset
let field_offset: usize = memory.offset_of<Point>("x")
```

#### Alignment Utilities
```flow
# Check pointer alignment
if memory.is_aligned(ptr, 16) {
    # Safe for SIMD operations
}

# Round sizes to alignment boundaries
let aligned_size: usize = memory.align_up(size, 16)
let rounded_down: usize = memory.align_down(size, 16)
```

### 4. Stack Allocation

#### Automatic Stack Memory
```flow
fn process_data() {
    # Stack-allocated memory (automatically freed)
    let stack_buffer: *mut void = memory.alloca(1024)
    
    # Stack-allocated array
    let stack_array: *mut i32 = memory.stack_array<i32>(100)
    
    # Memory automatically freed when function returns
}
```

### 5. Memory Pools

#### Pool Management
```flow
# Create memory pool
let pool: MemoryPool = memory.memory_pool_create(65536)  # 64KB pool

# Allocate from pool
let ptr1: *mut void = memory.memory_pool_alloc(&pool, 1024, 8)
let ptr2: *mut void = memory.memory_pool_alloc(&pool, 2048, 16)

# Reset pool (reuse all memory)
memory.memory_pool_reset(&pool)

# Destroy pool
memory.memory_pool_destroy(&pool)
```

### 6. Memory Safety and Debugging

#### Validation
```flow
# Check if memory is readable/writable
if memory.memory_check(ptr, size) {
    # Safe to read
}

if memory.memory_check_write(ptr, size) {
    # Safe to write
}

# Validate memory region
if memory.memory_validate(ptr, size) {
    # Memory appears valid
}
```

#### Debugging
```flow
# Dump memory contents
memory.memory_dump(ptr, size, 16)  # 16 bytes per line

# Output format:
# 0x7fff1234: 48 65 6c 6c 6f 20 57 6f 72 6c 64 00 00 00 00 00 |Hello World....|
```

## Performance Considerations

### Allocation Strategies
- **Stack allocation** (`alloca`) for temporary, function-local memory
- **Memory pools** for frequent small allocations with known lifetimes
- **Direct allocation** (`malloc`) for large or long-lived objects

### Copy Optimization
- Use `memcpy` for non-overlapping regions (fastest)
- Use `memmove` only when overlap is possible
- Use `memory_copy_nonoverlapping` when you can guarantee no overlap

### Alignment Benefits
- Properly aligned memory enables SIMD optimizations
- Cache-line alignment improves performance for frequently accessed data
- Page alignment benefits large buffer operations

## Safety Guidelines

### Memory Safety Rules
1. **Always check** allocation return values for null
2. **Match allocation/deallocation** functions (malloc/free, pool_alloc/pool_destroy)
3. **Respect alignment** requirements when casting pointers
4. **Avoid buffer overflows** by validating sizes
5. **Use appropriate copy functions** based on overlap possibility

### Common Pitfalls
```flow
# ❌ Dangerous - no null check
let ptr: *mut void = memory.malloc(size)
*ptr = value  # Crash if allocation failed

# ✅ Safe - check allocation
let ptr: *mut void = memory.malloc(size)
if ptr != null {
    *ptr = value
}

# ❌ Dangerous - potential overlap
memory.memcpy(dest, src, size)  # Undefined if dest/src overlap

# ✅ Safe - handles overlap
memory.memmove(dest, src, size)
```

## Integration with MLIR

Most memory functions are implemented as MLIR intrinsics for optimal performance:

```flow
# These compile directly to MLIR operations
memory.malloc()    # → mlir.alloc
memory.free()      # → mlir.dealloc  
memory.memcpy()    # → memref.copy
memory.alloca()    # → alloca operation
```

## Examples

### Dynamic Array Implementation
```flow
struct DynamicArray<T> {
    data: *mut T,
    size: usize,
    capacity: usize
}

fn dynamic_array_create<T>(initial_capacity: usize) -> DynamicArray<T> {
    let data: *mut T = memory.malloc(initial_capacity * memory.sizeof<T>()) as *mut T
    return DynamicArray<T> {
        data: data,
        size: 0,
        capacity: initial_capacity
    }
}

fn dynamic_array_push<T>(array: *mut DynamicArray<T>, item: T) -> void {
    if array.size >= array.capacity {
        # Grow array
        let new_capacity: usize = array.capacity * 2
        let new_data: *mut T = memory.realloc(array.data as *mut void, 
                                            new_capacity * memory.sizeof<T>()) as *mut T
        if new_data != null {
            array.data = new_data
            array.capacity = new_capacity
        }
    }
    
    if array.size < array.capacity {
        array.data[array.size] = item
        array.size = array.size + 1
    }
}
```

### SIMD-Optimized Buffer
```flow
fn process_simd_buffer(data: *mut f32, count: usize) -> void {
    # Ensure 16-byte alignment for SIMD
    let aligned_data: *mut f32 = memory.aligned_alloc(16, count * 4) as *mut f32
    
    if memory.is_aligned(aligned_data, 16) {
        # Safe to use SIMD operations
        # Process 4 floats at once...
    }
    
    memory.free(aligned_data as *mut void)
}
```

## API Reference

### Allocation Functions
- `malloc(size: usize) -> *mut void`
- `calloc(nmemb: usize, size: usize) -> *mut void`
- `realloc(ptr: *mut void, size: usize) -> *mut void`
- `free(ptr: *mut void) -> void`
- `aligned_alloc(alignment: usize, size: usize) -> *mut void`

### Manipulation Functions
- `memcpy(dest: *mut void, src: *const void, n: usize) -> *mut void`
- `memmove(dest: *mut void, src: *const void, n: usize) -> *mut void`
- `memset(dest: *mut void, c: i32, n: usize) -> *mut void`
- `memcmp(s1: *const void, s2: *const void, n: usize) -> i32`

### Alignment Functions
- `alignof<T>() -> usize`
- `sizeof<T>() -> usize`
- `offset_of<T>(field: str) -> usize`
- `is_aligned(ptr: *const void, alignment: usize) -> bool`
- `align_up(size: usize, alignment: usize) -> usize`
- `align_down(size: usize, alignment: usize) -> usize`

### Safety Functions
- `memory_check(ptr: *const void, size: usize) -> bool`
- `memory_check_write(ptr: *mut void, size: usize) -> bool`
- `memory_validate(ptr: *const void, size: usize) -> bool`

### Stack Functions
- `alloca(size: usize) -> *mut void`
- `stack_array<T>(count: usize) -> *mut T`

### Pool Functions
- `memory_pool_create(size: usize) -> MemoryPool`
- `memory_pool_alloc(pool: *mut MemoryPool, size: usize, alignment: usize) -> *mut void`
- `memory_pool_reset(pool: *mut MemoryPool) -> void`
- `memory_pool_destroy(pool: *mut MemoryPool) -> void`

### Debug Functions
- `memory_dump(ptr: *const void, size: usize, bytes_per_line: usize) -> void`
- `memory_fill_pattern(ptr: *mut void, pattern: u32, count: usize) -> void`

This memory management library provides the foundation for high-performance systems programming in FLOW while maintaining safety and debugging capabilities.
