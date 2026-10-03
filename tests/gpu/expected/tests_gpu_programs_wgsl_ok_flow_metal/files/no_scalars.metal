#include <metal_stdlib>
using namespace metal;

kernel void no_scalars(
    device int* a [[buffer(0)]],
    device uint* b [[buffer(1)]],
    uint tid [[thread_position_in_grid]]
) {
    b[0] = b[1];
}