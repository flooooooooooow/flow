"""Python called from Flow, unchanged between CPython and Pyodide.

Flow reaches these through lib/stdlib/python_embed.flow. Natively that is
libpython in-process; in a browser it is Pyodide, and this file does not know
the difference.
"""

import math
import platform
import sys

_events = []


def banner() -> None:
    """python_call0: no arguments, no return value."""
    _events.append("banner")
    print(f"  [python] {platform.python_implementation()} {sys.version.split()[0]}")
    print(f"  [python] platform: {sys.platform}")


def greet(name: str) -> str:
    """python_call1_str: a string across the boundary."""
    _events.append(f"greet:{name}")
    print(f"  [python] hello, {name}")
    return name


def square(n: int) -> int:
    """python_call1_i32."""
    _events.append(f"square:{n}")
    print(f"  [python] {n} squared is {n * n}")
    return n * n


def scale(x: float) -> float:
    """python_call1_f32."""
    _events.append(f"scale:{x:.4f}")
    print(f"  [python] {x:.4f} * 3 = {x * 3:.4f}")
    return x * 3.0


def toggle(flag: bool) -> bool:
    """python_call1_bool."""
    _events.append(f"toggle:{flag}")
    print(f"  [python] not {flag} is {not flag}")
    return not flag


def hypot3(a: int, b: int, c: int) -> float:
    """python_call3_i32_f64: three ints in, one double back.

    The value Flow prints comes out of CPython's own math library, so it is
    evidence that Python ran rather than that a stub returned something.
    """
    _events.append(f"hypot3:{a},{b},{c}")
    return math.sqrt(a * a + b * b + c * c)


def event_count() -> int:
    """Module state survives between calls, so this counts the calls above."""
    print(f"  [python] module state recorded {len(_events)} calls: {_events}")
    return len(_events)


def boom() -> None:
    """Raises, so the error path can be shown working."""
    raise ValueError("this exception was raised inside Python")
