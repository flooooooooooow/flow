// Generated from Flow @gpu function `gpu_matmul_row` by src/flow/wgsl_codegen.py
const WORKGROUP_SIZE: i32 = 64;

@group(0) @binding(0) var<storage, read> A: array<f32>;
@group(0) @binding(1) var<storage, read> B: array<f32>;
@group(0) @binding(2) var<storage, read_write> C: array<f32>;

struct Params {
    M: i32,
    K: i32,
    N: i32,
    _pad0: u32,
};
@group(0) @binding(3) var<uniform> params: Params;

@compute @workgroup_size(64)
fn gpu_matmul_row(
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
                acc = (acc + (A[((row * params.K) + k)] * B[((k * params.N) + col)]));
            }
            C[((row * params.N) + col)] = acc;
        }
    }
}
