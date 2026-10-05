"""Every program in the Flow Way gallery runs in the browser interpreter.

The gallery teaches idioms, and a reader should be able to press Run on each
one. Four of the five could not: effects, a pipeline fork into a struct,
enums with `choose`, and a flow block were all outside the subset.

Each case is checked against the native compiler's own output where the
program prints something, because agreeing with `./flow run` is the only
standard that matters for an interpreter that exists to preview it.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "site" / "flow-compile.js"
GALLERY = ROOT / "examples" / "flow_way" / "README.md"

pytestmark = pytest.mark.skipif(
    shutil.which("node") is None, reason="the browser interpreter is JavaScript"
)


def run_in_browser_engine(source: str) -> dict:
    """Execute one program through site/flow-compile.js under node."""
    driver = (
        "const fs=require('fs'); global.window={};\n"
        f"eval(fs.readFileSync({json.dumps(str(ENGINE))},'utf8'));\n"
        "const src=fs.readFileSync(process.argv[2],'utf8');\n"
        "const r=window.FlowCompile.run(src);\n"
        "process.stdout.write(JSON.stringify({ok:r.ok,output:r.output,"
        "exit:r.exitCode,detail:r.construct||String(r.error||'')}));\n"
    )
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        js, flow = Path(td) / "d.js", Path(td) / "p.flow"
        js.write_text(driver)
        flow.write_text(source)
        proc = subprocess.run(
            ["node", str(js), str(flow)], capture_output=True, text=True, timeout=90
        )
    assert proc.returncode == 0, proc.stderr[-500:]
    return json.loads(proc.stdout)


def gallery_programs() -> list[str]:
    """Use the repository's own extractor.

    A regex over fences mispairs a closing fence with the next opening one,
    which is why scripts/docs_blocks.py exists.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    from docs_blocks import iter_blocks

    return [
        b.code
        for b in iter_blocks(GALLERY.read_text(), str(GALLERY))
        if b.lang == "flow" and re.search(r"function\s+main\s*\(", b.code)
    ]


def test_the_gallery_has_the_programs_this_asserts_about():
    """A guard: if the gallery grows, this file should see the new ones."""
    assert len(gallery_programs()) == 5


@pytest.mark.parametrize("index", range(5))
def test_every_gallery_program_runs_and_exits_zero(index):
    """Each gallery program returns 1 on a failed assertion, so exit 0 is the
    program checking itself, not merely reaching the end."""
    program = gallery_programs()[index]
    result = run_in_browser_engine(program)
    assert result["ok"], result["detail"][:200]
    assert result["exit"] == 0, result["output"]


def test_a_flow_block_integrates_the_same_as_the_native_compiler():
    """20000 Euler steps with an every-block firing 200 times.

    A stepper that is close is not the same as one that agrees, so this
    compares the printed state against `./flow run` rather than a tolerance.
    """
    program = """
function bang(temp: f64, heater: f64, low: f64, high: f64) -> f64 {
    if temp < low { return 1.0 }
    if temp > high { return 0.0 }
    return heater
}

flow Thermostat {
    state temperature : f64 = 12.0
    state heater      : f64 = 1.0
    param ambient     : f64 = 8.0
    param leak        : f64 = 0.12
    param power       : f64 = 1.8
    param low         : f64 = 19.5
    param high        : f64 = 20.5

    solver { dt 1 ms  method euler }

    temperature evolves as (ambient - temperature) * leak + heater * power

    every 100 ms {
        heater becomes bang(temperature, heater, low, high)
    }
}

function main() -> i32 {
    let mut room: Thermostat = Thermostat_new()
    let mut i: i32 = 0
    while i < 20000 {
        Thermostat_step(&room, 0.001)
        i = i + 1
    }
    printf("temp=%.3f heater=%.1f\\n", room.temperature, room.heater)
    return 0
}
"""
    result = run_in_browser_engine(program)
    assert result["ok"], result["detail"][:200]
    assert result["output"].strip() == "temp=20.414 heater=1.0", result["output"]


def test_an_unimplemented_solver_method_says_which_one():
    result = run_in_browser_engine("""
flow F {
    state x : f64 = 0.0
    solver { dt 1 ms  method rk4 }
    x evolves as 1.0
}
function main() -> i32 { return 0 }
""")
    assert not result["ok"]
    assert "rk4" in result["detail"], result["detail"]


def test_a_top_level_const_is_available():
    """Constants were parsed and then never installed as globals."""
    result = run_in_browser_engine(
        'const LIMIT: i32 = 7\nfunction main() -> i32 { printf("%d\\n", LIMIT * 2) return 0 }'
    )
    assert result["ok"], result["detail"][:200]
    assert result["output"].strip() == "14"
