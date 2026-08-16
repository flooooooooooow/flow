import pytest
from unittest.mock import Mock, patch

from flow.gpu_runtime import gpu_free, gpu_allocate, gpu_copy_to_device, gpu_copy_from_device, gpu_synchronize

def test_gpu_allocate():
    with patch("flow.gpu_runtime.get_gpu_runtime") as mock_get_runtime:
        mock_runtime = Mock()
        mock_backend = Mock()

        mock_get_runtime.return_value = mock_runtime
        mock_runtime.get_backend.return_value = mock_backend
        mock_backend.allocate_memory.return_value = 98765

        result = gpu_allocate(1024, backend="cuda")

        mock_runtime.get_backend.assert_called_once_with("cuda")
        mock_backend.allocate_memory.assert_called_once_with(1024)
        assert result == 98765

def test_gpu_free():
    with patch("flow.gpu_runtime.get_gpu_runtime") as mock_get_runtime:
        mock_runtime = Mock()
        mock_backend = Mock()

        mock_get_runtime.return_value = mock_runtime
        mock_runtime.get_backend.return_value = mock_backend

        gpu_free(12345, backend="cuda")

        mock_runtime.get_backend.assert_called_once_with("cuda")
        mock_backend.free_memory.assert_called_once_with(12345)

def test_gpu_free_default_backend():
    with patch("flow.gpu_runtime.get_gpu_runtime") as mock_get_runtime:
        mock_runtime = Mock()
        mock_backend = Mock()

        mock_get_runtime.return_value = mock_runtime
        mock_runtime.get_backend.return_value = mock_backend

        gpu_free(67890)

        mock_runtime.get_backend.assert_called_once_with("cuda")
        mock_backend.free_memory.assert_called_once_with(67890)

def test_gpu_copy_to_device():
    with patch("flow.gpu_runtime.get_gpu_runtime") as mock_get_runtime:
        mock_runtime = Mock()
        mock_backend = Mock()

        mock_get_runtime.return_value = mock_runtime
        mock_runtime.get_backend.return_value = mock_backend

        mock_array = Mock()
        gpu_copy_to_device(mock_array, 12345, backend="cuda")

        mock_runtime.get_backend.assert_called_once_with("cuda")
        mock_backend.copy_to_device.assert_called_once_with(mock_array, 12345)

def test_gpu_copy_from_device():
    with patch("flow.gpu_runtime.get_gpu_runtime") as mock_get_runtime:
        mock_runtime = Mock()
        mock_backend = Mock()

        mock_get_runtime.return_value = mock_runtime
        mock_runtime.get_backend.return_value = mock_backend

        mock_array = Mock()
        gpu_copy_from_device(12345, mock_array, backend="cuda")

        mock_runtime.get_backend.assert_called_once_with("cuda")
        mock_backend.copy_from_device.assert_called_once_with(12345, mock_array)

def test_gpu_synchronize():
    with patch("flow.gpu_runtime.get_gpu_runtime") as mock_get_runtime:
        mock_runtime = Mock()
        mock_backend = Mock()

        mock_get_runtime.return_value = mock_runtime
        mock_runtime.get_backend.return_value = mock_backend

        gpu_synchronize(backend="cuda")

        mock_runtime.get_backend.assert_called_once_with("cuda")
        mock_backend.synchronize.assert_called_once_with()
