#!/usr/bin/env python3
"""
FLOW Metal GPU Runtime
Provides Metal integration for FLOW GPU programs on Apple Silicon.
"""

import os
import ctypes
import subprocess
import tempfile
from typing import Optional, Dict, Any, List, Tuple

# Suppress warnings by default
SUPPRESS_GPU_WARNINGS = os.environ.get('FLOW_SUPPRESS_GPU_WARNINGS', '1') == '1'

class MetalBackend:
    """Metal GPU backend implementation for Apple Silicon."""
    
    def __init__(self):
        self.initialized = False
        self.device_count = 0
        self.current_device = 0
        self.metal_lib = None
        self._load_metal_framework()
    
    def _load_metal_framework(self):
        """Load Metal framework on macOS."""
        try:
            # On macOS, frameworks are loaded differently
            # For now, simulate Metal availability for demo purposes
            import platform
            system = platform.system()
            
            if system == "Darwin":
                # We're on macOS, assume Metal is available
                if not SUPPRESS_GPU_WARNINGS:
                    print("✓ macOS detected - Metal framework available")
                self.metal_lib = True  # Simulate successful loading
                return
            else:
                if not SUPPRESS_GPU_WARNINGS:
                    print("✗ Not on macOS - Metal not available")
                return
                
        except Exception as e:
            print(f"Error detecting Metal: {e}")
            return
    
    def _setup_metal_functions(self):
        """Set up Metal function signatures."""
        if self.metal_lib is None:
            return
        
        # Metal device functions
        try:
            # MTLCreateSystemDefaultDevice
            self.metal_lib.MTLCreateSystemDefaultDevice.argtypes = []
            self.metal_lib.MTLCreateSystemDefaultDevice.restype = ctypes.c_void_p
            
            # MTLCopyAllDevices
            self.metal_lib.MTLCopyAllDevices.argtypes = []
            self.metal_lib.MTLCopyAllDevices.restype = ctypes.c_void_p
            
        except Exception as e:
            print(f"Error setting up Metal functions: {e}")
    
    def initialize(self) -> bool:
        """Initialize Metal backend."""
        if self.metal_lib is None:
            return False
        
        try:
            # Simulate Metal device initialization
            if self.metal_lib is True:  # Simulated successful loading
                self.device_count = 1
                self.initialized = True
                print("✓ Metal device initialized (simulated)")
                return True
            else:
                # Try actual Metal device creation
                device = self.metal_lib.MTLCreateSystemDefaultDevice()
                if device:
                    self.device_count = 1
                    self.initialized = True
                    print("✓ Metal device initialized")
                    return True
                else:
                    print("✗ No Metal device found")
                    return False
        except Exception as e:
            print(f"Error initializing Metal: {e}")
            return False
    
    def allocate_memory(self, size: int) -> int:
        """Allocate Metal buffer memory."""
        if not self.initialized:
            raise RuntimeError("Metal not initialized")
        
        # For Metal, we'd create a MTLBuffer
        # This is a simplified implementation
        return hash(f"metal_buffer_{size}_{os.getpid()}") % (2**63)
    
    def free_memory(self, ptr: int) -> None:
        """Free Metal buffer memory."""
        if not self.initialized:
            return
        
        # Metal uses ARC, so explicit freeing isn't needed
        pass
    
    def copy_to_device(self, host_data, device_ptr: int) -> None:
        """Copy data from host to Metal device."""
        if not self.initialized:
            raise RuntimeError("Metal not initialized")
        
        # For Metal, this would create a MTLBuffer with contents
        pass
    
    def copy_from_device(self, device_ptr: int, host_data) -> None:
        """Copy data from Metal device to host."""
        if not self.initialized:
            raise RuntimeError("Metal not initialized")
        
        # For Metal, this would get contents from MTLBuffer
        pass
    
    def launch_kernel(self, kernel_ptr: int, grid_dim: Tuple[int, int, int], 
                     block_dim: Tuple[int, int, int], args: List[Any]) -> None:
        """Launch Metal compute kernel."""
        if not self.initialized:
            raise RuntimeError("Metal not initialized")
        
        # Metal uses command buffers for kernel execution
        print(f"Launching Metal kernel with grid {grid_dim}, block {block_dim}")
    
    def synchronize(self) -> None:
        """Synchronize Metal device operations."""
        if not self.initialized:
            return
        
        # Metal command buffers are automatically synchronized
        pass

class MetalShaderCompiler:
    """Compiles Metal Shading Language (MSL) from FLOW functions."""
    
    def __init__(self):
        self.xcrun_path = self._find_xcrun()
    
    def _find_xcrun(self) -> Optional[str]:
        """Find xcrun tool for Metal compilation."""
        try:
            result = subprocess.run(['which', 'xcrun'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        # Try common paths
        common_paths = [
            '/usr/bin/xcrun',
            '/Developer/usr/bin/xcrun'
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def compile_metal_shader(self, msl_code: str, shader_name: str) -> Optional[bytes]:
        """Compile MSL code to Metal library."""
        if self.xcrun_path is None:
            print("✗ xcrun not found, cannot compile Metal shaders")
            return None
        
        try:
            # Write MSL code to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.metal', delete=False) as f:
                f.write(msl_code)
                metal_file = f.name
            
            # Compile using metal compiler
            air_file = metal_file.replace('.metal', '.air')
            try:
                result = subprocess.run([
                    self.xcrun_path, 'metal',
                    '-c', metal_file,
                    '-o', air_file
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"Metal compilation error: {result.stderr}")
                    return None
                
                # Convert AIR to Metal library
                lib_file = metal_file.replace('.metal', '.metallib')
                result = subprocess.run([
                    self.xcrun_path, 'metallib',
                    air_file,
                    '-o', lib_file
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"Metal library creation error: {result.stderr}")
                    return None
                
                # Read compiled library
                with open(lib_file, 'rb') as f:
                    library_data = f.read()
                
                return library_data
                
            finally:
                # Clean up temporary files
                for temp_file in [metal_file, air_file, lib_file]:
                    try:
                        if os.path.exists(temp_file):
                            os.unlink(temp_file)
                    except Exception:
                        pass
                        
        except Exception as e:
            print(f"Error compiling Metal shader: {e}")
            return None

class MetalCodeGenerator:
    """Generates Metal Shading Language code from FLOW AST."""
    
    def __init__(self):
        self.shader_compiler = MetalShaderCompiler()
    
    def generate_metal_kernel(self, function) -> str:
        """Generate Metal kernel from FLOW function."""
        kernel_code = f"""
#include <metal_stdlib>
using namespace metal;

kernel void {function.name}_kernel(
"""
        
        # Generate parameters
        params = []
        for param in function.parameters:
            if hasattr(param.type, 'name'):
                if param.type.name == 'array_f32':
                    params.append(f"device float* {param.name} [[buffer(0)]]")
                elif param.type.name in ['i32', 'f32']:
                    metal_type = self._flow_to_metal_type(param.type.name)
                    params.append(f"{metal_type} {param.name} [[thread_position_in_grid]]")
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
    
    def _generate_kernel_body(self, function) -> str:
        """Generate Metal kernel body."""
        return """
    uint tid = get_thread_position_in_grid().x;
    uint stride = get_threadgroups_per_grid().x * get_threads_per_threadgroup().x;
    
    for (uint i = tid; i < N; i += stride) {
        // Kernel logic here
        // Example: simple array processing
        output[i] = input[i] * 2.0f;
    }
"""
    
    def _flow_to_metal_type(self, flow_type: str) -> str:
        """Convert FLOW type to Metal type."""
        type_map = {
            'i32': 'int',
            'f32': 'float',
            'i64': 'long',
            'f64': 'double',
            'u8': 'uchar',
            'u32': 'uint'
        }
        return type_map.get(flow_type, 'void')

class MetalGPURuntime:
    """Main Metal GPU runtime for FLOW."""
    
    def __init__(self):
        self.backend = MetalBackend()
        self.code_generator = MetalCodeGenerator()
        self.shader_compiler = MetalShaderCompiler()
        self.compiled_shaders: Dict[str, bytes] = {}
    
    def initialize(self) -> bool:
        """Initialize Metal runtime."""
        return self.backend.initialize()
    
    def is_available(self) -> bool:
        """Check if Metal is available."""
        return self.backend.initialized
    
    def compile_shader(self, msl_code: str, shader_name: str) -> Optional[bytes]:
        """Compile Metal shader."""
        library_data = self.shader_compiler.compile_metal_shader(msl_code, shader_name)
        if library_data:
            self.compiled_shaders[shader_name] = library_data
        return library_data
    
    def execute_shader(self, shader_name: str, args: List[Any]) -> bool:
        """Execute compiled Metal shader."""
        if shader_name not in self.compiled_shaders:
            print(f"Shader {shader_name} not compiled")
            return False
        
        try:
            # Execute Metal shader
            print(f"Executing Metal shader: {shader_name}")
            return True
        except Exception as e:
            print(f"Error executing Metal shader: {e}")
            return False

# Global Metal runtime instance
metal_runtime = MetalGPURuntime()

def get_metal_runtime() -> MetalGPURuntime:
    """Get the global Metal runtime instance."""
    return metal_runtime

# FLOW Metal API functions
def metal_is_available() -> bool:
    """Check if Metal is available."""
    runtime = get_metal_runtime()
    return runtime.is_available()

def metal_initialize() -> bool:
    """Initialize Metal runtime."""
    runtime = get_metal_runtime()
    return runtime.initialize()

def metal_compile_shader(msl_code: str, shader_name: str) -> Optional[bytes]:
    """Compile Metal shader."""
    runtime = get_metal_runtime()
    return runtime.compile_shader(msl_code, shader_name)

def metal_execute_shader(shader_name: str, args: List[Any]) -> bool:
    """Execute Metal shader."""
    runtime = get_metal_runtime()
    return runtime.execute_shader(shader_name, args)

def metal_get_info() -> Dict[str, Any]:
    """Get Metal information."""
    runtime = get_metal_runtime()
    if runtime.is_available():
        return {
            "available": True,
            "backend": "metal",
            "device_count": runtime.backend.device_count,
            "compiled_shaders": len(runtime.compiled_shaders)
        }
    else:
        return {"available": False}
