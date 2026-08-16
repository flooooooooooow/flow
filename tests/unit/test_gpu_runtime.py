import pytest
from unittest.mock import patch, MagicMock

from flow.gpu_runtime import (
    gpu_is_available,
    gpu_get_backend_count,
    gpu_list_backends,
    GPURuntime,
)


def test_gpu_is_available_true():
    mock_runtime = MagicMock(spec=GPURuntime)
    mock_runtime.is_available.return_value = True

    with patch("flow.gpu_runtime.get_gpu_runtime", return_value=mock_runtime):
        assert gpu_is_available() is True


def test_gpu_is_available_false():
    mock_runtime = MagicMock(spec=GPURuntime)
    mock_runtime.is_available.return_value = False

    with patch("flow.gpu_runtime.get_gpu_runtime", return_value=mock_runtime):
        assert gpu_is_available() is False


def test_gpu_get_backend_count():
    mock_runtime = MagicMock(spec=GPURuntime)
    mock_runtime.list_backends.return_value = ["cuda", "opencl"]

    with patch("flow.gpu_runtime.get_gpu_runtime", return_value=mock_runtime):
        assert gpu_get_backend_count() == 2


def test_gpu_list_backends():
    mock_runtime = MagicMock(spec=GPURuntime)
    mock_runtime.list_backends.return_value = ["cuda", "opencl"]

    with patch("flow.gpu_runtime.get_gpu_runtime", return_value=mock_runtime):
        assert gpu_list_backends() == ["cuda", "opencl"]
