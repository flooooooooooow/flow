#include <metal_stdlib>
using namespace metal;

kernel void reserved_names(
    device float* loop [[buffer(0)]],
    device float* ref [[buffer(1)]],
    constant int& target [[buffer(2)]],
    constant int& __tmp [[buffer(3)]],
    constant int& switch [[buffer(4)]],
    uint tid [[thread_position_in_grid]]
) {
    int filter = (target + __tmp);
    float self_ = 0.0;
    ref[filter] = loop[(filter + switch)];
}