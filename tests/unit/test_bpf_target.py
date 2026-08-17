from pathlib import Path

import pytest

from flow.bpf_target import (
    BPFEL,
    BPFTargetError,
    target_for_name,
    validate_bpf_llvm_ir,
    with_bpf_target_header,
)


def test_bpfel_target_matches_llvm_contract():
    assert BPFEL.triple == "bpfel"
    assert BPFEL.data_layout == "e-m:e-p:64:64-i64:64-i128:128-n32:64-S128"
    assert BPFEL.pointer_bits == 64
    assert BPFEL.max_stack_bytes == 512
    assert BPFEL.little_endian is True


def test_public_target_aliases_resolve_to_bpfel():
    assert target_for_name("bpfel") is BPFEL
    assert target_for_name("bpf") is BPFEL
    assert target_for_name("ebpf") is BPFEL


def test_unknown_bpf_target_is_rejected():
    with pytest.raises(BPFTargetError, match="unknown BPF target"):
        target_for_name("bpfeb")


def test_target_header_replaces_host_triple_and_layout():
    source = '''target datalayout = "host-layout"
target triple = "x86_64-unknown-linux-gnu"
define i64 @entry(i64 %x) {
  ret i64 %x
}
'''
    targeted = with_bpf_target_header(source)
    assert 'target triple = "bpfel"' in targeted
    assert f'target datalayout = "{BPFEL.data_layout}"' in targeted
    assert "x86_64-unknown-linux-gnu" not in targeted
    assert "host-layout" not in targeted


@pytest.mark.parametrize(
    "llvm_ir, expected",
    [
        ("declare ptr @malloc(i64)\n", "malloc"),
        ("declare void @free(ptr)\n", "free"),
        ("define void @f() { invoke void @g() to label %ok unwind label %bad }\n", "invoke"),
        ("define void @f() { %x = landingpad { ptr, i32 } cleanup }\n", "landingpad"),
        ("declare void @_Unwind_Resume(ptr)\n", "_Unwind_"),
    ],
)
def test_verifier_hostile_runtime_or_unwind_constructs_are_rejected(llvm_ir, expected):
    with pytest.raises(BPFTargetError, match=expected):
        validate_bpf_llvm_ir(llvm_ir)


def test_dynamic_alloca_is_rejected():
    llvm_ir = "define void @f(i64 %n) { %p = alloca i8, i64 %n ret void }\n"
    with pytest.raises(BPFTargetError, match="statically bounded stack allocation"):
        validate_bpf_llvm_ir(llvm_ir)


def test_static_alloca_is_allowed_by_initial_target_gate():
    llvm_ir = "define void @f() { %p = alloca i8, i64 8 ret void }\n"
    validate_bpf_llvm_ir(llvm_ir)
