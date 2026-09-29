# Repository files: didOpen diagnostics and documentSymbol over the stdlib,
# examples (effects, enums, dynamics DSL, proofs), a tests/lang program and
# a compiler source file.
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"capabilities":{}}}
@open file://@ROOT@/lib/stdlib/math.flow lib/stdlib/math.flow
{"jsonrpc":"2.0","id":2,"method":"textDocument/documentSymbol","params":{"textDocument":{"uri":"file://@ROOT@/lib/stdlib/math.flow"}}}
@open file://@ROOT@/lib/stdlib/option.flow lib/stdlib/option.flow
{"jsonrpc":"2.0","id":3,"method":"textDocument/documentSymbol","params":{"textDocument":{"uri":"file://@ROOT@/lib/stdlib/option.flow"}}}
@open file://@ROOT@/examples/basics/fibonacci.flow examples/basics/fibonacci.flow
{"jsonrpc":"2.0","id":4,"method":"textDocument/documentSymbol","params":{"textDocument":{"uri":"file://@ROOT@/examples/basics/fibonacci.flow"}}}
@open file://@ROOT@/examples/effects/async_effects.flow examples/effects/async_effects.flow
{"jsonrpc":"2.0","id":5,"method":"textDocument/documentSymbol","params":{"textDocument":{"uri":"file://@ROOT@/examples/effects/async_effects.flow"}}}
@open file://@ROOT@/examples/generics_traits/enums_demo.flow examples/generics_traits/enums_demo.flow
{"jsonrpc":"2.0","id":6,"method":"textDocument/documentSymbol","params":{"textDocument":{"uri":"file://@ROOT@/examples/generics_traits/enums_demo.flow"}}}
@open file://@ROOT@/examples/dynamics/controllability_demo.flow examples/dynamics/controllability_demo.flow
{"jsonrpc":"2.0","id":7,"method":"textDocument/documentSymbol","params":{"textDocument":{"uri":"file://@ROOT@/examples/dynamics/controllability_demo.flow"}}}
@open file://@ROOT@/examples/verify/analysis/sine-derivatives-at-zero.flow examples/verify/analysis/sine-derivatives-at-zero.flow
{"jsonrpc":"2.0","id":8,"method":"textDocument/documentSymbol","params":{"textDocument":{"uri":"file://@ROOT@/examples/verify/analysis/sine-derivatives-at-zero.flow"}}}
@open file://@ROOT@/tests/lang/test_generics.flow tests/lang/test_generics.flow
{"jsonrpc":"2.0","id":9,"method":"textDocument/documentSymbol","params":{"textDocument":{"uri":"file://@ROOT@/tests/lang/test_generics.flow"}}}
@open file://@ROOT@/compiler/src/lsp_utils.flow compiler/src/lsp_utils.flow
{"jsonrpc":"2.0","id":10,"method":"textDocument/documentSymbol","params":{"textDocument":{"uri":"file://@ROOT@/compiler/src/lsp_utils.flow"}}}
@open file://@ROOT@/examples/packages/use_hello_lib/src/main.flow examples/packages/use_hello_lib/src/main.flow
{"jsonrpc":"2.0","id":11,"method":"textDocument/documentSymbol","params":{"textDocument":{"uri":"file://@ROOT@/examples/packages/use_hello_lib/src/main.flow"}}}
@open file:///t/const_effect.flow tests/tools/lsp/fixtures/const_effect.flow
{"jsonrpc":"2.0","id":12,"method":"textDocument/documentSymbol","params":{"textDocument":{"uri":"file:///t/const_effect.flow"}}}
{"jsonrpc":"2.0","id":13,"method":"shutdown","params":null}
{"jsonrpc":"2.0","method":"exit","params":null}
