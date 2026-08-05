# Publishing the FLOW VS Code / Cursor extension

Cursor, VSCodium, Gitpod and friends install extensions from
[**Open VSX**](https://open-vsx.org), so that is our primary registry. It needs
no Microsoft or Azure account. The Visual Studio Marketplace is documented at
the end as an optional extra.

Publisher / Open VSX namespace: **`quilio`** (matches `"publisher"` in
`package.json`). The GitHub org for the Flow repo remains
`flooooooooooow` — that is unrelated.

The recommended path is the GitHub Actions workflow — no token ever touches your
machine. Local publishing is documented too, for one-off releases.

---

## Publish via GitHub Actions (recommended)

The workflow at [`.github/workflows/publish-open-vsx.yml`](../../../../.github/workflows/publish-open-vsx.yml)
builds, packages and publishes `flow-language` to Open VSX.

### One-time setup

1. Sign in at https://open-vsx.org with GitHub.
2. **Sign the Eclipse Foundation Publisher Agreement** (Profile → *Publisher
   Agreement*). Publishing is rejected until this is signed, with an unhelpful
   error — this is the step everyone gets stuck on.
3. Create a token: Profile → *Access Tokens* → **Generate New Token**.
4. Add it to the repository as an Actions secret named `OVSX_PAT`:

   ```bash
   gh secret set OVSX_PAT --body '…your token…'
   gh secret list            # confirm OVSX_PAT is listed
   ```

   (Or via the web UI: repo → Settings → Secrets and variables → Actions → *New
   repository secret*.)

### Run it

The workflow triggers two ways:

- **Manually** — Actions tab → *Publish VS Code extension to Open VSX* → **Run
  workflow**.
- **On a tag** — push a tag matching `vscode-v*`:

  ```bash
  git tag vscode-v0.1.3
  git push origin vscode-v0.1.3
  ```

It compiles the extension, uploads the `.vsix` as a build artifact, claims the
`quilio` namespace on first run, then publishes. If `OVSX_PAT` is
missing the run fails fast with a clear message.

---

## Publish locally (one-off)

### One-time setup

Steps 1–3 above, then export the token instead of storing it as a secret:

```bash
export OVSX_PAT='…your token…'   # do not commit
```

### Package & publish

From the repo root:

```bash
./scripts/publish_vscode_extension.sh          # package only (.vsix)
./scripts/publish_vscode_extension.sh --ovsx   # package + publish to Open VSX
```

Or manually:

```bash
cd third_party/integrations/vscode/flow-language
npm ci
npm run compile
npx --yes @vscode/vsce package --no-dependencies
npx --yes ovsx create-namespace quilio --pat "$OVSX_PAT"  # first time only
npx --yes ovsx publish flow-language-*.vsix --pat "$OVSX_PAT"
```

---

## Versioning

Open VSX (like the Marketplace) refuses to overwrite a version that already
exists, so bump `"version"` in `package.json` (semver) before every release. The
publisher id in `package.json` (`"publisher": "quilio"`) must match the
namespace you claimed, or the upload is rejected.

## After publish

```bash
cursor --install-extension quilio.flow-language
code   --install-extension quilio.flow-language   # if VS Code is used
```

Verify at https://open-vsx.org/extension/quilio/flow-language.

---

## Optional: Visual Studio Marketplace

Only relevant if you also want plain VS Code users to find the extension in the
built-in Marketplace. This is the one path that requires a Microsoft account.

Create a Marketplace publisher named **`quilio`** (must match `package.json`) at
https://marketplace.visualstudio.com/manage.

**Do not build a workflow around `VSCE_PAT`.** Global Azure DevOps Personal
Access Tokens are retired on **1 December 2026**. Use trusted publishing
instead — GitHub Actions OIDC, no stored secret:

```yaml
permissions:
  contents: read
  id-token: write
steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-node@v4
    with: { node-version: 22 }
  - run: npm ci
  - run: npx @vscode/vsce publish --oidc
```

You configure a trusted-publishing policy for the repo + workflow on the
Marketplace side; see the
[VS Code publishing docs](https://code.visualstudio.com/api/working-with-extensions/publishing-extension).
