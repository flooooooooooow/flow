#!/usr/bin/env bash
# Heading-id generation and the anchor half of the link checker
# (`./flow tool doc_links`).
source "$(dirname "$0")/lib.sh"

checker() { "$T_ROOT/flow" tool doc_links "$@"; }

# heading_slug follows GitHub, including where that looks odd.
check_slug() {
    local heading="$1" slug="$2"
    t_run checker --slug "$heading"
    [[ "$T_RC" -eq 0 ]] || { cat "$T_ERR"; return 1; }
    # The slug and one trailing newline, nothing else.
    a_file_is "$T_OUT" "$slug"$'\n'
}

# site/wiki.js must not collapse dash runs either.
#
# The two implementations are in different languages, so the only thing
# holding them together is that neither collapses. Pin the JS source.
check_the_published_wiki_slugger_agrees_with_this_one() {
    awk '
        !found { i = index($0, "function headingSlug"); if (!i) next; found = 1; $0 = substr($0, i) }
        /^}/ { exit }
        { print }
    ' site/wiki.js > "$T_TMP/body.js"
    [[ -s "$T_TMP/body.js" ]] || { echo "function headingSlug not found in site/wiki.js"; return 1; }
    if grep -qF '/-+/g' "$T_TMP/body.js"; then
        echo "site/wiki.js collapses runs of dashes again; that breaks every anchor into a heading containing punctuation"
        return 1
    fi
    grep -qF "replace(/\\s/g, '-')" "$T_TMP/body.js" || grep -qF 'replace(/\s/g, "-")' "$T_TMP/body.js" \
        || { echo "headingSlug no longer replaces each whitespace character with a dash"; return 1; }
}

# Anchors the checker finds in a page, one per line, into $T_TMP/anchors.
anchors_in() {
    t_run checker --anchors "$1"
    [[ "$T_RC" -eq 0 ]] || { cat "$T_ERR"; return 1; }
    cp "$T_OUT" "$T_TMP/anchors"
}

has_anchor() {
    a_true "anchor $1" grep -qxF -- "$1" "$T_TMP/anchors"
}

check_anchors_come_from_headings() {
    printf '# Title\n\n## A Section\n\ntext\n\n### Deep One\n' > "$T_TMP/p.md"
    anchors_in "$T_TMP/p.md"
    has_anchor title
    has_anchor a-section
    has_anchor deep-one
}

check_repeated_headings_are_numbered() {
    printf '## Notes\n\n## Notes\n\n## Notes\n' > "$T_TMP/p.md"
    anchors_in "$T_TMP/p.md"
    has_anchor notes
    has_anchor notes-1
    has_anchor notes-2
}

check_explicit_html_ids_count_as_anchors() {
    printf '# T\n\n<a id="hand-written"></a>\n' > "$T_TMP/p.md"
    anchors_in "$T_TMP/p.md"
    has_anchor hand-written
}

# The repository as it stands. One run of the checker serves both checks.
FULL_OUT="$T_WORK/full.out"
FULL_RC=0
checker > "$FULL_OUT" 2>&1 || FULL_RC=$?

# The whole point: no link points at a heading that is not there.
check_every_documented_anchor_resolves() {
    [[ "$FULL_RC" -eq 0 ]] || { cat "$FULL_OUT"; return 1; }
    a_file_contains "$FULL_OUT" "all relative links and fragments resolve"
}

# `#` used to sit in the external-skip list, so 55 anchors went unchecked.
check_same_page_anchors_are_actually_checked() {
    local n
    n="$(grep -oE 'checked [0-9]+ link fragment' "$FULL_OUT" | head -n 1 | grep -oE '[0-9]+' || true)"
    [[ -n "$n" && "$n" -gt 100 ]] || { cat "$FULL_OUT"; return 1; }
}

t_check "heading_slug_matches_github[Overview]" check_slug "Overview" "overview"
t_check "heading_slug_matches_github[1. Lexical Structure]" check_slug "1. Lexical Structure" "1-lexical-structure"
t_check "heading_slug_matches_github[3.6 Attributes]" check_slug "3.6 Attributes" "36-attributes"
t_check "heading_slug_matches_github[\`flow\` blocks]" check_slug "\`flow\` blocks" "flow-blocks"
t_check "heading_slug_matches_github[Types & Values]" check_slug "Types & Values" "types--values"
# A removed punctuation mark leaves the spaces either side, and GitHub turns
# each into its own dash. Collapsing them is what made 11 anchors resolve on
# GitHub and die on the published wiki.
t_check "runs_of_dashes_are_preserved[10. Domain / DSL Surfaces]" check_slug "10. Domain / DSL Surfaces" "10-domain--dsl-surfaces"
t_check "runs_of_dashes_are_preserved[4.4 Lambdas / Closures]" check_slug "4.4 Lambdas / Closures" "44-lambdas--closures"
t_check "runs_of_dashes_are_preserved[5.6 Concurrency (language + stdlib)]" check_slug "5.6 Concurrency (language + stdlib)" "56-concurrency-language--stdlib"
t_check the_published_wiki_slugger_agrees_with_this_one check_the_published_wiki_slugger_agrees_with_this_one
t_check anchors_come_from_headings check_anchors_come_from_headings
t_check repeated_headings_are_numbered check_repeated_headings_are_numbered
t_check explicit_html_ids_count_as_anchors check_explicit_html_ids_count_as_anchors
t_check every_documented_anchor_resolves check_every_documented_anchor_resolves
t_check same_page_anchors_are_actually_checked check_same_page_anchors_are_actually_checked
t_done
