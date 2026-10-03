#include <metal_stdlib>
using namespace metal;

kernel void classifier(
    device float* input [[buffer(0)]],
    device float* output [[buffer(1)]],
    uint tid [[thread_position_in_grid]]
) {
}