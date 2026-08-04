# Core Library

The FLOW core library provides fundamental types, operations, and runtime functions for the language.

## 🔧 Runtime System

### GPU Runtime

FLOW includes a comprehensive GPU runtime system with support for multiple backends:

```flow
# GPU runtime functions
function gpu_init() -> bool
function gpu_shutdown() -> void
function gpu_is_available() -> bool
function gpu_get_backend() -> str
function gpu_get_device_count() -> i32
function gpu_get_device_info(device_id: i32) -> DeviceInfo
```

### Metal Runtime (Apple Silicon)

Native Metal GPU integration for macOS:

```flow
# Metal-specific functions
function metal_is_available() -> bool
function metal_initialize() -> bool
function metal_get_info() -> MetalInfo
function metal_compile_shader(code: str, name: str) -> ShaderHandle
function metal_execute_shader(shader: str, args: [any]) -> bool
```

#### MetalInfo Structure

```flow
struct MetalInfo {
    available: bool,
    backend: str,
    device_count: i32,
    compiled_shaders: i32,
    device_name: str,
    max_buffer_size: i64
}
```

## 📊 Memory Management

### GPU / Unified Memory (shipped)

See **[gpu-memory.md](gpu-memory.md)** — `import "stdlib/gpu_memory.flow"`.

```flow
import "stdlib/gpu_memory.flow"

let buf: GpuBuffer = gpu_alloc(4096)          # shared/unified on Metal
let u: GpuBuffer = unified_allocate(4096)     # alias
gpu_copy_to_device(buf, host, 4096)
gpu_copy_from_device(host, buf, 4096)
let mapped: ptr<void> = gpu_host_ptr(buf)     # unified mapping
gpu_free(buf)
```

CPU heap remains in [memory.md](memory.md). CUDA / explicit migrate APIs are future work.

## 🚀 GPU Computing

### Kernel Execution

```flow
# GPU kernel functions
function gpu_launch_kernel(name: str, grid: [i32], block: [i32], args: [any]) -> void
function gpu_synchronize() -> void
function gpu_set_stream(stream: GPUStream) -> void
function gpu_get_stream() -> GPUStream

# Kernel compilation
function gpu_compile_kernel(source: str, name: str, backend: str) -> KernelHandle
function gpu_validate_kernel(kernel: KernelHandle) -> bool
function gpu_get_kernel_info(kernel: KernelHandle) -> KernelInfo
```

### Performance Monitoring

```flow
# GPU profiling
function gpu_start_profiling() -> void
function gpu_stop_profiling() -> ProfilingData
function gpu_get_timestamp() -> i64
function gpu_measure_kernel(kernel: KernelHandle, args: [any]) -> f64
```

## 🎨 Graphics Operations

### Rendering Pipeline

```flow
# Graphics functions
function graphics_init() -> bool
function graphics_create_window(width: i32, height: i32, title: str) -> Window
function graphics_create_context(window: Window) -> GraphicsContext
function graphics_swap_buffers(context: GraphicsContext) -> void

# Shader operations
function graphics_create_shader(type: ShaderType, source: str) -> Shader
function graphics_create_program(vertex: Shader, fragment: Shader) -> Program
function graphics_use_program(program: Program) -> void
```

### Buffer Management

```flow
# Graphics buffers
function graphics_create_buffer(type: BufferType, size: i64) -> Buffer
function graphics_buffer_data(buffer: Buffer, data: any, usage: BufferUsage) -> void
function graphics_bind_buffer(buffer: Buffer, target: BufferTarget) -> void
function graphics_draw_arrays(mode: DrawMode, count: i32) -> void
function graphics_draw_elements(mode: DrawMode, count: i32) -> void
```

## 🔍 Debugging and Validation

### GPU Debugging

```flow
# Debug functions
function gpu_set_debug_mode(enabled: bool) -> void
function gpu_validate_kernels(enabled: bool) -> void
function gpu_get_last_error() -> GPUError
function gpu_clear_errors() -> void
function gpu_dump_memory(ptr: GPUPtr, size: i64) -> void
```

### Memory Tracking

```flow
# Memory debugging
function gpu_track_memory(enabled: bool) -> void
function gpu_get_memory_usage() -> MemoryUsage
function gpu_check_memory_leaks() -> [MemoryLeak]
function gpu_dump_memory_stats() -> void
```

## 📡 Platform Integration

### System Information

```flow
# Platform detection
function get_platform() -> Platform
function get_cpu_architecture() -> str
function get_gpu_info() -> [GPUInfo]
function is_apple_silicon() -> bool
function is_metal_available() -> bool
```

### Platform Types

```flow
enum Platform {
    Windows,
    macOS,
    Linux,
    Unknown
}

struct GPUInfo {
    name: str,
    vendor: str,
    memory: i64,
    backend: str,
    available: bool
}
```

## 🛠️ Utility Functions

### Type Conversion

```flow
# Type conversion utilities
function i32_to_f32(value: i32) -> f32
function f32_to_i32(value: f32) -> i32
function str_to_i32(s: str) -> i32
function str_to_f32(s: str) -> f32
function i32_to_str(value: i32) -> str
function f32_to_str(value: f32) -> str
```

### Math Operations

```flow
# Math utilities
function abs<T>(value: T) -> T
function min<T>(a: T, b: T) -> T
function max<T>(a: T, b: T) -> T
function clamp<T>(value: T, min: T, max: T) -> T
function lerp(a: f32, b: f32, t: f32) -> f32
function smoothstep(edge0: f32, edge1: f32, x: f32) -> f32
```

### Array Operations

```flow
# Array utilities
function array_length<T>(arr: [T]) -> i32
function array_copy<T>(src: [T], dst: [T], count: i32) -> void
function array_fill<T>(arr: [T], value: T, count: i32) -> void
function array_reverse<T>(arr: [T]) -> [T]
function array_sort<T>(arr: [T], compare: (T, T) -> i32) -> [T]
```

## 🎯 Performance Primitives

### SIMD Operations

```flow
# SIMD vector operations
function simd_add(a: [f32], b: [f32]) -> [f32]
function simd_sub(a: [f32], b: [f32]) -> [f32]
function simd_mul(a: [f32], b: [f32]) -> [f32]
function simd_div(a: [f32], b: [f32]) -> [f32]
function simd_dot(a: [f32], b: [f32]) -> f32
function simd_normalize(v: [f32]) -> [f32]
function simd_length(v: [f32]) -> f32
```

### Parallel Operations

```flow
# Parallel processing
function parallel_for(start: i32, end: i32, body: (i32) -> void) -> void
function parallel_map<T, U>(arr: [T], fn: (T) -> U) -> [U]
function parallel_reduce<T>(arr: [T], fn: (T, T) -> T, init: T) -> T
function parallel_filter<T>(arr: [T], predicate: (T) -> bool) -> [T]
```

## 🔒 Error Handling

### Error Types

```flow
enum ErrorType {
    NoError,
    InvalidArgument,
    OutOfMemory,
    DeviceError,
    CompilationError,
    RuntimeError,
    UnknownError
}

struct Error {
    type: ErrorType,
    message: str,
    code: i32,
    file: str,
    line: i32
}
```

### Error Handling Functions

```flow
# Error management
function get_last_error() -> Error
function clear_error() -> void
function set_error_handler(handler: (Error) -> void) -> void
function panic(message: str) -> void
function assert(condition: bool, message: str) -> void
```

## 📊 Configuration

### Runtime Configuration

```flow
# Configuration functions
function set_gpu_backend(backend: str) -> bool
function get_gpu_backend() -> str
function set_memory_limit(limit: i64) -> void
function get_memory_limit() -> i64
function enable_optimizations(enabled: bool) -> void
function set_log_level(level: LogLevel) -> void
```

### Configuration Options

```flow
enum LogLevel {
    Debug,
    Info,
    Warning,
    Error,
    Fatal
}

enum BackendType {
    Auto,
    Metal,
    CUDA,
    OpenCL,
    CPU
}
```

## 🎮 Examples

### Basic GPU Setup

```flow
function setup_gpu() -> bool {
    if not gpu_init() {
        print("Failed to initialize GPU")
        return false
    }
    
    if is_apple_silicon() and metal_is_available() {
        print("Using Metal backend on Apple Silicon")
        metal_initialize()
    }
    
    return true
}
```

### Memory Management

```flow
function gpu_array_example() -> [f32] {
    let size = 1024
    let gpu_array = gpu_allocate_array<f32>(size)
    
    # Copy data to GPU
    let host_data = [1.0f, 2.0f, 3.0f, 4.0f]
    gpu_copy_to_device(host_data, gpu_array)
    
    # Process on GPU
    gpu_launch_kernel("process_array", [size], [1], gpu_array)
    gpu_synchronize()
    
    # Copy results back
    let result = gpu_copy_from_device(gpu_array, size * 4)
    gpu_free(gpu_array)
    
    return result
}
```

### Error Handling

```flow
function safe_gpu_operation() -> bool {
    set_error_handler(func(error: Error) {
        print("GPU Error: ", error.message)
    })
    
    if not gpu_init() {
        let error = get_last_error()
        print("Initialization failed: ", error.message)
        return false
    }
    
    return true
}
```
