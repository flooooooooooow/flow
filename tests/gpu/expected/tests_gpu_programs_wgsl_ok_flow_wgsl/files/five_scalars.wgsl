// Generated from Flow @gpu function `five_scalars` by tools/gpu/main.flow
const WORKGROUP_SIZE: i32 = 64;

@group(0) @binding(0) var<storage, read_write> data: array<f32>;

struct Params {
    alpha: f32,
    beta: f32,
    n: i32,
    m: u32,
    flag: bool,
    _pad0: u32,
    _pad1: u32,
    _pad2: u32,
};
@group(0) @binding(1) var<uniform> params: Params;

@compute @workgroup_size(64)
fn five_scalars(
    @builtin(global_invocation_id) global_id: vec3<u32>,
    @builtin(workgroup_id) group_id: vec3<u32>,
    @builtin(local_invocation_id) local_id: vec3<u32>,
) {
    let tid: i32 = i32(global_id.x);
    let i: i32 = tid;
    data[i] = ((data[i] * params.alpha) + params.beta);
}
