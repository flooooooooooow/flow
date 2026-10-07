# CI runners

The CI workflow (`.github/workflows/ci.yml`) runs on two pools.

- **ubuntu-latest**, GitHub-hosted. The heavy jobs: self-host, roundtrip,
  goldens and MLIR, parity gates, corpus parity, native tools, tier-2 and
  the Windows smoke. The free plan allows 20 of these at a
  time for the whole repository.
- **flow-vps-1 and flow-vps-2**, self-hosted, labels `self-hosted`, `linux`,
  `x64` and `flow-vps`. The light jobs: Detect changes, the checks job (Doc
  links), the small report jobs that carry required check names, Doc
  examples, Smoke and CI, and Language tests (with Runtime tests), which
  measured faster here: about 50 s against 80 s on ubuntu-latest. The long
  jobs stay hosted so they never hold up the two VPS runners that every run
  needs for Detect changes and CI.

## Which events use the VPS

Every routed job takes its `runs-on` from the `&flow-runner` anchor on the
`changes` job. It picks the VPS when all of these hold:

- the repository variable `FLOW_VPS_RUNNERS` is not `off`;
- the event is a push to `main`, a merge queue batch, or a pull request
  whose head branch is in this repository.

Anything else, a pull request from a fork included, runs on ubuntu-latest.
Code from outside the repository never runs on the VPS.

## When the VPS is down

A job waiting for a self-hosted runner stays queued; `timeout-minutes`
only counts once a job has started. To send every job back to the hosted
pool:

```
gh variable set FLOW_VPS_RUNNERS --body off -R flooooooooooow/flow
```

Then re-run the runs that were waiting. To use the VPS again:

```
gh variable delete FLOW_VPS_RUNNERS -R flooooooooooow/flow
```

Check the runners with
`gh api repos/flooooooooooow/flow/actions/runners`.

## The host

The runners are registered at repository level and run on one Ubuntu 24.04
VPS, as systemd services `flow-runner@flow-vps-1` and
`flow-runner@flow-vps-2`.

- **User.** `ghrunner`, unprivileged: no sudo, no Docker group, home mode
  700. The services also set `NoNewPrivileges`, so setuid programs cannot
  raise privileges.
- **Isolation.** Each instance has its own `HOME` and its own `/tmp`
  (`PrivateTmp`), and sees no other user's home (`ProtectHome`) and no
  Docker state. A firewall rule for the `ghrunner` uid blocks loopback
  ports below 30000 (other services on the host) and the private and
  Docker networks; DNS and the public internet stay open, and a test can
  still reach a server it starts on an ephemeral loopback port.
- **Resources.** Both instances share the `flow-runners.slice` cgroup:
  `CPUQuota=150%` (1.5 of 2 cores), `MemoryMax=5G` (`MemoryHigh=4.5G`),
  `MemorySwapMax=512M`, and a lower CPU and IO weight than the host's own
  services. The kernel picks a runner job first when memory runs out
  (`OOMScoreAdjust=500`).
- **Clean runs.** A job hook runs before and after every job. It deletes
  the checkout under `_work`, the instance's `HOME` and its `/tmp` files,
  and keeps only the runner, its configuration and the action and tool
  caches. No state carries from one job to the next.
- **Toolchain.** Installed by root ahead of time, so jobs never need sudo:
  build-essential, clang 18, LLVM, clang, lld and MLIR 22 from apt.llvm.org
  (the versions `.github/actions/install-toolchain` pins), shellcheck,
  python3 with venv, jq and zstd.
- **Build cache.** The runners set `ImageOS=ubuntu24`. The VPS has the same
  Ubuntu release and the same `cc` as ubuntu-latest, so
  `.github/actions/flow-bin-cache` computes the same key on both pools and
  either one can restore binaries the other built.

To add or replace a runner, take a registration token from
`gh api -X POST repos/flooooooooooow/flow/actions/runners/registration-token`
and run the runner's `config.sh` as `ghrunner` with
`--labels self-hosted,linux,x64,flow-vps`. The token is single-use and
expires after an hour; it is not stored on the host.
