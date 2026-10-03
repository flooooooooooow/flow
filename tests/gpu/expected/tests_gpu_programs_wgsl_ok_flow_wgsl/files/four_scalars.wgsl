// Generated from Flow @gpu function `four_scalars` by tools/gpu/main.flow
const WORKGROUP_SIZE: i32 = 64;

@group(0) @binding(0) var<storage, read_write> a: array<f32>;

struct Params {
    w: f32,
    x: f32,
    y: f32,
    z: f32,
};
@group(0) @binding(1) var<uniform> params: Params;

@compute @workgroup_size(64)
fn four_scalars(
    @builtin(global_invocation_id) global_id: vec3<u32>,
    @builtin(workgroup_id) group_id: vec3<u32>,
    @builtin(local_invocation_id) local_id: vec3<u32>,
) {
    let tid: i32 = i32(global_id.x);
    a[0] = (((params.w + params.x) + params.y) + params.z);
}
