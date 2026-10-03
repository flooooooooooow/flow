# Repo stats (Flow)

Counts tracked source files and refreshes:

- `docs/generated/repository-stats.json`
- the `<!-- repo-stats:start -->` … `<!-- repo-stats:end -->` block in `README.md`

## Run

```bash
./flow tool repo_stats
./flow tool repo_stats --check
```

`flow tool` builds `main.flow` with the Stage-A flowc from the bootstrap C,
so only a C compiler is needed, and runs it. The program runs git itself
through `std.process`, and runs its work in a child process under a time
limit (`FLOW_STATS_TIMEOUT` seconds, default 90).

## Split of responsibility

| Layer | Owns |
|-------|------|
| `flow tool` | build the program and run it from the caller's directory |
| `main.flow` | the time limit, git calls, revision skipping, exclude rules, line counts, area/language totals, JSON + README splice |
