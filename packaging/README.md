# Flow Packaging & Distribution

This directory contains official package definitions and build specifications for installing Flow across various package managers and operating systems.

## Available Packaging Targets

### 1. Homebrew (macOS / Linux)
- Location: `packaging/homebrew/Formula/flow.rb`
- Repository: `flooooooooooow/homebrew-flow`
- Installation:
  ```bash
  brew tap flooooooooooow/flow
  brew install flow
  ```

### 2. Nix / NixOS
- Locations: `packaging/nix/default.nix`, `packaging/nix/flake.nix`
- Installation via Nix Flakes:
  ```bash
  nix run github:flooooooooooow/flow
  ```
- Installation via nix-env / legacy Nix:
  ```bash
  nix-env -f packaging/nix/default.nix -i
  ```

### 3. Debian / Ubuntu (APT)
- Location: `packaging/deb/`
- Build package:
  ```bash
  ./packaging/deb/build-deb.sh
  ```
- Installation:
  ```bash
  sudo dpkg -i flow_1.0.2-1_amd64.deb
  sudo apt-get install -f
  ```

### 4. Arch Linux (pacman / AUR)
- Location: `packaging/arch/PKGBUILD`
- Build & Install:
  ```bash
  cd packaging/arch
  makepkg -si
  ```

### 5. Windows Scoop
- Location: `packaging/scoop/flow.json`
- Installation:
  ```bash
  scoop install https://raw.githubusercontent.com/flooooooooooow/flow/main/packaging/scoop/flow.json
  ```
