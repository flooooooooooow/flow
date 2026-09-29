// Generated from Flow @gpu function `local_add` by src/flow/wgsl_codegen.py
const WORKGROUP_SIZE: i32 = 64;

@group(0) @binding(0) var<storage, read_write> a: array<f32>;
@group(0) @binding(1) var<storage, read> b: array<f32>;

@compute @workgroup_size(64)
fn local_add(
    @builtin(global_invocation_id) global_id: vec3<u32>,
    @builtin(workgroup_id) group_id: vec3<u32>,
    @builtin(local_invocation_id) local_id: vec3<u32>,
) {
    let tid: i32 = i32(global_id.x);
    let i: i32 = tid;
    a[i] = (a[i] + b[i]);
}
