// Auto-generated Metal host code
#import <Metal/Metal.h>
#import <Foundation/Foundation.h>

void run_reserved_names(
    int loop, int ref, int target, int __tmp, int switch, size_t count
) {
    @autoreleasepool {
        // Get default Metal device
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (!device) {
            NSLog(@"Metal is not supported on this device");
            return;
        }

        // Load shader library
        NSString* shaderPath = @"@ROOT@/build/gpu/reserved_names.metal";
        NSError* error = nil;
        NSString* shaderSource = [NSString stringWithContentsOfFile:shaderPath encoding:NSUTF8StringEncoding error:&error];
        id<MTLLibrary> library = [device newLibraryWithSource:shaderSource options:nil error:&error];
        if (!library) {
            NSLog(@"Failed to compile shader: %@", error);
            return;
        }

        id<MTLFunction> kernel = [library newFunctionWithName:@"reserved_names"];
        id<MTLComputePipelineState> pipeline = [device newComputePipelineStateWithFunction:kernel error:&error];

        // Create command queue
        id<MTLCommandQueue> queue = [device newCommandQueue];
        id<MTLCommandBuffer> commandBuffer = [queue commandBuffer];
        id<MTLComputeCommandEncoder> encoder = [commandBuffer computeCommandEncoder];
        [encoder setComputePipelineState:pipeline];

        [encoder setBytes:&loop length:sizeof(loop) atIndex:0];
        [encoder setBytes:&ref length:sizeof(ref) atIndex:1];
        [encoder setBytes:&target length:sizeof(target) atIndex:2];
        [encoder setBytes:&__tmp length:sizeof(__tmp) atIndex:3];
        [encoder setBytes:&switch length:sizeof(switch) atIndex:4];

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