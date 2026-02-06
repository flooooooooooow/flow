#include <cstdlib>
#include <cstdint>
#include <cstdio>

extern int flow_vk_triangle_entry();
extern "C" void flow_vk_triangle_configure(int32_t width, int32_t height, float clear_r, float clear_g, float clear_b, const char* title);

extern "C" int flow_vulkan_basic_run(int32_t pretty, int32_t trace, int32_t validation,
                                     int32_t width, int32_t height,
                                     float clear_r, float clear_g, float clear_b,
                                     const char* title) {
    setenv("FLOW_VK_PRETTY", pretty ? "1" : "0", 1);
    setenv("FLOW_VK_TRACE", trace ? "1" : "0", 1);
    if (validation) {
        unsetenv("FLOW_VK_NO_VALIDATION");
    } else {
        setenv("FLOW_VK_NO_VALIDATION", "1", 1);
    }
    flow_vk_triangle_configure(width, height, clear_r, clear_g, clear_b, title);
    return flow_vk_triangle_entry();
}

extern "C" int flow_vulkan_advanced_run(int32_t pretty, int32_t trace, int32_t validation,
                                        int32_t width, int32_t height,
                                        float clear_r, float clear_g, float clear_b,
                                        float rotation_speed, const char* title,
                                        const char* texture_path, const char* texture_path2,
                                        float camera_distance, float camera_pitch, float camera_yaw,
                                        float move_speed, float mouse_sensitivity,
                                        float camera_smoothing,
                                        float mesh1_r, float mesh1_g, float mesh1_b,
                                        float mesh2_r, float mesh2_g, float mesh2_b,
                                        int32_t instance_count) {
    (void)pretty;
    (void)trace;
    (void)validation;
    (void)width;
    (void)height;
    (void)clear_r;
    (void)clear_g;
    (void)clear_b;
    (void)rotation_speed;
    (void)title;
    (void)texture_path;
    (void)texture_path2;
    (void)camera_distance;
    (void)camera_pitch;
    (void)camera_yaw;
    (void)move_speed;
    (void)mouse_sensitivity;
    (void)camera_smoothing;
    (void)mesh1_r;
    (void)mesh1_g;
    (void)mesh1_b;
    (void)mesh2_r;
    (void)mesh2_g;
    (void)mesh2_b;
    (void)instance_count;
    std::fprintf(stderr, "Vulkan: advanced demo not linked in this build (use vulkan-flow advanced)\n");
    return -1;
}
