#!/usr/bin/env bash
# Sync packaging/homebrew/Formula → flooooooooooow/homebrew-flow (Homebrew tap).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC_FORMULA="$ROOT/packaging/homebrew/Formula/flow.rb"
TAP_OWNER="${FLOW_TAP_OWNER:-flooooooooooow}"
TAP_REPO="${FLOW_TAP_REPO:-homebrew-flow}"
TAP_FULL="$TAP_OWNER/$TAP_REPO"

if [[ ! -f "$SRC_FORMULA" ]]; then
  echo "missing formula: $SRC_FORMULA" >&2
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI required" >&2
  exit 1
fi

# Create the public tap repo if it doesn't exist.
if ! gh repo view "$TAP_FULL" >/dev/null 2>&1; then
  echo "Creating GitHub repo $TAP_FULL ..."
  gh repo create "$TAP_FULL" --public \
    --description "Homebrew tap for the Flow programming language" \
    --homepage "https://github.com/flooooooooooow/flow"
fi

TMP="$(mktemp -d)"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

echo "Cloning $TAP_FULL ..."
if gh repo clone "$TAP_FULL" "$TMP/tap" 2>/dev/null; then
  :
else
  # Empty brand-new repo: init locally and set remote.
  mkdir -p "$TMP/tap"
  git -C "$TMP/tap" init -b main
  git -C "$TMP/tap" remote add origin "https://github.com/$TAP_FULL.git"
fi

mkdir -p "$TMP/tap/Formula"
cp "$SRC_FORMULA" "$TMP/tap/Formula/flow.rb"

cat > "$TMP/tap/README.md" <<EOF
# homebrew-flow

Homebrew tap for [Flow](https://github.com/flooooooooooow/flow).

\`\`\`bash
brew tap flooooooooooow/flow
brew install flow
flow help
\`\`\`

Formula source of truth lives in the main repo at
\`packaging/homebrew/Formula/flow.rb\`.
EOF

git -C "$TMP/tap" add Formula/flow.rb README.md
if git -C "$TMP/tap" diff --cached --quiet; then
  echo "Tap already up to date."
  exit 0
fi

git -C "$TMP/tap" -c user.email="flow-bot@users.noreply.github.com" \
  -c user.name="Flow Homebrew sync" \
  commit -m "Update flow formula from flooooooooooow/flow"

git -C "$TMP/tap" push -u origin HEAD:main
echo "Pushed tap: https://github.com/$TAP_FULL"
echo "Install with: brew tap flooooooooooow/flow && brew install flow"
