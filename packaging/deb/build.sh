#!/usr/bin/env bash
# Reproducible, local-only Debian package from an exact committed Flow tree.
# Never installs, publishes, tags or modifies the source checkout.
set -euo pipefail

usage() {
    echo "usage: bash packaging/deb/build.sh [--rev COMMIT] [--out DIR]" >&2
}
rev="HEAD"
out="dist/deb"
while (($#)); do
    case "$1" in
        --rev|--out)
            if (($# < 2)); then usage; exit 2; fi
            if [[ "$1" == --rev ]]; then rev="$2"; else out="$2"; fi
            shift 2
            ;;
        -h|--help) usage; exit 0 ;;
        *) usage; exit 2 ;;
    esac
done
[[ "$(uname -s)" == Linux ]] || { echo "Debian packaging requires Linux" >&2; exit 2; }
for tool in git tar dpkg-deb sha256sum realpath touch find; do
    command -v "$tool" >/dev/null || { echo "missing $tool" >&2; exit 2; }
done
repo="$(cd "$(dirname "$0")/../.." && pwd)"
commit="$(git -C "$repo" rev-parse --verify "$rev^{commit}")" || exit 1
out="$(realpath -m "$out")"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/source" "$tmp/package/DEBIAN" "$tmp/package/usr/lib/flow" "$tmp/package/usr/bin" "$out"
git -C "$repo" archive --format=tar "$commit" | tar -xf - -C "$tmp/source"

version_file="$tmp/source/VERSION"
[[ -s "$version_file" ]] || { echo "commit lacks VERSION: $commit" >&2; exit 1; }
IFS= read -r version < "$version_file" || true
[[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || {
    echo "invalid Debian upstream version: $version" >&2; exit 1
}
for entry in flow flow-lsp compiler lib runtime tools scripts registry flow.toml VERSION; do
    [[ -e "$tmp/source/$entry" ]] || { echo "missing source entry: $entry" >&2; exit 1; }
    cp -a "$tmp/source/$entry" "$tmp/package/usr/lib/flow/"
done
for optional in examples src pyproject.toml requirements.txt; do
    if [[ -e "$tmp/source/$optional" ]]; then
        cp -a "$tmp/source/$optional" "$tmp/package/usr/lib/flow/"
    fi
done
chmod 0755 "$tmp/package/usr/lib/flow/flow"
chmod 0755 "$tmp/package/usr/lib/flow/flow-lsp"
ln -s ../lib/flow/flow "$tmp/package/usr/bin/flow"
ln -s ../lib/flow/flow-lsp "$tmp/package/usr/bin/flow-lsp"
cat > "$tmp/package/DEBIAN/control" <<EOF
Package: flow
Version: $version-1
Section: devel
Priority: optional
Architecture: all
Maintainer: Flow Language Team <team@flow-lang.org>
Depends: gcc | clang, libc6-dev
Homepage: https://github.com/flooooooooooow/flow
Description: Flow programming language compiler and runtime
 Flow is a statically typed compiled language with algebraic effects.
EOF

if [[ -z "${SOURCE_DATE_EPOCH:-}" ]]; then
    SOURCE_DATE_EPOCH="$(git -C "$repo" show -s --format=%ct "$commit")"
fi
[[ "$SOURCE_DATE_EPOCH" =~ ^[0-9]+$ ]] || { echo "invalid SOURCE_DATE_EPOCH" >&2; exit 2; }
export SOURCE_DATE_EPOCH TZ=UTC LC_ALL=C
find "$tmp/package" -exec touch -h -d "@$SOURCE_DATE_EPOCH" {} +
filename="flow_$version-1_all.deb"
dpkg-deb --root-owner-group --build -Zgzip "$tmp/package" "$out/$filename"
digest="$(sha256sum "$out/$filename" | cut -d" " -f1)"
printf '%s  %s\n' "$digest" "$filename" > "$out/SHA256SUMS.deb.txt"
printf 'source-commit: %s\nsource-version: %s\npublished: false\n' "$commit" "$version" > "$out/deb-provenance.txt"
echo "Wrote $out/$filename"
echo "Wrote $out/SHA256SUMS.deb.txt (local package, not a published release)"
