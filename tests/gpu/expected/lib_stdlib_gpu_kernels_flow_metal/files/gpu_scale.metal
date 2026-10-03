#include <metal_stdlib>
using namespace metal;

kernel void gpu_scale(
    device float* inp [[buffer(0)]],
    device float* out [[buffer(1)]],
    constant int& n [[buffer(2)]],
    constant float& alpha [[buffer(3)]],
    uint tid [[thread_position_in_grid]]
) {
    int i = tid;
    if ((i < n)) {
        out[i] = (inp[i] * alpha);
    }
}