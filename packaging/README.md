# Flow Packaging & Distribution

This directory contains packaging definitions maintained with the Flow source tree. A definition being present here does not mean the package has been published to an external package registry.

## Published channel

### Homebrew (macOS / Linux)

Homebrew is the currently published package-manager channel:

```bash
brew tap flooooooooooow/flow
brew install flow
```

The tap is maintained in `flooooooooooow/homebrew-flow`.

## Build-from-checkout specifications

### Nix / NixOS

`packaging/nix/default.nix` and `packaging/nix/flake.nix` build the current checkout rather than fetching a guessed release tag or placeholder hash:

```bash
nix build ./packaging/nix#flow
./result/bin/flow version
```

This is a repository-local flake specification. It is not a claim that Flow has been accepted into nixpkgs.

### Debian / Ubuntu

`packaging/deb/` contains Debian metadata for building a package from the current checkout:

```bash
./flow tool build_deb
```

The tool prints the path of the generated `.deb`. This repository does not currently advertise an APT repository.

## Deferred channels

Arch/AUR packaging is deferred until a stable versioned source artifact exists that a PKGBUILD can verify reproducibly.

Windows/Scoop packaging is deferred until Flow has a supported Windows release artifact. Do not publish a Scoop manifest that points at source archives or placeholder hashes.

External package-manager documentation should be promoted to the published section only after that channel is actually installable and verified.
