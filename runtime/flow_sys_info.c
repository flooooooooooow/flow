#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

#if defined(__APPLE__)
#include <sys/sysctl.h>
#include <unistd.h>
#include <sys/utsname.h>
#elif defined(__linux__)
#include <unistd.h>
#include <sys/utsname.h>
#endif

static int flow_sysctl_string(const char* key, char* out, size_t out_len) {
#if defined(__APPLE__)
    size_t size = out_len;
    if (sysctlbyname(key, out, &size, NULL, 0) == 0) {
        out[out_len - 1] = '\0';
        return 0;
    }
    return -1;
#else
    (void)key; (void)out; (void)out_len;
    return -1;
#endif
}

int32_t num_cores() {
#if defined(__APPLE__) || defined(__linux__)
    long cores = sysconf(_SC_NPROCESSORS_ONLN);
    if (cores < 1) cores = 1;
    return (int32_t)cores;
#else
    return 1;
#endif
}

int32_t os_is_linux() {
#if defined(__linux__)
    return 1;
#else
    return 0;
#endif
}

int32_t os_is_windows() {
#if defined(_WIN32) || defined(_WIN64)
    return 1;
#else
    return 0;
#endif
}

int32_t os_is_macos() {
#if defined(__APPLE__)
    return 1;
#else
    return 0;
#endif
}

static int has_feature_token(const char* token, const char* feature_list) {
    if (!feature_list || !token) return 0;
    return strstr(feature_list, token) != NULL;
}

int32_t has_sse4() {
#if defined(__APPLE__)
    char buf[1024] = {0};
    if (flow_sysctl_string("machdep.cpu.features", buf, sizeof(buf)) == 0) {
        return has_feature_token("SSE4", buf) || has_feature_token("SSE4.1", buf) || has_feature_token("SSE4.2", buf);
    }
#endif
    return 0;
}

int32_t has_avx() {
#if defined(__APPLE__)
    char buf[1024] = {0};
    if (flow_sysctl_string("machdep.cpu.features", buf, sizeof(buf)) == 0) {
        return has_feature_token("AVX", buf);
    }
#endif
    return 0;
}

int32_t has_avx2() {
#if defined(__APPLE__)
    char buf[1024] = {0};
    if (flow_sysctl_string("machdep.cpu.leaf7_features", buf, sizeof(buf)) == 0) {
        return has_feature_token("AVX2", buf);
    }
#endif
    return 0;
}

int32_t has_avx512f() {
#if defined(__APPLE__)
    char buf[1024] = {0};
    if (flow_sysctl_string("machdep.cpu.leaf7_features", buf, sizeof(buf)) == 0) {
        return has_feature_token("AVX512F", buf);
    }
#endif
    return 0;
}

int32_t has_avx512_vnni() {
#if defined(__APPLE__)
    char buf[1024] = {0};
    if (flow_sysctl_string("machdep.cpu.leaf7_features", buf, sizeof(buf)) == 0) {
        return has_feature_token("AVX512VNNI", buf);
    }
#endif
    return 0;
}

int32_t has_neon() {
#if defined(__APPLE__)
    int value = 0;
    size_t size = sizeof(value);
    if (sysctlbyname("hw.optional.neon", &value, &size, NULL, 0) == 0) {
        return value ? 1 : 0;
    }
#endif
#if defined(__ARM_NEON)
    return 1;
#else
    return 0;
#endif
}

int32_t is_apple_m1() {
#if defined(__APPLE__)
    char buf[1024] = {0};
    if (flow_sysctl_string("machdep.cpu.brand_string", buf, sizeof(buf)) == 0) {
        return strstr(buf, "Apple M1") != NULL;
    }
#endif
    return 0;
}

int32_t has_intel_amx() {
#if defined(__APPLE__)
    char buf[1024] = {0};
    if (flow_sysctl_string("machdep.cpu.leaf7_features", buf, sizeof(buf)) == 0) {
        return has_feature_token("AMX", buf);
    }
#endif
    return 0;
}

char* current_cpu() {
    static char buf[256];
    buf[0] = '\0';
#if defined(__APPLE__)
    if (flow_sysctl_string("machdep.cpu.brand_string", buf, sizeof(buf)) == 0) {
        return buf;
    }
    if (flow_sysctl_string("hw.model", buf, sizeof(buf)) == 0) {
        return buf;
    }
    if (flow_sysctl_string("hw.machine", buf, sizeof(buf)) == 0) {
        return buf;
    }
#endif
#if defined(__APPLE__) && defined(__aarch64__)
    snprintf(buf, sizeof(buf), "Apple Silicon");
    return buf;
#endif
    snprintf(buf, sizeof(buf), "unknown");
    return buf;
}

char* current_arch() {
    static char buf[256];
    buf[0] = '\0';
#if defined(__APPLE__)
    if (flow_sysctl_string("hw.machine", buf, sizeof(buf)) == 0) {
        return buf;
    }
#endif
#if defined(__linux__)
    struct utsname u;
    if (uname(&u) == 0) {
        strncpy(buf, u.machine, sizeof(buf) - 1);
        buf[sizeof(buf) - 1] = '\0';
        return buf;
    }
#endif
    snprintf(buf, sizeof(buf), "unknown");
    return buf;
}

char* _cpu_features_string() {
    static char buf[512];
    buf[0] = '\0';

    const struct {
        const char* label;
        int32_t (*fn)();
    } features[] = {
        { " sse4", has_sse4 },
        { " avx", has_avx },
        { " avx2", has_avx2 },
        { " avx512f", has_avx512f },
        { " avx512_vnni", has_avx512_vnni },
        { " intel_amx", has_intel_amx },
        { " neon", has_neon },
        { " Apple M1", is_apple_m1 },
    };

    for (size_t i = 0; i < sizeof(features) / sizeof(features[0]); i++) {
        if (features[i].fn && features[i].fn()) {
            strncat(buf, features[i].label, sizeof(buf) - strlen(buf) - 1);
        }
    }
    if (buf[0] == '\0') {
        strncpy(buf, " (none)", sizeof(buf) - 1);
        buf[sizeof(buf) - 1] = '\0';
    }
    return buf;
}

void print_kv_str(const char* label, const char* val) {
    if (!label) label = "";
    if (!val) val = "";
    printf("%s %s\n", label, val);
}

void print_kv_i32(const char* label, int32_t val) {
    if (!label) label = "";
    printf("%s %d\n", label, val);
}
