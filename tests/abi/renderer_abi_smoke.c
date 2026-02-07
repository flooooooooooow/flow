#include "../../demos/vulkan_abi/renderer.h"

int main(void) {
    // Compile-time ABI smoke test only.
    (void)flow_vk_2048_init(0, 0, "abi-test", 16);
    (void)flow_vk_2048_should_close();
    flow_vk_2048_poll();
    flow_vk_2048_key_down(0);
    flow_vk_2048_draw((const float*)0, 0);
    flow_vk_2048_upload_texture((const uint8_t*)0, 0, 0);
    flow_vk_begin_frame();
    flow_vk_end_frame();
    (void)flow_vk_create_instance_buffer(16);
    flow_vk_update_instance_buffer(1, (const float*)0, 0);
    flow_vk_draw_instance_buffer(1, 0);
    (void)flow_vk_create_texture(64, 64);
    flow_vk_update_texture(1, (const uint8_t*)0, 0, 0);
    flow_vk_upload_mesh((const float*)0, 0, (const uint16_t*)0, 0);
    flow_vk_set_clear_color(0.0f, 0.0f, 0.0f);
    flow_vk_set_camera(0.0f, 0.0f, 0.0f);
    flow_vk_set_viewport(0, 0);
    flow_vk_set_window_scale(1.0f, 0);
    flow_vk_2048_shutdown();
    return 0;
}
