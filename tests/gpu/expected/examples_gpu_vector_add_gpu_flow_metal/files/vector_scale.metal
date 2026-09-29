#include <metal_stdlib>
using namespace metal;

kernel void vector_scale(
    device float* input [[buffer(0)]],
    device float* output [[buffer(1)]],
    constant float& scale [[buffer(2)]],
    constant int& n [[buffer(3)]],
    uint tid [[thread_position_in_grid]]
) {
    auto i = tid;
    if ((i < n)) {
        output[i] = (input[i] * scale);
    }
}