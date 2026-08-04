"""Dynamics DSL IntelliSense data for the FLOW language server.

Complements `dynamics_dsl.py` (pre-parse expander). Bare keywords and the
`dyn.` / `dynamics.` / `dynamics { }` namespace forms are all documented here
so editors surface the same vocabulary the expander accepts.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# CompletionItemKind
KIND_KEYWORD = 14
KIND_SNIPPET = 15
KIND_MODULE = 9

DYNAMICS_HOVER: Dict[str, str] = {
    "dsys": (
        "**`dsys`** — declare a linear plant (dynamics DSL).\n\n"
        "```flow\n"
        "dyn.dsys plant {\n"
        "    discrete   # or continuous\n"
        "    dt 0.1\n"
        "    n 2 m 1 p 1\n"
        "    A 1.0 0.1 0.0 1.0\n"
        "    B 0.0 0.1\n"
        "    C 1.0 0.0\n"
        "}\n"
        "```\n"
        "Prefixed form: `dyn.dsys` / `dynamics.dsys`. See docs/language/dynamics-dsl.md."
    ),
    "horizon": (
        "**`horizon`** — name a finite or infinite analysis horizon.\n\n"
        "```flow\ndyn.horizon rollout finite 50\n"
        "dyn.horizon asymptotic infinite gamma 0.99\n```"
    ),
    "sense": (
        "**`sense on`** — open-loop analysis bindings.\n\n"
        "```flow\n"
        "dyn.sense on plant {\n"
        "    controllable -> plant_ok\n"
        "    spectral -> rho_open\n"
        "    gramian finite rollout trace -> wc_fin\n"
        "}\n```"
    ),
    "ga": (
        "**`ga evolve`** — genetic search for state-feedback gains.\n\n"
        "```flow\n"
        "dyn.ga evolve on plant over rollout -> k1 k2 {\n"
        "    population 12\n"
        "    generations 30\n"
        "    mutation 0.3\n"
        "}\n```"
    ),
    "closed": (
        "**`closed`** — certify closed-loop `A - B K`.\n\n"
        "```flow\n"
        "dyn.closed plant with k1 k2 {\n"
        "    spectral -> rho_cl\n"
        "    energy over rollout -> E_cl\n"
        "    stable -> stable_cl\n"
        "}\n```"
    ),
    "analyze": (
        "**`analyze`** — one-shot GA + controllability + Gramian report.\n\n"
        "```flow\n"
        "dyn.analyze plant ga k1 k2 over rollout -> report { full }\n```\n"
        "Binds a `GAAnalysisReport` and assigns `k1`/`k2`."
    ),
    "wfc": (
        "**`wfc field`** — Wave Function Collapse field (experimental coupling).\n\n"
        "```flow\ndyn.wfc field layout { size 4 4  tiles 3  seed 7 }\n```"
    ),
    "dynamics": (
        "**`dynamics { ... }`** — namespace block for the dynamics DSL.\n\n"
        "Body uses bare `dsys` / `horizon` / `sense` / `ga evolve` / … lines.\n"
        "Line prefix alternative: `dyn.horizon …` / `dynamics.sense on …`."
    ),
    "dyn": (
        "**`dyn.`** — short namespace prefix for dynamics DSL constructs "
        "(`dyn.dsys`, `dyn.horizon`, `dyn.sense`, `dyn.ga`, `dyn.closed`, "
        "`dyn.analyze`, `dyn.wfc`)."
    ),
    "controllable": "`controllable -> name` — bind `i32` 1 if rank(ctrb)==n (sense block).",
    "spectral": "`spectral -> name` — bind spectral radius `f64` (sense/closed).",
    "gramian": (
        "`gramian finite HZ trace -> name` / `gramian infinite HZ trace -> name` "
        "— bind controllability Gramian trace (sense block)."
    ),
    "stable": "`stable -> name` — bind `i32` 1 if closed-loop |λ|_max < 1.",
    "energy": "`energy over HZ -> name` — bind trajectory energy over a horizon (closed).",
    "population": "GA population size (default 8).",
    "generations": "GA generations (default 20, max 32).",
    "mutation": "GA mutation rate (default 0.3).",
    "discrete": "Plant is discrete-time: `x[k+1] = A x[k] + B u[k]`.",
    "continuous": "Plant is continuous-time; Euler-discretized at `dt` before analysis.",
}


def dynamics_completion_items(prefix: str = "") -> List[Dict[str, Any]]:
    """Return LSP completion items for dynamics DSL (+ optional typed prefix)."""
    items: List[Dict[str, Any]] = []

    def add(
        label: str,
        *,
        kind: int = KIND_SNIPPET,
        detail: str = "dynamics DSL",
        doc: str = "",
        insert: Optional[str] = None,
    ) -> None:
        item: Dict[str, Any] = {
            "label": label,
            "kind": kind,
            "detail": detail,
            "documentation": doc or DYNAMICS_HOVER.get(label.split(".")[-1].split()[0], ""),
        }
        if insert is not None:
            item["insertText"] = insert
            item["insertTextFormat"] = 2  # Snippet
        items.append(item)

    # Namespace entry points
    add(
        "dynamics",
        kind=KIND_MODULE,
        detail="dynamics namespace block",
        insert="dynamics {\n    $0\n}",
        doc=DYNAMICS_HOVER["dynamics"],
    )
    add(
        "dyn.",
        kind=KIND_MODULE,
        detail="dynamics prefix",
        insert="dyn.",
        doc=DYNAMICS_HOVER["dyn"],
    )

    snippets = [
        (
            "dyn.dsys",
            "dyn.dsys ${1:plant} {\n"
            "    ${2|discrete,continuous|}\n"
            "    dt ${3:0.1}\n"
            "    n ${4:2} m ${5:1} p ${6:1}\n"
            "    A ${7:1.0 0.1 0.0 1.0}\n"
            "    B ${8:0.0 0.1}\n"
            "    C ${9:1.0 0.0}\n"
            "}",
        ),
        ("dyn.horizon", "dyn.horizon ${1:rollout} finite ${2:50}"),
        (
            "dyn.sense",
            "dyn.sense on ${1:plant} {\n"
            "    controllable -> ${2:plant_ok}\n"
            "    spectral -> ${3:rho_open}\n"
            "    $0\n"
            "}",
        ),
        (
            "dyn.ga evolve",
            "dyn.ga evolve on ${1:plant} over ${2:rollout} -> ${3:k1} ${4:k2} {\n"
            "    population ${5:12}\n"
            "    generations ${6:30}\n"
            "    mutation ${7:0.3}\n"
            "}",
        ),
        (
            "dyn.closed",
            "dyn.closed ${1:plant} with ${2:k1} ${3:k2} {\n"
            "    spectral -> ${4:rho_cl}\n"
            "    energy over ${5:rollout} -> ${6:E_cl}\n"
            "    stable -> ${7:stable_cl}\n"
            "}",
        ),
        (
            "dyn.analyze",
            "dyn.analyze ${1:plant} ga ${2:k1} ${3:k2} over ${4:rollout} -> ${5:report} {\n"
            "    full\n"
            "}",
        ),
        (
            "dyn.wfc field",
            "dyn.wfc field ${1:layout} {\n"
            "    size ${2:4} ${3:4}\n"
            "    tiles ${4:3}\n"
            "    seed ${5:7}\n"
            "}",
        ),
        # Bare forms (still valid)
        (
            "dsys",
            "dsys ${1:plant} {\n"
            "    discrete\n"
            "    dt 0.1\n"
            "    n 2 m 1 p 1\n"
            "    A 1.0 0.1 0.0 1.0\n"
            "    B 0.0 0.1\n"
            "    C 1.0 0.0\n"
            "}",
        ),
        ("horizon", "horizon ${1:rollout} finite ${2:50}"),
        (
            "sense on",
            "sense on ${1:plant} {\n"
            "    controllable -> ${2:plant_ok}\n"
            "    spectral -> ${3:rho_open}\n"
            "}",
        ),
        (
            "ga evolve",
            "ga evolve on ${1:plant} over ${2:rollout} -> ${3:k1} ${4:k2} {\n"
            "    population 12\n"
            "    generations 30\n"
            "    mutation 0.3\n"
            "}",
        ),
        (
            "closed",
            "closed ${1:plant} with ${2:k1} ${3:k2} {\n"
            "    spectral -> ${4:rho_cl}\n"
            "    stable -> ${5:stable_cl}\n"
            "}",
        ),
        (
            "analyze",
            "analyze ${1:plant} ga ${2:k1} ${3:k2} over ${4:rollout} -> ${5:report} {\n"
            "    full\n"
            "}",
        ),
    ]

    for label, insert in snippets:
        add(label, insert=insert, doc=DYNAMICS_HOVER.get(label.split()[0].split(".")[-1], ""))

    # Inner-block keywords
    for kw, detail in [
        ("controllable", "sense binding"),
        ("spectral", "sense/closed binding"),
        ("gramian finite", "sense Gramian binding"),
        ("gramian infinite", "sense Gramian binding"),
        ("stable", "closed-loop stability binding"),
        ("energy over", "closed-loop energy binding"),
        ("population", "GA setting"),
        ("generations", "GA setting"),
        ("mutation", "GA setting"),
        ("discrete", "dsys mode"),
        ("continuous", "dsys mode"),
        ("full", "analyze report mode"),
    ]:
        add(kw, kind=KIND_KEYWORD, detail=detail, insert=None)

    if prefix:
        p = prefix.lower()
        items = [
            it
            for it in items
            if it["label"].lower().startswith(p)
            or p in it["label"].lower()
            or (it.get("insertText") or "").lower().startswith(p)
        ]
    return items


def dynamics_hover(word: str) -> Optional[str]:
    if word in DYNAMICS_HOVER:
        return DYNAMICS_HOVER[word]
    # dyn.dsys → dsys
    if "." in word:
        tail = word.split(".")[-1]
        if tail in DYNAMICS_HOVER:
            return DYNAMICS_HOVER[tail]
    return None
