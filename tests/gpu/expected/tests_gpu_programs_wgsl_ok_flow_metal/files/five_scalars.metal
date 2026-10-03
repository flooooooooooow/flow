#include <metal_stdlib>
using namespace metal;

kernel void five_scalars(
    device float* data [[buffer(0)]],
    constant float& alpha [[buffer(1)]],
    constant float& beta [[buffer(2)]],
    constant int& n [[buffer(3)]],
    constant uint& m [[buffer(4)]],
    constant bool& flag [[buffer(5)]],
    uint tid [[thread_position_in_grid]]
) {
    int i = tid;
    data[i] = ((data[i] * alpha) + beta);
}