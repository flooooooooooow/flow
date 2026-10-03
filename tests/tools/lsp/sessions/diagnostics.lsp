# Parse errors, type findings, a clean file, coalesced edits, idiom hints,
# code actions and didClose (ported from scripts/test_lsp_server.py and
# tests/unit/test_lsp_idioms.py).
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"capabilities":{}}}
@open file:///test/main.flow tests/tools/lsp/fixtures/broken.flow
@change file:///test/main.flow tests/tools/lsp/fixtures/type_error.flow 2
@sleep
@change file:///test/main.flow tests/tools/lsp/fixtures/clean.flow 3
@sleep
# Three rapid edits publish once, for the final text.
@change file:///test/main.flow tests/tools/lsp/fixtures/broken.flow 10
@change file:///test/main.flow tests/tools/lsp/fixtures/type_error.flow 11
@change file:///test/main.flow tests/tools/lsp/fixtures/clean.flow 12
@sleep
@open file:///test/idiom.flow tests/tools/lsp/fixtures/idiom.flow
{"jsonrpc":"2.0","id":2,"method":"textDocument/codeAction","params":{"textDocument":{"uri":"file:///test/idiom.flow"},"range":{"start":{"line":1,"character":4},"end":{"line":1,"character":11}},"context":{"diagnostics":[{"range":{"start":{"line":1,"character":4},"end":{"line":1,"character":11}},"severity":4,"source":"flow-idiom","code":"FIDIOM001","message":"m","data":{"replacement":"let x","rule_id":"FIDIOM001"}}]}}}
@open file:///test/idiom_allow.flow tests/tools/lsp/fixtures/idiom_allow.flow
@open file:///test/typed_local.flow tests/tools/lsp/fixtures/typed_local.flow
@open file:///test/const_effect.flow tests/tools/lsp/fixtures/const_effect.flow
@open file:///test/params.flow tests/tools/lsp/fixtures/params.flow
@open file:///test/match.flow tests/tools/lsp/fixtures/match.flow
@open file:///test/pipe.flow tests/tools/lsp/fixtures/pipe.flow
{"jsonrpc":"2.0","method":"textDocument/didClose","params":{"textDocument":{"uri":"file:///test/main.flow"}}}
{"jsonrpc":"2.0","id":3,"method":"shutdown","params":null}
{"jsonrpc":"2.0","method":"exit","params":null}
