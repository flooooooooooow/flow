import pytest
from unittest.mock import Mock, patch

from flow.gpu_runtime import (
    gpu_synchronize,
    GPUBackend,
    GPURuntime,
    get_gpu_runtime,
)

def test_gpu_synchronize():
    """Test that gpu_synchronize correctly delegates to the appropriate backend."""
    # We will mock the get_gpu_runtime to return a mocked runtime

    mock_runtime = Mock(spec=GPURuntime)
    mock_backend = Mock(spec=GPUBackend)

    mock_runtime.get_backend.return_value = mock_backend

    with patch('flow.gpu_runtime.get_gpu_runtime', return_value=mock_runtime):
        gpu_synchronize("test_backend")

    mock_runtime.get_backend.assert_called_once_with("test_backend")
    mock_backend.synchronize.assert_called_once()
