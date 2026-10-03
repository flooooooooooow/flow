"""
FLOW Typed GPU Render & Compute Graph (#812).

Provides backend-independent graph representation for multi-pass GPU programs,
storage textures/buffers, ping-pong resources, workgroup memory/barriers,
transient allocations, explicit read/write access, compile-time hazard checks,
and pass dependency derivation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union


class GpuResourceType(str, Enum):
    BUFFER = "buffer"
    STORAGE_BUFFER = "storage_buffer"
    TEXTURE = "texture"
    STORAGE_TEXTURE = "storage_texture"
    SAMPLER = "sampler"
    PING_PONG = "ping_pong"


class ResourceAccess(str, Enum):
    READ = "read"
    WRITE = "write"
    READ_WRITE = "read_write"
    SWAP = "swap"


@dataclass
class ResourceBinding:
    """Binding of a resource to a parameter/attachment in a GPU pass."""
    param_name: str
    resource_name: str
    access: ResourceAccess = ResourceAccess.READ
    ping_pong_base: Optional[str] = None
    ping_pong_mode: Optional[str] = None  # "read", "write", "next"

    @property
    def key(self) -> str:
        return f"{self.param_name}:{self.resource_name}:{self.access.value}"


@dataclass
class GpuResource:
    """A typed GPU buffer, texture, or sampler resource."""
    name: str
    resource_type: GpuResourceType
    format_or_elem: str  # e.g. "rgba16f", "f32", "r32f"
    dimensions: Tuple[int, ...] = (1,)  # e.g. (128, 128) or (1024,)
    access: ResourceAccess = ResourceAccess.READ
    is_transient: bool = False
    is_ping_pong: bool = False

    @property
    def is_texture(self) -> bool:
        return self.resource_type in (
            GpuResourceType.TEXTURE,
            GpuResourceType.STORAGE_TEXTURE,
        )

    @property
    def is_buffer(self) -> bool:
        return self.resource_type in (
            GpuResourceType.BUFFER,
            GpuResourceType.STORAGE_BUFFER,
        )


class PingPongResource:
    """A pair of resources used for alternating ping-pong reads/writes."""

    def __init__(
        self,
        base_name: str,
        resource_type: GpuResourceType,
        format_or_elem: str,
        dimensions: Tuple[int, ...] = (1,),
        is_transient: bool = False,
    ):
        self.base_name = base_name
        self.resource_type = resource_type
        self.format_or_elem = format_or_elem
        self.dimensions = dimensions
        self.is_transient = is_transient
        self._read_idx = 0

        self.front = GpuResource(
            name=f"{base_name}_0",
            resource_type=resource_type,
            format_or_elem=format_or_elem,
            dimensions=dimensions,
            access=ResourceAccess.READ_WRITE,
            is_transient=is_transient,
            is_ping_pong=True,
        )
        self.back = GpuResource(
            name=f"{base_name}_1",
            resource_type=resource_type,
            format_or_elem=format_or_elem,
            dimensions=dimensions,
            access=ResourceAccess.READ_WRITE,
            is_transient=is_transient,
            is_ping_pong=True,
        )

    @property
    def read(self) -> GpuResource:
        """Resource currently bound for reading."""
        return self.front if self._read_idx == 0 else self.back

    @property
    def write(self) -> GpuResource:
        """Resource currently bound for writing."""
        return self.back if self._read_idx == 0 else self.front

    @property
    def next(self) -> GpuResource:
        """Alias for write resource."""
        return self.write

    def swap(self) -> None:
        """Exchange read and write resource roles."""
        self._read_idx = 1 - self._read_idx


@dataclass
class ComputePass:
    """A compute dispatch pass in the GPU graph."""
    name: str
    kernel_name: str
    dispatch_dims: Tuple[int, int, int] = (1, 1, 1)
    workgroup_size: Tuple[int, int, int] = (16, 16, 1)
    bindings: List[ResourceBinding] = field(default_factory=list)
    workgroup_memory_bytes: int = 0


@dataclass
class RenderPass:
    """A render pass drawing geometry or fullscreen quads in the GPU graph."""
    name: str
    shader_name: str
    color_attachments: List[ResourceBinding] = field(default_factory=list)
    depth_attachment: Optional[ResourceBinding] = None
    bindings: List[ResourceBinding] = field(default_factory=list)


@dataclass
class RepeatPassBlock:
    """A repeated sequence of passes (e.g. Jacobi iterations in fluid solver)."""
    count: int
    passes: List[Union[ComputePass, RenderPass]] = field(default_factory=list)
    swaps: List[str] = field(default_factory=list)  # Ping-pong base names swapped each iteration


GpuPass = Union[ComputePass, RenderPass]


class GpuHazardError(Exception):
    """Raised when a GPU graph resource hazard or alias violation is detected."""


@dataclass
class DependencyEdge:
    """Dependency edge between two passes due to resource access."""
    producer: str
    consumer: str
    resource_name: str
    dependency_type: str  # "RAW" (Read-After-Write), "WAW", "WAR"


@dataclass
class PassDependencyGraph:
    """Directed Acyclic Graph (DAG) of pass dependencies."""
    nodes: List[str]
    edges: List[DependencyEdge]
    adjacency: Dict[str, Set[str]] = field(default_factory=dict)
    in_degree: Dict[str, int] = field(default_factory=dict)

    def topological_sort(self) -> List[str]:
        """Returns topological ordering of passes."""
        in_deg = dict(self.in_degree)
        queue = [node for node in self.nodes if in_deg.get(node, 0) == 0]
        sorted_nodes: List[str] = []

        while queue:
            node = queue.pop(0)
            sorted_nodes.append(node)
            for neighbor in sorted(self.adjacency.get(node, set())):
                in_deg[neighbor] -= 1
                if in_deg[neighbor] == 0:
                    queue.append(neighbor)

        if len(sorted_nodes) != len(self.nodes):
            raise GpuHazardError("Cyclic pass dependency detected in GPU graph")
        return sorted_nodes

    def execution_stages(self) -> List[List[str]]:
        """Groups passes into independent parallel execution stages/encoders."""
        in_deg = dict(self.in_degree)
        current_stage = [node for node in self.nodes if in_deg.get(node, 0) == 0]
        stages: List[List[str]] = []

        visited_count = 0
        while current_stage:
            stages.append(list(current_stage))
            visited_count += len(current_stage)
            next_stage: List[str] = []
            for node in current_stage:
                for neighbor in sorted(self.adjacency.get(node, set())):
                    in_deg[neighbor] -= 1
                    if in_deg[neighbor] == 0:
                        next_stage.append(neighbor)
            current_stage = next_stage

        if visited_count != len(self.nodes):
            raise GpuHazardError("Cyclic pass dependency detected during stage grouping")
        return stages


class GpuGraph:
    """
    A backend-independent render and compute graph.

    Represents GPU resources, ping-pong targets, transient allocations, compute
    and render passes, repeat loops, compile-time hazard checks, and pass
    dependency derivation.
    """

    def __init__(self, name: str = "main_frame"):
        self.name = name
        self.resources: Dict[str, GpuResource] = {}
        self.ping_pongs: Dict[str, PingPongResource] = {}
        self.passes: List[Union[GpuPass, RepeatPassBlock]] = []

    def add_resource(
        self,
        name: str,
        resource_type: GpuResourceType,
        format_or_elem: str,
        dimensions: Tuple[int, ...] = (1,),
        access: ResourceAccess = ResourceAccess.READ,
        is_transient: bool = False,
    ) -> GpuResource:
        res = GpuResource(
            name=name,
            resource_type=resource_type,
            format_or_elem=format_or_elem,
            dimensions=dimensions,
            access=access,
            is_transient=is_transient,
        )
        self.resources[name] = res
        return res

    def add_ping_pong(
        self,
        base_name: str,
        resource_type: GpuResourceType,
        format_or_elem: str,
        dimensions: Tuple[int, ...] = (1,),
        is_transient: bool = False,
    ) -> PingPongResource:
        pp = PingPongResource(
            base_name=base_name,
            resource_type=resource_type,
            format_or_elem=format_or_elem,
            dimensions=dimensions,
            is_transient=is_transient,
        )
        self.ping_pongs[base_name] = pp
        self.resources[pp.front.name] = pp.front
        self.resources[pp.back.name] = pp.back
        return pp

    def add_compute_pass(
        self,
        name: str,
        kernel_name: str,
        dispatch_dims: Tuple[int, int, int] = (1, 1, 1),
        workgroup_size: Tuple[int, int, int] = (16, 16, 1),
        bindings: Optional[List[ResourceBinding]] = None,
        workgroup_memory_bytes: int = 0,
    ) -> ComputePass:
        cp = ComputePass(
            name=name,
            kernel_name=kernel_name,
            dispatch_dims=dispatch_dims,
            workgroup_size=workgroup_size,
            bindings=bindings or [],
            workgroup_memory_bytes=workgroup_memory_bytes,
        )
        self.passes.append(cp)
        return cp

    def add_render_pass(
        self,
        name: str,
        shader_name: str,
        color_attachments: Optional[List[ResourceBinding]] = None,
        depth_attachment: Optional[ResourceBinding] = None,
        bindings: Optional[List[ResourceBinding]] = None,
    ) -> RenderPass:
        rp = RenderPass(
            name=name,
            shader_name=shader_name,
            color_attachments=color_attachments or [],
            depth_attachment=depth_attachment,
            bindings=bindings or [],
        )
        self.passes.append(rp)
        return rp

    def add_repeat_block(
        self,
        count: int,
        passes: List[GpuPass],
        swaps: Optional[List[str]] = None,
    ) -> RepeatPassBlock:
        block = RepeatPassBlock(count=count, passes=passes, swaps=swaps or [])
        self.passes.append(block)
        return block

    def get_resource(self, name: str) -> Optional[GpuResource]:
        if name in self.resources:
            return self.resources[name]
        if name in self.ping_pongs:
            return self.ping_pongs[name].read
        return None

    def resolve_binding_resource(self, binding: ResourceBinding) -> str:
        """Resolve resource name for a binding, dynamically respecting current ping-pong state."""
        if binding.ping_pong_base and binding.ping_pong_base in self.ping_pongs:
            pp = self.ping_pongs[binding.ping_pong_base]
            if binding.ping_pong_mode in ("write", "next"):
                return pp.write.name
            return pp.read.name
        return binding.resource_name

    def _instantiate_pass(self, p: GpuPass, instance_name: str) -> GpuPass:
        """Create a pass instance with binding resource names resolved against current ping-pong state."""
        if isinstance(p, ComputePass):
            resolved_bindings = [
                ResourceBinding(
                    param_name=b.param_name,
                    resource_name=self.resolve_binding_resource(b),
                    access=b.access,
                    ping_pong_base=b.ping_pong_base,
                    ping_pong_mode=b.ping_pong_mode,
                )
                for b in p.bindings
            ]
            return ComputePass(
                name=instance_name,
                kernel_name=p.kernel_name,
                dispatch_dims=p.dispatch_dims,
                workgroup_size=p.workgroup_size,
                bindings=resolved_bindings,
                workgroup_memory_bytes=p.workgroup_memory_bytes,
            )
        else:
            resolved_bindings = [
                ResourceBinding(
                    param_name=b.param_name,
                    resource_name=self.resolve_binding_resource(b),
                    access=b.access,
                    ping_pong_base=b.ping_pong_base,
                    ping_pong_mode=b.ping_pong_mode,
                )
                for b in p.bindings
            ]
            resolved_colors = [
                ResourceBinding(
                    param_name=b.param_name,
                    resource_name=self.resolve_binding_resource(b),
                    access=b.access,
                    ping_pong_base=b.ping_pong_base,
                    ping_pong_mode=b.ping_pong_mode,
                )
                for b in p.color_attachments
            ]
            resolved_depth = None
            if p.depth_attachment:
                b = p.depth_attachment
                resolved_depth = ResourceBinding(
                    param_name=b.param_name,
                    resource_name=self.resolve_binding_resource(b),
                    access=b.access,
                    ping_pong_base=b.ping_pong_base,
                    ping_pong_mode=b.ping_pong_mode,
                )
            return RenderPass(
                name=instance_name,
                shader_name=p.shader_name,
                color_attachments=resolved_colors,
                depth_attachment=resolved_depth,
                bindings=resolved_bindings,
            )

    def flatten_passes(self) -> List[Tuple[str, GpuPass]]:
        """
        Flatten repeat blocks into concrete pass execution steps,
        updating ping-pong states across iterations and dynamically re-binding resources.
        Returns list of (pass_instance_name, pass_obj).
        """
        # Save initial ping-pong state
        initial_states = {name: pp._read_idx for name, pp in self.ping_pongs.items()}

        flattened: List[Tuple[str, GpuPass]] = []
        try:
            for pass_or_block in self.passes:
                if isinstance(pass_or_block, (ComputePass, RenderPass)):
                    cloned_pass = self._instantiate_pass(pass_or_block, pass_or_block.name)
                    flattened.append((pass_or_block.name, cloned_pass))
                elif isinstance(pass_or_block, RepeatPassBlock):
                    for iter_idx in range(pass_or_block.count):
                        for inner_pass in pass_or_block.passes:
                            instance_name = f"{inner_pass.name}_iter{iter_idx}"
                            cloned_pass = self._instantiate_pass(inner_pass, instance_name)
                            flattened.append((instance_name, cloned_pass))
                        for pp_name in pass_or_block.swaps:
                            if pp_name in self.ping_pongs:
                                self.ping_pongs[pp_name].swap()
        finally:
            # Restore initial ping-pong state
            for name, idx in initial_states.items():
                self.ping_pongs[name]._read_idx = idx

        return flattened

    def validate_hazards(self, max_workgroup_memory: int = 32768) -> None:
        """
        Validate resource access hazards and alias conflicts across all passes.

        Checks:
        1. All referenced resources are declared in the graph.
        2. Same-Pass Read/Write Conflict: a pass cannot bind a resource as both
           READ and WRITE unless explicitly configured as READ_WRITE.
        3. Conflicting Binding Aliases: multiple parameters in a single pass
           cannot bind to the same physical resource with conflicting access modes.
        4. Workgroup Memory Limit: workgroup_memory_bytes cannot exceed max_workgroup_memory.
        """
        flattened = self.flatten_passes()

        for pass_instance_name, pass_obj in flattened:
            # Check workgroup memory
            if isinstance(pass_obj, ComputePass):
                if pass_obj.workgroup_memory_bytes > max_workgroup_memory:
                    raise GpuHazardError(
                        f"Pass '{pass_instance_name}' exceeds maximum workgroup memory: "
                        f"{pass_obj.workgroup_memory_bytes} > {max_workgroup_memory} bytes"
                    )

            # Collect bindings for this pass instance
            all_bindings: List[ResourceBinding] = list(pass_obj.bindings)
            if isinstance(pass_obj, RenderPass):
                all_bindings.extend(pass_obj.color_attachments)
                if pass_obj.depth_attachment:
                    all_bindings.append(pass_obj.depth_attachment)

            # Map resource_name -> list of ResourceBinding in this pass
            res_to_bindings: Dict[str, List[ResourceBinding]] = {}
            for b in all_bindings:
                res_name = b.resource_name
                # Verify resource existence
                if res_name not in self.resources:
                    raise GpuHazardError(
                        f"Pass '{pass_instance_name}' references undeclared resource '{res_name}'"
                    )
                res_to_bindings.setdefault(res_name, []).append(b)

            # Check same-pass read/write and alias hazards
            for res_name, bindings in res_to_bindings.items():
                accesses = {b.access for b in bindings}
                has_read = ResourceAccess.READ in accesses
                has_write = ResourceAccess.WRITE in accesses
                has_rw = ResourceAccess.READ_WRITE in accesses

                # Same-pass read and write hazard without READ_WRITE mode
                if has_read and has_write and not has_rw:
                    raise GpuHazardError(
                        f"Pass '{pass_instance_name}' has same-pass read/write hazard on "
                        f"resource '{res_name}'. Use separate read/write ping-pong resources "
                        f"or explicit READ_WRITE access mode."
                    )

                # Parameter alias conflict with conflicting modes
                if len(bindings) > 1:
                    params = [b.param_name for b in bindings]
                    if (has_read and has_write) or (has_rw and len(bindings) > 1):
                        raise GpuHazardError(
                            f"Pass '{pass_instance_name}' has conflicting binding alias "
                            f"on resource '{res_name}' across parameters {params}"
                        )

    def compute_dependencies(self) -> PassDependencyGraph:
        """
        Derive Directed Acyclic Graph (DAG) of pass dependencies based on
        resource access patterns (RAW, WAW, WAR).
        """
        self.validate_hazards()
        flattened = self.flatten_passes()

        pass_names = [pname for pname, _ in flattened]
        adj: Dict[str, Set[str]] = {pname: set() for pname in pass_names}
        in_deg: Dict[str, int] = {pname: 0 for pname in pass_names}
        edges: List[DependencyEdge] = []

        # Track last reader(s) and writer for each physical resource
        last_writers: Dict[str, str] = {}
        last_readers: Dict[str, Set[str]] = {}

        for pname, pass_obj in flattened:
            bindings = list(pass_obj.bindings)
            if isinstance(pass_obj, RenderPass):
                bindings.extend(pass_obj.color_attachments)
                if pass_obj.depth_attachment:
                    bindings.append(pass_obj.depth_attachment)

            for b in bindings:
                res_name = b.resource_name
                mode = b.access

                # Read access (RAW dependency if previously written)
                if mode in (ResourceAccess.READ, ResourceAccess.READ_WRITE):
                    if res_name in last_writers:
                        prev_writer = last_writers[res_name]
                        if prev_writer != pname and pname not in adj[prev_writer]:
                            adj[prev_writer].add(pname)
                            in_deg[pname] += 1
                            edges.append(DependencyEdge(prev_writer, pname, res_name, "RAW"))
                    last_readers.setdefault(res_name, set()).add(pname)

                # Write access (WAW and WAR dependencies)
                if mode in (ResourceAccess.WRITE, ResourceAccess.READ_WRITE):
                    # WAW: Write-After-Write
                    if res_name in last_writers:
                        prev_writer = last_writers[res_name]
                        if prev_writer != pname and pname not in adj[prev_writer]:
                            adj[prev_writer].add(pname)
                            in_deg[pname] += 1
                            edges.append(DependencyEdge(prev_writer, pname, res_name, "WAW"))

                    # WAR: Write-After-Read
                    if res_name in last_readers:
                        for prev_reader in last_readers[res_name]:
                            if prev_reader != pname and pname not in adj[prev_reader]:
                                adj[prev_reader].add(pname)
                                in_deg[pname] += 1
                                edges.append(DependencyEdge(prev_reader, pname, res_name, "WAR"))
                        last_readers[res_name] = set()

                    last_writers[res_name] = pname

        return PassDependencyGraph(
            nodes=pass_names,
            edges=edges,
            adjacency=adj,
            in_degree=in_deg,
        )

    def generate_metal(self) -> Dict[str, str]:
        """
        Generate Metal (MSL + Objective-C/Metal host orchestration) code
        for executing the GPU graph frame.
        """
        dag = self.compute_dependencies()
        order = dag.topological_sort()
        flattened_dict = dict(self.flatten_passes())

        lines = [
            f"// Generated Metal pipeline orchestration for GPU graph '{self.name}'",
            "#import <Metal/Metal.h>",
            "#import <Foundation/Foundation.h>",
            "",
            f"void run_{self.name}_frame(id<MTLDevice> device, id<MTLCommandQueue> commandQueue) {{",
            "    @autoreleasepool {",
            "        id<MTLCommandBuffer> commandBuffer = [commandQueue commandBuffer];",
            "",
            "        // 1. Allocate GPU resources",
        ]

        # Allocate static and ping-pong resources
        for res_name, res in self.resources.items():
            if res.is_texture:
                w = res.dimensions[0] if len(res.dimensions) > 0 else 1
                h = res.dimensions[1] if len(res.dimensions) > 1 else 1
                fmt_msl = {
                    "rgba8unorm": "MTLPixelFormatRGBA8Unorm",
                    "rgba16f": "MTLPixelFormatRGBA16Float",
                    "rgba32f": "MTLPixelFormatRGBA32Float",
                    "r16f": "MTLPixelFormatR16Float",
                    "r32f": "MTLPixelFormatR32Float",
                }.get(res.format_or_elem, "MTLPixelFormatRGBA8Unorm")
                lines.append(
                    f"        MTLTextureDescriptor* desc_{res_name} = "
                    f"[MTLTextureDescriptor texture2DDescriptorWithPixelFormat:{fmt_msl} "
                    f"width:{w} height:{h} mipmapped:NO];"
                )
                lines.append(
                    f"        desc_{res_name}.usage = MTLTextureUsageShaderRead | MTLTextureUsageShaderWrite | MTLTextureUsageRenderTarget;"
                )
                lines.append(
                    f"        id<MTLTexture> res_{res_name} = [device newTextureWithDescriptor:desc_{res_name}];"
                )
            else:
                sz = res.dimensions[0] * 4  # default f32
                lines.append(
                    f"        id<MTLBuffer> res_{res_name} = "
                    f"[device newBufferWithLength:{sz} options:MTLResourceStorageModeShared];"
                )

        lines.append("")
        lines.append("        // 2. Pass execution order derived from resource DAG")

        for pname in order:
            pobj = flattened_dict[pname]
            lines.append(f"        // Pass: {pname}")

            if isinstance(pobj, ComputePass):
                lines.append("        {")
                lines.append(
                    f"            id<MTLComputeCommandEncoder> encoder = [commandBuffer computeCommandEncoder];"
                )
                for idx, b in enumerate(pobj.bindings):
                    lines.append(
                        f"            [encoder setTexture:res_{b.resource_name} atIndex:{idx}];"
                    )
                dx, dy, dz = pobj.dispatch_dims
                wx, wy, wz = pobj.workgroup_size
                lines.append(
                    f"            MTLSize gridSize = MTLSizeMake({dx}, {dy}, {dz});"
                )
                lines.append(
                    f"            MTLSize threadgroupSize = MTLSizeMake({wx}, {wy}, {wz});"
                )
                lines.append(
                    "            [encoder dispatchThreadgroups:gridSize threadsPerThreadgroup:threadgroupSize];"
                )
                lines.append("            [encoder endEncoding];")
                lines.append("        }")
            elif isinstance(pobj, RenderPass):
                lines.append("        {")
                lines.append("            MTLRenderPassDescriptor* renderPassDesc = [MTLRenderPassDescriptor renderPassDescriptor];")
                color_target = pobj.color_attachments[0].resource_name if pobj.color_attachments else (pobj.bindings[0].resource_name if pobj.bindings else "surface")
                lines.append(f"            renderPassDesc.colorAttachments[0].texture = res_{color_target};")
                lines.append("            renderPassDesc.colorAttachments[0].loadAction = MTLLoadActionClear;")
                lines.append("            renderPassDesc.colorAttachments[0].storeAction = MTLStoreActionStore;")
                lines.append("            id<MTLRenderCommandEncoder> renderEncoder = [commandBuffer renderCommandEncoderWithDescriptor:renderPassDesc];")
                for idx, b in enumerate(pobj.bindings):
                    lines.append(f"            [renderEncoder setFragmentTexture:res_{b.resource_name} atIndex:{idx}];")
                lines.append("            [renderEncoder drawPrimitives:MTLPrimitiveTypeTriangle vertexStart:0 vertexCount:6];")
                lines.append("            [renderEncoder endEncoding];")
                lines.append("        }")

        lines.append("")
        lines.append("        [commandBuffer commit];")
        lines.append("        [commandBuffer waitUntilCompleted];")
        lines.append("    }")
        lines.append("}")

        return {
            "metal_host_code": "\n".join(lines) + "\n",
            "name": self.name,
        }

    def generate_webgpu_js(self) -> Dict[str, str]:
        """
        Generate WGSL + JavaScript WebGPU orchestration code for executing the GPU graph frame.
        """
        dag = self.compute_dependencies()
        order = dag.topological_sort()
        flattened_dict = dict(self.flatten_passes())

        js_lines = [
            f"// Generated WebGPU orchestration for GPU graph '{self.name}'",
            f"export async function run_{self.name}_frame(device) {{",
            "    const commandEncoder = device.createCommandEncoder();",
            "",
            "    // 1. Create WebGPU Resources",
        ]

        for res_name, res in self.resources.items():
            if res.is_texture:
                w = res.dimensions[0] if len(res.dimensions) > 0 else 1
                h = res.dimensions[1] if len(res.dimensions) > 1 else 1
                fmt_wgpu = {
                    "rgba8unorm": "rgba8unorm",
                    "rgba16f": "rgba16float",
                    "rgba32f": "rgba32float",
                    "r16f": "r16float",
                    "r32f": "r32float",
                }.get(res.format_or_elem, "rgba8unorm")
                js_lines.append(f"    const res_{res_name} = device.createTexture({{")
                js_lines.append(f"        size: [{w}, {h}, 1],")
                js_lines.append(f"        format: '{fmt_wgpu}',")
                js_lines.append(
                    "        usage: GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.STORAGE_BINDING | GPUTextureUsage.RENDER_ATTACHMENT,"
                )
                js_lines.append("    });")
            else:
                sz = res.dimensions[0] * 4
                js_lines.append(f"    const res_{res_name} = device.createBuffer({{")
                js_lines.append(f"        size: {sz},")
                js_lines.append(
                    "        usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC | GPUBufferUsage.COPY_DST,"
                )
                js_lines.append("    });")

        js_lines.append("")
        js_lines.append("    // 2. Pass Execution (DAG Order)")

        for pname in order:
            pobj = flattened_dict[pname]
            js_lines.append(f"    // Pass: {pname}")

            if isinstance(pobj, ComputePass):
                js_lines.append("    {")
                js_lines.append("        const passEncoder = commandEncoder.beginComputePass();")
                dx, dy, dz = pobj.dispatch_dims
                js_lines.append(f"        passEncoder.dispatchWorkgroups({dx}, {dy}, {dz});")
                js_lines.append("        passEncoder.end();")
                js_lines.append("    }")
            elif isinstance(pobj, RenderPass):
                color_target = pobj.color_attachments[0].resource_name if pobj.color_attachments else (pobj.bindings[0].resource_name if pobj.bindings else "surface")
                js_lines.append("    {")
                js_lines.append("        const renderPassDesc = {")
                js_lines.append("            colorAttachments: [{")
                js_lines.append(f"                view: res_{color_target}.createView(),")
                js_lines.append("                clearValue: { r: 0, g: 0, b: 0, a: 1 },")
                js_lines.append("                loadOp: 'clear',")
                js_lines.append("                storeOp: 'store',")
                js_lines.append("            }],")
                js_lines.append("        };")
                js_lines.append("        const passEncoder = commandEncoder.beginRenderPass(renderPassDesc);")
                js_lines.append("        passEncoder.draw(6);")
                js_lines.append("        passEncoder.end();")
                js_lines.append("    }")

        js_lines.append("")
        js_lines.append("    device.queue.submit([commandEncoder.finish()]);")
        js_lines.append("}")

        return {
            "webgpu_js_code": "\n".join(js_lines) + "\n",
            "name": self.name,
        }


def _extract_brace_content(source: str, open_idx: int) -> Tuple[str, int]:
    depth = 0
    i = open_idx
    while i < len(source):
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth == 0:
                return source[open_idx + 1:i], i + 1
        i += 1
    raise GpuHazardError("Unclosed '{' in GPU graph DSL")


_GPU_RESOURCE_BLOCK_RX = re.compile(r"\bgpu\s+resource\s*\{", re.MULTILINE)
_GPU_FRAME_BLOCK_RX = re.compile(r"\bgpu\s+frame\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{", re.MULTILINE)


def parse_gpu_graph(source: str) -> GpuGraph:
    """
    Parse `gpu resource` and `gpu frame` blocks from Flow source code into a GpuGraph.
    """
    graph = GpuGraph("gpu_frame")

    # 1. Parse `gpu resource { ... }` if present
    res_m = _GPU_RESOURCE_BLOCK_RX.search(source)
    if res_m:
        brace_idx = source.find("{", res_m.start())
        res_body, _ = _extract_brace_content(source, brace_idx)
        _parse_resource_block(res_body, graph)

    # 2. Parse `gpu frame <name> { ... }`
    frame_m = _GPU_FRAME_BLOCK_RX.search(source)
    if frame_m:
        graph.name = frame_m.group(1)
        brace_idx = source.find("{", frame_m.start())
        frame_body, _ = _extract_brace_content(source, brace_idx)
        _parse_frame_block(frame_body, graph)

    return graph


def _parse_resource_block(body: str, graph: GpuGraph) -> None:
    # Lines like: texture velocity: rgba16f(128, 128) ping_pong
    # or: buffer particle_data: f32(1024) transient
    res_line_rx = re.compile(
        r"(texture|buffer|storage_texture|storage_buffer)\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([A-Za-z0-9_]+)(?:\(([^)]*)\))?\s*(ping_pong|transient)*\s*(ping_pong|transient)*",
        re.IGNORECASE,
    )
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("//") or line.startswith("#"):
            continue
        m = res_line_rx.search(line)
        if not m:
            continue
        kind_str, name, fmt, dims_str, flag1, flag2 = m.groups()
        flags = {f.lower() for f in (flag1, flag2) if f}

        dims: Tuple[int, ...] = (1,)
        if dims_str:
            dims = tuple(int(d.strip()) for d in dims_str.split(",") if d.strip())

        is_ping_pong = "ping_pong" in flags
        is_transient = "transient" in flags

        rtype = GpuResourceType.TEXTURE
        if kind_str.lower() == "buffer":
            rtype = GpuResourceType.BUFFER
        elif kind_str.lower() == "storage_buffer":
            rtype = GpuResourceType.STORAGE_BUFFER
        elif kind_str.lower() == "storage_texture":
            rtype = GpuResourceType.STORAGE_TEXTURE

        if is_ping_pong:
            graph.add_ping_pong(
                base_name=name,
                resource_type=rtype,
                format_or_elem=fmt,
                dimensions=dims,
                is_transient=is_transient,
            )
        else:
            graph.add_resource(
                name=name,
                resource_type=rtype,
                format_or_elem=fmt,
                dimensions=dims,
                is_transient=is_transient,
            )


def _parse_frame_block(body: str, graph: GpuGraph) -> None:
    # Parses compute passes, repeat blocks, and render passes inside gpu frame.
    lines = [ln.strip() for ln in body.splitlines() if ln.strip() and not ln.strip().startswith("//")]

    i = 0
    while i < len(lines):
        line = lines[i]

        # repeat N { ... }
        repeat_m = re.match(r"^repeat\s+(\d+)\s*\{", line)
        if repeat_m:
            count = int(repeat_m.group(1))
            # collect block
            block_lines = []
            i += 1
            while i < len(lines) and lines[i] != "}":
                block_lines.append(lines[i])
                i += 1
            i += 1  # skip '}'

            inner_passes: List[GpuPass] = []
            swaps: List[str] = []
            for inner_line in block_lines:
                if inner_line.endswith(".swap()"):
                    pp_name = inner_line[:-7].strip()
                    swaps.append(pp_name)
                elif inner_line.startswith("compute"):
                    cp = _parse_compute_pass_line(inner_line, graph)
                    if cp:
                        inner_passes.append(cp)

            graph.add_repeat_block(count=count, passes=inner_passes, swaps=swaps)
            continue

        # compute pass: compute advect[16, 16, 1](velocity.read, velocity.write)
        if line.startswith("compute"):
            cp = _parse_compute_pass_line(line, graph)
            if cp:
                graph.passes.append(cp)

        # render pass: render surface { draw fluid(velocity.read) }
        elif line.startswith("render"):
            render_m = re.match(r"^render\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{", line)
            if render_m:
                pass_name = render_m.group(1)
                i += 1
                draw_line = ""
                while i < len(lines) and lines[i] != "}":
                    if lines[i].startswith("draw"):
                        draw_line = lines[i]
                    i += 1
                if draw_line:
                    rp = _parse_draw_line(pass_name, draw_line, graph)
                    if rp:
                        graph.passes.append(rp)

        i += 1


def _parse_compute_pass_line(line: str, graph: GpuGraph) -> Optional[ComputePass]:
    # e.g.: compute advect[16, 16, 1](velocity.read, velocity.write)
    # or: compute divergence[128, 128, 1](velocity.read, divergence.write)
    m = re.match(
        r"^compute\s+([A-Za-z_][A-Za-z0-9_]*)(?:\[\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\])?\s*\(([^)]*)\)",
        line,
    )
    if not m:
        return None
    kernel_name, dx, dy, dz, args_str = m.groups()
    dispatch_dims = (int(dx or 1), int(dy or 1), int(dz or 1))

    bindings: List[ResourceBinding] = []
    if args_str:
        for idx, raw_arg in enumerate(args_str.split(",")):
            raw_arg = raw_arg.strip()
            if not raw_arg:
                continue
            param_name = f"arg{idx}"
            access = ResourceAccess.READ
            res_name = raw_arg
            pp_base = None
            pp_mode = None

            if "." in raw_arg:
                base, mode_str = raw_arg.split(".", 1)
                if mode_str in ("read", "read_write", "write", "next"):
                    access = ResourceAccess.WRITE if mode_str in ("write", "next") else ResourceAccess.READ
                if base in graph.ping_pongs:
                    pp_base = base
                    pp_mode = mode_str
                    pp = graph.ping_pongs[base]
                    res_name = pp.write.name if mode_str in ("write", "next") else pp.read.name
                else:
                    res_name = base

            bindings.append(
                ResourceBinding(
                    param_name=param_name,
                    resource_name=res_name,
                    access=access,
                    ping_pong_base=pp_base,
                    ping_pong_mode=pp_mode,
                )
            )

    return ComputePass(
        name=kernel_name,
        kernel_name=kernel_name,
        dispatch_dims=dispatch_dims,
        bindings=bindings,
    )


def _parse_draw_line(pass_name: str, line: str, graph: GpuGraph) -> Optional[RenderPass]:
    # e.g.: draw fluid(velocity.read, dye.read)
    m = re.match(r"^draw\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)", line)
    if not m:
        return None
    shader_name, args_str = m.groups()

    bindings: List[ResourceBinding] = []
    if args_str:
        for idx, raw_arg in enumerate(args_str.split(",")):
            raw_arg = raw_arg.strip()
            if not raw_arg:
                continue
            param_name = f"arg{idx}"
            access = ResourceAccess.READ
            res_name = raw_arg
            pp_base = None
            pp_mode = None

            if "." in raw_arg:
                base, mode_str = raw_arg.split(".", 1)
                if mode_str in ("read", "read_write", "write", "next"):
                    access = ResourceAccess.WRITE if mode_str in ("write", "next") else ResourceAccess.READ
                if base in graph.ping_pongs:
                    pp_base = base
                    pp_mode = mode_str
                    pp = graph.ping_pongs[base]
                    res_name = pp.write.name if mode_str in ("write", "next") else pp.read.name
                else:
                    res_name = base

            bindings.append(
                ResourceBinding(
                    param_name=param_name,
                    resource_name=res_name,
                    access=access,
                    ping_pong_base=pp_base,
                    ping_pong_mode=pp_mode,
                )
            )

    return RenderPass(
        name=pass_name,
        shader_name=shader_name,
        bindings=bindings,
    )
