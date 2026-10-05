// dsp_bench — scalar CPU vs NEON SIMD vs Metal GPU on a bank of Schur all-pass
// chains. The chains are independent (this is the honest parallel axis); each
// chain is internally serial (recursive IIR), so speed comes from processing
// many chains at once, not from vectorising one chain.
//
//   Build:  ./build.sh        (or see the clang line at the bottom of that file)
//   Run:    ./dsp_bench --chains 4096 --sections 8 --samples 48000
//
// Apple Silicon only (NEON + Metal). Emits a table and, with --json, machine
// readable results.

#import <Metal/Metal.h>
#import <Foundation/Foundation.h>

#include <arm_neon.h>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

namespace
{
constexpr int   kMaxSections = 16;
using Clock  = std::chrono::high_resolution_clock;
using Sec    = std::chrono::duration<double>;

struct Config
{
    int chains   = 4096;
    int sections = 8;
    int samples  = 48000;
    int reps     = 3;
    bool json    = false;
    bool runGpu  = true;
};

struct Result
{
    std::string name;
    double  seconds   = 0.0;     // best of reps
    double  throughput= 0.0;     // section-updates / second
    double  maxDiff   = 0.0;     // vs scalar reference
    bool    ok        = true;
};

inline float clampK (float k) { return k < -0.999f ? -0.999f : (k > 0.999f ? 0.999f : k); }

// ---- reference scalar kernel: one chain at a time, fully serial ----
void runScalar (const std::vector<float>& in, const std::vector<float>& k,
                int B, int O, int N, std::vector<float>& checksum)
{
    for (int b = 0; b < B; ++b)
    {
        float xs[kMaxSections] = {0}, ys[kMaxSections] = {0};
        const float* kb = &k[(size_t) b * O];
        double acc = 0.0;
        for (int n = 0; n < N; ++n)
        {
            float x = in[(size_t) n];
            for (int o = 0; o < O; ++o)
            {
                const float ki = kb[o];
                const float y = ki * x + xs[o] - ki * ys[o];
                xs[o] = x; ys[o] = y; x = y;
            }
            acc += x;
        }
        checksum[(size_t) b] = (float) (acc / (double) N);
    }
}

// ---- NEON kernel: 4 independent chains per 128-bit lane group ----
void runNeon (const std::vector<float>& in, const std::vector<float>& kSoA,
              const std::vector<float>& kAoS,
              int B, int O, int N, std::vector<float>& checksum)
{
    const int groups = B / 4;
    for (int g = 0; g < groups; ++g)
    {
        float32x4_t xs[kMaxSections], ys[kMaxSections], kk[kMaxSections];
        for (int o = 0; o < O; ++o)
        {
            xs[o] = vdupq_n_f32 (0.0f);
            ys[o] = vdupq_n_f32 (0.0f);
            kk[o] = vld1q_f32 (&kSoA[((size_t) g * O + o) * 4]);
        }
        float32x4_t acc = vdupq_n_f32 (0.0f);
        for (int n = 0; n < N; ++n)
        {
            float32x4_t x = vdupq_n_f32 (in[(size_t) n]);  // shared input across chains
            for (int o = 0; o < O; ++o)
            {
                // y = k*x + xs - k*ys  = k*(x - ys) + xs
                const float32x4_t y = vmlaq_f32 (xs[o], kk[o], vsubq_f32 (x, ys[o]));
                xs[o] = x; ys[o] = y; x = y;
            }
            acc = vaddq_f32 (acc, x);
        }
        acc = vmulq_n_f32 (acc, 1.0f / (float) N);
        float out[4]; vst1q_f32 (out, acc);
        for (int l = 0; l < 4; ++l)
            checksum[(size_t) g * 4 + l] = out[l];
    }
    // scalar tail for a non-multiple-of-4 chain count
    for (int b = groups * 4; b < B; ++b)
    {
        float xs[kMaxSections] = {0}, ys[kMaxSections] = {0};
        const float* kb = &kAoS[(size_t) b * O];
        double acc = 0.0;
        for (int n = 0; n < N; ++n)
        {
            float x = in[(size_t) n];
            for (int o = 0; o < O; ++o)
            {
                const float ki = kb[o];
                const float y = ki * x + xs[o] - ki * ys[o];
                xs[o] = x; ys[o] = y; x = y;
            }
            acc += x;
        }
        checksum[(size_t) b] = (float) (acc / (double) N);
    }
}

const char* kMetalSrc = R"METAL(
#include <metal_stdlib>
using namespace metal;

kernel void allpass_bank (device const float*  input   [[buffer(0)]],
                          device const float*  kcoef   [[buffer(1)]],
                          device float*        outSum  [[buffer(2)]],
                          constant uint&        B       [[buffer(3)]],
                          constant uint&        O       [[buffer(4)]],
                          constant uint&        N       [[buffer(5)]],
                          uint gid [[thread_position_in_grid]])
{
    if (gid >= B) return;
    float xs[16]; float ys[16];
    for (uint o = 0; o < O; ++o) { xs[o] = 0.0f; ys[o] = 0.0f; }
    device const float* k = kcoef + gid * O;
    float acc = 0.0f;
    for (uint n = 0; n < N; ++n)
    {
        float x = input[n];
        for (uint o = 0; o < O; ++o)
        {
            float ki = k[o];
            float y = ki * x + xs[o] - ki * ys[o];
            xs[o] = x; ys[o] = y; x = y;
        }
        acc += x;
    }
    outSum[gid] = acc / (float) N;
}
)METAL";

double maxDiff (const std::vector<float>& a, const std::vector<float>& b)
{
    double m = 0.0;
    for (size_t i = 0; i < a.size(); ++i)
        m = std::max (m, (double) std::fabs (a[i] - b[i]));
    return m;
}
} // namespace

int main (int argc, char** argv)
{
    Config cfg;
    for (int i = 1; i < argc; ++i)
    {
        std::string a = argv[i];
        auto next = [&] { return (i + 1 < argc) ? std::atoi (argv[++i]) : 0; };
        if      (a == "--chains")   cfg.chains   = next();
        else if (a == "--sections") cfg.sections = std::min (next(), kMaxSections);
        else if (a == "--samples")  cfg.samples  = next();
        else if (a == "--reps")     cfg.reps     = std::max (1, next());
        else if (a == "--json")     cfg.json     = true;
        else if (a == "--no-gpu")   cfg.runGpu   = false;
        else if (a == "--help")     { printf ("usage: dsp_bench [--chains N --sections N --samples N --reps N --json --no-gpu]\n"); return 0; }
    }

    const int B = cfg.chains, O = cfg.sections, N = cfg.samples;
    const double sectionUpdates = (double) B * N * O;

    // ---- data: a shared input signal + per-chain random-ish reflection coeffs ----
    std::vector<float> input ((size_t) N);
    unsigned seed = 22463;
    auto rnd = [&] { seed = seed * 1664525u + 1013904223u; return (float) ((seed >> 8) & 0xffff) / 32768.0f - 1.0f; };
    for (int n = 0; n < N; ++n) input[(size_t) n] = rnd();

    std::vector<float> k ((size_t) B * O);
    for (int b = 0; b < B; ++b)
        for (int o = 0; o < O; ++o)
            k[(size_t) b * O + o] = clampK (0.85f * rnd());

    // NEON wants a grouped SoA copy: [group][section][lane]
    std::vector<float> kSoA ((size_t) B * O, 0.0f);
    const int groups = B / 4;
    for (int g = 0; g < groups; ++g)
        for (int o = 0; o < O; ++o)
            for (int l = 0; l < 4; ++l)
                kSoA[((size_t) g * O + o) * 4 + l] = k[((size_t) (g * 4 + l)) * O + o];

    std::vector<Result> results;
    std::vector<float> ref ((size_t) B), tmp ((size_t) B);

    auto timeit = [&] (const char* name, auto&& fn, std::vector<float>& out, const std::vector<float>* cmp) -> Result
    {
        double best = 1e30;
        for (int r = 0; r < cfg.reps; ++r)
        {
            std::fill (out.begin(), out.end(), 0.0f);
            const auto t0 = Clock::now();
            fn();
            const double s = Sec (Clock::now() - t0).count();
            best = std::min (best, s);
        }
        Result res;
        res.name = name;
        res.seconds = best;
        res.throughput = sectionUpdates / best;
        if (cmp) res.maxDiff = maxDiff (out, *cmp);
        return res;
    };

    // scalar reference
    results.push_back (timeit ("CPU scalar", [&] { runScalar (input, k, B, O, N, ref); }, ref, nullptr));

    // NEON
    results.push_back (timeit ("CPU NEON x4", [&] { runNeon (input, kSoA, k, B, O, N, tmp); }, tmp, &ref));

    // Metal
    if (cfg.runGpu)
    {
        @autoreleasepool {
            id<MTLDevice> dev = MTLCreateSystemDefaultDevice();
            if (! dev) { fprintf (stderr, "no Metal device\n"); }
            else
            {
                NSError* err = nil;
                id<MTLLibrary> lib = [dev newLibraryWithSource: [NSString stringWithUTF8String: kMetalSrc]
                                                       options: nil error: &err];
                if (! lib) { fprintf (stderr, "metal compile: %s\n", err.localizedDescription.UTF8String); }
                else
                {
                    id<MTLFunction> fn = [lib newFunctionWithName: @"allpass_bank"];
                    id<MTLComputePipelineState> pso = [dev newComputePipelineStateWithFunction: fn error: &err];
                    id<MTLCommandQueue> queue = [dev newCommandQueue];

                    id<MTLBuffer> inBuf  = [dev newBufferWithBytes: input.data() length: input.size()*sizeof(float) options: MTLResourceStorageModeShared];
                    id<MTLBuffer> kBuf   = [dev newBufferWithBytes: k.data()     length: k.size()*sizeof(float)     options: MTLResourceStorageModeShared];
                    id<MTLBuffer> outBuf = [dev newBufferWithLength: (size_t) B*sizeof(float) options: MTLResourceStorageModeShared];
                    uint uB = (uint) B, uO = (uint) O, uN = (uint) N;

                    auto dispatch = [&]
                    {
                        id<MTLCommandBuffer> cb = [queue commandBuffer];
                        id<MTLComputeCommandEncoder> enc = [cb computeCommandEncoder];
                        [enc setComputePipelineState: pso];
                        [enc setBuffer: inBuf  offset: 0 atIndex: 0];
                        [enc setBuffer: kBuf   offset: 0 atIndex: 1];
                        [enc setBuffer: outBuf offset: 0 atIndex: 2];
                        [enc setBytes: &uB length: sizeof(uint) atIndex: 3];
                        [enc setBytes: &uO length: sizeof(uint) atIndex: 4];
                        [enc setBytes: &uN length: sizeof(uint) atIndex: 5];
                        NSUInteger tpt = std::min<NSUInteger> (pso.maxTotalThreadsPerThreadgroup, 256);
                        [enc dispatchThreads: MTLSizeMake ((NSUInteger) B, 1, 1)
                              threadsPerThreadgroup: MTLSizeMake (tpt, 1, 1)];
                        [enc endEncoding];
                        [cb commit];
                        [cb waitUntilCompleted];
                    };

                    dispatch(); // warm-up (compile/upload excluded from timing)
                    Result res;
                    res.name = "GPU Metal";
                    double best = 1e30;
                    for (int r = 0; r < cfg.reps; ++r)
                    {
                        const auto t0 = Clock::now();
                        dispatch();
                        best = std::min (best, Sec (Clock::now() - t0).count());
                    }
                    memcpy (tmp.data(), [outBuf contents], (size_t) B*sizeof(float));
                    res.seconds = best;
                    res.throughput = sectionUpdates / best;
                    res.maxDiff = maxDiff (tmp, ref);
                    results.push_back (res);
                }
            }
        }
    }

    // ---- report ----
    const double base = results[0].throughput;
    for (auto& r : results) r.ok = (&r == &results[0]) || (r.maxDiff < 1e-3);

    if (cfg.json)
    {
        printf ("{\n  \"config\": {\"chains\": %d, \"sections\": %d, \"samples\": %d, \"reps\": %d},\n",
                B, O, N, cfg.reps);
        printf ("  \"device\": \"Apple M-series (Metal)\",\n  \"results\": [\n");
        for (size_t i = 0; i < results.size(); ++i)
        {
            const auto& r = results[i];
            printf ("    {\"backend\": \"%s\", \"seconds\": %.6f, \"gsu_per_s\": %.3f, \"speedup\": %.2f, \"max_diff\": %.2e, \"ok\": %s}%s\n",
                    r.name.c_str(), r.seconds, r.throughput / 1e9, r.throughput / base, r.maxDiff,
                    r.ok ? "true" : "false", (i + 1 < results.size()) ? "," : "");
        }
        printf ("  ]\n}\n");
        return 0;
    }

    printf ("\n  dsp_bench — Schur all-pass bank   (%d chains x %d sections x %d samples)\n", B, O, N);
    printf ("  workload: %.2f G section-updates per run,  best of %d reps\n\n", sectionUpdates / 1e9, cfg.reps);
    printf ("  %-14s %10s %14s %10s %12s  %s\n", "backend", "time (ms)", "Gupdates/s", "speedup", "max-diff", "check");
    printf ("  %s\n", "------------------------------------------------------------------------------");
    for (const auto& r : results)
        printf ("  %-14s %10.2f %14.2f %9.2fx %12.1e  %s\n",
                r.name.c_str(), r.seconds * 1e3, r.throughput / 1e9,
                r.throughput / base, r.maxDiff, r.ok ? "ok" : "MISMATCH");
    printf ("\n");
    return 0;
}
