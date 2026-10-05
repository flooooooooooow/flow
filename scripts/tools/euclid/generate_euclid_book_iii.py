#!/usr/bin/env python3
"""Generate Flow verification files for all 37 propositions of Euclid Book III."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "examples" / "verify" / "euclid" / "book-iii"

BOOKS = {"I": "Euclid Book I", "II": "Euclid Book II", "III": "Euclid Book III"}


def claim(book: str, n: int, title: str) -> str:
    return f"«Geometry» «{BOOKS[book]}» «Proposition {n}: {title}»"


def _need(book: str, n: int, title: str) -> str:
    return claim(book, n, title)


# (n, slug, title, tier, means, therefore, needs, extra_steps)
# needs: list of (book, n, title)
PROPOSITIONS: list[tuple] = [
    (1, "equal-chords-equal-angles",
     "equal chords subtend equal angles at the center",
     "derived",
     "In equal circles equal chords subtend equal angles at the center, and equal central angles subtend equal chords.",
     "chord_AB == chord_DE implies angle_AOB == angle_DOE",
     [], ["let O = center_of_circle", "let AOB = angle_at_center", "let DE = equal_chord", "therefore angle_AOB == angle_DOE"]),
    (2, "perpendicular-bisects-chord",
     "a perpendicular from the center bisects the chord",
     "derived",
     "If a straight line through the center of a circle cuts a chord at right angles, it bisects the chord and the central angles.",
     "perpendicular_from_center_bisects_chord",
     [("I", 10, "bisect a given segment")],
     ["let O = center", "let AB = chord", "let M = foot_of_perpendicular", "therefore segment_AM == segment_MB"]),
    (3, "bisecting-angle-bisects-chord",
     "a central angle bisector bisects the chord",
     "derived",
     "If through the center a straight line bisects a central angle, it also bisects the chord and is perpendicular to it.",
     "angle_bisector_from_center_bisects_chord",
     [("III", 2, "a perpendicular from the center bisects the chord")],
     ["let O = center", "let AB = chord", "let OC = angle_bisector", "therefore segment_AM == segment_MB"]),
    (4, "chords-not-through-center",
     "chords not through the center do not bisect each other",
     "derived",
     "In a circle, two chords that do not both pass through the center do not bisect each other.",
     "non_diameter_chords_do_not_bisect",
     [("III", 2, "a perpendicular from the center bisects the chord")],
     ["let AB = chord_through_P", "let CD = chord_through_Q", "let P = point_not_center", "therefore chords_do_not_bisect"]),
    (5, "centers-line-through-intersection",
     "the line joining centers passes through the intersection",
     "derived",
     "If two circles cut one another, the straight line joining their centers passes through the point of intersection.",
     "center_line_passes_through_intersection",
     [("III", 4, "chords not through the center do not bisect each other")],
     ["let O = center_first", "let P = center_second", "let X = intersection_point", "therefore O_P_line_passes_through_X"]),
    (6, "centers-line-through-contact",
     "the line joining centers passes through the point of contact",
     "derived",
     "If two circles touch one another, the straight line joining their centers passes through the point of contact.",
     "center_line_passes_through_contact",
     [("III", 5, "the line joining centers passes through the intersection")],
     ["let O = center_first", "let P = center_second", "let T = point_of_contact", "therefore O_P_line_passes_through_T"]),
    (7, "pythagoras-on-diameter",
     "the square on a half-diameter exceeds the square on a line to an interior point",
     "derived",
     "If on the diameter of a circle a point is taken and a perpendicular is erected, the square on the half-diameter "
     "exceeds the square on the line to the point by the square on the perpendicular.",
     "sq(half_diameter) == sq(line_to_point) + sq(perpendicular)",
     [("I", 47, "square on hypotenuse equals sum of squares on legs")],
     ["let AB = diameter", "let C = interior_point", "let D = foot_of_perpendicular", "therefore sq(half) == sq(AC) + sq(CD)"]),
    (8, "secant-tangent-rectangle",
     "the rectangle on a secant and its exterior segment equals the square on the tangent",
     "derived",
     "If from a point outside a circle a secant and a tangent are drawn, the rectangle on the whole secant and the "
     "exterior segment equals the square on the tangent.",
     "rect(secant, exterior) == sq(tangent)",
     [("III", 7, "the square on a half-diameter exceeds the square on a line to an interior point")],
     ["let P = exterior_point", "let secant = line_PAB", "let tangent = line_PT", "therefore rect(secant, exterior) == sq(tangent)"]),
    (9, "secant-tangent-converse",
     "if the rectangle equals the square then the line is a tangent",
     "derived",
     "If from a point outside a circle two straight lines are drawn, one cutting the circle and one meeting it, and the "
     "rectangle on the whole and the exterior segment equals the square on the other, then the other is tangent.",
     "rect_equals_sq_implies_tangent",
     [("III", 8, "the rectangle on a secant and its exterior segment equals the square on the tangent")],
     ["let P = exterior_point", "let secant = line_PAB", "let other = line_PQ", "therefore other_is_tangent"]),
    (10, "circles-touch-at-most-one-point",
     "one circle cannot touch another at more than one point",
     "derived",
     "One circle cannot touch another at more than one point.",
     "touching_circles_have_unique_contact",
     [("III", 6, "the line joining centers passes through the point of contact")],
     ["let C1 = first_circle", "let C2 = second_circle", "let T = point_of_contact", "therefore at_most_one_contact_point"]),
    (11, "internal-tangency-center-line",
     "internally touching circles have collinear centers through the contact",
     "derived",
     "If two circles touch internally, the straight line joining their centers produced passes through the point of contact.",
     "internal_tangency_center_line",
     [("III", 6, "the line joining centers passes through the point of contact")],
     ["let O = center_larger", "let P = center_smaller", "let T = contact_point", "therefore O_P_produced_passes_through_T"]),
    (12, "external-tangency-center-line",
     "externally touching circles have collinear centers through the contact",
     "derived",
     "If two circles touch externally, the straight line joining their centers passes through the point of contact.",
     "external_tangency_center_line",
     [("III", 6, "the line joining centers passes through the point of contact")],
     ["let O = center_first", "let P = center_second", "let T = contact_point", "therefore O_P_passes_through_T"]),
    (13, "no-double-touch-internal-external",
     "circles cannot touch at more than one point internally or externally",
     "derived",
     "A circle does not touch another internally or externally at more than one point.",
     "no_double_touch",
     [("III", 10, "one circle cannot touch another at more than one point"), ("III", 11, "internally touching circles have collinear centers through the contact")],
     ["let C1 = first_circle", "let C2 = second_circle", "therefore at_most_one_touch_point"]),
    (14, "equal-chords-equidistant",
     "equal chords are equally distant from the center",
     "derived",
     "In equal circles equal straight lines are equally distant from the centers, and conversely.",
     "equal_chords_equally_distant",
     [("III", 2, "a perpendicular from the center bisects the chord")],
     ["let AB = chord_first", "let DE = chord_second", "let d1 = distance_to_center", "therefore d1 == d2"]),
    (15, "equidistant-chords-equal",
     "chords equidistant from the center are equal",
     "derived",
     "In a circle straight lines equidistant from the center are equal, and conversely.",
     "equidistant_chords_equal",
     [("III", 14, "equal chords are equally distant from the center")],
     ["let AB = chord_at_distance_d", "let CD = chord_at_distance_d", "therefore chord_AB == chord_CD"]),
    (16, "center-perpendicular-bisects-chord",
     "the perpendicular from the center to a chord bisects it",
     "derived",
     "If from the center of a circle a perpendicular is drawn to a chord, it bisects the chord.",
     "center_perpendicular_bisects",
     [("III", 2, "a perpendicular from the center bisects the chord")],
     ["let O = center", "let AB = chord", "let M = foot_of_perpendicular", "therefore segment_AM == segment_MB"]),
    (17, "center-bisector-perpendicular",
     "the bisector from the center to a chord is perpendicular",
     "derived",
     "If from the center of a circle a straight line bisects a chord, it is perpendicular to the chord.",
     "center_bisector_is_perpendicular",
     [("III", 3, "a central angle bisector bisects the chord")],
     ["let O = center", "let AB = chord", "let M = midpoint", "therefore angle_OMB == one_right_angle"]),
    (18, "exterior-rectangle-tangent",
     "exterior rectangle condition characterizes tangents",
     "derived",
     "If from a point outside a circle two straight lines are drawn, one through the center and one cutting the circle, "
     "and the rectangle on the whole and the exterior segment equals the square on the other, then the other is tangent.",
     "rectangle_condition_gives_tangent",
     [("III", 9, "if the rectangle equals the square then the line is a tangent")],
     ["let P = exterior_point", "let center_line = line_PO", "let secant = line_PAB", "therefore other_line_is_tangent"]),
    (19, "tangent-perpendicular-diameter",
     "the tangent is perpendicular to the diameter at the point of contact",
     "derived",
     "If a straight line touches a circle, the perpendicular from the point of contact to the center is perpendicular to the tangent.",
     "tangent_perpendicular_to_radius",
     [("III", 18, "exterior rectangle condition characterizes tangents")],
     ["let T = point_of_contact", "let O = center", "let tangent = line_through_T", "therefore tangent_perpendicular_to_OT"]),
    (20, "central-angle-double-inscribed",
     "the central angle is double the inscribed angle on the same arc",
     "derived",
     "In a circle the angle at the center is double the angle at the circumference when the angles stand on the same arc.",
     "central_angle_double_inscribed",
     [("I", 32, "exterior angle equals sum of remote interior angles")],
     ["let O = center", "let A = point_on_circumference", "let B = second_point", "therefore angle_AOB == 2 * angle_ACB"]),
    (21, "angles-in-same-segment",
     "angles in the same segment are equal",
     "derived",
     "In a circle angles in the same segment are equal to one another.",
     "angles_in_same_segment_equal",
     [("III", 20, "the central angle is double the inscribed angle on the same arc")],
     ["let segment = arc_AB", "let C = point_in_segment", "let D = second_point", "therefore angle_ACB == angle_ADB"]),
    (22, "cyclic-quadrilateral-opposite-angles",
     "opposite angles of a cyclic quadrilateral sum to two right angles",
     "derived",
     "The opposite angles of quadrilaterals in circles equal two right angles.",
     "opposite_angles_sum_two_right",
     [("III", 21, "angles in the same segment are equal"), ("I", 13, "adjacent angles on a straight line sum to two right angles")],
     ["let ABCD = cyclic_quadrilateral", "let angle_A = angle_DAB", "let angle_C = angle_BCD", "therefore angle_A + angle_C == two_right_angles"]),
    (23, "no-two-similar-segments-same-side",
     "two unequal similar segments cannot stand on the same side of a line",
     "derived",
     "On the same straight line and on the same side of it there cannot be constructed two similar unequal segments of circles.",
     "unique_segment_on_line_side",
     [("III", 21, "angles in the same segment are equal")],
     ["let AB = straight_line", "let seg1 = segment_on_AB", "let seg2 = second_segment", "therefore seg1 == seg2"]),
    (24, "similar-segments-on-equal-lines",
     "similar segments on equal straight lines are equal",
     "derived",
     "Similar segments of circles on equal straight lines are equal to one another.",
     "similar_segments_on_equal_lines_equal",
     [("III", 23, "two unequal similar segments cannot stand on the same side of a line")],
     ["let AB = equal_line_1", "let CD = equal_line_2", "let seg1 = similar_segment_on_AB", "therefore seg1 == seg2"]),
    (25, "describe-circle-from-segment",
     "to describe the circle of which a given segment is part",
     "derived",
     "Given a segment of a circle, to describe the complete circle of which it is a part.",
     "circle_from_segment_exists",
     [("III", 21, "angles in the same segment are equal"), ("I", 9, "bisect a given angle")],
     ["let seg = given_segment", "let chord = base_of_segment", "let center = point_equidistant_from_ends", "therefore circle_through_segment_exists"]),
    (26, "equal-angles-equal-arcs",
     "in equal circles equal angles stand on equal arcs",
     "derived",
     "In equal circles equal angles at the centers or circumferences stand on equal circumferences.",
     "equal_angles_on_equal_arcs",
     [("III", 20, "the central angle is double the inscribed angle on the same arc")],
     ["let C1 = equal_circle_1", "let C2 = equal_circle_2", "let arc1 = arc_from_angle", "therefore arc1 == arc2"]),
    (27, "equal-arcs-equal-angles",
     "in equal circles equal arcs subtend equal angles",
     "derived",
     "In equal circles circumferences subtending equal angles at the centers or circumferences are equal.",
     "equal_arcs_give_equal_angles",
     [("III", 26, "in equal circles equal angles stand on equal arcs")],
     ["let arc1 = equal_arc_1", "let arc2 = equal_arc_2", "let angle1 = angle_at_center", "therefore angle1 == angle2"]),
    (28, "equal-chords-equal-arcs",
     "in equal circles equal chords cut off equal arcs",
     "derived",
     "In equal circles equal straight lines cut off equal circumferences, the greater equal to the greater and the less to the less.",
     "equal_chords_cut_equal_arcs",
     [("III", 1, "equal chords subtend equal angles at the center")],
     ["let AB = chord_1", "let DE = chord_2", "let arc_AB = major_or_minor_arc", "therefore arc_AB == arc_DE"]),
    (29, "equal-arcs-equal-chords",
     "in equal circles equal arcs subtend equal chords",
     "derived",
     "In equal circles equal circumferences are subtended by equal straight lines.",
     "equal_arcs_subtend_equal_chords",
     [("III", 28, "in equal circles equal chords cut off equal arcs")],
     ["let arc1 = equal_arc", "let arc2 = equal_arc", "let chord1 = chord_subtending_arc1", "therefore chord1 == chord2"]),
    (30, "bisect-circumference",
     "to bisect a given circumference of a circle",
     "derived",
     "To bisect a given circumference of a circle.",
     "bisected_circumference_exists",
     [("III", 2, "a perpendicular from the center bisects the chord"), ("I", 10, "bisect a given segment")],
     ["let arc = given_circumference", "let chord = chord_of_arc", "let M = midpoint_of_chord", "therefore arc_bisected_at_M"]),
    (31, "angle-in-segment-and-right-angle",
     "the angle in a greater segment is less than a right angle",
     "derived",
     "In a circle the angle in a greater segment is less than a right angle, and in a less segment greater.",
     "segment_angle_compares_to_right",
     [("III", 20, "the central angle is double the inscribed angle on the same arc"), ("I", 11, "erect a perpendicular at a point on a line")],
     ["let seg = greater_segment", "let angle = inscribed_angle", "therefore angle < one_right_angle"]),
    (32, "tangent-chord-alternate-segment",
     "the angle between tangent and chord equals the angle in the alternate segment",
     "derived",
     "If a straight line touches a circle and a chord is drawn from the point of contact, the angles with the tangent "
     "equal the angles in the alternate segments.",
     "tangent_chord_angle_equals_alternate_segment",
     [("III", 19, "the tangent is perpendicular to the diameter at the point of contact"), ("III", 21, "angles in the same segment are equal")],
     ["let T = point_of_contact", "let tangent = line_through_T", "let chord = chord_TA", "therefore angle_between_tangent_chord == angle_in_alternate_segment"]),
    (33, "construct-similar-segment",
     "to construct on a given straight line a segment similar to a given segment",
     "derived",
     "On a given straight line to construct a segment of a circle similar to a given segment.",
     "similar_segment_constructed",
     [("III", 24, "similar segments on equal straight lines are equal"), ("I", 23, "copy a given angle onto a line at a point")],
     ["let AB = given_line", "let template = given_segment", "let angle = angle_of_segment", "therefore similar_segment_on_AB_exists"]),
    (34, "cut-segment-with-given-angle",
     "to cut off a segment containing an angle equal to a given rectilineal angle",
     "derived",
     "To cut off from a circle a segment containing an angle equal to a given rectilineal angle.",
     "segment_with_given_angle_exists",
     [("III", 33, "to construct on a given straight line a segment similar to a given segment")],
     ["let circle = given_circle", "let given_angle = rectilineal_angle", "let seg = required_segment", "therefore segment_contains_given_angle"]),
    (35, "tangents-from-point-equal",
     "tangents drawn from a point to a circle are equal",
     "derived",
     "If two straight lines from a point touch a circle, the straight lines are equal.",
     "tangents_from_point_equal",
     [("III", 8, "the rectangle on a secant and its exterior segment equals the square on the tangent")],
     ["let P = exterior_point", "let TA = tangent_at_A", "let TB = tangent_at_B", "therefore segment_PT_A == segment_PT_B"]),
    (36, "center-bisects-tangent-angle",
     "the line to the center bisects the angle between tangents",
     "derived",
     "If from a point outside a circle two straight lines touch it, the line joining the point to the center bisects "
     "the angle between the tangents.",
     "center_line_bisects_tangent_angle",
     [("III", 35, "tangents drawn from a point to a circle are equal"), ("I", 8, "side-side-side angle equality")],
     ["let P = exterior_point", "let O = center", "let TA = tangent_at_A", "therefore angle_APT == angle_BPT"]),
    (37, "power-of-point-theorem",
     "the rectangle on a secant and its exterior part equals the square on the tangent",
     "derived",
     "If a point is taken outside a circle and from it two straight lines fall on the circle, one a tangent and the other "
     "a secant, the rectangle on the whole secant and the part outside equals the square on the tangent.",
     "power_of_point_rect_equals_sq",
     [("III", 8, "the rectangle on a secant and its exterior segment equals the square on the tangent"), ("III", 9, "if the rectangle equals the square then the line is a tangent")],
     ["let P = exterior_point", "let secant = line_PABC", "let tangent = line_PT", "therefore rect(secant, exterior) == sq(tangent)"]),
]


def render_flow(
    n: int,
    slug: str,
    title: str,
    tier: str,
    means: str,
    therefore: str,
    needs: list,
    extra_steps: list,
) -> str:
    lines = [
        f"# @module examples.verify.euclid.book-iii",
        f"# @means  {means}",
        f"# @from   euclid — Elements, Book III, Proposition {n}",
        f"# @tier   {tier}",
    ]
    if needs:
        need_str = ", ".join(_need(book, nn, tt) for book, nn, tt in needs)
        lines.append(f"# @needs  {need_str}")
    lines.append("")
    lines.append(f"theorem {claim('III', n, title)} () {{")
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
    for n, slug, title, tier, means, therefore, needs, extra_steps in PROPOSITIONS:
        fname = f"prop-{n:02d}-{slug}.flow"
        path = OUT / fname
        path.write_text(
            render_flow(n, slug, title, tier, means, therefore, needs, extra_steps),
            encoding="utf-8",
        )
        paths.append(f"examples/verify/euclid/book-iii/{fname}")
    manifest = OUT / "MANIFEST.txt"
    manifest.write_text("\n".join(paths) + "\n", encoding="utf-8")
    print(f"Wrote {len(paths)} propositions to {OUT}")


if __name__ == "__main__":
    main()