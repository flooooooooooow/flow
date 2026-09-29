// Auto-generated Metal host code
#import <Metal/Metal.h>
#import <Foundation/Foundation.h>

void run_gpu_mse_grad(
    int pred, int target, int grad, int n, size_t count
) {
    @autoreleasepool {
        // Get default Metal device
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (!device) {
            NSLog(@"Metal is not supported on this device");
            return;
        }

        // Load shader library
        NSString* shaderPath = @"@ROOT@/build/gpu/gpu_mse_grad.metal";
        NSError* error = nil;
        NSString* shaderSource = [NSString stringWithContentsOfFile:shaderPath encoding:NSUTF8StringEncoding error:&error];
        id<MTLLibrary> library = [device newLibraryWithSource:shaderSource options:nil error:&error];
        if (!library) {
            NSLog(@"Failed to compile shader: %@", error);
            return;
        }

        id<MTLFunction> kernel = [library newFunctionWithName:@"gpu_mse_grad"];
        id<MTLComputePipelineState> pipeline = [device newComputePipelineStateWithFunction:kernel error:&error];

        // Create command queue
        id<MTLCommandQueue> queue = [device newCommandQueue];
        id<MTLCommandBuffer> commandBuffer = [queue commandBuffer];
        id<MTLComputeCommandEncoder> encoder = [commandBuffer computeCommandEncoder];
        [encoder setComputePipelineState:pipeline];

        [encoder setBytes:&pred length:sizeof(pred) atIndex:0];
        [encoder setBytes:&target length:sizeof(target) atIndex:1];
        [encoder setBytes:&grad length:sizeof(grad) atIndex:2];
        [encoder setBytes:&n length:sizeof(n) atIndex:3];

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