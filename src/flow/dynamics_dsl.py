"""
Flow Dynamical Systems DSL
==========================

Novel surface syntax for control / GA / Gramian / attractor analysis.
Expanded before parse — desugars to stdlib dynamics calls.

Syntax
------

    dsys plant {
        discrete
        dt 0.1
        n 2 m 1 p 1
        A 1.0 0.1 0.0 1.0
        B 0.0 0.1
        C 1.0 0.0
    }

    horizon rollout finite 50
    horizon asymptotic infinite gamma 0.99

    sense on plant {
        controllable -> plant_ok
        spectral -> rho_open
        gramian finite rollout trace -> wc_fin
        gramian infinite asymptotic trace -> wc_inf
    }

    ga evolve on plant over rollout -> k1 k2 {
        population 12
        generations 30
        mutation 0.3
    }

    closed plant with k1 k2 {
        spectral -> rho_cl
        energy over rollout -> E_cl
        stable -> stable_cl
    }

    analyze plant ga k1 k2 over rollout -> report {
        full
    }
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class DsysDecl:
    name: str
    mode: str  # discrete | continuous
    dt: float
    n: int
    m: int
    p: int
    A: List[float]
    B: List[float]
    C: List[float]


@dataclass
class HorizonDecl:
    name: str
    kind: str  # finite | infinite
    steps: int = 0
    gamma: float = 1.0


@dataclass
class SenseDecl:
    system: str
    bindings: List[Tuple[str, str, Optional[str]]] = field(default_factory=list)
    # (kind, var, horizon_name optional)  kind: controllable|spectral|gramian_finite|gramian_infinite


@dataclass
class GAEvolveDecl:
    system: str
    horizon: str
    k1_var: str
    k2_var: str
    population: int = 8
    generations: int = 20
    mutation: float = 0.3


@dataclass
class ClosedDecl:
    system: str
    k1_var: str
    k2_var: str
    bindings: List[Tuple[str, str, Optional[str]]] = field(default_factory=list)
    # spectral, energy+horizon, stable


@dataclass
class AnalyzeDecl:
    system: str
    k1_var: str
    k2_var: str
    horizon: str
    report_var: str


@dataclass
class DynamicsProgram:
    systems: Dict[str, DsysDecl] = field(default_factory=dict)
    horizons: Dict[str, HorizonDecl] = field(default_factory=dict)
    senses: List[SenseDecl] = field(default_factory=list)
    ga_evolutions: List[GAEvolveDecl] = field(default_factory=list)
    closed_blocks: List[ClosedDecl] = field(default_factory=list)
    analyzes: List[AnalyzeDecl] = field(default_factory=list)


def _strip_comments(line: str) -> str:
    if "#" in line:
        return line.split("#", 1)[0].strip()
    return line.strip()


def _parse_floats(text: str) -> List[float]:
    return [float(x) for x in text.split() if x]


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


def parse_dynamics_dsl(source: str) -> Tuple[DynamicsProgram, str]:
    """Parse DSL constructs and return program + source with DSL blocks removed."""
    program = DynamicsProgram()
    lines = source.splitlines()
    out_lines: List[str] = []
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = _strip_comments(raw)
        if not line:
            out_lines.append(raw)
            i += 1
            continue

        if line.startswith("dsys "):
            m = re.match(r"dsys\s+(\w+)\s*\{", line)
            if not m:
                raise SyntaxError(f"Invalid dsys declaration: {line}")
            name = m.group(1)
            body_lines, i = _extract_brace_block(lines, i)
            decl = DsysDecl(name, "discrete", 0.1, 2, 1, 1, [], [], [])
            for bl in body_lines:
                b = _strip_comments(bl)
                if not b:
                    continue
                if b == "discrete":
                    decl.mode = "discrete"
                elif b == "continuous":
                    decl.mode = "continuous"
                elif b.startswith("dt "):
                    decl.dt = float(b.split()[1])
                elif b.startswith("n "):
                    parts = b.split()
                    decl.n = int(parts[1])
                    if "m" in parts:
                        decl.m = int(parts[parts.index("m") + 1])
                    if "p" in parts:
                        decl.p = int(parts[parts.index("p") + 1])
                elif b.startswith("A "):
                    decl.A = _parse_floats(b[2:])
                elif b.startswith("B "):
                    decl.B = _parse_floats(b[2:])
                elif b.startswith("C "):
                    decl.C = _parse_floats(b[2:])
            program.systems[name] = decl
            continue

        if line.startswith("horizon "):
            m = re.match(r"horizon\s+(\w+)\s+finite\s+(\d+)", line)
            if m:
                program.horizons[m.group(1)] = HorizonDecl(
                    m.group(1), "finite", steps=int(m.group(2))
                )
                i += 1
                continue
            m2 = re.match(
                r"horizon\s+(\w+)\s+infinite\s+gamma\s+([\d.]+)", line
            )
            if m2:
                program.horizons[m2.group(1)] = HorizonDecl(
                    m2.group(1), "infinite", gamma=float(m2.group(2))
                )
                i += 1
                continue
            raise SyntaxError(f"Invalid horizon: {line}")

        if line.startswith("sense on "):
            m = re.match(r"sense\s+on\s+(\w+)\s*\{", line)
            if not m:
                raise SyntaxError(f"Invalid sense block: {line}")
            sense = SenseDecl(m.group(1))
            body_lines, i = _extract_brace_block(lines, i)
            for bl in body_lines:
                b = _strip_comments(bl)
                if "->" not in b:
                    continue
                lhs, rhs = [x.strip() for x in b.split("->", 1)]
                if lhs == "controllable":
                    sense.bindings.append(("controllable", rhs, None))
                elif lhs == "spectral":
                    sense.bindings.append(("spectral", rhs, None))
                elif lhs.startswith("gramian finite "):
                    parts = lhs.split()
                    sense.bindings.append(("gramian_finite", rhs, parts[2]))
                elif lhs.startswith("gramian infinite "):
                    parts = lhs.split()
                    sense.bindings.append(("gramian_infinite", rhs, parts[2]))
            program.senses.append(sense)
            continue

        if line.startswith("ga evolve on "):
            m = re.match(
                r"ga\s+evolve\s+on\s+(\w+)\s+over\s+(\w+)\s*->\s*(\w+)\s+(\w+)\s*\{",
                line,
            )
            if not m:
                raise SyntaxError(f"Invalid ga evolve block: {line}")
            ga = GAEvolveDecl(m.group(1), m.group(2), m.group(3), m.group(4))
            body_lines, i = _extract_brace_block(lines, i)
            for bl in body_lines:
                b = _strip_comments(bl)
                if b.startswith("population "):
                    ga.population = int(b.split()[1])
                elif b.startswith("generations "):
                    ga.generations = int(b.split()[1])
                elif b.startswith("mutation "):
                    ga.mutation = float(b.split()[1])
            program.ga_evolutions.append(ga)
            continue

        if line.startswith("closed "):
            m = re.match(
                r"closed\s+(\w+)\s+with\s+(\w+)\s+(\w+)\s*\{", line
            )
            if not m:
                raise SyntaxError(f"Invalid closed block: {line}")
            closed = ClosedDecl(m.group(1), m.group(2), m.group(3))
            body_lines, i = _extract_brace_block(lines, i)
            for bl in body_lines:
                b = _strip_comments(bl)
                if "->" not in b:
                    continue
                lhs, rhs = [x.strip() for x in b.split("->", 1)]
                if lhs == "spectral":
                    closed.bindings.append(("spectral", rhs, None))
                elif lhs == "stable":
                    closed.bindings.append(("stable", rhs, None))
                elif lhs.startswith("energy over "):
                    hz = lhs.split()[2]
                    closed.bindings.append(("energy", rhs, hz))
            program.closed_blocks.append(closed)
            continue

        if line.startswith("analyze "):
            m = re.match(
                r"analyze\s+(\w+)\s+ga\s+(\w+)\s+(\w+)\s+over\s+(\w+)\s*->\s*(\w+)\s*\{",
                line,
            )
            if not m:
                raise SyntaxError(f"Invalid analyze block: {line}")
            program.analyzes.append(
                AnalyzeDecl(m.group(1), m.group(2), m.group(3), m.group(4), m.group(5))
            )
            body_lines, i = _extract_brace_block(lines, i)
            continue

        out_lines.append(raw)
        i += 1

    return program, "\n".join(out_lines)


def _flat_array(vals: List[float], name: str) -> str:
    inner = ", ".join(f"{v:.17g}" for v in vals)
    return f"let {name}: array<f64, {max(len(vals), 1)}> = [{inner}]"


def _zero_f64_array(size: int) -> str:
    n = max(size, 1)
    inner = ", ".join("0.0" for _ in range(n))
    return f"[{inner}]"


def compile_dynamics_program(program: DynamicsProgram) -> str:
    """Emit Flow setup code injected into main()."""
    if not any(
        [
            program.systems,
            program.senses,
            program.ga_evolutions,
            program.closed_blocks,
            program.analyzes,
        ]
    ):
        return ""

    lines: List[str] = [
        "    # --- dsys DSL expansion (auto-generated) ---",
    ]

    sys_vars: Dict[str, str] = {}
    hz_steps: Dict[str, int] = {}

    for name, hz in program.horizons.items():
        if hz.kind == "finite":
            lines.append(f"    let h_{name}: Horizon = horizon_finite({hz.steps})")
            hz_steps[name] = hz.steps
        else:
            lines.append(
                f"    let h_{name}: Horizon = horizon_infinite({hz.gamma:.17g})"
            )

    buf_i = 0

    def _bufs(count: int = 12) -> str:
        nonlocal buf_i
        names = []
        for _ in range(count):
            lines.append(f"    let __dsys_b{buf_i}: array<f64, 4> = [0.0, 0.0, 0.0, 0.0]")
            names.append(f"__dsys_b{buf_i}")
            buf_i += 1
        return names

    for name, sys in program.systems.items():
        var = f"__dsys_{name}"
        sys_vars[name] = var
        lines.append(f"    {_flat_array(sys.A, f'__dsys_{name}_A')}")
        lines.append(f"    {_flat_array(sys.B, f'__dsys_{name}_B')}")
        lines.append(f"    {_flat_array(sys.C, f'__dsys_{name}_C')}")
        if sys.mode == "continuous":
            lines.append(
                f"    let {var}_cont: DynamicalSystem = dsys_continuous("
                f"{sys.n}, {sys.m}, {sys.p}, {sys.dt:.17g}, "
                f"Matrix {{ data: __dsys_{name}_A, rows: {sys.n}, cols: {sys.n} }}, "
                f"Matrix {{ data: __dsys_{name}_B, rows: {sys.n}, cols: {sys.m} }}, "
                f"Matrix {{ data: __dsys_{name}_C, rows: {sys.p}, cols: {sys.n} }})"
            )
            bufs = _bufs(5)
            lines.append(
                f"    let {var}: DynamicalSystem = dsys_euler_discretize("
                f"{var}_cont, {bufs[0]}, {bufs[1]}, {bufs[2]}, {bufs[3]})"
            )
        else:
            lines.append(
                f"    let {var}: DynamicalSystem = dsys_discrete("
                f"{sys.n}, {sys.m}, {sys.p}, {sys.dt:.17g}, "
                f"Matrix {{ data: __dsys_{name}_A, rows: {sys.n}, cols: {sys.n} }}, "
                f"Matrix {{ data: __dsys_{name}_B, rows: {sys.n}, cols: {sys.m} }}, "
                f"Matrix {{ data: __dsys_{name}_C, rows: {sys.p}, cols: {sys.n} }})"
            )

    for sense in program.senses:
        sysv = sys_vars[sense.system]
        for kind, var, hz_name in sense.bindings:
            if kind == "controllable":
                bufs = _bufs(5)
                lines.append(f"    let mut {var}: i32 = 0")
                lines.append(
                    f"    {var} = is_controllable({sysv}, {bufs[0]}, {bufs[1]}, "
                    f"{bufs[2]}, {bufs[3]}, {bufs[4]})"
                )
            elif kind == "spectral":
                lines.append(f"    let mut {var}: f64 = 0.0")
                lines.append(f"    {var} = matrix_spectral_radius_2x2({sysv}.A)")
            elif kind == "gramian_finite":
                bufs = _bufs(4)
                lines.append(f"    let mut {var}: f64 = 0.0")
                lines.append(
                    f"    let __W_{var}: Matrix = gramian_finite_horizon("
                    f"{sysv}, h_{hz_name}, {bufs[0]}, {bufs[1]}, {bufs[2]}, {bufs[3]})"
                )
                lines.append(f"    {var} = matrix_trace(__W_{var})")
            elif kind == "gramian_infinite":
                bufs = _bufs(4)
                lines.append(f"    let mut {var}: f64 = 0.0")
                lines.append(
                    f"    let __W_{var}: Matrix = gramian_infinite_horizon("
                    f"{sysv}, h_{hz_name}, {bufs[0]}, {bufs[1]}, {bufs[2]}, {bufs[3]})"
                )
                lines.append(f"    {var} = matrix_trace(__W_{var})")

    ga_cfg_by_key: Dict[Tuple[str, str], GAEvolveDecl] = {}
    for ga in program.ga_evolutions:
        ga_cfg_by_key[(ga.system, ga.horizon)] = ga

    for gi, ga in enumerate(program.ga_evolutions):
        sysv = sys_vars[ga.system]
        steps = hz_steps.get(ga.horizon, 50)
        pop = ga.population
        tag = f"__ga_e{gi}"
        lines.append(f"    let mut {ga.k1_var}: f64 = 0.0")
        lines.append(f"    let mut {ga.k2_var}: f64 = 0.0")
        lines.append(f"    let {tag}_k1: array<f64, {pop}> = {_zero_f64_array(pop)}")
        lines.append(f"    let {tag}_k2: array<f64, {pop}> = {_zero_f64_array(pop)}")
        lines.append(f"    let {tag}_fit: array<f64, {pop}> = {_zero_f64_array(pop)}")
        lines.append(f"    let {tag}_bk1: array<f64, 1> = [0.0]")
        lines.append(f"    let {tag}_bk2: array<f64, 1> = [0.0]")
        lines.append(f"    let {tag}_hist: array<f64, 32> = {_zero_f64_array(32)}")
        lines.append(
            f"    let {tag}_cfg: GAConfig = GAConfig {{ population: {pop}, "
            f"generations: {ga.generations}, horizon: {steps}, "
            f"mutation: {ga.mutation:.17g} }}"
        )
        lines.append(
            f"    ga_evolve_traced({sysv}, {steps}, {tag}_cfg, {tag}_k1, {tag}_k2, "
            f"{tag}_fit, {tag}_bk1, {tag}_bk2, {tag}_hist)"
        )
        lines.append(f"    {ga.k1_var} = {tag}_bk1[0]")
        lines.append(f"    {ga.k2_var} = {tag}_bk2[0]")

    for closed in program.closed_blocks:
        sysv = sys_vars[closed.system]
        bufs = _bufs(2)
        lines.append(
            f"    let __cl_{closed.system}: DynamicalSystem = "
            f"ga_closed_loop_matrix({sysv}, {closed.k1_var}, {closed.k2_var}, "
            f"{bufs[0]}, {bufs[1]})"
        )
        for kind, var, hz_name in closed.bindings:
            if kind == "spectral":
                lines.append(
                    f"    let mut {var}: f64 = matrix_spectral_radius_2x2(__cl_{closed.system}.A)"
                )
            elif kind == "stable":
                lines.append(f"    let mut {var}: i32 = 0")
                lines.append(
                    f"    if matrix_spectral_radius_2x2(__cl_{closed.system}.A) < 1.0 {{ "
                    f"{var} = 1 }}"
                )
            elif kind == "energy":
                steps = hz_steps.get(hz_name or "", 50)
                lines.append(
                    f"    let mut {var}: f64 = ga_closed_loop_energy(__cl_{closed.system}, {steps})"
                )

    for ai, analyze in enumerate(program.analyzes):
        sysv = sys_vars[analyze.system]
        steps = hz_steps.get(analyze.horizon, 50)
        linked = ga_cfg_by_key.get((analyze.system, analyze.horizon))
        pop = linked.population if linked else 12
        gens = linked.generations if linked else 30
        mut = linked.mutation if linked else 0.3
        tag = f"__ga_a{ai}"
        lines.append(f"    let mut {analyze.report_var}: GAAnalysisReport = GAAnalysisReport {{")
        lines.append("        plant_controllable: 0, plant_spectral_radius: 0.0,")
        lines.append("        closed_spectral_radius: 0.0, gramian_open_finite: 0.0,")
        lines.append("        gramian_open_infinite: 0.0, closed_loop_energy: 0.0,")
        lines.append("        baseline_cost: 0.0, evolved_cost: 0.0, fitness_drop: 0.0,")
        lines.append("        convergence_gen: 0, stable_closed_loop: 0")
        lines.append("    }")
        lines.append(f"    let {tag}_k1: array<f64, {pop}> = {_zero_f64_array(pop)}")
        lines.append(f"    let {tag}_k2: array<f64, {pop}> = {_zero_f64_array(pop)}")
        lines.append(f"    let {tag}_fit: array<f64, {pop}> = {_zero_f64_array(pop)}")
        lines.append(f"    let {tag}_bk1: array<f64, 1> = [0.0]")
        lines.append(f"    let {tag}_bk2: array<f64, 1> = [0.0]")
        lines.append(f"    let {tag}_hist: array<f64, 32> = {_zero_f64_array(32)}")
        bufs = _bufs(12)
        lines.append(
            f"    let {tag}_cfg: GAConfig = GAConfig {{ population: {pop}, "
            f"generations: {gens}, horizon: {steps}, mutation: {mut:.17g} }}"
        )
        lines.append(
            f"    {analyze.report_var} = ga_analyze_control_search("
            f"{sysv}, {steps}, {tag}_cfg, {tag}_k1, {tag}_k2, {tag}_fit, {tag}_bk1, "
            f"{tag}_bk2, {tag}_hist, {bufs[0]}, {bufs[1]}, {bufs[2]}, {bufs[3]}, "
            f"{bufs[4]}, {bufs[5]}, {bufs[6]}, {bufs[7]}, {bufs[8]}, {bufs[9]}, "
            f"{bufs[10]}, {bufs[11]})"
        )
        lines.append(f"    {analyze.k1_var} = {tag}_bk1[0]")
        lines.append(f"    {analyze.k2_var} = {tag}_bk2[0]")

    lines.append("    # --- end dsys DSL expansion ---")
    return "\n".join(lines)


def inject_dynamics_setup(flow_source: str, setup: str) -> str:
    """Insert generated setup at the beginning of main()'s body."""
    if not setup.strip():
        return flow_source
    marker = re.search(r"function\s+main\s*\([^)]*\)\s*->\s*\w+\s*\{", flow_source)
    if not marker:
        return flow_source + "\n\nfunction main() -> i32 {\n" + setup + "\n    return 0\n}\n"
    insert_at = marker.end()
    return flow_source[:insert_at] + "\n" + setup + flow_source[insert_at:]


def expand_dynamics_dsl(source: str) -> str:
    """Full pipeline: parse DSL blocks, compile, inject into main."""
    if not has_dynamics_dsl(source):
        return source
    program, stripped = parse_dynamics_dsl(source)
    setup = compile_dynamics_program(program)
    if not setup:
        return stripped
    merged = stripped
    if 'import "stdlib/dynamics/ga_analysis.flow"' not in merged:
        merged = 'import "stdlib/dynamics/ga_analysis.flow"\n\n' + merged
    return inject_dynamics_setup(merged, setup)


def has_dynamics_dsl(source: str) -> bool:
    return bool(
        re.search(r"^\s*dsys\s+\w+", source, re.MULTILINE)
        or re.search(r"^\s*horizon\s+\w+", source, re.MULTILINE)
        or re.search(r"^\s*sense\s+on\s+", source, re.MULTILINE)
        or re.search(r"^\s*ga\s+evolve\s+", source, re.MULTILINE)
        or re.search(r"^\s*closed\s+\w+", source, re.MULTILINE)
        or re.search(r"^\s*analyze\s+\w+", source, re.MULTILINE)
    )