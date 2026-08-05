"""Codegen checks for concurrency: TLS effect handlers + parallel for OpenMP."""

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c


def test_effect_handlers_are_thread_local():
    src = """
effect Log {
    write(msg: i32) -> void,
}
function main() -> i32 {
    return 0
}
"""
    c = flow_to_c(parse_flow_code(src))
    assert "_Thread_local" in c
    assert "_current_Log_handler" in c


def test_parallel_for_emits_openmp_pragma():
    src = """
function main() -> i32 {
    parallel for i in 0 to 10 {
        let x: i32 = i
    }
    return 0
}
"""
    c = flow_to_c(parse_flow_code(src))
    assert "#pragma omp parallel for" in c
    assert "#ifdef _OPENMP" in c
