# Patches for sibling repos

## `doom-flow-mlir-o2.patch`

Apply on [doom-flow](https://github.com/godofecht/doom-flow) `main` after Flow `#257`:

```bash
cd ~/doom-flow
git apply ~/flow/docs/project/patches/doom-flow-mlir-o2.patch
```

Switches `BACKEND=mlir` to `emcc -O2` and drops the stale
`fix/mlir-static-string-arrays` checkout gate (flow#253 / #254).

Please also close flow#253 and #254, and refresh the checklist on flow#256.
