# Nix packaging for Flow

Flow provides a reproducible Nix flake (`flake.nix`) and derivation (`default.nix`) supporting `x86_64-linux`, `aarch64-linux`, `x86_64-darwin`, and `aarch64-darwin`.

## Quickstart

### Run directly via Flake

Run Flow without installing:

```bash
nix run github:flooooooooooow/flow -- version
```

Or from a local checkout:

```bash
nix run . -- version
nix run . -- run examples/basics/hello_world.flow
```

### Install to profile

Install Flow to your Nix profile:

```bash
nix profile install github:flooooooooooow/flow
```

Or locally:

```bash
nix profile install .
```

### Build with Nix

Build the package locally into `./result`:

```bash
nix build
./result/bin/flow version
```

Or using legacy Nix tools:

```bash
nix-build packaging/nix/default.nix
```

### Development shell

Enter a development shell with `flow`, `python3`, `numpy`, and `pytest` on PATH:

```bash
nix develop
```
