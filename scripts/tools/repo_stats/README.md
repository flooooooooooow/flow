# Repo stats (Flow)

Counts tracked source files and refreshes:

- `docs/generated/repository-stats.json`
- the `<!-- repo-stats:start -->` … `<!-- repo-stats:end -->` block in `README.md`

## Run

```bash
./scripts/update_repo_stats.sh
./scripts/update_repo_stats.sh --check
```

The shell shim dumps `git ls-files` + commit metadata (stdout capture), then runs
`main.flow`. If Flow compile/run fails, it falls back to
`scripts/update_repo_stats.py`.

## Split of responsibility

| Layer | Owns |
|-------|------|
| `update_repo_stats.sh` | `git ls-files`, revision skipping, compile/run, Python fallback |
| `main.flow` | exclude rules, line counts, area/language totals, JSON + README splice |
| `update_repo_stats.py` | reference implementation / fallback |
