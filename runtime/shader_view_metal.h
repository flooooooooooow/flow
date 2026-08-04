/* Fullscreen Metal fill-shader viewer for FLOW Shader Language demos. */
#ifndef FLOW_SHADER_VIEW_METAL_H
#define FLOW_SHADER_VIEW_METAL_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Single fragment entry. max_frames <= 0 runs until close/Esc. */
int flow_shader_show(
    const char *metal_source,
    const char *fragment_fn,
    int32_t width,
    int32_t height,
    int32_t max_frames
);

/* Gallery: cycle fragment entries with Left/Right/Space. */
int flow_shader_show_gallery(
    const char *metal_source,
    const char **fragment_fns,
    int32_t fragment_count,
    int32_t width,
    int32_t height,
    int32_t max_frames
);

int flow_shader_show_file(
    const char *metal_path,
    const char *fragment_fn,
    int32_t width,
    int32_t height,
    int32_t max_frames
);

/* Load metal + sibling .entries list (one entry name per line). */
int flow_shader_show_gallery_file(
    const char *metal_path,
    const char *entries_path,
    int32_t width,
    int32_t height,
    int32_t max_frames
);

#ifdef __cplusplus
}
#endif

#endif /* FLOW_SHADER_VIEW_METAL_H */
