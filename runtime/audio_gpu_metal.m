// Flow Audio GPU Backend - Metal (experimental)
//
// Provides simple gain and convolution compute kernels.

#ifdef __APPLE__

#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#include <stdint.h>

static id<MTLDevice> g_device = nil;
static id<MTLCommandQueue> g_queue = nil;
static id<MTLLibrary> g_library = nil;
static id<MTLComputePipelineState> g_gainPSO = nil;
static id<MTLComputePipelineState> g_convPSO = nil;

static const char* kAudioMetalSource =
"#include <metal_stdlib>\\n"
"using namespace metal;\\n"
"kernel void gain_kernel(const device float* in [[buffer(0)]],\\n"
"                        device float* out [[buffer(1)]],\\n"
"                        constant uint& count [[buffer(2)]],\\n"
"                        constant float& gain [[buffer(3)]],\\n"
"                        uint gid [[thread_position_in_grid]]) {\\n"
"    if (gid >= count) return;\\n"
"    out[gid] = in[gid] * gain;\\n"
"}\\n"
"kernel void conv_kernel(const device float* in [[buffer(0)]],\\n"
"                        device float* out [[buffer(1)]],\\n"
"                        const device float* impulse [[buffer(2)]],\\n"
"                        constant uint& frames [[buffer(3)]],\\n"
"                        constant uint& channels [[buffer(4)]],\\n"
"                        constant uint& imp_len [[buffer(5)]],\\n"
"                        uint gid [[thread_position_in_grid]]) {\\n"
"    uint total = frames * channels;\\n"
"    if (gid >= total) return;\\n"
"    uint channel = gid % channels;\\n"
"    uint frame = gid / channels;\\n"
"    float acc = 0.0f;\\n"
"    for (uint k = 0; k < imp_len; ++k) {\\n"
"        if (frame < k) break;\\n"
"        uint idx = (frame - k) * channels + channel;\\n"
"        acc += in[idx] * impulse[k];\\n"
"    }\\n"
"    out[gid] = acc;\\n"
"}\\n";

static int flow_audio_metal_init(void) {
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
            return -1;
        }
        NSError* error = nil;
        NSString* source = [NSString stringWithUTF8String:kAudioMetalSource];
        g_library = [g_device newLibraryWithSource:source options:nil error:&error];
        if (g_library == nil) {
            return -1;
        }
        id<MTLFunction> gainFn = [g_library newFunctionWithName:@"gain_kernel"];
        id<MTLFunction> convFn = [g_library newFunctionWithName:@"conv_kernel"];
        if (gainFn == nil || convFn == nil) {
            return -1;
        }
        g_gainPSO = [g_device newComputePipelineStateWithFunction:gainFn error:&error];
        g_convPSO = [g_device newComputePipelineStateWithFunction:convFn error:&error];
        if (g_gainPSO == nil || g_convPSO == nil) {
            return -1;
        }
    }
    return 0;
}

int flow_audio_metal_available(void) {
    return flow_audio_metal_init() == 0 ? 1 : 0;
}

int flow_audio_metal_gain_f32(float* data, int frames, int channels, float gain) {
    if (flow_audio_metal_init() != 0 || !data || frames <= 0 || channels <= 0) {
        return -1;
    }
    @autoreleasepool {
        uint32_t total = (uint32_t)(frames * channels);
        id<MTLBuffer> inBuf = [g_device newBufferWithBytes:data length:total * sizeof(float) options:MTLResourceStorageModeShared];
        id<MTLBuffer> outBuf = [g_device newBufferWithLength:total * sizeof(float) options:MTLResourceStorageModeShared];
        id<MTLBuffer> countBuf = [g_device newBufferWithBytes:&total length:sizeof(uint32_t) options:MTLResourceStorageModeShared];
        id<MTLBuffer> gainBuf = [g_device newBufferWithBytes:&gain length:sizeof(float) options:MTLResourceStorageModeShared];

        id<MTLCommandBuffer> cmd = [g_queue commandBuffer];
        id<MTLComputeCommandEncoder> enc = [cmd computeCommandEncoder];
        [enc setComputePipelineState:g_gainPSO];
        [enc setBuffer:inBuf offset:0 atIndex:0];
        [enc setBuffer:outBuf offset:0 atIndex:1];
        [enc setBuffer:countBuf offset:0 atIndex:2];
        [enc setBuffer:gainBuf offset:0 atIndex:3];

        MTLSize grid = MTLSizeMake(total, 1, 1);
        NSUInteger tg = g_gainPSO.maxTotalThreadsPerThreadgroup;
        if (tg == 0) tg = 256;
        MTLSize group = MTLSizeMake(tg, 1, 1);
        [enc dispatchThreads:grid threadsPerThreadgroup:group];
        [enc endEncoding];
        [cmd commit];
        [cmd waitUntilCompleted];

        memcpy(data, outBuf.contents, total * sizeof(float));
    }
    return 0;
}

int flow_audio_metal_convolution_f32(float* data, int frames, int channels, const float* impulse, int impulse_len) {
    if (flow_audio_metal_init() != 0 || !data || !impulse || frames <= 0 || channels <= 0 || impulse_len <= 0) {
        return -1;
    }
    @autoreleasepool {
        uint32_t total = (uint32_t)(frames * channels);
        uint32_t uframes = (uint32_t)frames;
        uint32_t uchannels = (uint32_t)channels;
        uint32_t uimp = (uint32_t)impulse_len;

        id<MTLBuffer> inBuf = [g_device newBufferWithBytes:data length:total * sizeof(float) options:MTLResourceStorageModeShared];
        id<MTLBuffer> outBuf = [g_device newBufferWithLength:total * sizeof(float) options:MTLResourceStorageModeShared];
        id<MTLBuffer> impBuf = [g_device newBufferWithBytes:impulse length:impulse_len * sizeof(float) options:MTLResourceStorageModeShared];
        id<MTLBuffer> framesBuf = [g_device newBufferWithBytes:&uframes length:sizeof(uint32_t) options:MTLResourceStorageModeShared];
        id<MTLBuffer> chBuf = [g_device newBufferWithBytes:&uchannels length:sizeof(uint32_t) options:MTLResourceStorageModeShared];
        id<MTLBuffer> impLenBuf = [g_device newBufferWithBytes:&uimp length:sizeof(uint32_t) options:MTLResourceStorageModeShared];

        id<MTLCommandBuffer> cmd = [g_queue commandBuffer];
        id<MTLComputeCommandEncoder> enc = [cmd computeCommandEncoder];
        [enc setComputePipelineState:g_convPSO];
        [enc setBuffer:inBuf offset:0 atIndex:0];
        [enc setBuffer:outBuf offset:0 atIndex:1];
        [enc setBuffer:impBuf offset:0 atIndex:2];
        [enc setBuffer:framesBuf offset:0 atIndex:3];
        [enc setBuffer:chBuf offset:0 atIndex:4];
        [enc setBuffer:impLenBuf offset:0 atIndex:5];

        MTLSize grid = MTLSizeMake(total, 1, 1);
        NSUInteger tg = g_convPSO.maxTotalThreadsPerThreadgroup;
        if (tg == 0) tg = 256;
        MTLSize group = MTLSizeMake(tg, 1, 1);
        [enc dispatchThreads:grid threadsPerThreadgroup:group];
        [enc endEncoding];
        [cmd commit];
        [cmd waitUntilCompleted];

        memcpy(data, outBuf.contents, total * sizeof(float));
    }
    return 0;
}

#else

int flow_audio_metal_available(void) { return 0; }
int flow_audio_metal_gain_f32(float* data, int frames, int channels, float gain) {
    (void)data; (void)frames; (void)channels; (void)gain;
    return -1;
}
int flow_audio_metal_convolution_f32(float* data, int frames, int channels, const float* impulse, int impulse_len) {
    (void)data; (void)frames; (void)channels; (void)impulse; (void)impulse_len;
    return -1;
}

#endif
