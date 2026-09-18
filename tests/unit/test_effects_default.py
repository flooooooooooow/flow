"""Stable 1.0 default for unhandled effects (issue #563).

Normal compilation performs effect-row coverage checking. An unhandled effect
is a compile error, and `--permissive-effects` restores the legacy soft path
that returns zero defaults.
"""

import os
import subprocess
import sys
import tempfile

SRC_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "src")

UNHANDLED = """\
effect Log {
    info(msg: string) -> void,
}

function main() -> i32 {
    Log.info("no handler")
    return 0
}
"""


def _transpile(source, *extra):
    with tempfile.NamedTemporaryFile("w", suffix=".flow", delete=False) as f:
        f.write(source)
        path = f.name
    out_c = path + ".c"
    env = dict(os.environ)
    env["PYTHONPATH"] = SRC_DIR + os.pathsep + env.get("PYTHONPATH", "")
    try:
        return subprocess.run(
            [sys.executable, "-m", "flow.transpiler", path, "--c", "-o", out_c, *extra],
            capture_output=True, text=True, env=env,
        )
    finally:
        for p in (path, out_c):
            try:
                os.unlink(p)
            except OSError:
                pass


def test_unhandled_effect_is_an_error_by_default():
    result = _transpile(UNHANDLED)
    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert "Unhandled effect 'Log.info'" in combined
    assert "--permissive-effects" in combined


def test_permissive_effects_allows_unhandled():
    result = _transpile(UNHANDLED, "--permissive-effects")
    assert result.returncode == 0, result.stdout + result.stderr


def test_strict_effects_flag_is_a_no_op_alias():
    # `--strict-effects` now names the default rather than opting into it.
    result = _transpile(UNHANDLED, "--strict-effects")
    assert result.returncode != 0
    assert "Unhandled effect 'Log.info'" in (result.stdout + result.stderr)
