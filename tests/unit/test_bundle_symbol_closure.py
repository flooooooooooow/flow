from flow.module_resolver import resolve_modules
from tests.unit.compiler_helpers import flow_to_c, monomorphize
from flow.type_checker import TypeChecker
import re

def test_single_candidate_bundle_symbol_closure(tmp_path):
    main_flow = tmp_path / "main.flow"
    helper_flow = tmp_path / "helper.flow"

    main_flow.write_text("""
import .helper { helper }
function main() -> i32 {
    return helper();
}
    """)
    helper_flow.write_text("""
export function helper() -> i32 { return 42; }
    """)

    decls = resolve_modules(str(main_flow))
    checker = TypeChecker()
    checker.strict = True
    checker.check(decls)

    c_code = flow_to_c(monomorphize(decls))

    call_sites = set()
    definitions = set()

    def_pattern = re.compile(r'^\w+(?:\s+\w+)?\s+(\w+)\(')
    call_pattern = re.compile(r'(\w+)\(')

    for line in c_code.split("\n"):
        if "helper" in line:
            m = def_pattern.match(line.strip())
            if m:
                definitions.add(m.group(1))
            else:
                m_call = call_pattern.search(line.strip())
                if m_call and m_call.group(1) != "main":
                    call_sites.add(m_call.group(1))

    for call in call_sites:
        if "helper" in call:
            assert call in definitions

def test_overload_bundle_symbol_closure(tmp_path):
    # Multiple candidates should resolve correctly
    main_flow = tmp_path / "main.flow"
    helper_flow = tmp_path / "helper.flow"

    main_flow.write_text("""
import .helper { overload_func }
function main() -> i32 {
    return overload_func(42);
}
    """)
    helper_flow.write_text("""
export function overload_func(x: i32) -> i32 { return x; }
export function overload_func(x: f32) -> f32 { return x; }
    """)

    decls = resolve_modules(str(main_flow))
    checker = TypeChecker()
    checker.strict = True
    checker.check(decls)

    c_code = flow_to_c(monomorphize(decls))

    call_sites = set()
    definitions = set()

    def_pattern = re.compile(r'^\w+(?:\s+\w+)?\s+(\w+)\(')
    call_pattern = re.compile(r'(\w+)\(')

    for line in c_code.split("\n"):
        if "overload_func" in line:
            m = def_pattern.match(line.strip())
            if m:
                definitions.add(m.group(1))
            else:
                m_call = call_pattern.search(line.strip())
                if m_call and m_call.group(1) != "main":
                    call_sites.add(m_call.group(1))

    for call in call_sites:
        if "overload_func" in call:
            assert call in definitions


# test_compile_bundle_symbol_closure compiled and ran a selective import.
# It is now tests/lang/test_selective_import.flow.
