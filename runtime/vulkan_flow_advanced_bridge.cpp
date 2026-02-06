#include <cstdlib>
#include <cstdint>

extern int flow_vk_scene_entry();
extern int flow_vk_triangle_entry();
extern "C" void flow_vk_scene_configure(int32_t width, int32_t height, float clear_r, float clear_g, float clear_b,
                                        float rotation_speed, const char* title,
                                        const char* texture_path, const char* texture_path2,
                                        float camera_distance, float camera_pitch, float camera_yaw,
                                        float move_speed, float mouse_sensitivity,
                                        float camera_smoothing,
                                        float mesh1_r, float mesh1_g, float mesh1_b,
                                        float mesh2_r, float mesh2_g, float mesh2_b,
                                        int32_t instance_count);
extern "C" void flow_vk_triangle_configure(int32_t width, int32_t height, float clear_r, float clear_g, float clear_b, const char* title);

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
    setenv("FLOW_VK_PRETTY", pretty ? "1" : "0", 1);
    setenv("FLOW_VK_TRACE", trace ? "1" : "0", 1);
    if (validation) {
        unsetenv("FLOW_VK_NO_VALIDATION");
    } else {
        setenv("FLOW_VK_NO_VALIDATION", "1", 1);
    }
    flow_vk_scene_configure(width, height, clear_r, clear_g, clear_b, rotation_speed, title,
                            texture_path, texture_path2,
                            camera_distance, camera_pitch, camera_yaw,
                            move_speed, mouse_sensitivity,
                            camera_smoothing,
                            mesh1_r, mesh1_g, mesh1_b,
                            mesh2_r, mesh2_g, mesh2_b,
                            instance_count);
    return flow_vk_scene_entry();
}

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
