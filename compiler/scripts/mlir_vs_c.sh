#!/usr/bin/env bash
# The MLIR backend against the C backend, program by program.
#
# Every tracked .flow file that defines main() is built twice the way `flow
# run` builds it: `flow compile` (the C backend) and `flow compile
# --backend=mlir` (compiler/src/mlirgen.flow, flow mlir-lower,
# clang). Both executables run from the repository root with stdin closed
# and a timeout. A program is "same" when both build and the runs agree on
# exit code and stdout. The C backend is the reference: a program it does
# not build is counted apart and never gates.
#
#   ./compiler/scripts/mlir_vs_c.sh
#       run the corpus and print the report
#   --check          fail when fewer programs are "same" than the floor
#   --update         write compiler/mlir_vs_c/report.txt and the floor
#   --failures       list every program the C backend builds that is not same
#   --jobs N         parallel builds (default: half the CPUs)
#   --timeout S      seconds per program run (default 10)
#   --build-timeout S  seconds per build, either backend (default 300)
#   --only REGEX     restrict the corpus to paths matching REGEX
#   --save PATH      also write the per-program table to PATH
#
# Statuses, for programs the C backend builds:
#   same          same exit code and stdout
#   nondet        stdout differs, but so does a second run of either build
#                 (clocks, addresses); exit codes still agree
#   mlir-emit     flowc emits no MLIR (a refusal or a type error)
#   mlir-lower    mlir-opt or mlir-translate rejects the MLIR
#   mlir-link     clang cannot compile or link the lowered LLVM IR
#   mlir-slow     the MLIR build takes longer than --build-timeout
#   run-exit      both build, the exit codes differ
#   run-stdout    both build, same exit code, stdout differs
#   run-timeout   the MLIR build times out and the C build does not
# and for the rest:
#   c-fail        the C backend does not build it (not gated)
#   c-fail-mlir   the C backend does not build it, the MLIR backend does
#
# Failure causes are clustered by the first diagnostic line with file names,
# positions, numbers and quoted names replaced, and ranked by count.
# compiler/mlir_vs_c/nondet.txt lists programs whose stdout depends on the
# clock or the machine; their stdout is not compared.
#
# Needs mlir-opt and mlir-translate (LLVM 22; Homebrew llvm on macOS). The
# floor is kept per OS (`uname -s`).
#
# Env: FLOWC_BIN=<path> tests that binary; by default the checked-in
# bootstrap C is compiled to compiler/build/flowc_bootstrap.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

DATA=compiler/mlir_vs_c
FLOOR_FILE="$DATA/floor.txt"
REPORT="$DATA/report.txt"

run_limited() {
    local secs="$1"
    shift
    if command -v timeout >/dev/null 2>&1; then
        timeout "$secs" "$@"
    else
        perl -e '$SIG{ALRM} = sub { kill 9, $pid; exit 124 }; $pid = fork; if ($pid == 0) { exec @ARGV[1..$#ARGV] } alarm $ARGV[0]; waitpid $pid, 0; exit($? & 127 ? 128 + ($? & 127) : $? >> 8)' "$secs" "$@"
    fi
}

# First diagnostic line, normalized for clustering.
normalize_cause() {
    sed -E \
        -e 's/\x1b\[[0-9;]*m//g' \
        -e "s#$ROOT/##g" \
        -e 's#^[^ :]*\.(flow|c|h|mlir|ll):[0-9]+:[0-9]+: ##' \
        -e 's#^[^ :]*\.(flow|c|h|mlir|ll):[0-9]+: ##' \
        -e 's#[^ ]*\.(flow|c|h|mlir|ll)\b#<file>#g' \
        -e 's/%[A-Za-z0-9_]+/%v/g' \
        -e 's/@[A-Za-z_][A-Za-z0-9_.$]*/@f/g' \
        -e "s/'[^']*'/'X'/g" \
        -e 's/"[^"]*"/"S"/g' \
        -e 's/[0-9]+/N/g' \
        -e 's/[[:space:]]+$//' \
        | cut -c1-160
}

# pick_cause <log> <stage>: the line that says why a build failed.
pick_cause() {
    local log="$1" stage="$2" line="" plain
    plain="$(sed -E 's/\x1b\[[0-9;]*m//g' "$log" | grep -v -E '^(ℹ️|✅|❌|⚠️|🚀)' || true)"
    case "$stage" in
        mlir-emit)
            line="$(printf '%s\n' "$plain" | grep -m1 -E 'unsupported|error' || true)" ;;
        mlir-lower)
            line="$(printf '%s\n' "$plain" | grep -m1 -E 'error:' || true)" ;;
        *)
            line="$(printf '%s\n' "$plain" | grep -m1 -E '(fatal )?error:' || true)"
            if [[ -z "$line" ]]; then
                local sym
                sym="$(printf '%s\n' "$plain" | sed -n -E \
                    -e 's/^[[:space:]]*"_?([^"]+)", referenced from:.*/\1/p' \
                    -e "s/.*undefined reference to \`([^']+)'.*/\\1/p" | head -1)"
                [[ -n "$sym" ]] && line="link: undefined symbol $sym"
            fi ;;
    esac
    [[ -z "$line" ]] && line="$(printf '%s\n' "$plain" | grep -m1 -E '[^[:space:]]' || true)"
    [[ -z "$line" ]] && line="no diagnostic"
    printf '%s\n' "$line" | normalize_cause | tr '\t' ' '
}

# build <backend> <file> <dir>: 0 when <dir>/<base> is an executable; the
# stage that failed on stdout otherwise.
build() {
    local backend="$1" file="$2" dir="$3" rc=0
    local base
    base="$(basename "$file" .flow)"
    if [[ "$backend" == "c" ]]; then
        FLOWC_BIN="$FLOWC_BIN" FLOW_BUILD_ROOT="$dir" run_limited "$BUILD_SECS" ./flow compile "$file" > "$dir/build.log" 2>&1 < /dev/null || rc=$?
    else
        FLOWC_BIN="$FLOWC_BIN" FLOW_BUILD_ROOT="$dir" run_limited "$BUILD_SECS" ./flow compile --backend=mlir "$file" > "$dir/build.log" 2>&1 < /dev/null || rc=$?
    fi
    if (( rc == 0 )) && [[ -x "$dir/$base" ]]; then
        return 0
    fi
    if [[ "$backend" == "c" ]]; then
        echo "c-fail"
    elif (( rc == 124 || rc == 137 )); then
        echo "mlir-slow"
    elif grep -q 'FLOW MLIR compilation failed' "$dir/build.log"; then
        echo "mlir-emit"
    elif grep -q 'MLIR lowering failed' "$dir/build.log"; then
        echo "mlir-lower"
    else
        echo "mlir-link"
    fi
    return 1
}

# run_one <exe> <out>: exit code on stdout ("timeout" on a timeout).
run_one() {
    local ec=0
    run_limited "$SECS" "$1" < /dev/null > "$2" 2> /dev/null || ec=$?
    if (( ec == 124 || ec == 137 )); then
        ec="timeout"
    fi
    echo "$ec"
}

# worker <file> <work>: one TSV record: path status c-exit mlir-exit cause
worker() {
    local file="$1" work="$2"
    local dir
    dir="$(mktemp -d "$work/job.XXXXXX")"
    mkdir -p "$dir/c" "$dir/m"
    local base
    base="$(basename "$file" .flow)"
    local c_ok=1 m_ok=1 c_stage="" m_stage=""
    c_stage="$(build c "$file" "$dir/c")" || c_ok=0
    m_stage="$(build mlir "$file" "$dir/m")" || m_ok=0
    if (( ! c_ok )); then
        if (( m_ok )); then
            printf '%s\tc-fail-mlir\t-\t-\t%s\n' "$file" "$(pick_cause "$dir/c/build.log" c)"
        else
            printf '%s\tc-fail\t-\t-\t%s\n' "$file" "$(pick_cause "$dir/c/build.log" c)"
        fi
        rm -rf "$dir"
        return 0
    fi
    if (( ! m_ok )); then
        printf '%s\t%s\t-\t-\t%s\n' "$file" "$m_stage" "$(pick_cause "$dir/m/build.log" "$m_stage")"
        rm -rf "$dir"
        return 0
    fi
    local ce me st why="-"
    ce="$(run_one "$dir/c/$base" "$dir/c.out")"
    me="$(run_one "$dir/m/$base" "$dir/m.out")"
    if [[ "$me" == "timeout" && "$ce" != "timeout" ]]; then
        st="run-timeout"
        why="MLIR build times out (C exit $ce)"
    elif [[ "$ce" != "$me" ]]; then
        st="run-exit"
        why="exit code differs (C $ce, MLIR $me)"
    elif cmp -s "$dir/c.out" "$dir/m.out" || grep -qxF "$file" "$work/nondet"; then
        st="same"
    else
        # A second run of each: output that changes from run to run is
        # not comparable.
        run_one "$dir/c/$base" "$dir/c.out2" > /dev/null
        run_one "$dir/m/$base" "$dir/m.out2" > /dev/null
        if ! cmp -s "$dir/c.out" "$dir/c.out2" || ! cmp -s "$dir/m.out" "$dir/m.out2"; then
            st="nondet"
        else
            st="run-stdout"
            why="stdout differs at line $(cmp "$dir/c.out" "$dir/m.out" 2>/dev/null | sed -n -E 's/.* line ([0-9]+).*/\1/p' | head -1 || true)"
            [[ "$why" == "stdout differs at line " ]] && why="stdout differs (one is a prefix of the other)"
        fi
    fi
    printf '%s\t%s\t%s\t%s\t%s\n' "$file" "$st" "$ce" "$me" "$why"
    rm -rf "$dir"
}

worker_loop() {
    # --worker <work>: file paths on stdin
    local work="$1" f
    while IFS= read -r f; do
        worker "$f" "$work" >> "$work/results.$$"
    done
}

# The driver is one function, called on the last line, so bash has read the
# whole file before any of it runs and an edit during a run cannot shift it.
main() {
    SECS=10
    BUILD_SECS="${BUILD_SECS:-300}"
    export BUILD_SECS
    if [[ "${1:-}" == "--worker" ]]; then
        SECS="$3"
        worker_loop "$2"
        exit 0
    fi
    local check=0 update=0 failures=0 only="" save=""
    local jobs=$(( $( (getconf _NPROCESSORS_ONLN 2>/dev/null || echo 4) ) / 2 ))
    (( jobs < 1 )) && jobs=1
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --check) check=1 ;;
            --update) update=1 ;;
            --failures) failures=1 ;;
            --jobs) shift; jobs="$1" ;;
            --timeout) shift; SECS="$1" ;;
            --build-timeout) shift; BUILD_SECS="$1" ;;
            --only) shift; only="$1" ;;
            --save) shift; save="$1" ;;
            -h|--help) sed -n '2,46p' "$0"; exit 0 ;;
            *) echo "mlir_vs_c: unknown argument $1" >&2; exit 2 ;;
        esac
        shift
    done

    if ! ./flow mlir-lower --tools > /dev/null 2>&1; then
        echo "mlir_vs_c: mlir-opt / mlir-translate not found (brew install llvm, or set LLVM_PATH)" >&2
        exit 2
    fi

    if [[ -z "${FLOWC_BIN:-}" ]]; then
        mkdir -p compiler/build
        FLOWC_BIN="$ROOT/compiler/build/flowc_bootstrap"
        if [[ ! -x "$FLOWC_BIN" || compiler/bootstrap/flowc_stage_a.c -nt "$FLOWC_BIN" ]]; then
            "${CC:-cc}" -O2 -w -o "$FLOWC_BIN.tmp.$$" compiler/bootstrap/flowc_stage_a.c -lm
            mv -f "$FLOWC_BIN.tmp.$$" "$FLOWC_BIN"
        fi
    fi
    case "$FLOWC_BIN" in /*) ;; *) FLOWC_BIN="$ROOT/$FLOWC_BIN" ;; esac
    export FLOWC_BIN

    mkdir -p "$ROOT/build"
    local work
    work="$(mktemp -d "$ROOT/build/mlir_vs_c.XXXXXX")"
    # shellcheck disable=SC2064
    trap "rm -rf '$work'" EXIT

    git ls-files -z '*.flow' | xargs -0 grep -l -E 'function[[:space:]]+main' 2>/dev/null \
        | LC_ALL=C sort > "$work/files" || true
    if [[ -n "$only" ]]; then
        grep -E "$only" "$work/files" > "$work/files.only" || true
        mv "$work/files.only" "$work/files"
    fi
    touch "$work/nondet"
    if [[ -f "$DATA/nondet.txt" ]]; then
        grep -v -e '^#' -e '^$' "$DATA/nondet.txt" > "$work/nondet" || true
    fi
    local total
    total=$(wc -l < "$work/files" | tr -d ' ')
    git status --porcelain --untracked-files=normal | sed -n 's/^?? //p' | LC_ALL=C sort > "$work/untracked.before"
    echo "mlir_vs_c: $total programs, jobs: $jobs, timeout: ${SECS}s" >&2

    local i=0 f c
    while IFS= read -r f; do
        printf '%s\n' "$f" >> "$work/chunk.$(( i % jobs ))"
        i=$(( i + 1 ))
    done < "$work/files"
    for c in "$work"/chunk.*; do
        [[ -e "$c" ]] || continue
        "$0" --worker "$work" "$SECS" < "$c" &
    done
    wait

    cat "$work"/results.* 2>/dev/null | LC_ALL=C sort > "$work/joined" || true
    git status --porcelain --untracked-files=normal | sed -n 's/^?? //p' | LC_ALL=C sort > "$work/untracked.after"
    if comm -13 "$work/untracked.before" "$work/untracked.after" | grep -q .; then
        echo "mlir_vs_c: the programs left these untracked paths behind:" >&2
        comm -13 "$work/untracked.before" "$work/untracked.after" | sed 's/^/  /' >&2
    fi

    count() { awk -F'\t' -v s="$1" '$2 == s' "$work/joined" | wc -l | tr -d ' '; }
    local same nondet c_built
    same=$(count same)
    nondet=$(count nondet)
    c_built=$(awk -F'\t' '$2 != "c-fail" && $2 != "c-fail-mlir"' "$work/joined" | wc -l | tr -d ' ')
    local m_built
    m_built=$(awk -F'\t' '$2 == "same" || $2 == "nondet" || $2 ~ /^run-/' "$work/joined" | wc -l | tr -d ' ')
    pct() { awk -v a="$1" -v b="$2" 'BEGIN { if (b == 0) print "0.0"; else printf "%.1f", 100 * a / b }'; }

    {
        echo "MLIR backend against the C backend"
        echo
        echo "programs with main():   $total"
        echo "C backend builds:       $c_built"
        echo "MLIR builds too:        $m_built of $c_built ($(pct "$m_built" "$c_built")%)"
        echo "same run:               $same of $c_built ($(pct "$same" "$c_built")%)"
        echo "nondeterministic:       $nondet"
        echo
        echo "by status:"
        cut -f2 "$work/joined" | sort | uniq -c | sort -rn | awk '{ printf "  %-15s %5d\n", $2, $1 }'
        echo
        echo "failure causes, ranked (count, status, first diagnostic):"
        awk -F'\t' '$2 != "same" && $2 != "nondet" && $2 != "c-fail" && $2 != "c-fail-mlir" { print $2 "\t" $5 }' "$work/joined" \
            | sort | uniq -c | sort -rn \
            | awk '{ c = $1; $1 = ""; sub(/^ /, ""); split($0, a, "\t"); printf "  %5d  %-12s %s\n", c, a[1], a[2] }' | head -60
    } > "$work/report"
    cat "$work/report"

    if [[ -n "$save" ]]; then
        cp "$work/joined" "$save"
    fi
    if (( failures )); then
        echo
        echo "programs the C backend builds that are not same:"
        awk -F'\t' '$2 != "same" && $2 != "nondet" && $2 != "c-fail" && $2 != "c-fail-mlir" { printf "  %-12s %s  (%s)\n", $2, $1, $5 }' "$work/joined"
    fi

    local os
    os="$(uname -s)"
    if (( update )); then
        mkdir -p "$DATA"
        cp "$work/report" "$REPORT"
        {
            echo "# Programs built by both backends with the same run, per OS (uname -s)."
            echo "# mlir_vs_c.sh --check fails below it. --update sets it FLOOR_MARGIN"
            echo "# (default 5) under the run, for timing programs that are flaky in parallel."
            if [[ -f "$FLOOR_FILE" ]]; then
                grep -v -E "^(#|$os )" "$FLOOR_FILE" || true
            fi
            echo "$os $(( same - ${FLOOR_MARGIN:-5} ))"
        } > "$work/floor"
        mv "$work/floor" "$FLOOR_FILE"
        echo
        echo "wrote $REPORT and floor $os $(( same - ${FLOOR_MARGIN:-5} )) ($same same)"
    fi

    if (( check )); then
        local floor=""
        if [[ -f "$FLOOR_FILE" ]]; then
            floor="$(awk -v os="$os" '$1 == os { print $2 }' "$FLOOR_FILE")"
        fi
        echo
        if [[ -n "$only" ]]; then
            echo "mlir_vs_c: --only runs part of the corpus; the floor is not checked"
        elif [[ -z "$floor" ]]; then
            echo "mlir_vs_c: no floor recorded for $os; $same same (not gated)"
        elif (( same < floor )); then
            echo "mlir_vs_c regressed: $same < floor $floor on $os" >&2
            exit 1
        else
            echo "mlir_vs_c OK: $same >= floor $floor on $os"
            if (( same > floor + ${FLOOR_MARGIN:-5} )); then
                echo "(run ./compiler/scripts/mlir_vs_c.sh --update to raise the floor)"
            fi
        fi
    fi
}

main "$@"
