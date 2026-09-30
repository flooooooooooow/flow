#!/usr/bin/env bash
# Audit rendered text contrast across the wiki and tutorials shells.
#
# Walks every visible text-bearing element, resolves its effective background
# by compositing ancestor backgrounds, and reports anything under the WCAG AA
# bar. Exits 1 when any element fails.
#
# Needs the built wiki served at http://localhost:8899/ (FLOW_WIKI_BASE
# overrides it) and a Chrome or Chromium (CHROME overrides the search):
#
#   ./scripts/build_wiki.sh
#   ./scripts/wiki_serve.sh build/wiki 8899 &
#   ./scripts/wiki_contrast.sh
#
# The checker is the Flow program in scripts/tools/wiki_browser. It drives
# headless Chrome over the DevTools Protocol; the audit script is
# scripts/tools/wiki_browser/contrast_audit.js.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
# shellcheck source=scripts/tools/wiki_browser/env.sh
# shellcheck disable=SC1091 # shared env, checked on its own
source "$ROOT/scripts/tools/wiki_browser/env.sh"
wiki_browser_check contrast
