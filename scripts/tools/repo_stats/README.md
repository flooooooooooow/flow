# Repo stats (Flow)

Counts tracked source files and refreshes:

- `docs/generated/repository-stats.json`
- the `<!-- repo-stats:start -->` … `<!-- repo-stats:end -->` block in `README.md`

## Run

```bash
./scripts/update_repo_stats.sh
./scripts/update_repo_stats.sh --check
```

The shell shim dumps the tracked-file list and the commit metadata into
`build/repo-stats/`, builds `main.flow` with `scripts/tools/build_tool.sh`
(Stage-A flowc from the bootstrap C, so only a C compiler is needed), then
runs it.

## Split of responsibility

| Layer | Owns |
|-------|------|
| `update_repo_stats.sh` | tracked-file list, revision skipping, build and run with a timeout |
| `main.flow` | exclude rules, line counts, area/language totals, JSON + README splice |
