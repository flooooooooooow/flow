#include <metal_stdlib>
using namespace metal;

kernel void calls(
    device float* out [[buffer(0)]],
    device int* output [[buffer(1)]],
    device float* result_x [[buffer(2)]],
    constant int& n [[buffer(3)]],
    uint tid [[thread_position_in_grid]]
) {
    float a = (((sin(1.0) + cos(2.0)) + max(1.0, 2.0)) + pow(2.0, 3.0));
    out[0] = a;
    output[0] = helper(n, 2);
    result_x[0] = __flow_dbg(a);
}