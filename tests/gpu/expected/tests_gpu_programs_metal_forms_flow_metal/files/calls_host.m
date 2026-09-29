// Auto-generated Metal host code
#import <Metal/Metal.h>
#import <Foundation/Foundation.h>

void run_calls(
    int out, int output, int result_x, int n, size_t count
) {
    @autoreleasepool {
        // Get default Metal device
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (!device) {
            NSLog(@"Metal is not supported on this device");
            return;
        }

        // Load shader library
        NSString* shaderPath = @"@ROOT@/build/gpu/calls.metal";
        NSError* error = nil;
        NSString* shaderSource = [NSString stringWithContentsOfFile:shaderPath encoding:NSUTF8StringEncoding error:&error];
        id<MTLLibrary> library = [device newLibraryWithSource:shaderSource options:nil error:&error];
        if (!library) {
            NSLog(@"Failed to compile shader: %@", error);
            return;
        }

        id<MTLFunction> kernel = [library newFunctionWithName:@"calls"];
        id<MTLComputePipelineState> pipeline = [device newComputePipelineStateWithFunction:kernel error:&error];

        // Create command queue
        id<MTLCommandQueue> queue = [device newCommandQueue];
        id<MTLCommandBuffer> commandBuffer = [queue commandBuffer];
        id<MTLComputeCommandEncoder> encoder = [commandBuffer computeCommandEncoder];
        [encoder setComputePipelineState:pipeline];

        [encoder setBytes:&out length:sizeof(out) atIndex:0];
        [encoder setBytes:&output length:sizeof(output) atIndex:1];
        [encoder setBytes:&result_x length:sizeof(result_x) atIndex:2];
        [encoder setBytes:&n length:sizeof(n) atIndex:3];

        // Dispatch threads
        MTLSize gridSize = MTLSizeMake(count, 1, 1);
        NSUInteger threadGroupSize = MIN(pipeline.maxTotalThreadsPerThreadgroup, count);
        MTLSize threadgroupSize = MTLSizeMake(threadGroupSize, 1, 1);
        [encoder dispatchThreads:gridSize threadsPerThreadgroup:threadgroupSize];

        [encoder endEncoding];
        [commandBuffer commit];
        [commandBuffer waitUntilCompleted];

        memcpy(out, buffer0.contents, count * sizeof(float));
        memcpy(output, buffer1.contents, count * sizeof(float));
        memcpy(result_x, buffer2.contents, count * sizeof(float));
    }
}