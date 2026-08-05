# Flow install

```bash
./flow install
```

Symlinks the repo's `flow` (and `flow-lsp`) into `~/.local/bin` so you can run
`flow` from anywhere.

Override the bin dir:

```bash
FLOW_INSTALL_BIN=/usr/local/bin ./flow install   # may need write permission
```

Optional extras:

```bash
FLOW_INSTALL_DEPS=1 ./flow install   # also run scripts/tools/install/setup.flow (clang/SDL2/…)
FLOW_INSTALL_PKGS=1 ./flow install   # also install cwd flow.toml packages
```
