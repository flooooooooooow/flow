import pytest
import os
import shutil
from flow.module_resolver import resolve_modules
from tests.unit.compiler_helpers import flow_to_c, typecheck, monomorphize, compile_and_run
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

@pytest.mark.skipif(shutil.which('cc') is None and shutil.which('clang') is None, reason="No C compiler")
def test_compile_bundle_symbol_closure(tmp_path):
    main_flow = tmp_path / "main.flow"
    helper_flow = tmp_path / "helper.flow"
    
    main_flow.write_text("""
import .helper { helper }
function main() -> i32 {
    return helper() - 42;
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
    
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        c_path = os.path.join(td, "prog.c")
        bin_path = os.path.join(td, "prog")
        with open(c_path, "w") as f:
            f.write(c_code)
        
        compiler = shutil.which('cc') or shutil.which('clang')
        import subprocess
        res = subprocess.run([compiler, "-O0", "-o", bin_path, c_path, "-lm"])
        assert res.returncode == 0
        
        res = subprocess.run([bin_path])
        assert res.returncode == 0

