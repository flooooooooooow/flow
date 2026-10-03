"""
Unit tests for typed GPU render/compute graph, storage textures, and hazard checks (#812).
"""

from flow.gpu_graph import (
    GpuAccess,
    GpuTextureFormat,
    GpuBuffer,
    GpuTexture,
    GpuSampler,
    GpuComputePass,
    GpuRenderPass,
    GpuGraph,
    GpuHazardChecker,
    HazardType,
)
from flow.gpu_integration import create_gpu_graph, analyze_gpu_graph


class TestGpuResources:
    """Test typed GPU resources and storage textures."""

    def test_buffer_creation(self):
        buf = GpuBuffer(name="velocity", element_type="f32", capacity=2048, access=GpuAccess.READ_WRITE)
        assert buf.name == "velocity"
        assert buf.element_type == "f32"
        assert buf.capacity == 2048
        assert buf.access == GpuAccess.READ_WRITE

    def test_storage_texture_creation(self):
        tex = GpuTexture(
            name="pressure_tex",
            dimensions=(1024, 1024),
            format=GpuTextureFormat.RGBA16F,
            access=GpuAccess.READ_WRITE,
            is_storage=True,
        )
        assert tex.name == "pressure_tex"
        assert tex.dimensions == (1024, 1024)
        assert tex.format == GpuTextureFormat.RGBA16F
        assert tex.is_storage is True
        assert tex.access == GpuAccess.READ_WRITE


class TestGpuPassesAndGraph:
    """Test GPU render and compute pass graph assembly."""

    def test_compute_pass_bindings(self):
        cp = GpuComputePass("advect", kernel_name="advect_kernel", workgroup_size=(16, 16, 1))
        cp.bind_input("velocity_read").bind_output("velocity_next").bind_storage("field_tex")
        assert "velocity_read" in cp.inputs
        assert "velocity_next" in cp.outputs
        assert "field_tex" in cp.storage_bindings

    def test_render_pass_bindings(self):
        rp = GpuRenderPass("draw_fluid")
        rp.bind_color_attachment("swapchain_color")
        rp.bind_depth_attachment("depth_buffer")
        rp.bind_sample_texture("albedo_tex")
        rp.bind_storage_texture("accum_tex")
        assert rp.color_attachments == ["swapchain_color"]
        assert rp.depth_attachment == "depth_buffer"
        assert "albedo_tex" in rp.inputs
        assert "accum_tex" in rp.storage_textures

    def test_graph_assembly(self):
        graph = GpuGraph("fluid_frame")
        graph.add_buffer("velocity", capacity=4096)
        graph.add_storage_texture("pressure", dimensions=(512, 512), format=GpuTextureFormat.R32F)

        cp = GpuComputePass("pressure_solver", "solver_kernel")
        cp.bind_storage("pressure")
        graph.add_compute_pass(cp)

        assert "velocity" in graph.buffers
        assert "pressure" in graph.textures
        assert graph.textures["pressure"].is_storage is True
        assert len(graph.passes) == 1


class TestGpuHazardChecker:
    """Test compile-time hazard checks for storage textures and buffers."""

    def test_simultaneous_read_write_hazard(self):
        graph = GpuGraph("conflict_frame")
        graph.add_storage_texture("state_tex")

        cp = GpuComputePass("bad_pass", "bad_kernel")
        cp.bind_input("state_tex")
        cp.bind_output("state_tex")
        graph.add_compute_pass(cp)

        hazards, _ = GpuHazardChecker.analyze_graph(graph)
        assert len(hazards) == 1
        assert hazards[0].hazard_type == HazardType.SIMULTANEOUS_READ_WRITE
        assert hazards[0].resource_name == "state_tex"

    def test_read_after_write_hazard(self):
        graph = GpuGraph("raw_frame")
        graph.add_storage_texture("density")

        cp1 = GpuComputePass("advect", "advect_kernel")
        cp1.bind_output("density")
        graph.add_compute_pass(cp1)

        cp2 = GpuComputePass("diffuse", "diffuse_kernel")
        cp2.bind_input("density")
        graph.add_compute_pass(cp2)

        hazards, edges = GpuHazardChecker.analyze_graph(graph)
        assert len(hazards) == 1
        assert hazards[0].hazard_type == HazardType.READ_AFTER_WRITE
        assert hazards[0].source_pass == "advect"
        assert hazards[0].target_pass == "diffuse"
        assert ("advect", "diffuse", "density") in edges

    def test_barrier_resolves_raw_hazard(self):
        graph = GpuGraph("raw_frame")
        graph.add_storage_texture("density")

        cp1 = GpuComputePass("advect", "advect_kernel")
        cp1.bind_output("density")
        graph.add_compute_pass(cp1)

        cp2 = GpuComputePass("diffuse", "diffuse_kernel")
        cp2.bind_input("density")
        graph.add_compute_pass(cp2)

        # Add explicit barrier
        graph.add_barrier("advect", "diffuse", "density")

        hazards, _ = GpuHazardChecker.analyze_graph(graph)
        assert len(hazards) == 0

    def test_integration_helper_functions(self):
        graph = create_gpu_graph("test_frame")
        graph.add_storage_texture("tex_a")

        p1 = GpuComputePass("pass1", "k1").bind_output("tex_a")
        p2 = GpuComputePass("pass2", "k2").bind_input("tex_a")
        graph.add_compute_pass(p1)
        graph.add_compute_pass(p2)

        hazards, edges = analyze_gpu_graph(graph)
        assert len(hazards) == 1
        assert len(edges) >= 1
