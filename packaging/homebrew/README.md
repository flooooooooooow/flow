# Homebrew tap for Flow

Install Flow with Homebrew:

```bash
brew tap flooooooooooow/flow
brew install flooooooooooow/flow/flow
# Or track main:
# brew install --HEAD flooooooooooow/flow/flow

flow help
```

This is a **formula** (CLI / language toolchain) rather than a **cask**. Casks are for
GUI `.app` / binary app distributions; Flow ships as source + a `flow` driver.

## Tap repository

Homebrew expects the tap repo to be named `homebrew-flow`:

| Piece | Location |
|-------|----------|
| Public tap | `https://github.com/flooooooooooow/homebrew-flow` |
| Formula source of truth (this monorepo) | `packaging/homebrew/Formula/flow.rb` |

Users run: `brew tap flooooooooooow/flow` → clones `homebrew-flow`.

## HEAD vs stable

| Install | When |
|---------|------|
| `brew install …` | Last published release archive + verified SHA256 (see `Formula/flow.rb`). |
| `brew install --HEAD …` | Builds from `main`. |

### Validate the in-repo formula (no tap push)

```bash
./flow tool qualify_release --check-formula
```

That check exits 0 only when `url`, `sha256` (64 hex digits) and `version`
agree. It does not download the tarball and does not publish. After a real
non-RC GitHub Release exists, install from a clean checkout:

```bash
brew style ./packaging/homebrew/Formula/flow.rb
brew audit --strict --offline ./packaging/homebrew/Formula/flow.rb
brew install --build-from-source ./packaging/homebrew/Formula/flow.rb
```

### Updating the stable formula

After cutting a new **non-RC** release:

1. Wait for `.github/workflows/release.yml` to attach the release archive.
2. Read the SHA256 from the attached `SHA256SUMS.txt`:
   ```bash
   gh release download vX.Y.Z -R flooooooooooow/flow -p SHA256SUMS.txt
   ```
3. Apply that exact digest (do not guess):
   ```bash
   ./flow tool sync_version --homebrew --sha256 <digest>
   ```
4. Re-run `--check-formula`, then sync the tap (below).

## Publishing / updating the tap

`./flow tool packaging/homebrew/sync-tap.flow` **clones the tap and `git push`es** to
`flooooooooooow/homebrew-flow`. Only run it when you intend to publish.

Local formula edits in this monorepo do **not** require running sync-tap.

From the Flow repo root (needs `gh` auth), when ready to publish:

```bash
./flow tool packaging/homebrew/sync-tap.flow
```

Or manually copy `Formula/flow.rb` into the `homebrew-flow` repo and push.

## Local test (no tap push)

```bash
brew install --build-from-source ./packaging/homebrew/Formula/flow.rb
```
