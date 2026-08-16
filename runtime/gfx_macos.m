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

    // Pointer state, in framebuffer coordinates (y down from the top row).
    int32_t mouse_x;
    int32_t mouse_y;
    bool mouse_left;
    bool mouse_right;
    bool mouse_middle;
    int32_t mouse_wheel;  // cumulative signed total, never reset by a read
    bool mouse_inside;
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

/* Modifier keys arrive through flagsChanged:, not keyDown:, so without this
 * Shift/Ctrl/Alt/Cmd never register. NSEvent gives the physical keyCode of the
 * modifier that moved; the flag mask says whether it went down or up. */
- (void)flagsChanged:(NSEvent*)event {
    FlowGfxContext* ctx = self.ctx;
    if (!ctx) return;
    unsigned short code = event.keyCode;
    if (code >= 256) return;
    NSEventModifierFlags flags = event.modifierFlags;
    NSEventModifierFlags mask = 0;
    switch (code) {
        case 56: case 60: mask = NSEventModifierFlagShift; break;   // L/R shift
        case 59: case 62: mask = NSEventModifierFlagControl; break; // L/R ctrl
        case 58: case 61: mask = NSEventModifierFlagOption; break;  // L/R alt
        case 55: case 54: mask = NSEventModifierFlagCommand; break; // L/R cmd
        default: return;
    }
    ctx->keys[code] = (flags & mask) != 0;
}

/* Framebuffer coordinates from a mouse event.
 *
 * Buffer row 0 is the TOP of the image: drawRect: hands the buffer to
 * CGBitmapContextCreate and CGContextDrawImage places row 0 at the top of the
 * destination rect. Measured, not assumed — filling row 0 red and row h-1 blue
 * produces a PPM whose first row is red.
 *
 * NSView here is not flipped, so locationInWindow has its origin at the
 * bottom-left. The two therefore disagree and y must be inverted. Do not
 * "fix" this by overriding isFlipped: that would flip rendering for every
 * existing demo. */
- (void)flowUpdateMouseFrom:(NSEvent*)event {
    FlowGfxContext* ctx = self.ctx;
    if (!ctx) return;
    NSPoint p = [self convertPoint:event.locationInWindow fromView:nil];
    int32_t x = (int32_t)floor(p.x);
    int32_t y = (int32_t)floor(p.y);
    ctx->mouse_x = x;
    ctx->mouse_y = (ctx->height - 1) - y;
    ctx->mouse_inside = (x >= 0 && x < ctx->width && y >= 0 && y < ctx->height);
}

- (void)mouseMoved:(NSEvent*)event      { [self flowUpdateMouseFrom:event]; }
- (void)mouseDragged:(NSEvent*)event    { [self flowUpdateMouseFrom:event]; }
- (void)rightMouseDragged:(NSEvent*)e   { [self flowUpdateMouseFrom:e]; }
- (void)otherMouseDragged:(NSEvent*)e   { [self flowUpdateMouseFrom:e]; }

- (void)mouseDown:(NSEvent*)event {
    [self flowUpdateMouseFrom:event];
    if (self.ctx) self.ctx->mouse_left = true;
}
- (void)mouseUp:(NSEvent*)event {
    [self flowUpdateMouseFrom:event];
    if (self.ctx) self.ctx->mouse_left = false;
}
- (void)rightMouseDown:(NSEvent*)event {
    [self flowUpdateMouseFrom:event];
    if (self.ctx) self.ctx->mouse_right = true;
}
- (void)rightMouseUp:(NSEvent*)event {
    [self flowUpdateMouseFrom:event];
    if (self.ctx) self.ctx->mouse_right = false;
}
- (void)otherMouseDown:(NSEvent*)event {
    [self flowUpdateMouseFrom:event];
    if (self.ctx) self.ctx->mouse_middle = true;
}
- (void)otherMouseUp:(NSEvent*)event {
    [self flowUpdateMouseFrom:event];
    if (self.ctx) self.ctx->mouse_middle = false;
}

/* Cumulative wheel total. Callers diff it against their own previous value,
 * matching the *_held edge-detection idiom the demos already use, and keeping
 * this side of the ABI stateless. */
- (void)scrollWheel:(NSEvent*)event {
    FlowGfxContext* ctx = self.ctx;
    if (!ctx) return;
    double dy = event.scrollingDeltaY;
    if (event.hasPreciseScrollingDeltas) dy /= 10.0;
    if (dy > 0.0) ctx->mouse_wheel += (int32_t)ceil(dy);
    else if (dy < 0.0) ctx->mouse_wheel += (int32_t)floor(dy);
}

- (void)mouseEntered:(NSEvent*)event { if (self.ctx) self.ctx->mouse_inside = true; }
- (void)mouseExited:(NSEvent*)event  { if (self.ctx) self.ctx->mouse_inside = false; }

/* Re-arm tracking whenever the view geometry changes. */
- (void)updateTrackingAreas {
    [super updateTrackingAreas];
    for (NSTrackingArea* a in [self trackingAreas]) [self removeTrackingArea:a];
    NSTrackingAreaOptions opts = NSTrackingMouseMoved | NSTrackingMouseEnteredAndExited |
                                 NSTrackingActiveInKeyWindow | NSTrackingInVisibleRect;
    NSTrackingArea* area = [[NSTrackingArea alloc] initWithRect:[self bounds]
                                                        options:opts
                                                          owner:self
                                                       userInfo:nil];
    [self addTrackingArea:area];
    FLOW_RELEASE(area);
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
        // Without this, mouseMoved: is never delivered (only drags are).
        [ctx->window setAcceptsMouseMovedEvents:YES];
        [ctx->view updateTrackingAreas];

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

/* Whole pointer state in one call.
 *
 *   out[0] x        framebuffer column
 *   out[1] y        framebuffer row, 0 = top
 *   out[2] left     1 while held
 *   out[3] right
 *   out[4] middle
 *   out[5] wheel    cumulative signed total, never reset by a read
 *   out[6] inside   1 while the cursor is over the framebuffer
 *
 * Returns 0 when the backend has no pointer, leaving out[] zeroed, so a demo
 * can degrade rather than fail. One symbol rather than five accessors: five
 * accessors across five backends would be 25 functions to keep in step. */
int32_t flow_gfx_mouse(void* handle, int32_t* out) {
    if (!out) return 0;
    FlowGfxContext* ctx = (FlowGfxContext*)handle;
    if (!ctx) {
        for (int i = 0; i < 7; i++) out[i] = 0;
        return 0;
    }
    out[0] = ctx->mouse_x;
    out[1] = ctx->mouse_y;
    out[2] = ctx->mouse_left ? 1 : 0;
    out[3] = ctx->mouse_right ? 1 : 0;
    out[4] = ctx->mouse_middle ? 1 : 0;
    out[5] = ctx->mouse_wheel;
    out[6] = ctx->mouse_inside ? 1 : 0;
    return 1;
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


/* Blit a packed RGB8 buffer (w*h*3 bytes, row-major, no padding) into the
 * framebuffer at (x, y). Per-pixel work belongs here rather than in a
 * fill_rect call per pixel: a 320x240 particle field is 76800 rects a frame,
 * which the rect path cannot sustain. Clipped like fill_rect. */
void flow_gfx_blit_rgb(void *handle, int32_t x, int32_t y, int32_t w, int32_t h,
                       const uint8_t *src) {
    FlowGfxContext *ctx = (FlowGfxContext *)handle;
    if (!ctx || !ctx->pixels || !src) return;
    if (w <= 0 || h <= 0) return;

    int x0 = x < 0 ? 0 : x;
    int y0 = y < 0 ? 0 : y;
    int x1 = x + w; if (x1 > ctx->width) x1 = ctx->width;
    int y1 = y + h; if (y1 > ctx->height) y1 = ctx->height;
    if (x0 >= x1 || y0 >= y1) return;

    uint8_t *dst = ctx->pixels;
    for (int yy = y0; yy < y1; yy++) {
        const uint8_t *srow = src + ((size_t)(yy - y) * (size_t)w + (size_t)(x0 - x)) * 3u;
        uint8_t *drow = dst + ((size_t)yy * (size_t)ctx->width + (size_t)x0) * 4u;
        for (int xx = x0; xx < x1; xx++) {
            drow[0] = srow[0];
            drow[1] = srow[1];
            drow[2] = srow[2];
            drow[3] = 255;
            srow += 3;
            drow += 4;
        }
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

/* Milliseconds since the first call. CACurrentMediaTime is the mach monotonic
 * clock, so it does not jump when the wall clock is adjusted. */
double flow_gfx_time_ms(void* handle) {
    (void)handle;
    static double origin = -1.0;
    double now = CACurrentMediaTime() * 1000.0;
    if (origin < 0.0) origin = now;
    return now - origin;
}

/* Sleep out the remainder of a frame at target_fps. There is no vsync on this
 * path, so without this a demo runs as fast as the machine allows and its
 * animation speed becomes hardware-dependent. */
void flow_gfx_wait_frame(void* handle, int32_t target_fps) {
    static double next = 0.0;
    if (target_fps <= 0) return;
    double period = 1000.0 / (double)target_fps;
    double now = flow_gfx_time_ms(handle);
    if (next <= 0.0) { next = now + period; return; }
    double wait = next - now;
    if (wait > 0.0) {
        if (wait > period) wait = period;   /* clock jumped; do not stall */
        usleep((useconds_t)(wait * 1000.0));
    }
    next = (wait < -period) ? now + period : next + period;  /* resync if far behind */
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
