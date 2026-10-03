#include <metal_stdlib>
using namespace metal;

kernel void local_add(
    device float* a [[buffer(0)]],
    device float* b [[buffer(1)]],
    uint tid [[thread_position_in_grid]]
) {
    int i = tid;
    a[i] = (a[i] + b[i]);
}