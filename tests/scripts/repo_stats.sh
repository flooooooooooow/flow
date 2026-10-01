#!/usr/bin/env bash
# Repository statistics formatting and path classification.
#
# The counter is the Flow program in scripts/tools/repo_stats/main.flow. These
# tests build it with scripts/tools/build_tool.sh and run it in a scratch tree
# with a hand-written file list (--inputs), so no git is involved. The formatting rules
# are pinned here because a truncating Flow counter once published 72.5k
# against a README that said 72.6k.
source "$(dirname "$0")/lib.sh"

START="<!-- repo-stats:start -->"
END="<!-- repo-stats:end -->"
NO_LINES="-"

COUNTER=""
COUNTER_ERR=""
if command -v cc > /dev/null 2>&1 || command -v clang > /dev/null 2>&1; then
    if out="$(scripts/tools/build_tool.sh repo_stats 2> "$T_WORK/build.err")"; then
        COUNTER="$T_ROOT/$out"
    else
        COUNTER_ERR="$(cat "$T_WORK/build.err")"
    fi
fi

counter() {
    t_need_cc
    [[ -n "$COUNTER" ]] || { echo "build_tool.sh repo_stats failed: $COUNTER_ERR"; return 1; }
}

# Lay out files ("path:lines" arguments) in $T_TMP/tree and run the counter
# over them. MODE (write or check) and README (text) come from the
# environment. Leaves T_RC, T_OUT, T_ERR, and $T_TMP/tree/README.md.
run_counter() {
    local tree="$T_TMP/tree" spec rel lines
    mkdir -p "$tree/build/repo-stats" "$tree/docs/generated"
    : > "$tree/build/repo-stats/files.txt"
    for spec in "$@"; do
        rel="${spec%:*}"
        lines="${spec##*:}"
        mkdir -p "$(dirname "$tree/$rel")"
        awk -v n="$lines" 'BEGIN { for (i = 0; i < n; i++) print "x" }' > "$tree/$rel"
        printf '%s\n' "$rel" >> "$tree/build/repo-stats/files.txt"
    done
    # scripts/update_repo_stats.sh creates docs/generated before running the
    # counter.
    printf 'commit=abcdef123456\ngenerated_at=2026-01-01T00:00:00+00:00\n' > "$tree/build/repo-stats/meta.txt"
    printf '%s\n' "${MODE:-write}" > "$tree/build/repo-stats/mode.txt"
    if [[ -n "${README+set}" ]]; then
        printf '%s' "$README" > "$tree/README.md"
    else
        printf '# Title\n\n%s\nold\n%s\n\ntail\n' "$START" "$END" > "$tree/README.md"
    fi
    T_OUT="$T_TMP/counter.out"
    T_ERR="$T_TMP/counter.err"
    set +e
    (cd "$tree" && "$COUNTER" --inputs build/repo-stats) > "$T_OUT" 2> "$T_ERR"
    T_RC=$?
    set -e
    STATS="$tree/docs/generated/repository-stats.json"
}

# Badge text: plain below 1k, one rounded decimal below 100k, then k.
check_compact() {
    local value="$1" expected="$2"
    counter
    run_counter "lib/stdlib/a.flow:$value"
    [[ "$T_RC" -eq 0 ]] || { cat "$T_ERR"; return 1; }
    a_eq "$(jq -r .badges.flow "$STATS")" "$expected Flow LOC" "flow badge"
    a_eq "$(jq -r .badges.loc "$STATS")" "$expected LOC" "loc badge"
}

# Areas match whole path components, never bare string prefixes.
check_directory_prefix_and_partial_component() {
    counter
    run_counter src/flow/parser.py:5 src/flowers/parser.py:7 runtime:3 docs/index.md:2
    [[ "$T_RC" -eq 0 ]] || { cat "$T_ERR"; return 1; }
    a_eq "$(jq -c '.areas.python_compiler' "$STATS")" '{"files":1,"lines":5}' "python_compiler area"
    a_eq "$(jq '.areas.runtime.files' "$STATS")" 0 "runtime area files"
    a_eq "$(jq -c '.languages.Python' "$STATS")" '{"files":2,"lines":12}' "Python language"
}

# The rendered block is delimited and uses grouped numbers.
markdown_block() {
    counter
    run_counter lib/stdlib/big.flow:2000 src/flow/a.py:1500 registry/packages/x/flow.toml:4
    [[ "$T_RC" -eq 0 ]] || { cat "$T_ERR"; return 1; }
    sed -n "/$START/,/$END/p" "$T_TMP/tree/README.md" > "$T_TMP/block"
    [[ -s "$T_TMP/block" ]] || { echo "no stats block in README.md"; return 1; }
}

check_numbers_are_grouped() {
    markdown_block
    a_file_contains "$T_TMP/block" "| **Tracked source** | 2 | 3,500 |"
}

check_registry_packages_reports_no_line_count() {
    markdown_block
    a_file_contains "$T_TMP/block" "| **Registry packages** | 1 | $NO_LINES |"
}

check_languages_ordered_by_lines_descending() {
    markdown_block
    local flow_at python_at
    flow_at="$(awk 'index($0, "| Flow |") { print NR; exit }' "$T_TMP/block")"
    python_at="$(awk 'index($0, "| Python |") { print NR; exit }' "$T_TMP/block")"
    [[ -n "$flow_at" && -n "$python_at" ]] || { cat "$T_TMP/block"; return 1; }
    a_true "Flow row ($flow_at) before Python row ($python_at)" test "$flow_at" -lt "$python_at"
}

check_footnote_credits_the_flow_counter() {
    markdown_block
    a_file_contains "$T_TMP/block" "scripts/tools/repo_stats/main.flow"
}

# The markers have to survive edits, or every refresh fails.
check_readme_has_both_markers() {
    a_eq "$(grep -oF -- "$START" README.md | wc -l | tr -d ' ')" 1 "start markers in README.md"
    a_eq "$(grep -oF -- "$END" README.md | wc -l | tr -d ' ')" 1 "end markers in README.md"
}

check_update_replaces_only_the_block() {
    counter
    run_counter a.flow:1
    [[ "$T_RC" -eq 0 ]] || { cat "$T_ERR"; return 1; }
    local readme="$T_TMP/tree/README.md"
    printf '# Title\n\n%s\n' "$START" > "$T_TMP/want_head"
    printf '%s\n\ntail\n' "$END" > "$T_TMP/want_tail"
    head -c "$(($(wc -c < "$T_TMP/want_head")))" "$readme" > "$T_TMP/got_head"
    tail -c "$(($(wc -c < "$T_TMP/want_tail")))" "$readme" > "$T_TMP/got_tail"
    a_true "README.md starts with the title and the start marker" cmp -s "$T_TMP/want_head" "$T_TMP/got_head"
    a_true "README.md ends with the end marker and the tail" cmp -s "$T_TMP/want_tail" "$T_TMP/got_tail"
    if grep -qxF old "$readme"; then
        echo "the old block body survived"
        return 1
    fi
}

check_missing_markers_fail() {
    counter
    README=$'no markers\n' run_counter a.flow:1
    a_eq "$T_RC" 1 "exit status"
    a_file_contains "$T_ERR" "missing repository-stat markers"
}

check_check_mode_reports_stale_files() {
    counter
    MODE=check run_counter a.flow:1
    a_eq "$T_RC" 1 "exit status"
    a_file_is "$T_OUT" $'Repository statistics are stale: docs/generated/repository-stats.json, README.md\n'
}

t_check "compact[999]" check_compact 999 "999"
t_check "compact[1000]" check_compact 1000 "1.0k"
t_check "compact[72586]" check_compact 72586 "72.6k"
t_check "compact[99960]" check_compact 99960 "100.0k"
t_check "compact[100000]" check_compact 100000 "100k"
t_check "compact[171889]" check_compact 171889 "172k"
t_check "compact[1234000]" check_compact 1234000 "1,234k"
t_check under/directory_prefix_and_partial_component check_directory_prefix_and_partial_component
t_check markdown/numbers_are_grouped check_numbers_are_grouped
t_check markdown/registry_packages_reports_no_line_count check_registry_packages_reports_no_line_count
t_check markdown/languages_ordered_by_lines_descending check_languages_ordered_by_lines_descending
t_check markdown/footnote_credits_the_flow_counter check_footnote_credits_the_flow_counter
t_check readme/has_both_markers check_readme_has_both_markers
t_check readme/update_replaces_only_the_block check_update_replaces_only_the_block
t_check readme/missing_markers_fail check_missing_markers_fail
t_check readme/check_mode_reports_stale_files check_check_mode_reports_stale_files
t_done
