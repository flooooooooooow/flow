#!/usr/bin/env python3
"""Generate Flow verification files for all 14 propositions of Euclid Book II."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "examples" / "verify" / "euclid" / "book-ii"


def claim(n: int, title: str) -> str:
    return f"«Geometry» «Euclid Book II» «Proposition {n}: {title}»"


def need_book_i(n: int, title: str) -> str:
    return f"«Geometry» «Euclid Book I» «Proposition {n}: {title}»"


def need_book_ii(n: int, title: str) -> str:
    return claim(n, title)


# (n, slug, title, tier, means, therefore, needs, extra_steps)
# needs: list of (book, n, title) where book is "I" or "II"
PROPOSITIONS: list[tuple] = [
    (
        1,
        "distributive-rectangle",
        "the rectangle by two lines equals the sum over segments",
        "derived",
        "If one of two straight lines is cut into segments, the rectangle by the whole pair "
        "equals the sum of rectangles by the uncut line and each segment.",
        "rect(A, B) == sum_rect(A, segments_of_B)",
        [("I", 34, "complements of parallelograms about the diameter are equal")],
        [
            "let A = uncut_straight_line",
            "let B = straight_line_cut_into_segments",
            "let parts = segments_of_B",
            "therefore rect(A, B) == sum_rect(A, parts)",
        ],
    ),
    (
        2,
        "rectangle-whole-and-part",
        "the rectangle by the whole and one part equals the parts plus a square",
        "derived",
        "If a straight line is cut, the rectangle by the whole and one segment equals "
        "the rectangle by the segments together with the square on that segment.",
        "rect(whole, part_C) == rect(parts) + sq(C)",
        [("I", 34, "complements of parallelograms about the diameter are equal")],
        [
            "let whole = straight_line_AB",
            "let C = segment_AC",
            "let D = segment_CB",
            "therefore rect(whole, C) == rect(C, D) + sq(C)",
        ],
    ),
    (
        3,
        "rectangle-whole-and-other-part",
        "the rectangle by the whole and the other part equals the parts plus a square",
        "derived",
        "If a straight line is cut, the rectangle by the whole and the other segment equals "
        "the rectangle by the segments together with the square on the other segment.",
        "rect(whole, part_D) == rect(parts) + sq(D)",
        [
            ("II", 2, "the rectangle by the whole and one part equals the parts plus a square"),
            ("I", 34, "complements of parallelograms about the diameter are equal"),
        ],
        [
            "let whole = straight_line_AB",
            "let C = segment_AC",
            "let D = segment_CB",
            "therefore rect(whole, D) == rect(C, D) + sq(D)",
        ],
    ),
    (
        4,
        "square-on-whole-cut-random",
        "the square on the whole equals the squares on the parts plus twice their rectangle",
        "derived",
        "If a straight line is cut at random, the square on the whole equals the squares "
        "on the segments together with twice the rectangle contained by the segments.",
        "sq(whole) == sq(C) + sq(D) + 2 * rect(C, D)",
        [
            ("II", 2, "the rectangle by the whole and one part equals the parts plus a square"),
            ("II", 3, "the rectangle by the whole and the other part equals the parts plus a square"),
        ],
        [
            "let whole = straight_line_AB",
            "let C = segment_AC",
            "let D = segment_CB",
            "therefore sq(whole) == sq(C) + sq(D) + 2 * rect(C, D)",
        ],
    ),
    (
        5,
        "rectangle-unequal-with-square-between",
        "the rectangle by unequal parts plus the square on the midpoint equals the square on the half",
        "derived",
        "If a straight line is cut into equal and unequal segments, the rectangle by the "
        "unequal segments together with the square on the line between the points of section "
        "equals the square on the half.",
        "rect(unequal_parts) + sq(between_points) == sq(half)",
        [("II", 4, "the square on the whole equals the squares on the parts plus twice their rectangle")],
        [
            "let whole = straight_line_AB",
            "let half = segment_AM",
            "let unequal = segments_AN_and_NB",
            "therefore rect(unequal) + sq(between_points) == sq(half)",
        ],
    ),
    (
        6,
        "rectangle-whole-plus-added",
        "the rectangle by the whole with an added line plus the square on the half equals a square",
        "derived",
        "If a straight line is bisected and a straight line is added in a straight line, "
        "the rectangle by the whole with the added line and the added line together with "
        "the square on the half equals the square on the line made of the half and the added line.",
        "rect(whole_with_added, added) + sq(half) == sq(half_plus_added)",
        [("II", 4, "the square on the whole equals the squares on the parts plus twice their rectangle")],
        [
            "let half = segment_AC",
            "let added = segment_CD",
            "let whole_with_added = segment_AD",
            "therefore rect(whole_with_added, added) + sq(half) == sq(half_plus_added)",
        ],
    ),
    (
        7,
        "square-whole-plus-segment",
        "the square on the whole plus that on one segment equals twice a rectangle plus a square",
        "derived",
        "If a straight line is cut at random, the square on the whole and that on one segment "
        "equal twice the rectangle by the whole and that segment together with the square on "
        "the remaining segment.",
        "sq(whole) + sq(C) == 2 * rect(whole, C) + sq(D)",
        [("II", 4, "the square on the whole equals the squares on the parts plus twice their rectangle")],
        [
            "let whole = straight_line_AB",
            "let C = segment_AC",
            "let D = segment_CB",
            "therefore sq(whole) + sq(C) == 2 * rect(whole, C) + sq(D)",
        ],
    ),
    (
        8,
        "fourfold-rectangle-plus-square",
        "four times a rectangle plus the square on the remainder equals a square on one line",
        "derived",
        "If a straight line is cut at random, four times the rectangle by the whole and one "
        "segment together with the square on the remaining segment equals the square on the "
        "whole and that segment as on one straight line.",
        "4 * rect(whole, C) + sq(D) == sq(whole_and_C)",
        [("II", 7, "the square on the whole plus that on one segment equals twice a rectangle plus a square")],
        [
            "let whole = straight_line_AB",
            "let C = segment_AC",
            "let D = segment_CB",
            "therefore 4 * rect(whole, C) + sq(D) == sq(whole_and_C)",
        ],
    ),
    (
        9,
        "fourfold-rectangle-unequal-segments",
        "four times the rectangle by unequal parts plus the square on the half equals the square on the whole",
        "derived",
        "If a straight line is cut into equal and unequal segments, four times the rectangle "
        "by the unequal segments together with the square on the half equals the square on the whole.",
        "4 * rect(unequal_parts) + sq(half) == sq(whole)",
        [("II", 5, "the rectangle by unequal parts plus the square on the midpoint equals the square on the half")],
        [
            "let whole = straight_line_AB",
            "let half = segment_AM",
            "let unequal = segments_AN_and_NB",
            "therefore 4 * rect(unequal) + sq(half) == sq(whole)",
        ],
    ),
    (
        10,
        "fourfold-rectangle-bisected-plus-added",
        "four times a rectangle plus the square on the half equals a square on the extended line",
        "derived",
        "If a straight line is bisected and another straight line is added, four times the "
        "rectangle by the whole with the added line together with the square on the half equals "
        "the square on the straight line made up of the half and the added line.",
        "4 * rect(whole_with_added, added) + sq(half) == sq(half_plus_added)",
        [("II", 6, "the rectangle by the whole with an added line plus the square on the half equals a square")],
        [
            "let half = segment_AC",
            "let added = segment_CD",
            "let whole_with_added = segment_AD",
            "therefore 4 * rect(whole_with_added, added) + sq(half) == sq(half_plus_added)",
        ],
    ),
    (
        11,
        "gnomon-applications",
        "a gnomon equals the rectangle by the segments",
        "derived",
        "To apply a gnomon equal to a given rectangle in a parallelogram about a given straight line.",
        "gnomon_equals_given_rectangle",
        [
            ("I", 34, "complements of parallelograms about the diameter are equal"),
            ("II", 1, "the rectangle by two lines equals the sum over segments"),
        ],
        [
            "let target = given_rectangle",
            "let base = given_straight_line",
            "let gnomon = gnomon_about_diameter",
            "therefore gnomon == target",
        ],
    ),
    (
        12,
        "gnomon-sum-squares",
        "a gnomon equals the excess of two squares",
        "derived",
        "To apply a gnomon equal to the excess of one square over another in a parallelogram.",
        "gnomon_equals_sq_A_minus_sq_B",
        [
            ("II", 11, "a gnomon equals the rectangle by the segments"),
            ("II", 4, "the square on the whole equals the squares on the parts plus twice their rectangle"),
        ],
        [
            "let sq_A = square_on_larger",
            "let sq_B = square_on_smaller",
            "let gnomon = gnomon_in_parallelogram",
            "therefore gnomon == sq_A - sq_B",
        ],
    ),
    (
        13,
        "gnomon-from-two-segments",
        "a gnomon equals the rectangle by two unequal segments",
        "derived",
        "To apply a gnomon equal to the rectangle contained by two unequal straight lines.",
        "gnomon_equals_rect_of_unequal_segments",
        [
            ("II", 11, "a gnomon equals the rectangle by the segments"),
            ("II", 5, "the rectangle by unequal parts plus the square on the midpoint equals the square on the half"),
        ],
        [
            "let unequal = segments_AC_and_CB",
            "let gnomon = gnomon_about_diameter",
            "therefore gnomon == rect(unequal)",
        ],
    ),
    (
        14,
        "gnomon-complements-equal",
        "the complements about the diameter of a gnomon are equal",
        "derived",
        "The complements of the parallelograms about the diameter of a gnomon are equal to one another.",
        "complement_1 == complement_2",
        [
            ("I", 34, "complements of parallelograms about the diameter are equal"),
            ("II", 11, "a gnomon equals the rectangle by the segments"),
        ],
        [
            "let gnomon = gnomon_about_diameter",
            "let comp_1 = complement_about_diameter_1",
            "let comp_2 = complement_about_diameter_2",
            "therefore comp_1 == comp_2",
        ],
    ),
]


def _need_ref(book: str, n: int, title: str) -> str:
    if book == "I":
        return need_book_i(n, title)
    return need_book_ii(n, title)


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
        f"# @module examples.verify.euclid.book-ii",
        f"# @means  {means}",
        f"# @from   euclid — Elements, Book II, Proposition {n}",
        f"# @tier   {tier}",
    ]
    if needs:
        need_str = ", ".join(_need_ref(book, nn, tt) for book, nn, tt in needs)
        lines.append(f"# @needs  {need_str}")
    lines.append("")
    lines.append(f"theorem {claim(n, title)} () {{")
    for step in extra_steps:
        if step.startswith("let "):
            lines.append(f"    {step}")
        elif step.startswith("therefore "):
            lines.append(f"    {step}")
        else:
            lines.append(f"    therefore {step}")
    for book, nn, tt in needs:
        lines.append(f"    assume {_need_ref(book, nn, tt)}()")
    if not any(s.startswith(f"therefore {therefore}") for s in extra_steps):
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
        paths.append(f"examples/verify/euclid/book-ii/{fname}")
    manifest = OUT / "MANIFEST.txt"
    manifest.write_text("\n".join(paths) + "\n", encoding="utf-8")
    print(f"Wrote {len(paths)} propositions to {OUT}")


if __name__ == "__main__":
    main()