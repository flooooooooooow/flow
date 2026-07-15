"""Proof kernel compilation."""

import json
import os

from flow.proof_kernel import compile_file_kernel, write_kernel_json


FIXTURE = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "examples",
    "verify",
    "math",
    "derived",
    "Nat-plus-zero-right.flow",
)


class TestProofKernel:
    def test_compile_kernel_has_edges(self):
        k = compile_file_kernel(FIXTURE, instantiation={"n": "0"})
        assert "natural numbers" in k.claim_display
        assert len(k.nodes) >= 5
        assert len(k.edges) >= 3
        assert any(e[0] < e[1] for e in k.edges)

    def test_write_kernel_json(self, tmp_path):
        import shutil

        dst = tmp_path / "Nat-plus-zero-right.flow"
        shutil.copy(FIXTURE, dst)
        path = write_kernel_json(str(dst), instantiation={"n": "0"})
        data = json.loads(open(path).read())
        assert "nodes" in data
        assert data["instantiation"]["n"] == "0"