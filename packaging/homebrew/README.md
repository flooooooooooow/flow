# Homebrew tap for Flow

Install Flow with Homebrew:

```bash
brew tap flooooooooooow/flow
brew install flooooooooooow/flow/flow
# Or track main:
# brew install --HEAD flooooooooooow/flow/flow

flow help
```

This is a **formula** (CLI / language toolchain), not a **cask**. Casks are for
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
| `brew install …` | Stable **v0.8.0** release archive + verified SHA256. |
| `brew install --HEAD …` | Builds from `main`. |

### Updating the stable formula

After cutting a new release:

1. Wait for `.github/workflows/release.yml` to attach the release archive.
2. Read the SHA256 from the attached `SHA256SUMS.txt`:
   ```bash
   gh release download vX.Y.Z -R flooooooooooow/flow -p SHA256SUMS.txt
   ```
3. Update `url`, `sha256`, and `version` in `Formula/flow.rb`.
4. Sync the tap (below).

## Publishing / updating the tap

`packaging/homebrew/sync-tap.sh` **clones the tap and `git push`es** to
`flooooooooooow/homebrew-flow`. Only run it when you intend to publish.

Local formula edits in this monorepo do **not** require running sync-tap.

From the Flow repo root (needs `gh` auth), when ready to publish:

```bash
./packaging/homebrew/sync-tap.sh
```

Or manually copy `Formula/flow.rb` into the `homebrew-flow` repo and push.

## Local test (no tap push)

```bash
brew install --build-from-source ./packaging/homebrew/Formula/flow.rb
```
