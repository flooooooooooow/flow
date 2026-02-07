#include "../../demos/vulkan_abi/renderer.h"

int main(void) {
    // Compile-time ABI smoke test only.
    (void)flow_vk_2048_init(0, 0, "abi-test", 16);
    (void)flow_vk_2048_should_close();
    flow_vk_2048_poll();
    flow_vk_2048_key_down(0);
    flow_vk_2048_draw((const float*)0, 0);
    flow_vk_2048_upload_texture((const uint8_t*)0, 0, 0);
    flow_vk_2048_shutdown();
    return 0;
}
