#include <metal_stdlib>
using namespace metal;

kernel void gpu_scale_grad(
    device float* dout [[buffer(0)]],
    device float* dx [[buffer(1)]],
    constant int& n [[buffer(2)]],
    constant float& alpha [[buffer(3)]],
    uint tid [[thread_position_in_grid]]
) {
    int i = tid;
    if ((i < n)) {
        dx[i] = (dout[i] * alpha);
    }
}