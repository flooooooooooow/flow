import pytest
from unittest.mock import MagicMock, patch
import numpy as np

from flow.gpu_runtime import (
    gpu_allocate,
    gpu_free,
    gpu_copy_to_device,
    gpu_copy_from_device,
    gpu_synchronize,
    gpu_is_available,
    gpu_get_backend_count,
    gpu_list_backends
)

def test_gpu_allocate():
    mock_backend = MagicMock()
    mock_backend.allocate_memory.return_value = 12345
    mock_runtime = MagicMock()
    mock_runtime.get_backend.return_value = mock_backend

    with patch('flow.gpu_runtime.get_gpu_runtime', return_value=mock_runtime):
        result = gpu_allocate(1024, backend="mock")

    assert result == 12345
    mock_runtime.get_backend.assert_called_once_with("mock")
    mock_backend.allocate_memory.assert_called_once_with(1024)

def test_gpu_free():
    mock_backend = MagicMock()
    mock_runtime = MagicMock()
    mock_runtime.get_backend.return_value = mock_backend

    with patch('flow.gpu_runtime.get_gpu_runtime', return_value=mock_runtime):
        gpu_free(12345, backend="mock")

    mock_runtime.get_backend.assert_called_once_with("mock")
    mock_backend.free_memory.assert_called_once_with(12345)

def test_gpu_copy_to_device():
    # Setup mock backend and runtime
    mock_backend = MagicMock()
    mock_runtime = MagicMock()
    mock_runtime.get_backend.return_value = mock_backend

    device_ptr = 12345
    host_data = np.array([1, 2, 3], dtype=np.int32)

    with patch('flow.gpu_runtime.get_gpu_runtime', return_value=mock_runtime):
        gpu_copy_to_device(host_data, device_ptr, backend="mock")

    mock_runtime.get_backend.assert_called_once_with("mock")
    mock_backend.copy_to_device.assert_called_once_with(host_data, device_ptr)

def test_gpu_copy_from_device():
    # Setup mock backend and runtime
    mock_backend = MagicMock()
    mock_runtime = MagicMock()
    mock_runtime.get_backend.return_value = mock_backend

    device_ptr = 12345
    host_data = np.array([1, 2, 3], dtype=np.int32)

    with patch('flow.gpu_runtime.get_gpu_runtime', return_value=mock_runtime):
        gpu_copy_from_device(device_ptr, host_data, backend="mock")

    mock_runtime.get_backend.assert_called_once_with("mock")
    mock_backend.copy_from_device.assert_called_once_with(device_ptr, host_data)

def test_gpu_synchronize():
    mock_backend = MagicMock()
    mock_runtime = MagicMock()
    mock_runtime.get_backend.return_value = mock_backend

    with patch('flow.gpu_runtime.get_gpu_runtime', return_value=mock_runtime):
        gpu_synchronize(backend="mock")

    mock_runtime.get_backend.assert_called_once_with("mock")
    mock_backend.synchronize.assert_called_once()

def test_gpu_is_available():
    mock_runtime = MagicMock()
    mock_runtime.is_available.return_value = True

    with patch('flow.gpu_runtime.get_gpu_runtime', return_value=mock_runtime):
        result = gpu_is_available()

    assert result is True
    mock_runtime.is_available.assert_called_once()

def test_gpu_get_backend_count():
    mock_runtime = MagicMock()
    mock_runtime.list_backends.return_value = ["mock1", "mock2"]

    with patch('flow.gpu_runtime.get_gpu_runtime', return_value=mock_runtime):
        result = gpu_get_backend_count()

    assert result == 2
    mock_runtime.list_backends.assert_called_once()

def test_gpu_list_backends():
    mock_runtime = MagicMock()
    mock_runtime.list_backends.return_value = ["mock1", "mock2"]

    with patch('flow.gpu_runtime.get_gpu_runtime', return_value=mock_runtime):
        result = gpu_list_backends()

    assert result == ["mock1", "mock2"]
    mock_runtime.list_backends.assert_called_once()
