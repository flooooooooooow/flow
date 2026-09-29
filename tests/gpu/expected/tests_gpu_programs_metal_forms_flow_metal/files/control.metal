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
    auto j = thread_position_in_grid.x;
    float acc = 0.0;
    int k = 0;
    int h = 255;
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
        // Unsupported: ContinueStatement
    }
    for (int s = 0; s < n; s += 2) {
        acc = (acc - 0.25);
        // Unsupported: BreakStatement
    }
    for (int t = 1; t < 10; t++) {
        out[t] = (out[t] / 3.0);
    }
    out[i] = (acc % 7.0);
    threadgroup_barrier(mem_flags::mem_threadgroup);
    threadgroup_barrier(mem_flags::mem_threadgroup);
    int lx = thread_position_in_threadgroup.x;
    int bx = threadgroup_position_in_grid.y;
    int g = threads_per_grid;
    int bs = threads_per_threadgroup;
    int z = thread_position_in_grid.z;
    auto bi = threadgroup_position_in_grid;
    auto li = thread_position_in_threadgroup;
}