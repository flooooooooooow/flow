/*
 * Headless ABI smoke for gfx_* backends under -DFLOW_GFX_STUB.
 * Expects init → NULL, should_close → 1, and other ops to be no-ops.
 */
#include <stdio.h>
#include <stdlib.h>

void *flow_gfx_init(int width, int height, const char *title);
void flow_gfx_shutdown(void *g);
void flow_gfx_poll(void *g);
int flow_gfx_should_close(void *g);
int flow_gfx_key_down(void *g, int keycode);
void flow_gfx_clear(void *g, int r, int gch, int b);
void flow_gfx_fill_rect(void *g, int x, int y, int w, int h, int r, int gch, int b);
void flow_gfx_present(void *g);

int main(void) {
    void *g = flow_gfx_init(320, 240, "stub-smoke");
    if (g != NULL) {
        fprintf(stderr, "expected stub init to return NULL\n");
        return 1;
    }
    /* Ops must tolerate a NULL handle (stub path). */
    flow_gfx_poll(g);
    if (!flow_gfx_should_close(g)) {
        fprintf(stderr, "expected stub should_close == 1\n");
        return 2;
    }
    (void)flow_gfx_key_down(g, 0);
    flow_gfx_clear(g, 0, 0, 0);
    flow_gfx_fill_rect(g, 0, 0, 1, 1, 255, 0, 0);
    flow_gfx_present(g);
    flow_gfx_shutdown(g);
    puts("gfx stub smoke ok");
    return 0;
}
