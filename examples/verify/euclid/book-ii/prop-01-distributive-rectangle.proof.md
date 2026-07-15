# examples.verify.euclid.book-ii

*If one of two straight lines is cut into segments, the rectangle by the whole pair equals the sum of rectangles by the uncut line and each segment.*

**Source.** euclid — Elements, Book II, Proposition 1

## Derived fact 1 — If one of two straight lines is cut into segments, the rectangle by the whole pair equals the sum of rectangles by the uncut line and each segment

**Coordinate.** the Euclidean plane · Euclid Book II · Proposition 1: the rectangle by two lines equals the sum over segments · **Derived fact**

*Source: euclid — Elements, Book II, Proposition 1*

*Built on: proposition 34: complements of parallelograms about the diameter are equal, for Book I of the Elements in on the Euclidean plane*

> **Goal.** If one of two straight lines is cut into segments, the rectangle by the whole pair equals the sum of rectangles by the uncut line and each segment
>
> $$rect(A, B) = \text{sum rect}(A, \text{segments of B})$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that proposition 1: the rectangle by two lines equals the sum over segments for Euclid Book II the Euclidean plane. |  |  |
| ② | Let A = uncut_straight_line. |  |  |
| ③ | Let B = straight_line_cut_into_segments. |  |  |
| ④ | Let parts = segments_of_B. |  |  |
| ⑤ | From step 2, step 3, and step 4, we can deduce that rect(A, B) equals sum rect(A, parts). | ⑤ | $rect(A, B) = \text{sum rect}(A, parts)$ |
| ⑥ | We invoke the derived fact governing Book I of the Elements in the Euclidean plane: proposition 34: complements of parallelograms about the diameter are equal, for Book I of the Elements in on the Euclidean plane. |  |  |
| ⑦ | From step 6, this implies rect(A, B) equals sum rect(A, segments of B). Hence proven. | ⑦ | $rect(A, B) = \text{sum rect}(A, \text{segments of B})$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |
| ⑦ | step 6 |

`the Euclidean plane · Euclid Book II · Proposition 1: the rectangle by two lines equals the sum over segments`
