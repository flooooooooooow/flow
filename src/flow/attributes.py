"""Function attribute vocabulary shared by the type checker and the C backend.

Attributes are written `@name` or `@name(arg, ...)` in front of a `function`
declaration.  The parser flattens each one into a string: `"inline"`,
`"target(avx2,fma)"`.  This module is the single place that knows which names
exist, what they mean, and how the code-generation attributes lower to C.

See docs/LANGUAGE_SPEC.md §3.6 for the user-facing description.
"""

from __future__ import annotations

import re
from typing import List, Optional, Tuple

# Codegen attributes: these change the emitted C function declaration.
CODEGEN_ATTRIBUTES = frozenset({
    "inline",
    "noinline",
    "always_inline",
    "target",
})

# Build-guard attributes consumed by the transpiler's mode filter
# (see `_function_allowed` in transpiler.py).
GUARD_ATTRIBUTES = frozenset({
    "only",
    "guard",
    "compile",
    "jit",
    "hot",
    "interp",
    "mlir",
    "c",
})

# Semantic / backend-selection attributes handled elsewhere in the pipeline.
SEMANTIC_ATTRIBUTES = frozenset({
    "gpu",        # device codegen (mlir_gpu_codegen / metal_codegen)
    "rt_safe",    # real-time safety checking (type_checker)
    "flow_api",   # stable C ABI name (c_generator name mangling)
    "test",       # synthesized by the parser for `test "..." { }` blocks
    "monomorphized",  # synthesized by monomorphize.py
    "lifetime",   # lifetime domain (type_checker; docs/language/lifetime-domains.md)
    # Physical-systems W0 (docs/vision/physical-systems.md)
    "dma",
    "noncacheable",
    "aligned",
    "hardware",
    "radiation_sensitive",
    "deterministic",
    "guarantee",
})

KNOWN_ATTRIBUTES = CODEGEN_ATTRIBUTES | GUARD_ATTRIBUTES | SEMANTIC_ATTRIBUTES

# Attributes that take arguments. Everything else must be bare.
ATTRIBUTES_WITH_ARGS = frozenset({
    "only", "guard", "target", "lifetime", "aligned", "guarantee",
})

# Allowed arguments for @guarantee(...).
GUARANTEE_ARGS = frozenset({
    "no_alloc",
    "no_block",
    "heap_allocations_eq_0",
    "blocking_eq_false",
})

# Lifetime domains, shortest-lived first (docs/language/lifetime-domains.md).
LIFETIME_DOMAINS: Tuple[str, ...] = ("callback", "frame", "session", "application")


def domain_rank(domain: str) -> int:
    """Position of `domain` in the lifetime order (smaller = shorter-lived)."""
    return LIFETIME_DOMAINS.index(domain)


def lifetime_domain(attrs: Optional[List[str]]) -> Optional[str]:
    """The declared lifetime domain of a declaration, or None if unannotated."""
    for attr in attrs or []:
        name, args = parse_attribute(attr)
        if name == "lifetime" and len(args) == 1 and args[0] in LIFETIME_DOMAINS:
            return args[0]
    return None

# One comma-separated item of a `target(...)` spec.
_TARGET_ITEM_RE = re.compile(
    r"^[+-]?[A-Za-z0-9_.]+(?:-[A-Za-z0-9_.]+)*"
    r"(?:=[A-Za-z0-9_.+]+(?:-[A-Za-z0-9_.+]+)*)?$"
)


def parse_attribute(attr: str) -> Tuple[str, List[str]]:
    """Split a flattened attribute string into `(name, args)`."""
    if "(" in attr and attr.endswith(")"):
        name, rest = attr.split("(", 1)
        args = [a.strip() for a in rest[:-1].split(",") if a.strip()]
        return name.strip(), args
    return attr.strip(), []


def attrs_imply_rt_safe(attrs: Optional[List[str]]) -> bool:
    """True when attributes require the @rt_safe call-graph discipline.

    `@deterministic` and any `@guarantee(...)` map onto the same no-heap /
    no-block checker as `@rt_safe` for physical-systems W0.
    """
    for attr in attrs or []:
        name, _args = parse_attribute(attr)
        if name in ("rt_safe", "deterministic", "guarantee"):
            return True
    return False


def validate_target_spec(spec: str) -> Optional[str]:
    """Check a `@target(...)` string's *shape*."""
    if not spec:
        return "@target(...) requires a non-empty target string"
    items = spec.split(",")
    for item in items:
        item = item.strip()
        if not item:
            return f"@target(\"{spec}\") has an empty component"
        if not _TARGET_ITEM_RE.match(item):
            return (
                f"@target(\"{spec}\") component '{item}' is not a valid target "
                "feature; expected forms are 'avx2', '+avx2', '-sse', "
                "'no-sse', 'arch=haswell' or 'tune=native'"
            )
    return None


def normalize_target_spec(spec: str) -> str:
    """Canonical comma-joined form used inside the emitted C attribute."""
    return ",".join(item.strip() for item in spec.split(",") if item.strip())


def attribute_errors(fn_name: str, attrs: List[str]) -> List[str]:
    """Validate one declaration's attribute list. Returns error strings."""
    errors: List[str] = []
    seen = set()
    lifetime_seen = False
    for attr in attrs:
        name, args = parse_attribute(attr)
        if name not in KNOWN_ATTRIBUTES:
            known = ", ".join(f"@{n}" for n in sorted(KNOWN_ATTRIBUTES))
            errors.append(
                f"Unknown attribute '@{name}' on function '{fn_name}'. "
                f"Known attributes: {known}"
            )
            continue
        seen.add(name)
        if args and name not in ATTRIBUTES_WITH_ARGS:
            errors.append(
                f"Attribute '@{name}' on function '{fn_name}' takes no arguments"
            )
            continue
        if name == "lifetime":
            known = ", ".join(LIFETIME_DOMAINS)
            if lifetime_seen:
                errors.append(
                    f"'{fn_name}' declares more than one '@lifetime' domain; "
                    f"a declaration lives in exactly one domain"
                )
                continue
            lifetime_seen = True
            if len(args) != 1:
                errors.append(
                    f"Attribute '@lifetime' on '{fn_name}' takes exactly one "
                    f"domain: {known}"
                )
            elif args[0] not in LIFETIME_DOMAINS:
                errors.append(
                    f"Unknown lifetime domain '{args[0]}' on '{fn_name}'. "
                    f"Known domains: {known} "
                    f"(see docs/language/lifetime-domains.md)"
                )
            continue
        if name == "aligned":
            if len(args) != 1 or not args[0].isdigit() or int(args[0]) < 1:
                errors.append(
                    f"Attribute '@aligned' on '{fn_name}' requires a positive "
                    f"integer byte alignment, e.g. @aligned(64)"
                )
            continue
        if name == "guarantee":
            if not args:
                errors.append(
                    f"Attribute '@guarantee' on '{fn_name}' requires at least "
                    f"one contract, e.g. @guarantee(no_alloc, no_block)"
                )
            else:
                for arg in args:
                    if arg not in GUARANTEE_ARGS:
                        known = ", ".join(sorted(GUARANTEE_ARGS))
                        errors.append(
                            f"Unknown guarantee '{arg}' on '{fn_name}'. "
                            f"Known: {known}"
                        )
            continue
        if name == "target":
            if not args:
                errors.append(
                    f"Attribute '@target' on function '{fn_name}' requires a "
                    "target string, e.g. @target(\"avx2\")"
                )
            else:
                problem = validate_target_spec(",".join(args))
                if problem:
                    errors.append(f"{problem} (on function '{fn_name}')")

    if "noinline" in seen and ("inline" in seen or "always_inline" in seen):
        errors.append(
            f"Function '{fn_name}' cannot be both '@noinline' and "
            "'@inline'/'@always_inline'"
        )
    return errors
