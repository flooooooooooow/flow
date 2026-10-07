# Flow Packaging & Distribution

This directory contains packaging definitions maintained with the Flow source tree. A definition being present here does not mean the package has been published to an external package registry.

## Published channel

### Homebrew (macOS; Linux requires separate validation)

Homebrew is the currently published package-manager channel:

```bash
brew tap flooooooooooow/flow
brew install flow
```

The tap is maintained in `flooooooooooow/homebrew-flow`. A published formula is not evidence of a successful Linux Homebrew installation; run the local Linux package checks below and validate Homebrew separately before claiming support.

## Build-from-checkout specifications

### Nix / NixOS

`packaging/nix/default.nix` and `packaging/nix/flake.nix` build the current checkout rather than fetching a guessed release tag or placeholder hash:

```bash
nix build .#default
./result/bin/flow version
```

The root `flake.nix` builds the same package (`nix build .#flow`, or `nix run github:flooooooooooow/flow -- version`). Both flakes call `packaging/nix/default.nix`. The package builds the bootstrap compiler and the `flow` command at build time. At run time the store copy is read-only, so compiled programs go to `$FLOW_BUILD_ROOT` (default `~/.cache/flow/build`) and tool binaries and the runtime archive go to `~/.cache/flow`. The `Nix package` workflow builds both flakes and runs a program on Linux and macOS.

This is a repository-local flake specification. It is not a claim that Flow has been accepted into nixpkgs.

### Debian / Ubuntu

`packaging/deb/` contains Debian metadata for building a package from the current checkout:

```bash
./flow tool build_deb --rev HEAD --out dist/deb
```

The tool prints the path of the generated `.deb` and records its actual SHA-256. This repository does not currently advertise an APT repository.

## Deferred channels

Arch/AUR packaging is deferred until a stable versioned source artifact exists that a PKGBUILD can verify reproducibly.

Windows/Scoop packaging is deferred until Flow has a supported Windows release artifact. Do not publish a Scoop manifest that points at source archives or placeholder hashes.

External package-manager documentation should be promoted to the published section only after that channel is actually installable and verified.

## Linux release acceptance (local-only)

On an x86-64 Linux machine, use the published asset and its actual SHA-256 (from
GitHub's release asset or `SHA256SUMS.txt`). The qualification tool rejects a
missing or wrong digest, unpacks to a disposable directory, runs `flow version`,
compiles the bundled Fibonacci sample and checks its exit status (55).

```bash
./flow tool qualify_linux_archive \
  --archive dist/flow-v1.0.1.tar.gz \
  --sha256 deb4978f97cb5643c29fcb9d73ab72a8eb121e2e31c60df73ba6870d04f5229b
```

The example digest is the published v1.0.1 artifact digest, **not** a checksum
for any future candidate. Run against the exact published tarball, not a moving
source checkout. Passing evidence is written to
`build/linux-qualification/qualification-linux.txt`.

### Debian / Ubuntu (unpublished local artifacts)

Build from one pinned commit, without a network connection or system install:

```bash
./flow tool build_deb --rev HEAD --out dist/deb
cat dist/deb/SHA256SUMS.deb.txt
```

The tool uses `git archive`, `SOURCE_DATE_EPOCH`, fixed ownership and gzip
compression to create `flow_VERSION-1_all.deb`. The package installs the
source-based compiler/runtime under `/usr/lib/flow`, with command symlinks in
`/usr/bin`. It never publishes or installs anything. **HEAD is a development
example**; use a frozen release commit when qualifying a release.

For a local install/execution check without root, pass the computed hash:

```bash
./flow tool qualify_deb \
  --package dist/deb/flow_2.0.0-1_all.deb \
  --sha256 "$(awk '$2 == "flow_2.0.0-1_all.deb" { print $1 }' dist/deb/SHA256SUMS.deb.txt)"
```

This package name describes the currently declared 2.0.0 tree, not a published
Flow 2.0 release. The `.deb` verifier checks the archive, package metadata,
installed symlinks, `flow version`, compiler execution and Fibonacci's exit
status. Its evidence is in `build/linux-deb-qualification/qualification-deb.txt`.
No APT repository or signed DEB release is claimed.

### Nix / NixOS

The repository's top-level flake is the supported build-from-checkout entry:

```bash
nix build .#default
./result/bin/flow version
```

Nix package availability or installation on Linux is not proven by the presence
of a flake alone; record the platform, resolved inputs and an actual build
result before promising supported binaries.
