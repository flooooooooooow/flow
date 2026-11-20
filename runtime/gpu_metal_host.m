/* Resident Metal host for Flow. See runtime/gpu_metal_host.h and docs/gpu-host.md.
 *
 * Built with ARC (the runtime archive and the gfx link add -fobjc-arc for this file).
 * Window presentation reaches the gfx window through two symbols that
 * runtime/gfx_macos.m exports (flow_gfx_set_layer, flow_gfx_view_info). They
 * are looked up with dlsym, so a program that never opens a gfx window links
 * without Cocoa.
 */
#ifdef __APPLE__

#if !__has_feature(objc_arc)
#error gpu_metal_host.m must be compiled with -fobjc-arc
#endif

#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <QuartzCore/QuartzCore.h>

#include <dlfcn.h>
#include <stdarg.h>
#include <mach/mach.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "gpu_metal_host.h"

#define MAX_RES 65536
#define MAX_BUF_SLOTS 31
#define MAX_TEX_SLOTS 16
#define MAX_FRAMES 3
#define RING_BYTES (4 * 1024 * 1024)
#define MAX_TIMED_PASSES 32
#define VERTEX_SLOT_BASE 16

enum { KIND_BUFFER = 1, KIND_TEXTURE = 2, KIND_COMPUTE = 3, KIND_RENDER = 4 };
enum { TEX_GPU_ONLY = 16 };

/* ------------------------------------------------------------------ */
/* Resources                                                           */
/* ------------------------------------------------------------------ */

@interface GLRes : NSObject {
@public
    int kind;
    int ncopies;
    id<MTLBuffer> buf[MAX_FRAMES];
    id<MTLTexture> tex[MAX_FRAMES];
    int64_t bytes;
    int w, h, format, usage;
    bool gpu_only;
    /* pipelines */
    id<MTLComputePipelineState> cps;
    id<MTLRenderPipelineState> rps;
    id<MTLDepthStencilState> dss;
    NSUInteger max_threads, exec_width;
    int cull, depth_mode, cfmt, dfmt, blend;
    bool built, has_vd;
    MTLVertexDescriptor *vd;
    NSString *msl, *vs, *fs;
}
@end
@implementation GLRes
@end

typedef struct { int32_t handle; int64_t offset; int ring; int32_t ring_n; } BufBind;

static pthread_mutex_t g_tab_lock = PTHREAD_MUTEX_INITIALIZER;
static __strong GLRes *g_tab[MAX_RES];
static uint16_t g_gen[MAX_RES];
static int32_t g_free[MAX_RES];
static int32_t g_nfree = 0;
static int32_t g_next = 0;

static __thread char t_err[512];
static void set_err(const char *fmt, ...) __attribute__((format(printf, 1, 2)));
static void set_err(const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(t_err, sizeof t_err, fmt, ap);
    va_end(ap);
}
static int32_t fail(const char *fmt, ...) __attribute__((format(printf, 1, 2)));
static int32_t fail(const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(t_err, sizeof t_err, fmt, ap);
    va_end(ap);
    return -1;
}

/* ------------------------------------------------------------------ */
/* Global state                                                        */
/* ------------------------------------------------------------------ */

static id<MTLDevice> g_dev;
static id<MTLCommandQueue> g_queue;
static bool g_force_off = false;
static bool g_ready = false;
static int g_nslots = MAX_FRAMES;

/* library cache */
static pthread_mutex_t g_lib_lock = PTHREAD_MUTEX_INITIALIZER;
static NSMutableDictionary<NSString *, NSMutableArray *> *g_libs; /* hash -> [ [src, lib], ... ] */
static int64_t g_lib_compiles, g_lib_hits;

/* counters */
static int64_t g_n_buffers, g_n_textures, g_n_pipelines, g_res_bytes, g_allocs;
static int64_t g_submitted;
static int64_t g_completed;
static int64_t g_drawables;
static pthread_mutex_t g_done_lock = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t g_done_cv = PTHREAD_COND_INITIALIZER;
static double g_gpu_ms = 0.0;
static int g_pass_n = 0;
static double g_pass_ms[MAX_TIMED_PASSES];

/* frame */
static dispatch_semaphore_t g_sem;
static int64_t g_frame_no = 0;     /* frames begun */
static bool g_frame_open = false;
static int g_slot = 0;
static id<MTLCommandBuffer> g_cmd;
static id<MTLComputeCommandEncoder> g_cenc;
static id<MTLRenderCommandEncoder> g_renc;
static id<MTLBuffer> g_ring[MAX_FRAMES];
static int64_t g_ring_off = 0;
static BufBind g_bbuf[MAX_BUF_SLOTS];
static int32_t g_btex[MAX_TEX_SLOTS];
static int8_t g_bsamp[MAX_TEX_SLOTS]; /* 0 unset, 1 + linear*2 + repeat */
static id<MTLSamplerState> g_samplers[4];
static int g_pass_cfmt, g_pass_dfmt, g_pass_w, g_pass_h;
static bool g_pass_open;
static id<MTLCounterSampleBuffer> g_sb[MAX_FRAMES];
static bool g_timing_ok = false;
static char g_next_name[32];
static char g_pass_names[MAX_FRAMES][MAX_TIMED_PASSES][32];
static char g_last_names[MAX_TIMED_PASSES][32];
static int g_frame_passes = 0;     /* timed passes encoded in the open frame */
static double g_ts_scale = 1.0;    /* GPU timestamp ticks to nanoseconds */

/* window */
static int32_t g_ov_tex = 0;
static CAMetalLayer *g_layer;
static void *g_gfx_ctx;
static id<CAMetalDrawable> g_drawable;
static bool g_drawn;               /* the drawable was drawn into this frame */
static int g_win_w, g_win_h;
static double g_win_scale = 1.0;
typedef int32_t (*set_layer_fn)(void *, void *);
typedef int32_t (*view_info_fn)(void *, double *);

/* internal blit pipelines: [dst format index][blend] */
static id<MTLRenderPipelineState> g_blit_ps[8][4];

static const char *blit_msl =
    "#include <metal_stdlib>\n"
    "using namespace metal;\n"
    "struct O { float4 p [[position]]; float2 uv; };\n"
    "vertex O blit_vs(uint vid [[vertex_id]]) {\n"
    "  float2 xy = float2(float((vid << 1) & 2u), float(vid & 2u));\n"
    "  O o; o.p = float4(xy * 2.0 - 1.0, 0.0, 1.0); o.uv = float2(xy.x, 1.0 - xy.y); return o; }\n"
    "fragment float4 blit_fs(O i [[stage_in]], texture2d<float> t [[texture(0)]], sampler s [[sampler(0)]]) {\n"
    "  return t.sample(s, i.uv); }\n";

/* ------------------------------------------------------------------ */
/* Handles                                                             */
/* ------------------------------------------------------------------ */

static int32_t tab_add(GLRes *r)
{
    pthread_mutex_lock(&g_tab_lock);
    int32_t idx;
    if (g_nfree > 0) idx = g_free[--g_nfree];
    else if (g_next < MAX_RES) idx = g_next++;
    else { pthread_mutex_unlock(&g_tab_lock); return fail("too many live resources (%d)", MAX_RES); }
    g_gen[idx] = (uint16_t)((g_gen[idx] % 1023) + 1);
    g_tab[idx] = r;
    int32_t h = ((int32_t)g_gen[idx] << 20) | (idx + 1);
    pthread_mutex_unlock(&g_tab_lock);
    return h;
}

static GLRes *tab_get(int32_t h, int kind)
{
    if (h <= 0) return nil;
    int32_t idx = (h & 0xFFFFF) - 1;
    int32_t gen = h >> 20;
    if (idx < 0 || idx >= MAX_RES) return nil;
    pthread_mutex_lock(&g_tab_lock);
    GLRes *r = g_tab[idx];
    if (r && g_gen[idx] != gen) r = nil;
    pthread_mutex_unlock(&g_tab_lock);
    if (r && kind && r->kind != kind) return nil;
    return r;
}

static GLRes *tab_take(int32_t h)
{
    if (h <= 0) return nil;
    int32_t idx = (h & 0xFFFFF) - 1;
    int32_t gen = h >> 20;
    if (idx < 0 || idx >= MAX_RES) return nil;
    pthread_mutex_lock(&g_tab_lock);
    GLRes *r = g_tab[idx];
    if (r && g_gen[idx] == gen) { g_tab[idx] = nil; g_free[g_nfree++] = idx; }
    else r = nil;
    pthread_mutex_unlock(&g_tab_lock);
    return r;
}

static int copy_index(GLRes *r) { return r->ncopies > 1 ? (g_slot % r->ncopies) : 0; }

/* ------------------------------------------------------------------ */
/* Formats                                                             */
/* ------------------------------------------------------------------ */

static MTLPixelFormat mtl_fmt(int f, int *bpp)
{
    switch (f) {
    case FLOW_GL_RGBA8: *bpp = 4; return MTLPixelFormatRGBA8Unorm;
    case FLOW_GL_BGRA8: *bpp = 4; return MTLPixelFormatBGRA8Unorm;
    case FLOW_GL_RGBA16F: *bpp = 8; return MTLPixelFormatRGBA16Float;
    case FLOW_GL_R32F: *bpp = 4; return MTLPixelFormatR32Float;
    case FLOW_GL_RGBA32F: *bpp = 16; return MTLPixelFormatRGBA32Float;
    case FLOW_GL_R8: *bpp = 1; return MTLPixelFormatR8Unorm;
    case FLOW_GL_DEPTH32F: *bpp = 4; return MTLPixelFormatDepth32Float;
    }
    *bpp = 0;
    return MTLPixelFormatInvalid;
}

static int fmt_index(int f) { return (f >= 1 && f <= 7) ? f : 0; }

/* ------------------------------------------------------------------ */
/* Lifecycle                                                           */
/* ------------------------------------------------------------------ */

static NSString *hash_key(const char *s)
{
    uint64_t h = 1469598103934665603ULL;
    for (const unsigned char *p = (const unsigned char *)s; *p; p++) { h ^= *p; h *= 1099511628211ULL; }
    return [NSString stringWithFormat:@"%016llx", (unsigned long long)h];
}

static void make_samplers(void)
{
    for (int i = 0; i < 4; i++) {
        MTLSamplerDescriptor *d = [MTLSamplerDescriptor new];
        MTLSamplerMinMagFilter f = (i & 2) ? MTLSamplerMinMagFilterLinear : MTLSamplerMinMagFilterNearest;
        d.minFilter = f;
        d.magFilter = f;
        MTLSamplerAddressMode a = (i & 1) ? MTLSamplerAddressModeRepeat : MTLSamplerAddressModeClampToEdge;
        d.sAddressMode = a;
        d.tAddressMode = a;
        g_samplers[i] = [g_dev newSamplerStateWithDescriptor:d];
        g_allocs++;
    }
}

static void calibrate_timestamps(void)
{
    /* GPU counter ticks to ns: compare two (cpu, gpu) timestamp pairs 40 ms apart. */
    MTLTimestamp c0 = 0, g0 = 0, c1 = 0, g1 = 0;
    [g_dev sampleTimestamps:&c0 gpuTimestamp:&g0];
    usleep(40000);
    [g_dev sampleTimestamps:&c1 gpuTimestamp:&g1];
    if (g1 > g0 && c1 > c0) g_ts_scale = (double)(c1 - c0) / (double)(g1 - g0);
}

static void setup_timing(void)
{
    g_timing_ok = false;
    if (@available(macOS 11.0, *)) {
        if (![g_dev supportsCounterSampling:MTLCounterSamplingPointAtStageBoundary]) return;
        id<MTLCounterSet> ts = nil;
        for (id<MTLCounterSet> cs in g_dev.counterSets) {
            if ([cs.name isEqualToString:MTLCommonCounterSetTimestamp]) ts = cs;
        }
        if (!ts) return;
        for (int i = 0; i < g_nslots; i++) {
            MTLCounterSampleBufferDescriptor *d = [MTLCounterSampleBufferDescriptor new];
            d.counterSet = ts;
            d.storageMode = MTLStorageModeShared;
            d.sampleCount = MAX_TIMED_PASSES * 2;
            d.label = @"flow_gl_pass_timing";
            NSError *e = nil;
            g_sb[i] = [g_dev newCounterSampleBufferWithDescriptor:d error:&e];
            if (!g_sb[i]) { for (int k = 0; k < i; k++) g_sb[k] = nil; return; }
        }
        calibrate_timestamps();
        g_timing_ok = true;
    }
}

int32_t flow_gl_init(int32_t flags)
{
    @autoreleasepool {
        if (g_ready) return 1;
        const char *env = getenv("FLOW_GL_FORCE_OFF");
        if (g_force_off || (env && env[0] == '1')) { set_err("GPU path forced off"); return 0; }
        g_dev = MTLCreateSystemDefaultDevice();
        if (!g_dev) { set_err("no Metal device"); return 0; }
        if (!g_dev.hasUnifiedMemory) { g_dev = nil; set_err("device has no unified memory"); return 0; }
        g_queue = [g_dev newCommandQueue];
        if (!g_queue) { g_dev = nil; set_err("cannot create a command queue"); return 0; }
        int n = flags & 3;
        g_nslots = (n >= 1 && n <= 3) ? n : MAX_FRAMES;
        g_sem = dispatch_semaphore_create(g_nslots);
        g_libs = [NSMutableDictionary new];
        for (int i = 0; i < g_nslots; i++) {
            g_ring[i] = [g_dev newBufferWithLength:RING_BYTES options:MTLResourceStorageModeShared | MTLResourceCPUCacheModeWriteCombined];
            if (!g_ring[i]) { set_err("cannot allocate the uniform ring"); g_dev = nil; return 0; }
            g_allocs++;
        }
        make_samplers();
        setup_timing();
        g_frame_no = 0; g_submitted = 0; g_completed = 0;
        g_frame_open = false;
        g_ready = true;
        return 1;
    }
}

int32_t flow_gl_available(void) { return g_ready ? 1 : 0; }

void flow_gl_force_off(int32_t off) { g_force_off = off != 0; }

const char *flow_gl_last_error(void) { return t_err; }

const char *flow_gl_device_name(void)
{
    static __thread char name[128];
    if (!g_ready) return "";
    snprintf(name, sizeof name, "%s", g_dev.name.UTF8String);
    return name;
}

static void wait_done_to(int64_t target)
{
    pthread_mutex_lock(&g_done_lock);
    while (g_completed < target) pthread_cond_wait(&g_done_cv, &g_done_lock);
    pthread_mutex_unlock(&g_done_lock);
}

int32_t flow_gl_wait_idle(void)
{
    if (!g_ready) return fail("GPU host is not initialised");
    wait_done_to(g_submitted);
    return 0;
}

static void end_encoders(void);

void flow_gl_shutdown(void)
{
    @autoreleasepool {
        if (!g_ready) return;
        if (g_frame_open) { end_encoders(); [g_cmd commit]; g_submitted++; g_frame_open = false; }
        wait_done_to(g_submitted);
        flow_gl_detach_window();
        pthread_mutex_lock(&g_tab_lock);
        for (int i = 0; i < g_next; i++) g_tab[i] = nil;
        g_next = 0; g_nfree = 0;
        pthread_mutex_unlock(&g_tab_lock);
        for (int i = 0; i < MAX_FRAMES; i++) { g_ring[i] = nil; g_sb[i] = nil; }
        for (int i = 0; i < 4; i++) g_samplers[i] = nil;
        memset(g_blit_ps, 0, sizeof g_blit_ps);
        g_libs = nil; g_cmd = nil; g_cenc = nil; g_renc = nil; g_drawable = nil;
        g_queue = nil; g_dev = nil;
        g_n_buffers = g_n_textures = g_n_pipelines = g_res_bytes = 0;
        g_ready = false;
    }
}

int64_t flow_gl_stat(int32_t which)
{
    switch (which) {
    case FLOW_GL_STAT_BUFFERS: return g_n_buffers;
    case FLOW_GL_STAT_TEXTURES: return g_n_textures;
    case FLOW_GL_STAT_PIPELINES: return g_n_pipelines;
    case FLOW_GL_STAT_RESOURCE_BYTES: return g_res_bytes;
    case FLOW_GL_STAT_ALLOCATIONS: return g_allocs;
    case FLOW_GL_STAT_FRAMES_SUBMITTED: return g_submitted;
    case FLOW_GL_STAT_FRAMES_COMPLETED: return g_completed;
    case FLOW_GL_STAT_DEVICE_BYTES: return g_ready ? (int64_t)g_dev.currentAllocatedSize : 0;
    case FLOW_GL_STAT_PROCESS_RSS: {
        mach_task_basic_info_data_t info;
        mach_msg_type_number_t cnt = MACH_TASK_BASIC_INFO_COUNT;
        if (task_info(mach_task_self(), MACH_TASK_BASIC_INFO, (task_info_t)&info, &cnt) != KERN_SUCCESS) return -1;
        return (int64_t)info.resident_size;
    }
    case FLOW_GL_STAT_LIBRARY_COMPILES: return g_lib_compiles;
    case FLOW_GL_STAT_LIBRARY_HITS: return g_lib_hits;
    case FLOW_GL_STAT_DRAWABLES: return g_drawables;
    case FLOW_GL_STAT_FRAME_SLOTS: return g_nslots;
    case FLOW_GL_STAT_PASS_TIMING: return g_timing_ok ? 1 : 0;
    case FLOW_GL_STAT_UNIFIED_MEMORY: return g_ready ? 1 : 0;
    case FLOW_GL_STAT_OVERLAY_TEXTURE: return g_ov_tex;
    }
    return -1;
}

#define NEED_READY() do { if (!g_ready) return fail("GPU host is not initialised (call gl_init)"); } while (0)

/* ------------------------------------------------------------------ */
/* Window                                                              */
/* ------------------------------------------------------------------ */

static void sync_layer_size(void)
{
    if (!g_layer || !g_gfx_ctx) return;
    view_info_fn info = (view_info_fn)dlsym(RTLD_DEFAULT, "flow_gfx_view_info");
    if (!info) return;
    double v[3] = {0, 0, 1};
    if (!info(g_gfx_ctx, v) || v[0] < 1 || v[1] < 1) return;
    double scale = v[2] > 0 ? v[2] : 1.0;
    int w = (int)(v[0] * scale + 0.5), h = (int)(v[1] * scale + 0.5);
    if (w != g_win_w || h != g_win_h || scale != g_win_scale) {
        g_win_w = w; g_win_h = h; g_win_scale = scale;
        [CATransaction begin];
        [CATransaction setDisableActions:YES];
        g_layer.contentsScale = scale;
        g_layer.frame = CGRectMake(0, 0, v[0], v[1]);
        g_layer.drawableSize = CGSizeMake(w, h);
        [CATransaction commit];
    }
}

int32_t flow_gl_attach_window(void *gfx_ctx, int32_t vsync)
{
    @autoreleasepool {
        NEED_READY();
        if (!gfx_ctx) return fail("attach_window: null window context");
        set_layer_fn setl = (set_layer_fn)dlsym(RTLD_DEFAULT, "flow_gfx_set_layer");
        view_info_fn info = (view_info_fn)dlsym(RTLD_DEFAULT, "flow_gfx_view_info");
        if (!setl || !info) return fail("attach_window: this program has no gfx window backend");
        if (g_layer) flow_gl_detach_window();
        CAMetalLayer *l = [CAMetalLayer layer];
        l.device = g_dev;
        l.pixelFormat = MTLPixelFormatBGRA8Unorm;
        l.framebufferOnly = YES;
        l.opaque = YES;
        l.maximumDrawableCount = 3;
        l.displaySyncEnabled = vsync != 0;
        l.allowsNextDrawableTimeout = YES;
        g_layer = l;
        g_gfx_ctx = gfx_ctx;
        g_win_w = g_win_h = 0;
        if (!setl(gfx_ctx, (__bridge void *)l)) { g_layer = nil; g_gfx_ctx = NULL; return fail("attach_window: the window rejected the layer"); }
        sync_layer_size();
        return 0;
    }
}

void flow_gl_detach_window(void)
{
    @autoreleasepool {
        if (!g_layer) return;
        set_layer_fn setl = (set_layer_fn)dlsym(RTLD_DEFAULT, "flow_gfx_set_layer");
        if (setl && g_gfx_ctx) setl(g_gfx_ctx, NULL);
        g_drawable = nil;
        g_layer = nil;
        g_gfx_ctx = NULL;
        g_win_w = g_win_h = 0;
    }
}

int32_t flow_gl_window_info(int32_t *out)
{
    if (!out) return -1;
    sync_layer_size();
    out[0] = g_layer ? g_win_w : 0;
    out[1] = g_layer ? g_win_h : 0;
    out[2] = (int32_t)(g_win_scale * 100.0 + 0.5);
    out[3] = g_layer ? 1 : 0;
    return 0;
}

void flow_gl_set_vsync(int32_t on)
{
    if (g_layer) g_layer.displaySyncEnabled = on != 0;
}

/* ------------------------------------------------------------------ */
/* Buffers                                                             */
/* ------------------------------------------------------------------ */

int32_t flow_gl_buffer_new(int64_t bytes, int32_t flags)
{
    @autoreleasepool {
        NEED_READY();
        if (bytes <= 0 || bytes > (int64_t)g_dev.maxBufferLength) return fail("buffer_new: bad size %lld", (long long)bytes);
        GLRes *r = [GLRes new];
        r->kind = KIND_BUFFER;
        r->bytes = bytes;
        r->ncopies = (flags & FLOW_GL_BUF_STREAM) ? g_nslots : 1;
        for (int i = 0; i < r->ncopies; i++) {
            r->buf[i] = [g_dev newBufferWithLength:(NSUInteger)bytes options:MTLResourceStorageModeShared];
            if (!r->buf[i]) return fail("buffer_new: allocation of %lld bytes failed", (long long)bytes);
            g_allocs++;
        }
        int32_t h = tab_add(r);
        if (h < 0) return h;
        g_n_buffers++;
        g_res_bytes += bytes * r->ncopies;
        return h;
    }
}

int32_t flow_gl_buffer_wrap(uint8_t *ptr, int64_t bytes)
{
    @autoreleasepool {
        NEED_READY();
        long page = sysconf(_SC_PAGESIZE);
        if (!ptr || bytes <= 0 || ((uintptr_t)ptr % (uintptr_t)page) != 0 || (bytes % page) != 0)
            return fail("buffer_wrap: the pointer and the size must both be page aligned (page = %ld)", page);
        GLRes *r = [GLRes new];
        r->kind = KIND_BUFFER;
        r->bytes = bytes;
        r->ncopies = 1;
        r->buf[0] = [g_dev newBufferWithBytesNoCopy:ptr length:(NSUInteger)bytes options:MTLResourceStorageModeShared deallocator:nil];
        if (!r->buf[0]) return fail("buffer_wrap: Metal refused the memory");
        g_allocs++;
        int32_t h = tab_add(r);
        if (h < 0) return h;
        g_n_buffers++;
        return h;
    }
}

static int ensure_frame(void);

static int32_t buffer_copy_target(GLRes *r)
{
    if (r->ncopies > 1 && !g_frame_open) return fail("stream resources are written between gl_begin_frame and gl_present");
    return copy_index(r);
}

int32_t flow_gl_buffer_write(int32_t h, int64_t offset, const uint8_t *src, int64_t n)
{
    NEED_READY();
    GLRes *r = tab_get(h, KIND_BUFFER);
    if (!r) return fail("buffer_write: invalid buffer handle %d", h);
    if (!src && n > 0) return fail("buffer_write: null source");
    if (offset < 0 || n < 0 || offset + n > r->bytes) return fail("buffer_write: range %lld+%lld exceeds the buffer (%lld bytes)", (long long)offset, (long long)n, (long long)r->bytes);
    int c = buffer_copy_target(r);
    if (c < 0) return -1;
    memcpy((uint8_t *)r->buf[c].contents + offset, src, (size_t)n);
    return 0;
}

uint8_t *flow_gl_buffer_ptr(int32_t h)
{
    if (!g_ready) { set_err("GPU host is not initialised"); return NULL; }
    GLRes *r = tab_get(h, KIND_BUFFER);
    if (!r) { set_err("buffer_ptr: invalid buffer handle %d", h); return NULL; }
    int c = buffer_copy_target(r);
    if (c < 0) return NULL;
    return (uint8_t *)r->buf[c].contents;
}

int32_t flow_gl_buffer_read(int32_t h, int64_t offset, uint8_t *dst, int64_t n)
{
    NEED_READY();
    GLRes *r = tab_get(h, KIND_BUFFER);
    if (!r) return fail("buffer_read: invalid buffer handle %d", h);
    if (!dst || offset < 0 || n < 0 || offset + n > r->bytes) return fail("buffer_read: bad range");
    if (g_frame_open) return fail("buffer_read: a frame is open; submit it first");
    wait_done_to(g_submitted);
    int c = r->ncopies > 1 ? (int)((g_frame_no > 0 ? g_frame_no - 1 : 0) % r->ncopies) : 0;
    memcpy(dst, (uint8_t *)r->buf[c].contents + offset, (size_t)n);
    return 0;
}

int32_t flow_gl_buffer_free(int32_t h)
{
    @autoreleasepool {
        GLRes *r = tab_take(h);
        if (!r || r->kind != KIND_BUFFER) return fail("buffer_free: invalid buffer handle %d", h);
        g_n_buffers--;
        g_res_bytes -= r->bytes * r->ncopies;
        return 0;
    }
}

/* ------------------------------------------------------------------ */
/* Textures                                                            */
/* ------------------------------------------------------------------ */

int32_t flow_gl_texture_new(int32_t w, int32_t hh, int32_t format, int32_t usage)
{
    @autoreleasepool {
        NEED_READY();
        int bpp;
        MTLPixelFormat pf = mtl_fmt(format, &bpp);
        if (pf == MTLPixelFormatInvalid) return fail("texture_new: unknown format %d", format);
        if (w < 1 || hh < 1 || w > 16384 || hh > 16384) return fail("texture_new: bad size %dx%d", w, hh);
        GLRes *r = [GLRes new];
        r->kind = KIND_TEXTURE;
        r->w = w; r->h = hh; r->format = format; r->usage = usage;
        r->gpu_only = (usage & TEX_GPU_ONLY) != 0 || format == FLOW_GL_DEPTH32F;
        if ((usage & FLOW_GL_TEX_STREAM) && r->gpu_only) return fail("texture_new: a stream texture must be CPU writable");
        r->ncopies = (usage & FLOW_GL_TEX_STREAM) ? g_nslots : 1;
        MTLTextureUsage mu = 0;
        if (usage & FLOW_GL_TEX_SAMPLED) mu |= MTLTextureUsageShaderRead;
        if (usage & FLOW_GL_TEX_STORAGE) mu |= MTLTextureUsageShaderRead | MTLTextureUsageShaderWrite;
        if (usage & FLOW_GL_TEX_TARGET) mu |= MTLTextureUsageRenderTarget;
        if (mu == 0) mu = MTLTextureUsageShaderRead;
        for (int i = 0; i < r->ncopies; i++) {
            MTLTextureDescriptor *d = [MTLTextureDescriptor texture2DDescriptorWithPixelFormat:pf width:(NSUInteger)w height:(NSUInteger)hh mipmapped:NO];
            d.usage = mu;
            d.storageMode = r->gpu_only ? MTLStorageModePrivate : MTLStorageModeShared;
            r->tex[i] = [g_dev newTextureWithDescriptor:d];
            if (!r->tex[i]) return fail("texture_new: allocation of %dx%d failed", w, hh);
            g_allocs++;
        }
        r->bytes = (int64_t)w * hh * bpp;
        int32_t h = tab_add(r);
        if (h < 0) return h;
        g_n_textures++;
        g_res_bytes += r->bytes * r->ncopies;
        return h;
    }
}

int32_t flow_gl_texture_upload_rect(int32_t h, int32_t x, int32_t y, int32_t w, int32_t hh, const uint8_t *src, int32_t bpr)
{
    @autoreleasepool {
        NEED_READY();
        GLRes *r = tab_get(h, KIND_TEXTURE);
        if (!r) return fail("texture_upload: invalid texture handle %d", h);
        if (r->gpu_only) return fail("texture_upload: texture is GPU only");
        if (!src) return fail("texture_upload: null source");
        if (x < 0 || y < 0 || w < 1 || hh < 1 || x + w > r->w || y + hh > r->h) return fail("texture_upload: rectangle outside the texture");
        int bpp; mtl_fmt(r->format, &bpp);
        if (bpr < w * bpp) return fail("texture_upload: bytes_per_row %d too small", bpr);
        int c = buffer_copy_target(r);
        if (c < 0) return -1;
        [r->tex[c] replaceRegion:MTLRegionMake2D((NSUInteger)x, (NSUInteger)y, (NSUInteger)w, (NSUInteger)hh)
                     mipmapLevel:0 withBytes:src bytesPerRow:(NSUInteger)bpr];
        return 0;
    }
}

int32_t flow_gl_texture_upload(int32_t h, const uint8_t *src, int32_t bpr)
{
    GLRes *r = tab_get(h, KIND_TEXTURE);
    if (!r) return fail("texture_upload: invalid texture handle %d", h);
    return flow_gl_texture_upload_rect(h, 0, 0, r->w, r->h, src, bpr);
}

int32_t flow_gl_texture_read(int32_t h, uint8_t *dst, int32_t bpr)
{
    @autoreleasepool {
        NEED_READY();
        GLRes *r = tab_get(h, KIND_TEXTURE);
        if (!r) return fail("texture_read: invalid texture handle %d", h);
        if (!dst) return fail("texture_read: null destination");
        if (r->format == FLOW_GL_DEPTH32F) return fail("texture_read: depth textures cannot be read back");
        int bpp; mtl_fmt(r->format, &bpp);
        if (bpr < r->w * bpp) return fail("texture_read: bytes_per_row %d too small", bpr);
        if (g_frame_open) return fail("texture_read: a frame is open; submit it first");
        wait_done_to(g_submitted);
        int c = r->ncopies > 1 ? (int)((g_frame_no > 0 ? g_frame_no - 1 : 0) % r->ncopies) : 0;
        id<MTLTexture> t = r->tex[c];
        if (!r->gpu_only) {
            [t getBytes:dst bytesPerRow:(NSUInteger)bpr fromRegion:MTLRegionMake2D(0, 0, (NSUInteger)r->w, (NSUInteger)r->h) mipmapLevel:0];
            return 0;
        }
        NSUInteger row = (NSUInteger)r->w * (NSUInteger)bpp;
        id<MTLBuffer> stage = [g_dev newBufferWithLength:row * (NSUInteger)r->h options:MTLResourceStorageModeShared];
        if (!stage) return fail("texture_read: cannot allocate a staging buffer");
        id<MTLCommandBuffer> cb = [g_queue commandBuffer];
        id<MTLBlitCommandEncoder> be = [cb blitCommandEncoder];
        [be copyFromTexture:t sourceSlice:0 sourceLevel:0 sourceOrigin:MTLOriginMake(0, 0, 0)
                 sourceSize:MTLSizeMake((NSUInteger)r->w, (NSUInteger)r->h, 1)
                   toBuffer:stage destinationOffset:0 destinationBytesPerRow:row destinationBytesPerImage:row * (NSUInteger)r->h];
        [be endEncoding];
        [cb commit];
        [cb waitUntilCompleted];
        if (cb.status != MTLCommandBufferStatusCompleted) return fail("texture_read: blit failed");
        for (int y = 0; y < r->h; y++) memcpy(dst + (size_t)y * (size_t)bpr, (uint8_t *)stage.contents + (size_t)y * row, row);
        return 0;
    }
}

int32_t flow_gl_texture_free(int32_t h)
{
    @autoreleasepool {
        GLRes *r = tab_take(h);
        if (!r || r->kind != KIND_TEXTURE) return fail("texture_free: invalid texture handle %d", h);
        g_n_textures--;
        g_res_bytes -= r->bytes * r->ncopies;
        return 0;
    }
}

/* ------------------------------------------------------------------ */
/* Pipelines                                                           */
/* ------------------------------------------------------------------ */

/* Compile once per distinct source. Returns nil and sets the error on failure. */
static id<MTLLibrary> library_for(const char *msl)
{
    NSString *key = hash_key(msl);
    NSString *src = [NSString stringWithUTF8String:msl];
    pthread_mutex_lock(&g_lib_lock);
    NSMutableArray *bucket = g_libs[key];
    for (NSArray *e in bucket) {
        if ([e[0] isEqualToString:src]) { g_lib_hits++; id<MTLLibrary> l = e[1]; pthread_mutex_unlock(&g_lib_lock); return l; }
    }
    NSError *err = nil;
    id<MTLLibrary> lib = [g_dev newLibraryWithSource:src options:nil error:&err];
    if (!lib) {
        const char *m = err ? err.localizedDescription.UTF8String : "unknown error";
        set_err("shader compile failed: %.400s", m);
        pthread_mutex_unlock(&g_lib_lock);
        return nil;
    }
    g_lib_compiles++;
    g_allocs++;
    if (!bucket) { bucket = [NSMutableArray new]; g_libs[key] = bucket; }
    [bucket addObject:@[src, lib]];
    pthread_mutex_unlock(&g_lib_lock);
    return lib;
}

int32_t flow_gl_compute_pipeline(const char *msl, const char *entry)
{
    @autoreleasepool {
        NEED_READY();
        if (!msl || !entry) return fail("compute_pipeline: null source or entry");
        id<MTLLibrary> lib = library_for(msl);
        if (!lib) return -1;
        id<MTLFunction> fn = [lib newFunctionWithName:[NSString stringWithUTF8String:entry]];
        if (!fn) return fail("compute_pipeline: no function named '%s'", entry);
        NSError *e = nil;
        id<MTLComputePipelineState> ps = [g_dev newComputePipelineStateWithFunction:fn error:&e];
        if (!ps) return fail("compute_pipeline: %.400s", e ? e.localizedDescription.UTF8String : "failed");
        g_allocs++;
        GLRes *r = [GLRes new];
        r->kind = KIND_COMPUTE;
        r->cps = ps;
        r->max_threads = ps.maxTotalThreadsPerThreadgroup;
        r->exec_width = ps.threadExecutionWidth;
        r->built = true;
        int32_t h = tab_add(r);
        if (h > 0) g_n_pipelines++;
        return h;
    }
}

int32_t flow_gl_render_pipeline_begin(const char *msl, const char *vs, const char *fs, int32_t cfmt, int32_t dfmt, int32_t blend)
{
    @autoreleasepool {
        NEED_READY();
        if (!msl || !vs || !fs) return fail("render_pipeline: null source or entry");
        int bpp;
        if (cfmt != FLOW_GL_FORMAT_NONE && (mtl_fmt(cfmt, &bpp) == MTLPixelFormatInvalid || cfmt == FLOW_GL_DEPTH32F)) return fail("render_pipeline: bad colour format %d", cfmt);
        if (dfmt != 0 && dfmt != FLOW_GL_DEPTH32F) return fail("render_pipeline: depth format must be 0 or GL_DEPTH32F");
        if (blend < 0 || blend > 3) return fail("render_pipeline: bad blend mode %d", blend);
        GLRes *r = [GLRes new];
        r->kind = KIND_RENDER;
        r->msl = [NSString stringWithUTF8String:msl];
        r->vs = [NSString stringWithUTF8String:vs];
        r->fs = [NSString stringWithUTF8String:fs];
        r->cfmt = cfmt; r->dfmt = dfmt; r->blend = blend;
        r->cull = FLOW_GL_CULL_NONE;
        r->depth_mode = dfmt ? FLOW_GL_DEPTH_WRITE : FLOW_GL_DEPTH_OFF;
        r->vd = [MTLVertexDescriptor vertexDescriptor];
        return tab_add(r);
    }
}

int32_t flow_gl_pipeline_vertex_layout(int32_t h, int32_t slot, int32_t stride, int32_t per_instance)
{
    GLRes *r = tab_get(h, KIND_RENDER);
    if (!r || r->built) return fail("vertex_layout: not an unbuilt render pipeline");
    if (slot < 0 || slot > 14 || stride < 1) return fail("vertex_layout: bad slot or stride");
    r->vd.layouts[VERTEX_SLOT_BASE + slot].stride = (NSUInteger)stride;
    r->vd.layouts[VERTEX_SLOT_BASE + slot].stepFunction = per_instance ? MTLVertexStepFunctionPerInstance : MTLVertexStepFunctionPerVertex;
    r->has_vd = true;
    return 0;
}

int32_t flow_gl_pipeline_vertex_attr(int32_t h, int32_t loc, int32_t slot, int32_t format, int32_t offset)
{
    GLRes *r = tab_get(h, KIND_RENDER);
    if (!r || r->built) return fail("vertex_attr: not an unbuilt render pipeline");
    if (loc < 0 || loc > 30 || slot < 0 || slot > 14 || offset < 0) return fail("vertex_attr: bad location, slot or offset");
    MTLVertexFormat f;
    switch (format) {
    case FLOW_GL_V_FLOAT: f = MTLVertexFormatFloat; break;
    case FLOW_GL_V_FLOAT2: f = MTLVertexFormatFloat2; break;
    case FLOW_GL_V_FLOAT3: f = MTLVertexFormatFloat3; break;
    case FLOW_GL_V_FLOAT4: f = MTLVertexFormatFloat4; break;
    case FLOW_GL_V_UCHAR4_NORM: f = MTLVertexFormatUChar4Normalized; break;
    case FLOW_GL_V_UINT: f = MTLVertexFormatUInt; break;
    case FLOW_GL_V_INT: f = MTLVertexFormatInt; break;
    default: return fail("vertex_attr: unknown format %d", format);
    }
    r->vd.attributes[loc].format = f;
    r->vd.attributes[loc].offset = (NSUInteger)offset;
    r->vd.attributes[loc].bufferIndex = (NSUInteger)(VERTEX_SLOT_BASE + slot);
    r->has_vd = true;
    return 0;
}

int32_t flow_gl_pipeline_state(int32_t h, int32_t cull, int32_t depth_mode)
{
    GLRes *r = tab_get(h, KIND_RENDER);
    if (!r || r->built) return fail("pipeline_state: not an unbuilt render pipeline");
    if (cull < 0 || cull > 2 || depth_mode < 0 || depth_mode > 2) return fail("pipeline_state: bad cull or depth mode");
    r->cull = cull; r->depth_mode = depth_mode;
    return 0;
}

int32_t flow_gl_pipeline_build(int32_t h)
{
    @autoreleasepool {
        NEED_READY();
        GLRes *r = tab_get(h, KIND_RENDER);
        if (!r) return fail("pipeline_build: invalid render pipeline handle %d", h);
        if (r->built) return 0;
        id<MTLLibrary> lib = library_for(r->msl.UTF8String);
        if (!lib) return -1;
        id<MTLFunction> vf = [lib newFunctionWithName:r->vs];
        id<MTLFunction> ff = [lib newFunctionWithName:r->fs];
        if (!vf) return fail("pipeline_build: no vertex function '%s'", r->vs.UTF8String);
        if (!ff) return fail("pipeline_build: no fragment function '%s'", r->fs.UTF8String);
        MTLRenderPipelineDescriptor *d = [MTLRenderPipelineDescriptor new];
        d.vertexFunction = vf;
        d.fragmentFunction = ff;
        int bpp;
        MTLRenderPipelineColorAttachmentDescriptor *ca = d.colorAttachments[0];
        ca.pixelFormat = r->cfmt ? mtl_fmt(r->cfmt, &bpp) : MTLPixelFormatInvalid;
        if (r->cfmt && r->blend != FLOW_GL_BLEND_NONE) {
            ca.blendingEnabled = YES;
            ca.rgbBlendOperation = MTLBlendOperationAdd;
            ca.alphaBlendOperation = MTLBlendOperationAdd;
            if (r->blend == FLOW_GL_BLEND_ALPHA) {
                ca.sourceRGBBlendFactor = MTLBlendFactorSourceAlpha;
                ca.destinationRGBBlendFactor = MTLBlendFactorOneMinusSourceAlpha;
                ca.sourceAlphaBlendFactor = MTLBlendFactorOne;
                ca.destinationAlphaBlendFactor = MTLBlendFactorOneMinusSourceAlpha;
            } else if (r->blend == FLOW_GL_BLEND_PREMUL) {
                ca.sourceRGBBlendFactor = MTLBlendFactorOne;
                ca.destinationRGBBlendFactor = MTLBlendFactorOneMinusSourceAlpha;
                ca.sourceAlphaBlendFactor = MTLBlendFactorOne;
                ca.destinationAlphaBlendFactor = MTLBlendFactorOneMinusSourceAlpha;
            } else {
                ca.sourceRGBBlendFactor = MTLBlendFactorOne;
                ca.destinationRGBBlendFactor = MTLBlendFactorOne;
                ca.sourceAlphaBlendFactor = MTLBlendFactorOne;
                ca.destinationAlphaBlendFactor = MTLBlendFactorOne;
            }
        }
        if (r->dfmt) d.depthAttachmentPixelFormat = MTLPixelFormatDepth32Float;
        if (r->has_vd) d.vertexDescriptor = r->vd;
        NSError *e = nil;
        id<MTLRenderPipelineState> ps = [g_dev newRenderPipelineStateWithDescriptor:d error:&e];
        if (!ps) return fail("pipeline_build: %.400s", e ? e.localizedDescription.UTF8String : "failed");
        g_allocs++;
        if (r->dfmt) {
            MTLDepthStencilDescriptor *dd = [MTLDepthStencilDescriptor new];
            dd.depthCompareFunction = r->depth_mode == FLOW_GL_DEPTH_OFF ? MTLCompareFunctionAlways : MTLCompareFunctionLess;
            dd.depthWriteEnabled = r->depth_mode == FLOW_GL_DEPTH_WRITE;
            r->dss = [g_dev newDepthStencilStateWithDescriptor:dd];
            g_allocs++;
        }
        r->rps = ps;
        r->built = true;
        g_n_pipelines++;
        return 0;
    }
}

int32_t flow_gl_pipeline_free(int32_t h)
{
    @autoreleasepool {
        GLRes *r = tab_take(h);
        if (!r || (r->kind != KIND_COMPUTE && r->kind != KIND_RENDER)) return fail("pipeline_free: invalid pipeline handle %d", h);
        if (r->built) g_n_pipelines--;
        return 0;
    }
}

/* ------------------------------------------------------------------ */
/* Frame                                                               */
/* ------------------------------------------------------------------ */

static void on_complete(id<MTLCommandBuffer> cb, int slot, int npass)
{
    double ms = (cb.GPUEndTime - cb.GPUStartTime) * 1000.0;
    double pm[MAX_TIMED_PASSES];
    char names[MAX_TIMED_PASSES][32];
    memcpy(names, g_pass_names[slot], sizeof names);
    int n = 0;
    if (g_timing_ok && npass > 0) {
        if (npass > MAX_TIMED_PASSES) npass = MAX_TIMED_PASSES;
        NSData *d = [g_sb[slot] resolveCounterRange:NSMakeRange(0, (NSUInteger)npass * 2)];
        if (d && d.length >= (NSUInteger)npass * 2 * sizeof(MTLCounterResultTimestamp)) {
            const MTLCounterResultTimestamp *t = (const MTLCounterResultTimestamp *)d.bytes;
            for (int i = 0; i < npass; i++) {
                uint64_t a = t[2 * i].timestamp, b = t[2 * i + 1].timestamp;
                pm[n++] = (b > a && a != MTLCounterErrorValue && b != MTLCounterErrorValue) ? (double)(b - a) * g_ts_scale * 1e-6 : 0.0;
            }
        }
    }
    pthread_mutex_lock(&g_done_lock);
    g_gpu_ms = ms;
    g_pass_n = n;
    for (int i = 0; i < n; i++) { g_pass_ms[i] = pm[i]; memcpy(g_last_names[i], names[i], 32); }
    g_completed++;
    pthread_cond_broadcast(&g_done_cv);
    pthread_mutex_unlock(&g_done_lock);
    dispatch_semaphore_signal(g_sem);
}

/* Name the pass about to be counted. Call before g_frame_passes++. */
static void note_pass(const char *dflt)
{
    int i = g_frame_passes;
    if (i < MAX_TIMED_PASSES) snprintf(g_pass_names[g_slot][i], 32, "%s", g_next_name[0] ? g_next_name : dflt);
    g_next_name[0] = 0;
}

int32_t flow_gl_pass_name(const char *name)
{
    NEED_READY();
    snprintf(g_next_name, sizeof g_next_name, "%s", name ? name : "");
    if (g_cenc) { [g_cenc endEncoding]; g_cenc = nil; }
    return 0;
}

const char *flow_gl_pass_label(int32_t i)
{
    /* Rotating buffers, so several labels can be alive in one expression. */
    static __thread char bufs[8][32];
    static __thread int next;
    char *buf = bufs[next++ & 7];
    pthread_mutex_lock(&g_done_lock);
    if (i >= 0 && i < g_pass_n) snprintf(buf, 32, "%s", g_last_names[i]); else buf[0] = 0;
    pthread_mutex_unlock(&g_done_lock);
    return buf;
}

static int ensure_frame(void)
{
    if (g_frame_open) return 0;
    if (!g_ready) return fail("GPU host is not initialised (call gl_init)");
    dispatch_semaphore_wait(g_sem, DISPATCH_TIME_FOREVER);
    g_slot = (int)(g_frame_no % g_nslots);
    g_frame_no++;
    g_cmd = [g_queue commandBuffer];
    if (!g_cmd) { dispatch_semaphore_signal(g_sem); g_frame_no--; return fail("cannot create a command buffer"); }
    g_frame_open = true;
    g_ring_off = 0;
    g_frame_passes = 0;
    g_drawn = false;
    g_drawable = nil;
    g_pass_open = false;
    sync_layer_size();
    return 0;
}

int32_t flow_gl_begin_frame(void)
{
    @autoreleasepool { return ensure_frame(); }
}

static void end_encoders(void)
{
    if (g_cenc) { [g_cenc endEncoding]; g_cenc = nil; }
    if (g_renc) { [g_renc endEncoding]; g_renc = nil; }
    g_pass_open = false;
}

static id<MTLBuffer> buf_of(int32_t h, int *err)
{
    GLRes *r = tab_get(h, KIND_BUFFER);
    if (!r) { *err = 1; return nil; }
    return r->buf[copy_index(r)];
}

static id<MTLTexture> tex_of(int32_t h)
{
    GLRes *r = tab_get(h, KIND_TEXTURE);
    return r ? r->tex[copy_index(r)] : nil;
}

static void apply_bind_buffer_compute(int slot)
{
    BufBind *b = &g_bbuf[slot];
    if (b->ring) { [g_cenc setBuffer:g_ring[g_slot] offset:(NSUInteger)b->offset atIndex:(NSUInteger)slot]; return; }
    if (b->handle <= 0) return;
    int err = 0;
    id<MTLBuffer> mb = buf_of(b->handle, &err);
    if (mb) [g_cenc setBuffer:mb offset:(NSUInteger)b->offset atIndex:(NSUInteger)slot];
}

static void apply_bind_buffer_render(int slot)
{
    BufBind *b = &g_bbuf[slot];
    id<MTLBuffer> mb = nil;
    if (b->ring) mb = g_ring[g_slot];
    else if (b->handle > 0) { int err = 0; mb = buf_of(b->handle, &err); }
    if (!mb) return;
    [g_renc setVertexBuffer:mb offset:(NSUInteger)b->offset atIndex:(NSUInteger)slot];
    [g_renc setFragmentBuffer:mb offset:(NSUInteger)b->offset atIndex:(NSUInteger)slot];
}

static void apply_all_compute(void)
{
    for (int i = 0; i < MAX_BUF_SLOTS; i++) apply_bind_buffer_compute(i);
    for (int i = 0; i < MAX_TEX_SLOTS; i++) {
        if (g_btex[i] > 0) { id<MTLTexture> t = tex_of(g_btex[i]); if (t) [g_cenc setTexture:t atIndex:(NSUInteger)i]; }
        if (g_bsamp[i]) [g_cenc setSamplerState:g_samplers[g_bsamp[i] - 1] atIndex:(NSUInteger)i];
    }
}

static void apply_all_render(void)
{
    for (int i = 0; i < MAX_BUF_SLOTS; i++) apply_bind_buffer_render(i);
    for (int i = 0; i < MAX_TEX_SLOTS; i++) {
        if (g_btex[i] > 0) {
            id<MTLTexture> t = tex_of(g_btex[i]);
            if (t) { [g_renc setVertexTexture:t atIndex:(NSUInteger)i]; [g_renc setFragmentTexture:t atIndex:(NSUInteger)i]; }
        }
        if (g_bsamp[i]) {
            [g_renc setVertexSamplerState:g_samplers[g_bsamp[i] - 1] atIndex:(NSUInteger)i];
            [g_renc setFragmentSamplerState:g_samplers[g_bsamp[i] - 1] atIndex:(NSUInteger)i];
        }
    }
}

int32_t flow_gl_bind_buffer(int32_t slot, int32_t buf, int64_t offset)
{
    @autoreleasepool {
        NEED_READY();
        if (slot < 0 || slot >= MAX_BUF_SLOTS) return fail("bind_buffer: slot %d outside 0..%d", slot, MAX_BUF_SLOTS - 1);
        GLRes *r = buf ? tab_get(buf, KIND_BUFFER) : nil;
        if (buf != 0 && !r) return fail("bind_buffer: invalid buffer handle %d", buf);
        if (r && (offset < 0 || offset >= r->bytes)) return fail("bind_buffer: offset outside the buffer");
        g_bbuf[slot].handle = buf; g_bbuf[slot].offset = offset; g_bbuf[slot].ring = 0;
        if (g_cenc) apply_bind_buffer_compute(slot);
        if (g_renc) apply_bind_buffer_render(slot);
        return 0;
    }
}

int32_t flow_gl_bind_texture(int32_t slot, int32_t tex)
{
    @autoreleasepool {
        NEED_READY();
        if (slot < 0 || slot >= MAX_TEX_SLOTS) return fail("bind_texture: slot %d outside 0..%d", slot, MAX_TEX_SLOTS - 1);
        if (tex != 0 && !tab_get(tex, KIND_TEXTURE)) return fail("bind_texture: invalid texture handle %d", tex);
        g_btex[slot] = tex;
        id<MTLTexture> t = tex ? tex_of(tex) : nil;
        if (g_cenc && t) [g_cenc setTexture:t atIndex:(NSUInteger)slot];
        if (g_renc && t) { [g_renc setVertexTexture:t atIndex:(NSUInteger)slot]; [g_renc setFragmentTexture:t atIndex:(NSUInteger)slot]; }
        return 0;
    }
}

int32_t flow_gl_bind_sampler(int32_t slot, int32_t linear, int32_t repeat)
{
    NEED_READY();
    if (slot < 0 || slot >= MAX_TEX_SLOTS) return fail("bind_sampler: slot %d outside 0..%d", slot, MAX_TEX_SLOTS - 1);
    int idx = (linear ? 2 : 0) + (repeat ? 1 : 0);
    g_bsamp[slot] = (int8_t)(idx + 1);
    if (g_cenc) [g_cenc setSamplerState:g_samplers[idx] atIndex:(NSUInteger)slot];
    if (g_renc) {
        [g_renc setVertexSamplerState:g_samplers[idx] atIndex:(NSUInteger)slot];
        [g_renc setFragmentSamplerState:g_samplers[idx] atIndex:(NSUInteger)slot];
    }
    return 0;
}

int32_t flow_gl_bind_bytes(int32_t slot, const uint8_t *src, int32_t n)
{
    @autoreleasepool {
        NEED_READY();
        if (slot < 0 || slot >= MAX_BUF_SLOTS) return fail("bind_bytes: slot %d outside 0..%d", slot, MAX_BUF_SLOTS - 1);
        if (!src || n < 1) return fail("bind_bytes: empty data");
        if (ensure_frame() != 0) return -1;
        int64_t off = (g_ring_off + 255) & ~(int64_t)255;
        if (off + n > RING_BYTES) return fail("bind_bytes: the %d MB uniform ring is full for this frame", RING_BYTES >> 20);
        memcpy((uint8_t *)g_ring[g_slot].contents + off, src, (size_t)n);
        g_ring_off = off + n;
        g_bbuf[slot].handle = 0; g_bbuf[slot].offset = off; g_bbuf[slot].ring = 1; g_bbuf[slot].ring_n = n;
        if (g_cenc) apply_bind_buffer_compute(slot);
        if (g_renc) apply_bind_buffer_render(slot);
        return 0;
    }
}

/* A compute encoder, opened on demand, ended when a render pass begins or the frame ends. */
static int open_compute(void)
{
    if (g_cenc) return 0;
    if (ensure_frame() != 0) return -1;
    if (g_renc) { [g_renc endEncoding]; g_renc = nil; g_pass_open = false; }
    if (g_timing_ok && g_frame_passes < MAX_TIMED_PASSES) {
        note_pass("compute");
        MTLComputePassDescriptor *cpd = [MTLComputePassDescriptor computePassDescriptor];
        cpd.sampleBufferAttachments[0].sampleBuffer = g_sb[g_slot];
        cpd.sampleBufferAttachments[0].startOfEncoderSampleIndex = (NSUInteger)g_frame_passes * 2;
        cpd.sampleBufferAttachments[0].endOfEncoderSampleIndex = (NSUInteger)g_frame_passes * 2 + 1;
        g_cenc = [g_cmd computeCommandEncoderWithDescriptor:cpd];
        g_frame_passes++;
    } else {
        g_cenc = [g_cmd computeCommandEncoder];
    }
    if (!g_cenc) return fail("cannot create a compute encoder");
    apply_all_compute();
    return 0;
}

int32_t flow_gl_dispatch_groups(int32_t p, int32_t gx, int32_t gy, int32_t gz, int32_t tx, int32_t ty, int32_t tz)
{
    @autoreleasepool {
        NEED_READY();
        GLRes *r = tab_get(p, KIND_COMPUTE);
        if (!r) return fail("dispatch: invalid compute pipeline handle %d", p);
        if (gx < 1 || gy < 1 || gz < 1 || tx < 1 || ty < 1 || tz < 1) return fail("dispatch: sizes must be at least 1");
        if ((NSUInteger)tx * (NSUInteger)ty * (NSUInteger)tz > r->max_threads) return fail("dispatch: threadgroup of %d threads exceeds this pipeline's limit of %lu", tx * ty * tz, (unsigned long)r->max_threads);
        if (open_compute() != 0) return -1;
        [g_cenc setComputePipelineState:r->cps];
        [g_cenc dispatchThreadgroups:MTLSizeMake((NSUInteger)gx, (NSUInteger)gy, (NSUInteger)gz)
              threadsPerThreadgroup:MTLSizeMake((NSUInteger)tx, (NSUInteger)ty, (NSUInteger)tz)];
        return 0;
    }
}

int32_t flow_gl_dispatch(int32_t p, int32_t x, int32_t y, int32_t z)
{
    @autoreleasepool {
        NEED_READY();
        GLRes *r = tab_get(p, KIND_COMPUTE);
        if (!r) return fail("dispatch: invalid compute pipeline handle %d", p);
        if (x < 1 || y < 1 || z < 1) return fail("dispatch: sizes must be at least 1");
        NSUInteger mx = r->max_threads, tx, ty = 1, tz = 1;
        if (y == 1 && z == 1) { tx = mx < 256 ? mx : 256; }
        else if (z == 1) { tx = mx >= 256 ? 16 : 8; ty = tx; }
        else { tx = 8; ty = 8; tz = 4; while (tx * ty * tz > mx && tz > 1) tz >>= 1; }
        if (open_compute() != 0) return -1;
        [g_cenc setComputePipelineState:r->cps];
        [g_cenc dispatchThreads:MTLSizeMake((NSUInteger)x, (NSUInteger)y, (NSUInteger)z) threadsPerThreadgroup:MTLSizeMake(tx, ty, tz)];
        return 0;
    }
}

int32_t flow_gl_dispatch_indirect(int32_t p, int32_t args, int64_t offset, int32_t tx, int32_t ty, int32_t tz)
{
    @autoreleasepool {
        NEED_READY();
        GLRes *r = tab_get(p, KIND_COMPUTE);
        if (!r) return fail("dispatch_indirect: invalid compute pipeline handle %d", p);
        GLRes *ab = tab_get(args, KIND_BUFFER);
        if (!ab || offset < 0 || offset + 12 > ab->bytes || (offset & 3)) return fail("dispatch_indirect: bad argument buffer or offset");
        if (tx < 1 || ty < 1 || tz < 1 || (NSUInteger)tx * (NSUInteger)ty * (NSUInteger)tz > r->max_threads) return fail("dispatch_indirect: bad threadgroup size");
        if (open_compute() != 0) return -1;
        [g_cenc setComputePipelineState:r->cps];
        [g_cenc dispatchThreadgroupsWithIndirectBuffer:ab->buf[copy_index(ab)] indirectBufferOffset:(NSUInteger)offset
                                 threadsPerThreadgroup:MTLSizeMake((NSUInteger)tx, (NSUInteger)ty, (NSUInteger)tz)];
        return 0;
    }
}

static int acquire_drawable(void)
{
    if (g_drawable) return 0;
    if (!g_layer) return fail("no window is attached (gl_attach_window)");
    sync_layer_size();
    g_drawable = [g_layer nextDrawable];
    if (!g_drawable) return fail("no drawable available (window hidden or occluded?)");
    g_drawables++;
    return 0;
}

static int begin_render_pass(id<MTLTexture> color, id<MTLTexture> depth, int cfmt, int dfmt, int load, float r, float g, float b, float a, float cd, bool is_window)
{
    if (ensure_frame() != 0) return -1;
    end_encoders();
    MTLRenderPassDescriptor *rp = [MTLRenderPassDescriptor renderPassDescriptor];
    rp.colorAttachments[0].texture = color;
    rp.colorAttachments[0].storeAction = MTLStoreActionStore;
    if (load == FLOW_GL_LOAD_KEEP && (!is_window || g_drawn)) {
        rp.colorAttachments[0].loadAction = MTLLoadActionLoad;
    } else {
        rp.colorAttachments[0].loadAction = MTLLoadActionClear;
        rp.colorAttachments[0].clearColor = MTLClearColorMake(r, g, b, a);
    }
    if (depth) {
        rp.depthAttachment.texture = depth;
        rp.depthAttachment.loadAction = MTLLoadActionClear;
        rp.depthAttachment.clearDepth = cd;
        rp.depthAttachment.storeAction = MTLStoreActionStore;
    }
    if (g_timing_ok && g_frame_passes < MAX_TIMED_PASSES) {
        note_pass(is_window ? "window" : "render");
        rp.sampleBufferAttachments[0].sampleBuffer = g_sb[g_slot];
        rp.sampleBufferAttachments[0].startOfVertexSampleIndex = (NSUInteger)g_frame_passes * 2;
        rp.sampleBufferAttachments[0].endOfVertexSampleIndex = MTLCounterDontSample;
        rp.sampleBufferAttachments[0].startOfFragmentSampleIndex = MTLCounterDontSample;
        rp.sampleBufferAttachments[0].endOfFragmentSampleIndex = (NSUInteger)g_frame_passes * 2 + 1;
        g_frame_passes++;
    }
    g_renc = [g_cmd renderCommandEncoderWithDescriptor:rp];
    if (!g_renc) return fail("cannot create a render encoder");
    g_pass_open = true;
    g_pass_cfmt = cfmt; g_pass_dfmt = dfmt;
    g_pass_w = (int)color.width; g_pass_h = (int)color.height;
    if (is_window) g_drawn = true;
    return 0;
}

int32_t flow_gl_pass_begin(int32_t color, int32_t depth, int32_t load, float r, float g, float b, float a, float clear_depth)
{
    @autoreleasepool {
        NEED_READY();
        id<MTLTexture> ct = nil, dt = nil;
        int cfmt = FLOW_GL_BGRA8, dfmt = 0;
        bool win = color == 0;
        if (ensure_frame() != 0) return -1;
        if (win) {
            if (acquire_drawable() != 0) return -1;
            ct = g_drawable.texture;
        } else {
            GLRes *cr = tab_get(color, KIND_TEXTURE);
            if (!cr) return fail("pass_begin: invalid colour texture handle %d", color);
            if (!(cr->usage & FLOW_GL_TEX_TARGET)) return fail("pass_begin: colour texture lacks GL_TEX_TARGET");
            if (cr->format == FLOW_GL_DEPTH32F) return fail("pass_begin: colour texture has a depth format");
            if (ensure_frame() != 0) return -1;
            ct = cr->tex[copy_index(cr)];
            cfmt = cr->format;
        }
        if (depth != 0) {
            GLRes *dr = tab_get(depth, KIND_TEXTURE);
            if (!dr || dr->format != FLOW_GL_DEPTH32F || !(dr->usage & FLOW_GL_TEX_TARGET)) return fail("pass_begin: depth must be a GL_DEPTH32F texture with GL_TEX_TARGET");
            if ((int)dr->w != (int)ct.width || (int)dr->h != (int)ct.height) return fail("pass_begin: depth and colour sizes differ");
            if (ensure_frame() != 0) return -1;
            dt = dr->tex[copy_index(dr)];
            dfmt = FLOW_GL_DEPTH32F;
        }
        if (begin_render_pass(ct, dt, cfmt, dfmt, load, r, g, b, a, clear_depth, win) != 0) return -1;
        apply_all_render();
        return 0;
    }
}

int32_t flow_gl_pass_begin_noattach(int32_t w, int32_t h)
{
    @autoreleasepool {
        NEED_READY();
        if (w < 1 || h < 1 || w > 16384 || h > 16384) return fail("pass_begin_noattach: bad size %dx%d", w, h);
        if (ensure_frame() != 0) return -1;
        end_encoders();
        MTLRenderPassDescriptor *rp = [MTLRenderPassDescriptor renderPassDescriptor];
        rp.renderTargetWidth = (NSUInteger)w;
        rp.renderTargetHeight = (NSUInteger)h;
        rp.defaultRasterSampleCount = 1;
        if (g_timing_ok && g_frame_passes < MAX_TIMED_PASSES) {
            note_pass("raster");
            rp.sampleBufferAttachments[0].sampleBuffer = g_sb[g_slot];
            rp.sampleBufferAttachments[0].startOfVertexSampleIndex = (NSUInteger)g_frame_passes * 2;
            rp.sampleBufferAttachments[0].endOfVertexSampleIndex = MTLCounterDontSample;
            rp.sampleBufferAttachments[0].startOfFragmentSampleIndex = MTLCounterDontSample;
            rp.sampleBufferAttachments[0].endOfFragmentSampleIndex = (NSUInteger)g_frame_passes * 2 + 1;
            g_frame_passes++;
        }
        g_renc = [g_cmd renderCommandEncoderWithDescriptor:rp];
        if (!g_renc) return fail("cannot create a render encoder");
        g_pass_open = true;
        g_pass_cfmt = 0; g_pass_dfmt = 0; g_pass_w = w; g_pass_h = h;
        apply_all_render();
        return 0;
    }
}

static MTLPrimitiveType prim(int t)
{
    switch (t) {
    case FLOW_GL_LINES: return MTLPrimitiveTypeLine;
    case FLOW_GL_POINTS: return MTLPrimitiveTypePoint;
    case FLOW_GL_TRIANGLE_STRIP: return MTLPrimitiveTypeTriangleStrip;
    }
    return MTLPrimitiveTypeTriangle;
}

static GLRes *draw_setup(int32_t p, int32_t topology)
{
    if (!g_ready) { fail("GPU host is not initialised"); return nil; }
    GLRes *r = tab_get(p, KIND_RENDER);
    if (!r || !r->built) { fail("draw: invalid or unbuilt render pipeline handle %d", p); return nil; }
    if (!g_pass_open || !g_renc) { fail("draw: no render pass is open (gl_pass_begin)"); return nil; }
    if (topology < 0 || topology > 3) { fail("draw: bad topology %d", topology); return nil; }
    if (r->cfmt != g_pass_cfmt) { fail("draw: pipeline colour format %d does not match the pass (%d)", r->cfmt, g_pass_cfmt); return nil; }
    if (r->dfmt != g_pass_dfmt) { fail("draw: pipeline and pass disagree about a depth attachment"); return nil; }
    [g_renc setRenderPipelineState:r->rps];
    [g_renc setCullMode:r->cull == FLOW_GL_CULL_BACK ? MTLCullModeBack : (r->cull == FLOW_GL_CULL_FRONT ? MTLCullModeFront : MTLCullModeNone)];
    [g_renc setFrontFacingWinding:MTLWindingCounterClockwise];
    if (r->dss) [g_renc setDepthStencilState:r->dss];
    return r;
}

int32_t flow_gl_draw(int32_t p, int32_t topology, int32_t first, int32_t count, int32_t instances)
{
    @autoreleasepool {
        GLRes *r = draw_setup(p, topology);
        if (!r) return -1;
        if (first < 0 || count < 0 || instances < 0) return fail("draw: negative count");
        if (count == 0 || instances == 0) return 0;
        [g_renc drawPrimitives:prim(topology) vertexStart:(NSUInteger)first vertexCount:(NSUInteger)count instanceCount:(NSUInteger)instances];
        return 0;
    }
}

int32_t flow_gl_draw_indexed(int32_t p, int32_t topology, int32_t ib, int32_t u32, int32_t first_index, int32_t count, int32_t instances)
{
    @autoreleasepool {
        GLRes *r = draw_setup(p, topology);
        if (!r) return -1;
        GLRes *b = tab_get(ib, KIND_BUFFER);
        if (!b) return fail("draw_indexed: invalid index buffer handle %d", ib);
        if (first_index < 0 || count < 0 || instances < 0) return fail("draw_indexed: negative count");
        int64_t isz = u32 ? 4 : 2;
        if ((int64_t)(first_index + (int64_t)count) * isz > b->bytes) return fail("draw_indexed: indices run past the end of the buffer");
        if (count == 0 || instances == 0) return 0;
        [g_renc drawIndexedPrimitives:prim(topology) indexCount:(NSUInteger)count indexType:u32 ? MTLIndexTypeUInt32 : MTLIndexTypeUInt16
                          indexBuffer:b->buf[copy_index(b)] indexBufferOffset:(NSUInteger)(first_index * isz) instanceCount:(NSUInteger)instances];
        return 0;
    }
}

int32_t flow_gl_draw_indirect(int32_t p, int32_t topology, int32_t args, int64_t offset)
{
    @autoreleasepool {
        GLRes *r = draw_setup(p, topology);
        if (!r) return -1;
        GLRes *b = tab_get(args, KIND_BUFFER);
        if (!b || offset < 0 || offset + 16 > b->bytes || (offset & 3)) return fail("draw_indirect: bad argument buffer or offset");
        [g_renc drawPrimitives:prim(topology) indirectBuffer:b->buf[copy_index(b)] indirectBufferOffset:(NSUInteger)offset];
        return 0;
    }
}

int32_t flow_gl_pass_end(void)
{
    @autoreleasepool {
        if (!g_renc) return fail("pass_end: no render pass is open");
        [g_renc endEncoding];
        g_renc = nil;
        g_pass_open = false;
        return 0;
    }
}

static int blit_pipeline(int dst_fmt, int blend, id<MTLRenderPipelineState> *out)
{
    int fi = fmt_index(dst_fmt);
    if (g_blit_ps[fi][blend]) { *out = g_blit_ps[fi][blend]; return 0; }
    id<MTLLibrary> lib = library_for(blit_msl);
    if (!lib) return -1;
    MTLRenderPipelineDescriptor *d = [MTLRenderPipelineDescriptor new];
    d.vertexFunction = [lib newFunctionWithName:@"blit_vs"];
    d.fragmentFunction = [lib newFunctionWithName:@"blit_fs"];
    int bpp;
    MTLRenderPipelineColorAttachmentDescriptor *ca = d.colorAttachments[0];
    ca.pixelFormat = mtl_fmt(dst_fmt, &bpp);
    if (blend != FLOW_GL_BLEND_NONE) {
        ca.blendingEnabled = YES;
        ca.sourceRGBBlendFactor = blend == FLOW_GL_BLEND_ALPHA ? MTLBlendFactorSourceAlpha : MTLBlendFactorOne;
        ca.destinationRGBBlendFactor = blend == FLOW_GL_BLEND_ADD ? MTLBlendFactorOne : MTLBlendFactorOneMinusSourceAlpha;
        ca.sourceAlphaBlendFactor = MTLBlendFactorOne;
        ca.destinationAlphaBlendFactor = blend == FLOW_GL_BLEND_ADD ? MTLBlendFactorOne : MTLBlendFactorOneMinusSourceAlpha;
    }
    NSError *e = nil;
    id<MTLRenderPipelineState> ps = [g_dev newRenderPipelineStateWithDescriptor:d error:&e];
    if (!ps) return fail("blit pipeline: %.300s", e ? e.localizedDescription.UTF8String : "failed");
    g_allocs++;
    g_blit_ps[fi][blend] = ps;
    *out = ps;
    return 0;
}

int32_t flow_gl_blit(int32_t src, int32_t dst, int32_t blend)
{
    @autoreleasepool {
        NEED_READY();
        GLRes *sr = tab_get(src, KIND_TEXTURE);
        if (!sr || !(sr->usage & (FLOW_GL_TEX_SAMPLED | FLOW_GL_TEX_STORAGE)) || sr->format == FLOW_GL_DEPTH32F) return fail("blit: source must be a colour texture with GL_TEX_SAMPLED");
        if (blend < 0 || blend > 3) return fail("blit: bad blend mode");
        id<MTLTexture> dt = nil;
        int dfmt = FLOW_GL_BGRA8;
        bool win = dst == 0;
        if (ensure_frame() != 0) return -1;
        if (win) {
            if (acquire_drawable() != 0) return -1;
            dt = g_drawable.texture;
        } else {
            GLRes *dr = tab_get(dst, KIND_TEXTURE);
            if (!dr || !(dr->usage & FLOW_GL_TEX_TARGET) || dr->format == FLOW_GL_DEPTH32F) return fail("blit: destination must be a colour texture with GL_TEX_TARGET");
            if (dr == sr) return fail("blit: source and destination are the same texture");
            dt = dr->tex[copy_index(dr)];
            dfmt = dr->format;
        }
        id<MTLRenderPipelineState> ps = nil;
        if (blit_pipeline(dfmt, blend, &ps) != 0) return -1;
        bool keep = blend != FLOW_GL_BLEND_NONE;
        if (begin_render_pass(dt, nil, dfmt, 0, keep ? FLOW_GL_LOAD_KEEP : FLOW_GL_LOAD_CLEAR, 0, 0, 0, 1, 1.0f, win) != 0) return -1;
        bool same = (int)dt.width == sr->w && (int)dt.height == sr->h;
        [g_renc setRenderPipelineState:ps];
        [g_renc setFragmentTexture:sr->tex[copy_index(sr)] atIndex:0];
        [g_renc setFragmentSamplerState:g_samplers[same ? 0 : 2] atIndex:0];
        [g_renc drawPrimitives:MTLPrimitiveTypeTriangle vertexStart:0 vertexCount:3];
        [g_renc endEncoding];
        g_renc = nil;
        g_pass_open = false;
        return 0;
    }
}

/* CPU overlay: the gfx framebuffer, drawn with alpha 0 as background, is
 * uploaded to a stream texture and composited with premultiplied blending. */
typedef uint8_t *(*pixels_fn)(void *, int32_t *);
static int32_t g_ov_dst = 0;
static int g_ov_w, g_ov_h;
static uint8_t *g_ov_px;
#define OV_HIST (MAX_FRAMES + 1)
static int g_ov_rect[OV_HIST][4]; /* x0, y0, x1, y1 of the last presents */
static int g_ov_n;                   /* rects recorded */
static bool g_ov_dirty_all;

static uint8_t *ov_pixels(void *ctx)
{
    pixels_fn f = (pixels_fn)dlsym(RTLD_DEFAULT, "flow_gfx_pixels");
    if (!f) { set_err("overlay: this program has no gfx window backend"); return NULL; }
    int32_t wh[2] = {0, 0};
    uint8_t *px = f(ctx, wh);
    if (!px || wh[0] < 1 || wh[1] < 1) { set_err("overlay: the window has no CPU framebuffer"); return NULL; }
    if (px != g_ov_px || wh[0] != g_ov_w || wh[1] != g_ov_h) {
        g_ov_px = px; g_ov_w = wh[0]; g_ov_h = wh[1];
        g_ov_dirty_all = true;
        g_ov_n = 0;
        if (g_ov_tex > 0) { flow_gl_texture_free(g_ov_tex); g_ov_tex = 0; }
    }
    return px;
}

int32_t flow_gl_overlay_target(int32_t dst)
{
    NEED_READY();
    if (dst != 0 && !tab_get(dst, KIND_TEXTURE)) return fail("overlay_target: invalid texture handle %d", dst);
    g_ov_dst = dst;
    return 0;
}

int32_t flow_gl_overlay_begin(void *gfx_ctx)
{
    NEED_READY();
    uint8_t *px = ov_pixels(gfx_ctx);
    if (!px) return -1;
    if (g_ov_dirty_all) {
        memset(px, 0, (size_t)g_ov_w * (size_t)g_ov_h * 4u);
    } else if (g_ov_n > 0) {
        int *r = g_ov_rect[(g_ov_n - 1) % OV_HIST];
        for (int y = r[1]; y < r[3]; y++) memset(px + ((size_t)y * (size_t)g_ov_w + (size_t)r[0]) * 4u, 0, (size_t)(r[2] - r[0]) * 4u);
    }
    return 0;
}

int32_t flow_gl_overlay_present(int32_t x, int32_t y, int32_t w, int32_t h)
{
    @autoreleasepool {
        NEED_READY();
        if (!g_ov_px) return fail("overlay_present: call gl_overlay_begin first");
        if (x < 0) { w += x; x = 0; }
        if (y < 0) { h += y; y = 0; }
        if (x + w > g_ov_w) w = g_ov_w - x;
        if (y + h > g_ov_h) h = g_ov_h - y;
        if (w < 0) w = 0;
        if (h < 0) h = 0;
        if (ensure_frame() != 0) return -1;
        if (g_ov_tex <= 0) {
            g_ov_tex = flow_gl_texture_new(g_ov_w, g_ov_h, FLOW_GL_RGBA8, FLOW_GL_TEX_SAMPLED | FLOW_GL_TEX_STREAM);
            if (g_ov_tex < 0) { g_ov_tex = 0; return -1; }
            g_ov_dirty_all = true;
        }
        int slot = g_ov_n % OV_HIST;
        g_ov_rect[slot][0] = x; g_ov_rect[slot][1] = y; g_ov_rect[slot][2] = x + w; g_ov_rect[slot][3] = y + h;
        g_ov_n++;
        /* Each texture copy is stale by up to nslots frames: upload the union of the last nslots rectangles. */
        int ux0 = x, uy0 = y, ux1 = x + w, uy1 = y + h;
        if (g_ov_dirty_all) { ux0 = 0; uy0 = 0; ux1 = g_ov_w; uy1 = g_ov_h; }
        else {
            for (int k = 1; k <= g_nslots && k < g_ov_n; k++) {
                int *r = g_ov_rect[(g_ov_n - 1 - k) % OV_HIST];
                if (r[2] <= r[0] || r[3] <= r[1]) continue;
                if (ux1 <= ux0 || uy1 <= uy0) { ux0 = r[0]; uy0 = r[1]; ux1 = r[2]; uy1 = r[3]; continue; }
                if (r[0] < ux0) ux0 = r[0];
                if (r[1] < uy0) uy0 = r[1];
                if (r[2] > ux1) ux1 = r[2];
                if (r[3] > uy1) uy1 = r[3];
            }
        }
        g_ov_dirty_all = false;
        if (ux1 > ux0 && uy1 > uy0) {
            const uint8_t *src = g_ov_px + ((size_t)uy0 * (size_t)g_ov_w + (size_t)ux0) * 4u;
            if (flow_gl_texture_upload_rect(g_ov_tex, ux0, uy0, ux1 - ux0, uy1 - uy0, src, g_ov_w * 4) != 0) return -1;
        }
        g_next_name[0] = 0;
        snprintf(g_next_name, sizeof g_next_name, "overlay");
        return flow_gl_blit(g_ov_tex, g_ov_dst, FLOW_GL_BLEND_PREMUL);
    }
}

static int commit_frame(bool present)
{
    if (!g_frame_open) { if (ensure_frame() != 0) return -1; }
    end_encoders();
    if (present && g_drawable) [g_cmd presentDrawable:g_drawable];
    int slot = g_slot, np = g_frame_passes;
    [g_cmd addCompletedHandler:^(id<MTLCommandBuffer> cb) { on_complete(cb, slot, np); }];
    [g_cmd commit];
    g_submitted++;
    g_cmd = nil; g_drawable = nil;
    g_frame_open = false;
    return 0;
}

int32_t flow_gl_present(void)
{
    @autoreleasepool { NEED_READY(); return commit_frame(true); }
}

int32_t flow_gl_submit(void)
{
    @autoreleasepool { NEED_READY(); return commit_frame(false); }
}

double flow_gl_gpu_time_ms(void)
{
    pthread_mutex_lock(&g_done_lock);
    double v = g_gpu_ms;
    pthread_mutex_unlock(&g_done_lock);
    return v;
}

int32_t flow_gl_pass_count(void)
{
    pthread_mutex_lock(&g_done_lock);
    int v = g_pass_n;
    pthread_mutex_unlock(&g_done_lock);
    return v;
}

double flow_gl_pass_time_ms(int32_t i)
{
    pthread_mutex_lock(&g_done_lock);
    double v = (i >= 0 && i < g_pass_n) ? g_pass_ms[i] : -1.0;
    pthread_mutex_unlock(&g_done_lock);
    return v;
}

#endif /* __APPLE__ */
