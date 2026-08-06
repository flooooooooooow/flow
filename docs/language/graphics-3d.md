# 3D in Flow

`lib/stdlib/render3d.flow` is a software 3D renderer written in Flow. There is
no GPU, no driver and no shading language anywhere in it. A frame is a packed
RGB8 buffer that the renderer fills a pixel at a time and hands to
`gfx_blit_rgb` once, which is the only reason a per-pixel rasterizer is viable
through the 2D window API at all.

Everything on this page is in that one file plus the examples in
`examples/threed/`. For the 2D window API underneath it, see
[graphics.md](graphics.md).

```bash
./flow gfx examples/threed/spinning_solids.flow
./flow record examples/threed/physics3d.flow --frames 90 --gif docs/demos/threed/physics3d.gif
```

## Coordinates

Right-handed world space, +Y up. The projection is the OpenGL form, so `clip.w`
equals the view-space distance in front of the eye and NDC z runs from -1 at the
near plane to +1 at the far one. Screen y points down. The depth buffer stores
`(z + 1) / 2`, so smaller is nearer, and it is cleared to `1e30`.

A 4x4 matrix is `array<f32, 16>` in row-major order, applied to a column vector.
Builders take `out: ptr<f32>` and consumers take `&[f32]`. There is no `Mat4`
struct because module statics cannot hold structs, so a program declares its
matrices as fixed arrays in `main` and passes the pointers down.

```flow
let mut proj: array<f32, 16> = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
                                0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
let pproj: ptr<f32> = proj
m4_perspective(pproj, r3d_radians(60.0), r3d_aspect(), 0.1, 90.0)
```

## Pipeline

Seven stages, in the order a triangle goes through them.

| Stage | What happens | Entry points |
|---|---|---|
| 1. Mesh build | Positions, normals and base colours are appended to module-static arrays. | `r3d_mesh_reset`, `r3d_mesh_vertex`, `r3d_mesh_tri`, `r3d_mesh_quad`, `r3d_mesh_box`, `r3d_mesh_box_face`, `r3d_mesh_sphere` |
| 2. Vertex stage | Model matrix to world space, then the view-projection matrix to clip space. Normals go through the model matrix as directions. Per-vertex lighting and fog are evaluated here. | `r3d_draw_mesh` |
| 3. Near clipping | Sutherland-Hodgman against the single plane `w >= near`. One triangle becomes zero, one or two. This is what stops geometry behind the eye wrapping around the screen. | `r3d_clip_and_raster`, `r3d_set_near` |
| 4. Projection | Perspective divide, then the viewport map. | internal |
| 5. Culling | Signed screen-space area: back, front, or neither. | `r3d_set_cull` |
| 6. Rasterization | Edge functions over the bounding box, barycentric weights normalized by the signed area. Depth is the interpolated NDC z, linear in screen space. Colour is interpolated as c/w against 1/w and divided back, the perspective-correct form. | `r3d_raster_tri` |
| 7. Presentation | One `gfx_blit_rgb` of the whole colour buffer. HUD text is drawn afterwards with `stdlib/text.flow`, so it sits on top and is never depth-tested. | `r3d_present` |

Shading modes for `r3d_draw_mesh`: `R3D_WIRE`, `R3D_FLAT`, `R3D_GOURAUD`,
`R3D_UNLIT`. Lighting is one directional light plus a constant ambient term
(`r3d_set_ambient`), evaluated per vertex. Fog is linear between two distances
(`r3d_set_fog`) and is applied in the vertex stage as well, so it interpolates
across the triangle along with the colour.

Immediate-mode paths skip the mesh arrays: `r3d_tri` takes three world points
and three colours and goes straight to clipping; `r3d_line3` and `r3d_line_clip`
do the same for segments; `r3d_sprite` and `r3d_sprite_blend` draw a
screen-aligned disc at a world point.

`r3d_sprite_blend` reads the depth buffer and does not write it. That is what
lets solid geometry hide a sprite while two sprites still blend with each other,
and it is why the caller has to submit translucent sprites back to front.
`examples/threed/billboard_particles.flow` does that with a counting sort.

## Ray casting

The same geometry, queried instead of drawn. `r3d_ray_aabb` is the slab test and
returns the entry distance along a unit-length ray, or -1 for a miss;
`r3d_ray_sphere` returns the nearer root. `examples/threed/raycast_shooter.flow`
uses one `r3d_ray_aabb` query per frame for both the crosshair highlight and the
shot, so the highlight and the hit cannot disagree.

## Fixed limits

Every buffer is allocated once, in `r3d_init`, to these caps. Nothing grows and
nothing is freed.

| Constant | Value | What it bounds |
|---|---:|---|
| `R3D_MAX_W` | 640 | Framebuffer width |
| `R3D_MAX_H` | 480 | Framebuffer height |
| `R3D_MAX_VERTS` | 16384 | Vertices in the mesh at one time |
| `R3D_MAX_TRIS` | 24576 | Triangles in the mesh at one time |
| `R3D_CLIP_MAX` | 8 | Clip scratch vertices per triangle |
| `R3D_DEPTH_FAR` | 1e30 | Depth clear value |

640 x 480 of RGB8 plus a float depth buffer is 2.1 MB, which is the renderer's
whole memory budget apart from the mesh arrays. `r3d_init` returns false rather
than allocating past the cap. `r3d_mesh_vertex` returns -1 and `r3d_mesh_tri`
returns false when the mesh is full; neither aborts.

## Measured frame rates

All eight examples run at 480 x 360. Each number is 600 presented frames from
the headless recorder with frame writeout disabled
(`FLOW_GFX_RECORD_SKIP=1000`), so it is the cost of simulating, rasterizing and
compositing a frame with no PPM or window in the way. Apple M4 Max,
`clang -O2`, single thread.

| Example | ms / frame | frames / s | What dominates |
|---|---:|---:|---|
| `spinning_solids.flow` | 0.27 | 3727 | One convex solid, rebuilt on demand |
| `physics3d.flow` | 0.75 | 1330 | 14 UV spheres, 2688 triangles submitted, 91 pair tests |
| `raycast_shooter.flow` | 0.66 | 1511 | 10 boxes, a 22 x 22 ground grid, 10 ray tests |
| `heightmap_terrain.flow` | 1.11 | 902 | Terrain fill |
| `billboard_particles.flow` | 1.15 | 873 | ~1200 blended sprites, ~185k sprite pixels |
| `fps_camera.flow` | 1.16 | 860 | Level fill and per-axis collision |
| `voxel_world.flow` | 1.45 | 692 | Visible-face meshing and fill |
| `third_person.flow` | 1.48 | 678 | Character rig plus level fill |

Two things to read carefully. These are compute rates, not display rates: on a
real window the frame is capped by the compositor long before the rasterizer
runs out of headroom. And they are fill-bound, so they scale with pixels, not
with the frame budget you would get at a higher resolution. Doubling to
960 x 720 is roughly four times the fill.

The same numbers are on each example's HUD at run time. `r3d_tick` measures
process CPU time between calls and keeps an exponential moving average, so the
HUD figure is the cost of the frame on the machine running it. Recording to PPM
adds roughly 5 ms a frame at this resolution, which is why the frame rate on
a recorded GIF's HUD sits well below the table above.

## What is not here

Stated plainly, because a software renderer that pretends otherwise wastes your
time:

- **Software only.** No GPU path, no Metal, no Vulkan, no compute. One thread.
- **No texturing.** Colour is per vertex and interpolated. There is no
  sampler, no texture coordinate on a vertex, and no mipmaps. The UV sphere
  helper is named for its parameterization, not for a texture.
- **No shadows.** No shadow maps, no shadow volumes, no ambient occlusion. A
  surface facing away from the light is dark because of the Lambert term, and
  that is the whole of it.
- **One light.** A single directional light plus ambient, evaluated per vertex.
  No point lights, no specular term, no normal mapping.
- **Opaque meshes only.** The mesh path has no alpha blending. Translucency
  exists only in `r3d_sprite_blend`, which is a disc, and the caller sorts.
- **Near plane only.** Clipping is against `w >= near` and nothing else.
  Geometry off the sides of the screen is handled by the rasterizer's bounding
  box, which is correct but does more work than a side-plane clip would.
- **No top-left fill rule.** Triangles sharing an edge can write the same pixel
  twice in a frame. With a depth test that is invisible; without one it costs a
  little fill.
- **No multi-sampling.** Edges are hard. There is no coverage, no MSAA, no
  post-process antialiasing.
- **Fixed caps.** See the table above. Exceeding them drops geometry rather
  than growing a buffer.
- **No scene graph, no culling beyond back-face.** No frustum culling, no
  spatial index, no occlusion queries. Every submitted triangle goes through
  the vertex stage.

## Related

- `lib/stdlib/render3d.flow` — the renderer
- `examples/threed/README.md` — what each example demonstrates
- [graphics.md](graphics.md) — the 2D window API underneath
- [../demos/threed/](../demos/threed/) — recorded clips
