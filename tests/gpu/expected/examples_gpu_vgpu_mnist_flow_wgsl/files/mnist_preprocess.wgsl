// Generated from Flow @gpu function `mnist_preprocess` by tools/gpu/main.flow
const WORKGROUP_SIZE: i32 = 64;

@group(0) @binding(0) var<storage, read> raw: array<f32>;
@group(0) @binding(1) var<storage, read_write> norm: array<f32>;

struct Params {
    n: i32,
    _pad0: u32,
    _pad1: u32,
    _pad2: u32,
};
@group(0) @binding(2) var<uniform> params: Params;

@compute @workgroup_size(64)
fn mnist_preprocess(
    @builtin(global_invocation_id) global_id: vec3<u32>,
    @builtin(workgroup_id) group_id: vec3<u32>,
    @builtin(local_invocation_id) local_id: vec3<u32>,
) {
    let tid: i32 = i32(global_id.x);
    let i: i32 = tid;
    if ((i < params.n)) {
        norm[i] = (raw[i] / 255.0);
    }
}
