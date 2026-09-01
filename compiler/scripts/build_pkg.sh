#!/bin/bash
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
mkdir -p build compiler/build

export PYTHONPATH="$REPO_ROOT/src"

cat compiler/src/fileio.flow compiler/src/toml.flow compiler/src/project_config.flow compiler/src/semver.flow compiler/src/pkg.flow compiler/src/pkg_main.flow > build/pkg_bundle.flow
sed -i '/import \./d' build/pkg_bundle.flow

python3 -m flow.transpiler build/pkg_bundle.flow --c --lenient -o build/pkg_bundle.c || true

sed -i 's/int32_t main_i32_ptr_ptr_u8(int32_t argc, uint8_t\*\* argv) {/int main(int argc, char** argv_c)\n{\nuint8_t** argv = (uint8_t**)argv_c;/g' build/pkg_bundle.c
sed -i 's/int32_t main_i32_ptr_ptr_u8(int32_t argc, uint8_t\*\* argv);/int main(int argc, char** argv_c);/g' build/pkg_bundle.c
sed -i 's/flowc_pkg_dispatch_fallback_i32_ptr_ptr_u8(argc, argv)/flowc_pkg_dispatch_fallback_i32_ptr_ptr_u8(argc, (uint8_t\*\*)argv)/g' build/pkg_bundle.c
sed -i 's/int32_t ret = stat(path, (&(buf\[0\])));/int32_t ret = stat(path, (struct stat*)(\&(buf\[0\])));/g' build/pkg_bundle.c

cat << 'PYEOF2' > build/fix_c.py
import re
with open("build/pkg_bundle.c", "r") as f: c = f.read()
replacements = {
    "flowc_toml_is_ws": "flowc_toml_is_ws_i32",
    "flowc_toml_is_key_char": "flowc_toml_is_key_char_i32",
    "flowc_toml_skip_ws": "flowc_toml_skip_ws_ptr_u8_i32_i32",
    "flowc_toml_skip_line": "flowc_toml_skip_line_ptr_u8_i32_i32",
    "flowc_toml_bytes_eq": "flowc_toml_bytes_eq_ptr_u8_i32_i32_string",
    "flowc_toml_copy_bytes": "flowc_toml_copy_bytes_ptr_u8_ptr_u8_i32_i32",
    "flowc_toml_parse_i32_at": "flowc_toml_parse_i32_at_ptr_u8_i32_i32",
    "flowc_toml_key_matches": "flowc_toml_key_matches_ptr_u8_i32_ptr_u8_i32_i32_string",
    "flowc_toml_find_value": "flowc_toml_find_value_string_string",
    "toml_get_keys_in_section": "toml_get_keys_in_section_string_string_ptr_u8_i32",
    "toml_has_key": "toml_has_key_string_string",
    "toml_get_string": "toml_get_string_string_string_ptr_u8_i32",
    "toml_get_i32": "toml_get_i32_string_string",
    "toml_get_bool": "toml_get_bool_string_string",
    "flowc_load_project_config": "flowc_load_project_config_string_ptr_ProjectConfig",
    "flowc_semver_format_lock_entry": "flowc_semver_format_lock_entry_string_string_string_ptr_u8_i32",
    "flowc_semver_write_lockfile": "flowc_semver_write_lockfile_string_string"
}
for k, v in replacements.items():
    c = re.sub(r'(?<!int32_t )(?<!void )(?<!int )(?<!char )\b' + k + r'\(', v + '(', c)
with open("build/pkg_bundle.c", "w") as f: f.write(c)
PYEOF2
python3 build/fix_c.py

cc -O2 -Wno-implicit-function-declaration -Wno-format-extra-args -Wno-incompatible-pointer-types -o build/flow_pkg build/pkg_bundle.c
echo "Built build/flow_pkg natively!"
rm -f build/fix_c.py build/pkg_bundle.flow build/pkg_bundle.c
