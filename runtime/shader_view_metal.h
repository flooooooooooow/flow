/* Fullscreen Metal fill-shader viewer for FLOW Shader Language demos. */
#ifndef FLOW_SHADER_VIEW_METAL_H
#define FLOW_SHADER_VIEW_METAL_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Layout modes for multi-shader viewing */
enum {
    FLOW_SHADER_LAYOUT_CYCLE = 0, /* one shader at a time (←/→) */
    FLOW_SHADER_LAYOUT_GRID  = 1  /* all shaders tiled in a grid */
};

int flow_shader_show(
    const char *metal_source,
    const char *fragment_fn,
    int32_t width,
    int32_t height,
    int32_t max_frames
);

int flow_shader_show_gallery(
    const char *metal_source,
    const char **fragment_fns,
    int32_t fragment_count,
    int32_t width,
    int32_t height,
    int32_t max_frames
);

/* Like show_gallery, with explicit layout (CYCLE or GRID). */
int flow_shader_show_gallery_ex(
    const char *metal_source,
    const char **fragment_fns,
    int32_t fragment_count,
    int32_t width,
    int32_t height,
    int32_t max_frames,
    int32_t layout
);

int flow_shader_show_file(
    const char *metal_path,
    const char *fragment_fn,
    int32_t width,
    int32_t height,
    int32_t max_frames
);

int flow_shader_show_gallery_file(
    const char *metal_path,
    const char *entries_path,
    int32_t width,
    int32_t height,
    int32_t max_frames
);

int flow_shader_show_gallery_file_ex(
    const char *metal_path,
    const char *entries_path,
    int32_t width,
    int32_t height,
    int32_t max_frames,
    int32_t layout
);

#ifdef __cplusplus
}
#endif

#endif /* FLOW_SHADER_VIEW_METAL_H */
