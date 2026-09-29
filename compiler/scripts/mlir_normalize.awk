# Normalize textual MLIR for the parity gate (compiler/scripts/parity_mlir.sh).
#
# The Flow emitter and the Python generator number SSA values and blocks
# differently: Python allocates a number before it emits the op that defines
# it (a call result gets its number before the argument values do), and it
# indents region bodies unevenly. Neither changes the program. This filter
# makes the two comparable:
#
#   * leading and trailing blanks are dropped, and empty lines skipped;
#   * every %<digits> value is renamed %v<k> in order of first appearance
#     (%argN block arguments and named values such as %in are kept);
#   * every ^bb<digits> label is renamed ^b<k> the same way;
#   * the value names start over at each `gpu.func`, which the GPU
#     generator numbers from %1 on its own.
#
# Global string constants (`llvm.mlir.global ...`) are left as they are, so
# a format string such as "%5d" is never touched. Plain awk, no Python.
{
    line = $0
    sub(/^[ \t]+/, "", line)
    sub(/[ \t]+$/, "", line)
    if (line == "") {
        next
    }
    if (index(line, "llvm.mlir.global ") == 1) {
        print line
        next
    }
    # Each @gpu kernel numbers its values from %1 again (Python's
    # MLIRGpuGenerator), independently of the host code: rename afresh.
    if (index(line, "gpu.func ") == 1) {
        split("", vals)
    }
    out = ""
    while (match(line, /%[0-9]+|\^bb[0-9]+/)) {
        tok = substr(line, RSTART, RLENGTH)
        out = out substr(line, 1, RSTART - 1)
        if (substr(tok, 1, 1) == "%") {
            if (!(tok in vals)) {
                nv++
                vals[tok] = "%v" nv
            }
            out = out vals[tok]
        } else {
            if (!(tok in labels)) {
                nl++
                labels[tok] = "^b" nl
            }
            out = out labels[tok]
        }
        line = substr(line, RSTART + RLENGTH)
    }
    print out line
}
