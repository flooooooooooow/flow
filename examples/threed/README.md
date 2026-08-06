# 3D examples

Eight programs on `lib/stdlib/render3d.flow`, a software rasterizer written in
Flow. No GPU is involved: each frame is a packed RGB8 buffer filled a pixel at a
time and handed to `gfx_blit_rgb` once.

```bash
./flow gfx examples/threed/spinning_solids.flow          # native window
./flow record examples/threed/spinning_solids.flow --frames 90 --gif out.gif
```

The renderer's pipeline, matrix conventions, fixed caps and limitations are in
[docs/language/graphics-3d.md](../../docs/language/graphics-3d.md). Recorded
clips are in [docs/demos/threed/](../../docs/demos/threed/).

| Example | What it is for | Frame cost | Clip |
|---|---|---:|---|
| `spinning_solids.flow` | The five Platonic solids from vertex lists alone: faces recovered by a convex-hull plane sweep, then fan-triangulated. Wire, flat, Gouraud and unlit side by side. | 0.27 ms | [gif](../../docs/demos/threed/spinning_solids.gif) |
| `raycast_shooter.flow` | Ray-vs-AABB picking and hitscan from the same `r3d_ray_aabb` query, so the crosshair highlight and the shot cannot disagree. Waves, score, accuracy. | 0.66 ms | [gif](../../docs/demos/threed/raycast_shooter.gif) |
| `physics3d.flow` | Rigid spheres under gravity: sphere-plane and sphere-sphere impulse response with restitution, and an honest energy readout that falls to the resting potential. | 0.75 ms | [gif](../../docs/demos/threed/physics3d.gif) |
| `heightmap_terrain.flow` | Four octaves of value noise on a 64 x 64 grid, walked in first person with linear distance fog. Deterministic from a fixed seed. | 1.11 ms | [gif](../../docs/demos/threed/heightmap_terrain.gif) |
| `billboard_particles.flow` | Up to 1200 alpha-blended billboards ordered far to near by a counting sort on quantized depth, tested against solid geometry that writes depth. | 1.15 ms | [gif](../../docs/demos/threed/billboard_particles.gif) |
| `fps_camera.flow` | Yaw and pitch camera, per-axis collision resolution against a box level, gravity and jumping at a fixed step. | 1.16 ms | [gif](../../docs/demos/threed/fps_camera.gif) |
| `voxel_world.flow` | A 24 x 16 x 24 block field in 8^3 chunks: empty chunks skipped whole, faces emitted only against air, and a raycast block selector. | 1.45 ms | [gif](../../docs/demos/threed/voxel_world.gif) |
| `third_person.flow` | Chase camera with orbit, smoothing, and occlusion pull-in that casts `r3d_ray_aabb` back from the avatar so the view never clips through a wall. | 1.48 ms | [gif](../../docs/demos/threed/third_person.gif) |

Frame cost is 600 presented frames through the headless recorder with frame
writeout disabled, at 480 x 360 on an Apple M4 Max with `clang -O2`. It is a
compute cost, not a display rate. Every example also shows its own measured
frame time on the HUD.

## Shared controls

Arrows look or orbit, WASD moves where there is something to move, Space is the
per-program action, R resets, Esc quits. Each file's header comment lists its
own keys.

## Environment switches

Three examples print structured output when asked, which is how their claims
were checked:

| Variable | Example | What it prints |
|---|---|---|
| `FLOW_PHYS_LOG=1` | `physics3d.flow` | KE, PE, total energy and E/E0 every 30 frames, plus frame cost |
| `FLOW_PHYS_PROBE=N` | `physics3d.flow` | Moves the per-sphere projection probe to frame N |
| `FLOW_SHOOT_LOG=1` | `raycast_shooter.flow` | A line whenever the aimed target changes, and one per shot |
| `FLOW_PART_LOG=1` | `billboard_particles.flow` | Sort quality at frame 45 and how many particles each pillar hides |
