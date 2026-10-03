"""Unit tests for FLOW typed GPU render & compute graph (GpuGraph)."""

import pytest

from flow.gpu_graph import (
    ComputePass,
    GpuGraph,
    GpuHazardError,
    GpuResource,
    GpuResourceType,
    RenderPass,
    ResourceAccess,
    ResourceBinding,
    parse_gpu_graph,
)


def test_gpu_resource_and_ping_pong_creation():
    graph = GpuGraph("test_frame")
    buf = graph.add_resource("buf", GpuResourceType.STORAGE_BUFFER, "f32", (1024,))
    assert buf.name == "buf"
    assert buf.is_buffer
    assert not buf.is_texture

    pp = graph.add_ping_pong("vel", GpuResourceType.STORAGE_TEXTURE, "rgba16f", (128, 128))
    assert pp.read.name == "vel_0"
    assert pp.write.name == "vel_1"

    pp.swap()
    assert pp.read.name == "vel_1"
    assert pp.write.name == "vel_0"


def test_gpu_graph_pass_flattening():
    graph = GpuGraph("test_loop")
    vel = graph.add_ping_pong("vel", GpuResourceType.STORAGE_TEXTURE, "rgba16f", (128, 128))

    cp = ComputePass(
        name="advect",
        kernel_name="advect_kernel",
        bindings=[
            ResourceBinding("v_in", vel.read.name, ResourceAccess.READ, ping_pong_base="vel", ping_pong_mode="read"),
            ResourceBinding("v_out", vel.write.name, ResourceAccess.WRITE, ping_pong_base="vel", ping_pong_mode="write"),
        ],
    )

    graph.add_repeat_block(count=3, passes=[cp], swaps=["vel"])
    flattened = graph.flatten_passes()

    assert len(flattened) == 3
    assert [name for name, _ in flattened] == ["advect_iter0", "advect_iter1", "advect_iter2"]

    # Verify dynamic ping-pong re-binding across iterations:
    # Iteration 0: read vel_0, write vel_1
    # Iteration 1: read vel_1, write vel_0
    # Iteration 2: read vel_0, write vel_1
    assert flattened[0][1].bindings[0].resource_name == "vel_0"
    assert flattened[0][1].bindings[1].resource_name == "vel_1"

    assert flattened[1][1].bindings[0].resource_name == "vel_1"
    assert flattened[1][1].bindings[1].resource_name == "vel_0"

    assert flattened[2][1].bindings[0].resource_name == "vel_0"
    assert flattened[2][1].bindings[1].resource_name == "vel_1"


def test_gpu_graph_hazard_validation_catches_same_pass_conflict():
    graph = GpuGraph("bad_frame")
    graph.add_resource("tex", GpuResourceType.STORAGE_TEXTURE, "rgba16f", (128, 128))

    graph.add_compute_pass(
        "conflict_pass",
        "kernel",
        bindings=[
            ResourceBinding("in_tex", "tex", ResourceAccess.READ),
            ResourceBinding("out_tex", "tex", ResourceAccess.WRITE),
        ],
    )

    with pytest.raises(GpuHazardError) as exc_info:
        graph.validate_hazards()

    assert "same-pass read/write hazard" in str(exc_info.value)
    assert "tex" in str(exc_info.value)


def test_gpu_graph_hazard_validation_catches_workgroup_memory_limit():
    graph = GpuGraph("over_memory_frame")
    graph.add_compute_pass(
        "heavy_pass",
        "kernel",
        workgroup_memory_bytes=65536,
    )

    with pytest.raises(GpuHazardError) as exc_info:
        graph.validate_hazards(max_workgroup_memory=32768)

    assert "exceeds maximum workgroup memory" in str(exc_info.value)


def test_gpu_graph_hazard_validation_catches_undeclared_resource():
    graph = GpuGraph("missing_res")
    graph.add_compute_pass(
        "pass_a",
        "kernel",
        bindings=[ResourceBinding("arg0", "unknown_tex", ResourceAccess.READ)],
    )

    with pytest.raises(GpuHazardError) as exc_info:
        graph.validate_hazards()

    assert "undeclared resource" in str(exc_info.value)


def test_gpu_graph_pass_dependency_dag():
    graph = GpuGraph("fluid_dag")
    graph.add_ping_pong("vel", GpuResourceType.STORAGE_TEXTURE, "rgba16f", (128, 128))
    graph.add_resource("div", GpuResourceType.STORAGE_TEXTURE, "r16f", (128, 128), is_transient=True)

    vel = graph.ping_pongs["vel"]
    graph.add_compute_pass(
        "advect",
        "advect_kernel",
        bindings=[
            ResourceBinding("v_in", vel.read.name, ResourceAccess.READ),
            ResourceBinding("v_out", vel.write.name, ResourceAccess.WRITE),
        ],
    )

    graph.add_compute_pass(
        "divergence",
        "div_kernel",
        bindings=[
            ResourceBinding("v_in", vel.write.name, ResourceAccess.READ),
            ResourceBinding("d_out", "div", ResourceAccess.WRITE),
        ],
    )

    dag = graph.compute_dependencies()
    order = dag.topological_sort()
    assert order == ["advect", "divergence"]

    stages = dag.execution_stages()
    assert stages == [["advect"], ["divergence"]]
    assert len(dag.edges) == 1
    assert dag.edges[0].producer == "advect"
    assert dag.edges[0].consumer == "divergence"
    assert dag.edges[0].dependency_type == "RAW"


def test_parse_gpu_graph_dsl():
    dsl = """
gpu resource {
    texture velocity: rgba16f(128, 128) ping_pong
    texture pressure: r16f(128, 128) ping_pong
    texture divergence: r16f(128, 128) transient
}

gpu frame fluid_sim {
    compute advect[128, 128, 1](velocity.read, velocity.write)
    compute divergence[128, 128, 1](velocity.read, divergence.write)

    repeat 5 {
        compute pressure[128, 128, 1](pressure.read, divergence.read, pressure.write)
        pressure.swap()
    }

    render surface {
        draw fluid(velocity.read)
    }
}
"""

    graph = parse_gpu_graph(dsl)
    assert graph.name == "fluid_sim"
    assert "velocity_0" in graph.resources
    assert "velocity_1" in graph.resources
    assert "divergence" in graph.resources
    assert len(graph.passes) == 4

    metal = graph.generate_metal()
    assert "run_fluid_sim_frame" in metal["metal_host_code"]
    assert "MTLTextureDescriptor" in metal["metal_host_code"]

    wgpu = graph.generate_webgpu_js()
    assert "run_fluid_sim_frame" in wgpu["webgpu_js_code"]
    assert "createTexture" in wgpu["webgpu_js_code"]
