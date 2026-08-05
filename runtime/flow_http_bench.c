/* HTTP socket bodies for Flow harness (lib/runtime/http_bench.flow). */
#include <arpa/inet.h>
#include <netinet/in.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

static const char *RESP =
    "HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\nOK";

typedef struct {
    int listen_fd;
    volatile int stop;
} http_srv;

static void *accept_loop(void *arg) {
    http_srv *s = (http_srv *)arg;
    char buf[1024];
    while (!s->stop) {
        int cfd = accept(s->listen_fd, NULL, NULL);
        if (cfd < 0) {
            if (s->stop) break;
            continue;
        }
        (void)recv(cfd, buf, sizeof(buf), 0);
        (void)send(cfd, RESP, (int)strlen(RESP), 0);
        close(cfd);
    }
    return NULL;
}

int64_t flow_rt_http_serve_hello(int32_t port, int32_t n_req) {
    static const char *HELLO =
        "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n"
        "Content-Length: 15\r\nConnection: close\r\n\r\n"
        "Hello from Flow";
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return -1;
    int yes = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons((uint16_t)port);
    if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0 || listen(fd, 32) < 0) {
        close(fd);
        return -1;
    }
    int64_t served = 0;
    char buf[1024];
    while (served < n_req) {
        int cfd = accept(fd, NULL, NULL);
        if (cfd < 0) continue;
        (void)recv(cfd, buf, sizeof(buf), 0);
        (void)send(cfd, HELLO, (int)strlen(HELLO), 0);
        close(cfd);
        served++;
    }
    close(fd);
    return served;
}

/* Client GETs against accept_loop server; returns completed count (no timing). */
int64_t flow_rt_http_bench_run(int32_t port, int32_t n_req) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return -1;
    int yes = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons((uint16_t)port);
    if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        close(fd);
        return -1;
    }
    if (listen(fd, 128) < 0) {
        close(fd);
        return -1;
    }

    http_srv srv = {.listen_fd = fd, .stop = 0};
    pthread_t th;
    if (pthread_create(&th, NULL, accept_loop, &srv) != 0) {
        close(fd);
        return -1;
    }

    for (int i = 0; i < 20; i++) {
        int c = socket(AF_INET, SOCK_STREAM, 0);
        if (c < 0) continue;
        if (connect(c, (struct sockaddr *)&addr, sizeof(addr)) == 0) {
            const char *req = "GET / HTTP/1.0\r\n\r\n";
            send(c, req, (int)strlen(req), 0);
            char b[256];
            (void)recv(c, b, sizeof(b), 0);
        }
        close(c);
    }

    int64_t ok = 0;
    for (int i = 0; i < n_req; i++) {
        int c = socket(AF_INET, SOCK_STREAM, 0);
        if (c < 0) continue;
        if (connect(c, (struct sockaddr *)&addr, sizeof(addr)) == 0) {
            const char *req = "GET / HTTP/1.0\r\n\r\n";
            if (send(c, req, (int)strlen(req), 0) > 0) {
                char b[256];
                if (recv(c, b, sizeof(b), 0) > 0) ok++;
            }
        }
        close(c);
    }

    srv.stop = 1;
    int poke = socket(AF_INET, SOCK_STREAM, 0);
    if (poke >= 0) {
        (void)connect(poke, (struct sockaddr *)&addr, sizeof(addr));
        close(poke);
    }
    close(fd);
    pthread_join(th, NULL);
    return ok;
}
