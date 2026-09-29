#include <metal_stdlib>
using namespace metal;

kernel void gpu_heavy_mix(
    device float* a [[buffer(0)]],
    device float* b [[buffer(1)]],
    device float* out [[buffer(2)]],
    constant int& n [[buffer(3)]],
    uint tid [[thread_position_in_grid]]
) {
    int i = tid;
    if ((i < n)) {
        float scale = b[i];
        float t = a[i];
        float acc = 0.0;
        for (int k = 0; k < 128; k++) {
            t = (t + 1.0);
            acc = (acc + sqrtf(fabsf((t * scale))));
        }
        out[i] = acc;
    }
}