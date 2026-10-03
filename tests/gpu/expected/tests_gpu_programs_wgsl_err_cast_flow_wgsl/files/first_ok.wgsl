// Generated from Flow @gpu function `first_ok` by tools/gpu/main.flow
const WORKGROUP_SIZE: i32 = 64;

@group(0) @binding(0) var<storage, read_write> a: array<f32>;

@compute @workgroup_size(64)
fn first_ok(
    @builtin(global_invocation_id) global_id: vec3<u32>,
    @builtin(workgroup_id) group_id: vec3<u32>,
    @builtin(local_invocation_id) local_id: vec3<u32>,
) {
    let tid: i32 = i32(global_id.x);
    a[0] = 1.0;
}
