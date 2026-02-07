#include "../../demos/vulkan_abi/vulkan_renderer.h"

int main(void) {
    (void)flow_vulkan_basic_run(0, 0, 0, 0, 0, 0.0f, 0.0f, 0.0f, "test");
    (void)flow_vulkan_advanced_run(0, 0, 0, 0, 0, 0.0f, 0.0f, 0.0f, 0.0f,
                                   "test", "", "", 0.0f, 0.0f, 0.0f, 0.0f, 0.0f,
                                   0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0);
    return 0;
}
