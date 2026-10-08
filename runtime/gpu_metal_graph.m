/* FLOW GPU graph executor, Metal backend (#812).
 *
 * Runs the passes of a validated stdlib/gpu_graph.flow graph over
 * persistent device resources. See gpu_graph_exec.h for the contract.
 *
 * Builds with or without ARC: Objective-C objects are held as retained
 * CoreFoundation references, and objects returned at +1 by new* methods
 * are balanced with FG_AUTORELEASE before being kept.
 */
#ifdef __APPLE__

#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#include "gpu_graph_exec.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if __has_feature(objc_arc)
#define FG_AUTORELEASE(x) (x)
#else
#define FG_AUTORELEASE(x) [(x) autorelease]
#endif

#define FG_MAX_RES 16
#define FG_MAX_PASS 16
#define FG_MAX_BIND 8
#define FG_MAX_ITER 1024
#define FG_MAX_DIM 16384

typedef struct FgRes {
    int32_t used;
    int32_t kind;
    int32_t format;
    int32_t width;
    int32_t height;
    int32_t texel_bytes;
    int64_t bytes;
    void *obj; /* id<MTLBuffer> or id<MTLTexture> */
} FgRes;

typedef struct FgPass {
    int32_t kind;
    int32_t wg[3];
    int32_t grid[3];
    int32_t iterations;
    int32_t barrier_before;
    int32_t nbind;
    int32_t slot[FG_MAX_BIND];
    int32_t even[FG_MAX_BIND];
    int32_t odd[FG_MAX_BIND];
    void *pso; /* compute or render pipeline state */
} FgPass;

typedef struct FgExec {
    void *device;
    void *queue;
    FgRes res[FG_MAX_RES];
    FgPass pass[FG_MAX_PASS];
    int32_t npass;
    void *output;   /* rgba8unorm render target */
    void *readback; /* shared buffer holding the last frame */
    int32_t out_w;
    int32_t out_h;
    int32_t have_frame;
    int32_t stat_dispatches;
    int32_t stat_barriers;
    int32_t stat_render;
    int32_t stat_frames;
    double gpu_ms;
    char err[512];
} FgExec;

static void *fg_keep(id obj) {
    return obj ? (void *)CFBridgingRetain(obj) : NULL;
}

static void fg_drop(void *ref) {
    if (ref) {
        CFRelease((CFTypeRef)ref);
    }
}

static int32_t fg_fail(FgExec *ex, const char *msg) {
    if (ex) {
        snprintf(ex->err, sizeof(ex->err), "%s", msg);
    }
    return -1;
}

static int32_t fg_failf(FgExec *ex, const char *msg, const char *detail) {
    if (ex) {
        snprintf(ex->err, sizeof(ex->err), "%s: %s", msg, detail ? detail : "");
    }
    return -1;
}

static id<MTLDevice> fg_device(FgExec *ex) {
    return (__bridge id<MTLDevice>)ex->device;
}

static id<MTLCommandQueue> fg_queue(FgExec *ex) {
    return (__bridge id<MTLCommandQueue>)ex->queue;
}

static int fg_texel_bytes(int32_t format, MTLPixelFormat *pf) {
    switch (format) {
    case 1: *pf = MTLPixelFormatR32Float; return 4;
    case 2: *pf = MTLPixelFormatRG32Float; return 8;
    case 3: *pf = MTLPixelFormatRGBA16Float; return 8;
    case 4: *pf = MTLPixelFormatRGBA8Unorm; return 4;
    default: return 0;
    }
}

static int fg_physical_ok(FgExec *ex, int32_t physical) {
    return ex && physical >= 0 && physical < FG_MAX_RES && ex->res[physical].used;
}

/* Wait for a one-off command buffer and report its error, if any. */
static int32_t fg_finish(FgExec *ex, id<MTLCommandBuffer> cmd, const char *what) {
    [cmd commit];
    [cmd waitUntilCompleted];
    if ([cmd status] != MTLCommandBufferStatusCompleted) {
        NSError *e = [cmd error];
        return fg_failf(ex, what, e ? [[e localizedDescription] UTF8String] : "command buffer failed");
    }
    return 0;
}

void *flow_gpu_graph_exec_new(void) {
    @autoreleasepool {
        id<MTLDevice> dev = FG_AUTORELEASE(MTLCreateSystemDefaultDevice());
        if (dev == nil) {
            return NULL;
        }
        id<MTLCommandQueue> q = FG_AUTORELEASE([dev newCommandQueue]);
        if (q == nil) {
            return NULL;
        }
        FgExec *ex = (FgExec *)calloc(1, sizeof(FgExec));
        if (!ex) {
            return NULL;
        }
        ex->device = fg_keep(dev);
        ex->queue = fg_keep(q);
        snprintf(ex->err, sizeof(ex->err), "ok");
        return ex;
    }
}

void flow_gpu_graph_exec_free(void *handle) {
    FgExec *ex = (FgExec *)handle;
    if (!ex) {
        return;
    }
    for (int i = 0; i < FG_MAX_RES; i++) {
        fg_drop(ex->res[i].obj);
    }
    for (int i = 0; i < ex->npass; i++) {
        fg_drop(ex->pass[i].pso);
    }
    fg_drop(ex->output);
    fg_drop(ex->readback);
    fg_drop(ex->queue);
    fg_drop(ex->device);
    free(ex);
}

const char *flow_gpu_graph_exec_error(void *handle) {
    FgExec *ex = (FgExec *)handle;
    if (!ex) {
        return "no Metal device";
    }
    return ex->err;
}

static int32_t fg_zero_fill(FgExec *ex, FgRes *r) {
    @autoreleasepool {
        id<MTLCommandBuffer> cmd = [fg_queue(ex) commandBuffer];
        id<MTLBlitCommandEncoder> blit = [cmd blitCommandEncoder];
        if (r->kind == FLOW_GPU_GRAPH_KIND_BUFFER) {
            id<MTLBuffer> buf = (__bridge id<MTLBuffer>)r->obj;
            [blit fillBuffer:buf range:NSMakeRange(0, (NSUInteger)r->bytes) value:0];
        } else {
            id<MTLBuffer> zero = FG_AUTORELEASE([fg_device(ex) newBufferWithLength:(NSUInteger)r->bytes
                                                                          options:MTLResourceStorageModePrivate]);
            if (zero == nil) {
                [blit endEncoding];
                return fg_fail(ex, "zero staging allocation failed");
            }
            [blit fillBuffer:zero range:NSMakeRange(0, (NSUInteger)r->bytes) value:0];
            [blit copyFromBuffer:zero
                    sourceOffset:0
               sourceBytesPerRow:(NSUInteger)(r->width * r->texel_bytes)
             sourceBytesPerImage:(NSUInteger)r->bytes
                      sourceSize:MTLSizeMake((NSUInteger)r->width, (NSUInteger)r->height, 1)
                       toTexture:(__bridge id<MTLTexture>)r->obj
                destinationSlice:0
                destinationLevel:0
               destinationOrigin:MTLOriginMake(0, 0, 0)];
        }
        [blit endEncoding];
        return fg_finish(ex, cmd, "zero fill failed");
    }
}

int32_t flow_gpu_graph_exec_add_buffer(void *handle, int32_t physical, int64_t bytes) {
    FgExec *ex = (FgExec *)handle;
    if (!ex) {
        return -1;
    }
    if (physical < 0 || physical >= FG_MAX_RES || ex->res[physical].used) {
        return fg_fail(ex, "buffer id out of range or already allocated");
    }
    if (bytes < 4 || bytes % 4 != 0 || bytes > (int64_t)[fg_device(ex) maxBufferLength]) {
        return fg_fail(ex, "storage buffer size must be a positive multiple of 4 within the device limit");
    }
    @autoreleasepool {
        id<MTLBuffer> buf = FG_AUTORELEASE([fg_device(ex) newBufferWithLength:(NSUInteger)bytes
                                                                     options:MTLResourceStorageModePrivate]);
        if (buf == nil) {
            return fg_fail(ex, "storage buffer allocation failed");
        }
        FgRes *r = &ex->res[physical];
        r->used = 1;
        r->kind = FLOW_GPU_GRAPH_KIND_BUFFER;
        r->bytes = bytes;
        r->obj = fg_keep(buf);
        return fg_zero_fill(ex, r);
    }
}

int32_t flow_gpu_graph_exec_add_texture(void *handle, int32_t physical, int32_t format,
                                        int32_t width, int32_t height) {
    FgExec *ex = (FgExec *)handle;
    if (!ex) {
        return -1;
    }
    if (physical < 0 || physical >= FG_MAX_RES || ex->res[physical].used) {
        return fg_fail(ex, "texture id out of range or already allocated");
    }
    MTLPixelFormat pf = MTLPixelFormatInvalid;
    int tb = fg_texel_bytes(format, &pf);
    if (tb == 0) {
        return fg_fail(ex, "unknown storage texture format");
    }
    if (width < 1 || height < 1 || width > FG_MAX_DIM || height > FG_MAX_DIM) {
        return fg_fail(ex, "texture size outside 1..16384");
    }
    @autoreleasepool {
        MTLTextureDescriptor *d =
            [MTLTextureDescriptor texture2DDescriptorWithPixelFormat:pf
                                                               width:(NSUInteger)width
                                                              height:(NSUInteger)height
                                                           mipmapped:NO];
        d.usage = MTLTextureUsageShaderRead | MTLTextureUsageShaderWrite;
        d.storageMode = MTLStorageModePrivate;
        id<MTLTexture> tex = FG_AUTORELEASE([fg_device(ex) newTextureWithDescriptor:d]);
        if (tex == nil) {
            return fg_fail(ex, "storage texture allocation failed");
        }
        FgRes *r = &ex->res[physical];
        r->used = 1;
        r->kind = FLOW_GPU_GRAPH_KIND_TEXTURE;
        r->format = format;
        r->width = width;
        r->height = height;
        r->texel_bytes = tb;
        r->bytes = (int64_t)width * (int64_t)height * (int64_t)tb;
        r->obj = fg_keep(tex);
        return fg_zero_fill(ex, r);
    }
}

static const char *kFgVertexSource =
    "\nstruct FlowGraphVertexOut { float4 pos [[position]]; };\n"
    "vertex FlowGraphVertexOut flow_graph_vertex(uint vid [[vertex_id]]) {\n"
    "    float2 p = vid == 0u ? float2(-1.0, -1.0) : (vid == 1u ? float2(3.0, -1.0) : float2(-1.0, 3.0));\n"
    "    FlowGraphVertexOut o;\n"
    "    o.pos = float4(p, 0.0, 1.0);\n"
    "    return o;\n"
    "}\n";

int32_t flow_gpu_graph_exec_add_pass(void *handle, int32_t kind, const char *source,
                                     const char *entry,
                                     int32_t wg_x, int32_t wg_y, int32_t wg_z,
                                     int32_t grid_x, int32_t grid_y, int32_t grid_z,
                                     int32_t iterations, int32_t barrier_before) {
    FgExec *ex = (FgExec *)handle;
    if (!ex) {
        return -1;
    }
    if (ex->npass >= FG_MAX_PASS) {
        return fg_fail(ex, "too many passes");
    }
    if (!source || !source[0] || !entry || !entry[0]) {
        return fg_fail(ex, "pass needs Metal source and an entry point");
    }
    if (kind != FLOW_GPU_GRAPH_PASS_COMPUTE && kind != FLOW_GPU_GRAPH_PASS_RENDER) {
        return fg_fail(ex, "unknown pass kind");
    }
    if (iterations < 1 || iterations > FG_MAX_ITER) {
        return fg_fail(ex, "iterations outside 1..1024");
    }
    if (kind == FLOW_GPU_GRAPH_PASS_RENDER && iterations != 1) {
        return fg_fail(ex, "a render pass runs once");
    }
    if (kind == FLOW_GPU_GRAPH_PASS_COMPUTE) {
        if (wg_x < 1 || wg_y < 1 || wg_z < 1 || grid_x < 1 || grid_y < 1 || grid_z < 1) {
            return fg_fail(ex, "workgroup and grid axes must be >= 1");
        }
        if ((int64_t)wg_x * wg_y * wg_z > 1024) {
            return fg_fail(ex, "workgroup exceeds 1024 threads");
        }
    }
    @autoreleasepool {
        id<MTLDevice> dev = fg_device(ex);
        NSError *error = nil;
        NSMutableString *src = [NSMutableString stringWithUTF8String:source];
        if (src == nil) {
            return fg_fail(ex, "pass source is not UTF-8");
        }
        if (kind == FLOW_GPU_GRAPH_PASS_RENDER) {
            [src appendString:[NSString stringWithUTF8String:kFgVertexSource]];
        }
        id<MTLLibrary> lib = FG_AUTORELEASE([dev newLibraryWithSource:src options:nil error:&error]);
        if (lib == nil) {
            return fg_failf(ex, "Metal compile failed",
                            error ? [[error localizedDescription] UTF8String] : entry);
        }
        id<MTLFunction> fn = FG_AUTORELEASE([lib newFunctionWithName:[NSString stringWithUTF8String:entry]]);
        if (fn == nil) {
            return fg_failf(ex, "entry point missing", entry);
        }
        FgPass *p = &ex->pass[ex->npass];
        memset(p, 0, sizeof(*p));
        if (kind == FLOW_GPU_GRAPH_PASS_COMPUTE) {
            id<MTLComputePipelineState> pso =
                FG_AUTORELEASE([dev newComputePipelineStateWithFunction:fn error:&error]);
            if (pso == nil) {
                return fg_failf(ex, "compute pipeline failed",
                                error ? [[error localizedDescription] UTF8String] : entry);
            }
            if ((int64_t)wg_x * wg_y * wg_z > (int64_t)[pso maxTotalThreadsPerThreadgroup]) {
                return fg_failf(ex, "workgroup exceeds the pipeline thread limit", entry);
            }
            p->pso = fg_keep(pso);
        } else {
            id<MTLFunction> vfn = FG_AUTORELEASE([lib newFunctionWithName:@"flow_graph_vertex"]);
            MTLRenderPipelineDescriptor *rd = FG_AUTORELEASE([[MTLRenderPipelineDescriptor alloc] init]);
            rd.vertexFunction = vfn;
            rd.fragmentFunction = fn;
            rd.colorAttachments[0].pixelFormat = MTLPixelFormatRGBA8Unorm;
            id<MTLRenderPipelineState> pso =
                FG_AUTORELEASE([dev newRenderPipelineStateWithDescriptor:rd error:&error]);
            if (pso == nil) {
                return fg_failf(ex, "render pipeline failed",
                                error ? [[error localizedDescription] UTF8String] : entry);
            }
            p->pso = fg_keep(pso);
        }
        p->kind = kind;
        p->wg[0] = wg_x;
        p->wg[1] = wg_y;
        p->wg[2] = wg_z;
        p->grid[0] = grid_x;
        p->grid[1] = grid_y;
        p->grid[2] = grid_z;
        p->iterations = iterations;
        p->barrier_before = barrier_before ? 1 : 0;
        return ex->npass++;
    }
}

int32_t flow_gpu_graph_exec_bind(void *handle, int32_t pass, int32_t slot,
                                 int32_t even_physical, int32_t odd_physical) {
    FgExec *ex = (FgExec *)handle;
    if (!ex) {
        return -1;
    }
    if (pass < 0 || pass >= ex->npass) {
        return fg_fail(ex, "bind: unknown pass");
    }
    FgPass *p = &ex->pass[pass];
    if (slot < 0 || slot >= FG_MAX_BIND || p->nbind >= FG_MAX_BIND) {
        return fg_fail(ex, "bind: slot outside 0..7");
    }
    if (!fg_physical_ok(ex, even_physical) || !fg_physical_ok(ex, odd_physical)) {
        return fg_fail(ex, "bind: resource not allocated");
    }
    if (ex->res[even_physical].kind != ex->res[odd_physical].kind) {
        return fg_fail(ex, "bind: ping-pong sides differ in kind");
    }
    for (int i = 0; i < p->nbind; i++) {
        if (p->slot[i] == slot) {
            return fg_fail(ex, "bind: slot already bound");
        }
    }
    p->slot[p->nbind] = slot;
    p->even[p->nbind] = even_physical;
    p->odd[p->nbind] = odd_physical;
    p->nbind++;
    return 0;
}

int32_t flow_gpu_graph_exec_upload(void *handle, int32_t physical, const void *src, int64_t nbytes) {
    FgExec *ex = (FgExec *)handle;
    if (!ex) {
        return -1;
    }
    if (!fg_physical_ok(ex, physical) || !src) {
        return fg_fail(ex, "upload: unknown resource");
    }
    FgRes *r = &ex->res[physical];
    if (nbytes != r->bytes) {
        return fg_fail(ex, "upload: byte count must equal the resource size");
    }
    @autoreleasepool {
        id<MTLBuffer> staging = FG_AUTORELEASE([fg_device(ex) newBufferWithBytes:src
                                                                          length:(NSUInteger)nbytes
                                                                         options:MTLResourceStorageModeShared]);
        if (staging == nil) {
            return fg_fail(ex, "upload: staging allocation failed");
        }
        id<MTLCommandBuffer> cmd = [fg_queue(ex) commandBuffer];
        id<MTLBlitCommandEncoder> blit = [cmd blitCommandEncoder];
        if (r->kind == FLOW_GPU_GRAPH_KIND_BUFFER) {
            [blit copyFromBuffer:staging sourceOffset:0
                        toBuffer:(__bridge id<MTLBuffer>)r->obj destinationOffset:0
                            size:(NSUInteger)nbytes];
        } else {
            [blit copyFromBuffer:staging
                    sourceOffset:0
               sourceBytesPerRow:(NSUInteger)(r->width * r->texel_bytes)
             sourceBytesPerImage:(NSUInteger)r->bytes
                      sourceSize:MTLSizeMake((NSUInteger)r->width, (NSUInteger)r->height, 1)
                       toTexture:(__bridge id<MTLTexture>)r->obj
                destinationSlice:0
                destinationLevel:0
               destinationOrigin:MTLOriginMake(0, 0, 0)];
        }
        [blit endEncoding];
        return fg_finish(ex, cmd, "upload failed");
    }
}

int32_t flow_gpu_graph_exec_read_resource(void *handle, int32_t physical, void *dst, int64_t nbytes) {
    FgExec *ex = (FgExec *)handle;
    if (!ex) {
        return -1;
    }
    if (!fg_physical_ok(ex, physical) || !dst) {
        return fg_fail(ex, "read: unknown resource");
    }
    FgRes *r = &ex->res[physical];
    if (nbytes != r->bytes) {
        return fg_fail(ex, "read: byte count must equal the resource size");
    }
    @autoreleasepool {
        id<MTLBuffer> staging = FG_AUTORELEASE([fg_device(ex) newBufferWithLength:(NSUInteger)nbytes
                                                                          options:MTLResourceStorageModeShared]);
        if (staging == nil) {
            return fg_fail(ex, "read: staging allocation failed");
        }
        id<MTLCommandBuffer> cmd = [fg_queue(ex) commandBuffer];
        id<MTLBlitCommandEncoder> blit = [cmd blitCommandEncoder];
        if (r->kind == FLOW_GPU_GRAPH_KIND_BUFFER) {
            [blit copyFromBuffer:(__bridge id<MTLBuffer>)r->obj sourceOffset:0
                        toBuffer:staging destinationOffset:0
                            size:(NSUInteger)nbytes];
        } else {
            [blit copyFromTexture:(__bridge id<MTLTexture>)r->obj
                      sourceSlice:0
                      sourceLevel:0
                     sourceOrigin:MTLOriginMake(0, 0, 0)
                       sourceSize:MTLSizeMake((NSUInteger)r->width, (NSUInteger)r->height, 1)
                         toBuffer:staging
                destinationOffset:0
           destinationBytesPerRow:(NSUInteger)(r->width * r->texel_bytes)
         destinationBytesPerImage:(NSUInteger)r->bytes];
        }
        [blit endEncoding];
        if (fg_finish(ex, cmd, "read failed") != 0) {
            return -1;
        }
        memcpy(dst, [staging contents], (size_t)nbytes);
        return 0;
    }
}

static int32_t fg_ensure_output(FgExec *ex, int32_t width, int32_t height) {
    if (ex->output && ex->out_w == width && ex->out_h == height) {
        return 0;
    }
    fg_drop(ex->output);
    fg_drop(ex->readback);
    ex->output = NULL;
    ex->readback = NULL;
    ex->have_frame = 0;
    MTLTextureDescriptor *d =
        [MTLTextureDescriptor texture2DDescriptorWithPixelFormat:MTLPixelFormatRGBA8Unorm
                                                           width:(NSUInteger)width
                                                          height:(NSUInteger)height
                                                       mipmapped:NO];
    d.usage = MTLTextureUsageRenderTarget;
    d.storageMode = MTLStorageModePrivate;
    id<MTLTexture> out = FG_AUTORELEASE([fg_device(ex) newTextureWithDescriptor:d]);
    id<MTLBuffer> rb = FG_AUTORELEASE([fg_device(ex) newBufferWithLength:(NSUInteger)width * (NSUInteger)height * 4u
                                                                 options:MTLResourceStorageModeShared]);
    if (out == nil || rb == nil) {
        return fg_fail(ex, "output target allocation failed");
    }
    ex->output = fg_keep(out);
    ex->readback = fg_keep(rb);
    ex->out_w = width;
    ex->out_h = height;
    return 0;
}

static void fg_bind_compute(FgExec *ex, id<MTLComputeCommandEncoder> enc, FgPass *p, int32_t it) {
    for (int i = 0; i < p->nbind; i++) {
        FgRes *r = &ex->res[(it % 2 == 0) ? p->even[i] : p->odd[i]];
        if (r->kind == FLOW_GPU_GRAPH_KIND_BUFFER) {
            [enc setBuffer:(__bridge id<MTLBuffer>)r->obj offset:0 atIndex:(NSUInteger)p->slot[i]];
        } else {
            [enc setTexture:(__bridge id<MTLTexture>)r->obj atIndex:(NSUInteger)p->slot[i]];
        }
    }
}

static void fg_bind_fragment(FgExec *ex, id<MTLRenderCommandEncoder> enc, FgPass *p) {
    for (int i = 0; i < p->nbind; i++) {
        FgRes *r = &ex->res[p->even[i]];
        if (r->kind == FLOW_GPU_GRAPH_KIND_BUFFER) {
            [enc setFragmentBuffer:(__bridge id<MTLBuffer>)r->obj offset:0 atIndex:(NSUInteger)p->slot[i]];
        } else {
            [enc setFragmentTexture:(__bridge id<MTLTexture>)r->obj atIndex:(NSUInteger)p->slot[i]];
        }
    }
}

int32_t flow_gpu_graph_exec_run(void *handle, int32_t width, int32_t height) {
    FgExec *ex = (FgExec *)handle;
    if (!ex) {
        return -1;
    }
    if (ex->npass < 1) {
        return fg_fail(ex, "run: graph has no passes");
    }
    if (width < 1 || height < 1 || width > FG_MAX_DIM || height > FG_MAX_DIM) {
        return fg_fail(ex, "run: output size outside 1..16384");
    }
    int renders = 0;
    for (int i = 0; i < ex->npass; i++) {
        if (ex->pass[i].kind == FLOW_GPU_GRAPH_PASS_RENDER) {
            renders++;
        }
    }
    if (renders != 1) {
        return fg_fail(ex, "run: the graph needs exactly one render pass");
    }
    @autoreleasepool {
        if (fg_ensure_output(ex, width, height) != 0) {
            return -1;
        }
        ex->have_frame = 0;
        int32_t dispatches = 0, barriers = 0, rendered = 0;
        id<MTLCommandBuffer> cmd = [fg_queue(ex) commandBuffer];
        if (cmd == nil) {
            return fg_fail(ex, "run: no command buffer");
        }
        id<MTLComputeCommandEncoder> enc = nil;
        for (int pi = 0; pi < ex->npass; pi++) {
            FgPass *p = &ex->pass[pi];
            if (p->kind == FLOW_GPU_GRAPH_PASS_COMPUTE) {
                int fresh = 0;
                if (enc == nil) {
                    enc = [cmd computeCommandEncoderWithDispatchType:MTLDispatchTypeConcurrent];
                    if (enc == nil) {
                        return fg_fail(ex, "run: no compute encoder");
                    }
                    fresh = 1;
                }
                [enc setComputePipelineState:(__bridge id<MTLComputePipelineState>)p->pso];
                MTLSize groups = MTLSizeMake(
                    (NSUInteger)((p->grid[0] + p->wg[0] - 1) / p->wg[0]),
                    (NSUInteger)((p->grid[1] + p->wg[1] - 1) / p->wg[1]),
                    (NSUInteger)((p->grid[2] + p->wg[2] - 1) / p->wg[2]));
                MTLSize threads = MTLSizeMake((NSUInteger)p->wg[0], (NSUInteger)p->wg[1], (NSUInteger)p->wg[2]);
                for (int32_t it = 0; it < p->iterations; it++) {
                    /* A dependency on an earlier dispatch in this encoder, or
                     * the previous iteration's ping-pong write, needs a barrier. */
                    if ((it > 0) || (p->barrier_before && !fresh)) {
                        [enc memoryBarrierWithScope:MTLBarrierScopeBuffers | MTLBarrierScopeTextures];
                        barriers++;
                    }
                    fg_bind_compute(ex, enc, p, it);
                    [enc dispatchThreadgroups:groups threadsPerThreadgroup:threads];
                    dispatches++;
                    fresh = 0;
                }
            } else {
                if (enc != nil) {
                    [enc endEncoding];
                    enc = nil;
                }
                MTLRenderPassDescriptor *rp = [MTLRenderPassDescriptor renderPassDescriptor];
                rp.colorAttachments[0].texture = (__bridge id<MTLTexture>)ex->output;
                rp.colorAttachments[0].loadAction = MTLLoadActionClear;
                rp.colorAttachments[0].storeAction = MTLStoreActionStore;
                rp.colorAttachments[0].clearColor = MTLClearColorMake(0.0, 0.0, 0.0, 1.0);
                id<MTLRenderCommandEncoder> renc = [cmd renderCommandEncoderWithDescriptor:rp];
                if (renc == nil) {
                    return fg_fail(ex, "run: no render encoder");
                }
                [renc setRenderPipelineState:(__bridge id<MTLRenderPipelineState>)p->pso];
                fg_bind_fragment(ex, renc, p);
                [renc drawPrimitives:MTLPrimitiveTypeTriangle vertexStart:0 vertexCount:3];
                [renc endEncoding];
                rendered++;
            }
        }
        if (enc != nil) {
            [enc endEncoding];
        }
        id<MTLBlitCommandEncoder> blit = [cmd blitCommandEncoder];
        [blit copyFromTexture:(__bridge id<MTLTexture>)ex->output
                  sourceSlice:0
                  sourceLevel:0
                 sourceOrigin:MTLOriginMake(0, 0, 0)
                   sourceSize:MTLSizeMake((NSUInteger)width, (NSUInteger)height, 1)
                     toBuffer:(__bridge id<MTLBuffer>)ex->readback
            destinationOffset:0
       destinationBytesPerRow:(NSUInteger)width * 4u
     destinationBytesPerImage:(NSUInteger)width * (NSUInteger)height * 4u];
        [blit endEncoding];
        if (fg_finish(ex, cmd, "run: command buffer failed") != 0) {
            return -1;
        }
        CFTimeInterval t0 = [cmd GPUStartTime];
        CFTimeInterval t1 = [cmd GPUEndTime];
        ex->gpu_ms = (t1 > t0) ? (t1 - t0) * 1000.0 : 0.0;
        ex->stat_dispatches = dispatches;
        ex->stat_barriers = barriers;
        ex->stat_render = rendered;
        ex->stat_frames++;
        ex->have_frame = 1;
        snprintf(ex->err, sizeof(ex->err), "ok");
        return 0;
    }
}

int32_t flow_gpu_graph_exec_readback(void *handle, void *dst, int64_t nbytes) {
    FgExec *ex = (FgExec *)handle;
    if (!ex) {
        return -1;
    }
    if (!ex->have_frame || !dst) {
        return fg_fail(ex, "readback: no completed run");
    }
    if (nbytes != (int64_t)ex->out_w * (int64_t)ex->out_h * 4) {
        return fg_fail(ex, "readback: byte count must be width * height * 4");
    }
    memcpy(dst, [(__bridge id<MTLBuffer>)ex->readback contents], (size_t)nbytes);
    return 0;
}

int32_t flow_gpu_graph_exec_stat(void *handle, int32_t which) {
    FgExec *ex = (FgExec *)handle;
    if (!ex) {
        return -1;
    }
    switch (which) {
    case FLOW_GPU_GRAPH_STAT_DISPATCHES: return ex->stat_dispatches;
    case FLOW_GPU_GRAPH_STAT_BARRIERS: return ex->stat_barriers;
    case FLOW_GPU_GRAPH_STAT_RENDER_PASSES: return ex->stat_render;
    case FLOW_GPU_GRAPH_STAT_FRAMES: return ex->stat_frames;
    case FLOW_GPU_GRAPH_STAT_PASSES: return ex->npass;
    case FLOW_GPU_GRAPH_STAT_RESOURCES: {
        int32_t n = 0;
        for (int i = 0; i < FG_MAX_RES; i++) {
            n += ex->res[i].used;
        }
        return n;
    }
    default: return -1;
    }
}

double flow_gpu_graph_exec_gpu_ms(void *handle) {
    FgExec *ex = (FgExec *)handle;
    return ex ? ex->gpu_ms : 0.0;
}

#endif /* __APPLE__ */
