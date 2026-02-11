#!/usr/bin/env python3
"""
FLOW GPU Runtime
Provides CUDA and OpenCL integration for FLOW GPU programs.
"""

import os
import ctypes
import numpy as np
from typing import Optional, Dict, Any, List, Tuple

# Suppress warnings by default
SUPPRESS_GPU_WARNINGS = os.environ.get('FLOW_SUPPRESS_GPU_WARNINGS', '1') == '1'

class GPUBackend:
    """Base class for GPU backends."""
    
    def __init__(self):
        self.initialized = False
        self.device_count = 0
        self.current_device = 0
    
    def initialize(self) -> bool:
        """Initialize the GPU backend."""
        raise NotImplementedError
    
    def allocate_memory(self, size: int) -> int:
        """Allocate GPU memory and return device pointer."""
        raise NotImplementedError
    
    def free_memory(self, ptr: int) -> None:
        """Free GPU memory."""
        raise NotImplementedError
    
    def copy_to_device(self, host_data: np.ndarray, device_ptr: int) -> None:
        """Copy data from host to device."""
        raise NotImplementedError
    
    def copy_from_device(self, device_ptr: int, host_data: np.ndarray) -> None:
        """Copy data from device to host."""
        raise NotImplementedError
    
    def launch_kernel(self, kernel_ptr: int, grid_dim: Tuple[int, int, int], 
                     block_dim: Tuple[int, int, int], args: List[Any]) -> None:
        """Launch a GPU kernel."""
        raise NotImplementedError
    
    def synchronize(self) -> None:
        """Synchronize device operations."""
        raise NotImplementedError

class CUDABackend(GPUBackend):
    """CUDA GPU backend implementation."""
    
    def __init__(self):
        super().__init__()
        self.cuda_lib = None
        self.cufft_lib = None
        self._load_libraries()
    
    def _load_libraries(self):
        """Load CUDA libraries."""
        try:
            # Try different CUDA library paths
            cuda_paths = [
                "libcuda.so.1",
                "libcuda.dylib",
                "cuda.dll",
                "/usr/local/cuda/lib64/libcuda.so.1",
                "/opt/cuda/lib64/libcuda.so.1"
            ]
            
            for path in cuda_paths:
                try:
                    self.cuda_lib = ctypes.CDLL(path)
                    break
                except Exception:
                    continue
            
            if self.cuda_lib is None:
                if not SUPPRESS_GPU_WARNINGS:
                    print("Warning: CUDA library not found")
                return
            
            # Load cuFFT library
            cufft_paths = [
                "libcufft.so.10",
                "libcufft.dylib", 
                "cufft.dll",
                "/usr/local/cuda/lib64/libcufft.so.10",
                "/opt/cuda/lib64/libcufft.so.10"
            ]
            
            for path in cufft_paths:
                try:
                    self.cufft_lib = ctypes.CDLL(path)
                    break
                except Exception:
                    continue
            
            # Set up function signatures
            self._setup_cuda_functions()
            
        except Exception as e:
            print(f"Error loading CUDA libraries: {e}")
    
    def _setup_cuda_functions(self):
        """Set up CUDA function signatures."""
        if self.cuda_lib is None:
            return
        
        # cudaMalloc
        self.cuda_lib.cudaMalloc.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_size_t]
        self.cuda_lib.cudaMalloc.restype = ctypes.c_int
        
        # cudaFree
        self.cuda_lib.cudaFree.argtypes = [ctypes.c_void_p]
        self.cuda_lib.cudaFree.restype = ctypes.c_int
        
        # cudaMemcpy
        self.cuda_lib.cudaMemcpy.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int]
        self.cuda_lib.cudaMemcpy.restype = ctypes.c_int
        
        # cudaDeviceSynchronize
        self.cuda_lib.cudaDeviceSynchronize.argtypes = []
        self.cuda_lib.cudaDeviceSynchronize.restype = ctypes.c_int
        
        # cudaMemcpyHostToDevice
        self.cudaMemcpyHostToDevice = 1
        self.cudaMemcpyDeviceToHost = 2
    
    def initialize(self) -> bool:
        """Initialize CUDA backend."""
        if self.cuda_lib is None:
            return False
        
        try:
            # Get device count
            device_count = ctypes.c_int()
            result = self.cuda_lib.cudaGetDeviceCount(ctypes.byref(device_count))
            if result != 0:
                return False
            
            self.device_count = device_count.value
            self.initialized = True
            return True
        except Exception:
            return False
    
    def allocate_memory(self, size: int) -> int:
        """Allocate CUDA memory."""
        if not self.initialized:
            raise RuntimeError("CUDA not initialized")
        
        device_ptr = ctypes.c_void_p()
        result = self.cuda_lib.cudaMalloc(ctypes.byref(device_ptr), size)
        if result != 0:
            raise RuntimeError(f"CUDA malloc failed: {result}")
        
        return device_ptr.value
    
    def free_memory(self, ptr: int) -> None:
        """Free CUDA memory."""
        if not self.initialized:
            return
        
        self.cuda_lib.cudaFree(ctypes.c_void_p(ptr))
    
    def copy_to_device(self, host_data: np.ndarray, device_ptr: int) -> None:
        """Copy data from host to device."""
        if not self.initialized:
            raise RuntimeError("CUDA not initialized")
        
        size = host_data.nbytes
        result = self.cuda_lib.cudaMemcpy(
            ctypes.c_void_p(device_ptr),
            host_data.ctypes.data_as(ctypes.c_void_p),
            size,
            self.cudaMemcpyHostToDevice
        )
        if result != 0:
            raise RuntimeError(f"CUDA memcpy to device failed: {result}")
    
    def copy_from_device(self, device_ptr: int, host_data: np.ndarray) -> None:
        """Copy data from device to host."""
        if not self.initialized:
            raise RuntimeError("CUDA not initialized")
        
        size = host_data.nbytes
        result = self.cuda_lib.cudaMemcpy(
            host_data.ctypes.data_as(ctypes.c_void_p),
            ctypes.c_void_p(device_ptr),
            size,
            self.cudaMemcpyDeviceToHost
        )
        if result != 0:
            raise RuntimeError(f"CUDA memcpy from device failed: {result}")
    
    def launch_kernel(self, kernel_ptr: int, grid_dim: Tuple[int, int, int], 
                     block_dim: Tuple[int, int, int], args: List[Any]) -> None:
        """Launch CUDA kernel."""
        if not self.initialized:
            raise RuntimeError("CUDA not initialized")
        
        # This is a simplified implementation
        # In practice, you'd need to set up kernel launch parameters
        # and handle argument marshaling
        pass
    
    def synchronize(self) -> None:
        """Synchronize CUDA device."""
        if not self.initialized:
            return
        
        self.cuda_lib.cudaDeviceSynchronize()

class OpenCLBackend(GPUBackend):
    """OpenCL GPU backend implementation."""
    
    def __init__(self):
        super().__init__()
        self.opencl_lib = None
        self._load_libraries()
    
    def _load_libraries(self):
        """Load OpenCL libraries."""
        try:
            # Try different OpenCL library paths
            opencl_paths = [
                "libOpenCL.so.1",
                "libOpenCL.dylib",
                "OpenCL.dll",
                "/usr/lib/x86_64-linux-gnu/libOpenCL.so.1"
            ]
            
            for path in opencl_paths:
                try:
                    self.opencl_lib = ctypes.CDLL(path)
                    break
                except Exception:
                    continue
            
            if self.opencl_lib is None:
                if not SUPPRESS_GPU_WARNINGS:
                    print("Warning: OpenCL library not found")
                return
            
            # Set up function signatures
            self._setup_opencl_functions()
            
        except Exception as e:
            print(f"Error loading OpenCL libraries: {e}")
    
    def _setup_opencl_functions(self):
        """Set up OpenCL function signatures."""
        if self.opencl_lib is None:
            return
        
        # clGetPlatformIDs
        self.opencl_lib.clGetPlatformIDs.argtypes = [
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(ctypes.c_uint32)
        ]
        self.opencl_lib.clGetPlatformIDs.restype = ctypes.c_int
    
    def initialize(self) -> bool:
        """Initialize OpenCL backend."""
        if self.opencl_lib is None:
            return False
        
        try:
            # Get platform count
            platform_count = ctypes.c_uint32()
            result = self.opencl_lib.clGetPlatformIDs(0, None, ctypes.byref(platform_count))
            if result != 0:
                return False
            
            self.device_count = platform_count.value
            self.initialized = True
            return True
        except Exception:
            return False
    
    def allocate_memory(self, size: int) -> int:
        """Allocate OpenCL memory."""
        if not self.initialized:
            raise RuntimeError("OpenCL not initialized")
        
        # Simplified OpenCL memory allocation
        # In practice, you'd need to create context, command queue, etc.
        return 0  # Placeholder
    
    def free_memory(self, ptr: int) -> None:
        """Free OpenCL memory."""
        pass
    
    def copy_to_device(self, host_data: np.ndarray, device_ptr: int) -> None:
        """Copy data from host to device."""
        pass
    
    def copy_from_device(self, device_ptr: int, host_data: np.ndarray) -> None:
        """Copy data from device to host."""
        pass
    
    def launch_kernel(self, kernel_ptr: int, grid_dim: Tuple[int, int, int], 
                     block_dim: Tuple[int, int, int], args: List[Any]) -> None:
        """Launch OpenCL kernel."""
        pass
    
    def synchronize(self) -> None:
        """Synchronize OpenCL device."""
        pass

class GPURuntime:
    """Main GPU runtime that manages backends."""
    
    def __init__(self):
        self.backends: Dict[str, GPUBackend] = {}
        self.current_backend: Optional[str] = None
        self._initialize_backends()
    
    def _initialize_backends(self):
        """Initialize available GPU backends."""
        # Try CUDA first
        cuda_backend = CUDABackend()
        if cuda_backend.initialize():
            self.backends["cuda"] = cuda_backend
            self.current_backend = "cuda"
        
        # Try OpenCL
        opencl_backend = OpenCLBackend()
        if opencl_backend.initialize():
            self.backends["opencl"] = opencl_backend
            if self.current_backend is None:
                self.current_backend = "opencl"
    
    def get_backend(self, backend_name: Optional[str] = None) -> GPUBackend:
        """Get a GPU backend."""
        if backend_name is None:
            backend_name = self.current_backend
        
        if backend_name is None or backend_name not in self.backends:
            raise RuntimeError("No GPU backend available")
        
        return self.backends[backend_name]
    
    def list_backends(self) -> List[str]:
        """List available GPU backends."""
        return list(self.backends.keys())
    
    def is_available(self) -> bool:
        """Check if any GPU backend is available."""
        return len(self.backends) > 0

# Global GPU runtime instance
gpu_runtime = GPURuntime()

def get_gpu_runtime() -> GPURuntime:
    """Get the global GPU runtime instance."""
    return gpu_runtime

# FLOW GPU API functions
def gpu_allocate(size: int, backend: str = "cuda") -> int:
    """Allocate GPU memory."""
    runtime = get_gpu_runtime()
    gpu_backend = runtime.get_backend(backend)
    return gpu_backend.allocate_memory(size)

def gpu_free(ptr: int, backend: str = "cuda") -> None:
    """Free GPU memory."""
    runtime = get_gpu_runtime()
    gpu_backend = runtime.get_backend(backend)
    gpu_backend.free_memory(ptr)

def gpu_copy_to_device(host_data: np.ndarray, device_ptr: int, backend: str = "cuda") -> None:
    """Copy data from host to device."""
    runtime = get_gpu_runtime()
    gpu_backend = runtime.get_backend(backend)
    gpu_backend.copy_to_device(host_data, device_ptr)

def gpu_copy_from_device(device_ptr: int, host_data: np.ndarray, backend: str = "cuda") -> None:
    """Copy data from device to host."""
    runtime = get_gpu_runtime()
    gpu_backend = runtime.get_backend(backend)
    gpu_backend.copy_from_device(device_ptr, host_data)

def gpu_synchronize(backend: str = "cuda") -> None:
    """Synchronize GPU operations."""
    runtime = get_gpu_runtime()
    gpu_backend = runtime.get_backend(backend)
    gpu_backend.synchronize()

def gpu_is_available() -> bool:
    """Check if GPU is available."""
    runtime = get_gpu_runtime()
    return runtime.is_available()

def gpu_get_backend_count() -> int:
    """Get number of available GPU backends."""
    runtime = get_gpu_runtime()
    return len(runtime.list_backends())

def gpu_list_backends() -> List[str]:
    """List available GPU backends."""
    runtime = get_gpu_runtime()
    return runtime.list_backends()
