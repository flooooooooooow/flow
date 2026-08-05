# Releasing Flow

Flow uses annotated semantic-version tags and GitHub Releases.

## Before tagging

1. Choose the version (`vMAJOR.MINOR.PATCH`).
2. Update all authoritative version surfaces:
   - `flow.toml`
   - `pyproject.toml`
   - `flow` (`flow version`)
   - `CITATION.cff`
   - `docs/wiki-home.md`
   - `docs/project/CHANGELOG.md`
3. Run:
   ```bash
   ./flow test --strict --tier2
   FLOWC_PHASE_A_ONLY=1 ./compiler/scripts/roundtrip.sh
   python3 scripts/build_wiki.py
   python3 scripts/check_wiki_links.py
   ```
4. Merge the release PR and require green `CI`.

## Tag and publish

```bash
git fetch origin main --tags
git tag -a vX.Y.Z origin/main -m "Flow vX.Y.Z"
git push origin vX.Y.Z
```

`.github/workflows/release.yml` creates:

- GitHub Release notes
- `flow-vX.Y.Z.tar.gz`
- `flow-vX.Y.Z.zip`
- `SHA256SUMS.txt`

## Homebrew

After the release workflow succeeds:

1. Download/read `SHA256SUMS.txt`.
2. Update `packaging/homebrew/Formula/flow.rb`.
3. Test the formula locally.
4. Run `packaging/homebrew/sync-tap.sh`.

## After release

- Mark the release as latest.
- Verify https://flooooooooooow.github.io/flow/.
- Ensure the next milestone exists and the roadmap names the current release.
- Announce compatibility changes explicitly.
