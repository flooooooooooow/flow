"""
Unit tests for compiler performance remarks (FPERF rules) in Flow.
"""

import pytest
from flow.idioms import IdiomAdvisor
from flow.parser import Parser, Lexer
from flow.lsp_server import FlowLanguageServer
import flow.check as flow_check


def test_fperf001_detects_missed_loop_vectorization_due_to_control_flow():
    code = """
    function main() -> void {
        let mut arr = [1, 2, 3, 4];
        for i in 0..4 {
            if i % 2 == 0 {
                arr[i] = i * 2;
            }
        }
    }
    """
    ast = Parser(Lexer(code)).parse()
    advisor = IdiomAdvisor()
    advisor.analyze_program(ast)

    fperf_findings = [f for f in advisor.findings if f.rule_id == "FPERF001"]
    assert len(fperf_findings) >= 1
    assert "Missed loop vectorization" in fperf_findings[0].title
    assert "contains control flow" in fperf_findings[0].rationale


def test_fperf001_detects_missed_loop_vectorization_due_to_missing_step():
    code = """
    function main() -> void {
        for i in 0..10 {
            let x = i + 1;
        }
    }
    """
    ast = Parser(Lexer(code)).parse()
    advisor = IdiomAdvisor()
    advisor.analyze_program(ast)

    fperf_findings = [f for f in advisor.findings if f.rule_id == "FPERF001"]
    assert len(fperf_findings) >= 1
    assert "missing explicit step 1" in fperf_findings[0].rationale


def test_fperf002_detects_dynamic_effect_dispatch_outside_handle():
    code = """
    effect Logger {
        function log(msg: i32) -> void
    }

    function test_unhandled() -> void {
        Logger::log(42);
    }
    """
    ast = Parser(Lexer(code)).parse()
    advisor = IdiomAdvisor()
    advisor.analyze_program(ast)

    fperf_findings = [f for f in advisor.findings if f.rule_id == "FPERF002"]
    assert len(fperf_findings) == 1
    assert "Dynamic effect dispatch overhead" in fperf_findings[0].title
    assert "outside a 'handle' block" in fperf_findings[0].rationale


def test_fperf002_ignores_effect_call_inside_handle():
    code = """
    effect Logger {
        function log(msg: i32) -> void
    }

    function test_handled() -> void {
        handle Logger with MyLogger {
            Logger::log(42);
        }
    }
    """
    ast = Parser(Lexer(code)).parse()
    advisor = IdiomAdvisor()
    advisor.analyze_program(ast)

    fperf_findings = [f for f in advisor.findings if f.rule_id == "FPERF002"]
    assert len(fperf_findings) == 0


def test_fperf003_detects_struct_allocation_inside_loop():
    code = """
    struct Point { x: i32, y: i32 }

    function main() -> void {
        for i in 0..10 step 1 {
            let p = Point{ x: i, y: i + 1 };
        }
    }
    """
    ast = Parser(Lexer(code)).parse()
    advisor = IdiomAdvisor()
    advisor.analyze_program(ast)

    fperf_findings = [f for f in advisor.findings if f.rule_id == "FPERF003"]
    assert len(fperf_findings) == 1
    assert "Allocation inside loop" in fperf_findings[0].title
    assert "Struct literal is repeatedly constructed inside loop body" in fperf_findings[0].rationale


def test_fperf004_detects_unspanned_array_indexing_inside_loop():
    code = """
    function main() -> void {
        let arr = [1, 2, 3, 4, 5];
        for i in 0..5 step 1 {
            let x = arr[i];
        }
    }
    """
    ast = Parser(Lexer(code)).parse()
    advisor = IdiomAdvisor()
    advisor.analyze_program(ast)

    fperf_findings = [f for f in advisor.findings if f.rule_id == "FPERF004"]
    assert len(fperf_findings) == 1
    assert "Un-spanned array indexing inside loop" in fperf_findings[0].title
    assert "indexed inside loop without span borrowing" in fperf_findings[0].rationale


def test_fperf_suppression_comments():
    code = """
    function main() -> void {
        let mut arr = [1, 2, 3, 4];
        # flow-idiom: allow FPERF001
        for i in 0..4 {
            arr[i] = i * 2;
        }
    }
    """
    ast = Parser(Lexer(code)).parse()
    advisor = IdiomAdvisor()
    advisor.analyze_program(ast)

    # In IdiomAdvisor engine findings are produced; suppression is filtered by consumer (check.py / LSP)
    assert any(f.rule_id == "FPERF001" for f in advisor.findings)


def test_lsp_publishes_fperf_hints():
    server = FlowLanguageServer()
    uri = "file:///test_perf.flow"
    server.documents[uri] = """function main() -> void {
    let arr = [1, 2, 3];
    for i in 0..3 {
        let x = arr[i];
    }
}"""

    diagnostics = server._compute_diagnostics(server.documents[uri], uri)
    fperf_diags = [d for d in diagnostics if d.get('code') and d['code'].startswith('FPERF')]
    assert len(fperf_diags) >= 1
    assert fperf_diags[0]['severity'] == 4  # Hint


def test_cli_check_perf_remarks(tmp_path, capsys):
    file_path = tmp_path / "test.flow"
    file_path.write_text("""function main() -> void {
    let arr = [1, 2, 3];
    for i in 0..3 {
        let x = arr[i];
    }
}""")

    res = flow_check.main(["--perf-remarks", str(file_path)])
    captured = capsys.readouterr()
    assert "FPERF" in captured.out or "FPERF" in captured.err or res == 1
