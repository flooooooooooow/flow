#!/usr/bin/env bash
# Smoke-test the built wiki shell in a real browser.
#
# Checks the things that are easy to break silently in a client-rendered docs
# site: console errors, syntax highlighting, callouts, code copy buttons, TOC
# scroll-spy, and contrast of the hero call-to-action. Prints "All wiki
# checks passed", or FAIL and one line per failed check and exits 1.
#
# Needs the built wiki served at http://localhost:8899/ (FLOW_WIKI_BASE
# overrides it) and a Chrome or Chromium (CHROME overrides the search):
#
#   ./scripts/build_wiki.sh
#   ./scripts/wiki_serve.sh build/wiki 8899 &
#   ./scripts/wiki_verify.sh
#
# The checker is the Flow program in scripts/tools/wiki_browser. It drives
# headless Chrome over the DevTools Protocol.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
# shellcheck source=scripts/tools/wiki_browser/env.sh
# shellcheck disable=SC1091 # shared env, checked on its own
source "$ROOT/scripts/tools/wiki_browser/env.sh"
wiki_browser_check verify
