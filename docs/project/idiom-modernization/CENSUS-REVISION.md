# Census revision pin

FM-001 records the exact Git revision and the host toolchain used for the
source census tools. The pin is produced by `./flow tool census_revision`.

## Commands

```
./flow tool census_revision
./flow tool census_revision --write
./flow tool census_revision --check
./flow tool census_revision --run-checks
./flow tool census_revision --snapshot PATH
```

Default output is `flow.census-revision.v1` JSON for the current `HEAD`.
`--write` records that report, including the exit status of each census
tool, at `docs/project/idiom-modernization/census-revision.json` unless
`--snapshot` names another path. `--check` validates a snapshot.

The census tools invoked, and recorded in the snapshot, are:

- `./flow tool idiom_census --check`
- `./flow tool feature_evidence --check`
- `./flow tool compiler/scripts/parse_coverage.flow --check`
- `./flow tool doc_coverage`

## Dirty worktree

`git status --porcelain` must be empty for `--write` and `--check`. The
default JSON report still prints when the tree is dirty, with
`worktree_clean` set to `false`, and then exits 1. A pin is never written
from a dirty tree, so uncommitted files cannot be mixed into a HEAD SHA.

## What the snapshot is and is not

`revision` is the full SHA of the tree the snapshot describes.
`--check` requires that SHA to be a Git commit in this repository. It does
not require `revision` to equal the current `HEAD`, because later commits
can add tooling without taking a new census. Toolchain fields (`flow`,
`flow_host`, `uname_s`, `uname_m`, `cc`, `mlir_opt`) describe the recording
host and are not compared across machines.

Selection rules are in the `selection` object: tracked files from
`git ls-files`. `examples/verify` and `compiler/fixtures` are inventoried
as proof or fixture sources. Those classes stay out of an adoption
denominator. A resolved path is an anchor. That anchor does not prove
the feature works. Missing evidence stays unverified. A nonzero exit
from a census tool is a recorded baseline failure. That failure is not
a shipped or absent feature label.

This pin does not assign stable feature IDs and does not replace
`feature_evidence` or `idiom_census`.
