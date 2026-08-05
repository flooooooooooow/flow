# FLOW Language for VS Code & Cursor

Syntax, snippets, formatter, debug, test explorer, tasks, and LSP for
[FLOW](https://github.com/flooooooooooow/flow).

## Features (0.3)

| Area | What you get |
|------|----------------|
| Language | `.flow` grammar, icons, folding, bracket colorization |
| LSP | hover, go-to-def, refs, rename, completions, **format**, highlights, diagnostics |
| Edit | rich snippets; format on save (default) |
| Run | **Run** / **Compile** title buttons; `Cmd+Shift+R` / `B` |
| Debug | **Debug Current File** → build `-g` binary → CodeLLDB / cppdbg / terminal `lldb` |
| Test | Testing view: `tests/**/*.flow`, `tests/unit`, CLI suites |
| Themes | install **Flow Pack** for Flow Dark / Dim + CodeLLDB |

## Install

```bash
cd third_party/integrations/vscode
./install-local.sh
```

Reload the window. Optional: install CodeLLDB when prompted, or:

```bash
cursor --install-extension vadimcn.vscode-lldb
```

### Marketplace

```bash
export VSCE_PAT=…   # Azure DevOps PAT
./publish.sh
```

## Commands

| Command | Shortcut |
|---------|----------|
| FLOW: Run Current File | `Cmd+Shift+R` |
| FLOW: Compile Current File | `Cmd+Shift+B` |
| FLOW: Debug Current File | `Cmd+Shift+D` |
| FLOW: Format Current File | Format Document |
| FLOW: Restart Language Server | — |
| FLOW: Refresh Test Explorer | — |

## Settings

| Setting | Purpose |
|---------|---------|
| `flow.repoPath` | Flow checkout (auto-detected here) |
| `flow.pythonPath` | Python for LSP / debug transpile |
| `flow.lspPath` | Optional dedicated LSP binary |

## Related

- `flow-themes` — Flow Dark / Flow Dim
- `flow-pack` — language + themes + CodeLLDB
