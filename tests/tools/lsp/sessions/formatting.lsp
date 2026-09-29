# Formatting and range formatting: a messy fixture, an already formatted
# file, a file that does not parse, and repository files.
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"capabilities":{}}}
@open file:///t/messy.flow tests/tools/lsp/fixtures/messy.flow
{"jsonrpc":"2.0","id":2,"method":"textDocument/formatting","params":{"textDocument":{"uri":"file:///t/messy.flow"},"options":{"tabSize":4,"insertSpaces":true}}}
{"jsonrpc":"2.0","id":3,"method":"textDocument/rangeFormatting","params":{"textDocument":{"uri":"file:///t/messy.flow"},"range":{"start":{"line":0,"character":0},"end":{"line":1,"character":0}},"options":{"tabSize":4,"insertSpaces":true}}}
@open file:///t/broken.flow tests/tools/lsp/fixtures/broken.flow
{"jsonrpc":"2.0","id":4,"method":"textDocument/formatting","params":{"textDocument":{"uri":"file:///t/broken.flow"},"options":{"tabSize":4,"insertSpaces":true}}}
@open file:///t/clean.flow tests/tools/lsp/fixtures/clean.flow
{"jsonrpc":"2.0","id":5,"method":"textDocument/formatting","params":{"textDocument":{"uri":"file:///t/clean.flow"},"options":{"tabSize":4,"insertSpaces":true}}}
@open file:///t/params.flow tests/tools/lsp/fixtures/params.flow
{"jsonrpc":"2.0","id":6,"method":"textDocument/formatting","params":{"textDocument":{"uri":"file:///t/params.flow"},"options":{"tabSize":4,"insertSpaces":true}}}
@open file://@ROOT@/examples/basics/fibonacci.flow examples/basics/fibonacci.flow
{"jsonrpc":"2.0","id":7,"method":"textDocument/formatting","params":{"textDocument":{"uri":"file://@ROOT@/examples/basics/fibonacci.flow"},"options":{"tabSize":4,"insertSpaces":true}}}
@open file://@ROOT@/examples/basics/gcd.flow examples/basics/gcd.flow
{"jsonrpc":"2.0","id":8,"method":"textDocument/formatting","params":{"textDocument":{"uri":"file://@ROOT@/examples/basics/gcd.flow"},"options":{"tabSize":4,"insertSpaces":true}}}
{"jsonrpc":"2.0","id":9,"method":"shutdown","params":null}
{"jsonrpc":"2.0","method":"exit","params":null}
