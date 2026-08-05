#!/usr/bin/env bash
# Build and install Flow VS Code / Cursor extensions locally.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

need() { command -v "$1" >/dev/null 2>&1 || { echo "missing: $1" >&2; exit 1; }; }
need npm
need npx

# Stale .vsix files from earlier versions would make the `ls | tail -1` picks
# below sort lexically rather than by version (0.10.0 < 0.3.0).
echo "==> flow-language"
cd "$ROOT/flow-language"
rm -f ./*.vsix
npm install --silent
npm run compile
npx --yes @vscode/vsce package --no-dependencies
LANG_VSIX=$(ls -1 flow-language-*.vsix | tail -1)

echo "==> flow-themes"
cd "$ROOT/flow-themes"
rm -f ./*.vsix
npx --yes @vscode/vsce package --no-dependencies
THEME_VSIX=$(ls -1 flow-themes-*.vsix | tail -1)

echo "==> flow-pack"
cd "$ROOT/flow-pack"
rm -f ./*.vsix
npx --yes @vscode/vsce package --no-dependencies
PACK_VSIX=$(ls -1 flow-pack-*.vsix | tail -1)

install_all() {
  local cli=$1
  if ! command -v "$cli" >/dev/null 2>&1; then
    echo "skip $cli (not on PATH)"
    return
  fi
  echo "==> install via $cli"
  "$cli" --install-extension "$ROOT/flow-language/$LANG_VSIX" --force
  "$cli" --install-extension "$ROOT/flow-themes/$THEME_VSIX" --force
  "$cli" --install-extension "$ROOT/flow-pack/$PACK_VSIX" --force
}

if [[ -z "${FLOW_VSCE_PACKAGE_ONLY:-}" ]]; then
  install_all cursor
  install_all code
fi

echo "Done."
echo "  language: $LANG_VSIX"
echo "  themes:   $THEME_VSIX"
echo "  pack:     $PACK_VSIX"
if [[ -z "${FLOW_VSCE_PACKAGE_ONLY:-}" ]]; then
  echo "Reload the window (Cmd+Shift+P → Developer: Reload Window) to activate."
  echo "Optional: Cmd+K Cmd+T → pick 'Flow Dark'."
fi
