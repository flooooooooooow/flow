# Publishing the FLOW VS Code / Cursor extension

Cursor installs the same VSIX format as VS Code. Publish to:

1. **Visual Studio Marketplace** (primary — `vsce`)
2. **Open VSX** (optional — some Cursor / VSCodium users; `ovsx`)

## One-time setup

1. Create a publisher id matching `package.json` → `"publisher": "flooooooooooow"`
   - https://marketplace.visualstudio.com/manage  
   - Sign in with the GitHub / Microsoft account that owns `flooooooooooow`
2. Create an Azure DevOps Personal Access Token with **Marketplace → Manage** scope:
   - https://dev.azure.com → User settings → Personal access tokens  
3. Export it (do not commit):

```bash
export VSCE_PAT='…your token…'
# optional Open VSX: https://open-vsx.org → Access Token
export OVSX_PAT='…'
```

## Package & publish

From repo root:

```bash
./scripts/publish_vscode_extension.sh          # package only
./scripts/publish_vscode_extension.sh --publish  # vsce publish (needs VSCE_PAT)
./scripts/publish_vscode_extension.sh --ovsx     # also ovsx publish
```

Or manually:

```bash
cd third_party/integrations/vscode/flow-language
npm ci
npm run compile
npx vsce package --no-dependencies
npx vsce publish --no-dependencies   # uses VSCE_PAT
npx ovsx publish flow-language-*.vsix # uses OVSX_PAT
```

## After publish

```bash
cursor --install-extension flooooooooooow.flow-language
code --install-extension flooooooooooow.flow-language
```

Bump `"version"` in `package.json` for each release (semver).
