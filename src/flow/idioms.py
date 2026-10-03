"""
Semantic Idiom Advisor for Flow

Exposes a shared engine for finding code that is valid but could be
written in a clearer, safer, more Flow-native way.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from .parser import (
    Block, VarDecl, Assignment, ReturnStatement, StructLiteral, IfStatement, MatchStatement,
    Expression, FunctionDecl, FieldAccess, Variable
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
        """Analyze a single function for idioms."""
        if func.body:
            self._check_fidiom001(func.body)
            self._check_fidiom002(func.body)
            
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
                if node.else_if:
                    visit(node.else_if)
            elif isinstance(node, MatchStatement):
                for branch in node.branches:
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
                    line = decl.location.line
                    col = decl.location.column
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
                                line = node.location.line
                                col = node.location.column
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
                if node.else_if:
                    visit(node.else_if)
            elif isinstance(node, MatchStatement):
                for branch in node.branches:
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
