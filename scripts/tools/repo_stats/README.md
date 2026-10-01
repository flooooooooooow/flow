# Repo stats (Flow)

Counts tracked source files and refreshes:

- `docs/generated/repository-stats.json`
- the `<!-- repo-stats:start -->` … `<!-- repo-stats:end -->` block in `README.md`

## Run

```bash
./scripts/update_repo_stats.sh
./scripts/update_repo_stats.sh --check
```

The script builds `main.flow` with `scripts/tools/build_tool.sh` (Stage-A
flowc from the bootstrap C, so only a C compiler is needed) and runs it.
The program runs git itself through `std.process`.

## Split of responsibility

| Layer | Owns |
|-------|------|
| `update_repo_stats.sh` | build and run with a timeout |
| `main.flow` | git calls, revision skipping, exclude rules, line counts, area/language totals, JSON + README splice |
