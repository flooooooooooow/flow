#!/usr/bin/env bash
# Smoke-test a Debian package without root or a system-wide installation.
set -euo pipefail
usage() {
    echo "usage: bash packaging/linux/qualify-deb.sh --package flow_VERSION_all.deb --sha256 DIGEST [--out DIR]" >&2
}
deb=""
digest=""
out="build/linux-deb-qualification"
while (($#)); do
    case "$1" in
        --package|--sha256|--out)
            if (($# < 2)); then usage; exit 2; fi
            case "$1" in
                --package) deb="$2" ;;
                --sha256) digest="$2" ;;
                --out) out="$2" ;;
            esac
            shift 2
            ;;
        -h|--help) usage; exit 0 ;;
        *) usage; exit 2 ;;
    esac
done
[[ "$(uname -s)" == Linux && -f "$deb" && "$digest" =~ ^[0-9a-f]{64}$ ]] || { usage; exit 2; }
for tool in dpkg-deb sha256sum mktemp cc awk realpath; do
    command -v "$tool" >/dev/null || { echo "missing $tool" >&2; exit 2; }
done
deb="$(realpath "$deb")"
out="$(realpath -m "$out")"
actual="$(sha256sum "$deb" | awk '{print $1}')"
[[ "$actual" == "$digest" ]] || { echo "Debian artifact SHA-256 mismatch" >&2; exit 1; }

[[ "$(dpkg-deb --field "$deb" Package)" == flow ]] || { echo "not a Flow package" >&2; exit 1; }
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
dpkg-deb --extract "$deb" "$tmp"
root="$tmp/usr/lib/flow"
[[ -f "$root/flow" && -f "$root/VERSION" && -d "$root/compiler" && -d "$root/tools" ]] || {
    echo "incomplete Debian payload" >&2; exit 1
}
[[ -L "$tmp/usr/bin/flow" && "$(readlink "$tmp/usr/bin/flow")" == ../lib/flow/flow ]] || {
    echo "broken Debian command symlink" >&2; exit 1
}
(
    cd "$root"
    ./flow version
    [[ -f examples/basics/fibonacci.flow ]] || { echo "missing smoke-test fixture" >&2; exit 1; }
    FLOW_HOST=flowc ./flow compile examples/basics/fibonacci.flow
    [[ -x build/fibonacci ]] || { echo "no compiled binary" >&2; exit 1; }
)
set +e
"$root/build/fibonacci"
rc=$?
set -e
[[ "$rc" -eq 55 ]] || { echo "Debian fibonacci returned $rc; expected 55" >&2; exit 1; }
mkdir -p "$out"
{
    printf 'status: PASS\npublished: false\n'
    printf 'package: %s\nsha256: %s\n' "$(basename "$deb")" "$actual"
    printf 'version: %s\n' "$(dpkg-deb --field "$deb" Version)"
    printf 'platform: %s\n' "$(uname -sm)"
    printf 'test: extract, version, compile and execute fibonacci (exit 55)\n'
} > "$out/qualification-deb.txt"
echo "PASS: Linux Debian package qualification ($actual)"
echo "Record: $out/qualification-deb.txt"
