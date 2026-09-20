"""Rosetta Code task solutions stay compilable (issue #896).

Each `examples/rosetta/*.flow` is a canonical Rosetta task written in Flow.
Every one must parse and generate C through the frontend, so the published
examples do not rot as the compiler changes. The parse + `flow_to_c` path is
fast, so it runs for every example. The full compile-and-run check lives in the
example driver and is exercised by hand; see examples/rosetta/README.md.
"""

import glob
import os

import pytest

import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c

ROSETTA_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "examples", "rosetta"
)

EXAMPLES = sorted(glob.glob(os.path.join(ROSETTA_DIR, "*.flow")))


def test_rosetta_examples_exist():
    # Guard against an empty glob silently passing every parametrised test.
    assert len(EXAMPLES) >= 8, EXAMPLES


@pytest.mark.parametrize("path", EXAMPLES, ids=[os.path.basename(p) for p in EXAMPLES])
def test_rosetta_example_generates_c(path):
    with open(path) as f:
        source = f.read()
    c = flow_to_c(parse_flow_code(source))
    assert "main(" in c, path
