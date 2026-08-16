import pytest
from flow.gpu_runtime import get_gpu_runtime, GPURuntime, gpu_runtime

def test_get_gpu_runtime_returns_instance():
    """Test that get_gpu_runtime returns an instance of GPURuntime."""
    runtime = get_gpu_runtime()
    assert isinstance(runtime, GPURuntime)

def test_get_gpu_runtime_singleton():
    """Test that multiple calls to get_gpu_runtime return the same instance."""
    runtime1 = get_gpu_runtime()
    runtime2 = get_gpu_runtime()
    assert runtime1 is runtime2

def test_get_gpu_runtime_matches_global():
    """Test that get_gpu_runtime returns the global gpu_runtime object."""
    runtime = get_gpu_runtime()
    assert runtime is gpu_runtime
