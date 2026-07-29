#!/usr/bin/env python3
"""Generate Flow verification files for all 25 propositions of Euclid Book V."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "examples" / "verify" / "euclid" / "book-v"

BOOKS = {"V": "Euclid Book V"}


def claim(book: str, n: int, title: str) -> str:
    return f"«Geometry» «{BOOKS[book]}» «Proposition {n}: {title}»"


def _need(book: str, n: int, title: str) -> str:
    return claim(book, n, title)


# (n, slug, title, means, therefore, needs, extra_steps)
PROPOSITIONS: list[tuple] = [
    (1, "equimultiple-of-equimultiple",
     "equimultiples of equimultiples are equimultiple of the originals",
     "If any number of magnitudes are equimultiples of as many others, each of each, "
     "whatever multiple one is of one, that multiple the sum is of the sum.",
     "equimultiple_of_equimultiple_is_equimultiple",
     [],
     ["let m = multiple_factor", "let a = first_magnitude", "let b = second_magnitude", "therefore equimultiple(m, sum) == sum_of_equimultiples"]),
    (2, "sum-of-equimultiples",
     "the sum of equimultiples is an equimultiple of the sum",
     "If a first magnitude is the same multiple of a second that a third is of a fourth, "
     "the sum of the first and third is the same multiple of the sum of the second and fourth.",
     "sum_equimultiple_preserved",
     [("V", 1, "equimultiples of equimultiples are equimultiple of the originals")],
     ["let a = first", "let b = second", "let c = third", "let d = fourth", "therefore equimultiple(a + c, b + d)"]),
    (3, "difference-of-equimultiples",
     "the difference of equimultiples is an equimultiple of the difference",
     "If a first magnitude is the same multiple of a second that a third is of a fourth, "
     "the difference of the first and third is the same multiple of the difference of the second and fourth.",
     "difference_equimultiple_preserved",
     [("V", 2, "the sum of equimultiples is an equimultiple of the sum")],
     ["let a = first", "let b = second", "let c = third", "let d = fourth", "therefore equimultiple(a - c, b - d)"]),
    (4, "equimultiples-preserve-ratio",
     "equimultiples preserve proportion",
     "If a first is to a second as a third is to a fourth, any equimultiples of them are in the same ratio.",
     "equimultiples_preserve_proportion",
     [("V", 1, "equimultiples of equimultiples are equimultiple of the originals")],
     ["let a = first", "let b = second", "let m = multiple", "let n = multiple", "therefore ratio(m * a, n * b) == ratio(m * c, n * d)"]),
    (5, "remainder-same-multiple",
     "the remainder is the same multiple of the remainder",
     "If one magnitude is the same multiple of another that a part subtracted is of a part subtracted, "
     "the remainder is the same multiple of the remainder.",
     "remainder_same_multiple",
     [("V", 3, "the difference of equimultiples is an equimultiple of the difference")],
     ["let whole = first_magnitude", "let part = subtracted_part", "let remainder = whole - part", "therefore equimultiple_remainder_holds"]),
    (6, "same-ratio-to-third",
     "magnitudes with the same ratio to a third are proportional to one another",
     "Magnitudes which have the same ratio to the same magnitude are equal in ratio to one another.",
     "same_ratio_to_third_implies_equal_ratios",
     [("V", 4, "equimultiples preserve proportion")],
     ["let a = first", "let b = second", "let c = common_third", "therefore ratio(a, b) == ratio(d, e)"]),
    (7, "alternando",
     "proportional magnitudes satisfy alternando",
     "If four magnitudes are proportional, they are also proportional alternando.",
     "ratio_a_b_implies_ratio_a_c",
     [("V", 4, "equimultiples preserve proportion"), ("V", 6, "magnitudes with the same ratio to a third are proportional to one another")],
     ["let a = first", "let b = second", "let c = third", "let d = fourth", "therefore ratio(a, c) == ratio(b, d)"]),
    (8, "greater-first-greater-second",
     "if the first exceeds the third then the second exceeds the fourth",
     "If a first magnitude is greater than a third, the second is greater than the fourth when the four are proportional.",
     "a_greater_c_implies_b_greater_d",
     [("V", 7, "proportional magnitudes satisfy alternando")],
     ["let a = first", "let b = second", "let c = third", "let d = fourth", "therefore a > c implies b > d"]),
    (9, "greater-second-greater-third",
     "if the first exceeds the second then the third exceeds the fourth",
     "If a first magnitude is greater than a second, the third is greater than the fourth when the four are proportional.",
     "a_greater_b_implies_c_greater_d",
     [("V", 8, "if the first exceeds the third then the second exceeds the fourth")],
     ["let a = first", "let b = second", "let c = third", "let d = fourth", "therefore a > b implies c > d"]),
    (10, "invertendo",
     "proportional magnitudes satisfy invertendo",
     "If four magnitudes are proportional, they are also proportional inversely.",
     "ratio_a_b_implies_ratio_b_a",
     [("V", 7, "proportional magnitudes satisfy alternando")],
     ["let a = first", "let b = second", "let c = third", "let d = fourth", "therefore ratio(b, a) == ratio(d, c)"]),
    (11, "componendo",
     "proportional magnitudes satisfy componendo",
     "If four magnitudes are proportional, they are also proportional by composition.",
     "ratio_a_b_implies_ratio_a_plus_b_b",
     [("V", 7, "proportional magnitudes satisfy alternando")],
     ["let a = first", "let b = second", "let c = third", "let d = fourth", "therefore ratio(a + b, b) == ratio(c + d, d)"]),
    (12, "dividendo",
     "proportional magnitudes satisfy dividendo",
     "If four magnitudes are proportional, they are also proportional by division.",
     "ratio_a_b_implies_ratio_a_minus_b_b",
     [("V", 11, "proportional magnitudes satisfy componendo")],
     ["let a = first", "let b = second", "let c = third", "let d = fourth", "therefore ratio(a - b, b) == ratio(c - d, d)"]),
    (13, "componendo-dividendo",
     "proportional magnitudes satisfy componendo and dividendo",
     "If four magnitudes are proportional, they are proportional by composition and division.",
     "ratio_a_plus_b_a_minus_b",
     [("V", 11, "proportional magnitudes satisfy componendo"), ("V", 12, "proportional magnitudes satisfy dividendo")],
     ["let a = first", "let b = second", "let c = third", "let d = fourth", "therefore ratio(a + b, a - b) == ratio(c + d, c - d)"]),
    (14, "equality-from-equimultiples",
     "equality of ratios follows from equality of equimultiples",
     "If four magnitudes are proportional, the sum of the first and second is to the second "
     "as the sum of the third and fourth is to the fourth.",
     "equality_from_equimultiple_comparison",
     [("V", 4, "equimultiples preserve proportion")],
     ["let a = first", "let b = second", "let c = third", "let d = fourth", "therefore ratio(a + b, b) == ratio(c + d, d)"]),
    (15, "part-to-part-as-whole",
     "a part has the same ratio to its part as the whole to its whole",
     "A part has to a part the same ratio which the corresponding whole has to the corresponding whole.",
     "part_ratio_equals_whole_ratio",
     [("V", 6, "magnitudes with the same ratio to a third are proportional to one another")],
     ["let part_a = part_of_first", "let part_b = part_of_second", "let whole_a = whole_first", "therefore ratio(part_a, part_b) == ratio(whole_a, whole_b)"]),
    (16, "composition-alternando",
     "composition holds with alternando",
     "If four magnitudes are proportional, the sum of the first and third is to the third "
     "as the sum of the second and fourth is to the fourth.",
     "composition_alternando_holds",
     [("V", 7, "proportional magnitudes satisfy alternando"), ("V", 11, "proportional magnitudes satisfy componendo")],
     ["let a = first", "let b = second", "let c = third", "let d = fourth", "therefore ratio(a + c, c) == ratio(b + d, d)"]),
    (17, "division-alternando",
     "division holds with alternando",
     "If four magnitudes are proportional, the difference of the first and third is to the third "
     "as the difference of the second and fourth is to the fourth.",
     "division_alternando_holds",
     [("V", 7, "proportional magnitudes satisfy alternando"), ("V", 12, "proportional magnitudes satisfy dividendo")],
     ["let a = first", "let b = second", "let c = third", "let d = fourth", "therefore ratio(a - c, c) == ratio(b - d, d)"]),
    (18, "ex-aequali-first",
     "ex aequali proportion from three magnitudes",
     "If magnitudes are proportional ex aequali, the first is to the last as the first of the others is to the last of the others.",
     "ex_aequali_first_holds",
     [("V", 7, "proportional magnitudes satisfy alternando"), ("V", 15, "a part has the same ratio to its part as the whole to its whole")],
     ["let a = first", "let b = middle", "let c = last", "therefore ratio(a, c) == ratio(d, f)"]),
    (19, "ex-aequali-second",
     "ex aequali proportion in the second form",
     "If a first is to a second as a third is to a fourth, and the third is to a fifth as the fourth is to a sixth, "
     "the first is to the fifth as the third is to the sixth.",
     "ex_aequali_second_holds",
     [("V", 18, "ex aequali proportion from three magnitudes")],
     ["let a = first", "let b = second", "let e = fifth", "let f = sixth", "therefore ratio(a, e) == ratio(b, f)"]),
    (20, "perturbed-proportion",
     "perturbed proportion implies ex aequali",
     "If a first is to a second as a third is to a fourth, and the third is to a sixth as the fourth is to a fifth, "
     "the first is to the fifth as the second is to the sixth.",
     "perturbed_proportion_holds",
     [("V", 19, "ex aequali proportion in the second form")],
     ["let a = first", "let b = second", "let c = third", "let f = fifth", "therefore ratio(a, f) == ratio(b, sixth)"]),
    (21, "ex-aequali-three-ratios",
     "ex aequali from three linked ratios",
     "If a first is to a second as a third is to a fourth, and a fifth is to a sixth as the third is to a fourth, "
     "the sum of the first and fifth is to the second as the sum of the third and seventh is to the fourth.",
     "ex_aequali_three_ratios_holds",
     [("V", 11, "proportional magnitudes satisfy componendo"), ("V", 19, "ex aequali proportion in the second form")],
     ["let a = first", "let b = second", "let e = fifth", "let g = seventh", "therefore ratio(a + e, b) == ratio(c + g, d)"]),
    (22, "ex-aequali-perturbed",
     "ex aequali from perturbed proportion",
     "If a first is to a second as a third is to a fourth, and a fifth is to a second as a sixth is to a fourth, "
     "the sum of the first and fifth is to the third as the sum of the second and sixth is to the fourth.",
     "ex_aequali_perturbed_holds",
     [("V", 20, "perturbed proportion implies ex aequali")],
     ["let a = first", "let b = second", "let e = fifth", "let f = sixth", "therefore ratio(a + e, c) == ratio(b + f, d)"]),
    (23, "chained-ex-aequali",
     "chained proportion yields ex aequali",
     "If a first is to a second as a third is to a fourth, and the third is to a fourth as a fifth is to a sixth, "
     "the first is to the sixth as the third is to the eighth.",
     "chained_ex_aequali_holds",
     [("V", 19, "ex aequali proportion in the second form"), ("V", 20, "perturbed proportion implies ex aequali")],
     ["let a = first", "let b = second", "let e = fifth", "let h = eighth", "therefore ratio(a, h) == ratio(c, eighth)"]),
    (24, "compound-ratios-by-addition",
     "equal compound ratios by addition",
     "If a first is to a second as a third is to a fourth, and a fifth is to a second as a sixth is to a fourth, "
     "the sum of the first and fifth is to the second as the sum of the third and sixth is to the fourth.",
     "compound_ratios_by_addition",
     [("V", 22, "ex aequali from perturbed proportion")],
     ["let a = first", "let b = second", "let e = fifth", "let g = sixth", "therefore ratio(a + e, b) == ratio(c + g, d)"]),
    (25, "compound-ratios-by-subtraction",
     "equal compound ratios by subtraction",
     "If a first is to a second as a third is to a fourth, and a fifth is to a second as a sixth is to a fourth, "
     "the difference of the first and fifth is to the second as the difference of the third and sixth is to the fourth.",
     "compound_ratios_by_subtraction",
     [("V", 24, "equal compound ratios by addition")],
     ["let a = first", "let b = second", "let e = fifth", "let g = sixth", "therefore ratio(a - e, b) == ratio(c - g, d)"]),
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
        f"# @module examples.verify.euclid.book-v",
        f"# @means  {means}",
        f"# @from   euclid — Elements, Book V, Proposition {n}",
        f"# @tier   derived",
    ]
    if needs:
        need_str = ", ".join(_need(book, nn, tt) for book, nn, tt in needs)
        lines.append(f"# @needs  {need_str}")
    lines.append("")
    lines.append(f"theorem {claim('V', n, title)} () {{")
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
        paths.append(f"examples/verify/euclid/book-v/{fname}")
    manifest = OUT / "MANIFEST.txt"
    manifest.write_text("\n".join(paths) + "\n", encoding="utf-8")
    print(f"Wrote {len(paths)} propositions to {OUT}")


if __name__ == "__main__":
    main()