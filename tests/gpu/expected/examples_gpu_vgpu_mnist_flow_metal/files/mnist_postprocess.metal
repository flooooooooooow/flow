#include <metal_stdlib>
using namespace metal;

kernel void mnist_postprocess(
    device float* logits [[buffer(0)]],
    device float* probs [[buffer(1)]],
    constant int& n [[buffer(2)]],
    uint tid [[thread_position_in_grid]]
) {
    int i = tid;
    if ((i < n)) {
        float val = logits[i];
        if ((val > 0.0)) {
            probs[i] = val;
        } else {
            probs[i] = 0.0;
        }
    }
}