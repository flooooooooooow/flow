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
#import <CoreText/CoreText.h>

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

    // HiDPI mode (flow_gfx_init_hidpi). The framebuffer is in device pixels:
    // width = view points * scale. Mouse and text coordinates follow it.
    bool hidpi;
    double scale;         // backingScaleFactor, 1.0 outside HiDPI mode
    int32_t generation;   // bumped whenever the framebuffer is reallocated
    int32_t cursor;       // last cursor kind set through flow_gfx_cursor
    CGContextRef text_cg; // bitmap context over pixels, rebuilt on realloc
    CTFontRef fonts[16];  // small cache for flow_gfx_text_ex
    int32_t font_key[16];
    int32_t font_next;
};

static void flow_gfx_drop_text_cg(FlowGfxContext* ctx) {
    if (ctx->text_cg) { CGContextRelease(ctx->text_cg); ctx->text_cg = NULL; }
}

/* HiDPI: size the framebuffer to the view in device pixels. Contents are
 * cleared to black; the program sees a new generation and repaints. */
static void flow_gfx_fit_framebuffer(FlowGfxContext* ctx) {
    if (!ctx || !ctx->hidpi || !ctx->view) return;
    NSRect b = [ctx->view bounds];
    double scale = ctx->window ? [ctx->window backingScaleFactor] : 1.0;
    if (scale <= 0.0) scale = 1.0;
    int w = (int)lround(b.size.width * scale);
    int h = (int)lround(b.size.height * scale);
    if (w < 1) w = 1;
    if (h < 1) h = 1;
    if (ctx->pixels && w == ctx->width && h == ctx->height && scale == ctx->scale) return;
    uint8_t* px = (uint8_t*)calloc((size_t)w * (size_t)h * 4u, 1);
    if (!px) return;
    for (size_t i = 0; i < (size_t)w * (size_t)h; i++) px[i * 4 + 3] = 255;
    flow_gfx_drop_text_cg(ctx);
    free(ctx->pixels);
    ctx->pixels = px;
    ctx->width = w;
    ctx->height = h;
    ctx->scale = scale;
    ctx->generation++;
}

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
    if (ctx->hidpi) {
        /* Device pixels, y down from the top of the view. */
        double top = [self bounds].size.height - p.y;
        int32_t x = (int32_t)floor(p.x * ctx->scale);
        int32_t y = (int32_t)floor(top * ctx->scale);
        ctx->mouse_x = x;
        ctx->mouse_y = y;
        ctx->mouse_inside = (x >= 0 && x < ctx->width && y >= 0 && y < ctx->height);
        return;
    }
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

- (BOOL)isOpaque { return YES; }

- (void)setFrameSize:(NSSize)size {
    [super setFrameSize:size];
    if (self.ctx && self.ctx->hidpi) flow_gfx_fit_framebuffer(self.ctx);
}

- (void)viewDidChangeBackingProperties {
    [super viewDidChangeBackingProperties];
    if (self.ctx && self.ctx->hidpi) flow_gfx_fit_framebuffer(self.ctx);
}

- (void)drawRect:(NSRect)dirtyRect {
    [super drawRect:dirtyRect];
    FlowGfxContext* ctx = self.ctx;
    if (!ctx || !ctx->pixels) return;

    if (ctx->hidpi) {
        /* One framebuffer pixel per device pixel: draw the image at its size
         * in points, pinned to the top-left, with no resampling. */
        CGContextRef cg = [[NSGraphicsContext currentContext] CGContext];
        if (!cg) return;
        NSRect b = [self bounds];
        CGContextSetRGBFillColor(cg, 0, 0, 0, 1);
        CGContextFillRect(cg, NSRectToCGRect(b));
        CGColorSpaceRef cs = CGColorSpaceCreateDeviceRGB();
        size_t bytes = (size_t)ctx->width * (size_t)ctx->height * 4u;
        CGDataProviderRef dp = CGDataProviderCreateWithData(NULL, ctx->pixels, bytes, NULL);
        CGImageRef img = CGImageCreate((size_t)ctx->width, (size_t)ctx->height, 8, 32,
                                       (size_t)ctx->width * 4u, cs,
                                       kCGBitmapByteOrder32Big | kCGImageAlphaNoneSkipLast,
                                       dp, NULL, false, kCGRenderingIntentDefault);
        if (img) {
            double pw = ctx->width / ctx->scale;
            double ph = ctx->height / ctx->scale;
            CGContextSetInterpolationQuality(cg, kCGInterpolationNone);
            CGContextDrawImage(cg, CGRectMake(0, b.size.height - ph, pw, ph), img);
            CGImageRelease(img);
        }
        CGDataProviderRelease(dp);
        CGColorSpaceRelease(cs);
        return;
    }

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

static void* flow_gfx_open_window(int32_t w, int32_t h, const char* title_utf8,
                                  bool hidpi, bool resizable) {
    @autoreleasepool {
        NSApplication* app = [NSApplication sharedApplication];
        [app setActivationPolicy:NSApplicationActivationPolicyRegular];
        /* Events are pumped by hand rather than through [NSApp run], which
         * would call this. Without it the app never finishes launching:
         * accessibility clients (System Events, window managers) see no
         * windows. */
        static bool launched = false;
        if (!launched) {
            [app finishLaunching];
            launched = true;
        }

        FlowGfxContext* ctx = (FlowGfxContext*)calloc(1, sizeof(FlowGfxContext));
        ctx->width = (int)w;
        ctx->height = (int)h;
        ctx->scale = 1.0;
        ctx->hidpi = hidpi;
        if (!hidpi) ctx->pixels = (uint8_t*)calloc((size_t)w * (size_t)h * 4u, 1);

        NSString* title = title_utf8 ? [NSString stringWithUTF8String:title_utf8] : @"FLOW";
        NSRect frame = NSMakeRect(100, 100, w, h);
        NSUInteger style = NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskMiniaturizable;
        if (resizable) style |= NSWindowStyleMaskResizable;
        ctx->window = [[NSWindow alloc] initWithContentRect:frame
                                                  styleMask:style
                                                    backing:NSBackingStoreBuffered
                                                      defer:NO];
        [ctx->window setTitle:title];
        [ctx->window setReleasedWhenClosed:NO];
        if (resizable) [ctx->window setContentMinSize:NSMakeSize(480, 320)];

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

        if (hidpi) {
            [ctx->window center];
            flow_gfx_fit_framebuffer(ctx);
        }
        [ctx->window makeKeyAndOrderFront:nil];
        [app activateIgnoringOtherApps:YES];
        if (hidpi) flow_gfx_fit_framebuffer(ctx);

        return (void*)ctx;
    }
}

void* flow_gfx_init(int32_t w, int32_t h, const char* title_utf8) {
    return flow_gfx_open_window(w, h, title_utf8, false, false);
}

/* A window of w x h points whose framebuffer is in device pixels, so a Retina
 * display gets one framebuffer pixel per screen pixel with no scaling.
 * flags: 1 = resizable. Read the real size back with flow_gfx_metrics. */
void* flow_gfx_init_hidpi(int32_t w, int32_t h, const char* title_utf8, int32_t flags) {
    return flow_gfx_open_window(w, h, title_utf8, true, (flags & 1) != 0);
}

/*   out[0] framebuffer width in pixels
 *   out[1] framebuffer height in pixels
 *   out[2] pixels per point x 100 (200 on a Retina display)
 *   out[3] generation: changes whenever the framebuffer is reallocated,
 *          after a resize or a move to a display with another scale */
int32_t flow_gfx_metrics(void* handle, int32_t* out) {
    FlowGfxContext* ctx = (FlowGfxContext*)handle;
    if (!out) return 0;
    if (!ctx) { out[0] = out[1] = out[2] = out[3] = 0; return 0; }
    out[0] = ctx->width;
    out[1] = ctx->height;
    out[2] = (int32_t)lround(ctx->scale * 100.0);
    out[3] = ctx->generation;
    return 1;
}

/* 0 arrow, 1 pointing hand, 2 crosshair, 3 resize left-right,
 * 4 resize up-down, 5 open hand, 6 closed hand, 7 I-beam. */
void flow_gfx_cursor(void* handle, int32_t kind) {
    FlowGfxContext* ctx = (FlowGfxContext*)handle;
    if (!ctx || ctx->cursor == kind) return;
    ctx->cursor = kind;
    NSCursor* c = [NSCursor arrowCursor];
    if (kind == 1) c = [NSCursor pointingHandCursor];
    if (kind == 2) c = [NSCursor crosshairCursor];
    if (kind == 3) c = [NSCursor resizeLeftRightCursor];
    if (kind == 4) c = [NSCursor resizeUpDownCursor];
    if (kind == 5) c = [NSCursor openHandCursor];
    if (kind == 6) c = [NSCursor closedHandCursor];
    if (kind == 7) c = [NSCursor IBeamCursor];
    [c set];
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
        flow_gfx_drop_text_cg(ctx);
        for (int i = 0; i < 16; i++) if (ctx->fonts[i]) CFRelease(ctx->fonts[i]);
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

/* Render platform typography into the same framebuffer as the UI shapes. */
void flow_gfx_text(void *handle, int32_t x, int32_t y, const char *text,
                   int32_t size, uint8_t r, uint8_t g, uint8_t b) {
    FlowGfxContext *ctx = (FlowGfxContext *)handle;
    if (!ctx || !ctx->pixels || !text || size <= 0) return;
    CGColorSpaceRef cs = CGColorSpaceCreateDeviceRGB();
    CGContextRef cg = CGBitmapContextCreate(ctx->pixels, ctx->width, ctx->height,
                                             8, (size_t)ctx->width * 4u, cs,
                                             kCGImageAlphaPremultipliedLast);
    if (!cg) { CGColorSpaceRelease(cs); return; }
    CFStringRef value = CFStringCreateWithCString(NULL, text, kCFStringEncodingUTF8);
    CTFontRef font = CTFontCreateWithName(CFSTR("SF Pro Display"), (CGFloat)size, NULL);
    if (!font) font = CTFontCreateWithName(CFSTR("Helvetica Neue"), (CGFloat)size, NULL);
    if (value && font) {
        CGFloat components[4] = { r / 255.0, g / 255.0, b / 255.0, 1.0 };
        CGColorRef color = CGColorCreate(cs, components);
        const void *keys[] = { kCTFontAttributeName, kCTForegroundColorAttributeName };
        const void *vals[] = { font, color };
        CFDictionaryRef attrs = CFDictionaryCreate(NULL, keys, vals, 2,
                                                     &kCFTypeDictionaryKeyCallBacks,
                                                     &kCFTypeDictionaryValueCallBacks);
        CFAttributedStringRef attributed = CFAttributedStringCreate(NULL, value, attrs);
        CTLineRef line = CTLineCreateWithAttributedString(attributed);
        CGContextSetTextPosition(cg, (CGFloat)x, (CGFloat)(ctx->height - y - size));
        CTLineDraw(line, cg);
        CFRelease(line); CFRelease(attributed); CFRelease(attrs); CGColorRelease(color);
    }
    if (font) CFRelease(font);
    if (value) CFRelease(value);
    CGContextRelease(cg); CGColorSpaceRelease(cs);
}

/* System font for flow_gfx_text_ex, cached by (size, style). */
static CTFontRef flow_gfx_font(FlowGfxContext* ctx, int32_t size, int32_t style) {
    int32_t key = size * 64 + (style & 15);
    for (int i = 0; i < 16; i++) {
        if (ctx->fonts[i] && ctx->font_key[i] == key) return ctx->fonts[i];
    }
    NSFontWeight weights[4] = { NSFontWeightRegular, NSFontWeightMedium,
                                NSFontWeightSemibold, NSFontWeightBold };
    NSFontWeight wt = weights[style & 3];
    NSFont* f = nil;
    if (style & 8) f = [NSFont monospacedSystemFontOfSize:(CGFloat)size weight:wt];
    else if (style & 4) f = [NSFont monospacedDigitSystemFontOfSize:(CGFloat)size weight:wt];
    else f = [NSFont systemFontOfSize:(CGFloat)size weight:wt];
    if (!f) return NULL;
    CTFontRef ct = (CTFontRef)CFBridgingRetain(f);
    int slot = ctx->font_next;
    ctx->font_next = (ctx->font_next + 1) % 16;
    if (ctx->fonts[slot]) CFRelease(ctx->fonts[slot]);
    ctx->fonts[slot] = ct;
    ctx->font_key[slot] = key;
    return ct;
}

/* Text with the system font, positioned on its baseline, in framebuffer
 * pixels (device pixels in HiDPI mode). Returns the advance width in pixels,
 * rounded up. With measure = 1 nothing is drawn.
 *
 *   style & 3   weight: 0 regular, 1 medium, 2 semibold, 3 bold
 *   style & 4   tabular (fixed-width) digits
 *   style & 8   monospaced (SF Mono)
 *   style & 16  tracked: +6% letter spacing, for small capitals labels
 *   rgb         0xRRGGBB */
int32_t flow_gfx_text_ex(void* handle, int32_t x, int32_t baseline, const char* text,
                         int32_t size, int32_t rgb, int32_t style, int32_t measure) {
    FlowGfxContext* ctx = (FlowGfxContext*)handle;
    if (!ctx || !ctx->pixels || !text || size <= 0) return 0;
    @autoreleasepool {
        CTFontRef font = flow_gfx_font(ctx, size, style);
        if (!font) return 0;
        CFStringRef value = CFStringCreateWithCString(NULL, text, kCFStringEncodingUTF8);
        if (!value) return 0;
        CGColorSpaceRef cs = CGColorSpaceCreateDeviceRGB();
        CGFloat comp[4] = { ((rgb >> 16) & 255) / 255.0, ((rgb >> 8) & 255) / 255.0,
                            (rgb & 255) / 255.0, 1.0 };
        CGColorRef color = CGColorCreate(cs, comp);
        CGFloat kern = (style & 16) ? 0.06 * (CGFloat)size : 0.0;
        CFNumberRef kn = CFNumberCreate(NULL, kCFNumberCGFloatType, &kern);
        const void* keys[] = { kCTFontAttributeName, kCTForegroundColorAttributeName, kCTKernAttributeName };
        const void* vals[] = { font, color, kn };
        CFDictionaryRef attrs = CFDictionaryCreate(NULL, keys, vals, 3,
                                                   &kCFTypeDictionaryKeyCallBacks,
                                                   &kCFTypeDictionaryValueCallBacks);
        CFAttributedStringRef attributed = CFAttributedStringCreate(NULL, value, attrs);
        CTLineRef line = CTLineCreateWithAttributedString(attributed);
        double width = CTLineGetTypographicBounds(line, NULL, NULL, NULL);
        if (!measure) {
            if (!ctx->text_cg) {
                ctx->text_cg = CGBitmapContextCreate(ctx->pixels, ctx->width, ctx->height,
                                                     8, (size_t)ctx->width * 4u, cs,
                                                     (CGBitmapInfo)kCGImageAlphaPremultipliedLast);
            }
            CGContextRef cg = ctx->text_cg;
            if (cg) {
                CGContextSetAllowsFontSubpixelPositioning(cg, true);
                CGContextSetShouldSubpixelPositionFonts(cg, true);
                CGContextSetAllowsAntialiasing(cg, true);
                CGContextSetShouldAntialias(cg, true);
                CGContextSetTextMatrix(cg, CGAffineTransformIdentity);
                CGContextSetTextPosition(cg, (CGFloat)x, (CGFloat)(ctx->height - baseline));
                CTLineDraw(line, cg);
                CGContextFlush(cg);
            }
        }
        CFRelease(line); CFRelease(attributed); CFRelease(attrs); CFRelease(kn);
        CGColorRelease(color); CGColorSpaceRelease(cs); CFRelease(value);
        return (int32_t)ceil(width);
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
