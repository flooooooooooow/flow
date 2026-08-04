/* FLOW fill-shader viewer — Metal + Cocoa (macOS). */
#ifdef __APPLE__

#import <Cocoa/Cocoa.h>
#import <Metal/Metal.h>
#import <QuartzCore/CAMetalLayer.h>
#include "shader_view_metal.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mach/mach_time.h>

typedef struct {
    float time;
    float width;
    float height;
} FlowShaderUniforms;

@interface FlowShaderView : NSView
@property(nonatomic, strong) id<MTLDevice> device;
@property(nonatomic, strong) id<MTLCommandQueue> queue;
@property(nonatomic, strong) id<MTLRenderPipelineState> pipeline;
@property(nonatomic, strong) CAMetalLayer *metalLayer;
@property(nonatomic, assign) BOOL running;
@property(nonatomic, assign) int32_t maxFrames;
@property(nonatomic, assign) int32_t frameCount;
@property(nonatomic, assign) uint64_t startAbs;
@end

@implementation FlowShaderView

- (instancetype)initWithFrame:(NSRect)frame
                       device:(id<MTLDevice>)device
                        queue:(id<MTLCommandQueue>)queue
                     pipeline:(id<MTLRenderPipelineState>)pipeline
                    maxFrames:(int32_t)maxFrames {
    self = [super initWithFrame:frame];
    if (self) {
        self.device = device;
        self.queue = queue;
        self.pipeline = pipeline;
        self.maxFrames = maxFrames;
        self.frameCount = 0;
        self.running = YES;
        self.startAbs = mach_absolute_time();
        self.wantsLayer = YES;
        CAMetalLayer *layer = [CAMetalLayer layer];
        layer.device = device;
        layer.pixelFormat = MTLPixelFormatBGRA8Unorm;
        layer.framebufferOnly = YES;
        layer.contentsScale = [[NSScreen mainScreen] backingScaleFactor];
        self.layer = layer;
        self.metalLayer = layer;
    }
    return self;
}

- (BOOL)acceptsFirstResponder {
    return YES;
}

- (void)keyDown:(NSEvent *)event {
    if (event.keyCode == 53) { /* Esc */
        self.running = NO;
        [self.window close];
    }
}

- (void)drawFrame {
    if (!self.running) {
        return;
    }
    CGSize size = self.metalLayer.drawableSize;
    if (size.width < 1 || size.height < 1) {
        CGFloat scale = self.metalLayer.contentsScale;
        self.metalLayer.drawableSize = CGSizeMake(self.bounds.size.width * scale,
                                                  self.bounds.size.height * scale);
        size = self.metalLayer.drawableSize;
    }

    id<CAMetalDrawable> drawable = [self.metalLayer nextDrawable];
    if (!drawable) {
        return;
    }

    mach_timebase_info_data_t info;
    mach_timebase_info(&info);
    uint64_t elapsed = mach_absolute_time() - self.startAbs;
    double seconds = (double)elapsed * (double)info.numer / (double)info.denom / 1.0e9;

    FlowShaderUniforms uniforms;
    uniforms.time = (float)seconds;
    uniforms.width = (float)size.width;
    uniforms.height = (float)size.height;

    MTLRenderPassDescriptor *pass = [MTLRenderPassDescriptor renderPassDescriptor];
    pass.colorAttachments[0].texture = drawable.texture;
    pass.colorAttachments[0].loadAction = MTLLoadActionClear;
    pass.colorAttachments[0].storeAction = MTLStoreActionStore;
    pass.colorAttachments[0].clearColor = MTLClearColorMake(0, 0, 0, 1);

    id<MTLCommandBuffer> cmd = [self.queue commandBuffer];
    id<MTLRenderCommandEncoder> enc = [cmd renderCommandEncoderWithDescriptor:pass];
    [enc setRenderPipelineState:self.pipeline];
    [enc setVertexBytes:&uniforms length:sizeof(uniforms) atIndex:0];
    [enc setFragmentBytes:&uniforms length:sizeof(uniforms) atIndex:0];
    [enc drawPrimitives:MTLPrimitiveTypeTriangle vertexStart:0 vertexCount:3];
    [enc endEncoding];
    [cmd presentDrawable:drawable];
    [cmd commit];

    self.frameCount += 1;
    if (self.maxFrames > 0 && self.frameCount >= self.maxFrames) {
        self.running = NO;
        [self.window close];
    }
}

@end

@interface FlowShaderAppDelegate : NSObject <NSApplicationDelegate, NSWindowDelegate>
@property(nonatomic, strong) FlowShaderView *view;
@property(nonatomic, strong) NSTimer *timer;
@property(nonatomic, assign) int result;
@end

@implementation FlowShaderAppDelegate
- (void)applicationDidFinishLaunching:(NSNotification *)notification {
    (void)notification;
}
- (BOOL)applicationShouldTerminateAfterLastWindowClosed:(NSApplication *)sender {
    (void)sender;
    return YES;
}
- (void)windowWillClose:(NSNotification *)notification {
    (void)notification;
    self.view.running = NO;
    [self.timer invalidate];
    self.timer = nil;
}
@end

static char *flow_read_file(const char *path, size_t *out_len) {
    FILE *f = fopen(path, "rb");
    if (!f) {
        return NULL;
    }
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    fseek(f, 0, SEEK_SET);
    if (n < 0) {
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
    if (out_len) {
        *out_len = (size_t)n;
    }
    return buf;
}

int flow_shader_show(
    const char *metal_source,
    const char *fragment_fn,
    int32_t width,
    int32_t height,
    int32_t max_frames
) {
    if (!metal_source || !fragment_fn || width <= 0 || height <= 0) {
        fprintf(stderr, "flow_shader_show: invalid arguments\n");
        return 1;
    }

    @autoreleasepool {
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (!device) {
            fprintf(stderr, "flow_shader_show: no Metal device\n");
            return 1;
        }
        id<MTLCommandQueue> queue = [device newCommandQueue];
        if (!queue) {
            fprintf(stderr, "flow_shader_show: no command queue\n");
            return 1;
        }

        NSError *error = nil;
        NSString *src = [NSString stringWithUTF8String:metal_source];
        id<MTLLibrary> lib = [device newLibraryWithSource:src options:nil error:&error];
        if (!lib) {
            fprintf(stderr, "flow_shader_show: Metal compile failed: %s\n",
                    error ? [[error localizedDescription] UTF8String] : "?");
            return 1;
        }

        id<MTLFunction> vert = [lib newFunctionWithName:@"flow_shader_vertex"];
        id<MTLFunction> frag = [lib newFunctionWithName:[NSString stringWithUTF8String:fragment_fn]];
        if (!vert || !frag) {
            fprintf(stderr, "flow_shader_show: missing vertex/fragment entry (%s)\n", fragment_fn);
            return 1;
        }

        MTLRenderPipelineDescriptor *desc = [[MTLRenderPipelineDescriptor alloc] init];
        desc.vertexFunction = vert;
        desc.fragmentFunction = frag;
        desc.colorAttachments[0].pixelFormat = MTLPixelFormatBGRA8Unorm;
        id<MTLRenderPipelineState> pipeline =
            [device newRenderPipelineStateWithDescriptor:desc error:&error];
        if (!pipeline) {
            fprintf(stderr, "flow_shader_show: pipeline error: %s\n",
                    error ? [[error localizedDescription] UTF8String] : "?");
            return 1;
        }

        [NSApplication sharedApplication];
        [NSApp setActivationPolicy:NSApplicationActivationPolicyRegular];

        FlowShaderAppDelegate *delegate = [[FlowShaderAppDelegate alloc] init];
        delegate.result = 0;
        [NSApp setDelegate:delegate];

        NSRect rect = NSMakeRect(100, 100, width, height);
        NSWindow *window = [[NSWindow alloc]
            initWithContentRect:rect
                      styleMask:(NSWindowStyleMaskTitled |
                                 NSWindowStyleMaskClosable |
                                 NSWindowStyleMaskMiniaturizable |
                                 NSWindowStyleMaskResizable)
                        backing:NSBackingStoreBuffered
                          defer:NO];
        [window setTitle:[NSString stringWithFormat:@"FLOW shader — %s", fragment_fn]];
        [window setReleasedWhenClosed:NO];

        FlowShaderView *view = [[FlowShaderView alloc] initWithFrame:rect
                                                              device:device
                                                               queue:queue
                                                            pipeline:pipeline
                                                           maxFrames:max_frames];
        window.contentView = view;
        window.delegate = delegate;
        delegate.view = view;
        [window makeKeyAndOrderFront:nil];
        [NSApp activateIgnoringOtherApps:YES];

        delegate.timer = [NSTimer scheduledTimerWithTimeInterval:1.0 / 60.0
                                                         repeats:YES
                                                           block:^(__unused NSTimer *t) {
                                                             [view drawFrame];
                                                             if (!view.running) {
                                                                 [NSApp stop:nil];
                                                             }
                                                           }];

        [NSApp run];
        return delegate.result;
    }
}

int flow_shader_show_file(
    const char *metal_path,
    const char *fragment_fn,
    int32_t width,
    int32_t height,
    int32_t max_frames
) {
    size_t n = 0;
    char *src = flow_read_file(metal_path, &n);
    if (!src) {
        fprintf(stderr, "flow_shader_show_file: cannot read %s\n", metal_path);
        return 1;
    }
    int rc = flow_shader_show(src, fragment_fn, width, height, max_frames);
    free(src);
    return rc;
}

#else /* !__APPLE__ */

#include "shader_view_metal.h"
#include <stdio.h>

int flow_shader_show(
    const char *metal_source,
    const char *fragment_fn,
    int32_t width,
    int32_t height,
    int32_t max_frames
) {
    (void)metal_source;
    (void)fragment_fn;
    (void)width;
    (void)height;
    (void)max_frames;
    fprintf(stderr, "flow_shader_show: Metal viewer is only available on macOS\n");
    return 1;
}

int flow_shader_show_file(
    const char *metal_path,
    const char *fragment_fn,
    int32_t width,
    int32_t height,
    int32_t max_frames
) {
    (void)metal_path;
    (void)fragment_fn;
    (void)width;
    (void)height;
    (void)max_frames;
    fprintf(stderr, "flow_shader_show_file: Metal viewer is only available on macOS\n");
    return 1;
}

#endif
