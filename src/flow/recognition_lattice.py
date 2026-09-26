"""Relations between recognition domains."""

from dataclasses import dataclass
from typing import Any, Iterable, Optional, Tuple

from .recognition import recognition_signature


@dataclass(frozen=True)
class RecognitionResidual:
    erased_by: str
    retained_by: str
    coarse_signature: tuple
    before_fine: tuple
    after_fine: tuple


@dataclass(frozen=True)
class RefinementCounterexample:
    left_index: int
    right_index: int
    fine: str
    coarse: str


def recognition_equivalent(left: Any, right: Any, domain: str) -> bool:
    return recognition_signature(left, domain) == recognition_signature(right, domain)


def recognition_residual(before: Any, after: Any, erased_by: str, retained_by: str) -> Optional[RecognitionResidual]:
    coarse_before = recognition_signature(before, erased_by)
    coarse_after = recognition_signature(after, erased_by)
    if coarse_before != coarse_after:
        return None
    fine_before = recognition_signature(before, retained_by)
    fine_after = recognition_signature(after, retained_by)
    if fine_before == fine_after:
        return None
    return RecognitionResidual(erased_by, retained_by, coarse_before, fine_before, fine_after)


def refinement_counterexamples(corpus: Iterable[Any], fine: str, coarse: str) -> Tuple[RefinementCounterexample, ...]:
    items = tuple(corpus)
    fine_sigs = tuple(recognition_signature(item, fine) for item in items)
    coarse_sigs = tuple(recognition_signature(item, coarse) for item in items)
    failures = []
    for left in range(len(items)):
        for right in range(left + 1, len(items)):
            if fine_sigs[left] == fine_sigs[right] and coarse_sigs[left] != coarse_sigs[right]:
                failures.append(RefinementCounterexample(left, right, fine, coarse))
    return tuple(failures)


def refines_on_corpus(corpus: Iterable[Any], fine: str, coarse: str) -> bool:
    return not refinement_counterexamples(corpus, fine, coarse)
