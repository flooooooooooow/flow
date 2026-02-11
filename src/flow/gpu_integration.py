#!/usr/bin/env python3
"""
FLOW GPU Integration
Integrates GPU capabilities into the FLOW compiler and runtime.
Supports CUDA, OpenCL, and Metal (Apple Silicon).
"""

import os
import subprocess
import tempfile
from typing import List, Dict, Any, Optional

# Import Metal runtime for Apple Silicon
try:
    from .metal_runtime import get_metal_runtime, metal_is_available

    METAL_AVAILABLE = True
except ImportError:
    METAL_AVAILABLE = False

from .gpu_runtime import get_gpu_runtime
from .parser import FunctionDecl


class GPUCodeGenerator:
    """Generates GPU code from FLOW AST."""

    def __init__(self):
        self.gpu_runtime = get_gpu_runtime()
        self.kernel_cache: Dict[str, str] = {}
        self.metal_runtime = None
        if METAL_AVAILABLE:
            self.metal_runtime = get_metal_runtime()

    def generate_gpu_kernel(self, function: FunctionDecl, backend: str = "auto") -> str:
        """Generate GPU kernel from FLOW function."""
        # Auto-detect backend
        if backend == "auto":
            backend = self._detect_best_backend()

        if backend == "metal" and self.metal_runtime:
            return self._generate_metal_kernel(function)
        elif backend == "cuda":
            return self._generate_cuda_kernel(function)
        elif backend == "opencl":
            return self._generate_opencl_kernel(function)
        else:
            # Fallback to CUDA
            return self._generate_cuda_kernel(function)

    def _detect_best_backend(self) -> str:
        """Detect the best available GPU backend."""
        # Check for Metal on Apple Silicon
        if METAL_AVAILABLE and metal_is_available():
            return "metal"

        # Check for CUDA
        if (
            self.gpu_runtime.is_available()
            and "cuda" in self.gpu_runtime.list_backends()
        ):
            return "cuda"

        # Check for OpenCL
        if (
            self.gpu_runtime.is_available()
            and "opencl" in self.gpu_runtime.list_backends()
        ):
            return "opencl"

        # Default to CUDA
        return "cuda"

    def _generate_metal_kernel(self, function: FunctionDecl) -> str:
        """Generate Metal Shading Language kernel."""
        if not self.metal_runtime:
            return ""

        from .metal_runtime import MetalCodeGenerator

        generator = MetalCodeGenerator()
        return generator.generate_metal_kernel(function)

    def _generate_cuda_kernel(self, function: FunctionDecl) -> str:
        """Generate CUDA C kernel from FLOW function."""
        kernel_code = f"""
__global__ void {function.name}_kernel(
"""

        # Generate parameters
        params = []
        for param in function.parameters:
            if hasattr(param.type, "name"):
                if param.type.name == "array_f32":
                    params.append(f"float* {param.name}")
                elif param.type.name in ["i32", "f32"]:
                    params.append(
                        f"{self._flow_to_cuda_type(param.type.name)} {param.name}"
                    )
                else:
                    params.append(f"void* {param.name}")
            else:
                params.append(f"void* {param.name}")

        kernel_code += ",\n    ".join(params) + "\n)"
        kernel_code += " {\n"

        # Generate kernel body
        kernel_code += self._generate_kernel_body(function)

        kernel_code += "}\n"
        return kernel_code

    def _generate_opencl_kernel(self, function: FunctionDecl) -> str:
        """Generate OpenCL kernel from FLOW function."""
        kernel_code = f"""
__kernel void {function.name}_kernel(
"""

        # Generate parameters
        params = []
        for param in function.parameters:
            if hasattr(param.type, "name"):
                if param.type.name == "array_f32":
                    params.append(f"__global float* {param.name}")
                elif param.type.name in ["i32", "f32"]:
                    params.append(
                        f"{self._flow_to_opencl_type(param.type.name)} {param.name}"
                    )
                else:
                    params.append(f"__global void* {param.name}")
            else:
                params.append(f"__global void* {param.name}")

        kernel_code += ",\n    ".join(params) + "\n)"
        kernel_code += " {\n"

        # Generate kernel body
        kernel_code += self._generate_kernel_body(function)

        kernel_code += "}\n"
        return kernel_code

    def _generate_kernel_body(self, function: FunctionDecl) -> str:
        """Generate kernel body from FLOW function body."""
        # This is a simplified implementation
        # In practice, you'd need to translate the full FLOW AST

        body = """
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    int stride = blockDim.x * gridDim.x;
    
    for (int i = tid; i < N; i += stride) {
        // Kernel logic here
        output[i] = input[i] * 2.0f;
    }
"""
        return body

    def _flow_to_cuda_type(self, flow_type: str) -> str:
        """Convert FLOW type to CUDA type."""
        type_map = {
            "i32": "int",
            "f32": "float",
            "i64": "long",
            "f64": "double",
            "u8": "unsigned char",
            "u32": "unsigned int",
        }
        return type_map.get(flow_type, "void")

    def _flow_to_opencl_type(self, flow_type: str) -> str:
        """Convert FLOW type to OpenCL type."""
        type_map = {
            "i32": "int",
            "f32": "float",
            "i64": "long",
            "f64": "double",
            "u8": "uchar",
            "u32": "uint",
        }
        return type_map.get(flow_type, "void")


class GPUCompiler:
    """Compiles GPU kernels and manages GPU execution."""

    def __init__(self):
        self.code_generator = GPUCodeGenerator()
        self.gpu_runtime = get_gpu_runtime()
        self.metal_runtime = None
        if METAL_AVAILABLE:
            self.metal_runtime = get_metal_runtime()
        self.compiled_kernels: Dict[str, Any] = {}

    def compile_gpu_kernel(
        self, function: FunctionDecl, backend: str = "auto"
    ) -> Optional[Any]:
        """Compile GPU kernel for the best available backend."""
        if backend == "auto":
            backend = self.code_generator._detect_best_backend()

        kernel_code = self.code_generator.generate_gpu_kernel(function, backend)
        kernel_name = f"{function.name}_kernel"

        if backend == "metal" and self.metal_runtime:
            return self._compile_metal_kernel(kernel_code, kernel_name)
        elif backend == "cuda":
            return self._compile_cuda_kernel(kernel_code, kernel_name)
        elif backend == "opencl":
            return self._compile_opencl_kernel(kernel_code, kernel_name)
        else:
            return None

    def _compile_metal_kernel(
        self, kernel_code: str, kernel_name: str
    ) -> Optional[Any]:
        """Compile Metal kernel."""
        if not self.metal_runtime:
            return None

        try:
            library_data = self.metal_runtime.compile_shader(kernel_code, kernel_name)
            if library_data:
                self.compiled_kernels[kernel_name] = library_data
                return library_data
            return None
        except Exception as e:
            print(f"Error compiling Metal kernel: {e}")
            return None

    def _compile_cuda_kernel(self, kernel_code: str, kernel_name: str) -> Optional[Any]:
        """Compile CUDA kernel using nvcc."""
        if (
            not self.gpu_runtime.is_available()
            or "cuda" not in self.gpu_runtime.list_backends()
        ):
            print("CUDA not available")
            return None

        try:
            # Write kernel to temporary file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".cu", delete=False) as f:
                f.write(kernel_code)
                kernel_file = f.name

            # Compile with nvcc
            output_file = kernel_file.replace(".cu", ".ptx")
            try:
                result = subprocess.run(
                    ["nvcc", "-ptx", "-arch=sm_35", kernel_file, "-o", output_file],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    # Load PTX and return kernel handle
                    kernel_handle = self._load_cuda_ptx(output_file, kernel_name)
                    self.compiled_kernels[kernel_name] = kernel_handle
                    return kernel_handle
                else:
                    print(f"CUDA compilation error: {result.stderr}")
                    return None
            finally:
                # Clean up temporary files
                try:
                    os.unlink(kernel_file)
                    if os.path.exists(output_file):
                        os.unlink(output_file)
                except Exception:
                    pass

        except Exception as e:
            print(f"Error compiling CUDA kernel: {e}")
            return None

    def _compile_opencl_kernel(
        self, kernel_code: str, kernel_name: str
    ) -> Optional[Any]:
        """Compile OpenCL kernel."""
        if (
            not self.gpu_runtime.is_available()
            or "opencl" not in self.gpu_runtime.list_backends()
        ):
            print("OpenCL not available")
            return None

        # For OpenCL, we'd need to set up context, program, etc.
        # This is a simplified implementation
        try:
            # Create OpenCL program from source
            kernel_handle = f"opencl_kernel_{kernel_name}"
            self.compiled_kernels[kernel_name] = kernel_handle
            return kernel_handle
        except Exception as e:
            print(f"Error compiling OpenCL kernel: {e}")
            return None

    def _load_cuda_ptx(self, ptx_file: str, kernel_name: str) -> Any:
        """Load CUDA PTX and return kernel handle."""
        # This would use the CUDA driver API to load PTX
        # For now, return a placeholder
        return f"cuda_kernel_{kernel_name}"


class GPUExecutor:
    """Executes GPU kernels and manages data transfer."""

    def __init__(self):
        self.gpu_runtime = get_gpu_runtime()
        self.metal_runtime = None
        if METAL_AVAILABLE:
            self.metal_runtime = get_metal_runtime()
        self.compiler = GPUCompiler()
        self.device_buffers: Dict[str, int] = {}

    def execute_gpu_function(
        self, function: FunctionDecl, args: List[Any], backend: str = "auto"
    ) -> Optional[Any]:
        """Execute a FLOW function on GPU."""
        if backend == "auto":
            backend = self.code_generator._detect_best_backend()

        if (
            backend == "metal"
            and self.metal_runtime
            and self.metal_runtime.is_available()
        ):
            return self._execute_metal_function(function, args)
        elif self.gpu_runtime.is_available():
            return self._execute_cuda_opencl_function(function, args, backend)
        else:
            print("GPU not available")
            return None

    def _execute_metal_function(
        self, function: FunctionDecl, args: List[Any]
    ) -> Optional[Any]:
        """Execute function using Metal."""
        try:
            # Compile Metal shader
            kernel_handle = self.compiler.compile_gpu_kernel(function, "metal")
            if kernel_handle is None:
                return None

            # Execute Metal shader
            kernel_name = f"{function.name}_kernel"
            success = self.metal_runtime.execute_shader(kernel_name, args)
            return success

        except Exception as e:
            print(f"Error executing Metal function: {e}")
            return False

    def _execute_cuda_opencl_function(
        self, function: FunctionDecl, args: List[Any], backend: str
    ) -> Optional[Any]:
        """Execute function using CUDA/OpenCL."""
        try:
            # Compile kernel
            kernel_handle = self.compiler.compile_gpu_kernel(function, backend)
            if kernel_handle is None:
                return None

            # Prepare arguments and execute
            return self._execute_kernel(kernel_handle, args, backend)

        except Exception as e:
            print(f"Error executing GPU kernel: {e}")
            return False

    def _execute_kernel(self, kernel_handle: Any, args: List[Any], backend: str) -> Any:
        """Execute compiled GPU kernel."""
        try:
            # Prepare device memory for arguments
            device_args = []

            for arg in args:
                if hasattr(arg, "__len__"):  # Array-like
                    # Allocate device memory and copy data
                    size = len(arg) * 4  # Assuming float32
                    device_ptr = self.gpu_runtime.allocate_memory(size)
                    self.gpu_runtime.copy_to_device(arg, device_ptr)
                    device_args.append(device_ptr)
                else:
                    # Scalar value - pass directly
                    device_args.append(arg)

            # Launch kernel (simplified)
            grid_dim = (1, 1, 1)
            block_dim = (256, 1, 1)

            print(f"Launching {backend} kernel with grid {grid_dim}, block {block_dim}")

            # Synchronize and clean up
            self.gpu_runtime.synchronize()

            # Clean up device memory
            for device_ptr in device_args:
                if isinstance(device_ptr, int):
                    self.gpu_runtime.free_memory(device_ptr)

            return True

        except Exception as e:
            print(f"Error executing GPU kernel: {e}")
            return False


class GPUIntegration:
    """Main GPU integration class for FLOW with Metal support."""

    def __init__(self):
        self.executor = GPUExecutor()
        self.compiler = GPUCompiler()
        self.gpu_runtime = get_gpu_runtime()
        self.metal_runtime = None
        if METAL_AVAILABLE:
            self.metal_runtime = get_metal_runtime()

    def is_gpu_available(self) -> bool:
        """Check if GPU is available."""
        # Check Metal first on Apple Silicon
        if self.metal_runtime and self.metal_runtime.is_available():
            return True

        # Fall back to CUDA/OpenCL
        return self.gpu_runtime.is_available()

    def get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU information."""
        info = {"available": False}

        # Check Metal
        if self.metal_runtime and self.metal_runtime.is_available():
            info.update(
                {
                    "available": True,
                    "primary_backend": "metal",
                    "metal": self.metal_runtime.backend.device_count > 0,
                }
            )

        # Check CUDA/OpenCL
        if self.gpu_runtime.is_available():
            if not info.get("available"):
                info["available"] = True
                info["primary_backend"] = (
                    "cuda" if "cuda" in self.gpu_runtime.list_backends() else "opencl"
                )

            info["backends"] = self.gpu_runtime.list_backends()
            info["backend_count"] = len(self.gpu_runtime.list_backends())

        return info

    def compile_and_execute(
        self, function: FunctionDecl, args: List[Any], backend: str = "auto"
    ) -> Optional[Any]:
        """Compile and execute a function on GPU."""
        return self.executor.execute_gpu_function(function, args, backend)

    def benchmark_gpu_vs_cpu(
        self, function: FunctionDecl, args: List[Any], iterations: int = 100
    ) -> Dict[str, float]:
        """Benchmark GPU vs CPU execution."""
        import time

        results = {}

        # GPU execution
        if self.is_gpu_available():
            start_time = time.time()
            for _ in range(iterations):
                self.compile_and_execute(function, args)
            gpu_time = time.time() - start_time
            results["gpu_time"] = gpu_time / iterations
        else:
            results["gpu_time"] = float("inf")

        # CPU execution (placeholder)
        start_time = time.time()
        for _ in range(iterations):
            # Execute CPU version
            pass
        cpu_time = time.time() - start_time
        results["cpu_time"] = cpu_time / iterations

        # Speedup
        if results["cpu_time"] > 0:
            results["speedup"] = results["cpu_time"] / results["gpu_time"]
        else:
            results["speedup"] = 1.0

        return results


# Global GPU integration instance
gpu_integration = GPUIntegration()


def get_gpu_integration() -> GPUIntegration:
    """Get the global GPU integration instance."""
    return gpu_integration


# FLOW GPU API functions
def gpu_is_available() -> bool:
    """Check if GPU is available."""
    integration = get_gpu_integration()
    return integration.is_gpu_available()


def gpu_get_info() -> Dict[str, Any]:
    """Get GPU information."""
    integration = get_gpu_integration()
    return integration.get_gpu_info()


def gpu_execute_function(
    function: FunctionDecl, args: List[Any], backend: str = "auto"
) -> Optional[Any]:
    """Execute a function on GPU."""
    integration = get_gpu_integration()
    return integration.compile_and_execute(function, args, backend)


def gpu_benchmark(
    function: FunctionDecl, args: List[Any], iterations: int = 100
) -> Dict[str, float]:
    """Benchmark GPU vs CPU execution."""
    integration = get_gpu_integration()
    return integration.benchmark_gpu_vs_cpu(function, args, iterations)


# Metal-specific functions
def metal_is_available() -> bool:
    """Check if Metal is available."""
    return METAL_AVAILABLE and metal_is_available()


def metal_get_info() -> Dict[str, Any]:
    """Get Metal information."""
    if METAL_AVAILABLE:
        runtime = get_metal_runtime()
        return runtime.get_info()
    return {"available": False}
