#include <vulkan/vulkan.h>
#include <GLFW/glfw3.h>

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <optional>
#include <set>
#include <string>
#include <vector>
#include <sys/stat.h>

#include "../vulkan_abi/renderer.h"

#ifdef __APPLE__
#include <CoreFoundation/CoreFoundation.h>
#include <CoreGraphics/CoreGraphics.h>
#include <ImageIO/ImageIO.h>
#include <CoreText/CoreText.h>
#endif

namespace {

class VulkanApp;

struct Config {
    uint32_t width = 960;
    uint32_t height = 640;
    float clearR = 0.02f;
    float clearG = 0.02f;
    float clearB = 0.05f;
    float rotationSpeed = 1.0f;
    std::string title = "Vulkan Scene";
    std::string texturePath = "";
    std::string texturePath2 = "";
    float cameraDistance = 2.5f;
    float cameraPitch = 0.3f;
    float cameraYaw = 0.6f;
    float moveSpeed = 1.5f;
    float mouseSensitivity = 0.2f;
    float cameraSmoothing = 0.15f;
    float mesh1Color[3] = {1.0f, 1.0f, 1.0f};
    float mesh2Color[3] = {0.8f, 0.9f, 1.0f};
    uint32_t instanceCount = 16;
};

Config g_config;
bool g_tileMode = false;
bool g_externalInstanceMode = false;
uint32_t g_externalInstanceCapacity = 0;
static VulkanApp* g_flow_app = nullptr;

#ifndef FLOW_VK_STANDALONE
extern "C" void flow_2048_init_ptr_i32_ptr_i32_ptr_i32(int32_t* board, int32_t* score, int32_t* rng);
extern "C" void flow_2048_step_ptr_i32_ptr_i32_ptr_i32_i32(int32_t* board, int32_t* score, int32_t* rng, int32_t dir);
extern "C" int32_t flow_2048_score_ptr_i32(int32_t* score);
extern "C" int32_t flow_2048_can_move_ptr_i32(int32_t* board);
#endif
static double g_scrollDelta = 0.0;

const std::vector<const char*> kValidationLayers = {
    "VK_LAYER_KHRONOS_validation",
};

const std::vector<const char*> kDeviceExtensions = {
    VK_KHR_SWAPCHAIN_EXTENSION_NAME,
};

static bool validationLayersEnabled() {
#ifdef NDEBUG
    return false;
#else
    const char* env = std::getenv("FLOW_VK_NO_VALIDATION");
    return env == nullptr || std::string(env) != "1";
#endif
}

static bool prettyValidation() {
    const char* env = std::getenv("FLOW_VK_PRETTY");
    return env != nullptr && std::string(env) == "1";
}

static bool traceEnabled() {
    const char* env = std::getenv("FLOW_VK_TRACE");
    return env != nullptr && std::string(env) == "1";
}

static void trace(const char* msg) {
    if (traceEnabled()) {
        std::cerr << "Vulkan: " << msg << std::endl;
    }
}

struct QueueFamilyIndices {
    std::optional<uint32_t> graphicsFamily;
    std::optional<uint32_t> presentFamily;

    bool isComplete() const {
        return graphicsFamily.has_value() && presentFamily.has_value();
    }
};

struct SwapChainSupportDetails {
    VkSurfaceCapabilitiesKHR capabilities{};
    std::vector<VkSurfaceFormatKHR> formats;
    std::vector<VkPresentModeKHR> presentModes;
};

struct Vertex {
    float pos[3];
    float color[3];
    float uv[2];
};

struct InstanceData {
    float offset[3];
    float scale;
    float uvOffset[2];
    float uvScale[2];
    float color[4];
};

struct MeshRange {
    uint32_t firstIndex;
    uint32_t indexCount;
    int32_t vertexOffset;
};

struct UniformBufferObject {
    float view[16];
    float proj[16];
    float model[16];
};

static std::vector<char> readFile(const std::string& filename) {
    std::ifstream file(filename, std::ios::ate | std::ios::binary);
    if (!file.is_open()) {
        throw std::runtime_error("failed to open file: " + filename);
    }
    size_t fileSize = static_cast<size_t>(file.tellg());
    std::vector<char> buffer(fileSize);
    file.seekg(0);
    file.read(buffer.data(), fileSize);
    file.close();
    return buffer;
}

static bool fileNewer(const char* a, const char* b) {
    struct stat sa{};
    struct stat sb{};
    if (stat(a, &sa) != 0) {
        return false;
    }
    if (stat(b, &sb) != 0) {
        return true;
    }
    return sa.st_mtime > sb.st_mtime;
}

static void ensureShadersBuilt() {
    const char* vertSrc = "demos/vulkan_scene/shaders/scene.vert";
    const char* fragSrc = "demos/vulkan_scene/shaders/scene.frag";
    const char* vertSpv = "demos/vulkan_scene/shaders/scene.vert.spv";
    const char* fragSpv = "demos/vulkan_scene/shaders/scene.frag.spv";

    bool buildVert = fileNewer(vertSrc, vertSpv);
    bool buildFrag = fileNewer(fragSrc, fragSpv);
    if (!buildVert && !buildFrag) {
        return;
    }
    if (buildVert) {
        std::string cmd = std::string("glslangValidator -V ") + vertSrc + " -o " + vertSpv;
        int rc = std::system(cmd.c_str());
        if (rc != 0) {
            std::cerr << "error: failed to compile vertex shader via glslangValidator\n";
            throw std::runtime_error("shader compilation failed");
        }
    }
    if (buildFrag) {
        std::string cmd = std::string("glslangValidator -V ") + fragSrc + " -o " + fragSpv;
        int rc = std::system(cmd.c_str());
        if (rc != 0) {
            std::cerr << "error: failed to compile fragment shader via glslangValidator\n";
            throw std::runtime_error("shader compilation failed");
        }
    }
}

static std::string pickFileDialog(const char* title) {
#ifdef __APPLE__
    std::string script = "osascript -e 'set theFile to choose file with prompt \"" + std::string(title) + "\"' "
                         "-e 'POSIX path of theFile'";
    FILE* pipe = popen(script.c_str(), "r");
    if (!pipe) {
        return "";
    }
    char buffer[1024];
    std::string result;
    while (fgets(buffer, sizeof(buffer), pipe)) {
        result += buffer;
    }
    pclose(pipe);
    if (!result.empty() && result.back() == '\n') {
        result.pop_back();
    }
    return result;
#else
    (void)title;
    return "";
#endif
}

static void mat4_identity(float* out) {
    std::memset(out, 0, sizeof(float) * 16);
    out[0] = out[5] = out[10] = out[15] = 1.0f;
}

static void mat4_mul(const float* a, const float* b, float* out) {
    float r[16];
    for (int row = 0; row < 4; ++row) {
        for (int col = 0; col < 4; ++col) {
            r[row * 4 + col] =
                a[row * 4 + 0] * b[0 * 4 + col] +
                a[row * 4 + 1] * b[1 * 4 + col] +
                a[row * 4 + 2] * b[2 * 4 + col] +
                a[row * 4 + 3] * b[3 * 4 + col];
        }
    }
    std::memcpy(out, r, sizeof(r));
}

static void mat4_perspective(float fovy, float aspect, float znear, float zfar, float* out) {
    float f = 1.0f / std::tan(fovy * 0.5f);
    std::memset(out, 0, sizeof(float) * 16);
    out[0] = f / aspect;
    out[5] = f;
    out[10] = (zfar + znear) / (znear - zfar);
    out[11] = -1.0f;
    out[14] = (2.0f * zfar * znear) / (znear - zfar);
}

static void mat4_ortho(float left, float right, float top, float bottom, float znear, float zfar, float* out) {
    std::memset(out, 0, sizeof(float) * 16);
    out[0] = 2.0f / (right - left);
    out[5] = 2.0f / (bottom - top);
    out[10] = -2.0f / (zfar - znear);
    out[12] = -(right + left) / (right - left);
    out[13] = -(bottom + top) / (bottom - top);
    out[14] = -(zfar + znear) / (zfar - znear);
    out[15] = 1.0f;
}

static void mat4_lookat(const float* eye, const float* center, const float* up, float* out) {
    float f[3] = {center[0] - eye[0], center[1] - eye[1], center[2] - eye[2]};
    float f_len = std::sqrt(f[0]*f[0] + f[1]*f[1] + f[2]*f[2]);
    f[0] /= f_len; f[1] /= f_len; f[2] /= f_len;

    float s[3] = {f[1]*up[2] - f[2]*up[1], f[2]*up[0] - f[0]*up[2], f[0]*up[1] - f[1]*up[0]};
    float s_len = std::sqrt(s[0]*s[0] + s[1]*s[1] + s[2]*s[2]);
    s[0] /= s_len; s[1] /= s_len; s[2] /= s_len;

    float u[3] = {s[1]*f[2] - s[2]*f[1], s[2]*f[0] - s[0]*f[2], s[0]*f[1] - s[1]*f[0]};

    mat4_identity(out);
    out[0] = s[0]; out[4] = s[1]; out[8] = s[2];
    out[1] = u[0]; out[5] = u[1]; out[9] = u[2];
    out[2] = -f[0]; out[6] = -f[1]; out[10] = -f[2];
    out[12] = -(s[0]*eye[0] + s[1]*eye[1] + s[2]*eye[2]);
    out[13] = -(u[0]*eye[0] + u[1]*eye[1] + u[2]*eye[2]);
    out[14] = (f[0]*eye[0] + f[1]*eye[1] + f[2]*eye[2]);
}

static void makeMissingTexture(int& width, int& height, std::vector<uint8_t>& pixels) {
    if (g_tileMode || g_externalInstanceMode) {
        width = 2;
        height = 2;
        pixels.assign(static_cast<size_t>(width) * height * 4, 255);
        return;
    }
    width = 64;
    height = 64;
    pixels.resize(static_cast<size_t>(width) * height * 4);
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            const bool checker = ((x / 8) + (y / 8)) % 2 == 0;
            uint8_t base = checker ? 200 : 40;
            bool border = (x < 2 || y < 2 || x >= width - 2 || y >= height - 2);
            bool diag = (x == y) || (x == width - 1 - y);
            bool qmark = (y < 10 && x > 24 && x < 40) || (y > 10 && y < 26 && x > 38 && x < 44) ||
                         (y > 24 && y < 34 && x > 24 && x < 40) || (y > 38 && y < 44 && x > 32 && x < 36);
            uint8_t r = base;
            uint8_t g = base;
            uint8_t b = base;
            if (border || diag || qmark) {
                r = 255;
                g = 80;
                b = 80;
            }
            size_t idx = static_cast<size_t>((y * width + x) * 4);
            pixels[idx + 0] = r;
            pixels[idx + 1] = g;
            pixels[idx + 2] = b;
            pixels[idx + 3] = 255;
        }
    }
}

struct TileLabel {
    int value;
    const char* text;
};

static const TileLabel kTileLabels[] = {
    {0, ""},
    {2, "2"},
    {4, "4"},
    {8, "8"},
    {16, "16"},
    {32, "32"},
    {64, "64"},
    {128, "128"},
    {256, "256"},
    {512, "512"},
    {1024, "1024"},
    {2048, "2048"},
};

static int tileLabelIndex(int value) {
    for (size_t i = 0; i < sizeof(kTileLabels) / sizeof(kTileLabels[0]); ++i) {
        if (kTileLabels[i].value == value) {
            return static_cast<int>(i);
        }
    }
    return 0;
}
class VulkanApp {
public:
    void run() {
        tileMode = g_tileMode;
        trace("Startup: initializing window");
        initWindow();
        trace("Startup: initializing Vulkan");
        initVulkan();
        trace("Main loop: running");
        mainLoop();
        trace("Shutdown: cleaning up");
        cleanup();
    }

    void init() {
        tileMode = g_tileMode;
        externalInstanceMode = g_externalInstanceMode;
        externalInstanceCapacity = g_externalInstanceCapacity;
        trace("Startup: initializing window");
        initWindow();
        trace("Startup: initializing Vulkan");
        initVulkan();
    }

    void shutdown() {
        trace("Shutdown: cleaning up");
        cleanup();
    }

    void waitIdle() {
        if (device != VK_NULL_HANDLE) {
            vkDeviceWaitIdle(device);
        }
    }

    bool shouldClose() const {
        return window && glfwWindowShouldClose(window);
    }

    void poll() {
        if (window) {
            glfwPollEvents();
        }
    }

    void renderExternal(const float* instanceData, uint32_t count) {
        if (!externalInstanceMode) {
            return;
        }
        updateExternalInstanceBuffer(instanceData, count);
        drawFrame();
    }

    void uploadExternalTexture(const uint8_t* pixels, int width, int height) {
        if (!externalInstanceMode) {
            return;
        }
        uploadTexturePixels(width, height, pixels);
        createTextureImageView();
        textureImage2 = textureImage;
        textureImageMemory2 = textureImageMemory;
        textureImageView2 = textureImageView;
        createDescriptorSets();
    }

    int keyDown(int key) const {
        if (!window) {
            return 0;
        }
        return glfwGetKey(window, key) == GLFW_PRESS ? 1 : 0;
    }

private:
    GLFWwindow* window = nullptr;
    bool tileMode = false;
    bool tileInited = false;
    bool keyLeftDown = false;
    bool keyRightDown = false;
    bool keyUpDown = false;
    bool keyDownDown = false;
    bool keyRestartDown = false;
    std::array<int32_t, 16> tileValues{};
    std::array<int32_t, 16> tileBoard{};
    int32_t tileScore = 0;
    int32_t tileRng = 1;
    float tileSize = 0.0f;
    float tileGap = 0.0f;
    int tileAtlasCols = 1;
    float tileAtlasU = 1.0f;
    float tileAtlasV = 1.0f;
    float tileAtlasPad = 2.0f;
    float tileAtlasCell = 64.0f;
    bool instanceBufferHostVisible = false;
    bool externalInstanceMode = false;
    uint32_t externalInstanceCount = 0;
    uint32_t externalInstanceCapacity = 0;

    VkInstance instance = VK_NULL_HANDLE;
    VkDebugUtilsMessengerEXT debugMessenger = VK_NULL_HANDLE;
    VkSurfaceKHR surface = VK_NULL_HANDLE;

    VkPhysicalDevice physicalDevice = VK_NULL_HANDLE;
    VkDevice device = VK_NULL_HANDLE;

    VkQueue graphicsQueue = VK_NULL_HANDLE;
    VkQueue presentQueue = VK_NULL_HANDLE;

    VkSwapchainKHR swapChain = VK_NULL_HANDLE;
    std::vector<VkImage> swapChainImages;
    VkFormat swapChainImageFormat = VK_FORMAT_UNDEFINED;
    VkExtent2D swapChainExtent{};
    std::vector<VkImageView> swapChainImageViews;

    VkRenderPass renderPass = VK_NULL_HANDLE;
    VkDescriptorSetLayout descriptorSetLayout = VK_NULL_HANDLE;
    VkPipelineLayout pipelineLayout = VK_NULL_HANDLE;
    VkPipeline graphicsPipeline = VK_NULL_HANDLE;

    std::vector<VkFramebuffer> swapChainFramebuffers;

    VkCommandPool commandPool = VK_NULL_HANDLE;
    std::vector<VkCommandBuffer> commandBuffers;

    VkBuffer vertexBuffer = VK_NULL_HANDLE;
    VkDeviceMemory vertexBufferMemory = VK_NULL_HANDLE;
    VkBuffer indexBuffer = VK_NULL_HANDLE;
    VkDeviceMemory indexBufferMemory = VK_NULL_HANDLE;
    VkBuffer instanceBuffer = VK_NULL_HANDLE;
    VkDeviceMemory instanceBufferMemory = VK_NULL_HANDLE;

    std::vector<VkBuffer> uniformBuffers;
    std::vector<VkDeviceMemory> uniformBuffersMemory;

    VkDescriptorPool descriptorPool = VK_NULL_HANDLE;
    std::vector<VkDescriptorSet> descriptorSets;

    VkImage textureImage = VK_NULL_HANDLE;
    VkDeviceMemory textureImageMemory = VK_NULL_HANDLE;
    VkImageView textureImageView = VK_NULL_HANDLE;
    VkSampler textureSampler = VK_NULL_HANDLE;
    int textureWidth = 0;
    int textureHeight = 0;

    VkImage textureImage2 = VK_NULL_HANDLE;
    VkDeviceMemory textureImageMemory2 = VK_NULL_HANDLE;
    VkImageView textureImageView2 = VK_NULL_HANDLE;

    VkImage depthImage = VK_NULL_HANDLE;
    VkDeviceMemory depthImageMemory = VK_NULL_HANDLE;
    VkImageView depthImageView = VK_NULL_HANDLE;

    std::vector<Vertex> vertices;
    std::vector<uint16_t> indices;
    std::vector<MeshRange> meshes;
    uint32_t instanceCount = 0;
    float instanceSpan = 0.0f;
    float cameraDistance = 2.5f;
    float cameraPitch = 0.3f;
    float cameraYaw = 0.6f;
    float targetCameraDistance = 2.5f;
    float targetCameraPitch = 0.3f;
    float targetCameraYaw = 0.6f;
    double lastFrameTime = 0.0;

    std::vector<VkSemaphore> imageAvailableSemaphores;
    std::vector<VkSemaphore> renderFinishedSemaphores;
    std::vector<VkFence> inFlightFences;
    std::vector<VkFence> imagesInFlight;
    size_t currentFrame = 0;

    void initWindow() {
        if (!glfwInit()) {
            throw std::runtime_error("failed to init GLFW");
        }
        if (!glfwVulkanSupported()) {
            glfwTerminate();
            throw std::runtime_error("GLFW reports Vulkan is not supported (check Vulkan loader/install)");
        }
        int windowPosX = 0;
        int windowPosY = 0;
        if (externalInstanceMode) {
            uint32_t side = std::min(g_config.width, g_config.height);
            GLFWmonitor* monitor = glfwGetPrimaryMonitor();
            const GLFWvidmode* mode = monitor ? glfwGetVideoMode(monitor) : nullptr;
            if (mode) {
                side = static_cast<uint32_t>(std::min(mode->width, mode->height) / 4);
            }
            if (side == 0) {
                side = 225;
            }
            side = static_cast<uint32_t>((side * 9) / 10);
            g_config.width = side;
            g_config.height = side;
            if (mode) {
                windowPosX = (mode->width - static_cast<int>(g_config.width)) / 2;
                windowPosY = (mode->height - static_cast<int>(g_config.height)) / 2;
            }
        }
        glfwWindowHint(GLFW_CLIENT_API, GLFW_NO_API);
        glfwWindowHint(GLFW_RESIZABLE, GLFW_FALSE);
        window = glfwCreateWindow(g_config.width, g_config.height, g_config.title.c_str(), nullptr, nullptr);
        if (!window) {
            glfwTerminate();
            throw std::runtime_error("failed to create GLFW window");
        }
        glfwSetWindowUserPointer(window, this);
        if (externalInstanceMode && (windowPosX != 0 || windowPosY != 0)) {
            glfwSetWindowPos(window, windowPosX, windowPosY);
        }
        glfwSetScrollCallback(window, [](GLFWwindow* win, double /*xoff*/, double yoff) {
            (void)win;
            g_scrollDelta += yoff;
        });
    }

    void initVulkan() {
        ensureShadersBuilt();
        trace("Init: create instance");
        createInstance();
        trace("Init: setup debug messenger");
        setupDebugMessenger();
        trace("Init: create surface");
        createSurface();
        trace("Init: pick physical device");
        pickPhysicalDevice();
        trace("Init: create logical device");
        createLogicalDevice();
        trace("Init: create swapchain");
        createSwapChain();
        trace("Init: create image views");
        createImageViews();
        trace("Init: create render pass");
        createRenderPass();
        trace("Init: create descriptor set layout");
        createDescriptorSetLayout();
        trace("Init: create graphics pipeline");
        createGraphicsPipeline();
        trace("Init: create command pool");
        createCommandPool();
        trace("Init: create depth resources");
        createDepthResources();
        trace("Init: create framebuffers");
        createFramebuffers();
        trace("Init: create texture");
        createTextureImage();
        createTextureImageView();
        createTextureImage2();
        createTextureImageView2();
        createTextureSampler();
        cameraDistance = g_config.cameraDistance;
        cameraPitch = g_config.cameraPitch;
        cameraYaw = g_config.cameraYaw;
        targetCameraDistance = cameraDistance;
        targetCameraPitch = cameraPitch;
        targetCameraYaw = cameraYaw;
        lastFrameTime = glfwGetTime();
        trace("Init: build mesh/instance data");
        buildMeshData();
        buildInstanceData();
        trace("Init: create vertex/index buffers");
        createVertexBuffer();
        createIndexBuffer();
        createInstanceBuffer();
        trace("Init: create uniform buffers");
        createUniformBuffers();
        trace("Init: create descriptor pool/sets");
        createDescriptorPool();
        createDescriptorSets();
        trace("Init: allocate command buffers");
        createCommandBuffers();
        trace("Init: create sync objects");
        createSyncObjects();
    }

    void mainLoop() {
#ifndef FLOW_VK_STANDALONE
        if (tileMode && !tileInited) {
            flow_2048_init_ptr_i32_ptr_i32_ptr_i32(tileBoard.data(), &tileScore, &tileRng);
            std::memcpy(tileValues.data(), tileBoard.data(), sizeof(int32_t) * tileBoard.size());
            tileInited = true;
        }
#endif
        while (!glfwWindowShouldClose(window)) {
            glfwPollEvents();
            if (tileMode) {
                handleTileInput();
#ifndef FLOW_VK_STANDALONE
                std::memcpy(tileValues.data(), tileBoard.data(), sizeof(int32_t) * tileBoard.size());
#endif
                updateTileInstanceBuffer();
            } else {
                handleInput();
            }
            drawFrame();
        }
        trace("Shutdown: waiting for device idle");
        vkDeviceWaitIdle(device);
    }

    void cleanupSwapChain() {
        for (auto framebuffer : swapChainFramebuffers) {
            vkDestroyFramebuffer(device, framebuffer, nullptr);
        }
        if (depthImageView) {
            vkDestroyImageView(device, depthImageView, nullptr);
        }
        if (depthImage) {
            vkDestroyImage(device, depthImage, nullptr);
        }
        if (depthImageMemory) {
            vkFreeMemory(device, depthImageMemory, nullptr);
        }
        for (auto imageView : swapChainImageViews) {
            vkDestroyImageView(device, imageView, nullptr);
        }
        vkDestroySwapchainKHR(device, swapChain, nullptr);
    }

    void cleanup() {
        trace("Shutdown: destroy swapchain resources");
        cleanupSwapChain();

        vkDestroySampler(device, textureSampler, nullptr);
        vkDestroyImageView(device, textureImageView, nullptr);
        vkDestroyImage(device, textureImage, nullptr);
        vkFreeMemory(device, textureImageMemory, nullptr);

        if (textureImage2 && textureImage2 != textureImage) {
            vkDestroyImageView(device, textureImageView2, nullptr);
            vkDestroyImage(device, textureImage2, nullptr);
            vkFreeMemory(device, textureImageMemory2, nullptr);
        }

        vkDestroyDescriptorPool(device, descriptorPool, nullptr);
        vkDestroyDescriptorSetLayout(device, descriptorSetLayout, nullptr);

        for (size_t i = 0; i < uniformBuffers.size(); ++i) {
            vkDestroyBuffer(device, uniformBuffers[i], nullptr);
            vkFreeMemory(device, uniformBuffersMemory[i], nullptr);
        }

        vkDestroyBuffer(device, indexBuffer, nullptr);
        vkFreeMemory(device, indexBufferMemory, nullptr);

        vkDestroyBuffer(device, instanceBuffer, nullptr);
        vkFreeMemory(device, instanceBufferMemory, nullptr);

        vkDestroyBuffer(device, vertexBuffer, nullptr);
        vkFreeMemory(device, vertexBufferMemory, nullptr);

        trace("Shutdown: destroy pipeline and render pass");
        vkDestroyPipeline(device, graphicsPipeline, nullptr);
        vkDestroyPipelineLayout(device, pipelineLayout, nullptr);
        vkDestroyRenderPass(device, renderPass, nullptr);

        trace("Shutdown: destroy sync objects");
        for (size_t i = 0; i < imageAvailableSemaphores.size(); ++i) {
            vkDestroySemaphore(device, imageAvailableSemaphores[i], nullptr);
            vkDestroyFence(device, inFlightFences[i], nullptr);
        }
        for (size_t i = 0; i < renderFinishedSemaphores.size(); ++i) {
            vkDestroySemaphore(device, renderFinishedSemaphores[i], nullptr);
        }

        trace("Shutdown: destroy command pool");
        vkDestroyCommandPool(device, commandPool, nullptr);
        trace("Shutdown: destroy device");
        vkDestroyDevice(device, nullptr);

        if (validationLayersEnabled()) {
            trace("Shutdown: destroy debug messenger");
            destroyDebugUtilsMessengerEXT(instance, debugMessenger, nullptr);
        }

        trace("Shutdown: destroy surface and instance");
        vkDestroySurfaceKHR(instance, surface, nullptr);
        vkDestroyInstance(instance, nullptr);

        trace("Shutdown: destroy window");
        glfwDestroyWindow(window);
        glfwTerminate();
        trace("Shutdown: complete");
    }

    void createInstance() {
        if (validationLayersEnabled() && !checkValidationLayerSupport()) {
            throw std::runtime_error("validation layers requested, but not available");
        }

        VkApplicationInfo appInfo{};
        appInfo.sType = VK_STRUCTURE_TYPE_APPLICATION_INFO;
        appInfo.pApplicationName = "Vulkan Scene";
        appInfo.applicationVersion = VK_MAKE_VERSION(1, 0, 0);
        appInfo.pEngineName = "No Engine";
        appInfo.engineVersion = VK_MAKE_VERSION(1, 0, 0);
        appInfo.apiVersion = VK_API_VERSION_1_2;

        VkInstanceCreateInfo createInfo{};
        createInfo.sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO;
        createInfo.pApplicationInfo = &appInfo;

        auto extensions = getRequiredExtensions();
        createInfo.enabledExtensionCount = static_cast<uint32_t>(extensions.size());
        createInfo.ppEnabledExtensionNames = extensions.data();

        VkDebugUtilsMessengerCreateInfoEXT debugCreateInfo{};
        if (validationLayersEnabled()) {
            createInfo.enabledLayerCount = static_cast<uint32_t>(kValidationLayers.size());
            createInfo.ppEnabledLayerNames = kValidationLayers.data();
            populateDebugMessengerCreateInfo(debugCreateInfo);
            createInfo.pNext = &debugCreateInfo;
        } else {
            createInfo.enabledLayerCount = 0;
            createInfo.pNext = nullptr;
        }

#ifdef __APPLE__
#ifndef VK_INSTANCE_CREATE_ENUMERATE_PORTABILITY_BIT_KHR
#define VK_INSTANCE_CREATE_ENUMERATE_PORTABILITY_BIT_KHR 0x00000001
#endif
        createInfo.flags |= VK_INSTANCE_CREATE_ENUMERATE_PORTABILITY_BIT_KHR;
#elif defined(VK_INSTANCE_CREATE_ENUMERATE_PORTABILITY_BIT_KHR)
        createInfo.flags |= VK_INSTANCE_CREATE_ENUMERATE_PORTABILITY_BIT_KHR;
#endif

        if (vkCreateInstance(&createInfo, nullptr, &instance) != VK_SUCCESS) {
            throw std::runtime_error("failed to create instance");
        }
    }

    void createSurface() {
        VkResult result = glfwCreateWindowSurface(instance, window, nullptr, &surface);
        if (result != VK_SUCCESS) {
            const char* glfwError = nullptr;
            glfwGetError(&glfwError);
            std::string msg = "failed to create window surface";
            if (glfwError && *glfwError) {
                msg += ": ";
                msg += glfwError;
            }
            throw std::runtime_error(msg);
        }
    }

    void pickPhysicalDevice() {
        uint32_t deviceCount = 0;
        vkEnumeratePhysicalDevices(instance, &deviceCount, nullptr);
        if (deviceCount == 0) {
            throw std::runtime_error("failed to find GPUs with Vulkan support");
        }
        std::vector<VkPhysicalDevice> devices(deviceCount);
        vkEnumeratePhysicalDevices(instance, &deviceCount, devices.data());
        for (const auto& dev : devices) {
            if (isDeviceSuitable(dev)) {
                physicalDevice = dev;
                break;
            }
        }
        if (physicalDevice == VK_NULL_HANDLE) {
            throw std::runtime_error("failed to find a suitable GPU");
        }
    }

    void createLogicalDevice() {
        QueueFamilyIndices indices = findQueueFamilies(physicalDevice);

        std::vector<VkDeviceQueueCreateInfo> queueCreateInfos;
        std::set<uint32_t> uniqueQueueFamilies = {
            indices.graphicsFamily.value(),
            indices.presentFamily.value(),
        };

        float queuePriority = 1.0f;
        for (uint32_t queueFamily : uniqueQueueFamilies) {
            VkDeviceQueueCreateInfo queueCreateInfo{};
            queueCreateInfo.sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO;
            queueCreateInfo.queueFamilyIndex = queueFamily;
            queueCreateInfo.queueCount = 1;
            queueCreateInfo.pQueuePriorities = &queuePriority;
            queueCreateInfos.push_back(queueCreateInfo);
        }

        VkPhysicalDeviceFeatures deviceFeatures{};

        VkDeviceCreateInfo createInfo{};
        createInfo.sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO;
        createInfo.queueCreateInfoCount = static_cast<uint32_t>(queueCreateInfos.size());
        createInfo.pQueueCreateInfos = queueCreateInfos.data();
        createInfo.pEnabledFeatures = &deviceFeatures;

        std::vector<const char*> deviceExtensions = kDeviceExtensions;
        if (supportsExtension(physicalDevice, "VK_KHR_portability_subset")) {
            deviceExtensions.push_back("VK_KHR_portability_subset");
        }

        createInfo.enabledExtensionCount = static_cast<uint32_t>(deviceExtensions.size());
        createInfo.ppEnabledExtensionNames = deviceExtensions.data();

        if (validationLayersEnabled()) {
            createInfo.enabledLayerCount = static_cast<uint32_t>(kValidationLayers.size());
            createInfo.ppEnabledLayerNames = kValidationLayers.data();
        } else {
            createInfo.enabledLayerCount = 0;
        }

        if (vkCreateDevice(physicalDevice, &createInfo, nullptr, &device) != VK_SUCCESS) {
            throw std::runtime_error("failed to create logical device");
        }

        vkGetDeviceQueue(device, indices.graphicsFamily.value(), 0, &graphicsQueue);
        vkGetDeviceQueue(device, indices.presentFamily.value(), 0, &presentQueue);
    }

    void createSwapChain() {
        SwapChainSupportDetails details = querySwapChainSupport(physicalDevice);

        VkSurfaceFormatKHR surfaceFormat = chooseSwapSurfaceFormat(details.formats);
        VkPresentModeKHR presentMode = chooseSwapPresentMode(details.presentModes);
        VkExtent2D extent = chooseSwapExtent(details.capabilities);

        uint32_t imageCount = details.capabilities.minImageCount + 1;
        if (details.capabilities.maxImageCount > 0 && imageCount > details.capabilities.maxImageCount) {
            imageCount = details.capabilities.maxImageCount;
        }

        VkSwapchainCreateInfoKHR createInfo{};
        createInfo.sType = VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR;
        createInfo.surface = surface;
        createInfo.minImageCount = imageCount;
        createInfo.imageFormat = surfaceFormat.format;
        createInfo.imageColorSpace = surfaceFormat.colorSpace;
        createInfo.imageExtent = extent;
        createInfo.imageArrayLayers = 1;
        createInfo.imageUsage = VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT;

        QueueFamilyIndices indices = findQueueFamilies(physicalDevice);
        uint32_t queueFamilyIndices[] = {indices.graphicsFamily.value(), indices.presentFamily.value()};
        if (indices.graphicsFamily != indices.presentFamily) {
            createInfo.imageSharingMode = VK_SHARING_MODE_CONCURRENT;
            createInfo.queueFamilyIndexCount = 2;
            createInfo.pQueueFamilyIndices = queueFamilyIndices;
        } else {
            createInfo.imageSharingMode = VK_SHARING_MODE_EXCLUSIVE;
            createInfo.queueFamilyIndexCount = 0;
            createInfo.pQueueFamilyIndices = nullptr;
        }

        createInfo.preTransform = details.capabilities.currentTransform;
        createInfo.compositeAlpha = VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR;
        createInfo.presentMode = presentMode;
        createInfo.clipped = VK_TRUE;
        createInfo.oldSwapchain = VK_NULL_HANDLE;

        if (vkCreateSwapchainKHR(device, &createInfo, nullptr, &swapChain) != VK_SUCCESS) {
            throw std::runtime_error("failed to create swap chain");
        }

        vkGetSwapchainImagesKHR(device, swapChain, &imageCount, nullptr);
        swapChainImages.resize(imageCount);
        vkGetSwapchainImagesKHR(device, swapChain, &imageCount, swapChainImages.data());

        swapChainImageFormat = surfaceFormat.format;
        swapChainExtent = extent;
    }

    void createImageViews() {
        swapChainImageViews.resize(swapChainImages.size());
        for (size_t i = 0; i < swapChainImages.size(); ++i) {
            swapChainImageViews[i] = createImageView(swapChainImages[i], swapChainImageFormat, VK_IMAGE_ASPECT_COLOR_BIT);
        }
    }

    void createRenderPass() {
        VkAttachmentDescription colorAttachment{};
        colorAttachment.format = swapChainImageFormat;
        colorAttachment.samples = VK_SAMPLE_COUNT_1_BIT;
        colorAttachment.loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR;
        colorAttachment.storeOp = VK_ATTACHMENT_STORE_OP_STORE;
        colorAttachment.stencilLoadOp = VK_ATTACHMENT_LOAD_OP_DONT_CARE;
        colorAttachment.stencilStoreOp = VK_ATTACHMENT_STORE_OP_DONT_CARE;
        colorAttachment.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;
        colorAttachment.finalLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR;

        VkAttachmentDescription depthAttachment{};
        depthAttachment.format = findDepthFormat();
        depthAttachment.samples = VK_SAMPLE_COUNT_1_BIT;
        depthAttachment.loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR;
        depthAttachment.storeOp = VK_ATTACHMENT_STORE_OP_DONT_CARE;
        depthAttachment.stencilLoadOp = VK_ATTACHMENT_LOAD_OP_DONT_CARE;
        depthAttachment.stencilStoreOp = VK_ATTACHMENT_STORE_OP_DONT_CARE;
        depthAttachment.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;
        depthAttachment.finalLayout = VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL;

        VkAttachmentReference colorAttachmentRef{};
        colorAttachmentRef.attachment = 0;
        colorAttachmentRef.layout = VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL;

        VkAttachmentReference depthAttachmentRef{};
        depthAttachmentRef.attachment = 1;
        depthAttachmentRef.layout = VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL;

        VkSubpassDescription subpass{};
        subpass.pipelineBindPoint = VK_PIPELINE_BIND_POINT_GRAPHICS;
        subpass.colorAttachmentCount = 1;
        subpass.pColorAttachments = &colorAttachmentRef;
        subpass.pDepthStencilAttachment = &depthAttachmentRef;

        VkSubpassDependency dependency{};
        dependency.srcSubpass = VK_SUBPASS_EXTERNAL;
        dependency.dstSubpass = 0;
        dependency.srcStageMask = VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT | VK_PIPELINE_STAGE_EARLY_FRAGMENT_TESTS_BIT;
        dependency.srcAccessMask = 0;
        dependency.dstStageMask = VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT | VK_PIPELINE_STAGE_EARLY_FRAGMENT_TESTS_BIT;
        dependency.dstAccessMask = VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT | VK_ACCESS_DEPTH_STENCIL_ATTACHMENT_WRITE_BIT;

        std::array<VkAttachmentDescription, 2> attachments = {colorAttachment, depthAttachment};

        VkRenderPassCreateInfo renderPassInfo{};
        renderPassInfo.sType = VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO;
        renderPassInfo.attachmentCount = static_cast<uint32_t>(attachments.size());
        renderPassInfo.pAttachments = attachments.data();
        renderPassInfo.subpassCount = 1;
        renderPassInfo.pSubpasses = &subpass;
        renderPassInfo.dependencyCount = 1;
        renderPassInfo.pDependencies = &dependency;

        if (vkCreateRenderPass(device, &renderPassInfo, nullptr, &renderPass) != VK_SUCCESS) {
            throw std::runtime_error("failed to create render pass");
        }
    }

    void createDescriptorSetLayout() {
        VkDescriptorSetLayoutBinding uboLayoutBinding{};
        uboLayoutBinding.binding = 0;
        uboLayoutBinding.descriptorType = VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER;
        uboLayoutBinding.descriptorCount = 1;
        uboLayoutBinding.stageFlags = VK_SHADER_STAGE_VERTEX_BIT;

        VkDescriptorSetLayoutBinding samplerLayoutBinding{};
        samplerLayoutBinding.binding = 1;
        samplerLayoutBinding.descriptorType = VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER;
        samplerLayoutBinding.descriptorCount = 2;
        samplerLayoutBinding.stageFlags = VK_SHADER_STAGE_FRAGMENT_BIT;

        std::array<VkDescriptorSetLayoutBinding, 2> bindings = {uboLayoutBinding, samplerLayoutBinding};

        VkDescriptorSetLayoutCreateInfo layoutInfo{};
        layoutInfo.sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO;
        layoutInfo.bindingCount = static_cast<uint32_t>(bindings.size());
        layoutInfo.pBindings = bindings.data();

        if (vkCreateDescriptorSetLayout(device, &layoutInfo, nullptr, &descriptorSetLayout) != VK_SUCCESS) {
            throw std::runtime_error("failed to create descriptor set layout");
        }
    }

    void createGraphicsPipeline() {
        auto vertShaderCode = readFile("demos/vulkan_scene/shaders/scene.vert.spv");
        auto fragShaderCode = readFile("demos/vulkan_scene/shaders/scene.frag.spv");

        VkShaderModule vertShaderModule = createShaderModule(vertShaderCode);
        VkShaderModule fragShaderModule = createShaderModule(fragShaderCode);

        VkPipelineShaderStageCreateInfo vertShaderStageInfo{};
        vertShaderStageInfo.sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;
        vertShaderStageInfo.stage = VK_SHADER_STAGE_VERTEX_BIT;
        vertShaderStageInfo.module = vertShaderModule;
        vertShaderStageInfo.pName = "main";

        VkPipelineShaderStageCreateInfo fragShaderStageInfo{};
        fragShaderStageInfo.sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;
        fragShaderStageInfo.stage = VK_SHADER_STAGE_FRAGMENT_BIT;
        fragShaderStageInfo.module = fragShaderModule;
        fragShaderStageInfo.pName = "main";

        VkPipelineShaderStageCreateInfo shaderStages[] = {vertShaderStageInfo, fragShaderStageInfo};

        VkVertexInputBindingDescription bindingDescription{};
        bindingDescription.binding = 0;
        bindingDescription.stride = sizeof(Vertex);
        bindingDescription.inputRate = VK_VERTEX_INPUT_RATE_VERTEX;

        VkVertexInputBindingDescription instanceBinding{};
        instanceBinding.binding = 1;
        instanceBinding.stride = sizeof(InstanceData);
        instanceBinding.inputRate = VK_VERTEX_INPUT_RATE_INSTANCE;

        std::array<VkVertexInputAttributeDescription, 8> attributeDescriptions{};
        attributeDescriptions[0].binding = 0;
        attributeDescriptions[0].location = 0;
        attributeDescriptions[0].format = VK_FORMAT_R32G32B32_SFLOAT;
        attributeDescriptions[0].offset = offsetof(Vertex, pos);

        attributeDescriptions[1].binding = 0;
        attributeDescriptions[1].location = 1;
        attributeDescriptions[1].format = VK_FORMAT_R32G32B32_SFLOAT;
        attributeDescriptions[1].offset = offsetof(Vertex, color);

        attributeDescriptions[2].binding = 0;
        attributeDescriptions[2].location = 2;
        attributeDescriptions[2].format = VK_FORMAT_R32G32_SFLOAT;
        attributeDescriptions[2].offset = offsetof(Vertex, uv);

        attributeDescriptions[3].binding = 1;
        attributeDescriptions[3].location = 3;
        attributeDescriptions[3].format = VK_FORMAT_R32G32B32_SFLOAT;
        attributeDescriptions[3].offset = offsetof(InstanceData, offset);

        attributeDescriptions[4].binding = 1;
        attributeDescriptions[4].location = 4;
        attributeDescriptions[4].format = VK_FORMAT_R32_SFLOAT;
        attributeDescriptions[4].offset = offsetof(InstanceData, scale);
        attributeDescriptions[5].binding = 1;
        attributeDescriptions[5].location = 5;
        attributeDescriptions[5].format = VK_FORMAT_R32G32_SFLOAT;
        attributeDescriptions[5].offset = offsetof(InstanceData, uvOffset);
        attributeDescriptions[6].binding = 1;
        attributeDescriptions[6].location = 6;
        attributeDescriptions[6].format = VK_FORMAT_R32G32_SFLOAT;
        attributeDescriptions[6].offset = offsetof(InstanceData, uvScale);
        attributeDescriptions[7].binding = 1;
        attributeDescriptions[7].location = 7;
        attributeDescriptions[7].format = VK_FORMAT_R32G32B32A32_SFLOAT;
        attributeDescriptions[7].offset = offsetof(InstanceData, color);

        std::array<VkVertexInputBindingDescription, 2> bindings = {bindingDescription, instanceBinding};

        VkPipelineVertexInputStateCreateInfo vertexInputInfo{};
        vertexInputInfo.sType = VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO;
        vertexInputInfo.vertexBindingDescriptionCount = static_cast<uint32_t>(bindings.size());
        vertexInputInfo.pVertexBindingDescriptions = bindings.data();
        vertexInputInfo.vertexAttributeDescriptionCount = static_cast<uint32_t>(attributeDescriptions.size());
        vertexInputInfo.pVertexAttributeDescriptions = attributeDescriptions.data();

        VkPipelineInputAssemblyStateCreateInfo inputAssembly{};
        inputAssembly.sType = VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO;
        inputAssembly.topology = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST;
        inputAssembly.primitiveRestartEnable = VK_FALSE;

        VkViewport viewport{};
        viewport.x = 0.0f;
        viewport.y = 0.0f;
        viewport.width = static_cast<float>(swapChainExtent.width);
        viewport.height = static_cast<float>(swapChainExtent.height);
        viewport.minDepth = 0.0f;
        viewport.maxDepth = 1.0f;

        VkRect2D scissor{};
        scissor.offset = {0, 0};
        scissor.extent = swapChainExtent;

        VkPipelineViewportStateCreateInfo viewportState{};
        viewportState.sType = VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO;
        viewportState.viewportCount = 1;
        viewportState.pViewports = &viewport;
        viewportState.scissorCount = 1;
        viewportState.pScissors = &scissor;

        VkPipelineRasterizationStateCreateInfo rasterizer{};
        rasterizer.sType = VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO;
        rasterizer.depthClampEnable = VK_FALSE;
        rasterizer.rasterizerDiscardEnable = VK_FALSE;
        rasterizer.polygonMode = VK_POLYGON_MODE_FILL;
        rasterizer.lineWidth = 1.0f;
        rasterizer.cullMode = (tileMode || externalInstanceMode) ? VK_CULL_MODE_NONE : VK_CULL_MODE_BACK_BIT;
        rasterizer.frontFace = VK_FRONT_FACE_COUNTER_CLOCKWISE;
        rasterizer.depthBiasEnable = VK_FALSE;

        VkPipelineMultisampleStateCreateInfo multisampling{};
        multisampling.sType = VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO;
        multisampling.sampleShadingEnable = VK_FALSE;
        multisampling.rasterizationSamples = VK_SAMPLE_COUNT_1_BIT;

        VkPipelineDepthStencilStateCreateInfo depthStencil{};
        depthStencil.sType = VK_STRUCTURE_TYPE_PIPELINE_DEPTH_STENCIL_STATE_CREATE_INFO;
        depthStencil.depthTestEnable = VK_TRUE;
        depthStencil.depthWriteEnable = VK_TRUE;
        depthStencil.depthCompareOp = VK_COMPARE_OP_LESS;
        depthStencil.depthBoundsTestEnable = VK_FALSE;
        depthStencil.stencilTestEnable = VK_FALSE;

        VkPipelineColorBlendAttachmentState colorBlendAttachment{};
        colorBlendAttachment.colorWriteMask = VK_COLOR_COMPONENT_R_BIT | VK_COLOR_COMPONENT_G_BIT | VK_COLOR_COMPONENT_B_BIT | VK_COLOR_COMPONENT_A_BIT;
        colorBlendAttachment.blendEnable = VK_FALSE;

        VkPipelineColorBlendStateCreateInfo colorBlending{};
        colorBlending.sType = VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO;
        colorBlending.logicOpEnable = VK_FALSE;
        colorBlending.logicOp = VK_LOGIC_OP_COPY;
        colorBlending.attachmentCount = 1;
        colorBlending.pAttachments = &colorBlendAttachment;

        struct PushConstants {
            float color[4];
            int32_t texIndex;
            int32_t pad[3];
            float meshOffset[4];
        };

        VkPushConstantRange pushRange{};
        pushRange.stageFlags = VK_SHADER_STAGE_FRAGMENT_BIT | VK_SHADER_STAGE_VERTEX_BIT;
        pushRange.offset = 0;
        pushRange.size = sizeof(PushConstants);

        VkPipelineLayoutCreateInfo pipelineLayoutInfo{};
        pipelineLayoutInfo.sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO;
        pipelineLayoutInfo.setLayoutCount = 1;
        pipelineLayoutInfo.pSetLayouts = &descriptorSetLayout;
        pipelineLayoutInfo.pushConstantRangeCount = 1;
        pipelineLayoutInfo.pPushConstantRanges = &pushRange;

        if (vkCreatePipelineLayout(device, &pipelineLayoutInfo, nullptr, &pipelineLayout) != VK_SUCCESS) {
            throw std::runtime_error("failed to create pipeline layout");
        }

        VkGraphicsPipelineCreateInfo pipelineInfo{};
        pipelineInfo.sType = VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO;
        pipelineInfo.stageCount = 2;
        pipelineInfo.pStages = shaderStages;
        pipelineInfo.pVertexInputState = &vertexInputInfo;
        pipelineInfo.pInputAssemblyState = &inputAssembly;
        pipelineInfo.pViewportState = &viewportState;
        pipelineInfo.pRasterizationState = &rasterizer;
        pipelineInfo.pMultisampleState = &multisampling;
        pipelineInfo.pDepthStencilState = &depthStencil;
        pipelineInfo.pColorBlendState = &colorBlending;
        pipelineInfo.layout = pipelineLayout;
        pipelineInfo.renderPass = renderPass;
        pipelineInfo.subpass = 0;

        if (vkCreateGraphicsPipelines(device, VK_NULL_HANDLE, 1, &pipelineInfo, nullptr, &graphicsPipeline) != VK_SUCCESS) {
            throw std::runtime_error("failed to create graphics pipeline");
        }

        vkDestroyShaderModule(device, fragShaderModule, nullptr);
        vkDestroyShaderModule(device, vertShaderModule, nullptr);
    }

    void createFramebuffers() {
        swapChainFramebuffers.resize(swapChainImageViews.size());
        for (size_t i = 0; i < swapChainImageViews.size(); ++i) {
            std::array<VkImageView, 2> attachments = {swapChainImageViews[i], depthImageView};

            VkFramebufferCreateInfo framebufferInfo{};
            framebufferInfo.sType = VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO;
            framebufferInfo.renderPass = renderPass;
            framebufferInfo.attachmentCount = static_cast<uint32_t>(attachments.size());
            framebufferInfo.pAttachments = attachments.data();
            framebufferInfo.width = swapChainExtent.width;
            framebufferInfo.height = swapChainExtent.height;
            framebufferInfo.layers = 1;

            if (vkCreateFramebuffer(device, &framebufferInfo, nullptr, &swapChainFramebuffers[i]) != VK_SUCCESS) {
                throw std::runtime_error("failed to create framebuffer");
            }
        }
    }

    void createCommandPool() {
        QueueFamilyIndices queueFamilyIndices = findQueueFamilies(physicalDevice);

        VkCommandPoolCreateInfo poolInfo{};
        poolInfo.sType = VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO;
        poolInfo.flags = VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;
        poolInfo.queueFamilyIndex = queueFamilyIndices.graphicsFamily.value();

        if (vkCreateCommandPool(device, &poolInfo, nullptr, &commandPool) != VK_SUCCESS) {
            throw std::runtime_error("failed to create command pool");
        }
    }

    void createDepthResources() {
        VkFormat depthFormat = findDepthFormat();
        createImage(swapChainExtent.width, swapChainExtent.height, depthFormat,
                    VK_IMAGE_TILING_OPTIMAL,
                    VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT,
                    VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT,
                    depthImage, depthImageMemory);
        depthImageView = createImageView(depthImage, depthFormat, VK_IMAGE_ASPECT_DEPTH_BIT);
    }

    void createTextureImage() {
        int texWidth = 2;
        int texHeight = 2;
        std::vector<uint8_t> pixels;

        if (tileMode || externalInstanceMode) {
            const int cell = 64;
            tileAtlasCell = static_cast<float>(cell);
            tileAtlasPad = 2.0f;
            tileAtlasCols = static_cast<int>(sizeof(kTileLabels) / sizeof(kTileLabels[0]));
            tileAtlasU = 1.0f / static_cast<float>(tileAtlasCols);
            tileAtlasV = 1.0f;
            texWidth = cell * tileAtlasCols;
            texHeight = cell;
            pixels.assign(static_cast<size_t>(texWidth) * texHeight * 4, 0);
#ifdef __APPLE__
            CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
            CGContextRef ctx = CGBitmapContextCreate(
                pixels.data(), texWidth, texHeight, 8, texWidth * 4,
                colorSpace, kCGImageAlphaPremultipliedLast | kCGBitmapByteOrder32Big
            );
            if (ctx) {
                CGContextSetRGBFillColor(ctx, 0, 0, 0, 0);
                CGContextFillRect(ctx, CGRectMake(0, 0, texWidth, texHeight));

                CTFontRef font = CTFontCreateWithName(CFSTR("Helvetica Neue Bold"), cell * 0.6, nullptr);
                if (font) {
                    for (int i = 0; i < tileAtlasCols; ++i) {
                        const char* text = kTileLabels[i].text;
                        if (!text || text[0] == '\0') {
                            continue;
                        }
                        CFStringRef cfText = CFStringCreateWithCString(kCFAllocatorDefault, text, kCFStringEncodingUTF8);
                        if (!cfText) continue;
                        CFMutableDictionaryRef attrs = CFDictionaryCreateMutable(kCFAllocatorDefault, 0,
                                                                                &kCFTypeDictionaryKeyCallBacks,
                                                                                &kCFTypeDictionaryValueCallBacks);
                        CFDictionarySetValue(attrs, kCTFontAttributeName, font);
                        CFDictionarySetValue(attrs, kCTForegroundColorFromContextAttributeName, kCFBooleanTrue);
                        CFAttributedStringRef attrStr = CFAttributedStringCreate(kCFAllocatorDefault, cfText, attrs);
                        CTLineRef line = CTLineCreateWithAttributedString(attrStr);
                        CFRelease(attrStr);
                        CFRelease(attrs);
                        CFRelease(cfText);

                        CGRect bounds = CTLineGetBoundsWithOptions(line, kCTLineBoundsUseOpticalBounds);
                        float textW = bounds.size.width;
                        float textH = bounds.size.height;
                        float x = i * cell + (cell - textW) * 0.5f - bounds.origin.x;
                        float y = (cell - textH) * 0.5f - bounds.origin.y;

                        CGContextSaveGState(ctx);
                        CGContextTranslateCTM(ctx, 0, texHeight);
                        CGContextScaleCTM(ctx, 1, -1);
                        CGContextSetRGBFillColor(ctx, 1, 1, 1, 1);
                        CGContextSetTextPosition(ctx, x, texHeight - cell + y);
                        CTLineDraw(line, ctx);
                        CGContextRestoreGState(ctx);

                        CFRelease(line);
                    }
                    CFRelease(font);
                }
                CGContextRelease(ctx);
            }
            CGColorSpaceRelease(colorSpace);
#endif
        } else {
        if (g_config.texturePath == "__PICK__") {
            g_config.texturePath = pickFileDialog("Select texture");
        }
        if (!g_config.texturePath.empty()) {
#ifdef __APPLE__
            CFURLRef url = CFURLCreateFromFileSystemRepresentation(
                kCFAllocatorDefault,
                reinterpret_cast<const UInt8*>(g_config.texturePath.c_str()),
                g_config.texturePath.size(),
                false
            );
            if (url) {
                CGImageSourceRef source = CGImageSourceCreateWithURL(url, nullptr);
                if (source) {
                    CGImageRef image = CGImageSourceCreateImageAtIndex(source, 0, nullptr);
                    if (image) {
                        texWidth = static_cast<int>(CGImageGetWidth(image));
                        texHeight = static_cast<int>(CGImageGetHeight(image));
                        pixels.resize(static_cast<size_t>(texWidth) * texHeight * 4);
                        CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
                        CGContextRef context = CGBitmapContextCreate(
                            pixels.data(), texWidth, texHeight, 8, texWidth * 4,
                            colorSpace, kCGImageAlphaPremultipliedLast | kCGBitmapByteOrder32Big
                        );
                        if (context) {
                            CGContextDrawImage(context, CGRectMake(0, 0, texWidth, texHeight), image);
                            CGContextRelease(context);
                        }
                        CGColorSpaceRelease(colorSpace);
                        CGImageRelease(image);
                    }
                    CFRelease(source);
                }
                CFRelease(url);
            }
#endif
        }
        }

        if (pixels.empty()) {
            makeMissingTexture(texWidth, texHeight, pixels);
        }

        uploadTexturePixels(texWidth, texHeight, pixels.data());
    }

    void uploadTexturePixels(int texWidth, int texHeight, const uint8_t* pixels) {
        if (texWidth <= 0 || texHeight <= 0 || pixels == nullptr) {
            throw std::runtime_error("invalid texture upload");
        }

        bool needRecreate = (textureImage == VK_NULL_HANDLE) ||
                            (texWidth != textureWidth) ||
                            (texHeight != textureHeight);

        VkDeviceSize imageSize = static_cast<VkDeviceSize>(texWidth) * texHeight * 4;

        VkBuffer stagingBuffer;
        VkDeviceMemory stagingBufferMemory;
        createBuffer(imageSize, VK_BUFFER_USAGE_TRANSFER_SRC_BIT,
                     VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT,
                     stagingBuffer, stagingBufferMemory);

        void* data;
        vkMapMemory(device, stagingBufferMemory, 0, imageSize, 0, &data);
        std::memcpy(data, pixels, static_cast<size_t>(imageSize));
        vkUnmapMemory(device, stagingBufferMemory);

        if (needRecreate) {
            if (textureImageView) {
                vkDestroyImageView(device, textureImageView, nullptr);
                textureImageView = VK_NULL_HANDLE;
            }
            if (textureImageView2 && textureImageView2 != textureImageView) {
                vkDestroyImageView(device, textureImageView2, nullptr);
            }
            textureImageView2 = VK_NULL_HANDLE;
            if (textureImage) {
                vkDestroyImage(device, textureImage, nullptr);
                textureImage = VK_NULL_HANDLE;
            }
            if (textureImageMemory) {
                vkFreeMemory(device, textureImageMemory, nullptr);
                textureImageMemory = VK_NULL_HANDLE;
            }
            if (textureImage2) {
                textureImage2 = VK_NULL_HANDLE;
                textureImageMemory2 = VK_NULL_HANDLE;
            }

            createImage(texWidth, texHeight, VK_FORMAT_R8G8B8A8_UNORM,
                        VK_IMAGE_TILING_OPTIMAL,
                        VK_IMAGE_USAGE_TRANSFER_DST_BIT | VK_IMAGE_USAGE_SAMPLED_BIT,
                        VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT,
                        textureImage, textureImageMemory);
            transitionImageLayout(textureImage, VK_FORMAT_R8G8B8A8_UNORM,
                                  VK_IMAGE_LAYOUT_UNDEFINED, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);
        } else {
            transitionImageLayout(textureImage, VK_FORMAT_R8G8B8A8_UNORM,
                                  VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);
        }

        copyBufferToImage(stagingBuffer, textureImage, texWidth, texHeight);
        transitionImageLayout(textureImage, VK_FORMAT_R8G8B8A8_UNORM,
                              VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);

        vkDestroyBuffer(device, stagingBuffer, nullptr);
        vkFreeMemory(device, stagingBufferMemory, nullptr);

        textureWidth = texWidth;
        textureHeight = texHeight;
    }

    void createTextureImage2() {
        if (g_config.texturePath2 == "__PICK__") {
            g_config.texturePath2 = pickFileDialog("Select second texture");
        }
        if (g_config.texturePath2.empty()) {
            textureImage2 = textureImage;
            textureImageMemory2 = textureImageMemory;
            textureImageView2 = textureImageView;
            return;
        }

        int texWidth = 2;
        int texHeight = 2;
        std::vector<uint8_t> pixels;

#ifdef __APPLE__
        CFURLRef url = CFURLCreateFromFileSystemRepresentation(
            kCFAllocatorDefault,
            reinterpret_cast<const UInt8*>(g_config.texturePath2.c_str()),
            g_config.texturePath2.size(),
            false
        );
        if (url) {
            CGImageSourceRef source = CGImageSourceCreateWithURL(url, nullptr);
            if (source) {
                CGImageRef image = CGImageSourceCreateImageAtIndex(source, 0, nullptr);
                if (image) {
                    texWidth = static_cast<int>(CGImageGetWidth(image));
                    texHeight = static_cast<int>(CGImageGetHeight(image));
                    pixels.resize(static_cast<size_t>(texWidth) * texHeight * 4);
                    CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
                    CGContextRef context = CGBitmapContextCreate(
                        pixels.data(), texWidth, texHeight, 8, texWidth * 4,
                        colorSpace, kCGImageAlphaPremultipliedLast | kCGBitmapByteOrder32Big
                    );
                    if (context) {
                        CGContextDrawImage(context, CGRectMake(0, 0, texWidth, texHeight), image);
                        CGContextRelease(context);
                    }
                    CGColorSpaceRelease(colorSpace);
                    CGImageRelease(image);
                }
                CFRelease(source);
            }
            CFRelease(url);
        }
#endif

        if (pixels.empty()) {
            makeMissingTexture(texWidth, texHeight, pixels);
        }

        VkDeviceSize imageSize = static_cast<VkDeviceSize>(texWidth) * texHeight * 4;

        VkBuffer stagingBuffer;
        VkDeviceMemory stagingBufferMemory;
        createBuffer(imageSize, VK_BUFFER_USAGE_TRANSFER_SRC_BIT,
                     VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT,
                     stagingBuffer, stagingBufferMemory);

        void* data;
        vkMapMemory(device, stagingBufferMemory, 0, imageSize, 0, &data);
        std::memcpy(data, pixels.data(), static_cast<size_t>(imageSize));
        vkUnmapMemory(device, stagingBufferMemory);

        createImage(texWidth, texHeight, VK_FORMAT_R8G8B8A8_UNORM,
                    VK_IMAGE_TILING_OPTIMAL,
                    VK_IMAGE_USAGE_TRANSFER_DST_BIT | VK_IMAGE_USAGE_SAMPLED_BIT,
                    VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT,
                    textureImage2, textureImageMemory2);

        transitionImageLayout(textureImage2, VK_FORMAT_R8G8B8A8_UNORM,
                              VK_IMAGE_LAYOUT_UNDEFINED, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);
        copyBufferToImage(stagingBuffer, textureImage2, texWidth, texHeight);
        transitionImageLayout(textureImage2, VK_FORMAT_R8G8B8A8_UNORM,
                              VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);

        vkDestroyBuffer(device, stagingBuffer, nullptr);
        vkFreeMemory(device, stagingBufferMemory, nullptr);
    }

    void createTextureImageView2() {
        if (textureImage2 == textureImage) {
            textureImageView2 = textureImageView;
            return;
        }
        textureImageView2 = createImageView(textureImage2, VK_FORMAT_R8G8B8A8_UNORM, VK_IMAGE_ASPECT_COLOR_BIT);
    }

    void createTextureImageView() {
        if (textureImageView) {
            vkDestroyImageView(device, textureImageView, nullptr);
            textureImageView = VK_NULL_HANDLE;
        }
        textureImageView = createImageView(textureImage, VK_FORMAT_R8G8B8A8_UNORM, VK_IMAGE_ASPECT_COLOR_BIT);
    }

    void createTextureSampler() {
        VkSamplerCreateInfo samplerInfo{};
        samplerInfo.sType = VK_STRUCTURE_TYPE_SAMPLER_CREATE_INFO;
        bool atlasMode = tileMode || externalInstanceMode;
        samplerInfo.magFilter = atlasMode ? VK_FILTER_NEAREST : VK_FILTER_LINEAR;
        samplerInfo.minFilter = atlasMode ? VK_FILTER_NEAREST : VK_FILTER_LINEAR;
        samplerInfo.addressModeU = atlasMode ? VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE : VK_SAMPLER_ADDRESS_MODE_REPEAT;
        samplerInfo.addressModeV = atlasMode ? VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE : VK_SAMPLER_ADDRESS_MODE_REPEAT;
        samplerInfo.addressModeW = atlasMode ? VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE : VK_SAMPLER_ADDRESS_MODE_REPEAT;
        samplerInfo.anisotropyEnable = VK_FALSE;
        samplerInfo.maxAnisotropy = 1.0f;
        samplerInfo.borderColor = VK_BORDER_COLOR_INT_OPAQUE_BLACK;
        samplerInfo.unnormalizedCoordinates = VK_FALSE;
        samplerInfo.compareEnable = VK_FALSE;
        samplerInfo.compareOp = VK_COMPARE_OP_ALWAYS;
        samplerInfo.mipmapMode = VK_SAMPLER_MIPMAP_MODE_LINEAR;

        if (vkCreateSampler(device, &samplerInfo, nullptr, &textureSampler) != VK_SUCCESS) {
            throw std::runtime_error("failed to create texture sampler");
        }
    }

    void buildMeshData() {
        vertices.clear();
        indices.clear();
        meshes.clear();

        std::vector<Vertex> quad;
        if (tileMode || externalInstanceMode) {
            quad = {
                {{-0.6f, -0.6f, 0.0f}, {1.0f, 1.0f, 1.0f}, {0.0f, 0.0f}},
                {{0.6f, -0.6f, 0.0f}, {1.0f, 1.0f, 1.0f}, {1.0f, 0.0f}},
                {{0.6f, 0.6f, 0.0f}, {1.0f, 1.0f, 1.0f}, {1.0f, 1.0f}},
                {{-0.6f, 0.6f, 0.0f}, {1.0f, 1.0f, 1.0f}, {0.0f, 1.0f}},
            };
        } else {
            quad = {
                {{-0.6f, -0.6f, 0.0f}, {1.0f, 0.3f, 0.3f}, {0.0f, 0.0f}},
                {{0.6f, -0.6f, 0.0f}, {0.3f, 1.0f, 0.3f}, {1.0f, 0.0f}},
                {{0.6f, 0.6f, 0.0f}, {0.3f, 0.3f, 1.0f}, {1.0f, 1.0f}},
                {{-0.6f, 0.6f, 0.0f}, {1.0f, 1.0f, 0.3f}, {0.0f, 1.0f}},
            };
        }
        const std::vector<uint16_t> quadIdx = {0, 1, 2, 2, 3, 0};

        uint32_t baseVertex = 0;
        vertices.insert(vertices.end(), quad.begin(), quad.end());
        indices.insert(indices.end(), quadIdx.begin(), quadIdx.end());
        meshes.push_back({0, static_cast<uint32_t>(quadIdx.size()), static_cast<int32_t>(baseVertex)});

        if (!tileMode && !externalInstanceMode) {
            const std::vector<Vertex> tri = {
                {{0.0f, -0.7f, 0.0f}, {0.9f, 0.6f, 0.2f}, {0.5f, 0.0f}},
                {{0.7f, 0.7f, 0.0f}, {0.2f, 0.8f, 0.9f}, {1.0f, 1.0f}},
                {{-0.7f, 0.7f, 0.0f}, {0.9f, 0.2f, 0.7f}, {0.0f, 1.0f}},
            };
            const std::vector<uint16_t> triIdx = {0, 1, 2};
            baseVertex = static_cast<uint32_t>(vertices.size());
            uint32_t firstIndex = static_cast<uint32_t>(indices.size());
            vertices.insert(vertices.end(), tri.begin(), tri.end());
            for (auto idx : triIdx) {
                indices.push_back(static_cast<uint16_t>(idx + baseVertex));
            }
            meshes.push_back({firstIndex, static_cast<uint32_t>(triIdx.size()), static_cast<int32_t>(0)});
        }
    }

    void buildInstanceData() {
        if (externalInstanceMode) {
            instanceCount = externalInstanceCapacity > 0 ? externalInstanceCapacity : 1;
        } else if (tileMode) {
            instanceCount = 16;
        } else {
            instanceCount = std::max<uint32_t>(1, g_config.instanceCount);
        }
    }

    void createVertexBuffer() {
        VkDeviceSize bufferSize = sizeof(vertices[0]) * vertices.size();

        VkBuffer stagingBuffer;
        VkDeviceMemory stagingBufferMemory;
        createBuffer(bufferSize, VK_BUFFER_USAGE_TRANSFER_SRC_BIT,
                     VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT,
                     stagingBuffer, stagingBufferMemory);

        void* data;
        vkMapMemory(device, stagingBufferMemory, 0, bufferSize, 0, &data);
        std::memcpy(data, vertices.data(), static_cast<size_t>(bufferSize));
        vkUnmapMemory(device, stagingBufferMemory);

        createBuffer(bufferSize, VK_BUFFER_USAGE_TRANSFER_DST_BIT | VK_BUFFER_USAGE_VERTEX_BUFFER_BIT,
                     VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT, vertexBuffer, vertexBufferMemory);

        copyBuffer(stagingBuffer, vertexBuffer, bufferSize);

        vkDestroyBuffer(device, stagingBuffer, nullptr);
        vkFreeMemory(device, stagingBufferMemory, nullptr);
    }

    void createIndexBuffer() {
        VkDeviceSize bufferSize = sizeof(indices[0]) * indices.size();

        VkBuffer stagingBuffer;
        VkDeviceMemory stagingBufferMemory;
        createBuffer(bufferSize, VK_BUFFER_USAGE_TRANSFER_SRC_BIT,
                     VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT,
                     stagingBuffer, stagingBufferMemory);

        void* data;
        vkMapMemory(device, stagingBufferMemory, 0, bufferSize, 0, &data);
        std::memcpy(data, indices.data(), static_cast<size_t>(bufferSize));
        vkUnmapMemory(device, stagingBufferMemory);

        createBuffer(bufferSize, VK_BUFFER_USAGE_TRANSFER_DST_BIT | VK_BUFFER_USAGE_INDEX_BUFFER_BIT,
                     VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT, indexBuffer, indexBufferMemory);

        copyBuffer(stagingBuffer, indexBuffer, bufferSize);

        vkDestroyBuffer(device, stagingBuffer, nullptr);
        vkFreeMemory(device, stagingBufferMemory, nullptr);
    }

    void createInstanceBuffer() {
        std::vector<InstanceData> instances;
        if (externalInstanceMode) {
            uint32_t capacity = externalInstanceCapacity > 0 ? externalInstanceCapacity : instanceCount;
            if (capacity == 0) {
                capacity = 1;
            }
            VkDeviceSize bufferSize = sizeof(InstanceData) * capacity;
            createBuffer(bufferSize, VK_BUFFER_USAGE_VERTEX_BUFFER_BIT,
                         VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT,
                         instanceBuffer, instanceBufferMemory);
            std::vector<InstanceData> zero(capacity);
            void* data;
            vkMapMemory(device, instanceBufferMemory, 0, bufferSize, 0, &data);
            std::memcpy(data, zero.data(), static_cast<size_t>(bufferSize));
            vkUnmapMemory(device, instanceBufferMemory);
            instanceBufferHostVisible = true;
            externalInstanceCapacity = capacity;
            externalInstanceCount = 0;
            return;
        }
        if (tileMode) {
            buildTileInstances(instances);
            VkDeviceSize bufferSize = sizeof(InstanceData) * instances.size();
            createBuffer(bufferSize, VK_BUFFER_USAGE_VERTEX_BUFFER_BIT,
                         VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT,
                         instanceBuffer, instanceBufferMemory);
            void* data;
            vkMapMemory(device, instanceBufferMemory, 0, bufferSize, 0, &data);
            std::memcpy(data, instances.data(), static_cast<size_t>(bufferSize));
            vkUnmapMemory(device, instanceBufferMemory);
            instanceBufferHostVisible = true;
            return;
        }
        instanceBufferHostVisible = false;

        instances.reserve(instanceCount);
        const uint32_t grid = static_cast<uint32_t>(std::ceil(std::sqrt(static_cast<float>(instanceCount))));
        const float spacing = 1.6f;
        instanceSpan = spacing * static_cast<float>(grid > 0 ? (grid - 1) : 0);
        uint32_t placed = 0;
        for (uint32_t y = 0; y < grid && placed < instanceCount; ++y) {
            for (uint32_t x = 0; x < grid && placed < instanceCount; ++x) {
                float ox = (static_cast<float>(x) - (grid - 1) * 0.5f) * spacing;
                float oy = (static_cast<float>(y) - (grid - 1) * 0.5f) * spacing;
                instances.push_back({{ox, oy, 0.0f}, 0.6f, {0.0f, 0.0f}, {1.0f, 1.0f}, {1.0f, 1.0f, 1.0f, 1.0f}});
                placed++;
            }
        }

        VkDeviceSize bufferSize = sizeof(InstanceData) * instances.size();

        VkBuffer stagingBuffer;
        VkDeviceMemory stagingBufferMemory;
        createBuffer(bufferSize, VK_BUFFER_USAGE_TRANSFER_SRC_BIT,
                     VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT,
                     stagingBuffer, stagingBufferMemory);

        void* data;
        vkMapMemory(device, stagingBufferMemory, 0, bufferSize, 0, &data);
        std::memcpy(data, instances.data(), static_cast<size_t>(bufferSize));
        vkUnmapMemory(device, stagingBufferMemory);

        createBuffer(bufferSize, VK_BUFFER_USAGE_TRANSFER_DST_BIT | VK_BUFFER_USAGE_VERTEX_BUFFER_BIT,
                     VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT, instanceBuffer, instanceBufferMemory);

        copyBuffer(stagingBuffer, instanceBuffer, bufferSize);

        vkDestroyBuffer(device, stagingBuffer, nullptr);
        vkFreeMemory(device, stagingBufferMemory, nullptr);
    }

    void buildTileInstances(std::vector<InstanceData>& instances) {
        instances.clear();
        instances.reserve(16);

        const float width = static_cast<float>(swapChainExtent.width);
        const float height = static_cast<float>(swapChainExtent.height);
        const float boardSize = std::min(width, height) * 0.78f;
        tileGap = std::max(6.0f, boardSize * 0.03f);
        tileSize = (boardSize - tileGap * 3.0f) / 4.0f;

        const float startX = (width - boardSize) * 0.5f + tileSize * 0.5f;
        const float startY = (height - boardSize) * 0.5f + tileSize * 0.5f;

        for (int r = 0; r < 4; ++r) {
            for (int c = 0; c < 4; ++c) {
                float x = startX + static_cast<float>(c) * (tileSize + tileGap);
                float y = startY + static_cast<float>(r) * (tileSize + tileGap);
                int idx = r * 4 + c;
                int labelIdx = tileLabelIndex(tileValues[idx]);
                float padU = tileAtlasPad / (tileAtlasCell * static_cast<float>(tileAtlasCols));
                float padV = tileAtlasPad / tileAtlasCell;
                float cellU = tileAtlasU;
                float cellV = tileAtlasV;
                float u0 = static_cast<float>(labelIdx) * cellU + padU;
                float v0 = padV;
                float uScale = cellU - padU * 2.0f;
                float vScale = cellV - padV * 2.0f;
                float tileCol[4];
                tileColor(tileValues[idx], tileCol);
                instances.push_back({{x, y, 0.0f}, tileSize / 1.2f, {u0, v0}, {uScale, vScale}, {tileCol[0], tileCol[1], tileCol[2], tileCol[3]}});
            }
        }
    }

    void updateTileInstanceBuffer() {
        if (!instanceBufferHostVisible) {
            return;
        }
        std::vector<InstanceData> instances;
        buildTileInstances(instances);
        VkDeviceSize bufferSize = sizeof(InstanceData) * instances.size();
        void* data;
        vkMapMemory(device, instanceBufferMemory, 0, bufferSize, 0, &data);
        std::memcpy(data, instances.data(), static_cast<size_t>(bufferSize));
        vkUnmapMemory(device, instanceBufferMemory);
    }

    void updateExternalInstanceBuffer(const float* instanceData, uint32_t count) {
        if (!instanceBufferHostVisible) {
            throw std::runtime_error("external instance buffer not host visible");
        }
        if (count > externalInstanceCapacity) {
            count = externalInstanceCapacity;
        }
        externalInstanceCount = count;
        if (count == 0) {
            return;
        }
        VkDeviceSize bufferSize = sizeof(InstanceData) * count;
        void* data;
        vkMapMemory(device, instanceBufferMemory, 0, bufferSize, 0, &data);
        std::memcpy(data, instanceData, static_cast<size_t>(bufferSize));
        vkUnmapMemory(device, instanceBufferMemory);
    }

    void handleTileInput() {
#ifndef FLOW_VK_STANDALONE
        auto pressed = [&](int key) { return glfwGetKey(window, key) == GLFW_PRESS; };

        bool left = pressed(GLFW_KEY_LEFT) || pressed(GLFW_KEY_A);
        bool right = pressed(GLFW_KEY_RIGHT) || pressed(GLFW_KEY_D);
        bool up = pressed(GLFW_KEY_UP) || pressed(GLFW_KEY_W);
        bool down = pressed(GLFW_KEY_DOWN) || pressed(GLFW_KEY_S);
        bool restart = pressed(GLFW_KEY_R);

        if (left && !keyLeftDown) {
            flow_2048_step_ptr_i32_ptr_i32_ptr_i32_i32(tileBoard.data(), &tileScore, &tileRng, 0);
        }
        if (right && !keyRightDown) {
            flow_2048_step_ptr_i32_ptr_i32_ptr_i32_i32(tileBoard.data(), &tileScore, &tileRng, 1);
        }
        if (up && !keyUpDown) {
            flow_2048_step_ptr_i32_ptr_i32_ptr_i32_i32(tileBoard.data(), &tileScore, &tileRng, 2);
        }
        if (down && !keyDownDown) {
            flow_2048_step_ptr_i32_ptr_i32_ptr_i32_i32(tileBoard.data(), &tileScore, &tileRng, 3);
        }
        if (restart && !keyRestartDown) {
            flow_2048_step_ptr_i32_ptr_i32_ptr_i32_i32(tileBoard.data(), &tileScore, &tileRng, 4);
        }

        keyLeftDown = left;
        keyRightDown = right;
        keyUpDown = up;
        keyDownDown = down;
        keyRestartDown = restart;
#else
        (void)window;
#endif
    }

    static void tileColor(int value, float* out) {
        struct Color { int v; float r; float g; float b; };
        static const Color palette[] = {
            {0, 0.20f, 0.19f, 0.18f},
            {2, 0.93f, 0.89f, 0.85f},
            {4, 0.93f, 0.87f, 0.78f},
            {8, 0.95f, 0.69f, 0.47f},
            {16, 0.96f, 0.58f, 0.39f},
            {32, 0.96f, 0.49f, 0.37f},
            {64, 0.96f, 0.37f, 0.23f},
            {128, 0.93f, 0.81f, 0.45f},
            {256, 0.93f, 0.80f, 0.38f},
            {512, 0.93f, 0.78f, 0.31f},
            {1024, 0.93f, 0.76f, 0.25f},
            {2048, 0.93f, 0.75f, 0.20f},
        };
        for (const auto& c : palette) {
            if (value == c.v) {
                out[0] = c.r; out[1] = c.g; out[2] = c.b; out[3] = 1.0f;
                return;
            }
        }
        out[0] = 0.23f; out[1] = 0.23f; out[2] = 0.23f; out[3] = 1.0f;
    }

    void createUniformBuffers() {
        VkDeviceSize bufferSize = sizeof(UniformBufferObject);
        uniformBuffers.resize(swapChainImages.size());
        uniformBuffersMemory.resize(swapChainImages.size());

        for (size_t i = 0; i < swapChainImages.size(); ++i) {
            createBuffer(bufferSize, VK_BUFFER_USAGE_UNIFORM_BUFFER_BIT,
                         VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT,
                         uniformBuffers[i], uniformBuffersMemory[i]);
        }
    }

    void createDescriptorPool() {
        std::array<VkDescriptorPoolSize, 2> poolSizes{};
        poolSizes[0].type = VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER;
        poolSizes[0].descriptorCount = static_cast<uint32_t>(swapChainImages.size());
        poolSizes[1].type = VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER;
        poolSizes[1].descriptorCount = static_cast<uint32_t>(swapChainImages.size()) * 2;

        VkDescriptorPoolCreateInfo poolInfo{};
        poolInfo.sType = VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO;
        poolInfo.poolSizeCount = static_cast<uint32_t>(poolSizes.size());
        poolInfo.pPoolSizes = poolSizes.data();
        poolInfo.maxSets = static_cast<uint32_t>(swapChainImages.size());

        if (vkCreateDescriptorPool(device, &poolInfo, nullptr, &descriptorPool) != VK_SUCCESS) {
            throw std::runtime_error("failed to create descriptor pool");
        }
    }

    void createDescriptorSets() {
        if (descriptorSets.size() != swapChainImages.size()) {
            std::vector<VkDescriptorSetLayout> layouts(swapChainImages.size(), descriptorSetLayout);
            VkDescriptorSetAllocateInfo allocInfo{};
            allocInfo.sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO;
            allocInfo.descriptorPool = descriptorPool;
            allocInfo.descriptorSetCount = static_cast<uint32_t>(swapChainImages.size());
            allocInfo.pSetLayouts = layouts.data();

            descriptorSets.resize(swapChainImages.size());
            if (vkAllocateDescriptorSets(device, &allocInfo, descriptorSets.data()) != VK_SUCCESS) {
                throw std::runtime_error("failed to allocate descriptor sets");
            }
        }

        for (size_t i = 0; i < swapChainImages.size(); ++i) {
            VkDescriptorBufferInfo bufferInfo{};
            bufferInfo.buffer = uniformBuffers[i];
            bufferInfo.offset = 0;
            bufferInfo.range = sizeof(UniformBufferObject);

            VkDescriptorImageInfo imageInfos[2]{};
            imageInfos[0].imageLayout = VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL;
            imageInfos[0].imageView = textureImageView;
            imageInfos[0].sampler = textureSampler;
            imageInfos[1].imageLayout = VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL;
            imageInfos[1].imageView = textureImageView2 ? textureImageView2 : textureImageView;
            imageInfos[1].sampler = textureSampler;

            std::array<VkWriteDescriptorSet, 2> descriptorWrites{};
            descriptorWrites[0].sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET;
            descriptorWrites[0].dstSet = descriptorSets[i];
            descriptorWrites[0].dstBinding = 0;
            descriptorWrites[0].descriptorType = VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER;
            descriptorWrites[0].descriptorCount = 1;
            descriptorWrites[0].pBufferInfo = &bufferInfo;

            descriptorWrites[1].sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET;
            descriptorWrites[1].dstSet = descriptorSets[i];
            descriptorWrites[1].dstBinding = 1;
            descriptorWrites[1].descriptorType = VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER;
            descriptorWrites[1].descriptorCount = 2;
            descriptorWrites[1].pImageInfo = imageInfos;

            vkUpdateDescriptorSets(device, static_cast<uint32_t>(descriptorWrites.size()), descriptorWrites.data(), 0, nullptr);
        }
    }

    void createCommandBuffers() {
        commandBuffers.resize(swapChainFramebuffers.size());

        VkCommandBufferAllocateInfo allocInfo{};
        allocInfo.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO;
        allocInfo.commandPool = commandPool;
        allocInfo.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
        allocInfo.commandBufferCount = static_cast<uint32_t>(commandBuffers.size());

        if (vkAllocateCommandBuffers(device, &allocInfo, commandBuffers.data()) != VK_SUCCESS) {
            throw std::runtime_error("failed to allocate command buffers");
        }
    }

    void recordCommandBuffer(VkCommandBuffer commandBuffer, uint32_t imageIndex) {
        VkCommandBufferBeginInfo beginInfo{};
        beginInfo.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;

        if (vkBeginCommandBuffer(commandBuffer, &beginInfo) != VK_SUCCESS) {
            throw std::runtime_error("failed to begin recording command buffer");
        }

        VkRenderPassBeginInfo renderPassInfo{};
        renderPassInfo.sType = VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO;
        renderPassInfo.renderPass = renderPass;
        renderPassInfo.framebuffer = swapChainFramebuffers[imageIndex];
        renderPassInfo.renderArea.offset = {0, 0};
        renderPassInfo.renderArea.extent = swapChainExtent;

        std::array<VkClearValue, 2> clearValues{};
        clearValues[0].color = {{g_config.clearR, g_config.clearG, g_config.clearB, 1.0f}};
        clearValues[1].depthStencil = {1.0f, 0};
        renderPassInfo.clearValueCount = static_cast<uint32_t>(clearValues.size());
        renderPassInfo.pClearValues = clearValues.data();

        vkCmdBeginRenderPass(commandBuffer, &renderPassInfo, VK_SUBPASS_CONTENTS_INLINE);
        vkCmdBindPipeline(commandBuffer, VK_PIPELINE_BIND_POINT_GRAPHICS, graphicsPipeline);

        VkBuffer vertexBuffers[] = {vertexBuffer};
        VkDeviceSize offsets[] = {0};
        vkCmdBindVertexBuffers(commandBuffer, 0, 1, vertexBuffers, offsets);
        VkBuffer instanceBuffers[] = {instanceBuffer};
        VkDeviceSize instanceOffsets[] = {0};
        vkCmdBindVertexBuffers(commandBuffer, 1, 1, instanceBuffers, instanceOffsets);
        vkCmdBindIndexBuffer(commandBuffer, indexBuffer, 0, VK_INDEX_TYPE_UINT16);

        vkCmdBindDescriptorSets(commandBuffer, VK_PIPELINE_BIND_POINT_GRAPHICS, pipelineLayout, 0, 1, &descriptorSets[imageIndex], 0, nullptr);

        struct PushConstants {
            float color[4];
            int32_t texIndex;
            int32_t pad[3];
            float meshOffset[4];
        } pc{};
        if (externalInstanceMode) {
            const auto& mesh = meshes[0];
            pc.texIndex = 0;
            pc.color[0] = 1.0f;
            pc.color[1] = 1.0f;
            pc.color[2] = 1.0f;
            pc.color[3] = -1.0f;
            pc.meshOffset[0] = 0.0f;
            pc.meshOffset[1] = 0.0f;
            pc.meshOffset[2] = 0.0f;
            pc.meshOffset[3] = 0.0f;
            uint32_t count = externalInstanceCount > 0 ? externalInstanceCount : 1;
            vkCmdPushConstants(commandBuffer, pipelineLayout, VK_SHADER_STAGE_FRAGMENT_BIT | VK_SHADER_STAGE_VERTEX_BIT, 0, sizeof(PushConstants), &pc);
            vkCmdDrawIndexed(commandBuffer, mesh.indexCount, count, mesh.firstIndex, mesh.vertexOffset, 0);
        } else if (tileMode) {
            const auto& mesh = meshes[0];
            pc.texIndex = 0;
            pc.meshOffset[0] = 0.0f;
            pc.meshOffset[1] = 0.0f;
            pc.meshOffset[2] = 0.0f;
            pc.meshOffset[3] = 0.0f;
            for (uint32_t i = 0; i < 16; ++i) {
                tileColor(tileValues[i], pc.color);
                pc.color[3] = -1.0f;
                vkCmdPushConstants(commandBuffer, pipelineLayout, VK_SHADER_STAGE_FRAGMENT_BIT | VK_SHADER_STAGE_VERTEX_BIT, 0, sizeof(PushConstants), &pc);
                vkCmdDrawIndexed(commandBuffer, mesh.indexCount, 1, mesh.firstIndex, mesh.vertexOffset, i);
            }
        } else {
            for (size_t i = 0; i < meshes.size(); ++i) {
                pc.texIndex = static_cast<int32_t>(i % 2);
                const float* col = (i % 2 == 0) ? g_config.mesh1Color : g_config.mesh2Color;
                pc.color[0] = col[0];
                pc.color[1] = col[1];
                pc.color[2] = col[2];
                pc.color[3] = 1.0f;
                float meshOffsetX = (i == 0) ? -(instanceSpan + 1.5f) : (instanceSpan + 1.5f);
                pc.meshOffset[0] = meshOffsetX;
                pc.meshOffset[1] = 0.0f;
                pc.meshOffset[2] = 0.0f;
                pc.meshOffset[3] = 0.0f;
                vkCmdPushConstants(commandBuffer, pipelineLayout, VK_SHADER_STAGE_FRAGMENT_BIT | VK_SHADER_STAGE_VERTEX_BIT, 0, sizeof(PushConstants), &pc);
                const auto& mesh = meshes[i];
                vkCmdDrawIndexed(commandBuffer, mesh.indexCount, instanceCount, mesh.firstIndex, mesh.vertexOffset, 0);
            }
        }
        vkCmdEndRenderPass(commandBuffer);

        if (vkEndCommandBuffer(commandBuffer) != VK_SUCCESS) {
            throw std::runtime_error("failed to record command buffer");
        }
    }

    void createSyncObjects() {
        const size_t maxFramesInFlight = 2;
        imageAvailableSemaphores.resize(maxFramesInFlight);
        inFlightFences.resize(maxFramesInFlight);
        renderFinishedSemaphores.resize(swapChainImages.size());
        imagesInFlight.resize(swapChainImages.size(), VK_NULL_HANDLE);

        VkSemaphoreCreateInfo semaphoreInfo{};
        semaphoreInfo.sType = VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO;

        VkFenceCreateInfo fenceInfo{};
        fenceInfo.sType = VK_STRUCTURE_TYPE_FENCE_CREATE_INFO;
        fenceInfo.flags = VK_FENCE_CREATE_SIGNALED_BIT;

        for (size_t i = 0; i < maxFramesInFlight; ++i) {
            if (vkCreateSemaphore(device, &semaphoreInfo, nullptr, &imageAvailableSemaphores[i]) != VK_SUCCESS ||
                vkCreateFence(device, &fenceInfo, nullptr, &inFlightFences[i]) != VK_SUCCESS) {
                throw std::runtime_error("failed to create synchronization objects");
            }
        }

        for (size_t i = 0; i < renderFinishedSemaphores.size(); ++i) {
            if (vkCreateSemaphore(device, &semaphoreInfo, nullptr, &renderFinishedSemaphores[i]) != VK_SUCCESS) {
                throw std::runtime_error("failed to create render-finished semaphores");
            }
        }
    }

    void updateUniformBuffer(uint32_t currentImage) {
        UniformBufferObject ubo{};
        if (tileMode || externalInstanceMode) {
            float model[16];
            float view[16];
            float proj[16];
            mat4_identity(model);
            mat4_identity(view);
            float orthoWidth = static_cast<float>(swapChainExtent.width);
            float orthoHeight = static_cast<float>(swapChainExtent.height);
            if (tileMode || externalInstanceMode) {
                orthoWidth = static_cast<float>(g_config.width);
                orthoHeight = static_cast<float>(g_config.height);
            }
            mat4_ortho(0.0f,
                       orthoWidth,
                       orthoHeight,
                       0.0f,
                       -1.0f, 1.0f,
                       proj);
            std::memcpy(ubo.view, view, sizeof(view));
            std::memcpy(ubo.proj, proj, sizeof(proj));
            std::memcpy(ubo.model, model, sizeof(model));

            void* data;
            vkMapMemory(device, uniformBuffersMemory[currentImage], 0, sizeof(ubo), 0, &data);
            std::memcpy(data, &ubo, sizeof(ubo));
            vkUnmapMemory(device, uniformBuffersMemory[currentImage]);
            return;
        }
        float angle = static_cast<float>(glfwGetTime()) * g_config.rotationSpeed;
        float c = std::cos(angle);
        float s = std::sin(angle);

        float model[16];
        mat4_identity(model);
        model[0] = c;
        model[1] = s;
        model[4] = -s;
        model[5] = c;

        float smooth = std::clamp(g_config.cameraSmoothing, 0.0f, 1.0f);
        cameraDistance += (targetCameraDistance - cameraDistance) * smooth;
        cameraPitch += (targetCameraPitch - cameraPitch) * smooth;
        cameraYaw += (targetCameraYaw - cameraYaw) * smooth;

        float eye[3] = {
            cameraDistance * std::cos(cameraPitch) * std::cos(cameraYaw),
            cameraDistance * std::sin(cameraPitch),
            cameraDistance * std::cos(cameraPitch) * std::sin(cameraYaw)
        };
        float center[3] = {0.0f, 0.0f, 0.0f};
        float up[3] = {0.0f, 1.0f, 0.0f};

        float view[16];
        mat4_lookat(eye, center, up, view);

        float proj[16];
        float aspect = static_cast<float>(swapChainExtent.width) / static_cast<float>(swapChainExtent.height);
        mat4_perspective(0.9f, aspect, 0.1f, 50.0f, proj);
        // Vulkan clip correction
        proj[5] *= -1.0f;

        std::memcpy(ubo.view, view, sizeof(view));
        std::memcpy(ubo.proj, proj, sizeof(proj));
        std::memcpy(ubo.model, model, sizeof(model));

        void* data;
        vkMapMemory(device, uniformBuffersMemory[currentImage], 0, sizeof(ubo), 0, &data);
        std::memcpy(data, &ubo, sizeof(ubo));
        vkUnmapMemory(device, uniformBuffersMemory[currentImage]);
    }

    void drawFrame() {
        vkWaitForFences(device, 1, &inFlightFences[currentFrame], VK_TRUE, UINT64_MAX);

        uint32_t imageIndex = 0;
        VkResult result = vkAcquireNextImageKHR(device, swapChain, UINT64_MAX, imageAvailableSemaphores[currentFrame], VK_NULL_HANDLE, &imageIndex);
        if (result != VK_SUCCESS) {
            throw std::runtime_error("failed to acquire swap chain image");
        }

        if (imagesInFlight[imageIndex] != VK_NULL_HANDLE) {
            vkWaitForFences(device, 1, &imagesInFlight[imageIndex], VK_TRUE, UINT64_MAX);
        }
        imagesInFlight[imageIndex] = inFlightFences[currentFrame];

        vkResetFences(device, 1, &inFlightFences[currentFrame]);

        updateUniformBuffer(imageIndex);

        vkResetCommandBuffer(commandBuffers[imageIndex], 0);
        recordCommandBuffer(commandBuffers[imageIndex], imageIndex);

        VkSubmitInfo submitInfo{};
        submitInfo.sType = VK_STRUCTURE_TYPE_SUBMIT_INFO;

        VkSemaphore waitSemaphores[] = {imageAvailableSemaphores[currentFrame]};
        VkPipelineStageFlags waitStages[] = {VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT};
        submitInfo.waitSemaphoreCount = 1;
        submitInfo.pWaitSemaphores = waitSemaphores;
        submitInfo.pWaitDstStageMask = waitStages;

        submitInfo.commandBufferCount = 1;
        submitInfo.pCommandBuffers = &commandBuffers[imageIndex];

        VkSemaphore signalSemaphores[] = {renderFinishedSemaphores[imageIndex]};
        submitInfo.signalSemaphoreCount = 1;
        submitInfo.pSignalSemaphores = signalSemaphores;

        if (vkQueueSubmit(graphicsQueue, 1, &submitInfo, inFlightFences[currentFrame]) != VK_SUCCESS) {
            throw std::runtime_error("failed to submit draw command buffer");
        }

        VkPresentInfoKHR presentInfo{};
        presentInfo.sType = VK_STRUCTURE_TYPE_PRESENT_INFO_KHR;
        presentInfo.waitSemaphoreCount = 1;
        presentInfo.pWaitSemaphores = signalSemaphores;

        VkSwapchainKHR swapChains[] = {swapChain};
        presentInfo.swapchainCount = 1;
        presentInfo.pSwapchains = swapChains;
        presentInfo.pImageIndices = &imageIndex;

        result = vkQueuePresentKHR(presentQueue, &presentInfo);
        if (result != VK_SUCCESS) {
            throw std::runtime_error("failed to present swap chain image");
        }

        currentFrame = (currentFrame + 1) % imageAvailableSemaphores.size();
    }

    VkShaderModule createShaderModule(const std::vector<char>& code) {
        VkShaderModuleCreateInfo createInfo{};
        createInfo.sType = VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO;
        createInfo.codeSize = code.size();
        createInfo.pCode = reinterpret_cast<const uint32_t*>(code.data());

        VkShaderModule shaderModule = VK_NULL_HANDLE;
        if (vkCreateShaderModule(device, &createInfo, nullptr, &shaderModule) != VK_SUCCESS) {
            throw std::runtime_error("failed to create shader module");
        }
        return shaderModule;
    }

    bool isDeviceSuitable(VkPhysicalDevice deviceCandidate) {
        QueueFamilyIndices indices = findQueueFamilies(deviceCandidate);

        bool extensionsSupported = checkDeviceExtensionSupport(deviceCandidate);
        bool swapChainAdequate = false;
        if (extensionsSupported) {
            SwapChainSupportDetails swapChainSupport = querySwapChainSupport(deviceCandidate);
            swapChainAdequate = !swapChainSupport.formats.empty() && !swapChainSupport.presentModes.empty();
        }

        return indices.isComplete() && extensionsSupported && swapChainAdequate;
    }

    bool checkDeviceExtensionSupport(VkPhysicalDevice deviceCandidate) {
        uint32_t extensionCount = 0;
        vkEnumerateDeviceExtensionProperties(deviceCandidate, nullptr, &extensionCount, nullptr);
        std::vector<VkExtensionProperties> availableExtensions(extensionCount);
        vkEnumerateDeviceExtensionProperties(deviceCandidate, nullptr, &extensionCount, availableExtensions.data());

        std::set<std::string> requiredExtensions(kDeviceExtensions.begin(), kDeviceExtensions.end());
        for (const auto& ext : availableExtensions) {
            requiredExtensions.erase(ext.extensionName);
        }
        return requiredExtensions.empty();
    }

    bool supportsExtension(VkPhysicalDevice deviceCandidate, const char* name) {
        uint32_t extensionCount = 0;
        vkEnumerateDeviceExtensionProperties(deviceCandidate, nullptr, &extensionCount, nullptr);
        std::vector<VkExtensionProperties> availableExtensions(extensionCount);
        vkEnumerateDeviceExtensionProperties(deviceCandidate, nullptr, &extensionCount, availableExtensions.data());
        for (const auto& ext : availableExtensions) {
            if (std::strcmp(ext.extensionName, name) == 0) {
                return true;
            }
        }
        return false;
    }

    QueueFamilyIndices findQueueFamilies(VkPhysicalDevice deviceCandidate) {
        QueueFamilyIndices indices;

        uint32_t queueFamilyCount = 0;
        vkGetPhysicalDeviceQueueFamilyProperties(deviceCandidate, &queueFamilyCount, nullptr);
        std::vector<VkQueueFamilyProperties> queueFamilies(queueFamilyCount);
        vkGetPhysicalDeviceQueueFamilyProperties(deviceCandidate, &queueFamilyCount, queueFamilies.data());

        int i = 0;
        for (const auto& queueFamily : queueFamilies) {
            if (queueFamily.queueFlags & VK_QUEUE_GRAPHICS_BIT) {
                indices.graphicsFamily = i;
            }
            VkBool32 presentSupport = VK_FALSE;
            vkGetPhysicalDeviceSurfaceSupportKHR(deviceCandidate, i, surface, &presentSupport);
            if (presentSupport) {
                indices.presentFamily = i;
            }
            if (indices.isComplete()) {
                break;
            }
            ++i;
        }
        return indices;
    }

    SwapChainSupportDetails querySwapChainSupport(VkPhysicalDevice deviceCandidate) {
        SwapChainSupportDetails details;
        vkGetPhysicalDeviceSurfaceCapabilitiesKHR(deviceCandidate, surface, &details.capabilities);

        uint32_t formatCount = 0;
        vkGetPhysicalDeviceSurfaceFormatsKHR(deviceCandidate, surface, &formatCount, nullptr);
        if (formatCount != 0) {
            details.formats.resize(formatCount);
            vkGetPhysicalDeviceSurfaceFormatsKHR(deviceCandidate, surface, &formatCount, details.formats.data());
        }

        uint32_t presentModeCount = 0;
        vkGetPhysicalDeviceSurfacePresentModesKHR(deviceCandidate, surface, &presentModeCount, nullptr);
        if (presentModeCount != 0) {
            details.presentModes.resize(presentModeCount);
            vkGetPhysicalDeviceSurfacePresentModesKHR(deviceCandidate, surface, &presentModeCount, details.presentModes.data());
        }

        return details;
    }

    VkSurfaceFormatKHR chooseSwapSurfaceFormat(const std::vector<VkSurfaceFormatKHR>& availableFormats) {
        for (const auto& availableFormat : availableFormats) {
            if (availableFormat.format == VK_FORMAT_B8G8R8A8_SRGB &&
                availableFormat.colorSpace == VK_COLOR_SPACE_SRGB_NONLINEAR_KHR) {
                return availableFormat;
            }
        }
        return availableFormats[0];
    }

    VkPresentModeKHR chooseSwapPresentMode(const std::vector<VkPresentModeKHR>& availablePresentModes) {
        for (const auto& availablePresentMode : availablePresentModes) {
            if (availablePresentMode == VK_PRESENT_MODE_MAILBOX_KHR) {
                return availablePresentMode;
            }
        }
        return VK_PRESENT_MODE_FIFO_KHR;
    }

    VkExtent2D chooseSwapExtent(const VkSurfaceCapabilitiesKHR& capabilities) {
        if (capabilities.currentExtent.width != UINT32_MAX) {
            return capabilities.currentExtent;
        }
        VkExtent2D actualExtent = {g_config.width, g_config.height};
        actualExtent.width = std::max(capabilities.minImageExtent.width, std::min(capabilities.maxImageExtent.width, actualExtent.width));
        actualExtent.height = std::max(capabilities.minImageExtent.height, std::min(capabilities.maxImageExtent.height, actualExtent.height));
        return actualExtent;
    }

    std::vector<const char*> getRequiredExtensions() {
        uint32_t glfwExtensionCount = 0;
        const char** glfwExtensions = glfwGetRequiredInstanceExtensions(&glfwExtensionCount);
        if (!glfwExtensions || glfwExtensionCount == 0) {
            throw std::runtime_error("GLFW did not provide required Vulkan instance extensions");
        }
        std::vector<const char*> extensions(glfwExtensions, glfwExtensions + glfwExtensionCount);

        extensions.push_back(VK_KHR_GET_PHYSICAL_DEVICE_PROPERTIES_2_EXTENSION_NAME);
#ifdef __APPLE__
#ifdef VK_KHR_PORTABILITY_ENUMERATION_EXTENSION_NAME
        extensions.push_back(VK_KHR_PORTABILITY_ENUMERATION_EXTENSION_NAME);
#else
        extensions.push_back("VK_KHR_portability_enumeration");
#endif
#else
#ifdef VK_KHR_PORTABILITY_ENUMERATION_EXTENSION_NAME
        extensions.push_back(VK_KHR_PORTABILITY_ENUMERATION_EXTENSION_NAME);
#endif
#endif

        if (validationLayersEnabled()) {
            extensions.push_back(VK_EXT_DEBUG_UTILS_EXTENSION_NAME);
        }

        return extensions;
    }

    bool checkValidationLayerSupport() {
        uint32_t layerCount = 0;
        vkEnumerateInstanceLayerProperties(&layerCount, nullptr);
        std::vector<VkLayerProperties> availableLayers(layerCount);
        vkEnumerateInstanceLayerProperties(&layerCount, availableLayers.data());

        for (const char* layerName : kValidationLayers) {
            bool layerFound = false;
            for (const auto& layerProperties : availableLayers) {
                if (std::strcmp(layerName, layerProperties.layerName) == 0) {
                    layerFound = true;
                    break;
                }
            }
            if (!layerFound) {
                return false;
            }
        }
        return true;
    }

    uint32_t findMemoryType(uint32_t typeFilter, VkMemoryPropertyFlags properties) {
        VkPhysicalDeviceMemoryProperties memProperties{};
        vkGetPhysicalDeviceMemoryProperties(physicalDevice, &memProperties);

        for (uint32_t i = 0; i < memProperties.memoryTypeCount; i++) {
            if ((typeFilter & (1 << i)) && (memProperties.memoryTypes[i].propertyFlags & properties) == properties) {
                return i;
            }
        }

        throw std::runtime_error("failed to find suitable memory type");
    }

    void createBuffer(VkDeviceSize size, VkBufferUsageFlags usage, VkMemoryPropertyFlags properties,
                      VkBuffer& buffer, VkDeviceMemory& bufferMemory) {
        VkBufferCreateInfo bufferInfo{};
        bufferInfo.sType = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO;
        bufferInfo.size = size;
        bufferInfo.usage = usage;
        bufferInfo.sharingMode = VK_SHARING_MODE_EXCLUSIVE;

        if (vkCreateBuffer(device, &bufferInfo, nullptr, &buffer) != VK_SUCCESS) {
            throw std::runtime_error("failed to create buffer");
        }

        VkMemoryRequirements memRequirements{};
        vkGetBufferMemoryRequirements(device, buffer, &memRequirements);

        VkMemoryAllocateInfo allocInfo{};
        allocInfo.sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO;
        allocInfo.allocationSize = memRequirements.size;
        allocInfo.memoryTypeIndex = findMemoryType(memRequirements.memoryTypeBits, properties);

        if (vkAllocateMemory(device, &allocInfo, nullptr, &bufferMemory) != VK_SUCCESS) {
            throw std::runtime_error("failed to allocate buffer memory");
        }

        vkBindBufferMemory(device, buffer, bufferMemory, 0);
    }

    void copyBuffer(VkBuffer srcBuffer, VkBuffer dstBuffer, VkDeviceSize size) {
        VkCommandBuffer commandBuffer = beginSingleTimeCommands();

        VkBufferCopy copyRegion{};
        copyRegion.size = size;
        vkCmdCopyBuffer(commandBuffer, srcBuffer, dstBuffer, 1, &copyRegion);

        endSingleTimeCommands(commandBuffer);
    }

    void createImage(uint32_t width, uint32_t height, VkFormat format, VkImageTiling tiling,
                     VkImageUsageFlags usage, VkMemoryPropertyFlags properties,
                     VkImage& image, VkDeviceMemory& imageMemory) {
        VkImageCreateInfo imageInfo{};
        imageInfo.sType = VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO;
        imageInfo.imageType = VK_IMAGE_TYPE_2D;
        imageInfo.extent.width = width;
        imageInfo.extent.height = height;
        imageInfo.extent.depth = 1;
        imageInfo.mipLevels = 1;
        imageInfo.arrayLayers = 1;
        imageInfo.format = format;
        imageInfo.tiling = tiling;
        imageInfo.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;
        imageInfo.usage = usage;
        imageInfo.samples = VK_SAMPLE_COUNT_1_BIT;
        imageInfo.sharingMode = VK_SHARING_MODE_EXCLUSIVE;

        if (vkCreateImage(device, &imageInfo, nullptr, &image) != VK_SUCCESS) {
            throw std::runtime_error("failed to create image");
        }

        VkMemoryRequirements memRequirements{};
        vkGetImageMemoryRequirements(device, image, &memRequirements);

        VkMemoryAllocateInfo allocInfo{};
        allocInfo.sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO;
        allocInfo.allocationSize = memRequirements.size;
        allocInfo.memoryTypeIndex = findMemoryType(memRequirements.memoryTypeBits, properties);

        if (vkAllocateMemory(device, &allocInfo, nullptr, &imageMemory) != VK_SUCCESS) {
            throw std::runtime_error("failed to allocate image memory");
        }

        vkBindImageMemory(device, image, imageMemory, 0);
    }

    VkImageView createImageView(VkImage image, VkFormat format, VkImageAspectFlags aspectFlags) {
        VkImageViewCreateInfo viewInfo{};
        viewInfo.sType = VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO;
        viewInfo.image = image;
        viewInfo.viewType = VK_IMAGE_VIEW_TYPE_2D;
        viewInfo.format = format;
        if (aspectFlags & VK_IMAGE_ASPECT_DEPTH_BIT) {
            if (format == VK_FORMAT_D32_SFLOAT_S8_UINT || format == VK_FORMAT_D24_UNORM_S8_UINT) {
                viewInfo.subresourceRange.aspectMask = aspectFlags | VK_IMAGE_ASPECT_STENCIL_BIT;
            } else {
                viewInfo.subresourceRange.aspectMask = aspectFlags;
            }
        } else {
            viewInfo.subresourceRange.aspectMask = aspectFlags;
        }
        viewInfo.subresourceRange.baseMipLevel = 0;
        viewInfo.subresourceRange.levelCount = 1;
        viewInfo.subresourceRange.baseArrayLayer = 0;
        viewInfo.subresourceRange.layerCount = 1;

        VkImageView imageView;
        if (vkCreateImageView(device, &viewInfo, nullptr, &imageView) != VK_SUCCESS) {
            throw std::runtime_error("failed to create texture image view");
        }
        return imageView;
    }

    VkCommandBuffer beginSingleTimeCommands() {
        VkCommandBufferAllocateInfo allocInfo{};
        allocInfo.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO;
        allocInfo.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
        allocInfo.commandPool = commandPool;
        allocInfo.commandBufferCount = 1;

        VkCommandBuffer commandBuffer;
        vkAllocateCommandBuffers(device, &allocInfo, &commandBuffer);

        VkCommandBufferBeginInfo beginInfo{};
        beginInfo.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;
        beginInfo.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;

        vkBeginCommandBuffer(commandBuffer, &beginInfo);
        return commandBuffer;
    }

    void endSingleTimeCommands(VkCommandBuffer commandBuffer) {
        vkEndCommandBuffer(commandBuffer);

        VkSubmitInfo submitInfo{};
        submitInfo.sType = VK_STRUCTURE_TYPE_SUBMIT_INFO;
        submitInfo.commandBufferCount = 1;
        submitInfo.pCommandBuffers = &commandBuffer;

        vkQueueSubmit(graphicsQueue, 1, &submitInfo, VK_NULL_HANDLE);
        vkQueueWaitIdle(graphicsQueue);

        vkFreeCommandBuffers(device, commandPool, 1, &commandBuffer);
    }

    void transitionImageLayout(VkImage image, VkFormat format, VkImageLayout oldLayout, VkImageLayout newLayout) {
        VkCommandBuffer commandBuffer = beginSingleTimeCommands();

        VkImageMemoryBarrier barrier{};
        barrier.sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER;
        barrier.oldLayout = oldLayout;
        barrier.newLayout = newLayout;
        barrier.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
        barrier.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
        barrier.image = image;

        if (newLayout == VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL) {
            barrier.subresourceRange.aspectMask = VK_IMAGE_ASPECT_DEPTH_BIT;
        } else {
            barrier.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
        }

        barrier.subresourceRange.baseMipLevel = 0;
        barrier.subresourceRange.levelCount = 1;
        barrier.subresourceRange.baseArrayLayer = 0;
        barrier.subresourceRange.layerCount = 1;

        VkPipelineStageFlags sourceStage;
        VkPipelineStageFlags destinationStage;

        if (oldLayout == VK_IMAGE_LAYOUT_UNDEFINED && newLayout == VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL) {
            barrier.srcAccessMask = 0;
            barrier.dstAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;

            sourceStage = VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT;
            destinationStage = VK_PIPELINE_STAGE_TRANSFER_BIT;
        } else if (oldLayout == VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL && newLayout == VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL) {
            barrier.srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
            barrier.dstAccessMask = VK_ACCESS_SHADER_READ_BIT;

            sourceStage = VK_PIPELINE_STAGE_TRANSFER_BIT;
            destinationStage = VK_PIPELINE_STAGE_FRAGMENT_SHADER_BIT;
        } else {
            barrier.srcAccessMask = 0;
            barrier.dstAccessMask = 0;
            sourceStage = VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT;
            destinationStage = VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT;
        }

        vkCmdPipelineBarrier(
            commandBuffer,
            sourceStage, destinationStage,
            0,
            0, nullptr,
            0, nullptr,
            1, &barrier
        );

        endSingleTimeCommands(commandBuffer);
    }

    void copyBufferToImage(VkBuffer buffer, VkImage image, uint32_t width, uint32_t height) {
        VkCommandBuffer commandBuffer = beginSingleTimeCommands();

        VkBufferImageCopy region{};
        region.bufferOffset = 0;
        region.bufferRowLength = 0;
        region.bufferImageHeight = 0;
        region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
        region.imageSubresource.mipLevel = 0;
        region.imageSubresource.baseArrayLayer = 0;
        region.imageSubresource.layerCount = 1;
        region.imageOffset = {0, 0, 0};
        region.imageExtent = {width, height, 1};

        vkCmdCopyBufferToImage(commandBuffer, buffer, image, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &region);

        endSingleTimeCommands(commandBuffer);
    }

    VkFormat findSupportedFormat(const std::vector<VkFormat>& candidates, VkImageTiling tiling, VkFormatFeatureFlags features) {
        for (VkFormat format : candidates) {
            VkFormatProperties props;
            vkGetPhysicalDeviceFormatProperties(physicalDevice, format, &props);

            if (tiling == VK_IMAGE_TILING_LINEAR && (props.linearTilingFeatures & features) == features) {
                return format;
            } else if (tiling == VK_IMAGE_TILING_OPTIMAL && (props.optimalTilingFeatures & features) == features) {
                return format;
            }
        }

        throw std::runtime_error("failed to find supported format");
    }

    VkFormat findDepthFormat() {
        return findSupportedFormat(
            {VK_FORMAT_D32_SFLOAT, VK_FORMAT_D32_SFLOAT_S8_UINT, VK_FORMAT_D24_UNORM_S8_UINT},
            VK_IMAGE_TILING_OPTIMAL,
            VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT
        );
    }

    void handleInput() {
        if (!window) {
            return;
        }

        double now = glfwGetTime();
        float dt = static_cast<float>(now - lastFrameTime);
        lastFrameTime = now;
        if (dt <= 0.0f || dt > 0.1f) {
            dt = 0.016f;
        }

        float speed = g_config.moveSpeed * dt;
        if (glfwGetKey(window, GLFW_KEY_LEFT_SHIFT) == GLFW_PRESS) {
            speed *= 2.0f;
        }

        if (glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS) {
            targetCameraPitch += speed;
        }
        if (glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS) {
            targetCameraPitch -= speed;
        }
        if (glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS) {
            targetCameraYaw -= speed;
        }
        if (glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS) {
            targetCameraYaw += speed;
        }
        if (glfwGetKey(window, GLFW_KEY_Q) == GLFW_PRESS) {
            targetCameraDistance += speed;
        }
        if (glfwGetKey(window, GLFW_KEY_E) == GLFW_PRESS) {
            targetCameraDistance -= speed;
        }

        if (g_scrollDelta != 0.0) {
            targetCameraDistance -= static_cast<float>(g_scrollDelta) * 0.5f;
            g_scrollDelta = 0.0;
        }

        static double lastX = 0.0;
        static double lastY = 0.0;
        static bool first = true;
        if (glfwGetMouseButton(window, GLFW_MOUSE_BUTTON_LEFT) == GLFW_PRESS) {
            double x, y;
            glfwGetCursorPos(window, &x, &y);
            if (first) {
                lastX = x;
                lastY = y;
                first = false;
            }
            double dx = x - lastX;
            double dy = y - lastY;
            lastX = x;
            lastY = y;
            targetCameraYaw += static_cast<float>(dx) * g_config.mouseSensitivity * 0.002f;
            targetCameraPitch += static_cast<float>(dy) * g_config.mouseSensitivity * 0.002f;
        } else {
            first = true;
        }
    }

    static VKAPI_ATTR VkBool32 VKAPI_CALL debugCallback(
        VkDebugUtilsMessageSeverityFlagBitsEXT messageSeverity,
        VkDebugUtilsMessageTypeFlagsEXT messageType,
        const VkDebugUtilsMessengerCallbackDataEXT* pCallbackData,
        void* pUserData) {
        (void)messageSeverity;
        (void)messageType;
        (void)pUserData;
        if (prettyValidation()) {
            if (messageSeverity >= VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT) {
                const char* level = (messageSeverity >= VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT) ? "error" : "warning";
                const char* msg = pCallbackData && pCallbackData->pMessage ? pCallbackData->pMessage : "";
                std::string high;
                if (std::strstr(msg, "vkDestroyDevice") && std::strstr(msg, "has not been destroyed")) {
                    high = "Shutdown cleanup bug: some Vulkan resources were not released before closing the device.";
                } else if (std::strstr(msg, "vkQueueSubmit") && std::strstr(msg, "semaphore")) {
                    high = "GPU sync issue: a semaphore was reused before the swapchain finished using it.";
                } else if (std::strstr(msg, "failed to create window surface")) {
                    high = "Window surface creation failed: Vulkan/GLFW couldn't hook into macOS.";
                } else if (std::strstr(msg, "VK_LAYER_KHRONOS_validation")) {
                    high = "Validation layer failed to load: Vulkan validation is installed but not found at runtime.";
                }
                if (!high.empty()) {
                    std::cerr << "Vulkan " << level << ": " << high << std::endl;
                } else {
                    std::cerr << "Vulkan " << level << ": " << msg << std::endl;
                }
            }
        } else {
            std::cerr << "validation layer: " << pCallbackData->pMessage << std::endl;
        }
        return VK_FALSE;
    }

    void setupDebugMessenger() {
        if (!validationLayersEnabled()) {
            return;
        }
        VkDebugUtilsMessengerCreateInfoEXT createInfo{};
        populateDebugMessengerCreateInfo(createInfo);

        if (createDebugUtilsMessengerEXT(instance, &createInfo, nullptr, &debugMessenger) != VK_SUCCESS) {
            throw std::runtime_error("failed to set up debug messenger");
        }
    }

    void populateDebugMessengerCreateInfo(VkDebugUtilsMessengerCreateInfoEXT& createInfo) {
        createInfo = {};
        createInfo.sType = VK_STRUCTURE_TYPE_DEBUG_UTILS_MESSENGER_CREATE_INFO_EXT;
        createInfo.messageSeverity =
            VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT |
            VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT |
            VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT;
        createInfo.messageType =
            VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT |
            VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT |
            VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT;
        createInfo.pfnUserCallback = debugCallback;
    }

    static VkResult createDebugUtilsMessengerEXT(VkInstance instance,
                                                 const VkDebugUtilsMessengerCreateInfoEXT* pCreateInfo,
                                                 const VkAllocationCallbacks* pAllocator,
                                                 VkDebugUtilsMessengerEXT* pDebugMessenger) {
        auto func = (PFN_vkCreateDebugUtilsMessengerEXT)vkGetInstanceProcAddr(instance, "vkCreateDebugUtilsMessengerEXT");
        if (func != nullptr) {
            return func(instance, pCreateInfo, pAllocator, pDebugMessenger);
        }
        return VK_ERROR_EXTENSION_NOT_PRESENT;
    }

    static void destroyDebugUtilsMessengerEXT(VkInstance instance,
                                              VkDebugUtilsMessengerEXT debugMessenger,
                                              const VkAllocationCallbacks* pAllocator) {
        auto func = (PFN_vkDestroyDebugUtilsMessengerEXT)vkGetInstanceProcAddr(instance, "vkDestroyDebugUtilsMessengerEXT");
        if (func != nullptr) {
            func(instance, debugMessenger, pAllocator);
        }
    }
};

}  // namespace

extern "C" void flow_vk_scene_configure(int32_t width, int32_t height, float clear_r, float clear_g, float clear_b,
                                        float rotation_speed, const char* title,
                                        const char* texture_path, const char* texture_path2,
                                        float camera_distance, float camera_pitch, float camera_yaw,
                                        float move_speed, float mouse_sensitivity,
                                        float camera_smoothing,
                                        float mesh1_r, float mesh1_g, float mesh1_b,
                                        float mesh2_r, float mesh2_g, float mesh2_b,
                                        int32_t instance_count) {
    if (width > 0) {
        g_config.width = static_cast<uint32_t>(width);
    }
    if (height > 0) {
        g_config.height = static_cast<uint32_t>(height);
    }
    g_config.clearR = clear_r;
    g_config.clearG = clear_g;
    g_config.clearB = clear_b;
    if (rotation_speed > 0.0f) {
        g_config.rotationSpeed = rotation_speed;
    }
    if (title && *title) {
        g_config.title = title;
    }
    if (texture_path && *texture_path) {
        g_config.texturePath = texture_path;
    }
    if (texture_path2 && *texture_path2) {
        g_config.texturePath2 = texture_path2;
    }
    if (camera_distance > 0.0f) {
        g_config.cameraDistance = camera_distance;
    }
    g_config.cameraPitch = camera_pitch;
    g_config.cameraYaw = camera_yaw;
    if (move_speed > 0.0f) {
        g_config.moveSpeed = move_speed;
    }
    if (mouse_sensitivity > 0.0f) {
        g_config.mouseSensitivity = mouse_sensitivity;
    }
    if (camera_smoothing >= 0.0f) {
        g_config.cameraSmoothing = camera_smoothing;
    }
    g_config.mesh1Color[0] = mesh1_r;
    g_config.mesh1Color[1] = mesh1_g;
    g_config.mesh1Color[2] = mesh1_b;
    g_config.mesh2Color[0] = mesh2_r;
    g_config.mesh2Color[1] = mesh2_g;
    g_config.mesh2Color[2] = mesh2_b;
    if (instance_count > 0) {
        g_config.instanceCount = static_cast<uint32_t>(instance_count);
    }
}

extern "C" int flow_vk_2048_init(int32_t width, int32_t height, const char* title, int32_t capacity) {
    if (g_flow_app) {
        return 0;
    }
    g_tileMode = false;
    g_externalInstanceMode = true;
    g_externalInstanceCapacity = capacity > 0 ? static_cast<uint32_t>(capacity) : 16;
    g_config.rotationSpeed = 0.0f;
    g_config.cameraSmoothing = 0.0f;
    g_config.instanceCount = g_externalInstanceCapacity;
    g_config.clearR = 0.10f;
    g_config.clearG = 0.09f;
    g_config.clearB = 0.08f;
    if (width > 0) {
        g_config.width = static_cast<uint32_t>(width);
    }
    if (height > 0) {
        g_config.height = static_cast<uint32_t>(height);
    }
    if (title && *title) {
        g_config.title = title;
    } else {
        g_config.title = "Flow Vulkan 2048";
    }

    g_flow_app = new VulkanApp();
    try {
        g_flow_app->init();
    } catch (const std::exception& e) {
        std::cerr << "error: " << e.what() << std::endl;
        delete g_flow_app;
        g_flow_app = nullptr;
        return -1;
    }
    return 0;
}

extern "C" void flow_vk_2048_shutdown() {
    if (!g_flow_app) {
        return;
    }
    g_flow_app->waitIdle();
    g_flow_app->shutdown();
    delete g_flow_app;
    g_flow_app = nullptr;
}

extern "C" int32_t flow_vk_2048_should_close() {
    if (!g_flow_app) {
        return 1;
    }
    return g_flow_app->shouldClose() ? 1 : 0;
}

extern "C" void flow_vk_2048_poll() {
    if (!g_flow_app) {
        return;
    }
    g_flow_app->poll();
}

extern "C" int32_t flow_vk_2048_key_down(int32_t key) {
    if (!g_flow_app) {
        return 0;
    }
    return g_flow_app->keyDown(key);
}

extern "C" void flow_vk_2048_draw(const float* instance_data, int32_t count) {
    if (!g_flow_app) {
        return;
    }
    if (!instance_data || count <= 0) {
        g_flow_app->renderExternal(nullptr, 0);
        return;
    }
    g_flow_app->renderExternal(instance_data, static_cast<uint32_t>(count));
}

extern "C" void flow_vk_2048_upload_texture(const uint8_t* pixels, int32_t width, int32_t height) {
    if (!g_flow_app) {
        return;
    }
    if (!pixels || width <= 0 || height <= 0) {
        return;
    }
    g_flow_app->uploadExternalTexture(pixels, width, height);
}

extern "C" int flow_vulkan_2048_run(int32_t pretty, int32_t trace, int32_t validation,
                                   int32_t width, int32_t height, const char* title) {
    if (pretty) {
        setenv("FLOW_VK_PRETTY", "1", 1);
    }
    if (trace) {
        setenv("FLOW_VK_TRACE", "1", 1);
    }
    if (!validation) {
        setenv("FLOW_VK_NO_VALIDATION", "1", 1);
    }

    g_tileMode = true;
    if (width > 0) {
        g_config.width = static_cast<uint32_t>(width);
    }
    if (height > 0) {
        g_config.height = static_cast<uint32_t>(height);
    }
    g_config.rotationSpeed = 0.0f;
    g_config.cameraSmoothing = 0.0f;
    g_config.instanceCount = 16;
    g_config.clearR = 0.10f;
    g_config.clearG = 0.09f;
    g_config.clearB = 0.08f;
    if (title && *title) {
        g_config.title = title;
    } else {
        g_config.title = "Flow Vulkan 2048";
    }

    VulkanApp app;
    try {
        app.run();
    } catch (const std::exception& e) {
        std::cerr << "error: " << e.what() << std::endl;
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}

#ifndef FLOW_VK_STANDALONE
int flow_vk_scene_entry() {
#else
int main() {
#endif
    VulkanApp app;
    try {
        app.run();
    } catch (const std::exception& e) {
        std::cerr << "error: " << e.what() << std::endl;
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
