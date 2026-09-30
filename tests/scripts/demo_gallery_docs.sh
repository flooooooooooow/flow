#!/usr/bin/env bash
# Contracts for the data-driven Wiki demo/gallery system.
#
# The generators are Flow programs behind scripts/build_shader_gallery.sh and
# scripts/build_demo_overview.sh. Their --check mode regenerates the page and
# compares it with the checked-in copy, so the checked-in pages stand for the
# generated output here.
source "$(dirname "$0")/lib.sh"

PAGE="$T_ROOT/docs/demos/shaders.md"
CATALOG="$T_ROOT/docs/demos/catalog.json"

count_of() {
    grep -oF -- "$1" "$2" | wc -l | tr -d ' '
}

# Text between the demo-feature-grid opening tag and the first "</div>" that
# ends a line followed by a blank line.
featured_block() {
    awk '
        !found {
            i = index($0, "<div class=\"demo-feature-grid\">")
            if (!i) next
            found = 1
            $0 = substr($0, i + length("<div class=\"demo-feature-grid\">"))
        }
        {
            if (have) {
                if ($0 == "" && prev ~ /<\/div>$/) {
                    sub(/<\/div>$/, "", prev)
                    print prev
                    exit
                }
                print prev
            }
            prev = $0
            have = 1
        }
    ' "$PAGE"
}

check_photoreal_gallery_generator_tracks_all_fsl_entries() {
    t_need_cc
    t_run scripts/build_shader_gallery.sh --check
    [[ "$T_RC" -eq 0 ]] || { cat "$T_ERR"; return 1; }
    a_file_is "$T_OUT" $'shader gallery page is current\n'

    grep -oE '<img src="./shaders/photoreal_[A-Za-z0-9_]+\.gif"' "$PAGE" \
        | sed -E 's#.*/(photoreal_[A-Za-z0-9_]+)\.gif"#\1#' > "$T_TMP/names"
    a_eq "$(wc -l < "$T_TMP/names" | tr -d ' ')" 64 "photoreal images"
    a_eq "$(sort -u "$T_TMP/names" | wc -l | tr -d ' ')" 64 "unique photoreal images"
    local featured
    featured="$(featured_block | grep -oE -- '--name photoreal_[A-Za-z0-9_]+' | sed 's/^--name //' | tr '\n' ' ')"
    a_eq "$featured" "photoreal_studio photoreal_glass photoreal_marble photoreal_chrome " "featured tiles"
    a_true "photoreal_gold listed" grep -qxF photoreal_gold "$T_TMP/names"
    a_true "photoreal_energy_crystal listed" grep -qxF photoreal_energy_crystal "$T_TMP/names"
    a_true "photoreal_underwater listed" grep -qxF photoreal_underwater "$T_TMP/names"
    a_eq "$(count_of '<figure class="demo-tile' "$PAGE")" 64 "demo tiles"
    a_file_contains "$PAGE" "record_shader_gallery.sh --group photoreal"
}

check_demo_catalog_is_unique_and_covers_expected_collections() {
    a_eq "$(jq '[.collections[].id] | length == (unique | length)' "$CATALOG")" true "ids are unique"
    a_eq "$(jq '.collections | length' "$CATALOG")" 12 "collections"
    a_eq "$(jq '[.collections[].id] as $ids | ["shaders","games","morphogenesis","neuro","threed","planet","wasm"] - $ids | length' "$CATALOG")" 0 \
        "expected collections present"
    a_eq "$(jq -c '[.collections[].section] | unique' "$CATALOG")" \
        '["Interactive","Numerics","Rendering","Systems through time"]' "sections"
    a_eq "$(jq 'all(.collections[]; .page | endswith(".md"))' "$CATALOG")" true "pages end in .md"
    a_eq "$(jq 'all(.collections[]; .preview | endswith(".gif"))' "$CATALOG")" true "previews end in .gif"
}

check_demo_overview_is_derived_from_catalog() {
    t_need_cc
    t_run scripts/build_demo_overview.sh --check --check-previews
    [[ "$T_RC" -eq 0 ]] || { cat "$T_ERR"; return 1; }
    local page="$T_ROOT/docs/demos/overview.md"
    a_file_contains "$page" "# Demo Showcase"
    local cards collections
    cards="$(count_of 'class="demo-collection-card' "$page")"
    collections="$(jq '.collections | length' "$CATALOG")"
    a_true "cards ($cards) >= collections ($collections)" test "$cards" -ge "$collections"
    a_file_contains "$page" "Photoreal FSL"
    a_file_contains "$page" "Systems through time"
    a_file_contains "$page" "Live WebAssembly"
}

check_demo_navigation_is_synced_with_catalog() {
    t_need_cc
    t_run scripts/sync_demo_nav.sh --check
    [[ "$T_RC" -eq 0 ]] || { cat "$T_ERR"; return 1; }
    a_file_is "$T_OUT" $'demo navigation is current\n'
}

check_wiki_shell_loads_gallery_presentation_assets() {
    a_file_contains site/index.html 'href="assets/demo-gallery.css"'
    a_file_contains site/index.html 'src="assets/gallery-enhance.js"'
    a_file_contains docs/assets/gallery-enhance.js "MutationObserver"
    a_file_contains docs/assets/gallery-enhance.js "demo-tile-grid-enhanced"
}

t_check photoreal_gallery_generator_tracks_all_fsl_entries check_photoreal_gallery_generator_tracks_all_fsl_entries
t_check demo_catalog_is_unique_and_covers_expected_collections check_demo_catalog_is_unique_and_covers_expected_collections
t_check demo_overview_is_derived_from_catalog check_demo_overview_is_derived_from_catalog
t_check demo_navigation_is_synced_with_catalog check_demo_navigation_is_synced_with_catalog
t_check wiki_shell_loads_gallery_presentation_assets check_wiki_shell_loads_gallery_presentation_assets
t_done
