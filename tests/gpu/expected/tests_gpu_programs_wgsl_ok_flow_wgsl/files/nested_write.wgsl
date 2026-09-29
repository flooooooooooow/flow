// Generated from Flow @gpu function `nested_write` by tools/gpu/main.flow
const WORKGROUP_SIZE: i32 = 64;

@group(0) @binding(0) var<storage, read_write> bufs: array<f32>;
@group(0) @binding(1) var<storage, read> src: array<f32>;

struct Params {
    n: i32,
    _pad0: u32,
    _pad1: u32,
    _pad2: u32,
};
@group(0) @binding(2) var<uniform> params: Params;

@compute @workgroup_size(64)
fn nested_write(
    @builtin(global_invocation_id) global_id: vec3<u32>,
    @builtin(workgroup_id) group_id: vec3<u32>,
    @builtin(local_invocation_id) local_id: vec3<u32>,
) {
    let tid: i32 = i32(global_id.x);
    var v: f32;
    v = src[0];
    if ((params.n > 0)) {
        while ((params.n > 1)) {
            for (var i: i32 = 0; i < params.n; i = i + 1) {
                bufs[i] = v;
            }
        }
    }
}
