from unittest.mock import MagicMock, patch
from flow.gpu_runtime import gpu_list_backends, gpu_get_backend_count

def test_gpu_list_backends():
    with patch("flow.gpu_runtime.get_gpu_runtime") as mock_get_runtime:
        mock_runtime = MagicMock()
        mock_runtime.list_backends.return_value = ["cuda", "opencl", "metal"]
        mock_get_runtime.return_value = mock_runtime

        backends = gpu_list_backends()
        assert backends == ["cuda", "opencl", "metal"]
        mock_runtime.list_backends.assert_called_once()

def test_gpu_get_backend_count():
    with patch("flow.gpu_runtime.get_gpu_runtime") as mock_get_runtime:
        mock_runtime = MagicMock()
        mock_runtime.list_backends.return_value = ["cuda", "opencl"]
        mock_get_runtime.return_value = mock_runtime

        count = gpu_get_backend_count()
        assert count == 2
        mock_runtime.list_backends.assert_called_once()
