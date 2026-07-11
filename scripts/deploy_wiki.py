#!/usr/bin/env python3
"""Build and deploy the Flow wiki to the VPS."""

from __future__ import annotations

import os
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build" / "wiki"
AISSH = Path("/Users/abhishekshivakumar/website/aissh")
REMOTE_DIR = "/var/www/transpile"


def main() -> int:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_wiki.py")], check=True)

    if not BUILD.exists():
        print("Build directory missing", file=sys.stderr)
        return 1

    sys.path.insert(0, str(AISSH))
    from ssh_client import get_config  # noqa: E402

    config = get_config()
    host = os.environ.get("WIKI_SSH_HOST") or config["host"]
    user = os.environ.get("WIKI_SSH_USER") or config["user"]
    password = (
        os.environ.get("WIKI_SSH_PASSWORD")
        or os.environ.get("AISSH_HOSTINGER_PWD")
        or config["password"]
    )

    if not password:
        print("No SSH password configured — set SSH_PASSWORD or .ssh_config", file=sys.stderr)
        return 1

    env = {**os.environ, "SSHPASS": password}
    ssh_opts = [
        "-o", "PreferredAuthentications=password",
        "-o", "PubkeyAuthentication=no",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ConnectTimeout=30",
    ]
    ssh_base = ["sshpass", "-e", "ssh", *ssh_opts, f"{user}@{host}"]

    tarball = ROOT / "build" / "flow-wiki-deploy.tgz"
    print(f"Packaging wiki ({_dir_size(BUILD):.1f} MB) → {tarball}")
    with tarfile.open(tarball, "w:gz") as tar:
        tar.add(BUILD, arcname=".")

    print(f"Testing SSH to {host}…")
    try:
        ping = subprocess.run(
            ssh_base + ["echo connected"],
            env=env,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except subprocess.TimeoutExpired:
        ping = None

    if ping is None or ping.returncode != 0:
        err = ping.stderr.strip() if ping else "timeout after 20s"
        print(f"\n❌ SSH unreachable: {err}", file=sys.stderr)
        _print_manual_deploy(tarball, user, host)
        return 1

    print(f"Uploading to {host}:{REMOTE_DIR} …")
    scp_cmd = [
        "sshpass", "-e", "scp",
        *ssh_opts,
        str(tarball),
        f"{user}@{host}:/tmp/flow-wiki.tgz",
    ]
    try:
        if subprocess.run(scp_cmd, env=env, timeout=120).returncode != 0:
            return 1
    except subprocess.TimeoutExpired:
        print("❌ Upload timed out after 120s", file=sys.stderr)
        return 1

    extract_cmd = (
        f"mkdir -p {REMOTE_DIR} && "
        f"find {REMOTE_DIR} -mindepth 1 -delete && "
        f"tar xzf /tmp/flow-wiki.tgz -C {REMOTE_DIR} && "
        f"rm /tmp/flow-wiki.tgz && "
        f"echo deployed && wc -c {REMOTE_DIR}/index.html"
    )
    try:
        result = subprocess.run(
            ssh_base + [extract_cmd],
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        print("❌ Remote extract timed out", file=sys.stderr)
        return 1

    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return result.returncode

    print("✅ Live → https://abhishek-shivakumar.com/transpile/")
    return 0


def _dir_size(path: Path) -> float:
    total = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    return total / (1024 * 1024)


def _print_manual_deploy(tarball: Path, user: str, host: str) -> None:
    print("\nManual deploy (run from your terminal):")
    print(f"  scp {tarball} {user}@{host}:/tmp/flow-wiki.tgz")
    print(
        f"  ssh {user}@{host} "
        f"'mkdir -p {REMOTE_DIR} && find {REMOTE_DIR} -mindepth 1 -delete "
        f"&& tar xzf /tmp/flow-wiki.tgz -C {REMOTE_DIR} && rm /tmp/flow-wiki.tgz'"
    )
    print("\nThen open https://abhishek-shivakumar.com/transpile/")


if __name__ == "__main__":
    raise SystemExit(main())