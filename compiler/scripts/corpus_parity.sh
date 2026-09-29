#!/usr/bin/env bash
# Corpus parity between the flowc host and the Python host on the C backend.
#
# Every tracked .flow file that defines main() is built the way `flow run`
# builds it (`flow compile`, the dependency sync aside), once with
# FLOW_HOST=flowc and once with FLOW_HOST=python, and both executables run
# with a timeout from the repository root with stdin closed. A file is at
# parity when both hosts reject it, or when both build it and the runs agree
# on exit code and stdout.
#
#   ./compiler/scripts/corpus_parity.sh
#       flowc live, Python from the recorded goldens in
#       compiler/corpus_parity/python_golden.tsv. Needs no Python.
#   ./compiler/scripts/corpus_parity.sh --python
#       also run the Python host live and compare flowc against it.
#   ./compiler/scripts/corpus_parity.sh --python --record
#       as --python, then rewrite the goldens from the live Python results.
#   --check          fail when fewer files are at parity than the floor
#   --update         write compiler/corpus_parity/report.txt and the floor
#   --failures       list every file not at parity with its cause
#   --jobs N         parallel builds (default: half the CPUs)
#   --timeout S      seconds per program run (default 10)
#   --only REGEX     restrict the corpus to paths matching REGEX
#   --save PATH      also write the per-file table (path, status, Python
#                    build and exit, flowc build and exit, cause) to PATH
#
# The goldens hold, per file, the Python result: build (ok, reject, ccfail),
# exit code, a checksum of stdout, and whether stdout changed between two
# runs of the same Python-built binary (nondet). For nondet files stdout is
# not compared. The floor is kept per OS (`uname -s`), because some programs
# need a platform runtime; --check passes with a note when this OS has no
# floor yet.
#
# Failure causes are clustered by the first diagnostic line with the file
# name, positions, numbers and quoted names replaced, and ranked by count.
#
# Env: FLOWC_BIN=<path> tests that binary; by default the checked-in
# bootstrap C is compiled to compiler/build/flowc_bootstrap.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

DATA=compiler/corpus_parity
GOLDEN="$DATA/python_golden.tsv"
FLOOR_FILE="$DATA/floor.txt"
REPORT="$DATA/report.txt"

# ---------------------------------------------------------------------------
# Worker: build and run one file with one host, print one TSV record:
#   build <TAB> exit <TAB> stdout-cksum <TAB> nondet <TAB> cause
# ---------------------------------------------------------------------------
run_limited() {
    local secs="$1"
    shift
    if command -v timeout >/dev/null 2>&1; then
        timeout "$secs" "$@"
    else
        perl -e '$SIG{ALRM} = sub { kill 9, $pid; exit 124 }; $pid = fork; if ($pid == 0) { exec @ARGV[1..$#ARGV] } alarm $ARGV[0]; waitpid $pid, 0; exit($? & 127 ? 128 + ($? & 127) : $? >> 8)' "$secs" "$@"
    fi
}

sum_of() {
    cksum < "$1" | awk '{print $1 "-" $2}'
}

# First diagnostic line of a failed build, normalized for clustering.
normalize_cause() {
    sed -E \
        -e 's/\x1b\[[0-9;]*m//g' \
        -e "s#$ROOT/##g" \
        -e 's#^[^ :]*\.(flow|c|h):[0-9]+:[0-9]+: ##' \
        -e 's#^[^ :]*\.(flow|c|h):[0-9]+: ##' \
        -e 's#[^ ]*\.(flow|c|h)\b#<file>#g' \
        -e 's/\(byte [0-9]+\)//' \
        -e 's/\(unnamed (struct|union) at [^)]*\)/(unnamed \1)/g' \
        -e "s/unexpected identifier '[^']*'/unexpected identifier/" \
        -e "s/'[A-Za-z_][A-Za-z0-9_.]*'/'X'/g" \
        -e 's/"[^"]*"/"S"/g' \
        -e 's/\b[0-9]+\b/N/g' \
        -e 's/[[:space:]]+$//' \
        | cut -c1-160
}

# Pick the line that says why a build failed. flow-driver's own messages are
# colored and start with an escape; generic flowc summaries come last.
pick_cause() {
    local log="$1" host="$2" kind="$3" line=""
    local plain
    plain="$(sed -E 's/\x1b\[[0-9;]*m//g' "$log" | grep -v -E '^(ℹ️|✅|❌|⚠️|🚀)' || true)"
    if [[ "$kind" == "ccfail" ]]; then
        # An error in the generated .c first: flowc's own C header import
        # can print preprocessor noise from system headers before it.
        line="$(printf '%s\n' "$plain" | grep -m1 -E '\.c:[0-9]+:[0-9]+: (fatal )?error:' || true)"
        if [[ -z "$line" ]]; then
            # Link failure: name the first undefined symbol (Mach-O prints
            # `  "_sym", referenced from:`, GNU ld `undefined reference to `sym'`).
            local sym
            sym="$(printf '%s\n' "$plain" | sed -n -E \
                -e 's/^[[:space:]]*"_?([^"]+)", referenced from:.*/\1/p' \
                -e "s/.*undefined reference to \`([^']+)'.*/\\1/p" | head -1)"
            [[ -n "$sym" ]] && line="link: undefined symbol $sym"
        fi
        [[ -z "$line" ]] && line="$(printf '%s\n' "$plain" | grep -m1 -E 'ld: |linker command failed' || true)"
        [[ -z "$line" ]] && line="$(printf '%s\n' "$plain" | grep -m1 -E '(^|: )(fatal )?error:' || true)"
        [[ -z "$line" ]] && line="$(printf '%s\n' "$plain" | grep -m1 -E 'Undefined symbols|undefined reference|ld: ' || true)"
    else
        line="$(printf '%s\n' "$plain" | grep -v -E '^(flowc emit|flowc gather|flowc bundle tc|stage_a_driver_flow|flowc): ' \
            | grep -v -E '^(Resolving modules|Parsed [0-9]+ functions|Generated C written|Traceback|  File |    )' \
            | grep -m1 -E '[^[:space:]]' || true)"
        [[ -z "$line" ]] && line="$(printf '%s\n' "$plain" | grep -m1 -E '[^[:space:]]' || true)"
    fi
    [[ -z "$line" ]] && line="no diagnostic"
    printf '%s\n' "$line" | normalize_cause | tr '\t' ' '
}

worker() {
    local host="$1" file="$2" secs="$3" work="$4"
    local dir
    dir="$(mktemp -d "$work/job.XXXXXX")"
    local base
    base="$(basename "$file" .flow)"
    local log="$dir/build.log"
    local rc=0
    if [[ "$host" == "python" ]]; then
        FLOW_HOST=python FLOW_BUILD_ROOT="$dir" ./flow compile "$file" > "$log" 2>&1 < /dev/null || rc=$?
    else
        FLOW_HOST=flowc FLOWC_BIN="$FLOWC_BIN" FLOW_BUILD_ROOT="$dir" ./flow compile "$file" > "$log" 2>&1 < /dev/null || rc=$?
    fi
    local build="ok"
    if (( rc != 0 )) || [[ ! -x "$dir/$base" ]]; then
        if grep -q -E 'C compilation/linking failed' "$log"; then
            build="ccfail"
        else
            build="reject"
        fi
        printf '%s\t-\t-\t-\t%s\n' "$build" "$(pick_cause "$log" "$host" "$build")"
        rm -rf "$dir"
        return 0
    fi
    local ec=0
    run_limited "$secs" "$dir/$base" < /dev/null > "$dir/out1" 2> /dev/null || ec=$?
    local nondet="-"
    if [[ "$host" == "python" ]]; then
        local ec2=0
        run_limited "$secs" "$dir/$base" < /dev/null > "$dir/out2" 2> /dev/null || ec2=$?
        nondet="det"
        if ! cmp -s "$dir/out1" "$dir/out2" || (( ec != ec2 )); then
            nondet="nondet"
        fi
    fi
    if (( ec == 124 || ec == 137 )); then
        ec="timeout"
    fi
    printf '%s\t%s\t%s\t%s\t-\n' "$build" "$ec" "$(sum_of "$dir/out1")" "$nondet"
    rm -rf "$dir"
}

worker_loop() {
    # --worker <work> <secs> <hosts>: file paths on stdin
    local work="$1" secs="$2" hosts="$3" f h rec
    while IFS= read -r f; do
        for h in $hosts; do
            rec="$(worker "$h" "$f" "$secs" "$work")"
            printf '%s\t%s\t%s\n' "$h" "$f" "$rec" >> "$work/results.$h.$$"
        done
    done
}

# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
# The driver is one function, called on the last line, so bash has read the
# whole file before any of it runs and an edit during a run cannot shift it.
main() {
    if [[ "${1:-}" == "--worker" ]]; then
        shift
        worker_loop "$@"
        exit 0
    fi
    live_python=0 record=0 check=0 update=0 failures=0 only="" save="" secs=10
    jobs=$(( $( (getconf _NPROCESSORS_ONLN 2>/dev/null || echo 4) ) / 2 ))
    (( jobs < 1 )) && jobs=1
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --python) live_python=1 ;;
            --record) record=1 ;;
            --check) check=1 ;;
            --update) update=1 ;;
            --failures) failures=1 ;;
            --jobs) shift; jobs="$1" ;;
            --timeout) shift; secs="$1" ;;
            --only) shift; only="$1" ;;
            --save) shift; save="$1" ;;
            *) echo "corpus_parity: unknown argument $1" >&2; exit 2 ;;
        esac
        shift
    done
    if (( record && !live_python )); then
        echo "corpus_parity: --record needs --python" >&2
        exit 2
    fi

    if [[ -z "${FLOWC_BIN:-}" ]]; then
        mkdir -p compiler/build
        FLOWC_BIN="$ROOT/compiler/build/flowc_bootstrap"
        if [[ ! -x "$FLOWC_BIN" || compiler/bootstrap/flowc_stage_a.c -nt "$FLOWC_BIN" ]]; then
            "${CC:-cc}" -O2 -w -o "$FLOWC_BIN" compiler/bootstrap/flowc_stage_a.c
        fi
    fi
    case "$FLOWC_BIN" in /*) ;; *) FLOWC_BIN="$ROOT/$FLOWC_BIN" ;; esac
    export FLOWC_BIN

    mkdir -p "$ROOT/build"
    work="$(mktemp -d "$ROOT/build/corpus_parity.XXXXXX")"
    trap 'rm -rf "$work"' EXIT

    # The corpus: tracked files with main(), as `flow run` decides it.
    git ls-files -z '*.flow' | xargs -0 grep -l -E 'function[[:space:]]+main' 2>/dev/null \
        | LC_ALL=C sort > "$work/files" || true
    if [[ -n "$only" ]]; then
        grep -E "$only" "$work/files" > "$work/files.only" || true
        mv "$work/files.only" "$work/files"
    fi
    total=$(wc -l < "$work/files" | tr -d ' ')

    hosts="flowc"
    (( live_python )) && hosts="flowc python"
    echo "corpus_parity: $total files, hosts: $hosts, jobs: $jobs, timeout: ${secs}s" >&2

    # Deal the files round-robin to the workers.
    i=0
    while IFS= read -r f; do
        printf '%s\n' "$f" >> "$work/chunk.$(( i % jobs ))"
        i=$(( i + 1 ))
    done < "$work/files"
    for c in "$work"/chunk.*; do
        [[ -e "$c" ]] || continue
        "$0" --worker "$work" "$secs" "$hosts" < "$c" &
    done
    wait

    cat "$work"/results.flowc.* 2>/dev/null | cut -f2- | LC_ALL=C sort > "$work/flowc.tsv" || true
    if (( live_python )); then
        cat "$work"/results.python.* 2>/dev/null | cut -f2- | LC_ALL=C sort > "$work/python.tsv" || true
        if (( record )); then
            mkdir -p "$DATA"
            if [[ -n "$only" && -f "$GOLDEN" ]]; then
                # Replace only the re-recorded rows.
                cut -f1 "$work/python.tsv" > "$work/redone"
                awk -F'\t' 'NR == FNR { redo[$1] = 1; next } !($1 in redo)' "$work/redone" "$GOLDEN" \
                    | cat - "$work/python.tsv" | LC_ALL=C sort > "$work/golden.new"
                mv "$work/golden.new" "$GOLDEN"
            else
                cp "$work/python.tsv" "$GOLDEN"
            fi
            echo "corpus_parity: recorded $(wc -l < "$work/python.tsv" | tr -d ' ') Python results in $GOLDEN" >&2
        fi
        ref="$work/python.tsv"
    else
        if [[ ! -f "$GOLDEN" ]]; then
            echo "corpus_parity: no goldens at $GOLDEN; run with --python --record" >&2
            exit 2
        fi
        ref="$GOLDEN"
    fi

    # Join: path, py build/exit/sum/nondet/cause, flowc build/exit/sum/-/cause.
    # Files without a recorded Python result are counted as "no golden".
    awk -F'\t' -v OFS='\t' '
        NR == FNR { py[$1] = $2 OFS $3 OFS $4 OFS $5 OFS $6; next }
        {
            if (!($1 in py)) { print $1, "nogolden", "-", "-", "-", "-", "no Python golden for this file"; next }
            split(py[$1], p, "\t")
            pb = p[1]; pe = p[2]; ps = p[3]; pn = p[4]
            fb = $2; fe = $3; fs = $4; fc = $6
            if (pb != "ok" && fb != "ok") { st = "match"; why = "both reject" }
            else if (pb != "ok" && fb == "ok") { st = "flowc-accepts"; why = "Python " pb ": " p[5] }
            else if (fb == "reject") { st = "flowc-reject"; why = fc }
            else if (fb == "ccfail") { st = "flowc-ccfail"; why = fc }
            else if (fe == "timeout" && pe != "timeout") { st = "run-timeout"; why = "flowc build times out (Python exit " pe ")" }
            else if (fe != pe) { st = "run-exit"; why = "exit code differs (Python " pe ", flowc " fe ")" }
            else if (pn != "nondet" && fs != ps) { st = "run-stdout"; why = "stdout differs" }
            else { st = "match"; why = (pb == "ok") ? "same run" : "both reject" }
            print $1, st, pb, pe, fb, fe, why
        }' "$ref" "$work/flowc.tsv" > "$work/joined"

    group_of() {
        awk -F'\t' -v OFS='\t' '{
            n = split($1, a, "/")
            if (n <= 2) g = a[1]
            else if (a[1] == "examples" || a[1] == "tests" || a[1] == "compiler" || a[1] == "benchmarks") g = a[1] "/" a[2]
            else g = a[1]
            print g, $0
        }'
    }

    pass=$(awk -F'\t' '$2 == "match"' "$work/joined" | wc -l | tr -d ' ')
    both_reject=$(awk -F'\t' '$2 == "match" && $3 != "ok"' "$work/joined" | wc -l | tr -d ' ')
    py_ok=$(awk -F'\t' '$3 == "ok"' "$work/joined" | wc -l | tr -d ' ')
    py_ok_match=$(awk -F'\t' '$3 == "ok" && $2 == "match"' "$work/joined" | wc -l | tr -d ' ')
    pct() { awk -v a="$1" -v b="$2" 'BEGIN { if (b == 0) print "0.0"; else printf "%.1f", 100 * a / b }'; }

    {
        echo "flowc corpus parity with the Python host (C backend)"
        echo
        echo "files with main(): $total"
        echo "at parity:         $pass ($(pct "$pass" "$total")%)"
        echo "  same run:        $py_ok_match of $py_ok that Python builds ($(pct "$py_ok_match" "$py_ok")%)"
        echo "  both reject:     $both_reject"
        echo
        echo "by status:"
        cut -f2 "$work/joined" | sort | uniq -c | sort -rn | awk '{ printf "  %-15s %5d\n", $2, $1 }'
        echo
        echo "by directory (parity / files):"
        group_of < "$work/joined" | awk -F'\t' '
            { t[$1]++; if ($3 == "match") p[$1]++ }
            END { for (g in t) printf "  %-32s %5d / %5d  %5.1f%%\n", g, p[g] + 0, t[g], 100 * (p[g] + 0) / t[g] }' | sort
        echo
        echo "failure causes, ranked (count, status, first flowc diagnostic):"
        awk -F'\t' '$2 != "match" { print $2 "\t" $7 }' "$work/joined" | sort | uniq -c | sort -rn \
            | awk '{ c = $1; $1 = ""; sub(/^ /, ""); split($0, a, "\t"); printf "  %5d  %-14s %s\n", c, a[1], a[2] }' | head -60
    } > "$work/report"

    cat "$work/report"

    if [[ -n "$save" ]]; then
        cp "$work/joined" "$save"
    fi

    if (( failures )); then
        echo
        echo "files not at parity:"
        awk -F'\t' '$2 != "match" { printf "  %-14s %s  (%s)\n", $2, $1, $7 }' "$work/joined"
    fi

    os="$(uname -s)"
    if (( update )); then
        mkdir -p "$DATA"
        cp "$work/report" "$REPORT"
        {
            echo "# Files at parity per OS (uname -s). corpus_parity.sh --check fails below it."
            if [[ -f "$FLOOR_FILE" ]]; then
                grep -v -E "^(#|$os )" "$FLOOR_FILE" || true
            fi
            echo "$os $pass"
        } > "$work/floor"
        mv "$work/floor" "$FLOOR_FILE"
        echo
        echo "wrote $REPORT and floor $os $pass"
    fi

    if (( check )); then
        floor=""
        if [[ -f "$FLOOR_FILE" ]]; then
            floor="$(awk -v os="$os" '$1 == os { print $2 }' "$FLOOR_FILE")"
        fi
        echo
        if [[ -z "$floor" ]]; then
            echo "corpus parity: no floor recorded for $os; $pass at parity (not gated)"
        elif (( pass < floor )); then
            echo "corpus parity regressed: $pass < floor $floor on $os" >&2
            awk -F'\t' '$2 != "match" { printf "  %-14s %s  (%s)\n", $2, $1, $7 }' "$work/joined" >&2
            exit 1
        else
            echo "corpus parity OK: $pass >= floor $floor on $os"
            if (( pass > floor )); then
                echo "(run ./compiler/scripts/corpus_parity.sh --update to raise the floor)"
            fi
        fi
    fi
}

main "$@"
