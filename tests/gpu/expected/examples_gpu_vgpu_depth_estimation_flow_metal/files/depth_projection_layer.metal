#include <metal_stdlib>
using namespace metal;

kernel void depth_projection_layer(
    device float* features [[buffer(0)]],
    device float* weights [[buffer(1)]],
    device float* depth_map [[buffer(2)]],
    constant int& M [[buffer(3)]],
    constant int& K [[buffer(4)]],
    constant int& N [[buffer(5)]],
    uint tid [[thread_position_in_grid]]
) {
    int row = tid;
    if ((row < M)) {
        for (int col = 0; col < N; col++) {
            float acc = 0.0;
            for (int k = 0; k < K; k++) {
                acc = (acc + (features[((row * K) + k)] * weights[((k * N) + col)]));
            }
            depth_map[((row * N) + col)] = acc;
        }
    }
}