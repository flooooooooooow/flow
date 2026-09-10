from flow.idioms import IdiomAdvisor, IdiomFinding
from flow.parser import Parser, Lexer

def test_fidiom001_detects_unused_mut():
    code = """
    function main() -> void {
        let mut x = 5;
        let mut y = 10;
        y = 20;
    }
    """
    ast = Parser(Lexer(code)).parse()
    advisor = IdiomAdvisor()
    advisor.analyze_function(ast[0])
    
    findings = advisor.findings
    assert len(findings) == 1
    assert findings[0].rule_id == "FIDIOM001"
    assert "Variable 'x' is declared 'mut' but is never reassigned" in findings[0].rationale

def test_fidiom001_ignores_used_mut():
    code = """
    function main() -> void {
        let mut x = 5;
        x = 10;
    }
    """
    ast = Parser(Lexer(code)).parse()
    advisor = IdiomAdvisor()
    advisor.analyze_function(ast[0])
    
    assert len(advisor.findings) == 0

def test_fidiom002_redundant_return_shapes():
    code = """
    struct Point { x: i32, y: i32 }
    function main() -> Point {
        let p = Point{x: 1, y: 2};
        return Point{x: p.x, y: p.y};
    }
    """
    ast = Parser(Lexer(code)).parse()
    advisor = IdiomAdvisor()
    advisor.analyze_function(ast[1])
    
    findings = advisor.findings
    assert len(findings) == 1
    assert findings[0].rule_id == "FIDIOM002"
    assert "Redundant return shape" in findings[0].title
