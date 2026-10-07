#include <metal_stdlib>
using namespace metal;

kernel void mnist_preprocess(
    device float* raw [[buffer(0)]],
    device float* norm [[buffer(1)]],
    constant int& n [[buffer(2)]],
    uint tid [[thread_position_in_grid]]
) {
    int i = tid;
    if ((i < n)) {
        norm[i] = (raw[i] / 255.0);
    }
}