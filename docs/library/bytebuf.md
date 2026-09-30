# Byte buffer

`lib/stdlib/bytebuf.flow` is a growable byte buffer with the ASCII
character tests that go with it. Import it as `std.bytebuf`.

The code lives in `compiler/src/bytebuf.flow`, a leaf module the
compiler's source expanders (the dynamics DSL, flow blocks and the shader
DSL) use for their output. The standard library re-exports it, so tools
and the compiler share one copy.

```flow
import std.bytebuf { ByteBuf, bb_new, bb_puts, bb_put_i32, bb_putc, bb_str, bb_free }

extern {
    function puts(s: string) -> i32
}

function main() -> i32 {
    let b: ptr<ByteBuf> = bb_new(64)
    bb_puts(b, "n = ")
    bb_put_i32(b, 42)
    let s: string = bb_str(b)
    bb_free(b)
    let _p: i32 = puts(s)
    return 0
}
```

The bytes are `p[0 .. len)`, and `p[len]` is always 0. The buffer doubles
when it fills. `err` is set if an allocation fails, and that write is
dropped.

| Call | Effect |
|------|--------|
| `bb_new(cap)`, `bb_free(b)` | make and free a buffer |
| `bb_putc(b, c)`, `bb_puts(b, s)` | append a byte or a string |
| `bb_put_span(b, src, s, e)`, `bb_put_bytes(b, src, n)` | append `src[s .. e)` or `n` bytes |
| `bb_put_i32(b, v)`, `bb_put_i64(b, v)` | append decimal text |
| `bb_len(b)`, `bb_at(b, i)` | length, and the byte at `i` (-1 outside) |
| `bb_cstr(b)` | the contents as a NUL-terminated view, valid until the next write |
| `bb_str(b)` | a copy that outlives the buffer |
| `bb_truncate(b, n)`, `bb_clear(b)`, `bb_reserve(b, n)` | shorten, empty, make room |
| `bb_is_space(c)` | Python `str.isspace()` over ASCII |
| `bb_is_digit(c)`, `bb_is_alpha(c)`, `bb_is_word(c)` | ASCII classes; `bb_is_word` is `[A-Za-z0-9_]` |
| `bb_span_eq(a, a_s, a_e, b, b_s, b_e)` | two byte spans hold the same bytes |

The tests are `tests/lang/test_stdlib_bytebuf.flow`.
