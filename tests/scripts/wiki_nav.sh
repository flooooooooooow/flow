#!/usr/bin/env bash
# The wiki nav manifest and the checks that keep it honest.
#
# The checks live in the Flow program scripts/tools/wiki_nav, run through
# scripts/wiki_nav.sh. The wiki build (scripts/build_wiki.sh) runs the same
# validation before it writes the sidebar.
source "$(dirname "$0")/lib.sh"

SHIM="$T_ROOT/scripts/wiki_nav.sh"
NAV="$T_ROOT/docs/nav.json"

# Non-empty stdout lines of the shim, into FILE.
lines() {
    local file="$1"
    shift
    bash "$SHIM" "$@" | awk 'length($0) > 0' > "$file" || true
}

# The real manifest.

# This is the check that would have caught project/PROJECT_STRUCTURE.md, a
# sidebar entry pointing at a file that only exists under archive/.
check_the_shipped_manifest_is_consistent_with_docs() {
    t_run bash "$SHIM" --problems
    [[ "$T_RC" -eq 0 ]] || { cat "$T_OUT"; return 1; }
    a_file_is "$T_OUT" ""
}

check_the_summary_reports_a_consistent_manifest() {
    t_run bash "$SHIM"
    [[ "$T_RC" -eq 0 ]] || { cat "$T_OUT"; return 1; }
    local want=$'\nnav is consistent with docs/\n'
    tail -c "${#want}" "$T_OUT" > "$T_TMP/tail"
    a_file_is "$T_TMP/tail" "$want"
}

# Pages under PREFIX that are neither listed in the sidebar nor unlisted
# with a reason. Asserts the prefix has pages at all.
check_reachable() {
    local prefix="$1"
    lines "$T_TMP/listed" --listed
    lines "$T_TMP/pages_all" --pages
    jq -r '(.unlisted // {}) | keys[]' "$NAV" > "$T_TMP/unlisted"
    grep -F -- "$prefix" "$T_TMP/pages_all" | awk -v p="$prefix" 'index($0, p) == 1' | sort -u > "$T_TMP/pages" || true
    [[ -s "$T_TMP/pages" ]] || { echo "no pages under $prefix"; return 1; }
    sort -u "$T_TMP/listed" "$T_TMP/unlisted" > "$T_TMP/reachable"
    comm -23 "$T_TMP/pages" "$T_TMP/reachable" > "$T_TMP/stranded"
    if [[ -s "$T_TMP/stranded" ]]; then
        echo "pages under $prefix missing from the sidebar:"
        cat "$T_TMP/stranded"
        return 1
    fi
}

# A reference manual whose reference pages are not in the sidebar is a
# reference manual you cannot use.
check_every_language_page_is_reachable_from_the_sidebar() {
    check_reachable language/
}

check_every_library_page_is_reachable_from_the_sidebar() {
    check_reachable library/
}

check_unlisted_pages_all_carry_a_reason() {
    local blank
    blank="$(jq -r '(.unlisted // {}) | to_entries[] | select((.value | tostring | gsub("^\\s+|\\s+$"; "")) == "") | .key' "$NAV")"
    [[ -z "$blank" ]] || { echo "unlisted with no reason: $blank"; return 1; }
}

check_sections_reference_declared_tabs() {
    a_eq "$(jq '[.tabs[].id] as $tabs | all(.sections[]; .tab as $t | $tabs | index($t) != null)' "$NAV")" true \
        "every section names a declared tab"
}

# Validation catches the failures it exists for. Builds a docs tree and a
# manifest in $T_TMP from SECTIONS and UNLISTED (JSON) plus page names, and
# leaves the problem lines in $T_TMP/problems.
problems() {
    local sections="$1" unlisted="$2"
    shift 2
    local docs="$T_TMP/docs" page
    mkdir -p "$docs"
    printf '# home' > "$docs/home.md"
    for page in "$@"; do
        printf '# page' > "$docs/$page"
    done
    jq -n --argjson sections "$sections" --argjson unlisted "$unlisted" \
        '{default: "home.md", tabs: [{id: "start", label: "Start"}], sections: $sections, unlisted: $unlisted}' \
        > "$T_TMP/nav.json"
    lines "$T_TMP/problems" --manifest "$T_TMP/nav.json" --docs "$docs" --problems
}

HOME_ONLY='[{"id": "s", "tab": "start", "title": "S", "items": [{"label": "Home", "path": "home.md"}]}]'

no_problems() {
    if [[ -s "$T_TMP/problems" ]]; then
        echo "expected no problems, got:"
        cat "$T_TMP/problems"
        return 1
    fi
}

check_a_nav_entry_pointing_at_nothing_is_a_failure() {
    problems '[{"id": "s", "tab": "start", "title": "S", "items": [
        {"label": "Home", "path": "home.md"},
        {"label": "Ghost", "path": "does-not-exist.md"}]}]' '{}'
    a_file_contains "$T_TMP/problems" "does-not-exist.md"
}

check_a_page_in_no_section_is_a_failure() {
    problems "$HOME_ONLY" '{}' stranded.md
    a_file_contains "$T_TMP/problems" "stranded.md"
}

check_an_unlisted_page_with_a_reason_is_accepted() {
    problems "$HOME_ONLY" '{"internal.md": "internal runbook, not reader documentation"}' internal.md
    no_problems
}

check_an_unlisted_page_with_a_blank_reason_is_a_failure() {
    problems "$HOME_ONLY" '{"internal.md": "   "}' internal.md
    a_file_contains "$T_TMP/problems" "written reason"
}

check_a_page_cannot_be_both_listed_and_unlisted() {
    problems "$HOME_ONLY" '{"home.md": "some reason"}'
    a_file_contains "$T_TMP/problems" "both in the nav"
}

check_a_section_naming_an_unknown_tab_is_a_failure() {
    problems '[{"id": "s", "tab": "nope", "title": "S", "items": [{"label": "Home", "path": "home.md"}]}]' '{}'
    a_file_contains "$T_TMP/problems" "does not exist"
}

# releases.md and friends are written into build/wiki from sources outside
# docs/, so requiring them here would fail every build.
check_build_generated_pages_do_not_have_to_exist_on_disk() {
    problems '[{"id": "s", "tab": "start", "title": "S", "items": [
        {"label": "Home", "path": "home.md"},
        {"label": "Releases", "path": "releases.md"}]}]' '{}'
    no_problems
}

# Derived views.
check_generated_sections_are_filled_in_at_build_time() {
    t_run bash "$SHIM" --sections --fill euclid "Book I" x.md
    jq -c '.[] | select(.id == "proofs-euclid")' "$T_OUT" > "$T_TMP/euclid"
    [[ -s "$T_TMP/euclid" ]] || { echo "no proofs-euclid section"; cat "$T_OUT" | head -c 400; return 1; }
    a_eq "$(jq -c .items "$T_TMP/euclid")" '[{"label":"Book I","path":"x.md"}]' "euclid items"
    a_eq "$(jq 'has("generated")' "$T_TMP/euclid")" false "euclid still marked generated"
}

category() {
    bash "$SHIM" --category "$1" | tr -d '[:space:]'
}

check_search_category_follows_the_tab_a_page_sits_under() {
    a_eq "$(category language/types.md)" reference "language/types.md"
    a_eq "$(category library/memory.md)" reference "library/memory.md"
    a_eq "$(category tutorials/beginner.md)" tutorial "tutorials/beginner.md"
    a_eq "$(category DEVELOPMENT.md)" tooling "DEVELOPMENT.md"
}

check_an_unknown_page_falls_back_to_guide() {
    a_eq "$(category no/such/page.md)" guide "no/such/page.md"
}

check_the_shipped_manifest_is_valid_json() {
    a_eq "$(jq '(.sections | length > 0) and (.tabs | length > 0)' "$NAV")" true "sections and tabs are non-empty"
}

t_check the_shipped_manifest_is_consistent_with_docs check_the_shipped_manifest_is_consistent_with_docs
t_check the_summary_reports_a_consistent_manifest check_the_summary_reports_a_consistent_manifest
t_check every_language_page_is_reachable_from_the_sidebar check_every_language_page_is_reachable_from_the_sidebar
t_check every_library_page_is_reachable_from_the_sidebar check_every_library_page_is_reachable_from_the_sidebar
t_check unlisted_pages_all_carry_a_reason check_unlisted_pages_all_carry_a_reason
t_check sections_reference_declared_tabs check_sections_reference_declared_tabs
t_check a_nav_entry_pointing_at_nothing_is_a_failure check_a_nav_entry_pointing_at_nothing_is_a_failure
t_check a_page_in_no_section_is_a_failure check_a_page_in_no_section_is_a_failure
t_check an_unlisted_page_with_a_reason_is_accepted check_an_unlisted_page_with_a_reason_is_accepted
t_check an_unlisted_page_with_a_blank_reason_is_a_failure check_an_unlisted_page_with_a_blank_reason_is_a_failure
t_check a_page_cannot_be_both_listed_and_unlisted check_a_page_cannot_be_both_listed_and_unlisted
t_check a_section_naming_an_unknown_tab_is_a_failure check_a_section_naming_an_unknown_tab_is_a_failure
t_check build_generated_pages_do_not_have_to_exist_on_disk check_build_generated_pages_do_not_have_to_exist_on_disk
t_check generated_sections_are_filled_in_at_build_time check_generated_sections_are_filled_in_at_build_time
t_check search_category_follows_the_tab_a_page_sits_under check_search_category_follows_the_tab_a_page_sits_under
t_check an_unknown_page_falls_back_to_guide check_an_unknown_page_falls_back_to_guide
t_check the_shipped_manifest_is_valid_json check_the_shipped_manifest_is_valid_json
t_done
