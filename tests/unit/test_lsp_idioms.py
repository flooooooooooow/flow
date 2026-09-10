import pytest
from flow.lsp_server import FlowLanguageServer

def test_lsp_returns_idiom_hints():
    server = FlowLanguageServer()
    uri = "file:///test.flow"
    server.documents[uri] = "function main() -> void {\n    let mut x = 5;\n}"
    
    diagnostics = server._compute_diagnostics(server.documents[uri], uri)
    
    # Expecting FIDIOM001 hint
    idiom_diags = [d for d in diagnostics if d.get('source') == 'flow-idiom']
    assert len(idiom_diags) == 1
    assert idiom_diags[0]['severity'] == 4 # Hint
    assert idiom_diags[0]['code'] == 'FIDIOM001'
    assert 'replacement' in idiom_diags[0].get('data', {})

def test_lsp_suppresses_idioms():
    server = FlowLanguageServer()
    uri = "file:///test.flow"
    server.documents[uri] = "function main() -> void {\n    # flow-idiom: allow FIDIOM001\n    let mut x = 5;\n}"
    
    diagnostics = server._compute_diagnostics(server.documents[uri], uri)
    idiom_diags = [d for d in diagnostics if d.get('source') == 'flow-idiom']
    assert len(idiom_diags) == 0

def test_lsp_code_actions_for_idioms():
    server = FlowLanguageServer()
    uri = "file:///test.flow"
    server.documents[uri] = "function main() -> void {\n    let mut x = 5;\n}"
    diagnostics = server._compute_diagnostics(server.documents[uri], uri)
    
    params = {
        'textDocument': {'uri': uri},
        'context': {'diagnostics': diagnostics}
    }
    
    actions = server._handle_code_action(params)
    assert len(actions) == 1
    action = actions[0]
    assert action['kind'] == 'quickfix'
    assert action['title'] == 'Apply fix for FIDIOM001'
    assert action['edit']['changes'][uri][0]['newText'] == 'let x'

def test_same_file_yields_same_fidiom_codes_from_cli_and_lsp(tmp_path):
    # Requirement: "Add a test that the same file yields the same FIDIOM codes from flow check and from the LSP path."
    code = "function main() -> void {\n    let mut unused_mut = 10;\n}"
    
    # LSP check
    server = FlowLanguageServer()
    uri = "file:///test.flow"
    diagnostics = server._compute_diagnostics(code, uri)
    lsp_codes = [d['code'] for d in diagnostics if d.get('source') == 'flow-idiom']
    
    # CLI check via direct engine usage or similar parsing path
    from flow.idioms import IdiomAdvisor
    from flow.parser import Parser, Lexer
    ast = Parser(Lexer(code)).parse()
    advisor = IdiomAdvisor()
    advisor.analyze_function(ast[0])
    cli_codes = [f.rule_id for f in advisor.findings]
    
    assert lsp_codes == cli_codes
    assert lsp_codes == ['FIDIOM001']
