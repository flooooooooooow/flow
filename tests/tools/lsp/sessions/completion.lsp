# Completion: prefixes over locals, keywords, built-ins, stdlib exports,
# dynamics and ordering snippets, struct fields after a dot, and the
# empty-prefix list (ported from tests/unit/test_lsp_hover.py and
# tests/unit/test_lsp_intel.py).
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"capabilities":{}}}
@open file:///t/compl_an.flow tests/tools/lsp/fixtures/compl_an.flow
{"jsonrpc":"2.0","id":2,"method":"textDocument/completion","params":{"textDocument":{"uri":"file:///t/compl_an.flow"},"position":{"line":2,"character":13}}}
{"jsonrpc":"2.0","id":3,"method":"textDocument/completion","params":{"textDocument":{"uri":"file:///t/compl_an.flow"},"position":{"line":2,"character":11}}}
@open file:///t/compl_ad.flow tests/tools/lsp/fixtures/compl_ad.flow
{"jsonrpc":"2.0","id":4,"method":"textDocument/completion","params":{"textDocument":{"uri":"file:///t/compl_ad.flow"},"position":{"line":1,"character":13}}}
@open file:///t/field_dot.flow tests/tools/lsp/fixtures/field_dot.flow
{"jsonrpc":"2.0","id":5,"method":"textDocument/completion","params":{"textDocument":{"uri":"file:///t/field_dot.flow"},"position":{"line":4,"character":13}}}
@open file:///t/field.flow tests/tools/lsp/fixtures/field.flow
{"jsonrpc":"2.0","id":6,"method":"textDocument/completion","params":{"textDocument":{"uri":"file:///t/field.flow"},"position":{"line":4,"character":14}}}
{"jsonrpc":"2.0","id":7,"method":"textDocument/completion","params":{"textDocument":{"uri":"file:///t/field.flow"},"position":{"line":2,"character":0}}}
@open file:///t/dsl.flow tests/tools/lsp/fixtures/dsl.flow
{"jsonrpc":"2.0","id":8,"method":"textDocument/completion","params":{"textDocument":{"uri":"file:///t/dsl.flow"},"position":{"line":0,"character":6}}}
{"jsonrpc":"2.0","id":9,"method":"textDocument/completion","params":{"textDocument":{"uri":"file:///t/dsl.flow"},"position":{"line":7,"character":11}}}
{"jsonrpc":"2.0","id":10,"method":"textDocument/completion","params":{"textDocument":{"uri":"file:///t/dsl.flow"},"position":{"line":1,"character":6}}}
{"jsonrpc":"2.0","id":11,"method":"textDocument/completion","params":{"textDocument":{"uri":"file:///t/dsl.flow"},"position":{"line":8,"character":5}}}
@open file:///t/const_effect.flow tests/tools/lsp/fixtures/const_effect.flow
{"jsonrpc":"2.0","id":12,"method":"textDocument/completion","params":{"textDocument":{"uri":"file:///t/const_effect.flow"},"position":{"line":8,"character":12}}}
{"jsonrpc":"2.0","id":13,"method":"textDocument/completion","params":{"textDocument":{"uri":"file:///t/const_effect.flow"},"position":{"line":4,"character":6}}}
{"jsonrpc":"2.0","id":14,"method":"shutdown","params":null}
{"jsonrpc":"2.0","method":"exit","params":null}
