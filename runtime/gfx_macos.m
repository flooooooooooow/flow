// Native macOS window + software 2D renderer for FLOW.
//
// This is an explicit backend for an explicit FLOW API:
// - create window
// - pump events
// - query key state
// - clear + filled rects into a pixel buffer
// - present
//
// Build (example):
//   clang -O2 prog.c runtime/gfx_macos.m -framework Cocoa -framework CoreGraphics -framework QuartzCore -o prog
//
// Pixel format: RGBA8 (bytes R,G,B,A).

#import <Cocoa/Cocoa.h>
#import <CoreGraphics/CoreGraphics.h>

typedef struct FlowGfxContext FlowGfxContext;
@class FlowGfxWindowDelegate;

#if __has_feature(objc_arc)
#define FLOW_RELEASE(obj) ((void)0)
#else
#define FLOW_RELEASE(obj) [obj release]
#endif

@interface FlowGfxView : NSView
@property(nonatomic, assign) FlowGfxContext* ctx;
@end

struct FlowGfxContext {
    NSWindow* window;
    FlowGfxView* view;
    FlowGfxWindowDelegate* delegate;
    int width;
    int height;
    uint8_t* pixels; // width*height*4 RGBA
    bool keys[256];  // macOS virtual keyCode state
    bool should_close;
};

static void flow_gfx_pump_events(FlowGfxContext* ctx) {
    @autoreleasepool {
        NSApplication* app = [NSApplication sharedApplication];
        for (;;) {
            NSEvent* event = [app nextEventMatchingMask:NSEventMaskAny
                                              untilDate:[NSDate distantPast]
                                                 inMode:NSDefaultRunLoopMode
                                                dequeue:YES];
            if (!event) break;
            [app sendEvent:event];
        }
        [app updateWindows];
    }
}

@implementation FlowGfxView

- (BOOL)acceptsFirstResponder { return YES; }

- (void)keyDown:(NSEvent*)event {
    unsigned short code = event.keyCode;
    if (code < 256) self.ctx->keys[code] = true;
}

- (void)keyUp:(NSEvent*)event {
    unsigned short code = event.keyCode;
    if (code < 256) self.ctx->keys[code] = false;
}

- (void)drawRect:(NSRect)dirtyRect {
    [super drawRect:dirtyRect];
    FlowGfxContext* ctx = self.ctx;
    if (!ctx || !ctx->pixels) return;

    CGColorSpaceRef cs = CGColorSpaceCreateDeviceRGB();
    CGContextRef cg = [[NSGraphicsContext currentContext] CGContext];
    if (!cg) { CGColorSpaceRelease(cs); return; }

    // Create a CGImage view of the pixel buffer and draw it.
    // This is simple and good enough for 2D UI + small games.
    size_t bytesPerRow = (size_t)ctx->width * 4;
    CGBitmapInfo info = kCGBitmapByteOrder32Big | kCGImageAlphaPremultipliedLast;

    CGContextRef bmp = CGBitmapContextCreate(ctx->pixels,
                                             (size_t)ctx->width,
                                             (size_t)ctx->height,
                                             8,
                                             bytesPerRow,
                                             cs,
                                             info);
    if (bmp) {
        CGImageRef img = CGBitmapContextCreateImage(bmp);
        if (img) {
            CGRect dst = CGRectMake(0, 0, ctx->width, ctx->height);
            CGContextDrawImage(cg, dst, img);
            CGImageRelease(img);
        }
        CGContextRelease(bmp);
    }
    CGColorSpaceRelease(cs);
}

@end

static void flow_gfx_request_close(FlowGfxContext* ctx, bool from_delegate) {
    if (!ctx) return;
    ctx->should_close = true;
    // Only call close if not already being called from windowWillClose delegate
    // to avoid infinite recursion
    if (!from_delegate && ctx->window) [ctx->window close];
}

@interface FlowGfxWindowDelegate : NSObject <NSWindowDelegate>
@property(nonatomic, assign) FlowGfxContext* ctx;
@end

@implementation FlowGfxWindowDelegate
- (void)windowWillClose:(NSNotification*)notification {
    flow_gfx_request_close(self.ctx, true);
}
@end

// ----------------- C API (called from generated C) -----------------

void* flow_gfx_init(int32_t w, int32_t h, const char* title_utf8) {
    @autoreleasepool {
        NSApplication* app = [NSApplication sharedApplication];
        [app setActivationPolicy:NSApplicationActivationPolicyRegular];

        FlowGfxContext* ctx = (FlowGfxContext*)calloc(1, sizeof(FlowGfxContext));
        ctx->width = (int)w;
        ctx->height = (int)h;
        ctx->pixels = (uint8_t*)calloc((size_t)w * (size_t)h * 4u, 1);

        NSString* title = title_utf8 ? [NSString stringWithUTF8String:title_utf8] : @"FLOW";
        NSRect frame = NSMakeRect(100, 100, w, h);
        NSUInteger style = NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskMiniaturizable;
        ctx->window = [[NSWindow alloc] initWithContentRect:frame
                                                  styleMask:style
                                                    backing:NSBackingStoreBuffered
                                                      defer:NO];
        [ctx->window setTitle:title];
        [ctx->window setReleasedWhenClosed:NO];

        ctx->view = [[FlowGfxView alloc] initWithFrame:frame];
        ctx->view.ctx = ctx;
        [ctx->window setContentView:ctx->view];
        [ctx->window makeFirstResponder:ctx->view];

        FlowGfxWindowDelegate* del = [[FlowGfxWindowDelegate alloc] init];
        del.ctx = ctx;
        ctx->delegate = del;
        [ctx->window setDelegate:del];

        [ctx->window makeKeyAndOrderFront:nil];
        [app activateIgnoringOtherApps:YES];

        return (void*)ctx;
    }
}

void flow_gfx_shutdown(void* handle) {
    @autoreleasepool {
        FlowGfxContext* ctx = (FlowGfxContext*)handle;
        if (!ctx) return;
        if (ctx->window) {
            if (ctx->delegate) {
                ctx->delegate.ctx = NULL;
            }
            [ctx->window setDelegate:nil];
            [ctx->window orderOut:nil];
            [ctx->window close];
        }
        if (ctx->view) {
            FLOW_RELEASE(ctx->view);
            ctx->view = nil;
        }
        if (ctx->delegate) {
            FLOW_RELEASE(ctx->delegate);
            ctx->delegate = nil;
        }
        if (ctx->window) {
            FLOW_RELEASE(ctx->window);
            ctx->window = nil;
        }
        free(ctx->pixels);
        free(ctx);
    }
}

int32_t flow_gfx_should_close(void* handle) {
    FlowGfxContext* ctx = (FlowGfxContext*)handle;
    if (!ctx) return 1;
    return ctx->should_close ? 1 : 0;
}

void flow_gfx_poll(void* handle) {
    FlowGfxContext* ctx = (FlowGfxContext*)handle;
    if (!ctx) return;
    flow_gfx_pump_events(ctx);
}

int32_t flow_gfx_key_down(void* handle, int32_t keycode) {
    FlowGfxContext* ctx = (FlowGfxContext*)handle;
    if (!ctx) return 0;
    if (keycode < 0 || keycode >= 256) return 0;
    return ctx->keys[keycode] ? 1 : 0;
}

void flow_gfx_clear(void* handle, uint8_t r, uint8_t g, uint8_t b) {
    FlowGfxContext* ctx = (FlowGfxContext*)handle;
    if (!ctx || !ctx->pixels) return;
    size_t n = (size_t)ctx->width * (size_t)ctx->height;
    uint8_t* p = ctx->pixels;
    for (size_t i = 0; i < n; i++) {
        p[i*4 + 0] = r;
        p[i*4 + 1] = g;
        p[i*4 + 2] = b;
        p[i*4 + 3] = 255;
    }
}

void flow_gfx_fill_rect(void* handle, int32_t x, int32_t y, int32_t w, int32_t h,
                        uint8_t r, uint8_t g, uint8_t b) {
    FlowGfxContext* ctx = (FlowGfxContext*)handle;
    if (!ctx || !ctx->pixels) return;
    if (w <= 0 || h <= 0) return;

    int x0 = x < 0 ? 0 : x;
    int y0 = y < 0 ? 0 : y;
    int x1 = x + w; if (x1 > ctx->width) x1 = ctx->width;
    int y1 = y + h; if (y1 > ctx->height) y1 = ctx->height;
    if (x0 >= x1 || y0 >= y1) return;

    uint8_t* p = ctx->pixels;
    for (int yy = y0; yy < y1; yy++) {
        for (int xx = x0; xx < x1; xx++) {
            size_t idx = ((size_t)yy * (size_t)ctx->width + (size_t)xx) * 4u;
            p[idx + 0] = r;
            p[idx + 1] = g;
            p[idx + 2] = b;
            p[idx + 3] = 255;
        }
    }
}

void flow_gfx_present(void* handle) {
    FlowGfxContext* ctx = (FlowGfxContext*)handle;
    if (!ctx || !ctx->view) return;
    @autoreleasepool {
        [ctx->view setNeedsDisplay:YES];
        [ctx->view displayIfNeeded];
    }
}

// User programs that call gfx_run / flow_gfx_run must define this symbol.
// Return 1 to continue, 0 to quit. Weak default keeps demos that only use
// gfx_frame_pump linkable without providing a frame callback.
__attribute__((weak)) int32_t flow_gfx_frame(void* handle, int32_t frame) {
    (void)handle;
    (void)frame;
    return 0;
}

int32_t flow_gfx_run(void* handle, int32_t max_frames) {
    if (!handle || max_frames <= 0) return 0;
    // KEY_ESC in lib/stdlib/gfx.flow
    const int32_t key_esc = 53;
    for (int32_t frame = 0; frame < max_frames; frame++) {
        flow_gfx_poll(handle);
        if (flow_gfx_should_close(handle)) return frame;
        if (flow_gfx_key_down(handle, key_esc)) return frame;
        if (!flow_gfx_frame(handle, frame)) return frame;
    }
    return max_frames;
}
