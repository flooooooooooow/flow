#!/usr/bin/env bash
# Parity gate for the Shader DSL (FSL) port (compiler/src/shader_dsl.flow).
#
# The Flow port replaced src/flow/shader_dsl.py, shader_codegen.py and
# shader_codegen_wgsl.py. Their output was recorded as goldens beside each
# fixture in compiler/fixtures/shader_dsl/:
#
#   <name>.metal.expected / <name>.wgsl.expected   every file the build
#       wrote, concatenated in name order under `=== <file>` headers
#   <name>.metal.error / <name>.wgsl.error          the exception text
#   <name>.expand                                   host-stub outcome:
#       `stub`, `pass` (source unchanged) or `err: <message>`
#   <name>.name                                     optional fill name
#   examples__gpu__<stem>.<target>.sha256           digest of the bundle for
#       each shader example (the Metal galleries run to megabytes)
#
#   ./compiler/scripts/parity_shader_dsl.sh
#       flowc vs goldens, the host stub over every tracked .flow file, and
#       the examples built end to end with python and python3 stubbed out.
#
#   ./compiler/scripts/parity_shader_dsl.sh --python <rev>
#       also run the original Python from git revision <rev> over every
#       tracked .flow file, both targets, and require byte-identical output
#       (or the same error) from flowc. Needs python3 and git.
#
#   ./compiler/scripts/parity_shader_dsl.sh --write-golden <rev>
#       rewrite the goldens from the Python at <rev>.
#
# The last Python revision is 0b6d6ac4 (origin/main before the port).
#
# One deliberate difference: flowc stubs a module only when a fill head
# starts a line. The Python matched one anywhere, so it stubbed the two
# tests/lang programs that name the syntax in a string literal.
#
# Env: FLOWC_BIN=<path> tests that binary instead of building
# compiler/build/flowc_bootstrap from the checked-in bootstrap C.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

FIX=compiler/fixtures/shader_dsl
WORK=compiler/build/parity_shader_dsl
DEVIATION=" tests/lang/test_dsl_detect.flow tests/lang/test_shader_dsl_port.flow "
STUB=$'function main() -> i32 {\n    return 0\n}'
mode="${1:-}"
rev="${2:-}"
rm -rf "$WORK"
mkdir -p "$WORK/flowc" "$WORK/python"

if [[ -n "${FLOWC_BIN:-}" ]]; then
    BIN="$FLOWC_BIN"
else
    BIN=compiler/build/flowc_bootstrap
    "${CC:-cc}" -O2 -o "$BIN" compiler/bootstrap/flowc_stage_a.c -lm 2>/dev/null
fi
case "$BIN" in
    /*) ;;
    *) BIN="$ROOT/$BIN" ;;
esac
echo "=== parity_shader_dsl: flowc = ${BIN} ==="

git ls-files '*.flow' | LC_ALL=C sort > "$WORK/corpus.txt"
# Shader examples: a line that opens a fill block.
examples=()
while IFS= read -r f; do
    examples+=("$f")
done < <(grep -lE '^[[:space:]]*shader[[:space:]]+fill[[:space:]]+[A-Za-z_][A-Za-z0-9_]*[[:space:]]*\{' \
    $(grep '^examples/' "$WORK/corpus.txt") | LC_ALL=C sort)
fixtures=()
for f in "$FIX"/*.flow; do
    fixtures+=("$f")
done

key_of() {
    local f="$1"
    f="${f//\//__}"
    printf '%s\n' "${f%.flow}"
}

name_of() {
    local side="${1%.flow}.name"
    if [[ -f "$side" ]]; then
        tr -d '\n' < "$side"
    fi
}

# bundle <dir>: every file in name order under a header.
bundle() {
    local d="$1" f
    for f in $(cd "$d" && ls | LC_ALL=C sort); do
        printf '=== %s\n' "$f"
        cat "$d/$f"
        printf '\n'
    done
}

# flowc_build <in> <target> <name> <out-prefix>: <out-prefix>.out (bundle)
# or <out-prefix>.err (message).
flowc_build() {
    local in="$1" target="$2" name="$3" pre="$4"
    local dir="$pre.d"
    rm -rf "$dir" "$pre.out" "$pre.err"
    mkdir -p "$dir"
    local log code
    set +e
    log="$(FLOWC_SHADER="$target" FLOWC_IN="$in" FLOWC_OUT="$dir" FLOWC_SHADER_NAME="$name" "$BIN" 2>&1)"
    code=$?
    set -e
    if [[ "$code" -ne 0 ]]; then
        if [[ "$log" == "flowc shader: "* ]]; then
            printf '%s\n' "${log#flowc shader: }" > "$pre.err"
        else
            printf 'flowc failed without a shader diagnostic: %s\n' "$log" > "$pre.err"
        fi
    else
        bundle "$dir" > "$pre.out"
    fi
    rm -rf "$dir"
}

# flowc_expand <in> <out>: stub, pass or err: <message>.
flowc_expand() {
    local in="$1" out="$2" log code
    set +e
    log="$(FLOWC_SHADER=expand FLOWC_IN="$in" FLOWC_OUT="$WORK/expand.flow" "$BIN" 2>&1)"
    code=$?
    set -e
    if [[ "$code" -ne 0 ]]; then
        printf 'err: %s\n' "${log#flowc shader: }" > "$out"
    elif cmp -s "$in" "$WORK/expand.flow"; then
        echo pass > "$out"
    elif [[ "$(cat "$WORK/expand.flow")" == "$STUB" ]]; then
        echo stub > "$out"
    else
        echo other > "$out"
    fi
}

# python_ref <rev> <list-file> <outdir>: the Python at <rev>. The list holds
# `path<TAB>name` rows; each gets <key>.<target>.out / .err and <key>.expand.
python_ref() {
    local r="$1" list="$2" outdir="$3" m
    mkdir -p "$WORK/pyref/fslref"
    : > "$WORK/pyref/fslref/__init__.py"
    for m in shader_dsl shader_codegen shader_codegen_wgsl; do
        git show "${r}:src/flow/${m}.py" > "$WORK/pyref/fslref/${m}.py"
    done
    python3 - "$WORK/pyref" "$list" "$outdir" <<'PY'
import os, shutil, sys, tempfile
sys.path.insert(0, sys.argv[1])
from fslref import shader_dsl as dsl
from fslref.shader_codegen import compile_shader_file as metal
from fslref.shader_codegen_wgsl import compile_shader_file_wgsl as wgsl

outdir = sys.argv[3]

def bundle(d):
    parts = []
    for name in sorted(os.listdir(d)):
        with open(os.path.join(d, name), "rb") as f:
            parts.append(b"=== " + name.encode() + b"\n" + f.read() + b"\n")
    return b"".join(parts)

for row in open(sys.argv[2], encoding="utf-8").read().split("\n"):
    if not row:
        continue
    path, name = row.split("\t")
    key = path.replace("/", "__")[: -len(".flow")]
    for target, build in (("metal", metal), ("wgsl", wgsl)):
        tmp = tempfile.mkdtemp()
        try:
            build(path, tmp, shader_name=name or None)
            with open(os.path.join(outdir, f"{key}.{target}.out"), "wb") as f:
                f.write(bundle(tmp))
        except Exception as e:
            with open(os.path.join(outdir, f"{key}.{target}.err"), "w", encoding="utf-8") as f:
                f.write(str(e) + "\n")
        finally:
            shutil.rmtree(tmp)
    # module_resolver: an FSL module becomes a stub main.
    with open(path, encoding="utf-8", errors="surrogateescape") as f:
        text = f.read()
    try:
        if dsl.has_fill_shader_dsl(text):
            mod = dsl.extract_shader_module(text)
            res = "stub" if mod.fills else "err: Fill-shader module has no `shader fill` blocks"
        else:
            res = "pass"
    except SyntaxError as e:
        res = "err: " + str(e)
    with open(os.path.join(outdir, f"{key}.expand"), "w", encoding="utf-8") as f:
        f.write(res + "\n")
PY
}

list_rows() {
    local f
    for f in "$@"; do
        printf '%s\t%s\n' "$f" "$(name_of "$f")"
    done
}

if [[ "$mode" == "--write-golden" ]]; then
    [[ -n "$rev" ]] || { echo "usage: $0 --write-golden <rev>" >&2; exit 2; }
    list_rows "${fixtures[@]}" "${examples[@]}" > "$WORK/list.txt"
    python_ref "$rev" "$WORK/list.txt" "$WORK/python"
    rm -f "$FIX"/*.expected "$FIX"/*.error "$FIX"/*.expand "$FIX"/*.sha256
    for f in "${fixtures[@]}"; do
        k="$(key_of "$f")"
        base="${f%.flow}"
        for t in metal wgsl; do
            if [[ -f "$WORK/python/$k.$t.err" ]]; then
                cp "$WORK/python/$k.$t.err" "$base.$t.error"
            else
                cp "$WORK/python/$k.$t.out" "$base.$t.expected"
            fi
        done
        cp "$WORK/python/$k.expand" "$base.expand"
    done
    for f in "${examples[@]}"; do
        k="$(key_of "$f")"
        for t in metal wgsl; do
            shasum -a 256 < "$WORK/python/$k.$t.out" | cut -d' ' -f1 > "$FIX/$k.$t.sha256"
        done
    done
    echo "wrote goldens for ${#fixtures[@]} fixtures and ${#examples[@]} examples from ${rev}"
    exit 0
fi

fail=0
pass=0

# 1. Fixtures and examples vs goldens.
for f in "${fixtures[@]}" "${examples[@]}"; do
    k="$(key_of "$f")"
    base="${f%.flow}"
    for t in metal wgsl; do
        flowc_build "$f" "$t" "$(name_of "$f")" "$WORK/flowc/$k.$t"
        got="$WORK/flowc/$k.$t"
        if [[ -f "$FIX/$k.$t.sha256" ]]; then
            if [[ -f "$got.out" ]] && [[ "$(shasum -a 256 < "$got.out" | cut -d' ' -f1)" == "$(cat "$FIX/$k.$t.sha256")" ]]; then
                pass=$((pass + 1))
            else
                fail=$((fail + 1))
                echo "FAIL $f ($t): digest differs from $FIX/$k.$t.sha256" >&2
                [[ -f "$got.err" ]] && echo "     flowc error: $(cat "$got.err")" >&2
            fi
        elif [[ -f "$base.$t.error" ]]; then
            if [[ -f "$got.err" ]] && cmp -s "$base.$t.error" "$got.err"; then
                pass=$((pass + 1))
            else
                fail=$((fail + 1))
                echo "FAIL $f ($t): want error: $(cat "$base.$t.error")" >&2
                [[ -f "$got.err" ]] && echo "     got error:  $(cat "$got.err")" >&2
            fi
        elif [[ -f "$base.$t.expected" ]]; then
            if [[ -f "$got.out" ]] && cmp -s "$base.$t.expected" "$got.out"; then
                pass=$((pass + 1))
            else
                fail=$((fail + 1))
                echo "FAIL $f ($t): output differs from $base.$t.expected" >&2
                if [[ -f "$got.out" ]]; then
                    diff "$base.$t.expected" "$got.out" | head -20 >&2 || true
                else
                    echo "     flowc error: $(cat "$got.err")" >&2
                fi
            fi
        else
            fail=$((fail + 1))
            echo "FAIL $f ($t): no golden" >&2
        fi
    done
    if [[ -f "$base.expand" ]]; then
        flowc_expand "$f" "$WORK/flowc/$k.expand"
        if cmp -s "$base.expand" "$WORK/flowc/$k.expand"; then
            pass=$((pass + 1))
        else
            fail=$((fail + 1))
            echo "FAIL $f: host stub $(cat "$WORK/flowc/$k.expand"), want $(cat "$base.expand")" >&2
        fi
    fi
done
echo "fixtures: pass=${pass} fail=${fail}"

# 2. Host stub over every tracked .flow: the shader examples become the
# stub, every other file passes through byte for byte.
corpus_n=0
corpus_fail=0
while IFS= read -r f; do
    [[ "$f" == "$FIX"/* ]] && continue
    k="$(key_of "$f")"
    corpus_n=$((corpus_n + 1))
    flowc_expand "$f" "$WORK/flowc/$k.expand"
    want=pass
    for e in "${examples[@]}"; do
        [[ "$e" == "$f" ]] && want=stub
    done
    if [[ "$(cat "$WORK/flowc/$k.expand")" != "$want" ]]; then
        corpus_fail=$((corpus_fail + 1))
        echo "FAIL host stub $f: $(cat "$WORK/flowc/$k.expand"), want $want" >&2
    fi
done < "$WORK/corpus.txt"
echo "host stub: files=${corpus_n} stubbed=${#examples[@]} fail=${corpus_fail}"
fail=$((fail + corpus_fail))

# 3. Optional: live diff against the Python at <rev>, every tracked file.
if [[ "$mode" == "--python" ]]; then
    [[ -n "$rev" ]] || { echo "usage: $0 --python <rev>" >&2; exit 2; }
    list_rows $(cat "$WORK/corpus.txt") > "$WORK/list.txt"
    python_ref "$rev" "$WORK/list.txt" "$WORK/python"
    live_n=0
    live_fail=0
    while IFS= read -r f; do
        k="$(key_of "$f")"
        nm="$(name_of "$f")"
        for t in metal wgsl; do
            live_n=$((live_n + 1))
            [[ -f "$WORK/flowc/$k.$t.out" || -f "$WORK/flowc/$k.$t.err" ]] || \
                flowc_build "$f" "$t" "$nm" "$WORK/flowc/$k.$t"
            py="$WORK/python/$k.$t"
            got="$WORK/flowc/$k.$t"
            if [[ -f "$py.err" ]]; then
                if ! cmp -s "$py.err" "$got.err" 2>/dev/null; then
                    live_fail=$((live_fail + 1))
                    echo "FAIL live $f ($t): python error differs" >&2
                fi
            elif ! cmp -s "$py.out" "$got.out" 2>/dev/null; then
                live_fail=$((live_fail + 1))
                echo "FAIL live $f ($t): python output differs" >&2
            fi
        done
        live_n=$((live_n + 1))
        [[ -f "$WORK/flowc/$k.expand" ]] || flowc_expand "$f" "$WORK/flowc/$k.expand"
        if [[ "$DEVIATION" == *" $f "* ]]; then
            if [[ "$(cat "$WORK/python/$k.expand")" != stub || "$(cat "$WORK/flowc/$k.expand")" != pass ]]; then
                live_fail=$((live_fail + 1))
                echo "FAIL live $f: expected the documented deviation (python stub, flowc pass)" >&2
            fi
        elif ! cmp -s "$WORK/python/$k.expand" "$WORK/flowc/$k.expand"; then
            live_fail=$((live_fail + 1))
            echo "FAIL live $f: host stub python=$(cat "$WORK/python/$k.expand") flowc=$(cat "$WORK/flowc/$k.expand")" >&2
        fi
    done < "$WORK/corpus.txt"
    echo "live python@${rev}: files=$(wc -l < "$WORK/corpus.txt" | tr -d ' ') checks=${live_n} fail=${live_fail} (deviation:${DEVIATION% })"
    fail=$((fail + live_fail))
fi

# 4. End to end with python and python3 stubbed out: ./flow shader builds
# the Metal gallery and WGSL, xcrun metal accepts the Metal when present,
# and a shader example compiles to a host program that runs.
NOPY="$WORK/nopy"
mkdir -p "$NOPY"
for py in python python3; do
    printf '#!/bin/sh\necho "%s $*" >> "%s/calls.log"\nexit 127\n' "$py" "$NOPY" > "$NOPY/$py"
    chmod +x "$NOPY/$py"
done
: > "$NOPY/calls.log"
e2e_fail=0
e2e() {
    PATH="$NOPY:$PATH" FLOWC_BIN="$BIN" "$@" > "$WORK/e2e.log" 2>&1
}
if e2e ./flow shader examples/gpu/shader_showcase.flow --emit-only; then
    gallery=build/shaders/shader_showcase_gallery.metal
    echo "e2e: ./flow shader --emit-only wrote $(grep -c . build/shaders/shader_showcase_gallery.entries) entries"
    if xcrun -sdk macosx -f metal >/dev/null 2>&1; then
        if xcrun -sdk macosx metal -c "$gallery" -o "$WORK/showcase.air" 2> "$WORK/metal.log"; then
            echo "e2e: xcrun metal compiled $gallery"
        else
            e2e_fail=$((e2e_fail + 1))
            echo "FAIL e2e: xcrun metal rejected $gallery" >&2
            head -20 "$WORK/metal.log" >&2
        fi
    fi
else
    e2e_fail=$((e2e_fail + 1))
    echo "FAIL e2e: ./flow shader --emit-only" >&2
    tail -5 "$WORK/e2e.log" >&2
fi
if e2e ./flow shader examples/gpu/vgpu/gradient.flow --wgsl --name vgpu_gradient && \
        grep -q 'fn vgpu_gradient_frag' build/shaders/vgpu_gradient_fill.wgsl; then
    echo "e2e: ./flow shader --wgsl wrote build/shaders/vgpu_gradient_fill.wgsl"
else
    e2e_fail=$((e2e_fail + 1))
    echo "FAIL e2e: ./flow shader --wgsl" >&2
    tail -5 "$WORK/e2e.log" >&2
fi
if FLOW_BUILD_ROOT="$ROOT/$WORK/fbuild" e2e ./flow compile examples/gpu/shader_plasma.flow && \
        e2e "$WORK/fbuild/shader_plasma"; then
    echo "e2e: ./flow compile shader_plasma host stub exit 0"
else
    e2e_fail=$((e2e_fail + 1))
    echo "FAIL e2e: ./flow compile examples/gpu/shader_plasma.flow" >&2
    tail -5 "$WORK/e2e.log" >&2
fi
if [[ -s "$NOPY/calls.log" ]]; then
    e2e_fail=$((e2e_fail + 1))
    echo "FAIL e2e: python was called:" >&2
    cat "$NOPY/calls.log" >&2
else
    echo "e2e: no python call logged"
fi
fail=$((fail + e2e_fail))

if [[ "$fail" -ne 0 ]]; then
    echo "parity_shader_dsl: FAIL (${fail})"
    exit 1
fi
echo "parity_shader_dsl: PASS"
