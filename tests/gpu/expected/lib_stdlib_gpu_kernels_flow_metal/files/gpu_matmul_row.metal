#include <metal_stdlib>
using namespace metal;

kernel void gpu_matmul_row(
    device float* A [[buffer(0)]],
    device float* B [[buffer(1)]],
    device float* C [[buffer(2)]],
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
                acc = (acc + (A[((row * K) + k)] * B[((k * N) + col)]));
            }
            C[((row * N) + col)] = acc;
        }
    }
}