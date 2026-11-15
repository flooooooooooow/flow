/* metal_run: run a .metallib from `flow gpu-lower --target metal` through
 * Metal compute.
 *
 *   metal_run KERNELS.metallib DATA_DIR OUT_DIR
 *
 * DATA_DIR/launch.txt has the format vk_run.c reads. The MSL comes from
 * SPIRV-Cross with --msl-decoration-binding, so kernel argument I (SPIR-V
 * set 0, binding I) is [[buffer(I)]]. Each dispatch runs GX*GY*GZ
 * threadgroups of 64x1x1 threads, the workgroup size the Flow emitter
 * gives every @gpu kernel, and completes before the next is encoded.
 * After the last one every buffer is written to OUT_DIR/gpu_IDX.bin.
 *
 * Status: 0 ran, 1 a Metal or file error, 2 usage, 3 no Metal device.
 */
#import <Foundation/Foundation.h>
#import <Metal/Metal.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_BUFS 32
#define MAX_ARGS 16

int main(int argc, char **argv) {
    @autoreleasepool {
        if (argc != 4) {
            fprintf(stderr, "usage: metal_run KERNELS.metallib DATA_DIR OUT_DIR\n");
            return 2;
        }
        id<MTLDevice> dev = MTLCreateSystemDefaultDevice();
        if (!dev) {
            fprintf(stderr, "metal_run: no Metal device\n");
            return 3;
        }
        fprintf(stderr, "metal_run: device %s\n", dev.name.UTF8String);
        NSError *err = nil;
        NSURL *url = [NSURL fileURLWithPath:[NSString stringWithUTF8String:argv[1]]];
        id<MTLLibrary> lib = [dev newLibraryWithURL:url error:&err];
        if (!lib) {
            fprintf(stderr, "metal_run: cannot load %s: %s\n", argv[1], err.localizedDescription.UTF8String);
            return 1;
        }
        id<MTLCommandQueue> q = [dev newCommandQueue];
        id<MTLBuffer> bufs[MAX_BUFS] = {nil};
        long bytes[MAX_BUFS] = {0};

        NSString *launch = [NSString stringWithContentsOfFile:[NSString stringWithFormat:@"%s/launch.txt", argv[2]]
                                                     encoding:NSUTF8StringEncoding
                                                        error:&err];
        if (!launch) {
            fprintf(stderr, "metal_run: cannot read %s/launch.txt\n", argv[2]);
            return 1;
        }
        NSCharacterSet *ws = [NSCharacterSet whitespaceCharacterSet];
        for (NSString *raw in [launch componentsSeparatedByString:@"\n"]) {
            NSMutableArray<NSString *> *t = [NSMutableArray array];
            for (NSString *w in [raw componentsSeparatedByCharactersInSet:ws]) {
                if (w.length > 0) {
                    [t addObject:w];
                }
            }
            if (t.count == 0) {
                continue;
            }
            if ([t[0] isEqualToString:@"buffer"] && t.count >= 5) {
                int idx = t[1].intValue;
                if (idx < 0 || idx >= MAX_BUFS) {
                    return 1;
                }
                bytes[idx] = (long)t[3].longLongValue * 4;
                NSString *p = [NSString stringWithFormat:@"%s/in_%d.bin", argv[2], idx];
                NSData *init = [NSData dataWithContentsOfFile:p];
                if (!init || (long)init.length != bytes[idx]) {
                    fprintf(stderr, "metal_run: %s missing or not %ld bytes\n", p.UTF8String, bytes[idx]);
                    return 1;
                }
                bufs[idx] = [dev newBufferWithBytes:init.bytes length:init.length options:MTLResourceStorageModeShared];
            } else if ([t[0] isEqualToString:@"dispatch"] && t.count >= 5) {
                NSString *name = t[1];
                id<MTLFunction> fn = [lib newFunctionWithName:name];
                if (!fn) {
                    /* SPIRV-Cross renames an entry point that is an MSL keyword. */
                    fn = [lib newFunctionWithName:[name stringByAppendingString:@"0"]];
                }
                if (!fn) {
                    fprintf(stderr, "metal_run: no kernel %s in %s\n", name.UTF8String, argv[1]);
                    return 1;
                }
                id<MTLComputePipelineState> pso = [dev newComputePipelineStateWithFunction:fn error:&err];
                if (!pso) {
                    fprintf(stderr, "metal_run: pipeline %s: %s\n", name.UTF8String, err.localizedDescription.UTF8String);
                    return 1;
                }
                id<MTLCommandBuffer> cb = [q commandBuffer];
                id<MTLComputeCommandEncoder> enc = [cb computeCommandEncoder];
                [enc setComputePipelineState:pso];
                for (NSUInteger i = 5; i < t.count && i - 5 < MAX_ARGS; i++) {
                    int b = t[i].intValue;
                    if (b < 0 || b >= MAX_BUFS || !bufs[b]) {
                        fprintf(stderr, "metal_run: dispatch %s names unknown buffer %d\n", name.UTF8String, b);
                        return 1;
                    }
                    [enc setBuffer:bufs[b] offset:0 atIndex:i - 5];
                }
                MTLSize groups = MTLSizeMake((NSUInteger)t[2].integerValue, (NSUInteger)t[3].integerValue, (NSUInteger)t[4].integerValue);
                [enc dispatchThreadgroups:groups threadsPerThreadgroup:MTLSizeMake(64, 1, 1)];
                [enc endEncoding];
                [cb commit];
                [cb waitUntilCompleted];
                if (cb.status != MTLCommandBufferStatusCompleted) {
                    fprintf(stderr, "metal_run: %s did not complete: %s\n", name.UTF8String, cb.error.localizedDescription.UTF8String);
                    return 1;
                }
            }
        }
        for (int b = 0; b < MAX_BUFS; b++) {
            if (!bufs[b]) {
                continue;
            }
            NSString *p = [NSString stringWithFormat:@"%s/gpu_%d.bin", argv[3], b];
            NSData *d = [NSData dataWithBytes:bufs[b].contents length:(NSUInteger)bytes[b]];
            if (![d writeToFile:p atomically:NO]) {
                fprintf(stderr, "metal_run: cannot write %s\n", p.UTF8String);
                return 1;
            }
        }
    }
    return 0;
}
