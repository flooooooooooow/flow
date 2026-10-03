import os
from pathlib import Path

import pytest
from flow.metal_codegen import generate_metal_shaders
from flow.parser import Block, FunctionDecl, Parameter, Type, parse_flow_code


def test_generate_metal_shaders_empty(tmp_path):
    """Test generating shaders with no declarations."""
    result = generate_metal_shaders([], output_dir=str(tmp_path))
    assert result == []
    assert not os.listdir(tmp_path)


def test_generate_metal_shaders_no_gpu_func(tmp_path):
    """Test generating shaders with declarations but no @gpu functions."""
    func = FunctionDecl(
        name="normal_func",
        parameters=[],
        return_type=Type("void"),
        body=Block([]),
        attributes=[],
    )
    result = generate_metal_shaders([func], output_dir=str(tmp_path))
    assert result == []
    assert not os.listdir(tmp_path)


def test_generate_metal_shaders_valid_gpu_func(tmp_path):
    """Test generating shaders with a valid @gpu function."""
    func = FunctionDecl(
        name="my_gpu_kernel",
        parameters=[
            Parameter("data", Type("ptr<f32>")),
            Parameter("size", Type("i32")),
        ],
        return_type=Type("void"),
        body=Block([]),
        attributes=["gpu"],
    )

    result = generate_metal_shaders([func], output_dir=str(tmp_path))

    assert len(result) == 1
    assert result[0][0] == "my_gpu_kernel"

    metal_file = os.path.join(tmp_path, "my_gpu_kernel.metal")
    host_file = os.path.join(tmp_path, "my_gpu_kernel_host.m")

    assert result[0][1] == metal_file

    assert os.path.exists(metal_file)
    assert os.path.exists(host_file)

    with open(metal_file, "r") as f:
        metal_content = f.read()

    assert "#include <metal_stdlib>" in metal_content
    assert "kernel void my_gpu_kernel(" in metal_content
    assert "device float* data [[buffer(0)]]" in metal_content
    assert "constant int& size [[buffer(1)]]" in metal_content
    assert "uint tid [[thread_position_in_grid]]" in metal_content

    with open(host_file, "r") as f:
        host_content = f.read()

    assert "void run_my_gpu_kernel(" in host_content
    assert "float* data, int size, size_t count" in host_content
    assert "id<MTLDevice> device = MTLCreateSystemDefaultDevice();" in host_content


def test_vgpu_mnist_and_depth_metal_codegen(tmp_path):
    mnist_path = Path("examples/gpu/vgpu/mnist.flow")
    mnist_decls = parse_flow_code(mnist_path.read_text(encoding="utf-8"))
    res_mnist = generate_metal_shaders(mnist_decls, output_dir=str(tmp_path / "mnist"))
    assert len(res_mnist) == 3
    kernel_names = [r[0] for r in res_mnist]
    assert "mnist_preprocess" in kernel_names
    assert "mnist_dense_layer" in kernel_names
    assert "mnist_postprocess" in kernel_names

    depth_path = Path("examples/gpu/vgpu/depth_estimation.flow")
    depth_decls = parse_flow_code(depth_path.read_text(encoding="utf-8"))
    res_depth = generate_metal_shaders(depth_decls, output_dir=str(tmp_path / "depth"))
    assert len(res_depth) == 3
    kernel_names_depth = [r[0] for r in res_depth]
    assert "depth_feature_extract" in kernel_names_depth
    assert "depth_projection_layer" in kernel_names_depth
    assert "depth_colormap_tint" in kernel_names_depth
