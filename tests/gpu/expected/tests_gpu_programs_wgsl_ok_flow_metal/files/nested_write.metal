#include <metal_stdlib>
using namespace metal;

kernel void nested_write(
    device float* bufs [[buffer(0)]],
    device float* src [[buffer(1)]],
    constant int& n [[buffer(2)]],
    uint tid [[thread_position_in_grid]]
) {
    float v;
    v = src[0];
    if ((n > 0)) {
        while ((n > 1)) {
            for (int i = 0; i < n; i++) {
                bufs[i] = v;
            }
        }
    }
}