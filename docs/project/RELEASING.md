# Releasing Flow

Flow uses annotated semantic-version tags and GitHub Releases. Qualify an
exact commit first. Do not tag, publish, or guess a Homebrew digest before
that commit has local qualification evidence.

The full pipeline, RC promotion rules and record format are in
[release-qualification.md](release-qualification.md).

## Qualify (does not publish)

From a clean checkout of the commit you intend to ship:

```bash
./flow tool qualify_release --dry-run --out build/qualify
./flow tool qualify_release --check-formula
```

`./flow tool qualify_release` never tags, never creates a GitHub Release,
never pushes, and never updates the public tap. `--publish` is refused.

The default local mode checks version mirrors and the changelog, validates
the in-repo Homebrew formula structure, writes `flow-vVERSION.tar.gz`,
`flow-vVERSION.zip` and `SHA256SUMS.txt` from `git archive`, and lists the
tarball for the paths a user needs after unpack.

For an RC of that same commit (still no tag):

```bash
./flow tool qualify_release --promote-rc --dry-run --out build/qualify
./flow tool qualify_release --print-tag-command
```

Also run, before a final tag:

```bash
./flow test --strict --tier2
./flow tool compiler/scripts/roundtrip.flow
./flow tool build_wiki
./flow tool wiki_links
```

`--mode full` on `qualify_release` adds the remaining hosted release gates
(stability completeness, strict documentation examples, Stable conformance,
bootstrap `--verify`). Use it when you are actually cutting an RC or final
tag.

## Tag only after review

1. Confirm `build/qualify/qualification.txt` (or the `--out` you chose)
   records the intended commit and `published: false`.
2. Choose `vMAJOR.MINOR.PATCH` or `vMAJOR.MINOR.PATCH-rc.N`.
3. Tag that exact SHA. Do not rebuild.

```bash
git fetch origin main --tags
git tag -a vX.Y.Z <qualified-commit> -m "Flow vX.Y.Z"
git push origin vX.Y.Z
```

`.github/workflows/release.yml` creates a GitHub Release, source archives and
`SHA256SUMS.txt` only for non-RC `v*` tags. RC tags (`-rc`) and
`workflow_dispatch` with `qualify_only` run qualification and stop. They do
not publish and do not rewrite Homebrew.

## Homebrew (after a published non-RC release)

Do not guess a checksum. Read the digest from the published
`SHA256SUMS.txt`, then:

```bash
./flow tool sync_version --homebrew --sha256 <digest>
brew style ./packaging/homebrew/Formula/flow.rb
brew audit --strict --offline ./packaging/homebrew/Formula/flow.rb
brew install --build-from-source ./packaging/homebrew/Formula/flow.rb
./flow tool packaging/homebrew/sync-tap.flow
./flow tool packaging/homebrew/check-formula-sync.flow ../homebrew-flow/Formula/flow.rb
```

`sync-tap` pushes to `flooooooooooow/homebrew-flow`. Only run it when you
intend to publish the tap.

## After a published release

- Mark the release as latest when it is the current stable line.
- Verify https://flooooooooooow.github.io/flow/.
- Ensure the next milestone exists and the roadmap names the current release.
- Announce compatibility changes explicitly.
