#!/usr/bin/env bash
# Feature coverage: does every part of the language have a documented home?
#
# The checker is the Flow program behind scripts/check_doc_coverage.sh. These
# tests drive it through the shim, using its --inventory, --map, --mentions
# and --is-backend options.
source "$(dirname "$0")/lib.sh"

CHECKER="$T_ROOT/scripts/check_doc_coverage.sh"
MAP="$T_ROOT/docs/coverage.json"

# The inventory comes from the compiler, so it cannot go stale. Read it once;
# each line is category:name.
INVENTORY="$T_WORK/inventory"
INVENTORY_RC=0
bash "$CHECKER" --inventory > "$INVENTORY" 2> "$T_WORK/inventory.err" || INVENTORY_RC=$?

inventory_ok() {
    [[ "$INVENTORY_RC" -eq 0 ]] || { cat "$T_WORK/inventory.err"; return 1; }
}

# Assert that each NAME is in CATEGORY.
in_inventory() {
    local category="$1"
    shift
    local name
    for name in "$@"; do
        a_true "$category:$name in the inventory" grep -qxF -- "$category:$name" "$INVENTORY" || return 1
    done
}

not_in_inventory() {
    local category="$1"
    shift
    local name
    for name in "$@"; do
        if grep -qxF -- "$category:$name" "$INVENTORY"; then
            echo "$category:$name must not be in the inventory"
            return 1
        fi
    done
}

check_keywords_come_from_the_lexer() {
    inventory_ok
    # A sample of constructs the parser really reserves.
    in_inventory keyword function effect capability distinct defer match
}

check_attributes_come_from_the_attribute_module() {
    inventory_ok
    in_inventory attribute inline only gpu rt_safe libm
    a_eq "$(grep '^attribute:' "$INVENTORY" | sort -u | wc -l | tr -d ' ')" 22 "attribute count"
}

check_cli_commands_come_from_the_dispatch_table() {
    inventory_ok
    in_inventory cli run compile test fmt repl wasm
    # Arch and profile `case` arms elsewhere in the driver must not leak in.
    not_in_inventory cli x86_64 aarch64 auto safety flight
}

check_stdlib_modules_are_discovered_including_subdirectories() {
    inventory_ok
    in_inventory stdlib array string gfx
    in_inventory stdlib filters oscillators || { echo "audio/ subdirectory missing"; return 1; }
    in_inventory stdlib lqr wfc || { echo "dynamics/ subdirectory missing"; return 1; }
}

check_backends_are_discovered() {
    inventory_ok
    in_inventory backend cgen mlirgen bpf_target
}

check_backend_discovery_covers_every_naming_convention() {
    local stem="$1" expected="$2"
    t_run bash "$CHECKER" --is-backend "$stem"
    a_eq "$(tr -d '[:space:]' < "$T_OUT")" "$expected" "--is-backend $stem"
}

# The shipped map.
check_every_feature_has_a_home_or_a_written_reason() {
    t_run bash "$CHECKER"
    [[ "$T_RC" -eq 0 ]] || { cat "$T_OUT" "$T_ERR"; return 1; }
    a_file_contains "$T_OUT" "every feature has a documented home"
}

check_every_exemption_carries_a_reason() {
    local blank
    blank="$(jq -r '(.exempt // {}) | to_entries[] | select((.value | tostring | gsub("^\\s+|\\s+$"; "")) == "") | .key' "$MAP")"
    [[ -z "$blank" ]] || { echo "exempt with no reason: $blank"; return 1; }
}

check_the_map_is_valid_json_and_sorted() {
    a_eq "$(jq '(.covered | length > 0) and has("exempt")' "$MAP")" true "covered is non-empty and exempt exists"
}

# A mapping has to point at a page that exists and mentions the feature.
# Write the real map with a jq edit applied and run the checker against it.
check_with_map() {
    jq "$1" "$MAP" > "$T_TMP/coverage.json"
    t_run bash "$CHECKER" --map "$T_TMP/coverage.json"
}

check_a_feature_with_no_mapping_is_reported() {
    check_with_map 'del(.covered["keyword:defer"])'
    a_eq "$T_RC" 1 "exit status"
    a_file_contains "$T_OUT" "keyword:defer has no documented home"
}

check_a_mapping_to_a_missing_page_fails() {
    check_with_map '.covered["keyword:defer"] = "no/such/page.md"'
    a_eq "$T_RC" 1 "exit status"
    a_file_contains "$T_OUT" "does not exist"
}

check_a_page_that_does_not_mention_the_feature_fails() {
    # An absolute page path is joined as-is, so the map can point outside docs/.
    local page="$T_TMP/empty.md"
    printf '# A page about something else entirely\n' > "$page"
    check_with_map ".covered[\"keyword:defer\"] = $(jq -Rn --arg p "$page" '$p')"
    a_eq "$T_RC" 1 "exit status"
    a_file_contains "$T_OUT" "keyword:defer maps to '$page', which never mentions it"

    printf '`defer` runs on scope exit\n' > "$page"
    t_run bash "$CHECKER" --map "$T_TMP/coverage.json"
    [[ "$T_RC" -eq 0 ]] || { cat "$T_OUT"; return 1; }
}

check_mentions_is_specific_enough_to_be_worth_something() {
    local category="$1" feature="$2" text="$3" expected="$4"
    printf '%s' "$text" > "$T_TMP/p.md"
    t_run bash "$CHECKER" --mentions "$category" "$feature" "$T_TMP/p.md"
    a_eq "$(tr -d '[:space:]' < "$T_OUT")" "$expected" "--mentions $category $feature"
}

t_check keywords_come_from_the_lexer check_keywords_come_from_the_lexer
t_check attributes_come_from_the_attribute_module check_attributes_come_from_the_attribute_module
t_check cli_commands_come_from_the_dispatch_table check_cli_commands_come_from_the_dispatch_table
t_check stdlib_modules_are_discovered_including_subdirectories check_stdlib_modules_are_discovered_including_subdirectories
t_check backends_are_discovered check_backends_are_discovered
t_check "backend_discovery_covers_every_naming_convention[x_generator]" check_backend_discovery_covers_every_naming_convention x_generator True
t_check "backend_discovery_covers_every_naming_convention[y_codegen]" check_backend_discovery_covers_every_naming_convention y_codegen True
t_check "backend_discovery_covers_every_naming_convention[z_compiler]" check_backend_discovery_covers_every_naming_convention z_compiler True
# A BPF target on an unmerged branch was named bpf_target.py, which the
# original three suffixes did not match, so a whole new compilation target
# would have landed undocumented.
t_check "backend_discovery_covers_every_naming_convention[bpf_target]" check_backend_discovery_covers_every_naming_convention bpf_target True
t_check "backend_discovery_covers_every_naming_convention[w_backend]" check_backend_discovery_covers_every_naming_convention w_backend True
t_check "backend_discovery_covers_every_naming_convention[mlirgen]" check_backend_discovery_covers_every_naming_convention mlirgen True
t_check "backend_discovery_covers_every_naming_convention[parser]" check_backend_discovery_covers_every_naming_convention parser False
t_check every_feature_has_a_home_or_a_written_reason check_every_feature_has_a_home_or_a_written_reason
t_check every_exemption_carries_a_reason check_every_exemption_carries_a_reason
t_check the_map_is_valid_json_and_sorted check_the_map_is_valid_json_and_sorted
t_check a_feature_with_no_mapping_is_reported check_a_feature_with_no_mapping_is_reported
t_check a_mapping_to_a_missing_page_fails check_a_mapping_to_a_missing_page_fails
t_check a_page_that_does_not_mention_the_feature_fails check_a_page_that_does_not_mention_the_feature_fails
t_check "mentions[attribute-gpu-attr]" check_mentions_is_specific_enough_to_be_worth_something attribute gpu "use @gpu on a kernel" True
# A bare word is not the attribute.
t_check "mentions[attribute-gpu-word]" check_mentions_is_specific_enough_to_be_worth_something attribute gpu "the gpu is fast" False
t_check "mentions[cli-run-command]" check_mentions_is_specific_enough_to_be_worth_something cli run "./flow run prog.flow" True
t_check "mentions[cli-run-word]" check_mentions_is_specific_enough_to_be_worth_something cli run "a long run of failures" False
t_check "mentions[keyword-defer-code]" check_mentions_is_specific_enough_to_be_worth_something keyword defer '`defer` runs on scope exit' True
t_check "mentions[keyword-defer-prefix]" check_mentions_is_specific_enough_to_be_worth_something keyword defer "deferred work" False
t_done
