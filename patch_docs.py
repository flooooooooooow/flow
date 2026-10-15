import re

with open('docs/design/mlir-in-flow.md', 'r') as f:
    code = f.read()

code = code.replace('''* Forms the emitter refuses: `impl Trait for Type` methods, which the
  parser skips; fields of a generic struct inferred at the call; two
  lowered forms of `test_lowered_forms.flow`; SIMD vector ops that
  mlir-opt does not know.''', '''* Forms the emitter refuses: `impl Trait for Type` methods, which the
  parser skips; fields of a generic struct inferred at the call; SIMD vector ops that
  mlir-opt does not know.''')

with open('docs/design/mlir-in-flow.md', 'w') as f:
    f.write(code)
