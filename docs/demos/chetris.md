# Chetris — flagship real-world project (#114)

Chetris is Flow’s substantial gameplay showcase: a Chess × Tetris hybrid with
both a headless mechanics suite and a full graphical client.

## Artifacts

| Path | Role |
|------|------|
| `examples/games/chetris_gfx.flow` | Interactive graphical game (~1100 lines) |
| `examples/games/chetris.flow` | Logic-oriented variant |
| `examples/games/chetris_test.flow` | Deterministic core-mechanics suite |
| `examples/games/tetris_gfx.flow` | Complete graphical Tetris sibling |
| `docs/demos/tetris.gif` | Recorded Tetris demo |

## Acceptance checklist

- [x] Piece mapping (tetromino → chess piece) covered in `chetris_test.flow`
- [x] King detection / board indexing covered
- [x] Line clear + gravity covered
- [x] `./flow run examples/games/chetris_test.flow` exits 0 (“All tests passed”)
- [x] Graphical launch documented:

```bash
./flow gfx examples/games/chetris_gfx.flow
./flow gfx examples/games/tetris_gfx.flow
```

## Related substantial apps

- `apps/flowdb/flowdb.flow` — in-memory CRUD store
- `examples/linalg/` — matrix ops / LU
- `examples/ml/` + `examples/neural_networks/` — training demos
- `examples/dynamics/ga_full_analysis.flow` — dynamics/GA analysis

Together these satisfy the “real-world projects” roadmap bar: non-trivial,
userable, end-to-end Flow programs beyond compiler unit tests.
