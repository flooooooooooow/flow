# initialize, unknown requests, string and numeric ids, requests for a
# document that was never opened, shutdown, exit
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"processId":null,"rootUri":null,"capabilities":{}}}
{"jsonrpc":"2.0","method":"initialized","params":{}}
{"jsonrpc":"2.0","id":"init-2","method":"initialize","params":{}}
{"jsonrpc":"2.0","id":3,"method":"workspace/symbol","params":{"query":"x"}}
{"jsonrpc":"2.0","method":"$/cancelRequest","params":{"id":3}}
{"jsonrpc":"2.0","id":4,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///never/opened.flow"},"position":{"line":0,"character":0}}}
{"jsonrpc":"2.0","id":5,"method":"textDocument/documentSymbol","params":{"textDocument":{"uri":"file:///never/opened.flow"}}}
{"jsonrpc":"2.0","id":6,"method":"textDocument/formatting","params":{"textDocument":{"uri":"file:///never/opened.flow"},"options":{"tabSize":4,"insertSpaces":true}}}
{"jsonrpc":"2.0","id":7,"method":"textDocument/documentHighlight","params":{"textDocument":{"uri":"file:///never/opened.flow"},"position":{"line":0,"character":0}}}
{"jsonrpc":"2.0","id":8,"method":"shutdown","params":null}
{"jsonrpc":"2.0","method":"exit","params":null}
