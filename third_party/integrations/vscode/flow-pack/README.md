# Flow Pack

Installs everything useful for Flow development in VS Code / Cursor:

- **FLOW Language** — syntax, snippets, run/compile, LSP
- **Flow Themes** — Flow Dark + Flow Dim

```bash
# after packaging siblings:
cursor --install-extension ../flow-language/flow-language-*.vsix --force
cursor --install-extension ../flow-themes/flow-themes-*.vsix --force
cursor --install-extension ./flow-pack-*.vsix --force
```
