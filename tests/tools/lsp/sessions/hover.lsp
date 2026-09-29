# Hover: operators, keywords, attributes, dynamics and ordering catalogs,
# locals and parameters, doc comments, consts, effects, struct fields,
# built-ins, stdlib and imported symbols (ported from
# tests/unit/test_lsp_hover.py and tests/unit/test_lsp_intel.py).
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"capabilities":{}}}
@open file:///t/pipe.flow tests/tools/lsp/fixtures/pipe.flow
{"jsonrpc":"2.0","id":2,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/pipe.flow"},"position":{"line":0,"character":3}}}
{"jsonrpc":"2.0","id":3,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/pipe.flow"},"position":{"line":0,"character":4}}}
{"jsonrpc":"2.0","id":4,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/pipe.flow"},"position":{"line":0,"character":6}}}
{"jsonrpc":"2.0","id":5,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/pipe.flow"},"position":{"line":0,"character":0}}}
@open file:///t/match.flow tests/tools/lsp/fixtures/match.flow
{"jsonrpc":"2.0","id":6,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/match.flow"},"position":{"line":1,"character":4}}}
{"jsonrpc":"2.0","id":7,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/match.flow"},"position":{"line":2,"character":8}}}
{"jsonrpc":"2.0","id":8,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/match.flow"},"position":{"line":2,"character":17}}}
{"jsonrpc":"2.0","id":9,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/match.flow"},"position":{"line":3,"character":0}}}
@open file:///t/docfn.flow tests/tools/lsp/fixtures/docfn.flow
{"jsonrpc":"2.0","id":10,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/docfn.flow"},"position":{"line":7,"character":11}}}
{"jsonrpc":"2.0","id":11,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/docfn.flow"},"position":{"line":2,"character":0}}}
{"jsonrpc":"2.0","id":12,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/docfn.flow"},"position":{"line":2,"character":19}}}
{"jsonrpc":"2.0","id":13,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/docfn.flow"},"position":{"line":2,"character":24}}}
{"jsonrpc":"2.0","id":14,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/docfn.flow"},"position":{"line":3,"character":11}}}
@open file:///t/params.flow tests/tools/lsp/fixtures/params.flow
{"jsonrpc":"2.0","id":15,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/params.flow"},"position":{"line":1,"character":25}}}
{"jsonrpc":"2.0","id":16,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/params.flow"},"position":{"line":2,"character":4}}}
{"jsonrpc":"2.0","id":17,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/params.flow"},"position":{"line":0,"character":9}}}
@open file:///t/shadow_sort.flow tests/tools/lsp/fixtures/shadow_sort.flow
{"jsonrpc":"2.0","id":18,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/shadow_sort.flow"},"position":{"line":1,"character":11}}}
@open file:///t/const_effect.flow tests/tools/lsp/fixtures/const_effect.flow
{"jsonrpc":"2.0","id":19,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/const_effect.flow"},"position":{"line":8,"character":11}}}
{"jsonrpc":"2.0","id":20,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/const_effect.flow"},"position":{"line":3,"character":7}}}
@open file:///t/field.flow tests/tools/lsp/fixtures/field.flow
{"jsonrpc":"2.0","id":21,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/field.flow"},"position":{"line":4,"character":13}}}
{"jsonrpc":"2.0","id":22,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/field.flow"},"position":{"line":4,"character":11}}}
{"jsonrpc":"2.0","id":23,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/field.flow"},"position":{"line":0,"character":8}}}
@open file:///t/typed_local.flow tests/tools/lsp/fixtures/typed_local.flow
{"jsonrpc":"2.0","id":24,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/typed_local.flow"},"position":{"line":3,"character":11}}}
@open file:///t/stdlib_add.flow tests/tools/lsp/fixtures/stdlib_add.flow
{"jsonrpc":"2.0","id":25,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/stdlib_add.flow"},"position":{"line":1,"character":11}}}
@open file:///t/sin_call.flow tests/tools/lsp/fixtures/sin_call.flow
{"jsonrpc":"2.0","id":26,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/sin_call.flow"},"position":{"line":1,"character":11}}}
@open file:///t/clean.flow tests/tools/lsp/fixtures/clean.flow
{"jsonrpc":"2.0","id":27,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/clean.flow"},"position":{"line":6,"character":11}}}
{"jsonrpc":"2.0","id":28,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/clean.flow"},"position":{"line":5,"character":17}}}
{"jsonrpc":"2.0","id":29,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/clean.flow"},"position":{"line":5,"character":9}}}
{"jsonrpc":"2.0","id":30,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/clean.flow"},"position":{"line":11,"character":8}}}
{"jsonrpc":"2.0","id":31,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/clean.flow"},"position":{"line":6,"character":19}}}
@open file:///t/attr.flow tests/tools/lsp/fixtures/attr.flow
{"jsonrpc":"2.0","id":32,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/attr.flow"},"position":{"line":0,"character":0}}}
{"jsonrpc":"2.0","id":33,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/attr.flow"},"position":{"line":0,"character":2}}}
{"jsonrpc":"2.0","id":34,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/attr.flow"},"position":{"line":5,"character":3}}}
{"jsonrpc":"2.0","id":35,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/attr.flow"},"position":{"line":2,"character":12}}}
@open file:///t/dsl.flow tests/tools/lsp/fixtures/dsl.flow
{"jsonrpc":"2.0","id":36,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/dsl.flow"},"position":{"line":0,"character":5}}}
{"jsonrpc":"2.0","id":37,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/dsl.flow"},"position":{"line":0,"character":1}}}
{"jsonrpc":"2.0","id":38,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/dsl.flow"},"position":{"line":1,"character":6}}}
{"jsonrpc":"2.0","id":39,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/dsl.flow"},"position":{"line":7,"character":10}}}
{"jsonrpc":"2.0","id":40,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/dsl.flow"},"position":{"line":7,"character":19}}}
{"jsonrpc":"2.0","id":41,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/dsl.flow"},"position":{"line":8,"character":4}}}
{"jsonrpc":"2.0","id":42,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/dsl.flow"},"position":{"line":8,"character":14}}}
{"jsonrpc":"2.0","id":43,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/dsl.flow"},"position":{"line":8,"character":8}}}
{"jsonrpc":"2.0","id":44,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/dsl.flow"},"position":{"line":9,"character":8}}}
{"jsonrpc":"2.0","id":45,"method":"textDocument/hover","params":{"textDocument":{"uri":"file:///t/dsl.flow"},"position":{"line":6,"character":14}}}
@open file://@ROOT@/examples/packages/use_hello_lib/src/main.flow examples/packages/use_hello_lib/src/main.flow
{"jsonrpc":"2.0","id":46,"method":"textDocument/hover","params":{"textDocument":{"uri":"file://@ROOT@/examples/packages/use_hello_lib/src/main.flow"},"position":{"line":19,"character":7}}}
{"jsonrpc":"2.0","id":47,"method":"textDocument/hover","params":{"textDocument":{"uri":"file://@ROOT@/examples/packages/use_hello_lib/src/main.flow"},"position":{"line":16,"character":5}}}
{"jsonrpc":"2.0","id":48,"method":"textDocument/hover","params":{"textDocument":{"uri":"file://@ROOT@/examples/packages/use_hello_lib/src/main.flow"},"position":{"line":13,"character":14}}}
@open file://@ROOT@/lib/stdlib/math.flow lib/stdlib/math.flow
{"jsonrpc":"2.0","id":49,"method":"textDocument/hover","params":{"textDocument":{"uri":"file://@ROOT@/lib/stdlib/math.flow"},"position":{"line":8,"character":17}}}
{"jsonrpc":"2.0","id":50,"method":"textDocument/hover","params":{"textDocument":{"uri":"file://@ROOT@/lib/stdlib/math.flow"},"position":{"line":9,"character":11}}}
{"jsonrpc":"2.0","id":51,"method":"shutdown","params":null}
{"jsonrpc":"2.0","method":"exit","params":null}
