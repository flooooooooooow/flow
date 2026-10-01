# Processes

`lib/stdlib/process.flow` runs other programs and reads this program's own
arguments and environment. Import it as `std.process`.

It compiles with the Stage-A compiler alone. Nothing from `runtime/` is
linked, so a tool built from the bootstrap C can use it.

## Running a command

A command is an argument vector. The child is started with `posix_spawnp`,
so no shell reads the arguments and none of them needs quoting.

```flow
import std.process { ProcCmd, ProcResult, proc_cmd, proc_arg, proc_timeout_ms, proc_run }

extern {
    function printf(fmt: string, ...) -> i32
}

function main() -> i32 {
    let c: ptr<ProcCmd> = proc_cmd("echo")
    proc_arg(c, "hello, world")
    proc_timeout_ms(c, 5000)
    let r: ptr<ProcResult> = proc_run(c)
    printf("exit %d: %s", r.exit_code, r.stdout)
    return r.exit_code
}
```

`proc_cmd(program)` looks `program` up on `PATH` when it has no slash.
`proc_sh(script)` builds `/bin/sh -c script` for when a shell is wanted.

Settings, each optional:

| Call | Effect |
|------|--------|
| `proc_arg(c, a)` | append an argument |
| `proc_env(c, name, value)` | set a variable in the child, on top of this program's environment |
| `proc_env_clear(c)` | start the child with only the `proc_env` variables |
| `proc_cwd(c, dir)` | run the child in `dir` |
| `proc_timeout_ms(c, ms)` | kill the child with `SIGKILL` after `ms` milliseconds |
| `proc_input(c, text)` | write `text` to the child's stdin, then close it |
| `proc_stdin(c, mode)` | `PROC_NULL` (the default) or `PROC_INHERIT` |
| `proc_stdout(c, mode)` | `PROC_CAPTURE` (the default), `PROC_INHERIT` or `PROC_NULL` |
| `proc_stderr(c, mode)` | as stdout, or `PROC_MERGE` to join stdout like `2>&1` |

`proc_run(c)` waits for the child and returns a `ptr<ProcResult>`:

| Field | Meaning |
|-------|---------|
| `exit_code` | the exit status, or minus the signal number when a signal ended the child, as in Python's `subprocess` |
| `stdout`, `stderr` | the captured output ("" for a stream that was not captured) |
| `timed_out` | the child ran past its timeout and was killed |
| `error` | "" when the child started, otherwise why it could not; `exit_code` is then 127 |
| `elapsed_ms` | wall time from spawn to exit |
| `pid` | the child's process id |

Shortcuts: `proc_status(c)` passes output through and returns the exit
code, `proc_output(c)` returns stdout, and `proc_ok(r)` is true when the
command started, exited 0 and did not time out.

Output is read while the child runs, through a `poll` loop over the pipes,
so a child that writes more than a pipe buffer holds does not stall.

## This program

| Call | Returns |
|------|---------|
| `proc_argc()`, `proc_argv(i)` | the command line, `proc_argv(0)` being the program name |
| `proc_args()` | the arguments after the program name, as a `ptr<ProcStrs>` |
| `proc_getenv(name)`, `proc_has_env(name)` | a variable's value ("" when unset) |
| `proc_setenv(name, value)`, `proc_unsetenv(name)` | change this program's environment |
| `proc_environ()` | every `NAME=value` pair |
| `proc_getcwd()`, `proc_chdir(dir)` | the working directory |
| `proc_which(name)` | the path `name` runs as, or "" |
| `proc_pid()`, `proc_now_ms()`, `proc_sleep_ms(ms)` | process id, a monotonic clock, a sleep |
| `proc_errno()`, `proc_strerror(e)` | the last system error |

A program does not need `main(argc, argv)` to read its arguments.

## How it is built

The spawn loop, the environment merge and the `PATH` search are Flow. A
short `@cEmbed` shim covers what differs between platforms: the
`posix_spawn` file actions, `poll`, the wait-status macros, and argv, which
C hands only to `main`. The shim declares `read`, `write`, `pipe` and the
other `unistd.h` calls under private names. A program can still declare
those functions itself through `extern` with Flow types, which would clash
with the header prototypes.

On glibc older than 2.29, which lacks `posix_spawn_file_actions_addchdir_np`,
`proc_cwd` runs the command through `/bin/sh -c 'cd "$0" && exec "$@"'`.

The tests are `tests/lang/test_stdlib_process.flow`.
