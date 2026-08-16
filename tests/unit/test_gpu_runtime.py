import pytest
from unittest.mock import patch

from flow.gpu_runtime import get_gpu_runtime, GPURuntime
import flow.gpu_runtime

def test_get_gpu_runtime_returns_global_instance():
    """Test that get_gpu_runtime returns the global GPURuntime instance."""
    runtime = get_gpu_runtime()

    assert isinstance(runtime, GPURuntime)
    assert runtime is flow.gpu_runtime.gpu_runtime

    # Test that multiple calls return the same instance (singleton behavior)
    runtime2 = get_gpu_runtime()
    assert runtime is runtime2

def test_get_gpu_runtime_mocked_instance():
    """Test that get_gpu_runtime strictly returns the gpu_runtime variable."""
    with patch('flow.gpu_runtime.gpu_runtime', "mocked_instance"):
        assert get_gpu_runtime() == "mocked_instance"
