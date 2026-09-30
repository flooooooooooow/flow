#!/usr/bin/env bash
# Keep every version string in the tree in sync with VERSION.
#
# The logic is the Flow program in scripts/tools/sync_version. Flow cannot
# make network requests, so for --sha256-from-release this shim downloads
# the release tarball, hashes it, and hands the digest over.
#
# Usage:
#   ./scripts/sync_version.sh              # rewrite mirrors from canonical
#   ./scripts/sync_version.sh --check      # exit 1 if any mirror drifted
#   ./scripts/sync_version.sh --set 0.12.0 # bump canonical, then rewrite
#   ./scripts/sync_version.sh --set v0.12.0 --release-date 2026-09-01
#   ./scripts/sync_version.sh --homebrew --sha256 <digest>
#   ./scripts/sync_version.sh --homebrew --sha256-from-release

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BIN="$(scripts/tools/build_tool.sh sync_version)"

want_fetch=0
have_sha=0
set_version=""
prev=""
for arg in "$@"; do
  case "$arg" in
    --sha256-from-release) want_fetch=1 ;;
    --sha256|--sha256=*) have_sha=1 ;;
    --set=*) set_version="${arg#--set=}" ;;
  esac
  if [[ "$prev" == "--set" ]]; then
    set_version="$arg"
  fi
  prev="$arg"
done

if [[ "$want_fetch" -eq 1 && "$have_sha" -eq 0 ]]; then
  if [[ -n "$set_version" ]]; then
    version="$set_version"
    while [[ "$version" == v* ]]; do version="${version#v}"; done
  else
    version="$(head -n 1 VERSION)"
  fi
  url="https://github.com/flooooooooooow/flow/releases/download/v${version}/flow-v${version}.tar.gz"
  tarball="$(mktemp)"
  trap 'rm -f "$tarball"' EXIT
  if ! curl -fsSL -o "$tarball" "$url"; then
    echo "error: could not download $url" >&2
    exit 1
  fi
  if command -v sha256sum >/dev/null 2>&1; then
    digest="$(sha256sum "$tarball" | cut -d' ' -f1)"
  else
    digest="$(shasum -a 256 "$tarball" | cut -d' ' -f1)"
  fi
  "$BIN" "$@" --prefetched-sha256 "$digest"
  exit $?
fi

exec "$BIN" "$@"
