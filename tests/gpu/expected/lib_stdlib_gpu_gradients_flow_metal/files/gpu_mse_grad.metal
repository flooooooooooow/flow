#include <metal_stdlib>
using namespace metal;

kernel void gpu_mse_grad(
    device float* pred [[buffer(0)]],
    device float* target [[buffer(1)]],
    device float* grad [[buffer(2)]],
    constant int& n [[buffer(3)]],
    uint tid [[thread_position_in_grid]]
) {
    int i = tid;
    if ((i < n)) {
        float inv_n = (1.0 / /* Unsupported: CastExpression */);
        grad[i] = ((2.0 * (pred[i] - target[i])) * inv_n);
    }
}