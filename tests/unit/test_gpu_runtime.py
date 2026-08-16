import pytest
from unittest.mock import MagicMock, patch

from flow.gpu_runtime import gpu_allocate, gpu_free

@patch('flow.gpu_runtime.get_gpu_runtime')
def test_gpu_allocate_success(mock_get_runtime):
    mock_runtime = MagicMock()
    mock_backend = MagicMock()
    mock_runtime.get_backend.return_value = mock_backend
    mock_get_runtime.return_value = mock_runtime

    mock_backend.allocate_memory.return_value = 12345

    ptr = gpu_allocate(1024, "cuda")

    assert ptr == 12345
    mock_get_runtime.assert_called_once()
    mock_runtime.get_backend.assert_called_once_with("cuda")
    mock_backend.allocate_memory.assert_called_once_with(1024)

@patch('flow.gpu_runtime.get_gpu_runtime')
def test_gpu_allocate_backend_error(mock_get_runtime):
    mock_runtime = MagicMock()
    mock_backend = MagicMock()
    mock_runtime.get_backend.return_value = mock_backend
    mock_get_runtime.return_value = mock_runtime

    mock_backend.allocate_memory.side_effect = RuntimeError("CUDA malloc failed")

    with pytest.raises(RuntimeError, match="CUDA malloc failed"):
        gpu_allocate(1024, "cuda")

    mock_get_runtime.assert_called_once()
    mock_runtime.get_backend.assert_called_once_with("cuda")
    mock_backend.allocate_memory.assert_called_once_with(1024)

@patch('flow.gpu_runtime.get_gpu_runtime')
def test_gpu_free(mock_get_runtime):
    mock_runtime = MagicMock()
    mock_backend = MagicMock()
    mock_runtime.get_backend.return_value = mock_backend
    mock_get_runtime.return_value = mock_runtime

    gpu_free(12345, "cuda")

    mock_get_runtime.assert_called_once()
    mock_runtime.get_backend.assert_called_once_with("cuda")
    mock_backend.free_memory.assert_called_once_with(12345)
