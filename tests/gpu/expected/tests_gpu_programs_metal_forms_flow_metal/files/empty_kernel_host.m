// Auto-generated Metal host code
#import <Metal/Metal.h>
#import <Foundation/Foundation.h>

void run_empty_kernel(
    size_t count
) {
    @autoreleasepool {
        // Get default Metal device
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (!device) {
            NSLog(@"Metal is not supported on this device");
            return;
        }

        // Load shader library
        NSString* shaderPath = @"@ROOT@/build/gpu/empty_kernel.metal";
        NSError* error = nil;
        NSString* shaderSource = [NSString stringWithContentsOfFile:shaderPath encoding:NSUTF8StringEncoding error:&error];
        id<MTLLibrary> library = [device newLibraryWithSource:shaderSource options:nil error:&error];
        if (!library) {
            NSLog(@"Failed to compile shader: %@", error);
            return;
        }

        id<MTLFunction> kernel = [library newFunctionWithName:@"empty_kernel"];
        id<MTLComputePipelineState> pipeline = [device newComputePipelineStateWithFunction:kernel error:&error];

        // Create command queue
        id<MTLCommandQueue> queue = [device newCommandQueue];
        id<MTLCommandBuffer> commandBuffer = [queue commandBuffer];
        id<MTLComputeCommandEncoder> encoder = [commandBuffer computeCommandEncoder];
        [encoder setComputePipelineState:pipeline];


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