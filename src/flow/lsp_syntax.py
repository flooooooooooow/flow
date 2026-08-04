"""Rich IDE hover catalog for Flow syntax, operators, keywords, and types."""

from __future__ import annotations

from typing import Dict, Optional

# Multi-character tokens detected when the cursor sits on them (longest first).
MULTI_CHAR_OPS = (
    "|>",
    "->",
    "=>",
    "==",
    "!=",
    "<=",
    ">=",
    "&&",
    "||",
    "..",
    "<<",
    ">>",
)

SYNTAX_HOVER: Dict[str, str] = {
    # --- Operators ---
    "|>": (
        "**`|>`** — pipe / pipeline operator.\n\n"
        "Feeds the left-hand value into the right-hand call or declarative form.\n\n"
        "```flow\nxs |> sort\nxs |> sortBy [desc .score, asc .name]\n"
        "value |> abs\n```\n"
        "See docs/language/syntax.md (and docs/language/ordering.md when present)."
    ),
    "->": (
        "**`->`** — function return type or effect/sense binding arrow.\n\n"
        "```flow\nfunction add(a: i32, b: i32) -> i32 { return a + b }\n"
        "controllable -> plant_ok\n```\n"
        "See docs/language/functions.md."
    ),
    "=>": (
        "**`=>`** — match-arm / closure arrow.\n\n"
        "```flow\nmatch x {\n    0 => print(\"zero\")\n    default => print(\"other\")\n}\n```\n"
        "See docs/language/syntax.md."
    ),
    "..": (
        "**`..`** — range / record-update rest.\n\n"
        "```flow\n# Record update (copy base, override fields)\nPoint { ..p, x: 1.0 }\n```\n"
        "See docs/language/syntax.md."
    ),
    "as": (
        "**`as`** — cast or unit conversion.\n\n"
        "Converts a value to another type (or unit with matching dimensions).\n\n"
        "```flow\nlet n: i32 = 3\nlet f: f64 = n as f64\nlet v: Velocity = (10.0 as Meter) / (2.0 as Second)\n```\n"
        "See docs/language/types.md."
    ),
    "==": "**`==`** — equality comparison.\n\nSee docs/language/syntax.md.",
    "!=": "**`!=`** — inequality comparison.\n\nSee docs/language/syntax.md.",
    "<=": "**`<=`** — less-than-or-equal.\n\nSee docs/language/syntax.md.",
    ">=": "**`>=`** — greater-than-or-equal.\n\nSee docs/language/syntax.md.",
    "&&": (
        "**`&&`** — short-circuit logical AND (also spelled `and`).\n\n"
        "See docs/language/syntax.md."
    ),
    "||": (
        "**`||`** — short-circuit logical OR (also spelled `or`).\n\n"
        "See docs/language/syntax.md."
    ),
    "<<": "**`<<`** — bitwise left shift.\n\nSee docs/language/syntax.md.",
    ">>": "**`>>`** — bitwise right shift.\n\nSee docs/language/syntax.md.",
    # --- Keywords ---
    "match": (
        "**`match`** — pattern matching on a value.\n\n"
        "```flow\nmatch day {\n    1 => print(\"Mon\")\n    default => print(\"other\")\n}\n```\n"
        "See docs/language/syntax.md."
    ),
    "default": (
        "**`default`** — catch-all arm in a `match`.\n\n"
        "```flow\nmatch x {\n    0 => 1\n    default => x\n}\n```"
    ),
    "effect": (
        "**`effect`** — declare an algebraic effect (operations without a default body).\n\n"
        "```flow\neffect Async {\n    delay(ms: i32) -> void\n    spawn(task_id: i32) -> i32\n}\n```\n"
        "See docs/language/async-effects.md."
    ),
    "capability": (
        "**`capability`** — implement an effect (handler / backend).\n\n"
        "```flow\ncapability SimulatedAsync for Async {\n    delay(ms: i32) -> void { }\n}\n```\n"
        "See docs/language/async-effects.md."
    ),
    "handle": (
        "**`handle`** — install an effect handler for a block.\n\n"
        "```flow\nhandle Async with SimulatedAsync {\n    result = fetch_user(1)\n}\n```\n"
        "See docs/language/async-effects.md."
    ),
    "with": (
        "**`with`** — pairs with `handle` (`handle E with Cap { ... }`) "
        "or qualifies declarative options (`with entropy`).\n\n"
        "See docs/language/async-effects.md."
    ),
    "parallel": (
        "**`parallel`** — parallel `for` loop (work may run concurrently).\n\n"
        "```flow\nparallel for i in 0 to n {\n    out[i] = in[i] * 2\n}\n```\n"
        "See docs/language/syntax.md."
    ),
    "for": (
        "**`for`** — counted loop (`for i in lo to hi` / `step`).\n\n"
        "```flow\nfor i in 0 to 10 {\n    print(i)\n}\nfor i in 0 to 10 step 2 { }\n```\n"
        "See docs/language/syntax.md."
    ),
    "to": (
        "**`to`** — upper bound of a `for` range (`for i in 0 to n`).\n\n"
        "End is exclusive in the usual Flow loop lowering.\n"
        "See docs/language/syntax.md."
    ),
    "step": (
        "**`step`** — stride for a `for` loop.\n\n"
        "```flow\nfor i in 0 to 10 step 2 { }\n```"
    ),
    "while": (
        "**`while`** — conditional loop.\n\n"
        "```flow\nwhile n > 0 {\n    n = n - 1\n}\n```\n"
        "See docs/language/syntax.md."
    ),
    "if": (
        "**`if`** — conditional branch.\n\n"
        "```flow\nif x > 0 {\n    return x\n} elif x == 0 {\n    return 0\n} else {\n    return -x\n}\n```"
    ),
    "elif": "**`elif`** — else-if branch after `if`.\n\nSee docs/language/syntax.md.",
    "else": "**`else`** — final branch of an `if` / `elif` chain.\n\nSee docs/language/syntax.md.",
    "return": (
        "**`return`** — exit the current function with a value (or void).\n\n"
        "```flow\nreturn a + b\n```\n"
        "See docs/language/functions.md."
    ),
    "let": (
        "**`let`** — bind a local (immutable unless `mut`).\n\n"
        "```flow\nlet x: i32 = 42\nlet mut counter: i32 = 0\n```\n"
        "See docs/language/variables.md."
    ),
    "mut": (
        "**`mut`** — marks a `let` binding as mutable.\n\n"
        "```flow\nlet mut n: i32 = 0\nn = n + 1\n```\n"
        "See docs/language/variables.md."
    ),
    "const": (
        "**`const`** — compile-time constant binding.\n\n"
        "```flow\nexport const PI: f32 = 3.14159265\n```\n"
        "See docs/language/variables.md."
    ),
    "struct": (
        "**`struct`** — product type with named fields.\n\n"
        "```flow\nstruct Point { x: f32, y: f32 }\n```\n"
        "See docs/language/types.md."
    ),
    "enum": (
        "**`enum`** — sum type with named variants.\n\n"
        "```flow\nenum Option<T> { Some(T), None }\n```\n"
        "See docs/language/types.md."
    ),
    "trait": (
        "**`trait`** — interface of method signatures.\n\n"
        "```flow\ntrait Printable {\n    function to_string(self) -> string\n}\n```\n"
        "See docs/language/types.md."
    ),
    "impl": (
        "**`impl`** — implement a trait for a type (or inherent methods).\n\n"
        "```flow\nimpl Printable for Point {\n    function to_string(self) -> string { ... }\n}\n```\n"
        "See docs/language/types.md."
    ),
    "function": (
        "**`function`** — declare a function.\n\n"
        "```flow\nfunction add(a: i32, b: i32) -> i32 {\n    return a + b\n}\n```\n"
        "See docs/language/functions.md."
    ),
    "import": (
        "**`import`** — bring a module or selected symbols into scope.\n\n"
        "```flow\nimport \"stdlib/math.flow\"\nimport my_pkg { foo, bar }\n```\n"
        "See docs/language/modules.md."
    ),
    "export": (
        "**`export`** — make a declaration (or list of names) visible to importers.\n\n"
        "```flow\nexport function add(a: f32, b: f32) -> f32 { return a + b }\nexport foo, bar\n```\n"
        "See docs/language/modules.md."
    ),
    "extern": (
        "**`extern`** — FFI declarations implemented outside Flow.\n\n"
        "```flow\nextern {\n    function malloc(size: i64) -> ptr<void>\n}\n```\n"
        "See docs/language/functions.md."
    ),
    "inline": (
        "**`inline`** — hint that a function should be inlined.\n\n"
        "```flow\ninline function fast_add(a: i32, b: i32) -> i32 {\n    return a + b\n}\n```\n"
        "See docs/language/language_design.md."
    ),
    "in": (
        "**`in`** — separator in `for i in lo to hi`.\n\n"
        "See docs/language/syntax.md."
    ),
    "module": (
        "**`module`** — declare a named module / namespace block.\n\n"
        "See docs/language/modules.md."
    ),
    # --- Math / domain ---
    "shader": (
        "**`shader`** — GPU shader / FSL entry (graphics pipeline).\n\n"
        "```flow\nshader main(uv: vec2) -> vec4 { ... }\n```\n"
        "See docs/language/graphics.md."
    ),
    "unit": (
        "**`unit`** — declare a unit of measure (dimensional type).\n\n"
        "```flow\nunit Meter\nunit Second\nunit Velocity = Meter / Second\n```\n"
        "Dimensions are checked at compile time and erase to `f64`.\n"
        "See docs/language/types.md."
    ),
    "theorem": (
        "**`theorem`** — verified claim at a Claim Path (proof-as-program).\n\n"
        "```flow\n# @means Adding zero on the right is identity.\n"
        "# @tier derived\ntheorem Nat/+.zero-right(n: Nat) { ... }\n```\n"
        "See docs/language/verification.md."
    ),
    "assume": (
        "**`assume`** — bring a prior claim into scope inside a proof.\n\n"
        "```flow\nassume Nat/+.zero-right(n)\n```\n"
        "See docs/language/verification.md."
    ),
    "therefore": (
        "**`therefore`** — conclusion the checker must verify.\n\n"
        "```flow\ntherefore n + 0 == n\n```\n"
        "See docs/language/verification.md."
    ),
    "claim": (
        "**`claim`** — claim-path vocabulary for verified facts "
        "(see theorem headers / epistemology).\n\n"
        "See docs/language/claim-coordinates.md and docs/language/epistemology.md."
    ),
    # --- Attributes ---
    "@gpu": (
        "**`@gpu`** — mark a function as a GPU kernel / offload candidate.\n\n"
        "```flow\n@gpu\nfunction saxpy(n: i32, a: f32, x: ptr<f32>, y: ptr<f32>) -> void { ... }\n```\n"
        "See docs/tutorials/advanced.md."
    ),
    "@rt_safe": (
        "**`@rt_safe`** — real-time safety attribute (no unbounded alloc / locks).\n\n"
        "```flow\n@rt_safe\nfunction process_block(buf: ptr<f32>, n: i32) -> void { ... }\n```"
    ),
    "@inline": (
        "**`@inline`** — attribute form of the inline hint.\n\n"
        "```flow\n@inline\nfunction tick() -> void { ... }\n```\n"
        "See also the `inline` keyword."
    ),
    # --- Types ---
    "array": (
        "**`array<T, N>`** — fixed-size array type.\n\n"
        "```flow\nlet xs: array<i32, 4> = [1, 2, 3, 4]\n```\n"
        "See docs/language/types.md."
    ),
    "ptr": (
        "**`ptr<T>`** — raw pointer (FFI / low-level buffers).\n\n"
        "```flow\nextern {\n    function malloc(size: i64) -> ptr<void>\n}\n```\n"
        "See docs/language/types.md."
    ),
    "bit": (
        "**`bit`** — single-bit / boolean-like hardware or verify type.\n\n"
        "See docs/language/types.md."
    ),
    "vec": (
        "**`vec`** — short vector type (SIMD / graphics).\n\n"
        "See docs/language/types.md and docs/language/graphics.md."
    ),
    "i8": "**`i8`** — signed 8-bit integer.\n\nSee docs/language/types.md.",
    "i16": "**`i16`** — signed 16-bit integer.\n\nSee docs/language/types.md.",
    "i32": "**`i32`** — signed 32-bit integer.\n\nSee docs/language/types.md.",
    "i64": "**`i64`** — signed 64-bit integer.\n\nSee docs/language/types.md.",
    "i128": "**`i128`** — signed 128-bit integer.\n\nSee docs/language/types.md.",
    "u8": "**`u8`** — unsigned 8-bit integer.\n\nSee docs/language/types.md.",
    "u16": "**`u16`** — unsigned 16-bit integer.\n\nSee docs/language/types.md.",
    "u32": "**`u32`** — unsigned 32-bit integer.\n\nSee docs/language/types.md.",
    "u64": "**`u64`** — unsigned 64-bit integer.\n\nSee docs/language/types.md.",
    "u128": "**`u128`** — unsigned 128-bit integer.\n\nSee docs/language/types.md.",
    "f32": (
        "**`f32`** — IEEE-754 single-precision floating point.\n\n"
        "See docs/language/types.md."
    ),
    "f64": (
        "**`f64`** — IEEE-754 double-precision floating point.\n\n"
        "See docs/language/types.md."
    ),
    "bool": "**`bool`** — boolean (`true` / `false`).\n\nSee docs/language/types.md.",
    "void": "**`void`** — no value (typical for side-effecting functions).\n\nSee docs/language/types.md.",
    "string": "**`string`** — UTF-8 string.\n\nSee docs/language/types.md.",
}


def syntax_hover(token: str) -> Optional[str]:
    """Return markdown hover text for a syntax token, or None."""
    if not token:
        return None
    if token in SYNTAX_HOVER:
        return SYNTAX_HOVER[token]
    # Normalize attribute without @
    if token.startswith("@") and token in SYNTAX_HOVER:
        return SYNTAX_HOVER[token]
    at_form = f"@{token}"
    if at_form in SYNTAX_HOVER:
        return SYNTAX_HOVER[at_form]
    return None


def syntax_token_at_position(text: str, line: int, character: int) -> Optional[str]:
    """Return the syntax token under the cursor, including multi-char operators.

    Unlike a plain identifier scan, this detects `|>`, `->`, `=>`, `..`,
    comparison/logical digraphs, and `@attr` attributes when the cursor is on them.
    """
    lines = text.split("\n")
    if line < 0 or line >= len(lines):
        return None
    line_text = lines[line]
    if not line_text:
        return None
    # Allow cursor at end-of-line to still hit a trailing operator char.
    col = character
    if col < 0:
        return None
    if col > len(line_text):
        return None
    if col == len(line_text):
        col = len(line_text) - 1
    if col < 0:
        return None

    # Prefer longest multi-char operator covering `col`.
    for op in MULTI_CHAR_OPS:
        op_len = len(op)
        start_min = max(0, col - op_len + 1)
        start_max = min(col, len(line_text) - op_len)
        for start in range(start_min, start_max + 1):
            if line_text[start : start + op_len] == op and start <= col < start + op_len:
                return op

    # Attributes: @gpu, @rt_safe, @inline
    if line_text[col] == "@" or (
        col > 0 and line_text[col - 1] == "@"
    ) or _in_attr_name(line_text, col):
        attr = _attribute_at(line_text, col)
        if attr:
            return attr

    # Identifier / keyword
    if line_text[col].isalnum() or line_text[col] == "_":
        start = col
        while start > 0 and (line_text[start - 1].isalnum() or line_text[start - 1] == "_"):
            start -= 1
        end = col
        while end < len(line_text) and (line_text[end].isalnum() or line_text[end] == "_"):
            end += 1
        word = line_text[start:end]
        return word or None

    return None


def _in_attr_name(line_text: str, col: int) -> bool:
    i = col
    while i > 0 and (line_text[i - 1].isalnum() or line_text[i - 1] == "_"):
        i -= 1
    return i > 0 and line_text[i - 1] == "@"


def _attribute_at(line_text: str, col: int) -> Optional[str]:
    # Walk left to '@'
    i = col
    if line_text[i] != "@":
        while i > 0 and line_text[i] != "@":
            if not (line_text[i].isalnum() or line_text[i] == "_"):
                break
            i -= 1
        if line_text[i] != "@":
            # Cursor on name; find preceding @
            j = col
            while j > 0 and (line_text[j - 1].isalnum() or line_text[j - 1] == "_"):
                j -= 1
            if j > 0 and line_text[j - 1] == "@":
                i = j - 1
            else:
                return None
    end = i + 1
    while end < len(line_text) and (line_text[end].isalnum() or line_text[end] == "_"):
        end += 1
    if end == i + 1:
        return "@"
    return line_text[i:end]
