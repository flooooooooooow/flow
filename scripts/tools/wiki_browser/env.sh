# Sourced by scripts/wiki_contrast.sh, scripts/wiki_verify.sh and
# scripts/wiki_serve.sh with ROOT set. Builds the Flow tool and defines
# wiki_browser_check, which runs a browser check and makes sure the Chrome
# it started is gone afterwards, even when the check is interrupted.

WIKI_BROWSER_BIN="$ROOT/$("$ROOT/scripts/tools/build_tool.sh" wiki_browser)"
export FLOW_REPO_ROOT="$ROOT"

# The tool writes the Chrome PID and profile directory it started to
# FLOW_WIKI_BROWSER_STATE and clears the file after a clean shutdown. If the
# check dies first, this kills that one PID and removes that one directory.
wiki_browser_cleanup() {
  local state="$1" pid="" dir=""
  if [[ -s "$state" ]]; then
    { read -r pid; read -r dir; } < "$state" || true
    if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      sleep 1
      kill -0 "$pid" 2>/dev/null && kill -9 "$pid" 2>/dev/null || true
    fi
    case "$dir" in
      */flow-wiki-browser.*) rm -rf "$dir" ;;
    esac
  fi
  rm -f "$state"
}

wiki_browser_check() {
  local mode="$1" rc=0
  WIKI_BROWSER_STATE="$(mktemp "${TMPDIR:-/tmp}/flow-wiki-browser-state.XXXXXX")"
  export FLOW_WIKI_BROWSER_STATE="$WIKI_BROWSER_STATE"
  trap 'wiki_browser_cleanup "$WIKI_BROWSER_STATE"' EXIT
  trap 'exit 130' INT
  trap 'exit 143' TERM
  "$WIKI_BROWSER_BIN" "$mode" || rc=$?
  return "$rc"
}
