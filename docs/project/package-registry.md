# Package Registry

**Status:** Implemented (local index + git/path; hosted API deferred)  
**Date:** 2026-08-04  
**Related:** [modules](../language/modules.md) · [third-party](../third-party/README.md)

Flow ships a name-based **package** manager: a versioned index, search/info/publish,
plus path and git dependencies.

---

## Quick start

```bash
./flow init my_app
cd my_app

# Name resolve from the bundled index
./flow add hello_lib
# or pin / caret:
./flow add hello_lib@0.1.0
./flow add hello_lib@^0.1

./flow install          # refresh flow_packages/ + flow.lock
./flow search verify
./flow info hello_lib
```

```toml
# flow.toml
[dependencies]
hello_lib = "0.1.0"                                    # registry
mathkit   = { path = "../mathkit" }                    # local
audio_dsp = { git = "https://github.com/org/repo", tag = "v0.3" }
ringbuf   = { git = "https://github.com/org/mono", tag = "v1", subdir = "packages/ringbuf" }
```

Git installs pin the resolved commit SHA in `flow.lock` under `resolved.rev`.
URL shorthand works from the CLI:

```bash
./flow add https://github.com/org/mylib.git --tag v0.1
./flow add --git https://github.com/org/mono --name ringbuf --subdir packages/ringbuf --tag v1
```

```flow ignore="hello_lib is the example package the page walks through"
import hello_lib.lib { greet, add }
```

Installed packages land in `flow_packages/<name>/` and are pinned in `flow.lock`.

---

## Commands

| Command | What it does |
|---------|----------------|
| `./flow init [name]` | Create `flow.toml` + `src/main.flow` |
| `./flow add foo` / `foo@^1.0` | Add a registry package |
| `./flow add https://…/foo.git [--tag v0.1]` | Git URL shorthand (name inferred) |
| `./flow add --git URL [--name foo] [--tag v0.1] [--subdir path]` | Git dependency |
| `./flow add --path ../foo --name foo` | Add a path dependency |
| `./flow search [query]` | Search the package index |
| `./flow info <package>` | Show versions / source |
| `./flow publish` | Register this package in the local index |
| `./flow build` | Build the project |

Also: `./flow pkg <subcommand>` → `python -m flow.package …`.

`./flow install` installs **project dependencies** when `flow.toml` exists.
Use `./flow setup` (or `./flow install --tools`) for LLVM/compiler tooling.

---

## Index format

Bundled index: [`registry/index.json`](../../registry/index.json)

```json
{
  "version": 1,
  "name": "flow-packages",
  "packages": {
    "hello_lib": {
      "description": "…",
      "license": "MIT",
      "versions": [
        { "version": "0.1.0", "yanked": false, "path": "registry/packages/hello_lib" }
      ]
    }
  }
}
```

A version entry is either:

- **`path`** — repo-relative (or absolute) directory with its own `flow.toml`
- **`git`** (+ optional `tag` / `rev` / `branch`) — cloned into `flow_packages/`

### Overrides

| Env | Meaning |
|-----|---------|
| `FLOW_REGISTRY_PATH` | Local `index.json` |
| `FLOW_REGISTRY_URL` | Remote JSON URL (cached under `~/.flow/cache/`) |
| `FLOW_HOME` | Override `~/.flow` |

Version requirements: `*`, exact (`0.1.0`), `^1.2.3`, `>=0.1.0`.

---

## Publishing

```bash
cd my_package        # has flow.toml with name + version
./flow publish       # if inside the Flow monorepo → path entry
./flow publish --git https://github.com/you/my_package --tag v0.1.0
./flow publish --dry-run
```

This updates `registry/index.json` (or `FLOW_REGISTRY_PATH`). There is **no**
account/API server yet — sharing means committing the index change or opening a
PR against the Flow repo (or hosting your own index JSON behind
`FLOW_REGISTRY_URL`).

---

## Bundled packages

| Package | Source |
|---------|--------|
| `hello_lib` | `registry/packages/hello_lib` (sample) |
| `mathkit` | `registry/packages/mathkit` |
| `ringbuf` | `registry/packages/ringbuf` |
| `json` / `toml` / `serde` / `strings` / `cli` / `log` / `testing` / `collectionsx` | Pure Flow app libs under `registry/packages/` |
| `http` / `sqlite` / `sqlkit` / `compress` / `dns` / `image` / `ffi` | Native wraps (`[native]` + system libs where needed) |
| `flow-verify` | `lib/verify` |

Demos: `examples/ecosystem/*_demo/` (and `http_get`). Native deps: `./flow install` then `./flow run-native`.

Human discovery still lives under [docs/third-party](../third-party/README.md).

---

## Out of scope (still)

- Hosted publish API / accounts / yank server  
- Full semver solver with dependency graphs (lock pins direct deps only)  
- CDN tarball mirrors  

---

## Decision log

| Date | Decision |
|------|----------|
| 2026-07-28 | Deferred central registry; git/path only |
| 2026-08-04 | Ship local package index + search/add/publish; remote URL optional |
| 2026-08-04 | Seed app ecosystem packages (`json`/`toml` rewrite; `http`/`sqlite` wrap); `build_native` collects dep `[native]` |
