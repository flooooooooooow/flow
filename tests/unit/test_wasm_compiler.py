from pathlib import Path
from types import SimpleNamespace

import pytest

import flow.wasm_compiler as wasm


def test_llvm_to_wasm_uses_wasm32_target(monkeypatch, tmp_path):
    commands = []

    monkeypatch.setattr(wasm, "_find_clang", lambda: "/opt/llvm/bin/clang")

    def fake_run(command, **kwargs):
        commands.append(command)
        output = Path(command[command.index("-o") + 1])
        output.write_bytes(b"\x00asm")
        return SimpleNamespace(returncode=0, stderr="")

    monkeypatch.setattr(wasm.subprocess, "run", fake_run)

    output = tmp_path / "kernel.wasm"
    wasm.llvm_to_wasm(
        "define i32 @add(i32 %a, i32 %b) { %v = add i32 %a, %b ret i32 %v }",
        output,
        exports=["add"],
    )

    command = commands[0]
    assert "--target=wasm32-unknown-unknown" in command
    assert "-nostdlib" in command
    assert "-Wl,--no-entry" in command
    assert "-Wl,--export=add" in command
    assert "-Wl,--export-memory" in command
    assert output.read_bytes() == b"\x00asm"


def test_llvm_to_wasm_rejects_missing_requested_export(tmp_path):
    with pytest.raises(RuntimeError, match=r"missing.*Defined functions: add"):
        wasm.llvm_to_wasm(
            "define i32 @add() { ret i32 42 }",
            tmp_path / "kernel.wasm",
            exports=["missing"],
        )


def test_defined_llvm_functions_handles_quoted_symbols():
    llvm_ir = '\n'.join([
        'define i32 @plain() { ret i32 0 }',
        'define void @"quoted.name"() { ret void }',
        'declare i32 @external()',
    ])
    assert wasm._defined_llvm_functions(llvm_ir) == {"plain", "quoted.name"}


def test_flow_to_wasm_goes_through_mlir_llvm_not_c(monkeypatch, tmp_path):
    source = tmp_path / "kernel.flow"
    source.write_text("export function add(a: i32, b: i32) -> i32 { return a + b }")
    seen = []

    def fake_run(command, **kwargs):
        seen.append(command)
        if "flow.transpiler" in command:
            output = Path(command[command.index("-o") + 1])
            output.write_text("define i32 @add(i32 %a, i32 %b) { ret i32 %a }")
        return SimpleNamespace(returncode=0, stderr="")

    def fake_llvm_to_wasm(llvm_ir, output, **kwargs):
        Path(output).write_bytes(b"\x00asm")
        return Path(output)

    monkeypatch.setattr(wasm.subprocess, "run", fake_run)
    monkeypatch.setattr(wasm, "llvm_to_wasm", fake_llvm_to_wasm)

    output = tmp_path / "kernel.wasm"
    wasm.flow_to_wasm(source, output)

    transpile = seen[0]
    assert "--wasm32" in transpile
    assert "--llvm" in transpile
    assert "--c" not in transpile
    assert output.exists()
