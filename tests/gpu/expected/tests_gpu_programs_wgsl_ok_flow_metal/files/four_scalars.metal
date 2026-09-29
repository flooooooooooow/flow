#include <metal_stdlib>
using namespace metal;

kernel void four_scalars(
    device float* a [[buffer(0)]],
    constant float& w [[buffer(1)]],
    constant float& x [[buffer(2)]],
    constant float& y [[buffer(3)]],
    constant float& z [[buffer(4)]],
    uint tid [[thread_position_in_grid]]
) {
    a[0] = (((w + x) + y) + z);
}