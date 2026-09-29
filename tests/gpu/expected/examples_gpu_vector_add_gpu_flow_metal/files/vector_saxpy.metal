#include <metal_stdlib>
using namespace metal;

kernel void vector_saxpy(
    device float* x [[buffer(0)]],
    device float* y [[buffer(1)]],
    constant float& a [[buffer(2)]],
    constant int& n [[buffer(3)]],
    uint tid [[thread_position_in_grid]]
) {
    auto i = tid;
    if ((i < n)) {
        y[i] = ((a * x[i]) + y[i]);
    }
}