// Generated from Flow @gpu function `no_scalars` by tools/gpu/main.flow
const WORKGROUP_SIZE: i32 = 64;

@group(0) @binding(0) var<storage, read> a: array<i32>;
@group(0) @binding(1) var<storage, read_write> b: array<u32>;

@compute @workgroup_size(64)
fn no_scalars(
    @builtin(global_invocation_id) global_id: vec3<u32>,
    @builtin(workgroup_id) group_id: vec3<u32>,
    @builtin(local_invocation_id) local_id: vec3<u32>,
) {
    let tid: i32 = i32(global_id.x);
    b[0] = b[1];
}
