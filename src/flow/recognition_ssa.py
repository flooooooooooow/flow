"""Recognition-indexed refinement for SSA transformations.

IR-agnostic: SSA/FIR-G/MLIR adapters supply discrete refinement and
continuous recognition witnesses. With no continuous contracts, legality
is exactly the supplied discrete SSA refinement.
"""

from dataclasses import dataclass
from math import isfinite
from typing import Callable, Iterable, Optional, Sequence, Tuple

class RecognitionRefinementError(ValueError):
    pass

@dataclass(frozen=True)
class AttractorSignature:
    fixed_points: Tuple[Tuple[float, ...], ...] = ()
    basin_labels: Tuple[int, ...] = ()
    stability: Tuple[float, ...] = ()
    invariants: Tuple[float, ...] = ()

@dataclass(frozen=True)
class RecognitionContract:
    domain: str
    epsilon: float = 0.0
    weights: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    def __post_init__(self) -> None:
        if not isfinite(self.epsilon) or self.epsilon < 0.0:
            raise RecognitionRefinementError("epsilon must be finite and non-negative")
        if len(self.weights) != 4 or any((not isfinite(w) or w < 0.0) for w in self.weights):
            raise RecognitionRefinementError("weights must be four finite non-negative values")

@dataclass(frozen=True)
class RecognitionWitness:
    domain: str
    distance: float
    epsilon: float
    @property
    def preserved(self) -> bool:
        return self.distance <= self.epsilon

@dataclass(frozen=True)
class RefinementCertificate:
    discrete_refinement: bool
    witnesses: Tuple[RecognitionWitness, ...]
    @property
    def preserved(self) -> bool:
        return self.discrete_refinement and all(w.preserved for w in self.witnesses)

def _vector_distance(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b):
        return float("inf")
    return max((abs(float(x) - float(y)) for x, y in zip(a, b)), default=0.0)

def _point_set_distance(a: Sequence[Sequence[float]], b: Sequence[Sequence[float]]) -> float:
    if not a and not b:
        return 0.0
    if not a or not b:
        return float("inf")
    def directed(xs: Sequence[Sequence[float]], ys: Sequence[Sequence[float]]) -> float:
        return max(min(_vector_distance(x, y) for y in ys) for x in xs)
    return max(directed(a, b), directed(b, a))

def attractor_distance(before: AttractorSignature, after: AttractorSignature, weights: Sequence[float] = (1.0, 1.0, 1.0, 1.0)) -> float:
    if tuple(before.basin_labels) != tuple(after.basin_labels):
        return float("inf")
    components = (_point_set_distance(before.fixed_points, after.fixed_points), 0.0, _vector_distance(before.stability, after.stability), _vector_distance(before.invariants, after.invariants))
    return max((float(w) * d for w, d in zip(weights, components)), default=0.0)

def check_recognition_refinement(before: object, after: object, *, discrete_refines: Callable[[object, object], bool], contracts: Iterable[RecognitionContract] = (), observe: Optional[Callable[[object, str], AttractorSignature]] = None) -> RefinementCertificate:
    discrete = bool(discrete_refines(before, after))
    contracts = tuple(contracts)
    if contracts and observe is None:
        raise RecognitionRefinementError("recognition contracts require an observation function")
    witnesses = []
    for contract in contracts:
        before_sig = observe(before, contract.domain)  # type: ignore[misc]
        after_sig = observe(after, contract.domain)  # type: ignore[misc]
        distance = attractor_distance(before_sig, after_sig, contract.weights)
        witnesses.append(RecognitionWitness(contract.domain, distance, contract.epsilon))
    return RefinementCertificate(discrete, tuple(witnesses))

def assert_recognition_refinement(before: object, after: object, *, discrete_refines: Callable[[object, object], bool], contracts: Iterable[RecognitionContract] = (), observe: Optional[Callable[[object, str], AttractorSignature]] = None) -> RefinementCertificate:
    certificate = check_recognition_refinement(before, after, discrete_refines=discrete_refines, contracts=contracts, observe=observe)
    if certificate.preserved:
        return certificate
    failures = []
    if not certificate.discrete_refinement:
        failures.append("discrete SSA refinement")
    failures.extend(f"{w.domain} ({w.distance:g} > {w.epsilon:g})" for w in certificate.witnesses if not w.preserved)
    raise RecognitionRefinementError("recognition-indexed refinement violated: " + ", ".join(failures))
