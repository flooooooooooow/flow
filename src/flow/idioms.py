"""
Semantic Idiom Advisor and Performance Remark Engine for Flow

Exposes a shared engine for finding code that is valid but could be
written in a clearer, safer, more Flow-native way, as well as emitting
compiler performance remarks explaining missed optimizations in idiomatic Flow.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from .parser import (
    Block, VarDecl, Assignment, ReturnStatement, StructLiteral, ArrayLiteral, IfStatement, MatchStatement,
    Expression, FunctionDecl, FieldAccess, Variable, ForStatement, WhileStatement,
    BreakStatement, ContinueStatement, FunctionCall, MethodCall, EffectCall, HandleStatement, ArrayAccess
)


@dataclass
class IdiomFinding:
    rule_id: str
    severity: str # "hint", "warning"
    line: int
    column: int
    title: str
    rationale: str
    applicability: str # "machine-applicable", "maybe-incorrect", "advisory"
    replacement: Optional[str] = None
    span_len: int = 0
    
    def to_dict(self):
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "line": self.line,
            "column": self.column,
            "title": self.title,
            "rationale": self.rationale,
            "applicability": self.applicability,
            "replacement": self.replacement,
            "span_len": self.span_len
        }


class IdiomAdvisor:
    def __init__(self):
        self.findings: List[IdiomFinding] = []
        
    def analyze_function(self, func: FunctionDecl):
        """Analyze a single function for idioms and performance remarks."""
        if func.body:
            self._check_fidiom001(func.body)
            self._check_fidiom002(func.body)
            self._check_fperf001(func.body)
            self._check_fperf002(func.body)
            self._check_fperf003(func.body)
            self._check_fperf004(func.body)

    def analyze_program(self, declarations: List[Any]):
        """Analyze all function declarations in a program."""
        for decl in declarations:
            if isinstance(decl, FunctionDecl):
                self.analyze_function(decl)
            
    def _check_fidiom001(self, block: Block):
        """
        FIDIOM001: immutable binding declared `mut` but never mutated.
        """
        mut_decls = {} # map name -> VarDecl
        mutations = set()
        
        def visit(node: Any):
            if isinstance(node, VarDecl):
                if node.is_mutable:
                    mut_decls[node.name] = node
            elif isinstance(node, Assignment):
                if node.target_expr is None:
                    mutations.add(node.target)
            elif isinstance(node, IfStatement):
                visit(node.then_block)
                if node.else_block:
                    visit(node.else_block)
                if hasattr(node, 'else_if') and node.else_if:
                    visit(node.else_if)
            elif isinstance(node, MatchStatement):
                branches = getattr(node, 'cases', getattr(node, 'branches', []))
                for branch in branches:
                    visit(branch.body)
            elif isinstance(node, FunctionDecl):
                if node.body:
                    visit(node.body)
            elif hasattr(node, 'body') and isinstance(node.body, Block):
                visit(node.body)
            elif hasattr(node, 'statements') and isinstance(node.statements, list):
                for stmt in node.statements:
                    visit(stmt)
            
        visit(block)
        
        for name, decl in mut_decls.items():
            if name not in mutations:
                line = 1
                col = 1
                if hasattr(decl, 'location') and decl.location:
                    line = getattr(decl.location, 'line', 1)
                    col = getattr(decl.location, 'column', 1)
                finding = IdiomFinding(
                    rule_id="FIDIOM001",
                    severity="hint",
                    line=line,
                    column=col,
                    title="Unnecessary 'mut' declaration",
                    rationale=f"Variable '{name}' is declared 'mut' but is never reassigned. Remove 'mut' to make it immutable.",
                    applicability="machine-applicable",
                    replacement=f"let {name}", # naive replacement, might need refinement
                    span_len=7 # "let mut"
                )
                self.findings.append(finding)

    def _check_fidiom002(self, block: Block):
        """
        FIDIOM002: redundant temporary/return shapes.
        (e.g., returning a struct literal that's identical to the expected return type, when a simple variable can be used)
        """
        def visit(node: Any):
            if isinstance(node, ReturnStatement):
                if node.value and isinstance(node.value, StructLiteral):
                    struct_lit = node.value
                    if struct_lit.fields:
                        base_var_name = None
                        all_match = True
                        for field_name, field_val in struct_lit.fields:
                            if isinstance(field_val, FieldAccess) and isinstance(field_val.object, Variable):
                                if field_val.field != field_name:
                                    all_match = False
                                    break
                                if base_var_name is None:
                                    base_var_name = field_val.object.name
                                elif base_var_name != field_val.object.name:
                                    all_match = False
                                    break
                            else:
                                all_match = False
                                break
                        if all_match and base_var_name is not None:
                            line = 1
                            col = 1
                            if hasattr(node, 'location') and node.location:
                                line = getattr(node.location, 'line', 1)
                                col = getattr(node.location, 'column', 1)
                            finding = IdiomFinding(
                                rule_id="FIDIOM002",
                                severity="hint",
                                line=line,
                                column=col,
                                title="Redundant return shape",
                                rationale=f"Returning a struct literal identical to `{base_var_name}`. Return `{base_var_name}` directly.",
                                applicability="machine-applicable",
                                replacement=f"return {base_var_name};",
                                span_len=6 # "return"
                            )
                            self.findings.append(finding)
                            
            elif isinstance(node, Block):
                for stmt in node.statements:
                    visit(stmt)
            elif isinstance(node, IfStatement):
                visit(node.then_block)
                if node.else_block:
                    visit(node.else_block)
                if hasattr(node, 'else_if') and node.else_if:
                    visit(node.else_if)
            elif isinstance(node, MatchStatement):
                branches = getattr(node, 'cases', getattr(node, 'branches', []))
                for branch in branches:
                    visit(branch.body)
            elif isinstance(node, FunctionDecl):
                if node.body:
                    visit(node.body)
            elif hasattr(node, 'body') and isinstance(node.body, Block):
                visit(node.body)
            elif hasattr(node, 'statements') and isinstance(node.statements, list):
                for stmt in node.statements:
                    visit(stmt)
        
        visit(block)

    def _check_fperf001(self, block: Block):
        """
        FPERF001: missed loop vectorization.
        Emits a performance remark when a `for` loop cannot be auto-vectorized
        because of control flow, non-math function calls, or missing explicit step.
        """
        math_functions = {'sin', 'cos', 'tan', 'sqrt', 'fabs', 'abs', 'log', 'exp', 'pow', 'tanh'}

        def _get_location(node: Any) -> tuple[int, int]:
            if hasattr(node, 'location') and node.location:
                return getattr(node.location, 'line', 1), getattr(node.location, 'column', 1)
            return 1, 1

        def _analyze_loop(st: ForStatement):
            reasons = []
            if st.step is None:
                reasons.append("missing explicit step 1")

            has_control_flow = False
            has_calls = False
            has_nested_loops = False

            def check_body(node: Any):
                nonlocal has_control_flow, has_calls, has_nested_loops
                if isinstance(node, (IfStatement, MatchStatement, BreakStatement, ContinueStatement, ReturnStatement)):
                    has_control_flow = True
                elif isinstance(node, (WhileStatement, ForStatement)) and node is not st:
                    has_nested_loops = True
                elif isinstance(node, FunctionCall):
                    if node.name not in math_functions:
                        has_calls = True
                elif isinstance(node, MethodCall):
                    has_calls = True

                if hasattr(node, 'body') and isinstance(node.body, Block):
                    for stmt in node.body.statements:
                        check_body(stmt)
                elif hasattr(node, 'then_block') and isinstance(node.then_block, Block):
                    for stmt in node.then_block.statements:
                        check_body(stmt)
                    if hasattr(node, 'else_block') and isinstance(node.else_block, Block):
                        for stmt in node.else_block.statements:
                            check_body(stmt)
                elif hasattr(node, 'statements') and isinstance(node.statements, list):
                    for stmt in node.statements:
                        check_body(stmt)

            if st.body:
                for stmt in st.body.statements:
                    check_body(stmt)

            if has_control_flow:
                reasons.append("contains control flow (if/match/break)")
            if has_calls:
                reasons.append("contains non-math function calls")
            if has_nested_loops:
                reasons.append("contains nested loops")

            if reasons:
                line, col = _get_location(st)
                reason_str = ", ".join(reasons)
                finding = IdiomFinding(
                    rule_id="FPERF001",
                    severity="hint",
                    line=line,
                    column=col,
                    title="Missed loop vectorization",
                    rationale=(
                        f"Loop cannot be auto-vectorized because it {reason_str}. "
                        "Use straight-line scalar arithmetic and explicit 'step 1' to enable SIMD vectorization."
                    ),
                    applicability="advisory",
                    span_len=3, # "for"
                )
                self.findings.append(finding)

        def visit(node: Any):
            if isinstance(node, ForStatement):
                _analyze_loop(node)
                if node.body:
                    visit(node.body)
            elif isinstance(node, Block):
                for stmt in node.statements:
                    visit(stmt)
            elif isinstance(node, IfStatement):
                if node.then_block:
                    visit(node.then_block)
                if node.else_block:
                    visit(node.else_block)
            elif isinstance(node, MatchStatement):
                branches = getattr(node, 'cases', getattr(node, 'branches', []))
                for branch in branches:
                    visit(branch.body)

        visit(block)

    def _check_fperf002(self, block: Block):
        """
        FPERF002: dynamic effect dispatch overhead.
        Emits a performance remark when an effect call is invoked outside a `handle` block.
        """
        def _get_location(node: Any) -> tuple[int, int]:
            if hasattr(node, 'location') and node.location:
                return getattr(node.location, 'line', 1), getattr(node.location, 'column', 1)
            return 1, 1

        def visit(node: Any, inside_handle: bool = False):
            if isinstance(node, HandleStatement):
                if hasattr(node, 'body') and node.body:
                    visit(node.body, inside_handle=True)
            elif isinstance(node, EffectCall) and not inside_handle:
                line, col = _get_location(node)
                op_name = getattr(node, 'operation', 'op')
                finding = IdiomFinding(
                    rule_id="FPERF002",
                    severity="hint",
                    line=line,
                    column=col,
                    title="Dynamic effect dispatch overhead",
                    rationale=(
                        f"Effect operation '{op_name}' is invoked outside a 'handle' block, "
                        "incurring dynamic vtable lookup at runtime. Enclose in a 'handle' block "
                        "to enable zero-cost direct call resolution."
                    ),
                    applicability="advisory",
                    span_len=len(op_name),
                )
                self.findings.append(finding)
            elif isinstance(node, Block):
                for stmt in node.statements:
                    visit(stmt, inside_handle)
            elif isinstance(node, VarDecl) and node.initializer:
                visit(node.initializer, inside_handle)
            elif isinstance(node, Assignment):
                if node.value:
                    visit(node.value, inside_handle)
                if node.target_expr:
                    visit(node.target_expr, inside_handle)
            elif isinstance(node, IfStatement):
                if node.then_block:
                    visit(node.then_block, inside_handle)
                if node.else_block:
                    visit(node.else_block, inside_handle)
            elif isinstance(node, ForStatement):
                if node.body:
                    visit(node.body, inside_handle)
            elif isinstance(node, WhileStatement):
                if node.body:
                    visit(node.body, inside_handle)

        visit(block)

    def _check_fperf003(self, block: Block):
        """
        FPERF003: allocation/struct creation inside loop.
        Emits a performance remark when a struct or array literal is created inside a loop.
        """
        def _get_location(node: Any) -> tuple[int, int]:
            if hasattr(node, 'location') and node.location:
                return getattr(node.location, 'line', 1), getattr(node.location, 'column', 1)
            return 1, 1

        def visit_loop_body(node: Any):
            if isinstance(node, (StructLiteral, ArrayLiteral)):
                line, col = _get_location(node)
                kind = "Struct" if isinstance(node, StructLiteral) else "Array"
                finding = IdiomFinding(
                    rule_id="FPERF003",
                    severity="hint",
                    line=line,
                    column=col,
                    title="Allocation inside loop",
                    rationale=(
                        f"{kind} literal is repeatedly constructed inside loop body. "
                        "Consider hoisting allocation or reusing a mutable buffer outside the loop."
                    ),
                    applicability="advisory",
                )
                self.findings.append(finding)

            if isinstance(node, Block):
                for stmt in node.statements:
                    visit_loop_body(stmt)
            elif isinstance(node, VarDecl) and node.initializer:
                visit_loop_body(node.initializer)
            elif isinstance(node, Assignment):
                if node.value:
                    visit_loop_body(node.value)
                if node.target_expr:
                    visit_loop_body(node.target_expr)
            elif isinstance(node, IfStatement):
                if node.then_block:
                    visit_loop_body(node.then_block)
                if node.else_block:
                    visit_loop_body(node.else_block)

        def visit(node: Any):
            if isinstance(node, (ForStatement, WhileStatement)):
                if hasattr(node, 'body') and node.body:
                    visit_loop_body(node.body)
            elif isinstance(node, Block):
                for stmt in node.statements:
                    visit(stmt)
            elif isinstance(node, IfStatement):
                if node.then_block:
                    visit(node.then_block)
                if node.else_block:
                    visit(node.else_block)

        visit(block)

    def _check_fperf004(self, block: Block):
        """
        FPERF004: un-spanned array indexing inside loop.
        Emits a performance remark when plain array access occurs inside a loop.
        """
        def _get_location(node: Any) -> tuple[int, int]:
            if hasattr(node, 'location') and node.location:
                return getattr(node.location, 'line', 1), getattr(node.location, 'column', 1)
            return 1, 1

        def visit_loop_body(node: Any):
            if isinstance(node, ArrayAccess) and isinstance(node.array, Variable):
                arr_name = node.array.name
                line, col = _get_location(node)
                finding = IdiomFinding(
                    rule_id="FPERF004",
                    severity="hint",
                    line=line,
                    column=col,
                    title="Un-spanned array indexing inside loop",
                    rationale=(
                        f"Array '{arr_name}' is indexed inside loop without span borrowing. "
                        f"Borrow a span slice ('let s = {arr_name}[..]') outside the loop to enable bounds-check elimination."
                    ),
                    applicability="advisory",
                    span_len=len(arr_name),
                )
                self.findings.append(finding)

            if isinstance(node, Block):
                for stmt in node.statements:
                    visit_loop_body(stmt)
            elif isinstance(node, VarDecl) and node.initializer:
                visit_loop_body(node.initializer)
            elif isinstance(node, Assignment):
                if node.value:
                    visit_loop_body(node.value)
                if node.target_expr:
                    visit_loop_body(node.target_expr)
            elif isinstance(node, IfStatement):
                if node.then_block:
                    visit_loop_body(node.then_block)
                if node.else_block:
                    visit_loop_body(node.else_block)

        def visit(node: Any):
            if isinstance(node, (ForStatement, WhileStatement)):
                if hasattr(node, 'body') and node.body:
                    visit_loop_body(node.body)
            elif isinstance(node, Block):
                for stmt in node.statements:
                    visit(stmt)
            elif isinstance(node, IfStatement):
                if node.then_block:
                    visit(node.then_block)
                if node.else_block:
                    visit(node.else_block)

        visit(block)
