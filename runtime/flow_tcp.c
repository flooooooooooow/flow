/* Thin TCP / HTTP route kernels for Flow harnesses (lib/runtime/tcp.flow, http_routed.flow). */
#include "flow_fiber.h"

#include <arpa/inet.h>
#include <netinet/in.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

/* Connect to 127.0.0.1:port. host_hash reserved (ignored; loopback only). */
int32_t flow_rt_tcp_connect(int32_t host_hash, int32_t port) {
    (void)host_hash;
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return -1;
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons((uint16_t)port);
    if (connect(fd, (struct sockaddr *)&addr, sizeof(addr)) != 0) {
        close(fd);
        return -1;
    }
    return (int32_t)fd;
}

int32_t flow_rt_tcp_listen(int32_t port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return -1;
    int yes = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons((uint16_t)port);
    if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        close(fd);
        return -1;
    }
    if (listen(fd, 128) < 0) {
        close(fd);
        return -1;
    }
    return (int32_t)fd;
}

int32_t flow_rt_tcp_accept(int32_t listen_fd) {
    if (listen_fd < 0) return -1;
    return (int32_t)accept(listen_fd, NULL, NULL);
}

int32_t flow_rt_tcp_close(int32_t fd) {
    if (fd < 0) return -1;
    return close(fd) == 0 ? 0 : -1;
}

int32_t flow_rt_tcp_recv(int32_t fd, void *buf, int32_t len) {
    if (fd < 0 || !buf || len <= 0) return -1;
    ssize_t n = recv(fd, buf, (size_t)len, 0);
    return (int32_t)n;
}

int32_t flow_rt_tcp_send(int32_t fd, const void *buf, int32_t len) {
    if (fd < 0 || !buf || len <= 0) return -1;
    ssize_t n = send(fd, buf, (size_t)len, 0);
    return (int32_t)n;
}

static int32_t flow_rt_http_parse_request(const char *req, int32_t req_len,
                                          char *out_path, int32_t path_cap) {
    if (!req || req_len <= 0 || !out_path || path_cap < 2) return -1;
    const char *p = req;
    const char *end = req + req_len;
    int method = 0;
    if (req_len >= 3 && memcmp(p, "GET", 3) == 0) {
        method = 1;
        p += 3;
    } else if (req_len >= 4 && memcmp(p, "POST", 4) == 0) {
        method = 2;
        p += 4;
    } else if (req_len >= 3 && memcmp(p, "PUT", 3) == 0) {
        method = 3;
        p += 3;
    } else if (req_len >= 6 && memcmp(p, "DELETE", 6) == 0) {
        method = 4;
        p += 6;
    } else {
        return 0;
    }
    while (p < end && *p == ' ') p++;
    int i = 0;
    while (p < end && *p != ' ' && *p != '\r' && *p != '\n' && i < path_cap - 1) {
        out_path[i++] = *p++;
    }
    out_path[i] = '\0';
    return method;
}

static int g_http_mw_reqid = 1;
static int g_http_mw_auth = 0; /* /api requires Authorization: Bearer flow */
static uint64_t g_http_req_seq = 0;
static int g_http_last_auth_ok = 0;

void flow_rt_http_mw_enable(int32_t on) {
    g_http_mw_reqid = on ? 1 : 0;
}

void flow_rt_http_mw_auth_enable(int32_t on) {
    g_http_mw_auth = on ? 1 : 0;
}

int32_t flow_rt_http_last_auth_ok(void) {
    return g_http_last_auth_ok ? 1 : 0;
}

static int header_has_bearer_flow(const char *req) {
    const char *p = strstr(req, "Authorization:");
    if (!p) p = strstr(req, "authorization:");
    if (!p) return 0;
    return strstr(p, "Bearer flow") != NULL || strstr(p, "bearer flow") != NULL;
}

int32_t flow_rt_http_reply(int32_t fd, int32_t status, const char *content_type,
                           const char *body, int32_t body_len) {
    if (fd < 0 || !body || body_len < 0) return -1;
    const char *reason = "OK";
    if (status == 404) reason = "Not Found";
    else if (status == 400) reason = "Bad Request";
    else if (status == 500) reason = "Internal Server Error";
    else if (status == 201) reason = "Created";
    else if (status == 401) reason = "Unauthorized";
    if (!content_type) content_type = "text/plain";
    char hdr[384];
    int n;
    if (g_http_mw_reqid) {
        uint64_t rid = __atomic_add_fetch(&g_http_req_seq, 1, __ATOMIC_RELAXED);
        n = snprintf(hdr, sizeof(hdr),
                     "HTTP/1.1 %d %s\r\nContent-Type: %s\r\n"
                     "X-Request-Id: %llu\r\n"
                     "Content-Length: %d\r\nConnection: close\r\n\r\n",
                     status, reason, content_type,
                     (unsigned long long)rid, body_len);
    } else {
        n = snprintf(hdr, sizeof(hdr),
                     "HTTP/1.1 %d %s\r\nContent-Type: %s\r\n"
                     "Content-Length: %d\r\nConnection: close\r\n\r\n",
                     status, reason, content_type, body_len);
    }
    if (n <= 0) return -1;
    if (flow_rt_tcp_send(fd, hdr, n) < 0) return -1;
    if (body_len > 0 && flow_rt_tcp_send(fd, body, body_len) < 0) return -1;
    return n + body_len;
}

/* route_kind: 0=GET /, 1=GET /api, 2=GET /health, 3=other/404, <0=fail */
int32_t flow_rt_http_recv_route_kind(int32_t cfd) {
    char buf[2048];
    char path[256];
    int32_t n = flow_rt_tcp_recv(cfd, buf, (int32_t)sizeof(buf) - 1);
    if (n <= 0) return -1;
    buf[n] = '\0';
    g_http_last_auth_ok = header_has_bearer_flow(buf);
    int32_t method = flow_rt_http_parse_request(buf, n, path, (int32_t)sizeof(path));
    if (method != 1) return 3;
    if (path[0] == '/' && path[1] == '\0') return 0;
    if (strcmp(path, "/api") == 0) return 1;
    if (strcmp(path, "/health") == 0) return 2;
    return 3;
}

int32_t flow_rt_http_mw_auth_required(void) {
    return g_http_mw_auth ? 1 : 0;
}

/* flow_http_route_one / flow_http_routed_serve → lib/runtime/http_routed.flow */
void flow_http_route_one(int32_t cfd); /* Flow */

typedef struct {
    int32_t lfd;
    int32_t n;
} serve_pack;

static void *serve_thread(void *arg) {
    serve_pack *p = (serve_pack *)arg;
    for (int i = 0; i < p->n; i++) {
        int32_t cfd = flow_rt_tcp_accept(p->lfd);
        if (cfd < 0) continue;
        flow_http_route_one(cfd);
        flow_rt_tcp_close(cfd);
    }
    return NULL;
}

static void http_conn_fiber(void *arg) {
    int32_t cfd = (int32_t)(intptr_t)arg;
    flow_http_route_one(cfd);
    flow_rt_tcp_close(cfd);
}

static void *fiber_accept_thread(void *arg) {
    serve_pack *p = (serve_pack *)arg;
    for (int i = 0; i < p->n; i++) {
        int32_t cfd = flow_rt_tcp_accept(p->lfd);
        if (cfd < 0) continue;
        if (flow_fiber_spawn(http_conn_fiber, (void *)(intptr_t)cfd) < 0) {
            flow_http_route_one(cfd);
            flow_rt_tcp_close(cfd);
        }
    }
    return NULL;
}

static int client_get_ex(int32_t port, const char *path, const char *extra_hdr,
                         char *out, int out_cap) {
    int c = socket(AF_INET, SOCK_STREAM, 0);
    if (c < 0) return -1;
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons((uint16_t)port);
    if (connect(c, (struct sockaddr *)&addr, sizeof(addr)) != 0) {
        close(c);
        return -1;
    }
    char req[384];
    if (extra_hdr && extra_hdr[0]) {
        snprintf(req, sizeof(req), "GET %s HTTP/1.0\r\n%s\r\n\r\n", path, extra_hdr);
    } else {
        snprintf(req, sizeof(req), "GET %s HTTP/1.0\r\n\r\n", path);
    }
    send(c, req, strlen(req), 0);
    int n = (int)recv(c, out, (size_t)(out_cap - 1), 0);
    if (n < 0) n = 0;
    out[n] = '\0';
    close(c);
    return n;
}

static int client_get(int32_t port, const char *path, char *out, int out_cap) {
    return client_get_ex(port, path, NULL, out, out_cap);
}

static int client_get_retry(int32_t port, const char *path, char *out, int out_cap) {
    for (int attempt = 0; attempt < 50; attempt++) {
        int n = client_get(port, path, out, out_cap);
        if (n > 0) return n;
        usleep(2000);
    }
    return -1;
}

static int client_get_auth_retry(int32_t port, const char *path, const char *hdr,
                                 char *out, int out_cap) {
    for (int attempt = 0; attempt < 50; attempt++) {
        int n = client_get_ex(port, path, hdr, out, out_cap);
        if (n > 0) return n;
        usleep(2000);
    }
    return -1;
}

/* Returns 1 if /, /api, /health, /missing + middleware header all pass. */
int32_t flow_rt_http_routed_selftest(int32_t port) {
    flow_rt_http_mw_enable(1);
    flow_rt_http_mw_auth_enable(0);
    int32_t lfd = flow_rt_tcp_listen(port);
    if (lfd < 0) return -1;
    serve_pack pack = {.lfd = lfd, .n = 4};
    pthread_t th;
    if (pthread_create(&th, NULL, serve_thread, &pack) != 0) {
        flow_rt_tcp_close(lfd);
        return -1;
    }
    usleep(5000);
    char resp[1024];
    int ok = 1;
    if (client_get_retry(port, "/", resp, (int)sizeof(resp)) <= 0 ||
        strstr(resp, "200") == NULL || strstr(resp, "X-Request-Id:") == NULL) {
        ok = 0;
    }
    if (client_get_retry(port, "/api", resp, (int)sizeof(resp)) <= 0 ||
        strstr(resp, "200") == NULL || strstr(resp, "ok") == NULL) {
        ok = 0;
    }
    if (client_get_retry(port, "/health", resp, (int)sizeof(resp)) <= 0 ||
        strstr(resp, "200") == NULL) {
        ok = 0;
    }
    if (client_get_retry(port, "/missing", resp, (int)sizeof(resp)) <= 0 ||
        strstr(resp, "404") == NULL) {
        ok = 0;
    }
    pthread_join(th, NULL);
    flow_rt_tcp_close(lfd);
    return ok ? 1 : 0;
}

/* Auth middleware + fiber-per-connection serve selftest.
 * Expect: /api without token → 401; with Bearer flow → 200; / → 200. */
int32_t flow_rt_http_fiber_selftest(int32_t port) {
    flow_rt_http_mw_enable(1);
    flow_rt_http_mw_auth_enable(1);
    flow_fiber_init();
    int32_t lfd = flow_rt_tcp_listen(port);
    if (lfd < 0) return -1;
    serve_pack pack = {.lfd = lfd, .n = 3};
    pthread_t th;
    if (pthread_create(&th, NULL, fiber_accept_thread, &pack) != 0) {
        flow_rt_tcp_close(lfd);
        return -1;
    }
    usleep(5000);
    char resp[1024];
    int ok = 1;
    if (client_get_auth_retry(port, "/api", NULL, resp, (int)sizeof(resp)) <= 0 ||
        strstr(resp, "401") == NULL) {
        ok = 0;
    }
    if (client_get_auth_retry(port, "/api", "Authorization: Bearer flow", resp,
                              (int)sizeof(resp)) <= 0 ||
        strstr(resp, "200") == NULL || strstr(resp, "ok") == NULL) {
        ok = 0;
    }
    if (client_get_retry(port, "/", resp, (int)sizeof(resp)) <= 0 ||
        strstr(resp, "200") == NULL) {
        ok = 0;
    }
    pthread_join(th, NULL);
    flow_fiber_run(); /* drain any leftover conn fibers */
    flow_rt_tcp_close(lfd);
    flow_rt_http_mw_auth_enable(0);
    return ok ? 1 : 0;
}
