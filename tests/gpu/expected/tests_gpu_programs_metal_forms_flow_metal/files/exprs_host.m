// Auto-generated Metal host code
#import <Metal/Metal.h>
#import <Foundation/Foundation.h>

void run_exprs(
    int p, int q, int r, int v, unsigned int u, int big, double d, int w, int s, size_t count
) {
    @autoreleasepool {
        // Get default Metal device
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (!device) {
            NSLog(@"Metal is not supported on this device");
            return;
        }

        // Load shader library
        NSString* shaderPath = @"@ROOT@/build/gpu/exprs.metal";
        NSError* error = nil;
        NSString* shaderSource = [NSString stringWithContentsOfFile:shaderPath encoding:NSUTF8StringEncoding error:&error];
        id<MTLLibrary> library = [device newLibraryWithSource:shaderSource options:nil error:&error];
        if (!library) {
            NSLog(@"Failed to compile shader: %@", error);
            return;
        }

        id<MTLFunction> kernel = [library newFunctionWithName:@"exprs"];
        id<MTLComputePipelineState> pipeline = [device newComputePipelineStateWithFunction:kernel error:&error];

        // Create command queue
        id<MTLCommandQueue> queue = [device newCommandQueue];
        id<MTLCommandBuffer> commandBuffer = [queue commandBuffer];
        id<MTLComputeCommandEncoder> encoder = [commandBuffer computeCommandEncoder];
        [encoder setComputePipelineState:pipeline];

        [encoder setBytes:&p length:sizeof(p) atIndex:0];
        [encoder setBytes:&q length:sizeof(q) atIndex:1];
        [encoder setBytes:&r length:sizeof(r) atIndex:2];
        [encoder setBytes:&v length:sizeof(v) atIndex:3];
        [encoder setBytes:&u length:sizeof(u) atIndex:4];
        [encoder setBytes:&big length:sizeof(big) atIndex:5];
        [encoder setBytes:&d length:sizeof(d) atIndex:6];
        [encoder setBytes:&w length:sizeof(w) atIndex:7];
        [encoder setBytes:&s length:sizeof(s) atIndex:8];

        // Dispatch threads
        MTLSize gridSize = MTLSizeMake(count, 1, 1);
        NSUInteger threadGroupSize = MIN(pipeline.maxTotalThreadsPerThreadgroup, count);
        MTLSize threadgroupSize = MTLSizeMake(threadGroupSize, 1, 1);
        [encoder dispatchThreads:gridSize threadsPerThreadgroup:threadgroupSize];

        [encoder endEncoding];
        [commandBuffer commit];
        [commandBuffer waitUntilCompleted];

    }
}