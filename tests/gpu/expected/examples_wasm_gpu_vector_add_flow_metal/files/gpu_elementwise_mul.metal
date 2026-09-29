#include <metal_stdlib>
using namespace metal;

kernel void gpu_elementwise_mul(
    device float* a [[buffer(0)]],
    device float* b [[buffer(1)]],
    device float* out [[buffer(2)]],
    constant int& n [[buffer(3)]],
    uint tid [[thread_position_in_grid]]
) {
    int i = tid;
    if ((i < n)) {
        out[i] = (a[i] * b[i]);
    }
}