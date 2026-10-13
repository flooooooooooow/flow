# Flow agent sandbox (Linux, experimental)

This is a real, opt-in **native execution** boundary for programs produced by AI agents, not an effect checker and not a general AI alignment guarantee.

It requires Linux bubblewrap at `/usr/bin/bwrap` and working unprivileged user namespaces. If either is unavailable, the launcher refuses to execute the guest, rather than silently falling back to native execution. It does not modify the existing `flow run`.

From the repository root:

```sh
mkdir -p /tmp/flow-agent-output
./flow tool agent_sandbox --workspace . --output /tmp/flow-agent-output --timeout-ms 5000 -- /bin/sh -c 'printf ok > /output/example.txt'
./flow tool tools/agent_sandbox/test.flow
```

The trusted caller supplies **existing** workspace and output directories. The launcher rejects an output directory that is identical to or contains the read-only workspace, since that would make workspace files writable through `/output`. The guest sees the former at `/workspace`, read-only, and the latter at `/output`, writable. Original host paths are not mounted at those locations. It gets a fresh mount root, PID namespace and network namespace, no inherited environment, a private `/tmp`, and read-only `/usr`, `/bin`, `/lib` and `/lib64` toolchain mounts. No host `/home`, `/etc`, network egress or arbitrary device pass-through is intended. A restricted `/dev` and `/proc` are mounted inside the sandbox. The executable/arguments are passed as an argv array; no shell is used by the launcher.

A wall-time limit of at most 30 seconds is enforced by `std.process` (default 5 seconds). A timeout exits 124. Configuration errors exit 2; failure to start isolation exits 125; otherwise the guest exit status is propagated.

**Trust assumptions:** The caller decides what directories to grant. Do not point `--workspace` at a directory containing credentials or secrets, or `--output` at an important host directory. The sandbox still sees and can alter contents of the explicitly writable output directory. The host OS kernel, bubblewrap and inherited loader/toolchain installations are trusted, and kernel vulnerabilities remain possible.

**Not yet enforced:** memory/address-space limits, process counts, seccomp, filesystem storage quotas (including the private tmpfs), verified executable identity, device and GPU isolation beyond minimal bubblewrap setup, preventing privileged host tooling from running the launcher itself, and portability beyond Linux. File paths are resolved before bubblewrap starts, so an attacker able to swap a host mount path concurrently may exploit a time-of-check/time-of-use race. Network namespace isolation does not by itself establish protection against host Unix-domain sockets that are accessible through a granted mount. The launcher forwards guest stdout and stderr to the host, so secrets visible in an authorised mount may leak through logs or written output files. Outputs must be treated as untrusted artifacts, never automatically run, deployed or used as privileged instructions. This tool must not be marketed as complete or production-qualified isolation. The static Flow effects feature is currently orthogonal and does not confer these OS permissions.

The hosted Linux GitHub Actions job `Agent sandbox boundary / Linux namespace enforcement` runs live runtime probes with a disposable workspace fixture: workspace read, output write, denied workspace write, denied host `/etc/passwd`, independent network namespace, attempted outbound TCP to an IP literal, denied writable ancestor alias, denied symlink write escape, guest exit status, timeout and invalid output path. The workflow is read-only and does not expose secrets. A skipped or missing check is not proof of safety; configure an external GitHub ruleset to require this check after it has passed.

Design and outstanding questions: [FSA architecture](../../docs/security/ai-safety-architecture.md), issue #1544. For a production safe profile, layer static effect checking and denial of unsafe FFI on top of OS isolation, then add kernel-enforced memory/process budgets and cross-backend parity tests.
