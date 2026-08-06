/* Per-OS host probes for lib/runtime/sysinfo_probes.flow.
 *
 * Only the syscalls (sysctlbyname, sysconf, uname) and the compile-time #if
 * branches live here. Every fallback chain, substring test, clamp, and string
 * default is in Flow.
 */
#include <stdint.h>
#include <string.h>

#if defined(__APPLE__)
#include <sys/sysctl.h>
#include <unistd.h>
#elif defined(__linux__)
#include <sys/utsname.h>
#include <unistd.h>
#endif

/* NUL-terminated sysctl string into buf. 1 when the key was read. */
int32_t flow_rt_sysctl_string(const char *key, char *buf, int64_t cap) {
    if (!buf || cap <= 0) return 0;
    buf[0] = '\0';
#if defined(__APPLE__)
    size_t size = (size_t)cap;
    if (sysctlbyname(key, buf, &size, NULL, 0) != 0) {
        buf[0] = '\0';
        return 0;
    }
    buf[cap - 1] = '\0';
    return 1;
#else
    (void)key;
    return 0;
#endif
}

/* Integer sysctl into *out. 1 when the key was read. */
int32_t flow_rt_sysctl_int(const char *key, int32_t *out) {
    if (!out) return 0;
    *out = 0;
#if defined(__APPLE__)
    int value = 0;
    size_t size = sizeof(value);
    if (sysctlbyname(key, &value, &size, NULL, 0) != 0) return 0;
    *out = (int32_t)value;
    return 1;
#else
    (void)key;
    return 0;
#endif
}

/* uname(2) machine name into buf. 1 when uname succeeded. */
int32_t flow_rt_uname_machine(char *buf, int64_t cap) {
    if (!buf || cap <= 0) return 0;
    buf[0] = '\0';
#if defined(__linux__)
    struct utsname u;
    if (uname(&u) != 0) return 0;
    strncpy(buf, u.machine, (size_t)cap - 1);
    buf[cap - 1] = '\0';
    return 1;
#else
    return 0;
#endif
}

/* Raw sysconf answer; 0 when the platform has no such call. Flow clamps. */
int32_t flow_rt_online_cpus(void) {
#if defined(__APPLE__) || defined(__linux__)
    return (int32_t)sysconf(_SC_NPROCESSORS_ONLN);
#else
    return 0;
#endif
}

/* Everything the preprocessor knows and the running host cannot be asked,
 * as one bitmask. Flow decodes it (FLOW_HOST_* in sysinfo_probes.flow). */
int32_t flow_rt_host_facts(void) {
    int32_t facts = 0;
#if defined(__APPLE__)
    facts |= 1;
#endif
#if defined(__linux__)
    facts |= 2;
#endif
#if defined(_WIN32) || defined(_WIN64)
    facts |= 4;
#endif
#if defined(__ARM_NEON)
    facts |= 8;
#endif
#if defined(__aarch64__) || defined(_M_ARM64)
    facts |= 16;
#endif
    return facts;
}
