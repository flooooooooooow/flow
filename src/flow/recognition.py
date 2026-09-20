"""Recognition-relative denotational semantics for Flow.

A flow has one latent denotation and several observer-relative projections.
A `recognize { ... }` block selects which projections a transformation must
preserve. Compiler passes can compare the projections before and after a
rewrite with `assert_recognition_preserved`.

This module intentionally depends only on Python's dataclass protocol rather
than parser classes. That keeps it usable by later IRs and avoids making the
front end the privileged semantic representation.
"""

from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Dict, Iterable, Optional, Tuple


RECOGNITION_DOMAINS: Tuple[str, ...] = (
    "numerical",
    "realtime",
    "causal",
    "safety",
    "memory",
)

_NON_SEMANTIC_FIELDS = {
    "line",
    "location",
    "text",
    "column",
    "end_line",
    "end_column",
}


class RecognitionError(ValueError):
    """Raised when a recognition contract is invalid or is not preserved."""


@dataclass(frozen=True)
class FlowDenotation:
    """Canonical semantic data extracted from a flow declaration.

    The fields deliberately separate the latent system from any one compiler
    representation. Recognition domains below are projections of this object.
    """

    state_schema: tuple
    input_schema: tuple
    output_schema: tuple
    param_schema: tuple
    initial_state: tuple
    param_defaults: tuple
    dynamics: tuple
    output_maps: tuple
    timing: tuple
    events: tuple
    discrete_updates: tuple
    constraints: tuple
    composition: tuple


@dataclass(frozen=True)
class RecognitionDrift:
    """One observer-relative semantic difference between two flow versions."""

    domain: str
    before: tuple
    after: tuple


def _freeze(value: Any) -> Any:
    """Convert parser/IR dataclasses into deterministic semantic tuples."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, tuple):
        return tuple(_freeze(v) for v in value)
    if isinstance(value, list):
        return tuple(_freeze(v) for v in value)
    if isinstance(value, dict):
        return tuple(
            (str(k), _freeze(v))
            for k, v in sorted(value.items(), key=lambda item: str(item[0]))
        )
    if is_dataclass(value):
        return (
            type(value).__name__,
            tuple(
                (f.name, _freeze(getattr(value, f.name)))
                for f in fields(value)
                if f.name not in _NON_SEMANTIC_FIELDS
            ),
        )
    raise TypeError(
        f"cannot form a semantic signature for {type(value).__name__}"
    )


def _schema(items: Iterable[Any]) -> tuple:
    return tuple(
        (item.name, _freeze(item.type))
        for item in items
    )


def denotation(flow: Any) -> FlowDenotation:
    """Return the representation-independent semantic object for a flow."""
    states = tuple(getattr(flow, "states", ()) or ())
    inputs = tuple(getattr(flow, "inputs", ()) or ())
    outputs = tuple(getattr(flow, "outputs", ()) or ())
    params = tuple(getattr(flow, "params", ()) or ())
    solver = getattr(flow, "solver", None)
    everys = tuple(getattr(flow, "everys", ()) or ())
    whens = tuple(getattr(flow, "whens", ()) or ())
    alwayses = tuple(getattr(flow, "alwayses", ()) or ())
    nevers = tuple(getattr(flow, "nevers", ()) or ())
    children = tuple(getattr(flow, "children", ()) or ())
    connections = tuple(getattr(flow, "connections", ()) or ())

    return FlowDenotation(
        state_schema=_schema(states),
        input_schema=_schema(inputs),
        output_schema=_schema(outputs),
        param_schema=_schema(params),
        initial_state=tuple(
            (state.name, _freeze(getattr(state, "initializer", None)))
            for state in states
        ),
        param_defaults=tuple(
            (param.name, _freeze(getattr(param, "initializer", None)))
            for param in params
        ),
        dynamics=tuple(
            (evolve.target, _freeze(evolve.expr))
            for evolve in (getattr(flow, "evolves", ()) or ())
        ),
        output_maps=tuple(
            (output.name, _freeze(getattr(output, "expr", None)))
            for output in outputs
        ),
        timing=(
            _freeze(solver),
            tuple(getattr(every, "period_ns", None) for every in everys),
        ),
        events=_freeze(whens),
        discrete_updates=_freeze(everys),
        constraints=(
            _freeze(alwayses),
            _freeze(nevers),
        ),
        composition=(
            _freeze(children),
            _freeze(connections),
        ),
    )


def _projection(d: FlowDenotation, domain: str) -> tuple:
    if domain == "numerical":
        return (
            d.state_schema,
            d.input_schema,
            d.output_schema,
            d.param_schema,
            d.initial_state,
            d.param_defaults,
            d.dynamics,
            d.output_maps,
            d.timing,
            d.events,
            d.discrete_updates,
        )
    if domain == "realtime":
        return (
            d.state_schema,
            d.input_schema,
            d.output_schema,
            d.param_schema,
            d.timing,
            d.events,
            d.discrete_updates,
            d.composition,
        )
    if domain == "causal":
        return (
            d.state_schema,
            d.input_schema,
            d.output_schema,
            d.dynamics,
            d.output_maps,
            d.events,
            d.discrete_updates,
            d.composition,
        )
    if domain == "safety":
        return (
            d.state_schema,
            d.input_schema,
            d.param_schema,
            d.dynamics,
            d.events,
            d.discrete_updates,
            d.constraints,
        )
    if domain == "memory":
        return (
            d.state_schema,
            d.input_schema,
            d.output_schema,
            d.param_schema,
            tuple(len(x) for x in (d.events, d.discrete_updates)),
            d.composition,
        )
    raise RecognitionError(
        f"unknown recognition domain '{domain}'; valid domains: "
        + ", ".join(RECOGNITION_DOMAINS)
    )


def declared_domains(flow: Any) -> tuple:
    declaration = getattr(flow, "recognition", None)
    if declaration is None:
        return ()
    return tuple(getattr(declaration, "domains", ()) or ())


def validate_recognition_contract(flow: Any) -> None:
    """Validate the domains named by a flow's recognize block."""
    seen = set()
    for domain in declared_domains(flow):
        if domain not in RECOGNITION_DOMAINS:
            raise RecognitionError(
                f"unknown recognition domain '{domain}' in flow "
                f"'{getattr(flow, 'name', '<anonymous>')}'; valid domains: "
                + ", ".join(RECOGNITION_DOMAINS)
            )
        if domain in seen:
            raise RecognitionError(
                f"recognition domain '{domain}' appears twice in flow "
                f"'{getattr(flow, 'name', '<anonymous>')}'"
            )
        seen.add(domain)


def recognition_signature(flow: Any, domain: str) -> tuple:
    """Project a flow's denotation through one recognition domain."""
    return _projection(denotation(flow), domain)


def recognition_manifest(
    flow: Any,
    domains: Optional[Iterable[str]] = None,
) -> Dict[str, tuple]:
    """Return canonical signatures for declared or explicitly named domains."""
    if domains is None:
        domains = declared_domains(flow)
    return {
        domain: recognition_signature(flow, domain)
        for domain in domains
    }


def compare_recognition(
    before: Any,
    after: Any,
    domains: Optional[Iterable[str]] = None,
) -> Tuple[RecognitionDrift, ...]:
    """Return every recognition domain whose observable meaning changed."""
    if domains is None:
        domains = declared_domains(before)
    drifts = []
    for domain in domains:
        before_sig = recognition_signature(before, domain)
        after_sig = recognition_signature(after, domain)
        if before_sig != after_sig:
            drifts.append(RecognitionDrift(domain, before_sig, after_sig))
    return tuple(drifts)


def assert_recognition_preserved(
    before: Any,
    after: Any,
    domains: Optional[Iterable[str]] = None,
) -> None:
    """Reject a transformation that changes a protected semantic projection."""
    drifts = compare_recognition(before, after, domains)
    if not drifts:
        return
    changed = ", ".join(drift.domain for drift in drifts)
    raise RecognitionError(
        "recognition contract violated; semantic drift in: " + changed
    )
