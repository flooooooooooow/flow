#include <metal_stdlib>
using namespace metal;

kernel void exprs(
    device int* p [[buffer(0)]],
    device float* q [[buffer(1)]],
    device float* r [[buffer(2)]],
    device float* v [[buffer(3)]],
    constant uint& u [[buffer(4)]],
    constant long& big [[buffer(5)]],
    constant double& d [[buffer(6)]],
    constant ulong& w [[buffer(7)]],
    constant Pair& s [[buffer(8)]],
    uint tid [[thread_position_in_grid]]
) {
    int x = (p[0] << 2);
    int y = (((p[1] >> 1) & 3) | (4 ^ 5));
    float c = /* Unsupported: CastExpression */;
    auto pr = /* Unsupported: StructLiteral */;
    auto arr = /* Unsupported: ArrayLiteral */;
    float m = sqrtf(s.a);
    int e = (~x);
    bool t = true;
    bool f = false;
    int neg = (-(x + y));
    float uninit;
    device float* buf;
    s.b = 3.0;
    p[x] = (p[y] + 1);
    p[1] = (p[1] - 1);
    bool ok = (((x != y) && (x <= y)) || (x > 1));
    return x;
}