#include <metal_stdlib>
using namespace metal;

kernel void k(
    constant int& n [[buffer(0)]],
    uint tid [[thread_position_in_grid]]
) {
    auto v = 0;
}