#include <metal_stdlib>
using namespace metal;

kernel void kernel(
    constant int& x [[buffer(0)]],
    uint tid [[thread_position_in_grid]]
) {
    return (x * x);
}