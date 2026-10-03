"""
Unit tests for FLOW vgpu compatibility test runner (src/flow/vgpu_runner.py).
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from flow.vgpu_runner import (
    VGPURunner,
    compare_numerical,
    compare_rgba8,
    evaluate_fsl_gradient_cpu,
    load_manifest,
    main,
)


def test_load_manifest_valid(tmp_path):
    manifest_data = {
        "suite": "vgpu",
        "cases": [
            {
                "id": "test_case",
                "source": "examples/gpu/vgpu/gradient.flow",
                "comparison": {"mode": "exact-rgba8"},
                "backends": ["webgpu"],
            }
        ],
    }
    manifest_file = tmp_path / "manifest.json"
    manifest_file.write_text(json.dumps(manifest_data), encoding="utf-8")

    loaded = load_manifest(manifest_file)
    assert loaded["suite"] == "vgpu"
    assert len(loaded["cases"]) == 1


def test_compare_rgba8_exact_and_tolerance():
    expected = b"\x01\x02\x03\xff\x04\x05\x06\xff"
    actual_exact = b"\x01\x02\x03\xff\x04\x05\x06\xff"
    res_exact = compare_rgba8(actual_exact, expected, tolerance=0)
    assert res_exact["exact"] is True
    assert res_exact["differing_bytes"] == 0
    assert res_exact["max_channel_error"] == 0

    actual_tol = b"\x01\x03\x03\xff\x04\x05\x08\xff"
    res_tol = compare_rgba8(actual_tol, expected, tolerance=2)
    assert res_tol["exact"] is False
    assert res_tol["within_tolerance"] is True
    assert res_tol["differing_bytes"] == 2
    assert res_tol["max_channel_error"] == 2

    res_fail = compare_rgba8(actual_tol, expected, tolerance=1)
    assert res_fail["within_tolerance"] is False


def test_compare_numerical():
    expected = [1.0, 2.0, 3.0]
    actual_exact = [1.0, 2.0, 3.0]
    res_exact = compare_numerical(actual_exact, expected, tolerance=1e-4)
    assert res_exact["exact"] is True
    assert res_exact["within_tolerance"] is True
    assert res_exact["max_abs_error"] == 0.0

    actual_near = [1.00005, 2.00002, 2.99998]
    res_near = compare_numerical(actual_near, expected, tolerance=1e-4)
    assert res_near["within_tolerance"] is True
    assert res_near["max_abs_error"] <= 1e-4

    res_far = compare_numerical(actual_near, expected, tolerance=1e-6)
    assert res_far["within_tolerance"] is False


def test_evaluate_fsl_gradient_cpu_dimensions():
    w, h = 40, 20
    rendered = evaluate_fsl_gradient_cpu(w, h)
    assert len(rendered) == w * h * 4


def test_vgpu_runner_gradient_case_exact():
    runner = VGPURunner("examples/gpu/vgpu/manifest.json")
    results, failed = runner.run_suite(requested_backends=["webgpu"])
    assert not failed

    gradient_res = next((r for r in results if r.case_id == "gradient" and r.backend == "webgpu"), None)
    assert gradient_res is not None
    assert gradient_res.status == "EXACT"
    assert gradient_res.differing_bytes == 0
    assert gradient_res.max_error == 0.0


def test_vgpu_runner_all_backends_summary(capsys):
    runner = VGPURunner("examples/gpu/vgpu/manifest.json")
    results, failed = runner.run_suite(all_backends=True)
    assert not failed
    assert len(results) > 0

    runner.print_summary(results)
    captured = capsys.readouterr().out
    assert "vgpu Conformance Suite" in captured
    assert "EXACT" in captured
    assert "NUMERICAL" in captured


def test_vgpu_runner_missing_source_fails(tmp_path):
    manifest_data = {
        "suite": "vgpu",
        "cases": [
            {
                "id": "missing_source",
                "source": str(tmp_path / "nonexistent.flow"),
                "comparison": {"mode": "exact-rgba8"},
                "backends": ["webgpu"],
            }
        ],
    }
    manifest_file = tmp_path / "manifest.json"
    manifest_file.write_text(json.dumps(manifest_data), encoding="utf-8")

    runner = VGPURunner(manifest_file)
    results, failed = runner.run_suite(all_backends=True)
    assert failed is True
    assert results[0].status == "FAIL"


def test_vgpu_runner_main_cli(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["vgpu_runner", "--manifest", "examples/gpu/vgpu/manifest.json", "--all-backends"],
    )
    exit_code = main()
    assert exit_code == 0
