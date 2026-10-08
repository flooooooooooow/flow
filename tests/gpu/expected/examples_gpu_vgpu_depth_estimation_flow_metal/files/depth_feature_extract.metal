#include <metal_stdlib>
using namespace metal;

kernel void depth_feature_extract(
    device float* image [[buffer(0)]],
    device float* features [[buffer(1)]],
    constant int& n [[buffer(2)]],
    uint tid [[thread_position_in_grid]]
) {
    int i = tid;
    if ((i < n)) {
        features[i] = ((image[i] * 0.8) + 0.1);
    }
}