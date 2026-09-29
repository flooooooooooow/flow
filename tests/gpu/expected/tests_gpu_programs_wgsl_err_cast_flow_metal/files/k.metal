#include <metal_stdlib>
using namespace metal;

kernel void k(
    device float* a [[buffer(0)]],
    constant int& n [[buffer(1)]],
    uint tid [[thread_position_in_grid]]
) {
    a[0] = /* Unsupported: CastExpression */;
}