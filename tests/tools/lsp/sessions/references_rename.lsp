# references, documentHighlight, prepareRename and rename across two open
# files (ported from scripts/test_lsp_server.py).
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"capabilities":{}}}
@open file:///test/main.flow tests/tools/lsp/fixtures/clean.flow
@open file:///test/other.flow tests/tools/lsp/fixtures/other.flow
# norm: declaration, same-file call, cross-file call
{"jsonrpc":"2.0","id":2,"method":"textDocument/references","params":{"textDocument":{"uri":"file:///test/main.flow"},"position":{"line":5,"character":9},"context":{"includeDeclaration":true}}}
{"jsonrpc":"2.0","id":3,"method":"textDocument/references","params":{"textDocument":{"uri":"file:///test/main.flow"},"position":{"line":5,"character":9},"context":{"includeDeclaration":false}}}
# Point from its use in main
{"jsonrpc":"2.0","id":4,"method":"textDocument/references","params":{"textDocument":{"uri":"file:///test/main.flow"},"position":{"line":10,"character":13},"context":{"includeDeclaration":true}}}
# local p stays in this file
{"jsonrpc":"2.0","id":5,"method":"textDocument/references","params":{"textDocument":{"uri":"file:///test/main.flow"},"position":{"line":10,"character":8},"context":{"includeDeclaration":true}}}
{"jsonrpc":"2.0","id":6,"method":"textDocument/documentHighlight","params":{"textDocument":{"uri":"file:///test/main.flow"},"position":{"line":10,"character":8}}}
{"jsonrpc":"2.0","id":7,"method":"textDocument/documentHighlight","params":{"textDocument":{"uri":"file:///test/main.flow"},"position":{"line":5,"character":0}}}
# A mention in a comment is not a reference.
@change file:///test/main.flow tests/tools/lsp/fixtures/clean_commented.flow 20
@sleep
{"jsonrpc":"2.0","id":8,"method":"textDocument/references","params":{"textDocument":{"uri":"file:///test/main.flow"},"position":{"line":5,"character":9},"context":{"includeDeclaration":true}}}
{"jsonrpc":"2.0","id":9,"method":"textDocument/prepareRename","params":{"textDocument":{"uri":"file:///test/main.flow"},"position":{"line":5,"character":9}}}
{"jsonrpc":"2.0","id":10,"method":"textDocument/prepareRename","params":{"textDocument":{"uri":"file:///test/main.flow"},"position":{"line":5,"character":0}}}
{"jsonrpc":"2.0","id":11,"method":"textDocument/prepareRename","params":{"textDocument":{"uri":"file:///test/main.flow"},"position":{"line":4,"character":0}}}
{"jsonrpc":"2.0","id":12,"method":"textDocument/prepareRename","params":{"textDocument":{"uri":"file:///test/main.flow"},"position":{"line":15,"character":3}}}
{"jsonrpc":"2.0","id":13,"method":"textDocument/rename","params":{"textDocument":{"uri":"file:///test/main.flow"},"position":{"line":5,"character":9},"newName":"while"}}
{"jsonrpc":"2.0","id":14,"method":"textDocument/rename","params":{"textDocument":{"uri":"file:///test/main.flow"},"position":{"line":5,"character":9},"newName":"123abc"}}
{"jsonrpc":"2.0","id":15,"method":"textDocument/rename","params":{"textDocument":{"uri":"file:///test/main.flow"},"position":{"line":5,"character":0},"newName":"whatever"}}
{"jsonrpc":"2.0","id":16,"method":"textDocument/rename","params":{"textDocument":{"uri":"file:///test/main.flow"},"position":{"line":5,"character":9},"newName":"magnitude"}}
{"jsonrpc":"2.0","id":17,"method":"textDocument/rename","params":{"textDocument":{"uri":"file:///test/main.flow"},"position":{"line":10,"character":8},"newName":"origin"}}
{"jsonrpc":"2.0","id":18,"method":"shutdown","params":null}
{"jsonrpc":"2.0","method":"exit","params":null}
