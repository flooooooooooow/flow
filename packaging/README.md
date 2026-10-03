# Flow Packaging & Distribution

This directory tracks packaging definitions and ecosystem distribution status for Flow across supported platforms.

## Package Manager Availability Matrix

| Package Manager | Target Systems | Status | Location / Command |
|---|---|---|---|
| **Homebrew** | macOS (`arm64`), Linux (`x86_64`) | **Available** (Tier-1) | `brew tap flooooooooooow/flow && brew install flow` ([packaging/homebrew](homebrew)) |
| **Nix Flake** | macOS (`aarch64`, `x86_64`), Linux (`x86_64`, `aarch64`) | **Available** (Tier-1 / Tier-2) | `nix profile install .` / `nix run .` ([packaging/nix](nix), `flake.nix`) |
| **Linux Distros** (APT/Debian, RPM/Fedora, Arch AUR) | Linux (`x86_64`) | **Evaluated** | Source builds require C11 + Python 3.9+; official distro repo submission evaluated as release artifacts fit |
| **Winget / Chocolatey** | Windows (`x86_64`) | **Deferred** | Windows is Tier-2 candidate; publication deferred until Windows has a supported Tier-1 release binary artifact |

## Active Package Ecosystems

### Homebrew Tap
Homebrew formula metadata and tap synchronization script live under `packaging/homebrew/`.
The tap repository is published at [`flooooooooooow/homebrew-flow`](https://github.com/flooooooooooow/homebrew-flow).

```bash
brew tap flooooooooooow/flow
brew install flow
```

### Nix Flake & Derivation
Flow includes a root `flake.nix` and `packaging/nix/default.nix` providing a reproducible build environment across supported Linux and macOS architectures (`x86_64-linux`, `aarch64-linux`, `x86_64-darwin`, `aarch64-darwin`).

```bash
nix run github:flooooooooooow/flow -- version
nix profile install github:flooooooooooow/flow
```

## Distro & Platform Packaging Evaluations

### Linux Native Packages (Debian / Fedora / Arch)
- **Status:** Evaluated.
- **Toolchain Requirements:** Conforming C11 compiler (`cc`) + Python 3.9+ runtime host.
- **Evaluation:** Direct inclusion in distro core repositories (e.g. Debian main or Fedora official) requires stable distro release tarballs and dedicated package maintainers. Community package targets (such as Arch AUR or Fedora COPR) are evaluated for community publication as release tarball pipelines stabilize.

### Windows (Winget & Chocolatey)
- **Status:** Deferred.
- **Reasoning:** In accordance with `PLATFORMS.md`, Windows is currently classified as a Tier-2 candidate platform. Full Tier-1 qualification requires continuous qualification matrix enforcement and release-artifact verification. Winget and Chocolatey package submission is deferred until Windows achieves a fully qualified Tier-1 release binary artifact.
