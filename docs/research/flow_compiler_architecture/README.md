# Flow Compiler Architecture (arXiv-style preprint)

LaTeX preprint describing the Flow dual-host compiler architecture:
production Python→C pipeline, algebraic-effect lowering, surface expanders,
secondary backends, and Stage-A `flowc` self-hosting bootstrap.

## Build PDF

```bash
cd docs/research/flow_compiler_architecture
pdflatex flow_compiler_architecture.tex
pdflatex flow_compiler_architecture.tex   # second pass for refs
```

Requires a standard TeX distribution (`pdflatex`, packages: `tikz`, `booktabs`,
`hyperref`, `listings`, `algorithm`/`algpseudocode`, `authblk`).

## arXiv upload

Upload `flow_compiler_architecture.tex` (and the PDF if desired) as a standard
`article`-class single-file submission. No external figures are required; the
pipeline diagram is TikZ-generated.

## Source of truth

Claims are calibrated against repository docs as of August 2026:

- `compiler/README.md`
- `docs/project/self-hosting.md`
- `docs/language/dynamics-dsl.md`
- `docs/effects-showcase.md`
- `docs/library/autodiff.md`
- `docs/language/wasm.md`
- `docs/comparison.md`
