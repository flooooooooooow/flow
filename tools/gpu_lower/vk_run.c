/* vk_run: run a SPIR-V compute module from `flow gpu-lower` through Vulkan.
 *
 *   vk_run MODULE.spv DATA_DIR OUT_DIR
 *
 * DATA_DIR/launch.txt lists the buffers and the dispatches:
 *
 *   buffer IDX f32|i32 COUNT in|out|scalar
 *   dispatch KERNEL GX GY GZ IDX...
 *
 * Buffer IDX starts from DATA_DIR/in_IDX.bin. A dispatch binds its buffers
 * to descriptor set 0, bindings 0.. in order, which is the interface
 * mlir-opt's convert-gpu-to-spirv gives each kernel argument (a scalar
 * argument is a one-element storage buffer). Each dispatch runs GX*GY*GZ
 * workgroups and finishes before the next starts. After the last one every
 * buffer is written to OUT_DIR/gpu_IDX.bin.
 *
 * On macOS the loader finds MoltenVK. MoltenVK's fast math is turned off
 * (MVK_CONFIG_FAST_MATH_ENABLED=0) unless the caller set it.
 *
 * Status: 0 ran, 1 a Vulkan or file error, 2 usage, 3 no Vulkan driver or
 * device.
 */
#include <vulkan/vulkan.h>

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_BUFS 32
#define MAX_DISPATCH 32
#define MAX_ARGS 16

typedef struct {
    int used;
    int64_t bytes;
    VkBuffer buf;
    VkDeviceMemory mem;
    void *map;
} Buf;

typedef struct {
    char kernel[128];
    uint32_t g[3];
    int nargs;
    int args[MAX_ARGS];
} Dispatch;

static Buf bufs[MAX_BUFS];
static Dispatch disp[MAX_DISPATCH];
static int ndisp = 0;

static int fail(const char *what, VkResult r) {
    fprintf(stderr, "vk_run: %s failed (VkResult %d)\n", what, (int)r);
    return 1;
}

static void *read_file(const char *path, int64_t *len) {
    FILE *f = fopen(path, "rb");
    if (!f) {
        return NULL;
    }
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    fseek(f, 0, SEEK_SET);
    void *p = malloc(n > 0 ? (size_t)n : 1);
    if (n > 0 && fread(p, 1, (size_t)n, f) != (size_t)n) {
        free(p);
        fclose(f);
        return NULL;
    }
    fclose(f);
    *len = n;
    return p;
}

static int parse_launch(const char *dir) {
    char path[4096];
    snprintf(path, sizeof path, "%s/launch.txt", dir);
    FILE *f = fopen(path, "r");
    if (!f) {
        fprintf(stderr, "vk_run: cannot open %s\n", path);
        return 1;
    }
    char line[1024];
    while (fgets(line, sizeof line, f)) {
        char *tok = strtok(line, " \t\r\n");
        if (!tok) {
            continue;
        }
        if (strcmp(tok, "buffer") == 0) {
            int idx = atoi(strtok(NULL, " \t\r\n"));
            char *ty = strtok(NULL, " \t\r\n");
            long count = atol(strtok(NULL, " \t\r\n"));
            if (idx < 0 || idx >= MAX_BUFS || !ty) {
                fclose(f);
                return 1;
            }
            bufs[idx].used = 1;
            bufs[idx].bytes = (int64_t)count * 4;
        } else if (strcmp(tok, "dispatch") == 0) {
            if (ndisp >= MAX_DISPATCH) {
                fclose(f);
                return 1;
            }
            Dispatch *d = &disp[ndisp++];
            snprintf(d->kernel, sizeof d->kernel, "%s", strtok(NULL, " \t\r\n"));
            for (int i = 0; i < 3; i++) {
                d->g[i] = (uint32_t)atol(strtok(NULL, " \t\r\n"));
            }
            char *a;
            d->nargs = 0;
            while ((a = strtok(NULL, " \t\r\n")) && d->nargs < MAX_ARGS) {
                d->args[d->nargs++] = atoi(a);
            }
        }
    }
    fclose(f);
    return 0;
}

int main(int argc, char **argv) {
    if (argc != 4) {
        fprintf(stderr, "usage: vk_run MODULE.spv DATA_DIR OUT_DIR\n");
        return 2;
    }
    setenv("MVK_CONFIG_FAST_MATH_ENABLED", "0", 0);
    if (parse_launch(argv[2]) != 0) {
        return 1;
    }
    int64_t code_len = 0;
    uint32_t *code = read_file(argv[1], &code_len);
    if (!code || code_len % 4 != 0) {
        fprintf(stderr, "vk_run: cannot read SPIR-V %s\n", argv[1]);
        return 1;
    }

    VkApplicationInfo app = {VK_STRUCTURE_TYPE_APPLICATION_INFO};
    app.pApplicationName = "flow-gpu-lower";
    app.apiVersion = VK_API_VERSION_1_1;
    const char *iexts[] = {"VK_KHR_portability_enumeration"};
    VkInstanceCreateInfo ici = {VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO};
    ici.pApplicationInfo = &app;
#ifdef __APPLE__
    ici.flags = VK_INSTANCE_CREATE_ENUMERATE_PORTABILITY_BIT_KHR;
    ici.enabledExtensionCount = 1;
    ici.ppEnabledExtensionNames = iexts;
#else
    (void)iexts;
#endif
    VkInstance inst;
    VkResult r = vkCreateInstance(&ici, NULL, &inst);
    if (r == VK_ERROR_INCOMPATIBLE_DRIVER) {
        fprintf(stderr, "vk_run: no Vulkan driver\n");
        return 3;
    }
    if (r != VK_SUCCESS) {
        return fail("vkCreateInstance", r);
    }
    uint32_t npd = 0;
    vkEnumeratePhysicalDevices(inst, &npd, NULL);
    if (npd == 0) {
        fprintf(stderr, "vk_run: no Vulkan device\n");
        return 3;
    }
    VkPhysicalDevice pds[8];
    if (npd > 8) {
        npd = 8;
    }
    vkEnumeratePhysicalDevices(inst, &npd, pds);
    VkPhysicalDevice pd = pds[0];
    VkPhysicalDeviceProperties props;
    vkGetPhysicalDeviceProperties(pd, &props);
    fprintf(stderr, "vk_run: device %s\n", props.deviceName);

    uint32_t nqf = 0;
    vkGetPhysicalDeviceQueueFamilyProperties(pd, &nqf, NULL);
    VkQueueFamilyProperties qfp[16];
    if (nqf > 16) {
        nqf = 16;
    }
    vkGetPhysicalDeviceQueueFamilyProperties(pd, &nqf, qfp);
    uint32_t qf = UINT32_MAX;
    for (uint32_t i = 0; i < nqf; i++) {
        if (qfp[i].queueFlags & VK_QUEUE_COMPUTE_BIT) {
            qf = i;
            break;
        }
    }
    if (qf == UINT32_MAX) {
        fprintf(stderr, "vk_run: no compute queue\n");
        return 1;
    }
    float prio = 1.0f;
    VkDeviceQueueCreateInfo qci = {VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO};
    qci.queueFamilyIndex = qf;
    qci.queueCount = 1;
    qci.pQueuePriorities = &prio;
    const char *dexts[] = {"VK_KHR_portability_subset"};
    VkDeviceCreateInfo dci = {VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO};
    dci.queueCreateInfoCount = 1;
    dci.pQueueCreateInfos = &qci;
#ifdef __APPLE__
    dci.enabledExtensionCount = 1;
    dci.ppEnabledExtensionNames = dexts;
#else
    (void)dexts;
#endif
    VkDevice dev;
    r = vkCreateDevice(pd, &dci, NULL, &dev);
    if (r != VK_SUCCESS) {
        return fail("vkCreateDevice", r);
    }
    VkQueue queue;
    vkGetDeviceQueue(dev, qf, 0, &queue);

    VkPhysicalDeviceMemoryProperties mp;
    vkGetPhysicalDeviceMemoryProperties(pd, &mp);
    VkMemoryPropertyFlags want = VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT;
    for (int b = 0; b < MAX_BUFS; b++) {
        if (!bufs[b].used) {
            continue;
        }
        char path[4096];
        snprintf(path, sizeof path, "%s/in_%d.bin", argv[2], b);
        int64_t n = 0;
        void *init = read_file(path, &n);
        if (!init || n != bufs[b].bytes) {
            fprintf(stderr, "vk_run: %s missing or not %lld bytes\n", path, (long long)bufs[b].bytes);
            return 1;
        }
        VkBufferCreateInfo bci = {VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};
        bci.size = (VkDeviceSize)bufs[b].bytes;
        bci.usage = VK_BUFFER_USAGE_STORAGE_BUFFER_BIT;
        bci.sharingMode = VK_SHARING_MODE_EXCLUSIVE;
        r = vkCreateBuffer(dev, &bci, NULL, &bufs[b].buf);
        if (r != VK_SUCCESS) {
            return fail("vkCreateBuffer", r);
        }
        VkMemoryRequirements req;
        vkGetBufferMemoryRequirements(dev, bufs[b].buf, &req);
        uint32_t mt = UINT32_MAX;
        for (uint32_t i = 0; i < mp.memoryTypeCount; i++) {
            if ((req.memoryTypeBits & (1u << i)) && (mp.memoryTypes[i].propertyFlags & want) == want) {
                mt = i;
                break;
            }
        }
        if (mt == UINT32_MAX) {
            fprintf(stderr, "vk_run: no host-visible memory type\n");
            return 1;
        }
        VkMemoryAllocateInfo mai = {VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
        mai.allocationSize = req.size;
        mai.memoryTypeIndex = mt;
        r = vkAllocateMemory(dev, &mai, NULL, &bufs[b].mem);
        if (r != VK_SUCCESS) {
            return fail("vkAllocateMemory", r);
        }
        vkBindBufferMemory(dev, bufs[b].buf, bufs[b].mem, 0);
        vkMapMemory(dev, bufs[b].mem, 0, VK_WHOLE_SIZE, 0, &bufs[b].map);
        memcpy(bufs[b].map, init, (size_t)n);
        free(init);
    }

    VkShaderModuleCreateInfo smci = {VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO};
    smci.codeSize = (size_t)code_len;
    smci.pCode = code;
    VkShaderModule sm;
    r = vkCreateShaderModule(dev, &smci, NULL, &sm);
    if (r != VK_SUCCESS) {
        return fail("vkCreateShaderModule", r);
    }
    VkCommandPoolCreateInfo cpci = {VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO};
    cpci.queueFamilyIndex = qf;
    cpci.flags = VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;
    VkCommandPool pool;
    vkCreateCommandPool(dev, &cpci, NULL, &pool);

    for (int di = 0; di < ndisp; di++) {
        Dispatch *d = &disp[di];
        VkDescriptorSetLayoutBinding lb[MAX_ARGS];
        for (int i = 0; i < d->nargs; i++) {
            if (d->args[i] < 0 || d->args[i] >= MAX_BUFS || !bufs[d->args[i]].used) {
                fprintf(stderr, "vk_run: dispatch %s names unknown buffer %d\n", d->kernel, d->args[i]);
                return 1;
            }
            memset(&lb[i], 0, sizeof lb[i]);
            lb[i].binding = (uint32_t)i;
            lb[i].descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;
            lb[i].descriptorCount = 1;
            lb[i].stageFlags = VK_SHADER_STAGE_COMPUTE_BIT;
        }
        VkDescriptorSetLayoutCreateInfo dlci = {VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO};
        dlci.bindingCount = (uint32_t)d->nargs;
        dlci.pBindings = lb;
        VkDescriptorSetLayout dsl;
        vkCreateDescriptorSetLayout(dev, &dlci, NULL, &dsl);
        VkPipelineLayoutCreateInfo plci = {VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO};
        plci.setLayoutCount = 1;
        plci.pSetLayouts = &dsl;
        VkPipelineLayout pl;
        vkCreatePipelineLayout(dev, &plci, NULL, &pl);
        VkComputePipelineCreateInfo cci = {VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO};
        cci.stage.sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;
        cci.stage.stage = VK_SHADER_STAGE_COMPUTE_BIT;
        cci.stage.module = sm;
        cci.stage.pName = d->kernel;
        cci.layout = pl;
        VkPipeline pipe;
        r = vkCreateComputePipelines(dev, VK_NULL_HANDLE, 1, &cci, NULL, &pipe);
        if (r != VK_SUCCESS) {
            return fail("vkCreateComputePipelines", r);
        }
        VkDescriptorPoolSize ps = {VK_DESCRIPTOR_TYPE_STORAGE_BUFFER, (uint32_t)d->nargs};
        VkDescriptorPoolCreateInfo dpci = {VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO};
        dpci.maxSets = 1;
        dpci.poolSizeCount = 1;
        dpci.pPoolSizes = &ps;
        VkDescriptorPool dp;
        vkCreateDescriptorPool(dev, &dpci, NULL, &dp);
        VkDescriptorSetAllocateInfo dsai = {VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO};
        dsai.descriptorPool = dp;
        dsai.descriptorSetCount = 1;
        dsai.pSetLayouts = &dsl;
        VkDescriptorSet ds;
        vkAllocateDescriptorSets(dev, &dsai, &ds);
        VkDescriptorBufferInfo dbi[MAX_ARGS];
        VkWriteDescriptorSet w[MAX_ARGS];
        for (int i = 0; i < d->nargs; i++) {
            dbi[i].buffer = bufs[d->args[i]].buf;
            dbi[i].offset = 0;
            dbi[i].range = VK_WHOLE_SIZE;
            memset(&w[i], 0, sizeof w[i]);
            w[i].sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET;
            w[i].dstSet = ds;
            w[i].dstBinding = (uint32_t)i;
            w[i].descriptorCount = 1;
            w[i].descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;
            w[i].pBufferInfo = &dbi[i];
        }
        vkUpdateDescriptorSets(dev, (uint32_t)d->nargs, w, 0, NULL);

        VkCommandBufferAllocateInfo cbai = {VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO};
        cbai.commandPool = pool;
        cbai.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
        cbai.commandBufferCount = 1;
        VkCommandBuffer cb;
        vkAllocateCommandBuffers(dev, &cbai, &cb);
        VkCommandBufferBeginInfo cbbi = {VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
        cbbi.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;
        vkBeginCommandBuffer(cb, &cbbi);
        vkCmdBindPipeline(cb, VK_PIPELINE_BIND_POINT_COMPUTE, pipe);
        vkCmdBindDescriptorSets(cb, VK_PIPELINE_BIND_POINT_COMPUTE, pl, 0, 1, &ds, 0, NULL);
        vkCmdDispatch(cb, d->g[0], d->g[1], d->g[2]);
        VkMemoryBarrier mb = {VK_STRUCTURE_TYPE_MEMORY_BARRIER};
        mb.srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
        mb.dstAccessMask = VK_ACCESS_HOST_READ_BIT;
        vkCmdPipelineBarrier(cb, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, VK_PIPELINE_STAGE_HOST_BIT, 0, 1, &mb, 0, NULL, 0, NULL);
        vkEndCommandBuffer(cb);
        VkSubmitInfo si = {VK_STRUCTURE_TYPE_SUBMIT_INFO};
        si.commandBufferCount = 1;
        si.pCommandBuffers = &cb;
        r = vkQueueSubmit(queue, 1, &si, VK_NULL_HANDLE);
        if (r != VK_SUCCESS) {
            return fail("vkQueueSubmit", r);
        }
        r = vkQueueWaitIdle(queue);
        if (r != VK_SUCCESS) {
            return fail("vkQueueWaitIdle", r);
        }
        vkFreeCommandBuffers(dev, pool, 1, &cb);
        vkDestroyDescriptorPool(dev, dp, NULL);
        vkDestroyPipeline(dev, pipe, NULL);
        vkDestroyPipelineLayout(dev, pl, NULL);
        vkDestroyDescriptorSetLayout(dev, dsl, NULL);
    }

    int rc = 0;
    for (int b = 0; b < MAX_BUFS; b++) {
        if (!bufs[b].used) {
            continue;
        }
        char path[4096];
        snprintf(path, sizeof path, "%s/gpu_%d.bin", argv[3], b);
        FILE *f = fopen(path, "wb");
        if (!f || fwrite(bufs[b].map, 1, (size_t)bufs[b].bytes, f) != (size_t)bufs[b].bytes) {
            fprintf(stderr, "vk_run: cannot write %s\n", path);
            rc = 1;
        }
        if (f) {
            fclose(f);
        }
        vkUnmapMemory(dev, bufs[b].mem);
        vkDestroyBuffer(dev, bufs[b].buf, NULL);
        vkFreeMemory(dev, bufs[b].mem, NULL);
    }
    vkDestroyShaderModule(dev, sm, NULL);
    vkDestroyCommandPool(dev, pool, NULL);
    vkDestroyDevice(dev, NULL);
    vkDestroyInstance(inst, NULL);
    free(code);
    return rc;
}
