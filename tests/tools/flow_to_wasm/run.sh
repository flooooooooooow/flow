#!/usr/bin/env bash
# Parity test for the legacy converter behind `flow wasm --legacy`
# (scripts/tools/flow_to_wasm/main.flow, shim scripts/flow_to_wasm.sh).
#
# The goldens in tests/tools/flow_to_wasm/expected were recorded from
# wasm/flow_to_wasm.py, the Python converter this tool replaced, before it
# was deleted. Only the usage text changed, to name the shim.
#
# Two stubs keep the cases fast and independent of the toolchain:
#   - a fake flowc (FLOWC_BIN, read by compiler/scripts/flowc_emit.sh)
#     writes fixed C, or fails for a source containing "broken";
#   - a fake emcc records its argv and, per FAKE_EMCC_MODE, succeeds
#     (writing the .js and .wasm), fails `--version`, or fails the compile
#     with more than 200 characters on stderr.
#
# Each case writes <case>.txt: stdout, the exit code and the emcc argv log.
# Generated .c, .html and index.html files are compared byte for byte.
# python and python3 are stubbed out on PATH, so a pass also shows the tool
# needs no Python.
#
# Usage:
#   tests/tools/flow_to_wasm/run.sh            check
#   tests/tools/flow_to_wasm/run.sh --update   rewrite the goldens from the tool
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT"
HERE="$ROOT/tests/tools/flow_to_wasm"
UPDATE=0
[ "${1:-}" = "--update" ] && UPDATE=1

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-to-wasm-tests.XXXXXX")"
work="$(cd "$work" && pwd -P)"
trap 'rm -rf "$work"' EXIT

TOOL="${FLOW_TO_WASM_TOOL:-$ROOT/$(scripts/tools/build_tool.sh flow_to_wasm)}"

# Stubs.
mkdir -p "$work/bin" "$work/nopy"
for py in python python3; do
    printf '#!/bin/sh\necho "%s: stubbed out by the flow_to_wasm test" >&2\nexit 127\n' "$py" > "$work/nopy/$py"
    chmod +x "$work/nopy/$py"
done
cat > "$work/flowc" <<'EOF'
#!/bin/sh
if grep -q broken "$FLOWC_IN"; then
    echo "fake flowc: parse error in $(basename "$FLOWC_IN")" >&2
    exit 1
fi
printf '/* fake flowc: %s */\nint main(void) {\n    return (0 < 1 && 2 > 1) ? 0 : 1;\n}\n' "$(basename "$FLOWC_IN")" > "$FLOWC_OUT"
EOF
cat > "$work/bin/emcc" <<'EOF'
#!/bin/sh
{
    printf 'argv:'
    for a in "$@"; do printf ' [%s]' "$a"; done
    printf '\n'
} >> "$FAKE_EMCC_LOG"
mode="${FAKE_EMCC_MODE:-ok}"
if [ "$1" = "--version" ]; then
    [ "$mode" = verfail ] && { echo "broken emcc" >&2; exit 3; }
    echo "emcc (fake) 1.0"
    exit 0
fi
if [ "$mode" = compfail ]; then
    echo "stdout is dropped"
    printf 'emcc: error: caf\303\251 %0250d\nsecond line\n' 0 >&2
    exit 1
fi
out=""
prev=""
for a in "$@"; do
    [ "$prev" = "-o" ] && out="$a"
    prev="$a"
done
echo "// fake js" > "$out"
printf 'wasm' > "${out%.js}.wasm"
EOF
chmod +x "$work/flowc" "$work/bin/emcc"
export FLOWC_BIN="$work/flowc"

# Sources: CRLF line ends and HTML metacharacters in the page text.
src="$work/src"
mkdir -p "$src"
printf 'function main() -> i32 {\r\n    # a < b && c > d\r\n    return 0\r\n}\r\n' > "$src/hello.flow"
printf 'function main() -> i32 {\n    return 0\n}\n' > "$src/plain.flow"
printf 'function main( {\n  broken\n' > "$src/broken.flow"

BASE_PATH="$work/nopy:/usr/bin:/bin:/usr/sbin:/sbin"
FAKE_PATH="$work/nopy:$work/bin:/usr/bin:/bin:/usr/sbin:/sbin"

pass=0
fail=0

compare() {
    local name="$1" expected="$2" actual="$3"
    if [ "$UPDATE" -eq 1 ]; then
        mkdir -p "$(dirname "$expected")"
        if [ -e "$actual" ]; then cp "$actual" "$expected"; else rm -f "$expected"; fi
        pass=$((pass + 1))
        return
    fi
    if [ ! -e "$actual" ] && [ ! -e "$expected" ]; then
        pass=$((pass + 1))
    elif [ -e "$actual" ] && [ -e "$expected" ] && cmp -s "$expected" "$actual"; then
        pass=$((pass + 1))
    else
        echo "FAIL flow_to_wasm/$name"
        diff -u "$expected" "$actual" 2>&1 | head -40 || true
        fail=$((fail + 1))
    fi
}

# run <case> <emcc mode> <PATH> <repo root> args...
# Runs from $work/cwd so relative output paths print the same everywhere.
run_case() {
    local name="$1" mode="$2" path="$3" repo="$4"
    shift 4
    local log="$work/$name.emcc" txt="$work/$name.txt" rc=0
    : > "$log"
    mkdir -p "$work/cwd"
    (cd "$work/cwd" && FLOW_REPO_ROOT="$repo" FAKE_EMCC_MODE="$mode" FAKE_EMCC_LOG="$log" \
        PATH="$path" "$TOOL" "$@" > "$txt" 2> "$work/$name.err") || rc=$?
    {
        echo "--- exit $rc"
        echo "--- emcc"
        sed "s|$work|WORK|g" "$log"
    } >> "$txt"
    sed -i.bak "s|$work|WORK|g" "$txt" && rm -f "$txt.bak"
    compare "$name.txt" "$HERE/expected/$name.txt" "$txt"
}

# The generated files of one case.
check_files() {
    local name="$1" dir="$2"
    shift 2
    local f
    for f in "$@"; do
        compare "$name/$f" "$HERE/expected/$name/$f" "$dir/$f"
    done
}

run_case usage ok "$FAKE_PATH" "$ROOT"
run_case missing ok "$FAKE_PATH" "$ROOT" nope.flow
run_case wasm ok "$FAKE_PATH" "$ROOT" ../src/hello.flow ./out/wasm/
check_files wasm "$work/cwd/out/wasm" hello.c hello.html
if PATH="$BASE_PATH" command -v emcc > /dev/null 2>&1; then
    echo "SKIP flow_to_wasm/no_emcc (emcc is in /usr/bin or /bin)"
else
    run_case no_emcc ok "$BASE_PATH" "$ROOT" "$src/hello.flow" "$work/cwd/out/no_emcc"
    check_files no_emcc "$work/cwd/out/no_emcc" hello.c hello.html
fi
run_case emcc_version_fails verfail "$FAKE_PATH" "$ROOT" ../src/plain.flow out/verfail extra args
check_files emcc_version_fails "$work/cwd/out/verfail" plain.c plain.html
run_case emcc_compile_fails compfail "$FAKE_PATH" "$ROOT" ../src/plain.flow out/compfail
run_case flowc_fails ok "$FAKE_PATH" "$ROOT" ../src/broken.flow out/broken
check_files flowc_fails "$work/cwd/out/broken" broken.c broken.html

# --all works on <root>/examples and writes <root>/wasm/wasm_examples. Give
# it a root of its own: the scripts the tool needs, three of the listed
# examples (one broken), and a page left over from an earlier run, which the
# index still links.
fake_root="$work/root"
mkdir -p "$fake_root/examples" "$fake_root/compiler" "$fake_root/wasm/wasm_examples"
ln -s "$ROOT/scripts" "$fake_root/scripts"
ln -s "$ROOT/compiler/scripts" "$fake_root/compiler/scripts"
cp "$src/plain.flow" "$fake_root/examples/fibonacci.flow"
cp "$src/hello.flow" "$fake_root/examples/gcd.flow"
cp "$src/broken.flow" "$fake_root/examples/simple_search.flow"
echo "<p>left over</p>" > "$fake_root/wasm/wasm_examples/power.html"
run_case all ok "$FAKE_PATH" "$fake_root" --all
check_files all "$fake_root/wasm/wasm_examples" index.html fibonacci.html gcd.html gcd.c

if [ "$UPDATE" -eq 1 ]; then
    echo "flow_to_wasm: goldens updated ($pass files)"
    exit 0
fi
echo "flow_to_wasm: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
