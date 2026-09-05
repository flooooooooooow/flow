import pytest
from flow.parser import Parser, Lexer
from flow.python_generator import infer_exports, ExportedSymbol, ExportDiagnostic, get_python_attrs

def test_get_python_attrs():
    attrs = ["inline", 'python(name="foo", exclude=true, doc="bar")']
    parsed = get_python_attrs(attrs)
    assert parsed.get("name") == "foo"
    assert parsed.get("exclude") == "true"
    assert parsed.get("doc") == "bar"

def test_python_export_overrides():
    code = """
    @python(name="py_func_name")
    function flow_func_name() -> void { }

    @python(doc="Computes the square root")
    function sqrt(x: f64) -> f64 { return x }

    @python(exclude=true)
    function dont_export() -> void { }

    function plain_func() -> void { }
    """
    
    ast = Parser(Lexer(code)).parse()
    functions = [node for node in ast if type(node).__name__ == "FunctionDecl"]
    
    exports = infer_exports(functions, {}, [], {})
    
    export_dict = {ex.name: ex for ex in exports.exports}
    diag_dict = {d.symbol: d for d in exports.diagnostics}
    
    assert "flow_func_name" in export_dict
    assert export_dict["flow_func_name"].python_name == "py_func_name"
    
    assert "sqrt" in export_dict
    assert export_dict["sqrt"].doc == "Computes the square root"
    
    assert "dont_export" not in export_dict
    assert "dont_export" in diag_dict
    assert diag_dict["dont_export"].kind == "excluded"
    assert "exclude=true" in diag_dict["dont_export"].reason
    
    assert "plain_func" in export_dict
    assert export_dict["plain_func"].python_name == "plain_func"

