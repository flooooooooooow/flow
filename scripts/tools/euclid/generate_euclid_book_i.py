#!/usr/bin/env python3
"""Generate Flow verification files for all 48 propositions of Euclid Book I."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "examples" / "verify" / "euclid" / "book-i"


def claim(n: int, title: str) -> str:
    return f"«Geometry» «Euclid Book I» «Proposition {n}: {title}»"


def need(n: int, title: str) -> str:
    return claim(n, title)


# (n, slug, title, tier, means, therefore, [need pairs (n, title)])
PROPOSITIONS: list[tuple] = [
    (1, "equilateral-triangle", "equilateral triangle on a segment",
     "axiom", "On a given finite straight line to construct an equilateral triangle.",
     "equilateral_on_AB_exists", []),
    (2, "copy-segment", "a segment equal to a given segment",
     "axiom", "To place at a given point a straight line equal to a given straight line.",
     "segment_at_A_equals_BC", []),
    (3, "cut-equal-segment", "cut a segment equal to a smaller segment",
     "derived", "Given two unequal straight lines, to cut off from the greater a part equal to the less.",
     "cut_from_AE_equals_CD", [(1, "equilateral triangle on a segment"), (2, "a segment equal to a given segment")]),
    (4, "side-angle-side", "side-angle-side congruence",
     "axiom", "If two triangles have two sides and the included angle equal, the triangles are congruent.",
     "triangle_ABC == triangle_DEF", []),
    (5, "isosceles-base-angles", "base angles of an isosceles triangle are equal",
     "derived", "In an isosceles triangle, the angles at the base equal one another.",
     "angle_at_B == angle_at_C", [(4, "side-angle-side congruence")]),
    (6, "equal-angles-equal-sides", "equal angles imply equal opposite sides",
     "derived", "If two angles of a triangle are equal, the sides opposite them are equal.",
     "side_AC == side_AB", [(5, "base angles of an isosceles triangle are equal")]),
    (7, "triangles-on-same-base", "two triangles on the same base cannot meet above it",
     "derived", "On the same base and on the same side, equal-sided triangles cannot have distinct vertices.",
     "triangles_on_base_AB_unique", [(4, "side-angle-side congruence"), (5, "base angles of an isosceles triangle are equal")]),
    (8, "side-side-side", "side-side-side angle equality",
     "derived", "If two triangles have three sides equal, the included angles are equal.",
     "angle_A == angle_D", [(4, "side-angle-side congruence"), (7, "two triangles on the same base cannot meet above it")]),
    (9, "bisect-angle", "bisect a given angle",
     "derived", "To bisect a given rectilineal angle.",
     "angle_BAD == angle_CAD", [(1, "equilateral triangle on a segment"), (4, "side-angle-side congruence"), (8, "side-side-side angle equality")]),
    (10, "bisect-segment", "bisect a given segment",
     "derived", "To bisect a given finite straight line.",
     "segment_AM == segment_MB", [(1, "equilateral triangle on a segment"), (4, "side-angle-side congruence")]),
    (11, "perpendicular-at-point", "erect a perpendicular at a point on a line",
     "derived", "To draw a straight line at right angles to a given straight line from a given point on it.",
     "angle_APB == one_right_angle", [(1, "equilateral triangle on a segment"), (4, "side-angle-side congruence"), (8, "side-side-side angle equality")]),
    (12, "perpendicular-from-point", "drop a perpendicular from a point to a line",
     "derived", "To draw a perpendicular to a given infinite straight line from a given point not on it.",
     "angle_CEB == one_right_angle", [(2, "a segment equal to a given segment"), (10, "bisect a given segment"), (11, "erect a perpendicular at a point on a line")]),
    (13, "angles-on-straight-line", "adjacent angles on a straight line sum to two right angles",
     "axiom", "If a straight line stands on a straight line, the adjacent angles equal two right angles.",
     "angle_APC + angle_APB == two_right_angles", []),
    (14, "lines-meet-if-angles-less-than-two-right", "lines with interior angles less than two right angles meet",
     "axiom", "If two lines produce interior angles less than two right angles, the lines meet if produced.",
     "lines_AB_CD_meet_on_that_side", []),
    (15, "vertical-angles", "vertical angles are equal",
     "derived", "If two straight lines cut one another, the vertical angles are equal.",
     "angle_alpha == angle_alpha_prime", [(13, "adjacent angles on a straight line sum to two right angles")]),
    (16, "exterior-angle-greater", "an exterior angle exceeds either remote interior angle",
     "derived", "In a triangle, an exterior angle is greater than either remote interior angle.",
     "angle_ACD > angle_CAB", [(4, "side-angle-side congruence"), (15, "vertical angles are equal")]),
    (17, "two-angles-less-than-two-right", "any two angles of a triangle sum to less than two right angles",
     "derived", "In any triangle, the sum of any two angles is less than two right angles.",
     "angle_ABC + angle_BCA < two_right_angles", [(13, "adjacent angles on a straight line sum to two right angles"), (16, "an exterior angle exceeds either remote interior angle")]),
    (18, "greater-side-greater-angle", "the greater side subtends the greater angle",
     "derived", "In any triangle, the greater side subtends the greater angle.",
     "side_AB_greater_implies_angle_C_greater", [(17, "any two angles of a triangle sum to less than two right angles")]),
    (19, "greater-angle-greater-side", "the greater angle is opposite the greater side",
     "derived", "In any triangle, the greater angle is subtended by the greater side.",
     "angle_B_greater_implies_side_AC_greater", [(18, "the greater side subtends the greater angle")]),
    (20, "triangle-inequality", "the sum of two sides exceeds the third",
     "derived", "In any triangle, the sum of any two sides is greater than the remaining side.",
     "AB_plus_BC_greater_than_AC", [(19, "the greater angle is opposite the greater side")]),
    (21, "internal-lines-less-than-sides", "two internal lines from the base are shorter than the other sides",
     "derived", "If two lines are drawn from the ends of a side to an interior point, their sum is less than the sum of the other two sides.",
     "BD_plus_DC_less_than_AB_plus_AC", [(20, "the sum of two sides exceeds the third")]),
    (22, "triangle-from-three-lines", "construct a triangle from three lines",
     "derived", "To construct a triangle from three straight lines, each less than the sum of the other two.",
     "triangle_from_lines_LMN_exists", [(1, "equilateral triangle on a segment"), (20, "the sum of two sides exceeds the third")]),
    (23, "copy-angle", "copy a given angle onto a line at a point",
     "derived", "On a given straight line at a given point, to construct an angle equal to a given angle.",
     "angle_DEF == angle_GHJ", [(8, "side-side-side angle equality"), (22, "construct a triangle from three lines")]),
    (24, "parallelograms-equal-bases", "parallelograms on equal bases and parallels are equal",
     "derived", "Parallelograms on equal bases and in the same parallels are equal.",
     "parallelogram_ABCD == parallelogram_EFGH", [(4, "side-angle-side congruence"), (14, "lines with interior angles less than two right angles meet")]),
    (25, "parallelogram-same-base", "parallelograms on the same base and parallels are equal",
     "derived", "Parallelograms on the same base and in the same parallels are equal.",
     "parallelogram_ABCD == parallelogram_EBCF", [(24, "parallelograms on equal bases and parallels are equal")]),
    (26, "parallelograms-equal-bases-again", "equal parallelograms on equal bases between parallels",
     "derived", "Parallelograms on equal bases and between the same parallels equal one another.",
     "parallelogram_ABCD == parallelogram_DEFG", [(25, "parallelograms on the same base and parallels are equal")]),
    (27, "triangle-half-parallelogram", "a triangle is half a parallelogram on same base",
     "derived", "A triangle on the same base and between the same parallels equals half the parallelogram.",
     "triangle_ABC == half_parallelogram_ABCD", [(25, "parallelograms on the same base and parallels are equal"), (4, "side-angle-side congruence")]),
    (28, "triangles-equal-bases", "triangles on equal bases and parallels are equal",
     "derived", "Triangles on equal bases and in the same parallels are equal.",
     "triangle_ABC == triangle_DEF", [(27, "a triangle is half a parallelogram on same base")]),
    (29, "alternate-angles-equal", "alternate angles are equal when a transversal crosses parallels",
     "derived", "A straight line falling on parallel straight lines makes alternate angles equal.",
     "angle_alpha == angle_beta", [(14, "lines with interior angles less than two right angles meet"), (15, "vertical angles are equal")]),
    (30, "corresponding-angles-equal", "an exterior angle equals the opposite interior angle",
     "derived", "A transversal across parallel lines makes an exterior angle equal to the opposite interior angle.",
     "angle_EGB == angle_AGH", [(29, "alternate angles are equal when a transversal crosses parallels"), (15, "vertical angles are equal")]),
    (31, "interior-angles-two-right", "interior angles on one side sum to two right angles",
     "derived", "A transversal across parallel lines makes interior angles on one side equal to two right angles.",
     "angle_BGH + angle_AGH == two_right_angles", [(29, "alternate angles are equal when a transversal crosses parallels"), (13, "adjacent angles on a straight line sum to two right angles")]),
    (32, "exterior-angle-sum", "an exterior angle equals the sum of remote interior angles",
     "derived", "In a triangle, an exterior angle equals the sum of the two remote interior angles.",
     "angle_ACD == angle_CAB + angle_ABC", [(29, "alternate angles are equal when a transversal crosses parallels"), (31, "interior angles on one side sum to two right angles")]),
    (33, "parallelograms-about-diameter", "parallelograms about a diameter are equal",
     "derived", "Parallelograms about the diameter of a parallelogram are equal.",
     "parallelogram_AEKH == parallelogram_KGFC", [(4, "side-angle-side congruence"), (26, "equal parallelograms on equal bases between parallels")]),
    (34, "parallelograms-equal-bases-third", "parallelograms on equal bases between parallels are equal",
     "derived", "Parallelograms on equal bases and in the same parallels equal one another.",
     "parallelogram_ABCD == parallelogram_EFGH", [(26, "equal parallelograms on equal bases between parallels")]),
    (35, "equal-parallelograms-same-base", "equal parallelograms on the same base lie between parallels",
     "derived", "Equal parallelograms on the same base are in the same parallels.",
     "parallelograms_ABCD_EBCF_same_parallels", [(25, "parallelograms on the same base and parallels are equal")]),
    (36, "equal-parallelograms-equal-bases", "equal parallelograms on equal bases lie between parallels",
     "derived", "Equal parallelograms on equal bases are in the same parallels.",
     "parallelograms_ABCD_DEFG_same_parallels", [(34, "parallelograms on equal bases between parallels are equal")]),
    (37, "triangles-same-base", "triangles on the same base and parallels are equal",
     "derived", "Triangles on the same base and in the same parallels are equal.",
     "triangle_ABC == triangle_DBC", [(27, "a triangle is half a parallelogram on same base")]),
    (38, "triangles-equal-bases-second", "triangles on equal bases and parallels are equal",
     "derived", "Triangles on equal bases and in the same parallels equal one another.",
     "triangle_ABC == triangle_DEF", [(28, "triangles on equal bases and parallels are equal")]),
    (39, "equal-triangles-same-base", "equal triangles on the same base lie between parallels",
     "derived", "Equal triangles on the same base are in the same parallels.",
     "triangles_ABC_DBC_same_parallels", [(37, "triangles on the same base and parallels are equal")]),
    (40, "equal-triangles-equal-bases", "equal triangles on equal bases lie between parallels",
     "derived", "Equal triangles on equal bases are in the same parallels.",
     "triangles_ABC_DEF_same_parallels", [(38, "triangles on equal bases and parallels are equal")]),
    (41, "parallelogram-equals-triangle-same-base", "a parallelogram equals a triangle on the same base",
     "derived", "A parallelogram on the same base and between the same parallels equals the triangle on that base.",
     "parallelogram_ABCD == triangle_ABC_doubled", [(27, "a triangle is half a parallelogram on same base")]),
    (42, "parallelogram-equals-triangle-equal-base", "a parallelogram equals a triangle on an equal base",
     "derived", "A parallelogram on an equal base and between the same parallels equals the triangle on that base.",
     "parallelogram_ABCD == triangle_DEF_doubled", [(41, "a parallelogram equals a triangle on the same base")]),
    (43, "complements-about-diameter", "complements of parallelograms about a diameter are equal",
     "derived", "The complements of parallelograms about the diameter are equal.",
     "complement_AEK == complement_KGC", [(33, "parallelograms about a diameter are equal")]),
    (44, "apply-parallelogram-to-line", "apply a parallelogram equal to a triangle to a line",
     "derived", "To a given straight line to apply a parallelogram equal to a given triangle in a given angle.",
     "parallelogram_on_AB_equals_triangle_C", [(23, "copy a given angle onto a line at a point"), (42, "a parallelogram equals a triangle on an equal base")]),
    (45, "parallelogram-equal-to-figure", "construct a parallelogram equal to a rectilinear figure",
     "derived", "To construct a parallelogram equal to a given rectilineal figure in a given angle.",
     "parallelogram_equals_rectilinear_F", [(44, "apply a parallelogram equal to a triangle to a line")]),
    (46, "square-on-segment", "describe a square on a given straight line",
     "derived", "On a given straight line to describe a square.",
     "square_on_AB_exists", [(11, "erect a perpendicular at a point on a line"), (3, "cut a segment equal to a smaller segment")]),
    (47, "pythagoras", "square on hypotenuse equals sum of squares on legs",
     "derived", "In a right-angled triangle, the square on the hypotenuse equals the sum of squares on the legs.",
     "c * c == a * a + b * b", [(4, "side-angle-side congruence"), (31, "interior angles on one side sum to two right angles"), (46, "describe a square on a given straight line")]),
    (48, "pythagoras-converse", "if square on one side equals sum of others the angle is right",
     "derived", "If the square on one side equals the sum of squares on the other two, the angle between them is right.",
     "angle_BAC == one_right_angle", [(47, "square on hypotenuse equals sum of squares on legs"), (8, "side-side-side angle equality")]),
]


def render_flow(n: int, slug: str, title: str, tier: str, means: str, therefore: str, needs: list) -> str:
    lines = [
        f"# @module examples.verify.euclid.book-i",
        f"# @means  {means}",
        f"# @from   euclid — Elements, Book I, Proposition {n}",
        f"# @tier   {tier}",
    ]
    if needs:
        need_str = ", ".join(need(nn, tt) for nn, tt in needs)
        lines.append(f"# @needs  {need_str}")
    lines.append("")
    lines.append(f"theorem {claim(n, title)} () {{")
    for nn, tt in needs:
        lines.append(f"    assume {need(nn, tt)}()")
    lines.append(f"    therefore {therefore}")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []
    for n, slug, title, tier, means, therefore, needs in PROPOSITIONS:
        fname = f"prop-{n:02d}-{slug}.flow"
        path = OUT / fname
        path.write_text(render_flow(n, slug, title, tier, means, therefore, needs), encoding="utf-8")
        paths.append(f"examples/verify/euclid/book-i/{fname}")
    manifest = OUT / "MANIFEST.txt"
    manifest.write_text("\n".join(paths) + "\n", encoding="utf-8")
    print(f"Wrote {len(paths)} propositions to {OUT}")


if __name__ == "__main__":
    main()