/* FLOW GPU memory — Metal backend (Apple Silicon / macOS).
 *
 * Shared storage = unified CPU/GPU memory (`flow_gpu_host_ptr` usable).
 * Private storage uses blit copies via a shared staging buffer.
 */
#ifdef __APPLE__

#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#include "gpu_memory.h"

#include <stdlib.h>
#include <string.h>

typedef struct FlowGpuBuffer {
    void *mtl_ref; /* CFBridgingRetain(id<MTLBuffer>) */
    int64_t size;
    int32_t flags;
    int shared;
} FlowGpuBuffer;

static id<MTLDevice> g_device = nil;
static id<MTLCommandQueue> g_queue = nil;

static id<MTLBuffer> flow_gpu_mtl(FlowGpuBuffer *buf) {
    if (!buf || !buf->mtl_ref) {
        return nil;
    }
    return (__bridge id<MTLBuffer>)buf->mtl_ref;
}

static int flow_gpu_metal_init(void) {
    if (g_device != nil) {
        return 0;
    }
    @autoreleasepool {
        g_device = MTLCreateSystemDefaultDevice();
        if (g_device == nil) {
            return -1;
        }
        g_queue = [g_device newCommandQueue];
        if (g_queue == nil) {
            g_device = nil;
            return -1;
        }
    }
    return 0;
}

int flow_gpu_available(void) {
    return flow_gpu_metal_init() == 0 ? 1 : 0;
}

const char *flow_gpu_backend_name(void) {
    return flow_gpu_available() ? "metal" : "stub";
}

void *flow_gpu_alloc(int64_t size, int32_t flags) {
    if (size <= 0 || flow_gpu_metal_init() != 0) {
        return NULL;
    }
    @autoreleasepool {
        MTLResourceOptions opts = MTLResourceStorageModeShared;
        int shared = 1;
        if (flags == FLOW_GPU_MEM_PRIVATE) {
            opts = MTLResourceStorageModePrivate;
            shared = 0;
        }

        id<MTLBuffer> mtl = [g_device newBufferWithLength:(NSUInteger)size options:opts];
        if (mtl == nil) {
            return NULL;
        }

        FlowGpuBuffer *buf = (FlowGpuBuffer *)calloc(1, sizeof(FlowGpuBuffer));
        if (!buf) {
            return NULL;
        }
        buf->mtl_ref = (void *)CFBridgingRetain(mtl);
        buf->size = size;
        buf->flags = (flags == FLOW_GPU_MEM_DEFAULT) ? FLOW_GPU_MEM_SHARED : flags;
        buf->shared = shared;
        return buf;
    }
}

void flow_gpu_free(void *handle) {
    if (!handle) {
        return;
    }
    FlowGpuBuffer *buf = (FlowGpuBuffer *)handle;
    if (buf->mtl_ref) {
        CFRelease((CFTypeRef)buf->mtl_ref);
        buf->mtl_ref = NULL;
    }
    free(buf);
}

int64_t flow_gpu_size(void *handle) {
    if (!handle) {
        return 0;
    }
    return ((FlowGpuBuffer *)handle)->size;
}

int32_t flow_gpu_flags(void *handle) {
    if (!handle) {
        return 0;
    }
    return ((FlowGpuBuffer *)handle)->flags;
}

void *flow_gpu_host_ptr(void *handle) {
    if (!handle) {
        return NULL;
    }
    FlowGpuBuffer *buf = (FlowGpuBuffer *)handle;
    if (!buf->shared) {
        return NULL;
    }
    id<MTLBuffer> mtl = flow_gpu_mtl(buf);
    if (!mtl) {
        return NULL;
    }
    return [mtl contents];
}

static int flow_gpu_blit_copy(id<MTLBuffer> dst, NSUInteger dst_off,
                              id<MTLBuffer> src, NSUInteger src_off,
                              NSUInteger len) {
    if (flow_gpu_metal_init() != 0 || !dst || !src || len == 0) {
        return -1;
    }
    @autoreleasepool {
        id<MTLCommandBuffer> cmd = [g_queue commandBuffer];
        if (!cmd) {
            return -1;
        }
        id<MTLBlitCommandEncoder> blit = [cmd blitCommandEncoder];
        [blit copyFromBuffer:src sourceOffset:src_off
                    toBuffer:dst destinationOffset:dst_off
                        size:len];
        [blit endEncoding];
        [cmd commit];
        [cmd waitUntilCompleted];
        return 0;
    }
}

int flow_gpu_copy_h2d(void *dst_gpu, const void *src_host, int64_t nbytes) {
    if (!dst_gpu || !src_host || nbytes <= 0) {
        return -1;
    }
    FlowGpuBuffer *dst = (FlowGpuBuffer *)dst_gpu;
    id<MTLBuffer> dst_mtl = flow_gpu_mtl(dst);
    if (!dst_mtl || nbytes > dst->size) {
        return -1;
    }
    @autoreleasepool {
        if (dst->shared) {
            memcpy([dst_mtl contents], src_host, (size_t)nbytes);
            return 0;
        }
        id<MTLBuffer> staging = [g_device newBufferWithBytes:src_host
                                                     length:(NSUInteger)nbytes
                                                    options:MTLResourceStorageModeShared];
        if (!staging) {
            return -1;
        }
        return flow_gpu_blit_copy(dst_mtl, 0, staging, 0, (NSUInteger)nbytes);
    }
}

int flow_gpu_copy_d2h(void *dst_host, void *src_gpu, int64_t nbytes) {
    if (!dst_host || !src_gpu || nbytes <= 0) {
        return -1;
    }
    FlowGpuBuffer *src = (FlowGpuBuffer *)src_gpu;
    id<MTLBuffer> src_mtl = flow_gpu_mtl(src);
    if (!src_mtl || nbytes > src->size) {
        return -1;
    }
    @autoreleasepool {
        if (src->shared) {
            memcpy(dst_host, [src_mtl contents], (size_t)nbytes);
            return 0;
        }
        id<MTLBuffer> staging = [g_device newBufferWithLength:(NSUInteger)nbytes
                                                     options:MTLResourceStorageModeShared];
        if (!staging) {
            return -1;
        }
        if (flow_gpu_blit_copy(staging, 0, src_mtl, 0, (NSUInteger)nbytes) != 0) {
            return -1;
        }
        memcpy(dst_host, [staging contents], (size_t)nbytes);
        return 0;
    }
}

int flow_gpu_copy_d2d(void *dst_gpu, void *src_gpu, int64_t nbytes) {
    if (!dst_gpu || !src_gpu || nbytes <= 0) {
        return -1;
    }
    FlowGpuBuffer *dst = (FlowGpuBuffer *)dst_gpu;
    FlowGpuBuffer *src = (FlowGpuBuffer *)src_gpu;
    id<MTLBuffer> dst_mtl = flow_gpu_mtl(dst);
    id<MTLBuffer> src_mtl = flow_gpu_mtl(src);
    if (!dst_mtl || !src_mtl || nbytes > dst->size || nbytes > src->size) {
        return -1;
    }
    @autoreleasepool {
        if (dst->shared && src->shared) {
            memcpy([dst_mtl contents], [src_mtl contents], (size_t)nbytes);
            return 0;
        }
        return flow_gpu_blit_copy(dst_mtl, 0, src_mtl, 0, (NSUInteger)nbytes);
    }
}

void flow_gpu_sync(void) {
    /* Per-copy waits already flush work. */
}

#endif /* __APPLE__ */
