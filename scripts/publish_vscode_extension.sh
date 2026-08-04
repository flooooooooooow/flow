#!/usr/bin/env bash
# Package (and optionally publish) the FLOW VS Code / Cursor extension.
#
# Usage:
#   ./scripts/publish_vscode_extension.sh              # build .vsix
#   ./scripts/publish_vscode_extension.sh --publish    # vsce publish (needs VSCE_PAT)
#   ./scripts/publish_vscode_extension.sh --ovsx       # also Open VSX (needs OVSX_PAT)
#   ./scripts/publish_vscode_extension.sh --install    # install VSIX into Cursor + VS Code
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EXT="$ROOT/third_party/integrations/vscode/flow-language"
cd "$EXT"

PUBLISH=0
OVSX=0
INSTALL=0
for arg in "$@"; do
  case "$arg" in
    --publish) PUBLISH=1 ;;
    --ovsx) OVSX=1 ;;
    --install) INSTALL=1 ;;
    -h|--help)
      sed -n '2,12p' "$0"
      exit 0
      ;;
  esac
done

npm install --no-fund --no-audit
npm run compile

# Prefer local @vscode/vsce; fall back to npx / homebrew vsce
VSCE=(npx --no-install vsce)
if ! npx --no-install vsce --version >/dev/null 2>&1; then
  if command -v vsce >/dev/null 2>&1; then
    VSCE=(vsce)
  else
    VSCE=(npx --yes @vscode/vsce)
  fi
fi

echo "Packaging…"
"${VSCE[@]}" package --no-dependencies
VSIX="$(ls -t flow-language-*.vsix | head -1)"
echo "Built $EXT/$VSIX"

if [[ "$INSTALL" -eq 1 ]]; then
  if command -v cursor >/dev/null 2>&1; then
    cursor --install-extension "$EXT/$VSIX" --force
    echo "Installed into Cursor"
  else
    echo "warn: cursor CLI not found" >&2
  fi
  if command -v code >/dev/null 2>&1; then
    code --install-extension "$EXT/$VSIX" --force
    echo "Installed into VS Code"
  fi
fi

if [[ "$PUBLISH" -eq 1 ]]; then
  if [[ -z "${VSCE_PAT:-}" ]]; then
    echo "error: set VSCE_PAT (Azure DevOps PAT with Marketplace Manage)." >&2
    echo "See $EXT/PUBLISH.md" >&2
    exit 1
  fi
  echo "Publishing to VS Marketplace…"
  "${VSCE[@]}" publish --no-dependencies --pat "$VSCE_PAT"
fi

if [[ "$OVSX" -eq 1 ]]; then
  if [[ -z "${OVSX_PAT:-}" ]]; then
    echo "error: set OVSX_PAT for Open VSX." >&2
    exit 1
  fi
  echo "Publishing to Open VSX…"
  npx --yes ovsx publish "$VSIX" --pat "$OVSX_PAT"
fi

echo "Done."
