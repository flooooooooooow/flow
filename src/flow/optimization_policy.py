"""Recognition-safe optimization policy layer."""

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Optional, Protocol, Tuple

from .recognition import compare_recognition


@dataclass(frozen=True)
class LoweringCandidate:
    name: str
    backend: str
    program: Any
    estimated_cost: float
    provenance: str = "heuristic"
    confidence: Optional[float] = None


@dataclass(frozen=True)
class CandidateEvaluation:
    candidate: LoweringCandidate
    admissible: bool
    changed_domains: Tuple[str, ...]
    score: float


class OptimizationPolicy(Protocol):
    def score(self, candidate: LoweringCandidate) -> float:
        ...


@dataclass(frozen=True)
class CostPolicy:
    def score(self, candidate: LoweringCandidate) -> float:
        return -candidate.estimated_cost


@dataclass(frozen=True)
class CallablePolicy:
    fn: Callable[[LoweringCandidate], float]

    def score(self, candidate: LoweringCandidate) -> float:
        return float(self.fn(candidate))


def evaluate_candidates(source: Any, candidates: Iterable[LoweringCandidate], protected_domains: Iterable[str], policy: OptimizationPolicy) -> Tuple[CandidateEvaluation, ...]:
    domains = tuple(protected_domains)
    evaluations = []
    for candidate in candidates:
        drift = compare_recognition(source, candidate.program, domains)
        admissible = not drift
        score = policy.score(candidate) if admissible else float("-inf")
        evaluations.append(CandidateEvaluation(candidate, admissible, tuple(item.domain for item in drift), score))
    return tuple(evaluations)


def choose_candidate(source: Any, candidates: Iterable[LoweringCandidate], protected_domains: Iterable[str], policy: OptimizationPolicy) -> Optional[CandidateEvaluation]:
    admissible = tuple(item for item in evaluate_candidates(source, candidates, protected_domains, policy) if item.admissible)
    if not admissible:
        return None
    return max(admissible, key=lambda item: item.score)
