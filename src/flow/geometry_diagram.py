#!/usr/bin/env python3
"""
Automatic geometric diagrams for Flow verification proofs.

Reads @diagram metadata or Claim Coordinates and emits SVG + TikZ figures.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from flow.proof_document import TheoremDoc


@dataclass
class Point:
    name: str
    x: float
    y: float


@dataclass
class AxesSpec:
    origin_x: float
    origin_y: float
    scale: float
    x_min: float
    x_max: float
    y_min: float
    y_max: float


@dataclass
class CurvePath:
    points: List[Tuple[float, float]]
    stroke: str = "#2980b9"
    stroke_width: float = 2.2
    dashed: bool = False
    label: str = ""


@dataclass
class FillRegion:
    polygon: List[Tuple[float, float]]
    fill: str = "#f39c12"
    opacity: float = 0.25


@dataclass
class DiagramLabel:
    x: float
    y: float
    text: str
    size: int = 14


@dataclass
class GeometryDiagram:
    title: str
    points: Dict[str, Point] = field(default_factory=dict)
    segments: List[Tuple[str, str]] = field(default_factory=list)
    angle_marks: List[Tuple[str, str, str, str]] = field(default_factory=list)
    right_angles: List[str] = field(default_factory=list)
    parallel_pairs: List[Tuple[str, str]] = field(default_factory=list)
    equal_tick_angles: List[List[str]] = field(default_factory=list)
    circles: List[Tuple[str, float]] = field(default_factory=list)
    curves: List[CurvePath] = field(default_factory=list)
    fills: List[FillRegion] = field(default_factory=list)
    labels: List[DiagramLabel] = field(default_factory=list)
    axes: Optional[AxesSpec] = None
    caption: str = ""
    width: int = 480
    height: int = 360


def fill_between_curves(
    top: List[Tuple[float, float]],
    bottom: List[Tuple[float, float]],
    color_spec: str,
) -> FillRegion:
    """Build a closed polygon between two polylines (top then bottom reversed)."""
    opacity = 0.25
    fill = color_spec
    if "@" in color_spec:
        fill, alpha = color_spec.rsplit("@", 1)
        try:
            opacity = int(alpha) / 100.0
        except ValueError:
            opacity = 0.25
    poly = list(top) + list(reversed(bottom))
    return FillRegion(polygon=poly, fill=fill, opacity=opacity)


def _pt(diag: GeometryDiagram, name: str) -> Point:
    return diag.points[name]


def _templates() -> Dict[str, GeometryDiagram]:
    """Built-in Euclidean figures keyed by @diagram id."""
    return {
        "triangle-angle-sum": GeometryDiagram(
            title="Triangle interior angles",
            points={
                "A": Point("A", 70, 290),
                "B": Point("B", 410, 290),
                "C": Point("C", 230, 70),
            },
            segments=[("A", "B"), ("B", "C"), ("C", "A")],
            angle_marks=[
                ("A", "C", "B", "α"),
                ("B", "A", "C", "β"),
                ("C", "B", "A", "γ"),
            ],
            caption="Triangle ABC — the three interior angles α, β, and γ sum to two right angles.",
        ),
        "isosceles-base-angles": GeometryDiagram(
            title="Isosceles triangle",
            points={
                "A": Point("A", 240, 60),
                "B": Point("B", 80, 300),
                "C": Point("C", 400, 300),
            },
            segments=[("A", "B"), ("A", "C"), ("B", "C")],
            angle_marks=[
                ("B", "A", "C", "θ"),
                ("C", "A", "B", "θ"),
                ("A", "B", "C", "φ"),
                ("A", "C", "B", "ψ"),
            ],
            equal_tick_angles=[["θ", "θ"], ["φ", "ψ"]],
            caption="Isosceles triangle with AB = AC — the base angles at B and C are equal.",
        ),
        "vertical-angles": GeometryDiagram(
            title="Vertical angles",
            points={
                "O": Point("O", 240, 180),
                "A": Point("A", 60, 80),
                "B": Point("B", 420, 280),
                "C": Point("C", 420, 80),
                "D": Point("D", 60, 280),
            },
            segments=[("A", "B"), ("C", "D")],
            angle_marks=[
                ("O", "A", "C", "α"),
                ("O", "C", "B", "β"),
                ("O", "B", "D", "α′"),
                ("O", "D", "A", "β′"),
            ],
            equal_tick_angles=[["α", "α′"], ["β", "β′"]],
            caption="Intersecting lines — vertical angles α and α′ are equal, as are β and β′.",
        ),
        "right-triangle-pythagoras": GeometryDiagram(
            title="Right triangle",
            points={
                "A": Point("A", 80, 300),
                "B": Point("B", 380, 300),
                "C": Point("C", 80, 80),
            },
            segments=[("A", "B"), ("B", "C"), ("C", "A")],
            right_angles=["A"],
            angle_marks=[
                ("B", "A", "C", "a"),
                ("C", "B", "A", "b"),
            ],
            caption="Right triangle with legs a, b and hypotenuse c — c² = a² + b².",
        ),
        "parallel-lines-alternate": GeometryDiagram(
            title="Parallel lines and a transversal",
            points={
                "P": Point("P", 60, 120),
                "Q": Point("Q", 420, 120),
                "R": Point("R", 40, 260),
                "S": Point("S", 440, 260),
                "T": Point("T", 120, 40),
                "U": Point("U", 360, 320),
                "X": Point("X", 200, 120),
                "Y": Point("Y", 260, 260),
            },
            segments=[("P", "Q"), ("R", "S"), ("T", "U")],
            parallel_pairs=[("PQ", "RS")],
            angle_marks=[
                ("X", "T", "P", "α"),
                ("Y", "R", "T", "α"),
                ("X", "Q", "U", "β"),
                ("Y", "S", "U", "β"),
            ],
            equal_tick_angles=[["α", "α"], ["β", "β"]],
            caption="Parallel lines cut by a transversal — alternate interior angles are equal.",
        ),
        "triangle-congruence-sas": GeometryDiagram(
            title="Side–angle–side congruence",
            points={
                "A": Point("A", 90, 280),
                "B": Point("B", 220, 280),
                "C": Point("C", 160, 100),
                "D": Point("D", 290, 280),
                "E": Point("E", 390, 280),
                "F": Point("F", 330, 100),
            },
            segments=[("A", "B"), ("B", "C"), ("C", "A"), ("D", "E"), ("E", "F"), ("F", "D")],
            angle_marks=[
                ("A", "B", "C", "θ"),
                ("D", "E", "F", "θ"),
            ],
            equal_tick_angles=[["θ", "θ"]],
            caption="Two triangles with two sides and the included angle equal — the triangles are congruent.",
        ),
        "thales-right-angle": GeometryDiagram(
            title="Thales' theorem",
            points={
                "O": Point("O", 240, 200),
                "A": Point("A", 100, 200),
                "B": Point("B", 380, 200),
                "C": Point("C", 240, 70),
            },
            circles=[("O", 130)],
            segments=[("A", "B"), ("A", "C"), ("B", "C")],
            right_angles=["C"],
            angle_marks=[
                ("C", "A", "B", "θ"),
            ],
            caption="Angle in a semicircle — when AB is a diameter, the inscribed angle at C is a right angle.",
        ),
        "circle-radii-equal": GeometryDiagram(
            title="Radii of a circle",
            points={
                "O": Point("O", 240, 180),
                "A": Point("A", 100, 220),
                "B": Point("B", 380, 140),
            },
            circles=[("O", 130)],
            segments=[("O", "A"), ("O", "B")],
            equal_tick_angles=[],
            caption="Circle with centre O — radii OA and OB are equal.",
        ),
        "inscribed-angle-half-central": GeometryDiagram(
            title="Inscribed and central angles",
            points={
                "O": Point("O", 240, 190),
                "A": Point("A", 110, 250),
                "B": Point("B", 370, 250),
                "P": Point("P", 240, 55),
            },
            circles=[("O", 135)],
            segments=[("O", "A"), ("O", "B"), ("P", "A"), ("P", "B")],
            angle_marks=[
                ("O", "A", "B", "2θ"),
                ("P", "A", "B", "θ"),
            ],
            caption="Inscribed angle θ at P equals half the central angle 2θ subtending arc AB.",
        ),
    }


def _infer_diagram_id(thm: "TheoremDoc") -> Optional[str]:
    law = thm.claim_path.lower()
    if "interior angles" in law or "angle-sum" in law or "two right" in law:
        return "triangle-angle-sum"
    if "isosceles" in law or "base angles" in law:
        return "isosceles-base-angles"
    if "vertical" in law:
        return "vertical-angles"
    if "pythagoras" in law or "hypotenuse" in law:
        return "right-triangle-pythagoras"
    if "alternate" in law:
        return "parallel-lines-alternate"
    if "side-angle-side" in law or "congruence" in law:
        return "triangle-congruence-sas"
    if "thales" in law or "semicircle" in law:
        return "thales-right-angle"
    if "inscribed" in law:
        return "inscribed-angle-half-central"
    return None


def diagram_for_theorem(
    thm: "TheoremDoc",
    *,
    flow_file_dir: Optional[str] = None,
) -> Optional[GeometryDiagram]:
    script = getattr(thm.meta, "diagram_script", "") or ""
    if script.strip():
        from flow.geometry_script import load_script_for_theorem

        return load_script_for_theorem(script, flow_file_dir=flow_file_dir)
    key = getattr(thm.meta, "diagram", "") or ""
    templates = _templates()
    if key and key in templates:
        return templates[key]
    inferred = _infer_diagram_id(thm)
    if inferred and inferred in templates:
        return templates[inferred]
    if "taylor" in thm.claim_path.lower() or "maclaurin" in thm.claim_path.lower():
        from flow.geometry_script import load_script_for_theorem

        return load_script_for_theorem(
            "taylor-sin.geom", flow_file_dir=flow_file_dir
        )
    return None


def _unit(vx: float, vy: float) -> Tuple[float, float]:
    m = math.hypot(vx, vy) or 1.0
    return vx / m, vy / m


def _angle_arc_path(
    vertex: Point,
    arm1: Point,
    arm2: Point,
    radius: float = 28,
) -> str:
    a1 = math.atan2(arm1.y - vertex.y, arm1.x - vertex.x)
    a2 = math.atan2(arm2.y - vertex.y, arm2.x - vertex.x)
    da = (a2 - a1) % (2 * math.pi)
    if da > math.pi:
        a1, a2 = a2, a1
        da = (a2 - a1) % (2 * math.pi)
    sx = vertex.x + radius * math.cos(a1)
    sy = vertex.y + radius * math.sin(a1)
    ex = vertex.x + radius * math.cos(a2)
    ey = vertex.y + radius * math.sin(a2)
    large = 1 if da > math.pi else 0
    return (
        f"M {sx:.1f} {sy:.1f} A {radius:.1f} {radius:.1f} 0 {large} 1 "
        f"{ex:.1f} {ey:.1f}"
    )


def _label_offset(vertex: Point, arm1: Point, arm2: Point, dist: float = 42) -> Tuple[float, float]:
    u1x, u1y = _unit(arm1.x - vertex.x, arm1.y - vertex.y)
    u2x, u2y = _unit(arm2.x - vertex.x, arm2.y - vertex.y)
    bx, by = u1x + u2x, u1y + u2y
    ux, uy = _unit(bx, by)
    return vertex.x + ux * dist, vertex.y + uy * dist


def _right_angle_marker(vertex: Point, arm1: Point, arm2: Point, size: float = 14) -> str:
    u1x, u1y = _unit(arm1.x - vertex.x, arm1.y - vertex.y)
    u2x, u2y = _unit(arm2.x - vertex.x, arm2.y - vertex.y)
    p1x, p1y = vertex.x + u1x * size, vertex.y + u1y * size
    p2x, p2y = vertex.x + u2x * size, vertex.y + u2y * size
    p3x = p1x + u2x * size
    p3y = p1y + u2y * size
    return f"M {p1x:.1f} {p1y:.1f} L {p3x:.1f} {p3y:.1f} L {p2x:.1f} {p2y:.1f}"


def _svg_polyline(points: List[Tuple[float, float]]) -> str:
    if not points:
        return ""
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def _render_axes_svg(ax: AxesSpec) -> List[str]:
    lines: List[str] = []
    x0 = ax.origin_x + ax.x_min * ax.scale
    x1 = ax.origin_x + ax.x_max * ax.scale
    y0 = ax.origin_y - ax.y_min * ax.scale
    y1 = ax.origin_y - ax.y_max * ax.scale
    ox, oy = ax.origin_x, ax.origin_y
    lines.append(
        f'<line x1="{x0:.1f}" y1="{oy:.1f}" x2="{x1:.1f}" y2="{oy:.1f}" '
        f'stroke="#bdc3c7" stroke-width="1.2"/>'
    )
    lines.append(
        f'<line x1="{ox:.1f}" y1="{y0:.1f}" x2="{ox:.1f}" y2="{y1:.1f}" '
        f'stroke="#bdc3c7" stroke-width="1.2"/>'
    )
    lines.append(
        f'<text x="{x1 - 8:.1f}" y="{oy + 16:.1f}" font-size="12" fill="#7f8c8d">x</text>'
    )
    lines.append(
        f'<text x="{ox + 6:.1f}" y="{y1 + 4:.1f}" font-size="12" fill="#7f8c8d">y</text>'
    )
    return lines


def render_svg(diagram: GeometryDiagram) -> str:
    lines: List[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {diagram.width} {diagram.height}" '
        f'width="{diagram.width}" height="{diagram.height}">',
        '<style>text{font-family:Georgia,serif;font-size:15px;fill:#1a1a1a}</style>',
        '<rect width="100%" height="100%" fill="#faf9f6"/>',
    ]

    if diagram.axes:
        lines.extend(_render_axes_svg(diagram.axes))

    for region in diagram.fills:
        pts = _svg_polyline(region.polygon)
        lines.append(
            f'<polygon points="{pts}" fill="{region.fill}" '
            f'fill-opacity="{region.opacity:.2f}" stroke="none"/>'
        )

    for curve in diagram.curves:
        pts = _svg_polyline(curve.points)
        dash = ' stroke-dasharray="7 5"' if curve.dashed else ""
        lines.append(
            f'<polyline points="{pts}" fill="none" stroke="{curve.stroke}" '
            f'stroke-width="{curve.stroke_width:.1f}" stroke-linecap="round"'
            f'{dash}/>'
        )
        if curve.label and curve.points:
            lx, ly = curve.points[len(curve.points) // 3]
            lines.append(
                f'<text x="{lx:.1f}" y="{ly - 8:.1f}" font-size="12" '
                f'fill="{curve.stroke}">{_svg_escape(curve.label)}</text>'
            )

    for center, radius in diagram.circles:
        c = _pt(diagram, center)
        lines.append(
            f'<circle cx="{c.x:.1f}" cy="{c.y:.1f}" r="{radius:.1f}" '
            f'fill="none" stroke="#95a5a6" stroke-width="1.8"/>'
        )

    for a, b in diagram.segments:
        p1, p2 = _pt(diagram, a), _pt(diagram, b)
        lines.append(
            f'<line x1="{p1.x:.1f}" y1="{p1.y:.1f}" x2="{p2.x:.1f}" y2="{p2.y:.1f}" '
            f'stroke="#2c3e50" stroke-width="2.2" stroke-linecap="round"/>'
        )

    for pair in diagram.parallel_pairs:
        for label in pair:
            if len(label) < 2:
                continue
            p1 = _pt(diagram, label[0])
            p2 = _pt(diagram, label[1])
            mx, my = (p1.x + p2.x) / 2, (p1.y + p2.y) / 2
            ux, uy = _unit(p2.x - p1.x, p2.y - p1.y)
            px, py = -uy, ux
            for offset in (-12, 12):
                cx, cy = mx + ux * offset, my + uy * offset
                lines.append(
                    f'<line x1="{cx + px * 6:.1f}" y1="{cy + py * 6:.1f}" '
                    f'x2="{cx - px * 6:.1f}" y2="{cy - py * 6:.1f}" '
                    f'stroke="#7f8c8d" stroke-width="1.4"/>'
                )

    for vertex, arm1n, arm2n, label in diagram.angle_marks:
        v = _pt(diagram, vertex)
        a1 = _pt(diagram, arm1n)
        a2 = _pt(diagram, arm2n)
        path = _angle_arc_path(v, a1, a2)
        lines.append(
            f'<path d="{path}" fill="none" stroke="#c0392b" stroke-width="1.6"/>'
        )
        lx, ly = _label_offset(v, a1, a2)
        lines.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle">{label}</text>')

    for vertex in diagram.right_angles:
        v = _pt(diagram, vertex)
        arms = [b for a, b in diagram.segments if a == vertex] + [
            a for a, b in diagram.segments if b == vertex
        ]
        if len(arms) >= 2:
            a1, a2 = _pt(diagram, arms[0]), _pt(diagram, arms[1])
            path = _right_angle_marker(v, a1, a2)
            lines.append(
                f'<path d="{path}" fill="none" stroke="#2c3e50" stroke-width="1.5"/>'
            )

    for lab in diagram.labels:
        lines.append(
            f'<text x="{lab.x:.1f}" y="{lab.y:.1f}" text-anchor="middle" '
            f'font-size="{lab.size}" fill="#2c3e50">{_svg_escape(lab.text)}</text>'
        )

    for name, p in diagram.points.items():
        lines.append(f'<circle cx="{p.x:.1f}" cy="{p.y:.1f}" r="4.5" fill="#2c3e50"/>')
        ox, oy = 0, -14
        if p.y < 120:
            oy = 20
        lines.append(
            f'<text x="{p.x + ox:.1f}" y="{p.y + oy:.1f}" '
            f'text-anchor="middle" font-weight="bold">{name}</text>'
        )

    if diagram.caption:
        lines.append(
            f'<text x="{diagram.width / 2:.0f}" y="{diagram.height - 16:.0f}" '
            f'text-anchor="middle" font-size="13" fill="#555">{_svg_escape(diagram.caption)}</text>'
        )

    lines.append("</svg>")
    return "\n".join(lines)


def _svg_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _collect_hex_colors(diagram: GeometryDiagram) -> dict[str, str]:
    """Map #RRGGBB hex colors to LaTeX-safe geomcN names."""
    color_map: dict[str, str] = {}
    for region in diagram.fills:
        if region.fill.startswith("#") and region.fill not in color_map:
            color_map[region.fill] = f"geomc{len(color_map)}"
    for curve in diagram.curves:
        if curve.stroke.startswith("#") and curve.stroke not in color_map:
            color_map[curve.stroke] = f"geomc{len(color_map)}"
    return color_map


def _tikz_color(color: str, color_map: dict[str, str]) -> str:
    if color.startswith("#"):
        return color_map[color]
    return color


def render_tikz(diagram: GeometryDiagram) -> str:
    """TikZ snippet for LaTeX proof documents."""
    color_map = _collect_hex_colors(diagram)
    lines = [
        r"\begin{center}",
        r"\begin{tikzpicture}[scale=0.035, line cap=round, line join=round]",
    ]
    for hex_color, name in color_map.items():
        lines.append(f"  \\definecolor{{{name}}}{{HTML}}{{{hex_color[1:]}}}")
    lines.append(
        rf"  \fill[fill=gray!4] (-10,-10) rectangle ({diagram.width + 20},{diagram.height + 10});"
    )

    if diagram.axes:
        ax = diagram.axes
        x0 = ax.origin_x + ax.x_min * ax.scale
        x1 = ax.origin_x + ax.x_max * ax.scale
        y0 = diagram.height - (ax.origin_y - ax.y_min * ax.scale)
        y1 = diagram.height - (ax.origin_y - ax.y_max * ax.scale)
        oy = diagram.height - ax.origin_y
        lines.append(f"  \\draw[gray!60] ({x0:.1f},{oy:.1f}) -- ({x1:.1f},{oy:.1f});")
        lines.append(
            f"  \\draw[gray!60] ({ax.origin_x:.1f},{y0:.1f}) -- ({ax.origin_x:.1f},{y1:.1f});"
        )

    for region in diagram.fills:
        coords = " ".join(
            f"({x:.1f},{diagram.height - y:.1f})" for x, y in region.polygon
        )
        fill = _tikz_color(region.fill, color_map)
        lines.append(
            f"  \\fill[fill={fill}, opacity={region.opacity:.2f}] {coords} -- cycle;"
        )

    for name, p in diagram.points.items():
        lines.append(
            f"  \\coordinate ({name}) at ({p.x:.1f},{diagram.height - p.y:.1f});"
        )

    for center, radius in diagram.circles:
        lines.append(f"  \\draw[gray] ({center}) circle ({radius:.1f});")

    for a, b in diagram.segments:
        lines.append(f"  \\draw[thick] ({a}) -- ({b});")

    for pair in diagram.parallel_pairs:
        for label in pair:
            if len(label) < 2:
                continue
            p1 = _pt(diagram, label[0])
            p2 = _pt(diagram, label[1])
            mx = (p1.x + p2.x) / 2
            my = diagram.height - (p1.y + p2.y) / 2
            ux, uy = _unit(p2.x - p1.x, p2.y - p1.y)
            px, py = -uy, ux
            for offset in (-12, 12):
                cx = mx + ux * offset
                cy = my + uy * offset
                lines.append(
                    f"  \\draw[gray] ({cx + px * 6:.1f},{cy + py * 6:.1f}) -- "
                    f"({cx - px * 6:.1f},{cy - py * 6:.1f});"
                )

    for vertex in diagram.right_angles:
        arms = [b for seg_a, b in diagram.segments if seg_a == vertex] + [
            a for a, seg_b in diagram.segments if seg_b == vertex
        ]
        if len(arms) >= 2:
            a1, a2 = arms[0], arms[1]
            lines.append(
                f"  \\pic [draw, angle radius=3.5mm] {{right angle = {a1}--{vertex}--{a2}}};"
            )

    for vertex, arm1n, arm2n, label in diagram.angle_marks:
        tex_label = _angle_label_tex(label)
        lines.append(
            f"  \\pic [draw, angle radius=5mm, \"{tex_label}\"] "
            f"{{angle = {arm1n}--{vertex}--{arm2n}}};"
        )

    for curve in diagram.curves:
        coords = " ".join(
            f"({x:.1f},{diagram.height - y:.1f})" for x, y in curve.points
        )
        style = "dashed, thick" if curve.dashed else "thick"
        stroke = _tikz_color(curve.stroke, color_map)
        lines.append(f"  \\draw[{style}, draw={stroke}] plot[smooth] coordinates {{{coords}}};")
        if curve.label and curve.points:
            lx, ly = curve.points[len(curve.points) // 3]
            lines.append(
                f"  \\node[font=\\scriptsize, text={stroke}] "
                f"at ({lx:.1f},{diagram.height - ly:.1f}) {{{_latex_escape(curve.label)}}};"
            )

    for lab in diagram.labels:
        lines.append(
            f"  \\node[font=\\small] at ({lab.x:.1f},{diagram.height - lab.y:.1f}) "
            f"{{{_latex_escape(lab.text)}}};"
        )

    for name, p in diagram.points.items():
        lines.append(f"  \\fill ({name}) circle (6pt);")
        oy = -14 if p.y >= 120 else 20
        lines.append(
            f"  \\node[font=\\bfseries] at ($( {name} ) + (0,{oy:.0f})$) {{{name}}};"
        )

    if diagram.caption:
        lines.append(
            r"  \node[below, text width=14cm, align=center, font=\small] "
            rf"at (240,20) {{{_latex_escape(diagram.caption)}}};"
        )
    lines.extend([r"\end{tikzpicture}", r"\end{center}"])
    return "\n".join(lines)


def _angle_label_tex(label: str) -> str:
    mapping = {
        "α": r"$\alpha$",
        "β": r"$\beta$",
        "γ": r"$\gamma$",
        "θ": r"$\theta$",
        "φ": r"$\varphi$",
        "ψ": r"$\psi$",
        "α′": r"$\alpha'$",
        "β′": r"$\beta'$",
        "2θ": r"$2\theta$",
        "a": r"$a$",
        "b": r"$b$",
    }
    return mapping.get(label, _latex_escape(label))


def _latex_escape(text: str) -> str:
    repl = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "_": r"\_"}
    out = text
    for a, b in repl.items():
        out = out.replace(a, b)
    return out


def write_diagram_artifacts(
    thm: "TheoremDoc",
    out_dir: Path,
    stem: str,
    *,
    index: int = 0,
    total: int = 1,
    flow_file_dir: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """Write .proof.svg and .proof-diagram.tex for one theorem. Returns paths."""
    diag = diagram_for_theorem(thm, flow_file_dir=flow_file_dir)
    if not diag:
        return None, None

    suffix = "" if total == 1 else f"-{index + 1}"
    svg_path = out_dir / f"{stem}{suffix}.proof.svg"
    tex_path = out_dir / f"{stem}{suffix}.proof-diagram.tex"
    svg_path.write_text(render_svg(diag), encoding="utf-8")
    tex_path.write_text(render_tikz(diag) + "\n", encoding="utf-8")
    return str(svg_path), str(tex_path)


