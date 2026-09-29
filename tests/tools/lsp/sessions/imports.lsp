# Imported symbols through `export import` forwards and a chain of them:
# hover, definition in the declaring file, completion and diagnostics
# (ported from tests/unit/test_module_reexport.py::TestLspFollowsReexports
# and tests/unit/test_lsp_intel.py).
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"capabilities":{}}}
@open file://@ROOT@/tests/fixtures/modules/consumer_reexport.flow tests/fixtures/modules/consumer_reexport.flow
{"jsonrpc":"2.0","id":2,"method":"textDocument/hover","params":{"textDocument":{"uri":"file://@ROOT@/tests/fixtures/modules/consumer_reexport.flow"},"position":{"line":5,"character":11}}}
{"jsonrpc":"2.0","id":3,"method":"textDocument/definition","params":{"textDocument":{"uri":"file://@ROOT@/tests/fixtures/modules/consumer_reexport.flow"},"position":{"line":5,"character":11}}}
{"jsonrpc":"2.0","id":4,"method":"textDocument/definition","params":{"textDocument":{"uri":"file://@ROOT@/tests/fixtures/modules/consumer_reexport.flow"},"position":{"line":5,"character":39}}}
{"jsonrpc":"2.0","id":5,"method":"textDocument/definition","params":{"textDocument":{"uri":"file://@ROOT@/tests/fixtures/modules/consumer_reexport.flow"},"position":{"line":5,"character":52}}}
{"jsonrpc":"2.0","id":6,"method":"textDocument/hover","params":{"textDocument":{"uri":"file://@ROOT@/tests/fixtures/modules/consumer_reexport.flow"},"position":{"line":5,"character":52}}}
{"jsonrpc":"2.0","id":7,"method":"textDocument/documentSymbol","params":{"textDocument":{"uri":"file://@ROOT@/tests/fixtures/modules/consumer_reexport.flow"}}}
@open file://@ROOT@/tests/fixtures/modules/consumer_reexport_chain.flow tests/fixtures/modules/consumer_reexport_chain.flow
{"jsonrpc":"2.0","id":8,"method":"textDocument/definition","params":{"textDocument":{"uri":"file://@ROOT@/tests/fixtures/modules/consumer_reexport_chain.flow"},"position":{"line":5,"character":11}}}
{"jsonrpc":"2.0","id":9,"method":"textDocument/hover","params":{"textDocument":{"uri":"file://@ROOT@/tests/fixtures/modules/consumer_reexport_chain.flow"},"position":{"line":5,"character":25}}}
{"jsonrpc":"2.0","id":10,"method":"shutdown","params":null}
{"jsonrpc":"2.0","method":"exit","params":null}
