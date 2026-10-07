// Generated from Flow @gpu function `depth_projection_layer` by tools/gpu/main.flow
const WORKGROUP_SIZE: i32 = 64;

@group(0) @binding(0) var<storage, read> features: array<f32>;
@group(0) @binding(1) var<storage, read> weights: array<f32>;
@group(0) @binding(2) var<storage, read_write> depth_map: array<f32>;

struct Params {
    M: i32,
    K: i32,
    N: i32,
    _pad0: u32,
};
@group(0) @binding(3) var<uniform> params: Params;

@compute @workgroup_size(64)
fn depth_projection_layer(
    @builtin(global_invocation_id) global_id: vec3<u32>,
    @builtin(workgroup_id) group_id: vec3<u32>,
    @builtin(local_invocation_id) local_id: vec3<u32>,
) {
    let tid: i32 = i32(global_id.x);
    let row: i32 = tid;
    if ((row < params.M)) {
        for (var col: i32 = 0; col < params.N; col = col + 1) {
            var acc: f32 = 0.0;
            for (var k: i32 = 0; k < params.K; k = k + 1) {
                acc = (acc + (features[((row * params.K) + k)] * weights[((k * params.N) + col)]));
            }
            depth_map[((row * params.N) + col)] = acc;
        }
    }
}
