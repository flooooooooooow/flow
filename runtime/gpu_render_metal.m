/* Metal host for Flow render jobs (#811).
 *
 * A Flow program built with lib/stdlib/gpu_render.flow writes a job
 * directory: job.txt (one command per line), the Metal and WGSL shaders
 * that the Flow program emitted, and raw buffer and texture blobs. This
 * host replays the job on the system Metal device, offscreen, and writes
 * the output texture as tightly packed RGBA8 bytes. The WebGPU host
 * (tools/gpu_render/webgpu_host.mjs) replays the same job. Neither host
 * carries shader source of its own.
 *
 * Build on macOS:
 *   xcrun clang -O2 -fobjc-arc runtime/gpu_render_metal.m \
 *     -framework Metal -framework Foundation -o build/gpu_render/gpu_render_metal
 *
 * Run:
 *   build/gpu_render/gpu_render_metal JOBDIR OUT.rgba
 *
 * Exit codes: 0 rendered, 1 job or device error, 3 no Metal device.
 *
 * Binding model, shared with the WGSL emitter: uniforms are buffer(0) in
 * both stages; texture slot s is texture(s) and sampler(s); vertex buffer
 * slot k is buffer(16 + k). Winding is counter-clockwise, as in WebGPU.
 */
#ifdef __APPLE__

#import <Foundation/Foundation.h>
#import <Metal/Metal.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { USE_SAMPLED = 1, USE_STORAGE = 2, USE_COLOR = 4, USE_DEPTH = 8 };
enum { VBUF_BASE = 16 };

static int g_failed = 0;

static void fail(NSString *msg)
{
    fprintf(stderr, "gpu_render_metal: %s\n", msg.UTF8String);
    g_failed = 1;
}

@interface FlowPipe : NSObject
@property NSString *shader;
@property NSString *topology, *cull, *depth, *blend, *colorFmt;
@property int samples;
@property BOOL hasDepth;
@property MTLVertexDescriptor *vdesc;
@property BOOL anyAttr;
@property id<MTLRenderPipelineState> state;
@property id<MTLDepthStencilState> dss;
@end
@implementation FlowPipe
@end

@interface FlowTex : NSObject
@property id<MTLTexture> tex;
@property NSString *fmt;
@property int w, h;
@end
@implementation FlowTex
@end

@interface FlowGroup : NSObject
@property NSString *uniform;
@property NSMutableArray *tex; /* of @[slot, tex, smp] */
@end
@implementation FlowGroup
@end

@interface FlowDraw : NSObject
@property NSString *pipe, *group, *ibuf, *ifmt;
@property int count, instances, first, baseVertex, firstInstance;
@property NSArray *vbs;
@end
@implementation FlowDraw
@end

@interface FlowPass : NSObject
@property NSString *color, *resolve, *depth, *load;
@property double r, g, b, a, depthClear;
@property NSMutableArray *draws;
@end
@implementation FlowPass
@end

static MTLPixelFormat pixel_format(NSString *f)
{
    if ([f isEqualToString:@"rgba8"]) return MTLPixelFormatRGBA8Unorm;
    if ([f isEqualToString:@"rgba16f"]) return MTLPixelFormatRGBA16Float;
    if ([f isEqualToString:@"depth32f"]) return MTLPixelFormatDepth32Float;
    return MTLPixelFormatInvalid;
}

static int render_job(const char *dir_c, const char *out_c)
{
    NSString *dir = [NSString stringWithUTF8String:dir_c];
    NSError *error = nil;
    NSString *text = [NSString stringWithContentsOfFile:[dir stringByAppendingPathComponent:@"job.txt"]
                                               encoding:NSUTF8StringEncoding error:&error];
    if (!text) { fail(@"cannot read job.txt"); return 1; }

    id<MTLDevice> device = MTLCreateSystemDefaultDevice();
    if (!device) {
        fprintf(stderr, "gpu_render_metal: no Metal device\n");
        return 3;
    }
    id<MTLCommandQueue> queue = [device newCommandQueue];

    NSMutableDictionary *buffers = [NSMutableDictionary dictionary];
    NSMutableDictionary *textures = [NSMutableDictionary dictionary];
    NSMutableDictionary *samplers = [NSMutableDictionary dictionary];
    NSMutableDictionary *libraries = [NSMutableDictionary dictionary];
    NSMutableDictionary *pipes = [NSMutableDictionary dictionary];
    NSMutableDictionary *groups = [NSMutableDictionary dictionary];
    NSMutableArray *passes = [NSMutableArray array];
    NSString *output = nil;
    int width = 0, height = 0;

    NSArray *lines = [text componentsSeparatedByString:@"\n"];
    BOOL first = YES;
    for (NSString *raw in lines) {
        NSString *line = [raw stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceCharacterSet]];
        if (line.length == 0 || [line hasPrefix:@"#"]) continue;
        if (first) {
            if (![line isEqualToString:@"flowjob 1"]) { fail(@"not a flowjob 1 file"); return 1; }
            first = NO;
            continue;
        }
        NSMutableArray *c = [NSMutableArray array];
        for (NSString *t in [line componentsSeparatedByCharactersInSet:[NSCharacterSet whitespaceCharacterSet]]) {
            if (t.length) [c addObject:t];
        }
        NSString *op = c[0];
        if ([op isEqualToString:@"size"]) {
            width = [c[1] intValue];
            height = [c[2] intValue];
        } else if ([op isEqualToString:@"buffer"]) {
            NSData *data = [NSData dataWithContentsOfFile:[dir stringByAppendingPathComponent:c[2]]];
            if (!data || (int)data.length != [c[3] intValue]) {
                fail([NSString stringWithFormat:@"buffer %@ missing or wrong size", c[1]]);
                return 1;
            }
            NSUInteger len = data.length < 16 ? 16 : data.length;
            id<MTLBuffer> b = [device newBufferWithLength:len options:MTLResourceStorageModeShared];
            memcpy(b.contents, data.bytes, data.length);
            buffers[c[1]] = b;
        } else if ([op isEqualToString:@"texture"]) {
            NSString *dim = c[2], *fmt = c[3], *file = c[9];
            int w = [c[4] intValue], h = [c[5] intValue], layers = [c[6] intValue];
            int samples = [c[7] intValue], bits = [c[8] intValue];
            MTLTextureDescriptor *td = [[MTLTextureDescriptor alloc] init];
            td.pixelFormat = pixel_format(fmt);
            if (td.pixelFormat == MTLPixelFormatInvalid) { fail(@"unknown texture format"); return 1; }
            td.width = (NSUInteger)w;
            td.height = (NSUInteger)h;
            if ([dim isEqualToString:@"cube"]) {
                td.textureType = MTLTextureTypeCube;
                if (layers != 6) { fail(@"cube textures have six layers"); return 1; }
            } else if (samples > 1) {
                td.textureType = MTLTextureType2DMultisample;
                td.sampleCount = (NSUInteger)samples;
            } else if (layers > 1) {
                td.textureType = MTLTextureType2DArray;
                td.arrayLength = (NSUInteger)layers;
            } else {
                td.textureType = MTLTextureType2D;
            }
            MTLTextureUsage usage = 0;
            if (bits & USE_SAMPLED) usage |= MTLTextureUsageShaderRead;
            if (bits & USE_STORAGE) usage |= MTLTextureUsageShaderRead | MTLTextureUsageShaderWrite;
            if (bits & (USE_COLOR | USE_DEPTH)) usage |= MTLTextureUsageRenderTarget;
            td.usage = usage;
            BOOL priv = samples > 1 || [fmt isEqualToString:@"depth32f"];
            td.storageMode = priv ? MTLStorageModePrivate : MTLStorageModeShared;
            id<MTLTexture> tex = [device newTextureWithDescriptor:td];
            if (!tex) { fail(@"cannot allocate texture"); return 1; }
            if (![file isEqualToString:@"-"]) {
                NSData *data = [NSData dataWithContentsOfFile:[dir stringByAppendingPathComponent:file]];
                NSUInteger bpp = [fmt isEqualToString:@"rgba16f"] ? 8 : 4;
                NSUInteger face = (NSUInteger)w * (NSUInteger)h * bpp;
                if (!data || data.length != face * (NSUInteger)layers) {
                    fail([NSString stringWithFormat:@"texture %@ data missing or wrong size", c[1]]);
                    return 1;
                }
                for (int s = 0; s < layers; s++) {
                    [tex replaceRegion:MTLRegionMake2D(0, 0, (NSUInteger)w, (NSUInteger)h)
                           mipmapLevel:0
                                 slice:(NSUInteger)s
                             withBytes:(const uint8_t *)data.bytes + face * (NSUInteger)s
                           bytesPerRow:(NSUInteger)w * bpp
                         bytesPerImage:face];
                }
            }
            FlowTex *ft = [[FlowTex alloc] init];
            ft.tex = tex;
            ft.fmt = fmt;
            ft.w = w;
            ft.h = h;
            textures[c[1]] = ft;
        } else if ([op isEqualToString:@"sampler"]) {
            MTLSamplerDescriptor *sd = [[MTLSamplerDescriptor alloc] init];
            sd.minFilter = [c[2] isEqualToString:@"linear"] ? MTLSamplerMinMagFilterLinear : MTLSamplerMinMagFilterNearest;
            sd.magFilter = [c[3] isEqualToString:@"linear"] ? MTLSamplerMinMagFilterLinear : MTLSamplerMinMagFilterNearest;
            MTLSamplerAddressMode m[3];
            for (int i = 0; i < 3; i++) {
                m[i] = [c[4 + i] isEqualToString:@"repeat"] ? MTLSamplerAddressModeRepeat : MTLSamplerAddressModeClampToEdge;
            }
            sd.sAddressMode = m[0];
            sd.tAddressMode = m[1];
            sd.rAddressMode = m[2];
            samplers[c[1]] = [device newSamplerStateWithDescriptor:sd];
        } else if ([op isEqualToString:@"shader"]) {
            NSString *src = [NSString stringWithContentsOfFile:[dir stringByAppendingPathComponent:c[3]]
                                                      encoding:NSUTF8StringEncoding error:&error];
            if (!src) { fail(@"cannot read Metal shader"); return 1; }
            id<MTLLibrary> lib = [device newLibraryWithSource:src options:nil error:&error];
            if (!lib) {
                fail([NSString stringWithFormat:@"Metal compile failed (%@): %@", c[3],
                      error ? error.localizedDescription : @"unknown"]);
                return 1;
            }
            libraries[c[1]] = lib;
        } else if ([op isEqualToString:@"pipeline"]) {
            FlowPipe *p = [[FlowPipe alloc] init];
            p.shader = c[2];
            p.topology = c[3];
            p.cull = c[4];
            p.depth = c[5];
            p.blend = c[6];
            p.samples = [c[7] intValue];
            p.colorFmt = c[8];
            p.hasDepth = [c[9] isEqualToString:@"1"];
            p.vdesc = [MTLVertexDescriptor vertexDescriptor];
            pipes[c[1]] = p;
        } else if ([op isEqualToString:@"vbuf"]) {
            FlowPipe *p = pipes[c[1]];
            NSUInteger idx = VBUF_BASE + (NSUInteger)[c[2] intValue];
            p.vdesc.layouts[idx].stride = (NSUInteger)[c[3] intValue];
            p.vdesc.layouts[idx].stepFunction = [c[4] isEqualToString:@"instance"]
                ? MTLVertexStepFunctionPerInstance : MTLVertexStepFunctionPerVertex;
            p.vdesc.layouts[idx].stepRate = 1;
        } else if ([op isEqualToString:@"vattr"]) {
            FlowPipe *p = pipes[c[1]];
            NSUInteger loc = (NSUInteger)[c[3] intValue];
            int n = [[c[4] substringFromIndex:4] intValue];
            MTLVertexFormat f = n == 1 ? MTLVertexFormatFloat : n == 2 ? MTLVertexFormatFloat2
                : n == 3 ? MTLVertexFormatFloat3 : MTLVertexFormatFloat4;
            p.vdesc.attributes[loc].format = f;
            p.vdesc.attributes[loc].offset = (NSUInteger)[c[5] intValue];
            p.vdesc.attributes[loc].bufferIndex = VBUF_BASE + (NSUInteger)[c[2] intValue];
            p.anyAttr = YES;
        } else if ([op isEqualToString:@"pbind"]) {
            /* Metal binds by index; the WGSL layout needs these, Metal does not. */
        } else if ([op isEqualToString:@"group"]) {
            FlowGroup *g = [[FlowGroup alloc] init];
            g.uniform = c[3];
            g.tex = [NSMutableArray array];
            groups[c[1]] = g;
        } else if ([op isEqualToString:@"gtex"]) {
            FlowGroup *g = groups[c[1]];
            [g.tex addObject:@[ c[2], c[3], c[4] ]];
        } else if ([op isEqualToString:@"pass"]) {
            FlowPass *p = [[FlowPass alloc] init];
            p.color = c[1];
            p.resolve = c[2];
            p.depth = c[3];
            p.load = c[4];
            p.r = [c[5] doubleValue];
            p.g = [c[6] doubleValue];
            p.b = [c[7] doubleValue];
            p.a = [c[8] doubleValue];
            p.depthClear = [c[9] doubleValue];
            p.draws = [NSMutableArray array];
            [passes addObject:p];
        } else if ([op isEqualToString:@"bundle-begin"] || [op isEqualToString:@"bundle-end"]) {
            /* A WebGPU render bundle; Metal encodes the same draws directly. */
        } else if ([op isEqualToString:@"draw"]) {
            FlowDraw *d = [[FlowDraw alloc] init];
            d.pipe = c[1];
            d.group = c[2];
            d.ibuf = c[3];
            d.ifmt = c[4];
            d.count = [c[5] intValue];
            d.instances = [c[6] intValue];
            d.first = [c[7] intValue];
            d.baseVertex = [c[8] intValue];
            d.firstInstance = [c[9] intValue];
            d.vbs = [c subarrayWithRange:NSMakeRange(10, c.count - 10)];
            FlowPass *pass = passes.lastObject;
            if (!pass) { fail(@"draw before pass"); return 1; }
            [pass.draws addObject:d];
        } else if ([op isEqualToString:@"output"]) {
            output = c[1];
        } else {
            fail([NSString stringWithFormat:@"unknown command %@", op]);
            return 1;
        }
    }

    /* Build pipeline states. */
    for (NSString *pid in pipes) {
        FlowPipe *p = pipes[pid];
        id<MTLLibrary> lib = libraries[p.shader];
        MTLRenderPipelineDescriptor *rd = [[MTLRenderPipelineDescriptor alloc] init];
        rd.vertexFunction = [lib newFunctionWithName:@"vs_main"];
        rd.fragmentFunction = [lib newFunctionWithName:@"fs_main"];
        if (!rd.vertexFunction || !rd.fragmentFunction) { fail(@"missing vs_main or fs_main"); return 1; }
        if (p.anyAttr) rd.vertexDescriptor = p.vdesc;
        rd.rasterSampleCount = (NSUInteger)p.samples;
        rd.colorAttachments[0].pixelFormat = pixel_format(p.colorFmt);
        if ([p.blend isEqualToString:@"alpha"]) {
            rd.colorAttachments[0].blendingEnabled = YES;
            rd.colorAttachments[0].sourceRGBBlendFactor = MTLBlendFactorSourceAlpha;
            rd.colorAttachments[0].destinationRGBBlendFactor = MTLBlendFactorOneMinusSourceAlpha;
            rd.colorAttachments[0].sourceAlphaBlendFactor = MTLBlendFactorOne;
            rd.colorAttachments[0].destinationAlphaBlendFactor = MTLBlendFactorOneMinusSourceAlpha;
        } else if ([p.blend isEqualToString:@"add"]) {
            rd.colorAttachments[0].blendingEnabled = YES;
            rd.colorAttachments[0].sourceRGBBlendFactor = MTLBlendFactorOne;
            rd.colorAttachments[0].destinationRGBBlendFactor = MTLBlendFactorOne;
            rd.colorAttachments[0].sourceAlphaBlendFactor = MTLBlendFactorOne;
            rd.colorAttachments[0].destinationAlphaBlendFactor = MTLBlendFactorOne;
        }
        if (p.hasDepth) rd.depthAttachmentPixelFormat = MTLPixelFormatDepth32Float;
        rd.inputPrimitiveTopology = [p.topology isEqualToString:@"line"]
            ? MTLPrimitiveTopologyClassLine : MTLPrimitiveTopologyClassTriangle;
        p.state = [device newRenderPipelineStateWithDescriptor:rd error:&error];
        if (!p.state) {
            fail([NSString stringWithFormat:@"pipeline %@ failed: %@", pid,
                  error ? error.localizedDescription : @"unknown"]);
            return 1;
        }
        if (p.hasDepth) {
            MTLDepthStencilDescriptor *dd = [[MTLDepthStencilDescriptor alloc] init];
            dd.depthCompareFunction = [p.depth isEqualToString:@"none"] ? MTLCompareFunctionAlways : MTLCompareFunctionLess;
            dd.depthWriteEnabled = [p.depth isEqualToString:@"write"];
            p.dss = [device newDepthStencilStateWithDescriptor:dd];
        }
    }

    id<MTLCommandBuffer> cmd = [queue commandBuffer];
    for (FlowPass *pass in passes) {
        FlowTex *color = textures[pass.color];
        if (!color) { fail(@"pass color texture missing"); return 1; }
        MTLRenderPassDescriptor *rp = [MTLRenderPassDescriptor renderPassDescriptor];
        rp.colorAttachments[0].texture = color.tex;
        rp.colorAttachments[0].loadAction = [pass.load isEqualToString:@"load"] ? MTLLoadActionLoad : MTLLoadActionClear;
        rp.colorAttachments[0].clearColor = MTLClearColorMake(pass.r, pass.g, pass.b, pass.a);
        if (![pass.resolve isEqualToString:@"-"]) {
            rp.colorAttachments[0].resolveTexture = ((FlowTex *)textures[pass.resolve]).tex;
            rp.colorAttachments[0].storeAction = MTLStoreActionStoreAndMultisampleResolve;
        } else {
            rp.colorAttachments[0].storeAction = MTLStoreActionStore;
        }
        if (![pass.depth isEqualToString:@"-"]) {
            rp.depthAttachment.texture = ((FlowTex *)textures[pass.depth]).tex;
            rp.depthAttachment.loadAction = MTLLoadActionClear;
            rp.depthAttachment.storeAction = MTLStoreActionStore;
            rp.depthAttachment.clearDepth = pass.depthClear;
        }
        id<MTLRenderCommandEncoder> enc = [cmd renderCommandEncoderWithDescriptor:rp];
        [enc setFrontFacingWinding:MTLWindingCounterClockwise];
        for (FlowDraw *d in pass.draws) {
            FlowPipe *p = pipes[d.pipe];
            if (!p) { fail(@"draw names an unknown pipeline"); return 1; }
            [enc setRenderPipelineState:p.state];
            if (p.dss) [enc setDepthStencilState:p.dss];
            MTLCullMode cull = MTLCullModeNone;
            if ([p.cull isEqualToString:@"back"]) cull = MTLCullModeBack;
            if ([p.cull isEqualToString:@"front"]) cull = MTLCullModeFront;
            [enc setCullMode:cull];
            if (![d.group isEqualToString:@"-"]) {
                FlowGroup *g = groups[d.group];
                if (![g.uniform isEqualToString:@"-"]) {
                    id<MTLBuffer> ub = buffers[g.uniform];
                    [enc setVertexBuffer:ub offset:0 atIndex:0];
                    [enc setFragmentBuffer:ub offset:0 atIndex:0];
                }
                for (NSArray *t in g.tex) {
                    NSUInteger slot = (NSUInteger)[t[0] intValue];
                    id<MTLTexture> tex = ((FlowTex *)textures[t[1]]).tex;
                    id<MTLSamplerState> smp = samplers[t[2]];
                    [enc setVertexTexture:tex atIndex:slot];
                    [enc setFragmentTexture:tex atIndex:slot];
                    [enc setVertexSamplerState:smp atIndex:slot];
                    [enc setFragmentSamplerState:smp atIndex:slot];
                }
            }
            for (NSUInteger k = 0; k < d.vbs.count; k++) {
                [enc setVertexBuffer:buffers[d.vbs[k]] offset:0 atIndex:VBUF_BASE + k];
            }
            MTLPrimitiveType prim = [p.topology isEqualToString:@"line"] ? MTLPrimitiveTypeLine : MTLPrimitiveTypeTriangle;
            if (![d.ibuf isEqualToString:@"-"]) {
                BOOL u16 = [d.ifmt isEqualToString:@"u16"];
                [enc drawIndexedPrimitives:prim
                                indexCount:(NSUInteger)d.count
                                 indexType:u16 ? MTLIndexTypeUInt16 : MTLIndexTypeUInt32
                               indexBuffer:buffers[d.ibuf]
                         indexBufferOffset:(NSUInteger)d.first * (u16 ? 2 : 4)
                             instanceCount:(NSUInteger)d.instances
                                baseVertex:d.baseVertex
                              baseInstance:(NSUInteger)d.firstInstance];
            } else {
                [enc drawPrimitives:prim
                        vertexStart:(NSUInteger)d.first
                        vertexCount:(NSUInteger)d.count
                      instanceCount:(NSUInteger)d.instances
                       baseInstance:(NSUInteger)d.firstInstance];
            }
        }
        [enc endEncoding];
    }

    FlowTex *out = output ? textures[output] : nil;
    if (!out || ![out.fmt isEqualToString:@"rgba8"]) { fail(@"output must name an rgba8 texture"); return 1; }
    if (width && (out.w != width || out.h != height)) { fail(@"output size differs from job size"); return 1; }
    NSUInteger row = (NSUInteger)out.w * 4;
    NSUInteger padded = (row + 255u) & ~(NSUInteger)255u;
    id<MTLBuffer> readback = [device newBufferWithLength:padded * (NSUInteger)out.h options:MTLResourceStorageModeShared];
    id<MTLBlitCommandEncoder> blit = [cmd blitCommandEncoder];
    [blit copyFromTexture:out.tex
              sourceSlice:0
              sourceLevel:0
             sourceOrigin:MTLOriginMake(0, 0, 0)
               sourceSize:MTLSizeMake((NSUInteger)out.w, (NSUInteger)out.h, 1)
                 toBuffer:readback
        destinationOffset:0
   destinationBytesPerRow:padded
 destinationBytesPerImage:padded * (NSUInteger)out.h];
    [blit endEncoding];
    [cmd commit];
    [cmd waitUntilCompleted];
    if (cmd.status == MTLCommandBufferStatusError) {
        fail([NSString stringWithFormat:@"command buffer failed: %@",
              cmd.error ? cmd.error.localizedDescription : @"unknown"]);
        return 1;
    }
    FILE *f = fopen(out_c, "wb");
    if (!f) { fail(@"cannot write output"); return 1; }
    const uint8_t *src = (const uint8_t *)readback.contents;
    for (int y = 0; y < out.h; y++) {
        if (fwrite(src + padded * (NSUInteger)y, 1, row, f) != row) {
            fclose(f);
            fail(@"short write");
            return 1;
        }
    }
    fclose(f);
    printf("gpu_render_metal: rendered %dx%d on %s\n", out.w, out.h, device.name.UTF8String);
    return g_failed;
}

int main(int argc, char **argv)
{
    if (argc != 3) {
        fprintf(stderr, "usage: gpu_render_metal JOBDIR OUT.rgba\n");
        return 1;
    }
    @autoreleasepool {
        return render_job(argv[1], argv[2]);
    }
}

#else

#include <stdio.h>

int main(void)
{
    fprintf(stderr, "gpu_render_metal: Metal is only available on macOS\n");
    return 3;
}

#endif
