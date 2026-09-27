from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DISPATCH = ROOT / "scripts" / "dispatch_uncovered_jules.sh"


def _fake_cli_dir(tmp_path: Path) -> Path:
    bindir = tmp_path / "bin"
    bindir.mkdir()

    gh = bindir / "gh"
    gh.write_text(
        """#!/bin/sh
set -eu
if [ "$1 $2" = "pr list" ]; then
    printf '%s\n' "${FAKE_PRS_JSON:-[]}"
    exit 0
fi
if [ "$1 $2" = "issue list" ]; then
    printf '%s\n' "${FAKE_ISSUES_JSON:-[]}"
    exit 0
fi
if [ "$1 $2" = "issue comment" ]; then
    printf '%s\n' "$*" >> "${FAKE_CLAIM_MARKER}"
    exit 0
fi
echo "unexpected gh invocation: $*" >&2
exit 2
"""
    )
    gh.chmod(0o755)

    jules = bindir / "jules"
    jules.write_text(
        """#!/bin/sh
set -eu
if [ "$1 $2 $3" = "remote list --session" ]; then
    printf '%b' "${FAKE_JULES_LIST:-}"
    exit 0
fi
if [ "$1 $2" = "remote new" ]; then
    cat >/dev/null
    : > "${FAKE_NEW_MARKER}"
    printf 'ID: 12345\nURL: https://jules.example/session/12345\n'
    exit 0
fi
echo "unexpected jules invocation: $*" >&2
exit 2
"""
    )
    jules.chmod(0o755)
    return bindir


def _run(tmp_path: Path, *, issues, prs, sessions="", extra_env=None):
    bindir = _fake_cli_dir(tmp_path)
    new_marker = tmp_path / "new-session"
    claim_marker = tmp_path / "claim"
    env = {
        **os.environ,
        "PATH": f"{bindir}:{os.environ['PATH']}",
        "FAKE_ISSUES_JSON": json.dumps(issues),
        "FAKE_PRS_JSON": json.dumps(prs),
        "FAKE_JULES_LIST": sessions,
        "FAKE_NEW_MARKER": str(new_marker),
        "FAKE_CLAIM_MARKER": str(claim_marker),
        "JULES_DISPATCH_NO_SLEEP": "1",
        "JULES_MAX_ACTIVE": "8",
        "JULES_MAX_AGENT_PRS": "12",
    }
    if extra_env:
        env.update(extra_env)
    proc = subprocess.run(
        [str(DISPATCH)],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
        timeout=120,
    )
    decision_path = tmp_path / "jules_dispatch_decisions.jsonl"
    decisions = decision_path.read_text() if decision_path.exists() else ""
    return proc, new_marker, claim_marker, decisions


def _issue(number: int, title: str = "Fix compiler regression"):
    return {"number": number, "title": title, "body": "repro", "labels": []}


def _pr(number: int, title: str, body: str, head: str = "jules/work"):
    return {
        "number": number,
        "title": title,
        "body": body,
        "headRefName": head,
        "isDraft": False,
    }


def test_open_agent_pr_limit_applies_backpressure(tmp_path):
    proc, new_marker, _, decisions = _run(
        tmp_path,
        issues=[_issue(42)],
        prs=[_pr(7, "Other work", "Created automatically by Jules https://jules.google.com/task/7")],
        extra_env={"JULES_MAX_AGENT_PRS": "1"},
    )

    assert proc.returncode == 0, proc.stderr
    assert "Backpressure: agent PR WIP limit reached" in proc.stdout
    assert not new_marker.exists()
    assert '"decision":"backpressure"' in decisions


def test_open_pr_for_issue_prevents_duplicate_dispatch(tmp_path):
    proc, new_marker, _, decisions = _run(
        tmp_path,
        issues=[_issue(42)],
        prs=[_pr(7, "Fix compiler regression", "Closes #42", head="fix/42")],
    )

    assert proc.returncode == 0, proc.stderr
    assert not new_marker.exists()
    assert '"decision":"deferred"' in decisions
    assert "overlaps open PR #7" in decisions


def test_stale_local_dispatch_state_is_not_a_permanent_claim(tmp_path):
    (tmp_path / "jules_dispatch_state.json").write_text(
        json.dumps(
            {
                "dispatched": {
                    "42": {
                        "issue": 42,
                        "title": "Fix compiler regression",
                        "session": "old",
                        "url": "",
                    }
                },
                "failed": {},
            }
        )
    )

    proc, new_marker, claim_marker, decisions = _run(
        tmp_path,
        issues=[_issue(42)],
        prs=[],
    )

    assert proc.returncode == 0, proc.stderr
    assert new_marker.exists()
    assert claim_marker.exists()
    assert '"decision":"dispatched"' in decisions


def test_live_session_limit_stops_new_work(tmp_path):
    proc, new_marker, _, decisions = _run(
        tmp_path,
        issues=[_issue(42)],
        prs=[],
        sessions="flooooooooooow/flow issue #99 running\n",
        extra_env={"JULES_MAX_ACTIVE": "1"},
    )

    assert proc.returncode == 0, proc.stderr
    assert "Backpressure: active Jules session limit reached" in proc.stdout
    assert not new_marker.exists()
    assert '"decision":"backpressure"' in decisions
