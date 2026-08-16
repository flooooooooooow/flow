"""Tests for GPU runtime functionality."""

import pytest
from unittest.mock import MagicMock, patch

from src.flow.gpu_runtime import gpu_get_backend_count


def test_gpu_get_backend_count():
    """Test getting the backend count with available backends."""
    with patch('src.flow.gpu_runtime.get_gpu_runtime') as mock_get_runtime:
        mock_runtime = MagicMock()
        mock_runtime.list_backends.return_value = ["cuda", "opencl"]
        mock_get_runtime.return_value = mock_runtime

        count = gpu_get_backend_count()

        assert count == 2
        mock_runtime.list_backends.assert_called_once()


def test_gpu_get_backend_count_empty():
    """Test getting the backend count with no available backends."""
    with patch('src.flow.gpu_runtime.get_gpu_runtime') as mock_get_runtime:
        mock_runtime = MagicMock()
        mock_runtime.list_backends.return_value = []
        mock_get_runtime.return_value = mock_runtime

        count = gpu_get_backend_count()

        assert count == 0
        mock_runtime.list_backends.assert_called_once()
