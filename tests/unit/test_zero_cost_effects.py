"""
Regression tests for zero-cost substitution (flow-zero-cost-substitution).

Inside a `handle Effect with Cap` block the handler is known at compile
time, so the C generator emits a direct call to the capability function
instead of routing through the vtable dispatch function. Dynamic dispatch
must be preserved everywhere the handler is unknowable at the call site:
in functions outside the block, in lambda bodies (closures may outlive the
block), and for operations the bound capability does not implement.
"""

import shutil
import subprocess

import pytest

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c


EFFECT_PRELUDE = """
effect Log {
    info(msg: string) -> void,
    metric(name: string, value: i32) -> i32,
}

capability Console {
    effect Log,
    function info(msg: string) -> void {
        printf("[console] %s\\n", msg)
    },
    function metric(name: string, value: i32) -> i32 {
        printf("[metric] %s=%d\\n", name, value)
        return value
    },
}

capability Quiet {
    effect Log,
    function info(msg: string) -> void {
        let unused: i32 = 0
    },
}
"""


def gen(main_body: str) -> str:
    code = EFFECT_PRELUDE + "function main() -> i32 {\n%s\n    return 0\n}\n" % main_body
    return flow_to_c(parse_flow_code(code))


def main_body_of(c_code: str) -> str:
    """Return the generated C of main() only, so prelude/vtable lines don't match."""
    start = c_code.index("int32_t main(")
    return c_code[start:]


def test_direct_call_inside_handle_block():
    c = gen(
        """
    handle Log with Console {
        Log.info("hello")
    }
"""
    )
    body = main_body_of(c)
    assert 'Console_info("hello")' in body
    assert 'Log_info("hello")' not in body


def test_dynamic_dispatch_outside_handle_block():
    c = gen(
        """
    Log.info("before")
    handle Log with Console {
        Log.info("inside")
    }
    Log.info("after")
"""
    )
    body = main_body_of(c)
    assert 'Log_info("before")' in body
    assert 'Console_info("inside")' in body
    assert 'Log_info("after")' in body


def test_dynamic_dispatch_in_called_function():
    code = EFFECT_PRELUDE + """
function helper() -> void {
    Log.info("from helper")
}

function main() -> i32 {
    handle Log with Console {
        helper()
    }
    return 0
}
"""
    c = flow_to_c(parse_flow_code(code))
    assert 'Log_info("from helper")' in c
    assert 'Console_info("from helper")' not in c


def test_nested_handle_overrides_and_restores():
    c = gen(
        """
    handle Log with Console {
        Log.info("outer")
        handle Log with Quiet {
            Log.info("inner")
        }
        Log.info("restored")
    }
"""
    )
    body = main_body_of(c)
    assert 'Console_info("outer")' in body
    assert 'Quiet_info("inner")' in body
    assert 'Console_info("restored")' in body


def test_missing_operation_falls_back_to_dispatch():
    c = gen(
        """
    handle Log with Quiet {
        let v: i32 = Log.metric("count", 1)
    }
"""
    )
    body = main_body_of(c)
    assert 'Log_metric("count", 1)' in body
    assert "Quiet_metric" not in body


def test_lambda_body_keeps_dynamic_dispatch():
    c = gen(
        """
    handle Log with Console {
        let f = |x: i32| -> void {
            Log.info("from lambda")
        }
    }
"""
    )
    assert 'Log_info("from lambda")' in c
    assert 'Console_info("from lambda")' not in c


def test_runtime_vtable_still_installed():
    """The handle block must still install the runtime handler so calls in
    other functions dispatch correctly."""
    c = gen(
        """
    handle Log with Console {
        Log.info("x")
    }
"""
    )
    body = main_body_of(c)
    assert "_current_Log_handler = &_Console_Log_vtable;" in body
    assert "_current_Log_handler = _prev_Log_handler;" in body


@pytest.mark.skipif(shutil.which("clang") is None, reason="clang not available")
def test_end_to_end_behavior(tmp_path):
    """Compile and run: direct calls, dynamic fallback, and handler restore
    must all produce the same observable behavior as full dynamic dispatch."""
    code = EFFECT_PRELUDE + """
function helper() -> void {
    Log.info("helper sees installed handler")
}

function main() -> i32 {
    Log.info("no handler, silent")
    handle Log with Console {
        Log.info("direct")
        helper()
        handle Log with Quiet {
            Log.info("quiet, silent")
            let v: i32 = Log.metric("quiet has no metric, silent", 1)
        }
        Log.info("restored")
    }
    return 0
}
"""
    c = flow_to_c(parse_flow_code(code))
    c_file = tmp_path / "zc.c"
    c_file.write_text(c)
    binary = tmp_path / "zc"
    subprocess.run(
        ["clang", "-O2", "-o", str(binary), str(c_file)],
        check=True,
        capture_output=True,
    )
    result = subprocess.run([str(binary)], check=True, capture_output=True, text=True)
    assert result.stdout == (
        "[console] direct\n"
        "[console] helper sees installed handler\n"
        "[console] restored\n"
    )
