#!/usr/bin/env python3
"""
FLOW Metal Shader Generator
Transpiles @gpu functions to Metal Shading Language (MSL).
"""

from typing import List, Dict, Any, Tuple
from pathlib import Path
from .parser import (
    FunctionDecl,
    Block,
    Statement,
    Expression,
    VarDecl,
    Assignment,
    IfStatement,
    WhileStatement,
    ForStatement,
    ReturnStatement,
    Literal,
    Variable,
    BinaryOperation,
    UnaryOperation,
    FunctionCall,
    ArrayAccess,
    FieldAccess,
    Type,
)


class MetalCodegen:
    """Generate Metal Shading Language code from FLOW GPU functions."""

    # Type mappings from FLOW to Metal
    TYPE_MAP = {
        "i32": "int",
        "i64": "long",
        "u32": "uint",
        "u64": "ulong",
        "f32": "float",
        "f64": "double",  # Note: double support varies by device
        "bool": "bool",
        "void": "void",
    }

    # Built-in GPU functions to Metal equivalents
    GPU_BUILTINS = {
        "gpu_thread_id": "thread_position_in_grid",
        "gpu_thread_id_x": "thread_position_in_grid.x",
        "gpu_thread_id_y": "thread_position_in_grid.y",
        "gpu_thread_id_z": "thread_position_in_grid.z",
        "gpu_block_id": "threadgroup_position_in_grid",
        "gpu_block_id_x": "threadgroup_position_in_grid.x",
        "gpu_block_id_y": "threadgroup_position_in_grid.y",
        "gpu_block_id_z": "threadgroup_position_in_grid.z",
        "gpu_local_id": "thread_position_in_threadgroup",
        "gpu_local_id_x": "thread_position_in_threadgroup.x",
        "gpu_block_size": "threads_per_threadgroup",
        "gpu_grid_size": "threads_per_grid",
        "gpu_barrier": "threadgroup_barrier(mem_flags::mem_threadgroup)",
        "gpu_sync": "threadgroup_barrier(mem_flags::mem_threadgroup)",
    }

    def __init__(self):
        self.indent_level = 0
        self.buffer_bindings: Dict[str, int] = {}
        self.binding_counter = 0
        self.kernel_name = ""

    def indent(self) -> str:
        return "    " * self.indent_level

    def map_type(self, flow_type: Type, is_buffer: bool = True) -> str:
        """Convert FLOW type to Metal type."""
        type_name = flow_type.name

        # Handle monomorphized array types (array_f32, array_i32, etc.)
        if type_name.startswith("array_") or (
            hasattr(flow_type, "element_type") and flow_type.element_type
        ):
            if flow_type.element_type:
                inner = flow_type.element_type.name
            else:
                inner = type_name[6:]  # array_f32 -> f32
            metal_inner = self.TYPE_MAP.get(inner, inner)
            return f"device {metal_inner}*"

        # Handle array types -> device buffer pointers
        if type_name.startswith("array<") or type_name.startswith("ptr<"):
            inner = (
                type_name[6:-1] if type_name.startswith("array<") else type_name[4:-1]
            )
            metal_inner = self.TYPE_MAP.get(inner, inner)
            return f"device {metal_inner}*"

        # Handle vec types -> Metal SIMD types
        if type_name.startswith("vec"):
            # vec4<f32> -> float4
            import re

            match = re.match(r"vec(\d+)<(\w+)>", type_name)
            if match:
                n, inner = match.groups()
                metal_inner = self.TYPE_MAP.get(inner, inner)
                return f"{metal_inner}{n}"

        return self.TYPE_MAP.get(type_name, type_name)

    def is_array_type(self, flow_type: Type) -> bool:
        """Check if type is an array/pointer type."""
        return (
            flow_type.name.startswith("array<")
            or flow_type.name.startswith("array_")
            or flow_type.name.startswith("ptr<")
            or (
                hasattr(flow_type, "element_type")
                and flow_type.element_type is not None
            )
        )

    def generate_kernel(self, func: FunctionDecl) -> str:
        """Generate a Metal compute kernel from a @gpu function."""
        self.kernel_name = func.name
        self.buffer_bindings.clear()
        self.binding_counter = 0

        lines = []

        # Include Metal headers
        lines.append("#include <metal_stdlib>")
        lines.append("using namespace metal;")
        lines.append("")

        # Generate kernel signature
        params = []

        # Convert FLOW parameters to Metal buffer bindings
        for param in func.parameters:
            metal_type = self.map_type(param.type)

            # Array/pointer parameters become buffer bindings
            if self.is_array_type(param.type):
                binding = self.binding_counter
                self.buffer_bindings[param.name] = binding
                self.binding_counter += 1
                params.append(f"{metal_type} {param.name} [[buffer({binding})]]")
            else:
                # Scalar parameters also get buffer bindings
                binding = self.binding_counter
                self.buffer_bindings[param.name] = binding
                self.binding_counter += 1
                params.append(
                    f"constant {metal_type}& {param.name} [[buffer({binding})]]"
                )

        # Add thread position parameter
        params.append("uint tid [[thread_position_in_grid]]")

        lines.append(f"kernel void {func.name}(")
        lines.append("    " + ",\n    ".join(params))
        lines.append(") {")

        self.indent_level = 1

        # Generate function body
        body_lines = self.generate_block(func.body)
        lines.extend(body_lines)

        self.indent_level = 0
        lines.append("}")

        return "\n".join(lines)

    def generate_block(self, block: Block) -> List[str]:
        """Generate Metal code for a block of statements."""
        lines = []
        for stmt in block.statements:
            stmt_lines = self.generate_statement(stmt)
            lines.extend(stmt_lines)
        return lines

    def generate_statement(self, stmt: Statement) -> List[str]:
        """Generate Metal code for a statement."""
        if isinstance(stmt, VarDecl):
            return self.generate_var_decl(stmt)
        elif isinstance(stmt, Assignment):
            return self.generate_assignment(stmt)
        elif isinstance(stmt, IfStatement):
            return self.generate_if(stmt)
        elif isinstance(stmt, WhileStatement):
            return self.generate_while(stmt)
        elif isinstance(stmt, ForStatement):
            return self.generate_for(stmt)
        elif isinstance(stmt, ReturnStatement):
            return self.generate_return(stmt)
        elif isinstance(stmt, Expression):
            expr = self.generate_expression(stmt)
            return [f"{self.indent()}{expr};"]
        else:
            return [f"{self.indent()}// Unsupported: {type(stmt).__name__}"]

    def generate_var_decl(self, decl: VarDecl) -> List[str]:
        """Generate variable declaration."""
        metal_type = self.map_type(decl.type)
        if decl.initializer:
            init = self.generate_expression(decl.initializer)
            # Use auto for simple expressions to avoid type mismatches
            if metal_type in ["int", "uint", "float", "double", "bool"]:
                return [f"{self.indent()}{metal_type} {decl.name} = {init};"]
            else:
                return [f"{self.indent()}auto {decl.name} = {init};"]
        else:
            return [f"{self.indent()}{metal_type} {decl.name};"]

    def generate_assignment(self, assign: Assignment) -> List[str]:
        """Generate assignment statement."""
        # Handle array access assignment (target_expr) vs simple variable (target)
        if assign.target_expr:
            target = self.generate_expression(assign.target_expr)
        else:
            target = (
                assign.target
                if isinstance(assign.target, str)
                else self.generate_expression(assign.target)
            )
        value = self.generate_expression(assign.value)
        return [f"{self.indent()}{target} = {value};"]

    def generate_if(self, stmt: IfStatement) -> List[str]:
        """Generate if statement."""
        lines = []
        cond = self.generate_expression(stmt.condition)
        lines.append(f"{self.indent()}if ({cond}) {{")

        self.indent_level += 1
        lines.extend(self.generate_block(stmt.then_block))
        self.indent_level -= 1

        if stmt.else_block:
            lines.append(f"{self.indent()}}} else {{")
            self.indent_level += 1
            lines.extend(self.generate_block(stmt.else_block))
            self.indent_level -= 1

        lines.append(f"{self.indent()}}}")
        return lines

    def generate_while(self, stmt: WhileStatement) -> List[str]:
        """Generate while loop."""
        lines = []
        cond = self.generate_expression(stmt.condition)
        lines.append(f"{self.indent()}while ({cond}) {{")

        self.indent_level += 1
        lines.extend(self.generate_block(stmt.body))
        self.indent_level -= 1

        lines.append(f"{self.indent()}}}")
        return lines

    def generate_for(self, stmt: ForStatement) -> List[str]:
        """Generate for loop."""
        lines = []
        var = stmt.variable
        start = self.generate_expression(stmt.start)
        end = self.generate_expression(stmt.end)

        lines.append(
            f"{self.indent()}for (int {var} = {start}; {var} < {end}; {var}++) {{"
        )

        self.indent_level += 1
        lines.extend(self.generate_block(stmt.body))
        self.indent_level -= 1

        lines.append(f"{self.indent()}}}")
        return lines

    def generate_return(self, stmt: ReturnStatement) -> List[str]:
        """Generate return statement."""
        if stmt.value:
            val = self.generate_expression(stmt.value)
            return [f"{self.indent()}return {val};"]
        return [f"{self.indent()}return;"]

    def generate_expression(self, expr: Expression) -> str:
        """Generate Metal expression."""
        if isinstance(expr, Literal):
            if expr.type == "float":
                return f"{expr.value}f"
            return str(expr.value)

        elif isinstance(expr, Variable):
            name = expr.name
            # Map GPU built-ins
            if name in self.GPU_BUILTINS:
                builtin = self.GPU_BUILTINS[name]
                # gpu_thread_id() -> tid (our parameter)
                if name == "gpu_thread_id":
                    return "tid"
                return builtin
            return name

        elif isinstance(expr, BinaryOperation):
            left = self.generate_expression(expr.left)
            right = self.generate_expression(expr.right)
            op = expr.operator
            # Map operators
            op_map = {
                "&&": "&&",
                "||": "||",
                "==": "==",
                "!=": "!=",
                "<=": "<=",
                ">=": ">=",
                "<": "<",
                ">": ">",
                "+": "+",
                "-": "-",
                "*": "*",
                "/": "/",
                "%": "%",
            }
            return f"({left} {op_map.get(op, op)} {right})"

        elif isinstance(expr, UnaryOperation):
            operand = self.generate_expression(expr.operand)
            return f"({expr.operator}{operand})"

        elif isinstance(expr, FunctionCall):
            name = expr.name

            # Handle GPU built-in functions
            if name == "gpu_thread_id":
                return "tid"
            if name == "gpu_barrier" or name == "gpu_sync":
                return "threadgroup_barrier(mem_flags::mem_threadgroup)"

            # Math functions
            math_funcs = [
                "sin",
                "cos",
                "tan",
                "sqrt",
                "exp",
                "log",
                "abs",
                "min",
                "max",
                "pow",
            ]
            if name in math_funcs:
                args = ", ".join(self.generate_expression(a) for a in expr.arguments)
                return f"{name}({args})"

            args = ", ".join(self.generate_expression(a) for a in expr.arguments)
            return f"{name}({args})"

        elif isinstance(expr, ArrayAccess):
            array = self.generate_expression(expr.array)
            index = self.generate_expression(expr.index)
            return f"{array}[{index}]"

        elif isinstance(expr, FieldAccess):
            obj = self.generate_expression(expr.object)
            return f"{obj}.{expr.field}"

        else:
            return f"/* Unsupported: {type(expr).__name__} */"

    def generate_host_code(self, func: FunctionDecl, shader_path: str) -> str:
        """Generate C/Objective-C host code to load and execute the Metal kernel."""
        params = func.parameters

        code = []
        code.append("// Auto-generated Metal host code")
        code.append("#import <Metal/Metal.h>")
        code.append("#import <Foundation/Foundation.h>")
        code.append("")
        code.append(f"void run_{func.name}(")

        # Parameters for the host function
        host_params = []
        for param in params:
            if param.type.name.startswith("array<") or param.type.name.startswith(
                "ptr<"
            ):
                inner = (
                    param.type.name[6:-1]
                    if param.type.name.startswith("array<")
                    else param.type.name[4:-1]
                )
                c_type = {
                    "f32": "float",
                    "f64": "double",
                    "i32": "int",
                    "u32": "unsigned int",
                }.get(inner, "float")
                host_params.append(f"{c_type}* {param.name}")
            else:
                c_type = {
                    "f32": "float",
                    "f64": "double",
                    "i32": "int",
                    "u32": "unsigned int",
                    "bool": "bool",
                }.get(param.type.name, "int")
                host_params.append(f"{c_type} {param.name}")

        host_params.append("size_t count")
        code.append("    " + ", ".join(host_params))
        code.append(") {")
        code.append("    @autoreleasepool {")
        code.append("        // Get default Metal device")
        code.append("        id<MTLDevice> device = MTLCreateSystemDefaultDevice();")
        code.append("        if (!device) {")
        code.append('            NSLog(@"Metal is not supported on this device");')
        code.append("            return;")
        code.append("        }")
        code.append("")
        code.append("        // Load shader library")
        code.append(f'        NSString* shaderPath = @"{shader_path}";')
        code.append("        NSError* error = nil;")
        code.append(
            "        NSString* shaderSource = [NSString stringWithContentsOfFile:shaderPath encoding:NSUTF8StringEncoding error:&error];"
        )
        code.append(
            "        id<MTLLibrary> library = [device newLibraryWithSource:shaderSource options:nil error:&error];"
        )
        code.append("        if (!library) {")
        code.append('            NSLog(@"Failed to compile shader: %@", error);')
        code.append("            return;")
        code.append("        }")
        code.append("")
        code.append(
            f'        id<MTLFunction> kernel = [library newFunctionWithName:@"{func.name}"];'
        )
        code.append(
            "        id<MTLComputePipelineState> pipeline = [device newComputePipelineStateWithFunction:kernel error:&error];"
        )
        code.append("")
        code.append("        // Create command queue")
        code.append("        id<MTLCommandQueue> queue = [device newCommandQueue];")
        code.append(
            "        id<MTLCommandBuffer> commandBuffer = [queue commandBuffer];"
        )
        code.append(
            "        id<MTLComputeCommandEncoder> encoder = [commandBuffer computeCommandEncoder];"
        )
        code.append("        [encoder setComputePipelineState:pipeline];")
        code.append("")

        # Set up buffer bindings
        for i, param in enumerate(params):
            if param.type.name.startswith("array<") or param.type.name.startswith(
                "ptr<"
            ):
                inner = (
                    param.type.name[6:-1]
                    if param.type.name.startswith("array<")
                    else param.type.name[4:-1]
                )
                c_type = {
                    "f32": "float",
                    "f64": "double",
                    "i32": "int",
                    "u32": "unsigned int",
                }.get(inner, "float")
                code.append(
                    f"        id<MTLBuffer> buffer{i} = [device newBufferWithBytes:{param.name} length:count * sizeof({c_type}) options:MTLResourceStorageModeShared];"
                )
                code.append(
                    f"        [encoder setBuffer:buffer{i} offset:0 atIndex:{i}];"
                )
            else:
                code.append(
                    f"        [encoder setBytes:&{param.name} length:sizeof({param.name}) atIndex:{i}];"
                )

        code.append("")
        code.append("        // Dispatch threads")
        code.append("        MTLSize gridSize = MTLSizeMake(count, 1, 1);")
        code.append(
            "        NSUInteger threadGroupSize = MIN(pipeline.maxTotalThreadsPerThreadgroup, count);"
        )
        code.append(
            "        MTLSize threadgroupSize = MTLSizeMake(threadGroupSize, 1, 1);"
        )
        code.append(
            "        [encoder dispatchThreads:gridSize threadsPerThreadgroup:threadgroupSize];"
        )
        code.append("")
        code.append("        [encoder endEncoding];")
        code.append("        [commandBuffer commit];")
        code.append("        [commandBuffer waitUntilCompleted];")
        code.append("")

        # Copy results back for output buffers
        for i, param in enumerate(params):
            if "out" in param.name.lower() or "result" in param.name.lower():
                inner = (
                    param.type.name[6:-1]
                    if param.type.name.startswith("array<")
                    else param.type.name[4:-1]
                )
                c_type = {
                    "f32": "float",
                    "f64": "double",
                    "i32": "int",
                    "u32": "unsigned int",
                }.get(inner, "float")
                code.append(
                    f"        memcpy({param.name}, buffer{i}.contents, count * sizeof({c_type}));"
                )

        code.append("    }")
        code.append("}")

        return "\n".join(code)


def extract_gpu_functions(declarations: List[Any]) -> List[FunctionDecl]:
    """Extract all @gpu annotated functions from declarations."""
    gpu_funcs = []
    for decl in declarations:
        if isinstance(decl, FunctionDecl):
            if "gpu" in decl.attributes:
                gpu_funcs.append(decl)
    return gpu_funcs


def generate_metal_shaders(
    declarations: List[Any], output_dir: str = "build/gpu"
) -> List[Tuple[str, str]]:
    """Generate Metal shaders for all @gpu functions.

    Returns list of (kernel_name, shader_path) tuples.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    gpu_funcs = extract_gpu_functions(declarations)
    codegen = MetalCodegen()

    results = []
    for func in gpu_funcs:
        # Generate Metal shader
        shader_code = codegen.generate_kernel(func)
        shader_file = output_path / f"{func.name}.metal"
        shader_file.write_text(shader_code)

        # Generate host code
        host_code = codegen.generate_host_code(func, str(shader_file))
        host_file = output_path / f"{func.name}_host.m"
        host_file.write_text(host_code)

        results.append((func.name, str(shader_file)))
        print(f"✅ Generated Metal shader: {shader_file}")

    return results
