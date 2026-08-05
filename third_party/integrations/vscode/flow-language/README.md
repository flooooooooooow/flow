# FLOW Language for VS Code & Cursor

Syntax highlighting and optional LSP for [FLOW](https://github.com/flooooooooooow/flow) — a language with algebraic effects, autodiff, and a portable C backend.

Works in **VS Code** and **Cursor** (same VSIX).

## Features

- `.flow` language mode + TextMate grammar
- LSP client → `python3 -m flow.lsp_server` (go-to-def, hover, completions, diagnostics when the server is available)
- Command: **FLOW: Restart Language Server**

## Install

### From the marketplace (once published)

Search **“FLOW Language”** by `quilio`, or:

```bash
cursor --install-extension quilio.flow-language
code --install-extension quilio.flow-language
```

### From this repo (local VSIX)

```bash
cd third_party/integrations/vscode/flow-language
npm install
npm run compile
npx vsce package --no-dependencies
cursor --install-extension ./flow-language-*.vsix --force
code --install-extension ./flow-language-*.vsix --force
```

## LSP setup

The extension looks for the Flow checkout automatically when you open this repo. Otherwise set:

| Setting | Purpose |
|---------|---------|
| `flow.repoPath` | Absolute path to the Flow git checkout (`…/flow`) |
| `flow.pythonPath` | Python that can import `flow` (default `python3`) |
| `flow.lspPath` | Optional dedicated LSP binary (skips Python module) |

Quick local check:

```bash
cd /path/to/flow
PYTHONPATH=src python3 -m flow.lsp_server
# should sit waiting on stdio — Ctrl-C to stop
```

Syntax highlighting works even if the LSP fails to start.

## Publish (maintainers)

See [PUBLISH.md](./PUBLISH.md).
