"""Unit tests for GPU Runtime API."""
import pytest
from unittest.mock import patch, MagicMock
from flow.gpu_runtime import gpu_copy_to_device, gpu_copy_from_device

def test_gpu_copy_to_device():
    mock_host_data = MagicMock()
    device_ptr = 12345

    with patch('flow.gpu_runtime.get_gpu_runtime') as mock_get_runtime:
        mock_runtime = MagicMock()
        mock_backend = MagicMock()

        mock_get_runtime.return_value = mock_runtime
        mock_runtime.get_backend.return_value = mock_backend

        gpu_copy_to_device(mock_host_data, device_ptr, backend="cuda")

        mock_get_runtime.assert_called_once()
        mock_runtime.get_backend.assert_called_once_with("cuda")
        mock_backend.copy_to_device.assert_called_once_with(mock_host_data, device_ptr)

def test_gpu_copy_from_device():
    mock_host_data = MagicMock()
    device_ptr = 12345

    with patch('flow.gpu_runtime.get_gpu_runtime') as mock_get_runtime:
        mock_runtime = MagicMock()
        mock_backend = MagicMock()

        mock_get_runtime.return_value = mock_runtime
        mock_runtime.get_backend.return_value = mock_backend

        gpu_copy_from_device(device_ptr, mock_host_data, backend="cuda")

        mock_get_runtime.assert_called_once()
        mock_runtime.get_backend.assert_called_once_with("cuda")
        mock_backend.copy_from_device.assert_called_once_with(device_ptr, mock_host_data)
