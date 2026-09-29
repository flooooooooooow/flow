#include <metal_stdlib>
using namespace metal;

kernel void empty_kernel(
    uint tid [[thread_position_in_grid]]
) {
}