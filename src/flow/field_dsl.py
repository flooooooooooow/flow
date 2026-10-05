"""
Field / boundary PDE surface (pattern-adoption #163).

Stage-1 expander — strips north-star grammar and emits a heat-step helper:

    field T : f64[32] on Line
    T evolves as laplacian(T)          # or `r * laplacian(T)` / `alpha * laplacian(T)`
    boundary T { left = AMBIENT  right = AMBIENT }

→ `T_field_step(u, next, r)` calling `heat_euler_step_1d`, plus size/BC consts.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class FieldDecl:
    name: str
    n: int
    domain: str = "Line"
    left_bc: str = "0.0"
    right_bc: str = "0.0"
    # Optional float multiplier baked into docs; step still takes r at call site
    # unless `r_literal` is set from `NUMBER * laplacian(Name)`.
    r_literal: Optional[float] = None
    evolve_seen: bool = False


_FIELD_RE = re.compile(
    r"^field\s+(\w+)\s*:\s*f64\s*\[\s*(\d+)\s*\]\s+on\s+(\w+)\s*$"
)
_BOUNDARY_HEAD_RE = re.compile(r"^boundary\s+(\w+)\s*\{")
_BOUNDARY_ASSIGN_RE = re.compile(r"^(left|right)\s*=\s*(.+)$")
_EVOLVE_RE = re.compile(r"^(\w+)\s+evolves\s+as\s+(.+)$")
_LAP_MUL_RE = re.compile(
    r"^(?:([+\-\d.eE]+|\w+)\s*\*\s*)?laplacian\s*\(\s*(\w+)\s*\)"
    r"(?:\s*\*\s*([+\-\d.eE]+|\w+))?\s*$"
)


def _strip_comments(line: str) -> str:
    if "#" in line:
        return line.split("#", 1)[0].strip()
    return line.strip()


def _extract_brace_block(lines: List[str], start: int) -> Tuple[List[str], int]:
    body: List[str] = []
    depth = 0
    i = start
    while i < len(lines):
        line = lines[i]
        depth += line.count("{") - line.count("}")
        if i > start or "{" in line:
            if depth > 0 or (i == start and "{" in line):
                inner = line
                if i == start:
                    inner = line.split("{", 1)[1]
                if depth > 0:
                    body.append(inner.rstrip("}").strip())
                elif "}" in line:
                    body.append(inner.split("}", 1)[0].strip())
        if depth <= 0 and i > start:
            return body, i + 1
        i += 1
    return body, i


def has_field_dsl(source: str) -> bool:
    return bool(
        re.search(r"^\s*field\s+\w+\s*:", source, re.MULTILINE)
        or re.search(r"^\s*boundary\s+\w+\s*\{", source, re.MULTILINE)
    )


def parse_field_dsl(source: str) -> Tuple[Dict[str, FieldDecl], str]:
    """Strip field/boundary/field-evolves lines; return decls + remainder."""
    lines = source.splitlines()
    out: List[str] = []
    fields: Dict[str, FieldDecl] = {}
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = _strip_comments(raw)

        field_m = _FIELD_RE.match(line) if line else None
        if field_m:
            name = field_m.group(1)
            n = int(field_m.group(2))
            domain = field_m.group(3)
            if domain != "Line":
                raise SyntaxError(
                    f"field '{name}': only `on Line` is supported in Stage-1 "
                    f"(got '{domain}')"
                )
            if n <= 1:
                raise SyntaxError(f"field '{name}': size must be > 1")
            if name in fields:
                raise SyntaxError(f"duplicate field '{name}'")
            fields[name] = FieldDecl(name=name, n=n, domain=domain)
            i += 1
            continue

        bound_m = _BOUNDARY_HEAD_RE.match(line) if line else None
        if bound_m:
            name = bound_m.group(1)
            if name not in fields:
                raise SyntaxError(
                    f"boundary '{name}': declare `field {name} : …` first"
                )
            body, next_i = _extract_brace_block(lines, i)
            left = None
            right = None
            items: List[str] = []
            for bl in body:
                b = _strip_comments(bl)
                if not b:
                    continue
                # Allow `left = X  right = Y` on one line.
                pieces = re.split(r"(?=\b(?:left|right)\s*=)", b)
                for piece in pieces:
                    piece = piece.strip()
                    if piece:
                        items.append(piece)
            for b in items:
                am = _BOUNDARY_ASSIGN_RE.match(b)
                if not am:
                    raise SyntaxError(
                        f"boundary '{name}': expected `left = …` / `right = …`, "
                        f"got '{b}'"
                    )
                side, val = am.group(1), am.group(2).strip()
                if not val:
                    raise SyntaxError(f"boundary '{name}': empty {side} value")
                if side == "left":
                    left = val
                else:
                    right = val
            if left is None or right is None:
                raise SyntaxError(
                    f"boundary '{name}': need both left and right"
                )
            fields[name].left_bc = left
            fields[name].right_bc = right
            i = next_i
            continue

        evolve_m = _EVOLVE_RE.match(line) if line else None
        if evolve_m and evolve_m.group(1) in fields:
            name = evolve_m.group(1)
            rhs = evolve_m.group(2).strip()
            lap_m = _LAP_MUL_RE.match(rhs)
            if not lap_m or lap_m.group(2) != name:
                raise SyntaxError(
                    f"field '{name}' evolves: Stage-1 expects "
                    f"`{name} evolves as laplacian({name})` or "
                    f"`c * laplacian({name})`"
                )
            pre, _lap_name, post = lap_m.group(1), lap_m.group(2), lap_m.group(3)
            if pre and post:
                raise SyntaxError(
                    f"field '{name}' evolves: use at most one multiplier"
                )
            mul = pre or post
            if mul is not None:
                try:
                    fields[name].r_literal = float(mul)
                except ValueError:
                    # Identifier multiplier — still pass r at call site
                    fields[name].r_literal = None
            fields[name].evolve_seen = True
            i += 1
            continue

        out.append(raw)
        i += 1

    for name, f in fields.items():
        if not f.evolve_seen:
            raise SyntaxError(
                f"field '{name}': missing `{name} evolves as laplacian({name})`"
            )
    return fields, "\n".join(out)


def compile_fields(fields: Dict[str, FieldDecl]) -> str:
    chunks: List[str] = []
    for f in fields.values():
        chunks.append(
            f"# generated from field {f.name} : f64[{f.n}] on {f.domain}\n"
            f"const {f.name}_field_n: i32 = {f.n}\n"
            f"\n"
            f"function {f.name}_field_step(\n"
            f"    u: ptr<f64>,\n"
            f"    next: ptr<f64>,\n"
            f"    r: f64\n"
            f") -> void {{\n"
            f"    heat_euler_step_1d(u, next, {f.n}, r, "
            f"{f.left_bc}, {f.right_bc})\n"
            f"}}\n"
        )
    return "\n".join(chunks)


def inject_before_main(flow_source: str, helpers: str) -> str:
    if not helpers.strip():
        return flow_source
    marker = re.search(r"\nfunction\s+main\s*\(", flow_source)
    if not marker:
        return flow_source.rstrip() + "\n\n" + helpers.strip() + "\n"
    return (
        flow_source[: marker.start()]
        + "\n\n"
        + helpers.strip()
        + "\n"
        + flow_source[marker.start() :]
    )


def expand_field_dsl(source: str) -> str:
    if not has_field_dsl(source):
        return source
    fields, stripped = parse_field_dsl(source)
    if not fields:
        return stripped
    helpers = compile_fields(fields)
    merged = stripped
    if 'import "stdlib/dynamics/pde.flow"' not in merged:
        merged = 'import "stdlib/dynamics/pde.flow"\n' + merged
    return inject_before_main(merged, helpers)
