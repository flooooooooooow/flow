#include <metal_stdlib>
using namespace metal;

kernel void first_ok(
    device float* a [[buffer(0)]],
    uint tid [[thread_position_in_grid]]
) {
    a[0] = 1.0;
}