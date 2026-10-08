#include <metal_stdlib>
using namespace metal;

kernel void depth_colormap_tint(
    device float* depth_map [[buffer(0)]],
    device float* colormap [[buffer(1)]],
    constant int& n [[buffer(2)]],
    uint tid [[thread_position_in_grid]]
) {
    int i = tid;
    if ((i < n)) {
        float val = depth_map[i];
        if ((val < 0.0)) {
            colormap[i] = 0.0;
        } else {
            colormap[i] = (1.0 - val);
        }
    }
}