#include "flow_dns.h"

#include <arpa/inet.h>
#include <netdb.h>
#include <netinet/in.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>

static int flow_dns_first_ipv4(const char *hostname, struct in_addr *out) {
    if (!hostname || !out) {
        return -1;
    }

    struct addrinfo hints;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;

    struct addrinfo *res = NULL;
    int rc = getaddrinfo(hostname, NULL, &hints, &res);
    if (rc != 0 || !res) {
        if (res) {
            freeaddrinfo(res);
        }
        return -1;
    }

    int ok = -1;
    for (struct addrinfo *ai = res; ai != NULL; ai = ai->ai_next) {
        if (ai->ai_family == AF_INET && ai->ai_addr) {
            struct sockaddr_in *sin = (struct sockaddr_in *)ai->ai_addr;
            *out = sin->sin_addr;
            ok = 0;
            break;
        }
    }
    freeaddrinfo(res);
    return ok;
}

int64_t flow_dns_lookup(const char *hostname, char *buf, int64_t buflen) {
    if (!hostname || !buf || buflen <= 0) {
        return -1;
    }
    buf[0] = '\0';

    struct in_addr addr;
    if (flow_dns_first_ipv4(hostname, &addr) != 0) {
        return -1;
    }

    const char *dotted = inet_ntoa(addr);
    if (!dotted) {
        return -1;
    }

    size_t n = strlen(dotted);
    if ((int64_t)n + 1 > buflen) {
        return -1;
    }
    memcpy(buf, dotted, n + 1);
    return (int64_t)n;
}

uint32_t flow_dns_lookup_u32(const char *hostname) {
    struct in_addr addr;
    if (flow_dns_first_ipv4(hostname, &addr) != 0) {
        return 0;
    }
    return (uint32_t)addr.s_addr;
}
