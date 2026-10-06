# Reproducible release qualification and RC promotion

Tracker: [#652](https://github.com/flooooooooooow/flow/issues/652).

This is the in-repo path that qualifies an exact commit before anyone tags or
publishes it. The qualifier writes archives, SHA-256 sums and a promotion
record. It never tags, never creates a GitHub Release, never pushes, and never
updates `flooooooooooow/homebrew-flow`.

The live operator checklist is [RELEASING.md](RELEASING.md). Hosted publication
still lives in `.github/workflows/release.yml` and runs only after a human tags
a commit that already has qualification evidence.

## Pipeline

The release pipeline qualifies the exact artifacts being published:

```text
commit/tag
  -> clean checkout
  -> bootstrap freshness
  -> self-host/fixed point
  -> conformance
  -> stdlib/runtime
  -> docs/examples
  -> platform matrix
  -> security/fuzz/perf gates
  -> package
  -> unpack/install in a clean environment
  -> compile/run a real program
  -> checksums/provenance
  -> publish
```

`publish` is a later, human-reviewed step. Qualification stops at checksums and
records `published: false`.

## Local command

```bash
./flow tool qualify_release --dry-run --out build/qualify
```

`--dry-run` is implied. The default `--mode local` path:

1. Runs `./flow tool sync_version --check` and `./flow tool changelog_check`.
2. Validates `packaging/homebrew/Formula/flow.rb` (url, 64-hex SHA-256, version,
   url/version agreement).
3. Builds `flow-vVERSION.tar.gz` and `flow-vVERSION.zip` with `git archive`
   from `--rev` (default `HEAD`).
4. Writes `SHA256SUMS.txt`.
5. Lists the tarball and checks that `VERSION`, `flow`, `compiler/`, `lib/`,
   `runtime/`, `tools/` and the Homebrew formula are present.
6. Writes `qualification.txt` and `qualification.json` with
   `published: false` and `tagged: false`.

`--artifacts-only` skips the version/changelog tool gates and still writes the
archives and record. `--mode full` also runs the expensive gates used by
`.github/workflows/release.yml` (stability completeness, strict documentation
examples, Stable conformance, bootstrap `--verify`). Do not use `--mode full`
unless you intend to wait for that matrix.

`--publish` exits 2 and changes nothing.

## Homebrew formula check

```bash
./flow tool qualify_release --check-formula
```

This is the local structural check: the in-repo formula must name a
`flow-vVERSION.tar.gz` URL, a 64-digit SHA-256, and a semantic `version` that
matches the URL. Without a `version` line, the version is read from the URL,
as Homebrew does. The formula may still point at the last *published* release
while the candidate version in `VERSION` is newer. That mismatch is printed and
does not count as a failure. Update url/sha256 only after the real artifact
exists; do not guess a digest.

When `--mode full` is used and `brew` is on `PATH`, the same check also runs:

```bash
brew style packaging/homebrew/Formula/flow.rb
brew audit --strict --offline packaging/homebrew/Formula/flow.rb
```

`brew install --build-from-source` downloads the published tarball. Run it from
a clean checkout only after that tarball exists:

```bash
brew install --build-from-source ./packaging/homebrew/Formula/flow.rb
./flow tool packaging/homebrew/check-formula-sync.flow ../homebrew-flow/Formula/flow.rb
```

`./flow tool packaging/homebrew/sync-tap.flow` pushes to the public tap. Do not
run it from qualification.

## RC promotion

Promote an exact qualified commit. Do not rebuild after qualification.

```bash
./flow tool qualify_release --promote-rc --dry-run --out build/qualify
./flow tool qualify_release --print-tag-command
```

`--promote-rc` writes `rc-promotion.txt` naming `vVERSION-rc.N` and the commit
SHA. It does not run `git tag`. `--print-tag-command` prints the command and
exits. After review, a human tags that SHA:

```bash
git tag -a vX.Y.Z-rc.N <commit> -m "Flow vX.Y.Z-rc.N"
```

`.github/workflows/release.yml` qualifies `v*` tags, including RCs, but does
not publish a GitHub Release or rewrite Homebrew when the tag contains `-rc`
or when `qualify_only` is set. `.github/workflows/release-qualify.yml` is the
hosted dry-run of `./flow tool qualify_release --dry-run` and never has
`contents: write`.

A final non-RC tag is the same commit that already passed this path, not a
rebuild. After that GitHub Release exists, compute the real tarball digest,
then:

```bash
./flow tool sync_version --homebrew --sha256 <digest>
./flow tool packaging/homebrew/check-formula-sync.flow ../homebrew-flow/Formula/flow.rb
```

## Records

A passing dry-run leaves at least:

| File | Meaning |
|------|---------|
| `flow-vVERSION.tar.gz` / `.zip` | Source archives of `--rev` |
| `SHA256SUMS.txt` | SHA-256 of those archives |
| `qualification.txt` / `.json` | Commit, digests, `published: false` |
| `rc-promotion.txt` | Only with `--promote-rc`; still `tagged: false` |
