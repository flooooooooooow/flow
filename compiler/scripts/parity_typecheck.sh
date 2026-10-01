#!/usr/bin/env bash
# Type checker parity between flowc and the retired Python checker
# (src/flow/type_checker.py).
#
# flowc's type check must reject every program the Python checker rejected,
# with the same diagnostic, so type_checker.py can go. The inputs are every
# tracked .flow file, every harness rung of every ```flow documentation block
# (tools/doc_examples `dump`), and the checker snippets that tests/unit fed
# the Python checker, kept as fixtures in compiler/fixtures/typecheck_parity/
# unit/. Each is checked twice: strict (Python `--strict`, the default; flowc
# `compiler/scripts/flowc_emit.sh --strict`) and lenient (Python `--lenient`,
# which rejects only its fatal errors; flowc_emit.sh --lenient, which is what
# `flow compile` runs).
#
#   ./compiler/scripts/parity_typecheck.sh [--check] [--list CLASS] [--only REGEX]
#       flowc live against the goldens in compiler/fixtures/typecheck_parity/
#       golden.txt. Needs no Python. Prints the five-way table per mode:
#
#         agree-accept       both accept
#         agree-same         both reject, same first diagnostic
#         agree-diff         both reject, different first diagnostic
#         py-only            Python rejects, flowc accepts (the dangerous one)
#         flowc-only         flowc rejects, Python accepts
#
#       An input whose front end failed on either side (parse or import
#       error, a Python crash) is counted as `frontend` and not compared.
#       An input whose text changed since the goldens were recorded is
#       `stale`. --check fails when py-only, agree-diff or flowc-only exceed
#       the ceilings in compiler/fixtures/typecheck_parity/ceiling.txt, kept
#       per OS (`uname -s`), since @cImport reads the OS's C headers; an OS
#       with no ceilings is reported and not checked.
#       --list CLASS prints the inputs of one class (py-only, agree-diff, ...)
#       with both diagnostics. --only REGEX and --keys FILE (one key per line)
#       restrict the inputs; --reuse compares the last run's flowc results
#       again without running flowc.
#
#       The checker's warnings (TypeCheckResult.warnings, #678) are compared
#       in strict mode against compiler/fixtures/typecheck_parity/
#       warnings.txt, on the inputs both sides type check with the same
#       verdict, as the sorted list of messages (flowc runs with
#       FLOWC_WARNINGS=all so library modules count too):
#
#         warn-same          both warn the same, or neither warns
#         warn-diff          both warn, with different messages
#         warn-py-only       Python warns, flowc does not
#         warn-flowc-only    flowc warns, Python does not
#
#       --check also holds warn-diff, warn-py-only and warn-flowc-only to
#       their ceilings.
#
#   ./compiler/scripts/parity_typecheck.sh --write-golden REV
#       rewrite the goldens from the Python checker at git revision REV
#       (src/flow from REV, run on the inputs of this tree). The last
#       revision recorded is named in golden.txt.
#
#   ./compiler/scripts/parity_typecheck.sh --write-warnings REV
#       rewrite warnings.txt the same way: the warnings of the strict Python
#       checker at REV on every input.
#
#   ./compiler/scripts/parity_typecheck.sh --extract-unit REV
#       rewrite compiler/fixtures/typecheck_parity/unit/ from the sources
#       REV's tests/unit handed to the Python checker.
#
# A diagnostic is compared as text. flowc prints `<file>:<line>:<col>:
# error: <message>`; the Python checker's message is the same text. The
# Python messages that spell a separator with an em dash or an ellipsis are
# mapped to ": " and "..." first, as parity_effects.sh does.
#
# Env: FLOWC_BIN=<path> tests that binary; by default the checked-in
# bootstrap C is compiled to compiler/build/flowc_bootstrap. JOBS=N sets the
# parallelism (default: the CPU count).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

DATA=compiler/fixtures/typecheck_parity
GOLDEN="$DATA/golden.txt"
WARNINGS="$DATA/warnings.txt"
CEILING="$DATA/ceiling.txt"
WORK="$ROOT/compiler/build/parity_typecheck"

mode="check"
rev=""
check=0
list=""
only=""
reuse=0
keys=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --write-golden) mode="write"; rev="${2:?--write-golden needs a revision}"; shift 2 ;;
        --write-warnings) mode="warnings"; rev="${2:?--write-warnings needs a revision}"; shift 2 ;;
        --extract-unit) mode="extract"; rev="${2:?--extract-unit needs a revision}"; shift 2 ;;
        --check) check=1; shift ;;
        --list) list="${2:?--list needs a class}"; shift 2 ;;
        --only) only="${2:?--only needs a regex}"; shift 2 ;;
        --reuse) reuse=1; shift ;;
        --keys) keys="${2:?--keys needs a file}"; shift 2 ;;
        *) echo "parity_typecheck: unknown argument $1" >&2; exit 2 ;;
    esac
done

jobs="${JOBS:-$(sysctl -n hw.ncpu 2>/dev/null || nproc 2>/dev/null || echo 4)}"
if [[ "$reuse" -eq 0 ]]; then
    rm -rf "$WORK"
fi
mkdir -p "$WORK"

# ---------------------------------------------------------------------------
# The Python checker from REV, for --write-golden and --extract-unit.
# ---------------------------------------------------------------------------
setup_python() {
    local ref="$WORK/pyref"
    mkdir -p "$ref"
    git archive "$1" src/flow tests lib pyproject.toml | tar -x -C "$ref"
    echo "$ref"
}

if [[ "$mode" == "extract" ]]; then
    ref="$(setup_python "$rev")"
    out="$ROOT/$DATA/unit"
    rm -rf "$out"
    mkdir -p "$out"
    # Every source a test lexes and then type checks, captured from inside
    # pytest. Snippets that import another file are left out: the file they
    # import lived in a temporary directory.
    tests=()
    while IFS= read -r t; do tests+=("$t"); done < <(cd "$ref" && grep -l 'TypeChecker\|type_checker' tests/unit/test_*.py | sort)
    (cd "$ref" && PYTHONPATH="$ref/src" PYTHONDONTWRITEBYTECODE=1 python3 - "$out" "${tests[@]}" <<'PY'
import hashlib, os, sys
import pytest
out = sys.argv[1]
tests = sys.argv[2:]
import flow.parser as fp
import flow.type_checker as ftc
current = {"test": None, "code": None}
seen = {}
order = []
orig_lexer_init = fp.Lexer.__init__
def lexer_init(self, code, *a, **k):
    current["code"] = code
    return orig_lexer_init(self, code, *a, **k)
fp.Lexer.__init__ = lexer_init
orig_check = ftc.TypeChecker.check
def check(self, declarations):
    code = current["code"]
    if code is not None and "import " not in code and code not in seen:
        seen[code] = current["test"]
        order.append(code)
    return orig_check(self, declarations)
ftc.TypeChecker.check = check
class Track:
    def pytest_runtest_setup(self, item):
        current["test"] = os.path.basename(str(item.fspath))[:-3]
        current["code"] = None
pytest.main(["-q", "-p", "no:cacheprovider", "--continue-on-collection-errors"] + tests, plugins=[Track()])
counts = {}
for code in order:
    test = seen[code] or "unit"
    counts[test] = counts.get(test, 0) + 1
    name = "%s_%03d.flow" % (test, counts[test])
    with open(os.path.join(out, name), "w") as f:
        f.write(code if code.endswith("\n") else code + "\n")
print("extracted %d snippets" % len(order), file=sys.stderr)
PY
    ) > "$WORK/extract.log" 2>&1 || { tail -20 "$WORK/extract.log" >&2; }
    grep -E '^extracted' "$WORK/extract.log" || true
    exit 0
fi

# ---------------------------------------------------------------------------
# Inputs: <key> TAB <path>, one per line.
# ---------------------------------------------------------------------------
INPUTS="$WORK/inputs.tsv"
if [[ "$reuse" -eq 0 ]]; then
{
    git ls-files '*.flow'
    ls "$DATA"/unit/*.flow 2>/dev/null || true
} | LC_ALL=C sort -u | while IFS= read -r f; do
    printf '%s\t%s\n' "$f" "$ROOT/$f"
done > "$INPUTS.files"

mkdir -p "$WORK/docdump"
FLOW_DOC_DUMP="$WORK/docdump" ./scripts/check_doc_examples.sh dump > "$WORK/docdump.log" 2>&1 || {
    cat "$WORK/docdump.log" >&2
    echo "parity_typecheck: the doc block dump failed" >&2
    exit 1
}
for k in "$WORK"/docdump/d*.key; do
    [[ -e "$k" ]] || continue
    printf 'doc:%s\t%s\n' "$(cat "$k")" "${k%.key}.flow"
done | LC_ALL=C sort -u -t $'\t' -k1,1 > "$INPUTS.docs"
cat "$INPUTS.files" "$INPUTS.docs" > "$INPUTS"
if [[ -n "$only" ]]; then
    grep -E "$only" "$INPUTS" > "$INPUTS.only" || true
    mv "$INPUTS.only" "$INPUTS"
fi
if [[ -n "$keys" ]]; then
    awk -F'\t' 'NR == FNR { want[$0] = 1; next } ($1 in want)' "$keys" "$INPUTS" > "$INPUTS.only"
    mv "$INPUTS.only" "$INPUTS"
fi

# Git blob hash of every input: a golden applies only to the text it was
# recorded from.
cut -f2 "$INPUTS" | git hash-object --stdin-paths > "$INPUTS.hash"
paste "$INPUTS" "$INPUTS.hash" > "$INPUTS.h"
mv "$INPUTS.h" "$INPUTS"
echo "=== parity_typecheck: $(wc -l < "$INPUTS" | tr -d ' ') inputs ==="
fi

# ---------------------------------------------------------------------------
# --write-golden: the Python checker, strict and lenient, on every input.
# ---------------------------------------------------------------------------
if [[ "$mode" == "write" || "$mode" == "warnings" ]]; then
    ref="$(setup_python "$rev")"
    sha="$(git rev-parse --short "$rev")"
    prog="$(cat <<'PY'
import os, signal, sys, warnings
warnings.simplefilter("ignore")
inputs, sha, what = sys.argv[1], sys.argv[2], sys.argv[3]
import flow.module_resolver as mr
# The resolver caches parses in .flow_cache/ next to the root file; keep
# the tree clean.
class _NoCache:
    @staticmethod
    def load(f): raise EOFError
    @staticmethod
    def dump(obj, f): raise OSError
mr.pickle = _NoCache
_real_makedirs = os.makedirs
def _makedirs(path, *a, **k):
    if str(path).endswith(".flow_cache"):
        return
    return _real_makedirs(path, *a, **k)
os.makedirs = _makedirs
from flow.type_checker import TypeChecker
from flow.c_header_parser import resolve_c_imports
from flow.transpiler import _filter_declarations

MODES = {"compile", "c"}
class Timeout(Exception):
    pass
def on_alarm(sig, frame):
    raise Timeout()
signal.signal(signal.SIGALRM, on_alarm)

def clean(msg):
    return str(msg).replace("—", ":").replace(" : ", ": ").replace("…", "...").replace("\\", "\\\\").replace("\n", "\\n")

def run(path, strict):
    signal.alarm(20)
    try:
        decls = mr.resolve_modules(path)
        decls = resolve_c_imports(decls, os.path.dirname(os.path.abspath(path)))
        decls = _filter_declarations(decls, MODES)
    except Timeout:
        return "frontend", ["timeout in the front end"], []
    except BaseException as e:
        signal.alarm(0)
        return "frontend", ["%s: %s" % (type(e).__name__, e)], []
    try:
        tc = TypeChecker()
        tc.strict = strict
        r = tc.check(decls)
    except Timeout:
        return "frontend", ["timeout in the checker"], []
    except BaseException as e:
        signal.alarm(0)
        return "frontend", ["checker crashed: %s: %s" % (type(e).__name__, e)], []
    signal.alarm(0)
    run.warnings = list(r.warnings)
    if strict:
        return ("reject" if r.errors else "accept"), list(r.errors), []
    fatal = list(getattr(r, "fatal_errors", []))
    warn = [e for e in r.errors if e not in fatal]
    return ("reject" if fatal else "accept"), fatal, warn

with open(inputs) as f:
    for line in f:
        key, path, blob = line.rstrip("\n").split("\t")
        cwd = os.getcwd()
        print("@ %s\t%s" % (key, blob))
        if what == "warnings":
            run.warnings = []
            verdict, errs, _ = run(path, True)
            os.chdir(cwd)
            print("S %s" % verdict)
            for w in sorted(clean(w) for w in run.warnings):
                print("W %s" % w)
            sys.stdout.flush()
            continue
        for tag, strict in (("S", True), ("L", False)):
            verdict, errs, warns = run(path, strict)
            os.chdir(cwd)
            print("%s %s" % (tag, verdict))
            for e in errs[:8]:
                print("%s %s" % (tag.lower(), clean(e)))
            for w in warns[:3]:
                print("w %s" % clean(w))
        sys.stdout.flush()
PY
)"
    # One Python process per chunk of inputs, in parallel, joined in order.
    total="$(wc -l < "$INPUTS")"
    awk -v n="$jobs" -v t="$total" -v w="$WORK" '{ c = int((NR - 1) * n / t); printf "%s\n", $0 > sprintf("%s/chunk.%03d", w, c) }' "$INPUTS"
    for c in "$WORK"/chunk.???; do
        PYTHONPATH="$ref/src" PYTHONDONTWRITEBYTECODE=1 python3 -c "$prog" "$c" "$sha" "$mode" > "$c.out" 2> "$c.log" &
    done
    wait
    if [[ "$mode" == "warnings" ]]; then
        { echo "# Python type checker warnings, strict (compiler/scripts/parity_typecheck.sh), rev $sha"
          for c in "$WORK"/chunk.???; do cat "$c.out"; done; } > "$WORK/warnings.new"
        mv "$WORK/warnings.new" "$ROOT/$WARNINGS"
        echo "wrote $WARNINGS ($(grep -c '^@ ' "$WARNINGS") inputs, $(grep -c '^W ' "$WARNINGS") warnings, rev $sha)"
        exit 0
    fi
    { echo "# Python type checker goldens (compiler/scripts/parity_typecheck.sh), rev $sha"
      for c in "$WORK"/chunk.???; do cat "$c.out"; done; } > "$WORK/golden.new"
    mv "$WORK/golden.new" "$ROOT/$GOLDEN"
    echo "wrote $GOLDEN ($(grep -c '^@ ' "$GOLDEN") inputs, rev $sha)"
    exit 0
fi

# ---------------------------------------------------------------------------
# flowc on every input, strict and lenient.
# ---------------------------------------------------------------------------
if [[ "$reuse" -eq 0 ]]; then
if [[ -n "${FLOWC_BIN:-}" ]]; then
    BIN="$FLOWC_BIN"
else
    BIN="$ROOT/compiler/build/flowc_bootstrap"
    "${CC:-cc}" -O2 -w -o "$BIN" compiler/bootstrap/flowc_stage_a.c -lm
fi
[[ "$BIN" == /* ]] || BIN="$ROOT/$BIN"
echo "=== flowc = $BIN ==="

# One record per input and mode: `<key> TAB <S|L> TAB <verdict> TAB <first
# diagnostic>`. The verdict is accept (the type check passed, whatever
# codegen made of it later), reject (the type check failed) or frontend.
cat > "$WORK/one.sh" <<'SH'
#!/usr/bin/env bash
key="$1"; path="$2"; out="$3"; bin="$4"; root="$5"
d="$out/$(printf '%s' "$key" | cksum | cut -d' ' -f1)"
mkdir -p "$d"
for m in S L; do
    flag=--strict
    [[ "$m" == L ]] && flag=--lenient
    rm -f "$d/o.c"
    (cd "$root" && ulimit -t 30 && FLOWC_CHECK_ONLY=1 FLOWC_WARNINGS=all FLOWC_BIN="$bin" compiler/scripts/flowc_emit.sh "$flag" "$path" "$d/o.c") > "$d/log.$m" 2>&1
    rc=$?
    log="$d/log.$m"
    if grep -qE 'parse error|flowc emit: parse failed|bundle tc: (gather|topo|read) failed|read FLOWC_IN failed|expansion overflowed|unsupported in Stage-A|cannot resolve|could not resolve|import not found' "$log"; then
        verdict=frontend
    elif grep -qE 'typecheck failed' "$log"; then
        verdict=reject
    elif grep -q "flowc: type check passed" "$log" || [[ "$rc" -eq 0 && -s "$d/o.c" ]]; then
        verdict=accept
    elif grep -qE 'emit failed|cgen|codegen' "$log"; then
        verdict=accept
    else
        verdict=frontend
    fi
    # -a: a log can echo source bytes that are not valid UTF-8, and GNU grep
    # would then print "binary file matches" instead of the line.
    msg=""
    if [[ "$verdict" == reject ]]; then
        msg="$(sed -n -E 's/^.*:[0-9]+:[0-9]+: error: //p' "$log" | head -1 | sed 's/\\/\\\\/g')"
        if [[ -z "$msg" ]]; then
            msg="$(grep -aE '^flowc tc: |^flowc: |error' "$log" | grep -avE 'typecheck failed|tc_errs=|module check failed|module_errs=' | head -1)"
        fi
    elif [[ "$verdict" == frontend ]]; then
        msg="$(grep -aE 'error|failed|unsupported' "$log" | head -1)"
    fi
    printf '%s\t%s\t%s\t%s\n' "$key" "$m" "$verdict" "$msg"
done
# The checker's warnings in strict mode, sorted, joined with " || ".
warns="$(LC_ALL=C sed -n -E 's/^.*:[0-9]+:[0-9]+: warning: //p' "$d/log.S" | LC_ALL=C sed 's/\\/\\\\/g' | LC_ALL=C sort | awk 'NR > 1 { printf " || " } { printf "%s", $0 }')"
printf '%s\tW\twarn\t%s\n' "$key" "$warns"
SH
chmod +x "$WORK/one.sh"
mkdir -p "$WORK/runs"
cut -f1,2 "$INPUTS" | while IFS=$'\t' read -r key path; do
    printf '%s\0%s\0' "$key" "$path"
done | xargs -0 -n 2 -P "$jobs" sh -c '"$0" "$1" "$2" "'"$WORK/runs"'" "'"$BIN"'" "'"$ROOT"'"' "$WORK/one.sh" \
    > "$WORK/flowc.tsv"
fi

# ---------------------------------------------------------------------------
# Compare.
# ---------------------------------------------------------------------------
[[ -f "$GOLDEN" ]] || { echo "parity_typecheck: no goldens ($GOLDEN); run --write-golden REV" >&2; exit 1; }
[[ -f "$WARNINGS" ]] || { echo "parity_typecheck: no warning goldens ($WARNINGS); run --write-warnings REV" >&2; exit 1; }
awk -F'\t' -v list="$list" -v inputs="$INPUTS" -v report="$WORK/report.txt" -v wfile="$WARNINGS" '
function norm(s) { gsub(/\\n/, " ", s); return s }
BEGIN {
    while ((getline line < inputs) > 0) {
        split(line, ip, "\t"); blob[ip[1]] = ip[3]; want[ip[1]] = 1
    }
    # warnings.txt: "@ key TAB blob", "S verdict", "W message" (sorted).
    while ((getline line < wfile) > 0) {
        if (line ~ /^#/) continue
        if (substr(line, 1, 2) == "@ ") {
            wcur = substr(line, 3); split(wcur, q, "\t"); wcur = q[1]; wblob[wcur] = q[2]; pw[wcur] = ""; continue
        }
        if (substr(line, 1, 2) == "W ") {
            pw[wcur] = (pw[wcur] == "" ? "" : pw[wcur] " || ") substr(line, 3)
        }
    }
}
FNR != NR && $2 == "W" { fw[$1] = $4; next }
FNR == NR {
    # golden.txt
    if ($0 ~ /^#/) next
    if (substr($0, 1, 2) == "@ ") {
        cur = substr($0, 3); split(cur, q, "\t"); cur = q[1]; gblob[cur] = q[2]; next
    }
    tag = substr($0, 1, 1); rest = substr($0, 3)
    if (tag == "S" || tag == "L") { pv[cur, tag] = rest; next }
    if (tag == "s" && !((cur, "S") in pm)) { pm[cur, "S"] = rest; next }
    if (tag == "l" && !((cur, "L") in pm)) { pm[cur, "L"] = rest; next }
    next
}
{
    key = $1; m = $2; fv = $3; fm = $4
    if (!(key in gblob)) { cls = "no-golden" }
    else if (gblob[key] != blob[key]) { cls = "stale" }
    else {
        pvv = pv[key, m]
        if (pvv == "frontend" || fv == "frontend") cls = "frontend"
        else if (pvv == "accept" && fv == "accept") cls = "agree-accept"
        else if (pvv == "reject" && fv == "accept") cls = "py-only"
        else if (pvv == "accept" && fv == "reject") cls = "flowc-only"
        else if (norm(pm[key, m]) == norm(fm)) cls = "agree-same"
        else cls = "agree-diff"
    }
    count[m, cls]++
    if (list != "" && cls == list) {
        printf "%s [%s]\n    python: %s\n    flowc:  %s\n", key, (m == "S" ? "strict" : "lenient"), pm[key, m], fm
    }
    # Warnings are compared where both sides type check the same way.
    if (m == "S" && (cls == "agree-accept" || cls == "agree-same" || cls == "agree-diff") && (key in wblob) && wblob[key] == blob[key]) {
        wkeys[key] = 1
    }
}
END {
    for (key in wkeys) {
        p = pw[key]; f = fw[key]
        if (p == f) wc = "warn-same"
        else if (p != "" && f != "") wc = "warn-diff"
        else if (p != "") wc = "warn-py-only"
        else wc = "warn-flowc-only"
        count["S", wc]++
        if (list != "" && wc == list) {
            printf "%s [strict]\n    python: %s\n    flowc:  %s\n", key, p, f
        }
    }
    n = split("agree-accept agree-same agree-diff py-only flowc-only frontend stale no-golden warn-same warn-diff warn-py-only warn-flowc-only", cl, " ")
    printf "%-16s %8s %8s\n", "class", "strict", "lenient" > report
    for (i = 1; i <= n; i++) printf "%-16s %8d %8d\n", cl[i], count["S", cl[i]], count["L", cl[i]] > report
    close(report)
}' "$GOLDEN" "$WORK/flowc.tsv"
echo
cat "$WORK/report.txt"

if [[ "$check" -eq 1 ]]; then
    [[ -f "$CEILING" ]] || { echo "parity_typecheck: no ceiling file $CEILING" >&2; exit 1; }
    os="$(uname -s)"
    if ! grep -qE "^$os " "$CEILING"; then
        # The goldens read @cImport headers of the OS they were recorded on;
        # another OS can differ where a header declares something else.
        echo "NOTE parity_typecheck: no ceilings for $os in $CEILING; not checked"
        exit 0
    fi
    fail=0
    while read -r cos cls ms ml; do
        [[ -z "$cos" || "$cos" == \#* || "$cos" != "$os" ]] && continue
        read -r _ gs gl < <(grep -E "^$cls " "$WORK/report.txt")
        if (( gs > ms || gl > ml )); then
            echo "FAIL $cls: strict $gs (ceiling $ms), lenient $gl (ceiling $ml)"
            fail=1
        fi
    done < "$CEILING"
    [[ "$fail" -eq 0 ]] && echo "PASS parity_typecheck within the ceilings"
    exit "$fail"
fi
