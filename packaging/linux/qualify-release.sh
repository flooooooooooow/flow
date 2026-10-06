#!/usr/bin/env bash
# Verify an exact published Flow source archive on Linux, locally.
set -euo pipefail

usage() {
    echo "usage: $0 --archive flow-vX.Y.Z.tar.gz --sha256 PUBLISHED_DIGEST [--out DIR]" >&2
}

archive=""
expected=""
out="build/linux-qualification"
while (($#)); do
    case "$1" in
        --archive|--sha256|--out)
            key="$1"
            if (($# < 2)); then usage; exit 2; fi
            case "$key" in
                --archive) archive="$2" ;;
                --sha256) expected="$2" ;;
                --out) out="$2" ;;
            esac
            shift 2
            ;;
        -h|--help) usage; exit 0 ;;
        *) usage; exit 2 ;;
    esac
done

[[ "$(uname -s)" == Linux ]] || { echo "Linux host required" >&2; exit 2; }
[[ -f "$archive" && "$expected" =~ ^[0-9a-f]{64}$ ]] || { usage; exit 2; }
for tool in sha256sum tar mktemp find cc realpath awk; do
    command -v "$tool" >/dev/null || { echo "missing $tool" >&2; exit 2; }
done
archive="$(realpath "$archive")"
out="$(realpath -m "$out")"
actual="$(sha256sum "$archive" | awk '{print $1}')"
[[ "$actual" == "$expected" ]] || {
    echo "SHA-256 mismatch: actual $actual, expected $expected" >&2
    exit 1
}

# Reject absolute paths, traversal and archives spanning multiple source roots.
prefix=""
while IFS= read -r entry; do
    [[ -n "$entry" && "$entry" != /* && "$entry" != *'/../'* && "$entry" != ../* && "$entry" != *'/..' ]] || {
        echo "unsafe archive member: $entry" >&2; exit 1
    }
    head="$(printf '%s\n' "$entry" | cut -d/ -f1)"
    [[ "$head" =~ ^flow-[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?$ ]] || {
        echo "unexpected archive prefix: $head" >&2; exit 1
    }
    if [[ -z "$prefix" ]]; then prefix="$head"; fi
    [[ "$head" == "$prefix" ]] || { echo "multiple archive roots" >&2; exit 1; }
done < <(tar -tzf "$archive")
[[ -n "$prefix" ]] || { echo "empty source archive" >&2; exit 1; }

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
tar -xzf "$archive" -C "$tmp"
root="$tmp/$prefix"
[[ -f "$root/flow" && -d "$root/compiler" && -d "$root/lib" && -d "$root/runtime" ]] || {
    echo "incomplete Flow source archive" >&2; exit 1
}
[[ -f "$root/examples/basics/fibonacci.flow" ]] || {
    echo "missing release smoke-test program" >&2; exit 1
}
chmod +x "$root/flow"
(
    cd "$root"
    ./flow version
    FLOW_HOST=flowc ./flow compile examples/basics/fibonacci.flow
    [[ -x build/fibonacci ]] || { echo "compiler did not emit build/fibonacci" >&2; exit 1; }
)
set +e
"$root/build/fibonacci"
result=$?
set -e
[[ "$result" -eq 55 ]] || {
    echo "packaged fibonacci exit code $result; expected 55" >&2; exit 1
}

mkdir -p "$out"
{
    printf 'status: PASS\n'
    printf 'published: false\n'
    printf 'archive: %s\n' "$(basename "$archive")"
    printf 'sha256: %s\n' "$actual"
    printf 'source-root: %s\n' "$prefix"
    printf 'platform: %s\n' "$(uname -sm)"
    printf 'cc: %s\n' "$(cc --version | head -n 1)"
    printf 'test: flow version; flow compile; fibonacci exit=55\n'
} > "$out/qualification-linux.txt"
echo "PASS: Linux archive qualification ($actual)"
echo "Record: $out/qualification-linux.txt"
