import pytest
import os
import tempfile
import json
import math
from pathlib import Path

from benchmarks.run_benchmarks import evaluate_regression, run_cmd, get_system_info, get_percentile

def test_regression_policy_faster_is_pass():
    old = {
        "os": "Linux",
        "cpu": "x86_64",
        "semantic_parity_status": "verified",
        "flow_metrics": {"median": 10.0}
    }
    new = {
        "os": "Linux",
        "cpu": "x86_64",
        "semantic_parity_status": "verified",
        "flow_metrics": {"median": 8.0}
    }
    assert evaluate_regression(old, new) == "pass"

def test_regression_policy_within_margin_is_pass():
    old = {
        "os": "Linux",
        "cpu": "x86_64",
        "semantic_parity_status": "verified",
        "flow_metrics": {"median": 10.0}
    }
    new = {
        "os": "Linux",
        "cpu": "x86_64",
        "semantic_parity_status": "verified",
        "flow_metrics": {"median": 10.2} # 2% slower, within 5% margin
    }
    assert evaluate_regression(old, new) == "pass_within_margin"

def test_regression_policy_regression():
    old = {
        "os": "Linux",
        "cpu": "x86_64",
        "semantic_parity_status": "verified",
        "flow_metrics": {"median": 10.0}
    }
    new = {
        "os": "Linux",
        "cpu": "x86_64",
        "semantic_parity_status": "verified",
        "flow_metrics": {"median": 11.0} # 10% slower, outside 5% margin
    }
    assert evaluate_regression(old, new) == "regression"

def test_regression_policy_env_mismatch():
    old = {
        "os": "Linux",
        "cpu": "x86_64",
        "semantic_parity_status": "verified",
        "flow_metrics": {"median": 10.0}
    }
    new = {
        "os": "Darwin",
        "cpu": "arm64",
        "semantic_parity_status": "verified",
        "flow_metrics": {"median": 11.0} 
    }
    assert evaluate_regression(old, new) == "skipped_env_mismatch"

def test_regression_policy_unresolved_correctness():
    old = {
        "os": "Linux",
        "cpu": "x86_64",
        "semantic_parity_status": "verified",
        "flow_metrics": {"median": 10.0}
    }
    new = {
        "os": "Linux",
        "cpu": "x86_64",
        "semantic_parity_status": "unresolved",
        "flow_metrics": {"median": 8.0}
    }
    assert evaluate_regression(old, new) == "skipped_unresolved_correctness"
    
def test_get_percentile():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert get_percentile(data, 0.5) == 5.5
    assert math.isclose(get_percentile(data, 0.95), 9.55)
    
def test_get_system_info():
    info = get_system_info()
    assert "os" in info
    assert "cpu" in info
    assert "arch" in info
    assert "flow_version" in info
