/* Thin sysctl/uname probes for Flow sysinfo (lib/runtime/sysinfo_probes.flow). */
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#if defined(__APPLE__)
#include <sys/sysctl.h>
#include <unistd.h>
#elif defined(__linux__)
#include <unistd.h>
#include <sys/utsname.h>
#endif

int32_t flow_rt_sysctl_has(const char *key, const char *token) {
#if defined(__APPLE__)
    char buf[1024] = {0};
    size_t size = sizeof(buf);
    if (sysctlbyname(key, buf, &size, NULL, 0) != 0) return 0;
    buf[sizeof(buf) - 1] = '\0';
    return token && strstr(buf, token) != NULL ? 1 : 0;
#else
    (void)key;
    (void)token;
    return 0;
#endif
}

int32_t flow_rt_sysctl_int_nonzero(const char *key) {
#if defined(__APPLE__)
    int value = 0;
    size_t size = sizeof(value);
    if (sysctlbyname(key, &value, &size, NULL, 0) != 0) return 0;
    return value ? 1 : 0;
#else
    (void)key;
#if defined(__ARM_NEON)
    if (key && strstr(key, "neon")) return 1;
#endif
    return 0;
#endif
}

int32_t flow_rt_num_cores(void) {
#if defined(__APPLE__) || defined(__linux__)
    long cores = sysconf(_SC_NPROCESSORS_ONLN);
    if (cores < 1) cores = 1;
    return (int32_t)cores;
#else
    return 1;
#endif
}

int32_t flow_rt_os_is_linux(void) {
#if defined(__linux__)
    return 1;
#else
    return 0;
#endif
}

int32_t flow_rt_os_is_windows(void) {
#if defined(_WIN32) || defined(_WIN64)
    return 1;
#else
    return 0;
#endif
}

int32_t flow_rt_os_is_macos(void) {
#if defined(__APPLE__)
    return 1;
#else
    return 0;
#endif
}

int32_t flow_rt_has_neon(void) {
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

char *flow_rt_current_cpu(void) {
    static char buf[256];
    buf[0] = '\0';
#if defined(__APPLE__)
    size_t size = sizeof(buf);
    if (sysctlbyname("machdep.cpu.brand_string", buf, &size, NULL, 0) == 0) return buf;
    size = sizeof(buf);
    if (sysctlbyname("hw.model", buf, &size, NULL, 0) == 0) return buf;
    size = sizeof(buf);
    if (sysctlbyname("hw.machine", buf, &size, NULL, 0) == 0) return buf;
#if defined(__aarch64__)
    snprintf(buf, sizeof(buf), "Apple Silicon");
    return buf;
#endif
#endif
    snprintf(buf, sizeof(buf), "unknown");
    return buf;
}

char *flow_rt_current_arch(void) {
    static char buf[256];
    buf[0] = '\0';
#if defined(__APPLE__)
    size_t size = sizeof(buf);
    if (sysctlbyname("hw.machine", buf, &size, NULL, 0) == 0) return buf;
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
