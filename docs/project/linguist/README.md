# github-linguist registration (#172)

GitHub does not yet classify `*.flow` as Flow. This directory holds the
upstream contribution draft:

| File | Purpose |
|------|---------|
| `languages.yml.snippet` | Entry to merge into linguist’s `languages.yml` |
| `samples/` | Representative `.flow` sources for the PR |
| VS Code grammar | `third_party/integrations/vscode/flow-language` (TextMate) |

Until upstream merges, `.gitattributes` keeps `*.flow linguist-detectable=true`.

Open the upstream PR against [github-linguist/linguist](https://github.com/github-linguist/linguist) using these files.
