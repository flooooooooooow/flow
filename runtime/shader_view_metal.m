/* FLOW Shader Language viewer — Metal + Cocoa gallery. */
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
@property(nonatomic, strong) id<MTLLibrary> library;
@property(nonatomic, strong) NSArray<id<MTLRenderPipelineState>> *pipelines;
@property(nonatomic, strong) NSArray<NSString *> *entryNames;
@property(nonatomic, strong) CAMetalLayer *metalLayer;
@property(nonatomic, assign) NSInteger index;
@property(nonatomic, assign) BOOL running;
@property(nonatomic, assign) int32_t maxFrames;
@property(nonatomic, assign) int32_t frameCount;
@property(nonatomic, assign) uint64_t startAbs;
@property(nonatomic, weak) NSWindow *hostWindow;
- (void)setTitleForCurrent;
- (void)nextShader;
- (void)prevShader;
@end

@implementation FlowShaderView

- (instancetype)initWithFrame:(NSRect)frame
                       device:(id<MTLDevice>)device
                        queue:(id<MTLCommandQueue>)queue
                      library:(id<MTLLibrary>)library
                    pipelines:(NSArray *)pipelines
                   entryNames:(NSArray<NSString *> *)entryNames
                    maxFrames:(int32_t)maxFrames {
    self = [super initWithFrame:frame];
    if (self) {
        self.device = device;
        self.queue = queue;
        self.library = library;
        self.pipelines = pipelines;
        self.entryNames = entryNames;
        self.index = 0;
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

- (BOOL)acceptsFirstResponder { return YES; }

- (void)setTitleForCurrent {
    if (!self.hostWindow || self.entryNames.count == 0) return;
    NSString *name = self.entryNames[self.index];
    if ([name hasSuffix:@"_frag"]) {
        name = [name substringToIndex:name.length - 5];
    }
    self.hostWindow.title = [NSString stringWithFormat:
        @"FLOW shaders — %@  (%ld/%lu)  [←/→ or Space]",
        name, (long)self.index + 1, (unsigned long)self.entryNames.count];
}

- (void)nextShader {
    if (self.pipelines.count == 0) return;
    self.index = (self.index + 1) % (NSInteger)self.pipelines.count;
    self.startAbs = mach_absolute_time();
    [self setTitleForCurrent];
}

- (void)prevShader {
    if (self.pipelines.count == 0) return;
    self.index = (self.index - 1 + (NSInteger)self.pipelines.count) % (NSInteger)self.pipelines.count;
    self.startAbs = mach_absolute_time();
    [self setTitleForCurrent];
}

- (void)keyDown:(NSEvent *)event {
    NSString *chars = event.charactersIgnoringModifiers;
    if (event.keyCode == 53) { /* Esc */
        self.running = NO;
        [self.window close];
        return;
    }
    if (event.keyCode == 123) { /* left */
        [self prevShader];
        return;
    }
    if (event.keyCode == 124 || event.keyCode == 49) { /* right / space */
        [self nextShader];
        return;
    }
    if (chars.length == 1) {
        unichar c = [chars characterAtIndex:0];
        if (c >= '1' && c <= '9') {
            NSInteger idx = (NSInteger)(c - '1');
            if (idx < (NSInteger)self.pipelines.count) {
                self.index = idx;
                self.startAbs = mach_absolute_time();
                [self setTitleForCurrent];
            }
        }
    }
}

- (void)drawFrame {
    if (!self.running || self.pipelines.count == 0) return;

    CGSize size = self.metalLayer.drawableSize;
    if (size.width < 1 || size.height < 1) {
        CGFloat scale = self.metalLayer.contentsScale;
        self.metalLayer.drawableSize = CGSizeMake(self.bounds.size.width * scale,
                                                  self.bounds.size.height * scale);
        size = self.metalLayer.drawableSize;
    }

    id<CAMetalDrawable> drawable = [self.metalLayer nextDrawable];
    if (!drawable) return;

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

    id<MTLRenderPipelineState> pipeline = self.pipelines[self.index];
    id<MTLCommandBuffer> cmd = [self.queue commandBuffer];
    id<MTLRenderCommandEncoder> enc = [cmd renderCommandEncoderWithDescriptor:pass];
    [enc setRenderPipelineState:pipeline];
    [enc setVertexBytes:&uniforms length:sizeof(uniforms) atIndex:0];
    [enc setFragmentBytes:&uniforms length:sizeof(uniforms) atIndex:0];
    [enc drawPrimitives:MTLPrimitiveTypeTriangle vertexStart:0 vertexCount:3];
    [enc endEncoding];
    [cmd presentDrawable:drawable];
    [cmd commit];

    self.frameCount += 1;
    if (self.maxFrames > 0 && self.frameCount >= self.maxFrames) {
        self.running = NO;
        [NSApp stop:nil];
        /* NSApp stop needs a queued event before the run loop actually exits. */
        NSEvent *ev = [NSEvent otherEventWithType:NSEventTypeApplicationDefined
                                         location:NSZeroPoint
                                    modifierFlags:0
                                        timestamp:0
                                     windowNumber:0
                                          context:nil
                                          subtype:0
                                            data1:0
                                            data2:0];
        [NSApp postEvent:ev atStart:YES];
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
    if (!f) return NULL;
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    fseek(f, 0, SEEK_SET);
    if (n < 0) { fclose(f); return NULL; }
    char *buf = (char *)malloc((size_t)n + 1);
    if (!buf) { fclose(f); return NULL; }
    if (fread(buf, 1, (size_t)n, f) != (size_t)n) {
        free(buf); fclose(f); return NULL;
    }
    buf[n] = '\0';
    fclose(f);
    if (out_len) *out_len = (size_t)n;
    return buf;
}

static int flow_shader_show_impl(
    const char *metal_source,
    const char **fragment_fns,
    int32_t fragment_count,
    int32_t width,
    int32_t height,
    int32_t max_frames
) {
    if (!metal_source || !fragment_fns || fragment_count <= 0 || width <= 0 || height <= 0) {
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
        NSError *error = nil;
        NSString *src = [NSString stringWithUTF8String:metal_source];
        id<MTLLibrary> lib = [device newLibraryWithSource:src options:nil error:&error];
        if (!lib) {
            fprintf(stderr, "flow_shader_show: Metal compile failed: %s\n",
                    error ? [[error localizedDescription] UTF8String] : "?");
            return 1;
        }

        id<MTLFunction> vert = [lib newFunctionWithName:@"flow_shader_vertex"];
        if (!vert) {
            fprintf(stderr, "flow_shader_show: missing flow_shader_vertex\n");
            return 1;
        }

        NSMutableArray *pipelines = [NSMutableArray array];
        NSMutableArray<NSString *> *names = [NSMutableArray array];
        for (int i = 0; i < fragment_count; i++) {
            NSString *fname = [NSString stringWithUTF8String:fragment_fns[i]];
            id<MTLFunction> frag = [lib newFunctionWithName:fname];
            if (!frag) {
                fprintf(stderr, "flow_shader_show: missing fragment %s\n", fragment_fns[i]);
                return 1;
            }
            MTLRenderPipelineDescriptor *desc = [[MTLRenderPipelineDescriptor alloc] init];
            desc.vertexFunction = vert;
            desc.fragmentFunction = frag;
            desc.colorAttachments[0].pixelFormat = MTLPixelFormatBGRA8Unorm;
            id<MTLRenderPipelineState> pso =
                [device newRenderPipelineStateWithDescriptor:desc error:&error];
            if (!pso) {
                fprintf(stderr, "flow_shader_show: pipeline error for %s: %s\n",
                        fragment_fns[i],
                        error ? [[error localizedDescription] UTF8String] : "?");
                return 1;
            }
            [pipelines addObject:pso];
            [names addObject:fname];
        }

        [NSApplication sharedApplication];
        [NSApp setActivationPolicy:NSApplicationActivationPolicyRegular];

        FlowShaderAppDelegate *delegate = [[FlowShaderAppDelegate alloc] init];
        [NSApp setDelegate:delegate];

        NSRect rect = NSMakeRect(80, 80, width, height);
        NSWindow *window = [[NSWindow alloc]
            initWithContentRect:rect
                      styleMask:(NSWindowStyleMaskTitled |
                                 NSWindowStyleMaskClosable |
                                 NSWindowStyleMaskMiniaturizable |
                                 NSWindowStyleMaskResizable)
                        backing:NSBackingStoreBuffered
                          defer:NO];
        [window setReleasedWhenClosed:NO];

        FlowShaderView *view = [[FlowShaderView alloc] initWithFrame:rect
                                                              device:device
                                                               queue:queue
                                                            library:lib
                                                          pipelines:pipelines
                                                         entryNames:names
                                                          maxFrames:max_frames];
        view.hostWindow = window;
        window.contentView = view;
        window.delegate = delegate;
        delegate.view = view;
        [view setTitleForCurrent];
        [window makeKeyAndOrderFront:nil];
        [NSApp activateIgnoringOtherApps:YES];

        delegate.timer = [NSTimer timerWithTimeInterval:1.0 / 60.0
                                                repeats:YES
                                                  block:^(__unused NSTimer *t) {
                                                    [view drawFrame];
                                                  }];
        [[NSRunLoop mainRunLoop] addTimer:delegate.timer forMode:NSRunLoopCommonModes];
        [NSApp run];
        [delegate.timer invalidate];
        return 0;
    }
}

int flow_shader_show(
    const char *metal_source,
    const char *fragment_fn,
    int32_t width,
    int32_t height,
    int32_t max_frames
) {
    const char *fns[1] = { fragment_fn };
    return flow_shader_show_impl(metal_source, fns, 1, width, height, max_frames);
}

int flow_shader_show_gallery(
    const char *metal_source,
    const char **fragment_fns,
    int32_t fragment_count,
    int32_t width,
    int32_t height,
    int32_t max_frames
) {
    return flow_shader_show_impl(
        metal_source, fragment_fns, fragment_count, width, height, max_frames
    );
}

int flow_shader_show_file(
    const char *metal_path,
    const char *fragment_fn,
    int32_t width,
    int32_t height,
    int32_t max_frames
) {
    char *src = flow_read_file(metal_path, NULL);
    if (!src) {
        fprintf(stderr, "flow_shader_show_file: cannot read %s\n", metal_path);
        return 1;
    }
    int rc = flow_shader_show(src, fragment_fn, width, height, max_frames);
    free(src);
    return rc;
}

int flow_shader_show_gallery_file(
    const char *metal_path,
    const char *entries_path,
    int32_t width,
    int32_t height,
    int32_t max_frames
) {
    char *src = flow_read_file(metal_path, NULL);
    if (!src) {
        fprintf(stderr, "flow_shader_show_gallery_file: cannot read %s\n", metal_path);
        return 1;
    }
    char *entries_raw = flow_read_file(entries_path, NULL);
    if (!entries_raw) {
        free(src);
        fprintf(stderr, "flow_shader_show_gallery_file: cannot read %s\n", entries_path);
        return 1;
    }

    const char *fns[64];
    char *dup = entries_raw;
    int count = 0;
    char *line = strtok(dup, "\n");
    while (line && count < 64) {
        while (*line == ' ' || *line == '\t') line++;
        size_t n = strlen(line);
        while (n > 0 && (line[n - 1] == '\r' || line[n - 1] == ' ')) {
            line[--n] = '\0';
        }
        if (n > 0) {
            fns[count++] = line;
        }
        line = strtok(NULL, "\n");
    }
    if (count == 0) {
        free(src);
        free(entries_raw);
        fprintf(stderr, "flow_shader_show_gallery_file: no entries\n");
        return 1;
    }
    int rc = flow_shader_show_gallery(src, fns, count, width, height, max_frames);
    free(src);
    free(entries_raw);
    return rc;
}

#else /* !__APPLE__ */

#include "shader_view_metal.h"
#include <stdio.h>

int flow_shader_show(const char *a, const char *b, int32_t c, int32_t d, int32_t e) {
    (void)a;(void)b;(void)c;(void)d;(void)e;
    fprintf(stderr, "flow_shader_show: macOS/Metal only\n");
    return 1;
}
int flow_shader_show_gallery(const char *a, const char **b, int32_t c, int32_t d, int32_t e, int32_t f) {
    (void)a;(void)b;(void)c;(void)d;(void)e;(void)f;
    fprintf(stderr, "flow_shader_show_gallery: macOS/Metal only\n");
    return 1;
}
int flow_shader_show_file(const char *a, const char *b, int32_t c, int32_t d, int32_t e) {
    (void)a;(void)b;(void)c;(void)d;(void)e;
    fprintf(stderr, "flow_shader_show_file: macOS/Metal only\n");
    return 1;
}
int flow_shader_show_gallery_file(const char *a, const char *b, int32_t c, int32_t d, int32_t e) {
    (void)a;(void)b;(void)c;(void)d;(void)e;
    fprintf(stderr, "flow_shader_show_gallery_file: macOS/Metal only\n");
    return 1;
}

#endif
