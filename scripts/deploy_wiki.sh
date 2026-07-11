#!/usr/bin/env bash
# Build and deploy the Flow wiki to the VPS.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD="$ROOT/build/wiki"
REMOTE="${FLOW_WIKI_REMOTE:-root@93.127.202.196:/var/www/transpile/}"

if [ -n "${AISSH_HOSTINGER_PWD:-}" ] || python3 -c "import sys; sys.path.insert(0,'/Users/abhishekshivakumar/website/aissh'); from ssh_client import get_config; exit(0 if get_config().get('password') else 1)" 2>/dev/null; then
    exec python3 "$ROOT/scripts/deploy_wiki.py"
fi

echo "ERROR: No SSH credentials. Set AISSH_HOSTINGER_PWD or configure aissh." >&2
echo "  export AISSH_HOSTINGER_PWD='…'" >&2
echo "  ./scripts/deploy_wiki.sh" >&2
exit 1