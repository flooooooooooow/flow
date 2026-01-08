# Metal GPU Examples

This section contains examples of using FLOW with Metal GPU integration on Apple Silicon.

## 🚀 Getting Started with Metal

### Basic Metal Detection

```flow
# Check if Metal is available
function metal_hello() -> i32 {
    print("FLOW Metal GPU Test")
    print("===================")
    
    if metal_is_available() {
        print("✓ Metal GPU is available")
        
        let info = metal_get_info()
        print("Backend: ", info.backend)
        print("Device count: ", info.device_count)
        
        return 0
    } else {
        print("✗ Metal GPU not available")
        return 1
    }
}
```

### Metal Initialization

```flow
function metal_setup() -> bool {
    print("Initializing Metal runtime...")
    
    if metal_initialize() {
        print("✓ Metal runtime initialized successfully")
        
        let info = metal_get_info()
        print("Device name: ", info.device_name)
        print("Max buffer size: ", info.max_buffer_size)
        
        return true
    } else {
        print("✗ Metal initialization failed")
        return false
    }
}
```

## 🎮 GPU Computation Examples

### Vector Addition

```flow
function metal_vector_add() -> i32 {
    print("Metal Vector Addition Example")
    
    if not metal_setup() {
        return 1
    }
    
    # Input vectors
    let a = [1.0f, 2.0f, 3.0f, 4.0f, 5.0f]
    let b = [2.0f, 3.0f, 4.0f, 5.0f, 6.0f]
    let n = length(a)
    
    # Allocate result vector
    let result = allocate_array<f32>(n)
    
    # Metal shader code
    let shader_code = """
    #include <metal_stdlib>
    using namespace metal;
    
    kernel void vector_add(
        device float* a [[buffer(0)]],
        device float* b [[buffer(1)]],
        device float* result [[buffer(2)]],
        uint id [[thread_position_in_grid]]
    ) {
        if (id < """ + i32_to_str(n) + """) {
            result[id] = a[id] + b[id];
        }
    }
    """
    
    # Compile shader
    let shader = metal_compile_shader(shader_code, "vector_add")
    if shader == null {
        print("✗ Shader compilation failed")
        return 1
    }
    
    print("✓ Shader compiled successfully")
    
    # Execute shader
    if metal_execute_shader("vector_add", [a, b, result]) {
        print("✓ Shader executed successfully")
        
        print("Results:")
        for i in 0..n {
            print("  result[", i, "] = ", result[i])
        }
        
        return 0
    } else {
        print("✗ Shader execution failed")
        return 1
    }
}
```

### Matrix Multiplication

```flow
function metal_matrix_multiply() -> i32 {
    print("Metal Matrix Multiplication Example")
    
    if not metal_setup() {
        return 1
    }
    
    # Input matrices (2x3 and 3x2)
    let a = [[1.0f, 2.0f, 3.0f],
             [4.0f, 5.0f, 6.0f]]
    let b = [[7.0f, 8.0f],
             [9.0f, 10.0f],
             [11.0f, 12.0f]]
    
    let m = rows(a)    # 2
    let n = cols(b)    # 2
    let p = cols(a)    # 3
    
    # Allocate result matrix (2x2)
    let result = allocate_matrix<f32>(m, n)
    
    # Metal shader for matrix multiplication
    let shader_code = """
    #include <metal_stdlib>
    using namespace metal;
    
    kernel void matmul(
        device float* a [[buffer(0)]],
        device float* b [[buffer(1)]],
        device float* result [[buffer(2)]],
        uint2 gid [[thread_position_in_grid]]
    ) {
        uint m = """ + i32_to_str(m) + """;
        uint n = """ + i32_to_str(n) + """;
        uint p = """ + i32_to_str(p) + """;
        
        if (gid.x < m && gid.y < n) {
            float sum = 0.0f;
            for (uint k = 0; k < p; k++) {
                sum += a[gid.x * p + k] * b[k * n + gid.y];
            }
            result[gid.x * n + gid.y] = sum;
        }
    }
    """
    
    # Compile and execute
    let shader = metal_compile_shader(shader_code, "matmul")
    if shader == null {
        print("✗ Matrix multiplication shader compilation failed")
        return 1
    }
    
    if metal_execute_shader("matmul", [a, b, result]) {
        print("✓ Matrix multiplication completed")
        
        print("Result matrix:")
        for i in 0..m {
            for j in 0..n {
                print("  result[", i, "][", j, "] = ", result[i][j])
            }
        }
        
        return 0
    } else {
        print("✗ Matrix multiplication failed")
        return 1
    }
}
```

## 🎨 Graphics Examples

### Simple Triangle Rendering

```flow
function metal_triangle() -> i32 {
    print("Metal Triangle Rendering Example")
    
    if not metal_setup() {
        return 1
    }
    
    # Triangle vertices
    let vertices = [
        [0.0f, 0.5f, 0.0f],   # Top
        [-0.5f, -0.5f, 0.0f], # Bottom left
        [0.5f, -0.5f, 0.0f]   # Bottom right
    ]
    
    # Vertex shader
    let vertex_shader = """
    #include <metal_stdlib>
    using namespace metal;
    
    struct VertexIn {
        float3 position [[attribute(0)]];
    };
    
    struct VertexOut {
        float4 position [[position]];
    };
    
    vertex VertexOut vertex_main(VertexIn in [[stage_in]]) {
        VertexOut out;
        out.position = float4(in.position, 1.0);
        return out;
    }
    """
    
    # Fragment shader
    let fragment_shader = """
    #include <metal_stdlib>
    using namespace metal;
    
    fragment float4 fragment_main() {
        return float4(1.0, 0.0, 0.0, 1.0); // Red color
    }
    """
    
    # Compile shaders
    let vs = metal_compile_shader(vertex_shader, "vertex_main")
    let fs = metal_compile_shader(fragment_shader, "fragment_main")
    
    if vs != null and fs != null {
        print("✓ Shaders compiled successfully")
        print("✓ Triangle rendering ready")
        
        # In a real application, you would set up the rendering pipeline
        # and execute the shaders here
        
        return 0
    } else {
        print("✗ Shader compilation failed")
        return 1
    }
}
```

### Image Processing

```flow
function metal_image_filter() -> i32 {
    print("Metal Image Processing Example")
    
    if not metal_setup() {
        return 1
    }
    
    # Simulate image data (4x4 grayscale)
    let image = [
        [255, 128, 64, 32],
        [16, 8, 4, 2],
        [1, 0, 1, 2],
        [4, 8, 16, 32]
    ]
    
    let width = 4
    let height = 4
    
    # Allocate output image
    let filtered = allocate_matrix<i32>(width, height)
    
    # Metal shader for grayscale filter
    let shader_code = """
    #include <metal_stdlib>
    using namespace metal;
    
    kernel void grayscale_filter(
        device uint* image [[buffer(0)]],
        device uint* result [[buffer(1)]],
        uint2 gid [[thread_position_in_grid]]
    ) {
        uint width = """ + i32_to_str(width) + """;
        uint height = """ + i32_to_str(height) + """;
        
        if (gid.x < width && gid.y < height) {
            uint idx = gid.y * width + gid.x;
            uint pixel = image[idx];
            
            // Apply simple brightness reduction
            result[idx] = pixel * 3 / 4;
        }
    }
    """
    
    # Compile and execute
    let shader = metal_compile_shader(shader_code, "grayscale_filter")
    if shader == null {
        print("✗ Image filter shader compilation failed")
        return 1
    }
    
    if metal_execute_shader("grayscale_filter", [image, filtered]) {
        print("✓ Image filter applied successfully")
        
        print("Filtered image:")
        for y in 0..height {
            for x in 0..width {
                print("  ", filtered[y][x])
            }
        }
        
        return 0
    } else {
        print("✗ Image filter failed")
        return 1
    }
}
```

## 🔧 Advanced Examples

### Performance Benchmark

```flow
function metal_benchmark() -> i32 {
    print("Metal Performance Benchmark")
    
    if not metal_setup() {
        return 1
    }
    
    let size = 1000000  # 1M elements
    let iterations = 100
    
    # Allocate arrays
    let a = allocate_array<f32>(size)
    let b = allocate_array<f32>(size)
    let result = allocate_array<f32>(size)
    
    # Initialize arrays
    for i in 0..size {
        a[i] = f32(i) * 0.001f
        b[i] = f32(i) * 0.002f
    }
    
    # Benchmark shader
    let shader_code = """
    #include <metal_stdlib>
    using namespace metal;
    
    kernel void benchmark_kernel(
        device float* a [[buffer(0)]],
        device float* b [[buffer(1)]],
        device float* result [[buffer(2)]],
        uint id [[thread_position_in_grid]]
    ) {
        uint size = """ + i32_to_str(size) + """;
        if (id < size) {
            result[id] = a[id] * b[id] + sin(a[id]);
        }
    }
    """
    
    let shader = metal_compile_shader(shader_code, "benchmark_kernel")
    if shader == null {
        print("✗ Benchmark shader compilation failed")
        return 1
    }
    
    # Warm up
    metal_execute_shader("benchmark_kernel", [a, b, result])
    
    # Benchmark
    let start_time = get_timestamp()
    
    for i in 0..iterations {
        metal_execute_shader("benchmark_kernel", [a, b, result])
    }
    
    gpu_synchronize()
    let end_time = get_timestamp()
    
    let elapsed = f64(end_time - start_time) / 1000000.0  # Convert to seconds
    let throughput = f64(size * iterations) / elapsed / 1000000.0  # Million ops/sec
    
    print("✓ Benchmark completed")
    print("Time: ", elapsed, " seconds")
    print("Throughput: ", throughput, " M ops/sec")
    
    # Cleanup
    gpu_free(a)
    gpu_free(b)
    gpu_free(result)
    
    return 0
}
```

### Multi-Kernel Pipeline

```flow
function metal_pipeline() -> i32 {
    print("Metal Multi-Kernel Pipeline Example")
    
    if not metal_setup() {
        return 1
    }
    
    let data_size = 1024
    
    # Stage 1: Generate data
    let stage1_shader = """
    #include <metal_stdlib>
    using namespace metal;
    
    kernel void generate_data(
        device float* data [[buffer(0)]],
        uint id [[thread_position_in_grid]]
    ) {
        data[id] = float(id) * 0.01f;
    }
    """
    
    # Stage 2: Process data
    let stage2_shader = """
    #include <metal_stdlib>
    using namespace metal;
    
    kernel void process_data(
        device float* input [[buffer(0)]],
        device float* output [[buffer(1)]],
        uint id [[thread_position_in_grid]]
    ) {
        float x = input[id];
        output[id] = sin(x) * cos(x) + sqrt(abs(x));
    }
    """
    
    # Stage 3: Reduce data
    let stage3_shader = """
    #include <metal_stdlib>
    using namespace metal;
    
    kernel void reduce_data(
        device float* input [[buffer(0)]],
        device float* result [[buffer(1)]],
        uint id [[thread_position_in_grid]]
    ) {
        if (id == 0) {
            float sum = 0.0f;
            for (uint i = 0; i < """ + i32_to_str(data_size) + """; i++) {
                sum += input[i];
            }
            result[0] = sum;
        }
    }
    """
    
    # Compile all shaders
    let shaders = [
        metal_compile_shader(stage1_shader, "generate_data"),
        metal_compile_shader(stage2_shader, "process_data"),
        metal_compile_shader(stage3_shader, "reduce_data")
    ]
    
    if shaders[0] != null and shaders[1] != null and shaders[2] != null {
        print("✓ All pipeline shaders compiled successfully")
        
        # Allocate buffers
        let data1 = allocate_array<f32>(data_size)
        let data2 = allocate_array<f32>(data_size)
        let result = allocate_array<f32>(1)
        
        # Execute pipeline
        metal_execute_shader("generate_data", [data1])
        metal_execute_shader("process_data", [data1, data2])
        metal_execute_shader("reduce_data", [data2, result])
        
        gpu_synchronize()
        
        print("✓ Pipeline executed successfully")
        print("Final result: ", result[0])
        
        return 0
    } else {
        print("✗ Pipeline shader compilation failed")
        return 1
    }
}
```

## 🛠️ Utility Examples

### Metal Information

```flow
function metal_info() -> i32 {
    print("Metal System Information")
    print("========================")
    
    if metal_is_available() {
        let info = metal_get_info()
        
        print("Available: ", info.available)
        print("Backend: ", info.backend)
        print("Device count: ", info.device_count)
        print("Compiled shaders: ", info.compiled_shaders)
        print("Device name: ", info.device_name)
        print("Max buffer size: ", info.max_buffer_size)
        
        return 0
    } else {
        print("Metal is not available on this system")
        return 1
    }
}
```

### Error Handling

```flow
function metal_error_handling() -> i32 {
    print("Metal Error Handling Example")
    
    # Try to compile invalid shader
    let invalid_shader = """
    #include <metal_stdlib>
    using namespace metal;
    
    kernel void invalid_shader(
        device float* data [[buffer(0)]]
    ) {
        // Intentional syntax error
        data[id] = data[id] + 1.0f; // id is not defined
    }
    """
    
    let shader = metal_compile_shader(invalid_shader, "invalid_shader")
    if shader == null {
        print("✓ Invalid shader correctly rejected")
    } else {
        print("✗ Invalid shader was accepted (unexpected)")
        return 1
    }
    
    # Try to execute non-existent shader
    if metal_execute_shader("non_existent", []) {
        print("✗ Non-existent shader executed (unexpected)")
        return 1
    } else {
        print("✓ Non-existent shader correctly rejected")
    }
    
    return 0
}
```

## 🎯 Complete Example

### Metal Demo Application

```flow
function metal_demo() -> i32 {
    print("FLOW Metal GPU Demo")
    print("===================")
    
    # System check
    if not metal_info() {
        return 1
    }
    
    print()
    
    # Run examples
    let examples = [
        ("Vector Addition", metal_vector_add),
        ("Matrix Multiplication", metal_matrix_multiply),
        ("Image Processing", metal_image_filter),
        ("Pipeline", metal_pipeline)
    ]
    
    for (name, func) in examples {
        print("Running: ", name)
        print("------------------------")
        
        let result = func()
        
        if result == 0 {
            print("✓ ", name, " completed successfully")
        } else {
            print("✗ ", name, " failed")
        }
        
        print()
    }
    
    print("Demo completed!")
    return 0
}
```

## 🚀 Running the Examples

To run these examples:

1. **Ensure you're on Apple Silicon macOS** with Metal support
2. **Compile with GPU support**: `flowc --gpu-backend=metal example.flow`
3. **Run the compiled program**: `./example`

### Command Line Options

```bash
# Compile with Metal backend
flowc --gpu-backend=metal --optimize metal_demo.flow

# Run with debugging
flowc --gpu-backend=metal --debug metal_demo.flow

# Benchmark performance
flowc --gpu-backend=metal --benchmark metal_benchmark.flow
```

## 📚 Best Practices

1. **Always check Metal availability** before using GPU features
2. **Handle shader compilation errors** gracefully
3. **Use proper memory management** - allocate and free GPU memory
4. **Synchronize GPU operations** when needed
5. **Profile GPU performance** for optimization
6. **Validate shader code** during development

## 🔍 Troubleshooting

### Common Issues

- **Metal not available**: Ensure you're running on macOS with Apple Silicon
- **Shader compilation fails**: Check MSL syntax and Metal API usage
- **GPU memory errors**: Verify buffer sizes and memory limits
- **Performance issues**: Use profiling tools to identify bottlenecks

### Debug Tips

```flow
function debug_metal() -> void {
    # Enable Metal debugging
    gpu_set_debug_mode(true)
    
    # Check Metal status
    if not metal_is_available() {
        print("Metal not available - check system requirements")
        return
    }
    
    # Get detailed info
    let info = metal_get_info()
    print("Metal info: ", info)
    
    # Test basic functionality
    if not metal_initialize() {
        print("Metal initialization failed")
        return
    }
    
    print("Metal debugging completed")
}
```
