#!/usr/bin/env bash
# Process shim for the Flow package manager (compiler/src/pkg.flow).
#
# Flow programs call system()/popen() with one command line; this script is
# that command line. It only runs the external programs the package manager
# needs. Every decision (what to fetch, where, which ref, what to do on
# failure) is made in pkg.flow.
#
#   copytree SRC DEST        replace DEST with a copy of SRC, following
#                            symlinks and leaving out .git, build,
#                            flow_packages, __pycache__ and *.pyc
#   copyfile SRC DEST        copy one file with its mode
#   rmtree PATH              remove PATH recursively
#   git ERRFILE ARGS...      run git ARGS, stdout discarded, stderr to ERRFILE;
#                            exit 200 when git is not installed
#   git-head DIR             print the HEAD commit of DIR
#   fetch-url URL DEST       download URL to DEST with curl (15 s timeout)
set -u

cmd="${1:-}"
shift || true

case "$cmd" in
    copytree)
        src="$1"
        dest="$2"
        rm -rf "$dest"
        mkdir -p "$dest"
        (cd "$src" && tar -chf - \
            --exclude .git --exclude build --exclude flow_packages \
            --exclude __pycache__ --exclude '*.pyc' .) \
            | (cd "$dest" && tar -xpf -)
        ;;
    copyfile)
        cp -p "$1" "$2" && touch "$2"
        ;;
    rmtree)
        rm -rf "$1"
        ;;
    git)
        errfile="$1"
        shift
        if ! command -v git >/dev/null 2>&1; then
            exit 200
        fi
        git "$@" >/dev/null 2>"$errfile"
        ;;
    git-head)
        git -C "$1" rev-parse HEAD 2>/dev/null
        ;;
    fetch-url)
        if ! command -v curl >/dev/null 2>&1; then
            exit 200
        fi
        curl -fsSL --max-time 15 -o "$2" "$1"
        ;;
    *)
        echo "pkg_fetch.sh: unknown command: $cmd" >&2
        exit 2
        ;;
esac
