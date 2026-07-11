#!/usr/bin/env bash
# Build and deploy the Flow wiki to the VPS.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD="$ROOT/build/wiki"
REMOTE="${FLOW_WIKI_REMOTE:-root@93.127.202.196:/var/www/transpile/}"

if command -v sshpass &>/dev/null && python3 -c "import sys; sys.path.insert(0,'/Users/abhishekshivakumar/website/aissh'); from ssh_client import get_config; exit(0 if get_config().get('password') else 1)" 2>/dev/null; then
    exec python3 "$ROOT/scripts/deploy_wiki.py"
fi

echo "Building wiki…"
python3 "$ROOT/scripts/build_wiki.py"

echo "Deploying to $REMOTE …"
rsync -avz --delete --exclude '.DS_Store' "$BUILD/" "$REMOTE"

echo "Done. Live at https://abhishek-shivakumar.com/transpile/"