#!/usr/bin/env bash
# Publish the Flow extensions to Open VSX (https://open-vsx.org).
#
# Open VSX is the registry Cursor, VSCodium and Gitpod install from. It needs
# no Microsoft or Azure account: sign in with GitHub, sign the Eclipse
# Foundation Publisher Agreement, then mint an access token.
#
#   1. https://open-vsx.org  -> Log in with GitHub
#   2. Profile -> Publisher Agreement -> sign it (one time, required)
#   3. Profile -> Access Tokens -> Generate New Token
#   4. export OVSX_PAT='...'
#   5. ./publish.sh
#
# Pass --dry-run to package and validate without uploading.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

DRY_RUN=0
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

EXTENSIONS=(flow-language flow-themes flow-pack)

publisher_of() { node -p "require('./$1/package.json').publisher"; }
version_of() { node -p "require('./$1/package.json').version"; }

NAMESPACE="$(publisher_of flow-language)"
for ext in "${EXTENSIONS[@]}"; do
  if [[ "$(publisher_of "$ext")" != "$NAMESPACE" ]]; then
    echo "publisher mismatch: $ext is '$(publisher_of "$ext")', expected '$NAMESPACE'" >&2
    echo "All three must share one namespace or flow-pack's references break." >&2
    exit 1
  fi
done

if [[ -z "${OVSX_PAT:-}" && $DRY_RUN -eq 0 ]]; then
  cat >&2 <<EOF
OVSX_PAT is not set. See the header of this script for how to get one,
or run './publish.sh --dry-run' to just build and validate the packages.
EOF
  exit 1
fi

echo "==> packaging (namespace: $NAMESPACE)"
FLOW_VSCE_PACKAGE_ONLY=1 ./install-local.sh

if [[ $DRY_RUN -eq 1 ]]; then
  echo
  echo "Dry run. Built:"
  for ext in "${EXTENSIONS[@]}"; do
    echo "  $ext/$(ls -1 "$ext"/*.vsix | tail -1 | xargs basename)"
  done
  exit 0
fi

# Idempotent: a namespace that already exists is not an error for us.
echo "==> claiming namespace '$NAMESPACE'"
if npx --yes ovsx create-namespace "$NAMESPACE" -p "$OVSX_PAT" 2>&1 | tee /tmp/ovsx-ns.log; then
  :
elif grep -qi "already owned\|already exists" /tmp/ovsx-ns.log; then
  echo "    (already yours)"
else
  echo "could not create namespace '$NAMESPACE'" >&2
  exit 1
fi

failed=()
for ext in "${EXTENSIONS[@]}"; do
  vsix="$ROOT/$ext/$(ls -1 "$ROOT/$ext"/*.vsix | tail -1 | xargs basename)"
  echo "==> publishing $ext $(version_of "$ext")"
  if ! npx --yes ovsx publish "$vsix" -p "$OVSX_PAT"; then
    failed+=("$ext")
  fi
done

if (( ${#failed[@]} )); then
  echo >&2
  echo "Failed: ${failed[*]}" >&2
  echo "A version that already exists cannot be overwritten; bump it in package.json." >&2
  exit 1
fi

echo
echo "Published. Verify at https://open-vsx.org/namespace/$NAMESPACE"
for ext in "${EXTENSIONS[@]}"; do
  echo "  https://open-vsx.org/extension/$NAMESPACE/$ext"
done
