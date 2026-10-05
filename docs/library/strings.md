# Strings, parse/format and text I/O

Flow strings are NUL-terminated UTF-8 byte sequences (`const char*` in the
C backend). Length, indexing and `+` are byte operations. This page is the
encoding and allocation contract for short-job text work (#747).

## Concatenation

`a + b` is concatenation when either operand is a string. A chain of three
or more parts is one allocation:

```flow
let s: string = "a" + "b" + "c" + "d"
let n = 1; let m = 2; let t: string = "x=" + n + " y=" + m
```

The C backend emits `__flowc_str_concatn`. The MLIR backend emits one
`malloc` plus one `memcpy` per part (strcat lowering), not nested pairwise
joins. Two-part joins stay `__flowc_str_concat` / `__flow_str_concat`.
Numeric and bool leaves are formatted first (`__flowc_str_of_*`, or
`"true"` / `"false"`).

Results are process-lifetime heap strings (not freed). That is a remaining
gap, not a licence to recopy every prefix.

## Parse and format

`std.string` walks the caller's buffer. Integer and float parse match
Python `int()` / `float()` on **ASCII**:

- leading and trailing space, tab, LF, VT, FF, CR
- optional `+` / `-`
- overflow and trailing junk are errors (`ok = false`), not wraparound
- `str_parse_i64` / `str_parse_f64` require the whole string
- `*_at` leaves the first unconsumed byte in `end`

`str_parse_f64` also accepts a fraction, an exponent, `inf` / `infinity` /
`nan` (any ASCII case), and `_` between digits. Hex floats (`0x1.8p+0`)
are rejected. More than 15 significant digits fall back to `strtod` on a
stack copy so rounding matches CPython.

Line walking (`str_line_end`, `str_line_next`) does not allocate.

These parsers do **not** decode UTF-8. A non-ASCII digit or separator is
junk, the same way `int("١")` fails in Python unless you go through a
locale.

## UTF-8 policy

| Surface | Policy |
|---|---|
| String literals and `+` | Bytes as written. The compiler does not insert U+FFFD. |
| `str_len` / index / line scan | Bytes, including interior NULs only up to `strlen`. |
| `str_parse_i64` / `str_parse_f64` | ASCII tokens only. |
| `str_utf8_valid` / `str_utf8_next` | Well-formed UTF-8, fail closed. Rejects overlong encodings, surrogates, truncated sequences and bytes above U+10FFFF. No allocation. |
| `io_read_file` | Binary: bytes as stored. A missing file is `ok = false`. |
| `io_read_text` | Same read, then `str_utf8_valid`. Invalid UTF-8 sets `ok = false` and leaves `data` as the raw bytes so the caller can inspect them. |

There is no silent `errors="replace"` path. A caller that wants U+FFFD
must write that conversion itself after a failed `io_read_text`.

`str_utf8_next(s, i)` returns the byte length of the sequence at `i`, or
`0` when the bytes there are not well-formed.

## File I/O

`std.io` uses `fread` / `fwrite` of a known size. Files larger than
`2^31-1` bytes are refused. Prefer `io_read_text` when the file is a
document and `io_read_file` when it is a blob.

## Harness rows

`./flow tool bench_harness` records `allocations` and `copies` for
`runtime_string_concat`, `runtime_parse_format` and `runtime_buffered_io`
from the workload stdout (`allocations: N`) and, when set, from the #740
memory profile.
