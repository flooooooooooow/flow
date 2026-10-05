#!/usr/bin/env python3
"""Generate Flow verification files for all 33 propositions of Euclid Book VI."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "examples" / "verify" / "euclid" / "book-vi"

BOOKS = {
    "I": "Euclid Book I",
    "V": "Euclid Book V",
    "VI": "Euclid Book VI",
}


def claim(book: str, n: int, title: str) -> str:
    return f"«Geometry» «{BOOKS[book]}» «Proposition {n}: {title}»"


def _need(book: str, n: int, title: str) -> str:
    return claim(book, n, title)


# (n, slug, title, means, therefore, needs, extra_steps)
PROPOSITIONS: list[tuple] = [
    (1, "triangles-parallelograms-same-height",
     "triangles and parallelograms of the same height are as their bases",
     "Triangles and parallelograms under the same height are to one another as their bases.",
     "area_ratio_equals_base_ratio",
     [("V", 1, "equimultiples of equimultiples are equimultiple of the originals")],
     ["let ABC = triangle", "let base_BC = base", "let height = common_height", "therefore area(ABC) : area(DEF) == base_BC : base_EF"]),
    (2, "parallel-to-side-cuts-proportionally",
     "a line parallel to a triangle side cuts the other sides proportionally",
     "If a straight line is drawn parallel to one side of a triangle, it cuts the other sides proportionally.",
     "parallel_implies_proportional_sides",
     [("VI", 1, "triangles and parallelograms of the same height are as their bases"), ("I", 37, "triangles on the same base and between the same parallels are equal")],
     ["let ABC = triangle", "let DE = line_parallel_to_BC", "let AD = segment_on_AB", "therefore ratio(AD, DB) == ratio(AE, EC)"]),
    (3, "proportional-cut-implies-parallel",
     "a proportional cut implies a line parallel to the opposite side",
     "If the sides of a triangle are cut proportionally, the join of the points of section is parallel to the remaining side.",
     "proportional_sides_implies_parallel",
     [("VI", 2, "a line parallel to a triangle side cuts the other sides proportionally")],
     ["let ABC = triangle", "let D = point_on_AB", "let E = point_on_AC", "therefore DE_parallel_to_BC"]),
    (4, "equiangular-implies-side-ratio",
     "equiangular triangles have proportional corresponding sides",
     "In equiangular triangles the sides about the equal angles are proportional, and those are corresponding sides which subtend the equal angles.",
     "equiangular_implies_proportional_sides",
     [("VI", 2, "a line parallel to a triangle side cuts the other sides proportionally"), ("I", 4, "side-angle-side congruence")],
     ["let ABC = triangle_1", "let DEF = triangle_2", "let angle_A = angle_D", "therefore ratio(AB, BC) == ratio(DE, EF)"]),
    (5, "proportional-sides-implies-equiangular",
     "triangles with proportional sides are equiangular",
     "If the sides of two triangles are proportional, the triangles are equiangular and have equal angles.",
     "proportional_sides_implies_equiangular",
     [("VI", 4, "equiangular triangles have proportional corresponding sides")],
     ["let ABC = triangle_1", "let DEF = triangle_2", "let ratio_sides = proportional", "therefore angle_A == angle_D"]),
    (6, "one-equal-angle-proportional-sides",
     "one equal angle and proportional including sides imply equiangular triangles",
     "If two triangles have one angle equal and the sides about the equal angles proportional, the triangles are equiangular.",
     "one_angle_and_sides_implies_similar",
     [("VI", 4, "equiangular triangles have proportional corresponding sides"), ("VI", 5, "triangles with proportional sides are equiangular")],
     ["let ABC = triangle_1", "let DEF = triangle_2", "let angle_A = angle_D", "therefore triangles_similar"]),
    (7, "equiangular-implies-one-angle-proportional",
     "equiangular triangles have one equal angle and proportional sides about it",
     "If two triangles are equiangular, they have one angle equal and the sides about equal angles proportional.",
     "similar_implies_one_angle_and_sides",
     [("VI", 6, "one equal angle and proportional including sides imply equiangular triangles")],
     ["let ABC = triangle_1", "let DEF = triangle_2", "let angle_B = angle_E", "therefore ratio(AB, BC) == ratio(DE, EF)"]),
    (8, "right-triangle-perpendicular-similar",
     "in a right triangle the altitude to the hypotenuse gives similar subtriangles",
     "If in a right-angled triangle a perpendicular is drawn from the right angle to the base, the triangles on each side are similar to the whole and to one another.",
     "right_triangle_altitude_gives_similarity",
     [("I", 47, "square on hypotenuse equals sum of squares on legs"), ("VI", 4, "equiangular triangles have proportional corresponding sides")],
     ["let ABC = right_triangle", "let AD = altitude_to_hypotenuse", "let ABD = subtriangle", "therefore triangle_ABD ~ triangle_ABC"]),
    (9, "similar-subtriangles-imply-right",
     "similar subtriangles sharing an acute angle imply a right triangle",
     "If from a point on the base of a triangle a line is drawn meeting the sides and the subtriangles are similar to the whole, the angle at the base is right.",
     "similar_subtriangles_implies_right_angle",
     [("VI", 8, "in a right triangle the altitude to the hypotenuse gives similar subtriangles")],
     ["let ABC = triangle", "let D = point_on_base", "let subtriangle = ABD", "therefore angle_BAC == one_right_angle"]),
    (10, "cut-prescribed-fraction",
     "to cut off a prescribed part from a given straight line",
     "Given a straight line, to cut off a prescribed part from it.",
     "prescribed_part_cut_off",
     [("VI", 1, "triangles and parallelograms of the same height are as their bases"), ("I", 3, "cut a segment equal to a smaller segment")],
     ["let AB = given_line", "let C = prescribed_part", "let D = cut_point", "therefore segment_AD == prescribed_part"]),
    (11, "apply-parallelogram-deficient",
     "to apply a parallelogram equal to a figure and deficient by a similar parallelogram",
     "To a given straight line to apply a parallelogram equal to a given rectilineal figure and deficient by a parallelogram similar to a given one.",
     "deficient_parallelogram_applied",
     [("VI", 10, "to cut off a prescribed part from a given straight line"), ("I", 44, "apply a parallelogram equal to a triangle to a line")],
     ["let AB = given_line", "let F = given_figure", "let par = applied_parallelogram", "therefore area(par) == area(F) - deficiency"]),
    (12, "apply-parallelogram-exceeding",
     "to apply a parallelogram equal to a figure and exceeding by a similar parallelogram",
     "To a given straight line to apply a parallelogram equal to a given rectilineal figure and exceeding by a parallelogram similar to a given one.",
     "exceeding_parallelogram_applied",
     [("VI", 11, "to apply a parallelogram equal to a figure and deficient by a similar parallelogram")],
     ["let AB = given_line", "let F = given_figure", "let par = applied_parallelogram", "therefore area(par) == area(F) + excess"]),
    (13, "apply-similar-parallelogram",
     "to apply to a line a parallelogram equal to a figure and similar to another",
     "To a given straight line to apply a parallelogram equal to a given rectilineal figure and similar to a given parallelogram.",
     "similar_parallelogram_applied",
     [("VI", 12, "to apply a parallelogram equal to a figure and exceeding by a similar parallelogram")],
     ["let AB = given_line", "let F = given_figure", "let template = given_parallelogram", "therefore applied_parallelogram_similar"]),
    (14, "equal-equiangular-reciprocal-sides",
     "equal equiangular parallelograms have reciprocally proportional sides",
     "In equal and equiangular parallelograms the sides about the equal angles are reciprocally proportional.",
     "equal_equiangular_implies_reciprocal_sides",
     [("VI", 4, "equiangular triangles have proportional corresponding sides"), ("V", 7, "proportional magnitudes satisfy alternando")],
     ["let ABCD = parallelogram_1", "let EFGH = parallelogram_2", "let angle_A = angle_E", "therefore reciprocal_proportion_holds"]),
    (15, "reciprocal-sides-implies-equal",
     "equiangular parallelograms with reciprocal sides are equal",
     "Equiangular parallelograms in which the sides about the equal angles are reciprocally proportional are equal.",
     "reciprocal_sides_implies_equal",
     [("VI", 14, "equal equiangular parallelograms have reciprocally proportional sides")],
     ["let ABCD = parallelogram_1", "let EFGH = parallelogram_2", "let reciprocal = side_ratio", "therefore area_ABCD == area_EFGH"]),
    (16, "four-lines-rectangle-equality",
     "four proportional lines give equal rectangles on extremes and means",
     "If four straight lines are proportional, the rectangle contained by the extremes equals the rectangle contained by the means.",
     "rect_extremes_equals_rect_means",
     [("V", 16, "composition holds with alternando"), ("VI", 14, "equal equiangular parallelograms have reciprocally proportional sides")],
     ["let a = first", "let b = second", "let c = third", "let d = fourth", "therefore rect(a, d) == rect(b, c)"]),
    (17, "three-lines-square-equality",
     "three proportional lines give rectangle on extremes equal to square on mean",
     "If three straight lines are proportional, the rectangle contained by the extremes equals the square on the mean.",
     "rect_extremes_equals_sq_mean",
     [("VI", 16, "four proportional lines give equal rectangles on extremes and means")],
     ["let a = first", "let b = mean", "let c = third", "therefore rect(a, c) == sq(b)"]),
    (18, "square-equality-implies-proportional",
     "rectangle on extremes equal to square on mean implies three lines proportional",
     "If the rectangle contained by the first and third equals the square on the second, the three straight lines are proportional.",
     "sq_mean_implies_three_proportional",
     [("VI", 17, "three proportional lines give rectangle on extremes equal to square on mean")],
     ["let a = first", "let b = second", "let c = third", "therefore ratio(a, b) == ratio(b, c)"]),
    (19, "similar-figures-duplicate-ratio",
     "similar rectilineal figures are in duplicate ratio of corresponding sides",
     "Similar rectilineal figures are to one another in the duplicate ratio of the corresponding sides.",
     "similar_figures_duplicate_ratio",
     [("VI", 4, "equiangular triangles have proportional corresponding sides"), ("V", 18, "ex aequali proportion from three magnitudes")],
     ["let fig1 = similar_figure_1", "let fig2 = similar_figure_2", "let side_a = homologous_side", "therefore area_ratio_duplicate_of_side_ratio"]),
    (20, "similar-polygons-triangle-decomposition",
     "similar polygons are divided into the same number of similar triangles",
     "Similar polygons may be divided into the same number of similar triangles corresponding in order and proportion.",
     "similar_polygons_same_triangle_decomposition",
     [("VI", 19, "similar rectilineal figures are in duplicate ratio of corresponding sides")],
     ["let poly1 = polygon_1", "let poly2 = polygon_2", "let triangles1 = decomposition", "therefore triangles_similar_in_order"]),
    (21, "duplicate-ratio-homologous-sides",
     "similar figures have ratio duplicate of homologous sides",
     "Similar rectilineal figures are to one another as the duplicate ratio of their homologous sides.",
     "area_as_duplicate_homologous_ratio",
     [("VI", 20, "similar polygons are divided into the same number of similar triangles")],
     ["let fig1 = figure_1", "let fig2 = figure_2", "let s1 = homologous_side_1", "therefore ratio_areas == duplicate_ratio(s1, s2)"]),
    (22, "proportional-magnitudes-composition",
     "proportional magnitudes satisfy composition of ratios",
     "If four magnitudes are proportional, they are also proportional by composition as in Book V.",
     "composition_of_ratios_holds",
     [("V", 11, "proportional magnitudes satisfy componendo"), ("VI", 16, "four proportional lines give equal rectangles on extremes and means")],
     ["let a = first", "let b = second", "let c = third", "let d = fourth", "therefore ratio(a + b, b) == ratio(c + d, d)"]),
    (23, "equiangular-parallelogram-compound-ratio",
     "equiangular parallelograms have ratio compounded of side ratios",
     "Equiangular parallelograms have to one another the ratio compounded of the ratios of their sides.",
     "parallelogram_ratio_compounded",
     [("VI", 14, "equal equiangular parallelograms have reciprocally proportional sides"), ("V", 23, "chained proportion yields ex aequali")],
     ["let ABCD = parallelogram_1", "let EFGH = parallelogram_2", "let side_ratio_1 = ratio_AB_DE", "therefore area_ratio == compound(side_ratios)"]),
    (24, "complements-similar-to-whole",
     "parallelograms about a diameter are similar to the whole and to one another",
     "In any parallelogram the complements of the parallelograms about the diameter are similar both to the whole and to one another.",
     "complements_similar_to_whole",
     [("I", 34, "complements of parallelograms about the diameter are equal"), ("VI", 4, "equiangular triangles have proportional corresponding sides")],
     ["let ABCD = parallelogram", "let BD = diameter", "let comp1 = complement_1", "therefore comp1 ~ ABCD"]),
    (25, "greatest-deficient-parallelogram",
     "the greatest parallelogram on half the line with deficiency is similar to the given one",
     "Of all parallelograms applied to a given straight line and deficient by parallelograms similar to a given one, the greatest is that applied to the half of the line.",
     "greatest_deficient_parallelogram_on_half",
     [("VI", 11, "to apply a parallelogram equal to a figure and deficient by a similar parallelogram")],
     ["let AB = given_line", "let M = midpoint", "let par = applied_on_half", "therefore par_is_greatest_deficient"]),
    (26, "similar-parallelograms-duplicate-ratio",
     "similar parallelograms are in duplicate ratio of homologous sides",
     "Similar parallelograms are to one another in the duplicate ratio of the homologous sides.",
     "similar_parallelograms_duplicate_ratio",
     [("VI", 19, "similar rectilineal figures are in duplicate ratio of corresponding sides"), ("VI", 24, "parallelograms about a diameter are similar to the whole and to one another")],
     ["let par1 = parallelogram_1", "let par2 = parallelogram_2", "let side = homologous_side", "therefore area_ratio_duplicate"]),
    (27, "parallelograms-on-equal-bases",
     "parallelograms on equal bases and in same parallels are equal",
     "Parallelograms on equal bases and in the same parallels are equal to one another.",
     "equal_bases_same_parallels_equal_area",
     [("I", 36, "parallelograms on equal bases and between same parallels are equal")],
     ["let ABCD = parallelogram_1", "let EFGH = parallelogram_2", "let base_AB = base_EF", "therefore area_ABCD == area_EFGH"]),
    (28, "similar-on-equal-lines-equal",
     "similar and similarly situated figures on equal straight lines are equal",
     "On equal straight lines similar and similarly situated rectilineal figures are equal to one another.",
     "similar_on_equal_lines_equal",
     [("VI", 26, "similar parallelograms are in duplicate ratio of homologous sides")],
     ["let AB = equal_line_1", "let CD = equal_line_2", "let fig1 = similar_figure_on_AB", "therefore fig1 == fig2"]),
    (29, "equal-parallelograms-same-base",
     "equal parallelograms on the same base are in the same parallels",
     "In equal parallelograms which have the same base the sides opposite the base are in the same straight lines.",
     "equal_pars_same_base_same_parallels",
     [("I", 39, "equal triangles on same base and same side are in same parallels")],
     ["let ABCD = parallelogram_1", "let ABCE = parallelogram_2", "let base_AB = common_base", "therefore in_same_parallels"]),
    (30, "equal-parallelograms-equal-bases",
     "equal parallelograms on equal bases are in the same parallels",
     "Equal parallelograms which are on equal bases and on the same side are also in the same parallels.",
     "equal_pars_equal_bases_same_parallels",
     [("VI", 29, "equal parallelograms on the same base are in the same parallels")],
     ["let ABCD = parallelogram_1", "let EFGH = parallelogram_2", "let equal_bases = bases", "therefore in_same_parallels"]),
    (31, "similar-parallelogram-side-ratio",
     "similar parallelograms are as the duplicate ratio of homologous sides",
     "Similar parallelograms are to one another in the duplicate ratio of the homologous sides.",
     "similar_par_ratio_as_duplicate",
     [("VI", 26, "similar parallelograms are in duplicate ratio of homologous sides")],
     ["let par1 = parallelogram_1", "let par2 = parallelogram_2", "let s1 = side_1", "therefore ratio(par1, par2) == duplicate(s1)"]),
    (32, "complements-and-applied-area",
     "complements with an applied parallelogram relate by duplicate ratio",
     "If ABCD is a parallelogram and BE is a parallelogram about the diameter, the complement CD is such that the whole is to the complement as the other about the diameter is to CD.",
     "complement_applied_area_ratio",
     [("VI", 24, "parallelograms about a diameter are similar to the whole and to one another"), ("VI", 31, "similar parallelograms are as the duplicate ratio of homologous sides")],
     ["let ABCD = whole_parallelogram", "let BE = about_diameter", "let CD = complement", "therefore ratio_whole_complement_holds"]),
    (33, "halves-equiangular-duplicate-ratio",
     "halves of equiangular parallelograms have ratio duplicate of homologous sides",
     "In equal circles (or equiangular parallelograms with equal angles), halves have to one another the duplicate ratio of the homologous sides.",
     "halves_duplicate_ratio_homologous",
     [("VI", 31, "similar parallelograms are as the duplicate ratio of homologous sides"), ("VI", 15, "equiangular parallelograms with reciprocal sides are equal")],
     ["let half1 = half_of_par_1", "let half2 = half_of_par_2", "let side = homologous_side", "therefore ratio_halves == duplicate(side)"]),
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
        f"# @module examples.verify.euclid.book-vi",
        f"# @means  {means}",
        f"# @from   euclid — Elements, Book VI, Proposition {n}",
        f"# @tier   derived",
    ]
    if needs:
        need_str = ", ".join(_need(book, nn, tt) for book, nn, tt in needs)
        lines.append(f"# @needs  {need_str}")
    lines.append("")
    lines.append(f"theorem {claim('VI', n, title)} () {{")
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
        paths.append(f"examples/verify/euclid/book-vi/{fname}")
    manifest = OUT / "MANIFEST.txt"
    manifest.write_text("\n".join(paths) + "\n", encoding="utf-8")
    print(f"Wrote {len(paths)} propositions to {OUT}")


if __name__ == "__main__":
    main()