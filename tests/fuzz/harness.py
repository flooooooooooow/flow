"""Stdlib-only fuzzing harness for the FLOW compiler front-end.

Three targets (see run_fuzz.py for the CLI):

  mutation  -- byte/token level mutations of the tracked .flow corpus plus
               pure-random inputs, fed to the lexer+parser.
  grammar   -- grammar-directed generation of syntactically plausible (not
               necessarily valid) programs, with deep nesting to stress
               recursive descent.
  pipeline  -- generation of known-valid programs which are then run through
               parse -> typecheck -> monomorphize -> C generation.

Contract under test: the compiler must never CRASH. A clean SyntaxError
(including FlowSyntaxError) from parsing is expected and fine; type errors
reported via TypeCheckResult.errors are fine. Anything else that escapes
(IndexError, AttributeError, RecursionError, KeyError, a hang, ...) is a
finding. Findings are deduplicated by (stage, exception type, deepest
src/flow frame), auto-minimized by line-removal + truncation bisection, and
can be persisted as regression fixtures under tests/fuzz/crashes/.

Everything is deterministic given --seed; the run length is bounded by a
wall-clock budget per target.
"""

from __future__ import annotations

import random
import signal
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = REPO_ROOT / "src"
CRASH_DIR = Path(__file__).resolve().parent / "crashes"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from flow.parser import (  # noqa: E402
    ConstDecl,
    EnumDecl,
    FunctionDecl,
    StructDecl,
    parse_flow_code,
)

# Exceptions that are legitimate "clean rejection" outcomes for hostile
# input.  FlowSyntaxError subclasses SyntaxError, and the lexer raises plain
# SyntaxError for bad characters, so SyntaxError covers the parser contract.
ALLOWED_PARSE_ERRORS = (SyntaxError,)

PER_INPUT_TIMEOUT = 5.0  # seconds before an input is classified as a hang


class FuzzTimeout(BaseException):
    """Raised by the SIGALRM handler when a single input hangs.

    BaseException so target code cannot swallow it with `except Exception`.
    """


@dataclass
class Finding:
    stage: str  # parse | typecheck | codegen | timeout stage
    exc_type: str
    location: str  # "file.py:function" of deepest src/flow frame
    message: str
    input_text: str
    minimized: Optional[str] = None

    @property
    def key(self) -> Tuple[str, str, str]:
        return (self.stage, self.exc_type, self.location)

    @property
    def slug(self) -> str:
        loc = self.location.replace(".py", "").replace(":", "-").replace("_", "-")
        return f"{self.stage}-{self.exc_type.lower()}-{loc}"


@dataclass
class FuzzStats:
    iterations: int = 0
    clean_errors: int = 0
    ok: int = 0
    findings: Dict[Tuple[str, str, str], Finding] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Execution guard: per-input wall-clock timeout via SIGALRM (main thread only)
# ---------------------------------------------------------------------------

def _alarm_handler(signum, frame):
    raise FuzzTimeout()


def run_guarded(fn: Callable[[], object], timeout: float = PER_INPUT_TIMEOUT):
    """Run fn(); return (outcome, exc). outcome in {ok, clean, crash, timeout}."""
    old = signal.signal(signal.SIGALRM, _alarm_handler)
    signal.setitimer(signal.ITIMER_REAL, timeout)
    try:
        fn()
        return "ok", None
    except ALLOWED_PARSE_ERRORS as e:
        return "clean", e
    except FuzzTimeout:
        return "timeout", None
    except Exception as e:  # noqa: BLE001 - crash bucket is the point
        return "crash", e
    except RecursionError as e:  # pragma: no cover - RecursionError is Exception
        return "crash", e
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def classify(exc: Optional[Exception], stage: str) -> Tuple[str, str, str]:
    """(stage, exc_type, deepest-src/flow-frame) for deduplication."""
    if exc is None:
        return (stage, "Timeout", "hang")
    location = "unknown"
    frames = traceback.extract_tb(exc.__traceback__)
    flow_frames = [
        f for f in frames if "/src/flow/" in f.filename.replace("\\", "/")
    ]
    if isinstance(exc, RecursionError) and flow_frames:
        # The deepest frame of a recursion cycle is arbitrary; use the most
        # frequent flow frame as the representative location.
        counts: Dict[str, int] = {}
        for f in flow_frames:
            key = f"{Path(f.filename).name}:{f.name}"
            counts[key] = counts.get(key, 0) + 1
        location = max(counts, key=lambda k: counts[k])
    elif flow_frames:
        f = flow_frames[-1]
        location = f"{Path(f.filename).name}:{f.name}"
    return (stage, type(exc).__name__, location)


# ---------------------------------------------------------------------------
# Pipeline stages
# ---------------------------------------------------------------------------

def parse_only(text: str) -> None:
    parse_flow_code(text)


def full_pipeline(text: str) -> str:
    """parse -> typecheck -> monomorphize -> C generation. Returns stage name
    reached; raises with ._fuzz_stage annotation on the exception via caller.
    """
    from flow.monomorphize import monomorphize
    from flow.c_generator import CGenerator
    from flow.type_checker import TypeChecker

    decls = parse_flow_code(text)
    stage = "typecheck"
    try:
        TypeChecker().check(decls)  # reported errors (result.errors) are fine
        stage = "codegen"
        decls = monomorphize(decls)
        gen = CGenerator()
        gen.generate_translation_unit(
            [d for d in decls if isinstance(d, ConstDecl)],
            [d for d in decls if isinstance(d, FunctionDecl)],
            structs=[d for d in decls if isinstance(d, StructDecl)],
            enums=[d for d in decls if isinstance(d, EnumDecl)],
        )
    except Exception as e:
        e._fuzz_stage = stage  # noqa: SLF001
        raise
    return stage


# ---------------------------------------------------------------------------
# Corpus
# ---------------------------------------------------------------------------

def load_corpus(max_bytes: int = 16384, limit: int = 400) -> List[str]:
    """Tracked .flow files (skipping third_party), size-capped, stable order."""
    try:
        out = subprocess.check_output(
            ["git", "-C", str(REPO_ROOT), "ls-files", "*.flow"], text=True
        )
        paths = [
            REPO_ROOT / line
            for line in out.splitlines()
            if line
            and not line.startswith("third_party/")
            and not line.startswith("tests/fuzz/crashes/")
        ]
    except Exception:
        paths = [
            p for p in REPO_ROOT.glob("tests/**/*.flow")
        ] + [p for p in REPO_ROOT.glob("examples/**/*.flow")]
    corpus = []
    for p in sorted(paths):
        try:
            data = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if 0 < len(data) <= max_bytes:
            corpus.append(data)
        if len(corpus) >= limit:
            break
    return corpus or ["function main() -> i32 {\n    return 0\n}\n"]


# ---------------------------------------------------------------------------
# Mutators (target a: corpus mutation + pure random)
# ---------------------------------------------------------------------------

KEYWORDS = [
    "function", "return", "let", "mut", "if", "else", "while", "for", "in",
    "struct", "enum", "match", "effect", "capability", "handle", "import",
    "export", "const", "type", "distinct", "trait", "impl", "true", "false",
]

INTERESTING = [
    "\x00", "\xff", '"', "'", "\\", "{", "}", "(", ")", "[", "]", "<", ">",
    "‮", "é", "\U0001f600", "﻿", "\t", "\r", "0x", "1e999",
    "..", "->", "=>", "::", "//", "/*", "*/", "\n\n", "@", "$", "`", "~",
]

BRACKETS = "(){}[]<>"


def mutate(rng: random.Random, corpus: List[str]) -> str:
    if rng.random() < 0.1:
        # pure random input
        n = rng.randint(1, 400)
        if rng.random() < 0.5:
            return "".join(chr(rng.randint(32, 126)) for _ in range(n))
        return "".join(chr(rng.randint(1, 0x10FF)) for _ in range(n))

    text = rng.choice(corpus)
    for _ in range(rng.randint(1, 3)):
        op = rng.randrange(8)
        if not text:
            break
        if op == 0:  # truncate
            text = text[: rng.randrange(len(text))]
        elif op == 1:  # delete a slice
            i = rng.randrange(len(text))
            j = min(len(text), i + rng.randint(1, 64))
            text = text[:i] + text[j:]
        elif op == 2:  # duplicate a slice
            i = rng.randrange(len(text))
            j = min(len(text), i + rng.randint(1, 64))
            text = text[:j] + text[i:j] + text[j:]
        elif op == 3:  # splice with another corpus file
            other = rng.choice(corpus)
            text = text[: rng.randrange(len(text))] + other[
                rng.randrange(len(other)) :
            ]
        elif op == 4:  # insert interesting tokens / random unicode
            i = rng.randrange(len(text) + 1)
            ins = rng.choice(INTERESTING) if rng.random() < 0.7 else chr(
                rng.randint(1, 0x10FF)
            )
            text = text[:i] + ins + text[i:]
        elif op == 5:  # bracket unbalancing: drop/flip/duplicate brackets
            pos = [k for k, c in enumerate(text) if c in BRACKETS]
            if pos:
                i = rng.choice(pos)
                mode = rng.randrange(3)
                if mode == 0:
                    text = text[:i] + text[i + 1 :]
                elif mode == 1:
                    text = text[:i] + rng.choice(BRACKETS) + text[i + 1 :]
                else:
                    text = text[:i] + text[i] * rng.randint(2, 40) + text[i:]
        elif op == 6:  # keyword swap
            kw = rng.choice(KEYWORDS)
            if kw in text:
                text = text.replace(kw, rng.choice(KEYWORDS), 1)
        else:  # shuffle tokens on one line
            lines = text.split("\n")
            i = rng.randrange(len(lines))
            toks = lines[i].split(" ")
            rng.shuffle(toks)
            lines[i] = " ".join(toks)
            text = "\n".join(lines)
    return text


# ---------------------------------------------------------------------------
# Grammar-directed generation (target b: plausible, possibly invalid)
# ---------------------------------------------------------------------------

TYPES = ["i32", "i64", "f32", "f64", "bool", "string"]
BINOPS = ["+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=", "&&", "||"]


def gen_expr(rng: random.Random, depth: int) -> str:
    if depth <= 0:
        return rng.choice(
            ["0", "1", "42", "3.14", "x", "y", "true", "false", '"s"', "-1"]
        )
    kind = rng.randrange(8)
    sub = lambda: gen_expr(rng, depth - 1)  # noqa: E731
    if kind == 0:
        return f"({sub()})"
    if kind == 1:
        return f"{sub()} {rng.choice(BINOPS)} {sub()}"
    if kind == 2:
        return f"-{sub()}" if rng.random() < 0.5 else f"!{sub()}"
    if kind == 3:
        return f"f({sub()}, {sub()})"
    if kind == 4:
        return "[" + ", ".join(sub() for _ in range(rng.randint(0, 3))) + "]"
    if kind == 5:
        return f"{sub()}[{sub()}]"
    if kind == 6:
        return f"p.{rng.choice(['x', 'y'])}"
    return f"P {{ x: {sub()}, y: {sub()} }}"


def gen_stmt(rng: random.Random, depth: int, indent: str) -> str:
    kind = rng.randrange(7)
    e = lambda: gen_expr(rng, min(depth, 3))  # noqa: E731
    if depth <= 0 or kind == 0:
        return f"{indent}let v{rng.randrange(9)}: {rng.choice(TYPES)} = {e()}"
    if kind == 1:
        body = gen_stmt(rng, depth - 1, indent + "    ")
        return f"{indent}if {e()} {{\n{body}\n{indent}}}"
    if kind == 2:
        body = gen_stmt(rng, depth - 1, indent + "    ")
        return (
            f"{indent}if {e()} {{\n{body}\n{indent}}} else {{\n"
            f"{gen_stmt(rng, depth - 1, indent + '    ')}\n{indent}}}"
        )
    if kind == 3:
        body = gen_stmt(rng, depth - 1, indent + "    ")
        return f"{indent}while {e()} {{\n{body}\n{indent}}}"
    if kind == 4:
        body = gen_stmt(rng, depth - 1, indent + "    ")
        return f"{indent}for i in 0..10 {{\n{body}\n{indent}}}"
    if kind == 5:
        return f"{indent}x = {e()}"
    return f"{indent}return {e()}"


def gen_grammar_program(rng: random.Random) -> str:
    """Plausible program; occasionally pathologically deep."""
    mode = rng.randrange(4)
    if mode == 0:
        # deep expression nesting - the classic recursive-descent killer
        depth = rng.randint(10, 600)
        opener = rng.choice(["(", "[", "-", "!"])
        closer = {"(": ")", "[": "]"}.get(opener, "")
        expr = opener * depth + "1" + closer * depth
        return f"function main() -> i32 {{\n    return {expr}\n}}\n"
    if mode == 1:
        # deep statement nesting
        depth = rng.randint(5, 250)
        return (
            "function main() -> i32 {\n"
            + "".join(
                "    " * (i + 1) + f"if x < {i} {{\n" for i in range(depth)
            )
            + "    " * (depth + 1)
            + "return 0\n"
            + "".join("    " * (depth - i) + "}\n" for i in range(depth))
            + "}\n"
        )
    if mode == 2:
        # random but structured expression trees
        stmts = "\n".join(
            gen_stmt(rng, rng.randint(1, 6), "    ")
            for _ in range(rng.randint(1, 6))
        )
        return (
            "struct P {\n    x: f64,\n    y: f64\n}\n"
            "function f(a: i32, b: i32) -> i32 {\n    return a + b\n}\n"
            f"function main() -> i32 {{\n{stmts}\n    return 0\n}}\n"
        )
    # top-level declaration soup
    parts = []
    for _ in range(rng.randint(1, 8)):
        d = rng.randrange(5)
        if d == 0:
            parts.append(
                f"struct S{rng.randrange(9)} {{\n    a: {rng.choice(TYPES)}\n}}"
            )
        elif d == 1:
            parts.append(f"enum E{rng.randrange(9)} {{\n    A,\n    B(i32)\n}}")
        elif d == 2:
            parts.append(f"const C{rng.randrange(9)}: i32 = {rng.randrange(100)}")
        elif d == 3:
            parts.append(f"type T{rng.randrange(9)} = {rng.choice(TYPES)}")
        else:
            body = gen_stmt(rng, rng.randint(0, 4), "    ")
            parts.append(
                f"function g{rng.randrange(9)}(x: i32) -> i32 {{\n{body}\n"
                "    return x\n}"
            )
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# Valid-program generation (target c: pipeline)
# ---------------------------------------------------------------------------

def gen_valid_expr(rng: random.Random, vars_: List[str], depth: int) -> str:
    if depth <= 0 or (not vars_ and rng.random() < 0.3):
        if vars_ and rng.random() < 0.5:
            return rng.choice(vars_)
        return str(rng.randrange(100))
    k = rng.randrange(4)
    if k == 0:
        return (
            f"({gen_valid_expr(rng, vars_, depth - 1)} "
            f"{rng.choice(['+', '-', '*'])} "
            f"{gen_valid_expr(rng, vars_, depth - 1)})"
        )
    if k == 1 and vars_:
        return rng.choice(vars_)
    if k == 2:
        return f"helper({gen_valid_expr(rng, vars_, depth - 1)})"
    return str(rng.randrange(100))


def gen_valid_program(rng: random.Random) -> str:
    lines = [
        "function helper(n: i32) -> i32 {",
        "    return n + 1",
        "}",
        "function main() -> i32 {",
    ]
    vars_: List[str] = []
    for i in range(rng.randint(1, 8)):
        name = f"v{i}"
        lines.append(
            f"    let {name}: i32 = {gen_valid_expr(rng, vars_, rng.randint(0, 4))}"
        )
        vars_.append(name)
        k = rng.randrange(4)
        if k == 0 and vars_:
            cond = f"{rng.choice(vars_)} < {rng.randrange(50)}"
            lines.append(f"    if {cond} {{")
            lines.append(
                f"        let t{i}: i32 = {gen_valid_expr(rng, vars_, 2)}"
            )
            lines.append("    }")
        elif k == 1:
            lines.append(f"    while {name} < 0 {{")
            lines.append(f"        {name} = {name} + 1")
            lines.append("    }")
        elif k == 2 and rng.random() < 0.5:
            n = rng.randint(1, 4)
            elems = ", ".join(
                gen_valid_expr(rng, vars_, 1) for _ in range(n)
            )
            lines.append(f"    let arr{i}: [i32; {n}] = [{elems}]")
    lines.append(f"    return {gen_valid_expr(rng, vars_, 2)}")
    lines.append("}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Shrinking: line-removal ddmin-lite, then truncation bisection
# ---------------------------------------------------------------------------

def _fails_same(text: str, runner: Callable[[str], None], key) -> bool:
    outcome, exc = run_guarded(lambda: runner(text), timeout=2.0)
    if outcome == "timeout":
        return key[1] == "Timeout"
    if outcome != "crash":
        return False
    got = classify(exc, key[0])
    # location can drift while shrinking; match on stage + exception type
    return (got[0], got[1]) == (key[0], key[1])


def shrink(
    text: str, runner: Callable[[str], None], key, max_rounds: int = 6
) -> str:
    # Phase 1: remove line chunks
    lines = text.split("\n")
    for _ in range(max_rounds):
        if len(lines) <= 1:
            break
        changed = False
        chunk = max(1, len(lines) // 4)
        i = 0
        while i < len(lines):
            candidate = lines[:i] + lines[i + chunk :]
            if candidate and _fails_same("\n".join(candidate), runner, key):
                lines = candidate
                changed = True
            else:
                i += chunk
        if not changed:
            if chunk == 1:
                break
    text = "\n".join(lines)
    # Phase 2: truncation bisection (shortest failing prefix)
    lo, hi = 1, len(text)
    while lo < hi:
        mid = (lo + hi) // 2
        if _fails_same(text[:mid], runner, key):
            hi = mid
        else:
            lo = mid + 1
    if _fails_same(text[:hi], runner, key):
        text = text[:hi]
    # Phase 3: strip leading chars
    while len(text) > 1 and _fails_same(text[1:], runner, key):
        text = text[1:]
    return text


# ---------------------------------------------------------------------------
# Fuzz loops
# ---------------------------------------------------------------------------

def _record(stats: FuzzStats, stage, exc, text, runner, do_shrink=True):
    key = classify(exc, stage)
    if key in stats.findings:
        return
    finding = Finding(
        stage=key[0],
        exc_type=key[1],
        location=key[2],
        message=(str(exc)[:200] if exc else "hang > timeout"),
        input_text=text,
    )
    if do_shrink:
        try:
            finding.minimized = shrink(text, runner, key)
        except Exception:  # noqa: BLE001 - shrinker must never kill the run
            finding.minimized = text
    else:
        finding.minimized = text
    stats.findings[key] = finding


def fuzz_mutation(seconds: float, seed: int, stats: Optional[FuzzStats] = None) -> FuzzStats:
    stats = stats or FuzzStats()
    rng = random.Random(seed)
    corpus = load_corpus()
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        text = mutate(rng, corpus)
        outcome, exc = run_guarded(lambda: parse_only(text))
        stats.iterations += 1
        if outcome == "ok":
            stats.ok += 1
        elif outcome == "clean":
            stats.clean_errors += 1
        elif outcome == "timeout":
            _record(stats, "parse", None, text, parse_only)
        else:
            _record(stats, "parse", exc, text, parse_only)
    return stats


def fuzz_grammar(seconds: float, seed: int, stats: Optional[FuzzStats] = None) -> FuzzStats:
    stats = stats or FuzzStats()
    rng = random.Random(seed)
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        text = gen_grammar_program(rng)
        outcome, exc = run_guarded(lambda: parse_only(text))
        stats.iterations += 1
        if outcome == "ok":
            stats.ok += 1
        elif outcome == "clean":
            stats.clean_errors += 1
        elif outcome == "timeout":
            _record(stats, "parse", None, text, parse_only)
        else:
            _record(stats, "parse", exc, text, parse_only)
    return stats


def _pipeline_runner(text: str) -> None:
    full_pipeline(text)


def fuzz_pipeline(seconds: float, seed: int, stats: Optional[FuzzStats] = None) -> FuzzStats:
    stats = stats or FuzzStats()
    rng = random.Random(seed)
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        text = gen_valid_program(rng)
        outcome, exc = run_guarded(lambda: _pipeline_runner(text))
        stats.iterations += 1
        if outcome == "ok":
            stats.ok += 1
        elif outcome == "clean":
            # generator produced something the parser rejects; acceptable but
            # counts separately so we notice generator rot
            stats.clean_errors += 1
        elif outcome == "timeout":
            _record(stats, "pipeline", None, text, _pipeline_runner)
        else:
            stage = getattr(exc, "_fuzz_stage", "parse")
            _record(stats, stage, exc, text, _pipeline_runner)
    return stats


TARGETS = {
    "mutation": fuzz_mutation,
    "grammar": fuzz_grammar,
    "pipeline": fuzz_pipeline,
}


def save_findings(stats: FuzzStats, out_dir: Path = CRASH_DIR) -> List[Path]:
    """Write minimized repros (raw bytes, no header) plus a JSON manifest
    entry per finding into out_dir/known_crashes.json. Returns written paths.
    """
    import json

    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "known_crashes.json"
    manifest = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    written = []
    for finding in stats.findings.values():
        fname = f"{finding.slug}.flow"
        path = out_dir / fname
        body = finding.minimized or finding.input_text
        path.write_text(body, encoding="utf-8")
        manifest[fname] = {
            "stage": finding.stage,
            "exception": finding.exc_type,
            "location": finding.location,
            "message": finding.message.splitlines()[0][:160]
            if finding.message
            else "",
        }
        written.append(path)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return written
