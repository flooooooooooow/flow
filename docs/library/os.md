# errno, signals and C constants

`lib/stdlib/os.flow` reads `errno`, installs signal handlers and declares
the common signal and errno constants. Import it as `std.os`.

```flow
import std.os { os_signal_watch, os_signal_take, os_raise, SIGINT, SIGUSR1 }

function main() -> i32 {
    if os_signal_watch(SIGUSR1) == false {
        return 1
    }
    let _r: i32 = os_raise(SIGUSR1)
    if os_signal_take(SIGUSR1) != 1 {
        return 2
    }
    if SIGINT != 2 {
        return 3
    }
    return 0
}
```

## C constants

The constants are `extern const` declarations (see the language spec,
section 3.5). Each names the C macro of the same name, so its value comes
from this platform's headers when the C output is compiled. `std.os`
declares:

- signals: `SIGHUP SIGINT SIGQUIT SIGABRT SIGKILL SIGPIPE SIGALRM SIGTERM
  SIGCHLD SIGCONT SIGSTOP SIGTSTP SIGUSR1 SIGUSR2 SIGWINCH`
- errno values: `EPERM ENOENT ESRCH EINTR EIO EBADF ECHILD EAGAIN
  EWOULDBLOCK ENOMEM EACCES EEXIST ENOTDIR EISDIR EINVAL ENOSPC EPIPE ERANGE
  EINPROGRESS EADDRINUSE ECONNREFUSED ECONNRESET ETIMEDOUT`

A program declares any other constant, size or offset the same way:

```flow-pseudocode
@cEmbed("#include <poll.h>
#include <stddef.h>")

extern {
    const POLLIN: i32
    const POLLFD_SIZE: i64 = "(int64_t)sizeof(struct pollfd)"
    const POLLFD_REVENTS: i64 = "(int64_t)offsetof(struct pollfd, revents)"
}
```

## errno

`errno` is a macro over a per-thread location (`__error()` on macOS,
`__errno_location()` on Linux), so it is read through a function:

| Call | Effect |
|------|--------|
| `os_errno()` | errno after the last failed system call |
| `os_set_errno(e)` | set it, for example to 0 before a call |
| `os_strerror(e)` | the system's text for `e` |

## Signals

| Call | Effect |
|------|--------|
| `os_signal_watch(sig)` | count deliveries of `sig` instead of taking its default action |
| `os_signal_take(sig)` | deliveries since the last call, and reset the count |
| `os_signal_pending(sig)` | deliveries not yet taken |
| `os_signal_handle(sig, f as ptr<void>)` | run the Flow function `f(sig: i32)` as the handler |
| `os_signal_ignore(sig)`, `os_signal_default(sig)` | `SIG_IGN`, `SIG_DFL` |
| `os_raise(sig)` | send `sig` to this process |

`os_signal_watch` is the safe choice. Its C handler only increments a
counter, and the program polls with `os_signal_take` from ordinary Flow
code, for example once per loop of a server. A handler installed with
`os_signal_handle` runs inside the signal, where only async-signal-safe
work is allowed. The watch functions return false for a signal that cannot
be caught (`SIGKILL`, `SIGSTOP`).

The tests are `tests/lang/test_extern_const.flow`.
