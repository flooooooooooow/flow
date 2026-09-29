#include <metal_stdlib>
using namespace metal;

kernel void gpu_relu_grad(
    device float* x [[buffer(0)]],
    device float* dout [[buffer(1)]],
    device float* dx [[buffer(2)]],
    constant int& n [[buffer(3)]],
    uint tid [[thread_position_in_grid]]
) {
    int i = tid;
    if ((i < n)) {
        if ((x[i] > 0.0)) {
            dx[i] = dout[i];
        } else {
            dx[i] = 0.0;
        }
    }
}