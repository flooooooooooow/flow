# Definition: locals, parameters, struct fields, same-file and cross-file
# symbols, imported symbols and stdlib exports (ported from
# tests/unit/test_lsp_hover.py and tests/unit/test_lsp_intel.py).
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"capabilities":{}}}
@open file:///t/clean.flow tests/tools/lsp/fixtures/clean.flow
@open file:///t/other.flow tests/tools/lsp/fixtures/other.flow
{"jsonrpc":"2.0","id":2,"method":"textDocument/definition","params":{"textDocument":{"uri":"file:///t/clean.flow"},"position":{"line":11,"character":12}}}
{"jsonrpc":"2.0","id":3,"method":"textDocument/definition","params":{"textDocument":{"uri":"file:///t/clean.flow"},"position":{"line":11,"character":17}}}
{"jsonrpc":"2.0","id":4,"method":"textDocument/definition","params":{"textDocument":{"uri":"file:///t/clean.flow"},"position":{"line":6,"character":17}}}
{"jsonrpc":"2.0","id":5,"method":"textDocument/definition","params":{"textDocument":{"uri":"file:///t/clean.flow"},"position":{"line":6,"character":19}}}
{"jsonrpc":"2.0","id":6,"method":"textDocument/definition","params":{"textDocument":{"uri":"file:///t/other.flow"},"position":{"line":2,"character":12}}}
{"jsonrpc":"2.0","id":7,"method":"textDocument/definition","params":{"textDocument":{"uri":"file:///t/other.flow"},"position":{"line":1,"character":13}}}
{"jsonrpc":"2.0","id":8,"method":"textDocument/definition","params":{"textDocument":{"uri":"file:///t/clean.flow"},"position":{"line":6,"character":11}}}
{"jsonrpc":"2.0","id":9,"method":"textDocument/definition","params":{"textDocument":{"uri":"file:///t/clean.flow"},"position":{"line":4,"character":0}}}
@open file:///t/field.flow tests/tools/lsp/fixtures/field.flow
{"jsonrpc":"2.0","id":10,"method":"textDocument/definition","params":{"textDocument":{"uri":"file:///t/field.flow"},"position":{"line":4,"character":13}}}
@open file:///t/stdlib_add.flow tests/tools/lsp/fixtures/stdlib_add.flow
{"jsonrpc":"2.0","id":11,"method":"textDocument/definition","params":{"textDocument":{"uri":"file:///t/stdlib_add.flow"},"position":{"line":1,"character":11}}}
@open file:///t/params.flow tests/tools/lsp/fixtures/params.flow
{"jsonrpc":"2.0","id":12,"method":"textDocument/definition","params":{"textDocument":{"uri":"file:///t/params.flow"},"position":{"line":2,"character":20}}}
{"jsonrpc":"2.0","id":13,"method":"textDocument/definition","params":{"textDocument":{"uri":"file:///t/params.flow"},"position":{"line":2,"character":4}}}
@open file://@ROOT@/examples/packages/use_hello_lib/src/main.flow examples/packages/use_hello_lib/src/main.flow
{"jsonrpc":"2.0","id":14,"method":"textDocument/definition","params":{"textDocument":{"uri":"file://@ROOT@/examples/packages/use_hello_lib/src/main.flow"},"position":{"line":19,"character":7}}}
{"jsonrpc":"2.0","id":15,"method":"textDocument/definition","params":{"textDocument":{"uri":"file://@ROOT@/examples/packages/use_hello_lib/src/main.flow"},"position":{"line":16,"character":5}}}
{"jsonrpc":"2.0","id":16,"method":"shutdown","params":null}
{"jsonrpc":"2.0","method":"exit","params":null}
