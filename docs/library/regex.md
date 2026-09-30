# Regular expressions

`lib/stdlib/regex.flow` is a backtracking matcher for the part of Python's
`re` syntax that programs and the repository tools use, with Python's
matching rules. Import it as `std.regex`.

```flow
import std.regex { Regex, RxMatch, rx_compile, rx_search, rx_m_group, rx_m_named, rx_m_start }

extern {
    function printf(fmt: string, ...) -> i32
}

function main() -> i32 {
    let r: ptr<Regex> = rx_compile("(\\w+)@(?P<host>[\\w.]+)", 0)
    let m: ptr<RxMatch> = rx_search(r, "mail bob@example.org today")
    if m == null {
        return 1
    }
    printf("%s at %s, from %d\n", rx_m_group(m, 1), rx_m_named(m, "host"), rx_m_start(m, 0))
    return 0
}
```

## Syntax

| Form | Meaning |
|------|---------|
| `.` `^` `$` | any character but a newline, line start, line end |
| `[a-z]` `[^...]` | classes with ranges and negation |
| `\d \D \w \W \s \S` | Unicode digit, word and space classes |
| `\b \B \A \Z` | word boundary, not a boundary, text start, text end |
| `\n \t \xhh \uhhhh \Uhhhhhhhh \0` | character escapes |
| `( )` `(?: )` `(?P<name> )` | capturing, non-capturing and named groups |
| `\1` `(?P=name)` | backreferences |
| `(?= )` `(?! )` | lookahead |
| `(?<= )` `(?<! )` | lookbehind of a fixed width |
| `a\|b` | alternation |
| `* + ? {m} {m,} {,n} {m,n}` | repeats, each lazy with a trailing `?` |
| `(?#...)` | a comment |
| `(?aims)` at the start | inline flags |

Scoped flags `(?i:...)`, conditionals, atomic groups, possessive
quantifiers and verbose mode are rejected with an error.

Flags have Python's values: `RX_IGNORECASE` (2), `RX_MULTILINE` (8),
`RX_DOTALL` (16) and `RX_ASCII` (256). Combine them with `|`.
`rx_py_flags()` is `RX_MULTILINE | RX_DOTALL`.

Matching runs on code points, so `.`, `{0,120}` and match positions count
characters as Python does. `\w`, `\d` and `\s` follow Python's Unicode
rules for ASCII and the common Latin, Greek, Cyrillic and mathematical
ranges, or ASCII alone under `RX_ASCII`. `RX_IGNORECASE` folds ASCII,
Latin-1, Greek and Cyrillic letters.

## Calls

| Call | Python |
|------|--------|
| `rx_compile(pattern, flags)` | `re.compile`. Check `rx_ok(r)` or `rx_error(r)`; a pattern that does not compile matches nothing |
| `rx_search(r, text)` | `r.search(text)`, a `ptr<RxMatch>` or null |
| `rx_search_from(r, text, pos)` | `r.search(text, pos)` |
| `rx_match(r, text)` | `r.match(text)` |
| `rx_fullmatch(r, text)` | `r.fullmatch(text)` |
| `rx_next(m)` | the next match of `r.finditer(text)` |
| `rx_test(r, text)` | `r.search(text) is not None` |
| `rx_findall(r, text)` | `r.findall(text)`, a `ptr<RxStrs>` |
| `rx_sub(r, repl, text, count)` | `r.sub(repl, text, count)`, with `\1`, `\g<name>` and `\g<0>` in `repl` |
| `rx_split(r, text, maxsplit)` | `r.split(text, maxsplit)` |
| `rx_escape(s)` | `re.escape(s)` |
| `rx_group_count(r)`, `rx_group_index(r, name)` | `r.groups`, `r.groupindex[name]` |

On a match:

| Call | Python |
|------|--------|
| `rx_m_group(m, g)` | `m.group(g)`, "" when the group did not take part |
| `rx_m_matched(m, g)` | `m.group(g) is not None` |
| `rx_m_named(m, name)` | `m.group(name)` |
| `rx_m_start(m, g)`, `rx_m_end(m, g)` | `m.start(g)`, `m.end(g)`, in code points |
| `rx_m_byte_start(m, g)`, `rx_m_byte_end(m, g)` | the same as UTF-8 byte offsets into the Flow string |
| `rx_m_expand(m, template)` | `m.expand(template)` |

`rx_findall` returns whole matches when the pattern has no group, the
group when it has one, and with two or more groups the groups of each match
one after another, `rx_strs_width(l)` per match. `rx_findall`, `rx_next`,
`rx_sub` and `rx_split` step over empty matches as Python 3.7 and later do:
`rx_sub(rx_compile("x*", 0), "-", "abxd", 0)` is `-a-b--d-`.

A text searched many times can be decoded once with `rx_text`; the
`_cps` form `rx_test_cps(r, cps, n)` searches code points already decoded
with `rx_decode`.

## Tests

`tests/lang/test_stdlib_regex.flow` checks 82 calls against the results
CPython gives. `challenges/flow-specific/check.sh self-test` checks 43
recorded `re.search` cases, and the challenge checker agrees with CPython
on every catalog pattern over the tracked `.flow` files.
