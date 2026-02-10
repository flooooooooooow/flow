"""
Flow to JavaScript Generator
Transpiles Flow AST to JavaScript for browser execution
"""

from typing import List, Dict, Any, Optional
from flow.parser import (
    FunctionDecl, StructDecl, ConstDecl,
    VarDecl, Assignment, ReturnStatement, IfStatement, WhileStatement, ForStatement,
    BinaryOperation, UnaryOperation, FunctionCall, ArrayAccess, FieldAccess,
    Literal, Variable, ArrayLiteral, StructLiteral, CastExpression,
    MatchStatement, Type, Block
)


class JSGenerator:
    """Generates JavaScript from Flow AST"""
    
    def __init__(self):
        self.output: List[str] = []
        self.indent_level = 0
        self.functions: Dict[str, FunctionDecl] = {}
        self.structs: Dict[str, StructDecl] = {}
        self.externs: set = set()
        self.output_buffer: List[str] = []  # For capturing print output
    
    def indent(self) -> str:
        return "    " * self.indent_level
    
    def emit(self, line: str):
        self.output.append(self.indent() + line)
    
    def emit_raw(self, line: str):
        self.output.append(line)
    
    def generate(self, declarations: List) -> str:
        """Generate JavaScript from declarations"""
        self.output = []
        
        # Emit header
        self.emit_raw("// Generated JavaScript from Flow")
        self.emit_raw("// Run with: eval(code) or in browser")
        self.emit_raw("")
        
        # Runtime support
        self.emit_raw("const __flow_runtime = {")
        self.emit_raw("    output: [],")
        self.emit_raw("    print: function(s) { this.output.push(String(s)); },")
        self.emit_raw("    println: function(s) { this.output.push(String(s) + '\\n'); },")
        self.emit_raw("    printf: function(fmt, ...args) {")
        self.emit_raw("        let i = 0;")
        self.emit_raw("        const result = fmt.replace(/%([dfsi])/g, (m, t) => {")
        self.emit_raw("            const v = args[i++];")
        self.emit_raw("            if (t === 'f') return v.toFixed(6);")
        self.emit_raw("            if (t === 'd' || t === 'i') return Math.floor(v);")
        self.emit_raw("            return v;")
        self.emit_raw("        });")
        self.emit_raw("        this.output.push(result);")
        self.emit_raw("    },")
        self.emit_raw("    getOutput: function() { return this.output.join(''); },")
        self.emit_raw("    clearOutput: function() { this.output = []; }")
        self.emit_raw("};")
        self.emit_raw("")
        
        # Math functions
        self.emit_raw("const sqrt = Math.sqrt;")
        self.emit_raw("const sin = Math.sin;")
        self.emit_raw("const cos = Math.cos;")
        self.emit_raw("const exp = Math.exp;")
        self.emit_raw("const log = Math.log;")
        self.emit_raw("const abs = Math.abs;")
        self.emit_raw("const floor = Math.floor;")
        self.emit_raw("const ceil = Math.ceil;")
        self.emit_raw("const pow = Math.pow;")
        self.emit_raw("const clock = () => performance.now() * 1000;")
        self.emit_raw("")
        
        # First pass: collect structs and function signatures
        for decl in declarations:
            if isinstance(decl, StructDecl):
                self.structs[decl.name] = decl
            elif isinstance(decl, FunctionDecl):
                self.functions[decl.name] = decl
            elif isinstance(decl, ExternBlock):
                for fn in decl.functions:
                    self.externs.add(fn.name)
        
        # Generate struct constructors
        for name, struct in self.structs.items():
            self._gen_struct(struct)
        
        # Generate constants
        for decl in declarations:
            if isinstance(decl, ConstDecl):
                self._gen_const(decl)
        
        # Generate functions
        for decl in declarations:
            if isinstance(decl, FunctionDecl):
                self._gen_function(decl)
        
        # Entry point wrapper
        self.emit_raw("")
        self.emit_raw("// Entry point")
        self.emit_raw("function __flow_run() {")
        self.emit_raw("    __flow_runtime.clearOutput();")
        self.emit_raw("    try {")
        self.emit_raw("        const result = typeof main === 'function' ? main() : 0;")
        self.emit_raw("        return { success: true, output: __flow_runtime.getOutput(), result: result };")
        self.emit_raw("    } catch (e) {")
        self.emit_raw("        return { success: false, output: __flow_runtime.getOutput(), error: e.toString() };")
        self.emit_raw("    }")
        self.emit_raw("}")
        
        return "\n".join(self.output)
    
    def _gen_struct(self, struct: StructDecl):
        """Generate struct as JS class"""
        name = struct.name.split('<')[0]  # Strip generic params
        fields = [f.name for f in struct.fields]
        
        self.emit(f"class {name} {{")
        self.indent_level += 1
        
        # Constructor
        self.emit(f"constructor({', '.join(fields)}) {{")
        self.indent_level += 1
        for field in fields:
            self.emit(f"this.{field} = {field};")
        self.indent_level -= 1
        self.emit("}")
        
        self.indent_level -= 1
        self.emit("}")
        self.emit("")
    
    def _gen_const(self, const: ConstDecl):
        """Generate constant"""
        value = self._gen_expr(const.value)
        self.emit(f"const {const.name} = {value};")
    
    def _gen_function(self, func: FunctionDecl):
        """Generate function"""
        # Skip extern functions
        if func.name in self.externs:
            return
        if getattr(func, 'is_forward_decl', False):
            return
        
        # Mangle name if generic
        name = func.name
        if hasattr(func, 'mangled_name') and func.mangled_name:
            name = func.mangled_name
        
        # Handle print/println as special
        if name in ('print', 'println', 'printf'):
            return
        
        # Parameter list
        params = [p.name for p in func.parameters]
        
        self.emit(f"function {name}({', '.join(params)}) {{")
        self.indent_level += 1
        
        # Generate body
        if func.body:
            for stmt in func.body.statements:
                self._gen_stmt(stmt)
        
        self.indent_level -= 1
        self.emit("}")
        self.emit("")
    
    def _gen_stmt(self, stmt):
        """Generate statement"""
        if isinstance(stmt, VarDecl):
            value = self._gen_expr(stmt.initializer) if stmt.initializer else "undefined"
            keyword = "let" if getattr(stmt, 'is_mutable', False) else "const"
            self.emit(f"{keyword} {stmt.name} = {value};")
        
        elif isinstance(stmt, Assignment):
            target = self._gen_expr(stmt.target)
            value = self._gen_expr(stmt.value)
            self.emit(f"{target} = {value};")
        
        elif isinstance(stmt, ReturnStatement):
            if stmt.value:
                value = self._gen_expr(stmt.value)
                self.emit(f"return {value};")
            else:
                self.emit("return;")
        
        elif isinstance(stmt, IfStatement):
            cond = self._gen_expr(stmt.condition)
            self.emit(f"if ({cond}) {{")
            self.indent_level += 1
            if isinstance(stmt.then_block, Block):
                for s in stmt.then_block.statements:
                    self._gen_stmt(s)
            self.indent_level -= 1
            
            if stmt.else_block:
                self.emit("} else {")
                self.indent_level += 1
                if isinstance(stmt.else_block, Block):
                    for s in stmt.else_block.statements:
                        self._gen_stmt(s)
                self.indent_level -= 1
            self.emit("}")
        
        elif isinstance(stmt, WhileStatement):
            cond = self._gen_expr(stmt.condition)
            self.emit(f"while ({cond}) {{")
            self.indent_level += 1
            if isinstance(stmt.body, Block):
                for s in stmt.body.statements:
                    self._gen_stmt(s)
            self.indent_level -= 1
            self.emit("}")
        
        elif isinstance(stmt, ForStatement):
            var = stmt.variable
            start = self._gen_expr(stmt.range_start) if stmt.range_start else "0"
            end = self._gen_expr(stmt.range_end)
            self.emit(f"for (let {var} = {start}; {var} < {end}; {var}++) {{")
            self.indent_level += 1
            if isinstance(stmt.body, Block):
                for s in stmt.body.statements:
                    self._gen_stmt(s)
            self.indent_level -= 1
            self.emit("}")
        
        elif isinstance(stmt, FunctionCall):
            # Statement-level call (like print)
            call = self._gen_expr(stmt)
            self.emit(f"{call};")
        
        elif isinstance(stmt, MatchStatement):
            self._gen_match(stmt)
        
        else:
            # Try to generate as expression statement
            try:
                expr = self._gen_expr(stmt)
                self.emit(f"{expr};")
            except:
                self.emit(f"// Unknown statement: {type(stmt).__name__}")
    
    def _gen_match(self, match: MatchStatement):
        """Generate match statement as switch/if-else"""
        value = self._gen_expr(match.value)
        
        first = True
        for case in match.cases:
            pattern = case.pattern
            if hasattr(pattern, 'value'):
                # Literal pattern
                pat_val = self._gen_expr(pattern)
                if first:
                    self.emit(f"if ({value} === {pat_val}) {{")
                    first = False
                else:
                    self.emit(f"}} else if ({value} === {pat_val}) {{")
            elif hasattr(pattern, 'name') and pattern.name == '_':
                # Wildcard
                self.emit("} else {")
            else:
                if first:
                    self.emit("if (true) {")
                    first = False
                else:
                    self.emit("} else {")
            
            self.indent_level += 1
            if isinstance(case.body, Block):
                for s in case.body.statements:
                    self._gen_stmt(s)
            self.indent_level -= 1
        
        self.emit("}")
    
    def _gen_expr(self, expr) -> str:
        """Generate expression"""
        if isinstance(expr, Literal):
            val = expr.value
            lit_type = expr.type if hasattr(expr, 'type') else None
            type_name = lit_type.name if lit_type and hasattr(lit_type, 'name') else ''
            
            # Check the type to determine output format
            if type_name in ('string', 'str'):
                # String literal - parser stores value WITH quotes, strip them
                s = str(val)
                if s.startswith('"') and s.endswith('"'):
                    s = s[1:-1]  # Remove surrounding quotes
                elif s.startswith("'") and s.endswith("'"):
                    s = s[1:-1]
                # Escape for JS
                escaped = s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                return f'"{escaped}"'
            elif type_name in ('i32', 'i64', 'i8', 'i16', 'u32', 'u64', 'u8', 'u16', 'f32', 'f64', 'int', 'float'):
                # Numeric - return as-is
                return str(val)
            elif type_name == 'bool':
                return "true" if val in ('true', True, '1') else "false"
            elif val == 'true':
                return 'true'
            elif val == 'false':
                return 'false'
            elif val == 'null' or val is None:
                return 'null'
            else:
                # Default: if it looks numeric, return as number
                try:
                    float(val)
                    return str(val)
                except (ValueError, TypeError):
                    # It's a string - strip quotes if present
                    s = str(val)
                    if s.startswith('"') and s.endswith('"'):
                        s = s[1:-1]
                    escaped = s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                    return f'"{escaped}"'
        
        elif isinstance(expr, Variable):
            return expr.name
        
        elif isinstance(expr, BinaryOperation):
            left = self._gen_expr(expr.left)
            right = self._gen_expr(expr.right)
            op = expr.operator
            
            # Handle Flow operators
            if op == 'and':
                op = '&&'
            elif op == 'or':
                op = '||'
            elif op == '%':
                return f"{left} % {right}"
            
            return f"({left} {op} {right})"
        
        elif isinstance(expr, UnaryOperation):
            operand = self._gen_expr(expr.operand)
            op = expr.operator
            if op == 'not':
                op = '!'
            return f"({op}{operand})"

        elif isinstance(expr, CastExpression):
            # JS is dynamically typed; casts are no-ops in runtime codegen.
            return f"({self._gen_expr(expr.expr)})"
        
        elif isinstance(expr, FunctionCall):
            func_name = expr.name if isinstance(expr.name, str) else self._gen_expr(expr.name)
            args = [self._gen_expr(a) for a in expr.arguments]
            
            # Handle special functions
            if func_name == 'print':
                args_str = ', '.join(args) if args else '""'
                return f"__flow_runtime.print({args_str})"
            elif func_name == 'println':
                args_str = ', '.join(args) if args else '""'
                return f"__flow_runtime.println({args_str})"
            elif func_name == 'printf':
                args_str = ', '.join(args)
                return f"__flow_runtime.printf({args_str})"
            
            return f"{func_name}({', '.join(args)})"
        
        elif isinstance(expr, ArrayAccess):
            base = self._gen_expr(expr.array)
            index = self._gen_expr(expr.index)
            return f"{base}[{index}]"
        
        elif isinstance(expr, FieldAccess):
            base = self._gen_expr(expr.object)
            return f"{base}.{expr.field}"
        
        elif isinstance(expr, ArrayLiteral):
            elements = [self._gen_expr(e) for e in expr.elements]
            return f"[{', '.join(elements)}]"
        
        elif isinstance(expr, StructLiteral):
            name = expr.struct_name.split('<')[0] if hasattr(expr, 'struct_name') else str(expr.name).split('<')[0]
            field_values = []
            for f in expr.fields:
                if hasattr(f, 'value'):
                    field_values.append(self._gen_expr(f.value))
                else:
                    field_values.append(self._gen_expr(f))
            return f"new {name}({', '.join(field_values)})"
        
        else:
            return f"/* unknown: {type(expr).__name__} */"


def flow_to_js(declarations: List) -> str:
    """Convert Flow AST to JavaScript"""
    gen = JSGenerator()
    return gen.generate(declarations)
