/* GPU microbenchmarks for Flow, on the Flow GPU runtime (runtime/gpu_memory.h;
 * Metal on macOS through runtime/gpu_metal.m).
 *
 * Measures:
 *   1. host-to-device (H2D) and device-to-host (D2H) transfer bandwidth;
 *   2. kernel launch overhead, as the time of a one-element kernel;
 *   3. a representative elementwise workload, to show the transfer to
 *      compute ratio.
 *
 * The numbers feed the backend cost model (#749). Without a GPU backend the
 * figures are the simulated ones the earlier Python benchmark printed.
 * Build and run with benchmarks/gpu/gpu_microbenchmark.sh.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "gpu_memory.h"

#ifndef __APPLE__
/* No GPU runtime on this platform: every probe reports unavailable. */
int flow_gpu_available(void) { return 0; }
const char *flow_gpu_backend_name(void) { return "stub"; }
void *flow_gpu_alloc(int64_t size, int32_t flags) { (void)size; (void)flags; return NULL; }
void flow_gpu_free(void *buf) { (void)buf; }
int flow_gpu_copy_h2d(void *d, const void *s, int64_t n) { (void)d; (void)s; (void)n; return -1; }
int flow_gpu_copy_d2h(void *d, void *s, int64_t n) { (void)d; (void)s; (void)n; return -1; }
void flow_gpu_sync(void) {}
int flow_gpu_mul_f32(void *o, void *a, void *b, int64_t n) { (void)o; (void)a; (void)b; (void)n; return -1; }
#endif

static double now_s(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

static const double GB = 1024.0 * 1024.0 * 1024.0;
static const double MB = 1024.0 * 1024.0;

static void bandwidth(int have_gpu, const char *backend) {
    printf("\n--- Bandwidth Test (%s) ---\n", backend);
    if (!have_gpu) {
        printf("No GPU available, running simulated test...\n");
        const double sizes[] = {1024.0, 1024.0 * 1024.0, 10.0 * 1024 * 1024, 100.0 * 1024 * 1024};
        for (int i = 0; i < 4; i++) {
            double size = sizes[i];
            double h2d = 0.000001 + size / (10.0 * GB);
            double d2h = 0.000001 + size / (8.0 * GB);
            printf("Size: %.2f MB\n", size / MB);
            printf("  H2D: %.2f GB/s (%.3f ms)\n", size / (h2d * GB), h2d * 1000.0);
            printf("  D2H: %.2f GB/s (%.3f ms)\n", size / (d2h * GB), d2h * 1000.0);
        }
        return;
    }
    const int64_t sizes[] = {1 << 20, 10 << 20, 100 << 20, 500LL << 20};
    for (int i = 0; i < 4; i++) {
        int64_t n = sizes[i];
        printf("\nBuffer Size: %.2f MB\n", (double)n / MB);
        float *host = malloc((size_t)n);
        float *back = malloc((size_t)n);
        void *dev = flow_gpu_alloc(n, FLOW_GPU_MEM_PRIVATE);
        if (!host || !back || !dev) {
            printf("  allocation failed, skipping\n");
            free(host);
            free(back);
            flow_gpu_free(dev);
            continue;
        }
        for (int64_t k = 0; k < n / 4; k++) {
            host[k] = (float)(k & 1023);
        }
        flow_gpu_sync();
        double t0 = now_s();
        int rc = flow_gpu_copy_h2d(dev, host, n);
        flow_gpu_sync();
        double h2d = now_s() - t0;
        t0 = now_s();
        rc |= flow_gpu_copy_d2h(back, dev, n);
        flow_gpu_sync();
        double d2h = now_s() - t0;
        if (rc != 0) {
            printf("  copy failed\n");
        } else {
            printf("  H2D: %.2f GB/s (%.3f ms)\n", (double)n / (h2d * GB), h2d * 1000.0);
            printf("  D2H: %.2f GB/s (%.3f ms)\n", (double)n / (d2h * GB), d2h * 1000.0);
            printf("  Round trip %s\n", memcmp(host, back, (size_t)n) == 0 ? "verified" : "MISMATCH");
        }
        flow_gpu_free(dev);
        free(host);
        free(back);
    }
}

static void launch_overhead(int have_gpu, const char *backend) {
    printf("\n--- Launch Overhead Test (%s) ---\n", backend);
    if (!have_gpu) {
        printf("No GPU available, running simulated test...\n");
        printf("Simulated Kernel Launch Overhead: %.4f ms\n", 0.015);
        return;
    }
    void *a = flow_gpu_alloc(4, FLOW_GPU_MEM_SHARED);
    void *b = flow_gpu_alloc(4, FLOW_GPU_MEM_SHARED);
    void *o = flow_gpu_alloc(4, FLOW_GPU_MEM_SHARED);
    if (!a || !b || !o) {
        printf("allocation failed\n");
        return;
    }
    /* Warm up: builds the pipeline state. */
    flow_gpu_mul_f32(o, a, b, 1);
    flow_gpu_sync();
    const int iters = 1000;
    double t0 = now_s();
    for (int i = 0; i < iters; i++) {
        flow_gpu_mul_f32(o, a, b, 1);
    }
    flow_gpu_sync();
    double per = (now_s() - t0) / iters;
    printf("Kernel launch overhead (one-element kernel, %d launches): %.4f ms\n", iters, per * 1000.0);
    flow_gpu_free(a);
    flow_gpu_free(b);
    flow_gpu_free(o);
}

static void workload(int have_gpu, const char *backend) {
    const int64_t n = 10 * 1024 * 1024;
    const int64_t bytes = n * 4;
    printf("\n--- Representative Workload: Vector Multiply (%s) ---\n", backend);
    printf("Workload size: %lld elements, %.2f MB per array (3 arrays)\n", (long long)n, (double)bytes / MB);
    double h2d, launch, compute, d2h;
    if (!have_gpu) {
        printf("No GPU available, running simulated test...\n");
        h2d = 0.008;
        launch = 0.000015;
        compute = 0.002;
        d2h = 0.010;
        printf("[GPU Profile] H2D Transfer: %.4fs (Simulated)\n", h2d);
        printf("[GPU Profile] Kernel Launch Overhead: %.6fs (Simulated)\n", launch);
        printf("[GPU Profile] Kernel Compute: %.4fs (Simulated)\n", compute);
        printf("[GPU Profile] D2H Transfer: %.4fs (Simulated)\n", d2h);
    } else {
        float *a = malloc((size_t)bytes);
        float *b = malloc((size_t)bytes);
        float *c = malloc((size_t)bytes);
        void *da = flow_gpu_alloc(bytes, FLOW_GPU_MEM_PRIVATE);
        void *db = flow_gpu_alloc(bytes, FLOW_GPU_MEM_PRIVATE);
        void *dc = flow_gpu_alloc(bytes, FLOW_GPU_MEM_PRIVATE);
        if (!a || !b || !c || !da || !db || !dc) {
            printf("allocation failed\n");
            return;
        }
        for (int64_t k = 0; k < n; k++) {
            a[k] = (float)(k % 7);
            b[k] = 2.0f;
        }
        double t0 = now_s();
        flow_gpu_copy_h2d(da, a, bytes);
        flow_gpu_copy_h2d(db, b, bytes);
        flow_gpu_sync();
        h2d = now_s() - t0;
        launch = 0.0;
        t0 = now_s();
        int rc = flow_gpu_mul_f32(dc, da, db, n);
        flow_gpu_sync();
        compute = now_s() - t0;
        t0 = now_s();
        flow_gpu_copy_d2h(c, dc, bytes);
        flow_gpu_sync();
        d2h = now_s() - t0;
        int ok = rc == 0;
        for (int64_t k = 0; ok && k < n; k += 4099) {
            ok = c[k] == a[k] * 2.0f;
        }
        printf("[GPU Profile] H2D Transfer: %.4fs\n", h2d);
        printf("[GPU Profile] Kernel Compute (with launch): %.4fs\n", compute);
        printf("[GPU Profile] D2H Transfer: %.4fs\n", d2h);
        printf("Result %s\n", ok ? "verified" : "MISMATCH");
        flow_gpu_free(da);
        flow_gpu_free(db);
        flow_gpu_free(dc);
        free(a);
        free(b);
        free(c);
    }
    double transfer = h2d + d2h;
    double comp = compute + launch;
    printf("\nSummary:\n");
    printf("  Transfer Time: %.4fs\n", transfer);
    printf("  Compute Time: %.6fs\n", comp);
    printf("  Ratio (Transfer/Compute): %.2f\n", comp > 0 ? transfer / comp : 0.0);
}

int main(void) {
    printf("========================================\n");
    printf("       GPU Performance Microbench       \n");
    printf("========================================\n");
    int have_gpu = flow_gpu_available();
    const char *backend = have_gpu ? flow_gpu_backend_name() : "simulated";
    if (!have_gpu) {
        printf("No GPU backends found. Falling back to simulated CPU path.\n");
    } else {
        printf("GPU backend: %s\n", backend);
    }
    bandwidth(have_gpu, backend);
    launch_overhead(have_gpu, backend);
    workload(have_gpu, backend);
    return 0;
}
