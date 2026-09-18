# Helix integration handoff

Helix language support should be submitted after `tree-sitter-flow` is published as a stable standalone repository.

The intended language registration is:

```toml
[[language]]
name = "flow"
scope = "source.flow"
file-types = ["flow"]
comment-token = "#"
language-servers = ["flow-lsp"]

[[grammar]]
name = "flow"
source = { git = "https://github.com/flooooooooooow/tree-sitter-flow", rev = "<pinned commit>" }
```

The exact schema and query layout must be checked against the current Helix repository at submission time. Copy the maintained highlight query from `third_party/integrations/tree-sitter-flow/queries/highlights.scm`, adapting capture names only where Helix requires it.

Do not submit this with a placeholder revision. Publish the grammar repository first, pin a real commit, run Helix's grammar fetch/build step, and then open the upstream PR.
