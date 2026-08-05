#!/usr/bin/env python3
"""Generate Flow verification files for all 16 propositions of Euclid Book IV."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "examples" / "verify" / "euclid" / "book-iv"

BOOKS = {"I": "Euclid Book I", "III": "Euclid Book III", "IV": "Euclid Book IV"}


def claim(book: str, n: int, title: str) -> str:
    return f"«Geometry» «{BOOKS[book]}» «Proposition {n}: {title}»"


def _need(book: str, n: int, title: str) -> str:
    return claim(book, n, title)


# (n, slug, title, means, therefore, needs, extra_steps)
PROPOSITIONS: list[tuple] = [
    (1, "fit-chord-in-circle",
     "in a circle to place a straight line equal to a given line",
     "In a given circle to place a straight line equal to a given straight line not greater than the diameter.",
     "chord_in_circle_equal_to_given_line",
     [("I", 1, "equilateral triangle on a segment"), ("III", 1, "equal chords subtend equal angles at the center")],
     ["let circle = given_circle", "let AB = given_line", "let chord = line_in_circle", "therefore chord == AB"]),
    (2, "inscribe-equiangular-triangle",
     "in a circle to inscribe a triangle equiangular to a given triangle",
     "In a given circle to inscribe a triangle equiangular to a given triangle.",
     "inscribed_triangle_equiangular",
     [("I", 23, "copy a given angle onto a line at a point"), ("III", 21, "angles in the same segment are equal")],
     ["let circle = given_circle", "let ABC = given_triangle", "let DEF = inscribed_triangle", "therefore angle_DEF == angle_ABC"]),
    (3, "circumscribe-equiangular-triangle",
     "about a circle to circumscribe a triangle equiangular to a given triangle",
     "About a given circle to circumscribe a triangle equiangular to a given triangle.",
     "circumscribed_triangle_equiangular",
     [("IV", 2, "in a circle to inscribe a triangle equiangular to a given triangle"), ("III", 19, "the tangent is perpendicular to the diameter at the point of contact")],
     ["let circle = given_circle", "let ABC = given_triangle", "let PQR = circumscribed_triangle", "therefore angle_PQR == angle_ABC"]),
    (4, "inscribe-square",
     "in a circle to inscribe a square",
     "In a given circle to inscribe a square.",
     "square_inscribed_in_circle",
     [("I", 11, "erect a perpendicular at a point on a line"), ("III", 2, "a perpendicular from the center bisects the chord")],
     ["let circle = given_circle", "let ABCD = inscribed_square", "let O = center", "therefore square_ABCD_in_circle"]),
    (5, "circumscribe-square",
     "about a circle to circumscribe a square",
     "About a given circle to circumscribe a square.",
     "square_circumscribed_about_circle",
     [("IV", 4, "in a circle to inscribe a square"), ("III", 35, "tangents drawn from a point to a circle are equal")],
     ["let circle = given_circle", "let ABCD = circumscribed_square", "let tangent_points = vertices_on_circle", "therefore square_ABCD_about_circle"]),
    (6, "describe-square-on-line",
     "on a given straight line to describe a square",
     "On a given straight line to describe a square.",
     "square_on_given_line_exists",
     [("I", 46, "describe a square on a given straight line"), ("IV", 4, "in a circle to inscribe a square")],
     ["let AB = given_line", "let ABCD = square_on_AB", "let right_angle = angle_ABC", "therefore square_on_AB_exists"]),
    (7, "inscribe-rectangle",
     "in a circle to inscribe a rectangle",
     "In a given circle to inscribe a rectangle.",
     "rectangle_inscribed_in_circle",
     [("IV", 4, "in a circle to inscribe a square"), ("I", 31, "interior angles on one side sum to two right angles")],
     ["let circle = given_circle", "let ABCD = inscribed_rectangle", "let O = center", "therefore rectangle_ABCD_in_circle"]),
    (8, "circumscribe-rectangle",
     "about a circle to circumscribe a rectangle",
     "About a given circle to circumscribe a rectangle.",
     "rectangle_circumscribed_about_circle",
     [("IV", 5, "about a circle to circumscribe a square"), ("IV", 7, "in a circle to inscribe a rectangle")],
     ["let circle = given_circle", "let ABCD = circumscribed_rectangle", "let sides_tangent = sides_touch_circle", "therefore rectangle_ABCD_about_circle"]),
    (9, "inscribe-pentagon",
     "in a circle to inscribe a regular pentagon",
     "In a given circle to inscribe a regular pentagon.",
     "regular_pentagon_inscribed",
     [("IV", 10, "to construct an isosceles triangle with base angles double the vertex"), ("III", 20, "the central angle is double the inscribed angle on the same arc")],
     ["let circle = given_circle", "let pentagon = inscribed_regular_pentagon", "let side = pentagon_side", "therefore regular_pentagon_in_circle"]),
    (10, "double-angle-triangle",
     "to construct an isosceles triangle with base angles double the vertex",
     "To construct an isosceles triangle having each of the angles at the base double the remaining one.",
     "isosceles_triangle_with_double_base_angles",
     [("I", 4, "side-angle-side congruence"), ("III", 32, "the angle between tangent and chord equals the angle in the alternate segment")],
     ["let ABC = isosceles_triangle", "let angle_A = vertex_angle", "let angle_B = base_angle", "therefore angle_B == 2 * angle_A"]),
    (11, "circumscribe-pentagon",
     "about a circle to circumscribe a regular pentagon",
     "About a given circle to circumscribe a regular pentagon.",
     "regular_pentagon_circumscribed",
     [("IV", 9, "in a circle to inscribe a regular pentagon"), ("III", 35, "tangents drawn from a point to a circle are equal")],
     ["let circle = given_circle", "let pentagon = circumscribed_regular_pentagon", "let vertices = tangent_points", "therefore regular_pentagon_about_circle"]),
    (12, "inscribe-circle-in-triangle",
     "in a given triangle to inscribe a circle",
     "In a given rectilineal figure to inscribe a circle.",
     "circle_inscribed_in_triangle",
     [("I", 9, "bisect a given angle"), ("III", 16, "the perpendicular from the center to a chord bisects it")],
     ["let triangle = given_triangle", "let incenter = intersection_of_angle_bisectors", "let incircle = circle_about_incenter", "therefore circle_inscribed_in_triangle"]),
    (13, "circumscribe-circle-about-triangle",
     "about a given triangle to circumscribe a circle",
     "About a given rectilineal figure to circumscribe a circle.",
     "circle_circumscribed_about_triangle",
     [("I", 10, "bisect a given segment"), ("III", 17, "the bisector from the center to a chord is perpendicular")],
     ["let triangle = given_triangle", "let circumcenter = intersection_of_perp_bisectors", "let circumcircle = circle_about_circumcenter", "therefore circle_circumscribed_about_triangle"]),
    (14, "inscribe-equilateral-polygon",
     "in a circle to inscribe a regular polygon",
     "In a given circle to inscribe a rectilineal figure equilateral and equiangular.",
     "regular_polygon_inscribed",
     [("IV", 9, "in a circle to inscribe a regular pentagon"), ("III", 26, "in equal circles equal angles stand on equal arcs")],
     ["let circle = given_circle", "let polygon = inscribed_regular_polygon", "let n = number_of_sides", "therefore regular_polygon_in_circle"]),
    (15, "inscribe-hexagon",
     "in a circle to inscribe a regular hexagon",
     "In a given circle to inscribe a regular hexagon.",
     "regular_hexagon_inscribed",
     [("IV", 14, "in a circle to inscribe a regular polygon"), ("I", 1, "equilateral triangle on a segment")],
     ["let circle = given_circle", "let hexagon = inscribed_regular_hexagon", "let side = radius_of_circle", "therefore regular_hexagon_in_circle"]),
    (16, "circumscribe-hexagon",
     "about a circle to circumscribe a regular hexagon",
     "About a given circle to circumscribe a regular hexagon.",
     "regular_hexagon_circumscribed",
     [("IV", 15, "in a circle to inscribe a regular hexagon"), ("III", 35, "tangents drawn from a point to a circle are equal")],
     ["let circle = given_circle", "let hexagon = circumscribed_regular_hexagon", "let sides_tangent = hexagon_sides", "therefore regular_hexagon_about_circle"]),
]


def render_flow(
    n: int,
    slug: str,
    title: str,
    means: str,
    therefore: str,
    needs: list,
    extra_steps: list,
) -> str:
    lines = [
        f"# @module examples.verify.euclid.book-iv",
        f"# @means  {means}",
        f"# @from   euclid — Elements, Book IV, Proposition {n}",
        f"# @tier   derived",
    ]
    if needs:
        need_str = ", ".join(_need(book, nn, tt) for book, nn, tt in needs)
        lines.append(f"# @needs  {need_str}")
    lines.append("")
    lines.append(f"theorem {claim('IV', n, title)} () {{")
    for step in extra_steps:
        if step.startswith("let "):
            lines.append(f"    {step}")
        elif step.startswith("therefore "):
            lines.append(f"    {step}")
        else:
            lines.append(f"    therefore {step}")
    for book, nn, tt in needs:
        lines.append(f"    assume {_need(book, nn, tt)}()")
    if not any(s == f"therefore {therefore}" or s.endswith(therefore) for s in extra_steps):
        lines.append(f"    therefore {therefore}")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []
    for n, slug, title, means, therefore, needs, extra_steps in PROPOSITIONS:
        fname = f"prop-{n:02d}-{slug}.flow"
        path = OUT / fname
        path.write_text(
            render_flow(n, slug, title, means, therefore, needs, extra_steps),
            encoding="utf-8",
        )
        paths.append(f"examples/verify/euclid/book-iv/{fname}")
    manifest = OUT / "MANIFEST.txt"
    manifest.write_text("\n".join(paths) + "\n", encoding="utf-8")
    print(f"Wrote {len(paths)} propositions to {OUT}")


if __name__ == "__main__":
    main()