/* Threaded accept-loop server for the Flow HTTP bench.
 * Serve and client loops live in lib/runtime/http_bench.flow; C keeps only
 * the background server thread (pthread + volatile stop flag) and a
 * string-typed send shim. */
#include <arpa/inet.h>
#include <netinet/in.h>
#include <pthread.h>
#include <stdint.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

static const char *RESP =
    "HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\nOK";

typedef struct {
    int listen_fd;
    int port;
    volatile int stop;
} http_srv;

static http_srv g_srv;
static pthread_t g_srv_thread;

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

int32_t flow_rt_http_bench_srv_start(int32_t port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return -1;
    int yes = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons((uint16_t)port);
    if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0 || listen(fd, 128) < 0) {
        close(fd);
        return -1;
    }
    g_srv.listen_fd = fd;
    g_srv.port = port;
    g_srv.stop = 0;
    if (pthread_create(&g_srv_thread, NULL, accept_loop, &g_srv) != 0) {
        close(fd);
        return -1;
    }
    return fd;
}

int32_t flow_rt_http_bench_srv_stop(void) {
    g_srv.stop = 1;
    /* Poke the accept loop awake. */
    int poke = socket(AF_INET, SOCK_STREAM, 0);
    if (poke >= 0) {
        struct sockaddr_in addr;
        memset(&addr, 0, sizeof(addr));
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
        addr.sin_port = htons((uint16_t)g_srv.port);
        (void)connect(poke, (struct sockaddr *)&addr, sizeof(addr));
        close(poke);
    }
    close(g_srv.listen_fd);
    pthread_join(g_srv_thread, NULL);
    return 0;
}

int32_t flow_rt_tcp_send_str(int32_t fd, const char *s, int32_t len) {
    if (fd < 0 || !s || len <= 0) return -1;
    return (int32_t)send(fd, s, (size_t)len, 0);
}
