#!/usr/bin/env bash
# Build the Flow wiki locally. VPS deploy is disabled; docs ship via GitHub
# Pages.
#
# CI: .github/workflows/wiki.yml publishes to GitHub Pages at
#   https://flooooooooooow.github.io/flow/
#
# The legacy VPS deploy remains behind FLOW_WIKI_VPS=1 for emergencies only.
# It packs build/wiki into a tarball, uploads it with scp and unpacks it into
# /var/www/transpile on the host.
#
#   WIKI_SSH_HOST       host (default 93.127.202.196)
#   WIKI_SSH_USER       user (default root)
#   WIKI_SSH_PASSWORD   password; AISSH_HOSTINGER_PWD is read too. With a
#                       password the upload needs sshpass. Without one, ssh
#                       uses your keys.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD="$ROOT/build/wiki"
REMOTE_DIR="/var/www/transpile"
PAGES_URL="https://flooooooooooow.github.io/flow/"

vps="$(printf '%s' "${FLOW_WIKI_VPS:-}" | tr -d '[:space:]')"
case "$vps" in
  1 | true | yes) vps=1 ;;
  *) vps=0 ;;
esac

if [[ "$vps" -eq 1 ]]; then
  host="${WIKI_SSH_HOST:-93.127.202.196}"
  user="${WIKI_SSH_USER:-root}"
  password="${WIKI_SSH_PASSWORD:-${AISSH_HOSTINGER_PWD:-}}"
  # Check the upload tools before spending time on the build.
  if [[ -n "$password" ]] && ! command -v sshpass >/dev/null 2>&1; then
    echo "A password is set (WIKI_SSH_PASSWORD or AISSH_HOSTINGER_PWD) but sshpass is not installed." >&2
    echo "Install sshpass, or unset the password to use SSH key authentication." >&2
    exit 1
  fi
fi

bash "$ROOT/scripts/build_wiki.sh"

if [[ ! -d "$BUILD" ]]; then
  echo "Build directory missing" >&2
  exit 1
fi

if [[ "$vps" -ne 1 ]]; then
  echo "Wiki built → $BUILD"
  echo "VPS deploy disabled. Docs publish via GitHub Pages:"
  echo "  $PAGES_URL"
  echo "Preview locally:  scripts/wiki_serve.sh build/wiki 8777"
  echo "Emergency VPS:    FLOW_WIKI_VPS=1 scripts/deploy_wiki.sh"
  exit 0
fi

ssh_opts=(
  -o StrictHostKeyChecking=no
  -o UserKnownHostsFile=/dev/null
  -o ConnectTimeout=30
)
if [[ -n "$password" ]]; then
  export SSHPASS="$password"
  ssh_opts+=(-o PreferredAuthentications=password -o PubkeyAuthentication=no)
  ssh_cmd=(sshpass -e ssh "${ssh_opts[@]}")
  scp_cmd=(sshpass -e scp "${ssh_opts[@]}")
else
  ssh_opts+=(-o BatchMode=yes)
  ssh_cmd=(ssh "${ssh_opts[@]}")
  scp_cmd=(scp "${ssh_opts[@]}")
fi

manual_deploy() {
  echo ""
  echo "Manual deploy (run from your terminal):"
  echo "  scp $tarball $user@$host:/tmp/flow-wiki.tgz"
  echo "  ssh $user@$host 'mkdir -p $REMOTE_DIR && find $REMOTE_DIR -mindepth 1 -delete && tar xzf /tmp/flow-wiki.tgz -C $REMOTE_DIR && rm /tmp/flow-wiki.tgz'"
  echo ""
  echo "Then open https://abhishek-shivakumar.com/transpile/"
}

tarball="$ROOT/build/flow-wiki-deploy.tgz"
size_mb="$(find "$BUILD" -type f -exec wc -c {} + | awk '$2 != "total" { s += $1 } END { printf "%.1f", s / 1048576 }')"
if [[ -f "$BUILD/pagefind/pagefind.js" ]]; then
  pf_note=" incl. Pagefind"
else
  pf_note=" (no Pagefind, local search only)"
fi
echo "Packaging wiki (${size_mb} MB${pf_note}) → $tarball"
tar czf "$tarball" -C "$BUILD" .

echo "Testing SSH to ${host}…"
ping_err=""
if ! ping_err="$("${ssh_cmd[@]}" "$user@$host" "echo connected" 2>&1 >/dev/null)"; then
  echo "" >&2
  echo "❌ SSH unreachable: ${ping_err:-ssh failed}" >&2
  manual_deploy
  exit 1
fi

echo "Uploading to $host:$REMOTE_DIR …"
if ! "${scp_cmd[@]}" "$tarball" "$user@$host:/tmp/flow-wiki.tgz"; then
  exit 1
fi

extract="mkdir -p $REMOTE_DIR && find $REMOTE_DIR -mindepth 1 -delete && tar xzf /tmp/flow-wiki.tgz -C $REMOTE_DIR && rm /tmp/flow-wiki.tgz && echo deployed && wc -c $REMOTE_DIR/index.html"
rc=0
"${ssh_cmd[@]}" "$user@$host" "$extract" || rc=$?
if [[ "$rc" -ne 0 ]]; then
  exit "$rc"
fi

echo "✅ Live → https://abhishek-shivakumar.com/flow/"
echo "   also → https://abhishek-shivakumar.com/transpile/"
