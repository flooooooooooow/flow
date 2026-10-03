#include <metal_stdlib>
using namespace metal;

kernel void lib_scale(
    device float* a [[buffer(0)]],
    constant float& s [[buffer(1)]],
    uint tid [[thread_position_in_grid]]
) {
    int i = tid;
    a[i] = (a[i] * s);
}