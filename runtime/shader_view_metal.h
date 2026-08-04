/* Fullscreen Metal fill-shader viewer for FLOW `shader fill` demos. */
#ifndef FLOW_SHADER_VIEW_METAL_H
#define FLOW_SHADER_VIEW_METAL_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Show a window running `fragment_fn` from `metal_source`.
 * Returns 0 on clean close, non-zero on error.
 * max_frames <= 0 means run until the window is closed (or Esc).
 */
int flow_shader_show(
    const char *metal_source,
    const char *fragment_fn,
    int32_t width,
    int32_t height,
    int32_t max_frames
);

/* Convenience: load Metal source from a file path. */
int flow_shader_show_file(
    const char *metal_path,
    const char *fragment_fn,
    int32_t width,
    int32_t height,
    int32_t max_frames
);

#ifdef __cplusplus
}
#endif

#endif /* FLOW_SHADER_VIEW_METAL_H */
