#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "../gfx_overlay.h"

static int check(int ok, const char *name) {
    if (!ok) fprintf(stderr, "FAIL %s\n", name);
    else fprintf(stdout, "PASS %s\n", name);
    return ok;
}

int main(void) {
    enum { W = 8, H = 6, N = W * H * 4 };
    uint8_t dst[N], src[N];
    memset(dst, 0, sizeof(dst));
    for (int i = 0; i < N; i++) src[i] = (uint8_t)(i % 251 + 1);
    const int32_t empty[4] = { W, H, 0, 0 };
    const int32_t a[4] = { 1, 1, 4, 4 };
    const int32_t b[4] = { 5, 2, 8, 5 };
    flow_gfx_overlay_patch(dst, src, W, H, empty, a);
    int ok = check(memcmp(dst + (1 * W + 1) * 4, src + (1 * W + 1) * 4, 12) == 0,
                   "copies current dirty rows");
    ok &= check(dst[(0 * W + 0) * 4 + 3] == 0, "leaves pixels outside dirty bounds clear");
    flow_gfx_overlay_patch(dst, src, W, H, a, b);
    ok &= check(dst[(1 * W + 1) * 4 + 3] == 0, "clears the previous slot bounds");
    ok &= check(memcmp(dst + (2 * W + 5) * 4, src + (2 * W + 5) * 4, 12) == 0,
                "copies the next slot bounds");
    const int32_t emptyNow[4] = { 0, 0, 0, 0 };
    flow_gfx_overlay_patch(dst, NULL, W, H, b, emptyNow);
    ok &= check(dst[(2 * W + 5) * 4 + 3] == 0, "clears a slot when no overlay is present");
    return ok ? 0 : 1;
}
