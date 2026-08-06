#!/usr/bin/env bash
# Package a distributable flowc: the Stage-A driver binary, the bootstrap C it
# was built from, and a build script that needs nothing but a C compiler.
#
#   ./compiler/scripts/package_flowc.sh              # dist/flowc-<ver>-<os>-<arch>.tar.gz
#   FLOWC_VERSION=v0.9.0 ./compiler/scripts/package_flowc.sh
#
# The tarball is self-contained: `cc bootstrap/flowc_stage_a.c -o flowc`
# rebuilds the compiler on any platform with a C compiler, so the shipped
# binary is a convenience rather than the only way in.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

VERSION="${FLOWC_VERSION:-$(git describe --tags --always --dirty 2>/dev/null || echo dev)}"
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"
NAME="flowc-${VERSION}-${OS}-${ARCH}"
STAGE="compiler/build/pkg/${NAME}"
DIST=dist

rm -rf "$STAGE"
mkdir -p "$STAGE/bin" "$STAGE/bootstrap" "$STAGE/examples" "$DIST"

# The binary: prefer a self-hosted driver, else build from the bootstrap C.
pick_driver() {
    local cand
    for cand in \
        compiler/build/stage_a_driver_flow_self \
        compiler/build/stage_a_driver_flow_g2 \
        compiler/build/stage_a_driver_flow \
        compiler/build/flowc_bootstrap
    do
        if [[ -x "$cand" ]]; then
            printf '%s\n' "$cand"
            return 0
        fi
    done
    return 1
}
if ! pick_driver >/dev/null; then
    ./compiler/scripts/bootstrap_from_c.sh >/dev/null
fi
DRIVER="$(pick_driver)"
echo "packaging ${DRIVER} as ${NAME}"
cp "$DRIVER" "$STAGE/bin/flowc"
chmod +x "$STAGE/bin/flowc"

cp compiler/bootstrap/flowc_stage_a.c "$STAGE/bootstrap/"
cp LICENSE "$STAGE/" 2>/dev/null || true
cp compiler/fixtures/stage_a_sum.flow "$STAGE/examples/"
cp examples/basics/fibonacci.flow "$STAGE/examples/" 2>/dev/null || true

cat >"$STAGE/build.sh" <<'BUILD'
#!/usr/bin/env sh
# Rebuild flowc from source with nothing but a C compiler.
set -e
cd "$(dirname "$0")"
"${CC:-cc}" ${CFLAGS:--O2} -o bin/flowc bootstrap/flowc_stage_a.c
echo "built bin/flowc"
BUILD
chmod +x "$STAGE/build.sh"

cat >"$STAGE/README.md" <<README
# flowc ${VERSION} (${OS}/${ARCH})

Stage-A Flow compiler, written in Flow. It reads a \`.flow\` file and writes C.

    bin/flowc examples/stage_a_sum.flow sum.c
    cc -o sum sum.c
    ./sum ; echo \$?      # 45

Multi-file programs: set \`FLOWC_BUNDLE=1\` and \`FLOWC_DIR=<source dir>\` and
relative imports are resolved and emitted into one translation unit.

    FLOWC_BUNDLE=1 FLOWC_DIR=src bin/flowc src/main.flow main.c

## Rebuilding

\`bootstrap/flowc_stage_a.c\` is the compiler itself, emitted by flowc as a
single translation unit. No Python, no package manager, no network:

    ./build.sh

That file is checked into the Flow repository and CI fails if it is not
byte-for-byte what flowc emits from \`compiler/src\` today, so the binary here
and the source in the repository cannot drift apart.

## Scope

Stage-A is a subset: functions, structs, \`let\`/\`const\`, control flow,
\`match\` on integers, pointers, arrays, casts, relative imports, and C
externs. Programs outside that subset need the full Flow toolchain.
README

tar -czf "${DIST}/${NAME}.tar.gz" -C "compiler/build/pkg" "$NAME"
( cd "$DIST" && shasum -a 256 "${NAME}.tar.gz" > "${NAME}.tar.gz.sha256" )
# Record the archive this run produced, so callers do not glob over stale ones.
printf '%s\n' "${DIST}/${NAME}.tar.gz" > "${DIST}/flowc-latest.txt"
echo "wrote ${DIST}/${NAME}.tar.gz"
ls -la "${DIST}/${NAME}.tar.gz"
