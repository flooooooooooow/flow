#!/usr/bin/env python3
"""
FLOW Typed GPU Render/Compute Graph and Hazard Analysis (#812)
Provides typed GPU resource abstractions (buffers, storage textures, samplers),
pass graph definitions (GpuComputePass, GpuRenderPass, GpuGraph), and
compile-time hazard analysis (RAW, WAR, WAW, simultaneous read-write conflicts).
"""

from __future__ import annotations

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple, Any


class GpuAccess(Enum):
    READ = auto()
    WRITE = auto()
    READ_WRITE = auto()


class GpuTextureFormat(Enum):
    RGBA8UNORM = "rgba8unorm"
    RGBA16F = "rgba16f"
    RGBA32F = "rgba32f"
    R32F = "r32f"
    DEPTH32F = "depth32f"


class GpuResourceType(Enum):
    BUFFER = auto()
    TEXTURE = auto()
    STORAGE_TEXTURE = auto()
    SAMPLER = auto()


@dataclass
class GpuBuffer:
    name: str
    element_type: str = "f32"
    capacity: int = 1024
    access: GpuAccess = GpuAccess.READ_WRITE
    lifetime: str = "frame"


@dataclass
class GpuTexture:
    name: str
    dimensions: Tuple[int, ...] = (512, 512)
    format: GpuTextureFormat = GpuTextureFormat.RGBA8UNORM
    access: GpuAccess = GpuAccess.READ
    is_storage: bool = False
    lifetime: str = "frame"


@dataclass
class GpuSampler:
    name: str
    filter_mode: str = "linear"
    address_mode: str = "clamp"


class HazardType(Enum):
    SIMULTANEOUS_READ_WRITE = "Simultaneous Read-Write Conflict"
    READ_AFTER_WRITE = "Read-After-Write (RAW) Hazard"
    WRITE_AFTER_READ = "Write-After-Read (WAR) Hazard"
    WRITE_AFTER_WRITE = "Write-After-Write (WAW) Hazard"


@dataclass
class GpuHazard:
    resource_name: str
    hazard_type: HazardType
    source_pass: str
    target_pass: str
    message: str


@dataclass
class GpuPassAccess:
    pass_name: str
    reads: Set[str] = field(default_factory=set)
    writes: Set[str] = field(default_factory=set)
    read_writes: Set[str] = field(default_factory=set)


class GpuComputePass:
    def __init__(self, name: str, kernel_name: str, workgroup_size: Tuple[int, int, int] = (16, 16, 1)):
        self.name = name
        self.kernel_name = kernel_name
        self.workgroup_size = workgroup_size
        self.inputs: Set[str] = set()
        self.outputs: Set[str] = set()
        self.storage_bindings: Set[str] = set()

    def bind_input(self, resource_name: str) -> GpuComputePass:
        self.inputs.add(resource_name)
        return self

    def bind_output(self, resource_name: str) -> GpuComputePass:
        self.outputs.add(resource_name)
        return self

    def bind_storage(self, resource_name: str) -> GpuComputePass:
        self.storage_bindings.add(resource_name)
        return self


class GpuRenderPass:
    def __init__(self, name: str):
        self.name = name
        self.vertex_shader: str = ""
        self.fragment_shader: str = ""
        self.color_attachments: List[str] = []
        self.depth_attachment: Optional[str] = None
        self.inputs: Set[str] = set()
        self.storage_textures: Set[str] = set()

    def bind_color_attachment(self, texture_name: str) -> GpuRenderPass:
        self.color_attachments.append(texture_name)
        return self

    def bind_depth_attachment(self, texture_name: str) -> GpuRenderPass:
        self.depth_attachment = texture_name
        return self

    def bind_sample_texture(self, texture_name: str) -> GpuRenderPass:
        self.inputs.add(texture_name)
        return self

    def bind_storage_texture(self, texture_name: str) -> GpuRenderPass:
        self.storage_textures.add(texture_name)
        return self


class GpuGraph:
    """Typed render and compute graph with explicit resource passes."""

    def __init__(self, name: str = "default_gpu_frame"):
        self.name = name
        self.buffers: Dict[str, GpuBuffer] = {}
        self.textures: Dict[str, GpuTexture] = {}
        self.samplers: Dict[str, GpuSampler] = {}
        self.passes: List[Any] = []
        self.barriers: List[Tuple[str, str, str]] = []  # (source_pass, target_pass, resource_name)

    def add_buffer(self, name: str, element_type: str = "f32", capacity: int = 1024, access: GpuAccess = GpuAccess.READ_WRITE) -> GpuBuffer:
        buf = GpuBuffer(name, element_type, capacity, access)
        self.buffers[name] = buf
        return buf

    def add_texture(self, name: str, dimensions: Tuple[int, ...] = (512, 512), format: GpuTextureFormat = GpuTextureFormat.RGBA8UNORM, is_storage: bool = False, access: GpuAccess = GpuAccess.READ) -> GpuTexture:
        tex = GpuTexture(name, dimensions, format, access, is_storage)
        self.textures[name] = tex
        return tex

    def add_storage_texture(self, name: str, dimensions: Tuple[int, ...] = (512, 512), format: GpuTextureFormat = GpuTextureFormat.RGBA16F, access: GpuAccess = GpuAccess.READ_WRITE) -> GpuTexture:
        return self.add_texture(name, dimensions, format, is_storage=True, access=access)

    def add_sampler(self, name: str, filter_mode: str = "linear", address_mode: str = "clamp") -> GpuSampler:
        sampler = GpuSampler(name, filter_mode, address_mode)
        self.samplers[name] = sampler
        return sampler

    def add_compute_pass(self, pass_obj: GpuComputePass) -> None:
        self.passes.append(pass_obj)

    def add_render_pass(self, pass_obj: GpuRenderPass) -> None:
        self.passes.append(pass_obj)

    def add_barrier(self, source_pass: str, target_pass: str, resource_name: str) -> None:
        self.barriers.append((source_pass, target_pass, resource_name))


class GpuHazardChecker:
    """Compile-time hazard analysis for GPU render and compute graphs."""

    @staticmethod
    def analyze_graph(graph: GpuGraph) -> Tuple[List[GpuHazard], List[Tuple[str, str, str]]]:
        """
        Analyzes a GpuGraph for resource hazards:
        1. Simultaneous Read-Write conflicts within a single pass.
        2. Read-After-Write (RAW), Write-After-Read (WAR), Write-After-Write (WAW) across passes.

        Returns:
            Tuple of (list_of_hazards, computed_dependency_edges).
        """
        hazards: List[GpuHazard] = []
        dependency_edges: List[Tuple[str, str, str]] = []

        pass_accesses: List[GpuPassAccess] = []

        # Step 1: Extract pass access sets
        for p in graph.passes:
            p_access = GpuPassAccess(pass_name=p.name)
            if isinstance(p, GpuComputePass):
                p_access.reads.update(p.inputs)
                p_access.writes.update(p.outputs)
                p_access.read_writes.update(p.storage_bindings)
            elif isinstance(p, GpuRenderPass):
                p_access.reads.update(p.inputs)
                p_access.writes.update(p.color_attachments)
                if p.depth_attachment:
                    p_access.writes.add(p.depth_attachment)
                p_access.read_writes.update(p.storage_textures)
            pass_accesses.append(p_access)

        # Step 2: Check for simultaneous read-write hazards in a single pass
        for acc in pass_accesses:
            conflict = acc.reads & acc.writes
            for res in conflict:
                hazards.append(GpuHazard(
                    resource_name=res,
                    hazard_type=HazardType.SIMULTANEOUS_READ_WRITE,
                    source_pass=acc.pass_name,
                    target_pass=acc.pass_name,
                    message=f"Pass '{acc.pass_name}' simultaneously reads and writes resource '{res}' without barrier."
                ))

        # Step 3: Check across sequential passes
        existing_barriers = set(graph.barriers)

        for i in range(len(pass_accesses)):
            acc_i = pass_accesses[i]
            reads_i = acc_i.reads | acc_i.read_writes
            writes_i = acc_i.writes | acc_i.read_writes

            for j in range(i + 1, len(pass_accesses)):
                acc_j = pass_accesses[j]
                reads_j = acc_j.reads | acc_j.read_writes
                writes_j = acc_j.writes | acc_j.read_writes

                # Check RAW hazard (i writes, j reads)
                raw_conflict = writes_i & reads_j
                for res in raw_conflict:
                    edge = (acc_i.pass_name, acc_j.pass_name, res)
                    dependency_edges.append(edge)
                    if edge not in existing_barriers:
                        hazards.append(GpuHazard(
                            resource_name=res,
                            hazard_type=HazardType.READ_AFTER_WRITE,
                            source_pass=acc_i.pass_name,
                            target_pass=acc_j.pass_name,
                            message=f"Pass '{acc_j.pass_name}' reads resource '{res}' written by previous pass '{acc_i.pass_name}' without explicit barrier."
                        ))

                # Check WAR hazard (i reads, j writes)
                war_conflict = reads_i & writes_j
                for res in war_conflict:
                    edge = (acc_i.pass_name, acc_j.pass_name, res)
                    dependency_edges.append(edge)
                    if edge not in existing_barriers:
                        hazards.append(GpuHazard(
                            resource_name=res,
                            hazard_type=HazardType.WRITE_AFTER_READ,
                            source_pass=acc_i.pass_name,
                            target_pass=acc_j.pass_name,
                            message=f"Pass '{acc_j.pass_name}' overwrites resource '{res}' read by previous pass '{acc_i.pass_name}' without explicit barrier."
                        ))

                # Check WAW hazard (i writes, j writes)
                waw_conflict = writes_i & writes_j
                for res in waw_conflict:
                    edge = (acc_i.pass_name, acc_j.pass_name, res)
                    dependency_edges.append(edge)
                    if edge not in existing_barriers:
                        hazards.append(GpuHazard(
                            resource_name=res,
                            hazard_type=HazardType.WRITE_AFTER_WRITE,
                            source_pass=acc_i.pass_name,
                            target_pass=acc_j.pass_name,
                            message=f"Pass '{acc_j.pass_name}' overwrites resource '{res}' written by previous pass '{acc_i.pass_name}' without explicit barrier."
                        ))

        return hazards, dependency_edges
