#include <metal_stdlib>
using namespace metal;

kernel void control(
    device float* a [[buffer(0)]],
    device float* out [[buffer(1)]],
    constant int& n [[buffer(2)]],
    constant bool& flag [[buffer(3)]],
    uint tid [[thread_position_in_grid]]
) {
    int i = tid;
    float acc = 0.0;
    int k = 0;
    int h = 16;
    bool t = true;
    if (((i < n) && flag)) {
        acc = (acc + a[i]);
    } else {
        acc = 2.0;
    }
    if ((i >= n)) {
        return;
    }
    while ((k < 4)) {
        k = (k + 1);
        acc = (acc * 2.0);
    }
    for (int s = 0; s < n; s += 2) {
        acc = (acc - 0.25);
    }
    for (int q = 1; q < 10; q++) {
        acc = (acc + 1.0);
    }
    out[i] = (((sqrtf(fabsf(acc)) + sin(acc)) + floorf(acc)) + fmaxf(acc, 1.0));
    threadgroup_barrier(mem_flags::mem_threadgroup);
    int x = (((thread_position_in_grid.x + threadgroup_position_in_grid.y) + thread_position_in_threadgroup) + threads_per_threadgroup);
}