#ifndef FLOW_DNS_H
#define FLOW_DNS_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Resolve hostname to first IPv4 address (dotted string into buf, NUL-terminated).
 * On success returns string length (excluding NUL). On failure returns -1. */
int64_t flow_dns_lookup(const char *hostname, char *buf, int64_t buflen);

/* Resolve hostname to first IPv4 as network-order u32. Returns 0 on failure. */
uint32_t flow_dns_lookup_u32(const char *hostname);

#ifdef __cplusplus
}
#endif

#endif /* FLOW_DNS_H */
