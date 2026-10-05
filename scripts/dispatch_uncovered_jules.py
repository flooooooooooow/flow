#!/usr/bin/env python3
"""Open a Jules session for every open issue that does not already have one.

The older dispatchers read `jules_sessions.json`, which drifts: sessions get
deleted server side and the file still lists them, so issues get skipped that
have no live session. This asks Jules what actually exists instead, and only
dispatches the difference.

Capacity is finite. A refused create is retried rather than dropped, and the
issue stays in the queue until it lands.
"""
import json
import re
import subprocess
import sys
import time

REPO = "flooooooooooow/flow"
STATE_PATH = "jules_dispatch_state.json"
RETRY_SECONDS = 45
MAX_CONSECUTIVE_REFUSALS = 40
# Sessions finish on their own schedule, so poll for a free slot slowly.
CAPACITY_WAIT_SECONDS = 300


def open_issues():
    out = subprocess.check_output(
        ["gh", "issue", "list", "--repo", REPO, "--state", "open",
         "--limit", "300", "--json", "number,title,body,labels"]
    )
    issues = json.loads(out)
    issues.sort(key=lambda i: i["number"])
    return issues


def covered_issue_numbers():
    """Issue numbers that already have a live Jules session for this repo."""
    out = subprocess.run(["jules", "remote", "list", "--session"],
                         capture_output=True, text=True, timeout=180)
    covered = set()
    for line in out.stdout.splitlines():
        if REPO not in line:
            continue
        match = re.search(r"issue #(\d+)", line)
        if match:
            covered.add(int(match.group(1)))
    return covered


def load_state():
    try:
        with open(STATE_PATH) as handle:
            return json.load(handle)
    except Exception:
        return {"dispatched": {}, "failed": {}}


def save_state(state):
    with open(STATE_PATH, "w") as handle:
        json.dump(state, handle, indent=2, sort_keys=True)


def task_text(issue):
    labels = ", ".join(l["name"] for l in issue.get("labels", [])) or "None"
    return f"""Work on issue #{issue['number']}: {issue['title']}

Labels: {labels}

## Issue
{issue.get('body') or '(no description)'}

## How this repository expects work to be done
- Follow Flow's own idioms. Read neighbouring code before adding a pattern.
- Anything under compiler/src changes the self-hosted compiler. The generated
  bootstrap C must be regenerated so it matches, and the three self-host
  scripts have to stay green: bootstrap_from_c.sh, selfcompile_audit.sh and
  roundtrip.sh.
- Run the suites that cover what you touched. `python3 -m pytest tests/unit`
  for the Python host, `./flow test --tier2 --strict` for the language.
- A test that cannot fail proves nothing. Where you add one, check it fails
  without your change.
- If the issue turns out to be already fixed, say so and show what proves it
  rather than inventing a change.
"""


def create_session(issue):
    proc = subprocess.Popen(
        ["jules", "remote", "new", "--repo", REPO],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True,
    )
    try:
        stdout, stderr = proc.communicate(input=task_text(issue), timeout=180)
    except subprocess.TimeoutExpired:
        proc.kill()
        return None, "timeout"
    session = re.search(r"ID:\s*(\d+)", stdout)
    url = re.search(r"URL:\s*(https://\S+)", stdout)
    if session:
        return session.group(1), url.group(1) if url else ""
    return None, (stderr or stdout).strip()[:200]


def main():
    state = load_state()
    covered = covered_issue_numbers()
    already = set(int(n) for n in state["dispatched"])
    queue = [i for i in open_issues()
             if i["number"] not in covered and i["number"] not in already]

    print(f"{len(covered)} issues already have a live session.", flush=True)
    print(f"{len(queue)} to dispatch.", flush=True)

    refusals = 0
    while queue:
        issue = queue[0]
        number = issue["number"]
        session, detail = create_session(issue)
        if session:
            state["dispatched"][str(number)] = {
                "issue": number, "title": issue["title"],
                "session": session, "url": detail,
            }
            save_state(state)
            queue.pop(0)
            refusals = 0
            print(f"  #{number} -> session {session}  ({len(queue)} left)", flush=True)
            time.sleep(3)
            continue

        # A capacity refusal says nothing about this issue, so it must not
        # count against it. Giving up here would walk the whole queue marking
        # every issue failed against the same full account. Wait instead: a
        # slot opens when a session finishes.
        if "all sessions failed to create" in detail or "quota" in detail.lower():
            print(f"  at capacity, holding on #{number}; retry in "
                  f"{CAPACITY_WAIT_SECONDS}s", flush=True)
            time.sleep(CAPACITY_WAIT_SECONDS)
            continue

        refusals += 1
        if refusals >= MAX_CONSECUTIVE_REFUSALS:
            state["failed"][str(number)] = detail
            save_state(state)
            print(f"  #{number} giving up after {refusals} refusals: {detail}",
                  flush=True)
            queue.pop(0)
            refusals = 0
            continue
        print(f"  #{number} refused ({detail}); retry {refusals} in "
              f"{RETRY_SECONDS}s", flush=True)
        time.sleep(RETRY_SECONDS)

    print(f"Done. {len(state['dispatched'])} dispatched, "
          f"{len(state['failed'])} gave up.", flush=True)


if __name__ == "__main__":
    sys.exit(main())
