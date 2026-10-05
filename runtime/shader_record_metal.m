/* Deterministic offscreen recorder for FLOW Shader Language (FSL).
 *
 * This is deliberately separate from shader_view_metal.m: the live viewer owns
 * a CAMetalLayer and wall-clock animation, while gallery recordings need no
 * window and must be reproducible. The program renders the exact generated MSL
 * fragment entry into an offscreen Metal texture, copies BGRA pixels back to a
 * shared buffer, and writes P6 PPM frames for scripts/frames_to_gif.py.
 *
 * Build on macOS:
 *   xcrun clang -O2 -fobjc-arc runtime/shader_record_metal.m \
 *     -framework Metal -framework Foundation -o build/shader_record_metal
 *
 * Run:
 *   build/shader_record_metal shader.metal entry_frag out/frames \
 *     640 360 24 12
 */
#ifdef __APPLE__

#import <Foundation/Foundation.h>
#import <Metal/Metal.h>

#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>

typedef struct {
    float time;
    float width;
    float height;
} FlowShaderUniforms;

static char *flow_read_file(const char *path)
{
    FILE *f = fopen(path, "rb");
    if (!f) return NULL;
    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return NULL;
    }
    long n = ftell(f);
    if (n < 0 || fseek(f, 0, SEEK_SET) != 0) {
        fclose(f);
        return NULL;
    }
    char *buf = (char *)malloc((size_t)n + 1);
    if (!buf) {
        fclose(f);
        return NULL;
    }
    if (fread(buf, 1, (size_t)n, f) != (size_t)n) {
        free(buf);
        fclose(f);
        return NULL;
    }
    buf[n] = '\0';
    fclose(f);
    return buf;
}

static int flow_mkdir_p(const char *path)
{
    char tmp[4096];
    size_t n = strlen(path);
    if (n == 0 || n >= sizeof(tmp)) return 0;
    memcpy(tmp, path, n + 1);

    for (char *p = tmp + 1; *p; p++) {
        if (*p != '/') continue;
        *p = '\0';
        if (mkdir(tmp, 0755) != 0 && errno != EEXIST) return 0;
        *p = '/';
    }
    return mkdir(tmp, 0755) == 0 || errno == EEXIST;
}

static int flow_write_ppm(
    const char *path,
    const uint8_t *bgra,
    int width,
    int height,
    size_t bytes_per_row
)
{
    FILE *f = fopen(path, "wb");
    if (!f) {
        fprintf(stderr, "shader_record: cannot write %s\n", path);
        return 0;
    }
    fprintf(f, "P6\n%d %d\n255\n", width, height);
    for (int y = 0; y < height; y++) {
        const uint8_t *row = bgra + (size_t)y * bytes_per_row;
        for (int x = 0; x < width; x++) {
            const uint8_t *px = row + (size_t)x * 4;
            const uint8_t rgb[3] = { px[2], px[1], px[0] };
            if (fwrite(rgb, 1, 3, f) != 3) {
                fclose(f);
                return 0;
            }
        }
    }
    fclose(f);
    return 1;
}

static int flow_shader_record(
    const char *metal_path,
    const char *fragment_name,
    const char *out_dir,
    int width,
    int height,
    int frames,
    int fps
)
{
    if (width <= 0 || height <= 0 || frames <= 0 || fps <= 0) {
        fprintf(stderr, "shader_record: width/height/frames/fps must be positive\n");
        return 1;
    }
    if (!flow_mkdir_p(out_dir)) {
        fprintf(stderr, "shader_record: cannot create %s\n", out_dir);
        return 1;
    }

    char *source = flow_read_file(metal_path);
    if (!source) {
        fprintf(stderr, "shader_record: cannot read %s\n", metal_path);
        return 1;
    }

    @autoreleasepool {
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (!device) {
            free(source);
            fprintf(stderr,
                "shader_record: no Metal device. The recorder needs a real or "
                "GPU-enabled macOS host.\n");
            return 2;
        }

        NSError *error = nil;
        NSString *src = [NSString stringWithUTF8String:source];
        id<MTLLibrary> library = [device newLibraryWithSource:src options:nil error:&error];
        free(source);
        if (!library) {
            fprintf(stderr, "shader_record: Metal compile failed: %s\n",
                error ? error.localizedDescription.UTF8String : "unknown error");
            return 1;
        }

        id<MTLFunction> vertex = [library newFunctionWithName:@"flow_shader_vertex"];
        NSString *fragment_string = [NSString stringWithUTF8String:fragment_name];
        id<MTLFunction> fragment = [library newFunctionWithName:fragment_string];
        if (!vertex || !fragment) {
            fprintf(stderr, "shader_record: missing vertex or fragment entry %s\n", fragment_name);
            return 1;
        }

        MTLRenderPipelineDescriptor *pipeline_desc = [[MTLRenderPipelineDescriptor alloc] init];
        pipeline_desc.vertexFunction = vertex;
        pipeline_desc.fragmentFunction = fragment;
        pipeline_desc.colorAttachments[0].pixelFormat = MTLPixelFormatBGRA8Unorm;
        id<MTLRenderPipelineState> pipeline =
            [device newRenderPipelineStateWithDescriptor:pipeline_desc error:&error];
        if (!pipeline) {
            fprintf(stderr, "shader_record: pipeline failed: %s\n",
                error ? error.localizedDescription.UTF8String : "unknown error");
            return 1;
        }

        id<MTLCommandQueue> queue = [device newCommandQueue];
        if (!queue) {
            fprintf(stderr, "shader_record: cannot create command queue\n");
            return 1;
        }

        MTLTextureDescriptor *texture_desc =
            [MTLTextureDescriptor texture2DDescriptorWithPixelFormat:MTLPixelFormatBGRA8Unorm
                                                               width:(NSUInteger)width
                                                              height:(NSUInteger)height
                                                           mipmapped:NO];
        texture_desc.usage = MTLTextureUsageRenderTarget;
        texture_desc.storageMode = MTLStorageModePrivate;
        id<MTLTexture> target = [device newTextureWithDescriptor:texture_desc];
        if (!target) {
            fprintf(stderr, "shader_record: cannot allocate render texture\n");
            return 1;
        }

        /* Metal texture-to-buffer blits require a 256-byte row alignment on
         * common Apple GPUs. Padding is ignored when the PPM is written. */
        size_t tight_row = (size_t)width * 4;
        size_t bytes_per_row = (tight_row + 255u) & ~255u;
        size_t buffer_bytes = bytes_per_row * (size_t)height;
        id<MTLBuffer> readback =
            [device newBufferWithLength:buffer_bytes options:MTLResourceStorageModeShared];
        if (!readback) {
            fprintf(stderr, "shader_record: cannot allocate readback buffer\n");
            return 1;
        }

        for (int frame = 0; frame < frames; frame++) {
            @autoreleasepool {
                FlowShaderUniforms uniforms;
                uniforms.time = (float)frame / (float)fps;
                uniforms.width = (float)width;
                uniforms.height = (float)height;

                MTLRenderPassDescriptor *pass = [MTLRenderPassDescriptor renderPassDescriptor];
                pass.colorAttachments[0].texture = target;
                pass.colorAttachments[0].loadAction = MTLLoadActionClear;
                pass.colorAttachments[0].storeAction = MTLStoreActionStore;
                pass.colorAttachments[0].clearColor = MTLClearColorMake(0, 0, 0, 1);

                id<MTLCommandBuffer> command = [queue commandBuffer];
                id<MTLRenderCommandEncoder> render =
                    [command renderCommandEncoderWithDescriptor:pass];
                [render setRenderPipelineState:pipeline];
                [render setVertexBytes:&uniforms length:sizeof(uniforms) atIndex:0];
                [render setFragmentBytes:&uniforms length:sizeof(uniforms) atIndex:0];
                [render drawPrimitives:MTLPrimitiveTypeTriangle vertexStart:0 vertexCount:3];
                [render endEncoding];

                id<MTLBlitCommandEncoder> blit = [command blitCommandEncoder];
                [blit copyFromTexture:target
                          sourceSlice:0
                          sourceLevel:0
                         sourceOrigin:MTLOriginMake(0, 0, 0)
                           sourceSize:MTLSizeMake((NSUInteger)width, (NSUInteger)height, 1)
                             toBuffer:readback
                    destinationOffset:0
               destinationBytesPerRow:bytes_per_row
             destinationBytesPerImage:buffer_bytes];
                [blit endEncoding];
                [command commit];
                [command waitUntilCompleted];

                if (command.status == MTLCommandBufferStatusError) {
                    fprintf(stderr, "shader_record: frame %d failed: %s\n", frame,
                        command.error ? command.error.localizedDescription.UTF8String : "unknown error");
                    return 1;
                }

                char path[4096];
                snprintf(path, sizeof(path), "%s/frame_%04d.ppm", out_dir, frame);
                if (!flow_write_ppm(path, (const uint8_t *)readback.contents,
                                    width, height, bytes_per_row)) {
                    return 1;
                }
            }
        }
    }
    return 0;
}

int main(int argc, char **argv)
{
    if (argc < 4) {
        fprintf(stderr,
            "Usage: %s <file.metal> <fragment_entry> <out_dir> "
            "[width=640] [height=360] [frames=24] [fps=12]\n",
            argv[0]);
        return 1;
    }
    int width = argc > 4 ? atoi(argv[4]) : 640;
    int height = argc > 5 ? atoi(argv[5]) : 360;
    int frames = argc > 6 ? atoi(argv[6]) : 24;
    int fps = argc > 7 ? atoi(argv[7]) : 12;
    return flow_shader_record(argv[1], argv[2], argv[3], width, height, frames, fps);
}

#else

#include <stdio.h>
int main(void)
{
    fprintf(stderr, "shader_record: macOS/Metal only\n");
    return 2;
}

#endif
