"""
Flow Dynamical Systems DSL
==========================

Novel surface syntax for control / GA / Gramian / attractor analysis.
Expanded before parse — desugars to stdlib dynamics calls.

Syntax
------

Bare forms and namespaced forms are equivalent. Prefer `dyn.*` / `dynamics { }`
when you want the vocabulary out of the global keyword soup:

    dynamics {
        dsys plant {
            discrete
            dt 0.1
            n 2 m 1 p 1
            A 1.0 0.1 0.0 1.0
            B 0.0 0.1
            C 1.0 0.0
        }
        horizon rollout finite 50
        sense on plant {
            controllable -> plant_ok
            spectral -> rho_open
        }
        ga evolve on plant over rollout -> k1 k2 {
            population 12
            generations 30
            mutation 0.3
        }
    }

    # Or line-prefixed: dyn.horizon rollout finite 50
    #                   dynamics.analyze plant ga k1 k2 over rollout -> report { full }

    dsys plant { ... }   # bare form still works
    horizon rollout finite 50
    sense on plant { controllable -> plant_ok  spectral -> rho_open }
    ga evolve on plant over rollout -> k1 k2 { population 12 generations 30 mutation 0.3 }
    closed plant with k1 k2 { spectral -> rho_cl  energy over rollout -> E_cl  stable -> stable_cl }
    analyze plant ga k1 k2 over rollout -> report { full }

    # Bridge from nonlinear `flow` → dsys (north-star §9 / represent-linear card).
    # Inside a flow body, or top-level `represent linear Name { ... }`.
    # Stage-1: explicit A/B/C matrices (manual linear model). Automatic
    # Jacobian-at-`at` linearization is not yet implemented — omitting A
    # raises "linearization coefficients required".
    #
    # flow Pendulum { ... represent linear { at (...)  A ... B ... C ... } }
    # → synthesizes dsys Pendulum_lin { continuous ... } for sense/ga/analyze.
    #
    # `represent nonlinear { }` is a recognized no-op (the flow *is* the
    # nonlinear model). `koopman` / `transfer_function` / `frequency` are
    # reserved and rejected with "not yet implemented".
    #
    # Grammar collision for `analyze` (vision form vs legacy GA form): one
    # token of lookahead after the name — `{` ⇒ vision (future); `ga` ⇒
    # legacy. Both remain supported (north-star §9.4).

    wfc field layout {
        size 4 4
        tiles 3
        seed 7
        pin 0 1
        collapse 20
    }

    couple plant field layout using report k1 k2 {
        guidance -> guide
        collapsed -> wfc_collapsed
    }

    guide plant with k1 k2 through layout using guide over rollout {
        input_scale -> B_scale
        energy -> E_guided
        spectral -> rho_guided
        stable -> stable_guided
    }
"""

from __future__ import annotations

import math
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
class AnalyzeLqrDecl:
    """`analyze plant { lqr { Q … R … -> k0 … } }` → dlqr_diag_q_scalar_u (#162)."""

    system: str
    q_diag: List[float] = field(default_factory=list)
    r: float = 1.0
    gain_vars: List[str] = field(default_factory=list)
    max_iter: int = 200


@dataclass
class WFCDecl:
    name: str
    width: int = 4
    height: int = 4
    tiles: int = 3
    seed: int = 7
    pin_cell: int = 0
    pin_tile: int = 1
    steps: int = 20


@dataclass
class CoupleDecl:
    system: str
    field: str
    report_var: str
    k1_var: str
    k2_var: str
    guidance_var: str = "guide"
    wfc_report_var: str = "wfc_report"
    bindings: List[Tuple[str, str]] = field(default_factory=list)


@dataclass
class GuideDecl:
    system: str
    k1_var: str
    k2_var: str
    field: str
    guidance_var: str
    horizon: str
    bindings: List[Tuple[str, str]] = field(default_factory=list)


@dataclass
class RepresentLinearDecl:
    """Manual (or future auto) linearization attached to a flow → `Name_lin` dsys."""

    flow_name: str
    mode: str = "continuous"  # continuous | discrete
    dt: float = 0.001
    n: int = 0
    m: int = 0
    p: int = 0
    A: List[float] = field(default_factory=list)
    B: List[float] = field(default_factory=list)
    C: List[float] = field(default_factory=list)
    at_point: Dict[str, float] = field(default_factory=dict)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)


@dataclass
class RepresentPhasePortraitDecl:
    """`represent phase_portrait(a, b) { … }` → `{Name}_portrait_frame` helper.

    Stage-1 lowers trail push + 2D projection draw; window open/present stay in
    main (pattern-adoption #165).
    """

    flow_name: str
    axis0: str
    axis1: str
    trail: int = 320
    win_w: int = 900
    win_h: int = 700
    pad_x: int = 10
    pad_y: int = 30
    # axis_name -> (lo, hi, "col"|"row")
    maps: Dict[str, Tuple[float, float, str]] = field(default_factory=dict)


@dataclass
class DynamicsProgram:
    systems: Dict[str, DsysDecl] = field(default_factory=dict)
    horizons: Dict[str, HorizonDecl] = field(default_factory=dict)
    wfc_fields: Dict[str, WFCDecl] = field(default_factory=dict)
    senses: List[SenseDecl] = field(default_factory=list)
    ga_evolutions: List[GAEvolveDecl] = field(default_factory=list)
    closed_blocks: List[ClosedDecl] = field(default_factory=list)
    analyzes: List[AnalyzeDecl] = field(default_factory=list)
    couples: List[CoupleDecl] = field(default_factory=list)
    guides: List[GuideDecl] = field(default_factory=list)
    represents: List[RepresentLinearDecl] = field(default_factory=list)
    portraits: List[RepresentPhasePortraitDecl] = field(default_factory=list)
    analyze_lqrs: List[AnalyzeLqrDecl] = field(default_factory=list)


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


_DYN_NS_RE = re.compile(r"^(?:dyn|dynamics)\.(.+)$")


def _extract_brace_block_preserving(
    lines: List[str], start: int
) -> Tuple[List[str], int]:
    """Extract `{ ... }` body while keeping nested braces in the returned lines.

    Unlike `_extract_brace_block`, closing `}` lines of *inner* blocks are
    preserved so the body can be re-parsed by `parse_dynamics_dsl`.
    """
    depth = 0
    i = start
    body: List[str] = []
    while i < len(lines):
        line = lines[i]
        if i == start:
            after = line.split("{", 1)[1] if "{" in line else ""
            depth = 1 + after.count("{") - after.count("}")
            if depth > 0:
                if after.strip():
                    body.append(after.rstrip())
            else:
                return body, i + 1
        else:
            depth += line.count("{") - line.count("}")
            if depth > 0:
                body.append(line)
            else:
                before, _, _rest = line.rpartition("}")
                if before.strip():
                    body.append(before.rstrip())
                return body, i + 1
        i += 1
    return body, i


def _merge_dynamics_program(dst: "DynamicsProgram", src: "DynamicsProgram") -> None:
    """Merge `src` into `dst` (used for `dynamics { ... }` namespace blocks)."""
    dst.systems.update(src.systems)
    dst.horizons.update(src.horizons)
    dst.senses.extend(src.senses)
    dst.ga_evolutions.extend(src.ga_evolutions)
    dst.closed_blocks.extend(src.closed_blocks)
    dst.analyzes.extend(src.analyzes)
    dst.wfc_fields.update(src.wfc_fields)
    dst.couples.extend(src.couples)
    dst.guides.extend(src.guides)
    dst.represents.extend(src.represents)
    dst.portraits.extend(src.portraits)
    dst.analyze_lqrs.extend(src.analyze_lqrs)


def _strip_dynamics_namespace(line: str) -> str:
    """Allow `dyn.dsys` / `dynamics.horizon` as namespaced aliases of bare DSL.

    Bare forms (`dsys`, `horizon`, …) remain valid. Namespaced forms keep the
    dynamics vocabulary out of the global identifier soup for editors and
    future grammar work — see docs/language/dynamics-dsl.md § Namespaces.
    """
    m = _DYN_NS_RE.match(line)
    return m.group(1).strip() if m else line


_REPRESENT_RESERVED = frozenset({"koopman", "transfer_function", "frequency"})
_REPRESENT_HEAD_RE = re.compile(
    r"^represent\s+(\w+)(?:\s+(?:for\s+)?(\w+))?\s*\{"
)
_REPRESENT_PORTRAIT_HEAD_RE = re.compile(
    r"^represent\s+phase_portrait\s*\(\s*(\w+)\s*,\s*(\w+)\s*\)\s*\{"
)
_FLOW_HEAD_RE = re.compile(r"^flow\s+(\w+)\s*\{")
_AT_POINT_RE = re.compile(r"^at\s*\((.*)\)\s*$")
_NAMED_LIST_RE = re.compile(r"^(inputs|outputs)\s*\((.*)\)\s*$")
_PORTRAIT_TRAIL_RE = re.compile(r"^trail\s+(\d+)\s*$")
_PORTRAIT_WINDOW_RE = re.compile(r"^window\s+(\d+)\s*,\s*(\d+)\s*$")
_PORTRAIT_MAP_RE = re.compile(
    r"^map\s+(\w+)\s+in\s*\[\s*([+\-\d.eE]+)\s*,\s*([+\-\d.eE]+)\s*\]\s*"
    r"->\s*(col|row)\s*$"
)


def _parse_at_point(inner: str) -> Dict[str, float]:
    """Parse `angle: 0.0, velocity: 0.0` bindings inside `at (...)`."""
    point: Dict[str, float] = {}
    inner = inner.strip()
    if not inner:
        return point
    for part in inner.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            raise SyntaxError(
                f"invalid `at` binding '{part}' in represent linear; "
                "expected name: value"
            )
        name, val = [x.strip() for x in part.split(":", 1)]
        if not re.match(r"^\w+$", name):
            raise SyntaxError(f"invalid state name in `at`: {name}")
        try:
            point[name] = float(val)
        except ValueError as exc:
            raise SyntaxError(
                f"invalid numeric value in `at` for '{name}': {val}"
            ) from exc
    return point


def _parse_name_list(inner: str) -> List[str]:
    inner = inner.strip()
    if not inner:
        return []
    names = []
    for part in inner.split(","):
        part = part.strip()
        if not part:
            continue
        if not re.match(r"^\w+$", part):
            raise SyntaxError(f"invalid name in represent linear list: {part}")
        names.append(part)
    return names


def _parse_represent_linear_body(
    flow_name: str, body_lines: List[str]
) -> RepresentLinearDecl:
    """Parse the body of `represent linear { ... }` into a decl.

    Stage-1 requires explicit A (and typically B/C) matrices. An `at (...)`
    operating point alone is not enough yet — automatic Jacobian evaluation
    is deferred (north-star §9.2 v1 goal; not shipped here).
    """
    decl = RepresentLinearDecl(flow_name=flow_name)
    for bl in body_lines:
        b = _strip_comments(bl)
        if not b:
            continue
        at_m = _AT_POINT_RE.match(b)
        if at_m:
            decl.at_point = _parse_at_point(at_m.group(1))
            continue
        list_m = _NAMED_LIST_RE.match(b)
        if list_m:
            kind, inner = list_m.group(1), list_m.group(2)
            names = _parse_name_list(inner)
            if kind == "inputs":
                decl.inputs = names
            else:
                decl.outputs = names
            continue
        if b == "continuous":
            decl.mode = "continuous"
        elif b == "discrete":
            decl.mode = "discrete"
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
        else:
            raise SyntaxError(
                f"unknown item in represent linear for '{flow_name}': {b}"
            )
    return decl


def _represent_to_dsys(rep: RepresentLinearDecl) -> DsysDecl:
    """Lower a represent-linear decl to a synthesized `Name_lin` DsysDecl."""
    if not rep.A:
        hint = ""
        if rep.at_point:
            hint = (
                f" (operating point at {rep.at_point} was given, but "
                "automatic Jacobian linearization is not yet implemented)"
            )
        raise SyntaxError(
            f"represent linear for '{rep.flow_name}': linearization "
            f"coefficients required{hint}; supply explicit A (and optional "
            "B/C) matrices in the represent linear block, e.g. "
            "`A 0.0 1.0 -9.81 0.0`"
        )
    n = rep.n
    if n <= 0:
        root = int(round(math.sqrt(len(rep.A))))
        if root * root != len(rep.A) or root < 1:
            raise SyntaxError(
                f"represent linear for '{rep.flow_name}': A must list n×n "
                f"floats (got {len(rep.A)} values); or set `n` explicitly"
            )
        n = root
    elif len(rep.A) != n * n:
        raise SyntaxError(
            f"represent linear for '{rep.flow_name}': A has {len(rep.A)} "
            f"entries but n={n} expects {n * n}"
        )

    m = rep.m
    B = list(rep.B)
    if not B:
        if m < 0:
            m = 0
        # Zero B column count when omitted (open dynamics / spectral-only).
        if m == 0 and rep.inputs:
            m = len(rep.inputs)
            B = [0.0] * (n * m)
        elif m == 0:
            B = [0.0]
        else:
            B = [0.0] * (n * m)
    else:
        if m <= 0:
            if len(B) % n != 0:
                raise SyntaxError(
                    f"represent linear for '{rep.flow_name}': B length "
                    f"{len(B)} is not a multiple of n={n}"
                )
            m = len(B) // n
        elif len(B) != n * m:
            raise SyntaxError(
                f"represent linear for '{rep.flow_name}': B has {len(B)} "
                f"entries but n={n} m={m} expects {n * m}"
            )

    p = rep.p
    C = list(rep.C)
    if not C:
        if p <= 0:
            p = n
        if p != n:
            raise SyntaxError(
                f"represent linear for '{rep.flow_name}': supply C (p×n) "
                f"when p != n (got p={p}, n={n})"
            )
        # Identity observation when C omitted.
        C = [1.0 if i == j else 0.0 for i in range(p) for j in range(n)]
    else:
        if p <= 0:
            if len(C) % n != 0:
                raise SyntaxError(
                    f"represent linear for '{rep.flow_name}': C length "
                    f"{len(C)} is not a multiple of n={n}"
                )
            p = len(C) // n
        elif len(C) != p * n:
            raise SyntaxError(
                f"represent linear for '{rep.flow_name}': C has {len(C)} "
                f"entries but p={p} n={n} expects {p * n}"
            )

    return DsysDecl(
        name=f"{rep.flow_name}_lin",
        mode=rep.mode,
        dt=rep.dt,
        n=n,
        m=m,
        p=p,
        A=list(rep.A),
        B=B,
        C=C,
    )


def _parse_represent_phase_portrait_body(
    flow_name: str,
    axis0: str,
    axis1: str,
    body_lines: List[str],
) -> RepresentPhasePortraitDecl:
    """Parse `represent phase_portrait(a, b) { trail …; window …; map … }`."""
    decl = RepresentPhasePortraitDecl(
        flow_name=flow_name, axis0=axis0, axis1=axis1
    )
    for bl in body_lines:
        b = _strip_comments(bl)
        if not b:
            continue
        trail_m = _PORTRAIT_TRAIL_RE.match(b)
        if trail_m:
            decl.trail = int(trail_m.group(1))
            if decl.trail <= 0:
                raise SyntaxError(
                    f"represent phase_portrait for '{flow_name}': "
                    "trail must be positive"
                )
            continue
        win_m = _PORTRAIT_WINDOW_RE.match(b)
        if win_m:
            decl.win_w = int(win_m.group(1))
            decl.win_h = int(win_m.group(2))
            continue
        map_m = _PORTRAIT_MAP_RE.match(b)
        if map_m:
            axis = map_m.group(1)
            if axis not in (axis0, axis1):
                raise SyntaxError(
                    f"represent phase_portrait for '{flow_name}': map axis "
                    f"'{axis}' is not one of ({axis0}, {axis1})"
                )
            try:
                lo = float(map_m.group(2))
                hi = float(map_m.group(3))
            except ValueError as exc:
                raise SyntaxError(
                    f"represent phase_portrait for '{flow_name}': invalid "
                    f"range in map for '{axis}'"
                ) from exc
            kind = map_m.group(4)
            decl.maps[axis] = (lo, hi, kind)
            continue
        raise SyntaxError(
            f"unknown item in represent phase_portrait for '{flow_name}': {b}"
        )

    if axis0 not in decl.maps or axis1 not in decl.maps:
        raise SyntaxError(
            f"represent phase_portrait for '{flow_name}': need map for both "
            f"'{axis0}' and '{axis1}'"
        )
    kinds = {decl.maps[axis0][2], decl.maps[axis1][2]}
    if kinds != {"col", "row"}:
        raise SyntaxError(
            f"represent phase_portrait for '{flow_name}': maps must assign "
            "one axis to col and one to row"
        )
    return decl


def _extract_represent_blocks(
    source: str,
) -> Tuple[List[RepresentLinearDecl], List[RepresentPhasePortraitDecl], str]:
    """Strip `represent …` blocks from source; return decls + remainder.

    Recognizes:
      - inside `flow Name { … represent linear { … } … }`
      - top-level `represent linear Name { … }` / `represent linear for Name { … }`
      - `represent phase_portrait(a, b) { … }` inside a flow (#165)
      - `represent nonlinear { … }` as a no-op strip
      - reserved kinds → SyntaxError ("not yet implemented")
    """
    lines = source.splitlines()
    out_lines: List[str] = []
    represents: List[RepresentLinearDecl] = []
    portraits: List[RepresentPhasePortraitDecl] = []
    i = 0
    brace_depth = 0
    current_flow: Optional[str] = None
    flow_body_depth: Optional[int] = None

    while i < len(lines):
        raw = lines[i]
        line = _strip_comments(raw)

        flow_m = _FLOW_HEAD_RE.match(line) if line else None
        if flow_m and brace_depth == 0:
            current_flow = flow_m.group(1)
            # Body depth is the depth after this line's braces are applied.
            delta = raw.count("{") - raw.count("}")
            flow_body_depth = brace_depth + delta
            out_lines.append(raw)
            brace_depth += delta
            i += 1
            continue

        portrait_m = _REPRESENT_PORTRAIT_HEAD_RE.match(line) if line else None
        if portrait_m:
            body_lines, next_i = _extract_brace_block(lines, i)
            if (
                current_flow is None
                or flow_body_depth is None
                or brace_depth < flow_body_depth
            ):
                raise SyntaxError(
                    "represent phase_portrait(...) must appear inside "
                    "`flow Name { ... }`"
                )
            portraits.append(
                _parse_represent_phase_portrait_body(
                    current_flow,
                    portrait_m.group(1),
                    portrait_m.group(2),
                    body_lines,
                )
            )
            i = next_i
            continue

        rep_m = _REPRESENT_HEAD_RE.match(line) if line else None
        if rep_m:
            kind = rep_m.group(1)
            explicit_name = rep_m.group(2)
            body_lines, next_i = _extract_brace_block(lines, i)

            if kind == "nonlinear":
                # Recognized no-op: the enclosing flow is the nonlinear model.
                i = next_i
                continue

            if kind == "phase_portrait":
                raise SyntaxError(
                    "represent phase_portrait needs axes: "
                    "`represent phase_portrait(x, z) { ... }`"
                )

            if kind in _REPRESENT_RESERVED:
                raise SyntaxError(
                    f"represent {kind}: not yet implemented "
                    "(Stage-1 ships `represent linear` with explicit A/B/C; "
                    "see docs/vision/north-star.md §9)"
                )

            if kind != "linear":
                raise SyntaxError(
                    f"unknown represent kind '{kind}'; expected linear, "
                    "nonlinear, phase_portrait, or a reserved form "
                    "(koopman|transfer_function|frequency)"
                )

            flow_name = explicit_name
            if flow_name is None:
                if (
                    current_flow is not None
                    and flow_body_depth is not None
                    and brace_depth >= flow_body_depth
                ):
                    flow_name = current_flow
                else:
                    raise SyntaxError(
                        "represent linear { ... } at top level needs a flow "
                        "name: `represent linear Name { ... }` or place the "
                        "block inside `flow Name { ... }`"
                    )

            rep = _parse_represent_linear_body(flow_name, body_lines)
            represents.append(rep)
            # Do not copy represent lines into out_lines (stripped).
            # Brace depth: the block's braces never entered the outer count
            # because we skipped via _extract_brace_block — no depth change.
            i = next_i
            continue

        # Track braces for flow-body association (skip empty/comment-only).
        if raw.strip():
            brace_depth += raw.count("{") - raw.count("}")
            if (
                current_flow is not None
                and flow_body_depth is not None
                and brace_depth < flow_body_depth
            ):
                current_flow = None
                flow_body_depth = None

        out_lines.append(raw)
        i += 1

    return represents, portraits, "\n".join(out_lines)


def parse_dynamics_dsl(source: str) -> Tuple[DynamicsProgram, str]:
    """Parse DSL constructs and return program + source with DSL blocks removed."""
    represents, portraits, source = _extract_represent_blocks(source)

    program = DynamicsProgram()
    program.represents = represents
    program.portraits = portraits
    for rep in represents:
        dsys = _represent_to_dsys(rep)
        if dsys.name in program.systems:
            raise SyntaxError(
                f"represent linear for '{rep.flow_name}' conflicts with an "
                f"existing dsys '{dsys.name}'"
            )
        program.systems[dsys.name] = dsys

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

        # Namespace block: dynamics { … } / dyn { … } — body uses bare DSL lines.
        # Use raw extraction so nested `dsys { }` / `sense { }` keep their braces
        # (the usual `_extract_brace_block` strips closing `}` and breaks re-parse).
        if re.match(r"^(?:dyn|dynamics)\s*\{", line):
            body_lines, i = _extract_brace_block_preserving(lines, i)
            body_src = "\n".join(body_lines) + "\n"
            inner_prog, leftover = parse_dynamics_dsl(body_src)
            if leftover.strip():
                raise SyntaxError(
                    "dynamics { ... } block may only contain dynamics DSL "
                    f"constructs; leftover:\n{leftover.strip()[:200]}"
                )
            _merge_dynamics_program(program, inner_prog)
            continue

        line = _strip_dynamics_namespace(line)

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
            if name in program.systems:
                raise SyntaxError(
                    f"dsys '{name}' redeclared (conflicts with a prior dsys "
                    f"or represent linear → '{name}')"
                )
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
            ga_m = re.match(
                r"analyze\s+(\w+)\s+ga\s+(\w+)\s+(\w+)\s+over\s+(\w+)\s*->\s*(\w+)\s*\{",
                line,
            )
            if ga_m:
                program.analyzes.append(
                    AnalyzeDecl(
                        ga_m.group(1),
                        ga_m.group(2),
                        ga_m.group(3),
                        ga_m.group(4),
                        ga_m.group(5),
                    )
                )
                body_lines, i = _extract_brace_block(lines, i)
                continue

            brace_m = re.match(r"analyze\s+(\w+)\s*\{", line)
            if not brace_m:
                raise SyntaxError(
                    f"Invalid analyze block: {line} "
                    "(expected `analyze Name ga k1 k2 over H -> r {{…}}` "
                    "or `analyze Name {{ lqr {{ … }} }}`)"
                )
            system = brace_m.group(1)
            body_lines, i = _extract_brace_block_preserving(lines, i)
            _parse_analyze_vision_body(program, system, body_lines)
            continue

        if line.startswith("wfc field "):
            m = re.match(r"wfc\s+field\s+(\w+)\s*\{", line)
            if not m:
                raise SyntaxError(f"Invalid wfc field block: {line}")
            wfc = WFCDecl(m.group(1))
            body_lines, i = _extract_brace_block(lines, i)
            for bl in body_lines:
                b = _strip_comments(bl)
                if b.startswith("size "):
                    parts = b.split()
                    wfc.width = int(parts[1])
                    wfc.height = int(parts[2])
                elif b.startswith("tiles "):
                    wfc.tiles = int(b.split()[1])
                elif b.startswith("seed "):
                    wfc.seed = int(b.split()[1])
                elif b.startswith("pin "):
                    parts = b.split()
                    wfc.pin_cell = int(parts[1])
                    wfc.pin_tile = int(parts[2])
                elif b.startswith("collapse "):
                    wfc.steps = int(b.split()[1])
            program.wfc_fields[wfc.name] = wfc
            continue

        if line.startswith("couple "):
            m = re.match(
                r"couple\s+(\w+)\s+field\s+(\w+)\s+using\s+(\w+)\s+(\w+)\s+(\w+)\s*\{",
                line,
            )
            if not m:
                raise SyntaxError(f"Invalid couple block: {line}")
            couple = CoupleDecl(
                m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
            )
            body_lines, i = _extract_brace_block(lines, i)
            for bl in body_lines:
                b = _strip_comments(bl)
                if "->" not in b:
                    continue
                lhs, rhs = [x.strip() for x in b.split("->", 1)]
                if lhs == "guidance":
                    couple.guidance_var = rhs
                else:
                    couple.bindings.append((lhs, rhs))
            program.couples.append(couple)
            continue

        if line.startswith("guide "):
            m = re.match(
                r"guide\s+(\w+)\s+with\s+(\w+)\s+(\w+)\s+through\s+(\w+)\s+using\s+(\w+)\s+over\s+(\w+)\s*\{",
                line,
            )
            if not m:
                raise SyntaxError(f"Invalid guide block: {line}")
            guide = GuideDecl(
                m.group(1),
                m.group(2),
                m.group(3),
                m.group(4),
                m.group(5),
                m.group(6),
            )
            body_lines, i = _extract_brace_block(lines, i)
            for bl in body_lines:
                b = _strip_comments(bl)
                if "->" not in b:
                    continue
                lhs, rhs = [x.strip() for x in b.split("->", 1)]
                guide.bindings.append((lhs, rhs))
            program.guides.append(guide)
            continue

        out_lines.append(raw)
        i += 1

    return program, "\n".join(out_lines)


def _parse_lqr_block_body(
    system: str, body_lines: List[str]
) -> AnalyzeLqrDecl:
    """Parse `lqr { Q …; R …; -> k0 k1 … }` inside `analyze Name { … }`."""
    decl = AnalyzeLqrDecl(system=system)
    for bl in body_lines:
        b = _strip_comments(bl)
        if not b:
            continue
        if b.startswith("Q "):
            decl.q_diag = _parse_floats(b[2:])
            continue
        if b.startswith("R "):
            parts = b.split()
            if len(parts) != 2:
                raise SyntaxError(
                    f"analyze {system} lqr: expected `R <scalar>`, got '{b}'"
                )
            decl.r = float(parts[1])
            continue
        if b.startswith("max_iter "):
            decl.max_iter = int(b.split()[1])
            continue
        if b.startswith("->"):
            names = b[2:].strip().split()
            if not names:
                raise SyntaxError(
                    f"analyze {system} lqr: `->` needs gain variable names"
                )
            for name in names:
                if not re.match(r"^\w+$", name):
                    raise SyntaxError(
                        f"analyze {system} lqr: invalid gain name '{name}'"
                    )
            decl.gain_vars = names
            continue
        raise SyntaxError(
            f"analyze {system} lqr: unknown item '{b}' "
            "(expected Q / R / max_iter / -> gains)"
        )
    if not decl.q_diag:
        raise SyntaxError(f"analyze {system} lqr: missing `Q …` diagonal")
    if not decl.gain_vars:
        raise SyntaxError(
            f"analyze {system} lqr: missing `-> k0 k1 …` gain bindings"
        )
    if len(decl.gain_vars) != len(decl.q_diag):
        raise SyntaxError(
            f"analyze {system} lqr: Q has {len(decl.q_diag)} entries but "
            f"-> lists {len(decl.gain_vars)} gains (need one gain per state)"
        )
    return decl


def _parse_analyze_vision_body(
    program: DynamicsProgram, system: str, body_lines: List[str]
) -> None:
    """Vision-form `analyze Name { … }` — Stage-1 ships nested `lqr { … }`."""
    i = 0
    saw_item = False
    while i < len(body_lines):
        b = _strip_comments(body_lines[i])
        if not b:
            i += 1
            continue
        if b.startswith("lqr") and "{" in b:
            # Re-join into a mini source so brace extract works on nested body.
            mini = body_lines[i:]
            # Find lqr head line index 0 in mini
            lqr_body, next_rel = _extract_brace_block(mini, 0)
            program.analyze_lqrs.append(
                _parse_lqr_block_body(system, lqr_body)
            )
            saw_item = True
            i += next_rel
            continue
        if b == "lqr":
            # `lqr` alone then `{` on next line
            if i + 1 >= len(body_lines) or "{" not in body_lines[i + 1]:
                raise SyntaxError(
                    f"analyze {system}: expected `lqr {{ … }}`"
                )
            mini = body_lines[i + 1 :]
            lqr_body, next_rel = _extract_brace_block(mini, 0)
            program.analyze_lqrs.append(
                _parse_lqr_block_body(system, lqr_body)
            )
            saw_item = True
            i = i + 1 + next_rel
            continue
        raise SyntaxError(
            f"analyze {system}: Stage-1 supports `lqr {{ … }}` only; "
            f"got '{b}'"
        )
    if not saw_item:
        raise SyntaxError(
            f"analyze {system}: empty body — add `lqr {{ Q … R … -> … }}`"
        )


def _flat_array(vals: List[float], name: str) -> str:
    inner = ", ".join(_flow_f64(v) for v in vals)
    return f"let {name}: array<f64, {max(len(vals), 1)}> = [{inner}]"


def _flow_f64(v: float) -> str:
    """Format a float literal that the Flow lexer always treats as f64."""
    s = f"{v:.17g}"
    if s.startswith("."):
        s = "0" + s
    if s.startswith("-."):
        s = "-0" + s[1:]
    if "e" not in s and "E" not in s and "." not in s:
        s += ".0"
    return s


def _zero_f64_array(size: int) -> str:
    n = max(size, 1)
    inner = ", ".join("0.0" for _ in range(n))
    return f"[{inner}]"


def _neg_one_i32_array(size: int) -> str:
    n = max(size, 1)
    inner = ", ".join("-1" for _ in range(n))
    return f"[{inner}]"


def _one_i32_array(size: int) -> str:
    n = max(size, 1)
    inner = ", ".join("1" for _ in range(n))
    return f"[{inner}]"


def compile_dynamics_program(program: DynamicsProgram) -> str:
    """Emit Flow setup code injected into main()."""
    if not any(
        [
            program.systems,
            program.wfc_fields,
            program.senses,
            program.ga_evolutions,
            program.closed_blocks,
            program.analyzes,
            program.analyze_lqrs,
            program.couples,
            program.guides,
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
        # Public alias so main can `state_step(plant, …)` without rebuilding
        # the matrices (pattern-adoption #160). Internal `__dsys_*` name stays
        # for sense/ga/closed expansion.
        if name.isidentifier() and name != var:
            lines.append(f"    let {name}: DynamicalSystem = {var}")

    for wf_name, wf in program.wfc_fields.items():
        cells_n = wf.width * wf.height
        opts_n = cells_n * wf.tiles
        grid_var = f"__wfc_{wf_name}"
        lines.append(
            f"    let {grid_var}_cells: array<i32, {cells_n}> = {_neg_one_i32_array(cells_n)}"
        )
        lines.append(
            f"    let {grid_var}_opts: array<i32, {opts_n}> = {_one_i32_array(opts_n)}"
        )
        lines.append(f"    for __wfc_i in 0 to {cells_n} {{")
        lines.append(f"        {grid_var}_cells[__wfc_i] = -1")
        lines.append("    }")
        lines.append(f"    for __wfc_j in 0 to {opts_n} {{")
        lines.append(f"        {grid_var}_opts[__wfc_j] = 1")
        lines.append("    }")
        lines.append(
            f"    {grid_var}_cells[{wf.pin_cell}] = {wf.pin_tile}"
        )
        lines.append(
            f"    let {grid_var}: WFCGrid = WFCGrid {{ width: {wf.width}, "
            f"height: {wf.height}, cells: {grid_var}_cells, "
            f"options: {grid_var}_opts }}"
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

    declared_gains: set = set()
    for gi, ga in enumerate(program.ga_evolutions):
        sysv = sys_vars[ga.system]
        steps = hz_steps.get(ga.horizon, 50)
        pop = ga.population
        tag = f"__ga_e{gi}"
        lines.append(f"    let mut {ga.k1_var}: f64 = 0.0")
        lines.append(f"    let mut {ga.k2_var}: f64 = 0.0")
        declared_gains.add(ga.k1_var)
        declared_gains.add(ga.k2_var)
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
        # Gains may be fresh names (not from a prior `ga evolve`); declare them.
        if analyze.k1_var not in declared_gains:
            lines.append(f"    let mut {analyze.k1_var}: f64 = 0.0")
            declared_gains.add(analyze.k1_var)
        if analyze.k2_var not in declared_gains:
            lines.append(f"    let mut {analyze.k2_var}: f64 = 0.0")
            declared_gains.add(analyze.k2_var)
        lines.append(f"    {analyze.k1_var} = {tag}_bk1[0]")
        lines.append(f"    {analyze.k2_var} = {tag}_bk2[0]")

    for li, lqr in enumerate(program.analyze_lqrs):
        if lqr.system not in program.systems:
            raise SyntaxError(
                f"analyze {lqr.system} lqr: unknown dsys '{lqr.system}'"
            )
        sys = program.systems[lqr.system]
        if sys.m != 1:
            raise SyntaxError(
                f"analyze {lqr.system} lqr: Stage-1 needs scalar input "
                f"(m=1), got m={sys.m}"
            )
        if len(lqr.q_diag) != sys.n:
            raise SyntaxError(
                f"analyze {lqr.system} lqr: Q length {len(lqr.q_diag)} "
                f"!= n={sys.n}"
            )
        if sys.n > 8:
            raise SyntaxError(
                f"analyze {lqr.system} lqr: n={sys.n} exceeds LQR_MAX_N=8"
            )
        sysv = sys_vars[lqr.system]
        tag = f"__lqr_{li}"
        n = sys.n
        lines.append(f"    {_flat_array(lqr.q_diag, f'{tag}_q')}")
        lines.append(
            f"    let mut {tag}_k: array<f64, {n}> = {_zero_f64_array(n)}"
        )
        # Use the (possibly Euler-discretized) plant matrices so continuous
        # dsys works the same as discrete.
        lines.append(
            f"    let {tag}_iters: i32 = dlqr_diag_q_scalar_u("
            f"{sysv}.A.data, {sysv}.B.data, {tag}_q, {_flow_f64(lqr.r)}, {n}, "
            f"{tag}_k, {lqr.max_iter})"
        )
        for gi, gname in enumerate(lqr.gain_vars):
            lines.append(f"    let {gname}: f64 = {tag}_k[{gi}]")

    for couple in program.couples:
        wf = program.wfc_fields[couple.field]
        grid_var = f"__wfc_{couple.field}"
        rep_var = f"__wfc_rep_{couple.field}"
        couple.wfc_report_var = rep_var
        lines.append(
            f"    let {couple.guidance_var}: CoupledGuidance = couple_ga_wfc_guidance("
            f"{couple.report_var}, {couple.k1_var}, {couple.k2_var}, "
            f"{wf.seed}, {wf.steps})"
        )
        lines.append(
            f"    let {rep_var}: WFCRunReport = wfc_run_guided("
            f"{grid_var}, {wf.tiles}, {couple.guidance_var})"
        )
        for lhs, var in couple.bindings:
            if lhs == "collapsed":
                lines.append(f"    let mut {var}: i32 = {rep_var}.collapsed")
            elif lhs == "wall_fraction":
                lines.append(f"    let mut {var}: f64 = {rep_var}.wall_fraction")
            elif lhs == "entropy":
                lines.append(f"    let mut {var}: f64 = {rep_var}.mean_entropy")

    for gi, guide in enumerate(program.guides):
        sysv = sys_vars[guide.system]
        steps = hz_steps.get(guide.horizon, 20)
        rep_var = f"__wfc_rep_{guide.field}"
        bufs = _bufs(3)
        ev_var = f"__guide_ev_{gi}"
        lines.append(
            f"    let {ev_var}: GuidedEvolutionReport = guide_state_evolution("
            f"{sysv}, {guide.k1_var}, {guide.k2_var}, {guide.guidance_var}, "
            f"{rep_var}, {steps}, {bufs[0]}, {bufs[1]}, {bufs[2]})"
        )
        binding_map = {
            "input_scale": f"{ev_var}.input_scale",
            "energy": f"{ev_var}.layout_energy",
            "spectral": f"{ev_var}.guided_spectral_radius",
            "stable": f"{ev_var}.stable_guided",
            "collapsed": f"{ev_var}.collapsed_cells",
        }
        for lhs, var in guide.bindings:
            if lhs in ("input_scale", "energy", "spectral"):
                lines.append(f"    let mut {var}: f64 = {binding_map[lhs]}")
            elif lhs in ("stable", "collapsed"):
                lines.append(f"    let mut {var}: i32 = {binding_map[lhs]}")
            elif lhs == "wall_fraction":
                lines.append(f"    let mut {var}: f64 = {rep_var}.wall_fraction")

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


def inject_before_main(flow_source: str, helpers: str) -> str:
    """Insert generated helpers immediately before `function main`."""
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


def _portrait_axis_project(
    decl: RepresentPhasePortraitDecl, axis: str
) -> Tuple[float, float]:
    """Return (vmin, vmax) for project_axis; invert range for row (screen y)."""
    lo, hi, kind = decl.maps[axis]
    if kind == "row":
        return hi, lo
    return lo, hi


def compile_phase_portraits(program: DynamicsProgram) -> str:
    """Emit `{Name}_portrait_frame` helpers from represent phase_portrait."""
    chunks: List[str] = []
    for p in program.portraits:
        a0_lo, a0_hi = _portrait_axis_project(p, p.axis0)
        a1_lo, a1_hi = _portrait_axis_project(p, p.axis1)
        chunks.append(
            f"# generated from represent phase_portrait for {p.flow_name}\n"
            f"const {p.flow_name}_portrait_trail: i32 = {p.trail}\n"
            f"const {p.flow_name}_portrait_win_w: i32 = {p.win_w}\n"
            f"const {p.flow_name}_portrait_win_h: i32 = {p.win_h}\n"
            f"\n"
            f"function {p.flow_name}_portrait_frame(\n"
            f"    g: Gfx,\n"
            f"    xs: ptr<f64>,\n"
            f"    zs: ptr<f64>,\n"
            f"    head: ptr<i32>,\n"
            f"    count: ptr<i32>,\n"
            f"    {p.axis0}: f64,\n"
            f"    {p.axis1}: f64\n"
            f") -> void {{\n"
            f"    trail_push_2d(xs, zs, {p.trail}, head, count, "
            f"{p.axis0}, {p.axis1})\n"
            f"    let h: i32 = head[0]\n"
            f"    let c: i32 = count[0]\n"
            f"    gfx_clear(g, 8, 8, 16)\n"
            f"    for i in 0 to c {{\n"
            f"        let idx: i32 = trail_index(h, c, {p.trail}, i)\n"
            f"        let px: i32 = project_axis(xs[idx], {a0_lo}, {a0_hi}, "
            f"{p.win_w}, {p.pad_x})\n"
            f"        let py: i32 = project_axis(zs[idx], {a1_lo}, {a1_hi}, "
            f"{p.win_h}, {p.pad_y})\n"
            f"        let b: i32 = 25 + (230 * (i + 1)) / c\n"
            f"        let mut size: i32 = 2\n"
            f"        if i >= c - 12 {{ size = 3 }}\n"
            f"        gfx_fill_rect(g, px, py, size, size, b, (b * 3) / 5, 30)\n"
            f"    }}\n"
            f"    let hx: i32 = project_axis({p.axis0}, {a0_lo}, {a0_hi}, "
            f"{p.win_w}, {p.pad_x})\n"
            f"    let hz: i32 = project_axis({p.axis1}, {a1_lo}, {a1_hi}, "
            f"{p.win_h}, {p.pad_y})\n"
            f"    gfx_fill_rect(g, hx - 1, hz - 1, 5, 5, 255, 240, 180)\n"
            f"}}\n"
        )
    return "\n".join(chunks)


def expand_dynamics_dsl(source: str) -> str:
    """Full pipeline: parse DSL blocks, compile, inject into main."""
    if not has_dynamics_dsl(source):
        return source
    program, stripped = parse_dynamics_dsl(source)
    setup = compile_dynamics_program(program)
    portraits = compile_phase_portraits(program)
    if not setup and not portraits:
        return stripped
    merged = stripped
    needs_coupling = bool(program.wfc_fields or program.couples or program.guides)
    needs_ga = bool(
        program.systems
        or program.senses
        or program.ga_evolutions
        or program.closed_blocks
        or program.analyzes
        or program.analyze_lqrs
    )
    if needs_coupling and 'import "stdlib/dynamics/wfc_ga_coupling.flow"' not in merged:
        merged = 'import "stdlib/dynamics/wfc_ga_coupling.flow"\n\n' + merged
    elif needs_ga and 'import "stdlib/dynamics/ga_analysis.flow"' not in merged:
        merged = 'import "stdlib/dynamics/ga_analysis.flow"\n\n' + merged
    if program.analyze_lqrs and 'import "stdlib/dynamics/lqr.flow"' not in merged:
        merged = 'import "stdlib/dynamics/lqr.flow"\n' + merged
    if program.portraits:
        if 'import "stdlib/dynamics/portrait.flow"' not in merged:
            merged = 'import "stdlib/dynamics/portrait.flow"\n' + merged
        if 'import "stdlib/gfx.flow"' not in merged:
            merged = 'import "stdlib/gfx.flow"\n' + merged
    if portraits:
        merged = inject_before_main(merged, portraits)
    if setup:
        merged = inject_dynamics_setup(merged, setup)
    return merged


def has_dynamics_dsl(source: str) -> bool:
    # Bare forms and namespaced `dyn.*` / `dynamics.*` / `dynamics { ... }`.
    ns = r"(?:(?:dyn|dynamics)\.)?"
    return bool(
        re.search(rf"^\s*{ns}dsys\s+\w+", source, re.MULTILINE)
        or re.search(rf"^\s*{ns}horizon\s+\w+", source, re.MULTILINE)
        or re.search(rf"^\s*{ns}sense\s+on\s+", source, re.MULTILINE)
        or re.search(rf"^\s*{ns}ga\s+evolve\s+", source, re.MULTILINE)
        or re.search(rf"^\s*{ns}closed\s+\w+", source, re.MULTILINE)
        or re.search(rf"^\s*{ns}analyze\s+\w+", source, re.MULTILINE)
        or re.search(rf"^\s*{ns}wfc\s+field\s+", source, re.MULTILINE)
        or re.search(rf"^\s*{ns}couple\s+\w+", source, re.MULTILINE)
        or re.search(rf"^\s*{ns}guide\s+\w+", source, re.MULTILINE)
        or re.search(r"^\s*(?:dyn|dynamics)\s*\{", source, re.MULTILINE)
        or re.search(r"^\s*represent\s+\w+", source, re.MULTILINE)
    )