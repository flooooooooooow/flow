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

`VERSION` is read from the commit that `--rev` names, so the archive and its
label come from the same commit. `--version` is only a check: it must equal
that `VERSION`. Without `--artifacts-only`, the gates run on the checkout, so
`--rev` must resolve to `HEAD`.

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

On Linux, `--mode full` additionally invokes the checksum-gated
`./flow tool qualify_linux_archive` against the newly created tarball,
and records its clean unpack / compile / execute evidence under `--out/linux/`.
The hash used here is computed from those archive bytes.

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

## Linux (Tier 1 x86-64) release-artifact qualification

Linux release acceptance is local-only and **separate** from macOS Homebrew
acceptance. Obtain the actual released `flow-vVERSION.tar.gz` and its SHA-256
from the corresponding published GitHub Release. Never use the SHA-256 from a
prior tag for a new candidate.

```bash
./flow tool qualify_linux_archive --archive /path/to/flow-vVERSION.tar.gz --sha256 ACTUAL_SHA256
```

This checks the hash *before extraction*, rejects unsafe/archive-mismatched
paths, unpacks the exact artifact in a temporary directory, runs the delivered
`flow version`, compiles the packaged Fibonacci sample and requires its exit
status to be 55. The resulting `qualification-linux.txt` names the artifact,
hash, host platform and C compiler. It does not publish or tag anything.

For Debian/Ubuntu, build a separate local `.deb` from the *frozen* source
commit and verify it without root:

```bash
./flow tool build_deb --rev QUALIFIED_COMMIT --out dist/deb
cat dist/deb/SHA256SUMS.deb.txt
./flow tool qualify_deb --package /path/to/flow_VERSION-1_all.deb --sha256 ACTUAL_DEB_SHA256
```

Both Linux qualification tools require a real locally available artifact; they never
invent digests or create an APT repository. `packaging/README.md` records the
Nix smoke command and the distinction between tested local specs and public
package-manager publication. Linux arm64 remains a Tier 2 candidate pending
its own native-run evidence. A green Linux test does not close the outstanding
macOS Homebrew test in #652.
