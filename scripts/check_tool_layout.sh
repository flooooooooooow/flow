#!/usr/bin/env bash
# Reject mirrored long-lived tool directories under tools/ and scripts/tools/.
#
# A tool lives in one place. scripts/ keeps thin automation around it.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

child_dirs() {
    [[ -d "$1" ]] || return 0
    find "$1" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort
}

mirrors="$(comm -12 <(child_dirs tools) <(child_dirs scripts/tools))"
if [[ -z "$mirrors" ]]; then
    echo "tool-layout: no mirrored tool directories"
    exit 0
fi

while IFS= read -r name; do
    echo "tool-layout: '$name' exists under both tools/ and scripts/tools/;" \
        "choose one canonical implementation and keep scripts/ as thin automation" >&2
done <<< "$mirrors"
exit 1
